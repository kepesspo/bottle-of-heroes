# v10.442 — Babakvíz: borító a kérdések elé ÉS a megoldások elé; a Szülők bármelyik
# oldalra ugorhatnak (nem csak léptethetnek).
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:120]); s = s.replace(old, new)

rep("const APP_VERSION = 'v10.441'", "const APP_VERSION = 'v10.442'")
rep("config/revealQuizState = { phase:'idle'|'q'|'sol'|'end', idx, run, qs }",
    "config/revealQuizState = { phase:'idle'|'cover'|'q'|'solcover'|'sol'|'end', idx, run, qs }")

# ── 1. a lapozás egy LINEÁRIS oldallistán megy: a lépés és az ugrás ugyanaz ──
a = s.index("function revealQuizStep(st, dir, qs) {")
b = s.index("function revealQuizWrite(st) {")
s = s[:a] + r'''// v10.442: az oldalak EGY lineáris listát adnak — borító → kérdések → megoldás-borító →
// megoldások → pontozás. A léptetés (±1) és az ugrás (tetszőleges oldal) UGYANAZT a
// pozíciót használja, így a kettő nem tud elcsúszni egymástól.
function revealQuizPages(n) {
  const p = [{ phase:'cover', idx:0 }];
  for (let i = 0; i < n; i++) p.push({ phase:'q', idx:i });
  p.push({ phase:'solcover', idx:0 });
  for (let i = 0; i < n; i++) p.push({ phase:'sol', idx:i });
  p.push({ phase:'end', idx:0 });
  return p;
}
function revealQuizPos(st) {
  const n = (st.qs || []).length, i = st.idx || 0;
  switch (st.phase) {
    case 'cover': return 0;
    case 'q': return 1 + i;
    case 'solcover': return 1 + n;
    case 'sol': return 2 + n + i;
    case 'end': return 2 + 2 * n;
    default: return -1;
  }
}
// ugrás egy oldalra — nem futó kvíznél el is indítja (új `run`, a kérdések lemásolva)
function revealQuizGoto(st, pos, qs) {
  const running = st && st.phase && st.phase !== 'idle';
  const list = (running && st.qs) || qs || [];
  const pages = revealQuizPages(list.length), k = Math.max(0, Math.min(pages.length - 1, pos));
  return Object.assign({}, running ? st : { run: revealToken() }, { qs: list }, pages[k]);
}
function revealQuizStep(st, dir, qs) {
  if (!st.phase || st.phase === 'idle') return dir > 0 ? revealQuizGoto(st, 0, qs) : st;
  const n = (st.qs || []).length, pos = revealQuizPos(st);
  if (dir > 0 && pos >= 2 + 2 * n) return { phase:'idle' };
  if (dir < 0 && pos <= 0) return st;
  return revealQuizGoto(st, pos + dir, qs);
}
function revealQuizNextLabel(st) {
  const last = Math.max(0, (st.qs || []).length - 1), idx = st.idx || 0;
  if (!st.phase || st.phase === 'idle') return 'Babakvíz indítása';
  if (st.phase === 'cover') return 'Első kérdés ›';
  if (st.phase === 'q') return idx < last ? 'Következő kérdés ›' : 'Megoldások ›';
  if (st.phase === 'solcover') return 'Első megoldás ›';
  if (st.phase === 'sol') return idx < last ? 'Következő megoldás ›' : 'Pontozás ›';
  return 'Kvíz vége';
}
''' + s[b:]

# ── 2. a vetítő: a két borító ──
rep("""  if (!q) return null;
  const sol = qstate.phase === 'sol';""", r"""  if (qstate.phase === 'cover' || qstate.phase === 'solcover') {
    const solc = qstate.phase === 'solcover';
    return (
      <div data-reveal-quiz={qstate.phase} style={bg}>
        {blobs}
        <div style={{ position:'absolute', inset:0, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:'2.6vh', padding:'6vh 6vw', textAlign:'center', boxSizing:'border-box' }}>
          <img src={REVEAL_LOGO} alt="" style={{ width:'min(24vh, 34vw)', height:'auto', animation:'revealFloat 4s ease-in-out infinite' }} />
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:'clamp(18px, 3.6vh, 44px)', letterSpacing:'0.22em', color:'#2F63A8' }}>{solc ? '🍼 BABAKVÍZ 🍼' : '🍼 INDUL A JÁTÉK 🍼'}</div>
          <div data-reveal-quiz-covertitle style={{ fontFamily:T.font, fontWeight:900, fontSize: narrow ? 'clamp(40px, 9vh, 80px)' : 'clamp(48px, 15vh, 180px)', lineHeight:1, color:ink }}>{solc ? 'Megoldások' : 'Babakvíz'}</div>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:'clamp(15px, 3vh, 36px)', color:ink, opacity:0.8, maxWidth:'26em', lineHeight:1.35 }}>
            {solc ? 'Jönnek a helyes válaszok — számoljátok össze, hány talált!' : `${qs.length} kérdés · karikázzátok be a válaszokat a lapon!`}
          </div>
          {!solc && <div style={{ display:'flex', gap:'1.4vw', marginTop:'1vh' }}>
            {['A', 'B', 'C'].map((l, i) => <span key={l} style={{ width:'clamp(40px, 9vh, 104px)', height:'clamp(40px, 9vh, 104px)', borderRadius:'50%', border:`0.45vh solid ${ink}`, background:REVEAL_QUIZ_COLORS[i], display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:'clamp(18px, 4.4vh, 52px)', color:ink }}>{l}</span>)}
          </div>}
        </div>
      </div>
    );
  }
  if (!q) return null;
  const sol = qstate.phase === 'sol';""")

