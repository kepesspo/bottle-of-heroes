// ── Gender Reveal: élő képvetítő kivetítőre (v10.430) ───────────────────────────
// Jelszó → szerep (Vetítő / Operátor). Az operátor folyamatosan tölt fel, a vetítő
// a `revealPhotos` gyűjteményt figyeli, és az új kép ÚJRATÖLTÉS NÉLKÜL bekerül:
// a mostani kép után RÖGTÖN az jön („ÚJ KÉP" jelöléssel), utána beáll a körbe.
// Adat:
//   config/revealConfig = { password, title }   — az admin állítja (Admin → Gender Reveal)
//   revealPhotos/<id>   = { src:<dataURL>, at:<ms>, w, h, hidden? }
// ⚠️ Nincs Storage SDK: a kép tömörítve, data URL-ként ül a dokumentumban, és a
// Firestore egy dokumentumot 1 MB-ban maximál — a `revealCompress` ezért addig
// kicsinyít, amíg REVEAL_MAX_CHARS alá nem kerül.
const REVEAL_LOGO = 'assets/dnr_reveal_mark.png';
const REVEAL_PINK = '#F496B4', REVEAL_BLUE = '#96C8F0', REVEAL_NIGHT = '#15121F';
const REVEAL_MAX_SIDE = 1920, REVEAL_MAX_CHARS = 900000;
const REVEAL_MODES = [
  { id:'fade',     label:'Áttűnés' },
  { id:'kenburns', label:'Ken Burns' },
  { id:'polaroid', label:'Polaroid' },
  { id:'collage',  label:'Kollázs' },
];
const REVEAL_SECS = [5, 8, 12, 20];
function revealStore(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch(e) {} return null; }
function revealDb() { return (typeof firebase !== 'undefined') ? firebase.firestore() : null; }
function useRevealCfg() {
  const [s, setS] = React.useState({ v:null, loaded:false });
  React.useEffect(() => {
    const db = revealDb(); if (!db) { setS({ v:null, loaded:true }); return; }
    const un = db.collection('config').doc('revealConfig').onSnapshot(d => setS({ v:(d && d.exists && d.data()) || null, loaded:true }), () => setS(p => ({ v:p.v, loaded:true })));
    return () => { try { un(); } catch(e) {} };
  }, []);
  return s;
}
// A képek, feltöltési sorrendben. `all` → a rejtetteket is (operátor), különben csak a látszók.
function useRevealPhotos(all) {
  const [s, setS] = React.useState({ list:[], loaded:false });
  React.useEffect(() => {
    const db = revealDb(); if (!db) { setS({ list:[], loaded:true }); return; }
    const un = db.collection('revealPhotos').orderBy('at', 'asc').onSnapshot(snap => {
      const list = snap.docs.map(d => Object.assign({ id:d.id }, d.data())).filter(p => p && p.src && (all || !p.hidden));
      list.sort((a, b) => (a.at || 0) - (b.at || 0) || (a.id < b.id ? -1 : 1));
      setS({ list, loaded:true });
    }, () => setS(p => ({ list:p.list, loaded:true })));
    return () => { try { un(); } catch(e) {} };
  }, [all]);
  return s;
}
// Fájl → tömörített data URL (≤ REVEAL_MAX_CHARS). Az EXIF-forgatást a böngésző a
// rajzolásnál alkalmazza (createImageBitmap `from-image`, ill. a modern <img>).
function revealLoadImage(file) {
  if (typeof createImageBitmap === 'function') {
    return createImageBitmap(file, { imageOrientation:'from-image' }).catch(() => revealLoadImgEl(file));
  }
  return revealLoadImgEl(file);
}
function revealLoadImgEl(file) {
  return new Promise((res, rej) => {
    const url = URL.createObjectURL(file), im = new Image();
    im.onload = () => { res(im); setTimeout(() => URL.revokeObjectURL(url), 1000); };
    im.onerror = () => { URL.revokeObjectURL(url); rej(new Error('decode')); };
    im.src = url;
  });
}
function revealCompress(file) {
  return revealLoadImage(file).then(img => {
    const W = img.width || img.naturalWidth, H = img.height || img.naturalHeight;
    if (!W || !H) throw new Error('decode');
    let side = REVEAL_MAX_SIDE, q = 0.82, out = '', w = W, h = H;
    for (let i = 0; i < 8; i++) {
      const k = Math.min(1, side / Math.max(W, H));
      w = Math.max(1, Math.round(W * k)); h = Math.max(1, Math.round(H * k));
      const c = document.createElement('canvas'); c.width = w; c.height = h;
      const ctx = c.getContext('2d'); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, w, h); ctx.drawImage(img, 0, 0, w, h);
      out = canvasToCompressedURL(c, q);
      if (out.length <= REVEAL_MAX_CHARS) break;
      side = Math.round(side * 0.85); q = Math.max(0.5, q - 0.06);
    }
    if (img.close) { try { img.close(); } catch(e) {} }
    if (out.length > REVEAL_MAX_CHARS) throw new Error('size');
    return { src:out, w, h };
  });
}
function revealUpload(file) {
  return revealCompress(file).then(r => {
    const db = revealDb(); if (!db) throw new Error('offline');
    return db.collection('revealPhotos').add({ src:r.src, w:r.w, h:r.h, at:Date.now(), hidden:false });
  });
}
// Egyszerű, determinisztikus „véletlen" a kulcsból — a polaroid dőlése és a Ken Burns
// iránya így minden újrarajzolásnál ugyanaz marad (véletlennel ugrálna).
function revealHash(s) { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0) / 4294967295; }

