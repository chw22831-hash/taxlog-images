#!/usr/bin/env python3
"""Tax.Log(@taxlog_woo) 인스타 카드뉴스 생성기 — 사용자 PPT(인디고·네이비·크림슨, 라벤더 카드) 스타일.

사용법: python3 make_cards.py spec.json out_dir
출력: out_dir/01.jpg ... (1080x1350 JPEG, 인스타 4:5)

spec.json 구조
{
  "date": "2026.11.06",
  "slides": [
    {"type":"cover", "tag":"정부안 · 국회 심의 중", "label":"TODAY'S TAX",
     "title":"ISA가 하나 더\\n생길 수도 있어요", "highlight":"하나 더", "subtitle":"..."},
    {"type":"list", "part":"NEWS", "label":"무슨 일이야?", "title":"...", "highlight":"...",
     "items":[{"head":"굵은 한 줄","sub":"설명"}], "quote":"하단 인용 박스(선택)"},
    {"type":"compare", "part":"COMPARE", "label":"...", "title":"...", "highlight":"...",
     "left":{"name":"일반 ISA","rows":[{"pill":"200만","head":"...","sub":"..."}]},
     "right":{"name":"생산적금융 ISA","rows":[...]}, "note":"하단 주석(선택)"},
    {"type":"stat", "part":"POINT", "label":"...", "title":"...", "highlight":"...",
     "stats":[{"cap":"연간 납입","value":"2,000만 원"}], "cards":[{"tag":"청년형","text":"..."}]},
    {"type":"action", "part":"CHECK", "label":"...", "title":"...", "highlight":"...",
     "dark_title":"그래서 지금은?", "dark_hl":"지금", "cards":[{"tag":"기존 ISA","text":"..."}]},
    {"type":"outro", "title":"...", "subtitle":"...", "sources":"출처: ..."}
  ]
}
highlight: 제목 안에서 크림슨으로 강조할 단어(선택)
cover 추가 옵션:
  "theme": "midnight"(기본·남색 글로우) | "light"(라벤더 밝은 톤) | "crimson"(와인→크림슨)
           | "indigo"(인디고 원형 라인) | "split"(위 남색 블록 + 큰 숫자, 아래 흰 바탕 제목)
  "big":   짧은 숫자·키워드(예: "2029", "22%") — 배경에 크게 깔림(split에선 메인 비주얼)
  ※ 전날 표지와 같은 theme 연속 사용 금지(겹치는 건 OK, 연속만 피하기)
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
M = 80
BG = (251, 251, 253)
INDIGO = (61, 43, 217)
NAVY = (18, 39, 122)
DEEP = (22, 19, 63)
DEEP2 = (13, 11, 40)
CRIMSON = (200, 51, 79)
WINE = (165, 40, 90)
YELLOW = (255, 229, 138)
GOLD = (232, 199, 122)
LAV = (236, 234, 243)
LAV2 = (245, 244, 250)
LINE = (226, 224, 236)
INK = (22, 22, 30)
SUB = (110, 110, 125)
WHITE = (255, 255, 255)
BRAND = "Tax.Log"
HANDLE = "@taxlog_woo"

FD = "/usr/share/fonts/opentype/noto/"


def F(w, s):
    for n in (f"NotoSansCJK-{w}.ttc", "NotoSansCJK-Bold.ttc", "NotoSansCJK-Regular.ttc"):
        p = os.path.join(FD, n)
        if os.path.exists(p):
            return ImageFont.truetype(p, s, index=1)
    return ImageFont.load_default(s)


def wrap(d, text, f, mw):
    out = []
    for para in str(text).split("\n"):
        cur = ""
        for word in para.split(" "):
            t = (cur + " " + word).strip()
            if d.textlength(t, font=f) <= mw:
                cur = t
                continue
            if cur:
                out.append(cur)
            cur = ""
            for ch in word:
                if d.textlength(cur + ch, font=f) > mw:
                    out.append(cur); cur = ch
                else:
                    cur += ch
        out.append(cur)
    return out


def draw_hl_line(d, x, y, line, f, color, hl, hlcolor):
    """한 줄을 그리되 hl 단어는 hlcolor로."""
    if hl and hl in line:
        a, b = line.split(hl, 1)
        d.text((x, y), a, font=f, fill=color); x += d.textlength(a, font=f)
        d.text((x, y), hl, font=f, fill=hlcolor); x += d.textlength(hl, font=f)
        d.text((x, y), b, font=f, fill=color)
    else:
        d.text((x, y), line, font=f, fill=color)


def block(d, x, y, text, f, color, mw, lh=1.4, hl=None, hlc=CRIMSON, align="left"):
    for line in wrap(d, text, f, mw):
        lx = x
        if align == "center":
            lx = x + (mw - d.textlength(line, font=f)) / 2
        draw_hl_line(d, lx, y, line, f, color, hl, hlc)
        y += int(f.size * lh)
    return y


def pill(d, x, y, text, f, fill, color, padx=22, h=None):
    h = h or int(f.size * 1.75)
    w = d.textlength(text, font=f) + padx * 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=fill)
    bb = d.textbbox((0, 0), text, font=f)
    d.text((x + padx, y + (h - (bb[3] - bb[1])) / 2 - bb[1]), text, font=f, fill=color)
    return x + w


def logo(d, x, y, dark=False, box=None, tcol=WHITE):
    s = 34
    d.rounded_rectangle([x, y, x + s, y + s], radius=8, fill=box or INDIGO)
    d.text((x + 8, y - 2), "T", font=F("Black", 30), fill=tcol)
    f = F("Bold", 30)
    c = WHITE if dark else NAVY
    d.text((x + s + 10, y - 2), "Tax", font=f, fill=c)
    tx = x + s + 10 + d.textlength("Tax", font=f)
    d.text((tx, y - 2), ".", font=f, fill=INDIGO if not dark else GOLD)
    d.text((tx + d.textlength(".", font=f), y - 2), "Log", font=f, fill=c)


def logo_w(d):
    f = F("Bold", 30)
    return 34 + 10 + d.textlength("Tax.Log", font=f)


def page(d, i, n, dark=False):
    f = F("Bold", 26)
    t = f"{i:02d}"
    d.text((W - M - d.textlength(t, font=f), H - 70), t, font=f, fill=(150, 150, 170) if not dark else (140, 140, 180))


def light_base(s, i, n):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    x = pill(d, M, 70, s.get("part", "NEWS"), F("Bold", 26), INDIGO, WHITE, padx=20)
    if s.get("label"):
        d.text((x + 16, 74), s["label"], font=F("Bold", 28), fill=INDIGO)
    logo(d, W - M - logo_w(d), 76)
    y = block(d, M, 140, s.get("title", ""), F("Black", 62), INK, W - 2 * M, 1.3, s.get("highlight"))
    page(d, i, n)
    return im, d, y + 30


def card(d, box, fill=WHITE, outline=LINE, r=22):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=2)


# ---------- slide types ----------

COVER_THEMES = ("midnight", "light", "crimson", "indigo", "split")


def _grad(c1, c2, vertical=True):
    im = Image.new("RGB", (W, H), c1)
    d = ImageDraw.Draw(im)
    n = H if vertical else W
    for k in range(n):
        t = k / (n - 1)
        c = tuple(int(c1[j] + (c2[j] - c1[j]) * t) for j in range(3))
        if vertical:
            d.line([(0, k), (W, k)], fill=c)
        else:
            d.line([(k, 0), (k, H)], fill=c)
    return im


def _cover_text(d, s, y, title_c, hl_c, sub_c, label_c, bar_c, tag_fill, tag_c, max_y=None):
    d.rectangle([M, y, M + 60, y + 4], fill=bar_c)
    d.text((M, y + 24), s.get("label", "TODAY'S TAX"), font=F("Bold", 30), fill=label_c)
    y += 100
    y = block(d, M, y, s["title"], F("Black", 104), title_c, W - 2 * M, 1.25, s.get("highlight"), hl_c)
    y += 30
    if s.get("subtitle"):
        y = block(d, M, y, s["subtitle"], F("Medium", 40), sub_c, W - 2 * M, 1.5)
    if s.get("tag"):
        pill(d, M, y + 40, "★ " + s["tag"], F("Bold", 30), tag_fill, tag_c)
        y += 40 + 52
    return y


def _cover_footer(d, date, dark, box=None, tcol=WHITE):
    logo(d, M, H - 110, dark=dark, box=box, tcol=tcol)
    f = F("Medium", 26)
    d.text((W - M - d.textlength(date, font=f), H - 106), date, font=f,
           fill=(140, 140, 180) if dark else SUB)


def _big(d, s, x_right, y, color):
    """선택: 'big' 필드(짧은 숫자·키워드)를 배경 장식으로 크게."""
    if not s.get("big"):
        return
    f = F("Black", 230)
    t = s["big"]
    while d.textlength(t, font=f) > W - 2 * M and f.size > 120:
        f = F("Black", f.size - 20)
    d.text((x_right - d.textlength(t, font=f), y), t, font=f, fill=color)


def s_cover(s, i, n, date):
    theme = s.get("theme", "midnight")
    if theme == "light":
        im = Image.new("RGB", (W, H), LAV2)
        d = ImageDraw.Draw(im)
        d.ellipse([W - 520, -260, W + 260, 520], fill=LAV)
        d.rectangle([0, 0, 24, H], fill=INDIGO)
        _big(d, s, W - M + 10, 20, (226, 222, 245))
        _cover_text(d, s, 330, INK, CRIMSON, SUB, INDIGO, CRIMSON, INDIGO, WHITE)
        _cover_footer(d, date, False)
        return im
    if theme == "crimson":
        im = _grad(WINE, CRIMSON)
        d = ImageDraw.Draw(im)
        d.ellipse([-300, H - 520, 420, H + 200], fill=tuple(min(255, c + 14) for c in CRIMSON))
        _big(d, s, W - M + 10, 20, tuple(min(255, c + 22) for c in WINE))
        _cover_text(d, s, 330, WHITE, YELLOW, (255, 225, 232), YELLOW, YELLOW, WHITE, WINE)
        _cover_footer(d, date, True)
        return im
    if theme == "indigo":
        im = _grad(INDIGO, NAVY, vertical=False)
        d = ImageDraw.Draw(im)
        for r, a in ((560, 18), (400, 30), (240, 44)):
            c = tuple(min(255, INDIGO[k] + a) for k in range(3))
            d.ellipse([W - 200 - r, 180 - r, W - 200 + r, 180 + r], outline=c, width=3)
        _big(d, s, W - M + 10, 20, tuple(min(255, c + 26) for c in INDIGO))
        _cover_text(d, s, 330, WHITE, YELLOW, (215, 215, 245), GOLD, GOLD, YELLOW, INK)
        _cover_footer(d, date, True, box=WHITE, tcol=INDIGO)
        return im
    if theme == "split":
        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im)
        top = 470
        d.rectangle([0, 0, W, top], fill=NAVY)
        d.ellipse([W - 360, -200, W + 200, 360], fill=INDIGO)
        if s.get("big"):
            f = F("Black", 230)
            while d.textlength(s["big"], font=f) > W - 2 * M and f.size > 100:
                f = F("Black", f.size - 20)
            bb = d.textbbox((0, 0), s["big"], font=f)
            d.text((M, top - 40 - bb[3]), s["big"], font=f, fill=YELLOW)
        d.text((M, 70), s.get("label", "TODAY'S TAX"), font=F("Bold", 30), fill=GOLD)
        y = top + 60
        y = block(d, M, y, s["title"], F("Black", 92), INK, W - 2 * M, 1.25, s.get("highlight"), CRIMSON)
        y += 24
        if s.get("subtitle"):
            y = block(d, M, y, s["subtitle"], F("Medium", 38), SUB, W - 2 * M, 1.5)
        if s.get("tag"):
            pill(d, M, y + 34, "★ " + s["tag"], F("Bold", 30), CRIMSON, WHITE)
        _cover_footer(d, date, False)
        return im
    # midnight (기본)
    im = Image.new("RGB", (W, H), DEEP2)
    d = ImageDraw.Draw(im)
    # 오른쪽 아래로 은은한 인디고 그라데이션 + 원형 글로우
    glow = Image.new("RGB", (W, H), DEEP2)
    gd = ImageDraw.Draw(glow)
    for r in range(700, 0, -10):
        t = r / 700
        c = tuple(int(DEEP2[k] + (INDIGO[k] - DEEP2[k]) * (1 - t) * 0.55) for k in range(3))
        gd.ellipse([W - 260 - r, H - 380 - r, W - 260 + r, H - 380 + r], fill=c)
    im = Image.blend(im, glow, 1.0)
    d = ImageDraw.Draw(im)
    y = 330
    d.rectangle([M, y, M + 60, y + 4], fill=GOLD)
    d.text((M, y + 24), s.get("label", "TODAY'S TAX"), font=F("Bold", 30), fill=GOLD)
    y += 100
    y = block(d, M, y, s["title"], F("Black", 104), WHITE, W - 2 * M, 1.25, s.get("highlight"), GOLD)
    y += 30
    if s.get("subtitle"):
        y = block(d, M, y, s["subtitle"], F("Medium", 40), (200, 200, 225), W - 2 * M, 1.5)
    if s.get("tag"):
        pill(d, M, y + 40, "★ " + s["tag"], F("Bold", 30), YELLOW, INK)
    logo(d, M, H - 110, dark=True)
    f = F("Medium", 26)
    d.text((W - M - d.textlength(date, font=f), H - 106), date, font=f, fill=(140, 140, 180))
    return im


def s_list(s, i, n):
    im, d, y = light_base(s, i, n)
    items = s.get("items", [])
    for k, it in enumerate(items, 1):
        hf, sf = F("Bold", 40), F("Regular", 32)
        hl = wrap(d, it["head"], hf, W - 2 * M - 150)
        sl = wrap(d, it.get("sub", ""), sf, W - 2 * M - 150) if it.get("sub") else []
        h = 60 + len(hl) * 54 + len(sl) * 46
        card(d, [M, y, W - M, y + h], fill=LAV2, outline=LAV)
        cx, cy = M + 62, y + 30 + 27
        d.ellipse([cx - 27, cy - 27, cx + 27, cy + 27], fill=CRIMSON)
        nf = F("Bold", 30)
        d.text((cx - d.textlength(str(k), font=nf) / 2, cy - 21), str(k), font=nf, fill=WHITE)
        ty = y + 30
        for line in hl:
            draw_hl_line(d, M + 120, ty, line, hf, INK, it.get("hl"), CRIMSON); ty += 54
        for line in sl:
            d.text((M + 120, ty + 4), line, font=sf, fill=SUB); ty += 46
        y += h + 22
    if s.get("quote"):
        qf = F("Bold", 32)
        ql = wrap(d, "“ " + s["quote"] + " ”", qf, W - 2 * M - 60)
        qh = 50 + len(ql) * 46
        y = max(y + 10, H - 130 - qh)
        d.rounded_rectangle([M, y, W - M, y + qh], radius=qh // 2 if len(ql) == 1 else 26, fill=LAV)
        block(d, M + 30, y + 25, "\n".join(ql), qf, NAVY, W - 2 * M - 60, 1.4, align="center")
    return im


def s_compare(s, i, n):
    im, d, y = light_base(s, i, n)
    colw = W - 2 * M
    for side, head in (("left", INDIGO), ("right", NAVY)):
        c = s[side]
        d.rounded_rectangle([M, y, W - M, y + 70], radius=14, fill=head)
        d.rectangle([M, y + 40, W - M, y + 70], fill=head)
        d.text((M + 28, y + 14), c["name"], font=F("Bold", 34), fill=WHITE)
        y += 70
        rows = c.get("rows", [])
        top = y
        y += 22
        for r in rows:
            pf = F("Bold", 30)
            pw = max(170, d.textlength(r["pill"], font=pf) + 44)
            pc = {"blue": (52, 108, 222), "wine": WINE}.get(r.get("color"), CRIMSON)
            d.rounded_rectangle([M + 26, y, M + 26 + pw, y + 62], radius=31, fill=pc)
            d.text((M + 26 + (pw - d.textlength(r["pill"], font=pf)) / 2, y + 11), r["pill"], font=pf, fill=WHITE)
            tx = M + 26 + pw + 24
            d.text((tx, y - 2), r["head"], font=F("Bold", 34), fill=INK)
            if r.get("sub"):
                d.text((tx, y + 42), r["sub"], font=F("Regular", 26), fill=SUB)
            y += 96
        d.rounded_rectangle([M, top, W - M, y], radius=0, outline=LINE, width=2)
        y += 34
    if s.get("note"):
        block(d, M, y, s["note"], F("Regular", 26), SUB, colw, 1.5)
    return im


def s_stat(s, i, n):
    im, d, y = light_base(s, i, n)
    stats = s.get("stats", [])
    box_h = 270
    card(d, [M, y, W - M, y + box_h * len(stats) + 20], fill=WHITE, outline=LINE)
    yy = y + 30
    for st in stats:
        d.text((M + 40, yy), st["cap"], font=F("Bold", 32), fill=SUB)
        d.text((M + 36, yy + 44), st["value"], font=F("Black", 108), fill=CRIMSON)
        if st.get("sub"):
            d.text((M + 40, yy + 200), st["sub"], font=F("Regular", 28), fill=SUB)
        yy += box_h
    y = y + box_h * len(stats) + 50
    for c in s.get("cards", []):
        tf = F("Regular", 32)
        tl = wrap(d, c["text"], tf, W - 2 * M - 80)
        h = 100 + len(tl) * 46
        d.rounded_rectangle([M, y, W - M, y + h], radius=22, fill=LAV2)
        pill(d, M + 34, y + 26, c["tag"], F("Bold", 26), YELLOW, INK)
        block(d, M + 40, y + 82, c["text"], tf, INK, W - 2 * M - 80, 1.42, c.get("hl"))
        y += h + 20
    return im


def s_action(s, i, n):
    im, d, y = light_base(s, i, n)
    top = y
    bottom = H - 120
    d.rounded_rectangle([M, top, W - M, bottom], radius=26, fill=DEEP)
    yy = block(d, M, top + 50, s.get("dark_title", "그래서 지금은?"), F("Black", 58), WHITE,
               W - 2 * M, 1.3, s.get("dark_hl"), YELLOW, align="center") + 30
    cards = s.get("cards", [])
    avail = bottom - 40 - yy
    ch = min(220, (avail - 20 * (len(cards) - 1)) // max(1, len(cards)))
    for c in cards:
        d.rounded_rectangle([M + 36, yy, W - M - 36, yy + ch], radius=20, fill=(38, 34, 92), outline=GOLD, width=2)
        pill(d, M + 66, yy + 24, c["tag"], F("Bold", 26), GOLD, INK)
        block(d, M + 70, yy + 82, c["text"], F("Medium", 32), WHITE, W - 2 * M - 140, 1.42, c.get("hl"), YELLOW)
        yy += ch + 20
    return im


def s_cta(s, i, n):
    """잠긴(블러) 카드로 궁금증 유발 + 댓글 키워드 안내."""
    from PIL import ImageFilter
    im = Image.new("RGB", (W, H), DEEP2)
    d = ImageDraw.Draw(im)
    logo(d, W - M - logo_w(d), 76, dark=True)
    y = 170
    d.rectangle([M, y, M + 60, y + 4], fill=GOLD)
    y = block(d, M, y + 36, s.get("title", ""), F("Black", 66), WHITE, W - 2 * M, 1.3, s.get("highlight"), GOLD) + 40
    for k, c in enumerate(s.get("locked", []), 1):
        h = 150
        d.rounded_rectangle([M, y, W - M, y + h], radius=22, fill=(38, 34, 92), outline=(70, 64, 140), width=2)
        cx, cy = M + 60, y + h // 2
        d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=GOLD)
        nf = F("Bold", 28)
        d.text((cx - d.textlength(str(k), font=nf) / 2, cy - 20), str(k), font=nf, fill=INK)
        # 흐리게 처리한 본문
        layer = Image.new("RGB", (W - 2 * M - 140, h - 40), (38, 34, 92))
        ld = ImageDraw.Draw(layer)
        block(ld, 0, 6, c, F("Bold", 36), WHITE, layer.width, 1.35)
        layer = layer.filter(ImageFilter.GaussianBlur(9))
        im.paste(layer, (M + 110, y + 20))
        d = ImageDraw.Draw(im)
        lf = F("Bold", 26)
        pill(d, W - M - 150, y + h // 2 - 23, "🔒 잠김" if False else "LOCK", lf, GOLD, INK, padx=18)
        y += h + 20
    y += 30
    kw = s.get("keyword", "알려줘")
    y = block(d, M, y, s.get("cta", f"댓글에 '{kw}' 남겨주시면\nDM으로 정리본 보내드려요"), F("Bold", 46), WHITE,
              W - 2 * M, 1.4, f"'{kw}'", YELLOW, align="center")
    block(d, M, H - 150, "본 콘텐츠는 일반 정보 제공 목적이며 개인별 세무·투자 자문이 아닙니다. 정부안·법안은 국회 심의 과정에서 달라질 수 있습니다.",
          F("Regular", 24), (150, 150, 185), W - 2 * M, 1.5)
    page(d, i, n, dark=True)
    return im


def s_outro(s, i, n):
    im = Image.new("RGB", (W, H), DEEP2)
    d = ImageDraw.Draw(im)
    y = 360
    d.rectangle([M, y, M + 60, y + 4], fill=GOLD)
    y += 40
    y = block(d, M, y, s.get("title", "세금은 아는 만큼\n아낄 수 있어요"), F("Black", 84), WHITE, W - 2 * M, 1.3, s.get("highlight"), GOLD)
    y += 30
    y = block(d, M, y, s.get("subtitle", "저장해두고 필요할 때 꺼내보세요.\n팔로우하면 새 소식을 놓치지 않아요."), F("Regular", 38), (200, 200, 225), W - 2 * M, 1.55)
    pill(d, M, y + 50, HANDLE, F("Bold", 40), GOLD, INK, padx=34)
    fy = H - 250
    if s.get("sources"):
        fy = block(d, M, fy, s["sources"], F("Regular", 24), (150, 150, 185), W - 2 * M, 1.5) + 10
    block(d, M, max(fy, H - 190), "본 콘텐츠는 일반 정보 제공 목적이며 개인별 세무·투자 자문이 아닙니다. 정부안·법안 내용은 국회 심의 과정에서 달라질 수 있습니다.",
          F("Regular", 24), (150, 150, 185), W - 2 * M, 1.5)
    logo(d, W - M - logo_w(d), H - 100, dark=True)
    return im


def main(spec_path, out_dir):
    spec = json.load(open(spec_path, encoding="utf-8"))
    slides = spec["slides"]
    n = len(slides)
    os.makedirs(out_dir, exist_ok=True)
    fn = {"list": s_list, "compare": s_compare, "stat": s_stat, "action": s_action, "cta": s_cta}
    paths = []
    for i, s in enumerate(slides, 1):
        t = s.get("type", "list")
        if t == "cover":
            im = s_cover(s, i, n, spec.get("date", ""))
        elif t == "outro":
            im = s_outro(s, i, n)
        else:
            im = fn.get(t, s_list)(s, i, n)
        p = os.path.join(out_dir, f"{i:02d}.jpg")
        im.save(p, "JPEG", quality=92)
        paths.append(p)
    print("\n".join(paths))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
