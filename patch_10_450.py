# v10.450 — a jóváhagyott design: Menü (szerepválasztó), Operátor, Jóváhagyás.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:140]); s = s.replace(old, new)
def between(a, b):
    i = s.index(a); j = s.index(b, i); return i, j

rep("const APP_VERSION = 'v10.449';", "const APP_VERSION = 'v10.450';")

# ── ikonok ─────────────────────────────────────────────────────────────────────────
rep("""    case 'screen': return <svg {...p}><rect x="3" y="4" width="18" height="12" rx="2" /><path d="M8 20h8M12 16v4" /></svg>;""",
"""    case 'screen': return <svg {...p}><rect x="3" y="4" width="18" height="12" rx="2" /><path d="M8 20h8M12 16v4" /></svg>;
    case 'cam': return <svg {...p}><path d="M4 8h3l2-3h6l2 3h3v11H4z" /><circle cx="12" cy="13" r="3.5" /></svg>;
    case 'heart': return <svg {...p}><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z" /></svg>;
    case 'eyeoff': return <svg {...p}><path d="M3 3l18 18M10.6 6.2A9.7 9.7 0 0 1 12 6c5 0 9 6 9 6a16 16 0 0 1-3 3.6M6.2 7.7C4.2 9.3 3 12 3 12s4 6 9 6a8.6 8.6 0 0 0 3.6-.8" /></svg>;
    case 'eye': return <svg {...p}><path d="M3 12s4-6 9-6 9 6 9 6-4 6-9 6-9-6-9-6z" /><circle cx="12" cy="12" r="2.6" /></svg>;
    case 'trash': return <svg {...p}><path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3" /></svg>;
    case 'upload': return <svg {...p}><path d="M12 16V4M7 9l5-5 5 5M5 20h14" /></svg>;
    case 'qr': return <svg {...p}><rect x="4" y="4" width="6" height="6" rx="1" /><rect x="14" y="4" width="6" height="6" rx="1" /><rect x="4" y="14" width="6" height="6" rx="1" /><path d="M14 14h2v2h-2zM18 18h2v2h-2zM14 18h2" /></svg>;
    case 'expand': return <svg {...p}><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" /></svg>;""")

# ── közös apróságok ────────────────────────────────────────────────────────────────
rep("""function RevealPendingReview({ items, onApprove, onReject, onClose }) {""",
"""// v10.450: „2 perce" — a beküldés / jóváhagyás ideje (`at`)
function revealAgo(at, now) {
  if (!at || at < 1e11) return '';
  const d = Math.max(0, ((now || Date.now()) - at) / 1000);
  if (d < 60) return 'most';
  if (d < 3600) return Math.floor(d / 60) + ' perce';
  try { return new Date(at).toLocaleTimeString('hu-HU', { hour:'2-digit', minute:'2-digit' }); } catch(e) { return ''; }
}
// kezdőbetűs korong a beküldőnek — a szín a névből (determinisztikus)
function revealAvatar(name, size) {
  const n = String(name || '?').trim() || '?', h = Math.round(revealHash(n) * 360);
  return <span aria-hidden="true" style={{ width:size, height:size, flexShrink:0, borderRadius:'50%', background:`hsl(${h} 55% 55%)`, color:'#fff', display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:Math.round(size * 0.42) }}>{n[0].toUpperCase()}</span>;
}
// v10.450: alsó dokk (operátor). Portál a body-ba, a képernyő alja alá nyúlva — a Szülők
// fül-sávjának mintája (v10.448, docs/safe-area.md).
function revealBottomDock(children, data) {
  return ReactDOM.createPortal(
    <div {...data} style={{ position:'fixed', left:0, right:0, bottom:'calc(-1 * env(safe-area-inset-bottom) - 80px)', zIndex:6600, background:T.surface,
      boxShadow:'0 -4px 18px rgba(20,30,50,0.10)', borderTopLeftRadius:22, borderTopRightRadius:22, padding:'10px 16px calc(env(safe-area-inset-bottom) + 92px)', boxSizing:'border-box' }}>
      <div style={{ maxWidth:720, margin:'0 auto', display:'flex', flexDirection:'column', gap:8 }}>{children}</div>
    </div>, document.body);
}
function RevealPendingReview({ items, onApprove, onReject, onClose }) {""")

