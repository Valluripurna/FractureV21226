from docx import Document
from docx.shared import Pt, Inches, RGBColor, Mm
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_style_font(style, name: str, size_pt: int, bold: bool = False, italic: bool = False, color_rgb=(0,0,0)):
    font = style.font
    font.name = name
    font.size = Pt(size_pt)
    font.bold = bold
    font.italic = italic
    r, g, b = color_rgb
    font.color.rgb = RGBColor(r, g, b)

def ensure_style(doc: Document, style_name: str, base_type=WD_STYLE_TYPE.PARAGRAPH):
    try:
        return doc.styles[style_name]
    except KeyError:
        return doc.styles.add_style(style_name, base_type)

def set_two_columns(section, space_pts: int = 18):
    # Add <w:cols w:num='2' w:space='...'> to section properties for two columns
    sectPr = section._sectPr
    cols = sectPr.find(qn('w:cols'))
    if cols is None:
        cols = OxmlElement('w:cols')
        sectPr.append(cols)
    cols.set(qn('w:num'), '2')
    cols.set(qn('w:space'), str(space_pts))

def set_margins(section, top_in=0.75, bottom_in=0.75, left_in=0.75, right_in=0.75):
    # Set page margins in inches per IEEE spec
    section.top_margin = Inches(top_in)
    section.bottom_margin = Inches(bottom_in)
    section.left_margin = Inches(left_in)
    section.right_margin = Inches(right_in)

def main():
    doc = Document()

    # Global styles (IEEE-like)
    normal = doc.styles['Normal']
    set_style_font(normal, 'Times New Roman', 10, color_rgb=(0,0,0))
    # Body text first-line indent per IEEE requirement
    if normal.type == WD_STYLE_TYPE.PARAGRAPH:
        pf = normal.paragraph_format
        pf.first_line_indent = Inches(0.25)
        pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Heading styles map to sections/subsections
    h1 = doc.styles['Heading 1']
    set_style_font(h1, 'Times New Roman', 10, bold=True, color_rgb=(0,0,0))
    h2 = doc.styles['Heading 2']
    set_style_font(h2, 'Times New Roman', 10, bold=True, color_rgb=(0,0,0))
    h3 = doc.styles['Heading 3']
    set_style_font(h3, 'Times New Roman', 10, bold=True, color_rgb=(0,0,0))

    # Title style for the paper title
    try:
        title_style = doc.styles['Title']
    except KeyError:
        title_style = doc.styles.add_style('Title', WD_STYLE_TYPE.PARAGRAPH)
    set_style_font(title_style, 'Times New Roman', 24, bold=True, color_rgb=(0,0,0))
    if title_style.type == WD_STYLE_TYPE.PARAGRAPH:
        pf = title_style.paragraph_format
        pf.space_before = Pt(0)
        pf.space_after = Pt(12)
        pf.alignment = WD_ALIGN_PARAGRAPH.CENTER

    caption = ensure_style(doc, 'Caption', WD_STYLE_TYPE.PARAGRAPH)
    set_style_font(caption, 'Times New Roman', 9, italic=False, color_rgb=(0,0,0))

    # Author/Affiliation styles
    author_style = ensure_style(doc, 'AuthorName', WD_STYLE_TYPE.PARAGRAPH)
    set_style_font(author_style, 'Times New Roman', 11, bold=False, italic=False, color_rgb=(0,0,0))
    aff_style = ensure_style(doc, 'Affiliation', WD_STYLE_TYPE.PARAGRAPH)
    set_style_font(aff_style, 'Times New Roman', 10, bold=False, italic=False, color_rgb=(0,0,0))

    # Reduce default spacing: single line, no extra space before/after
    for style in [normal, h1, h2, h3, title_style, caption, author_style, aff_style]:
        if style.type == WD_STYLE_TYPE.PARAGRAPH:
            pf = style.paragraph_format
            pf.space_before = Pt(0)
            pf.space_after = Pt(0)
            pf.line_spacing = Pt(12)  # ~ single
    # Heading spacing per IEEE
    for style in [h1, h2]:
        pf = style.paragraph_format
        pf.space_before = Pt(12)
        pf.space_after = Pt(6)
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # Sections: First section single column (title/abstract), body two columns
    # First section already exists; insert a section break for body
    # Note: python-docx doesn't expose explicit section breaks via API; we set two columns on the first section
    # so Pandoc output will inherit two columns when applying the reference doc.
    # Set A4 page size and margins; two columns with 0.25 in spacing (later sections will split)
    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    set_margins(section, top_in=0.75, bottom_in=0.75, left_in=0.75, right_in=0.75)
    # Column spacing: 0.25 in ≈ 18 pt
    set_two_columns(section, space_pts=18)

    # Provide hints paragraph so the file isn't empty
    p = doc.add_paragraph('IEEE Reference Template applied. Use as --reference-doc for Pandoc.')
    p.style = title_style

    doc.save('reference.docx')
    print('Created reference.docx with IEEE-like styles (Times 10pt, two columns, Caption 9pt italic).')

if __name__ == '__main__':
    main()
