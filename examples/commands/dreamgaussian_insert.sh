#!/usr/bin/env bash
set -e

cd ~/projects/Inpaint360GS
conda activate inpaint360gs

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

python tools/render_rgb_model.py \
  -s data/mydata/video2_table \
  -m output/mydata/video2_table \
  --object_path associated_sam2manual \
  --iteration _dream_insert/iteration_0 \
  --render_video