# ── Jóváhagyás: a design szerint ───────────────────────────────────────────────────
i, j = between("function RevealPendingReview({ items, onApprove, onReject, onClose }) {", "// ── Operátor (v10.445)")
s = s[:i] + r"""function RevealPendingReview({ items, onApprove, onReject, onClose }) {
  const trackRef = React.useRef(null);
  const [slide, setSlide] = React.useState(0);
  const n = items.length, cur = Math.min(slide, Math.max(0, n - 1));
  const go = i => { const el = trackRef.current; if (!el) return; const k = Math.max(0, Math.min(n - 1, i)); el.scrollTo({ left: k * el.clientWidth, behavior:'smooth' }); setSlide(k); };
  const onScroll = e => { const el = e.currentTarget, k = Math.round(el.scrollLeft / Math.max(1, el.clientWidth)); if (k !== slide) setSlide(k); };
  React.useEffect(() => { if (!n) onClose(); }, [n]);
  const DARK = '#16131C', item = items[cur];
  // v10.450: a döntés-gombok a lap ALJÁN, fixen — mindig az ÉPP látható tételre vonatkoznak.
  return (
    <div data-reveal-review style={{ position:'fixed', inset:0, zIndex:6800, display:'flex', flexDirection:'column', background:T.bg }}>
      <AppBar title="Jóváhagyás" onBack={onClose} right={<span data-reveal-reviewpos style={{ marginRight:4, height:30, padding:'0 11px', borderRadius:999, display:'inline-flex', alignItems:'center', background:RV_TONES.warn[0], color:RV_TONES.warn[1], fontFamily:T.font, fontWeight:900, fontSize:13, whiteSpace:'nowrap' }}>{n ? cur + 1 : 0} / {n}</span>} />
      <div style={{ flex:1, minHeight:0, display:'flex', flexDirection:'column', padding:'12px 16px', boxSizing:'border-box', maxWidth:720, width:'100%', margin:'0 auto' }}>
        <div ref={trackRef} data-reveal-reviewtrack onScroll={onScroll}
          style={{ flex:'1 1 0', minHeight:0, display:'flex', alignItems:'stretch', overflowX:'auto', overflowY:'hidden', scrollSnapType:'x mandatory', WebkitOverflowScrolling:'touch', scrollbarWidth:'none', margin:'0 -4px' }}>
          {items.map((p, i) => (
            <div key={p.id} data-reveal-pend={p.id} data-idx={i} style={{ flex:'0 0 100%', minWidth:0, boxSizing:'border-box', padding:'0 4px 2px', scrollSnapAlign:'center', display:'flex' }}>
              <div style={rvCard({ flex:1, minWidth:0, display:'flex', flexDirection:'column', border:'none', borderRadius:22, boxShadow:'0 5px 0 rgba(0,40,100,0.06), 0 12px 28px rgba(0,40,100,0.10)' })}>
                <div style={{ flexShrink:0, display:'flex', alignItems:'center', gap:12, padding:'12px 14px' }}>
                  {revealAvatar(p.by, 40)}
                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>{p.by || 'Ismeretlen'}</div>
                    <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkMute || T.inkSoft }}>{(p.kind === 'wish' ? 'Üzenet' : 'Fotó') + (revealAgo(p.at) ? ' · ' + revealAgo(p.at) : '')}</div>
                  </div>
                  {n > 1 && <span style={{ fontFamily:T.font, fontWeight:800, fontSize:12, color:T.inkMute || T.inkSoft, whiteSpace:'nowrap' }}>húzd oldalra ›</span>}
                </div>
                <div style={{ position:'relative', flex:'1 1 0', minHeight:120, margin:'0 10px 10px', borderRadius:16, background: p.kind === 'wish' ? (T.bgSoft || T.bg) : DARK, overflow:'hidden' }}>
                  {p.kind === 'wish'
                    ? <div style={{ position:'absolute', inset:0, display:'flex', alignItems:'center', justifyContent:'center' }}><RevealWishPolaroid text={p.text} by={p.by} width={240} /></div>
                    : <img src={p.src} alt={p.by ? 'Kép: ' + p.by : 'Kép'} style={{ width:'100%', height:'100%', objectFit:'contain', display:'block' }} />}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div data-reveal-reviewdock style={{ flexShrink:0, background:T.surface, borderTopLeftRadius:22, borderTopRightRadius:22, boxShadow:'0 -4px 18px rgba(20,30,50,0.08)', padding:'12px 16px calc(14px + env(safe-area-inset-bottom))' }}>
        <div style={{ maxWidth:720, margin:'0 auto' }}>
          {n > 1 && (
            <div style={{ display:'flex', justifyContent:'center', alignItems:'center', gap:6, marginBottom:12, flexWrap:'wrap' }}>
              {items.slice(0, 14).map((p, k) => (
                <button key={p.id} type="button" data-reveal-reviewdot={k} aria-label={(k + 1) + '. beküldés'} aria-current={k === cur ? 'true' : undefined} onClick={() => go(k)}
                  style={{ width: k === cur ? 18 : 7, height:7, padding:0, border:'none', borderRadius:999, cursor:'pointer', background: k === cur ? T.mint : (T.border || '#B8CDE2'), transition:'width .2s' }} />
              ))}
              {n > 14 && <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.inkSoft }}>+{n - 14}</span>}
            </div>
          )}
          <div style={{ display:'flex', gap:10 }}>
            <button type="button" data-reveal-reject disabled={!item} onClick={() => item && onReject(item)} style={rvBtn('danger', { width:112, height:54, borderRadius:16, fontSize:16, border:'1.5px solid #E8B4AE' })}>Eldob</button>
            <button type="button" data-reveal-approve disabled={!item} onClick={() => item && onApprove(item)} style={rvBtn('primary', { flex:1, height:54, borderRadius:16, fontSize:17, background:RV_TONES.ok[2] })}>Mehet a vetítőre</button>
          </div>
        </div>
      </div>
    </div>
  );
}
""" + s[j:]

