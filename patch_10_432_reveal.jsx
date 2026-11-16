// ── Gender Reveal: élő képvetítő kivetítőre (v10.430, bővítve v10.432) ─────────────
// Jelszó → szerep (Vetítő / Operátor / Leleplező). Az operátor folyamatosan tölt fel, a
// vetítő a `revealPhotos` gyűjteményt figyeli, és az új tétel ÚJRATÖLTÉS NÉLKÜL bekerül:
// a mostani után RÖGTÖN az jön („ÚJ" jelöléssel), utána beáll a körbe.
// A vendégek a vetítő QR-kódjával (jelszó nélkül, a `guestKey`-jel) képet és
// jókívánságot küldhetnek — ezek az operátor jóváhagyásáig `pending`-ek.
// Adat:
//   config/revealConfig    = { password, title, guestKey, albumKey }
//   config/revealSecret    = { result:'boy'|'girl', code, videoUrl }   — CSAK az admin írja
//   config/revealState     = { phase:'idle'|'reveal', run, test, result, videoUrl, at }
//   config/revealQuiz      = { questions:[{ q, opts:[…], ok }] }
//   config/revealQuizState = { phase:'idle'|'q'|'ans'|'board', idx, run, qs }
//   revealPhotos/<id>      = { src, w, h, at, hidden, pending, by }  — kép
//                          = { kind:'wish', text, by, at, hidden, pending } — jókívánság
//   revealQuizAns/<gid>    = { name, a:{ '<run>_<idx>': opció } }
// ⚠️ Nincs Storage SDK: a kép tömörítve, data URL-ként ül a dokumentumban, és a
// Firestore egy dokumentumot 1 MB-ban maximál — a `revealCompress` ezért addig
// kicsinyít, amíg REVEAL_MAX_CHARS alá nem kerül.
const REVEAL_LOGO = 'assets/dnr_reveal_mark.png';
const REVEAL_PINK = '#F496B4', REVEAL_BLUE = '#96C8F0', REVEAL_NIGHT = '#15121F';
const REVEAL_MAX_SIDE = 1920, REVEAL_MAX_CHARS = 900000, REVEAL_WISH_MAX = 140;
const REVEAL_MODES = [
  { id:'fade',     label:'Áttűnés' },
  { id:'kenburns', label:'Ken Burns' },
  { id:'polaroid', label:'Polaroid' },
  { id:'collage',  label:'Kollázs' },
];
const REVEAL_SECS = [5, 8, 12, 20];
// A leleplezés két kimenete. A szín a kiderülés UTÁN a vetítő hátterét is adja.
const REVEAL_RESULTS = {
  boy:  { word:'FIÚ!',  name:'Fiú',  emoji:'💙', c1:'#4FA3E8', c2:'#96C8F0', ink:'#0E2A4A' },
  girl: { word:'LÁNY!', name:'Lány', emoji:'💗', c1:'#F06292', c2:'#F8B4CC', ink:'#4A0E28' },
  test: { word:'PRÓBA', name:'Próba', emoji:'✅', c1:'#8E7CC3', c2:'#C7B8EC', ink:'#1E1438' },
};
const REVEAL_COUNT_FROM = 10;
const REVEAL_QUIZ_DEFAULT = [
  { q:'Hány csontja van nagyjából egy újszülöttnek?', opts:['206', 'kb. 300', '150', '100'], ok:1 },
  { q:'Hány órát alszik naponta egy újszülött?', opts:['8–10', '14–17', '20–22', '6–8'], ok:1 },
  { q:'Mikor mosolyog rá először tudatosan a babára figyelőkre?', opts:['2 hetesen', '6–8 hetesen', '4 hónaposan', '6 hónaposan'], ok:1 },
  { q:'Hány hónaposan jön ki általában az első foga?', opts:['2', '6', '10', '12'], ok:1 },
  { q:'Hány hétig tart átlagosan egy várandósság?', opts:['36', '40', '44', '32'], ok:1 },
  { q:'Mekkora egy újszülött gyomra az első napon?', opts:['Cseresznye', 'Dió', 'Alma', 'Narancs'], ok:0 },
  { q:'Hányat ver percenként egy újszülött szíve?', opts:['60–80', '120–160', '200–220', '40–60'], ok:1 },
  { q:'Mit NEM tud még egy újszülött?', opts:['Markolni', 'Szopni', 'Könnyezni sírás közben', 'Hallani'], ok:2 },
  { q:'Nagyjából hány pelenka fogy az első évben?', opts:['500', 'kb. 2500', '10 000', '1000'], ok:1 },
  { q:'Hány hónaposan ül fel általában önállóan?', opts:['2', '6', '10', '14'], ok:1 },
];
const REVEAL_QUIZ_COLORS = ['#E8667A', '#4FA3E8', '#E8B13C', '#5DBB8A'];
function revealStore(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch(e) {} return null; }
function revealDb() { return (typeof firebase !== 'undefined') ? firebase.firestore() : null; }
function revealToken() { return Date.now().toString(36) + Math.random().toString(36).slice(2, 8); }
function revealKeyGen() { let s = ''; while (s.length < 12) s += Math.random().toString(36).slice(2); return s.slice(0, 12); }
function revealBaseUrl() { try { return location.origin + location.pathname; } catch(e) { return ''; } }
function revealGuestUrl(cfg) { return cfg && cfg.guestKey ? revealBaseUrl() + '?screen=reveal&g=' + cfg.guestKey : ''; }
function revealAlbumUrl(cfg) { return cfg && cfg.albumKey ? revealBaseUrl() + '?screen=reveal&album=' + cfg.albumKey : ''; }
function revealParam(k) { try { return new URLSearchParams(location.search).get(k) || ''; } catch(e) { return ''; } }
function revealSpeed() { return (typeof window !== 'undefined' && window.__revealSpeed) || 1; }
function useRevealDoc(name) {
  const [s, setS] = React.useState({ v:null, loaded:false });
  React.useEffect(() => {
    const db = revealDb(); if (!db) { setS({ v:null, loaded:true }); return; }
    const un = db.collection('config').doc(name).onSnapshot(d => setS({ v:(d && d.exists && d.data()) || null, loaded:true }), () => setS(p => ({ v:p.v, loaded:true })));
    return () => { try { un(); } catch(e) {} };
  }, [name]);
  return s;
}
function useRevealCfg() { return useRevealDoc('revealConfig'); }
// A tételek (kép + jókívánság), feltöltési sorrendben. `all` → a rejtett és a
// jóváhagyásra váró is (operátor), különben csak ami a vetítőre mehet.
function useRevealPhotos(all) {
  const [s, setS] = React.useState({ list:[], loaded:false });
  React.useEffect(() => {
    const db = revealDb(); if (!db) { setS({ list:[], loaded:true }); return; }
    const un = db.collection('revealPhotos').orderBy('at', 'asc').onSnapshot(snap => {
      const list = snap.docs.map(d => Object.assign({ id:d.id }, d.data()))
        .filter(p => p && (p.src || (p.kind === 'wish' && p.text)) && (all || (!p.hidden && !p.pending)));
      list.sort((a, b) => (a.at || 0) - (b.at || 0) || (a.id < b.id ? -1 : 1));
      setS({ list, loaded:true });
    }, () => setS(p => ({ list:p.list, loaded:true })));
    return () => { try { un(); } catch(e) {} };
  }, [all]);
  return s;
}
function useRevealAnswers(on) {
  const [list, setList] = React.useState([]);
  React.useEffect(() => {
    const db = revealDb(); if (!db || !on) return;
    const un = db.collection('revealQuizAns').onSnapshot(snap => setList(snap.docs.map(d => Object.assign({ id:d.id }, d.data()))), () => {});
    return () => { try { un(); } catch(e) {} };
  }, [on]);
  return list;
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
// `extra`: a vendég feltöltése { pending:true, by:<név> } — az operátoré mehet egyből.
function revealUpload(file, extra) {
  return revealCompress(file).then(r => {
    const db = revealDb(); if (!db) throw new Error('offline');
    return db.collection('revealPhotos').add(Object.assign({ src:r.src, w:r.w, h:r.h, at:Date.now(), hidden:false, pending:false }, extra || {}));
  });
}
function revealSendWish(text, by) {
  const db = revealDb(); if (!db) return Promise.reject(new Error('offline'));
  return db.collection('revealPhotos').add({ kind:'wish', text: String(text).trim().slice(0, REVEAL_WISH_MAX), by: String(by || '').trim().slice(0, 40), at:Date.now(), hidden:false, pending:true });
}
// Egymás után tölt (párhuzamosan egy telefon memóriája elfogyhat). Hibánként visszahív.
function revealUploadMany(files, extra, onStep, onErr) {
  return files.reduce((p, f) => p.then(() => revealUpload(f, extra).catch(e => {
    const why = e && e.message === 'decode' ? 'nem olvasható (HEIC? küldd JPG-ként)' : e && e.message === 'size' ? 'túl nagy' : 'feltöltési hiba';
    onErr && onErr((f.name || 'kép') + ' — ' + why);
  }).then(() => onStep && onStep())), Promise.resolve());
}
function revealImageFiles(fl) { return Array.from(fl || []).filter(f => !f.type || f.type.indexOf('image/') === 0 || /\.(heic|heif|jpe?g|png|webp|gif)$/i.test(f.name || '')); }
// Egyszerű, determinisztikus „véletlen" a kulcsból — a polaroid dőlése és a Ken Burns
// iránya így minden újrarajzolásnál ugyanaz marad (véletlennel ugrálna).
function revealHash(s) { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0) / 4294967295; }

// ── Album: ZIP (tömörítés nélkül — a JPEG/WebP már tömörített) ───────────────────
function revealCrc32(u8) {
  let tbl = revealCrc32.t;
  if (!tbl) { tbl = revealCrc32.t = new Uint32Array(256); for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; tbl[n] = c >>> 0; } }
  let crc = 0xFFFFFFFF; for (let i = 0; i < u8.length; i++) crc = tbl[(crc ^ u8[i]) & 0xFF] ^ (crc >>> 8);
  return (crc ^ 0xFFFFFFFF) >>> 0;
}
function revealZip(files) {
  const enc = new TextEncoder(), parts = [], central = []; let off = 0;
  files.forEach(f => {
    const nm = enc.encode(f.name), crc = revealCrc32(f.data), sz = f.data.length;
    const lh = new DataView(new ArrayBuffer(30));
    lh.setUint32(0, 0x04034b50, true); lh.setUint16(4, 20, true); lh.setUint16(6, 0x0800, true);
    lh.setUint16(12, 0x21, true); lh.setUint32(14, crc, true); lh.setUint32(18, sz, true); lh.setUint32(22, sz, true); lh.setUint16(26, nm.length, true);
    parts.push(new Uint8Array(lh.buffer), nm, f.data);
    const ch = new DataView(new ArrayBuffer(46));
    ch.setUint32(0, 0x02014b50, true); ch.setUint16(4, 20, true); ch.setUint16(6, 20, true); ch.setUint16(8, 0x0800, true);
    ch.setUint16(14, 0x21, true); ch.setUint32(16, crc, true); ch.setUint32(20, sz, true); ch.setUint32(24, sz, true); ch.setUint16(28, nm.length, true); ch.setUint32(42, off, true);
    central.push(new Uint8Array(ch.buffer), nm);
    off += 30 + nm.length + sz;
  });
  const cd = central.reduce((a, b) => a + b.length, 0);
  const end = new DataView(new ArrayBuffer(22));
  end.setUint32(0, 0x06054b50, true); end.setUint16(8, files.length, true); end.setUint16(10, files.length, true); end.setUint32(12, cd, true); end.setUint32(16, off, true);
  return new Blob(parts.concat(central, [new Uint8Array(end.buffer)]), { type:'application/zip' });
}
function revealDataBytes(src) {
  const i = src.indexOf(','), bin = atob(src.slice(i + 1)), u = new Uint8Array(bin.length);
  for (let k = 0; k < bin.length; k++) u[k] = bin.charCodeAt(k);
  return u;
}
// A jóváhagyott, nem rejtett tételek albuma: képek + egy jokivansagok.txt.
function revealBuildAlbum(items) {
  const safe = s => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 24);
  const ok = items.filter(p => !p.hidden && !p.pending);
  const files = []; let n = 0;
  ok.filter(p => p.src).forEach(p => {
    n++; const ext = /^data:image\/webp/.test(p.src) ? 'webp' : /^data:image\/png/.test(p.src) ? 'png' : 'jpg';
    files.push({ name: 'kep_' + String(n).padStart(3, '0') + (p.by ? '_' + safe(p.by) : '') + '.' + ext, data: revealDataBytes(p.src) });
  });
  const wishes = ok.filter(p => p.kind === 'wish');
  if (wishes.length) files.push({ name:'jokivansagok.txt', data: new TextEncoder().encode(wishes.map(w => (w.by ? w.by + ': ' : '') + w.text).join('\n\n') + '\n') });
  return { blob: revealZip(files), count: files.length };
}
function revealDownload(blob, name) {
  const u = URL.createObjectURL(blob), a = document.createElement('a');
  a.href = u; a.download = name; document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(u), 4000);
}
function revealDownloadAlbum(items) {
  const r = revealBuildAlbum(items);
  revealDownload(r.blob, 'gender_reveal_album.zip');
  return r.count;
}

