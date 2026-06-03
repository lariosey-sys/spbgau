from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = ROOT.parent
LATEX_DIR = ROOT / "latex"
PREAMBLE = LATEX_DIR / "preamble.tex"
TITLE_PAGE = LATEX_DIR / "title_page.tex"
BUILD_DIR = ROOT / "build"
DIPLOMA_BUILDS_DIR = ROOT / "diploma_builds"
OUTPUT_BASENAME = "ВКР"
LEGACY_OUTPUT_BASENAME = "ВКР_латех"

CONTENT_FILES = [
    "abbreviations.md",
    "introduction.md",
    "chapter_01_literature_review.md",
    "chapter_02_system_design.md",
    "chapter_03_implementation_testing.md",
    "conclusion.md",
]


def ensure_tool(name: str) -> str:
    tool = shutil.which(name)
    if not tool:
        raise RuntimeError(f"Не найден инструмент `{name}`.")
    return tool


def next_version_number() -> int:
    DIPLOMA_BUILDS_DIR.mkdir(parents=True, exist_ok=True)
    patterns = [
        (DIPLOMA_BUILDS_DIR, re.compile(rf"^{re.escape(OUTPUT_BASENAME)}-(\d+)\.(?:tex|pdf)$")),
        (BUILD_DIR, re.compile(rf"^(\d+)_{re.escape(LEGACY_OUTPUT_BASENAME)}\.(?:tex|pdf)$")),
    ]
    max_version = 0
    for directory, pattern in patterns:
        if not directory.exists():
            continue
        for path in directory.iterdir():
            match = pattern.match(path.name)
            if match:
                max_version = max(max_version, int(match.group(1)))
    return max_version + 1


def versioned_output(version: int, suffix: str) -> Path:
    DIPLOMA_BUILDS_DIR.mkdir(parents=True, exist_ok=True)
    return DIPLOMA_BUILDS_DIR / f"{OUTPUT_BASENAME}-{version}{suffix}"


def run(command: list[str], *, cwd: Path = ROOT) -> None:
    subprocess.run(command, check=True, cwd=str(cwd))


def build_numbered_markdown() -> None:
    run(["bash", "build_numbered_draft.sh"])


def apply_citation_replacements(text: str) -> str:
    table = PROJECT_ROOT / "literature" / "citation_replacement_table.md"
    if not table.exists():
        return text
    for line in table.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        source = cells[0].strip("`")
        target = cells[1].strip("`")
        if source.startswith("["):
            text = text.replace(source, target)
    return text


