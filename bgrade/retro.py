#!/usr/bin/env python3
"""그림 AI 결과를 2000년대 초반 게임 스크린샷처럼: 저해상도로 줄였다가 픽셀 그대로 확대 + 색 단계 약간 감소.
사용법: python3 bgrade/retro.py in.(webp|png|jpg) out.jpg [W H] [factor=3]
"""
import sys
from PIL import Image, ImageEnhance
src, out = sys.argv[1], sys.argv[2]
W = int(sys.argv[3]) if len(sys.argv) > 3 else 1080
H = int(sys.argv[4]) if len(sys.argv) > 4 else 1350
f = float(sys.argv[5]) if len(sys.argv) > 5 else 3
im = Image.open(src).convert("RGB")
# 목표 비율로 가운데 자르기
r = W / H
w, h = im.size
if w / h > r:
    nw = int(h * r); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
else:
    nh = int(w / r); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
small = im.resize((int(W / f), int(H / f)), Image.BOX)
small = ImageEnhance.Color(small).enhance(float(sys.argv[6]) if len(sys.argv) > 6 else 0.9)
small = ImageEnhance.Contrast(small).enhance(0.95)
small = small.quantize(colors=128, dither=Image.Dither.NONE).convert("RGB")
small.resize((W, H), Image.NEAREST).save(out, quality=90)
print(out)
