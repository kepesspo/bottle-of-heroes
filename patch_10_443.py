# v10.443 — Gender Reveal: a vendég-QR mindig megjelenik (a kulcs magától létrejön),
# új vendégoldal (Kép / Üzenet fül, élő polaroid-előnézet, „Beküldéseid"), és az
# üzenet-polaroid saját designt kap (vonalas papír, washi-szalag) — EGY komponens a
# vetítőn és az előnézetben.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:120]); s = s.replace(old, new)

rep("const APP_VERSION = 'v10.442'", "const APP_VERSION = 'v10.443'")

# ── 1. a kulcsok magától létrejönnek ──
rep("function revealAlbumUrl(cfg) {", r"""// ⚠️ v10.443: a vendég- és album-kulcs eddig CSAK mentéskor keletkezett (admin jelszó /
// Szülők cím) — ha senki nem mentett, a vetítőn nem volt QR-kód. Most a vetítő és a
// Szülők nézet nyitáskor pótolja, ha hiányzik (csak a hiányzót írja, a meglévőt soha).
function revealEnsureKeys(cfg) {
  if (!cfg || (cfg.guestKey && cfg.albumKey)) return;
  const db = revealDb(); if (!db) return;
  const patch = {}; if (!cfg.guestKey) patch.guestKey = revealKeyGen(); if (!cfg.albumKey) patch.albumKey = revealKeyGen();
  db.collection('config').doc('revealConfig').set(patch, { merge:true }).catch(() => {});
}
function revealAlbumUrl(cfg) {""")
# a vetítő: a kapott cfg alapján
rep("""  const video = useRevealVideo();                          // a Szülők feltöltött videója (v10.439)
""", """  const video = useRevealVideo();                          // a Szülők feltöltött videója (v10.439)
  React.useEffect(() => { if (cfg) revealEnsureKeys(cfg); }, [cfg && cfg.guestKey, cfg && cfg.albumKey, !!cfg]);
""")
# a Szülők link-kártyája
rep("""  React.useEffect(() => { if (cfg.loaded && !init) { setTitle((cfg.v || {}).title || ''); setInit(true); } }, [cfg.loaded]);
  const db = revealDb();
  const v = cfg.v || {};""", """  React.useEffect(() => { if (cfg.loaded && !init) { setTitle((cfg.v || {}).title || ''); setInit(true); } }, [cfg.loaded]);
  React.useEffect(() => { if (cfg.loaded) revealEnsureKeys(cfg.v || {}); }, [cfg.loaded, cfg.v && cfg.v.guestKey, cfg.v && cfg.v.albumKey]);
  const db = revealDb();
  const v = cfg.v || {};""")
rep("""      </div> : <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft }}>A cím első mentésekor jön létre.</div>}""",
    """      </div> : <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft }}>Létrehozás…</div>}""")

# ── 2. a vetítő QR-kártyája: egyértelmű felirat ──
rep("""        <div style={{ fontWeight:900, fontSize: big ? 'clamp(20px, 3.4vh, 40px)' : 'clamp(12px, 1.7vh, 18px)', lineHeight:1.25, maxWidth: big ? '9em' : 'none' }}>{big ? 'Olvasd be, és válaszolj a telefonodon!' : '📷 Tölts fel képet'}</div>
        {!big && <div style={{ fontWeight:800, fontSize:'clamp(12px, 1.7vh, 18px)', lineHeight:1.25, marginTop:2 }}>💌 Írj a babának</div>}""",
"""        <div style={{ fontWeight:900, fontSize: big ? 'clamp(20px, 3.4vh, 40px)' : 'clamp(13px, 1.9vh, 20px)', lineHeight:1.2, maxWidth: big ? '9em' : 'none' }}>{big ? 'Olvasd be, és válaszolj a telefonodon!' : 'Küldj képet vagy üzenetet!'}</div>
        {!big && <div style={{ fontWeight:800, fontSize:'clamp(11px, 1.5vh, 16px)', lineHeight:1.3, marginTop:4, color:'#6B6475' }}>Olvasd be a telefonoddal — jóváhagyás után kerül ide.</div>}""")

