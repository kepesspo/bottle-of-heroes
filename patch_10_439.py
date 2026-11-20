# v10.439 — Gender Reveal: az admin beállításai is a Szülőkhöz kerülnek.
# Az adminban CSAK a titkos/belépési rész marad: jelszó, eredmény, szülői kód, videó-link
# (+ állapot és vészhelyzeti visszaállítás). Minden más (cím, linkek, időpont,
# visszaszámláló, Babakvíz-kérdések, album, ürítés) a Szülők nézetbe megy.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()

def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:120])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.438'", "const APP_VERSION = 'v10.439'")

# ── 1. a kvíz-szerkesztő: név + szöveg (a Szülők használják) ──
rep("function AdminRevealQuiz() {", "function RevealQuizEditor() {")
rep("A vendégek papíron karikáznak (A/B/C); a vetítőn vagy az operátor telefonján lapoztok.",
    "A vendégek papíron karikáznak (A/B/C); a lapozó fent van.")

# ── 2. az AdminReveal újraírva (csak a titkos rész) + a Szülők új kártyái ──
a = s.index("function AdminReveal() {")
b = s.index("// ── Pub: saját keverés űrlap")
NEW = r'''// Közös kártya-elemek a Szülők nézet kártyáihoz (függvények, nem komponensek — v10.335).
// ⚠️ A `T` futásidőben cserélődik (téma), ezért NEM modul-szintű konstans.
function rvCard(extra) { return Object.assign({ width:'100%', maxWidth:440, background:T.surface, borderRadius:20, padding:'16px', boxShadow:T.shadow, boxSizing:'border-box' }, extra || {}); }
function rvH(t) { return <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink }}>{t}</div>; }
function rvNote(t) { return <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:4, lineHeight:1.45 }}>{t}</div>; }
function rvLabel(t) { return <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, fontWeight:800, textTransform:'uppercase', letterSpacing:'0.07em', margin:'12px 0 6px' }}>{t}</div>; }
function rvInp(extra) { return Object.assign({ width:'100%', boxSizing:'border-box', padding:'12px', borderRadius:12, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none' }, extra || {}); }
function rvBtn(primary, extra) { return Object.assign({ padding:'11px 16px', borderRadius:12, border: primary ? 'none' : `1.5px solid ${T.border}`, background: primary ? T.mint : 'transparent', color: primary ? '#fff' : T.inkSoft, fontFamily:T.font, fontWeight:900, fontSize:13, cursor:'pointer' }, extra || {}); }
function rvMsg(m, data) { return m ? <span {...{ [data]: '' }} style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft }}>{m}</span> : null; }
function revealToLocalInput(ms) { if (!ms) return ''; const d = new Date(+ms), p2 = n => String(n).padStart(2, '0'); return d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate()) + 'T' + p2(d.getHours()) + ':' + p2(d.getMinutes()); }
function useRevealFlash() { const [m, setM] = React.useState(''); return [m, t => { setM(t); setTimeout(() => setM(''), 2500); }]; }

// ── Szülők: időpont + visszaszámláló (revealConfig — NEM titkos, a vetítő olvassa) ──
function RevealScheduleCard() {
  const cfg = useRevealCfg();
  const [when, setWhen] = React.useState('');
  const [cd, setCd] = React.useState(true);
  const [init, setInit] = React.useState(false);
  const [msg, flash] = useRevealFlash();
  React.useEffect(() => { if (cfg.loaded && !init) { const v = cfg.v || {}; setWhen(revealToLocalInput(v.revealAt)); setCd(v.countdownOn !== false); setInit(true); } }, [cfg.loaded]);
  const save = () => {
    const db = revealDb(); if (!db) return;
    const at = when ? Date.parse(when) : 0;     // datetime-local → HELYI idő
    db.collection('config').doc('revealConfig').set({ revealAt: isFinite(at) ? at : 0, countdownOn: !!cd }, { merge:true })
      .then(() => flash('Mentve ✓')).catch(e => flash('Nem sikerült menteni (' + ((e && e.code) || 'hiba') + ')'));
  };
  return (
    <div data-reveal-p-schedule style={rvCard()}>
      {rvH('⏰ Időpont')}
      {rvNote('Az időpontra a vetítő magától indul — de csak ha fent engedélyeztétek. Időpont nélkül csak a „Leleplezés most" gomb indítja.')}
      {rvLabel('A leleplezés időpontja')}
      <input data-reveal-p-when type="datetime-local" value={when} onChange={e => setWhen(e.target.value)} style={rvInp()} />
      <label style={{ display:'flex', alignItems:'center', gap:10, marginTop:12, cursor:'pointer', fontFamily:T.font, fontSize:13, fontWeight:700, color:T.ink }}>
        <input data-reveal-p-countdown type="checkbox" checked={cd} onChange={e => setCd(e.target.checked)} style={{ accentColor:T.mint }} />
        Visszaszámláló a vetítő tetején, középen
      </label>
      <div style={{ display:'flex', alignItems:'center', gap:12, marginTop:14 }}>
        <button data-reveal-p-schedsave onClick={save} style={rvBtn(true)}>Mentés</button>
        {rvMsg(msg, 'data-reveal-p-schedmsg')}
      </div>
    </div>
  );
}

// ── Szülők: a Babakvíz kérdései (lenyitható — ritkán kell) ──
function RevealQuizEditBox() {
  const [open, setOpen] = React.useState(false);
  return open ? <div data-reveal-p-quizedit style={{ display:'flex', flexDirection:'column', gap:8 }}>
      <RevealQuizEditor />
      <button onClick={() => setOpen(false)} style={rvBtn(false, { alignSelf:'center' })}>Kérdések bezárása</button>
    </div>
    : <button data-reveal-p-quizeditbtn onClick={() => setOpen(true)} style={rvBtn(false, { width:'100%' })}>✏️ Kérdések szerkesztése</button>;
}

// ── Szülők: cím + vendég- és galéria-link ──
function RevealLinksCard() {
  const cfg = useRevealCfg();
  const [title, setTitle] = React.useState('');
  const [init, setInit] = React.useState(false);
  const [msg, flash] = useRevealFlash();
  React.useEffect(() => { if (cfg.loaded && !init) { setTitle((cfg.v || {}).title || ''); setInit(true); } }, [cfg.loaded]);
  const db = revealDb();
  const v = cfg.v || {};
  // a kulcsok az első mentéskor keletkeznek (itt vagy az admin jelszó-mentésénél), utána változatlanok
  const save = () => { if (db) db.collection('config').doc('revealConfig').set({ title: title.trim(), guestKey: v.guestKey || revealKeyGen(), albumKey: v.albumKey || revealKeyGen() }, { merge:true })
    .then(() => flash('Mentve ✓')).catch(e => flash('Nem sikerült menteni (' + ((e && e.code) || 'hiba') + ')')); };
  const newKey = k => { if (db) db.collection('config').doc('revealConfig').set({ [k]: revealKeyGen() }, { merge:true }).then(() => flash('Új link kész — a régi már nem működik')).catch(() => {}); };
  const copy = t => { try { navigator.clipboard.writeText(t); flash('Link kimásolva'); } catch(e) {} };
  const row = (lab, url, k, data) => (
    <div>
      {rvLabel(lab)}
      {url ? <div style={{ display:'flex', gap:8 }}>
        <input readOnly value={url} {...{ [data]: '' }} style={rvInp({ fontSize:12, minWidth:0 })} />
        <button onClick={() => copy(url)} style={rvBtn(false, { padding:'11px 12px' })}>Másol</button>
        <button onClick={() => newKey(k)} style={rvBtn(false, { padding:'11px 12px' })}>Új</button>
      </div> : <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft }}>A cím első mentésekor jön létre.</div>}
    </div>
  );
  return (
    <div data-reveal-p-links style={rvCard()}>
      {rvH('🔗 Cím és linkek')}
      {rvLabel('Cím (a vetítőn és a vendégoldalon)')}
      <input data-reveal-p-title value={title} onChange={e => setTitle(e.target.value)} placeholder="Gender Reveal" style={rvInp()} />
      <div style={{ display:'flex', alignItems:'center', gap:12, marginTop:12 }}>
        <button data-reveal-p-titlesave onClick={save} style={rvBtn(true)}>Mentés</button>
        {rvMsg(msg, 'data-reveal-p-linksmsg')}
      </div>
      {row('Vendég-link (a vetítő QR-kódja ezt mutatja)', revealGuestUrl(v), 'guestKey', 'data-reveal-p-guesturl')}
      {row('Galéria-link (csak nézhető)', revealAlbumUrl(v), 'albumKey', 'data-reveal-p-albumurl')}
    </div>
  );
}

// ── Szülők: album letöltése + a képfolyam ürítése ──
function RevealAlbumCard() {
  const [msg, flash] = useRevealFlash();
  const [ask, setAsk] = React.useState(false);
  const [clearing, setClearing] = React.useState(false);
  const db = revealDb();
  const download = () => {
    if (!db) return;
    db.collection('revealPhotos').get().then(snap => {
      const n = revealDownloadAlbum(snap.docs.map(d => Object.assign({ id:d.id }, d.data()))); flash(`Album letöltve (${n} fájl)`);
    }).catch(() => flash('Az album nem sikerült'));
  };
  const clearAll = () => {
    if (!db) return;
    setClearing(true); setAsk(false);
    const wipe = coll => db.collection(coll).get().then(snap => {
      const refs = snap.docs.map(d => d.ref);
      const chunks = []; for (let i = 0; i < refs.length; i += 400) chunks.push(refs.slice(i, i + 400));
      return chunks.reduce((p, ch) => p.then(() => { const bt = db.batch(); ch.forEach(r => bt.delete(r)); return bt.commit(); }), Promise.resolve()).then(() => refs.length);
    });
    wipe('revealPhotos').then(n => wipe('revealQuizAns').then(() => n))
      .then(n => { setClearing(false); flash(`${n} kép és üzenet törölve`); }).catch(() => { setClearing(false); flash('Az ürítés nem sikerült'); });
  };
  return (
    <div data-reveal-p-album style={rvCard()}>
      {rvH('📦 Album és ürítés')}
      {rvNote('A buli után: töltsétek le az albumot (minden jóváhagyott kép + a jókívánságok egy szövegfájlban), és csak UTÁNA ürítsétek a képfolyamot.')}
      <div style={{ display:'flex', gap:10, marginTop:12, flexWrap:'wrap', alignItems:'center' }}>
        <button data-reveal-p-zip onClick={download} style={rvBtn(true)}>Album letöltése (ZIP)</button>
        <button data-reveal-p-clear disabled={clearing} onClick={() => setAsk(true)} style={rvBtn(false, { border:`1.5px solid ${T.coral}`, color:T.coral })}>{clearing ? 'Ürítés…' : 'Összes kép törlése'}</button>
        {rvMsg(msg, 'data-reveal-p-albummsg')}
      </div>
      {ask && (
        <ActionModal kicker="Képfolyam ürítése" onClose={() => setAsk(false)} onSecondary={() => setAsk(false)} secondaryLabel="Mégse"
          onPrimary={clearAll} primaryLabel="Mind törlése" primaryColor={T.coral}>
          Minden képet, üzenetet és kvízválaszt törölsz. Letöltöttétek már az albumot? Ez nem vonható vissza.
        </ActionModal>
      )}
    </div>
  );
}

// ── Admin (v10.439): CSAK a belépés és a titkos rész. Minden más a Szülők nézetben. ──
function AdminReveal() {
  const cfg = useRevealCfg();
  const secret = useRevealDoc('revealSecret');
  const rstate = useRevealDoc('revealState');
  const [pw, setPw] = React.useState('');
  const [result, setResult] = React.useState('');
  const [code, setCode] = React.useState('');
  const [videoUrl, setVideoUrl] = React.useState('');
  const [peek, setPeek] = React.useState(false);
  const [init, setInit] = React.useState(false);
  const [initS, setInitS] = React.useState(false);
  const [msg, setMsg] = React.useState('');
  const [msgS, setMsgS] = React.useState('');
  React.useEffect(() => { if (cfg.loaded && !init) { setPw((cfg.v || {}).password || ''); setInit(true); } }, [cfg.loaded]);
  React.useEffect(() => { if (secret.loaded && !initS) { const sc = secret.v || {}; setResult(sc.result || ''); setCode(sc.code || ''); setVideoUrl(sc.videoUrl || ''); setInitS(true); } }, [secret.loaded]);
  const flash = (set, m) => { set(m); setTimeout(() => set(''), 2500); };
  const db = revealDb();
  const save = () => {
    if (!db) return;
    const v = cfg.v || {};
    // a vendég- és album-kulcs az első mentéskor keletkezik, utána változatlan
    db.collection('config').doc('revealConfig').set({ password: pw.trim(), guestKey: v.guestKey || revealKeyGen(), albumKey: v.albumKey || revealKeyGen() }, { merge:true })
      .then(() => flash(setMsg, 'Mentve ✓')).catch(e => flash(setMsg, 'Nem sikerült menteni (' + ((e && e.code) || 'hiba') + ')'));
  };
  const saveSecret = () => {
    if (!db) return;
    db.collection('config').doc('revealSecret').set({ result, code: code.trim(), videoUrl: videoUrl.trim() }, { merge:true })
      .then(() => flash(setMsgS, 'Mentve ✓')).catch(e => flash(setMsgS, 'Nem sikerült menteni (' + ((e && e.code) || 'hiba') + ')'));
  };
  const resetState = () => { if (db) db.collection('config').doc('revealState').set({ phase:'idle', run: revealToken(), at: Date.now() }).then(() => flash(setMsgS, 'Visszaállítva')).catch(() => {}); };
  const label = t => <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', margin:'12px 0 6px' }}>{t}</div>;
  const inpSt = { width:'100%', boxSizing:'border-box', padding:'12px', borderRadius:12, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none' };
  const box = { background:T.surface, borderRadius:16, padding:16, boxShadow:T.shadow };
  const h = t => <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>{t}</div>;
  const note = t => <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:4, lineHeight:1.45 }}>{t}</div>;
  const btn = (primary, extra) => Object.assign({ padding:'11px 16px', borderRadius:12, border: primary ? 'none' : `1.5px solid ${T.border}`, background: primary ? T.mint : 'transparent', color: primary ? '#fff' : T.inkSoft, fontFamily:T.font, fontWeight:900, fontSize:13, cursor:'pointer' }, extra || {});
  if (!cfg.loaded) return <div style={{ textAlign:'center', padding:32, color:T.sub, fontFamily:T.font }}>Betöltés…</div>;
  const st = rstate.v || {};
  return (
    <div data-admin-reveal style={{ padding:16, display:'flex', flexDirection:'column', gap:14 }}>
      <div data-admin-reveal-moved style={Object.assign({}, box, { background:T.mintSoft, boxShadow:'none' })}>
        {h('👶 A többi beállítás a Szülőknél van')}
        {note('A cím, a vendég- és galéria-link, a leleplezés időpontja, a visszaszámláló, a vetítő beállításai, a Babakvíz kérdései, az album és az ürítés a Gender Reveal app „Szülők" szerepében állítható — a szülői kóddal. Itt csak a belépés és a titkos eredmény marad.')}
      </div>
      <div style={box}>
        {h('Belépés')}
        {note('Egy jelszó a vetítőnek és az operátornak is — minden megnyitáskor bekéri.')}
        {label('Jelszó')}
        <input data-admin-reveal-pw value={pw} onChange={e => setPw(e.target.value)} placeholder="pl. babavaro" style={inpSt} />
        <div style={{ display:'flex', alignItems:'center', gap:12, marginTop:14 }}>
          <button data-admin-reveal-save onClick={save} style={btn(true)}>Mentés</button>
          {msg && <span data-admin-reveal-msg style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft }}>{msg}</span>}
        </div>
      </div>
      <div data-admin-reveal-secret style={box}>
        {h('🎉 Leleplezés — titkos')}
        {note('Az eredményt csak itt látod — a szülők sem. A leleplezést a „Szülők" szerep indítja a saját kódjával.')}
        {label('Az eredmény')}
        <div style={{ display:'flex', gap:8, alignItems:'center' }}>
          {peek || !result ? ['boy', 'girl'].map(r => (
            <button key={r} data-admin-reveal-result={r} onClick={() => setResult(r)} style={btn(result === r, { flex:1, background: result === r ? REVEAL_RESULTS[r].c1 : 'transparent', border: result === r ? 'none' : `1.5px solid ${T.border}` })}>{REVEAL_RESULTS[r].emoji} {REVEAL_RESULTS[r].name}</button>
          )) : <div data-admin-reveal-masked style={{ flex:1, fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>●●● beállítva</div>}
          {result && <button data-admin-reveal-peek onClick={() => setPeek(p => !p)} style={btn(false)}>{peek ? 'Elrejt' : '👁 Mutat'}</button>}
        </div>
        {label('Szülői kód (nem a közös jelszó)')}
        <input data-admin-reveal-code value={code} onChange={e => setCode(e.target.value)} placeholder="pl. 2026" style={inpSt} />
        {label('Videó-link (nem kötelező — közvetlen .mp4 link)')}
        <input data-admin-reveal-video value={videoUrl} onChange={e => setVideoUrl(e.target.value)} placeholder="https://…/leleplezes.mp4" style={inpSt} />
        {note('A videót a vetítő laptopjáról is be lehet tölteni (🎬 Videó gomb a vetítőn) — az biztosabb. Ha ott van betöltött videó, az megy a link helyett. Próbánál soha nincs videó.')}
        <div style={{ display:'flex', alignItems:'center', gap:12, marginTop:14, flexWrap:'wrap' }}>
          <button data-admin-reveal-secretsave onClick={saveSecret} style={btn(true)}>Mentés</button>
          <span data-admin-reveal-state style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft }}>Állapot: {st.phase === 'reveal' ? (st.test ? 'próba lefutott' : 'leleplezve 🎉') : st.phase === 'armed' ? 'a szülő engedélyezte ✅' : 'szülői engedélyre vár'}</span>
          {(st.phase === 'reveal' || st.phase === 'armed') && <button data-admin-reveal-reset onClick={resetState} style={btn(false)}>Visszaállítás</button>}
          {msgS && <span data-admin-reveal-msgs style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft }}>{msgS}</span>}
        </div>
      </div>
    </div>
  );
}

'''
s = s[:a] + NEW + s[b:]

