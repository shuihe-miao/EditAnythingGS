# Expected Results

This document records the expected outputs for the reference tabletop scene
experiment. Exact numbers may change if you retrain the base 3DGS scene, change
mask quality, adjust thresholds, or use different inpainting settings.

## Reference Scene

```text
dataset: mydata
scene: video2_table
target object id: 2
target object name: water_bottle
inserted object: yellow toy car generated with DreamGaussian
```

## Main Output Stages

| Stage | Expected output |
| --- | --- |
| Original 3DGS scene | `output/mydata/video2_table/point_cloud/iteration_2000/point_cloud.ply` |
| Object removal | `output/mydata/video2_table/point_cloud_object_removal/iteration_2000/point_cloud.ply` |
| 3D inpainting | `output/mydata/video2_table/point_cloud_object_inpaint_virtual/iteration_5000/point_cloud.ply` |
| DreamGaussian insertion | `output/mydata/video2_table/point_cloud_dream_insert/iteration_0/point_cloud.ply` |
| RGB preview video | `output/mydata/video2_table/video_rgb/.../final_video.mp4` |

## Point Count Evidence

The reference run produced the following point-count pattern:

```text
original scene:       859050 points
after object removal: 850723 points
removed target:         8327 points
after inpainting:     851992 points
new inpainted points:   1269 points
```

These numbers are useful as sanity checks. They should not be treated as strict
unit-test values because retraining and mask changes can alter the final point
cloud.

## Videos to Inspect

For a complete visual check, compare:

1. original scene rendering,
2. object-removed rendering,
3. inpainted-scene rendering,
4. DreamGaussian-object inserted rendering,
5. optional 2x2 comparison video.

The most important visual checks are:

- the removed object should not leave obvious Gaussian fragments,
- the inpainted background should not contain large holes,
- the inserted object should have reasonable scale and position,
- RGB preview should be stable across multiple camera views.

## Common Differences

You may see different results if:

- SAM2 masks are tighter or looser than the reference masks,
- the object removal threshold changes,
- the LaMa mask dilation changes,
- the generated DreamGaussian object has a different scale or coordinate range,
- the insertion transform is tuned differently.

