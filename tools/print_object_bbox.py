import argparse
import os

import numpy as np
import torch
from plyfile import PlyData


def sorted_obj_names(names):
    obj_names = [name for name in names if name.startswith("obj_dc_")]
    return sorted(obj_names, key=lambda name: int(name.split("_")[-1]))


def load_vertices(path):
    return PlyData.read(path)["vertex"].data


def classify_objects(vertices, classifier_path):
    obj_names = sorted_obj_names(vertices.dtype.names)
    if not obj_names:
        raise RuntimeError("No obj_dc_* fields found in this PLY.")

    features = np.stack([vertices[name] for name in obj_names], axis=1).astype(np.float32)
    state = torch.load(classifier_path, map_location="cpu")

    if "weight" not in state or "bias" not in state:
        raise RuntimeError("Expected classifier state_dict with weight and bias.")

    weight = state["weight"].detach().cpu().numpy()
    bias = state["bias"].detach().cpu().numpy()

    weight = weight.reshape(weight.shape[0], weight.shape[1])
    logits = features @ weight.T + bias[None, :]
    labels = logits.argmax(axis=1)
    return labels, obj_names


def bbox(vertices, mask):
    xyz = np.stack([vertices["x"], vertices["y"], vertices["z"]], axis=1).astype(np.float32)
    selected = xyz[mask]
    return selected.min(axis=0), selected.max(axis=0), selected.mean(axis=0), selected.shape[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ply", required=True)
    parser.add_argument("--classifier", required=True)
    parser.add_argument("--object_id", type=int, default=2)
    args = parser.parse_args()

    if not os.path.exists(args.ply):
        raise FileNotFoundError(args.ply)
    if not os.path.exists(args.classifier):
        raise FileNotFoundError(args.classifier)

    vertices = load_vertices(args.ply)
    labels, obj_names = classify_objects(vertices, args.classifier)

    print(f"PLY: {args.ply}")
    print(f"classifier: {args.classifier}")
    print(f"object feature dims: {len(obj_names)}")
    print("class counts:")
    for class_id in sorted(np.unique(labels).tolist()):
        count = int((labels == class_id).sum())
        print(f"  class {class_id}: {count}")

    mask = labels == args.object_id
    if not mask.any():
        raise RuntimeError(f"No points classified as object_id={args.object_id}.")

    bmin, bmax, center, count = bbox(vertices, mask)
    extent = bmax - bmin
    up_axis = int(np.argmax(extent))

    print("")
    print(f"target object_id: {args.object_id}")
    print(f"target count: {count}")
    print(f"target bbox min: {bmin}")
    print(f"target bbox max: {bmax}")
    print(f"target center: {center}")
    print(f"target extent: {extent}")
    print(f"guessed vertical/up axis by largest extent: {'xyz'[up_axis]} ({up_axis})")


if __name__ == "__main__":
    main()
