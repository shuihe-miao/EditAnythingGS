import argparse
import math
import os

import numpy as np
from plyfile import PlyData, PlyElement


def read_vertices(path):
    ply = PlyData.read(path)
    return ply["vertex"].data


def make_output_dtype(base_vertices):
    return base_vertices.dtype


def copy_matching_fields(src, dst):
    src_names = set(src.dtype.names)
    for name in dst.dtype.names:
        if name in src_names:
            dst[name] = src[name]


def normalize_quaternion(q):
    norm = np.linalg.norm(q, axis=1, keepdims=True)
    norm[norm == 0] = 1
    return q / norm


def multiply_quaternion(a, b):
    aw, ax, ay, az = a[:, 0], a[:, 1], a[:, 2], a[:, 3]
    bw, bx, by, bz = b[:, 0], b[:, 1], b[:, 2], b[:, 3]
    return np.stack(
        [
            aw * bw - ax * bx - ay * by - az * bz,
            aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw,
        ],
        axis=1,
    )


def transform_object(vertices, args):
    xyz = np.stack([vertices["x"], vertices["y"], vertices["z"]], axis=1).astype(np.float32)
    center = xyz.mean(axis=0, keepdims=True)
    xyz = xyz - center

    theta = math.radians(args.rotate_z)
    c, s = math.cos(theta), math.sin(theta)
    rot = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]], dtype=np.float32)
    xyz = xyz @ rot.T
    xyz = xyz * args.scale + np.array([[args.tx, args.ty, args.tz]], dtype=np.float32)

    vertices["x"] = xyz[:, 0]
    vertices["y"] = xyz[:, 1]
    vertices["z"] = xyz[:, 2]

    for name in ("scale_0", "scale_1", "scale_2"):
        if name in vertices.dtype.names:
            vertices[name] = vertices[name] + math.log(args.scale)

    rot_names = [name for name in vertices.dtype.names if name.startswith("rot_")]
    rot_names = sorted(rot_names, key=lambda name: int(name.split("_")[-1]))
    if len(rot_names) == 4 and args.rotate_z != 0:
        q = np.stack([vertices[name] for name in rot_names], axis=1).astype(np.float32)
        q = normalize_quaternion(q)
        qz = np.zeros_like(q)
        qz[:, 0] = math.cos(theta / 2)
        qz[:, 3] = math.sin(theta / 2)
        q = normalize_quaternion(multiply_quaternion(qz, q))
        for i, name in enumerate(rot_names):
            vertices[name] = q[:, i]


def bbox(vertices):
    xyz = np.stack([vertices["x"], vertices["y"], vertices["z"]], axis=1).astype(np.float32)
    return xyz.min(axis=0), xyz.max(axis=0)


def main():
    parser = argparse.ArgumentParser(description="Insert a DreamGaussian Gaussian PLY into an Inpaint360GS scene PLY.")
    parser.add_argument("--base_ply", required=True)
    parser.add_argument("--object_ply", required=True)
    parser.add_argument("--out_ply", required=True)
    parser.add_argument("--tx", type=float, default=0.0)
    parser.add_argument("--ty", type=float, default=0.0)
    parser.add_argument("--tz", type=float, default=0.0)
    parser.add_argument("--scale", type=float, default=1.0)
    parser.add_argument("--rotate_z", type=float, default=0.0)
    parser.add_argument("--object_id", type=int, default=4)
    parser.add_argument("--object_feature_value", type=float, default=10.0)
    args = parser.parse_args()

    base = read_vertices(args.base_ply)
    obj_src = read_vertices(args.object_ply)

    out_dtype = make_output_dtype(base)
    obj = np.zeros(len(obj_src), dtype=out_dtype)
    copy_matching_fields(obj_src, obj)

    obj_dc_names = [name for name in out_dtype.names if name.startswith("obj_dc_")]
    for name in obj_dc_names:
        obj[name] = 0.0
    obj_name = f"obj_dc_{args.object_id}"
    if obj_name in out_dtype.names:
        obj[obj_name] = args.object_feature_value

    transform_object(obj, args)

    combined = np.empty(len(base) + len(obj), dtype=out_dtype)
    combined[: len(base)] = base
    combined[len(base) :] = obj

    os.makedirs(os.path.dirname(args.out_ply), exist_ok=True)
    PlyData([PlyElement.describe(combined, "vertex")]).write(args.out_ply)

    base_min, base_max = bbox(base)
    obj_min, obj_max = bbox(obj)
    print(f"base points: {len(base)}")
    print(f"object points: {len(obj)}")
    print(f"combined points: {len(combined)}")
    print(f"base bbox min/max: {base_min} / {base_max}")
    print(f"object bbox min/max: {obj_min} / {obj_max}")
    print(f"saved: {args.out_ply}")


if __name__ == "__main__":
    main()