# ── 3. az üzenet-polaroid: EGY arc (vetítő + előnézet) ──
rep("function RevealBoardCard({ item, g, z, isNew, isCur }) {", r"""// Az üzenet „arca" a polaroidon (v10.443): vonalas levélpapír rózsa → krém → kék
// átmenettel, rózsa margóvonal, halvány nagy idézőjel és két kis lufi a sarokban.
// ⚠️ EGY komponens: a vetítő polaroidja ÉS a vendég élő előnézete is ezt rajzolja —
// így a vendég pontosan azt látja, ami a kivetítőre kerül.
function revealWishFont(text, w, h) {
  const len = (text || '').length;
  return Math.max(13, Math.min(h / (len > 90 ? 7.4 : len > 50 ? 5.9 : 4.5), w / (len > 90 ? 13 : 10)));
}
function RevealWishFace({ text, w, h }) {
  const fs = revealWishFont(text, w, h), lh = Math.round(fs * 1.34);
  return (
    <div data-reveal-wishface style={{ position:'relative', width:w, height:h, borderRadius:2, overflow:'hidden', boxSizing:'border-box',
      background:'linear-gradient(165deg, #FFEFF5 0%, #FFF8EF 50%, #EAF4FD 100%)' }}>
      <div aria-hidden="true" style={{ position:'absolute', inset:0, backgroundImage:`repeating-linear-gradient(to bottom, transparent 0, transparent ${lh - 1}px, rgba(120,170,220,0.22) ${lh - 1}px, rgba(120,170,220,0.22) ${lh}px)` }} />
      <div aria-hidden="true" style={{ position:'absolute', top:0, bottom:0, left: Math.round(w * 0.1), width:2, background:'rgba(244,150,180,0.5)' }} />
      <div aria-hidden="true" style={{ position:'absolute', left: Math.round(w * 0.13), top: Math.round(-h * 0.05), fontFamily:'Georgia, "Times New Roman", serif', fontWeight:900, fontSize: Math.round(h * 0.36), lineHeight:1, color:REVEAL_PINK, opacity:0.38 }}>“</div>
      <svg aria-hidden="true" viewBox="0 0 60 70" style={{ position:'absolute', right: Math.round(w * 0.04), bottom: Math.round(h * 0.04), width: Math.round(Math.min(w, h) * 0.2), height:'auto', opacity:0.85 }}>
        <path d="M20 40 Q22 55 30 68 M42 36 Q40 52 30 68" fill="none" stroke="#6B6475" strokeWidth="1.4" />
        <ellipse cx="20" cy="22" rx="13" ry="16" fill={REVEAL_PINK} /><ellipse cx="42" cy="20" rx="12" ry="15" fill={REVEAL_BLUE} />
        <ellipse cx="16" cy="16" rx="3" ry="5" fill="#fff" opacity="0.55" /><ellipse cx="38" cy="14" rx="3" ry="5" fill="#fff" opacity="0.55" />
      </svg>
      <div style={{ position:'absolute', inset:0, display:'flex', alignItems:'center', justifyContent:'center', textAlign:'center', boxSizing:'border-box',
        padding:`${Math.round(h * 0.12)}px ${Math.round(w * 0.1)}px ${Math.round(h * 0.14)}px ${Math.round(w * 0.16)}px` }}>
        <div data-reveal-wishtext style={{ fontFamily:T.font, fontWeight:800, fontSize: fs, lineHeight: lh + 'px', color:'#3A2440', overflowWrap:'anywhere' }}>{text}</div>
      </div>
    </div>
  );
}
// a washi-szalag az üzenet-polaroid tetején (a lapon kívül lóg — a kártya nem vág)
function RevealWishTape({ w, pad }) {
  return <div aria-hidden="true" style={{ position:'absolute', left:'50%', top: -Math.round(pad * 1.1), width: Math.round(w * 0.34), height: Math.round(Math.max(14, pad * 2.2)),
    transform:'translateX(-50%) rotate(-3deg)', background:'repeating-linear-gradient(45deg, rgba(244,150,180,0.62) 0 8px, rgba(255,255,255,0.4) 8px 14px)', boxShadow:'0 1px 3px rgba(60,40,20,0.12)' }} />;
}
// a vendég élő előnézete: UGYANAZ a polaroid, mint a vetítőn
function RevealWishPolaroid({ text, by, width }) {
  const pad = Math.round(width * 0.045), bottom = Math.round(width * 0.17), iw = width - pad * 2, ih = Math.round(iw * 0.82);
  return (
    <div data-reveal-wishpreview style={{ position:'relative', width, boxSizing:'border-box', background:'#FFFFFF', border:'1px solid #EFE2D2', borderRadius:6,
      padding:`${pad}px ${pad}px ${bottom}px`, transform:'rotate(-2deg)', boxShadow:'0 14px 30px rgba(60,40,20,0.18)' }}>
      <RevealWishTape w={width} pad={pad} />
      <RevealWishFace text={text} w={iw} h={ih} />
      <div style={{ position:'absolute', left:0, right:0, bottom:0, height:bottom, display:'flex', alignItems:'center', justifyContent:'center', padding:'0 10px', boxSizing:'border-box',
        fontFamily:'"Comic Sans MS", "Segoe Print", "Bradley Hand", cursive', fontWeight:700, fontSize: Math.max(13, bottom * 0.42), color:'#C0507A', whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>{by ? '— ' + by : ''}</div>
    </div>
  );
}
function RevealBoardCard({ item, g, z, isNew, isCur }) {""")
rep("""      {wish ? (
        <div style={{ width: g.iw, height: g.ih, borderRadius:2, background:'#FFF1F5', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', textAlign:'center', padding:'6%', boxSizing:'border-box', overflow:'hidden' }}>
          <div aria-hidden="true" style={{ fontSize: Math.max(22, g.ih * 0.13), lineHeight:1, marginBottom: g.ih * 0.04 }}>💌</div>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize: fs, lineHeight:1.28, color:'#2A1E3A', overflowWrap:'anywhere' }}>„{item.text}”</div>
        </div>
      ) : (""", """      {wish && <RevealWishTape w={g.cw} pad={g.pad} />}
      {wish ? <RevealWishFace text={item.text} w={g.iw} h={g.ih} /> : (""")
