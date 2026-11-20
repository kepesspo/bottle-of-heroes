# v10.440 — Gender Reveal operátor: lapozó (a legújabb elöl), nagy kép, nagyobb tipp-gombok,
# sorszám felül, az Elrejt / Kuka a lap fejlécében (nem a képen).
P = 'app.src.html'
s = open(P, encoding='utf-8').read()

def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:120])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.439'", "const APP_VERSION = 'v10.440'")

# ── 1. nagyobb tipp-gombok (a választót csak az operátor használja) ──
rep("""  const seg = on => ({ flex:1, padding:'5px 0', borderRadius:8, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:11.5,""",
    """  const seg = on => ({ flex:1, padding:'11px 0', borderRadius:10, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize:15,""")
rep("""  const vb = (on, s) => ({ flex:1, minWidth:0, padding: pair ? '7px 0' : '7px 2px', borderRadius:10, cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize: pair ? 11 : 12,
    border: on ? `1.5px solid ${REVEAL_RESULTS[s].c1}` : `1.5px solid ${T.border}`,""",
    """  const vb = (on, s) => ({ flex:1, minWidth:0, minHeight:50, padding:'12px 4px', borderRadius:14, cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize: pair ? 15 : 16,
    border: on ? `2px solid ${REVEAL_RESULTS[s].c1}` : `2px solid ${T.border}`,""")
rep("""    <div key={i} style={{ display:'flex', alignItems:'center', gap: pair ? 4 : 5 }}>
      {pair && <span style={{ width:9, flexShrink:0, fontFamily:T.font, fontWeight:900, fontSize:11, color:T.inkSoft }}>{i + 1}</span>}""",
    """    <div key={i} style={{ display:'flex', alignItems:'center', gap:8 }}>
      {pair && <span style={{ width:14, flexShrink:0, fontFamily:T.font, fontWeight:900, fontSize:15, color:T.inkSoft, textAlign:'center' }}>{i + 1}</span>}""")
rep("""    <div data-reveal-votepick={item.id} data-pair={pair ? '1' : '0'} style={{ padding:8, display:'flex', flexDirection:'column', gap:6 }}>
      <div style={{ display:'flex', gap:3, padding:3, borderRadius:10, background:T.bg }}>""",
    """    <div data-reveal-votepick={item.id} data-pair={pair ? '1' : '0'} style={{ padding:12, display:'flex', flexDirection:'column', gap:10 }}>
      <div style={{ display:'flex', gap:4, padding:4, borderRadius:13, background:T.bg }}>""")

# ── 2. az operátor: lapozó a rács helyett ──
rep("""  const latest = approved.slice().reverse();
""", """  const latest = approved.slice().reverse();                 // ⚠️ a LEGÚJABB elöl
  // lapozó: vízszintes, scroll-snap — ujjal húzva és a ‹ › gombokkal is lép
  const trackRef = React.useRef(null);
  const [slide, setSlide] = React.useState(0);
  const nSlides = latest.length, curSlide = Math.min(slide, Math.max(0, nSlides - 1));
  const goSlide = i => { const el = trackRef.current; if (!el) return; const k = Math.max(0, Math.min(nSlides - 1, i)); el.scrollTo({ left: k * el.clientWidth, behavior:'smooth' }); setSlide(k); };
  const onTrackScroll = e => { const el = e.currentTarget, k = Math.round(el.scrollLeft / Math.max(1, el.clientWidth)); if (k !== slide) setSlide(k); };
  // új kép érkezett (feltöltés vagy jóváhagyás) → vissza az elejére, hogy rögtön tippelni lehessen rá
  const firstId = latest[0] ? latest[0].id : null, prevFirst = React.useRef(firstId);
  React.useEffect(() => {
    if (firstId && prevFirst.current && firstId !== prevFirst.current && trackRef.current) { trackRef.current.scrollTo({ left:0, behavior:'smooth' }); setSlide(0); }
    prevFirst.current = firstId;
  }, [firstId]);
""")