# ── Operátor: a design szerint ─────────────────────────────────────────────────────
i, j = between("  const tally = revealVoteTally(items);\n  const DARK = '#16131C';\n  const navBtn", "\n      {review && pending.length > 0 && <RevealPendingReview")
s = s[:i] + r"""  const tally = revealVoteTally(items);
  const DARK = '#16131C';
  const [now, setNow] = React.useState(() => Date.now());
  React.useEffect(() => { const iv = setInterval(() => setNow(Date.now()), 30000); return () => clearInterval(iv); }, []);
  // a bélyegkép-csík az aktív elemet görgeti láthatóvá — CSAK a csíkot (az oldal ne ugorjon)
  const stripRef = React.useRef(null);
  React.useEffect(() => {
    const st = stripRef.current, el = st && st.querySelector(`[data-reveal-strip="${curSlide}"]`); if (!el) return;
    const l = el.offsetLeft - st.offsetLeft, r = l + el.offsetWidth;
    if (l < st.scrollLeft) st.scrollTo({ left: l - 8, behavior:'smooth' });
    else if (r > st.scrollLeft + st.clientWidth) st.scrollTo({ left: r - st.clientWidth + 8, behavior:'smooth' });
  }, [curSlide, nSlides]);
  const tallyOn = tally.boy + tally.girl > 0;
  const iconBtn = (danger) => rvBtn('small', { width:40, height:40, padding:0, borderRadius:12, color: danger ? '#B04040' : T.inkSoft, borderColor: danger ? '#F0C8C8' : T.border });
  return (
    <div data-reveal-operator style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title="Operátor" onBack={onBack} right={
        <span data-reveal-opcount style={{ height:30, padding:'0 11px', borderRadius:999, display:'inline-flex', alignItems:'center', background:T.bgSoft || T.bg, fontFamily:T.font, fontWeight:900, fontSize:13, color:T.ink, whiteSpace:'nowrap' }}>
          {shown} kép{approved.length > shown ? ` · ${approved.length - shown} rejtve` : ''}</span>} />
      {/* v10.450: a görgő terület alja a fix alsó dokk magasságával */}
      <div data-reveal-opscroll style={{ flex:1, minHeight:0, overflowY:'auto', display:'flex', flexDirection:'column', padding:`10px 16px calc(env(safe-area-inset-bottom) + ${busy.total > 0 ? 112 : 82}px)`, boxSizing:'border-box', WebkitOverflowScrolling:'touch' }}>
        <div style={{ flex:'1 0 auto', width:'100%', maxWidth:720, margin:'0 auto', display:'flex', flexDirection:'column', gap:10 }}>
          {(pending.length > 0 || tallyOn) && (
            <div style={{ display:'flex', gap:8, flexShrink:0 }}>
              {pending.length > 0 && (
                <button type="button" data-reveal-pendbtn onClick={() => setReview(true)} style={{ flex:1, minWidth:0, height:40, borderRadius:14, border:'none', cursor:'pointer', background:RV_TONES.warn[0], color:RV_TONES.warn[1], fontFamily:T.font, fontWeight:900, fontSize:14, display:'inline-flex', alignItems:'center', justifyContent:'center', gap:8 }}>
                  <span style={{ minWidth:22, height:22, padding:'0 6px', boxSizing:'border-box', borderRadius:999, background:RV_TONES.warn[2], color:'#fff', fontSize:12, display:'grid', placeItems:'center' }}>{pending.length}</span>Jóváhagyásra vár</button>
              )}
              {tallyOn && (
                <span data-reveal-optally style={{ flex: pending.length ? '0 0 auto' : 1, height:40, padding:'0 12px', borderRadius:14, background:T.surface, display:'inline-flex', alignItems:'center', justifyContent:'center', gap:8, fontFamily:T.font, fontWeight:900, fontSize:14, whiteSpace:'nowrap' }}>
                  <span style={{ color:'#2F63A8' }}>{REVEAL_RESULTS.boy.emoji} {tally.boy}</span><span aria-hidden="true" style={{ width:1, height:18, background:T.border }} /><span style={{ color:'#A8325E' }}>{tally.girl} {REVEAL_RESULTS.girl.emoji}</span>
                </span>
              )}
            </div>
          )}
          {errs.length > 0 && (
            <div data-reveal-errors style={rvCard({ padding:'10px 14px', fontFamily:T.font, fontSize:13, fontWeight:700, color:'#A3342C', lineHeight:1.5, background:'#FBE7E4', border:'none' })}>
              {errs.map((e, i) => <div key={i}>⚠️ {e}</div>)}
            </div>
          )}
          {loaded && !approved.length && (
            <div data-reveal-opempty style={rvCard({ flex:'1 1 auto', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:10, padding:'32px 20px', textAlign:'center', border:`2px dashed ${T.border}`, background:'transparent' })}>
              <span style={{ width:56, height:56, borderRadius:18, background:T.surface, color:T.mint, display:'grid', placeItems:'center' }}>{rvIcon('cam', 28)}</span>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink }}>Még nincs feltöltött kép</div>
              <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkSoft }}>A lenti gombbal töltsd fel a fényképező képeit.</div>
            </div>
          )}
          {nSlides > 0 && (
            <div data-reveal-slider style={{ flex:'1 1 0', minHeight:330, display:'flex', flexDirection:'column', gap:10 }}>
              <div ref={trackRef} data-reveal-track onScroll={onTrackScroll}
                style={{ flex:'1 1 0', minHeight:0, display:'flex', alignItems:'stretch', overflowX:'auto', overflowY:'hidden', scrollSnapType:'x mandatory', WebkitOverflowScrolling:'touch', scrollbarWidth:'none', margin:'0 -4px' }}>
                {latest.map((p, i) => (
                  <div key={p.id} data-reveal-thumb={p.id} data-hidden={p.hidden ? '1' : '0'} data-idx={i} style={{ flex:'0 0 100%', minWidth:0, boxSizing:'border-box', padding:'0 4px 2px', scrollSnapAlign:'center', display:'flex' }}>
                    <div style={rvCard({ flex:1, minWidth:0, display:'flex', flexDirection:'column', border:'none', borderRadius:22, boxShadow:'0 5px 0 rgba(0,40,100,0.06), 0 12px 28px rgba(0,40,100,0.10)' })}>
                      {/* fejléc: sorszám, ki / mikor, rejtés + törlés — NEM a képen (v10.440) */}
                      <div data-reveal-slidehead style={{ flexShrink:0, display:'flex', alignItems:'center', gap:10, padding:'10px 10px 8px 16px' }}>
                        <div style={{ flex:1, minWidth:0 }}>
                          <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                            <span data-reveal-slidenum style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, whiteSpace:'nowrap' }}>{i + 1}. kép</span>
                            {i === 0 && <span style={{ flexShrink:0, height:20, padding:'0 7px', borderRadius:999, display:'inline-flex', alignItems:'center', background:T.mintSoft || T.bgSoft, color:T.mintDeep || T.mint, fontFamily:T.font, fontWeight:900, fontSize:10, letterSpacing:'0.06em' }}>LEGÚJABB</span>}
                            {p.hidden && <span style={{ flexShrink:0, height:20, padding:'0 7px', borderRadius:999, display:'inline-flex', alignItems:'center', background:'#2A2533', color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:10, letterSpacing:'0.06em' }}>REJTVE</span>}
                          </div>
                          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkMute || T.inkSoft, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>{[p.by || 'Operátor', revealAgo(p.at, now)].filter(Boolean).join(' · ')}</div>
                        </div>
                        <button type="button" data-reveal-hide onClick={() => setHidden(p, !p.hidden)} aria-label={p.hidden ? 'Mutat a vetítőn' : 'Elrejt a vetítőről'} title={p.hidden ? 'Mutat' : 'Elrejt'}
                          style={iconBtn(false)}>{rvIcon(p.hidden ? 'eye' : 'eyeoff', 18)}</button>
                        <button type="button" data-reveal-del onClick={() => setConfirmDel(p)} aria-label="Törlés" title="Törlés" style={iconBtn(true)}>{rvIcon('trash', 18)}</button>
                      </div>
                      <div data-reveal-slideimg onClick={() => p.kind !== 'wish' && setZoom(p)} style={{ position:'relative', flex:'1 1 0', minHeight:120, margin:'0 10px', borderRadius:16, background: p.kind === 'wish' ? (T.bgSoft || T.bg) : DARK, cursor: p.kind === 'wish' ? 'default' : 'zoom-in', overflow:'hidden' }}>
                        {p.kind === 'wish'
                          ? <div style={{ position:'absolute', inset:0, display:'flex', alignItems:'center', justifyContent:'center', opacity: p.hidden ? 0.4 : 1 }}><RevealWishPolaroid text={p.text} by={p.by} width={220} /></div>
                          : <img src={p.src} alt={p.by ? 'Kép: ' + p.by : 'Kép'} style={{ width:'100%', height:'100%', objectFit:'contain', display:'block', opacity: p.hidden ? 0.3 : 1 }} />}
                        {p.kind !== 'wish' && <div aria-hidden="true" style={{ position:'absolute', right:10, bottom:10, height:26, padding:'0 9px', borderRadius:999, background:'rgba(0,0,0,0.45)', color:'#fff', display:'inline-flex', alignItems:'center', gap:5, fontFamily:T.font, fontWeight:800, fontSize:11 }}>{rvIcon('expand', 13)}Nagyítás</div>}
                      </div>
                      {p.kind !== 'wish' ? <RevealVotePicker item={p} /> : <div style={{ height:10 }} />}
                    </div>
                  </div>
                ))}
              </div>
              {/* v10.450: bélyegkép-csík — egy koppintás bármelyik képre (a ‹ › helyett) */}
              <div ref={stripRef} data-reveal-slidenav style={{ flexShrink:0, display:'flex', gap:8, overflowX:'auto', overflowY:'hidden', padding:'4px 4px 6px', margin:'0 -4px', scrollbarWidth:'none', WebkitOverflowScrolling:'touch' }}>
                {latest.map((p, i) => (
                  <button key={p.id} type="button" data-reveal-strip={i} aria-label={(i + 1) + '. kép'} aria-current={i === curSlide ? 'true' : undefined} onClick={() => goSlide(i)}
                    style={{ width:50, height:50, flexShrink:0, padding:0, border:'none', borderRadius:12, cursor:'pointer', overflow:'hidden', position:'relative', display:'grid', placeItems:'center',
                      background: p.kind === 'wish' ? RV_TONES.pink[0] : DARK, boxShadow: i === curSlide ? `0 0 0 3px ${T.mint}` : 'none', opacity: p.hidden ? 0.45 : 1 }}>
                    {p.kind === 'wish' ? <span aria-hidden="true" style={{ fontSize:18 }}>💌</span> : <img src={p.src} alt="" style={{ width:'100%', height:'100%', objectFit:'cover', display:'block' }} />}
                    {p.hidden && <span aria-hidden="true" style={{ position:'absolute', inset:0, display:'grid', placeItems:'center', color:'#fff', background:'rgba(0,0,0,0.25)' }}>{rvIcon('eyeoff', 16)}</span>}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
      <input ref={pickRef} data-reveal-input type="file" accept="image/*" multiple style={{ display:'none' }} onChange={e => { onFiles(e.target.files); e.target.value = ''; }} />
      {/* a feltöltés a hüvelykujj alatt — fix alsó dokk; a fölé nyíló lapok alatt eltűnik (v10.322) */}
      {!review && !zoom && revealBottomDock(<React.Fragment>
        {busy.total > 0 && (
          <div data-reveal-progress style={{ display:'flex', flexDirection:'column', gap:6 }}>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.ink }}>{busy.done >= busy.total ? `Kész — ${busy.total} kép feltöltve` : `Feltöltés… ${busy.done} / ${busy.total}`}</div>
            <div style={{ height:6, borderRadius:3, background:T.bgSoft, overflow:'hidden' }}><div style={{ height:'100%', width:`${Math.round(busy.done / busy.total * 100)}%`, background:T.mint, transition:'width .3s' }} /></div>
          </div>
        )}
        <button type="button" data-reveal-pick onClick={() => pickRef.current && pickRef.current.click()} style={rvBtn('primary', { width:'100%', height:52, borderRadius:16 })}>{rvIcon('upload', 20)}Képek feltöltése</button>
      </React.Fragment>, { 'data-reveal-opdock':'' })}""" + s[j:]
