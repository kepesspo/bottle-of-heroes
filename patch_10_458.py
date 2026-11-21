# v10.458 — Gender Reveal: a videó MINDIG hanggal (hangerő a Szülőknél) + lágy átmenet a videó után
import sys
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.457';", "const APP_VERSION = 'v10.458';")

# ── konstansok + lágy konfetti-eső ─────────────────────────────────────────────
rep("const REVEAL_COUNT_FROM = 10;",
"""const REVEAL_COUNT_FROM = 10;
// v10.458: a videó hangereje (Szülők → Leleplezés). NINCS „némítva" opció — a videó mindig hanggal megy.
const REVEAL_VOLS = [0.25, 0.5, 0.75, 1];
function revealVolOf(v) { const n = +((v || {}).vol); return REVEAL_VOLS.includes(n) ? n : 1; }
// v10.458: a videó UTOLSÓ másodperceiben a kép a kiderült pasztellbe, a hang a csendbe úszik,
// utána a szín lassan feloldódik a polaroid-fal fölött, lágy konfetti-esővel — nincs éles vágás.
const REVEAL_OUTRO_FADE = 2.5;     // mp — ennyi ideig úszik ki a videó vége (rövid videónál a harmada)
const REVEAL_OUTRO_MS = 7000;      // ms — a feloldódás + konfetti-eső hossza a fal fölött""")

rep("""function RevealConfetti({ colors }) {""",
"""// v10.458: LÁGY konfetti-eső (felülről, lassan, ringatózva) — a videó utáni átmenethez. A robbanás
// `RevealConfetti`-je középről lő ki; ez nem robban, csak hullik, és magától elfogy.
function RevealConfettiRain({ colors, ms }) {
  const ref = React.useRef(null);
  React.useEffect(() => {
    const cv = ref.current; if (!cv) return;
    const ctx = cv.getContext('2d'); let raf = 0, dead = false; const t0 = performance.now(), spawnFor = (ms || 7000) * 0.6;
    const fit = () => { cv.width = innerWidth; cv.height = innerHeight; }; fit(); addEventListener('resize', fit);
    const P = [];
    const tick = now => {
      if (dead) return; ctx.clearRect(0, 0, cv.width, cv.height);
      if (now - t0 < spawnFor) for (let i = 0; i < 3; i++) P.push({ x: Math.random() * cv.width, y: -20, vy: 1.2 + Math.random() * 1.8, ph: Math.random() * 6.3, sw: 0.6 + Math.random() * 1.4,
        s: 6 + Math.random() * 8, r: Math.random() * 6, vr: (Math.random() - 0.5) * 0.08, c: colors[(Math.random() * colors.length) | 0] });
      for (let i = P.length - 1; i >= 0; i--) { const p = P[i]; p.y += p.vy; p.ph += 0.03; p.x += Math.sin(p.ph) * p.sw; p.r += p.vr;
        if (p.y > cv.height + 30) { P.splice(i, 1); continue; }
        ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.r); ctx.globalAlpha = 0.85; ctx.fillStyle = p.c; ctx.fillRect(-p.s / 2, -p.s / 4, p.s, p.s / 2); ctx.restore(); }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => { dead = true; cancelAnimationFrame(raf); removeEventListener('resize', fit); };
  }, []);
  return <canvas ref={ref} data-reveal-rain aria-hidden="true" style={{ position:'absolute', inset:0, pointerEvents:'none' }} />;
}
function RevealConfetti({ colors }) {""")

# ── RevealShow ────────────────────────────────────────────────────────────────
rep("function RevealShow({ show, video, onDone }) {", "function RevealShow({ show, video, onDone, onLand, volume }) {")
rep("const [stage, setStage] = React.useState('count');     // count | video | boom",
    "const [stage, setStage] = React.useState('count');     // count | video | outro | boom")
rep("""  const finishVideo = () => onDone();
  const vref = React.useRef(null), vBad = React.useRef(false);""",
"""  // v10.458: …de nem éles vágással: a videó vége a kiderült pasztellbe úszik (`fadeRef`), utána
  // az `outro` szakaszban a szín a polaroid-fal FÖLÖTT oldódik fel, lágy konfetti-esővel.
  const vol = REVEAL_VOLS.includes(+volume) ? +volume : 1;
  const vref = React.useRef(null), vBad = React.useRef(false), fadeRef = React.useRef(null), landed = React.useRef(false);
  const finishVideo = () => {
    if (landed.current) return; landed.current = true;
    const v = vref.current; if (v) try { v.pause(); } catch(e) {}
    setStage('outro'); if (onLand) onLand();
  };""")
