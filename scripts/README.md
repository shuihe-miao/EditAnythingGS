# Script Templates

These scripts are reproducibility templates. They assume the upstream projects
are installed separately and that you have exported local path variables.

Required environment variables:

```bash
export EDITANYTHINGGS_ROOT=/path/to/EditAnythingGS
export INPAINT360GS_ROOT=/path/to/Inpaint360GS
export DREAMGAUSSIAN_ROOT=/path/to/dreamgaussian
export DATASET_NAME=mydata
export SCENE_NAME=video2_table
export RESOLUTION=4
```

Run order:

```bash
bash scripts/00_prepare_workspace.sh
bash scripts/01_copy_tools_to_inpaint360gs.sh
bash scripts/02_reproduce_table_scene.sh
bash scripts/03_insert_dreamgaussian_object.sh
```

Read [../docs/REPRODUCE.md](../docs/REPRODUCE.md) before running the full
workflow.

