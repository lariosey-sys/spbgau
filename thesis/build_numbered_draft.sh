#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

bash ./build_assembled_draft.sh >/dev/null

src="assembled_draft.md"
out="assembled_draft_numbered.md"
tmp="${out}.tmp"

cp "$src" "$tmp"

while IFS='|' read -r _ raw_from raw_to _; do
  from="$(printf '%s' "$raw_from" | sed 's/^ *//; s/ *$//; s/^`//; s/`$//')"
  to="$(printf '%s' "$raw_to" | sed 's/^ *//; s/ *$//; s/^`//; s/`$//')"

  case "$from" in
    \[*\])
      FROM="$from" TO="$to" perl -0pi -e 's/\Q$ENV{FROM}\E/$ENV{TO}/g' "$tmp"
      ;;
  esac
done < ../literature/citation_replacement_table.md

{
  printf '> Версия с нумерованными ссылками. Файл генерируется скриптом `thesis/build_numbered_draft.sh`; править лучше исходные части и таблицу замен.\n\n'
  sed '1{/^# /!q;}' "$tmp"
} > "${tmp}.with-note"

mv "${tmp}.with-note" "$out"
rm -f "$tmp"

printf 'Built %s\n' "$out"