rep("""    try { v.currentTime = 0; } catch(e) {}
    const p = v.play();
    if (p && p.catch) p.catch(() => { v.muted = true; setMuted(true); const p2 = v.play(); if (p2 && p2.catch) p2.catch(() => setStage('boom')); });
  }, [stage]);""",
"""    try { v.currentTime = 0; } catch(e) {}
    v.muted = false; v.volume = vol;                       // v10.458: alapból HANGGAL, a Szülők hangerejével
    const p = v.play();
    if (p && p.catch) p.catch(() => { v.muted = true; setMuted(true); const p2 = v.play(); if (p2 && p2.catch) p2.catch(() => setStage('boom')); });
    // a vég kiúsztatása: a hátralévő idő szerint a kép a pasztellbe, a hang a csendbe
    let raf = 0;
    const loop = () => {
      const d = v.duration, f = (d && isFinite(d)) ? Math.min(REVEAL_OUTRO_FADE, d / 3) : 0;
      const k = f > 0 ? Math.max(0, Math.min(1, 1 - (d - v.currentTime) / f)) : 0;
      if (fadeRef.current) fadeRef.current.style.opacity = String(k);
      try { v.volume = Math.max(0, vol * (1 - k)); } catch(e) {}
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
  }, [stage]);
  React.useEffect(() => {
    if (stage !== 'outro') return;
    const t = setTimeout(onDone, REVEAL_OUTRO_MS * sp);
    return () => clearTimeout(t);
  }, [stage]);""")
rep("""      style={{ position:'absolute', inset:0, zIndex:40, overflow:'hidden', background: stage === 'boom' ? `radial-gradient(circle at 50% 55%, ${R.c2}, ${R.c1} 70%)` : REVEAL_PAPER, transition:'background .5s' }}>""",
"""      style={{ position:'absolute', inset:0, zIndex:40, overflow:'hidden', pointerEvents: stage === 'outro' ? 'none' : 'auto',
        background: stage === 'boom' ? `radial-gradient(circle at 50% 55%, ${R.c2}, ${R.c1} 70%)` : stage === 'outro' ? 'transparent' : REVEAL_PAPER, transition:'background .5s' }}>""")
rep("""      {stage === 'video' && (
        <div style={{ position:'absolute', right:18, bottom:18, display:'flex', gap:8 }}>
          {muted && <button data-reveal-unmute onClick={() => { const v = vref.current; if (v) { v.muted = false; v.play().catch(() => {}); } setMuted(false); }} style={{ padding:'8px 14px', borderRadius:999, border:'none', cursor:'pointer', background:'#fff', color:'#1B1830', fontFamily:T.font, fontWeight:900, fontSize:13 }}>🔊 Hang</button>}
          <button data-reveal-skipvideo onClick={finishVideo} style={{ padding:'8px 14px', borderRadius:999, border:'none', cursor:'pointer', background:'rgba(255,255,255,0.18)', color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:13 }}>Tovább ›</button>
        </div>
      )}""",
"""      {stage === 'video' && <div ref={fadeRef} data-reveal-videofade aria-hidden="true" style={{ position:'absolute', inset:0, background:`radial-gradient(circle at 50% 50%, ${R.c2}, ${R.c1} 85%)`, opacity:0, pointerEvents:'none' }} />}
      {stage === 'video' && muted && (
        // ⚠️ Hang NÉLKÜL nem mehet le: ha a böngésző nem engedte a hangos indítást, nagy gomb középen
        <button data-reveal-unmute onClick={() => { const v = vref.current; if (v) { v.muted = false; v.volume = vol; v.play().catch(() => {}); } setMuted(false); }}
          style={{ position:'absolute', left:'50%', top:'50%', transform:'translate(-50%,-50%)', padding:'18px 30px', borderRadius:999, border:'none', cursor:'pointer', background:'#fff', color:'#1B1830',
            fontFamily:T.font, fontWeight:900, fontSize:'clamp(18px, 3vh, 30px)', boxShadow:'0 10px 40px rgba(0,0,0,0.45)', animation:'revealBeat 1.4s ease-in-out infinite' }}>🔊 Hang bekapcsolása</button>
      )}
      {stage === 'video' && (
        <div style={{ position:'absolute', right:18, bottom:18, display:'flex', gap:8 }}>
          <button data-reveal-skipvideo onClick={finishVideo} style={{ padding:'8px 14px', borderRadius:999, border:'none', cursor:'pointer', background:'rgba(255,255,255,0.18)', color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:13 }}>Tovább ›</button>
        </div>
      )}
      {stage === 'outro' && (
        <React.Fragment>
          <div data-reveal-outro aria-hidden="true" style={{ position:'absolute', inset:0, background:`radial-gradient(circle at 50% 50%, ${R.c2}, ${R.c1} 85%)`, animation:`revealOutroFade ${2.8 * sp}s ease-in-out both` }} />
          <RevealConfettiRain colors={[R.c1, R.c2, '#ffffff', '#FFD54F']} ms={REVEAL_OUTRO_MS * sp} />
        </React.Fragment>
      )}""")

