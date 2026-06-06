import argparse
import math
import os
from types import SimpleNamespace

import numpy as np
from plyfile import PlyData, PlyElement

from insert_dreamgaussian_object import (
    bbox,
    copy_matching_fields,
    make_output_dtype,
    read_vertices,
    transform_object,
)
from print_object_bbox import classify_objects


def xyz_array(vertices):
    return np.stack([vertices["x"], vertices["y"], vertices["z"]], axis=1).astype(np.float32)


def target_bbox_from_classifier(target_ply, classifier_path, object_id):
    vertices = read_vertices(target_ply)
    labels, _ = classify_objects(vertices, classifier_path)
    mask = labels == object_id
    if not mask.any():
        raise RuntimeError(f"No points classified as object_id={object_id} in {target_ply}")

    xyz = xyz_array(vertices)[mask]
    return xyz.min(axis=0), xyz.max(axis=0), xyz.mean(axis=0), xyz.shape[0]


def local_object_bbox(vertices, scale, rotate_z):
    obj = vertices.copy()
    args = SimpleNamespace(tx=0.0, ty=0.0, tz=0.0, scale=scale, rotate_z=rotate_z)
    transform_object(obj, args)
    return bbox(obj)


def parse_axis(axis_name, target_extent):
    if axis_name == "auto":
        return int(np.argmax(target_extent))
    return {"x": 0, "y": 1, "z": 2}[axis_name]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_ply", required=True)
    parser.add_argument("--object_ply", required=True)
    parser.add_argument("--semantic_ply", required=True)
    parser.add_argument("--classifier", required=True)
    parser.add_argument("--out_ply", required=True)
    parser.add_argument("--target_object_id", type=int, default=2)
    parser.add_argument("--new_object_id", type=int, default=4)
    parser.add_argument("--object_feature_value", type=float, default=10.0)
    parser.add_argument("--scale", type=float, default=0.12)
    parser.add_argument("--rotate_z", type=float, default=0.0)
    parser.add_argument("--up_axis", choices=["auto", "x", "y", "z"], default="auto")
    parser.add_argument("--bottom_side", choices=["min", "max"], default="min")
    parser.add_argument("--floor_offset", type=float, default=0.0)
    parser.add_argument("--extra_tx", type=float, default=0.0)
    parser.add_argument("--extra_ty", type=float, default=0.0)
    parser.add_argument("--extra_tz", type=float, default=0.0)
    args = parser.parse_args()

    base = read_vertices(args.base_ply)
    obj_src = read_vertices(args.object_ply)
    target_min, target_max, target_center, target_count = target_bbox_from_classifier(
        args.semantic_ply, args.classifier, args.target_object_id
    )

    target_extent = target_max - target_min
    up_axis = parse_axis(args.up_axis, target_extent)

    local_min, local_max = local_object_bbox(obj_src, args.scale, args.rotate_z)
    translation = target_center.copy()
    if args.bottom_side == "min":
        translation[up_axis] = target_min[up_axis] - local_min[up_axis] + args.floor_offset
    else:
        translation[up_axis] = target_max[up_axis] - local_max[up_axis] + args.floor_offset
    translation += np.array([args.extra_tx, args.extra_ty, args.extra_tz], dtype=np.float32)

    out_dtype = make_output_dtype(base)
    obj = np.zeros(len(obj_src), dtype=out_dtype)
    copy_matching_fields(obj_src, obj)

    obj_dc_names = [name for name in out_dtype.names if name.startswith("obj_dc_")]
    for name in obj_dc_names:
        obj[name] = 0.0
    obj_name = f"obj_dc_{args.new_object_id}"
    if obj_name in out_dtype.names:
        obj[obj_name] = args.object_feature_value

    transform_args = SimpleNamespace(
        tx=float(translation[0]),
        ty=float(translation[1]),
        tz=float(translation[2]),
        scale=args.scale,
        rotate_z=args.rotate_z,
    )
    transform_object(obj, transform_args)

    combined = np.empty(len(base) + len(obj), dtype=out_dtype)
    combined[: len(base)] = base
    combined[len(base) :] = obj

    os.makedirs(os.path.dirname(args.out_ply), exist_ok=True)
    PlyData([PlyElement.describe(combined, "vertex")]).write(args.out_ply)

    obj_min, obj_max = bbox(obj)
    print(f"target object id: {args.target_object_id}")
    print(f"target count: {target_count}")
    print(f"target bbox min/max: {target_min} / {target_max}")
    print(f"target center: {target_center}")
    print(f"target extent: {target_extent}")
    print(f"chosen up axis: {'xyz'[up_axis]}")
    print(f"bottom side: {args.bottom_side}")
    print(f"translation tx ty tz: {translation}")
    print(f"inserted object bbox min/max: {obj_min} / {obj_max}")
    print(f"base points: {len(base)}")
    print(f"object points: {len(obj)}")
    print(f"combined points: {len(combined)}")
    print(f"saved: {args.out_ply}")


if __name__ == "__main__":
    main()
