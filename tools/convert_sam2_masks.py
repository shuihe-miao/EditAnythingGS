#!/usr/bin/env python3
import argparse
import json
import os

import cv2
import numpy as np


def parse_object(value):
    parts = value.split(":", 2)
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("Object mapping must be id:folder:name")
    obj_id = int(parts[0])
    if obj_id <= 0 or obj_id > 255:
        raise argparse.ArgumentTypeError("Object id must be in 1..255")
    return obj_id, parts[1], parts[2]


def main():
    parser = argparse.ArgumentParser(
        description="Convert per-object SAM2 binary masks into Inpaint360GS instance masks."
    )
    parser.add_argument("--scene_path", required=True, help="Scene path, e.g. data/mydata/video2_table")
    parser.add_argument("--sam2_root", required=True, help="SAM2 output root containing objects/obj_xxx folders")
    parser.add_argument("--image_folder", default="images_4", help="Reference image folder under scene_path")
    parser.add_argument("--mask_name", default="sam2manual", help="Output mask generator name")
    parser.add_argument(
        "--object",
        action="append",
        type=parse_object,
        required=True,
        help="Object mapping id:folder:name, e.g. 1:obj_001:dictionary. Repeat for each object.",
    )
    args = parser.parse_args()

    image_dir = os.path.join(args.scene_path, args.image_folder)
    out_raw = os.path.join(args.scene_path, f"raw_{args.mask_name}")
    out_assoc = os.path.join(args.scene_path, f"associated_{args.mask_name}")
    out_color = os.path.join(args.scene_path, f"associated_{args.mask_name}_color")

    os.makedirs(out_raw, exist_ok=True)
    os.makedirs(out_assoc, exist_ok=True)
    os.makedirs(out_color, exist_ok=True)

    objects = {obj_id: (folder, name) for obj_id, folder, name in args.object}

    frame_count = 0
    for image_name in sorted(os.listdir(image_dir)):
        if not image_name.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        image_path = os.path.join(image_dir, image_name)
        image = cv2.imread(image_path)
        if image is None:
            print(f"[skip] cannot read {image_path}")
            continue

        height, width = image.shape[:2]
        instance_mask = np.zeros((height, width), dtype=np.uint8)
        stem = os.path.splitext(image_name)[0]

        for obj_id, (folder, _) in objects.items():
            mask_path = os.path.join(args.sam2_root, "objects", folder, stem + ".png")
            if not os.path.exists(mask_path):
                continue
            mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            if mask is None:
                continue
            mask = cv2.resize(mask, (width, height), interpolation=cv2.INTER_NEAREST)
            instance_mask[mask > 127] = obj_id

        mask_name = stem + ".png"
        cv2.imwrite(os.path.join(out_raw, mask_name), instance_mask)
        cv2.imwrite(os.path.join(out_assoc, mask_name), instance_mask)

        overlay = image.copy()
        for obj_id, (_, obj_name) in objects.items():
            mask = instance_mask == obj_id
            if not np.any(mask):
                continue
            color = np.array(
                [(obj_id * 37) % 255, (obj_id * 91) % 255, (obj_id * 53) % 255],
                dtype=np.float32,
            )
            overlay[mask] = (0.55 * overlay[mask] + 0.45 * color).astype(np.uint8)
            ys, xs = np.where(mask)
            x, y = int(xs.mean()), int(ys.mean())
            cv2.putText(
                overlay,
                f"{obj_id}:{obj_name}",
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )
        cv2.imwrite(os.path.join(out_color, image_name), overlay)
        frame_count += 1

    scene_info = {
        "num_classes": max(objects.keys()) + 1,
        "raw_mask_folder": out_raw,
        "associated_mask_folder": out_assoc,
        "patches": 16,
        "objects": {str(obj_id): name for obj_id, (_, name) in objects.items()},
    }
    with open(os.path.join(out_assoc, "scene.json"), "w", encoding="utf-8") as f:
        json.dump(scene_info, f, indent=4)

    print(f"Converted {frame_count} frames")
    print(f"raw masks: {out_raw}")
    print(f"associated masks: {out_assoc}")
    print(f"preview: {out_color}")


if __name__ == "__main__":
    main()