// ── Hang: dobpergés + cintányér (WebAudio, fájl nélkül) ──────────────────────────
// Az AudioContext-et a vetítő megnyitásakor (felhasználói koppintás) hozzuk létre,
// különben a böngésző némítva tartaná a leleplezéskor.
function revealAudio() {
  if (revealAudio.ctx === undefined) { try { const AC = window.AudioContext || window.webkitAudioContext; revealAudio.ctx = AC ? new AC() : null; } catch(e) { revealAudio.ctx = null; } }
  const c = revealAudio.ctx; if (c && c.state === 'suspended') { try { c.resume(); } catch(e) {} }
  return c;
}
function revealNoise(ctx, t, dur, gain, hp) {
  const len = Math.max(1, Math.floor(ctx.sampleRate * dur)), b = ctx.createBuffer(1, len, ctx.sampleRate), d = b.getChannelData(0);
  for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 2);
  const s = ctx.createBufferSource(); s.buffer = b; const g = ctx.createGain(); g.gain.value = gain;
  if (hp) { const f = ctx.createBiquadFilter(); f.type = 'highpass'; f.frequency.value = hp; s.connect(f); f.connect(g); } else s.connect(g);
  g.connect(ctx.destination); s.start(t);
}
function revealDrumroll(sec) {
  const c = revealAudio(); if (!c) return;
  const t0 = c.currentTime; let t = 0;
  while (t < sec) { const p = t / sec; revealNoise(c, t0 + t, 0.07, 0.12 + 0.4 * p, 600); t += 0.12 - 0.075 * p; }
}
function revealCrash() {
  const c = revealAudio(); if (!c) return;
  const t = c.currentTime; revealNoise(c, t, 2.4, 0.55, 2500);
  [523.25, 659.25, 783.99, 1046.5].forEach((f, i) => {
    const o = c.createOscillator(), g = c.createGain(), s = t + i * 0.09;
    o.type = 'triangle'; o.frequency.value = f;
    g.gain.setValueAtTime(0.0001, s); g.gain.exponentialRampToValueAtTime(0.2, s + 0.03); g.gain.exponentialRampToValueAtTime(0.0001, s + 1.8);
    o.connect(g); g.connect(c.destination); o.start(s); o.stop(s + 1.9);
  });
}

// A vetítés sorrendje. Az ELSŐ pillanatképben érkező tételek a kör részei; ami UTÁNA
// jön (vagy amit az operátor ekkor hagy jóvá), az az `uj` sorba kerül, és a következő
// váltásnál elsőbbséget kap.
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
    // üres vetítő, vagy a mostani tételt közben elrejtették/törölték → azonnal tovább
    if (!cur || !byId[cur.id]) advance();
  }, [photos, loaded]);
  // ⚠️ Az időzítő a REF-en át hív: ha az `advance`-t tenné a függőségei közé, minden
  // beérkező kép (új pillanatkép → új `advance`) újraindítaná a mostani kép óráját.
  const advRef = React.useRef(advance); advRef.current = advance;
  React.useEffect(() => {
    if (!cur || paused) return;
    // teszt-fogódzó: window.__revealSpeed (pl. 0.05) az egész ütemet skálázza
    const t = setTimeout(() => advRef.current(), secs * 1000 * revealSpeed());
    return () => clearTimeout(t);
  }, [cur && cur.key, secs, paused]);
  const next = React.useCallback(() => advRef.current(), []);
  return { cur, photo: cur ? byId[cur.id] : null, next };
}

// Egy kép a teljes képernyőn: elmosott, kitöltő háttér + a teljes kép középen.
function RevealFullSlide({ photo, slideKey, kenburns, secs, cover }) {
  const r = revealHash(slideKey || '');
  const dx = (r - 0.5) * 6, dy = (revealHash((slideKey || '') + 'y') - 0.5) * 5;
  return (
    <div data-reveal-slide={photo.id} style={{ position:'absolute', inset:0, overflow:'hidden', animation:'revealFadeIn 1.2s ease both' }}>
      <img src={photo.src} alt="" aria-hidden="true" style={{ position:'absolute', inset:'-6%', width:'112%', height:'112%', objectFit:'cover', filter:'blur(42px) brightness(0.45) saturate(1.2)' }} />
      <img src={photo.src} alt="" style={{ position:'absolute', inset:0, width:'100%', height:'100%', objectFit: cover ? 'cover' : 'contain',
        animation: kenburns ? `revealKB ${secs + 2}s ease-in-out both` : undefined,
        ['--kb-x']: dx.toFixed(2) + '%', ['--kb-y']: dy.toFixed(2) + '%', transformOrigin: r > 0.5 ? '35% 40%' : '65% 60%' }} />
    </div>
  );
}
// Jókívánság-kártya. `compact` — kollázs-csempében (a vetítő mértékegysége ott nem vh).
function RevealWishCard({ wish, slideKey, compact }) {
  const r = revealHash(slideKey || wish.id || '');
  const bg = r < 0.33 ? '#FFF1F5' : r < 0.66 ? '#EEF6FF' : '#FFF8E8';
  const rot = compact ? 0 : (r - 0.5) * 4;
  const len = (wish.text || '').length;
  const fs = compact ? (len > 80 ? 15 : 19) : (len > 90 ? 'clamp(22px, 4.2vh, 54px)' : 'clamp(26px, 5.6vh, 72px)');
  return (
    <div data-reveal-wish={wish.id} style={{ position:'absolute', inset:0, display:'flex', alignItems:'center', justifyContent:'center', padding: compact ? 12 : '6vh 8vw', animation:'revealFadeIn 1s ease both' }}>
      <div style={{ position:'relative', maxWidth: compact ? '100%' : 'min(1100px, 84vw)', background:bg, color:'#2A1E3A', borderRadius: compact ? 16 : 28,
        padding: compact ? '16px 16px 14px' : '6vh 6vw 5vh', boxShadow:'0 3vh 8vh rgba(0,0,0,0.45)', transform:`rotate(${rot.toFixed(2)}deg)`, textAlign:'center', boxSizing:'border-box' }}>
        <div aria-hidden="true" style={{ fontSize: compact ? 24 : 'clamp(30px, 7vh, 90px)', lineHeight:1, marginBottom: compact ? 6 : '1.5vh' }}>💌</div>
        <div style={{ fontFamily:T.font, fontWeight:800, fontSize:fs, lineHeight:1.3, overflowWrap:'anywhere' }}>„{wish.text}”</div>
        {wish.by && <div style={{ marginTop: compact ? 8 : '3vh', fontFamily:'"Comic Sans MS", "Segoe Print", cursive', fontWeight:700, fontSize: compact ? 14 : 'clamp(18px, 3.4vh, 42px)', color:'#B04A78' }}>— {wish.by}</div>}
      </div>
    </div>
  );
}
function RevealNewBadge({ big, wish }) {
  return (
    // alul ül: felül a (3 mp után eltűnő) vezérlősáv takarná
    <div data-reveal-newbadge style={{ position:'absolute', bottom: big ? '4vh' : 10, left: big ? '3vw' : 10, zIndex:5, padding: big ? '1.1vh 1.6vw' : '5px 10px', borderRadius:999,
      background:`linear-gradient(90deg, ${REVEAL_PINK}, ${REVEAL_BLUE})`, color:'#1B1830', fontFamily:T.font, fontWeight:900,
      fontSize: big ? 'max(16px, 2.2vh)' : 12, letterSpacing:'0.1em', boxShadow:'0 6px 24px rgba(0,0,0,0.35)', animation:'revealPop 0.6s cubic-bezier(.3,1.6,.5,1) both' }}>{wish ? '💌 ÚJ ÜZENET' : '✨ ÚJ KÉP'}</div>
  );
}
function RevealPolaroid({ photo, slideKey, depth, isNew }) {
  const r = revealHash(slideKey), rot = (r - 0.5) * 11, ox = (revealHash(slideKey + 'x') - 0.5) * 14, oy = (revealHash(slideKey + 'z') - 0.5) * 6;
  const ar = (photo.w && photo.h) ? photo.w / photo.h : 1.33;
  // a kép-terület: max 64vh magas és 62vw széles, az arány megtartásával
  const ih = `min(64vh, calc(62vw / ${ar.toFixed(3)}))`;
  const cap = !depth ? (isNew ? '✨ friss! ✨' : photo.by || '') : '';
  return (
    <div data-reveal-polaroid={photo.id} style={{ position:'absolute', left:'50%', top:'50%', zIndex: 10 - depth,
      transform:`translate(calc(-50% + ${depth ? ox : 0}vw), calc(-50% + ${depth ? oy : 0}vh)) rotate(${rot.toFixed(2)}deg)`,
      background:'#FFFDF8', padding:'1.8vh 1.8vh 8vh', borderRadius:6, boxShadow:'0 2.5vh 6vh rgba(0,0,0,0.5)',
      filter: depth ? `brightness(${1 - depth * 0.12})` : undefined, animation: depth ? undefined : 'revealDrop 0.9s cubic-bezier(.2,1.2,.4,1) both' }}>
      <img src={photo.src} alt="" style={{ display:'block', height:ih, width:`calc(${ih} * ${ar.toFixed(3)})`, objectFit:'cover', borderRadius:2 }} />
      {cap && <div style={{ position:'absolute', left:0, right:0, bottom:'2.2vh', textAlign:'center', fontFamily:'"Comic Sans MS", "Segoe Print", cursive', fontWeight:700, fontSize:'3.4vh', color:'#C0507A' }}>{cap}</div>}
    </div>
  );
}
function RevealQrCard({ url, big }) {
  const src = React.useMemo(() => { try { return url && window.makeQRDataURL ? window.makeQRDataURL(url, 300) : ''; } catch(e) { return ''; } }, [url]);
  if (!src) return null;
  return (
    <div data-reveal-qr style={{ flex:'0 0 auto', maxWidth: big ? '42vw' : 'none', display:'flex', alignItems:'center', gap: big ? '2vw' : 12, background:'rgba(255,255,255,0.94)', borderRadius:16, padding: big ? '2vh 2vw' : 10, boxShadow:'0 8px 30px rgba(0,0,0,0.35)' }}>
      <img src={src} alt="QR" style={{ width: big ? 'min(26vh, 22vw)' : 'clamp(84px, 13vh, 150px)', height:'auto', display:'block', borderRadius:6 }} />
      <div style={{ fontFamily:T.font, color:'#1B1830', maxWidth: big ? 'none' : 150 }}>
        <div style={{ fontWeight:900, fontSize: big ? 'clamp(20px, 3.4vh, 40px)' : 'clamp(12px, 1.7vh, 18px)', lineHeight:1.25, maxWidth: big ? '9em' : 'none' }}>{big ? 'Olvasd be, és válaszolj a telefonodon!' : '📷 Tölts fel képet'}</div>
        {!big && <div style={{ fontWeight:800, fontSize:'clamp(12px, 1.7vh, 18px)', lineHeight:1.25, marginTop:2 }}>💌 Írj a babának</div>}
      </div>
    </div>
  );
}

