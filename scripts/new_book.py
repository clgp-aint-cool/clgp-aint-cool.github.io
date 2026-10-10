#!/usr/bin/env python3
"""Tạo trang sách mới từ file EPUB: lấy tên, tác giả, ảnh bìa.

Usage: python3 scripts/new_book.py <file.epub> [--force]

  - Bìa   -> static/images/books/<slug>.<ext>  (thu nhỏ còn 600px nếu có `sips` của macOS)
  - Trang -> content/books/<slug>.md  với status: reading
Tên sách lấy đúng từ metadata EPUB nên khớp với tên trong KOReader,
nhờ vậy mục "Đang đọc" tự ghép % tiến độ từ KOReader với bìa này.
"""
import json
import posixpath
import re
import shutil
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
NS = {
    "c": "urn:oasis:names:tc:opendocument:xmlns:container",
    "opf": "http://www.idpf.org/2007/opf",
    "dc": "http://purl.org/dc/elements/1.1/",
}
IMAGE_EXT = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}


def slugify(text):
    text = text.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def pick_author(opf):
    """Ưu tiên creator có role "aut" (EPUB2: opf:role, EPUB3: <meta refines>), bỏ qua dịch giả."""
    creators = opf.findall(".//dc:creator", NS)
    if not creators:
        return ""
    roles = {}
    for meta in opf.iter():
        if meta.tag.endswith("meta") and meta.get("property") == "role" and meta.get("refines"):
            roles[meta.get("refines").lstrip("#")] = (meta.text or "").strip()

    def role(c):
        return c.get(f"{{{NS['opf']}}}role") or roles.get(c.get("id"), "")

    # Element không có con bị coi là False -> phải so sánh với None, không dùng `or`
    for match in (lambda c: role(c) == "aut",
                  lambda c: role(c) != "trl" and "(dịch)" not in (c.text or ""),
                  lambda c: True):
        best = next((c for c in creators if match(c)), None)
        if best is not None:
            return (best.text or "").strip()


def read_epub(path):
    z = zipfile.ZipFile(path)
    container = ET.fromstring(z.read("META-INF/container.xml"))
    opf_path = container.find(".//c:rootfile", NS).get("full-path")
    opf = ET.fromstring(z.read(opf_path))

    title = opf.findtext(".//dc:title", default="", namespaces=NS).strip()
    author = pick_author(opf)

    items = opf.findall(".//opf:manifest/opf:item", NS)
    cover = None
    # EPUB 3: properties="cover-image"
    for it in items:
        if "cover-image" in (it.get("properties") or "").split():
            cover = it
    # EPUB 2: <meta name="cover" content="<item id>">
    if cover is None:
        meta = opf.find(".//opf:metadata/opf:meta[@name='cover']", NS)
        if meta is not None:
            cover = next((it for it in items if it.get("id") == meta.get("content")), None)
    # Cuối cùng: ảnh nào có chữ "cover" trong id/href
    if cover is None:
        cover = next((it for it in items if (it.get("media-type") or "").startswith("image/")
                      and "cover" in (it.get("id", "") + it.get("href", "")).lower()), None)

    cover_data = cover_ext = None
    if cover is not None:
        href = posixpath.normpath(posixpath.join(posixpath.dirname(opf_path), unquote(cover.get("href"))))
        cover_data = z.read(href)
        cover_ext = IMAGE_EXT.get(cover.get("media-type"), Path(href).suffix or ".jpg")
    return title, author, cover_data, cover_ext


def main(epub, force=False):
    title, author, cover_data, cover_ext = read_epub(epub)
    if not title:
        sys.exit("EPUB không có tên sách (dc:title)")
    slug = slugify(title)
    page = ROOT / "content" / "books" / f"{slug}.md"
    if page.exists() and not force:
        sys.exit(f"Đã có {page.relative_to(ROOT)} — thêm --force để ghi đè")

    cover_rel = ""
    if cover_data:
        cover_rel = f"images/books/{slug}{cover_ext}"
        cover_file = ROOT / "static" / cover_rel
        cover_file.write_bytes(cover_data)
        if shutil.which("sips"):
            subprocess.run(["sips", "-Z", "600", str(cover_file)], capture_output=True)
        print(f"Bìa:   static/{cover_rel}")
    else:
        print("⚠️  EPUB không có ảnh bìa — trang sẽ dùng bìa placeholder")

    now = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).isoformat(timespec="seconds")
    q = lambda s: json.dumps(s, ensure_ascii=False)
    page.write_text(f"""---
title: {q(title)}
author: {q(author)}
date: {now}
status: reading
progress: 0
rating: 0
review: ''
coverImage: {q(cover_rel)}
---

<-- more -->
""")
    print(f"Trang: {page.relative_to(ROOT)}")
    print(f"       {title} — {author}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--force"]
    if len(args) != 1:
        sys.exit(__doc__)
    main(args[0], force="--force" in sys.argv)