# ── 3. a Szülők nézet: leleplezés → időpont → vetítő → Babakvíz → cím/linkek → album ──
rep("""        {secret.loaded && sec.code && ok && <RevealProjectorPanel />}
        {secret.loaded && sec.code && ok && <div data-reveal-parentquiz style={{ width:'100%', maxWidth:440 }}><RevealQuizControl /></div>}""",
"""        {secret.loaded && sec.code && ok && <React.Fragment>
          <RevealScheduleCard />
          <RevealProjectorPanel />
          <div data-reveal-parentquiz style={{ width:'100%', maxWidth:440, display:'flex', flexDirection:'column', gap:10 }}><RevealQuizControl /><RevealQuizEditBox /></div>
          <RevealLinksCard />
          <RevealAlbumCard />
        </React.Fragment>}""")
rep("a leleplezést, a Babakvízt és a vetítő beállításait a szülők kezelik, ezzel a kóddal.",
    "a leleplezést, az időpontot, a Babakvízt, a vetítő és az esemény beállításait a szülők kezelik, ezzel a kóddal.")
rep("sub:'Külön kóddal — a nagy leleplezés, a Babakvíz és a vetítő beállításai. Az eredményt ők sem látják.' }",
    "sub:'Külön kóddal — a nagy leleplezés, a Babakvíz és minden beállítás. Az eredményt ők sem látják.' }")


