# v10.456 — Leleplezés: lágyabb dobpergés; ha van videó, a végén NINCS „Kisfiú/Kislány"
# robbanás-képernyő (a vetítő marad); a Szülők titkos kártyájáról kikerül a videó-link
# (a videót feltöltik); a vetítő a YouTube-linket figyelmen kívül hagyja.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:140]); s = s.replace(old, new)
rep("const APP_VERSION = 'v10.455';", "const APP_VERSION = 'v10.456';")

# ── lágy dobpergés ─────────────────────────────────────────────────────────────────
rep("""function revealDrumroll(sec) {
  const c = revealAudio(); if (!c) return;
  const t0 = c.currentTime; let t = 0;
  while (t < sec) { const p = t / sec; revealNoise(c, t0 + t, 0.07, 0.12 + 0.4 * p, 600); t += 0.12 - 0.075 * p; }
}""", """// v10.456: a pergés LÁGY — a régi (600 Hz fölötti, hirtelen indított zaj) élesen
// sercegett. Most sávszűrt (≈ 260 Hz körüli, a dob „teste"), puha felfutású ütések, és
// alatta egy halk, mély dübörgés erősödik — a hangerő a végére is mérsékelt marad.
function revealSoftHit(ctx, t, dur, gain) {
  const len = Math.max(1, Math.floor(ctx.sampleRate * dur)), b = ctx.createBuffer(1, len, ctx.sampleRate), d = b.getChannelData(0);
  for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
  const s = ctx.createBufferSource(); s.buffer = b;
  const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 260; bp.Q.value = 0.9;
  const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 1400;
  const g = ctx.createGain(); g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(gain, t + 0.012); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  s.connect(bp); bp.connect(lp); lp.connect(g); g.connect(ctx.destination); s.start(t); s.stop(t + dur + 0.02);
}
function revealDrumroll(sec) {
  const c = revealAudio(); if (!c) return;
  const t0 = c.currentTime; let t = 0;
  while (t < sec) { const p = t / sec; revealSoftHit(c, t0 + t, 0.11, 0.16 + 0.26 * p); t += 0.11 - 0.06 * p; }
  // mély dübörgés alatta (60 Hz körül), lassan erősödik, a végén elhal
  try {
    const o = c.createOscillator(), g = c.createGain(); o.type = 'sine'; o.frequency.value = 62;
    g.gain.setValueAtTime(0.0001, t0); g.gain.linearRampToValueAtTime(0.12, t0 + sec * 0.9); g.gain.exponentialRampToValueAtTime(0.0001, t0 + sec + 0.3);
    o.connect(g); g.connect(c.destination); o.start(t0); o.stop(t0 + sec + 0.4);
  } catch(e) {}
}""")

# ── videó után nincs robbanás-képernyő; YouTube-link nem videó ────────────────────
rep("""  const vidSrc = show.test ? '' : (video || show.videoUrl || '');""",
    """  // ⚠️ YouTube-linket a <video> nem játszik le — figyelmen kívül hagyjuk (a régi mentett link se akasszon)
  const vidSrc = show.test ? '' : (video || (show.videoUrl && !revealIsYoutube(show.videoUrl) ? show.videoUrl : ''));
  // v10.456: ha a videó LEMENT, a végén nincs „Kisfiú/Kislány" robbanás — a videó maga a
  // leleplezés, utána rögtön a vetítő jön (a kiderült színnel). Hibás/nem induló videónál
  // marad a robbanás, különben semmi nem mondaná ki az eredményt.
  const finishVideo = () => onDone();""")
rep("""onEnded={() => setStage('boom')}""", """onEnded={finishVideo}""")
rep("""<button data-reveal-skipvideo onClick={() => setStage('boom')}""", """<button data-reveal-skipvideo onClick={finishVideo}""")

# ── a titkos kártyáról a videó-link ki ─────────────────────────────────────────────
i = s.index("      {lbl('Videó-link (nem kötelező)')}")
j = s.index("      <div style={{ display:'flex', alignItems:'center', gap:10, marginTop:14, flexWrap:'wrap' }}>\n        <span data-reveal-p-state", i)
s = s[:i] + s[j:]
rep("""  const [url, setUrl] = React.useState(null);
""", "")
rep("""  const codeV = code === null ? (sec.code || '') : code, urlV = url === null ? (sec.videoUrl || '') : url;""",
    """  const codeV = code === null ? (sec.code || '') : code;""")
rep("""  const urlT = React.useRef(null);
  const onUrl = v => { setUrl(v); clearTimeout(urlT.current); urlT.current = setTimeout(() => save({ videoUrl: v.trim() }), 600); };
  React.useEffect(() => () => clearTimeout(urlT.current), []);
""", "")

# ── a szülők tudják az eredményt: a régi mondat már nem igaz ──────────────────────
rep("""'Az eredményt ti sem látjátok — a vetítő mu""", """'A vetítő mu""")
open(P, 'w', encoding='utf-8').write(s); print('ok')