# a régi felső feltöltő-sor és a progress/hiba-kártya a fenti blokk ELŐTT állt — ellenőrzés:
assert s.count('data-reveal-pick ') == 1 or s.count('data-reveal-pick onClick') == 1

# ── Menü (szerepválasztó) ──────────────────────────────────────────────────────────
rep("""  if (ok && role === 'projector') return <RevealProjectorHost""", """  const revealAt = +((cfg.v && cfg.v.revealAt) || 0);
  const [now, setNow] = React.useState(() => Date.now());
  React.useEffect(() => { const iv = setInterval(() => setNow(Date.now()), 30000); return () => clearInterval(iv); }, []);
  if (ok && role === 'projector') return <RevealProjectorHost""")
i, j = between("          // v10.447: EGY kártya, három sor", "      </div>\n    </div>\n  );\n}\n\n// Admin → Gender Reveal")
s = s[:i] + r"""          // v10.450 (a jóváhagyott design): felül az esemény és a leleplezés ideje, alatta a három
          // szerep sorokban — mindegyiknél, melyik KÉSZÜLÉKRE való. Legalul egy sor a vendégeknek.
          <div data-reveal-menu style={{ width:'100%', maxWidth:520, display:'flex', flexDirection:'column', gap:14, flex:'1 0 auto' }}>
            <div data-reveal-menuhero style={{ position:'relative', overflow:'hidden', borderRadius:22, padding:'16px 18px', background:'linear-gradient(135deg, #CFE6FB 0%, #F7D9E6 100%)', color:REVEAL_INK }}>
              <div aria-hidden="true" style={{ position:'absolute', right:-18, top:-26, width:110, height:110, borderRadius:'50%', background:'#fff', opacity:0.35 }} />
              <div aria-hidden="true" style={{ position:'absolute', right:54, bottom:-40, width:80, height:80, borderRadius:'50%', background:'#fff', opacity:0.3 }} />
              <div style={{ position:'relative', display:'flex', alignItems:'center', gap:14 }}>
                <span style={{ width:64, height:64, flexShrink:0, borderRadius:20, background:'#fff', display:'grid', placeItems:'center', boxShadow:'0 4px 14px rgba(0,40,100,0.10)' }}><img src={REVEAL_LOGO} alt="" style={{ width:52, height:52 }} /></span>
                <div style={{ minWidth:0 }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:11, letterSpacing:'0.14em', opacity:0.75 }}>GENDER REVEAL</div>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, letterSpacing:'-0.02em', lineHeight:1.15 }}>{title}</div>
                  <div data-reveal-menuwhen style={{ display:'inline-flex', alignItems:'center', gap:6, marginTop:6, minHeight:26, padding:'4px 10px', boxSizing:'border-box', borderRadius:13, background:'rgba(255,255,255,0.8)', fontFamily:T.font, fontWeight:800, fontSize:12, lineHeight:1.3 }}>
                    {rvIcon('timer', 14)}{!revealAt ? 'Az időpontot a szülők adják meg' : revealAt > now ? `Leleplezés ${revealFmtShort(revealAt)} · még ${revealFmtLeft(revealAt - now).replace(/:\d\d$/, '').replace(/(\d+):(\d\d)$/, '$1 ó $2 p')}` : 'A leleplezés ideje elérkezett'}</div>
                </div>
              </div>
            </div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13, letterSpacing:'0.06em', color:T.inkSoft, padding:'2px 4px 0' }}>MI LESZ EZ A KÉSZÜLÉK?</div>
            <div data-reveal-roles style={rvCard({ border:'none', borderRadius:22, boxShadow:'0 5px 0 rgba(0,40,100,0.06), 0 12px 28px rgba(0,40,100,0.10)' })}>
              {[
                { id:'projector', icon:'screen', bg:'#D0E8FF', fg:'#1050A0', name:'Vetítő', sub:'A képek és a leleplezés a kivetítőn', device:'Laptop · kivetítő' },
                { id:'operator', icon:'cam', bg:'#FFF1D6', fg:'#8A5A00', name:'Operátor', sub:'Fotók feltöltése, tippek, jóváhagyás', device:'Fotós telefonja' },
                { id:'trigger', icon:'heart', bg:'#FCE4EE', fg:'#A8325E', name:'Szülők', sub:'Leleplezés, vetítő, kvíz, esemény', device:'Csak a szülőknek · kóddal', lock:true },
              ].map((r, i) => (
                <button key={r.id} type="button" data-reveal-role={r.id} onClick={() => { if (r.id === 'projector') revealAudio(); setRole(r.id); }}
                  style={{ width:'100%', display:'flex', alignItems:'center', gap:14, padding:14, border:'none', borderTop: i ? `1px solid ${T.border}` : 'none', background:'transparent', cursor:'pointer', textAlign:'left', boxSizing:'border-box', color:T.ink }}>
                  <span aria-hidden="true" style={{ width:52, height:52, flexShrink:0, borderRadius:16, background:r.bg, color:r.fg, display:'grid', placeItems:'center' }}>{rvIcon(r.icon, 26)}</span>
                  <span style={{ flex:1, minWidth:0, display:'flex', flexDirection:'column', alignItems:'flex-start' }}>
                    <span style={{ display:'flex', alignItems:'center', gap:6, fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink }}>{r.name}{r.lock && <span style={{ color:T.inkMute || T.inkSoft, display:'inline-flex' }}>{rvIcon('lock', 14)}</span>}</span>
                    <span style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkSoft, marginTop:2 }}>{r.sub}</span>
                    <span data-reveal-roledevice style={{ display:'inline-flex', alignItems:'center', marginTop:6, height:22, padding:'0 8px', borderRadius:999, background:T.bgSoft || T.bg, color:T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:11 }}>{r.device}</span>
                  </span>
                  <span style={{ color:T.inkMute || T.inkSoft, display:'flex' }}>{rvIcon('chev', 18)}</span>
                </button>
              ))}
            </div>
            <div style={{ flex:1, minHeight:4 }} />
            <div data-reveal-menuguest style={{ display:'flex', alignItems:'center', gap:12, padding:'12px 14px', borderRadius:18, border:`1.5px dashed ${T.border}`, background:'rgba(255,255,255,0.5)' }}>
              <span aria-hidden="true" style={{ width:38, height:38, flexShrink:0, borderRadius:12, background:T.surface, display:'grid', placeItems:'center', color:T.mint }}>{rvIcon('qr', 20)}</span>
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>Vendég vagy?</div>
                <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft, lineHeight:1.4 }}>Olvasd be a kivetítő QR-kódját — ahhoz nem kell jelszó.</div>
              </div>
            </div>
          </div>
        )}
""" + s[j:]

