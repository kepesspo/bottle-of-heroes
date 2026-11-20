# v10.448 — Szülők: a fül-sáv PORTÁLBA, a valódi képernyő-aljhoz tapadva (docs/safe-area.md,
# ugyanaz a minta, mint a Pub gombsávjai); rövidebb állapot-pirulák (nem lógnak le).
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:120]); s = s.replace(old, new)

rep("const APP_VERSION = 'v10.447'", "const APP_VERSION = 'v10.448'")

# ── 1. a fül-sáv: portál, fixen a képernyő alján ──
rep("""function RevealParentTabs({ tab, onTab }) {
  return (
    <nav aria-label="Szülők fülek" data-reveal-ptabs style={{ flexShrink:0, display:'grid', gridTemplateColumns:'repeat(4, minmax(0, 1fr))', background:T.surface, borderTop:`1px solid ${T.border}`, padding:'4px 6px calc(4px + env(safe-area-inset-bottom))' }}>""",
"""// ⚠️ v10.448: PORTÁL + position:fixed, a képernyő ALJA ALÁ nyúlva (docs/safe-area.md — a
// Pub gombsávjainak mintája). Folyamban (v10.444) iOS PWA-ban NEM ért le a képernyő aljára:
// a gyökér konténer rövidebb a kijelzőnél, alatta üres sáv maradt, és a tartalom alja
// (Leleplezés most / Próba) a sáv alá csúszott. A görgő terület alsó paddingja ezért nagy.
function RevealParentTabs({ tab, onTab }) {
  return ReactDOM.createPortal(
    <nav aria-label="Szülők fülek" data-reveal-ptabs style={{ position:'fixed', left:0, right:0, bottom:'calc(-1 * env(safe-area-inset-bottom) - 80px)', zIndex:60,
      display:'grid', gridTemplateColumns:'repeat(4, minmax(0, 1fr))', background:T.surface, boxShadow:'0 -4px 18px rgba(20,30,50,0.08)',
      borderTopLeftRadius:20, borderTopRightRadius:20, padding:'4px 6px calc(env(safe-area-inset-bottom) + 108px)', boxSizing:'border-box' }}>""")
rep("""          <span style={{ width:52, height:30, borderRadius:999, display:'grid', placeItems:'center', background: on ? (T.mintSoft || T.bgSoft) : 'transparent' }}>{rvIcon(ic, 20)}</span>{label}</button>); })}
    </nav>
  );
}""", """          <span style={{ width:52, height:30, borderRadius:999, display:'grid', placeItems:'center', background: on ? (T.mintSoft || T.bgSoft) : 'transparent' }}>{rvIcon(ic, 20)}</span>{label}</button>); })}
    </nav>, document.body
  );
}""")
rep("""      <div data-reveal-pscroll style={{ flex:1, minHeight:0, overflowY:'auto', display:'flex', flexDirection:'column', padding:'2px 16px 14px', boxSizing:'border-box', WebkitOverflowScrolling:'touch' }}>""",
    """      <div data-reveal-pscroll style={{ flex:1, minHeight:0, overflowY:'auto', display:'flex', flexDirection:'column', padding:'2px 16px calc(env(safe-area-inset-bottom) + 100px)', boxSizing:'border-box', WebkitOverflowScrolling:'touch' }}>""")

# ── 2. rövidebb állapot-pirulák (kisebb méret, rövid dátum, tördelhető sor) ──
rep("""function rvPill(text, tone, data, icon) {
  const c = RV_TONES[tone];
  return <span {...(data || {})} style={{ display:'inline-flex', alignItems:'center', gap:6, height:28, padding:'0 10px', borderRadius:999, flexShrink:0, whiteSpace:'nowrap', fontFamily:T.font, fontWeight:800, fontSize:12,""",
    """function rvPill(text, tone, data, icon, sm) {
  const c = RV_TONES[tone];
  return <span {...(data || {})} style={{ display:'inline-flex', alignItems:'center', gap: sm ? 5 : 6, height: sm ? 26 : 28, padding: sm ? '0 9px' : '0 10px', borderRadius:999, flexShrink:0, whiteSpace:'nowrap', fontFamily:T.font, fontWeight:800, fontSize: sm ? 11.5 : 12,""")
rep("""    <div data-reveal-pstatus style={{ flexShrink:0, display:'flex', gap:6, padding:'10px 16px', overflowX:'auto', scrollbarWidth:'none' }}>
      {rvPill(at ? revealFmtWhen(at) : 'Nincs időpont', null, null, 'timer')}
      {done ? rvPill('Leleplezve', 'ok') : armed ? rvPill('Engedélyezve', 'ok') : rvPill('Engedélyre vár', 'warn')}
      {q.phase && q.phase !== 'idle' ? rvPill('Kvíz megy', 'info') : paused ? rvPill('Vetítő szünetel', 'warn') : rvPill('Képfolyam megy', 'ok')}
    </div>""", """    <div data-reveal-pstatus style={{ flexShrink:0, display:'flex', flexWrap:'wrap', gap:6, padding:'10px 16px' }}>
      {rvPill(at ? revealFmtShort(at) : 'Nincs időpont', null, null, 'timer', true)}
      {done ? rvPill('Leleplezve', 'ok', null, null, true) : armed ? rvPill('Engedélyezve', 'ok', null, null, true) : rvPill('Engedélyre vár', 'warn', null, null, true)}
      {q.phase && q.phase !== 'idle' ? rvPill('Kvíz megy', 'info', null, null, true) : paused ? rvPill('Vetítő áll', 'warn', null, null, true) : rvPill('Vetítő megy', 'ok', null, null, true)}
    </div>""")
rep("""function revealFmtLeft(ms) {""", """function revealFmtShort(ms) {
  if (!ms) return '';
  try { return new Date(ms).toLocaleString('hu-HU', { month:'short', day:'numeric', hour:'2-digit', minute:'2-digit' }); } catch(e) { return ''; }
}
function revealFmtLeft(ms) {""")

# ── 3. a sötét kártya kicsit alacsonyabb (több hely a gomboknak) ──
rep("""      <section data-reveal-phero style={{ position:'relative', overflow:'hidden', borderRadius:20, padding:'16px 18px', background:REVEAL_NIGHT, color:'#fff', flexShrink:0 }}>""",
    """      <section data-reveal-phero style={{ position:'relative', overflow:'hidden', borderRadius:20, padding:'14px 18px', background:REVEAL_NIGHT, color:'#fff', flexShrink:0 }}>""")
rep("""                  <span style={{ fontFamily:T.font, fontSize:42, fontWeight:900, lineHeight:1, fontVariantNumeric:'tabular-nums' }}>{n}</span>""",
    """                  <span style={{ fontFamily:T.font, fontSize:38, fontWeight:900, lineHeight:1, fontVariantNumeric:'tabular-nums' }}>{n}</span>""")
rep("""        <div style={{ position:'relative', fontFamily:T.font, fontSize:13, fontWeight:700, opacity:0.85, marginTop:10, lineHeight:1.4 }}>""",
    """        <div style={{ position:'relative', fontFamily:T.font, fontSize:12.5, fontWeight:700, opacity:0.85, marginTop:8, lineHeight:1.4 }}>""")
open(P, 'w', encoding='utf-8').write(s); print('ok')