a = s.index("          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(170px, 1fr))', gap:10, alignItems:'start' }}>")
b = s.index("        </div>\n      </div>\n      {confirmDel && (", a)
s = s[:a] + r'''          {nSlides > 0 && (
            <div data-reveal-slider style={{ display:'flex', flexDirection:'column', gap:10 }}>
              <div ref={trackRef} data-reveal-track onScroll={onTrackScroll}
                style={{ display:'flex', overflowX:'auto', overflowY:'hidden', scrollSnapType:'x mandatory', WebkitOverflowScrolling:'touch', scrollbarWidth:'none', margin:'0 -4px' }}>
                {latest.map((p, i) => (
                  <div key={p.id} data-reveal-thumb={p.id} data-hidden={p.hidden ? '1' : '0'} data-idx={i} style={{ flex:'0 0 100%', boxSizing:'border-box', padding:'0 4px', scrollSnapAlign:'center' }}>
                    <div style={{ borderRadius:18, overflow:'hidden', background:T.surface, boxShadow:T.shadow }}>
                      {/* fejléc: hányadik kép + Elrejt / Kuka — NEM a képen (v10.440) */}
                      <div data-reveal-slidehead style={{ display:'flex', alignItems:'center', gap:8, padding:'10px 12px' }}>
                        <span data-reveal-slidenum style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, whiteSpace:'nowrap' }}>{i + 1}. kép</span>
                        <span style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkSoft, whiteSpace:'nowrap' }}>/ {nSlides}</span>
                        {i === 0 && <span style={{ padding:'3px 8px', borderRadius:999, background:REVEAL_PINK, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:10, letterSpacing:'0.06em' }}>LEGÚJABB</span>}
                        <div style={{ flex:1 }} />
                        <button data-reveal-hide onClick={() => setHidden(p, !p.hidden)} style={{ padding:'8px 12px', borderRadius:10, border:`1.5px solid ${T.border}`, background: p.hidden ? T.mintSoft : 'transparent', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:13, color:T.ink, whiteSpace:'nowrap' }}>{p.hidden ? 'Mutat' : 'Elrejt'}</button>
                        <button data-reveal-del onClick={() => setConfirmDel(p)} aria-label="Törlés" style={{ width:40, height:36, flexShrink:0, borderRadius:10, border:`1.5px solid ${T.coral}`, background:'transparent', cursor:'pointer', fontSize:15 }}>🗑</button>
                      </div>
                      <div style={{ position:'relative', height:'clamp(220px, 46vh, 460px)', background:T.bg }}>
                        {p.kind === 'wish'
                          ? <div style={{ position:'absolute', inset:0, padding:'18px 16px', background:'#FFF1F5', display:'flex', alignItems:'center', justifyContent:'center', textAlign:'center', opacity: p.hidden ? 0.4 : 1 }}>
                              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:18, color:'#2A1E3A', lineHeight:1.4, overflowWrap:'anywhere' }}>💌 „{p.text}”</div>
                            </div>
                          : <img src={p.src} alt="" style={{ width:'100%', height:'100%', objectFit:'contain', display:'block', opacity: p.hidden ? 0.3 : 1 }} />}
                        {byLine(p)}
                        {p.hidden && <div style={{ position:'absolute', top:8, left:8, padding:'3px 8px', borderRadius:999, background:'rgba(0,0,0,0.6)', color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:11 }}>REJTVE</div>}
                      </div>
                      {p.kind !== 'wish' && <RevealVotePicker item={p} />}
                    </div>
                  </div>
                ))}
              </div>
              <div data-reveal-slidenav style={{ display:'flex', alignItems:'center', gap:10 }}>
                <button data-reveal-slideprev aria-label="Előző kép" disabled={curSlide <= 0} onClick={() => goSlide(curSlide - 1)}
                  style={{ width:54, height:48, borderRadius:14, border:`2px solid ${T.border}`, background:T.surface, cursor: curSlide > 0 ? 'pointer' : 'default', opacity: curSlide > 0 ? 1 : 0.35, fontFamily:T.font, fontWeight:900, fontSize:24, color:T.ink }}>‹</button>
                <div data-reveal-slidepos style={{ flex:1, textAlign:'center', fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink }}>{curSlide + 1} / {nSlides}</div>
                <button data-reveal-slidenext aria-label="Következő kép" disabled={curSlide >= nSlides - 1} onClick={() => goSlide(curSlide + 1)}
                  style={{ width:54, height:48, borderRadius:14, border:`2px solid ${T.border}`, background:T.surface, cursor: curSlide < nSlides - 1 ? 'pointer' : 'default', opacity: curSlide < nSlides - 1 ? 1 : 0.35, fontFamily:T.font, fontWeight:900, fontSize:24, color:T.ink }}>›</button>
              </div>
            </div>
          )}
''' + s[b:]

open(P, 'w', encoding='utf-8').write(s)
print('ok')