// ── A nagy leleplezés (vetítő) ────────────────────────────────────────────────────
// Szakaszok: visszaszámlálás (dobpergéssel) → [videó] → robbanás (konfetti, lufik,
// óriási felirat) → `onDone`. A videó a vetítő gépéről betöltött fájl VAGY az admin
// által megadott link; próbánál (test) soha nincs videó — az elárulná.
function RevealConfetti({ colors }) {
  const ref = React.useRef(null);
  React.useEffect(() => {
    const cv = ref.current; if (!cv) return;
    const ctx = cv.getContext('2d'); let raf = 0, dead = false;
    const fit = () => { cv.width = innerWidth; cv.height = innerHeight; }; fit(); addEventListener('resize', fit);
    const P = []; const W = () => cv.width, H = () => cv.height;
    const burst = n => { for (let i = 0; i < n; i++) P.push({ x: W() / 2, y: H() * 0.55, vx: (Math.random() - 0.5) * 26, vy: -Math.random() * 26 - 8, s: 6 + Math.random() * 10, r: Math.random() * 6, vr: (Math.random() - 0.5) * 0.4, c: colors[i % colors.length], life: 0 }); };
    burst(260); const again = setTimeout(() => burst(180), 900);
    const tick = () => {
      if (dead) return; ctx.clearRect(0, 0, W(), H());
      for (let i = P.length - 1; i >= 0; i--) { const p = P[i]; p.vy += 0.5; p.vx *= 0.99; p.x += p.vx; p.y += p.vy; p.r += p.vr; p.life++;
        if (p.y > H() + 40) { P.splice(i, 1); continue; }
        ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.r); ctx.fillStyle = p.c; ctx.fillRect(-p.s / 2, -p.s / 4, p.s, p.s / 2); ctx.restore(); }
      raf = requestAnimationFrame(tick);
    };
    tick();
    return () => { dead = true; cancelAnimationFrame(raf); clearTimeout(again); removeEventListener('resize', fit); };
  }, []);
  return <canvas ref={ref} aria-hidden="true" style={{ position:'absolute', inset:0, pointerEvents:'none' }} />;
}
function RevealShow({ show, video, onDone }) {
  const R = REVEAL_RESULTS[show.test ? 'test' : show.result] || REVEAL_RESULTS.test;
  const sp = revealSpeed();
  const [stage, setStage] = React.useState('count');     // count | video | boom
  const [n, setN] = React.useState(REVEAL_COUNT_FROM);
  const vidSrc = show.test ? '' : (video || show.videoUrl || '');
  React.useEffect(() => {
    revealDrumroll(REVEAL_COUNT_FROM * sp);
    let k = REVEAL_COUNT_FROM;
    const iv = setInterval(() => { k--; if (k > 0) setN(k); else { clearInterval(iv); setStage(vidSrc ? 'video' : 'boom'); } }, 1000 * sp);
    return () => clearInterval(iv);
  }, []);
  React.useEffect(() => {
    if (stage !== 'boom') return;
    revealCrash();
    const t = setTimeout(onDone, 14000 * sp);
    return () => clearTimeout(t);
  }, [stage]);
  const balloons = React.useMemo(() => Array.from({ length:16 }, (_, i) => ({ x: (i * 6.3 + revealHash('b' + i) * 5) % 100, d: 5 + revealHash('d' + i) * 4, del: revealHash('t' + i) * 2.4, s: 7 + revealHash('s' + i) * 6, c: i % 3 === 2 ? '#fff' : (i % 2 ? R.c1 : R.c2) })), []);
  return (
    <div data-reveal-show={stage} data-reveal-countdown={stage === 'count' ? n : ''} data-reveal-boom={stage === 'boom' ? (show.test ? 'test' : show.result) : ''}
      style={{ position:'absolute', inset:0, zIndex:40, overflow:'hidden', background: stage === 'boom' ? `radial-gradient(circle at 50% 55%, ${R.c2}, ${R.c1} 70%)` : '#07060C', transition:'background .5s' }}>
      {stage === 'count' && (
        <div style={{ position:'absolute', inset:0, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:'3vh' }}>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:'clamp(18px, 3.4vh, 40px)', letterSpacing:'0.3em', color:'rgba(255,255,255,0.7)' }}>{show.test ? 'PRÓBA-LELEPLEZÉS' : 'FIÚ VAGY LÁNY?'}</div>
          <div key={n} style={{ fontFamily:T.font, fontWeight:900, fontSize:'min(46vh, 40vw)', lineHeight:1, color:'#fff',
            background:`linear-gradient(90deg, ${REVEAL_PINK}, ${REVEAL_BLUE})`, WebkitBackgroundClip:'text', backgroundClip:'text', WebkitTextFillColor:'transparent',
            animation:`revealBeat ${sp}s ease-out both` }}>{n}</div>
        </div>
      )}
      {stage === 'video' && (
        <React.Fragment>
          <video data-reveal-video src={vidSrc} autoPlay playsInline onEnded={() => setStage('boom')} onError={() => setStage('boom')}
            style={{ position:'absolute', inset:0, width:'100%', height:'100%', objectFit:'contain', background:'#000' }} />
          <button data-reveal-skipvideo onClick={() => setStage('boom')} style={{ position:'absolute', right:18, bottom:18, padding:'8px 14px', borderRadius:999, border:'none', cursor:'pointer', background:'rgba(255,255,255,0.18)', color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:13 }}>Tovább ›</button>
        </React.Fragment>
      )}
      {stage === 'boom' && (
        <React.Fragment>
          {balloons.map((b, i) => (
            <div key={i} aria-hidden="true" style={{ position:'absolute', left: b.x + '%', bottom:'-20vh', width: b.s + 'vh', height: (b.s * 1.2) + 'vh', borderRadius:'50%', background:b.c,
              boxShadow:'inset -1vh -1.4vh 0 rgba(0,0,0,0.12)', animation:`revealRise ${b.d}s ease-in ${b.del}s both` }} />
          ))}
          <RevealConfetti colors={[R.c1, R.c2, '#ffffff', '#FFD54F']} />
          <div style={{ position:'absolute', inset:0, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:'2vh', pointerEvents:'none' }}>
            <div style={{ fontSize:'min(16vh, 14vw)', animation:'revealPop .8s cubic-bezier(.3,1.6,.5,1) both' }}>{R.emoji}</div>
            <div data-reveal-word style={{ fontFamily:T.font, fontWeight:900, fontSize:'min(30vh, 22vw)', lineHeight:0.95, color:'#fff', textShadow:`0 1.4vh 0 ${R.ink}55, 0 3vh 8vh rgba(0,0,0,0.3)`,
              animation:'revealSlam 1s cubic-bezier(.2,1.5,.4,1) both' }}>{R.word}</div>
            {show.test && <div style={{ fontFamily:T.font, fontWeight:800, fontSize:'clamp(18px, 3.4vh, 40px)', color:'#fff' }}>A leleplezés működik — az eredményt ez nem árulta el.</div>}
          </div>
          <button data-reveal-boomdone onClick={onDone} style={{ position:'absolute', right:18, bottom:18, padding:'8px 14px', borderRadius:999, border:'none', cursor:'pointer', background:'rgba(255,255,255,0.25)', color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:13 }}>Vissza a képekhez ›</button>
        </React.Fragment>
      )}
    </div>
  );
}

