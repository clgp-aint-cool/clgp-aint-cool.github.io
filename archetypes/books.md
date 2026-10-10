---
title: '{{ replace .File.ContentBaseName "-" " " | title }}'
author: ''
date: {{ .Date }}
# reading | read  (TBR thì ghi trong data/tbr.yaml)
status: reading
# % đã đọc, chỉ dùng khi status: reading
progress: 0
rating: 0
review: ''
coverImage: ''
---

{{ `<-- more -->` | safeHTML }}