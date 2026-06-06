#!/usr/bin/env bash
set -e

cd ~/projects/Inpaint360GS
conda activate inpaint360gs

export DATASET=mydata
export SCENE=video2_table
export RES=4
export PYTHONPATH=$(pwd):$(pwd)/seg:$(pwd)/seg/detectron2:$(pwd)/seg/detectron2/detectron2/projects/CropFormer:$PYTHONPATH

# 1. Convert high-quality external SAM2 masks into Inpaint360GS format.
python tools/convert_sam2_masks.py \
  --scene_path data/${DATASET}/${SCENE} \
  --sam2_root "/mnt/c/path/to/sam2_masks_v2" \
  --image_folder images_${RES} \
  --mask_name sam2manual \
  --object 1:obj_001:dictionary \
  --object 2:obj_002:water_bottle \
  --object 3:obj_003:tea_can

# 2. Distill object masks into 3DGS object features.
python seg/distillation.py \
  --source_path data/${DATASET}/${SCENE} \
  --model_path output/${DATASET}/${SCENE} \
  --vanilla_3dgs_path output/${DATASET}/${SCENE}/3dgs_output \
  --resolution ${RES} \
  --object_path associated_sam2manual

# 3. Remove object id 2.
python edit_object_removal.py \
  -s data/${DATASET}/${SCENE} \
  -m output/${DATASET}/${SCENE} \
  --object_path associated_sam2manual \
  --select_obj_id 2 \
  --render_video

