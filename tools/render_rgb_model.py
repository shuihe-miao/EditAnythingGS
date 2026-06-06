#
# RGB-only renderer for loading a custom Gaussian point_cloud.ply checkpoint.
# This intentionally skips semantic classifier loading so merged external
# Gaussian objects can be previewed before any semantic distillation.
#

import os
import sys
from argparse import ArgumentParser

import cv2
import torch
from tqdm import tqdm

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from arguments import ModelParams, PipelineParams, get_combined_args
from gaussian_renderer import render
from scene import GaussianModel, Scene
from utils.general_utils import safe_state


def tensor_to_bgr_uint8(image):
    image = torch.clamp(image, 0.0, 1.0).detach().cpu()
    image = image.permute(1, 2, 0).numpy()
    image = (image * 255).astype("uint8")
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


def safe_iter_name(iteration):
    return str(iteration).strip("/").replace("/", "_").replace("\\", "_")


def render_video(scene, gaussians, pipeline, background, out_dir, fps=24):
    if hasattr(scene, "getVideoCameras"):
        cameras = scene.getVideoCameras()
    else:
        cameras = []

    if not cameras and hasattr(scene, "getTestCameras"):
        cameras = scene.getTestCameras()

    if not cameras:
        cameras = scene.getTrainCameras()

    os.makedirs(out_dir, exist_ok=True)
    render_dir = os.path.join(out_dir, "renders")
    os.makedirs(render_dir, exist_ok=True)

    writer = None
    video_path = os.path.join(out_dir, "final_video.mp4")

    for idx, view in enumerate(tqdm(cameras, desc="Rendering RGB preview")):
        package = render(view, gaussians, pipeline, background)
        frame = tensor_to_bgr_uint8(package["render"])

        if writer is None:
            height, width = frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

        writer.write(frame)
        cv2.imwrite(os.path.join(render_dir, f"{idx:05d}.png"), frame)

    if writer is not None:
        writer.release()

    print(f"[OK] RGB preview video saved to {video_path}")
    print(f"[OK] RGB preview frames saved to {render_dir}")


def render_sets(dataset, iteration, pipeline, render_video_flag):
    gaussians = GaussianModel(dataset.sh_degree)
    scene = Scene(dataset, gaussians, load_iteration=iteration, shuffle=False)

    bg_color = [1, 1, 1] if dataset.white_background else [0, 0, 0]
    background = torch.tensor(bg_color, dtype=torch.float32, device="cuda")

    out_dir = os.path.join(
        dataset.model_path,
        "video_rgb",
        f"ours_{safe_iter_name(scene.loaded_iter)}",
    )

    if render_video_flag:
        render_video(scene, gaussians, pipeline, background, out_dir)
    else:
        render_video(scene, gaussians, pipeline, background, out_dir)


if __name__ == "__main__":
    parser = ArgumentParser(description="Render RGB-only Gaussian checkpoint")
    model = ModelParams(parser, sentinel=True)
    pipeline = PipelineParams(parser)
    parser.add_argument("--iteration", default="_dream_insert/iteration_0")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--render_video", action="store_true")

    args = get_combined_args(parser)
    safe_state(args.quiet)
    render_sets(model.extract(args), args.iteration, pipeline.extract(args), args.render_video)
