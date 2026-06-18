#!/usr/bin/env bash
set -euo pipefail

: "${EDITANYTHINGGS_ROOT:?Set EDITANYTHINGGS_ROOT=/path/to/EditAnythingGS}"
: "${INPAINT360GS_ROOT:?Set INPAINT360GS_ROOT=/path/to/Inpaint360GS}"
: "${DREAMGAUSSIAN_ROOT:?Set DREAMGAUSSIAN_ROOT=/path/to/dreamgaussian}"

echo "[EditAnythingGS] checking workspace paths"

for path in "$EDITANYTHINGGS_ROOT" "$INPAINT360GS_ROOT" "$DREAMGAUSSIAN_ROOT"; do
  if [ ! -d "$path" ]; then
    echo "[ERROR] directory not found: $path" >&2
    exit 1
  fi
  echo "[OK] $path"
done

mkdir -p "$EDITANYTHINGGS_ROOT/weights"
mkdir -p "$EDITANYTHINGGS_ROOT/releases"

echo "[OK] workspace is ready"

