#!/usr/bin/env python3
"""Tax.Log(@taxlog_woo) 카드뉴스 생성기 v2 — 뉴스형(MZ) 스타일.

레퍼런스: 사진/폰 화면을 꽉 채운 배경 + 아래쪽 어두운 그라데이션 + 큰 흰 글씨(한 줄만 노란 강조)
+ 기사체 본문. 라벨·뱃지·번호 카드·이모지 없이 '뉴스 계정'처럼 보이게 만든다.

★ 현재 표준(2026-11-13 사용자 확정): 모든 장에 실제 사진 배경 — 슬라이드마다 "photo"(저장소 경로, 예: photos/unsplash/<id>.jpg)와 "pos"를 지정.
  같은 촬영 세트에서 5장, 장마다 다른 사진. "scene"(폰 화면)·layout "text"/"number"/"split"은 쓰지 않음.
  로고는 오른쪽 하단 Tax.Log만 자동 표시. 기업 이슈면 슬라이드에 "brand": "SK hynix" 처럼 회사명을 넣으면 반투명 글씨로 깔림. 마지막 장 "foot"에 출처 + "Photo: 작가 / Unsplash" + 면책.

사용법: python3 make_cards_mz.py spec.json out_dir   → out_dir/01.jpg ... (1080x1350)
폰트: 저장소 fonts/ 의 Pretendard(SIL OFL 1.1)

spec.json
{
 "date": "2026.11.13",
 "slides": [
  {"type":"cover", "scene":{...}, "lines":["첫 줄", "둘째 줄", "[노란 줄]"]},
  {"type":"body",  "scene":{...}, "headline":"35% 구간, [2008년 그대로]",
   "sub":"굵은 소제목 한 줄", "body":"기사체 본문. **굵게** 강조 가능.",
   "foot":"(마지막 장만) 출처·면책 작은 글씨"}
 ]
}
텍스트 규칙: [대괄호] = 노란 강조, **별표** = 굵게(본문). 문장은 '~다/~입니다' 기사체.

scene (배경 폰 화면) 종류 — 화면 속 숫자도 카드 내용과 같은 '확인된 값'만 쓴다:
  {"kind":"bars", "title":"근로소득세 수입", "unit":"조 원", "items":[["2015",27.1],["2025",68.4]]}
  {"kind":"table","title":"종합소득세 세율", "rows":[["1,400만 원 이하","6%"], ...], "mark":3}
  {"kind":"list", "title":"제목", "rows":[["항목","값"], ...]}
  {"kind":"memo", "title":"제목", "text":"메모 앱처럼 보이는 짧은 글"}
  공통 옵션: "tilt"(기본 -7), "x"(가로 위치 %, 기본 50), "zoom"(기본 1.0)
※ 실존 기관·앱 로고나 이름(홈택스·은행 등)은 화면에 넣지 않는다.
"""
import html, json, os, re, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(ROOT, "fonts")
W, H = 1080, 1350
YEL = "#FFD43B"


def fmt(t, bold=True):
    t = html.escape(t)
    t = re.sub(r"\[(.+?)\]", r'<span class="y">\1</span>', t)
    if bold:
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return t.replace("\n", "<br>")


def scene_html(sc):
    k = sc.get("kind", "memo")
    title = html.escape(sc.get("title", ""))
    if k == "bars":
        mx = max(v for _, v in sc["items"])
        bars = "".join(
            f'<div class="bar"><div class="bv">{v:g}</div><div class="bf" style="height:{int(420*v/mx)}px"></div>'
            f'<div class="bl">{html.escape(l)}</div></div>' for l, v in sc["items"])
        body = f'<div class="unit">단위: {html.escape(sc.get("unit",""))}</div><div class="bars">{bars}</div>'
    elif k in ("table", "list"):
        mark = sc.get("mark", -1)
        rows = "".join(
            f'<div class="row{" mk" if i == mark else ""}"><span>{html.escape(a)}</span><b>{html.escape(b)}</b></div>'
            for i, (a, b) in enumerate(sc["rows"]))
        body = f'<div class="rows">{rows}</div>'
    else:
        body = f'<div class="memo">{fmt(sc.get("text",""))}</div>'
    return f'''
<div class="phone" style="left:{sc.get("x",50)}%;transform:translateX(-50%) rotate({sc.get("tilt",-7)}deg) scale({sc.get("zoom",1.0)})">
 <div class="scr">
  <div class="sb"><span>9:41</span><span class="isl"></span><span class="sig">▂▄▆ ■</span></div>
  <div class="apphd"><span class="back">‹</span><span>{title}</span><span class="dots">···</span></div>
  {body}
 </div>
</div>'''


