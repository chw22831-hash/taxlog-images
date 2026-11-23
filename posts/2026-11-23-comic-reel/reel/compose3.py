import sys, json, html, re
from playwright.sync_api import sync_playwright
R='/home/claude/taxlog-images'; D=sys.argv[1]
S=json.load(open(f'{D}/subs.json'))
def fmt(t):
    t=html.escape(t); t=re.sub(r"\[(.+?)\]",r'<span style="color:#FFD43B">\1</span>',t); return t.replace("\n","<br>")
wm='<div style="position:absolute;top:120px;right:80px;font-weight:900;font-size:36px;color:#fff;letter-spacing:-0.03em;text-shadow:0 2px 8px rgba(0,0,0,.5)">Tax.Log</div>'
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1920})
    for k,lines in enumerate(S,1):
        css=("@font-face{font-family:P;src:url('file://%s/fonts/Pretendard-Bold.otf');font-weight:700}"
             "@font-face{font-family:P;src:url('file://%s/fonts/Pretendard-Black.otf');font-weight:900}"
             "body{margin:0;width:1080px;height:1920px;font-family:P;background:url('file://%s/r%d.jpg') 0 0/1080px 1920px}"
             ".sub{position:absolute;left:0;right:0;bottom:400px;display:flex;justify-content:center}"
             ".sub div{max-width:900px;background:rgba(0,0,0,.62);color:#fff;font-weight:700;font-size:54px;line-height:1.38;"
             "letter-spacing:-0.03em;text-align:center;padding:22px 40px;border-radius:14px;word-break:keep-all}")%(R,R,D,k)
        for j,t in enumerate(lines,1):
            open(f'{D}/u{k}_{j}.html','w').write(f'<html><head><meta charset=utf-8><style>{css}</style></head><body><div class="sub"><div>{fmt(t)}</div></div>{wm}</body></html>')
            pg.goto(f'file://{D}/u{k}_{j}.html'); pg.wait_for_timeout(200); pg.screenshot(path=f'{D}/t{k}_{j}.png')
    b.close()
