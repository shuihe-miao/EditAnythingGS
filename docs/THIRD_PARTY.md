# Third-Party Projects and Attribution

EditAnythingGS is an integration and reproducibility project. It relies on
several upstream research projects. The upstream algorithms, pretrained weights,
and original implementations remain the work of their authors.

## Upstream Projects

| Component | Role in this project | Notes |
| --- | --- | --- |
| Inpaint360GS | object-aware 3DGS editing, removal, virtual views, 3D inpainting | Follow the official repository license and citation. |
| DreamGaussian | generate an external Gaussian object PLY | Follow the official repository license and citation. |
| LaMa | RGB/depth inpainting backend | Follow the official repository license and checkpoint terms. |
| Segment-and-Track-Anything | optional mask propagation / refinement | Follow the official repository license. |
| SAM2 or equivalent mask source | high-quality object masks | Follow the model and checkpoint terms. |
| COLMAP | camera reconstruction | Follow COLMAP licensing and citation guidance. |

## Project-Specific Contributions

The project-specific work in this repository includes:

- custom-scene workflow documentation,
- SAM2-to-instance-mask conversion,
- object-id mapping and mask preview generation,
- DreamGaussian PLY transform and insertion utilities,
- RGB-only rendering helper for merged scenes,
- reproducibility scripts and command templates,
- experiment notes for a tabletop scene editing demo.

## What This Repository Does Not Claim

This repository does not claim authorship of the core methods introduced by
Inpaint360GS, DreamGaussian, LaMa, SAM2, or COLMAP. It packages a practical
workflow that connects those methods for a custom 3DGS scene-editing task.

## Checkpoint and Data Policy

Third-party checkpoints should not be committed into this repository unless
their licenses explicitly allow redistribution and the files are suitable for
Git hosting. Prefer download scripts, official links, or release assets.

Generated results from this project can be released separately, but they should
be labeled clearly as experiment outputs rather than upstream model weights.

## Citation Guidance

When publishing results based on this repository, cite the upstream papers and
repositories that provide the core algorithms. If you use this integration
workflow directly, also mention EditAnythingGS as the reproducibility wrapper or
engineering pipeline used for the experiment.