// ── Babaquiz a vetítőn ───────────────────────────────────────────────────────────
function revealQuizScores(qs, run, answers, upto) {
  return answers.map(a => {
    let pts = 0; (qs || []).forEach((q, i) => { if (i <= upto && a.a && a.a[run + '_' + i] === q.ok) pts++; });
    return { id:a.id, name:a.name || 'Vendég', pts };
  }).filter(x => x.name).sort((x, y) => y.pts - x.pts || (x.name < y.name ? -1 : 1));
}
function RevealQuizStage({ qstate, answers, qrUrl }) {
  const qs = qstate.qs || [], idx = qstate.idx || 0, q = qs[idx];
  const key = qstate.run + '_' + idx;
  const counts = (q ? q.opts : []).map((_, i) => answers.filter(a => a.a && a.a[key] === i).length);
  const total = counts.reduce((a, b) => a + b, 0);
  if (qstate.phase === 'board') {
    const sc = revealQuizScores(qs, qstate.run, answers, qs.length - 1).slice(0, 10);
    return (
      <div data-reveal-quiz="board" style={{ position:'absolute', inset:0, zIndex:30, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', padding:'4vh 6vw', gap:'2vh', background:REVEAL_NIGHT }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:'clamp(28px, 6vh, 80px)', color:'#fff' }}>🏆 Babaquiz — eredmény</div>
        <div style={{ width:'min(900px, 90vw)', display:'flex', flexDirection:'column', gap:'1.2vh' }}>
          {sc.length === 0 && <div style={{ fontFamily:T.font, color:'rgba(255,255,255,0.7)', fontSize:'3vh', textAlign:'center' }}>Senki nem válaszolt.</div>}
          {sc.map((s, i) => (
            <div key={s.id} data-reveal-quiz-row style={{ display:'flex', alignItems:'center', gap:'2vw', padding:'1.4vh 2vw', borderRadius:16, background: i === 0 ? `linear-gradient(90deg, ${REVEAL_PINK}, ${REVEAL_BLUE})` : 'rgba(255,255,255,0.1)', color: i === 0 ? '#1B1830' : '#fff', fontFamily:T.font, fontWeight:900, fontSize:'clamp(18px, 3.6vh, 44px)', animation:`revealFadeIn .5s ${i * 0.08}s both` }}>
              <span style={{ width:'3em' }}>{i < 3 ? ['🥇','🥈','🥉'][i] : (i + 1) + '.'}</span>
              <span style={{ flex:1, minWidth:0, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{s.name}</span>
              <span>{s.pts} / {qs.length}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }
  if (!q) return null;
  const showAns = qstate.phase === 'ans';
  return (
    <div data-reveal-quiz={qstate.phase} data-reveal-quiz-idx={idx} style={{ position:'absolute', inset:0, zIndex:30, display:'flex', flexDirection:'column', padding:'5vh 5vw 4vh', gap:'3vh', background:REVEAL_NIGHT }}>
      <div style={{ display:'flex', alignItems:'center', gap:'2vw' }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:'clamp(16px, 2.8vh, 32px)', color:REVEAL_PINK, letterSpacing:'0.1em' }}>🍼 BABAQUIZ · {idx + 1} / {qs.length}</div>
        <div style={{ flex:1 }} />
        <div data-reveal-quiz-total style={{ fontFamily:T.font, fontWeight:800, fontSize:'clamp(14px, 2.4vh, 28px)', color:'rgba(255,255,255,0.75)' }}>{total} válasz</div>
      </div>
      <div style={{ display:'flex', gap:'3vw', alignItems:'center' }}>
        <div style={{ flex:1, fontFamily:T.font, fontWeight:900, fontSize:'clamp(26px, 6.4vh, 84px)', lineHeight:1.15, color:'#fff' }}>{q.q}</div>
        {!showAns && qrUrl && <RevealQrCard url={qrUrl} big />}
      </div>
      <div style={{ flex:1, display:'grid', gridTemplateColumns:'1fr 1fr', gap:'2.4vh 2vw', alignContent:'end' }}>
        {q.opts.map((o, i) => {
          const good = showAns && i === q.ok, dim = showAns && i !== q.ok;
          const pct = total ? Math.round(counts[i] / total * 100) : 0;
          return (
            <div key={i} data-reveal-quiz-opt={i} data-correct={good ? '1' : '0'} style={{ position:'relative', overflow:'hidden', borderRadius:22, padding:'3vh 2.4vw', background: REVEAL_QUIZ_COLORS[i % 4], opacity: dim ? 0.35 : 1,
              boxShadow: good ? '0 0 0 0.8vh #fff, 0 2vh 6vh rgba(0,0,0,0.4)' : '0 1vh 3vh rgba(0,0,0,0.3)', transform: good ? 'scale(1.03)' : 'none', transition:'all .5s' }}>
              {showAns && <div style={{ position:'absolute', left:0, top:0, bottom:0, width: pct + '%', background:'rgba(255,255,255,0.22)', transition:'width .8s' }} />}
              <div style={{ position:'relative', display:'flex', alignItems:'center', gap:'1.4vw', fontFamily:T.font, fontWeight:900, color:'#fff', fontSize:'clamp(20px, 4.4vh, 58px)' }}>
                <span style={{ opacity:0.75 }}>{'ABCD'[i]}</span>
                <span style={{ flex:1 }}>{o}</span>
                {showAns && <span data-reveal-quiz-count style={{ fontSize:'0.7em' }}>{counts[i]}{good ? ' ✓' : ''}</span>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function RevealProjector({ title, cfg, onExit }) {
  const { list: photos, loaded } = useRevealPhotos(false);
  const rstate = useRevealDoc('revealState');
  const qdoc = useRevealDoc('revealQuizState');
  const qstate = qdoc.v && qdoc.v.phase && qdoc.v.phase !== 'idle' ? qdoc.v : null;
  const answers = useRevealAnswers(!!qstate);
  const [mode, setMode] = React.useState(() => { const m = revealStore('boh_reveal_mode'); return REVEAL_MODES.some(x => x.id === m) ? m : 'fade'; });
  const [secs, setSecs] = React.useState(() => { const n = +revealStore('boh_reveal_secs'); return REVEAL_SECS.includes(n) ? n : 8; });
  const [showQr, setShowQr] = React.useState(() => revealStore('boh_reveal_qr') !== '0');
  const [paused, setPaused] = React.useState(false);
  const [ui, setUi] = React.useState(true);
  const [fs, setFs] = React.useState(false);
  // a leleplezés: `show` a futó előadás, `revealed` a kiderült eredmény (a háttér színe)
  const [show, setShow] = React.useState(null);
  const [revealed, setRevealed] = React.useState(null);
  const [video, setVideo] = React.useState(null);         // { url, name } — a vetítő gépéről
  const videoRef = React.useRef(null);
  const seq = useRevealSequence(photos, loaded, secs, paused || !!show || !!qstate);
  const pick = (k, v, set) => { set(v); revealStore(k, String(v)); };
  const qrUrl = revealGuestUrl(cfg);

  // ⚠️ Az ELSŐ pillanatképben ülő leleplezést NEM játsszuk le (az már megtörtént — a
  // később nyitó vetítő rögtön a kiderült színt kapja). Csak a menet közben érkező
  // új `run` indít előadást. Óra-független: nem hasonlítunk időbélyeget a helyi órához.
  const firstRef = React.useRef(true), lastRun = React.useRef(null);
  React.useEffect(() => {
    if (!rstate.loaded) return;
    const v = rstate.v || {};
    if (firstRef.current) {
      firstRef.current = false; lastRun.current = v.run || null;
      if (v.phase === 'reveal' && !v.test && REVEAL_RESULTS[v.result]) setRevealed(v.result);
      return;
    }
    if (v.phase !== 'reveal') { setRevealed(null); setShow(null); lastRun.current = v.run || null; return; }
    if (v.run && v.run !== lastRun.current) { lastRun.current = v.run; setShow({ run:v.run, test:!!v.test, result:v.result, videoUrl:v.videoUrl || '' }); }
  }, [rstate]);
  const finishShow = () => { setShow(s => { if (s && !s.test && REVEAL_RESULTS[s.result]) setRevealed(s.result); return null; }); };
  const replay = () => { const v = rstate.v || {}; if (v.phase === 'reveal') setShow({ run:'replay' + Date.now(), test:!!v.test, result:v.result, videoUrl:v.videoUrl || '' }); };
  const pickVideo = f => { if (!f) return; setVideo(old => { if (old) try { URL.revokeObjectURL(old.url); } catch(e) {} return { url: URL.createObjectURL(f), name: f.name || 'videó' }; }); };

  // a legutóbb mutatott tételek (polaroid-halom, áttűnés alsó rétege)
  const [hist, setHist] = React.useState([]);
  React.useEffect(() => { if (seq.cur) setHist(h => [seq.cur].concat(h.filter(x => x.key !== seq.cur.key)).slice(0, 4)); }, [seq.cur && seq.cur.key]);
  // kollázs: három hely; az új tétel mindig a nagyba kerül, a többi körbe jár
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

  const RR = revealed ? REVEAL_RESULTS[revealed] : null;
  const byId = {}; photos.forEach(p => { byId[p.id] = p; });
  const isWish = it => it && it.kind === 'wish';
  const chip = (on) => ({ padding:'7px 12px', borderRadius:999, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:13,
    background: on ? '#fff' : 'rgba(255,255,255,0.14)', color: on ? '#1B1830' : '#fff' });
  const grad = RR
    ? `radial-gradient(70% 80% at 20% 20%, ${RR.c1}66, transparent 70%), radial-gradient(70% 80% at 80% 80%, ${RR.c2}55, transparent 70%), ${REVEAL_NIGHT}`
    : `radial-gradient(60% 70% at 15% 20%, ${REVEAL_PINK}33, transparent 70%), radial-gradient(60% 70% at 85% 80%, ${REVEAL_BLUE}33, transparent 70%), ${REVEAL_NIGHT}`;
  const stage = () => {
    if (!seq.photo) return (
      <div data-reveal-empty style={{ position:'absolute', inset:0, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:'2.4vh', textAlign:'center', padding:'0 6vw' }}>
        <img src={REVEAL_LOGO} alt="" style={{ width:'min(30vh, 40vw)', height:'auto', animation:'revealFloat 4s ease-in-out infinite' }} />
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:'clamp(32px, 7vh, 96px)', lineHeight:1.05, background:`linear-gradient(90deg, ${RR ? RR.c1 : REVEAL_PINK}, ${RR ? RR.c2 : REVEAL_BLUE})`, WebkitBackgroundClip:'text', backgroundClip:'text', color:'transparent' }}>{title || 'Gender Reveal'}</div>
        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:'clamp(15px, 2.6vh, 32px)', color:'rgba(255,255,255,0.7)' }}>{loaded ? 'Hamarosan érkeznek a képek…' : 'Betöltés…'}</div>
      </div>
    );
    if (mode === 'polaroid') {
      const ph = hist.filter(h => byId[h.id] && !isWish(byId[h.id]));
      return (
        <div style={{ position:'absolute', inset:0 }}>
          {ph.slice().reverse().map(h => { const d = isWish(seq.photo) ? ph.indexOf(h) + 1 : ph.indexOf(h); return <RevealPolaroid key={h.key} photo={byId[h.id]} slideKey={h.key} depth={d} isNew={h.isNew} />; })}
          {isWish(seq.photo) && <div style={{ position:'absolute', inset:0, zIndex:12 }}><RevealWishCard wish={seq.photo} slideKey={seq.cur.key} /></div>}
          {seq.cur.isNew && <RevealNewBadge big wish={isWish(seq.photo)} />}
        </div>
      );
    }
    if (mode === 'collage') return (
      <div data-reveal-collage style={{ position:'absolute', inset:'2.5vh 2vw', display:'grid', gridTemplateColumns:'2fr 1fr', gridTemplateRows:'1fr 1fr', gap:'2vh' }}>
        {slots.map((s, i) => {
          const p = s && byId[s.id];
          return (
            <div key={i} style={{ position:'relative', borderRadius:18, overflow:'hidden', background:'rgba(255,255,255,0.05)', gridRow: i === 0 ? '1 / span 2' : undefined,
              boxShadow: s && s.key === seq.cur.key ? `0 0 0 3px ${seq.cur.isNew ? REVEAL_PINK : 'rgba(255,255,255,0.35)'}` : 'none', transition:'box-shadow .6s' }}>
              {p && (isWish(p) ? <RevealWishCard key={s.key} wish={p} slideKey={s.key} compact={i > 0} /> : <RevealFullSlide key={s.key} photo={p} slideKey={s.key} secs={secs} cover={i > 0} />)}
              {s && s.isNew && s.key === seq.cur.key && <RevealNewBadge wish={isWish(p)} />}
            </div>
          );
        })}
      </div>
    );
    const layers = hist.slice(0, 2).reverse();
    return (
      <div style={{ position:'absolute', inset:0 }}>
        {layers.map(h => { const p = byId[h.id]; if (!p) return null;
          return isWish(p) ? <div key={h.key} style={{ position:'absolute', inset:0, background:grad }}><RevealWishCard wish={p} slideKey={h.key} /></div>
                           : <RevealFullSlide key={h.key} photo={p} slideKey={h.key} kenburns={mode === 'kenburns'} secs={secs} />; })}
        {seq.cur.isNew && <RevealNewBadge big wish={isWish(seq.photo)} />}
      </div>
    );
  };
  return ReactDOM.createPortal(
    <div data-reveal-projector data-reveal-mode={mode} data-reveal-current={seq.cur ? seq.cur.id : ''} data-reveal-isnew={seq.cur && seq.cur.isNew ? '1' : '0'} data-reveal-revealed={revealed || ''}
      style={{ position:'fixed', inset:0, zIndex:6000, overflow:'hidden', cursor: ui ? 'default' : 'none', background:grad, transition:'background 1.5s' }}>
      <style>{`
@keyframes revealFadeIn { from { opacity:0 } to { opacity:1 } }
@keyframes revealKB { from { transform:scale(1) translate(0,0) } to { transform:scale(1.12) translate(var(--kb-x), var(--kb-y)) } }
@keyframes revealPop { 0% { transform:scale(.4); opacity:0 } 100% { transform:scale(1); opacity:1 } }
@keyframes revealDrop { 0% { opacity:0; transform:translate(-50%, -50%) translateY(-30vh) rotate(-25deg) scale(1.2) } }
@keyframes revealFloat { 0%,100% { transform:translateY(0) } 50% { transform:translateY(-1.6vh) } }
@keyframes revealBeat { 0% { transform:scale(1.5); opacity:0 } 25% { opacity:1 } 100% { transform:scale(0.92); opacity:0.85 } }
@keyframes revealSlam { 0% { transform:scale(3); opacity:0 } 60% { transform:scale(0.92); opacity:1 } 100% { transform:scale(1) } }
@keyframes revealRise { from { transform:translateY(0) } to { transform:translateY(-140vh) } }
`}</style>
      {stage()}
      {RR && !show && (
        <div data-reveal-resultbadge style={{ position:'absolute', top:'3vh', right:'2.4vw', zIndex:8, padding:'1vh 1.6vw', borderRadius:999, background:`linear-gradient(90deg, ${RR.c1}, ${RR.c2})`, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:'clamp(16px, 3vh, 36px)', boxShadow:'0 8px 30px rgba(0,0,0,0.35)' }}>{RR.emoji} {RR.word}</div>
      )}
      {showQr && qrUrl && !qstate && !show && (
        <div style={{ position:'absolute', right:'2vw', bottom:'3vh', zIndex:8 }}><RevealQrCard url={qrUrl} /></div>
      )}
      {qstate && !show && <RevealQuizStage qstate={qstate} answers={answers} qrUrl={qrUrl} />}
      {show && <RevealShow key={show.run} show={show} video={video && video.url} onDone={finishShow} />}
      <div data-reveal-controls style={{ position:'absolute', left:0, right:0, top:0, display:'flex', alignItems:'center', gap:8, flexWrap:'wrap', padding:'14px 18px',
        background:'linear-gradient(rgba(0,0,0,0.6), transparent)', opacity: ui ? 1 : 0, pointerEvents: ui ? 'auto' : 'none', transition:'opacity .4s', zIndex:60 }}>
        <button data-reveal-exit onClick={() => { try { if (document.fullscreenElement) document.exitFullscreen(); } catch(e) {} onExit(); }} aria-label="Vissza" style={{ ...chip(false), padding:'7px 10px' }}>‹ Vissza</button>
        <div style={{ display:'flex', gap:6, flexWrap:'wrap' }}>
          {REVEAL_MODES.map(m => <button key={m.id} data-reveal-modebtn={m.id} onClick={() => pick('boh_reveal_mode', m.id, setMode)} style={chip(mode === m.id)}>{m.label}</button>)}
        </div>
        <div style={{ display:'flex', gap:6 }}>
          {REVEAL_SECS.map(n => <button key={n} data-reveal-secs={n} onClick={() => pick('boh_reveal_secs', n, setSecs)} style={chip(secs === n)}>{n} mp</button>)}
        </div>
        <div style={{ flex:1 }} />
        <span data-reveal-count style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:'rgba(255,255,255,0.8)' }}>{photos.filter(p => p.src).length} kép</span>
        {qrUrl && <button data-reveal-qrbtn onClick={() => { const v = !showQr; setShowQr(v); revealStore('boh_reveal_qr', v ? '1' : '0'); }} style={chip(showQr)}>QR</button>}
        <button data-reveal-videobtn onClick={() => videoRef.current && videoRef.current.click()} title={video ? video.name : ''} style={chip(!!video)}>{video ? '🎬 Videó kész' : '🎬 Videó'}</button>
        <input ref={videoRef} data-reveal-videoinput type="file" accept="video/*" style={{ display:'none' }} onChange={e => { pickVideo(e.target.files && e.target.files[0]); e.target.value = ''; }} />
        {rstate.v && rstate.v.phase === 'reveal' && !show && <button data-reveal-replay onClick={replay} style={chip(false)}>↻ Leleplezés újra</button>}
        <button data-reveal-pause onClick={() => setPaused(p => !p)} style={chip(paused)}>{paused ? '▶ Folytatás' : '⏸ Szünet'}</button>
        <button data-reveal-next onClick={seq.next} style={chip(false)}>Következő ›</button>
        <button data-reveal-fs onClick={toggleFs} style={chip(fs)}>{fs ? 'Kilépés a teljes képernyőből' : '⛶ Teljes képernyő'}</button>
      </div>
    </div>,
    document.body
  );
}

// ── Babaquiz-vezérlő (operátor) ──────────────────────────────────────────────────
function RevealQuizControl() {
  const quiz = useRevealDoc('revealQuiz');
  const qdoc = useRevealDoc('revealQuizState');
  const st = qdoc.v || { phase:'idle' };
  const active = st.phase && st.phase !== 'idle';
  const answers = useRevealAnswers(active);
  const qs = (quiz.v && Array.isArray(quiz.v.questions) && quiz.v.questions.length) ? quiz.v.questions : REVEAL_QUIZ_DEFAULT;
  const write = d => { const db = revealDb(); if (db) db.collection('config').doc('revealQuizState').set(d).catch(() => {}); };
  const start = () => write({ phase:'q', idx:0, run: revealToken(), qs });
  const key = st.run + '_' + (st.idx || 0);
  const nAns = active ? answers.filter(a => a.a && a.a[key] !== undefined).length : 0;
  const last = active && (st.idx || 0) >= (st.qs || []).length - 1;
  const btn = (primary) => ({ flex:1, padding:'13px 10px', borderRadius:14, border: primary ? 'none' : `1.5px solid ${T.border}`, cursor:'pointer', background: primary ? T.mint : 'transparent', color: primary ? '#fff' : T.inkSoft, fontFamily:T.font, fontWeight:900, fontSize:14 });
  return (
    <div data-reveal-quizctl={st.phase || 'idle'} style={{ background:T.surface, borderRadius:16, padding:14, boxShadow:T.shadow }}>
      <div style={{ display:'flex', alignItems:'baseline', justifyContent:'space-between' }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>🍼 Babaquiz</div>
        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft }}>{active ? (st.phase === 'board' ? 'Eredménytábla' : `${(st.idx || 0) + 1}. / ${(st.qs || []).length} kérdés · ${nAns} válasz`) : `${qs.length} kérdés`}</div>
      </div>
      {active && st.phase !== 'board' && st.qs && st.qs[st.idx || 0] && <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.ink, marginTop:8, lineHeight:1.4 }}>{st.qs[st.idx || 0].q}</div>}
      <div style={{ display:'flex', gap:8, marginTop:12 }}>
        {!active && <button data-reveal-quiz-start onClick={start} style={btn(true)}>Kvíz indítása a vetítőn</button>}
        {st.phase === 'q' && <button data-reveal-quiz-show onClick={() => write(Object.assign({}, st, { phase:'ans' }))} style={btn(true)}>Megoldás mutatása</button>}
        {st.phase === 'ans' && !last && <button data-reveal-quiz-next onClick={() => write(Object.assign({}, st, { phase:'q', idx:(st.idx || 0) + 1 }))} style={btn(true)}>Következő kérdés</button>}
        {st.phase === 'ans' && last && <button data-reveal-quiz-board onClick={() => write(Object.assign({}, st, { phase:'board' }))} style={btn(true)}>Eredménytábla</button>}
        {active && <button data-reveal-quiz-end onClick={() => write({ phase:'idle' })} style={btn(st.phase === 'board')}>{st.phase === 'board' ? 'Kvíz vége' : 'Megszakítás'}</button>}
      </div>
    </div>
  );
}

function RevealOperator({ onBack }) {
  const { list: items, loaded } = useRevealPhotos(true);
  const [busy, setBusy] = React.useState({ done:0, total:0 });
  const [errs, setErrs] = React.useState([]);
  const [confirmDel, setConfirmDel] = React.useState(null);
  const pickRef = React.useRef(null), camRef = React.useRef(null);
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
  const latest = approved.slice().reverse();
  const bigBtn = (primary) => ({ flex:1, minWidth:0, padding:'18px 10px', borderRadius:18, border: primary ? 'none' : `2px solid ${T.mint}`, cursor:'pointer',
    background: primary ? T.mint : T.surface, color: primary ? '#fff' : T.mint, fontFamily:T.font, fontWeight:900, fontSize:16, display:'flex', flexDirection:'column', alignItems:'center', gap:6 });
  const tileBody = p => p.kind === 'wish'
    ? <div style={{ position:'absolute', inset:0, padding:'12px 10px 46px', background:'#FFF1F5', display:'flex', flexDirection:'column', justifyContent:'center', textAlign:'center', opacity: p.hidden ? 0.4 : 1 }}>
        <div style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:'#2A1E3A', lineHeight:1.35, overflow:'hidden', display:'-webkit-box', WebkitLineClamp:5, WebkitBoxOrient:'vertical', overflowWrap:'anywhere' }}>💌 „{p.text}”</div>
      </div>
    : <img src={p.src} alt="" style={{ width:'100%', height:'100%', objectFit:'cover', opacity: p.hidden ? 0.3 : 1 }} />;
  const byLine = p => p.by ? <div style={{ position:'absolute', top:8, right:8, maxWidth:'70%', padding:'3px 8px', borderRadius:999, background:'rgba(0,0,0,0.6)', color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:11, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.by}</div> : null;
  const smallBtn = (bg, fg) => ({ flex:1, padding:'7px 0', borderRadius:10, border:'none', cursor:'pointer', background:bg, color:fg, fontFamily:T.font, fontWeight:800, fontSize:12 });
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
          {pending.length > 0 && (
            <div data-reveal-pending style={{ background:T.surface, borderRadius:16, padding:14, boxShadow:T.shadow, border:`2px solid ${REVEAL_PINK}` }}>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink, marginBottom:10 }}>Jóváhagyásra vár ({pending.length})</div>
              <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(150px, 1fr))', gap:10 }}>
                {pending.map(p => (
                  <div key={p.id} data-reveal-pend={p.id} style={{ position:'relative', borderRadius:14, overflow:'hidden', background:T.bg, aspectRatio:'1 / 1' }}>
                    {tileBody(p)}{byLine(p)}
                    <div style={{ position:'absolute', left:6, right:6, bottom:6, display:'flex', gap:6 }}>
                      <button data-reveal-approve onClick={() => approve(p)} style={smallBtn(T.mint, '#fff')}>Mehet</button>
                      <button data-reveal-reject onClick={() => del(p)} style={smallBtn('rgba(220,70,70,0.92)', '#fff')}>Eldob</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          <RevealQuizControl />
          <div style={{ display:'flex', alignItems:'baseline', justifyContent:'space-between', marginTop:4 }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>A vetítőn</div>
            <div data-reveal-opcount style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkSoft }}>{loaded ? `${shown} a vetítőn${approved.length > shown ? ` · ${approved.length - shown} rejtve` : ''}` : 'Betöltés…'}</div>
          </div>
          {loaded && !approved.length && <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, textAlign:'center', padding:'24px 0' }}>Még nincs feltöltött kép.</div>}
          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(150px, 1fr))', gap:10 }}>
            {latest.map(p => (
              <div key={p.id} data-reveal-thumb={p.id} data-hidden={p.hidden ? '1' : '0'} style={{ position:'relative', borderRadius:14, overflow:'hidden', background:T.surface, boxShadow:T.shadow, aspectRatio:'1 / 1' }}>
                {tileBody(p)}{byLine(p)}
                {p.hidden && <div style={{ position:'absolute', top:8, left:8, padding:'3px 8px', borderRadius:999, background:'rgba(0,0,0,0.6)', color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:11 }}>REJTVE</div>}
                <div style={{ position:'absolute', left:6, right:6, bottom:6, display:'flex', gap:6 }}>
                  <button data-reveal-hide onClick={() => setHidden(p, !p.hidden)} style={smallBtn('rgba(255,255,255,0.92)', '#1B1830')}>{p.hidden ? 'Mutat' : 'Elrejt'}</button>
                  <button data-reveal-del onClick={() => setConfirmDel(p)} aria-label="Törlés" style={{ width:36, padding:'7px 0', borderRadius:10, border:'none', cursor:'pointer', background:'rgba(220,70,70,0.92)', color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:12 }}>🗑</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
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

// ── Leleplező: külön kóddal, NEM az operátor ─────────────────────────────────────
// Az eredményt a leleplező SEM látja: a gomb csak átmásolja a titkos dokumentumból a
// szobába (`revealState`), a vetítő pedig ott olvassa először.
function RevealTrigger({ onBack }) {
  const secret = useRevealDoc('revealSecret');
  const rstate = useRevealDoc('revealState');
  const [code, setCode] = React.useState('');
  const [ok, setOk] = React.useState(false);
  const [bad, setBad] = React.useState(false);
  const [ask, setAsk] = React.useState(false);
  const [msg, setMsg] = React.useState('');
  const sec = secret.v || {};
  const ready = !!(REVEAL_RESULTS[sec.result] && sec.result !== 'test');
  const st = rstate.v || {};
  const done = st.phase === 'reveal' && !st.test;
  const fire = test => {
    const db = revealDb(); if (!db) return;
    if (!test && !ready) return;
    db.collection('config').doc('revealState').set({ phase:'reveal', run: revealToken(), test: !!test, result: test ? 'test' : sec.result, videoUrl: test ? '' : (sec.videoUrl || ''), at: Date.now() })
      .then(() => { setMsg(test ? 'Próba elindítva a vetítőn' : 'Elindult a leleplezés!'); setTimeout(() => setMsg(''), 4000); })
      .catch(e => setMsg('Nem sikerült (' + ((e && e.code) || 'hiba') + ')'));
    setAsk(false);
  };
  const card = { width:'100%', maxWidth:440, background:T.surface, borderRadius:22, padding:'22px 20px', boxShadow:T.shadow, boxSizing:'border-box' };
  return (
    <div data-reveal-trigger style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title="Leleplezés" onBack={onBack} />
      <div style={{ flex:1, overflowY:'auto', display:'flex', flexDirection:'column', alignItems:'center', gap:16, padding:'22px 16px calc(24px + env(safe-area-inset-bottom))' }}>
        {!secret.loaded ? <div style={{ fontFamily:T.font, color:T.inkSoft }}>Betöltés…</div>
        : !sec.code ? <div data-reveal-nocode style={{ ...card, textAlign:'center', fontFamily:T.font, fontSize:14, fontWeight:700, color:T.inkSoft, lineHeight:1.5 }}>Még nincs leleplező kód beállítva.<br/>Admin → Gender Reveal → Leleplezés</div>
        : !ok ? (
          <div data-reveal-codegate style={{ ...card, display:'flex', flexDirection:'column', gap:12 }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, textAlign:'center' }}>🎉 Leleplező kód</div>
            <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', lineHeight:1.45 }}>Ez nem a közös jelszó — csak az indíthatja a leleplezést, aki ezt a kódot ismeri.</div>
            <input data-reveal-code type="password" value={code} autoFocus onChange={e => { setCode(e.target.value); setBad(false); }} onKeyDown={e => { if (e.key === 'Enter') { if (code.trim() === sec.code) setOk(true); else setBad(true); } }}
              style={{ width:'100%', boxSizing:'border-box', padding:'14px', borderRadius:14, border:`1.5px solid ${bad ? T.coral : T.border}`, background:T.bg, fontFamily:T.font, fontSize:17, fontWeight:700, color:T.ink, textAlign:'center', outline:'none' }} />
            {bad && <div data-reveal-codebad style={{ fontFamily:T.font, fontSize:13, fontWeight:800, color:T.coral, textAlign:'center' }}>Hibás kód</div>}
            <PrimaryButton onClick={() => { if (code.trim() === sec.code) setOk(true); else setBad(true); }} disabled={!code.trim()}>Tovább</PrimaryButton>
          </div>
        ) : (
          <div data-reveal-firepanel style={{ ...card, display:'flex', flexDirection:'column', gap:14, textAlign:'center' }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink }}>{done ? 'Leleplezve 🎉' : 'Kész a nagy pillanatra?'}</div>
            <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, lineHeight:1.5 }}>Az eredményt itt sem látod — a vetítő mutatja meg mindenkinek egyszerre. 10-től visszaszámol{sec.videoUrl ? ', lejátssza a videót,' : ''} majd jön a nagy robbanás.</div>
            {!ready && <div data-reveal-notready style={{ fontFamily:T.font, fontSize:13, fontWeight:800, color:T.coral }}>Az admin még nem állította be az eredményt.</div>}
            <button data-reveal-fire disabled={!ready} onClick={() => setAsk(true)} style={{ padding:'22px 12px', borderRadius:20, border:'none', cursor: ready ? 'pointer' : 'default', fontFamily:T.font, fontWeight:900, fontSize:22, color:'#fff',
              background: ready ? `linear-gradient(90deg, ${REVEAL_PINK}, ${REVEAL_BLUE})` : T.surfaceMuted, boxShadow: ready ? '0 10px 30px rgba(0,0,0,0.18)' : 'none' }}>{done ? '↻ Leleplezés újra' : '🎉 LELEPLEZÉS'}</button>
            <button data-reveal-test onClick={() => fire(true)} style={{ padding:'12px', borderRadius:14, border:`1.5px solid ${T.border}`, background:'transparent', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft }}>Próba-leleplezés (nem árulja el)</button>
            {msg && <div data-reveal-firemsg style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.mint }}>{msg}</div>}
          </div>
        )}
      </div>
      {ask && (
        <ActionModal kicker="Indulhat?" onClose={() => setAsk(false)} onSecondary={() => setAsk(false)} secondaryLabel="Még ne"
          onPrimary={() => fire(false)} primaryLabel="Indulhat!" primaryColor={T.mint}>
          A vetítőn elindul a visszaszámlálás. Mindenki nézzen oda! 🎉
        </ActionModal>
      )}
    </div>
  );
}