# ── 4. Polaroid-méret: a középső óra alatti falon a lap a teljes maradék magasságot használja ──
rep("function revealCardGeom(slot, n, vw, vh, item, key) {", "function revealCardGeom(slot, n, vw, vh, item, key, roomy) {")
rep("const maxW = Math.min(W * (n > 1 ? 1.08 : 0.86), vw * 0.92), maxH = vh * (n > 1 ? 0.7 : 0.78);",
    "// ⚠️ `roomy`: a fal a felső óra/jelvény ALATT kezdődik (v10.438) — a régi 70% a kisebb\n  // magasságból kisebb lapot adna (v10.439-ben jelezték), ezért ott a maradék 90%-a jár.\n  const maxW = Math.min(W * (n > 1 ? 1.08 : 0.86), vw * 0.92), maxH = vh * (roomy ? 0.9 : (n > 1 ? 0.7 : 0.78));")
rep("return { iw, ih, pad, bottom, cw, ch, cx, cy: vh * 0.52 + (r2 - 0.5) * vh * (n > 1 ? 0.07 : 0.03), rot };",
    "return { iw, ih, pad, bottom, cw, ch, cx, cy: vh * (roomy ? 0.5 : 0.52) + (r2 - 0.5) * vh * (roomy ? 0.03 : (n > 1 ? 0.07 : 0.03)), rot };")