rep("""  const len = (item.text || '').length;
  const fs = Math.max(14, Math.min(g.ih / (len > 90 ? 7.5 : len > 50 ? 6 : 4.6), g.iw / (len > 90 ? 13 : 10)));
  const vs = wish ? [] : revealVotesOf(item);""", """  const vs = wish ? [] : revealVotesOf(item);""")

# ── 4. az új vendégoldal ──
a = s.index("function RevealGuest({ cfg }) {")
b = s.index("// ── Album (csak nézhető galéria-link a szülőknek)")
s = s[:a] + r'''// v10.443: két fül (Kép / Üzenet). Az üzenet-fülön ÉLŐ polaroid-előnézet — pontosan az
// a lap, ami a kivetítőre kerül (`RevealWishPolaroid` → `RevealWishFace`). Alul a
// „Beküldéseid": a saját (név szerint) beküldések állapottal — jóváhagyásra vár / a
// kivetítőn. Az eldobott tétel törlődik, tehát onnan is eltűnik. A téma színeit viseli.
function RevealGuest({ cfg }) {
  const [name, setName] = React.useState(() => revealStore('boh_reveal_guest_name') || '');
  const [nameInp, setNameInp] = React.useState('');
  const [tab, setTab] = React.useState('photo');
  const [busy, setBusy] = React.useState({ done:0, total:0 });
  const [errs, setErrs] = React.useState([]);
  const [wish, setWish] = React.useState('');
  const [sent, setSent] = React.useState('');
  const pickRef = React.useRef(null), camRef = React.useRef(null);
  const { list: all } = useRevealPhotos(true);
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
  };
  const saveName = () => { const n = nameInp.trim(); if (!n) return; revealStore('boh_reveal_guest_name', n); setName(n); };
  const card = { background:T.surface, borderRadius:20, padding:16, boxShadow:T.shadow, boxSizing:'border-box' };
  const title = (cfg && cfg.title) || 'Gender Reveal';
  const segBtn = (id, label) => <button key={id} data-reveal-guesttab={id} role="tab" aria-selected={tab === id} onClick={() => setTab(id)}
    style={{ flex:1, height:42, borderRadius:12, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize:15,
      background: tab === id ? T.surface : 'transparent', color: tab === id ? T.ink : T.inkSoft, boxShadow: tab === id ? '0 1px 4px rgba(0,0,0,0.12)' : 'none' }}>{label}</button>;
  const pill = p => p.pending
    ? <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11, padding:'3px 8px', borderRadius:999, background:'#FFF1D6', color:'#7A4F00', whiteSpace:'nowrap' }}>Jóváhagyásra vár</span>
    : <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11, padding:'3px 8px', borderRadius:999, background:'#E2F3EC', color:'#1F6B50', whiteSpace:'nowrap' }}>A kivetítőn</span>;
  if (!name) return (
    <div data-reveal-guest="name" style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title={title} />
      <div style={{ flex:1, overflowY:'auto', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:18, padding:'22px 16px calc(24px + env(safe-area-inset-bottom))' }}>
        <img src={REVEAL_LOGO} alt="" style={{ width:120, height:120 }} />
        <div style={{ textAlign:'center' }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:24, color:T.ink }}>Küldj valamit a kivetítőre!</div>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.inkSoft, marginTop:6, lineHeight:1.45 }}>Egy fotót vagy egy kedves üzenetet — jóváhagyás után polaroidként jelenik meg.</div>
        </div>
        <div style={{ ...card, width:'100%', maxWidth:440, display:'flex', flexDirection:'column', gap:12 }}>
          <label htmlFor="rv-guestname" style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>Hogy hívnak?</label>
          <input id="rv-guestname" data-reveal-guestname value={nameInp} onChange={e => setNameInp(e.target.value.slice(0, 40))} onKeyDown={e => { if (e.key === 'Enter') saveName(); }} placeholder="A neved — ez kerül a polaroid aljára"
            style={{ width:'100%', boxSizing:'border-box', padding:'14px', borderRadius:14, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:17, fontWeight:700, color:T.ink, outline:'none' }} />
          <PrimaryButton onClick={saveName} disabled={!nameInp.trim()}>Tovább</PrimaryButton>
        </div>
      </div>
    </div>
  );
  return (
    <div data-reveal-guest="main" style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title={title} />
      <div style={{ flex:1, overflowY:'auto', padding:'14px 16px calc(24px + env(safe-area-inset-bottom))' }}>
        <div style={{ maxWidth:520, margin:'0 auto', display:'flex', flexDirection:'column', gap:14 }}>
          <div style={{ display:'flex', alignItems:'center', gap:10 }}>
            <div style={{ flex:1, fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink }}>Szia, {name}!</div>
            <button onClick={() => { setName(''); setNameInp(name); }} style={{ border:'none', background:'transparent', color:T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:13, cursor:'pointer', padding:'8px 4px' }}>Nem te vagy?</button>
          </div>
          <input ref={camRef} type="file" accept="image/*" capture="environment" style={{ display:'none' }} onChange={e => { onFiles(e.target.files); e.target.value = ''; }} />
          <input ref={pickRef} data-reveal-guestinput type="file" accept="image/*" multiple style={{ display:'none' }} onChange={e => { onFiles(e.target.files); e.target.value = ''; }} />
          <div role="tablist" aria-label="Mit küldesz?" style={{ display:'flex', gap:4, padding:4, borderRadius:16, background:T.bgSoft || T.surfaceMuted }}>
            {segBtn('photo', 'Kép')}{segBtn('wish', 'Üzenet')}
          </div>
          {tab === 'photo' ? (
            <div style={{ ...card, display:'flex', flexDirection:'column', alignItems:'center', gap:14, textAlign:'center', border:`2px dashed ${T.border}`, boxShadow:'none', padding:'22px 16px' }}>
              <div aria-hidden="true" style={{ width:64, height:64, borderRadius:20, background:T.mintSoft || T.bgSoft, display:'grid', placeItems:'center', fontSize:30 }}>📷</div>
              <div>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink }}>Fotó a kivetítőre</div>
                <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkSoft, marginTop:4 }}>Egyszerre többet is választhatsz.</div>
              </div>
              <div style={{ display:'flex', gap:10, width:'100%' }}>
                <button onClick={() => camRef.current && camRef.current.click()} style={{ flex:1, height:50, borderRadius:14, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer' }}>Fotózás</button>
                <button data-reveal-guestpick onClick={() => pickRef.current && pickRef.current.click()} style={{ flex:1, height:50, borderRadius:14, border:`2px solid ${T.mint}`, background:'transparent', color:T.mint, fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer' }}>Galériából</button>
              </div>
              {busy.total > 0 && <div style={{ width:'100%' }}>
                <div style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft, marginBottom:6 }}>{busy.done >= busy.total ? 'Feltöltve' : `Feltöltés… ${busy.done} / ${busy.total}`}</div>
                <div style={{ height:6, borderRadius:3, background:T.bgSoft, overflow:'hidden' }}><div style={{ height:'100%', width:`${Math.round(busy.done / Math.max(1, busy.total) * 100)}%`, background:T.mint, transition:'width .3s' }} /></div>
              </div>}
              {errs.map((e, i) => <div key={i} style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.coral }}>⚠️ {e}</div>)}
            </div>
          ) : (
            <div style={{ ...card, display:'flex', flexDirection:'column', gap:14 }}>
              <div style={{ display:'flex', justifyContent:'center', padding:'14px 0 4px' }}>
                <RevealWishPolaroid text={wish.trim() || 'Ide jön az üzeneted…'} by={name} width={250} />
              </div>
              <textarea data-reveal-wishinput value={wish} onChange={e => setWish(e.target.value.slice(0, REVEAL_WISH_MAX))} rows={3} placeholder="Írj egy kedves üzenetet a babának…" aria-label="Üzenet"
                style={{ width:'100%', boxSizing:'border-box', padding:'12px 14px', borderRadius:14, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:16, fontWeight:700, color:T.ink, outline:'none', resize:'none' }} />
              <div style={{ display:'flex', alignItems:'center', gap:10 }}>
                <span style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft }}>{wish.length} / {REVEAL_WISH_MAX}</span>
                <button data-reveal-wishsend disabled={!wish.trim()} onClick={sendWish} style={{ height:48, padding:'0 24px', borderRadius:14, border:'none', background: wish.trim() ? T.mint : T.surfaceMuted, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15, cursor: wish.trim() ? 'pointer' : 'default' }}>Küldés</button>
              </div>
            </div>
          )}
          {sent && <div data-reveal-guestsent role="status" style={{ ...card, padding:'12px 14px', fontFamily:T.font, fontWeight:800, fontSize:14, color:'#1F6B50', background:'#E2F3EC', boxShadow:'none', textAlign:'center' }}>{sent}</div>}
          {mine.length > 0 && (
            <div data-reveal-mine style={{ ...card, display:'flex', flexDirection:'column', gap:10 }}>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>Beküldéseid</div>
              {mine.slice(0, 8).map(p => (
                <div key={p.id} data-reveal-mineitem={p.id} data-pending={p.pending ? '1' : '0'} style={{ display:'flex', alignItems:'center', gap:12 }}>
                  {p.kind === 'wish'
                    ? <div aria-hidden="true" style={{ width:44, height:44, flexShrink:0, borderRadius:10, background:'linear-gradient(165deg, #FFEFF5, #EAF4FD)', display:'grid', placeItems:'center', fontSize:20 }}>💌</div>
                    : <img src={p.src} alt="" style={{ width:44, height:44, flexShrink:0, borderRadius:10, objectFit:'cover' }} />}
                  <div style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:700, fontSize:13, color:T.ink, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>{p.kind === 'wish' ? p.text : 'Fotó'}</div>
                  {pill(p)}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

''' + s[b:]
rep('  const boardH = meterOn ? vp.h * REVEAL_METER_ROOM : vp.h;', '  // v10.443: a vendég-QR (jobb alsó sarok) sem lóghat rá a lapokra — a fal alja a QR\n  // fölött van; a számláló és a QR közül a magasabb dönt.\n  const qrOn = !!(showQr && qrUrl && !qstate && !show && !narrow);\n  const qrRoom = qrOn ? Math.round(Math.min(Math.max(84, vp.h * 0.13), 150) + 20 + vp.h * 0.03 + 12) : 0;\n  const boardH = vp.h - Math.max(meterOn ? vp.h * (1 - REVEAL_METER_ROOM) : 0, qrRoom);')
rep('g={revealCardGeom(i, nSlots, vp.w, Math.max(1, boardH - topEdge), it, s.key, topEdge > 0)}', 'g={revealCardGeom(i, nSlots, vp.w, Math.max(1, boardH - topEdge), it, s.key, topEdge > 0 || boardH < vp.h)}')
open(P, 'w', encoding='utf-8').write(s); print('ok')
