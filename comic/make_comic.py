#!/usr/bin/env python3
"""Tax.Log B급 만화 생성기 (2026-11-25 사용자 요청 시안).
드리미나 장면 위에 레퍼런스 웹툰처럼 '깔끔한' 손그림 말풍선·내레이션 박스·자유 글씨를 얹는다.

사용법: python3 comic/make_comic.py comic.json out_dir
comic.json
{"size": 1080,
 "panels": [
  {"photo": "path.jpg",
   "items": [
     {"type": "bubble", "text": "말\\n두 줄", "x": 80, "y": 60, "w": 520, "tail": [400, 380], "size": 40, "bold": false},
     {"type": "box", "text": "다음 날", "x": 330, "y": 40, "size": 38},
     {"type": "free", "text": "으아아악!!", "x": 100, "y": 120, "size": 90, "rot": -6}
   ]}
 ]}
bubble: x,y = 말풍선 왼쪽 위, w = 너비(높이는 글 줄 수로 자동), tail = 꼬리 끝(캔버스 절대 좌표).
[ ] 안 글자는 빨간색 강조.
"""
import html, json, math, os, random, re, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "fonts")


def esc(t):
    t = html.escape(t)
    t = re.sub(r"\[(.+?)\]", r'<span style="color:#d81e1e">\1</span>', t)
    return t.replace("\n", "<br>")


def wobble_ellipse(cx, cy, rx, ry, seed, n=40, amp=0.018):
    rnd = random.Random(seed)
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        r = 1 + rnd.uniform(-amp, amp)
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    # 부드러운 닫힌 곡선(Catmull-Rom → Bezier)
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f} "
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} "
    return d + "Z"


def bubble(it, i):
    fs = it.get("size", 40)
    lines = it["text"].count("\n") + 1
    w = it.get("w", 520)
    h = it.get("h", int(lines * fs * 1.35 + fs * 1.6))
    x, y = it["x"], it["y"]
    cx, cy, rx, ry = x + w / 2, y + h / 2, w / 2, h / 2
    path = wobble_ellipse(cx, cy, rx, ry, seed=i * 7 + 3)
    tx, ty = it.get("tail", [cx, y + h + 60])
    ang = math.atan2(ty - cy, tx - cx)
    bx, by = cx + rx * 0.92 * math.cos(ang), cy + ry * 0.92 * math.sin(ang)
    px, py = -math.sin(ang), math.cos(ang)
    base = min(rx, ry) * 0.28
    a1 = (bx + px * base, by + py * base)
    a2 = (bx - px * base * 0.2, by - py * base * 0.2)
    mid = ((a1[0] + tx) / 2 + px * 8, (a1[1] + ty) / 2 + py * 8)
    tail = (f"M{a1[0]:.1f},{a1[1]:.1f} Q{mid[0]:.1f},{mid[1]:.1f} {tx:.1f},{ty:.1f} "
            f"Q{(a2[0]+tx)/2:.1f},{(a2[1]+ty)/2:.1f} {a2[0]:.1f},{a2[1]:.1f} Z")
    svg = (f'<path d="{tail}" fill="#fff" stroke="#111" stroke-width="4.5" stroke-linejoin="round"/>'
           f'<path d="{path}" fill="#fff" stroke="#111" stroke-width="4.5"/>'
           f'<path d="{tail}" fill="#fff" stroke="none" transform="translate(0,0)"/>')
    # 꼬리와 풍선 이음새를 지우기 위해 풍선 안쪽을 한 번 더 칠함
    svg += f'<path d="{wobble_ellipse(cx, cy, rx - 2.5, ry - 2.5, seed=i * 7 + 3)}" fill="#fff"/>'
    wt = 700 if it.get("bold") else 500
    txt = (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;display:flex;'
           f'align-items:center;justify-content:center;text-align:center;font-size:{fs}px;font-weight:{wt};'
           f'line-height:1.32;letter-spacing:-0.02em;color:#111"><div>{esc(it["text"])}</div></div>')
    return svg, txt