rep("g={revealCardGeom(i, nSlots, vp.w, Math.max(1, boardH - topEdge), it, s.key)}",
    "g={revealCardGeom(i, nSlots, vp.w, Math.max(1, boardH - topEdge), it, s.key, topEdge > 0)}")

# ── 5. A videó a Szülőknél: darabolt feltöltés a szobába, a vetítő onnan tölti be ──
rep("function revealCtlWrite(patch) {", r"""// ── Leleplező videó (v10.439): a Szülők töltik fel, a vetítő a szobából tölti be ──────────
// Storage SDK nincs, a Firestore-dokumentum max. 1 MB → a fájl `revealVideo/<vid>_NNN`
// darabokban megy (690 000 nyers bájt ≈ 920 KB base64). A `config/revealVideo` meta CSAK a
// teljes feltöltés UTÁN kapja meg a `vid`-et — addig `uploading:true`, a vetítő nem tölt.
const REVEAL_VIDEO_CHUNK = 690000;
const REVEAL_VIDEO_MAX = 60 * 1024 * 1024;
function revealB64(u8) { let s = ''; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000)); return btoa(s); }
function revealUnB64(b) { const s = atob(b), u = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) u[i] = s.charCodeAt(i); return u; }
function revealWipeVideo(db) { return db.collection('revealVideo').get().then(snap => snap.docs.reduce((p, d) => p.then(() => d.ref.delete()), Promise.resolve())); }
function revealUploadVideo(file, onProg) {
  const db = revealDb(); if (!db) return Promise.reject(new Error('nincs adatbázis'));
  if (file.size > REVEAL_VIDEO_MAX) return Promise.reject(new Error('A videó legfeljebb ' + Math.round(REVEAL_VIDEO_MAX / 1048576) + ' MB lehet'));
  const vid = revealToken(), meta = db.collection('config').doc('revealVideo');
  return meta.set({ vid:null, uploading:true, at:Date.now() })
    .then(() => revealWipeVideo(db))
    .then(() => file.arrayBuffer())
    .then(buf => {
      const u8 = new Uint8Array(buf), CH = REVEAL_VIDEO_CHUNK, n = Math.max(1, Math.ceil(u8.length / CH));
      let p = Promise.resolve();
      for (let i = 0; i < n; i++) p = p.then(() => db.collection('revealVideo').doc(vid + '_' + String(i).padStart(3, '0')).set({ vid, i, d: revealB64(u8.subarray(i * CH, (i + 1) * CH)) })).then(() => onProg && onProg(i + 1, n));
      return p.then(() => meta.set({ vid, n, name: file.name || 'videó', type: file.type || 'video/mp4', size: u8.length, at: Date.now(), uploading:false }));
    })
    .catch(e => meta.set({ vid:null, uploading:false, at:Date.now() }).then(() => { throw e; }));
}
function revealDeleteVideo() { const db = revealDb(); if (!db) return Promise.resolve(); return db.collection('config').doc('revealVideo').set({ vid:null, uploading:false, at:Date.now() }).then(() => revealWipeVideo(db)); }
// a vetítő: a meta új `vid`-jére összerakja a darabokat egy helyi Blob-URL-be
function useRevealVideo() {
  const meta = useRevealDoc('revealVideo');
  const m = meta.v || {};
  const [st, setSt] = React.useState({ id:null, url:null, name:'', loading:false });
  React.useEffect(() => {
    if (!meta.loaded || m.uploading) return;
    if (!m.vid) { setSt(o => { if (o.url) try { URL.revokeObjectURL(o.url); } catch(e) {} return { id:null, url:null, name:'', loading:false }; }); return; }
    let dead = false; const db = revealDb(); if (!db) return;
    setSt(o => Object.assign({}, o, { loading:true }));
    db.collection('revealVideo').get().then(snap => {
      if (dead) return;
      const parts = snap.docs.map(d => d.data()).filter(x => x.vid === m.vid).sort((a, b) => a.i - b.i);
      if (parts.length !== m.n) throw new Error('hiányos');
      const url = URL.createObjectURL(new Blob(parts.map(x => revealUnB64(x.d)), { type: m.type || 'video/mp4' }));
      setSt(o => { if (o.url) try { URL.revokeObjectURL(o.url); } catch(e) {} return { id:m.vid, url, name:m.name || 'videó', loading:false }; });
    }).catch(() => { if (!dead) setSt(o => Object.assign({}, o, { loading:false })); });
    return () => { dead = true; };
  }, [meta.loaded, m.vid, m.uploading]);
  return st;
}
// ── Szülők: a videó feltöltése. Előnézet SZÁNDÉKOSAN nincs — a szülők sem nézik meg előre.
function RevealVideoCard() {
  const meta = useRevealDoc('revealVideo');
  const m = meta.v || {};
  const [prog, setProg] = React.useState(null);      // { done, n }
  const [msg, flash] = useRevealFlash();
  const [ask, setAsk] = React.useState(false);
  const ref = React.useRef(null);
  const busy = !!prog || !!m.uploading;
  const pick = f => {
    if (!f) return;
    setProg({ done:0, n:1 });
    revealUploadVideo(f, (done, n) => setProg({ done, n }))
      .then(() => { setProg(null); flash('Feltöltve — a vetítő betölti'); })
      .catch(e => { setProg(null); flash((e && e.message) || 'A feltöltés nem sikerült'); });
  };
  return (
    <div data-reveal-p-video data-has={m.vid ? '1' : '0'} style={rvCard()}>
      {rvH('🎬 Leleplező videó')}
      {rvNote('A visszaszámlálás után ez megy a vetítőn, utána jön a robbanás. Itt nem játsszuk le — csak a vetítő mutatja. Legfeljebb ' + Math.round(REVEAL_VIDEO_MAX / 1048576) + ' MB; ha nincs, az admin videó-linkje megy (ha van).')}
      <div data-reveal-p-videostatus style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink, marginTop:12 }}>
        {prog ? `Feltöltés… ${prog.done} / ${prog.n}` : m.uploading ? 'Feltöltés folyamatban…' : m.vid ? `✅ ${m.name || 'videó'} · ${(m.size / 1048576).toFixed(1)} MB` : 'Nincs feltöltött videó'}
      </div>
      <div style={{ display:'flex', gap:10, marginTop:12, flexWrap:'wrap', alignItems:'center' }}>
        <button data-reveal-p-videopick disabled={busy} onClick={() => ref.current && ref.current.click()} style={rvBtn(true, busy ? { opacity:0.5, cursor:'default' } : null)}>{m.vid ? 'Csere' : '🎬 Videó feltöltése'}</button>
        {m.vid && !busy && <button data-reveal-p-videodel onClick={() => setAsk(true)} style={rvBtn(false, { border:`1.5px solid ${T.coral}`, color:T.coral })}>Törlés</button>}
        {rvMsg(msg, 'data-reveal-p-videomsg')}
      </div>
      <input ref={ref} data-reveal-p-videoinput type="file" accept="video/*" style={{ display:'none' }} onChange={e => { pick(e.target.files && e.target.files[0]); e.target.value = ''; }} />
      {ask && (
        <ActionModal kicker="Videó törlése" onClose={() => setAsk(false)} onSecondary={() => setAsk(false)} secondaryLabel="Mégse"
          onPrimary={() => { setAsk(false); revealDeleteVideo().then(() => flash('Videó törölve')).catch(() => {}); }} primaryLabel="Törlés" primaryColor={T.coral}>
          A leleplezéskor nem lesz videó (csak az admin linkje, ha van).
        </ActionModal>
      )}
    </div>
  );
}
function revealCtlWrite(patch) {""")
rep("""  const [video, setVideo] = React.useState(null);         // { url, name } — a vetítő gépéről
  const videoRef = React.useRef(null);
""", """  const video = useRevealVideo();                          // a Szülők feltöltött videója (v10.439)
""")
rep("""  const pickVideo = f => { if (!f) return; setVideo(old => { if (old) try { URL.revokeObjectURL(old.url); } catch(e) {} return { url: URL.createObjectURL(f), name: f.name || 'videó' }; }); };
""", "")
rep("""        <button data-reveal-videobtn onClick={() => videoRef.current && videoRef.current.click()} title={video ? video.name : ''} style={chip(!!video)}>{video ? '🎬 Videó kész' : '🎬 Videó'}</button>
        <input ref={videoRef} data-reveal-videoinput type="file" accept="video/*" style={{ display:'none' }} onChange={e => { pickVideo(e.target.files && e.target.files[0]); e.target.value = ''; }} />
""", """        {(video.url || video.loading) && <span data-reveal-videoready={video.url ? '1' : '0'} style={{ flexShrink:0, whiteSpace:'nowrap', fontFamily:T.font, fontWeight:800, fontSize:13, color:REVEAL_INK, opacity:0.7 }}>{video.url ? '🎬 videó kész' : '🎬 videó töltődik…'}</span>}
""")
rep("""          <RevealScheduleCard />
          <RevealProjectorPanel />""", """          <RevealScheduleCard />
          <RevealVideoCard />
          <RevealProjectorPanel />""")
rep("{note('A videót a vetítő laptopjáról is be lehet tölteni (🎬 Videó gomb a vetítőn) — az biztosabb. Ha ott van betöltött videó, az megy a link helyett. Próbánál soha nincs videó.')}",
    "{note('A videót a Szülők is feltölthetik (Szülők → 🎬 Leleplező videó) — ha van feltöltött videó, az megy a link helyett. Próbánál soha nincs videó.')}")
assert 'videoRef' not in s and 'pickVideo' not in s and 'data-reveal-videobtn' not in s
assert 'AdminRevealQuiz' not in s and 'data-admin-reveal-title' not in s and 'data-admin-reveal-when' not in s and 'data-admin-reveal-clear' not in s
open(P, 'w', encoding='utf-8').write(s)
print('ok')
