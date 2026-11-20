# Tax.Log 카드뉴스 메인 캐릭터·그림체 바이블 (사용자 확정 2026-11-18, 카드 그림 최우선 기준)

> 적용 범위: **인스타 카드뉴스 그림만**. 릴스는 기존 실사진(Unsplash) 방식 그대로(사용자 확정 2026-11-18).
> 기준 이미지: `bgrade/ref/main_char_ref1.webp`(주인공이 손가락을 치켜든 장면), `bgrade/ref/main_char_ref2.webp`(주인공이 폰을 들고 절규하는 장면).
> 이 문서가 bgrade/STYLE_GUIDE.md 의 이전 기준(three.js 렌더, 반실사 저폴리)보다 우선이에요.

## 1. 목표
경제 상황을 하나의 재미있는 만화 장면으로 재해석해, 웃고 놀라고 공감하면서 경제정보를 이해하게 만든다. "그림은 B급 만화, 정보는 A급." 고유한 메인 캐릭터 + 일관된 PS1 시절 반실사 저폴리 3D 그림체를 가진 경제 시사 만화 브랜드.

## 2. 메인 캐릭터 (모든 카드의 중심 주인공, 가상 인물)
- ★ 2026-11-20 사용자 지적 반영: 기준은 ref1·2 그대로 = PS1/구형 FPS 시절 반실사 저폴리 3D 캐릭터. 사람 머리 모양·성인 비율, 깎은 듯한 각진 턱·광대, 얼굴·손·정장에 큼직하게 보이는 저해상도 픽셀 텍스처. **마인크래프트·복셀(정육면체 머리, 네모 눈, 레고 같은 몸)은 금지** — 11/19 카드처럼 큐브 머리로 나오면 다시 생성.
- 짙은 갈색 짧은 머리(옆가르마), 굵고 뚜렷한 짙은 눈썹, 각진 턱, 개성 있는 얼굴
- 짙은 남색 정장 + 흰 셔츠 + 파란 넥타이
- 표정·감정·자세·동작·상황에 따른 의상 변화는 자유. 같은 표정·자세 반복 금지. 분노·기쁨·놀람·당황·좌절·의문을 과장되게.

## 3. 그림체 (절대 흔들리지 않게)
반드시: 반실사 저폴리 3D 입체(사람 얼굴), 각진 면과 큼직한 픽셀 텍스처, 자연스러운 3D 조명과 그림자, 과장된 표정, 영화적 카메라(로우앵글·클로즈업·원근 과장), 역동적 만화 연출, 회색 석조·벽돌 건물과 파란 하늘(장면에 따라 객장·은행·마트 등 배경 변경 가능), 원본과 어울리는 색감.
금지: 마인크래프트·복셀·큐브 머리, 2D 웹툰, 일본 애니, 디즈니·픽사풍, 실사 사진, 매끈한 일반 3D 애니, 콘텐츠마다 다른 그림체, '마인크래프트' 키워드만 넣고 원본 특징 무시.
조연(직장인·개미 투자자·CEO 역할·중앙은행 관계자 역할·시민)도 모두 같은 PS1 반실사 저폴리 세계관으로.

## 4. 연출
- 단순히 서 있는 그림 X. 장면마다 감정과 상황이 분명하게. 뉴스 발견 장면만 반복하지 않기.
- 사용 가능: 극단적 클로즈업, 로우·하이 앵글, 인물 간 대립·상호작용, 땀방울, 빨간 느낌표·물음표, 충격파·속도선, 빨강/파랑 강조, 숫자 없는 그래프(빨간 하락선·초록 상승선), 뉴스 속보 화면 느낌(글자 없이).
- 상황 예: 객장에서 폭락 목격 후 절규, 은행 창구에서 대출금리 보고 충격, 환율 급등에 여행 가방 내려놓기, 장바구니 들고 한숨, 급등에 환호하다 반전에 당황.
- 5장 안에서 카메라 구도·인물 배치·배경을 매번 다르게.

