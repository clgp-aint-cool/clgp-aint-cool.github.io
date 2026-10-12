#!/usr/bin/env python3
"""Lấy danh sách EPUB trong thư mục sách trên Koofr (WebDAV) -> data/koofr_library.json + bìa sách.

Usage: python3 scripts/koofr_library.py

Biến môi trường:
  KOREADER_WEBDAV_USER / KOREADER_WEBDAV_PASS   tài khoản WebDAV (dùng chung với sync stats)
  KOOFR_BOOKS_URL     URL thư mục sách, vd https://app.koofr.net/dav/Koofr/koreader/books/
                      (bỏ trống thì lấy thư mục books/ cạnh KOREADER_WEBDAV_URL)

  - Chỉ tải EPUB mới hoặc đã đổi dung lượng, sách cũ giữ nguyên thông tin trong JSON
  - Bìa -> static/images/books/koofr/<slug>.<ext> (thu nhỏ 300px nếu có Pillow/sips)
Trang /books/ đưa sách chưa mở trong KOReader, chưa có trang riêng vào TBR.
"""
import base64
import io
import json
import os
import posixpath
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote, unquote, urljoin, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from new_book import ROOT, read_epub, slugify  # noqa: E402

COVER_DIR = ROOT / "static" / "images" / "books" / "koofr"
OUT = ROOT / "data" / "koofr_library.json"
DAV = "{DAV:}"


def books_url():
    url = os.environ.get("KOOFR_BOOKS_URL")
    if url:
        return url if url.endswith("/") else url + "/"
    stats = os.environ.get("KOREADER_WEBDAV_URL")
    if not stats:
        sys.exit("Thiếu KOOFR_BOOKS_URL hoặc KOREADER_WEBDAV_URL")
    return urljoin(stats, "books/")


def request(url, method="GET", headers=None):
    auth = f"{os.environ['KOREADER_WEBDAV_USER']}:{os.environ['KOREADER_WEBDAV_PASS']}"
    h = {"Authorization": "Basic " + base64.b64encode(auth.encode()).decode(), **(headers or {})}
    with urllib.request.urlopen(urllib.request.Request(url, method=method, headers=h), timeout=60) as r:
        return r.read()


def list_epubs(url):
    """PROPFIND Depth 1 -> [(tên file, dung lượng)]."""
    xml = ET.fromstring(request(url, "PROPFIND", {"Depth": "1"}))
    files = []
    for resp in xml.iter(f"{DAV}response"):
        href = unquote(resp.findtext(f"{DAV}href", ""))
        name = posixpath.basename(href.rstrip("/"))
        size = resp.findtext(f".//{DAV}getcontentlength")
        if name.lower().endswith(".epub") and size:
            files.append((name, int(size)))
    return sorted(files)


def save_cover(data, ext, slug):
    cover_file = COVER_DIR / f"{slug}{ext}"
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(data))
        img.thumbnail((300, 300))
        img.convert("RGB").save(cover_file.with_suffix(".jpg"), quality=85)
        cover_file = cover_file.with_suffix(".jpg")
    except ImportError:
        cover_file.write_bytes(data)
        if shutil.which("sips"):
            subprocess.run(["sips", "-Z", "300", str(cover_file)], capture_output=True)
    return cover_file


def main():
    url = books_url()
    old = {b["file"]: b for b in json.loads(OUT.read_text())["books"]} if OUT.exists() else {}
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    books = []

    for name, size in list_epubs(url):
        prev = old.get(name)
        if prev and prev["size"] == size and (not prev["cover"] or (ROOT / "static" / prev["cover"]).exists()):
            books.append(prev)
            continue
        print(f"⬇️  {name}")
        with tempfile.NamedTemporaryFile(suffix=".epub") as tmp:
            tmp.write(request(urljoin(url, quote(name))))
            tmp.flush()
            try:
                title, author, cover_data, cover_ext = read_epub(tmp.name)
            except Exception as e:
                print(f"⚠️  Bỏ qua {name}: {e}")
                continue
        title = title or Path(name).stem
        cover_rel = ""
        if cover_data:
            cover_rel = str(save_cover(cover_data, cover_ext, slugify(title)).relative_to(ROOT / "static"))
        books.append({"file": name, "size": size, "title": title, "author": author, "cover": cover_rel})

    used = {Path(b["cover"]).name for b in books if b["cover"]}
    for f in COVER_DIR.iterdir():
        if f.name not in used:
            f.unlink()

    OUT.write_text(json.dumps({"books": books}, ensure_ascii=False, indent=2) + "\n")
    print(f"{len(books)} sách trên Koofr ({urlparse(url).path})")
    for b in books:
        print(f"  {b['title']} — {b['author']}")


if __name__ == "__main__":
    main()
