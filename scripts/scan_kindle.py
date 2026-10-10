#!/usr/bin/env python3
"""Quét sách EPUB trên Kindle (cắm USB) -> data/kindle_library.json + bìa sách.

Usage: python3 scripts/scan_kindle.py [kindle_root]     (mặc định /Volumes/Kindle)

  - Lấy tên, tác giả, bìa từ từng EPUB trong documents/books/
  - "opened": KOReader đã mở cuốn này chưa (có percent_finished trong .sdr)
  - Bìa -> static/images/books/kindle/<slug>.<ext> (thu nhỏ 300px), xoá bìa của sách không còn trên Kindle
Trang /books/ dùng file này để:
  - TBR = sách chưa mở, chưa có trang riêng trong content/books/, chưa có trong data/koreader.json
  - Lấy bìa cho mục "Đang đọc" khi KOReader sync sang cuốn mới
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from new_book import ROOT, read_epub, slugify  # noqa: E402

COVER_DIR = ROOT / "static" / "images" / "books" / "kindle"


def is_opened(epub):
    sdr = epub.with_suffix(".sdr")
    return any("percent_finished" in f.read_text(errors="ignore") for f in sdr.glob("metadata.*.lua"))


def blog_book_slugs():
    """Slug tên các sách đã có trang riêng (tên trên blog có thể viết không dấu)."""
    slugs = set()
    for md in (ROOT / "content" / "books").glob("*.md"):
        m = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', md.read_text(), re.M)
        if m and md.name != "_index.md":
            slugs.add(slugify(m.group(1)))
    return slugs


def main(kindle_root):
    books_dir = Path(kindle_root) / "documents" / "books"
    if not books_dir.is_dir():
        sys.exit(f"Không thấy {books_dir} — Kindle đã cắm chưa?")

    COVER_DIR.mkdir(parents=True, exist_ok=True)
    on_blog = blog_book_slugs()
    books, used_covers = [], set()

    for epub in sorted(books_dir.rglob("*.epub")):
        if epub.name.startswith("._"):  # file rác AppleDouble của macOS
            continue
        try:
            title, author, cover_data, cover_ext = read_epub(epub)
        except Exception as e:
            print(f"⚠️  Bỏ qua {epub.name}: {e}")
            continue
        title = title or epub.stem
        slug = slugify(title)

        cover_rel = ""
        if cover_data:
            cover_file = COVER_DIR / f"{slug}{cover_ext}"
            if not cover_file.exists():
                cover_file.write_bytes(cover_data)
                if shutil.which("sips"):
                    subprocess.run(["sips", "-Z", "300", str(cover_file)], capture_output=True)
            used_covers.add(cover_file.name)
            cover_rel = str(cover_file.relative_to(ROOT / "static"))

        books.append({
            "title": title,
            "author": author,
            "cover": cover_rel,
            "opened": is_opened(epub),
            "onBlog": slug in on_blog,
        })

    for f in COVER_DIR.iterdir():
        if f.name not in used_covers:
            f.unlink()

    (ROOT / "data" / "kindle_library.json").write_text(
        json.dumps({"books": books}, ensure_ascii=False, indent=2) + "\n")

    tbr = [b for b in books if not b["opened"] and not b["onBlog"]]
    print(f"{len(books)} sách trên Kindle · {sum(b['opened'] for b in books)} đã mở · "
          f"{sum(b['onBlog'] for b in books)} đã có trang · {len(tbr)} TBR")
    for b in tbr:
        print(f"  TBR: {b['title']} — {b['author']}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/Volumes/Kindle")
