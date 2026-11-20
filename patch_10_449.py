# v10.449 — Gender Reveal: (1) vendégenként 1 kép + 1 üzenet, (2) jóváhagyás a Szülők
# nézetből is, (3) a vetítőn fix képszámláló + jobb felső jelvény a várakozókról.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:140]); s = s.replace(old, new)

rep("const APP_VERSION = 'v10.448';", "const APP_VERSION = 'v10.449';")

# ── közös: jóváhagyás / törlés + vendég-azonosító ──────────────────────────────────
rep("""function revealSendWish(text, by) {
  const db = revealDb(); if (!db) return Promise.reject(new Error('offline'));
  return db.collection('revealPhotos').add({ kind:'wish', text: String(text).trim().slice(0, REVEAL_WISH_MAX), by: String(by || '').trim().slice(0, 40), at:Date.now(), hidden:false, pending:true });
}""", """function revealSendWish(text, by, gid) {
  const db = revealDb(); if (!db) return Promise.reject(new Error('offline'));
  const doc = { kind:'wish', text: String(text).trim().slice(0, REVEAL_WISH_MAX), by: String(by || '').trim().slice(0, 40), at:Date.now(), hidden:false, pending:true };
  if (gid) doc.gid = gid;
  return db.collection('revealPhotos').add(doc);
}
// v10.449: jóváhagyás / eldobás — az operátor ÉS a Szülők ugyanezt hívja.
// ⚠️ Jóváhagyáskor az `at` friss lesz: így a vetítő ÚJ tételnek látja, és rögtön a mostani után jön.
function revealApprove(p) { const db = revealDb(); if (db && p) db.collection('revealPhotos').doc(p.id).set({ pending:false, at:Date.now() }, { merge:true }).catch(() => {}); }
function revealRemove(p) { const db = revealDb(); if (db && p) db.collection('revealPhotos').doc(p.id).delete().catch(() => {}); }
// v10.449: vendég-azonosító ESZKÖZÖNKÉNT (nem név szerint) — a „Nem te vagy?" névcsere nem
// nyit új keretet. Egy vendég 1 képet + 1 üzenetet küldhet; ha a beküldését eldobják
// (törlődik), újra küldhet.
const REVEAL_GUEST_LIMIT = { photo:1, wish:1 };
function revealGuestId() {
  let g = revealStore('boh_reveal_gid');
  if (!g) { g = 'g' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8); revealStore('boh_reveal_gid', g); }
  return g;
}
function revealGuestMine(all, gid, name) {
  return all.filter(p => p.gid ? p.gid === gid : (!!name && p.by === name));
}""")

# ── operátor: a közös helperekre ───────────────────────────────────────────────────
rep("""  // ⚠️ Jóváhagyáskor az `at` friss lesz: így a vetítő ÚJ tételnek látja, és rögtön a mostani után jön.
  const approve = p => { if (db) db.collection('revealPhotos').doc(p.id).set({ pending:false, at:Date.now() }, { merge:true }).catch(() => {}); };
  const del = (p) => { if (db) db.collection('revealPhotos').doc(p.id).delete().catch(() => {}); setConfirmDel(null); };""",
"""  const approve = revealApprove;
  const del = (p) => { revealRemove(p); setConfirmDel(null); };""")

