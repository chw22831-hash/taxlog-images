# Tax.Log 카드 고정 이미지 스타일 — 미니서든 B급 3D 그래픽 (사용자 확정 2026-11-16, 카드 기본값)

> "그림은 B급, 정보는 A급." 진지한 경제뉴스를 설명하는데 등장인물은 옛날 저사양 FPS 게임에서 튀어나온 것 같은 웃기고 투박한 3D 캐릭터.

## 1. 핵심 스타일
(2026-11-16 사용자 최종 기준) 사용자가 만든 프로필 사진 느낌이 기준: 일반 성인 비율의 정장 캐릭터를 아래에서 올려다본 구도, 파란 하늘과 구름, 모래색 콘크리트 담·벽돌 건물(창문)·나무 상자가 있는 구형 FPS 맵, 형태는 매끈한 저폴리인데 텍스처(정장 천·벽·손)는 픽셀이 보이는 저해상도. SD(2.5등신)는 기본이 아님("sd": true 일 때만).
초창기 온라인 FPS(미니서든어택/X Operations 시절) 특유의 저폴리곤 3D 게임 그래픽. 현대적인 고퀄리티 일러스트가 아니라 2000년대 초반 PC 게임의 투박하고 어색한 3D 그래픽.

## 2. 그래픽 필수 설정
Low Poly 3D Character · Retro FPS Game Graphics · Early 2000s PC Game Aesthetic · Low Resolution Textures · Pixelated Texture Mapping · Angular and Blocky Character Models · Primitive 3D Geometry · Basic Game Engine Lighting · Slightly Awkward Character Proportions · Low-detail Facial Expressions · Old-school Multiplayer FPS Screenshot

## 3. 캐릭터 표현
- 3D 게임 모델처럼. 머리카락·손·의상은 각진 형태와 단순한 텍스처 우선. 손·얼굴 비율이 약간 어색해도 OK.
- 표정과 포즈는 과장되고 우스꽝스럽게.
- 실존 인물: 얼굴을 닮게 만들지 않는다(초상권·명예 문제, 계정의 '인물 비판 금지' 원칙). 대신 직장인·개미 투자자·정장 차림 경영진·공무원 같은 가상의 역할 캐릭터로 표현하고, 누구인지는 카드 글로 전달한다.

## 4. 배경과 조명
오래된 FPS 맵 같은 배경(콘크리트·벽돌 건물, 상자, 도로, 창고, 옥상). 밋밋한 기본 게임 엔진 조명, 시네마틱 조명 금지. 약간 흐릿하고 낮은 해상도의 텍스처. 실제 게임 플레이 화면을 캡처한 듯한 분위기.

## 5. 절대 금지
고해상도 디지털 일러스트, 픽사·디즈니, 애니메이션 스타일, 사실적인 인물 사진, 현대 AAA·UE5급 렌더, 과도한 피부·머리카락 디테일, 부드럽고 세련된 3D 캐릭터, 깔끔한 카툰. 마인크래프트·복셀 그래픽처럼 만들지 않는다(구형 PC FPS 캐릭터 모델 느낌). 실존 게임의 캐릭터·로고·UI·맵을 그대로 베끼지 않는다. 실존 기업 로고 금지(간판 글자는 KOSPI, IPO, Q3 같은 일반 단어·숫자만, 사실과 맞는 것만).

## 6. 제작 원칙
- 주제·인물·행동·표정·포즈·배경은 매번 요청에 맞게 바꾸되, 3D 그래픽 품질과 질감은 항상 동일.
- 특별한 요청이 없으면 게임 스크린샷 같은 자연스러운 구도. 과장된 표정·상황 연출 적극 사용.
- 웃음은 캐릭터의 어색함과 상황의 부조화에서.

## 구현 (자동 작업용)
- 렌더러: `python3 bgrade/render.py scene.json out.jpg [W H]` (기본 1080x1350). headless Chromium + three.js(bgrade/vendor, MIT)로 1/4 해상도로 그린 뒤 픽셀 그대로(NEAREST) 확대. 기본은 일반 비율 'cs' 스타일(1/2 해상도 렌더, 매끈한 형태 + 픽셀 텍스처, 둥근 머리에 얼굴·머리카락 텍스처). "sd": true 면 SD 2.5등신 + 1/4 해상도 픽셀 화면.
- scene.json: `map`(dust·alley·street·warehouse·rooftop), `cam`{pos,target,fov}, `signs`[{text,arrow:"up"/"down",bg,pos,w,size}], `chars`[{pos,ry,expr,pose,outfit{type:suit/hoodie/vest,top,shirt,tie,pants},skin,hair,hairStyle:swoop/side/long/bald,cap,prop,propHand,headTilt}], `items`[{type,pos,ry,scale}].
  - sd(기본 true) · `chars[].helmet`(색) 추가 가능
  - expr: neutral·stern·shock·happy·smug·sad·cry·angry / pose: point_up·idle·hands_up·cheer·point·facepalm·hold·shrug·head_grab·wallet_empty / prop: money·phone·briefcase·chart·receipt
- 카드 글이 아래쪽 약 45%를 덮으므로 캐릭터 얼굴은 화면 위쪽 절반에 오게 카메라를 잡는다(기본 cs 예: 한 명 클로즈업 로우앵글 cam.pos [0.5,1.6,3.0], target [0,2.75,0], fov 56 / 두세 명이면 cam.pos [0,1.8,5.5], target [0,2.4,0]). map 기본 추천 "dust", sky ["#3f78d6","#9cc0ee"].
- 렌더한 이미지를 make_cards_mz.py spec의 "photo"로 넣는다. 예시: samples/bgrade-v1/.