// ── Vendég-oldal (QR-kódról, jelszó NÉLKÜL — a `guestKey` a belépő) ────────────────
function RevealGuest({ cfg }) {
  const qdoc = useRevealDoc('revealQuizState');
  const qst = qdoc.v || { phase:'idle' };
  const [name, setName] = React.useState(() => revealStore('boh_reveal_guest_name') || '');
  const [nameInp, setNameInp] = React.useState('');
  const [gid] = React.useState(() => { let g = revealStore('boh_reveal_gid'); if (!g) { g = revealToken(); revealStore('boh_reveal_gid', g); } return g; });
  const [busy, setBusy] = React.useState({ done:0, total:0 });
  const [errs, setErrs] = React.useState([]);
  const [wish, setWish] = React.useState('');
  const [sent, setSent] = React.useState('');
  const [myAns, setMyAns] = React.useState({});
  const pickRef = React.useRef(null), camRef = React.useRef(null);
  const db = revealDb();
  React.useEffect(() => {
    if (!db) return;
    const un = db.collection('revealQuizAns').doc(gid).onSnapshot(d => setMyAns((d && d.exists && d.data() && d.data().a) || {}), () => {});
    return () => { try { un(); } catch(e) {} };
  }, [gid]);
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
  const answer = i => {
    const k = qst.run + '_' + (qst.idx || 0);
    if (!db || myAns[k] !== undefined) return;
    setMyAns(a => Object.assign({}, a, { [k]: i }));
    db.collection('revealQuizAns').doc(gid).set({ name, a:{ [k]: i } }, { merge:true }).catch(() => {});
  };
  const card = { background:T.surface, borderRadius:20, padding:'16px', boxShadow:T.shadow, display:'flex', flexDirection:'column', gap:10 };
  const title = (cfg && cfg.title) || 'Gender Reveal';
  if (!name) return (
    <div data-reveal-guest="name" style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title={title} />
      <div style={{ flex:1, overflowY:'auto', display:'flex', flexDirection:'column', alignItems:'center', gap:16, padding:'22px 16px' }}>
        <img src={REVEAL_LOGO} alt="" style={{ width:110, height:110 }} />
        <div style={{ ...card, width:'100%', maxWidth:440, boxSizing:'border-box' }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, textAlign:'center' }}>Szia! Hogy hívnak?</div>
          <input data-reveal-guestname value={nameInp} onChange={e => setNameInp(e.target.value.slice(0, 40))} onKeyDown={e => { if (e.key === 'Enter' && nameInp.trim()) { revealStore('boh_reveal_guest_name', nameInp.trim()); setName(nameInp.trim()); } }} placeholder="A neved"
            style={{ width:'100%', boxSizing:'border-box', padding:'14px', borderRadius:14, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:17, fontWeight:700, color:T.ink, textAlign:'center', outline:'none' }} />
          <PrimaryButton onClick={() => { revealStore('boh_reveal_guest_name', nameInp.trim()); setName(nameInp.trim()); }} disabled={!nameInp.trim()}>Tovább</PrimaryButton>
        </div>
      </div>
    </div>
  );
  const qk = qst.run + '_' + (qst.idx || 0), q = (qst.qs || [])[qst.idx || 0], mine = myAns[qk];
  const myScore = qst.phase === 'board' ? (qst.qs || []).reduce((s, qq, i) => s + (myAns[qst.run + '_' + i] === qq.ok ? 1 : 0), 0) : 0;
  return (
    <div data-reveal-guest="main" style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title={title} />
      <div style={{ flex:1, overflowY:'auto', padding:'16px 16px calc(24px + env(safe-area-inset-bottom))' }}>
        <div style={{ maxWidth:520, margin:'0 auto', display:'flex', flexDirection:'column', gap:14 }}>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft, textAlign:'center' }}>Szia, {name}! 👋 <button onClick={() => { setName(''); setNameInp(name); }} style={{ border:'none', background:'transparent', color:T.mint, fontFamily:T.font, fontWeight:800, fontSize:13, cursor:'pointer' }}>nem én vagyok</button></div>
          {qst.phase && qst.phase !== 'idle' && (
            <div data-reveal-guestquiz={qst.phase} style={{ ...card, border:`2px solid ${REVEAL_PINK}` }}>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:REVEAL_PINK, letterSpacing:'0.08em' }}>🍼 BABAQUIZ{qst.phase !== 'board' ? ` · ${(qst.idx || 0) + 1} / ${(qst.qs || []).length}` : ''}</div>
              {qst.phase === 'board' ? (
                <div data-reveal-guestscore style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink, textAlign:'center', padding:'8px 0' }}>{myScore} / {(qst.qs || []).length} jó válasz 🎉</div>
              ) : q && (
                <React.Fragment>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, lineHeight:1.3 }}>{q.q}</div>
                  {q.opts.map((o, i) => {
                    const ansPhase = qst.phase === 'ans';
                    const good = ansPhase && i === q.ok, wrong = ansPhase && mine === i && i !== q.ok;
                    return (
                      <button key={i} data-reveal-guestopt={i} disabled={mine !== undefined || ansPhase} onClick={() => answer(i)}
                        style={{ padding:'14px', borderRadius:14, border: mine === i ? '3px solid #1B1830' : '3px solid transparent', cursor: mine === undefined && !ansPhase ? 'pointer' : 'default',
                          background: REVEAL_QUIZ_COLORS[i % 4], color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:16, textAlign:'left', opacity: (ansPhase && !good && mine !== i) || (!ansPhase && mine !== undefined && mine !== i) ? 0.45 : 1 }}>
                        {'ABCD'[i]} · {o}{good ? ' ✓' : ''}{wrong ? ' ✗' : ''}
                      </button>
                    );
                  })}
                  <div data-reveal-guestquizmsg style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft, textAlign:'center' }}>
                    {qst.phase === 'ans' ? (mine === q.ok ? 'Eltaláltad! 🎉' : mine === undefined ? 'Erre nem válaszoltál.' : 'Most nem jött be.') : mine !== undefined ? 'Válasz rögzítve — figyeld a kivetítőt!' : 'Válassz egyet!'}
                  </div>
                </React.Fragment>
              )}
            </div>
          )}
          <div style={card}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink }}>📷 Kép a kivetítőre</div>
            <div style={{ display:'flex', gap:10 }}>
              <button onClick={() => camRef.current && camRef.current.click()} style={{ flex:1, padding:'14px 8px', borderRadius:14, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer' }}>Fotózás</button>
              <button data-reveal-guestpick onClick={() => pickRef.current && pickRef.current.click()} style={{ flex:1, padding:'14px 8px', borderRadius:14, border:`2px solid ${T.mint}`, background:'transparent', color:T.mint, fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer' }}>Galériából</button>
            </div>
            <input ref={camRef} type="file" accept="image/*" capture="environment" style={{ display:'none' }} onChange={e => { onFiles(e.target.files); e.target.value = ''; }} />
            <input ref={pickRef} data-reveal-guestinput type="file" accept="image/*" multiple style={{ display:'none' }} onChange={e => { onFiles(e.target.files); e.target.value = ''; }} />
            {busy.total > 0 && <div style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft }}>{busy.done >= busy.total ? 'Feltöltve ✓' : `Feltöltés… ${busy.done} / ${busy.total}`}</div>}
            {errs.map((e, i) => <div key={i} style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.coral }}>⚠️ {e}</div>)}
          </div>
          <div style={card}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink }}>💌 Üzenet a babának</div>
            <textarea data-reveal-wishinput value={wish} onChange={e => setWish(e.target.value.slice(0, REVEAL_WISH_MAX))} rows={3} placeholder="pl. Isten hozott, kicsi!"
              style={{ width:'100%', boxSizing:'border-box', padding:'12px', borderRadius:14, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:15, color:T.ink, outline:'none', resize:'none' }} />
            <div style={{ display:'flex', alignItems:'center', gap:10 }}>
              <span style={{ flex:1, fontFamily:T.font, fontSize:12, color:T.inkSoft }}>{wish.length} / {REVEAL_WISH_MAX}</span>
              <button data-reveal-wishsend disabled={!wish.trim()} onClick={sendWish} style={{ padding:'11px 20px', borderRadius:12, border:'none', background: wish.trim() ? T.mint : T.surfaceMuted, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14, cursor: wish.trim() ? 'pointer' : 'default' }}>Küldés</button>
            </div>
          </div>
          {sent && <div data-reveal-guestsent style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.mint, textAlign:'center' }}>{sent}</div>}
        </div>
      </div>
    </div>
  );
}

