#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

out="assembled_draft.md"
tmp="${out}.tmp"

{
  printf '# Разработка и внедрение интеллектуальной системы управления микроклиматом в теплице на основе машинного обучения\n\n'
  printf '> Рабочий собранный Markdown-черновик. Файл генерируется скриптом `thesis/build_assembled_draft.sh`; править лучше исходные части, а не этот файл.\n\n'

  printf '## Содержание\n\n'
  printf '1. Аннотация\n'
  printf '2. Список сокращений и обозначений\n'
  printf '3. Введение\n'
  printf '4. Глава 1. Аналитический обзор систем интеллектуального управления микроклиматом теплицы\n'
  printf '5. Глава 2. Проектирование расширяемой IoT/ML-платформы управления микроклиматом теплицы\n'
  printf '6. Глава 3. Реализация, опытное внедрение и анализ данных платформы\n'
  printf '7. Заключение\n'
  printf '8. Список литературы\n\n'

  for file in \
    abstract.md \
    abbreviations.md \
    introduction.md \
    chapter_01_literature_review.md \
    chapter_02_system_design.md \
    chapter_03_implementation_testing.md \
    conclusion.md
  do
    printf '\n\n'
    sed 's/\r$//' "$file"
  done

  printf '\n\n# Список литературы\n\n'
  sed '1{/^# /d;}' ../literature/references_numbered.md
} > "$tmp"

mv "$tmp" "$out"
printf 'Built %s\n' "$out"
