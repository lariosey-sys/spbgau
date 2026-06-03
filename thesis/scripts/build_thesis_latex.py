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
    # Версия определяется только по уже существующим V-файлам в diploma_builds:
    # ВКР-V1, ВКР-V2, ВКР-V3, ... Следующая сборка получает максимум + 1.
    DIPLOMA_BUILDS_DIR.mkdir(parents=True, exist_ok=True)
    pattern = re.compile(rf"^{re.escape(OUTPUT_BASENAME)}-V(\d+)\.(?:tex|pdf)$")
    max_version = 0
    for path in DIPLOMA_BUILDS_DIR.iterdir():
        match = pattern.match(path.name)
        if match:
            max_version = max(max_version, int(match.group(1)))
    return max_version + 1


def versioned_output(version: int, suffix: str) -> Path:
    DIPLOMA_BUILDS_DIR.mkdir(parents=True, exist_ok=True)
    return DIPLOMA_BUILDS_DIR / f"{OUTPUT_BASENAME}-V{version}{suffix}"


def run(command: list[str], *, cwd: Path = ROOT) -> None:
    subprocess.run(command, check=True, cwd=str(cwd))


def build_numbered_markdown() -> None:
    run(["bash", "build_numbered_draft.sh"])


def load_citation_key_map() -> dict[str, int]:
    """Карта citation key -> номер источника из literature/citation_number_map.md."""
    mapping: dict[str, int] = {}
    source = PROJECT_ROOT / "literature" / "citation_number_map.md"
    if not source.exists():
        return mapping
    row = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*(\d+)\s*\|")
    for line in source.read_text(encoding="utf-8").splitlines():
        match = row.match(line)
        if match:
            mapping[match.group(1)] = int(match.group(2))
    return mapping


# Группа цитирования: [key] или [key1; key2; ...]. Шаблон ключа намеренно
# широкий (латиница/цифры/подчеркивание, год не обязателен - например,
# vanharisov_cyberleninka); реальная проверка - членство в карте ключей,
# незнакомые скобочные конструкции остаются нетронутыми.
_CITATION_KEY = r"[A-Za-z][A-Za-z0-9_]{3,}"
_CITATION_GROUP = re.compile(
    r"\[\s*(" + _CITATION_KEY + r"(?:\s*;\s*" + _CITATION_KEY + r")*)\s*\]"
)


def apply_citation_replacements(text: str) -> str:
    """Заменяет служебные citation keys на нумерованные ссылки ГОСТ: [9, 10, 11].

    Работает по отдельным ключам, поэтому корректно обрабатывает любые группы
    `[k1; k2; k3]`, а не только заранее перечисленные комбинации.
    """
    key_map = load_citation_key_map()
    if not key_map:
        return text

    def repl(match: re.Match) -> str:
        keys = [k.strip() for k in match.group(1).split(";")]
        numbers: list[int] = []
        for key in keys:
            if key not in key_map:
                # Неизвестный ключ оставляем как есть, чтобы заметить при вычитке.
                return match.group(0)
            numbers.append(key_map[key])
        return "[" + ", ".join(str(n) for n in numbers) + "]"

    return _CITATION_GROUP.sub(repl, text)


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
    chunks.append(appendices_markdown())
    text = "\n\n".join(chunks).strip() + "\n"
    return apply_citation_replacements(text)


def preprocess_markdown(text: str) -> str:
    text = text.replace("CO2", r"CO$_2$")
    text = re.sub(r"URL:\s*(https?://[^\s)]+)", r"URL: <\1>", text)
    # DOI делаем кликабельной ссылкой на doi.org (отображается сам DOI).
    text = re.sub(
        r"DOI:\s*(10\.\d{4,}/[^\s]+?)\.(?=\s|$)",
        r"DOI: [\1](https://doi.org/\1).",
        text,
    )
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
        "--no-highlight",
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


_COLSPEC_TOKEN = re.compile(
    r"(?:>\{(?:[^{}]|\{[^{}]*\})*\}\s*)?"  # необязательный префикс >{...}
    r"(?:[plcrm]\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}|[lcr])",  # p{...} или l/c/r
    re.S,
)


def _grid_colspec(spec: str) -> str:
    """Добавляет вертикальные линии ГОСТ-таблицы в спецификацию колонок."""
    spec = spec.strip()
    if spec.startswith("@{}"):
        spec = spec[3:]
    if spec.endswith("@{}"):
        spec = spec[:-3]
    cols = _COLSPEC_TOKEN.findall(spec)
    if not cols:
        return spec
    return "|" + "|".join(c.strip() for c in cols) + "|"