## 5. 계정 규정과 맞춘 안전선 (사실 확인 규칙과 함께 꼭 지킴)
- **그림 안 글자·숫자는 AI로 그리지 않는다**(프롬프트에 "no text, no letters, no numbers, no logos"). AI가 글자를 뭉개고 숫자를 지어내기 때문. 숫자·지명·지수는 카드 글(make_cards_mz.py 텍스트)로만 전달. 레퍼런스 속 'KOSPI 2,393.36' 같은 가짜 수치, 'Mini SUDDEN ATTACK' 같은 실존 게임 로고는 넣지 않는다.
- 말풍선 대사가 필요하면 주인공·가상 인물의 짧은 감탄(예: "또?!")만, 그림이 아니라 카드 글/별도 오버레이로. 실존 인물 입에 실제 하지 않은 말을 넣지 않는다.
- 실존 인물(트럼프·정상·CEO·정치인 등): 사용자가 따로 정하지 않아 기본값으로 **얼굴은 닮게 만들지 않고 머리 모양·옷차림·소품으로만 연상**(2026-11-16 확정 규칙 유지). 발표·연설 같은 중립 장면만, 비하·조롱·스캔들·루머 연출 X, 그림에 실명·로고 X(누구인지는 카드 글이 전달). 일반인·사적 인물은 절대 X.
- 연출은 확인된 사실에 맞게만. 손가락 위로·환호 등으로 반등·급락 전망을 암시하지 않는다. 특정 집단(외국인 투자자 등)을 돈가방 들고 도망치는 식의 고정관념으로 그리지 않는다.

## 6. 제작 파이프라인
1. Hugging Face 이미지 생성(Z-Image-Turbo 우선, 안 되면 FLUX.1-Krea-dev). 해상도 "864x1152 ( 3:4 )".
2. 프롬프트 틀(영어, 장면 부분만 바꾼다):
   "Screenshot from a 1999 PlayStation 1 era 3D game, semi-realistic low-poly human characters with realistic adult proportions and natural human head shapes, faceted angular jaw and cheekbones, chunky pixelated low-resolution textures on faces, hands and clothes, simple game-engine lighting, cinematic low-angle camera, exaggerated cartoon expressions. Main character: a fictional young Korean man with a square jaw, thick dark eyebrows, short dark-brown side-parted hair, dark navy suit, white shirt and blue tie, <표정·동작>. <조연·소품·효과>. Background: <배경, 기본: grey stone-brick buildings under a bright blue sky with wispy clouds>. Not Minecraft, not voxel, no cube-shaped heads, no blocky Lego bodies. No text, no letters, no numbers, no logos."
   - 얼굴이 화면 위쪽 40% 안에 오게: "character's head in the upper third of the frame" 추가.
3. 후처리: 위에서 0~40px 아래부터 4:5로 잘라 `python3 bgrade/retro.py crop.png bgN.jpg 1080 1350 3 1.0 128` (factor 3 = 레퍼런스처럼 큼직한 픽셀).
4. posts/YYYY-MM-DD/scenes/ 에 raw1~5.webp, bg1~5.jpg, prompts.txt(장면별 프롬프트) 저장.
5. Read로 한 장씩 보며 그림체 일관성(주인공 머리·눈썹·정장·넥타이 색), 글에 얼굴이 가리지 않는지, 그림 속 글자가 생기지 않았는지 확인. 어긋나면 그 장만 다시 생성.
6. 무료 생성 한도(ZeroGPU, 하루 약 5~7장)가 바닥나면 그날 카드는 보류하고 이유를 알린다(사용자 최종 결정 2026-11-19). three.js 블록 렌더(bgrade/render.py)는 마인크래프트처럼 보여 기준 미달이라 절대 쓰지 않는다. 실사진 대체도 금지.
