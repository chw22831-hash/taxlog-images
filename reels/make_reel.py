#!/usr/bin/env python3
"""Tax.Log 릴스(9:16, 1080x1920) 생성기 — 카드뉴스와 같은 사진·톤.

사용법: python3 reels/make_reel.py reel.json out_dir
  → out_dir/reel.mp4, out_dir/cover.jpg

reel.json
{
 "bgm": false,   # 기본: 음악 없음(앱에서 인기곡 직접 선택). {"seed":..,"key":..}이면 make_bgm.py 자체 합성 음원
 "scene_sec": 5.6, "xfade": 0.5,
 "scenes": [
  {"photo": "photos/unsplash/<id>.jpg", "pos": "center", "cover": true,
   "lines": ["첫 줄", "둘째 줄", "[노란 줄]"]},
  {"photo": "...", "headline": "엔비디아 [17일 실적]", "points": ["한 줄", "**굵게** 한 줄"],
   "follow": "(마지막만) ...", "foot": "(마지막만) 출처·면책"}
 ]
}
규칙: [대괄호]=노란 강조, **별표**=굵게. 화면 아래 약 330px·오른쪽 약 160px은 릴스 UI 자리라 글을 두지 않는다.
"""
import html, json, os, re, subprocess, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "fonts")
W, H = 1080, 1920
FPS = 30


def fmt(t):
    t = html.escape(t)
    t = re.sub(r"\[(.+?)\]", r'<span class="y">\1</span>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return t.replace("\n", "<br>")


CSS = """
@font-face{font-family:P;src:url('file://FONTS/Pretendard-Regular.otf');font-weight:400}
@font-face{font-family:P;src:url('file://FONTS/Pretendard-SemiBold.otf');font-weight:600}
@font-face{font-family:P;src:url('file://FONTS/Pretendard-Bold.otf');font-weight:700}
@font-face{font-family:P;src:url('file://FONTS/Pretendard-ExtraBold.otf');font-weight:800}
@font-face{font-family:P;src:url('file://FONTS/Pretendard-Black.otf');font-weight:900}
html,body{margin:0;width:1080px;height:1920px;overflow:hidden;background:transparent;font-family:P,sans-serif;
 letter-spacing:-0.02em;word-break:keep-all;color:#fff}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.18) 0%,rgba(0,0,0,0) 22%,
 rgba(0,0,0,0) 28%,rgba(0,0,0,.72) 44%,rgba(0,0,0,.88) 62%,rgba(0,0,0,.92) 100%)}
.box{position:absolute;left:80px;right:150px;bottom:360px}
.y{color:#FFD43B}
h1{margin:0;font-weight:800;font-size:92px;line-height:1.22;letter-spacing:-0.035em;text-shadow:0 2px 18px rgba(0,0,0,.35)}
h2{margin:0 0 44px;font-weight:800;font-size:78px;line-height:1.24;letter-spacing:-0.035em}
.pt{font-weight:500;font-size:44px;line-height:1.5;margin:0 0 22px;color:#ededed}
.pt b{font-weight:800;color:#fff}
.follow{margin-top:50px;padding-top:34px;border-top:1px solid rgba(255,255,255,.25);font-weight:700;font-size:40px;line-height:1.45}
.foot{margin-top:26px;font-size:22px;line-height:1.5;color:#b3b3b3}
.wm{position:absolute;top:120px;right:80px;font-weight:900;font-size:36px;letter-spacing:-0.03em;opacity:.95}
.hide{visibility:hidden}
"""


def page_html(sc, part):
    """part: 'a' = 그라데이션+제목+로고, 'b' = 나머지(포인트·팔로우·출처). 같은 레이아웃에서 반대쪽을 숨겨 위치를 맞춘다."""
    ha = "" if part == "a" else " hide"
    hb = "" if part == "b" else " hide"
    shade = '<div class="shade"></div><div class="wm">Tax.Log</div>' if part == "a" else ""
    if sc.get("cover"):
        lines = "<br>".join(fmt(l) for l in sc["lines"])
        inner = f'<h1 class="{ha.strip()}">{lines}</h1>'
    else:
        inner = f'<h2 class="{ha.strip()}">{fmt(sc["headline"])}</h2>'
        for p in sc.get("points", []):
            inner += f'<div class="pt{hb}">{fmt(p)}</div>'
        if sc.get("follow"):
            inner += f'<div class="follow{hb}">{fmt(sc["follow"])}</div>'
        if sc.get("foot"):
            inner += f'<div class="foot{hb}">{fmt(sc["foot"])}</div>'
    return f"<html><head><style>{CSS.replace('FONTS', FONTS)}</style></head><body>{shade}<div class='box'>{inner}</div></body></html>"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-3000:])
        raise SystemExit(r.returncode)


