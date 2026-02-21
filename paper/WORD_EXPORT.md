# Word Export (LaTeX → DOCX)

This workflow generates a Word (`.docx`) file from the LaTeX paper, preserving section alignment, figures, tables, and math as closely as possible.

## Prerequisites
- Python 3.9+ on PATH (`python --version`)
- Pandoc installed and on PATH: https://pandoc.org/installing.html
- Internet access (for the IEEE CSL style URL). If offline, download `ieee.csl` and replace the URL in `word_export.bat` with the local path.

## How to Export
- Double-click `word_export.bat` in the `paper` folder, or run:

```
cd paper
word_export.bat
```

This will:
1. Preprocess `fracturedetect_ai_paper.tex` into `fracturedetect_ai_paper_word.tex` (replacing the custom `\napkinimage` macro with `\includegraphics`).
2. Convert the result to `fracturedetect_ai_paper.docx` using Pandoc with IEEE-style citations and the bibliography `references.bib`.
3. If `reference.docx` exists in the `paper` folder, Pandoc will use it to apply consistent Word styles (headings, captions, normal text).

## Notes
- Image cropping options (`clip, trim`) used in LaTeX are not supported by Word; the preprocessor keeps explicit `width=...` sizing for consistent layout.
- Equations are preserved as readable math; complex LaTeX constructs may render as inline text if they are outside math environments.
- Tables and section headings map to Word styles; you can adjust styles in Word to fine-tune spacing.
- If citations or bibliography don’t format correctly, ensure network access for the CSL style or specify a local `ieee.csl` file.

## Troubleshooting
- "command not found" for Pandoc: install and add to PATH, then reopen the terminal.
- Missing images: confirm files exist under `paper/figures/` and LaTeX references match their filenames.
- Want tighter control of Word styles: provide a Word template (`reference.docx`) and add `--reference-doc=reference.docx` to `word_export.bat`.

## Preserving Format When Replacing Images in Word
- Use "In line with text" wrapping: prevents layout shifts compared to "Square" or "Tight".
- Keep aspect ratio locked: resize via corner handles so width/height scale together.
- Match sizes used in LaTeX: most figures export at `~0.45–0.6 \textwidth`; in Word, set exact width (e.g., 12–14 cm) for consistency.
- Avoid auto-fitting tables: right-click table → Table Properties → uncheck "Automatically resize to fit contents".
- Use the Reference DOCX: set desired styles in `reference.docx` (Heading 1–3, Caption, Normal), then re-run `word_export.bat` for stable spacing.