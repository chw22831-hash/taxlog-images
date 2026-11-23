# 자체 합성 8비트(칩튠) 배경음 — B급 게임 감성, 저작권 없는 오리지널
import sys, numpy as np
from scipy.io import wavfile
SR=44100; out=sys.argv[1]; DUR=float(sys.argv[2]); rng=np.random.default_rng(int(sys.argv[3]))
BPM=132; beat=60/BPM; step=beat/2
def hz(m): return 440*2**((m-69)/12)
def sq(f,n,duty=.5):
    t=np.arange(n)/SR; return np.where((t*f)%1<duty,1.,-1.)
def tri(f,n):
    t=np.arange(n)/SR; return 2*np.abs(2*((t*f)%1)-1)-1
def env(n,a=.005,r=.06):
    e=np.ones(n); A=int(a*SR); R=min(int(r*SR),n)
    e[:A]=np.linspace(0,1,A); e[-R:]*=np.linspace(1,0,R); return e
N=int(DUR*SR); mix=np.zeros(N+SR)
root=60  # C
prog=[[0,4,7],[9,12,16],[5,9,12],[7,11,14]]  # C Am F G
scale=[0,2,4,7,9,12,14,16]
# 2마디 모티프를 만들고 반복·변형
motif=[(rng.choice(scale) if rng.random()>.2 else None) for _ in range(16)]
nsteps=int(DUR/step)
for s in range(nsteps):
    t0=int(s*step*SR); bar=(s//8)%4; ch=prog[bar]
    # 베이스(삼각파) 8분음표
    bn=root-24+ch[0]+(12 if s%2 else 0); n=int(step*SR*.9)
    mix[t0:t0+n]+=.32*tri(hz(bn),n)*env(n)
    # 아르페지오(얇은 사각파 12.5%)
    an=root+ch[s%3]; n2=int(step*SR*.5)
    mix[t0:t0+n2]+=.06*sq(hz(an+12),n2,.125)*env(n2)
    # 리드 멜로디(4마디 뒤부터)
    if s>=16:
        m=motif[s%16]
        if m is not None:
            if (s//16)%2==1 and s%16>=8: m=m+rng.choice([0,2,-3])
            n3=int(step*SR*.85); mix[t0:t0+n3]+=.11*sq(hz(root+12+m),n3,.25)*env(n3,.003,.05)
    # 드럼: 킥(1,3박) 스네어(2,4박) 하이햇
    if s%4==0:
        n4=int(.12*SR); tt=np.arange(n4)/SR; f=np.linspace(150,45,n4)
        mix[t0:t0+n4]+=.5*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*25)
    if s%4==2:
        n5=int(.1*SR); mix[t0:t0+n5]+=.18*rng.uniform(-1,1,n5)*np.exp(-np.arange(n5)/SR*30)
    n6=int(.025*SR); mix[t0:t0+n6]+=.05*rng.uniform(-1,1,n6)*np.exp(-np.arange(n6)/SR*120)
mix=mix[:N]; f=int(.4*SR); mix[:f]*=np.linspace(0,1,f); f=int(1.5*SR); mix[-f:]*=np.linspace(1,0,f)
mix=mix/np.max(np.abs(mix))*.85
wavfile.write(out,SR,(np.stack([mix,mix],1)*32767).astype(np.int16))
