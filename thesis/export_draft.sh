#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v pandoc >/dev/null 2>&1; then
  echo "pandoc is required for export" >&2
  exit 1
fi

bash ./build_numbered_draft.sh >/dev/null

src="assembled_draft_numbered.md"
docx="assembled_draft_numbered.docx"
html="assembled_draft_numbered.html"

pandoc "$src" \
  --from=gfm \
  --to=docx \
  --metadata=lang:ru-RU \
  --output="$docx"

pandoc "$src" \
  --from=gfm \
  --to=html5 \
  --standalone \
  --metadata=lang:ru-RU \
  --metadata=title:"Разработка и внедрение интеллектуальной системы управления микроклиматом в теплице" \
  --output="$html"

bash ./export_latex_pdf.sh >/dev/null

printf 'Built %s\n' "$docx"
printf 'Built %s\n' "$html"
printf 'Built %s\n' "assembled_draft_numbered.tex"
printf 'Built %s\n' "assembled_draft_numbered.pdf"
