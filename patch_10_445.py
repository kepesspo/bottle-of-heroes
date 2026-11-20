# v10.445 — Gender Reveal operátor újratervezve (a Szülők készletével, a DNR téma színeivel):
# a kép jól látható (sötét háttér, nagyobb, koppintásra teljes képernyő), a Kisfiú/Kislány
# választó kisebb (egy sor), a jóváhagyásra várók vízszintes csíkban.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:120]); s = s.replace(old, new)

rep("const APP_VERSION = 'v10.444'", "const APP_VERSION = 'v10.445'")

# ── 1. a tipp-választó: EGY sor (személynél), a Személy/Pár ikon-kapcsoló a sor elején ──
a = s.index("function RevealVotePicker({ item }) {")
b = s.index("function RevealQrCard({ url, big }) {")
s = s[:a] + r'''// v10.445: kompakt — egy sor: [👤|👥] kapcsoló + Kisfiú / Kislány (40 px). Párnál egy
// második sor jön („2. tipp"). A kép kapja a helyet, nem a választó.
function RevealVotePicker({ item }) {
  const pair = !!item.pair;
  const votes = Array.isArray(item.votes) ? item.votes : [];
  const cur = [votes[0] || null, votes[1] || null];
  const set = (i, v) => { const nv = cur.slice(); nv[i] = nv[i] === v ? null : v; revealVoteWrite(item, pair, nv); };
  const kindBtn = (k, ic, label) => { const on = (k === 'pair') === pair;
    return <button key={k} type="button" data-reveal-votekind={k} aria-pressed={on} aria-label={label} title={label} onClick={() => { if (!on) revealVoteWrite(item, k === 'pair', cur); }}
      style={{ width:38, height:34, border:'none', borderRadius:9, cursor:'pointer', fontSize:16, lineHeight:1, background: on ? T.surface : 'transparent', boxShadow: on ? '0 1px 3px rgba(0,0,0,0.14)' : 'none', opacity: on ? 1 : 0.5 }}>{ic}</button>; };
  const vb = (on, s) => ({ flex:1, minWidth:0, height:40, padding:'0 6px', borderRadius:12, cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize:14,
    border: on ? `2px solid ${REVEAL_RESULTS[s].c1}` : `1.5px solid ${T.border}`, background: on ? REVEAL_RESULTS[s].c1 : T.surface, color: on ? '#fff' : T.ink,
    whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis', boxSizing:'border-box' });
  const row = i => (
    <div key={i} style={{ display:'flex', alignItems:'center', gap:6 }}>
      {i === 0
        ? <div role="group" aria-label="Ki tippel?" style={{ display:'flex', gap:2, padding:3, borderRadius:12, background:T.bgSoft || T.bg, flexShrink:0 }}>{kindBtn('single', '👤', 'Személy — 1 tipp')}{kindBtn('pair', '👥', 'Pár — 2 tipp')}</div>
        : <div style={{ width:84, flexShrink:0, textAlign:'right', paddingRight:6, boxSizing:'border-box', fontFamily:T.font, fontWeight:800, fontSize:12, color:T.inkSoft }}>2. tipp</div>}
      {REVEAL_VOTE_SIDES.map(s => (
        <button key={s} type="button" data-reveal-vote={s} data-vote-idx={i} aria-pressed={cur[i] === s} onClick={() => set(i, s)} style={vb(cur[i] === s, s)}>{REVEAL_RESULTS[s].emoji} {REVEAL_RESULTS[s].name}</button>
      ))}
    </div>
  );
  return (
    <div data-reveal-votepick={item.id} data-pair={pair ? '1' : '0'} style={{ flexShrink:0, padding:'8px 10px 10px', display:'flex', flexDirection:'column', gap:6, borderTop:`1px solid ${T.border}` }}>
      {row(0)}{pair && row(1)}
    </div>
  );
}
''' + s[b:]