# 2. lépés: durva időformátum, a logó csak a jelszó előtt, a hookok a korai return ELŐTT
rep("""`Leleplezés ${revealFmtShort(revealAt)} · még ${revealFmtLeft(revealAt - now).replace(/:\\d\\d$/, '').replace(/(\\d+):(\\d\\d)$/, '$1 ó $2 p')}`""",
    "(`Leleplezés ${revealFmtShort(revealAt)}`).replace(/ /g, '\u00a0') + ' · ' + (`még ${revealFmtCoarse(revealAt - now)}`).replace(/ /g, '\u00a0')")
rep("""function revealFmtLeft(ms) {""", """// v10.450: „2 ó 14 p" / „3 nap 4 ó" / „12 p" — a Menü kártyájára (percre kerekítve, felfelé)
function revealFmtCoarse(ms) {
  const m0 = Math.max(0, Math.ceil(ms / 60000)), d = Math.floor(m0 / 1440), h = Math.floor(m0 % 1440 / 60), m = m0 % 60;
  return d ? d + ' nap ' + h + ' ó' : h ? h + ' ó ' + m + ' p' : m + ' p';
}
function revealFmtLeft(ms) {""")
rep("""        <img src={REVEAL_LOGO} alt="" style={{ width:104, height:104 }} />
        {!cfg.loaded ? (""", """        {!ok && <img src={REVEAL_LOGO} alt="" style={{ width:104, height:104 }} />}
        {!cfg.loaded ? (""")