CSS = """
@font-face{font-family:P;src:url('file://FONTS/Pretendard-Regular.otf');font-weight:400}
@font-face{font-family:P;src:url('file://FONTS/Pretendard-Medium.otf');font-weight:500}
@font-face{font-family:P;src:url('file://FONTS/Pretendard-SemiBold.otf');font-weight:600}
@font-face{font-family:P;src:url('file://FONTS/Pretendard-Bold.otf');font-weight:700}
@font-face{font-family:P;src:url('file://FONTS/Pretendard-ExtraBold.otf');font-weight:800}
@font-face{font-family:P;src:url('file://FONTS/Pretendard-Black.otf');font-weight:900}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1350px;overflow:hidden;background:#0b0b0d;font-family:P,sans-serif;letter-spacing:-0.02em;word-break:keep-all}
.bg{position:absolute;inset:0;background:
 radial-gradient(900px 700px at 70% 18%, #4a4640 0%, #2a2724 45%, #121110 100%)}
.bok{position:absolute;border-radius:50%;filter:blur(40px);opacity:.35}
.phone{position:absolute;top:70px;width:640px;height:1300px;border-radius:92px;background:#1b1b1d;padding:18px;
 box-shadow:0 60px 120px rgba(0,0,0,.6),0 0 0 3px #3a3a3e inset,0 0 0 2px #555 ;filter:blur(BLURpx)}
.scr{width:100%;height:100%;border-radius:76px;background:#f6f7f9;overflow:hidden;color:#111}
.sb{display:flex;justify-content:space-between;align-items:center;padding:30px 54px 0;font-weight:700;font-size:30px}
.isl{width:190px;height:54px;background:#000;border-radius:30px}
.sig{font-size:20px;letter-spacing:2px}
.apphd{display:flex;justify-content:space-between;padding:44px 40px 26px;font-size:36px;font-weight:700}
.back,.dots{color:#888;font-weight:400}
.rows{margin:10px 28px;background:#fff;border-radius:34px;padding:10px 0;box-shadow:0 2px 10px rgba(0,0,0,.05)}
.row{display:flex;justify-content:space-between;padding:30px 34px;font-size:31px;border-bottom:1px solid #eee;color:#333}
.row b{font-weight:700;color:#111}
.row.mk{background:#fff4c2}
.unit{padding:0 44px;color:#888;font-size:26px}
.bars{display:flex;justify-content:space-around;align-items:flex-end;height:620px;margin:20px 30px;background:#fff;border-radius:34px;padding:30px}
.bar{display:flex;flex-direction:column;align-items:center;width:150px}
.bf{width:120px;background:#3d5afe;border-radius:18px 18px 6px 6px}
.bar:first-child .bf{background:#c9cfe0}
.bv{font-size:40px;font-weight:800;margin-bottom:14px}
.bl{font-size:28px;color:#666;margin-top:14px}
.memo{margin:10px 40px;font-size:34px;line-height:1.65;color:#222;background:#fffbe6;border-radius:30px;padding:40px}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,0) 0%,rgba(0,0,0,.05) SHADE0%,rgba(0,0,0,.84) SHADE1%,rgba(0,0,0,.94) 100%)}
.grain{position:absolute;inset:0;opacity:.13;mix-blend-mode:overlay}
.vig{position:absolute;inset:0;box-shadow:inset 0 0 220px rgba(0,0,0,.55)}
.txt{position:absolute;left:84px;right:84px;color:#fff}
.y{color:#FFD43B}
.cover h1{font-weight:800;font-size:76px;line-height:1.22;letter-spacing:-0.035em;text-shadow:0 2px 18px rgba(0,0,0,.35)}
.foot1{position:absolute;bottom:70px;left:84px;right:84px;display:flex;justify-content:space-between;align-items:center;color:#fff}
.handle{font-weight:700;font-size:30px;opacity:.92}.handle i{display:inline-block;width:16px;height:16px;border-radius:50%;background:#7b7bd8;margin-right:12px;vertical-align:2px}
.wm{font-weight:900;font-size:36px;letter-spacing:-0.03em}
.body h2{font-weight:800;font-size:60px;line-height:1.25;letter-spacing:-0.035em;margin-bottom:40px}
.body h3{font-weight:700;font-size:37px;margin-bottom:16px}
.body p{font-weight:400;font-size:33px;line-height:1.62;color:#ececec}
.body p b{font-weight:700;color:#fff}
.wm2{position:absolute;bottom:56px;right:84px;text-align:right;color:#fff;font-weight:900;font-size:32px;opacity:.95}
.tag{position:absolute;top:56px;left:0;right:0;text-align:center;color:#fff;font-weight:600;font-size:26px;opacity:.75}
.tag i{display:inline-block;width:13px;height:13px;border-radius:50%;background:#7b7bd8;margin-right:10px;vertical-align:1px}
.fine{margin-top:34px;font-size:21px;line-height:1.5;color:#a9a9a9}
"""