// A vetítés sorrendje. Az ELSŐ pillanatképben érkező képek a kör részei; ami UTÁNA
// jön, az az `uj` sorba kerül, és a következő váltásnál elsőbbséget kap.
function useRevealSequence(photos, loaded, secs, paused) {
  const st = React.useRef({ inited:false, seen:new Set(), queue:[], lastRegular:null, n:0 });
  const [cur, setCur] = React.useState(null);      // { id, key, isNew }
  const byId = React.useMemo(() => { const m = {}; photos.forEach(p => { m[p.id] = p; }); return m; }, [photos]);
  const advance = React.useCallback(() => {
    const s = st.current;
    s.queue = s.queue.filter(id => byId[id]);
    let id = null, isNew = false;
    if (s.queue.length) { id = s.queue.shift(); isNew = true; }
    else if (photos.length) {
      const i = s.lastRegular ? photos.findIndex(p => p.id === s.lastRegular) : -1;
      id = photos[(i + 1) % photos.length].id;
      s.lastRegular = id;
    }
    s.n++;
    setCur(id ? { id, key: id + '#' + s.n, isNew } : null);
  }, [photos, byId]);
  React.useEffect(() => {
    if (!loaded) return;
    const s = st.current;
    if (!s.inited) { photos.forEach(p => s.seen.add(p.id)); s.inited = true; }
    else photos.forEach(p => { if (!s.seen.has(p.id)) { s.seen.add(p.id); s.queue.push(p.id); } });
    // üres vetítő, vagy a mostani képet közben elrejtették/törölték → azonnal tovább
    if (!cur || !byId[cur.id]) advance();
  }, [photos, loaded]);
  // ⚠️ Az időzítő a REF-en át hív: ha az `advance`-t tenné a függőségei közé, minden
  // beérkező kép (új pillanatkép → új `advance`) újraindítaná a mostani kép óráját.
  const advRef = React.useRef(advance); advRef.current = advance;
  React.useEffect(() => {
    if (!cur || paused) return;
    const t = setTimeout(() => advRef.current(), secs * 1000);
    return () => clearTimeout(t);
  }, [cur && cur.key, secs, paused]);
  const next = React.useCallback(() => advRef.current(), []);
  return { cur, photo: cur ? byId[cur.id] : null, next };
}

