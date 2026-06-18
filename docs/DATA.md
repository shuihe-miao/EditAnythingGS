# Data Guide

This project uses a custom tabletop scene sequence. The full image sequence is
large and should normally be distributed outside the Git history, for example
through GitHub Releases, cloud storage, or Hugging Face datasets.

## Recommended Public Repository Policy

Recommended:

- keep only a small preview or `dataset/README.md` in Git,
- publish the full image sequence as a downloadable archive,
- include checksums for released archives,
- document exactly where users should extract the data.

Avoid:

- committing large training outputs,
- committing generated PLY checkpoints,
- committing rendered videos,
- committing third-party checkpoints.

## Reference Scene

Reference scene name:

```text
video2_table
```

Dataset download:

```text
https://drive.google.com/drive/folders/1p9jbg28zGjfWnzGB-hka7sY-CYfn9VWL?usp=sharing
```

Download the dataset from the Google Drive folder and place the extracted scene
files under the Inpaint360GS data directory described below.

Reference object ids:

```text
1 -> dictionary
2 -> water_bottle
3 -> tea_can
```

The reference experiment removes object id `2` and inserts a generated yellow
toy-car object into the edited scene.

## Expected Inpaint360GS Scene Layout

After data preparation, place or generate the scene under:

```text
$INPAINT360GS_ROOT/data/mydata/video2_table/
  images/
    frame_00001.png
    frame_00002.png
    ...
  images_4/
    frame_00001.png
    frame_00002.png
    ...
  sparse/
    0/
      cameras.bin
      images.bin
      points3D.bin
```

After converting SAM2 masks:

```text
$INPAINT360GS_ROOT/data/mydata/video2_table/
  raw_sam2manual/
  associated_sam2manual/
    scene.json
  associated_sam2manual_color/
```

## Expected SAM2 Mask Layout

`tools/convert_sam2_masks.py` expects masks grouped by object folder:

```text
sam2_masks/
  objects/
    obj_001/
      frame_00001.png
      frame_00002.png
      ...
    obj_002/
      frame_00001.png
      frame_00002.png
      ...
    obj_003/
      frame_00001.png
      frame_00002.png
      ...
```

Each mask should be a binary or grayscale PNG. Values greater than `127` are
treated as foreground.

## Dataset Release Checklist

If you publish the full dataset archive, include:

- archive name and version,
- number of frames,
- image resolution,
- scene description,
- object-id mapping,
- license or usage note,
- checksum, for example SHA256,
- expected extraction path.

Example:

```text
editanythinggs_video2_table_v1.zip
download: https://drive.google.com/drive/folders/1p9jbg28zGjfWnzGB-hka7sY-CYfn9VWL?usp=sharing
sha256: <fill-after-upload-or-after-archive>
extract to: $INPAINT360GS_ROOT/data/mydata/video2_table/
```