def convert_longtables(tex: str) -> str:
    """Преобразует pandoc longtable в неразрывную среду vkrlongtab и придает
    таблицам закрытый ГОСТ-вид: вертикальные границы по бокам и между всеми
    колонками, горизонтальные линии (\\hline) вместо открытых booktabs-линеек,
    разделители между строками."""
    tex = re.sub(r"\\begin\{longtable\}\[[^\]]*\]", r"\\begin{vkrlongtab}", tex)
    tex = tex.replace(r"\begin{longtable}", r"\begin{vkrlongtab}")
    tex = tex.replace(r"\end{longtable}", r"\end{vkrlongtab}")
    tex = re.sub(r"(?m)^\s*\\end(?:firsthead|head|lastfoot|foot)\s*$", "", tex)

    def rework(match: re.Match) -> str:
        body = match.group(2)
        # спецификация колонок: первая брейс-группа после \begin{vkrlongtab}
        spec_match = re.match(r"\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}", body, re.S)
        if spec_match:
            spec = _grid_colspec(spec_match.group(1))
            body = "{" + spec + "}" + body[spec_match.end():]
        body = body.replace(r"\toprule", r"\hline")
        body = body.replace(r"\midrule", r"\hline")
        body = body.replace(r"\bottomrule", r"\hline")
        # разделитель после каждой строки, если за ней еще нет \hline
        body = re.sub(r"(\\\\\n)(?!\s*\\hline)", r"\1\\hline\n", body)
        # шапка таблицы (между первой и второй \hline) - полужирным
        parts = body.split(r"\hline", 2)
        if len(parts) == 3:
            head = parts[1]
            if r"\begin{minipage}" in head:
                head = head.replace("\\RaggedRight\n", "\\RaggedRight\\bfseries\n")
                head = head.replace("\\Centering\n", "\\Centering\\bfseries\n")
            else:
                # плоская строка заголовка: A & B & C \\
                head = re.sub(
                    r"^(\s*)(.+?)(\s*\\\\)",
                    lambda m: m.group(1)
                    + " & ".join(
                        "\\textbf{" + c.strip() + "}" for c in m.group(2).split("&")
                    )
                    + m.group(3),
                    head,
                    count=1,
                    flags=re.S,
                )
            body = parts[0] + r"\hline" + head + r"\hline" + parts[2]
        return match.group(1) + body + match.group(3)

    return re.sub(
        r"(\\begin\{vkrlongtab\})(.*?)(\\end\{vkrlongtab\})",
        rework,
        tex,
        flags=re.S,
    )


def constrain_graphics(tex: str) -> str:
    """Ограничивает размер каждой иллюстрации половиной страницы.

    pandoc выводит \\includegraphics без размеров, из-за чего фотографии с большим
    разрешением переполняют страницу. Проставляем width/height с keepaspectratio.
    """
    return re.sub(
        r"\\includegraphics\{",
        r"\\includegraphics[width=0.7\\linewidth,"
        r"height=0.44\\textheight,keepaspectratio]{",
        tex,
    )


def keep_listings_together(tex: str) -> str:
    """Не дает листингам (verbatim) разрываться между страницами: оборачивает
    каждый блок в неразрывный minipage. Короткие листинги ВКР целиком переходят
    на следующую страницу, если не помещаются, вместо некрасивого разрыва."""
    # \begin{verbatim}/\end{verbatim} (fancyvrb) должны стоять на отдельных
    # строках, поэтому обертку minipage отделяем переводами строки. Снаружи -
    # явные отступы 8 pt, чтобы листинг не сливался с текстом; внутри topsep
    # уменьшен, чтобы рамка не отъезжала от подписи.
    return re.sub(
        r"\\begin\{verbatim\}.*?\\end\{verbatim\}",
        lambda m: "\\par\\vspace{8pt}\\noindent\\begin{minipage}{\\linewidth}\n"
        "\\setlength{\\topsep}{3pt}\\setlength{\\partopsep}{0pt}\n"
        + m.group(0)
        + "\n\\end{minipage}\\par\\vspace{8pt}",
        tex,
        flags=re.DOTALL,
    )


def tighten_equations(tex: str) -> str:
    """Один отступ над формулой и под ней (текст - отступ - формула).

    pandoc отделяет формулу пустой строкой, из-за чего она начинает новый абзац
    и над ней появляется лишняя пустая строка поверх \\abovedisplayskip (двойной
    отступ). Присоединяем формулу к предыдущему абзацу. Пояснение «где ...» по
    ГОСТ начинается без абзацного отступа - продолжаем им тот же абзац."""
    tex = re.sub(r"\n\n+(\\begin\{equation\})", r"\n\1", tex)
    tex = re.sub(r"(\\end\{equation\})\n\n+(где )", r"\1\n\2", tex)
    return tex


