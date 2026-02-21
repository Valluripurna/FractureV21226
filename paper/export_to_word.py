import re
from pathlib import Path

SRC = Path(__file__).parent / "fracturedetect_ai_paper.tex"
OUT_TEX = Path(__file__).parent / "fracturedetect_ai_paper_word.tex"

def simplify_napkinimage(tex: str) -> str:
    # Replace \napkinimage[...]{file} with \includegraphics[width=...]{file}
    # Keep only width option; drop clip/trim to avoid Pandoc issues.
    pattern = re.compile(r"\\napkinimage(?:\[(?P<opts>[^\]]*)\])?\{(?P<file>[^\}]+)\}")

    def repl(m: re.Match) -> str:
        opts = m.group("opts") or ""
        width = None
        for part in [p.strip() for p in opts.split(",") if p.strip()]:
            if part.startswith("width="):
                width = part
                break
        opt_out = width if width else ""
        if opt_out:
            return f"\\includegraphics[{opt_out}]{{{m.group('file')}}}"
        return f"\\includegraphics{{{m.group('file')}}}"

    return pattern.sub(repl, tex)

def normalize_includegraphics_width(tex: str) -> str:
    # Ensure images without explicit width get a reasonable default
    pattern = re.compile(r"\\includegraphics(\[[^\]]*\])?\{([^}]+)\}")

    def has_width(opts: str) -> bool:
        return any(p.strip().startswith("width=") for p in opts.split(",") if p.strip())

    def repl(m: re.Match) -> str:
        opts = m.group(1) or ""
        fname = m.group(2)
        if opts and has_width(opts):
            return f"\\includegraphics{opts}{{{fname}}}"
        # Default to 0.6\textwidth to balance layout
        return f"\\includegraphics[width=0.6\\textwidth]{{{fname}}}"

    return pattern.sub(repl, tex)

def strip_unneeded_preamble(tex: str) -> str:
    # Pandoc focuses on document body; trim heavy class/packages to reduce conversion noise.
    # Keep \bibliography, figures, tables, math.
    # Remove the custom macro definition and grffile usage.
    tex = re.sub(r"\\newcommand\\napkinimage[\s\S]*?\n", "", tex)
    return tex

def normalize_math(tex: str) -> str:
    # Remove size commands like \Large inside align environments to help Pandoc parse math.
    def strip_large_in_align(match: re.Match) -> str:
        body = match.group(1)
        body = body.replace("\\Large", "")
        return f"\\begin{{align}}{body}\\end{{align}}"

    tex = re.sub(r"\\begin\{align\}([\s\S]*?)\\end\{align\}", strip_large_in_align, tex)
    return tex

def replace_centerline(tex: str) -> str:
    # Convert \centerline{...} to \centering ... to avoid brace issues
    def repl(m: re.Match) -> str:
        inner = m.group(1)
        return f"\\centering {inner}"

    return re.sub(r"\\centerline\{([\s\S]*?)\}", repl, tex)

def prefix_figures_path(tex: str) -> str:
    # Ensure includegraphics uses figures/ prefix when no path is present.
    # Matches \includegraphics[...]{name.ext} where name has no slash.
    pattern = re.compile(r"\\includegraphics(\[[^\]]*\])?\{(?P<file>[^\}]+)\}")

    def repl(m: re.Match) -> str:
        opts = m.group(1) or ""
        fname = m.group("file")
        # If already has a path separator, leave as is
        if "/" in fname or "\\" in fname:
            return f"\\includegraphics{opts}{{{fname}}}"
        return f"\\includegraphics{opts}{{figures/{fname}}}"

    return pattern.sub(repl, tex)

def main():
    src = SRC.read_text(encoding="utf-8")
    # Simplify image macro
    t = simplify_napkinimage(src)
    # Light preamble cleanup
    t = strip_unneeded_preamble(t)
    # Normalize math size commands inside align
    t = normalize_math(t)
    # Map centerline to center environment for consistent conversion
    t = replace_centerline(t)
    # Prefix figures path for image includes so Pandoc finds assets
    t = prefix_figures_path(t)
    # Ensure images without width get a default width
    t = normalize_includegraphics_width(t)
    # IEEE-specific textual formatting tweaks
    t = fix_abstract_label(t)
    t = fix_ieee_keywords(t)
    t = fix_section_headings(t)
    t = number_fig_captions(t)
    t = number_table_captions(t)
    OUT_TEX.write_text(t, encoding="utf-8")
    print(f"Prepared {OUT_TEX.name} for Pandoc conversion.")

def to_roman(num: int) -> str:
    vals = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
    res = []
    n = num
    for v, s in vals:
        while n >= v:
            res.append(s)
            n -= v
    return ''.join(res)

def fix_section_headings(tex: str) -> str:
    # Convert \section{Title} to IEEE style: I. TITLE (uppercase, roman numerals)
    sec_pattern = re.compile(r"\\section\{([^}]+)\}")
    counter = 0

    def repl(m: re.Match) -> str:
        nonlocal counter
        counter += 1
        title = m.group(1).strip().upper()
        return f"\\section{{{to_roman(counter)}. {title}}}"

    return sec_pattern.sub(repl, tex)

def fix_ieee_keywords(tex: str) -> str:
    # Replace IEEEkeywords env with a plain 'Keywords— ...' paragraph
    pattern = re.compile(r"\\begin\{IEEEkeywords\}([\s\S]*?)\\end\{IEEEkeywords\}")

    def repl(m: re.Match) -> str:
        content = ' '.join(line.strip() for line in m.group(1).splitlines()).strip()
        return f"\\noindent Keywords— {content}\n"

    return pattern.sub(repl, tex)

def fix_abstract_label(tex: str) -> str:
    # Prefix abstract with 'Abstract—' per IEEE style
    pattern = re.compile(r"\\begin\{abstract\}([\s\S]*?)\\end\{abstract\}")

    def repl(m: re.Match) -> str:
        body = m.group(1).strip()
        return f"\\noindent Abstract— {body}\n"

    return pattern.sub(repl, tex)

def number_fig_captions(tex: str) -> str:
    # Prefix figure captions with 'Fig n: '
    fig_pat = re.compile(r"(\\begin\{figure\}[\s\S]*?\\caption\{)([^}]*)(\}[\s\S]*?\\end\{figure\})")
    counter = 0

    def repl(m: re.Match) -> str:
        nonlocal counter
        counter += 1
        caption = m.group(2).strip()
        # Avoid double prefix if already starts with Fig.
        if caption.lower().startswith('fig'):
            new_cap = caption
        else:
            new_cap = f"Fig {counter}: {caption}"
        return f"{m.group(1)}{new_cap}{m.group(3)}"

    return fig_pat.sub(repl, tex)

def number_table_captions(tex: str) -> str:
    # Prefix table captions with 'Table n: '
    tab_pat = re.compile(r"(\\begin\{table\}[\s\S]*?\\caption\{)([^}]*)(\}[\s\S]*?\\end\{table\})")
    counter = 0

    def repl(m: re.Match) -> str:
        nonlocal counter
        counter += 1
        caption = m.group(2).strip()
        # Avoid double prefix
        if caption.lower().startswith('table'):
            new_cap = caption
        else:
            new_cap = f"Table {counter}: {caption}"
        return f"{m.group(1)}{new_cap}{m.group(3)}"

    return tab_pat.sub(repl, tex)

if __name__ == "__main__":
    main()
