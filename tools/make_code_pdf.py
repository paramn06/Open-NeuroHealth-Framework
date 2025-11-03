
# tools/make_code_pdf.py
"""
Create a PDF for copyright filing:
- Reads a UTF-8 text export (e.g., copyright_out/ONF_code_export.txt)
- Adds a professional cover page (title, author, date)
- If total pages <= 20 (by page_lines), include ALL pages.
- Else include FIRST 10 pages + LAST 10 pages.
- Outputs: copyright_out/ONF_code_first_last_10_pages.pdf

Usage:
  python tools\make_code_pdf.py --source copyright_out\ONF_code_export.txt --title "Open NeuroHealth Framework (StrokeAI prototype)" --author "Parameshwar"

Requires: reportlab
Install via:  python -m pip install reportlab
"""

from __future__ import annotations
import argparse, math
from pathlib import Path
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

FONT = "Courier"
FONT_SIZE = 9
HEADER_FONT_SIZE = 10
LINE_GAP = 11   # ~55 lines per page

def paginate_lines(lines, page_lines):
    for i in range(0, len(lines), page_lines):
        yield lines[i:i+page_lines]

def draw_cover_page(c: canvas.Canvas, title: str, author: str):
    w, h = A4
    c.setFillColor(colors.darkblue)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(w/2, h - 180, title)

    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    c.drawCentredString(w/2, h - 230, f"Author: {author}")
    c.drawCentredString(w/2, h - 260, f"Date of Creation: {datetime.now().strftime('%Y-%m-%d')}")

    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(w/2, h - 310, "Software Copyright Submission (Source Code Extract)")

    c.setFont("Helvetica", 10)
    c.setFillColor(colors.gray)
    c.drawCentredString(w/2, 80, f"Generated automatically on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.showPage()

def draw_page(c: canvas.Canvas, page_lines, left_margin, top_y, title, section, page_num, page_total):
    w, h = A4
    c.setFont(FONT, HEADER_FONT_SIZE)
    c.drawString(left_margin, h - 36, f"{title}")
    c.drawRightString(w - left_margin, h - 36, f"{section}  |  Page {page_num} of {page_total}")

    c.setFont(FONT, FONT_SIZE)
    y = top_y
    for line in page_lines:
        char_w = FONT_SIZE * 0.6
        max_chars = int((w - 2 * left_margin) / char_w)
        while line:
            c.drawString(left_margin, y, line[:max_chars])
            line = line[max_chars:]
            y -= LINE_GAP
    c.showPage()

def build_pdf(source_txt: Path, out_pdf: Path, title: str, author: str, page_lines=55):
    text = source_txt.read_text(encoding="utf-8", errors="replace")
    all_lines = text.splitlines()
    total_pages = math.ceil(len(all_lines) / page_lines)

    if total_pages <= 20:
        sections = [("Complete Code", all_lines)]
    else:
        first = all_lines[:page_lines*10]
        last  = all_lines[-page_lines*10:]
        sections = [("First 10 Pages", first), ("Last 10 Pages", last)]

    c = canvas.Canvas(str(out_pdf), pagesize=A4, pageCompression=1)
    draw_cover_page(c, title, author)

    w, h = A4
    left_margin = 36
    top_y = h - 60

    page_list = []
    for sec_name, sec_lines in sections:
        for p in paginate_lines(sec_lines, page_lines):
            page_list.append((sec_name, p))
    page_total = len(page_list)

    page_num = 1
    for sec_name, p_lines in page_list:
        draw_page(c, p_lines, left_margin, top_y, title, sec_name, page_num, page_total)
        page_num += 1

    c.setFont(FONT, 8)
    c.drawRightString(w - 36, 20, f"Generated {datetime.now().isoformat()}  |  Source: {source_txt.name}")
    c.save()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--author", required=True)
    ap.add_argument("--page-lines", type=int, default=55)
    args = ap.parse_args()

    src = Path(args.source)
    out = src.parent / "ONF_code_first_last_10_pages.pdf"
    build_pdf(src, out, title=args.title, author=args.author, page_lines=args.page_lines)
    print(f"✅ PDF ready with cover: {out}  (Upload this to the Copyright Office portal)")

if __name__ == "__main__":
    main()