def strip_heading(text: str) -> str:
    lines = text.strip().splitlines()
    if lines and lines[0].startswith("# "):
        return "\n".join(lines[1:]).strip()
    return text.strip()


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def normalize_chapter_heading(text: str) -> str:
    replacements = {
        "# Глава 1. Аналитический обзор систем интеллектуального управления микроклиматом теплицы":
            "# 1 Аналитический обзор систем интеллектуального управления микроклиматом теплицы",
        "# Глава 2. Проектирование программно-аппаратной системы мониторинга и управления микроклиматом теплицы":
            "# 2 Проектирование программно-аппаратной системы мониторинга и управления микроклиматом теплицы",
        "# Глава 2. Проектирование расширяемой IoT/ML-платформы управления микроклиматом теплицы":
            "# 2 Проектирование расширяемой IoT/ML-платформы управления микроклиматом теплицы",
        "# Глава 3. Реализация и проверка программно-аппаратной системы":
            "# 3 Реализация и проверка программно-аппаратной системы",
        "# Глава 3. Реализация, опытное внедрение и анализ данных платформы":
            "# 3 Реализация, опытное внедрение и анализ данных платформы",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    text = re.sub(r"(?m)^##\s+(\d+\.\d+)\.\s+", r"## \1 ", text)
    text = re.sub(r"(?m)^###\s+(\d+\.\d+\.\d+)\.\s+", r"### \1 ", text)
    return text


def references_markdown() -> str:
    source = PROJECT_ROOT / "literature" / "references_numbered.md"
    text = strip_heading(read_source(source))
    text = re.sub(
        r"(?s)^Это рабочая версия списка литературы.*?\n\n",
        "",
        text,
        count=1,
    )
    return "# СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ\n\n" + text.strip() + "\n"


def appendices_markdown() -> str:
    text = strip_heading(read_source(ROOT / "appendices_draft.md"))
    text = re.sub(
        r"(?s)^Этот файл содержит готовые заготовки приложений.*?\n\n",
        "",
        text,
        count=1,
    )
    text = re.sub(r"(?m)^##\s+Приложение\s+([А-Я])\.\s*(.*)$", r"# ПРИЛОЖЕНИЕ \1 \2", text)
    return text.strip() + "\n"


def count_sources() -> int:
    return len(re.findall(r"(?m)^\d+\.\s", references_markdown()))


def count_figures(text: str) -> int:
    return len(re.findall(r"!\[[^\]]*\]\([^)]+\)", text))


def count_tables(text: str) -> int:
    return len(re.findall(r"(?m)^\|(?:\s*:?-+:?\s*\|)+\s*$", text))


def abstract_markdown(figures: int, tables: int, sources: int) -> str:
    text = strip_heading(read_source(ROOT / "abstract.md"))
    lead = (
        f"Работа содержит \\pageref{{LastPage}} с., {figures} рис., "
        f"{tables} табл., {sources} источн.\n\n"
    )
    return "# РЕФЕРАТ\n\n" + lead + text.strip() + "\n"


def body_markdown() -> str:
    chunks: list[str] = []
    for filename in CONTENT_FILES:
        chunks.append(normalize_chapter_heading(read_source(ROOT / filename).strip()))
    chunks.append(references_markdown())
    text = "\n\n".join(chunks).strip() + "\n"
    return apply_citation_replacements(text)


def preprocess_markdown(text: str) -> str:
    text = text.replace("CO2", r"CO$_2$")
    text = re.sub(r"URL:\s*(https?://[^\s)]+)", r"URL: <\1>", text)
    return text


def run_pandoc(markdown_path: Path, tex_path: Path) -> None:
    pandoc = ensure_tool("pandoc")
    command = [
        pandoc,
        str(markdown_path),
        "--from",
        "markdown+pipe_tables+raw_tex+tex_math_dollars+implicit_figures",
        "--to",
        "latex",
        "--resource-path",
        str(ROOT),
        "--syntax-highlighting=none",
        "--output",
        str(tex_path),
    ]
    run(command)


def replace_structural_sections(tex: str) -> str:
    structural_sections = [
        (r"РЕФЕРАТ", "РЕФЕРАТ", "VkrStructuralSectionNoToc"),
        (r"Список сокращений и обозначений", "ПЕРЕЧЕНЬ СОКРАЩЕНИЙ И ОБОЗНАЧЕНИЙ", "VkrStructuralSection"),
        (r"Введение", "ВВЕДЕНИЕ", "VkrStructuralSection"),
        (r"Заключение", "ЗАКЛЮЧЕНИЕ", "VkrStructuralSection"),
        (r"СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ", "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ", "VkrStructuralSection"),
    ]
    for source, title, macro in structural_sections:
        source_pattern = r"\s+".join(re.escape(part) for part in source.split())
        tex = re.sub(
            rf"\\section\{{{source_pattern}\}}(?P<label>\\label\{{[^}}]+\}})?",
            lambda match: f"\\{macro}{{{title}}}" + (match.group("label") or ""),
            tex,
            count=1,
            flags=re.DOTALL,
        )
    tex = re.sub(
        r"\\section\{ПРИЛОЖЕНИЕ\s+([А-Я])\s+([^}]*)\}(?P<label>\\label\{[^}]+\})?",
        lambda match: f"\\VkrAppendixSection{{{match.group(1)}}}{{{match.group(2).strip()}}}"
        + (match.group("label") or ""),
        tex,
    )
    return tex


def normalize_enumeration_labels(tex: str) -> str:
    tex = tex.replace(
        r"\def\labelenumi{\arabic{enumi}.}",
        r"\def\labelenumi{\arabic{enumi})}",
    )
    pattern = re.compile(
        r"(\\VkrStructuralSection\{СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ\}.*?"
        r"\\def\\labelenumi\{\\arabic\{enumi\}\)\})",
        flags=re.DOTALL,
    )
    return pattern.sub(
        lambda match: match.group(1).replace(
            r"\def\labelenumi{\arabic{enumi})}",
            r"\def\labelenumi{\arabic{enumi}.}",
        ),
        tex,
        count=1,
    )


def normalize_tables(tex: str) -> str:
    replacements = {
        r"\toprule\noalign{}": r"\hline",
        r"\midrule\noalign{}": r"\hline",
        r"\bottomrule\noalign{}": r"\hline",
        r"\raggedright": r"\RaggedRight",
        r"\raggedleft": r"\Centering",
    }
    for source, target in replacements.items():
        tex = tex.replace(source, target)
    return tex


def postprocess_tex(tex: str) -> str:
    tex = replace_structural_sections(tex)
    tex = normalize_enumeration_labels(tex)
    tex = normalize_tables(tex)
    return tex


def build_main_tex(abstract_tex: str, body_tex: str) -> str:
    preamble = PREAMBLE.read_text(encoding="utf-8")
    title_page = TITLE_PAGE.read_text(encoding="utf-8")
    return "\n".join(
        [
            preamble,
            "",
            r"\begin{document}",
            r"\hypersetup{pageanchor=false}",
            title_page,
            r"\setcounter{page}{2}",
            r"\hypersetup{pageanchor=true}",
            "",
            abstract_tex,
            r"\clearpage",
            "",
            r"\VkrStructuralSectionNoToc{СОДЕРЖАНИЕ}",
            r"\makeatletter\@starttoc{toc}\makeatother",
            r"\clearpage",
            "",
            body_tex,
            "",
            r"\end{document}",
            "",
        ]
    )


def run_tectonic(tex_path: Path) -> Path:
    tectonic = ensure_tool("tectonic")
    run([tectonic, "--outdir", str(DIPLOMA_BUILDS_DIR), str(tex_path)])
    return DIPLOMA_BUILDS_DIR / f"{tex_path.stem}.pdf"


def build() -> tuple[Path, Path]:
    build_numbered_markdown()
    body_md = body_markdown()
    figures = count_figures(body_md)
    tables = count_tables(body_md)
    sources = count_sources()
    abstract_md = apply_citation_replacements(abstract_markdown(figures, tables, sources))

    version = next_version_number()
    tex_output = versioned_output(version, ".tex")
    pdf_output = tex_output.with_suffix(".pdf")

    with tempfile.TemporaryDirectory(prefix="spbgau_vkr_latex_") as temp_dir:
        temp_path = Path(temp_dir)
        abstract_md_path = temp_path / "abstract.md"
        body_md_path = temp_path / "body.md"
        abstract_tex_path = temp_path / "abstract.tex"
        body_tex_path = temp_path / "body.tex"
        abstract_md_path.write_text(preprocess_markdown(abstract_md), encoding="utf-8")
        body_md_path.write_text(preprocess_markdown(body_md), encoding="utf-8")
        run_pandoc(abstract_md_path, abstract_tex_path)
        run_pandoc(body_md_path, body_tex_path)
        abstract_tex = postprocess_tex(abstract_tex_path.read_text(encoding="utf-8"))
        body_tex = postprocess_tex(body_tex_path.read_text(encoding="utf-8"))
        tex_output.write_text(build_main_tex(abstract_tex, body_tex), encoding="utf-8")
        built_pdf = run_tectonic(tex_output)
        if built_pdf != pdf_output:
            built_pdf.replace(pdf_output)

    current_tex = ROOT / "assembled_draft_numbered.tex"
    current_pdf = ROOT / "assembled_draft_numbered.pdf"
    shutil.copy2(tex_output, current_tex)
    shutil.copy2(pdf_output, current_pdf)
    return tex_output, pdf_output


def main() -> None:
    tex_path, pdf_path = build()
    print(f"LaTeX source: {tex_path}")
    print(f"PDF output:   {pdf_path}")
    print(f"Current TeX:  {ROOT / 'assembled_draft_numbered.tex'}")
    print(f"Current PDF:  {ROOT / 'assembled_draft_numbered.pdf'}")


if __name__ == "__main__":
    main()
