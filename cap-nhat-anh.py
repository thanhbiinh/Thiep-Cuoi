#!/usr/bin/env python3
"""Quét thư mục anh/, nhac/, qr/ rồi ghi config.js cho thiệp cưới.

Cách dùng: bỏ ảnh vào thư mục anh/, chạy:  python cap-nhat-anh.py
- Số đầu tên file (01, 02, ...) dùng để sắp thứ tự ảnh.
- Nếu máy có Pillow (pip install pillow), ảnh được nén sang thư mục anh-web/
  (tối đa 1400px) và ảnh nhỏ trong anh-nho/ (520px, cho dải ảnh chạy) để khách mở nhanh.
  Ảnh gốc không bị sửa.
- nhac/: bỏ 1 file .mp3 làm nhạc nền. qr/: bỏ 1 ảnh QR ngân hàng.
"""

import json, os, re, sys
from urllib.parse import quote

AQ = (".jpg", ".jpeg", ".png", ".webp", ".gif")
AU = (".mp3", ".m4a", ".ogg", ".wav")
root = os.path.dirname(os.path.abspath(__file__))


def files(folder, exts):
    d = os.path.join(root, folder)
    if not os.path.isdir(d):
        return []

    def key(n):
        return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", n)]

    return sorted((n for n in os.listdir(d) if n.lower().endswith(exts)), key=key)


def caption(name):
    base = os.path.splitext(name)[0]
    base = re.sub(r"^[\d\s._\-]+", "", base).strip()
    return base


try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None
    print("Chưa có Pillow nên ảnh dùng nguyên bản gốc. Nên chạy: pip install pillow")

photos = []
out_dir = os.path.join(root, "anh-web")
th_dir = os.path.join(root, "anh-nho")
for n in files("anh", AQ):
    src = os.path.join(root, "anh", n)
    path = "anh/" + n
    thumb = ""
    if Image is not None and not n.lower().endswith(".gif"):
        os.makedirs(out_dir, exist_ok=True)
        os.makedirs(th_dir, exist_ok=True)
        new = os.path.splitext(n)[0] + ".jpg"
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        sm = im.copy()
        sm.thumbnail((520, 520))
        sm.save(
            os.path.join(th_dir, new),
            "JPEG",
            quality=76,
            optimize=True,
            progressive=True,
        )
        im.thumbnail((1400, 1400))
        im.save(
            os.path.join(out_dir, new),
            "JPEG",
            quality=82,
            optimize=True,
            progressive=True,
        )
        path = "anh-web/" + new
        thumb = "anh-nho/" + new
    item = {"src": quote(path), "cap": caption(n)}
    if thumb:
        item["thumb"] = quote(thumb)
    photos.append(item)

music = files("nhac", AU)
qr = files("qr", AQ)
cfg = {
    "photos": photos,
    "music": quote("nhac/" + music[0]) if music else "",
    "qrImg": quote("qr/" + qr[0]) if qr else "",
}
with open(os.path.join(root, "config.js"), "w", encoding="utf-8") as f:
    f.write(
        "// File này được tạo tự động bởi cap-nhat-anh.py. Bạn không cần sửa tay.\n"
    )
    f.write("window.CFG = " + json.dumps(cfg, ensure_ascii=False) + ";\n")
print(
    "Xong: %d ảnh, nhạc: %s, QR: %s"
    % (len(photos), cfg["music"] or "không", cfg["qrImg"] or "không")
)