// Egy kép a teljes képernyőn: elmosott, kitöltő háttér + a teljes kép középen.
function RevealFullSlide({ photo, slideKey, kenburns, secs, isNew }) {
  const r = revealHash(slideKey || '');
  const dx = (r - 0.5) * 6, dy = (revealHash((slideKey || '') + 'y') - 0.5) * 5;
  return (
    <div data-reveal-slide={photo.id} style={{ position:'absolute', inset:0, overflow:'hidden', animation:'revealFadeIn 1.2s ease both' }}>
      <img src={photo.src} alt="" aria-hidden="true" style={{ position:'absolute', inset:'-6%', width:'112%', height:'112%', objectFit:'cover', filter:'blur(42px) brightness(0.45) saturate(1.2)' }} />
      <img src={photo.src} alt="" style={{ position:'absolute', inset:0, width:'100%', height:'100%', objectFit:'contain',
        animation: kenburns ? `revealKB ${secs + 2}s ease-in-out both` : undefined,
        ['--kb-x']: dx.toFixed(2) + '%', ['--kb-y']: dy.toFixed(2) + '%', transformOrigin: r > 0.5 ? '35% 40%' : '65% 60%' }} />
    </div>
  );
}
function RevealNewBadge({ big }) {
  return (
    <div data-reveal-newbadge style={{ position:'absolute', top: big ? '4vh' : 10, left: big ? '3vw' : 10, zIndex:5, padding: big ? '1.1vh 1.6vw' : '5px 10px', borderRadius:999,
      background:`linear-gradient(90deg, ${REVEAL_PINK}, ${REVEAL_BLUE})`, color:'#1B1830', fontFamily:T.font, fontWeight:900,
      fontSize: big ? 'max(16px, 2.2vh)' : 12, letterSpacing:'0.1em', boxShadow:'0 6px 24px rgba(0,0,0,0.35)', animation:'revealPop 0.6s cubic-bezier(.3,1.6,.5,1) both' }}>✨ ÚJ KÉP</div>
  );
}
function RevealPolaroid({ photo, slideKey, depth, isNew }) {
  const r = revealHash(slideKey), rot = (r - 0.5) * 11, ox = (revealHash(slideKey + 'x') - 0.5) * 14, oy = (revealHash(slideKey + 'z') - 0.5) * 6;
  const ar = (photo.w && photo.h) ? photo.w / photo.h : 1.33;
  // a kép-terület: max 64vh magas és 62vw széles, az arány megtartásával
  const ih = `min(64vh, calc(62vw / ${ar.toFixed(3)}))`;
  return (
    <div data-reveal-polaroid={photo.id} style={{ position:'absolute', left:'50%', top:'50%', zIndex: 10 - depth,
      transform:`translate(calc(-50% + ${depth ? ox : 0}vw), calc(-50% + ${depth ? oy : 0}vh)) rotate(${rot.toFixed(2)}deg)`,
      background:'#FFFDF8', padding:'1.8vh 1.8vh 8vh', borderRadius:6, boxShadow:'0 2.5vh 6vh rgba(0,0,0,0.5)',
      filter: depth ? `brightness(${1 - depth * 0.12})` : undefined, animation: depth ? undefined : 'revealDrop 0.9s cubic-bezier(.2,1.2,.4,1) both' }}>
      <img src={photo.src} alt="" style={{ display:'block', height:ih, width:`calc(${ih} * ${ar.toFixed(3)})`, objectFit:'cover', borderRadius:2 }} />
      {!depth && isNew && <div style={{ position:'absolute', left:0, right:0, bottom:'2.2vh', textAlign:'center', fontFamily:'"Comic Sans MS", "Segoe Print", cursive', fontWeight:700, fontSize:'3.4vh', color:'#C0507A' }}>✨ friss! ✨</div>}
    </div>
  );
}

