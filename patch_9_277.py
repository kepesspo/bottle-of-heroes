#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. SFX: switch to WAV blob + new Audio() — same pattern as lóverseny
old = """// ─── Sound Effects (Web Audio API) ─────────────────────────────
const SFX = (() => {
  let ctx = null;
  const ac = () => {
    if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
    return ctx;
  };
  const play = (fn) => {
    try {
      const c = ac();
      if (c.state === 'suspended') {
        c.resume().then(() => { try { fn(c); } catch(e) {} }).catch(() => {});
      } else {
        fn(c);
      }
    } catch(e) {}
  };
  const tone = (freq, type, dur, vol, startFreq) => play(c => {
    const o = c.createOscillator(), g = c.createGain();
    o.connect(g); g.connect(c.destination);
    o.type = type; o.frequency.setValueAtTime(startFreq||freq, c.currentTime);
    if (startFreq) o.frequency.exponentialRampToValueAtTime(freq, c.currentTime + dur);
    g.gain.setValueAtTime(vol||0.18, c.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, c.currentTime + dur);
    o.start(c.currentTime); o.stop(c.currentTime + dur);
  });
  return {
    tap:   () => tone(1200, 'sine',     0.04, 0.10),
    win:   () => tone(880,  'sine',     0.35, 0.18, 440),
    lose:  () => tone(160,  'triangle', 0.35, 0.22, 280),
    ding:  () => tone(660,  'sine',     0.50, 0.15, 660),
  };
})();"""
new = """// ─── Sound Effects (WAV blob — same engine as lóverseny) ────────
const SFX = (() => {
  const SR = 22050;
  const mkWav = (samples) => {
    const N = samples.length;
    const buf = new ArrayBuffer(44 + N * 2);
    const v = new DataView(buf);
    const s = (o, t) => [...t].forEach((c, i) => v.setUint8(o + i, c.charCodeAt(0)));
    s(0,'RIFF'); v.setUint32(4, 36 + N*2, true); s(8,'WAVE'); s(12,'fmt ');
    v.setUint32(16,16,true); v.setUint16(20,1,true); v.setUint16(22,1,true);
    v.setUint32(24,SR,true); v.setUint32(28,SR*2,true);
    v.setUint16(32,2,true); v.setUint16(34,16,true);
    s(36,'data'); v.setUint32(40, N*2, true);
    samples.forEach((x, i) => v.setInt16(44 + i*2, Math.max(-32767, Math.min(32767, x|0)), true));
    return URL.createObjectURL(new Blob([buf], {type:'audio/wav'}));
  };
  const gen = (dur, fn) => {
    const N = Math.ceil(SR * dur);
    return mkWav(Array.from({length: N}, (_, i) => fn(i / SR, i / N)));
  };
  // Pre-generate sound URLs once
  const urls = {
    tap:  gen(0.07, (t, p) => Math.sin(2*Math.PI*1100*t) * Math.exp(-t*60) * 0.12 * 32767),
    win:  gen(0.50, (t, p) => Math.sin(2*Math.PI*(400 + 500*p)*t) * Math.exp(-t*3) * 0.22 * 32767),
    lose: gen(0.50, (t, p) => Math.sin(2*Math.PI*(320 - 180*p)*t) * Math.exp(-t*3) * 0.22 * 32767),
    ding: gen(0.60, (t, p) => (Math.sin(2*Math.PI*660*t) + 0.3*Math.sin(2*Math.PI*1320*t)) * Math.exp(-t*4) * 0.18 * 32767),
  };
  const play = (name) => {
    try { const a = new Audio(urls[name]); a.volume = 0.9; a.play().catch(()=>{}); } catch(e) {}
  };
  return { tap:()=>play('tap'), win:()=>play('win'), lose:()=>play('lose'), ding:()=>play('ding') };
})();"""
assert old in html, "FAIL: SFX block"
html = html.replace(old, new, 1)

# ── 2. Add dragIdxRef / overIdxRef next to dragIdx/overIdx state
old = """  const [dragIdx, setDragIdx] = useState(null);
  const [overIdx, setOverIdx] = useState(null);"""
new = """  const [dragIdx, setDragIdx] = useState(null);
  const [overIdx, setOverIdx] = useState(null);
  const dragIdxRef = useRef(null);
  const overIdxRef = useRef(null);"""
assert old in html, "FAIL: dragIdx state"
html = html.replace(old, new, 1)

