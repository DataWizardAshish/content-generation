"""
One-time script: extract Griffith Ramayana PDF into per-canto text files.

Usage:
    python scripts/extract_pdf.py --pdf 24869-pdf.pdf --out canto_cache/

Produces:
    canto_cache/Book_I/Canto_1.txt ... canto_cache/Book_VI/Canto_128.txt

Run once. Re-run only if the PDF changes.
"""
import argparse
import re
from collections import defaultdict
from pathlib import Path

import fitz  # pymupdf


CANTO_RE = re.compile(r"Canto\s+([IVXLCDM]+)\.", re.IGNORECASE)
BOOK_RE = re.compile(r"^Book\s+([IVXLCDM]+)\.", re.IGNORECASE | re.MULTILINE)
BOOK_DIRS = {1: "Book_I", 2: "Book_II", 3: "Book_III", 4: "Book_IV", 5: "Book_V", 6: "Book_VI"}


def roman_to_int(s: str) -> int:
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    s = s.upper()
    result, prev = 0, 0
    for ch in reversed(s):
        v = vals.get(ch, 0)
        result += v if v >= prev else -v
        prev = v
    return result


def extract(pdf_path: str, out_root: str):
    doc = fitz.open(pdf_path)
    print(f"Opened: {pdf_path} ({len(doc)} pages)")

    current_book = 0
    current_canto = 0
    pages_by_canto: dict[tuple[int, int], list[str]] = defaultdict(list)

    for page in doc:
        text = page.get_text()
        preview = text[:300]

        book_m = BOOK_RE.search(preview)
        if book_m:
            current_book = roman_to_int(book_m.group(1))

        canto_m = CANTO_RE.search(preview)
        if canto_m:
            current_canto = roman_to_int(canto_m.group(1))

        if current_book > 0 and current_canto > 0:
            pages_by_canto[(current_book, current_canto)].append(text)

    out_path = Path(out_root)
    counts: dict[int, int] = defaultdict(int)

    for (book, canto), pages in pages_by_canto.items():
        book_dir = out_path / BOOK_DIRS.get(book, f"Book_{book}")
        book_dir.mkdir(parents=True, exist_ok=True)
        canto_file = book_dir / f"Canto_{canto}.txt"
        canto_file.write_text("\n".join(pages), encoding="utf-8")
        counts[book] += 1

    print("\nExtraction complete:")
    total = 0
    for book in sorted(counts):
        n = counts[book]
        total += n
        print(f"  {BOOK_DIRS[book]}: {n} cantos")
    print(f"  Total: {total} canto files written to {out_root}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract Griffith Ramayana PDF into canto text files")
    parser.add_argument("--pdf", required=True, help="Path to PDF file")
    parser.add_argument("--out", default="canto_cache/", help="Output directory (default: canto_cache/)")
    args = parser.parse_args()
    extract(args.pdf, args.out)