// ── Album (csak nézhető galéria-link a szülőknek) ─────────────────────────────────
function RevealAlbum({ cfg }) {
  const { list, loaded } = useRevealPhotos(false);
  const [open, setOpen] = React.useState(-1);
  const photos = list.filter(p => p.src), wishes = list.filter(p => p.kind === 'wish');
  const title = (cfg && cfg.title) || 'Gender Reveal';
  return (
    <div data-reveal-album style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title={title + ' · album'} />
      <div style={{ flex:1, overflowY:'auto', padding:'16px 16px calc(24px + env(safe-area-inset-bottom))' }}>
        <div style={{ maxWidth:1100, margin:'0 auto', display:'flex', flexDirection:'column', gap:14 }}>
          <div style={{ display:'flex', alignItems:'center', gap:10, flexWrap:'wrap' }}>
            <div style={{ flex:1, fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft }}>{loaded ? `${photos.length} kép · ${wishes.length} üzenet` : 'Betöltés…'}</div>
            <button data-reveal-albumzip disabled={!loaded || !list.length} onClick={() => revealDownloadAlbum(list)} style={{ padding:'11px 16px', borderRadius:12, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14, cursor:'pointer' }}>📦 Összes letöltése (ZIP)</button>
          </div>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(160px, 1fr))', gap:10 }}>
            {photos.map((p, i) => <button key={p.id} data-reveal-albumthumb onClick={() => setOpen(i)} style={{ padding:0, border:'none', borderRadius:12, overflow:'hidden', aspectRatio:'1 / 1', cursor:'pointer', background:T.surface }}><img src={p.src} alt="" style={{ width:'100%', height:'100%', objectFit:'cover', display:'block' }} /></button>)}
          </div>
          {wishes.length > 0 && <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink, marginTop:6 }}>💌 Üzenetek a babának</div>}
          {wishes.map(w => <div key={w.id} style={{ background:T.surface, borderRadius:14, padding:'12px 14px', boxShadow:T.shadow, fontFamily:T.font, fontSize:15, color:T.ink, lineHeight:1.45 }}>„{w.text}”{w.by && <span style={{ color:T.inkSoft, fontWeight:800 }}> — {w.by}</span>}</div>)}
        </div>
      </div>
      {open >= 0 && photos[open] && ReactDOM.createPortal(
        <div data-reveal-lightbox onClick={() => setOpen(-1)} style={{ position:'fixed', inset:0, zIndex:7000, background:'rgba(0,0,0,0.92)', display:'flex', alignItems:'center', justifyContent:'center' }}>
          <img src={photos[open].src} alt="" style={{ maxWidth:'96vw', maxHeight:'90vh', objectFit:'contain' }} />
          {open > 0 && <button onClick={e => { e.stopPropagation(); setOpen(open - 1); }} aria-label="Előző" style={{ position:'absolute', left:12, top:'50%', width:46, height:46, borderRadius:'50%', border:'none', background:'rgba(255,255,255,0.2)', color:'#fff', fontSize:24, cursor:'pointer' }}>‹</button>}
          {open < photos.length - 1 && <button onClick={e => { e.stopPropagation(); setOpen(open + 1); }} aria-label="Következő" style={{ position:'absolute', right:12, top:'50%', width:46, height:46, borderRadius:'50%', border:'none', background:'rgba(255,255,255,0.2)', color:'#fff', fontSize:24, cursor:'pointer' }}>›</button>}
        </div>, document.body)}
    </div>
  );
}