# ── vendég: 1 kép + 1 üzenet ───────────────────────────────────────────────────────
rep("""  const { list: all } = useRevealPhotos(true);
  const mine = name ? all.filter(p => p.by === name).slice().reverse() : [];
  const flash = m => { setSent(m); setTimeout(() => setSent(''), 3500); };
  const onFiles = fl => {
    const files = revealImageFiles(fl); if (!files.length) return;
    setErrs([]); setBusy(b => ({ done:b.done, total:b.total + files.length }));
    revealUploadMany(files, { pending:true, by:name }, () => setBusy(b => ({ done:b.done + 1, total:b.total })), m => setErrs(x => x.concat(m)))
      .then(() => { flash('Köszönjük! Jóváhagyás után kerül a kivetítőre.'); setTimeout(() => setBusy({ done:0, total:0 }), 1500); });
  };
  const sendWish = () => {
    if (!wish.trim()) return;
    revealSendWish(wish, name).then(() => { setWish(''); flash('Köszönjük! Jóváhagyás után kerül a kivetítőre.'); }).catch(() => flash('Nem sikerült elküldeni.'));
  };""", """  const { list: all } = useRevealPhotos(true);
  const gid = React.useMemo(revealGuestId, []);
  const mine = revealGuestMine(all, gid, name).slice().reverse();
  // ⚠️ v10.449: egy vendég 1 kép + 1 üzenet. A küldés közbeni állapot (`sending`) is zár —
  // különben a pillanatkép visszaérkezéséig egy második koppintás átcsúszna.
  const [sending, setSending] = React.useState({ photo:false, wish:false });
  const myPhoto = mine.find(p => p.kind !== 'wish'), myWish = mine.find(p => p.kind === 'wish');
  const photoDone = !!myPhoto || sending.photo, wishDone = !!myWish || sending.wish;
  const flash = m => { setSent(m); setTimeout(() => setSent(''), 3500); };
  const onFiles = fl => {
    if (photoDone) return;
    const files = revealImageFiles(fl).slice(0, REVEAL_GUEST_LIMIT.photo); if (!files.length) return;
    setErrs([]); setSending(x => ({ ...x, photo:true })); setBusy({ done:0, total:files.length });
    revealUploadMany(files, { pending:true, by:name, gid }, () => setBusy(b => ({ done:b.done + 1, total:b.total })), m => setErrs(x => x.concat(m)))
      .then(() => { flash('Köszönjük! Jóváhagyás után kerül a kivetítőre.'); setTimeout(() => { setBusy({ done:0, total:0 }); setSending(x => ({ ...x, photo:false })); }, 1500); });
  };
  const sendWish = () => {
    if (!wish.trim() || wishDone) return;
    setSending(x => ({ ...x, wish:true }));
    revealSendWish(wish, name, gid).then(() => { setWish(''); flash('Köszönjük! Jóváhagyás után kerül a kivetítőre.'); })
      .catch(() => flash('Nem sikerült elküldeni.')).then(() => setTimeout(() => setSending(x => ({ ...x, wish:false })), 800));
  };
  // a „már elküldted" kártya — a saját beküldés, állapottal
  const doneCard = (p, what) => (
    <div data-reveal-guestdone={what} style={{ ...card, display:'flex', flexDirection:'column', alignItems:'center', gap:12, textAlign:'center', padding:'20px 16px' }}>
      {p && p.kind === 'wish' ? <RevealWishPolaroid text={p.text} by={p.by} width={220} />
        : p ? <img src={p.src} alt="" style={{ maxWidth:'100%', maxHeight:240, borderRadius:12, objectFit:'contain', background:'#16131C' }} />
        : <div aria-hidden="true" style={{ fontSize:30 }}>⏳</div>}
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink }}>{what === 'photo' ? 'A képedet elküldted' : 'Az üzenetedet elküldted'}</div>
      {p && pill(p)}
      <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkSoft, lineHeight:1.45 }}>Vendégenként egy kép és egy üzenet küldhető.{what === 'photo' ? (wishDone ? '' : ' Üzenetet még írhatsz!') : (photoDone ? '' : ' Képet még küldhetsz!')}</div>
      {what === 'photo' && !wishDone && <button onClick={() => setTab('wish')} style={rvBtn('secondary', { height:44 })}>Üzenet írása</button>}
      {what === 'wish' && !photoDone && <button onClick={() => setTab('photo')} style={rvBtn('secondary', { height:44 })}>Kép küldése</button>}
    </div>
  );""")
rep("""          <input ref={pickRef} data-reveal-guestinput type="file" accept="image/*" multiple style={{ display:'none' }} onChange={e => { onFiles(e.target.files); e.target.value = ''; }} />""",
    """          <input ref={pickRef} data-reveal-guestinput type="file" accept="image/*" style={{ display:'none' }} onChange={e => { onFiles(e.target.files); e.target.value = ''; }} />""")
rep("""            {segBtn('photo', 'Kép')}{segBtn('wish', 'Üzenet')}
          </div>
          {tab === 'photo' ? (""", """            {segBtn('photo', photoDone ? 'Kép · elküldve' : 'Kép')}{segBtn('wish', wishDone ? 'Üzenet · elküldve' : 'Üzenet')}
          </div>
          {tab === 'photo' && photoDone && !busy.total ? doneCard(myPhoto, 'photo')
          : tab === 'wish' && wishDone ? doneCard(myWish, 'wish')
          : tab === 'photo' ? (""")
