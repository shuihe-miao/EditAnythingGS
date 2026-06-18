# Reproduction Guide

This document describes how to reproduce the EditAnythingGS tabletop scene
editing result. The workflow assumes that the upstream projects are installed in
separate folders and environments.

## 0. Prepare Upstream Projects

Clone and install the upstream projects according to their official
instructions:

```text
Inpaint360GS       -> scene reconstruction, object distillation, removal, inpainting
DreamGaussian      -> image/text-to-3D object generation
LaMa               -> RGB/depth inpainting backend used by the editing workflow
SAM2 or equivalent -> high-quality object masks
```

Recommended environment split:

```text
conda env: inpaint360gs
conda env: lama
conda env: dreamgaussian
```

Do not force all dependencies into one environment. PyTorch, CUDA extensions,
NumPy, SciPy, and Hugging Face dependencies are easier to manage separately.

## 1. Set Local Paths

From this repository:

```bash
export EDITANYTHINGGS_ROOT=/path/to/EditAnythingGS
export INPAINT360GS_ROOT=/path/to/Inpaint360GS
export DREAMGAUSSIAN_ROOT=/path/to/dreamgaussian
export DATASET_NAME=mydata
export SCENE_NAME=video2_table
export RESOLUTION=4
```

Then copy the bridge tools into the Inpaint360GS working tree:

```bash
bash scripts/01_copy_tools_to_inpaint360gs.sh
```

## 2. Prepare Data

Download the reference `video2_table` dataset:

```text
https://drive.google.com/drive/folders/1p9jbg28zGjfWnzGB-hka7sY-CYfn9VWL?usp=sharing
```

Place the scene under the Inpaint360GS data directory:

```text
$INPAINT360GS_ROOT/data/mydata/video2_table/
  images/
  images_4/
  sparse/0/
  raw_sam2manual/
  associated_sam2manual/
  associated_sam2manual_color/
```

The exact folders depend on your preprocessing resolution. For details, see
[DATA.md](DATA.md).

## 3. Convert SAM2 Masks

Assume your SAM2 masks are stored as:

```text
sam2_masks/
  objects/
    obj_001/
      frame_00001.png
      ...
    obj_002/
    obj_003/
```

Run:

```bash
cd "$INPAINT360GS_ROOT"
conda activate inpaint360gs

python tools/convert_sam2_masks.py \
  --scene_path data/${DATASET_NAME}/${SCENE_NAME} \
  --sam2_root /path/to/sam2_masks \
  --image_folder images_${RESOLUTION} \
  --mask_name sam2manual \
  --object 1:obj_001:dictionary \
  --object 2:obj_002:water_bottle \
  --object 3:obj_003:tea_can
```

This creates:

```text
raw_sam2manual/
associated_sam2manual/
associated_sam2manual_color/
associated_sam2manual/scene.json
```

## 4. Train / Load the Base 3DGS Scene

Use the upstream Inpaint360GS preprocessing and vanilla 3DGS training flow to
obtain:

```text
output/mydata/video2_table/3dgs_output/
```

If you already have a trained base scene, place it at the path expected by the
upstream scripts.

## 5. Distill Object Masks into 3D Gaussian Features

```bash
cd "$INPAINT360GS_ROOT"
conda activate inpaint360gs

python seg/distillation.py \
  --source_path data/${DATASET_NAME}/${SCENE_NAME} \
  --model_path output/${DATASET_NAME}/${SCENE_NAME} \
  --vanilla_3dgs_path output/${DATASET_NAME}/${SCENE_NAME}/3dgs_output \
  --resolution ${RESOLUTION} \
  --object_path associated_sam2manual
```

The expected output is an object-aware Gaussian model with learned object
features and a classifier checkpoint.

## 6. Remove the Target Object

Example: remove object id `2`, the water bottle.

```bash
python edit_object_removal.py \
  -s data/${DATASET_NAME}/${SCENE_NAME} \
  -m output/${DATASET_NAME}/${SCENE_NAME} \
  --object_path associated_sam2manual \
  --select_obj_id 2 \
  --render_video
```

The removal stage writes a new Gaussian PLY and preview renders under the
upstream output directory.

## 7. Run RGB/Depth Inpainting and 3D Inpainting

Follow the Inpaint360GS inpainting stage with the virtual views generated after
object removal. The high-level steps are:

1. render virtual RGB/depth/mask views,
2. use Segment-and-Track-Anything or mask propagation if needed,
3. run LaMa RGB/depth inpainting,
4. fuse inpainted RGB/depth back to 3D points,
5. optimize newly added Gaussian points.

The expected completed inpainted scene is:

```text
output/mydata/video2_table/point_cloud_object_inpaint_virtual/iteration_5000/point_cloud.ply
```

Adjust the iteration path if your upstream script writes a different folder.

## 8. Generate a New Object with DreamGaussian

In the DreamGaussian environment, generate or prepare an object Gaussian PLY.
The reference experiment uses a yellow toy-car object.

Expected example path:

```text
$DREAMGAUSSIAN_ROOT/logs/yellow_car_front34_model.ply
```

## 9. Insert the DreamGaussian Object into the Edited Scene

```bash
cd "$INPAINT360GS_ROOT"
conda activate inpaint360gs

BASE=output/${DATASET_NAME}/${SCENE_NAME}/point_cloud_object_inpaint_virtual/iteration_5000/point_cloud.ply
DG_PLY=$DREAMGAUSSIAN_ROOT/logs/yellow_car_front34_model.ply

python tools/insert_dreamgaussian_object.py \
  --base_ply "$BASE" \
  --object_ply "$DG_PLY" \
  --out_ply output/${DATASET_NAME}/${SCENE_NAME}/point_cloud_dream_insert/iteration_0/point_cloud.ply \
  --scale 0.12 \
  --tx -0.3 \
  --ty 0.34 \
  --tz 0 \
  --rotate_z 0 \
  --object_id 4
```

The transform parameters are scene-specific. Use
`tools/print_object_bbox.py` or visual preview renders to tune them.

## 10. Render the RGB Preview

```bash
python tools/render_rgb_model.py \
  -s data/${DATASET_NAME}/${SCENE_NAME} \
  -m output/${DATASET_NAME}/${SCENE_NAME} \
  --object_path associated_sam2manual \
  --iteration _dream_insert/iteration_0 \
  --render_video
```

Expected output:

```text
output/mydata/video2_table/video_rgb/ours__dream_insert_iteration_0/final_video.mp4
```

The exact folder name depends on the iteration string.

## Troubleshooting

- If object removal leaves visible fragments, lower or tune the removal
  threshold in the upstream removal script.
- If LaMa output is too dark or inconsistent, enlarge the inpainting mask so the
  model receives more surrounding context.
- If the inserted object looks too large or too small, tune `--scale`.
- If the object floats or intersects the table, tune `--tx`, `--ty`, `--tz`.
- If RGB rendering fails because of semantic classifier mismatch, use
  `tools/render_rgb_model.py`, which intentionally skips classifier loading.
