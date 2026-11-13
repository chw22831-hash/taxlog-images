#!/usr/bin/env python3
"""게시물 하나에 쓸 배경 사진을 고르고 spec.json에 채워 넣는다.

규칙(사용자 요청 2026-11-13): 사진을 한 게시물에 몰아 쓰지 않는다.
- 한 게시물에 서로 다른 사진은 최대 2장(표지 1장 + 본문용 1장). 본문 장들은 같은 사진을
  위치(pos)를 바꿔 잘라 쓰고, 일부 장은 표지 사진을 다시 잘라 쓴다.
- 가장 오래 안 쓴(또는 한 번도 안 쓴) 사진부터 고르고, 직전 게시물 표지 사진은 표지로 다시 쓰지 않는다.
- 사용 기록은 photos/catalog.json 의 used 에 날짜로 남긴다.

사용법: python3 pick_photos.py posts/YYYY-MM-DD/spec.json YYYY-MM-DD [--dry]
"""
import json, sys

CAT = "photos/catalog.json"


def last(p):
    return max(p["used"]) if p["used"] else ""


def main():
    spec_p, day = sys.argv[1], sys.argv[2]
    dry = "--dry" in sys.argv
    cat = json.load(open(CAT, encoding="utf-8"))
    ph = cat["photos"]
    recent_cover = max((p for p in ph if p["used"]), key=last, default=None)
    covers = sorted([p for p in ph if p["cover_ok"] and p is not recent_cover], key=last)
    cover = covers[0]
    rest = sorted([p for p in ph if p is not cover], key=last)
    body = rest[0]
    spec = json.load(open(spec_p, encoding="utf-8"))
    bi = 0
    for i, s in enumerate(spec["slides"]):
        if s["type"] == "cover":
            s["photo"], s["pos"] = "photos/" + cover["file"], cover["pos"][0]
        else:
            src = body if i % 3 != 0 else cover  # 본문은 주로 두 번째 사진, 가끔 표지 사진을 다르게 잘라 씀
            s["photo"] = "photos/" + src["file"]
            s["pos"] = src["pos"][bi % len(src["pos"])] if src is body else src["pos"][-1]
            bi += 1
    if not dry:
        json.dump(spec, open(spec_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        for p in (cover, body):
            p["used"].append(day)
        json.dump(cat, open(CAT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("cover:", cover["file"], "| body:", body["file"])


if __name__ == "__main__":
    main()