def main():
    spec = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    tmp = os.path.join(out, "_tmp")
    os.makedirs(tmp, exist_ok=True)
    S = float(spec.get("scene_sec", 5.6))
    X = float(spec.get("xfade", 0.5))
    scenes = spec["scenes"]

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        for i, sc in enumerate(scenes):
            for part in ("a", "b"):
                pg.set_content(page_html(sc, part))
                pg.wait_for_timeout(150)
                pg.screenshot(path=f"{tmp}/t{i}{part}.png", omit_background=True)
        b.close()

    # 장면별 클립: 사진은 고정(확대·축소 없음, 2026-11-16 사용자 요청) + 제목 페이드인 + 포인트 늦게 페이드인
    clips = []
    for i, sc in enumerate(scenes):
        photo = os.path.join(ROOT, sc["photo"])
        clip = f"{tmp}/c{i}.mp4"
        fc = (
            f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
            f"eq=brightness=-0.03:saturation=0.95[bg];"
            f"[1:v]format=rgba,fade=t=in:st=0.25:d=0.6:alpha=1[a];"
            f"[2:v]format=rgba,fade=t=in:st={1.3 if not sc.get('cover') else 0}:d=0.6:alpha=1[b];"
            f"[bg][a]overlay=0:0:shortest=1[v1];[v1][b]overlay=0:0:shortest=1,format=yuv420p[v]"
        )
        run(["ffmpeg", "-y", "-loop", "1", "-i", photo, "-loop", "1", "-i", f"{tmp}/t{i}a.png",
             "-loop", "1", "-i", f"{tmp}/t{i}b.png", "-filter_complex", fc, "-map", "[v]",
             "-t", f"{S}", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "18", clip])
        clips.append(clip)

    # 크로스페이드로 잇기
    inputs = []
    for c in clips:
        inputs += ["-i", c]
    fc = ""
    prev = "[0:v]"
    for i in range(1, len(clips)):
        off = i * (S - X)
        lab = f"[x{i}]"
        fc += f"{prev}[{i}:v]xfade=transition=fade:duration={X}:offset={off:.3f}{lab};"
        prev = lab
    total = len(clips) * S - (len(clips) - 1) * X
    silent = f"{tmp}/silent.mp4"
    run(["ffmpeg", "-y", *inputs, "-filter_complex", fc.rstrip(";"), "-map", prev, "-c:v", "libx264",
         "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), silent])

    bgm = spec.get("bgm", {})
    final = os.path.join(out, "reel.mp4")
    if bgm is False:
        # 음악 없는 영상(사용자가 인스타 앱에서 인기곡을 골라 직접 올림, 2026-11-16 요청)
        run(["ffmpeg", "-y", "-i", silent, "-c:v", "copy", "-an", "-movflags", "+faststart", final])
    else:
        wav = f"{tmp}/bgm.wav"
        run([sys.executable, os.path.join(ROOT, "reels", "make_bgm.py"), wav, f"{total:.2f}",
             str(bgm.get("seed", 0)), bgm.get("key", "D")])
        run(["ffmpeg", "-y", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
             "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final])
    # 커버: 첫 장면 1.2초 지점
    run(["ffmpeg", "-y", "-ss", "1.2", "-i", final, "-frames:v", "1", "-q:v", "2", os.path.join(out, "cover.jpg")])
    print(final, f"{total:.1f}s")


if __name__ == "__main__":
    main()