function RevealProjector({ title, onExit }) {
  const { list: photos, loaded } = useRevealPhotos(false);
  const [mode, setMode] = React.useState(() => { const m = revealStore('boh_reveal_mode'); return REVEAL_MODES.some(x => x.id === m) ? m : 'fade'; });
  const [secs, setSecs] = React.useState(() => { const n = +revealStore('boh_reveal_secs'); return REVEAL_SECS.includes(n) ? n : 8; });
  const [paused, setPaused] = React.useState(false);
  const [ui, setUi] = React.useState(true);
  const [fs, setFs] = React.useState(false);
  const seq = useRevealSequence(photos, loaded, secs, paused);
  const pick = (k, v, set) => { set(v); revealStore(k, String(v)); };

  // a legutóbb mutatott képek (polaroid-halom, áttűnés alsó rétege)
  const [hist, setHist] = React.useState([]);
  React.useEffect(() => { if (seq.cur) setHist(h => [seq.cur].concat(h.filter(x => x.key !== seq.cur.key)).slice(0, 4)); }, [seq.cur && seq.cur.key]);
  // kollázs: három hely; az új kép mindig a nagyba kerül, a többi körbe jár
  const [slots, setSlots] = React.useState([null, null, null]);
  const rotRef = React.useRef(0);
  React.useEffect(() => {
    if (!seq.cur) return;
    setSlots(s => { const n = s.slice(); const i = seq.cur.isNew ? 0 : (rotRef.current++ % 3); n[i] = seq.cur; return n; });
  }, [seq.cur && seq.cur.key]);

  // a vezérlők 3 mp tétlenség után eltűnnek (a kurzorral együtt)
  React.useEffect(() => {
    let t = null;
    const wake = () => { setUi(true); clearTimeout(t); t = setTimeout(() => setUi(false), 3000); };
    wake();
    window.addEventListener('mousemove', wake); window.addEventListener('touchstart', wake); window.addEventListener('keydown', wake);
    return () => { clearTimeout(t); window.removeEventListener('mousemove', wake); window.removeEventListener('touchstart', wake); window.removeEventListener('keydown', wake); };
  }, []);
  // a laptop ne aludjon el vetítés közben
  React.useEffect(() => {
    let lock = null, dead = false;
    const req = () => { try { if (navigator.wakeLock && document.visibilityState === 'visible') navigator.wakeLock.request('screen').then(l => { if (dead) l.release(); else lock = l; }).catch(() => {}); } catch(e) {} };
    req(); document.addEventListener('visibilitychange', req);
    return () => { dead = true; document.removeEventListener('visibilitychange', req); try { lock && lock.release(); } catch(e) {} };
  }, []);
  React.useEffect(() => {
    const on = () => setFs(!!document.fullscreenElement);
    document.addEventListener('fullscreenchange', on);
    return () => document.removeEventListener('fullscreenchange', on);
  }, []);
  const toggleFs = () => { try { if (document.fullscreenElement) document.exitFullscreen(); else document.documentElement.requestFullscreen(); } catch(e) {} };
  React.useEffect(() => {
    const key = e => {
      if (e.key === 'ArrowRight') seq.next();
      else if (e.key === ' ') { e.preventDefault(); setPaused(p => !p); }
      else if (e.key === 'f' || e.key === 'F') toggleFs();
    };
    window.addEventListener('keydown', key);
    return () => window.removeEventListener('keydown', key);
  }, [seq.next]);

  const byId = {}; photos.forEach(p => { byId[p.id] = p; });
  const chip = (on) => ({ padding:'7px 12px', borderRadius:999, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:13,
    background: on ? '#fff' : 'rgba(255,255,255,0.14)', color: on ? '#1B1830' : '#fff' });
  const stage = () => {
    if (!seq.photo) return (
      <div data-reveal-empty style={{ position:'absolute', inset:0, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:'2.4vh', textAlign:'center', padding:'0 6vw' }}>
        <img src={REVEAL_LOGO} alt="" style={{ width:'min(30vh, 40vw)', height:'auto', animation:'revealFloat 4s ease-in-out infinite' }} />
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:'clamp(32px, 7vh, 96px)', lineHeight:1.05, background:`linear-gradient(90deg, ${REVEAL_PINK}, ${REVEAL_BLUE})`, WebkitBackgroundClip:'text', backgroundClip:'text', color:'transparent' }}>{title || 'Gender Reveal'}</div>
        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:'clamp(15px, 2.6vh, 32px)', color:'rgba(255,255,255,0.7)' }}>{loaded ? 'Hamarosan érkeznek a képek…' : 'Betöltés…'}</div>
      </div>
    );
    if (mode === 'polaroid') return (
      <div style={{ position:'absolute', inset:0 }}>
        {hist.slice().reverse().map((h) => { const d = hist.indexOf(h), p = byId[h.id]; return p ? <RevealPolaroid key={h.key} photo={p} slideKey={h.key} depth={d} isNew={h.isNew} /> : null; })}
        {seq.cur.isNew && <RevealNewBadge big />}
      </div>
    );
    if (mode === 'collage') return (
      <div data-reveal-collage style={{ position:'absolute', inset:'2.5vh 2vw', display:'grid', gridTemplateColumns:'2fr 1fr', gridTemplateRows:'1fr 1fr', gap:'2vh' }}>
        {slots.map((s, i) => {
          const p = s && byId[s.id];
          return (
            <div key={i} style={{ position:'relative', borderRadius:18, overflow:'hidden', background:'rgba(255,255,255,0.05)', gridRow: i === 0 ? '1 / span 2' : undefined,
              boxShadow: s && s.key === seq.cur.key ? `0 0 0 3px ${seq.cur.isNew ? REVEAL_PINK : 'rgba(255,255,255,0.35)'}` : 'none', transition:'box-shadow .6s' }}>
              {p && <RevealFullSlide key={s.key} photo={p} slideKey={s.key} secs={secs} />}
              {s && s.isNew && s.key === seq.cur.key && <RevealNewBadge />}
            </div>
          );
        })}
      </div>
    );
    const layers = hist.slice(0, 2).reverse();
    return (
      <div style={{ position:'absolute', inset:0 }}>
        {layers.map(h => byId[h.id] && <RevealFullSlide key={h.key} photo={byId[h.id]} slideKey={h.key} kenburns={mode === 'kenburns'} secs={secs} />)}
        {seq.cur.isNew && <RevealNewBadge big />}
      </div>
    );
  };
  return ReactDOM.createPortal(
    <div data-reveal-projector data-reveal-mode={mode} data-reveal-current={seq.cur ? seq.cur.id : ''} data-reveal-isnew={seq.cur && seq.cur.isNew ? '1' : '0'}
      style={{ position:'fixed', inset:0, zIndex:6000, overflow:'hidden', cursor: ui ? 'default' : 'none',
        background:`radial-gradient(60% 70% at 15% 20%, ${REVEAL_PINK}33, transparent 70%), radial-gradient(60% 70% at 85% 80%, ${REVEAL_BLUE}33, transparent 70%), ${REVEAL_NIGHT}` }}>
      <style>{`
@keyframes revealFadeIn { from { opacity:0 } to { opacity:1 } }
@keyframes revealKB { from { transform:scale(1) translate(0,0) } to { transform:scale(1.12) translate(var(--kb-x), var(--kb-y)) } }
@keyframes revealPop { 0% { transform:scale(.4); opacity:0 } 100% { transform:scale(1); opacity:1 } }
@keyframes revealDrop { 0% { opacity:0; transform:translate(-50%, -50%) translateY(-30vh) rotate(-25deg) scale(1.2) } }
@keyframes revealFloat { 0%,100% { transform:translateY(0) } 50% { transform:translateY(-1.6vh) } }
`}</style>
      {stage()}
      <div data-reveal-controls style={{ position:'absolute', left:0, right:0, top:0, display:'flex', alignItems:'center', gap:8, flexWrap:'wrap', padding:'14px 18px',
        background:'linear-gradient(rgba(0,0,0,0.6), transparent)', opacity: ui ? 1 : 0, pointerEvents: ui ? 'auto' : 'none', transition:'opacity .4s', zIndex:20 }}>
        <button data-reveal-exit onClick={() => { try { if (document.fullscreenElement) document.exitFullscreen(); } catch(e) {} onExit(); }} aria-label="Vissza" style={{ ...chip(false), padding:'7px 10px' }}>‹ Vissza</button>
        <div style={{ display:'flex', gap:6, flexWrap:'wrap' }}>
          {REVEAL_MODES.map(m => <button key={m.id} data-reveal-modebtn={m.id} onClick={() => pick('boh_reveal_mode', m.id, setMode)} style={chip(mode === m.id)}>{m.label}</button>)}
        </div>
        <div style={{ display:'flex', gap:6 }}>
          {REVEAL_SECS.map(n => <button key={n} data-reveal-secs={n} onClick={() => pick('boh_reveal_secs', n, setSecs)} style={chip(secs === n)}>{n} mp</button>)}
        </div>
        <div style={{ flex:1 }} />
        <span data-reveal-count style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:'rgba(255,255,255,0.8)' }}>{photos.length} kép</span>
        <button data-reveal-pause onClick={() => setPaused(p => !p)} style={chip(paused)}>{paused ? '▶ Folytatás' : '⏸ Szünet'}</button>
        <button data-reveal-next onClick={seq.next} style={chip(false)}>Következő ›</button>
        <button data-reveal-fs onClick={toggleFs} style={chip(fs)}>{fs ? 'Kilépés a teljes képernyőből' : '⛶ Teljes képernyő'}</button>
      </div>
    </div>,
    document.body
  );
}

