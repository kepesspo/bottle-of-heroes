# v10.446 — Gender Reveal operátor: a jóváhagyásra várók egy GOMB mögött, teljes képernyős
# lapozóban (ugyanaz a felület, mint az operátor lapozója): nagy kép, Mehet / Eldob, ‹ N / M ›.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:120]); s = s.replace(old, new)

rep("const APP_VERSION = 'v10.445'", "const APP_VERSION = 'v10.446'")

# ── 1. a jóváhagyó felület (modul-szintű) ──
rep("// ── Operátor (v10.445): a Szülők készletével, a DNR téma színeivel ─────────────────", r'''// ── Jóváhagyás (v10.446): teljes képernyős lapozó a beküldött képekhez/üzenetekhez ──
// UGYANAZ a felület, mint az operátor lapozója (lap = fejléc + nagy kép sötét háttéren),
// csak a tipp-sor helyén Eldob / Mehet. A sorrend a beküldésé (legrégebbi elöl — sor).
// Döntés után a tétel kiesik, a lapozó ugyanott marad → a következő csúszik a helyére.
// Ha elfogyott, magától bezárul. ⚠️ NEM portál: a szülő DOM-jában (position:fixed) marad.
function RevealPendingReview({ items, onApprove, onReject, onClose }) {
  const trackRef = React.useRef(null);
  const [slide, setSlide] = React.useState(0);
  const n = items.length, cur = Math.min(slide, Math.max(0, n - 1));
  const go = i => { const el = trackRef.current; if (!el) return; const k = Math.max(0, Math.min(n - 1, i)); el.scrollTo({ left: k * el.clientWidth, behavior:'smooth' }); setSlide(k); };
  const onScroll = e => { const el = e.currentTarget, k = Math.round(el.scrollLeft / Math.max(1, el.clientWidth)); if (k !== slide) setSlide(k); };
  React.useEffect(() => { if (!n) onClose(); }, [n]);
  const DARK = '#16131C';
  const navBtn = on => rvBtn('secondary', { width:52, height:44, borderRadius:14, opacity: on ? 1 : 0.35, cursor: on ? 'pointer' : 'default' });
  return (
    <div data-reveal-review style={{ position:'fixed', inset:0, zIndex:6800, display:'flex', flexDirection:'column', background:T.bg }}>
      <div style={{ flexShrink:0, display:'flex', alignItems:'center', gap:8, padding:'calc(8px + env(safe-area-inset-top)) 12px 8px', background:T.surface, borderBottom:`1px solid ${T.border}` }}>
        <button type="button" data-reveal-reviewclose aria-label="Bezárás" onClick={onClose} style={rvBtn('ghost', { width:44, height:44, padding:0, color:T.ink })}>{rvIcon('prev', 22)}</button>
        <div style={{ flex:1, fontFamily:T.font, fontWeight:900, fontSize:19, color:T.ink }}>Jóváhagyás</div>
        {rvPill(n + ' vár', 'pink')}
      </div>
      <div style={{ flex:1, minHeight:0, display:'flex', flexDirection:'column', gap:8, padding:'10px 16px calc(10px + env(safe-area-inset-bottom))', boxSizing:'border-box', maxWidth:720, width:'100%', margin:'0 auto' }}>
        <div ref={trackRef} data-reveal-reviewtrack onScroll={onScroll}
          style={{ flex:'1 1 0', minHeight:0, display:'flex', alignItems:'stretch', overflowX:'auto', overflowY:'hidden', scrollSnapType:'x mandatory', WebkitOverflowScrolling:'touch', scrollbarWidth:'none', margin:'0 -4px' }}>
          {items.map((p, i) => (
            <div key={p.id} data-reveal-pend={p.id} data-idx={i} style={{ flex:'0 0 100%', minWidth:0, boxSizing:'border-box', padding:'0 4px 2px', scrollSnapAlign:'center', display:'flex' }}>
              <div style={rvCard({ flex:1, minWidth:0, display:'flex', flexDirection:'column' })}>
                <div style={{ flexShrink:0, display:'flex', alignItems:'center', gap:8, padding:'10px 14px' }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, whiteSpace:'nowrap' }}>{i + 1}. / {n}</span>
                  {rvPill(p.kind === 'wish' ? 'Üzenet' : 'Fotó', p.kind === 'wish' ? 'pink' : 'info')}
                  <span style={{ flex:1, minWidth:0, textAlign:'right', fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>{p.by ? 'Beküldte: ' + p.by : ''}</span>
                </div>
                <div style={{ position:'relative', flex:'1 1 0', minHeight:120, background: p.kind === 'wish' ? (T.bgSoft || T.bg) : DARK, overflow:'hidden' }}>
                  {p.kind === 'wish'
                    ? <div style={{ position:'absolute', inset:0, display:'flex', alignItems:'center', justifyContent:'center' }}><RevealWishPolaroid text={p.text} by={p.by} width={260} /></div>
                    : <img src={p.src} alt={p.by ? 'Kép: ' + p.by : 'Kép'} style={{ width:'100%', height:'100%', objectFit:'contain', display:'block' }} />}
                </div>
                <div style={{ flexShrink:0, display:'flex', gap:8, padding:10, borderTop:`1px solid ${T.border}` }}>
                  <button type="button" data-reveal-reject onClick={() => onReject(p)} style={rvBtn('danger', { flex:1, height:52, borderRadius:14, fontSize:16 })}>Eldob</button>
                  <button type="button" data-reveal-approve onClick={() => onApprove(p)} style={rvBtn('primary', { flex:1.5, height:52, borderRadius:14, fontSize:16 })}>Mehet a vetítőre</button>
                </div>
              </div>
            </div>
          ))}
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:10, flexShrink:0 }}>
          <button type="button" data-reveal-reviewprev aria-label="Előző" disabled={cur <= 0} onClick={() => go(cur - 1)} style={navBtn(cur > 0)}>{rvIcon('prev', 20)}</button>
          <div data-reveal-reviewpos style={{ flex:1, textAlign:'center', fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{n ? cur + 1 : 0} / {n}</div>
          <button type="button" data-reveal-reviewnext aria-label="Következő" disabled={cur >= n - 1} onClick={() => go(cur + 1)} style={navBtn(cur < n - 1)}>{rvIcon('chev', 20)}</button>
        </div>
      </div>
    </div>
  );
}
// ── Operátor (v10.445): a Szülők készletével, a DNR téma színeivel ─────────────────''')

