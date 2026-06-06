import argparse
import json
import os

import cv2
import numpy as np
from tqdm import tqdm

from arguments import ModelParams, get_combined_args
from gaussian_renderer import GaussianModel
from scene import Scene
from utils.graphics_utils import getWorld2View2
from utils.point_utils import create_point_cloud, get_intrinsics, ply_color_fusion
from utils.pose_utils import generate_ellipse_path


def read_image(path, size_hw):
    image = cv2.imread(path)
    if image is None:
        raise FileNotFoundError(path)
    height, width = size_hw
    if image.shape[:2] != (height, width):
        image = cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)
    return image


def read_mask(path, size_hw, stride):
    mask = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise FileNotFoundError(path)
    height, width = size_hw
    if mask.shape[:2] != (height, width):
        mask = cv2.resize(mask, (width, height), interpolation=cv2.INTER_NEAREST)
    mask = mask > 127
    if stride > 1:
        keep = np.zeros_like(mask, dtype=bool)
        keep[::stride, ::stride] = True
        mask &= keep
    return mask.reshape(-1)


def make_fused_mask_ply(dataset, args, config):
    gaussians = GaussianModel(dataset.sh_degree)
    scene = Scene(dataset, gaussians, load_iteration=args.iteration, shuffle=False)

    views = scene.getTrainCameras()
    view = views[0]
    circle_radius = config.get("circle_radius")
    if circle_radius is None:
        raise ValueError("circle_radius is missing. Run tools/virtual_pose.py first.")

    poses = generate_ellipse_path(
        views,
        n_frames=args.n_frames,
        is_circle=True,
        circle_radius=circle_radius,
    )

    step_num = str(scene.loaded_iter)
    depth_dir = os.path.join(
        dataset.model_path,
        "virtual",
        "ours_object_removal",
        f"iteration_{step_num}",
        "depth_completed",
    )
    image_dir = os.path.join(dataset.source_path, config.get("images", "images_inpaint_unseen_virtual"))
    mask_dir = os.path.join(dataset.source_path, config.get("object_path", "inpaint_2d_unseen_mask_virtual"))
    out_dir = os.path.join(
        dataset.model_path,
        "virtual",
        "ours_object_removal",
        f"iteration_{step_num}",
        "fused_mask_col_dep_ply",
    )
    os.makedirs(out_dir, exist_ok=True)

    for idx, pose in enumerate(tqdm(poses, desc="Create fused mask ply")):
        name = f"{idx:05d}"
        depth_path = os.path.join(depth_dir, name + ".npy")
        image_path = os.path.join(image_dir, name + ".JPG")
        mask_path = os.path.join(mask_dir, name + ".png")

        if not os.path.exists(depth_path):
            raise FileNotFoundError(depth_path)

        depth = np.load(depth_path)
        height, width = depth.shape
        image = read_image(image_path, (height, width))
        mask = read_mask(mask_path, (height, width), args.stride)

        w2c = np.zeros((4, 4), dtype=np.float64)
        view_r = pose[:3, :3].T
        view_t = pose[:3, 3]
        w2c[:3, :3] = view_r.transpose()
        w2c[:3, 3] = view_t
        w2c[3, 3] = 1.0
        c2w = np.linalg.inv(w2c)

        intrinsics = get_intrinsics(height, width, view.FoVx, view.FoVy)
        points = create_point_cloud(depth, intrinsics, c2w)
        colors = image.reshape(-1, 3)

        out_path = os.path.join(out_dir, name + ".ply")
        ply_color_fusion(points, colors, out_path, mask=mask)

    print(f"Done. Fused mask ply files saved to: {out_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create masked fused point clouds from LaMa virtual inpainting results.")
    model = ModelParams(parser, sentinel=True)
    parser.add_argument("--iteration", default=-1, type=int)
    parser.add_argument("--config_file", required=True)
    parser.add_argument("--n_frames", default=30, type=int)
    parser.add_argument("--stride", default=1, type=int, help="Keep every Nth masked pixel to reduce seed points.")
    args = get_combined_args(parser)

    with open(args.config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    make_fused_mask_ply(model.extract(args), args, config)