# ── keyframe ───────────────────────────────────────────────────────────────────
rep("@keyframes revealRise { from { transform:translateY(0) } to { transform:translateY(-140vh) } }",
    "@keyframes revealRise { from { transform:translateY(0) } to { transform:translateY(-140vh) } }\n@keyframes revealOutroFade { 0% { opacity:1 } 30% { opacity:1 } 100% { opacity:0 } }")

# ── vetítő: hangerő + onLand + „koppints a hanghoz" jelzés ─────────────────────
rep("{show && <RevealShow key={show.run} show={show} video={video && video.url} onDone={finishShow} />}",
    "{show && <RevealShow key={show.run} show={show} video={video && video.url} volume={revealVolOf(ctl.v)} onDone={finishShow}\n        onLand={() => { if (!show.test && REVEAL_RESULTS[show.result]) setRevealed(show.result); }} />}")
rep("""  const [fs, setFs] = React.useState(false);
  // a KÖZÖS vezérlés (telefonos távirányító): beállítások + „következő" jelölő""",
"""  const [fs, setFs] = React.useState(false);
  // v10.458: a böngésző CSAK felhasználói koppintás után enged hangos lejátszást. Ha a vetítő
  // oldalát újratöltötték és még senki nem nyúlt hozzá, a szervezői csip szól (`data-reveal-needtap`).
  const [needTap, setNeedTap] = React.useState(() => { try { return !!(navigator.userActivation && !navigator.userActivation.hasBeenActive); } catch(e) { return false; } });
  React.useEffect(() => {
    if (!needTap) return;
    const off = () => setNeedTap(false);
    addEventListener('pointerdown', off, true); addEventListener('keydown', off, true);
    return () => { removeEventListener('pointerdown', off, true); removeEventListener('keydown', off, true); };
  }, [needTap]);
  // a KÖZÖS vezérlés (telefonos távirányító): beállítások + „következő" jelölő""")
rep("""          <span aria-hidden="true">📷</span><span data-reveal-count>{nPhotos} kép</span>""",
"""          <span aria-hidden="true">📷</span><span data-reveal-count>{nPhotos} kép</span>
          {needTap && video.url && <span data-reveal-needtap style={{ color:'#A3342C' }}><span aria-hidden="true" style={{ opacity:0.35, color:REVEAL_INK }}> · </span>🔇 koppints egyet a videó hangjáért</span>}""")

# ── Szülők: hangerő-sor a videó alatt ───────────────────────────────────────────
rep("""        <RevealVideoRow />
      </section>""",
"""        <RevealVideoRow />
        <RevealVolumeRow />
      </section>""")
rep("function RevealVideoRow() {",
"""// v10.458: a videó hangereje — csak ha van feltöltött videó. Némítás NINCS: hanggal megy.
function RevealVolumeRow() {
  const meta = useRevealDoc('revealVideo'), ctl = useRevealDoc('revealProjector');
  const [msg, flash] = useRevealFlash();
  if (!(meta.v || {}).vid) return null;
  const vol = revealVolOf(ctl.v);
  return rvRow({ tight:true, data:{ 'data-reveal-p-volrow':'' },
    label: <span>Hangerő{msg ? <span style={{ display:'block', marginTop:2 }}>{rvMsg(msg)}</span> : <span style={{ display:'block', fontWeight:700, fontSize:12, color:T.inkSoft, marginTop:2 }}>A videó mindig hanggal megy</span>}</span>,
    right: rvSeg(REVEAL_VOLS.map(n => ({ v:n, t: Math.round(n * 100) + '%' })), vol, n => { revealCtlWrite({ vol:n }); flash('Mentve'); }, 'data-reveal-p-vol', 'Videó hangereje') });
}
function RevealVideoRow() {""")

open(P, 'w', encoding='utf-8').write(s)
print('ok')