rep("""                <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkSoft, marginTop:4 }}>Egyszerre többet is választhatsz.</div>""",
    """                <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkSoft, marginTop:4 }}>Egy képet küldhetsz — válaszd a kedvencedet!</div>""")
rep("""                <button onClick={() => camRef.current && camRef.current.click()} style={""", """                <button disabled={photoDone} onClick={() => camRef.current && camRef.current.click()} style={""")
rep("""                <button data-reveal-guestpick onClick={() => pickRef.current && pickRef.current.click()} style={""", """                <button data-reveal-guestpick disabled={photoDone} onClick={() => pickRef.current && pickRef.current.click()} style={""")
rep("""<div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.inkSoft, marginTop:6, lineHeight:1.45 }}>Egy fotót vagy egy kedves üzenetet — jóváhagyás után polaroidként jelenik meg.</div>""",
    """<div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.inkSoft, marginTop:6, lineHeight:1.45 }}>Egy fotót és egy kedves üzenetet — jóváhagyás után polaroidként jelenik meg.</div>""")

# ── Szülők: jóváhagyó gomb az állapot-sorban + a közös lapozó ─────────────────────
rep("""function RevealParentStatus() {""", """function RevealParentStatus({ pending, onReview }) {""")
rep("""      {q.phase && q.phase !== 'idle' ? rvPill('Kvíz megy', 'info', null, null, true) : paused ? rvPill('Vetítő áll', 'warn', null, null, true) : rvPill('Vetítő megy', 'ok', null, null, true)}
    </div>""", """      {q.phase && q.phase !== 'idle' ? rvPill('Kvíz megy', 'info', null, null, true) : paused ? rvPill('Vetítő áll', 'warn', null, null, true) : rvPill('Vetítő megy', 'ok', null, null, true)}
      {pending > 0 && (
        <button type="button" data-reveal-ppendbtn onClick={onReview} aria-label={`Jóváhagyás: ${pending} vár`}
          style={{ display:'inline-flex', alignItems:'center', gap:6, height:26, padding:'0 10px 0 4px', borderRadius:999, border:'none', cursor:'pointer', background:RV_TONES.warn[0], color:RV_TONES.warn[1], fontFamily:T.font, fontWeight:900, fontSize:12, whiteSpace:'nowrap' }}>
          <span data-reveal-ppendcount style={{ minWidth:18, height:18, padding:'0 5px', boxSizing:'border-box', borderRadius:999, background:RV_TONES.warn[2], color:'#fff', fontSize:11, display:'grid', placeItems:'center' }}>{pending}</span>
          Jóváhagyás ›
        </button>
      )}
    </div>""")
rep("""  const [tab, setTab] = React.useState('reveal');
  const [dock, setDock] = React.useState(null);
  const sec = secret.v || {};""", """  const [tab, setTab] = React.useState('reveal');
  const [dock, setDock] = React.useState(null);
  // v10.449: a Szülők is jóváhagyhatnak — UGYANAZ a lapozó, mint az operátornál
  const { list: allItems } = useRevealPhotos(true);
  const pendingItems = allItems.filter(p => p.pending);
  const [review, setReview] = React.useState(false);
  React.useEffect(() => { if (!pendingItems.length && review) setReview(false); }, [pendingItems.length]);
  const sec = secret.v || {};""")
rep("""      <RevealParentStatus />""", """      <RevealParentStatus pending={pendingItems.length} onReview={() => setReview(true)} />""")
rep("""      <RevealParentTabs tab={tab} onTab={setTab} dockRef={setDock} />
    </div>""", """      <RevealParentTabs tab={tab} onTab={setTab} dockRef={setDock} />
      {review && pendingItems.length > 0 && <RevealPendingReview items={pendingItems} onApprove={revealApprove} onReject={revealRemove} onClose={() => setReview(false)} />}
    </div>""")

# ── vetítő: fix képszámláló (bal fent) + várakozók jelvénye (jobb fent) ─────────────
rep("""function RevealProjector({ title, cfg, onExit }) {
  const { list: photos, loaded } = useRevealPhotos(false);""", """function RevealProjector({ title, cfg, onExit }) {
  // v10.449: MINDEN tételt figyelünk — a vetítő a várakozók számát is kiírja (jobb fent)
  const { list: allItems, loaded } = useRevealPhotos(true);
  const photos = React.useMemo(() => allItems.filter(p => !p.hidden && !p.pending), [allItems]);
  const pendingN = allItems.filter(p => p.pending).length;""")