# ── 2. az operátorban: a csík helyett gomb a feltöltés mellett ──
rep("""  const [zoom, setZoom] = React.useState(null);
  // v10.437""", """  const [zoom, setZoom] = React.useState(null);
  const [review, setReview] = React.useState(false);
  // v10.437""")
a = s.index("""          <button type="button" data-reveal-pick onClick={() => pickRef.current && pickRef.current.click()} style={rvBtn('primary', { height:48, borderRadius:14, fontSize:16, flexShrink:0 })}>""")
b = s.index("""          <input ref={pickRef} data-reveal-input""", a)
s = s[:a] + """          <div style={{ display:'flex', gap:8, flexShrink:0 }}>
            <button type="button" data-reveal-pick onClick={() => pickRef.current && pickRef.current.click()} style={rvBtn('primary', { flex:1, minWidth:0, height:48, borderRadius:14, fontSize:15 })}>
              <span aria-hidden="true" style={{ fontSize:20, lineHeight:1 }}>🖼️</span>{pending.length ? 'Feltöltés' : 'Képek feltöltése'}</button>
            {pending.length > 0 && (
              <button type="button" data-reveal-pendbtn onClick={() => setReview(true)} style={rvBtn('secondary', { flex:1, minWidth:0, height:48, borderRadius:14, fontSize:15, fontWeight:900, border:`2px solid ${REVEAL_PINK}` })}>
                Jóváhagyás<span style={{ minWidth:24, height:24, padding:'0 7px', borderRadius:999, background:REVEAL_PINK, color:'#fff', fontSize:13, display:'inline-flex', alignItems:'center', justifyContent:'center', boxSizing:'border-box' }}>{pending.length}</span></button>
            )}
          </div>
""" + s[b:]
a = s.index("""          {pending.length > 0 && (
            <section data-reveal-pending""")
b = s.index("""          <div style={{ display:'flex', alignItems:'center', gap:8, flexShrink:0 }}>
            <div style={{ flex:1, fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>A vetítőn</div>""", a)
s = s[:a] + s[b:]
rep("""      {zoom && (
        // teljes képernyős nézet""", """      {review && pending.length > 0 && <RevealPendingReview items={pending} onApprove={approve} onReject={del} onClose={() => setReview(false)} />}
      {zoom && (
        // teljes képernyős nézet""")
rep('  const pending = items.filter(p => p.pending);\n  const approved = items.filter(p => !p.pending);\n  const shown = approved.filter(p => !p.hidden).length;\n  const latest = approved.slice().reverse();                 // ⚠️ a LEGÚJABB elöl\n  const trackRef', '  const pending = items.filter(p => p.pending);\n  // ⚠️ kiürült → zárva is marad (különben egy később érkező beküldés magától felnyitná)\n  React.useEffect(() => { if (!pending.length && review) setReview(false); }, [pending.length]);\n  const approved = items.filter(p => !p.pending);\n  const shown = approved.filter(p => !p.hidden).length;\n  const latest = approved.slice().reverse();                 // ⚠️ a LEGÚJABB elöl\n  const trackRef')
assert 'data-reveal-pending' not in s
open(P, 'w', encoding='utf-8').write(s); print('ok')
