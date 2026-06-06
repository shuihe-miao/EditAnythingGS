# EditAnythingGS

EditAnythingGS is a learning-oriented 3D Gaussian Splatting editing pipeline built around Inpaint360GS and DreamGaussian. The goal is not to reproduce every paper metric, but to build an end-to-end system that can remove objects, inpaint the background, and insert a generated 3D Gaussian object into a real captured scene.

This repository contains my bridge scripts, workflow notes, and command templates. It does not vendor the full third-party repositories, datasets, checkpoints, or training outputs.

## What This Project Does

1. Reconstruct a custom scene with 3D Gaussian Splatting.
2. Use manually prompted SAM2 masks instead of CropFormer when CropFormer is too heavy or inaccurate.
3. Distill object masks into 3DGS semantic/object features.
4. Remove a selected object from the scene.
5. Generate virtual views and run LaMa color/depth inpainting.
6. Fuse inpainted color/depth back into Gaussian points.
7. Generate a new object with DreamGaussian.
8. Insert the generated object PLY into the edited Inpaint360GS scene.
9. Render an RGB preview video of the combined scene.

## Third-Party Projects

This project depends on:

- Inpaint360GS: https://github.com/dfki-av/Inpaint360GS
- DreamGaussian: https://github.com/dreamgaussian/dreamgaussian
- Segment-and-Track-Anything
- LaMa
- SAM2 or another high-quality object mask source

Keep those projects in separate folders and copy the scripts in `tools/` into your Inpaint360GS working tree when needed.

## Repository Layout

```text
EditAnythingGS/
  tools/
    convert_sam2_masks.py
    create_fused_mask_ply.py
    insert_dreamgaussian_object.py
    insert_dreamgaussian_at_object.py
    print_object_bbox.py
    render_rgb_model.py
  docs/
    workflow_zh.md
    environment_notes_zh.md
  examples/
    commands/
      inpaint360_custom_scene.sh
      dreamgaussian_insert.sh
```

## Minimal Usage

Copy tools into Inpaint360GS:

```bash
cd ~/projects/Inpaint360GS
cp /path/to/EditAnythingGS/tools/*.py tools/
```

Insert a DreamGaussian object into an edited scene:

```bash
BASE=output/mydata/video2_table/point_cloud_object_inpaint_virtual/iteration_5000/point_cloud.ply
DG_PLY=~/projects/dreamgaussian/logs/yellow_car_front34_model.ply

python tools/insert_dreamgaussian_object.py \
  --base_ply "$BASE" \
  --object_ply "$DG_PLY" \
  --out_ply output/mydata/video2_table/point_cloud_dream_insert/iteration_0/point_cloud.ply \
  --scale 0.12 \
  --tx -0.3 \
  --ty 0.34 \
  --tz 0 \
  --rotate_z 0 \
  --object_id 4
```

Render an RGB-only preview:

```bash
python tools/render_rgb_model.py \
  -s data/mydata/video2_table \
  -m output/mydata/video2_table \
  --object_path associated_sam2manual \
  --iteration _dream_insert/iteration_0 \
  --render_video
```

## Notes

The project is designed as a practical learning demo. The inserted object is currently positioned by explicit scale/translation/rotation parameters. This makes the pipeline understandable and controllable. A future version can estimate placement from object masks, depth, or a user-selected anchor point.