rep("""  const topRef = React.useRef(null);
  const [topEdge, setTopEdge] = React.useState(0);
  React.useLayoutEffect(() => {
    const e = topRef.current;
    const v = e ? Math.round(e.offsetTop + e.offsetHeight + 10) : 0;
    if (v !== topEdge) setTopEdge(v);
  });""", """  // v10.449: a felső sor MINDEN eleme (jelvény/óra középen, számláló bal, várakozók jobb) —
  // a fal a legalacsonyabb ALJA alatt kezdődik.
  const topRef = React.useRef(null), rootRef = React.useRef(null);
  const [topEdge, setTopEdge] = React.useState(0);
  React.useLayoutEffect(() => {
    const els = rootRef.current ? Array.from(rootRef.current.querySelectorAll('[data-reveal-topm]')) : [];
    const v = els.reduce((m, e) => Math.max(m, Math.round(e.offsetTop + e.offsetHeight + 10)), 0);
    if (v !== topEdge) setTopEdge(v);
  });
  const nPhotos = photos.filter(p => p.src).length, nWish = photos.filter(p => p.kind === 'wish').length;
  const cornersOn = !qstate && !show;
  const cornerTop = narrow ? 56 : 'max(3vh, 74px)';
  const cornerChip = { position:'absolute', top:cornerTop, zIndex:45, display:'inline-flex', alignItems:'center', gap:'0.8vh', whiteSpace:'nowrap', padding: narrow ? '6px 12px' : '0.9vh 1.4vw', borderRadius:999,
    fontFamily:T.font, fontWeight:900, fontSize:'clamp(13px, 2.2vh, 26px)', boxShadow:'0 0.6vh 1.8vh rgba(60,40,20,0.12)' };""")
rep("""        <div ref={topRef} data-reveal-resultbadge style={{""", """        <div ref={topRef} data-reveal-topm data-reveal-resultbadge style={{""")
rep("""        <div ref={topRef} data-reveal-corner style={{""", """        <div ref={topRef} data-reveal-topm data-reveal-corner style={{""")
rep("""    <div data-reveal-projector data-reveal-current""", """    <div ref={rootRef} data-reveal-projector data-reveal-current""")
rep("""      {showQr && qrUrl && !qstate && !show && !narrow && (
        <div style={{ position:'absolute', right:'2vw', bottom:'3vh', zIndex:45 }}><RevealQrCard url={qrUrl} /></div>
      )}""", """      {cornersOn && (
        <div data-reveal-topm data-reveal-tally style={{ ...cornerChip, left:'2vw', background:'#fff', border:'2px solid #EFE2D2', color:REVEAL_INK }}>
          <span aria-hidden="true">📷</span><span data-reveal-count>{nPhotos} kép</span>
          {nWish > 0 && <React.Fragment><span aria-hidden="true" style={{ opacity:0.35 }}>·</span><span aria-hidden="true">💌</span><span data-reveal-wishcount>{nWish} üzenet</span></React.Fragment>}
        </div>
      )}
      {cornersOn && pendingN > 0 && (
        <div data-reveal-topm data-reveal-pendbadge={pendingN} style={{ ...cornerChip, right:'2vw', background:'#FFF1D6', border:'2px solid #F2D49A', color:'#7A4F00' }}>
          <span style={{ minWidth:'1.6em', height:'1.6em', padding:'0 0.4em', boxSizing:'border-box', borderRadius:999, background:'#E0A020', color:'#fff', display:'grid', placeItems:'center', fontSize:'0.85em' }}>{pendingN}</span>
          jóváhagyásra vár
        </div>
      )}
      {showQr && qrUrl && !qstate && !show && !narrow && (
        <div style={{ position:'absolute', right:'2vw', bottom:'3vh', zIndex:45 }}><RevealQrCard url={qrUrl} /></div>
      )}""")
rep("""        <span data-reveal-count style={{ flexShrink:0, whiteSpace:'nowrap', fontFamily:T.font, fontWeight:800, fontSize:13, color:REVEAL_INK, opacity:0.7 }}>{photos.filter(p => p.src).length} kép</span>
""", "")
open(P, 'w', encoding='utf-8').write(s); print('ok')