# ── 2. az operátor ──
a = s.index("function RevealOperator({ onBack }) {")
b = s.index("// ── Szülők: külön kóddal, NEM az operátor")
s = s[:a] + r'''// ── Operátor (v10.445): a Szülők készletével, a DNR téma színeivel ─────────────────
// Fentről: feltöltés · (jóváhagyásra várók csíkja) · „A vetítőn" + tippek · LAPOZÓ, ami a
// maradék helyet kapja. A lapon: fejléc (sorszám, név, Elrejt, 🗑) → a KÉP sötét háttéren,
// koppintásra teljes képernyő → kompakt tipp-sor. Lent ‹ N / M ›.
// ⚠️ A legújabb mindig elöl, új kép érkezésekor a lapozó az elejére ugrik (v10.440).
function RevealOperator({ onBack }) {
  const { list: items, loaded } = useRevealPhotos(true);
  const [busy, setBusy] = React.useState({ done:0, total:0 });
  const [errs, setErrs] = React.useState([]);
  const [confirmDel, setConfirmDel] = React.useState(null);
  const [zoom, setZoom] = React.useState(null);
  // v10.437: az operátor NEM fotóz az appból — a saját kamerájával készíti, és csak feltölti.
  const pickRef = React.useRef(null);
  const onFiles = (fl) => {
    const files = revealImageFiles(fl);
    if (!files.length) return;
    setErrs([]);
    setBusy(b => ({ done:b.done, total:b.total + files.length }));
    revealUploadMany(files, null, () => setBusy(b => ({ done:b.done + 1, total:b.total })), m => setErrs(x => x.concat(m)))
      .then(() => setTimeout(() => setBusy(b => b.done >= b.total ? { done:0, total:0 } : b), 1500));
  };
  const db = revealDb();
  const setHidden = (p, h) => { if (db) db.collection('revealPhotos').doc(p.id).set({ hidden:h }, { merge:true }).catch(() => {}); };
  // ⚠️ Jóváhagyáskor az `at` friss lesz: így a vetítő ÚJ tételnek látja, és rögtön a mostani után jön.
  const approve = p => { if (db) db.collection('revealPhotos').doc(p.id).set({ pending:false, at:Date.now() }, { merge:true }).catch(() => {}); };
  const del = (p) => { if (db) db.collection('revealPhotos').doc(p.id).delete().catch(() => {}); setConfirmDel(null); };
  const pending = items.filter(p => p.pending);
  const approved = items.filter(p => !p.pending);
  const shown = approved.filter(p => !p.hidden).length;
  const latest = approved.slice().reverse();                 // ⚠️ a LEGÚJABB elöl
  const trackRef = React.useRef(null);
  const [slide, setSlide] = React.useState(0);
  const nSlides = latest.length, curSlide = Math.min(slide, Math.max(0, nSlides - 1));
  const goSlide = i => { const el = trackRef.current; if (!el) return; const k = Math.max(0, Math.min(nSlides - 1, i)); el.scrollTo({ left: k * el.clientWidth, behavior:'smooth' }); setSlide(k); };
  const onTrackScroll = e => { const el = e.currentTarget, k = Math.round(el.scrollLeft / Math.max(1, el.clientWidth)); if (k !== slide) setSlide(k); };
  const firstId = latest[0] ? latest[0].id : null, prevFirst = React.useRef(firstId);
  React.useEffect(() => {
    if (firstId && prevFirst.current && firstId !== prevFirst.current && trackRef.current) { trackRef.current.scrollTo({ left:0, behavior:'smooth' }); setSlide(0); }
    prevFirst.current = firstId;
  }, [firstId]);
  const tally = revealVoteTally(items);
  const DARK = '#16131C';
  const navBtn = on => rvBtn('secondary', { width:52, height:44, borderRadius:14, opacity: on ? 1 : 0.35, cursor: on ? 'pointer' : 'default' });
  return (
    <div data-reveal-operator style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title="Operátor" onBack={onBack} />
      <div data-reveal-opscroll style={{ flex:1, minHeight:0, overflowY:'auto', display:'flex', flexDirection:'column', padding:'10px 16px calc(10px + env(safe-area-inset-bottom))', boxSizing:'border-box', WebkitOverflowScrolling:'touch' }}>
        <div style={{ flex:'1 0 auto', width:'100%', maxWidth:720, margin:'0 auto', display:'flex', flexDirection:'column', gap:10 }}>
          <button type="button" data-reveal-pick onClick={() => pickRef.current && pickRef.current.click()} style={rvBtn('primary', { height:48, borderRadius:14, fontSize:16, flexShrink:0 })}>
            <span aria-hidden="true" style={{ fontSize:20, lineHeight:1 }}>🖼️</span>Képek feltöltése</button>
          <input ref={pickRef} data-reveal-input type="file" accept="image/*" multiple style={{ display:'none' }} onChange={e => { onFiles(e.target.files); e.target.value = ''; }} />
          {busy.total > 0 && (
            <div data-reveal-progress style={rvCard({ padding:'10px 14px' })}>
              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.ink, marginBottom:6 }}>{busy.done >= busy.total ? `Kész — ${busy.total} kép feltöltve` : `Feltöltés… ${busy.done} / ${busy.total}`}</div>
              <div style={{ height:6, borderRadius:3, background:T.bgSoft, overflow:'hidden' }}><div style={{ height:'100%', width:`${Math.round(busy.done / busy.total * 100)}%`, background:T.mint, transition:'width .3s' }} /></div>
            </div>
          )}
          {errs.length > 0 && (
            <div data-reveal-errors style={rvCard({ padding:'10px 14px', fontFamily:T.font, fontSize:13, fontWeight:700, color:'#A3342C', lineHeight:1.5, background:'#FBE7E4', border:'none' })}>
              {errs.map((e, i) => <div key={i}>⚠️ {e}</div>)}
            </div>
          )}
          {pending.length > 0 && (
            <section data-reveal-pending style={rvCard({ padding:'10px 0 12px', border:`2px solid ${REVEAL_PINK}` })}>
              <div style={{ display:'flex', alignItems:'center', gap:8, padding:'0 14px 8px' }}>
                <span style={{ flex:1, fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>Jóváhagyásra vár</span>
                {rvPill(String(pending.length), 'pink')}
              </div>
              <div style={{ display:'flex', gap:10, overflowX:'auto', padding:'0 14px', scrollbarWidth:'none' }}>
                {pending.map(p => (
                  <div key={p.id} data-reveal-pend={p.id} style={{ flex:'0 0 112px', display:'flex', flexDirection:'column', gap:6 }}>
                    <div style={{ position:'relative', height:96, borderRadius:12, overflow:'hidden', background: p.kind === 'wish' ? 'linear-gradient(165deg, #FFEFF5, #EAF4FD)' : DARK }}>
                      {p.kind === 'wish'
                        ? <div style={{ position:'absolute', inset:0, padding:'8px', display:'flex', alignItems:'center', justifyContent:'center', textAlign:'center', fontFamily:T.font, fontWeight:800, fontSize:11, color:'#3A2440', lineHeight:1.3, overflow:'hidden', overflowWrap:'anywhere' }}>{p.text}</div>
                        : <img src={p.src} alt="" style={{ width:'100%', height:'100%', objectFit:'cover', display:'block' }} />}
                      {p.by && <div style={{ position:'absolute', left:4, right:4, bottom:4, padding:'2px 6px', borderRadius:999, background:'rgba(0,0,0,0.6)', color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:10, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>{p.by}</div>}
                    </div>
                    <div style={{ display:'flex', gap:4 }}>
                      <button type="button" data-reveal-approve onClick={() => approve(p)} style={rvBtn('small', { flex:1, height:32, padding:0, background:T.mint, color:'#fff', border:'none' })}>Mehet</button>
                      <button type="button" data-reveal-reject onClick={() => del(p)} style={rvBtn('small', { flex:1, height:32, padding:0, color:'#A3342C', borderColor:'#E8B4AE' })}>Eldob</button>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}
          <div style={{ display:'flex', alignItems:'center', gap:8, flexShrink:0 }}>
            <div style={{ flex:1, fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>A vetítőn</div>
            <div data-reveal-opcount style={{ display:'flex', alignItems:'center', gap:6, fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft }}>
              {tally.boy + tally.girl > 0 && <span data-reveal-optally style={{ fontWeight:900, color:T.ink }}>Tippek: {REVEAL_RESULTS.boy.emoji} {tally.boy} · {REVEAL_RESULTS.girl.emoji} {tally.girl}</span>}
              <span>{shown} kép{approved.length > shown ? ` · ${approved.length - shown} rejtve` : ''}</span>
            </div>
          </div>
          {loaded && !approved.length && <div style={{ fontFamily:T.font, fontSize:14, fontWeight:700, color:T.inkSoft, textAlign:'center', padding:'24px 0' }}>Még nincs feltöltött kép.</div>}
          {nSlides > 0 && (
            <div data-reveal-slider style={{ flex:'1 1 0', minHeight:360, display:'flex', flexDirection:'column', gap:8 }}>
              <div ref={trackRef} data-reveal-track onScroll={onTrackScroll}
                style={{ flex:'1 1 0', minHeight:0, display:'flex', alignItems:'stretch', overflowX:'auto', overflowY:'hidden', scrollSnapType:'x mandatory', WebkitOverflowScrolling:'touch', scrollbarWidth:'none', margin:'0 -4px' }}>
                {latest.map((p, i) => (
                  <div key={p.id} data-reveal-thumb={p.id} data-hidden={p.hidden ? '1' : '0'} data-idx={i} style={{ flex:'0 0 100%', minWidth:0, boxSizing:'border-box', padding:'0 4px 2px', scrollSnapAlign:'center', display:'flex' }}>
                    <div style={rvCard({ flex:1, minWidth:0, display:'flex', flexDirection:'column' })}>
                      {/* fejléc: sorszám + név, Elrejt / Kuka — NEM a képen (v10.440) */}
                      <div data-reveal-slidehead style={{ flexShrink:0, display:'flex', alignItems:'center', gap:8, padding:'8px 10px 8px 14px' }}>
                        <span data-reveal-slidenum style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, whiteSpace:'nowrap' }}>{i + 1}. kép</span>
                        <span style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkSoft, whiteSpace:'nowrap' }}>/ {nSlides}</span>
                        {i === 0 && <span style={{ flexShrink:0, height:22, padding:'0 8px', borderRadius:999, display:'inline-flex', alignItems:'center', background:RV_TONES.pink[0], color:RV_TONES.pink[1], fontFamily:T.font, fontWeight:900, fontSize:10, letterSpacing:'0.06em' }}>LEGÚJABB</span>}
                        <span style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>{p.by || ''}</span>
                        <button type="button" data-reveal-hide onClick={() => setHidden(p, !p.hidden)} style={rvBtn('small', { height:34, background: p.hidden ? (T.mintSoft || T.surface) : T.surface })}>{p.hidden ? 'Mutat' : 'Elrejt'}</button>
                        <button type="button" data-reveal-del onClick={() => setConfirmDel(p)} aria-label="Törlés" style={rvBtn('small', { width:36, height:34, padding:0, borderColor:'#E8B4AE', fontSize:15 })}>🗑</button>
                      </div>
                      <div data-reveal-slideimg onClick={() => p.kind !== 'wish' && setZoom(p)} style={{ position:'relative', flex:'1 1 0', minHeight:120, background: p.kind === 'wish' ? (T.bgSoft || T.bg) : DARK, cursor: p.kind === 'wish' ? 'default' : 'zoom-in', overflow:'hidden' }}>
                        {p.kind === 'wish'
                          ? <div style={{ position:'absolute', inset:0, display:'flex', alignItems:'center', justifyContent:'center', opacity: p.hidden ? 0.4 : 1 }}><RevealWishPolaroid text={p.text} by={p.by} width={220} /></div>
                          : <img src={p.src} alt={p.by ? 'Kép: ' + p.by : 'Kép'} style={{ width:'100%', height:'100%', objectFit:'contain', display:'block', opacity: p.hidden ? 0.3 : 1 }} />}
                        {p.hidden && <div style={{ position:'absolute', top:8, left:8, padding:'3px 8px', borderRadius:999, background:'rgba(0,0,0,0.65)', color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:11 }}>REJTVE</div>}
                        {p.kind !== 'wish' && <div aria-hidden="true" style={{ position:'absolute', right:8, bottom:8, width:30, height:30, borderRadius:10, background:'rgba(0,0,0,0.45)', color:'#fff', display:'grid', placeItems:'center' }}>
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" /></svg></div>}
                      </div>
                      {p.kind !== 'wish' && <RevealVotePicker item={p} />}
                    </div>
                  </div>
                ))}
              </div>
              <div data-reveal-slidenav style={{ display:'flex', alignItems:'center', gap:10, flexShrink:0 }}>
                <button type="button" data-reveal-slideprev aria-label="Előző kép" disabled={curSlide <= 0} onClick={() => goSlide(curSlide - 1)} style={navBtn(curSlide > 0)}>{rvIcon('prev', 20)}</button>
                <div data-reveal-slidepos style={{ flex:1, textAlign:'center', fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{curSlide + 1} / {nSlides}</div>
                <button type="button" data-reveal-slidenext aria-label="Következő kép" disabled={curSlide >= nSlides - 1} onClick={() => goSlide(curSlide + 1)} style={navBtn(curSlide < nSlides - 1)}>{rvIcon('chev', 20)}</button>
              </div>
            </div>
          )}
        </div>
      </div>
      {zoom && (
        // teljes képernyős nézet — a kép a lehető legnagyobb; koppintásra bezárul
        <div data-reveal-oplightbox onClick={() => setZoom(null)} style={{ position:'fixed', inset:0, zIndex:7000, background:'#000', display:'flex', alignItems:'center', justifyContent:'center', cursor:'zoom-out' }}>
          <img src={zoom.src} alt="" style={{ maxWidth:'100%', maxHeight:'100%', objectFit:'contain', display:'block' }} />
          <button type="button" onClick={e => { e.stopPropagation(); setZoom(null); }} style={rvBtn('small', { position:'absolute', top:'calc(12px + env(safe-area-inset-top))', right:12, background:'rgba(255,255,255,0.92)', border:'none' })}>Bezárás</button>
          {zoom.by && <div style={{ position:'absolute', left:16, bottom:'calc(16px + env(safe-area-inset-bottom))', padding:'6px 12px', borderRadius:999, background:'rgba(0,0,0,0.6)', color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:13 }}>{zoom.by}</div>}
        </div>
      )}
      {confirmDel && (
        <ActionModal kicker={confirmDel.kind === 'wish' ? 'Törlöd az üzenetet?' : 'Törlöd a képet?'} onClose={() => setConfirmDel(null)} onSecondary={() => setConfirmDel(null)} secondaryLabel="Mégse"
          onPrimary={() => del(confirmDel)} primaryLabel="Törlés" primaryColor={T.coral}>
          {confirmDel.kind === 'wish' ? <div data-reveal-delpreview style={{ fontSize:15 }}>„{confirmDel.text}”</div>
            : <img data-reveal-delpreview src={confirmDel.src} alt="" style={{ display:'block', width:'100%', maxHeight:240, objectFit:'contain', borderRadius:12 }} />}
        </ActionModal>
      )}
    </div>
  );
}

''' + s[b:]
open(P, 'w', encoding='utf-8').write(s); print('ok')
