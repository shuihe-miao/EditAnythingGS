# Weights and Checkpoints

Do not commit heavy model checkpoints or trained Gaussian outputs to the main
Git repository. Use this directory only as a local placeholder.

## Recommended Layout

```text
weights/
  inpaint360gs/
  lama/
  dreamgaussian/
  sam2/
  generated_assets/
```

## What Goes Where

- `inpaint360gs/`: upstream checkpoints or trained object-aware scene outputs if
  you are testing locally.
- `lama/`: LaMa inpainting checkpoints.
- `dreamgaussian/`: DreamGaussian checkpoints or generated object assets.
- `sam2/`: SAM2 checkpoints if used locally.
- `generated_assets/`: project-generated assets such as a yellow toy-car PLY.

## Public Release Recommendation

For public reproducibility, upload large files to one of:

- GitHub Releases,
- Hugging Face,
- Google Drive,
- another stable file host.

Then document:

```text
file name:
download URL:
target path:
SHA256:
source / owner:
license note:
```

## Example

```text
yellow_car_front34_model.ply
target path: $DREAMGAUSSIAN_ROOT/logs/yellow_car_front34_model.ply
source: generated with DreamGaussian for this demo
SHA256: <fill-after-upload>
```