function RevealScreen({ go, deepLink }) {
  const cfg = useRevealCfg();
  const pw = (cfg.v && cfg.v.password) || '';
  const title = (cfg.v && cfg.v.title) || 'Gender Reveal';
  const gParam = React.useMemo(() => revealParam('g'), []);
  const albumParam = React.useMemo(() => revealParam('album'), []);
  // ⚠️ A jelszót NEM mentjük (tulajdonosi döntés, v10.431): minden megnyitáskor bekéri.
  // Csak a munkamenetre él; a v10.430-ban esetleg eltárolt értéket is töröljük.
  const [saved, setSaved] = React.useState('');
  React.useEffect(() => { try { localStorage.removeItem('boh_reveal_pw'); } catch(e) {} }, []);
  const [inp, setInp] = React.useState('');
  const [bad, setBad] = React.useState(false);
  const [role, setRole] = React.useState(null);   // null | 'projector' | 'operator' | 'trigger'
  const ok = !!pw && saved === pw;
  const submit = () => {
    if (inp.trim() && inp.trim() === pw) { setSaved(inp.trim()); setBad(false); setInp(''); }
    else setBad(true);
  };
  const back = deepLink ? null : () => go('home');
  const card = { width:'100%', maxWidth:440, background:T.surface, borderRadius:22, padding:'22px 20px', boxShadow:T.shadow, boxSizing:'border-box' };
  // vendég- és album-link: jelszó nélkül, a saját kulcsukkal
  if ((gParam || albumParam) && cfg.loaded) {
    const v = cfg.v || {};
    if (gParam && v.guestKey && gParam === v.guestKey) return <RevealGuest cfg={v} />;
    if (albumParam && v.albumKey && albumParam === v.albumKey) return <RevealAlbum cfg={v} />;
    return (
      <div data-reveal-badlink style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:12, background:T.bg, padding:24, textAlign:'center' }}>
        <img src={REVEAL_LOGO} alt="" style={{ width:110, height:110 }} />
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink }}>Ez a link már nem érvényes</div>
        <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft }}>Kérj újat a szervezőktől.</div>
      </div>
    );
  }
  if (ok && role === 'projector') return <RevealProjector title={title} cfg={cfg.v} onExit={() => setRole(null)} />;
  if (ok && role === 'operator') return <RevealOperator onBack={() => setRole(null)} />;
  if (ok && role === 'trigger') return <RevealTrigger onBack={() => setRole(null)} />;
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
          <div data-reveal-roles style={{ width:'100%', maxWidth:860, display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(240px, 1fr))', gap:14 }}>
            {[
              { id:'projector', emoji:'📽️', name:'Vetítő', sub:'Laptop a kivetítőn — képek, üzenetek, Babaquiz és a nagy leleplezés.' },
              { id:'operator', emoji:'📷', name:'Operátor', sub:'Feltöltés, a vendégek képeinek jóváhagyása, a Babaquiz vezetése.' },
              { id:'trigger', emoji:'🎉', name:'Leleplező', sub:'Külön kóddal — ő indítja a nagy pillanatot. Az eredményt ő sem látja.' },
            ].map(r => (
              <button key={r.id} data-reveal-role={r.id} onClick={() => { if (r.id === 'projector') revealAudio(); setRole(r.id); }} style={{ ...card, maxWidth:'none', border:'none', cursor:'pointer', textAlign:'left', display:'flex', flexDirection:'column', gap:6 }}>
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

// Admin → Gender Reveal: belépés, leleplezés, Babaquiz, linkek, album és ürítés.
function AdminRevealQuiz() {
  const quiz = useRevealDoc('revealQuiz');
  const [qs, setQs] = React.useState(null);
  const [msg, setMsg] = React.useState('');
  React.useEffect(() => { if (quiz.loaded && qs === null) setQs(JSON.parse(JSON.stringify((quiz.v && Array.isArray(quiz.v.questions) && quiz.v.questions.length) ? quiz.v.questions : REVEAL_QUIZ_DEFAULT))); }, [quiz.loaded]);
  if (!qs) return null;
  const upd = (i, f) => setQs(a => a.map((q, k) => k === i ? f(Object.assign({}, q, { opts:q.opts.slice() })) : q));
  const save = () => {
    // üres opciók ki; a helyes válasz indexe követi a szűrést
    const clean = qs.map(q => { const keep = q.opts.map((o, i) => ({ o:String(o || '').trim(), i })).filter(x => x.o);
      const ok = Math.max(0, keep.findIndex(x => x.i === q.ok)); return { q:String(q.q || '').trim(), opts:keep.map(x => x.o), ok }; })
      .filter(q => q.q && q.opts.length >= 2);
    const db = revealDb(); if (!db) return;
    db.collection('config').doc('revealQuiz').set({ questions: clean }).then(() => { setQs(clean); setMsg('Mentve ✓'); setTimeout(() => setMsg(''), 2500); }).catch(e => setMsg('Nem sikerült (' + ((e && e.code) || 'hiba') + ')'));
  };
  const inp = { width:'100%', boxSizing:'border-box', padding:'9px 10px', borderRadius:10, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:13, color:T.ink, outline:'none' };
  return (
    <div data-admin-reveal-quiz style={{ background:T.surface, borderRadius:16, padding:16, boxShadow:T.shadow }}>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>🍼 Babaquiz kérdései</div>
      <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:4, lineHeight:1.45 }}>A kört az operátor vezeti, a vendégek a QR-kóddal válaszolnak. Jelöld a helyes választ — saját kérdés is mehet (pl. „Hány kilóval született az anyuka?").</div>
      {qs.map((q, i) => (
        <div key={i} data-admin-reveal-q={i} style={{ marginTop:12, padding:12, borderRadius:12, background:T.bg }}>
          <div style={{ display:'flex', gap:8, alignItems:'center' }}>
            <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:T.inkSoft }}>{i + 1}.</span>
            <input value={q.q} onChange={e => upd(i, x => Object.assign(x, { q:e.target.value }))} placeholder="Kérdés" style={inp} />
            <button onClick={() => setQs(a => a.filter((_, k) => k !== i))} aria-label="Kérdés törlése" style={{ border:'none', background:'transparent', cursor:'pointer', fontSize:16 }}>🗑</button>
          </div>
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:6, marginTop:8 }}>
            {[0, 1, 2, 3].map(k => (
              <label key={k} style={{ display:'flex', alignItems:'center', gap:6 }}>
                <input type="radio" name={'rq' + i} checked={q.ok === k} onChange={() => upd(i, x => Object.assign(x, { ok:k }))} />
                <input value={q.opts[k] || ''} onChange={e => upd(i, x => { x.opts[k] = e.target.value; return x; })} placeholder={'ABCD'[k] + ' válasz'} style={inp} />
              </label>
            ))}
          </div>
        </div>
      ))}
      <div style={{ display:'flex', gap:10, alignItems:'center', flexWrap:'wrap', marginTop:12 }}>
        <button data-admin-reveal-qadd onClick={() => setQs(a => a.concat({ q:'', opts:['', '', '', ''], ok:0 }))} style={{ padding:'10px 14px', borderRadius:12, border:`1.5px solid ${T.mint}`, background:'transparent', color:T.mint, fontFamily:T.font, fontWeight:900, fontSize:13, cursor:'pointer' }}>+ Kérdés</button>
        <button onClick={() => setQs(JSON.parse(JSON.stringify(REVEAL_QUIZ_DEFAULT)))} style={{ padding:'10px 14px', borderRadius:12, border:`1.5px solid ${T.border}`, background:'transparent', color:T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:13, cursor:'pointer' }}>Alap kérdések</button>
        <button data-admin-reveal-qsave onClick={save} style={{ padding:'10px 16px', borderRadius:12, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:13, cursor:'pointer' }}>Mentés</button>
        {msg && <span data-admin-reveal-qmsg style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft }}>{msg}</span>}
      </div>
    </div>
  );
}
function AdminReveal() {
  const cfg = useRevealCfg();
  const secret = useRevealDoc('revealSecret');
  const rstate = useRevealDoc('revealState');
  const [pw, setPw] = React.useState('');
  const [title, setTitle] = React.useState('');
  const [result, setResult] = React.useState('');
  const [code, setCode] = React.useState('');
  const [videoUrl, setVideoUrl] = React.useState('');
  const [peek, setPeek] = React.useState(false);
  const [init, setInit] = React.useState(false);
  const [initS, setInitS] = React.useState(false);
  const [msg, setMsg] = React.useState('');
  const [msgS, setMsgS] = React.useState('');
  const [ask, setAsk] = React.useState(false);
  const [clearing, setClearing] = React.useState(false);
  React.useEffect(() => { if (cfg.loaded && !init) { setPw((cfg.v && cfg.v.password) || ''); setTitle((cfg.v && cfg.v.title) || ''); setInit(true); } }, [cfg.loaded]);
  React.useEffect(() => { if (secret.loaded && !initS) { const s = secret.v || {}; setResult(s.result || ''); setCode(s.code || ''); setVideoUrl(s.videoUrl || ''); setInitS(true); } }, [secret.loaded]);
  const flash = (set, m) => { set(m); setTimeout(() => set(''), 2500); };
  const db = revealDb();
  const save = () => {
    if (!db) return;
    const v = cfg.v || {};
    // a vendég- és album-kulcs az első mentéskor keletkezik, utána változatlan
    db.collection('config').doc('revealConfig').set({ password: pw.trim(), title: title.trim(), guestKey: v.guestKey || revealKeyGen(), albumKey: v.albumKey || revealKeyGen() }, { merge:true })
      .then(() => flash(setMsg, 'Mentve ✓')).catch(e => flash(setMsg, 'Nem sikerült menteni (' + ((e && e.code) || 'hiba') + ')'));
  };
  const saveSecret = () => {
    if (!db) return;
    db.collection('config').doc('revealSecret').set({ result, code: code.trim(), videoUrl: videoUrl.trim() }, { merge:true })
      .then(() => flash(setMsgS, 'Mentve ✓')).catch(e => flash(setMsgS, 'Nem sikerült menteni (' + ((e && e.code) || 'hiba') + ')'));
  };
  const resetState = () => { if (db) db.collection('config').doc('revealState').set({ phase:'idle', run: revealToken(), at: Date.now() }).then(() => flash(setMsgS, 'Visszaállítva')).catch(() => {}); };
  const newKey = k => { if (db) db.collection('config').doc('revealConfig').set({ [k]: revealKeyGen() }, { merge:true }).then(() => flash(setMsg, 'Új link kész — a régi már nem működik')).catch(() => {}); };
  const downloadAlbum = () => {
    if (!db) return;
    db.collection('revealPhotos').get().then(snap => {
      const items = snap.docs.map(d => Object.assign({ id:d.id }, d.data()));
      const n = revealDownloadAlbum(items); flash(setMsg, `Album letöltve (${n} fájl)`);
    }).catch(() => flash(setMsg, 'Az album nem sikerült'));
  };
  const clearAll = () => {
    if (!db) return;
    setClearing(true); setAsk(false);
    const wipe = coll => db.collection(coll).get().then(snap => {
      const refs = snap.docs.map(d => d.ref);
      const chunks = []; for (let i = 0; i < refs.length; i += 400) chunks.push(refs.slice(i, i + 400));
      return chunks.reduce((p, ch) => p.then(() => { const b = db.batch(); ch.forEach(r => b.delete(r)); return b.commit(); }), Promise.resolve()).then(() => refs.length);
    });
    wipe('revealPhotos').then(n => wipe('revealQuizAns').then(() => n))
      .then(n => { setClearing(false); flash(setMsg, `${n} kép és üzenet törölve`); }).catch(() => { setClearing(false); flash(setMsg, 'Az ürítés nem sikerült'); });
  };
  const copy = t => { try { navigator.clipboard.writeText(t); flash(setMsg, 'Link kimásolva'); } catch(e) {} };
  const label = s => <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', margin:'12px 0 6px' }}>{s}</div>;
  const inpSt = { width:'100%', boxSizing:'border-box', padding:'12px', borderRadius:12, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none' };
  const box = { background:T.surface, borderRadius:16, padding:16, boxShadow:T.shadow };
  const h = s => <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>{s}</div>;
  const note = s => <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:4, lineHeight:1.45 }}>{s}</div>;
  const btn = (primary, extra) => Object.assign({ padding:'11px 16px', borderRadius:12, border: primary ? 'none' : `1.5px solid ${T.border}`, background: primary ? T.mint : 'transparent', color: primary ? '#fff' : T.inkSoft, fontFamily:T.font, fontWeight:900, fontSize:13, cursor:'pointer' }, extra || {});
  if (!cfg.loaded) return <div style={{ textAlign:'center', padding:32, color:T.sub, fontFamily:T.font }}>Betöltés…</div>;
  const st = rstate.v || {};
  const gUrl = revealGuestUrl(cfg.v), aUrl = revealAlbumUrl(cfg.v);
  const linkRow = (lab, url, k, data) => (
    <div style={{ marginTop:10 }}>
      {label(lab)}
      {url ? <div style={{ display:'flex', gap:8 }}>
        <input readOnly value={url} {...{ [data]: '' }} style={Object.assign({}, inpSt, { fontSize:12 })} />
        <button onClick={() => copy(url)} style={btn(false)}>Másol</button>
        <button onClick={() => newKey(k)} style={btn(false)}>Új</button>
      </div> : <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft }}>Az első mentéskor jön létre.</div>}
    </div>
  );
  return (
    <div data-admin-reveal style={{ padding:16, display:'flex', flexDirection:'column', gap:14 }}>
      <div style={box}>
        {h('Belépés és cím')}
        {note('Egy jelszó a vetítőnek és az operátornak is — minden megnyitáskor bekéri.')}
        {label('Jelszó')}
        <input data-admin-reveal-pw value={pw} onChange={e => setPw(e.target.value)} placeholder="pl. babavaro" style={inpSt} />
        {label('Cím (a vetítőn és a vendégoldalon)')}
        <input data-admin-reveal-title value={title} onChange={e => setTitle(e.target.value)} placeholder="Gender Reveal" style={inpSt} />
        <div style={{ display:'flex', alignItems:'center', gap:12, marginTop:14 }}>
          <button data-admin-reveal-save onClick={save} style={btn(true)}>Mentés</button>
          {msg && <span data-admin-reveal-msg style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft }}>{msg}</span>}
        </div>
        {linkRow('Vendég-link (a vetítő QR-kódja ezt mutatja)', gUrl, 'guestKey', 'data-admin-reveal-guesturl')}
        {linkRow('Galéria-link a szülőknek (csak nézhető)', aUrl, 'albumKey', 'data-admin-reveal-albumurl')}
      </div>
      <div data-admin-reveal-secret style={box}>
        {h('🎉 Leleplezés')}
        {note('Az eredményt csak itt látod. A leleplezést a „Leleplező" szerep indítja a saját kódjával — az operátor nem tudja elindítani.')}
        {label('Az eredmény')}
        <div style={{ display:'flex', gap:8, alignItems:'center' }}>
          {peek || !result ? ['boy', 'girl'].map(r => (
            <button key={r} data-admin-reveal-result={r} onClick={() => setResult(r)} style={btn(result === r, { flex:1, background: result === r ? REVEAL_RESULTS[r].c1 : 'transparent', border: result === r ? 'none' : `1.5px solid ${T.border}` })}>{REVEAL_RESULTS[r].emoji} {REVEAL_RESULTS[r].name}</button>
          )) : <div data-admin-reveal-masked style={{ flex:1, fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>●●● beállítva</div>}
          {result && <button data-admin-reveal-peek onClick={() => setPeek(p => !p)} style={btn(false)}>{peek ? 'Elrejt' : '👁 Mutat'}</button>}
        </div>
        {label('Leleplező kód (nem a közös jelszó)')}
        <input data-admin-reveal-code value={code} onChange={e => setCode(e.target.value)} placeholder="pl. 2026" style={inpSt} />
        {label('Videó-link (nem kötelező — közvetlen .mp4 link)')}
        <input data-admin-reveal-video value={videoUrl} onChange={e => setVideoUrl(e.target.value)} placeholder="https://…/leleplezes.mp4" style={inpSt} />
        {note('A videót a vetítő laptopjáról is be lehet tölteni (🎬 Videó gomb a vetítőn) — az biztosabb. Ha ott van betöltött videó, az megy a link helyett. Próbánál soha nincs videó.')}
        <div style={{ display:'flex', alignItems:'center', gap:12, marginTop:14, flexWrap:'wrap' }}>
          <button data-admin-reveal-secretsave onClick={saveSecret} style={btn(true)}>Mentés</button>
          <span data-admin-reveal-state style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft }}>Állapot: {st.phase === 'reveal' ? (st.test ? 'próba lefutott' : 'leleplezve 🎉') : 'még nem volt'}</span>
          {st.phase === 'reveal' && <button data-admin-reveal-reset onClick={resetState} style={btn(false)}>Visszaállítás</button>}
          {msgS && <span data-admin-reveal-msgs style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft }}>{msgS}</span>}
        </div>
      </div>
      <AdminRevealQuiz />
      <div style={box}>
        {h('📦 Album és ürítés')}
        {note('A buli után: töltsd le az albumot (minden jóváhagyott kép + a jókívánságok egy szövegfájlban), és csak UTÁNA ürítsd a képfolyamot.')}
        <div style={{ display:'flex', gap:10, marginTop:12, flexWrap:'wrap' }}>
          <button data-admin-reveal-zip onClick={downloadAlbum} style={btn(true)}>Album letöltése (ZIP)</button>
          <button data-admin-reveal-clear disabled={clearing} onClick={() => setAsk(true)} style={btn(false, { border:`1.5px solid ${T.coral}`, color:T.coral })}>{clearing ? 'Ürítés…' : 'Összes kép törlése'}</button>
        </div>
      </div>
      {ask && (
        <ActionModal kicker="Képfolyam ürítése" onClose={() => setAsk(false)} onSecondary={() => setAsk(false)} secondaryLabel="Mégse"
          onPrimary={clearAll} primaryLabel="Mind törlése" primaryColor={T.coral}>
          Minden képet, üzenetet és kvízválaszt törölsz. Letöltötted már az albumot? Ez nem vonható vissza.
        </ActionModal>
      )}
    </div>
  );
}