# ── 3. Sorrend touch handlers: use refs, prevent scroll, fix stale closure
old = """                        onTouchStart={e => { e.currentTarget._startY=e.touches[0].clientY; setDragIdx(i); }}
                          onTouchMove={e => {
                            e.preventDefault();
                            const dy = e.touches[0].clientY - e.currentTarget._startY;
                            const target = Math.max(0, Math.min(players.length-1, i + Math.round(dy/60)));
                            setOverIdx(target);
                          }}
                          onTouchEnd={e => { const oi = overIdx; const di = dragIdx; setDragIdx(null); setOverIdx(null); if(oi!==null && di!==null) movePlayer(di, oi); }}"""
new = """                        onTouchStart={e => { e.currentTarget._startY=e.touches[0].clientY; dragIdxRef.current=i; overIdxRef.current=i; setDragIdx(i); }}
                          onTouchMove={e => {
                            e.preventDefault();
                            const dy = e.touches[0].clientY - e.currentTarget._startY;
                            const target = Math.max(0, Math.min(players.length-1, i + Math.round(dy/60)));
                            overIdxRef.current = target; setOverIdx(target);
                          }}
                          onTouchEnd={e => { const di=dragIdxRef.current, oi=overIdxRef.current; dragIdxRef.current=null; overIdxRef.current=null; setDragIdx(null); setOverIdx(null); if(di!==null && oi!==null && di!==oi) movePlayer(di, oi); }}"""
assert old in html, "FAIL: touch handlers"
html = html.replace(old, new, 1)

# ── 4. Végtelen gyűrű: remove spin animation, show ∞ in center + pulsing arc
old = """                <circle cx="27" cy="27" r={rOuter} fill="none" stroke={ringColor} strokeWidth="2.5"
                  strokeDasharray={isInfinite ? `${circOuter * 0.15} ${circOuter * 0.85}` : circOuter}
                  strokeDashoffset={isInfinite ? 0 : circOuter - dashOuter}
                  strokeLinecap="round"
                  style={{ transition:'stroke-dashoffset 0.5s ease', animation: isInfinite ? 'spin 3s linear infinite' : 'none' }} />
                {/* Inner ring: static background */}
                <circle cx="27" cy="27" r={rInner} fill="none" stroke={T.inkMute} strokeWidth="2" opacity="0.12" />
              </svg>
              <div style={{ position:'absolute', inset:6, background:T.surface, borderRadius:'50%', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
                <div style={{ fontFamily:T.font, fontSize:8, fontWeight:700, color:T.inkSoft, letterSpacing:'0.07em', lineHeight:1 }}>{t('roundLabel')}</div>
                <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color:T.ink, lineHeight:1.1, fontVariantNumeric:'tabular-nums' }}>{round}</div>
              </div>"""
new = """                <circle cx="27" cy="27" r={rOuter} fill="none" stroke={ringColor} strokeWidth="2.5"
                  strokeDasharray={circOuter}
                  strokeDashoffset={isInfinite ? circOuter * 0.25 : circOuter - dashOuter}
                  strokeLinecap="round"
                  style={{ transition:'stroke-dashoffset 0.5s ease', animation:'none' }} />
                {/* Inner ring: static background */}
                <circle cx="27" cy="27" r={rInner} fill="none" stroke={T.inkMute} strokeWidth="2" opacity="0.12" />
              </svg>
              <div style={{ position:'absolute', inset:6, background:T.surface, borderRadius:'50%', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
                {isInfinite ? (
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.coral, lineHeight:1, animation:'pulse 1.4s infinite' }}>∞</div>
                ) : (<>
                  <div style={{ fontFamily:T.font, fontSize:8, fontWeight:700, color:T.inkSoft, letterSpacing:'0.07em', lineHeight:1 }}>{t('roundLabel')}</div>
                  <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color:T.ink, lineHeight:1.1, fontVariantNumeric:'tabular-nums' }}>{round}</div>
                </>)}
              </div>"""
assert old in html, "FAIL: ring inner"
html = html.replace(old, new, 1)

# ── version bump
old_v = "const APP_VERSION = 'v9.276';"
new_v = "const APP_VERSION = 'v9.277';"
assert old_v in html, "FAIL: version"
html = html.replace(old_v, new_v, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.277 — SFX WAV blob, sorrend ref fix, végtelen gyűrű ∞ pulzál")
