---
title: "Jailbreak Kindle | Cách giữ lửa đọc sách"
author: clgp
date: "2026-10-05T09:46:11+07:00"
categories:
  -
tags:
  - kindle
  - koreader
  - github-actions
---

Dạo này chăm đọc sách lại trên Kindle thì có một số chỗ gây ngứa: Con ppw4 quá lag, và quan trọng nhất là **mình không lấy được dữ liệu đọc sách của chính mình**. Thế là jailbreak, cài KOReader, rồi tiện tay làm luôn một cái heatmap đọc sách kiểu GitHub contributions trên trang [/books](/books/)

Bài này gồm 2 phần:

1. Jailbreak Kindle bằng **SpiderCat** và cài KOReader
2. Luồng đồng bộ `statistics.sqlite3` từ Kindle lên blog để theo dõi quá trình đọc

<!--more-->

## Phần 1: Jailbreak bằng SpiderCat

Mình làm theo hướng dẫn trên [kindlemodding.org: SpiderCat](https://kindlemodding.org/jailbreaking/SpiderCat/). SpiderCat là một jailbreak mới (ra ngày 01/09/26, tác giả sparklerfish), điểm hay là **không cần máy tính, không cần cắm dây**: toàn bộ exploit có thể thực hiện trực tiếp trên máy kindle

> ⚠️ Jailbreak có rủi ro, làm thì tự chịu trách nhiệm nha. Trước khi làm, dùng **Jailbreaking Wizard** trên kindlemodding.org để kiểm tra model + firmware của máy có được hỗ trợ không. Wizard bảo SpiderCat thì mới làm SpiderCat.

### Chuẩn bị

- Kindle có model/firmware được hỗ trợ (Wizard xác nhận)
- Wi-Fi: bắt buộc phải bật **suốt quá trình**, tắt giữa chừng là hỏng
- Đọc trang overview trước, và nếu guide yêu cầu thì **làm đầy bộ nhớ** (filler files) để Kindle không tự tải bản cập nhật vá lỗ hổng giữa lúc đang jailbreak

### Các bước

**1. Tải cuốn SpiderCat về Kindle**, chọn 1 trong 2 cách:

- Cắm USB vào máy tính, tải file SpiderCat rồi chép vào thư mục `documents/` của Kindle
- Hoặc mở **Web Browser** trên Kindle, vào `https://kindlemodding.org/spidercat` và tải trực tiếp

**2. Mở cuốn SpiderCat trong Library.** Có thể có hoặc không có ảnh bìa, tuỳ máy. Nhớ là **Wi-Fi vẫn phải bật**.

**3. Chờ.** Lúc đầu chỉ là một trang trắng vài giây, rồi chữ bắt đầu chạy từ trên xuống. Có popup "application error" thì kệ nó, không ảnh hưởng.

**4. Kindle tự khởi động lại.** Khi script chạy xong sẽ hiện "Restarting Kindle", máy reboot và thế là xong, đã jailbreak.

Nếu không có gì xảy ra khi mở sách → kiểm tra lại Wi-Fi. Nếu dòng cuối hiện `abort:no-firm` thay vì `executing` → model/firmware không tương thích, xem lại Wizard.

### Sau khi jailbreak

- SpiderCat đã **tự chặn OTA update** cho mình, nên giờ có thể xoá filler files. Nhớ xoá luôn các file `.bin` (file update) ở thư mục gốc của Kindle nếu có.
- Các jailbreak đời mới cài sẵn **KPM**: một package manager cho Kindle. Mọi thứ cài qua thanh tìm kiếm ở màn hình chính, gõ lệnh bắt đầu bằng `;`

### Cài KOReader

Reboot một lần cho chắc, bật Wi-Fi, rồi gõ vào **thanh tìm kiếm** ở home:

```
;kpm update
;kpm install koreader
```

Chờ chút, trên home sẽ xuất hiện một scriptlet KOReader, bấm vào là chạy (hoặc gõ `;kpm launch koreader`). Muốn gỡ thì `;kpm uninstall koreader`.

Từ đây mình chép EPUB thẳng vào `documents/books/` qua USB, mở bằng KOReader, khỏi convert gì nữa.

## Phần 2: Đưa dữ liệu đọc sách lên blog

KOReader có plugin **Reading statistics** ghi lại mọi thứ: đọc trang nào, lúc nào, bao lâu, tất cả nằm trong một file SQLite là `statistics.sqlite3`. Có file này rồi thì làm heatmap streak như GitHub chỉ là chuyện xử lý dữ liệu.

### Toàn cảnh

<img src = "/images/kindle_diagram.png" alt="Luồng sync: Kindle → Koofr → GitHub Actions → /books">

### 1. Sync từ Kindle lên cloud

KOReader hỗ trợ đồng bộ statistics qua Dropbox hoặc **WebDAV**. Mình không có Nextcloud nên dùng **[Koofr](https://koofr.eu)**: free 10GB và có sẵn WebDAV.

- Trên Koofr: tạo thư mục `koreader`, rồi vào _Preferences → Password_ tạo một **app password** riêng cho KOReader (đừng dùng mật khẩu chính)
- Trong KOReader: _Tools → Reading statistics → Settings → Cloud sync_, thêm WebDAV với địa chỉ:

```
https://app.koofr.net/dav/Koofr/koreader/
```

- Bấm **Synchronize now** → file `statistics.sqlite3` xuất hiện trên Koofr

KOReader không có nút "auto sync" cho statistics, nên mình dùng plugin **Profiles**: tạo một profile chỉ chứa action _Synchronize reading statistics_, rồi bật _Auto-execute → on book closing_. Đóng sách là tự sync. Thêm _Network → Action when Wi-Fi is off → turn on_ để nó tự bật Wi-Fi.

### 2. Đọc file SQLite

Trong `statistics.sqlite3` có 2 bảng chính:

- `book`: mỗi cuốn một dòng: title, authors, số trang, tổng thời gian đọc, lần mở cuối
- `page_stat_data`: mỗi lần lật trang một dòng: `id_book`, `page`, `start_time`, `duration`

Có một cái bẫy nhỏ: nếu đổi cỡ chữ giữa chừng thì tổng số trang của sách thay đổi, số trang trong `page_stat_data` bị lệch. KOReader đã tính sẵn chuyện này bằng view **`page_stat`**, quy đổi mọi số trang về cùng một thang theo `book.pages`. Nên mình đọc từ view này.

Script [`scripts/koreader_sync.py`](https://github.com/clgp-aint-cool/clgp-aint-cool.github.io/blob/main/scripts/koreader_sync.py) làm mấy việc:

- Mở DB ở chế độ **read-only** (`?mode=ro`) để không bao giờ đụng vào file gốc
- Đếm số trang **khác nhau** đọc mỗi ngày (đọc lại một trang không tính 2 lần), theo giờ `Asia/Ho_Chi_Minh`
- Tính % tiến độ từng cuốn = trang xa nhất đã đọc / tổng số trang
- Xuất ra 2 file:

```js
// data/reading_log.json, cho heatmap
{ "2026-10-05": 14, "2026-10-06": 1, ... }

// data/koreader.json, cho mục "Đang đọc"
{ "current": { "title": "...", "progress": 13, "readMinutes": 62, ... },
  "books": [ ... ] }
```

File `.sqlite3` là dữ liệu cá nhân nên mình thêm `*.sqlite3` vào `.gitignore`, chỉ có JSON đã tổng hợp là được commit.

### 3. GitHub Actions chạy mỗi đêm

Workflow `.github/workflows/sync-reading.yaml` chạy lúc **23:50 giờ VN** (cron `50 16 * * *` UTC):

1. `curl` tải `statistics.sqlite3` từ Koofr, thông tin đăng nhập để trong **GitHub Secrets** (`KOREADER_WEBDAV_URL`, `KOREADER_WEBDAV_USER`, `KOREADER_WEBDAV_PASS`)
2. Chạy `koreader_sync.py`
3. Có thay đổi thì commit dưới tên `github-actions[bot]`
4. Gọi `gh workflow run hugo.yaml` để build lại site

Bước 4 là chỗ mình bị hố: **push bằng `GITHUB_TOKEN` không trigger workflow khác** (GitHub chặn để tránh vòng lặp vô hạn), nên commit dữ liệu xong mà site không deploy. Phải gọi thẳng workflow deploy. Bước này chạy kể cả khi không có dữ liệu mới, vì streak phụ thuộc vào "hôm nay", không đọc thì streak cũng phải được tính lại.

Muốn cập nhật ngay không chờ tới đêm thì vào _Actions → Sync KOReader reading stats → Run workflow_.

### 4. Hiển thị trên Hugo

Mọi thứ được tính **lúc build**, trang tĩnh hoàn toàn, không cần JS gọi API:

- **Heatmap**: 53 tuần gần nhất, tuần bắt đầu từ Thứ 2. Mỗi ô có 5 mức màu theo số trang: 0 / 1–10 / 11–25 / 26–45 / >45
- **Streak**: đếm lùi từ hôm nay, hôm nay chưa đọc thì chưa tính là đứt (còn tới 23:59 mà)
- **Đang đọc**: lấy cuốn mở gần nhất trong `koreader.json`, ghép với trang sách có cùng tên để lấy bìa + review
- Sách giấy không có KOReader thì ghi tay vào `data/reading_manual.yaml`, cộng dồn vào heatmap

Bìa sách thì lấy thẳng từ file EPUB (`scripts/new_book.py`, `scripts/scan_kindle.py`): đọc `META-INF/container.xml` → file `.opf` → tìm ảnh có `properties="cover-image"` (EPUB3) hoặc `<meta name="cover">` (EPUB2). Script quét Kindle còn tạo luôn danh sách **TBR** từ những cuốn trên máy mà KOReader chưa từng mở.

### Hai cái bug lúc deploy

- **`int64` vs `int`**: Hugo 0.137 trên CI trả về `int64` từ `sub`/`mul`, còn `AddDate` chỉ nhận `int` → build fail, trong khi máy mình chạy Hugo 0.152 thì không sao. Fix: bọc `int (...)` và đồng bộ version Hugo trên CI với local.
- **Cache CSS**: deploy xong mở trang thấy vỡ layout HTML mới nhưng trình duyệt vẫn dùng CSS cũ trong cache (GitHub Pages để `max-age=600`). Fix: thêm hash nội dung vào URL CSS (`theme-override.css?v=<md5>`), CSS đổi thì URL đổi.

## Kết

Giờ mỗi tối đọc xong, đóng sách là Kindle tự sync, 23:50 GitHub Actions kéo dữ liệu về và ô heatmap hôm đó xanh lên. Nhìn streak 🔥 tăng dần cũng là một kiểu động lực.
Theo dõi mình đọc gì ở [/books](/books/) nha.