function RevealOperator({ onBack }) {
  const { list: photos, loaded } = useRevealPhotos(true);
  const [busy, setBusy] = React.useState({ done:0, total:0 });
  const [errs, setErrs] = React.useState([]);
  const [confirmDel, setConfirmDel] = React.useState(null);
  const pickRef = React.useRef(null), camRef = React.useRef(null);
  const onFiles = (fl) => {
    const files = Array.from(fl || []).filter(f => !f.type || f.type.indexOf('image/') === 0 || /\.(heic|heif|jpe?g|png|webp|gif)$/i.test(f.name || ''));
    if (!files.length) return;
    setErrs([]);
    setBusy(b => ({ done:b.done, total:b.total + files.length }));
    // egymás után: a tömörítés memóriaigényes, párhuzamosan egy telefon elfogyhat
    files.reduce((p, f) => p.then(() => revealUpload(f).catch(e => {
      const why = e && e.message === 'decode' ? 'nem olvasható (HEIC? küldd JPG-ként)' : e && e.message === 'size' ? 'túl nagy' : 'feltöltési hiba';
      setErrs(x => x.concat((f.name || 'kép') + ' — ' + why));
    }).then(() => setBusy(b => ({ done:b.done + 1, total:b.total })))), Promise.resolve())
      .then(() => setTimeout(() => setBusy(b => b.done >= b.total ? { done:0, total:0 } : b), 1500));
  };
  const setHidden = (p, h) => { const db = revealDb(); if (db) db.collection('revealPhotos').doc(p.id).set({ hidden:h }, { merge:true }).catch(() => {}); };
  const del = (p) => { const db = revealDb(); if (db) db.collection('revealPhotos').doc(p.id).delete().catch(() => {}); setConfirmDel(null); };
  const shown = photos.filter(p => !p.hidden).length;
  const latest = photos.slice().reverse();
  const bigBtn = (primary) => ({ flex:1, minWidth:0, padding:'18px 10px', borderRadius:18, border: primary ? 'none' : `2px solid ${T.mint}`, cursor:'pointer',
    background: primary ? T.mint : T.surface, color: primary ? '#fff' : T.mint, fontFamily:T.font, fontWeight:900, fontSize:16, display:'flex', flexDirection:'column', alignItems:'center', gap:6 });
  return (
    <div data-reveal-operator style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title="Operátor" onBack={onBack} />
      <div style={{ flex:1, overflowY:'auto', padding:'16px 16px calc(24px + env(safe-area-inset-bottom))', WebkitOverflowScrolling:'touch' }}>
        <div style={{ maxWidth:720, margin:'0 auto', display:'flex', flexDirection:'column', gap:14 }}>
          <div style={{ display:'flex', gap:10 }}>
            <button data-reveal-camera onClick={() => camRef.current && camRef.current.click()} style={bigBtn(true)}><span style={{ fontSize:28 }}>📷</span>Fotó készítése</button>
            <button data-reveal-pick onClick={() => pickRef.current && pickRef.current.click()} style={bigBtn(false)}><span style={{ fontSize:28 }}>🖼️</span>Képek kiválasztása</button>
          </div>
          <input ref={camRef} type="file" accept="image/*" capture="environment" style={{ display:'none' }} onChange={e => { onFiles(e.target.files); e.target.value = ''; }} />
          <input ref={pickRef} data-reveal-input type="file" accept="image/*" multiple style={{ display:'none' }} onChange={e => { onFiles(e.target.files); e.target.value = ''; }} />
          {busy.total > 0 && (
            <div data-reveal-progress style={{ background:T.surface, borderRadius:14, padding:'12px 14px', boxShadow:T.shadow }}>
              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink, marginBottom:8 }}>{busy.done >= busy.total ? `Kész — ${busy.total} kép feltöltve` : `Feltöltés… ${busy.done} / ${busy.total}`}</div>
              <div style={{ height:8, borderRadius:4, background:T.bgSoft, overflow:'hidden' }}><div style={{ height:'100%', width:`${Math.round(busy.done / busy.total * 100)}%`, background:T.mint, transition:'width .3s' }} /></div>
            </div>
          )}
          {errs.length > 0 && (
            <div data-reveal-errors style={{ background:T.coralSoft || T.surface, borderRadius:14, padding:'10px 14px', fontFamily:T.font, fontSize:13, fontWeight:700, color:T.coral, lineHeight:1.5 }}>
              {errs.map((e, i) => <div key={i}>⚠️ {e}</div>)}
            </div>
          )}
          <div style={{ display:'flex', alignItems:'baseline', justifyContent:'space-between', marginTop:4 }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>Feltöltött képek</div>
            <div data-reveal-opcount style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkSoft }}>{loaded ? `${shown} a vetítőn${photos.length > shown ? ` · ${photos.length - shown} rejtve` : ''}` : 'Betöltés…'}</div>
          </div>
          {loaded && !photos.length && <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, textAlign:'center', padding:'24px 0' }}>Még nincs feltöltött kép.</div>}
          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(150px, 1fr))', gap:10 }}>
            {latest.map(p => (
              <div key={p.id} data-reveal-thumb={p.id} data-hidden={p.hidden ? '1' : '0'} style={{ position:'relative', borderRadius:14, overflow:'hidden', background:T.surface, boxShadow:T.shadow, aspectRatio:'1 / 1' }}>
                <img src={p.src} alt="" style={{ width:'100%', height:'100%', objectFit:'cover', opacity: p.hidden ? 0.3 : 1 }} />
                {p.hidden && <div style={{ position:'absolute', top:8, left:8, padding:'3px 8px', borderRadius:999, background:'rgba(0,0,0,0.6)', color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:11 }}>REJTVE</div>}
                <div style={{ position:'absolute', left:6, right:6, bottom:6, display:'flex', gap:6 }}>
                  <button data-reveal-hide onClick={() => setHidden(p, !p.hidden)} style={{ flex:1, padding:'7px 0', borderRadius:10, border:'none', cursor:'pointer', background:'rgba(255,255,255,0.92)', color:'#1B1830', fontFamily:T.font, fontWeight:800, fontSize:12 }}>{p.hidden ? 'Mutat' : 'Elrejt'}</button>
                  <button data-reveal-del onClick={() => setConfirmDel(p)} aria-label="Törlés" style={{ width:36, padding:'7px 0', borderRadius:10, border:'none', cursor:'pointer', background:'rgba(220,70,70,0.92)', color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:12 }}>🗑</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      {confirmDel && (
        <ActionModal kicker="Törlöd a képet?" onClose={() => setConfirmDel(null)} onSecondary={() => setConfirmDel(null)} secondaryLabel="Mégse"
          onPrimary={() => del(confirmDel)} primaryLabel="Törlés" primaryColor={T.coral}>
          <img data-reveal-delpreview src={confirmDel.src} alt="" style={{ display:'block', width:'100%', maxHeight:240, objectFit:'contain', borderRadius:12 }} />
        </ActionModal>
      )}
    </div>
  );
}

function RevealScreen({ go, deepLink }) {
  const cfg = useRevealCfg();
  const pw = (cfg.v && cfg.v.password) || '';
  const title = (cfg.v && cfg.v.title) || 'Gender Reveal';
  const [saved, setSaved] = React.useState(() => revealStore('boh_reveal_pw') || '');
  const [inp, setInp] = React.useState('');
  const [bad, setBad] = React.useState(false);
  const [role, setRole] = React.useState(null);   // null | 'projector' | 'operator'
  const ok = !!pw && saved === pw;
  const submit = () => {
    if (inp.trim() && inp.trim() === pw) { revealStore('boh_reveal_pw', inp.trim()); setSaved(inp.trim()); setBad(false); setInp(''); }
    else setBad(true);
  };
  const back = deepLink ? null : () => go('home');
  if (ok && role === 'projector') return <RevealProjector title={title} onExit={() => setRole(null)} />;
  if (ok && role === 'operator') return <RevealOperator onBack={() => setRole(null)} />;
  const card = { width:'100%', maxWidth:440, background:T.surface, borderRadius:22, padding:'22px 20px', boxShadow:T.shadow, boxSizing:'border-box' };
  return (
    <div data-reveal-screen style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title={title} onBack={back} />
      <div style={{ flex:1, overflowY:'auto', display:'flex', flexDirection:'column', alignItems:'center', gap:16, padding:'22px 16px calc(24px + env(safe-area-inset-bottom))' }}>
        <img src={REVEAL_LOGO} alt="" style={{ width:120, height:120 }} />
        {!cfg.loaded ? (
          <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft }}>Betöltés…</div>
        ) : !pw ? (
          <div data-reveal-nopw style={{ ...card, textAlign:'center', fontFamily:T.font, fontSize:14, fontWeight:700, color:T.inkSoft, lineHeight:1.5 }}>Még nincs jelszó beállítva.<br/>Admin → Gender Reveal</div>
        ) : !ok ? (
          <div data-reveal-gate style={{ ...card, display:'flex', flexDirection:'column', gap:12 }}>
            <div style={{ display:'flex', alignItems:'center', gap:8, justifyContent:'center' }}><BohIcon name="lock" size={22} /><span style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink }}>Jelszó</span></div>
            <input data-reveal-pw type="password" value={inp} autoFocus onChange={e => { setInp(e.target.value); setBad(false); }} onKeyDown={e => { if (e.key === 'Enter') submit(); }} placeholder="Írd be a jelszót"
              style={{ width:'100%', boxSizing:'border-box', padding:'14px', borderRadius:14, border:`1.5px solid ${bad ? T.coral : T.border}`, background:T.bg, fontFamily:T.font, fontSize:17, fontWeight:700, color:T.ink, textAlign:'center', outline:'none' }} />
            {bad && <div data-reveal-bad style={{ fontFamily:T.font, fontSize:13, fontWeight:800, color:T.coral, textAlign:'center' }}>Hibás jelszó</div>}
            <PrimaryButton onClick={submit} disabled={!inp.trim()}>Belépés</PrimaryButton>
          </div>
        ) : (
          <div data-reveal-roles style={{ width:'100%', maxWidth:640, display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(240px, 1fr))', gap:14 }}>
            {[
              { id:'projector', emoji:'📽️', name:'Vetítő', sub:'Laptop a kivetítőn — a képek folyamatosan mennek, az újak azonnal bekerülnek.' },
              { id:'operator', emoji:'📷', name:'Operátor', sub:'Képek feltöltése telefonról vagy gépről, elrejtés és törlés.' },
            ].map(r => (
              <button key={r.id} data-reveal-role={r.id} onClick={() => setRole(r.id)} style={{ ...card, maxWidth:'none', border:'none', cursor:'pointer', textAlign:'left', display:'flex', flexDirection:'column', gap:6 }}>
                <span style={{ fontSize:34 }}>{r.emoji}</span>
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:19, color:T.ink }}>{r.name}</span>
                <span style={{ fontFamily:T.font, fontWeight:600, fontSize:13, color:T.inkSoft, lineHeight:1.45 }}>{r.sub}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Admin → Gender Reveal: jelszó, cím, és a képfolyam ürítése a következő bulira.
function AdminReveal() {
  const cfg = useRevealCfg();
  const [pw, setPw] = React.useState('');
  const [title, setTitle] = React.useState('');
  const [init, setInit] = React.useState(false);
  const [msg, setMsg] = React.useState('');
  const [ask, setAsk] = React.useState(false);
  const [clearing, setClearing] = React.useState(false);
  React.useEffect(() => { if (cfg.loaded && !init) { setPw((cfg.v && cfg.v.password) || ''); setTitle((cfg.v && cfg.v.title) || ''); setInit(true); } }, [cfg.loaded]);
  const flash = m => { setMsg(m); setTimeout(() => setMsg(''), 2500); };
  const save = () => {
    const db = revealDb(); if (!db) return;
    db.collection('config').doc('revealConfig').set({ password: pw.trim(), title: title.trim() }, { merge:true })
      .then(() => flash('Mentve ✓')).catch(e => flash('Nem sikerült menteni (' + ((e && e.code) || 'hiba') + ')'));
  };
  const clearAll = () => {
    const db = revealDb(); if (!db) return;
    setClearing(true); setAsk(false);
    db.collection('revealPhotos').get().then(snap => {
      const refs = snap.docs.map(d => d.ref);
      const chunks = []; for (let i = 0; i < refs.length; i += 400) chunks.push(refs.slice(i, i + 400));
      return chunks.reduce((p, ch) => p.then(() => { const b = db.batch(); ch.forEach(r => b.delete(r)); return b.commit(); }), Promise.resolve()).then(() => refs.length);
    }).then(n => { setClearing(false); flash(`${n} kép törölve`); }).catch(() => { setClearing(false); flash('Az ürítés nem sikerült'); });
  };
  const label = s => <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', margin:'12px 0 6px' }}>{s}</div>;
  const inpSt = { width:'100%', boxSizing:'border-box', padding:'12px', borderRadius:12, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none' };
  if (!cfg.loaded) return <div style={{ textAlign:'center', padding:32, color:T.sub, fontFamily:T.font }}>Betöltés…</div>;
  return (
    <div data-admin-reveal style={{ padding:16, display:'flex', flexDirection:'column', gap:14 }}>
      <div style={{ background:T.surface, borderRadius:16, padding:16, boxShadow:T.shadow }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>Belépés és cím</div>
        <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:4, lineHeight:1.45 }}>Egy jelszó a vetítőnek és az operátornak is. Ha megváltoztatod, minden eszköz újra kéri.</div>
        {label('Jelszó')}
        <input data-admin-reveal-pw value={pw} onChange={e => setPw(e.target.value)} placeholder="pl. babavaro" style={inpSt} />
        {label('Cím (a vetítő üres képernyőjén)')}
        <input data-admin-reveal-title value={title} onChange={e => setTitle(e.target.value)} placeholder="Gender Reveal" style={inpSt} />
        <div style={{ display:'flex', alignItems:'center', gap:12, marginTop:14 }}>
          <button data-admin-reveal-save onClick={save} style={{ padding:'11px 18px', borderRadius:12, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14, cursor:'pointer' }}>Mentés</button>
          {msg && <span data-admin-reveal-msg style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft }}>{msg}</span>}
        </div>
      </div>
      <div style={{ background:T.surface, borderRadius:16, padding:16, boxShadow:T.shadow }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>Képfolyam ürítése</div>
        <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:4, lineHeight:1.45 }}>Minden feltöltött kép végleg törlődik — a következő bulira tiszta lappal indul a vetítő.</div>
        <button data-admin-reveal-clear disabled={clearing} onClick={() => setAsk(true)} style={{ marginTop:12, padding:'11px 18px', borderRadius:12, border:`1.5px solid ${T.coral}`, background:'transparent', color:T.coral, fontFamily:T.font, fontWeight:900, fontSize:14, cursor:'pointer' }}>{clearing ? 'Ürítés…' : 'Összes kép törlése'}</button>
      </div>
      {ask && (
        <ActionModal kicker="Képfolyam ürítése" onClose={() => setAsk(false)} onSecondary={() => setAsk(false)} secondaryLabel="Mégse"
          onPrimary={clearAll} primaryLabel="Mind törlése" primaryColor={T.coral}>
          Minden képet törölsz? A vetítőről és az operátor listájáról is eltűnik. Ez nem vonható vissza.
        </ActionModal>
      )}
    </div>
  );
}