def bind_listing_captions(tex: str) -> str:
    """Привязывает подпись «Листинг N – …» к листингу: оба в одном неразрывном
    minipage, подпись кеглем 12 пт, между подписью и рамкой - запрет разрыва."""
    return re.sub(
        r"(?m)^(Листинг[ ~]\d[^\n]*(?:\n[^\n]+)*?)\n\n"
        r"\\par\\vspace\{8pt\}\\noindent\\begin\{minipage\}\{\\linewidth\}",
        r"\\par\\vspace{10pt}\\noindent\\begin{minipage}{\\linewidth}\n"
        r"\\setlength{\\parindent}{1.5cm}{\\small \1\\par}\\nopagebreak",
        tex,
    )


def bind_table_captions(tex: str) -> str:
    """Привязывает подпись «Таблица N – …» к таблице: оба оборачиваются в один
    неразрывный minipage, поэтому подпись не может остаться на одной странице,
    а таблица уехать на другую - блок целиком переносится при нехватке места."""
    return re.sub(
        r"(?m)^(Таблица[ ~]\d[^\n]*(?:\n[^\n]+)*?)\n\n(\\begin\{vkrlongtab\}.*?\\end\{vkrlongtab\})",
        r"\\par\\vspace{10pt}\\noindent\\begin{minipage}{\\linewidth}\n"
        r"\\setlength{\\parindent}{1.5cm}{\\small \1\\par}\\nopagebreak\n\2\n"
        r"\\end{minipage}\\par\\vspace{10pt}",
        tex,
        flags=re.S,
    )


def pin_figures(tex: str) -> str:
    """Фиксирует рисунки по месту (`[H]`), чтобы подписи не отрывались от
    иллюстраций и порядок рисунков совпадал с порядком ссылок в тексте."""
    return tex.replace(r"\begin{figure}", r"\begin{figure}[H]")


def postprocess_tex(tex: str) -> str:
    tex = replace_structural_sections(tex)
    tex = normalize_enumeration_labels(tex)
    tex = normalize_tables(tex)
    tex = convert_longtables(tex)
    tex = constrain_graphics(tex)
    tex = pin_figures(tex)
    tex = keep_listings_together(tex)
    tex = bind_listing_captions(tex)
    tex = bind_table_captions(tex)
    tex = tighten_equations(tex)
    return tex


# Временно отключено до получения точных данных титульного листа (факультет,
# кафедра, направление, руководитель). Вернуть в True, когда титул будет готов.
INCLUDE_TITLE_PAGE = False


def build_main_tex(abstract_tex: str, body_tex: str) -> str:
    preamble = PREAMBLE.read_text(encoding="utf-8")
    front_matter: list[str] = []
    if INCLUDE_TITLE_PAGE:
        title_page = TITLE_PAGE.read_text(encoding="utf-8")
        front_matter = [
            r"\hypersetup{pageanchor=false}",
            title_page,
            r"\setcounter{page}{2}",
            r"\hypersetup{pageanchor=true}",
        ]
    return "\n".join(
        [
            preamble,
            "",
            r"\begin{document}",
            *front_matter,
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


def fix_pdf_text_layer(pdf_path: Path) -> None:
    """Чинит текстовый слой PDF: шрифт Times New Roman использует один глиф для
    «;» и греческого знака вопроса (U+037E), и xdvipdfmx прописывает в ToUnicode
    именно U+037E. Визуально PDF корректен, но копирование/извлечение текста
    дает нестандартный символ. Заменяем отображение на обычную «;» (U+003B).
    Требует pikepdf; при его отсутствии шаг пропускается с предупреждением."""
    try:
        import pikepdf
    except ImportError:
        print("ПРЕДУПРЕЖДЕНИЕ: pikepdf не установлен - текстовый слой PDF "
              "не исправлен (U+037E вместо ';' при копировании).")
        return
    fixed = 0
    with pikepdf.open(str(pdf_path), allow_overwriting_input=True) as pdf:
        for obj in pdf.objects:
            try:
                if not isinstance(obj, pikepdf.Stream):
                    continue
                data = obj.read_bytes()
                if b"beginbfchar" not in data and b"beginbfrange" not in data:
                    continue
                if b"<037E>" in data:
                    obj.write(data.replace(b"<037E>", b"<003B>"))
                    fixed += 1
            except Exception:
                continue
        if fixed:
            pdf.save(str(pdf_path))
    if fixed:
        print(f"Текстовый слой PDF исправлен: {fixed} ToUnicode-карт(ы), ';' вместо U+037E.")


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
        fix_pdf_text_layer(built_pdf)
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