H = """  const revealAt = +((cfg.v && cfg.v.revealAt) || 0);
  const [now, setNow] = React.useState(() => Date.now());
  React.useEffect(() => { const iv = setInterval(() => setNow(Date.now()), 30000); return () => clearInterval(iv); }, []);
"""
rep(H, "")
rep("""  // vendég- és album-link: jelszó nélkül, a saját kulcsukkal
  if ((gParam || albumParam) && cfg.loaded) {""", """  // ⚠️ a hookok a korai return-ök ELŐTT (vendég/album ág) — különben a hook-sorrend elcsúszik
""" + H + """  // vendég- és album-link: jelszó nélkül, a saját kulcsukkal
  if ((gParam || albumParam) && cfg.loaded) {""")
rep("style={{ width:50, height:50, flexShrink:0, padding:0, border:'none', borderRadius:12, cursor:'pointer', overflow:'hidden'", "style={{ width:46, height:46, flexShrink:0, padding:0, border:'none', borderRadius:12, cursor:'pointer', overflow:'hidden'")
rep("<div data-reveal-slider style={{ flex:'1 1 0', minHeight:330, display:'flex', flexDirection:'column', gap:10 }}>", "<div data-reveal-slider style={{ flex:'1 1 0', minHeight:330, display:'flex', flexDirection:'column', gap:6 }}>")
rep("overflowY:'hidden', padding:'4px 4px 6px', margin:'0 -4px', scrollbarWidth:'none'", "overflowY:'hidden', padding:'4px 4px', margin:'0 -4px', scrollbarWidth:'none'")
open(P, 'w', encoding='utf-8').write(s); print('ok')
