#!/usr/bin/env python3
"""Chuyển statistics.sqlite3 của KOReader thành data cho trang /books/.

Usage: python3 scripts/koreader_sync.py <statistics.sqlite3> [data_dir]

Tạo ra:
  data/reading_log.json  {"YYYY-MM-DD": số trang đọc trong ngày}  -> heatmap
  data/koreader.json     {"current": {...}, "books": [...]}         -> mục "Đang đọc"
"""
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Ho_Chi_Minh")
IGNORE_TITLES = {"KOReader Quickstart Guide"}


def local_date(ts):
    return datetime.fromtimestamp(ts, TZ).strftime("%Y-%m-%d")


def main(db_path, data_dir):
    # Mở read-only để không bao giờ sửa file gốc
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row

    books = {
        row["id"]: row
        for row in con.execute("SELECT * FROM book")
        if row["title"] not in IGNORE_TITLES
    }

    # page_stat là view của KOReader: quy đổi số trang về cùng một thang (book.pages),
    # nên đổi cỡ chữ giữa chừng không làm lệch số trang.
    pages_per_day = {}
    max_page = {}
    seen = set()
    for row in con.execute("SELECT id_book, page, start_time FROM page_stat"):
        if row["id_book"] not in books:
            continue
        day = local_date(row["start_time"])
        key = (day, row["id_book"], row["page"])
        if key not in seen:
            seen.add(key)
            pages_per_day[day] = pages_per_day.get(day, 0) + 1
        max_page[row["id_book"]] = max(max_page.get(row["id_book"], 0), row["page"])

    book_list = []
    for book_id, b in books.items():
        if not b["total_read_pages"]:
            continue
        pages = b["pages"] or 0
        progress = round(100 * max_page.get(book_id, 0) / pages) if pages else 0
        book_list.append({
            "title": b["title"].strip(),
            # authors có thể nhiều dòng ("Tác giả\nDịch giả") -> lấy dòng đầu
            "author": (b["authors"] or "").split("\n")[0].strip(),
            "pages": pages,
            "progress": min(progress, 100),
            "readMinutes": round((b["total_read_time"] or 0) / 60),
            "lastOpen": datetime.fromtimestamp(b["last_open"], TZ).isoformat(),
        })
    book_list.sort(key=lambda x: x["lastOpen"], reverse=True)

    out = Path(data_dir)
    (out / "reading_log.json").write_text(
        json.dumps(dict(sorted(pages_per_day.items())), indent=2) + "\n")
    (out / "koreader.json").write_text(json.dumps({
        "current": book_list[0] if book_list else None,
        "books": book_list,
    }, ensure_ascii=False, indent=2) + "\n")

    print(f"{len(pages_per_day)} ngày, {sum(pages_per_day.values())} trang, {len(book_list)} sách")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "data")
