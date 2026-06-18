#!/usr/bin/env bash
set -euo pipefail

: "${INPAINT360GS_ROOT:?Set INPAINT360GS_ROOT=/path/to/Inpaint360GS}"
: "${SAM2_MASK_ROOT:?Set SAM2_MASK_ROOT=/path/to/sam2_masks}"

DATASET_NAME="${DATASET_NAME:-mydata}"
SCENE_NAME="${SCENE_NAME:-video2_table}"
RESOLUTION="${RESOLUTION:-4}"
OBJECT_PATH="${OBJECT_PATH:-associated_sam2manual}"

cd "$INPAINT360GS_ROOT"

echo "[1/3] converting SAM2 masks"
python tools/convert_sam2_masks.py \
  --scene_path "data/${DATASET_NAME}/${SCENE_NAME}" \
  --sam2_root "$SAM2_MASK_ROOT" \
  --image_folder "images_${RESOLUTION}" \
  --mask_name sam2manual \
  --object 1:obj_001:dictionary \
  --object 2:obj_002:water_bottle \
  --object 3:obj_003:tea_can

echo "[2/3] distilling object features"
python seg/distillation.py \
  --source_path "data/${DATASET_NAME}/${SCENE_NAME}" \
  --model_path "output/${DATASET_NAME}/${SCENE_NAME}" \
  --vanilla_3dgs_path "output/${DATASET_NAME}/${SCENE_NAME}/3dgs_output" \
  --resolution "$RESOLUTION" \
  --object_path "$OBJECT_PATH"

echo "[3/3] removing target object id 2"
python edit_object_removal.py \
  -s "data/${DATASET_NAME}/${SCENE_NAME}" \
  -m "output/${DATASET_NAME}/${SCENE_NAME}" \
  --object_path "$OBJECT_PATH" \
  --select_obj_id 2 \
  --render_video

echo "[OK] removal stage completed. Continue with upstream inpainting, then run 03_insert_dreamgaussian_object.sh"

