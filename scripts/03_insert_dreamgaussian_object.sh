#!/usr/bin/env bash
set -euo pipefail

: "${INPAINT360GS_ROOT:?Set INPAINT360GS_ROOT=/path/to/Inpaint360GS}"
: "${DREAMGAUSSIAN_ROOT:?Set DREAMGAUSSIAN_ROOT=/path/to/dreamgaussian}"

DATASET_NAME="${DATASET_NAME:-mydata}"
SCENE_NAME="${SCENE_NAME:-video2_table}"
OBJECT_PATH="${OBJECT_PATH:-associated_sam2manual}"
DG_PLY="${DG_PLY:-$DREAMGAUSSIAN_ROOT/logs/yellow_car_front34_model.ply}"
BASE_PLY="${BASE_PLY:-output/${DATASET_NAME}/${SCENE_NAME}/point_cloud_object_inpaint_virtual/iteration_5000/point_cloud.ply}"
OUT_PLY="${OUT_PLY:-output/${DATASET_NAME}/${SCENE_NAME}/point_cloud_dream_insert/iteration_0/point_cloud.ply}"

cd "$INPAINT360GS_ROOT"

echo "[1/2] inserting DreamGaussian object"
python tools/insert_dreamgaussian_object.py \
  --base_ply "$BASE_PLY" \
  --object_ply "$DG_PLY" \
  --out_ply "$OUT_PLY" \
  --scale "${DG_SCALE:-0.12}" \
  --tx "${DG_TX:--0.3}" \
  --ty "${DG_TY:-0.34}" \
  --tz "${DG_TZ:-0}" \
  --rotate_z "${DG_ROTATE_Z:-0}" \
  --object_id "${DG_OBJECT_ID:-4}"

echo "[2/2] rendering RGB preview"
python tools/render_rgb_model.py \
  -s "data/${DATASET_NAME}/${SCENE_NAME}" \
  -m "output/${DATASET_NAME}/${SCENE_NAME}" \
  --object_path "$OBJECT_PATH" \
  --iteration _dream_insert/iteration_0 \
  --render_video

echo "[OK] object insertion and RGB preview completed"
