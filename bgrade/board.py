#!/usr/bin/env python3
"""그림 AI 장면 속 빈 간판/화면에 '확인된 숫자'로 픽셀풍 막대그래프를 붙인다(숫자는 그림 AI에 맡기지 않음).
사용법: python3 bgrade/board.py in_img out.png board.json
board.json: {"box":[x0,y0,x1,y1], "title":"엔비디아 분기 매출", "unit":"억 달러",
             "bars":[["2분기 실적",962],["3분기 전망",1080]], "colors":["#76b900","#ffd43b"], "note":"전망은 회사 가이던스(±2%)"}
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = lambda s, w="Bold": ImageFont.truetype(os.path.join(ROOT, "fonts", f"Pretendard-{w}.otf"), s)
im = Image.open(sys.argv[1]).convert("RGB"); out = sys.argv[2]; b = json.load(open(sys.argv[3]))
x0, y0, x1, y1 = b["box"]; W, H = x1 - x0, y1 - y0
k = 3  # 1/3 크기로 그린 뒤 픽셀 그대로 확대
w, h = W // k, H // k
c = Image.new("RGB", (w, h), b.get("bg", "#f4f1e6")); d = ImageDraw.Draw(c)
d.rectangle([0, 0, w - 1, h - 1], outline="#2b2b2b", width=2)
d.text((8, 6), b["title"], font=F(max(12, h // 11)), fill="#1e1e1e")
d.text((w - 8, 8), b.get("unit", ""), font=F(max(9, h // 16), "Medium"), fill="#555", anchor="ra")
bars = b["bars"]; mx = max(v for _, v in bars)
top, base = int(h * 0.32), int(h * 0.72)
bw = int(w / (len(bars) * 1.9)); gap = (w - bw * len(bars)) // (len(bars) + 1)
cols = b.get("colors", ["#76b900", "#ffd43b", "#4aa3ff"])
for i, (lab, v) in enumerate(bars):
    bx = gap + i * (bw + gap); bh = int((base - top) * v / mx)
    d.rectangle([bx, base - bh, bx + bw, base], fill=cols[i % len(cols)], outline="#1e1e1e", width=2)
    d.text((bx + bw / 2, base - bh - 3), f"{v:,}", font=F(max(11, h // 12), "ExtraBold"), fill="#1e1e1e", anchor="md")
    d.text((bx + bw / 2, base + 4), lab, font=F(max(9, h // 15), "SemiBold"), fill="#2b2b2b", anchor="ma")
d.line([6, base, w - 6, base], fill="#1e1e1e", width=2)
if b.get("note"):
    d.text((8, h - 6), b["note"], font=F(max(8, h // 20), "Medium"), fill="#666", anchor="ld")
im.paste(c.resize((W, H), Image.NEAREST), (x0, y0))
im.save(out); print(out)
