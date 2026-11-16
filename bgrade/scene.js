// Tax.Log B급 3D 씬 빌더 — 2000년대 초반 PC FPS 느낌의 저폴리곤 캐릭터 + 투박한 맵.
// render.py 가 headless Chromium(WebGL)에서 이 파일을 실행한다. 외부 에셋 없이 전부 코드·캔버스 텍스처로 만든다.
/* global THREE */
(function () {
  const S = window.SCENE;
  const RW = S.render_w || 432, RH = S.render_h || 540; // 저해상도로 그린 뒤 확대 → 옛날 게임 화면 느낌
  const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(RW, RH);
  document.body.appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  const sky = S.sky || ["#5fa9ea", "#d4ecfb"];
  scene.background = gradTex(sky[0], sky[1]);
  scene.fog = new THREE.Fog(S.fog || "#b9c4c8", 14, 46);
  const cam = new THREE.PerspectiveCamera(S.cam?.fov || 55, RW / RH, 0.1, 200);
  const cp = S.cam?.pos || [0, 2.2, 6.2], ct = S.cam?.target || [0, 1.5, 0];
  cam.position.set(...cp); cam.lookAt(...ct);
  // 밋밋한 게임 엔진 조명: 앰비언트 + 방향광 하나, 그림자 없음
  scene.add(new THREE.AmbientLight(0xffffff, 0.78));
  const sun = new THREE.DirectionalLight(0xfff2dc, 0.75); sun.position.set(4, 9, 6); scene.add(sun);

  // ---------- 텍스처 ----------
  function rnd(seed) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
  function canvasTex(w, h, draw, rep) {
    const c = document.createElement("canvas"); c.width = w; c.height = h;
    const g = c.getContext("2d"); g.imageSmoothingEnabled = false; draw(g, w, h);
    const t = new THREE.CanvasTexture(c);
    t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; t.generateMipmaps = false;
    if (rep) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep[0], rep[1]); }
    return t;
  }
  function gradTex(a, b) {
    return canvasTex(4, 64, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, a); gr.addColorStop(1, b); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
  }
  function noise(g, w, h, base, amp, seed) {
    const r = rnd(seed || 7); const c = new THREE.Color(base);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const k = 1 + (r() - 0.5) * amp; g.fillStyle = `rgb(${c.r * 255 * k | 0},${c.g * 255 * k | 0},${c.b * 255 * k | 0})`; g.fillRect(x, y, 1, 1);
    }
  }
  const TX = {
    concrete: (rep) => canvasTex(32, 32, (g, w, h) => { noise(g, w, h, "#9a9890", 0.18, 3); g.fillStyle = "rgba(0,0,0,.18)"; g.fillRect(0, 15, w, 1); g.fillRect(15, 0, 1, 15); g.fillRect(4, 16, 1, 16); }, rep),
    brick: (rep) => canvasTex(32, 32, (g, w, h) => { noise(g, w, h, "#8e4a35", 0.25, 5); g.fillStyle = "#6d675e"; for (let y = 0; y < h; y += 8) { g.fillRect(0, y, w, 1); for (let x = (y / 8) % 2 ? 0 : 8; x < w; x += 16) g.fillRect(x, y, 1, 8); } }, rep),
    asphalt: (rep) => canvasTex(32, 32, (g, w, h) => { noise(g, w, h, "#55575a", 0.3, 9); }, rep),
    wood: (rep) => canvasTex(16, 16, (g, w, h) => { noise(g, w, h, "#9c7444", 0.2, 11); g.fillStyle = "#5b3f1f"; g.fillRect(0, 0, w, 1); g.fillRect(0, h - 1, w, 1); g.fillRect(0, 0, 1, h); g.fillRect(w - 1, 0, 1, h); for (let i = 0; i < w; i++) g.fillRect(i, i, 1, 1); }, rep),
    metal: (rep) => canvasTex(16, 16, (g, w, h) => { noise(g, w, h, "#5f6b63", 0.15, 13); g.fillStyle = "rgba(0,0,0,.25)"; g.fillRect(0, 7, w, 1); }, rep),
  };
  const lam = (opt) => new THREE.MeshLambertMaterial(Object.assign({ flatShading: true }, opt));
  const col = (c) => lam({ color: c });

  // ---------- 맵(배경) ----------
  function box(w, h, d, mat, x, y, z, ry) { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat); m.position.set(x, y, z); m.rotation.y = ry || 0; scene.add(m); return m; }
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(120, 120), lam({ map: TX.asphalt([40, 40]) }));
  ground.rotation.x = -Math.PI / 2; scene.add(ground);
  const map = S.map || "alley";
  if (map === "alley" || map === "street") {
    box(30, 9, 1, lam({ map: TX.brick([10, 3]) }), 0, 4.5, -9);
    box(1, 7, 30, lam({ map: TX.concrete([8, 2]) }), -10, 3.5, 0);
    box(1, 6, 30, lam({ map: TX.concrete([8, 2]) }), 11, 3, 0);
    box(6, 3, 1, lam({ map: TX.concrete([2, 1]) }), 6.5, 1.5, -6);
    box(1.4, 1.4, 1.4, lam({ map: TX.wood() }), -3.9, 0.7, -3.2, 0.3);
    box(1.4, 1.4, 1.4, lam({ map: TX.wood() }), -3.7, 2.1, -3.3, -0.2);
    box(1.4, 1.4, 1.4, lam({ map: TX.wood() }), -5.3, 0.7, -3.9, 0.1);
    box(2.2, 1.2, 1.1, lam({ map: TX.metal() }), 4.2, 0.6, -3.4, -0.4);
    if (map === "street") { for (let i = -3; i < 4; i++) box(0.3, 0.02, 2, col("#d8c46a"), 0, 0.02, i * 4); }
  } else if (map === "warehouse") {
    box(30, 10, 1, lam({ map: TX.metal([10, 3]) }), 0, 5, -9);
    box(1, 10, 30, lam({ map: TX.concrete([8, 3]) }), -10, 5, 0);
    for (let i = 0; i < 6; i++) box(1.4, 1.4, 1.4, lam({ map: TX.wood() }), -6 + (i % 3) * 1.5, 0.7 + Math.floor(i / 3) * 1.4, -5);
    box(3, 0.3, 1.5, col("#6b5a3c"), 4.5, 1.2, -4);
  } else if (map === "rooftop") {
    scene.fog.near = 20; scene.fog.far = 70;
    box(30, 1, 1, lam({ map: TX.concrete([10, 1]) }), 0, 0.5, -7);
    for (let i = 0; i < 7; i++) { const h = 6 + (i * 37 % 9); box(4, h, 4, lam({ map: TX.concrete([2, 3]) }), -16 + i * 5.5, h / 2 - 2, -24 - (i % 2) * 6); }
    box(2, 2.5, 2, lam({ map: TX.metal() }), 5, 1.25, -4);
  }

  // 간판(맵 속 표지판처럼): 짧은 글자·숫자·화살표. 실존 로고 금지.
  (S.signs || []).forEach((sg) => {
    const t = canvasTex(64, 32, (g, w, h) => {
      g.fillStyle = sg.bg || "#1d3b2a"; g.fillRect(0, 0, w, h); g.fillStyle = "#e9e3c8"; g.fillRect(1, 1, w - 2, 1); g.fillRect(1, h - 2, w - 2, 1);
      g.fillStyle = sg.fg || "#f0e6a0"; g.font = `bold ${sg.size || 13}px monospace`; g.textAlign = "center"; g.textBaseline = "middle";
      g.fillText(sg.text || "", w / 2, h / 2 + 1);
      if (sg.arrow === "up") { g.fillStyle = "#e33"; g.beginPath(); g.moveTo(56, 6); g.lineTo(61, 14); g.lineTo(51, 14); g.fill(); }
      if (sg.arrow === "down") { g.fillStyle = "#39f"; g.beginPath(); g.moveTo(56, 26); g.lineTo(61, 18); g.lineTo(51, 18); g.fill(); }
    });
    const m = new THREE.Mesh(new THREE.PlaneGeometry(sg.w || 4, (sg.w || 4) / 2), lam({ map: t, flatShading: false }));
    m.position.set(...(sg.pos || [0, 5, -8.4])); m.rotation.y = sg.ry || 0; scene.add(m);
  });

  // ---------- 캐릭터 ----------
  function faceTex(skin, expr, hair) {
    return canvasTex(48, 16, (g, w, h) => {
      g.fillStyle = skin; g.fillRect(0, 0, w, h);
      noise(g, w, h, skin, 0.06, 21);
      // 얼굴은 텍스처 가운데(카메라 쪽)에만 그린다. 픽셀 몇 개짜리 눈·코·입.
      const cx = 24; const E = expr || "neutral";
      g.fillStyle = hair; // 눈썹
      if (E === "angry") { g.fillRect(cx - 6, 4, 3, 1); g.fillRect(cx - 4, 5, 1, 1); g.fillRect(cx + 3, 4, 3, 1); g.fillRect(cx + 3, 5, 1, 1); }
      else if (E === "sad" || E === "cry") { g.fillRect(cx - 6, 5, 3, 1); g.fillRect(cx - 6, 4, 1, 1); g.fillRect(cx + 3, 5, 3, 1); g.fillRect(cx + 5, 4, 1, 1); }
      else if (E === "shock") { g.fillRect(cx - 6, 2, 3, 1); g.fillRect(cx + 3, 2, 3, 1); }
      else { g.fillRect(cx - 6, 4, 3, 1); g.fillRect(cx + 3, 4, 3, 1); }
      // 눈
      if (E === "shock") { g.fillStyle = "#fff"; g.fillRect(cx - 6, 4, 3, 3); g.fillRect(cx + 3, 4, 3, 3); g.fillStyle = "#111"; g.fillRect(cx - 5, 5, 1, 1); g.fillRect(cx + 4, 5, 1, 1); }
      else if (E === "happy" || E === "smug") { g.fillStyle = "#111"; g.fillRect(cx - 6, 6, 3, 1); g.fillRect(cx + 3, 6, 3, 1); g.fillRect(cx - 6, 5, 1, 1); g.fillRect(cx + 5, 5, 1, 1); }
      else { g.fillStyle = "#fff"; g.fillRect(cx - 6, 6, 3, 1); g.fillRect(cx + 3, 6, 3, 1); g.fillStyle = "#111"; g.fillRect(cx - 5, 6, 1, 1); g.fillRect(cx + 4, 6, 1, 1); }
      if (E === "cry") { g.fillStyle = "#6ab8ff"; g.fillRect(cx - 5, 7, 1, 5); g.fillRect(cx + 4, 7, 1, 5); }
      // 코
      g.fillStyle = "rgba(0,0,0,.22)"; g.fillRect(cx, 8, 1, 2);
      // 입
      g.fillStyle = "#5a1f1f";
      if (E === "shock") { g.fillRect(cx - 2, 11, 4, 4); g.fillStyle = "#2a0a0a"; g.fillRect(cx - 1, 12, 2, 2); }
      else if (E === "happy") { g.fillRect(cx - 4, 11, 9, 1); g.fillRect(cx - 3, 12, 7, 2); g.fillStyle = "#fff"; g.fillRect(cx - 3, 12, 7, 1); }
      else if (E === "smug") { g.fillRect(cx - 2, 12, 5, 1); g.fillRect(cx + 3, 11, 1, 1); }
      else if (E === "sad" || E === "cry") { g.fillRect(cx - 3, 13, 7, 1); g.fillRect(cx - 4, 14, 1, 1); g.fillRect(cx + 4, 14, 1, 1); }
      else if (E === "angry") { g.fillRect(cx - 3, 12, 7, 2); }
      else { g.fillRect(cx - 2, 12, 5, 1); }
    });
  }
  function outfitTex(o) {
    return canvasTex(32, 32, (g, w, h) => {
      noise(g, w, h, o.top || "#2b2f3a", 0.12, 31);
      if (o.type === "suit") { // 셔츠 V + 넥타이 (텍스처 가운데 = 정면)
        g.fillStyle = o.shirt || "#e8e8e8"; for (let y = 0; y < 12; y++) g.fillRect(16 - (12 - y) / 2, y, 12 - y, 1);
        g.fillStyle = o.tie || "#b02a2a"; g.fillRect(15, 1, 2, 14); g.fillRect(14, 12, 4, 3);
      } else if (o.type === "hoodie") { g.fillStyle = "rgba(0,0,0,.25)"; g.fillRect(10, 16, 12, 8); g.fillStyle = "#ddd"; g.fillRect(14, 0, 1, 8); g.fillRect(18, 0, 1, 8); }
      else if (o.type === "vest") { g.fillStyle = o.shirt || "#d6d0c0"; g.fillRect(12, 0, 8, 32); g.fillStyle = "#222"; for (let y = 4; y < 30; y += 6) g.fillRect(16, y, 1, 1); }
    });
  }
  function seg(r1, r2, len, mat, n) { // 아래로 늘어진 팔다리 조각(각진 실린더)
    const geo = new THREE.CylinderGeometry(r1, r2, len, n || 5, 1); geo.translate(0, -len / 2, 0);
    return new THREE.Mesh(geo, mat);
  }
  const POSES = {
    idle: { l: [0.1, 0, 0.15], r: [0.1, 0, -0.15], le: 0.2, re: 0.2 },
    hands_up: { l: [0, 0, 2.7], r: [0, 0, -2.7], le: 0.3, re: 0.3 },
    cheer: { l: [0, 0, 2.5], r: [-1.2, 0, -0.3], le: 0.2, re: 1.6 },
    point: { l: [0.1, 0, 0.2], r: [-1.5, 0.3, -0.1], le: 0.2, re: 0.05 },
    facepalm: { l: [0.1, 0, 0.2], r: [-1.3, 0, -0.6], le: 0.2, re: 2.3 },
    hold: { l: [-1.1, 0, 0.25], r: [-1.1, 0, -0.25], le: 0.6, re: 0.6 },
    shrug: { l: [0, 0, 1.0], r: [0, 0, -1.0], le: -1.5, re: -1.5 },
    head_grab: { l: [-0.3, 0, 2.15], r: [-0.3, 0, -2.15], le: 0, re: 0, lez: 2.05, rez: -2.05 },
    wallet_empty: { l: [-0.9, 0.2, 0.5], r: [-0.9, -0.2, -0.5], le: 0.4, re: 0.4 },
  };
  function makeChar(c) {
    const root = new THREE.Group(); const sc = c.scale || 1;
    // SD(미니 FPS식 2.5등신) 기본. S.sd === false 면 일반 비율
    const D = S.sd === false ? { leg: 1.3, lw: 1, torso: 1.15, head: 1, arm: 0.62, hand: 1 } : { leg: 0.62, lw: 1.25, torso: 0.82, head: 1.95, arm: 0.4, hand: 1.5 };
    const o = c.outfit || { type: "suit", top: "#262b36" };
    const skin = c.skin || "#d9a77f", hair = c.hair || "#1b1814";
    const clothM = lam({ map: outfitTex(o) }), sleeveM = col(o.top || "#262b36"), pantsM = col(o.pants || "#1f2128");
    const skinM = col(skin), shoeM = col(o.shoes || "#141414"), hairM = col(hair);
    // 다리
    [-0.2, 0.2].forEach((x, i) => {
      const leg = seg(0.17 * D.lw, 0.13 * D.lw, D.leg, pantsM, 5); leg.position.set(x, D.leg, 0); leg.rotation.z = (i ? -1 : 1) * (c.legSpread || 0.05); root.add(leg);
      const shoe = new THREE.Mesh(new THREE.BoxGeometry(0.26 * D.lw, 0.16 * D.lw, 0.46 * D.lw), shoeM); shoe.position.set(x * 1.15, 0.08, 0.08); root.add(shoe);
    });
    // 몸통(위가 넓은 각진 사다리꼴)
    const torsoG = new THREE.CylinderGeometry(0.46, 0.38, D.torso, 6, 1, false, -Math.PI); const torso = new THREE.Mesh(torsoG, clothM);
    torso.scale.z = 0.66; torso.position.y = D.leg + D.torso / 2; root.add(torso);
    // 목·머리 (머리는 6각 기둥 + 위아래 뚜껑: 복셀이 아닌 구형 FPS 모델 느낌)
    const neck = seg(0.11, 0.12, 0.16, skinM, 5); neck.position.y = D.leg + D.torso + 0.12; root.add(neck);
    const head = new THREE.Group(); head.position.y = D.leg + D.torso + 0.12 + 0.26 * D.head + (c.headLift || 0); head.scale.setScalar(D.head);
    const hg = new THREE.CylinderGeometry(0.29, 0.25, 0.52, 7, 1, false, -Math.PI); const hm = new THREE.Mesh(hg, [lam({ map: faceTex(skin, c.expr, hair) }), hairM, skinM]);
    hm.scale.set(c.headW || 1, 1, 0.92); head.add(hm);
    const crown = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.31, 0.16, 7), hairM); crown.position.y = 0.31; crown.scale.z = 0.95; head.add(crown);
    if (c.hairStyle === "side") { const h2 = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.1, 0.25), hairM); h2.position.set(0.04, 0.27, 0.16); h2.rotation.z = -0.15; head.add(h2); }
    if (c.hairStyle === "long") { const h3 = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.33, 0.6, 7), hairM); h3.position.set(0, -0.08, -0.08); h3.scale.z = 0.8; head.add(h3); }
    if (c.hairStyle === "bald") crown.material = skinM;
    if (c.glasses) { const gl = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.07, 0.05), col("#111")); gl.position.set(0, 0.05, 0.27); head.add(gl); }
    if (c.helmet) { const hm2 = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.34, 0.22, 8), col(c.helmet)); hm2.position.y = 0.3; head.add(hm2); }
    if (c.cap) { const cp = new THREE.Mesh(new THREE.CylinderGeometry(0.31, 0.31, 0.14, 7), col(c.cap)); cp.position.y = 0.33; head.add(cp); const br = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.04, 0.3), col(c.cap)); br.position.set(0, 0.28, 0.3); head.add(br); }
    head.rotation.set(c.headTilt?.[0] || 0, c.headTilt?.[1] || 0, c.headTilt?.[2] || 0);
    root.add(head);
    // 팔
    const POSES_SD = { head_grab: { l: [-0.25, 0, 2.55], r: [-0.25, 0, -2.55], le: 0, re: 0, lez: 1.1, rez: -1.1 }, facepalm: { l: [0.1, 0, 0.2], r: [-1.2, 0, -2.2], le: 0.2, re: 0, rez: -0.6 } };
    const P = (S.sd !== false && POSES_SD[c.pose]) || POSES[c.pose || "idle"] || POSES.idle;
    [["l", 1], ["r", -1]].forEach(([k, s]) => {
      const sh = new THREE.Group(); sh.position.set(0.53 * s, D.leg + D.torso - 0.08, 0);
      const ua = seg(0.13, 0.11, D.arm, sleeveM, 5); sh.add(ua);
      const el = new THREE.Group(); el.position.y = -D.arm; sh.add(el);
      const fa = seg(0.11, 0.09, D.arm * 0.9, sleeveM, 5); el.add(fa);
      const hand = new THREE.Mesh(new THREE.BoxGeometry(0.15 * D.hand, 0.2 * D.hand, 0.13 * D.hand), skinM); hand.position.y = -D.arm * 0.9 - 0.08 * D.hand; el.add(hand);
      sh.rotation.set(P[k][0], P[k][1], P[k][2]); el.rotation.x = -(k === "l" ? P.le : P.re); el.rotation.z = (k === "l" ? P.lez : P.rez) || 0;
      root.add(sh);
      if (c.prop && ((c.propHand || "r") === k)) el.add(makeProp(c.prop, -D.arm * 0.9 - 0.2));
    });
    root.position.set(...(c.pos || [0, 0, 0])); root.rotation.y = c.ry || 0; root.scale.setScalar(sc);
    scene.add(root);
  }
  function makeProp(p, y) {
    const g = new THREE.Group(); g.position.y = y;
    if (p === "money") { for (let i = 0; i < 4; i++) { const b = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.06, 0.2), col(i % 2 ? "#6fa36a" : "#5c8f58")); b.position.y = -i * 0.065; b.rotation.y = i * 0.15; g.add(b); } }
    else if (p === "phone") { const b = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.22, 0.03), col("#111")); g.add(b); }
    else if (p === "briefcase") { const b = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.4, 0.14), col("#4a2e17")); b.position.y = -0.2; g.add(b); }
    else if (p === "chart") {
      const t = canvasTex(32, 32, (q, w, h) => { q.fillStyle = "#f2efe2"; q.fillRect(0, 0, w, h); q.fillStyle = "#c33"; let yy = 26; for (let x = 3; x < 29; x++) { yy += (x % 5 === 0 ? -5 : 1) * 0.6; q.fillRect(x, Math.max(3, yy | 0), 1, 2); } q.fillStyle = "#333"; q.fillRect(2, 2, 1, 28); q.fillRect(2, 29, 28, 1); });
      const b = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.6, 0.03), [col("#ddd"), col("#ddd"), col("#ddd"), col("#ddd"), lam({ map: t }), col("#ccc")]); b.position.y = -0.1; g.add(b);
    }
    else if (p === "receipt") { const b = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.6, 0.01), col("#f4f1e8")); b.position.y = -0.25; g.add(b); }
    return g;
  }
  (S.chars || []).forEach(makeChar);
  // 바닥에 굴러다니는 소품
  (S.items || []).forEach((it) => { const m = makeProp(it.type, 0); m.position.set(...it.pos); m.rotation.y = it.ry || 0; m.scale.setScalar(it.scale || 1); scene.add(m); });

  renderer.render(scene, cam);
  window.DONE = true;
})();