GRAIN = ('<svg class="grain" width="1080" height="1350"><filter id="n"><feTurbulence type="fractalNoise" '
         'baseFrequency=".9" numOctaves="3" stitchTiles="stitch"/></filter><rect width="100%" height="100%" filter="url(#n)"/></svg>')


LAYOUT_CSS = """
.L{position:absolute;inset:0}
.split-ph{position:absolute;left:0;right:0;top:0;height:640px;background-repeat:no-repeat;filter:saturate(.92) contrast(1.04)}
.split-fade{position:absolute;left:0;right:0;top:440px;height:200px;background:linear-gradient(180deg,rgba(17,17,17,0),#111)}
.dark{background:#111;color:#fff}
.light{background:#f3f1ec;color:#141414}
.light .y{color:#141414;background:linear-gradient(transparent 58%,#FFD43B 58%)}
.light p{color:#3a3a3a}.light p b{color:#111}
.light .tag,.light .wm2{color:#141414}
.blk{position:absolute;left:84px;right:84px}
.blk h2{font-weight:800;font-size:60px;line-height:1.25;letter-spacing:-0.035em;margin-bottom:34px}
.blk h3{font-weight:700;font-size:37px;margin-bottom:16px}
.blk p{font-weight:400;font-size:33px;line-height:1.62}
.dark .blk p{color:#e6e6e6}.dark .blk p b{color:#fff}
.num{font-weight:900;font-size:210px;letter-spacing:-0.05em;line-height:1;color:#FFD43B}
.numcap{font-weight:600;font-size:34px;opacity:.75;margin:22px 0 60px}
.rule{width:64px;height:6px;background:#FFD43B;margin-bottom:40px}
.light .rule{background:#141414}
.fine2{margin-top:30px;font-size:21px;line-height:1.5;opacity:.6}
"""


def layout_page(s):
    """본문 장 레이아웃을 바꿔 '내용만 바꾼 템플릿' 느낌을 줄인다.
    layout: "photo"(사진 꽉 채움, 기본) | "split"(위 사진·아래 글) | "text"(사진 없는 글 장, theme dark/light) | "number"(큰 숫자 장)"""
    lay = s.get("layout", "photo")
    theme = s.get("theme", "dark")
    css = CSS.replace("FONTS", FONTS) + LAYOUT_CSS
    fine = f'<div class="fine2">{fmt(s["foot"])}</div>' if s.get("foot") else ""
    head = f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>'
    if lay == "split":
        ph = os.path.join(ROOT, s["photo"])
        out = (head + f'<div class="L dark"></div><div class="split-ph" style="background-image:url(\'file://{ph}\');'
               f'background-position:{s.get("pos","center")};background-size:{s.get("size","cover")}"></div><div class="split-fade"></div>'
               f'<div class="L dark" style="background:none"><div class="blk" style="top:640px"><h2>{fmt(s["headline"], bold=False)}</h2>'
               f'<h3>{fmt(s.get("sub",""), bold=False)}</h3><p>{fmt(s.get("body",""))}</p>{fine}</div></div>')
    elif lay == "number":
        out = (head + f'<div class="L {theme}"><div class="blk" style="top:50%;transform:translateY(-54%)"><div class="num">{html.escape(s["number"])}</div>'
               f'<div class="numcap">{fmt(s.get("caption",""), bold=False)}</div><h2>{fmt(s["headline"], bold=False)}</h2>'
               f'<p>{fmt(s.get("body",""))}</p>{fine}</div>')
    else:  # text
        out = (head + f'<div class="L {theme}"><div class="blk" style="top:50%;transform:translateY(-54%)"><div class="rule"></div><h2>{fmt(s["headline"], bold=False)}</h2>'
               f'<h3>{fmt(s.get("sub",""), bold=False)}</h3><p>{fmt(s.get("body",""))}</p>{fine}</div>')
    out += GRAIN.replace('class="grain"', 'class="grain" style="opacity:.05"')
    out += '<div class="wm2">Tax.Log</div>'  # 로고는 오른쪽 하단에만(사용자 요청 2026-11-13)
    if lay != "split":
        out += "</div>"
    return out + "</body></html>"


