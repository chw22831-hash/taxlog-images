#!/usr/bin/env python3
"""B급 3D 장면 렌더러(2000년대 초반 PC FPS 스크린샷 느낌).

사용법: python3 bgrade/render.py scene.json out.jpg [W H]
  기본 출력 1080x1350(카드). 릴스용은 1080 1920.
scene.json 형식은 bgrade/README.md 참고. 저해상도(render_w x render_h)로 그린 뒤 확대해 투박한 질감을 낸다.
three.js 는 bgrade/vendor/three.min.js (MIT) 를 쓴다.
"""
import json, os, sys
from PIL import Image, ImageFilter
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    spec = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    W = int(sys.argv[3]) if len(sys.argv) > 3 else 1080
    H = int(sys.argv[4]) if len(sys.argv) > 4 else 1350
    spec.setdefault("render_w", round(W / 2.5))
    spec.setdefault("render_h", round(H / 2.5))
    three = open(os.path.join(HERE, "vendor", "three.min.js")).read()
    scene_js = open(os.path.join(HERE, "scene.js")).read()
    html = ("<html><body style='margin:0;background:#000'>"
            f"<script>{three}</script><script>window.SCENE={json.dumps(spec)};</script>"
            f"<script>{scene_js}</script></body></html>")
    tmp = out + ".raw.png"
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = b.new_page(viewport={"width": spec["render_w"], "height": spec["render_h"]})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.set_content(html)
        pg.wait_for_function("window.DONE === true", timeout=20000)
        pg.locator("canvas").screenshot(path=tmp)
        b.close()
        if errs:
            print("JS errors:", errs)
    im = Image.open(tmp).convert("RGB")
    # 옛날 게임 화면: 살짝 뭉개진 확대 + 약한 색 단계 감소
    im = im.resize((W, H), Image.BILINEAR).filter(ImageFilter.SMOOTH)
    im = im.quantize(colors=96, dither=Image.Dither.NONE).convert("RGB")
    im.save(out, quality=88)
    os.remove(tmp)
    print(out)


if __name__ == "__main__":
    main()
