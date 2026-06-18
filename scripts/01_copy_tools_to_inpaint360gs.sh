#!/usr/bin/env bash
set -euo pipefail

: "${EDITANYTHINGGS_ROOT:?Set EDITANYTHINGGS_ROOT=/path/to/EditAnythingGS}"
: "${INPAINT360GS_ROOT:?Set INPAINT360GS_ROOT=/path/to/Inpaint360GS}"

mkdir -p "$INPAINT360GS_ROOT/tools"

cp "$EDITANYTHINGGS_ROOT"/tools/*.py "$INPAINT360GS_ROOT/tools/"

echo "[OK] copied EditAnythingGS tools to $INPAINT360GS_ROOT/tools"