def page(s, i, date):
    if s["type"] != "cover" and s.get("layout", "photo") != "photo":
        return layout_page(s)
    sc = s.get("scene", {})
    cover = s["type"] == "cover"
    blur = 0 if cover else 1.2
    shade = (28, 52) if cover else (8, 30)
    bok = ''.join(f'<div class="bok" style="left:{x}px;top:{y}px;width:{r}px;height:{r}px;background:{c}"></div>'
                  for x, y, r, c in [(40, 120, 260, "#e9c48a"), (860, 60, 200, "#fff3d6"), (900, 700, 300, "#8a7a66")])
    css = CSS.replace("FONTS", FONTS).replace("BLUR", str(blur)).replace("SHADE0", str(shade[0])).replace("SHADE1", str(shade[1]))
    if s.get("photo"):  # 실사진 배경(저장소 photos/ 안의 파일). 폰 화면 대신 사용 — 기본 방식
        ph = s["photo"] if s["photo"].startswith("http") else "file://" + os.path.join(ROOT, s["photo"])
        pos = s.get("pos", "center")
        dim = s.get("dim", 0.0)
        top = s.get("clear", 50 if cover else 34)  # 이 높이(%)까지는 사진이 그대로 보임
        grad = (f"linear-gradient(180deg,rgba(0,0,0,.18) 0%,rgba(0,0,0,0) 14%,rgba(0,0,0,0) {top}%,"
                f"rgba(0,0,0,.72) {top+20}%,rgba(0,0,0,.9) 100%)")
        css = css.replace("inset 0 0 220px rgba(0,0,0,.55)", "inset 0 0 160px rgba(0,0,0,.28)").replace("opacity:.13", "opacity:.08")
        bg = (f'<div style="position:absolute;inset:0;background:url(\'{ph}\') {pos}/{s.get("size","cover")} no-repeat;filter:saturate(.92) contrast(1.04)"></div>'
              f'<div style="position:absolute;inset:0;background:rgba(0,0,0,{dim})"></div>'
              f'<div style="position:absolute;inset:0;background:{grad}"></div>')
        brand = ""
        if s.get("brand"):  # 기업 이슈: 회사 이름을 반투명 글씨로 은은하게(로고 이미지는 쓰지 않음)
            top = 150 if cover else 210
            brand = (f'<div style="position:absolute;left:0;right:0;top:{top}px;text-align:center;color:#fff;opacity:{s.get("brand_op",0.3)};'
                     f'font-weight:900;font-size:{s.get("brand_size",170)}px;letter-spacing:-0.02em;white-space:nowrap;filter:blur(0.6px);'
                     f'text-shadow:0 0 30px rgba(255,255,255,.25)">{html.escape(s["brand"])}</div>')
        out = f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{bg}{brand}{GRAIN}<div class="vig"></div>'
    else:
        out = f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body><div class="bg"></div>{bok}{scene_html(sc)}<div class="shade"></div>{GRAIN}<div class="vig"></div>'
    if cover:
        lines = "<br>".join(fmt(l, bold=False) for l in s["lines"])
        out += f'<div class="txt cover" style="bottom:230px"><h1>{lines}</h1></div>'
        out += '<div class="wm2" style="bottom:66px;font-size:36px">Tax.Log</div>'  # 로고는 오른쪽 하단에만
    else:
        fine = f'<div class="fine">{fmt(s["foot"])}</div>' if s.get("foot") else ""
        bottom = 130
        out += (f'<div class="txt body" style="bottom:{bottom}px"><h2>{fmt(s["headline"], bold=False)}</h2>'
                f'<h3>{fmt(s.get("sub",""), bold=False)}</h3><p>{fmt(s.get("body",""))}</p>{fine}</div>')
        out += '<div class="wm2">Tax.Log</div>'
    return out + "</body></html>"


def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        for i, s in enumerate(spec["slides"], 1):
            hp = os.path.join(out, f".s{i:02d}.html")
            open(hp, "w", encoding="utf-8").write(page(s, i, spec.get("date", "")))
            pg.goto("file://" + os.path.abspath(hp))
            pg.wait_for_timeout(250)
            pg.screenshot(path=os.path.join(out, f"{i:02d}.jpg"), type="jpeg", quality=93)
            os.remove(hp)
            print(os.path.join(out, f"{i:02d}.jpg"))
        b.close()


if __name__ == "__main__":
    main()