def box(it, i):
    fs = it.get("size", 38)
    lines = it["text"].count("\n") + 1
    w = it.get("w", int(max(sum(0.55 if ord(c) < 128 else 0.98 for c in re.sub(r"[\[\]]", "", l)) for l in it["text"].split("\n")) * fs + fs * 1.6))
    h = int(lines * fs * 1.35 + fs * 1.1)
    x, y = it.get("x", 0), it["y"]
    if it.get("center"):
        x = (1080 - w) // 2
    rnd = random.Random(i)
    j = lambda: rnd.uniform(-2.5, 2.5)
    p = (f"M{x+j()},{y+j()} L{x+w+j()},{y+j()} L{x+w+j()},{y+h+j()} L{x+j()},{y+h+j()} Z")
    svg = (f'<path d="{p}" fill="#fff" stroke="#111" stroke-width="4"/>'
           f'<path d="M{x+6},{y+h+6} L{x+w+6},{y+h+6} L{x+w+6},{y+6}" fill="none" stroke="#111" stroke-width="4"/>')
    al = it.get("align", "center")
    txt = (f'<div style="position:absolute;left:{x+fs*0.55}px;top:{y}px;width:{w-fs*1.1}px;height:{h}px;display:flex;'
           f'align-items:center;justify-content:{"center" if al=="center" else "flex-start"};text-align:{al};'
           f'font-size:{fs}px;font-weight:500;line-height:1.35;letter-spacing:-0.02em;color:#111">'
           f'<div>{esc(it["text"])}</div></div>')
    return svg, txt


def free(it, i):
    fs = it.get("size", 60)
    col = it.get("color", "#111")
    stroke = it.get("stroke", "#fff")
    txt = (f'<div style="position:absolute;left:{it["x"]}px;top:{it["y"]}px;transform:rotate({it.get("rot",0)}deg);'
           f'transform-origin:left top;font-size:{fs}px;font-weight:{it.get("weight",800)};line-height:1.15;'
           f'letter-spacing:-0.03em;color:{col};-webkit-text-stroke:{it.get("sw",8)}px {stroke};paint-order:stroke fill;'
           f'white-space:nowrap">{esc(it["text"])}</div>')
    return "", txt


def page(pn, S):
    photo = "file://" + os.path.join(ROOT, pn["photo"])
    svg, txt = "", ""
    for i, it in enumerate(pn.get("items", [])):
        s, t = {"bubble": bubble, "box": box, "free": free}[it["type"]](it, i)
        svg += s
        txt += t
    logo = '<div style="position:absolute;right:34px;bottom:26px;font-weight:800;font-size:30px;color:#fff;opacity:.9;text-shadow:0 2px 6px rgba(0,0,0,.6)">Tax.Log</div>'
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:P;src:url('file://{FONTS}/Pretendard-Regular.otf');font-weight:400}}
@font-face{{font-family:P;src:url('file://{FONTS}/Pretendard-Medium.otf');font-weight:500}}
@font-face{{font-family:P;src:url('file://{FONTS}/Pretendard-Bold.otf');font-weight:700}}
@font-face{{font-family:P;src:url('file://{FONTS}/Pretendard-ExtraBold.otf');font-weight:800}}
@font-face{{font-family:P;src:url('file://{FONTS}/Pretendard-Black.otf');font-weight:900}}
@font-face{{font-family:P;src:url('file://{FONTS}/Pretendard-SemiBold.otf');font-weight:600}}
html,body{{margin:0;width:{S}px;height:{S}px;overflow:hidden;font-family:P,sans-serif}}
</style></head><body>
<div style="position:absolute;inset:0;background:url('{photo}') center/cover no-repeat"></div>
<svg style="position:absolute;left:0;top:0" width="{S}" height="{S}">{svg}</svg>{txt}{logo}
</body></html>"""


def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    S = spec.get("size", 1080)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": S, "height": S})
        for n, pn in enumerate(spec["panels"], 1):
            hp = os.path.join(out, f".p{n}.html")
            open(hp, "w", encoding="utf-8").write(page(pn, S))
            pg.goto("file://" + os.path.abspath(hp))
            pg.wait_for_timeout(400)
            f = os.path.join(out, f"{n:02d}.jpg")
            pg.screenshot(path=f, type="jpeg", quality=93)
            os.remove(hp)
            print(f)
        b.close()


if __name__ == "__main__":
    main()