# ── 3. a Szülők lapozója: fázis-felirat + „Ugrás oldalra" rács ──
rep("""  const cur = active && st.qs && st.qs[st.idx || 0];
  return (
    <div data-reveal-quizctl={st.phase || 'idle'}""", """  const cur = active && (st.phase === 'q' || st.phase === 'sol') && st.qs && st.qs[st.idx || 0];
  const [jumpOpen, setJumpOpen] = React.useState(false);
  const n = active ? (st.qs || []).length : qs.length, pos = active ? revealQuizPos(st) : -1;
  const where = !active ? `${qs.length} kérdés · papíron` : st.phase === 'cover' ? 'Borító' : st.phase === 'solcover' ? 'Megoldások borító' : st.phase === 'end' ? 'Pontozás'
    : `${st.phase === 'sol' ? 'Megoldás' : 'Kérdés'} ${(st.idx || 0) + 1} / ${n}`;
  const jump = p => revealQuizWrite(revealQuizGoto(st, p, qs));
  const chip = (p, label, wide) => <button key={p} data-reveal-quiz-jump={p} aria-pressed={pos === p} onClick={() => jump(p)}
    style={{ minWidth: wide ? 0 : 38, height:38, padding: wide ? '0 12px' : 0, gridColumn: wide ? 'span 3' : 'auto', borderRadius:10, cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize:13,
      border: pos === p ? 'none' : `1.5px solid ${T.border}`, background: pos === p ? T.mint : T.surface, color: pos === p ? '#fff' : T.ink }}>{label}</button>;
  const grid = (title, from, coverLabel) => (
    <div>
      <div style={{ fontFamily:T.font, fontWeight:800, fontSize:11, letterSpacing:'0.07em', color:T.inkSoft, textTransform:'uppercase', margin:'10px 0 6px' }}>{title}</div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(38px, 1fr))', gap:6 }}>
        {chip(from, coverLabel, true)}
        {Array.from({ length:n }, (_, i) => chip(from + 1 + i, String(i + 1)))}
      </div>
    </div>
  );
  return (
    <div data-reveal-quizctl={st.phase || 'idle'}""")
rep("""        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft }}>{!active ? `${qs.length} kérdés · papíron` : st.phase === 'end' ? 'Pontozás' : `${st.phase === 'sol' ? 'Megoldás' : 'Kérdés'} ${(st.idx || 0) + 1} / ${(st.qs || []).length}`}</div>""",
    """        <div data-reveal-quiz-where style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft }}>{where}</div>""")
rep("""        {active && <button data-reveal-quiz-prev onClick={() => step(-1)} disabled={st.phase === 'q' && !st.idx} style={btn(false)}>‹ Előző</button>}""",
    """        {active && <button data-reveal-quiz-prev onClick={() => step(-1)} disabled={st.phase === 'cover'} style={btn(false)}>‹ Előző</button>}""")
rep("""      {active && st.phase !== 'end' && <button data-reveal-quiz-end""",
    """      <button data-reveal-quiz-jumpbtn onClick={() => setJumpOpen(o => !o)} style={{ marginTop:8, width:'100%', padding:'10px', borderRadius:12, border:`1.5px solid ${T.border}`, background: jumpOpen ? T.bg : 'transparent', color:T.ink, fontFamily:T.font, fontWeight:800, fontSize:13, cursor:'pointer' }}>{jumpOpen ? 'Ugrás bezárása ▴' : '🔢 Ugrás oldalra ▾'}</button>
      {jumpOpen && <div data-reveal-quiz-jumps>
        {grid('Kérdések', 0, 'Borító')}
        {grid('Megoldások', 1 + n, 'Borító')}
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(38px, 1fr))', gap:6, marginTop:10 }}>{chip(2 + 2 * n, 'Pontozás', true)}</div>
      </div>}
      {active && st.phase !== 'end' && <button data-reveal-quiz-end""")
open(P, 'w', encoding='utf-8').write(s); print('ok')
