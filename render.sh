#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RENDERCV_BIN="$ROOT_DIR/.venv/bin/rendercv"
PYTHON_BIN="python3"
DESIGN_FILE="$ROOT_DIR/cv/config/design.yaml"
LOCALE_FILE="$ROOT_DIR/cv/config/locale.yaml"
SETTINGS_FILE="$ROOT_DIR/cv/config/settings.yaml"

if [[ ! -x "$RENDERCV_BIN" ]]; then
  RENDERCV_BIN="rendercv"
fi

variants=(full it it_core ita mechanics)
all_output_dir="$ROOT_DIR/cv/rendercv_output/all"

declare -A input_files=(
  [full]="$ROOT_DIR/cv/generated/jesus_erro_cv_full.yaml"
  [it]="$ROOT_DIR/cv/generated/jesus_erro_cv_it.yaml"
  [it_core]="$ROOT_DIR/cv/generated/jesus_erro_cv_it_core.yaml"
  [ita]="$ROOT_DIR/cv/generated/jesus_erro_cv_ita.yaml"
  [mechanics]="$ROOT_DIR/cv/generated/jesus_erro_cv_mechanics.yaml"
)

set -a
source <(sops --decrypt --input-type dotenv --output-type dotenv "$ROOT_DIR/.env.enc")
set +a

"$PYTHON_BIN" "$ROOT_DIR/scripts/build_cv_variants.py"

mkdir -p "$all_output_dir"
find "$all_output_dir" -mindepth 1 -maxdepth 1 -exec rm -rf {} +

for variant in "${variants[@]}"; do
  output_dir="$ROOT_DIR/cv/rendercv_output/$variant"
  mkdir -p "$output_dir"
  find "$output_dir" -mindepth 1 -maxdepth 1 -exec rm -rf {} +

  "$RENDERCV_BIN" render "${input_files[$variant]}" \
    --design "$DESIGN_FILE" \
    --locale-catalog "$LOCALE_FILE" \
    --settings "$SETTINGS_FILE" \
    --output-folder "$output_dir"

  source_pdf="$output_dir/Jesús_Erro_Iribarren_CV.pdf"
  target_pdf="$all_output_dir/Jesús_Erro_Iribarren_CV_${variant}.pdf"
  cp "$source_pdf" "$target_pdf"
done
