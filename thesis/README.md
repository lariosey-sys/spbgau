# Черновик ВКР

Тема: разработка и внедрение интеллектуальной системы управления микроклиматом в теплице на основе машинного обучения.

## Основные файлы

| Файл | Назначение |
|---|---|
| `abstract.md` | реферат/аннотация для текущей ВКР |
| `abbreviations.md` | список сокращений и обозначений |
| `introduction.md` | черновик введения |
| `chapter_01_literature_review.md` | аналитический обзор литературы |
| `chapter_02_system_design.md` | проектирование системы |
| `chapter_03_implementation_testing.md` | реализация, проверка и подготовка ML-эксперимента |
| `conclusion.md` | черновик заключения |
| `draft_full.md` | сборочный файл и оглавление единого черновика |
| `technical_spec.md` | техническая спецификация реализации |
| `diagrams.md` | Mermaid-схемы архитектуры, MQTT, правил, БД и ML-пайплайна |
| `ml_experiment_plan.md` | план подготовки датасета и ML-эксперимента |
| `test_protocol.md` | протокол испытаний системы перед защитой |
| `collect_evidence.sh` | сценарий сбора логов, MQTT, SQL и CSV для доказательной базы |
| `traceability_matrix.md` | связь задач ВКР с главами, кодом и доказательствами |
| `quality_audit.md` | аудит готовности черновика и остаточные риски |
| `vkr_architectural_plan.md` | исследовательская рамка, новизна и архитектура ВКР |
| `vkr_execution_plan.md` | поэтапный план выполнения ВКР по образцу МИФИ |
| `work_progress.md` | живой трекер статусов, чеклистов и журнала изменений |
| `formatting_rules.md` | зафиксированные правила LaTeX/PDF-оформления по эталонному шаблону |
| `appendices_plan.md` | план приложений к ВКР |
| `appendices_draft.md` | готовые заготовки приложений |
| `evidence_checklist.md` | checklist фактических материалов для защиты |
| `evidence/README.md` | папка и инструкция для фактических материалов запуска |
| `reference_mifi_vkr/README.md` | только reference-пример оформления готовой ВКР МИФИ |
| `defense_speech.md` | черновик 7-10 минутного доклада для защиты |
| `presentation_outline.md` | структура презентации и материалы для слайдов |
| `defense_qna.md` | ожидаемые вопросы комиссии и короткие ответы |
| `defense_presentation.pptx` | рабочая PowerPoint-презентация для защиты на 12 слайдов |
| `build_assembled_draft.sh` | сборка единого Markdown-черновика |
| `assembled_draft.md` | генерируемый единый черновик после запуска сборки |
| `build_numbered_draft.sh` | сборка версии с нумерованными ссылками |
| `assembled_draft_numbered.md` | генерируемый черновик с замененными ссылками |
| `export_draft.sh` | экспорт нумерованного черновика в DOCX и HTML через pandoc |
| `export_latex_pdf.sh` | экспорт нумерованного черновика в LaTeX и PDF |
| `latex/` | LaTeX-преамбула и титульный лист текущей ВКР |
| `scripts/build_thesis_latex.py` | основной сборщик оформленной LaTeX/PDF-версии |
| `diploma_builds/` | архив версионированных сборок диплома в формате `ВКР-1.pdf`, `ВКР-2.pdf` и т.д. |
| `assembled_draft_numbered.tex` | генерируемый LaTeX-черновик |
| `assembled_draft_numbered.pdf` | генерируемый PDF-черновик |
| `assembled_draft_numbered.docx` | генерируемый DOCX-черновик |
| `assembled_draft_numbered.html` | генерируемый HTML-черновик |
| `source_to_chapters.md` | раскладка источников по разделам |
| `thesis_structure_plan.md` | рабочая структура всей ВКР |

## Рекомендуемый порядок сборки текста

1. `introduction.md`
2. `chapter_01_literature_review.md`
3. `chapter_02_system_design.md`
4. `chapter_03_implementation_testing.md`
5. `conclusion.md`
6. Список литературы из `../literature/references_numbered.md` или `../literature/references_gost_draft.md` после ручной вычитки.
7. Приложения из `appendices_draft.md`, дополненные скриншотами и фактическими MQTT/SQL-логами.

Перед основным текстом в сборку также входят `abstract.md` и `abbreviations.md`.

## Что еще нужно довести перед финальной версией

1. Привести стиль цитирования к требованиям кафедры, используя `literature/citation_number_map.md` и `literature/citation_replacement_table.md`.
2. Уточнить ГОСТ-описания источников в `literature/references_gost_draft.md`.
3. Добавить фактические скриншоты dashboard и примеры MQTT-сообщений при запуске оборудования.
4. После накопления данных добавить результаты ML-эксперимента или честно оставить его как подготовленный план.
5. Довести LaTeX/PDF-шаблон до требований кафедры.
6. Закрыть пункты из `evidence_checklist.md`, которые требуют запуска оборудования.
7. Выполнить `test_protocol.md`, запустить `collect_evidence.sh` и сохранить результаты для главы 3 и приложений.
8. Экспортировать схемы из `diagrams.md` в PNG/SVG для финального документа.
9. Проверить остаточные риски по `quality_audit.md`.
10. Заменить evidence-slots в `defense_presentation.pptx` фактическими скриншотами, MQTT-логами и SQL-строками после запуска оборудования.

## Сборка единого Markdown

```bash
cd thesis
bash build_assembled_draft.sh
```

Скрипт создает `assembled_draft.md` из введения, глав 1-3, заключения и нумерованного списка литературы. Исходные разделы остаются основным местом редактирования.

Для сборки версии с нумерованными ссылками:

```bash
cd thesis
bash build_numbered_draft.sh
```

Скрипт создает `assembled_draft_numbered.md`, применяя замены из `literature/citation_replacement_table.md`.

Основной формат работы по ВКР - LaTeX с прямой сборкой в PDF. Правила оформления зафиксированы в `formatting_rules.md`; за основу взят LaTeX-контур из соседнего репозитория `../vkr` и его последняя проверенная сборка `87_ВКР_латех.pdf`.

Для экспорта в LaTeX и PDF:

```bash
cd thesis
bash export_latex_pdf.sh
```

Скрипт требует `pandoc` и `tectonic`, создает новую версионированную сборку в `thesis/diploma_builds/` с именами вида `ВКР-1.pdf`, `ВКР-2.pdf`, `ВКР-3.pdf` и обновляет `assembled_draft_numbered.tex` и `assembled_draft_numbered.pdf` как последнюю актуальную версию.

Для полного экспорта в DOCX, HTML, LaTeX и PDF:

```bash
cd thesis
bash export_draft.sh
```

Скрипт требует установленные `pandoc` и `tectonic`, создает `assembled_draft_numbered.docx`, `assembled_draft_numbered.html`, `assembled_draft_numbered.tex` и `assembled_draft_numbered.pdf`.
