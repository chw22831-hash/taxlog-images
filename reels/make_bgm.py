#!/usr/bin/env python3
"""Tax.Log 릴스용 오리지널 배경음 생성기(저작권 걱정 없는 자체 합성 음원).

가사 없는 웅장한 시네마틱 톤: 현악 패드 + 저음 브라스 + 스타카토 오스티나토 + 팀파니/타이코 히트 + 리버브.
사용법: python3 make_bgm.py out.wav [초=26] [seed=0] [key=D]
seed/key를 바꾸면 진행·리듬이 조금씩 달라져 매일 같은 곡 반복을 피할 수 있다.
"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 44100
out = sys.argv[1]
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 26.0
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 0
KEY = sys.argv[4] if len(sys.argv) > 4 else "D"
rng = np.random.default_rng(SEED)

NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
root_midi = 38 + (NOTE[KEY] - 2)  # D2 기준


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# 단조 진행(i - VI - III - VII) 변형들
PROGS = [[0, -4, 3, -2], [0, -4, -2, 3], [0, 3, -2, -4], [0, -4, -7, -2]]
prog = PROGS[SEED % len(PROGS)]
QUAL = {0: "m", -4: "M", 3: "M", -2: "M", -7: "m"}

BPM = 96
beat = 60 / BPM
bar = beat * 4
chord_len = bar * 2 if DUR > 20 else bar
n = int(DUR * SR)
t = np.arange(n) / SR
mix = np.zeros((n, 2))


def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, "low", fs=SR, output="sos"), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x)


def saw(f, tt, detune=0.0):
    ph = (f * (1 + detune)) * tt + rng.random()
    return 2 * (ph - np.floor(ph + 0.5))


def env_adsr(length, a, r):
    e = np.ones(length)
    ai = min(int(a * SR), length)
    ri = min(int(r * SR), length)
    if ai:
        e[:ai] = np.linspace(0, 1, ai)
    if ri:
        e[-ri:] *= np.linspace(1, 0, ri)
    return e


def add(sig, start, pan=0.0, gain=1.0):
    s = int(start * SR)
    if s >= n:
        return
    sig = sig[: n - s]
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    mix[s : s + len(sig), 0] += sig * l * gain
    mix[s : s + len(sig), 1] += sig * r * gain


# 전체 크레센도 곡선
cres = np.clip(0.35 + 0.65 * (t / DUR) ** 0.8, 0, 1)

ci = 0
start = 0.0
while start < DUR:
    off = prog[ci % len(prog)]
    q = QUAL[off]
    r = root_midi + off
    third = 3 if q == "m" else 4
    L = min(chord_len, DUR - start) + 0.6
    tt = np.arange(int(L * SR)) / SR
    e = env_adsr(len(tt), 0.5, 0.7)
    # 현악 패드(중음역 보이싱)
    pad = np.zeros(len(tt))
    for m in [r + 24, r + 24 + third, r + 31, r + 36]:
        for d in (-0.004, 0.0, 0.005):
            pad += saw(hz(m), tt, d)
    pad = lp(pad, 1800) * e / 12
    add(pad, start, pan=-0.35, gain=0.55)
    add(pad * 0.95, start + 0.012, pan=0.35, gain=0.55)
    # 저음 브라스
    brass = (saw(hz(r + 12), tt) + saw(hz(r + 19), tt, 0.003)) * e
    brass = lp(brass, 700) / 2
    add(brass, start, gain=0.38)
    # 서브 베이스
    sub = np.sin(2 * np.pi * hz(r) * tt) * e
    add(sub, start, gain=0.42)
    # 스타카토 오스티나토(8분음표)
    k = 0
    while k * beat / 2 < L - 0.6:
        tn = k * beat / 2
        m = r + 24 + ([0, 0, 7, 0, 12, 7, 0, 7][(k + SEED) % 8])
        ln = int(0.16 * SR)
        st = np.arange(ln) / SR
        note = saw(hz(m), st) * np.exp(-st * 22)
        note = lp(note, 2600)
        acc = 1.0 if k % 4 == 0 else 0.7
        add(note, start + tn, pan=0.5 if k % 2 else -0.5, gain=0.16 * acc)
        k += 1
    # 팀파니/타이코 히트
    for bi in range(int(np.ceil(L / beat))):
        tb = start + bi * beat
        if tb >= start + min(chord_len, DUR - start):
            break
        if bi % 4 in (0, 2) or (start > DUR * 0.55 and bi % 2 == 1 and rng.random() < 0.5):
            ln = int(1.1 * SR)
            st = np.arange(ln) / SR
            f0 = hz(r) * (1.6 if bi % 4 else 1.0)
            fsweep = f0 * (1 + 0.6 * np.exp(-st * 30))
            body = np.sin(2 * np.pi * np.cumsum(fsweep) / SR) * np.exp(-st * 4.5)
            noise = lp(rng.standard_normal(ln), 900) * np.exp(-st * 28) * 0.6
            hit = body + noise
            add(hit, tb, gain=0.55 if bi % 4 == 0 else 0.4)
    start += chord_len
    ci += 1

# 마지막 큰 히트(곡 끝 2.4초 전)
ln = int(2.4 * SR)
st = np.arange(ln) / SR
boom = np.sin(2 * np.pi * np.cumsum(hz(root_midi) * (1 + 0.8 * np.exp(-st * 18))) / SR) * np.exp(-st * 2.2)
boom += lp(rng.standard_normal(ln), 600) * np.exp(-st * 10) * 0.7
add(boom, max(0, DUR - 2.6), gain=0.8)

mix *= cres[:, None]

# 리버브(지수 감쇠 노이즈 IR)
irn = int(2.2 * SR)
it = np.arange(irn) / SR
for ch in range(2):
    ir = rng.standard_normal(irn) * np.exp(-it * 3.0)
    ir = lp(ir, 5000)
    ir /= np.sqrt(np.sum(ir**2))
    wet = fftconvolve(mix[:, ch], ir)[:n]
    mix[:, ch] = mix[:, ch] * 0.75 + wet * 0.35

mix = np.stack([hp(mix[:, 0], 30), hp(mix[:, 1], 30)], 1)
# 페이드 인/아웃
fi, fo = int(0.8 * SR), int(1.8 * SR)
mix[:fi] *= np.linspace(0, 1, fi)[:, None]
mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
# 소프트 리미트 + 노멀라이즈(피크 -1 dBFS)
mix = np.tanh(mix * 1.4)
mix *= 10 ** (-1 / 20) / np.max(np.abs(mix))
wavfile.write(out, SR, (mix * 32767).astype(np.int16))
print(out, f"{DUR:.1f}s seed={SEED} key={KEY}")
