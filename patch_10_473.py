# v10.473 — DNR Bingó: szettek (Foci VB / OTP Gála), korty-érték tételenként, kör-alapú jelölés,
# személyenkénti korty-összesítő + teli kártya, és a foci-beégetések kivezetése.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.472';", "const APP_VERSION = 'v10.473';")

# ── 1. szett-presetek a BINGO_ITEMS után ──
rep("""function bingoCardFor(pid, n) {""",
"""// v10.473: kész szettek. A tétel `k` mezője a korty (1–3): ennyit iszik, akinek a kártyáján
// rajta van, amikor megtörténik / elhangzik. A szett a cím, a fejléc-emoji és a középső
// (ingyen) mező is — a foci (DÖNTŐ, ⚽) innentől adat, nem kód.
const BINGO_FOCI_K = { 'Piros lap':2, 'Tizenegyes':2, 'Kapufa':2, 'Öngól':3, 'Csere gólt lő':2 };
const BINGO_PRESETS = {
  foci: { name:'Foci VB', title:'VB Bingó', titleEmoji:'⚽', center:{ e:'🏆', t:'DÖNTŐ' },
    items: BINGO_ITEMS.map(it => ({ e: it.e, t: it.t, k: BINGO_FOCI_K[it.t] || 1 })) },
  otp: { name:'OTP Gála', title:'OTP Gála Bingó', titleEmoji:'🎤', center:{ e:'🎤', t:'GÁLA' },
    items: [
      { e:'🙏', t:'Köszönöm', k:1 }, { e:'🤝', t:'Ügyfeleink', k:1 }, { e:'👥', t:'Csapat', k:1 },
      { e:'💡', t:'Innováció', k:2 }, { e:'📱', t:'Digitális', k:1 }, { e:'🌱', t:'Fenntartható', k:2 },
      { e:'🏘️', t:'Közösség', k:1 }, { e:'🧗', t:'Kihívás', k:1 }, { e:'🏆', t:'Siker', k:1 },
      { e:'🤲', t:'Bizalom', k:2 }, { e:'🔭', t:'Jövő', k:1 }, { e:'🎯', t:'Elkötelezett', k:2 },
      { e:'♟️', t:'Stratégia', k:2 }, { e:'📈', t:'Fejlődés', k:1 }, { e:'🔗', t:'Partnerség', k:2 },
      { e:'🚀', t:'Rekordév', k:3 }, { e:'🤖', t:'Mesterséges intelligencia', k:3 }, { e:'🦚', t:'Büszke vagyok', k:2 },
      { e:'🥂', t:'Közös siker', k:2 }, { e:'✨', t:'Ügyfélélmény', k:2 }, { e:'💎', t:'Értékteremtés', k:3 },
      { e:'📲', t:'Mobilbank', k:2 }, { e:'👏', t:'Taps beszéd közben', k:1 }, { e:'🖥️', t:'Elakad a prezentáció', k:3 },
    ] },
};
const bingoK = it => { const k = +((it || {}).k); return k >= 1 && k <= 3 ? Math.round(k) : 1; };
// A jelölések kör szerint: config/bingo.r_<kör>.<who> — új kör (szettváltás / „Új kör") = mindenki
// tiszta kártyával indul, a régi jelölések NEM csúsznak át más tételekre. Kör nélkül (régi config)
// a régi, felső szintű mezők élnek tovább.
function bingoMarkStore(marksAll, round) { return round ? ((marksAll && marksAll['r_' + round]) || {}) : (marksAll || {}); }
function bingoCardFor(pid, n) {""")

# ── 2. BingoScreen: tételek, középső mező, cím-emoji, kör ──
rep("""  const ITEMS = (cfg && Array.isArray(cfg.items) && cfg.items.length >= 24) ? cfg.items : BINGO_ITEMS;""",
"""  // ⚠️ v10.473: 1–23 tételnél NEM esik vissza csendben a foci-listára (egy rövidebb Gála-lista
  // mellett focis kártya jött volna) — ilyenkor a képernyő szól (`bingoTooFew`).
  const cfgItems = (cfg && Array.isArray(cfg.items)) ? cfg.items : [];
  const bingoTooFew = cfgItems.length > 0 && cfgItems.length < 24;
  const ITEMS = cfgItems.length >= 24 ? cfgItems : BINGO_PRESETS.foci.items;
  const bingoCenter = (cfg && cfg.center && cfg.center.t) ? cfg.center : BINGO_PRESETS.foci.center;
  const bingoEmoji = (cfg && typeof cfg.titleEmoji === 'string') ? cfg.titleEmoji : '⚽';
  const bingoRound = (cfg && cfg.bingoRound) || '';""")
rep("""  const headTitle = mode === 'torta' ? (tortaTitle + ' 🍽️') : (mode === 'tipp' ? tippTitle : bingoTitle) + (mode === 'tipp' ? ' 🎯' : ' ⚽');""",
    """  const headTitle = mode === 'torta' ? (tortaTitle + ' 🍽️') : (mode === 'tipp' ? (tippTitle + ' 🎯') : (bingoTitle + (bingoEmoji ? ' ' + bingoEmoji : '')));""")

# jelölések a kör tárolójából
rep("""  const myMarks = new Set(marksAll[who] || []);
  const persistMarks = arr => { if (db && who) db.collection('config').doc('bingo').set({ [who]: arr }, { merge: true }).catch(() => {}); };""",
"""  const markStore = bingoMarkStore(marksAll, bingoRound);
  const myMarks = new Set(markStore[who] || []);
  const putMarks = (prev, id, arr) => bingoRound
    ? Object.assign({}, prev, { ['r_' + bingoRound]: Object.assign({}, (prev && prev['r_' + bingoRound]) || {}, { [id]: arr }) })
    : Object.assign({}, prev, { [id]: arr });
  const persistMarks = arr => { if (db && who) db.collection('config').doc('bingo').set(bingoRound ? { ['r_' + bingoRound]: { [who]: arr } } : { [who]: arr }, { merge: true }).catch(() => {}); };""")
rep("""    const arr = Array.from(n).sort((a, b) => a - b);
    setMarksAll(prev => ({ ...prev, [who]: arr }));
    persistMarks(arr);""",
"""    const arr = Array.from(n).sort((a, b) => a - b);
    setMarksAll(prev => putMarks(prev, who, arr));
    persistMarks(arr);""")
rep("""{ if (confirmReset) { setMarksAll(prev => ({ ...prev, [who]: [] })); persistMarks([]);""",
    """{ if (confirmReset) { setMarksAll(prev => putMarks(prev, who, [])); persistMarks([]);""")

# korty + teli kártya
rep("""  const myBingos = (who && mode === 'bingo') ? bingosOf(myMarks) : 0;""",
"""  const myBingos = (who && mode === 'bingo') ? bingosOf(myMarks) : 0;
  // v10.473: korty — a megjelölt mezők tételeinek `k` összege (akinek a kártyáján van, az iszik)
  const sipsOf = (pid, set) => { const cd = bingoCardFor(pid, ITEMS.length); let t = 0; set.forEach(c => { if (c !== 12) { const it = ITEMS[cd[c < 12 ? c : c - 1]]; if (it) t += bingoK(it); } }); return t; };
  const myFull = (who && mode === 'bingo') ? myMarks.size >= 24 : false;
  const prevFull = React.useRef(null);
  React.useEffect(() => {
    if (!who || !loaded || mode !== 'bingo') return;
    if (prevFull.current === null) { prevFull.current = myFull; return; }
    if (myFull && !prevFull.current) setCelebrate('full');
    prevFull.current = myFull;
  }, [myFull, who, loaded, mode]);""")
rep("""  const bingoBoard = people
    .map(p => ({ p, n: (marksAll[p.id] || []).length, b: bingosOf(new Set(marksAll[p.id] || [])) }))
    .filter(x => x.n > 0)
    .sort((a, b) => (b.b - a.b) || (b.n - a.n));""",
"""  const bingoBoard = people
    .map(p => { const st = new Set(markStore[p.id] || []); return { p, n: st.size, b: bingosOf(st), k: sipsOf(p.id, st) }; })
    .filter(x => x.n > 0)
    .sort((a, b) => ((b.n >= 24) - (a.n >= 24)) || (b.b - a.b) || (b.n - a.n) || (b.k - a.k));""")
rep("""    if (myBingos > prevBingos.current) {
      setCelebrate(myBingos);""",
"""    if (myBingos > prevBingos.current && myMarks.size < 24) {
      setCelebrate(myBingos);""")

# picker szöveg: nem focis
rep("""    : 'Válaszd ki magad — mindenki saját kártyát kap, és X-elheti, ami a döntőben megtörténik.';""",
    """    : 'Válaszd ki magad — mindenki saját kártyát kap, és X-elheti, ami megtörténik vagy elhangzik.';""")

# a saját sáv: korty
rep("""<div style={{ fontFamily:T.font, fontWeight:700, fontSize:10.5, color:T.inkSoft }}>{myMarks.size}/24 kipipálva{myBingos ? ` · ${myBingos} bingó 🏆` : ''}</div>""",
    """<div data-bingo-mine style={{ fontFamily:T.font, fontWeight:700, fontSize:10.5, color:T.inkSoft }}>{myMarks.size}/24 kipipálva{myBingos ? ` · ${myBingos} bingó 🏆` : ''} · 🍺 <span data-bingo-mysips>{sipsOf(who, myMarks)}</span> korty{myFull ? ' · TELI KÁRTYA 🎉' : ''}</div>""")

# a mező: középső szett-mező + korty-jelvény
rep("""<span style={{ fontSize:15, lineHeight:1, opacity: on && !free ? 0.3 : 1 }}>{free ? '🏆' : item.e}</span>
                    <span style={{ fontFamily:T.font, fontWeight:800, fontSize:7.6, lineHeight:1.12, textAlign:'center', color: free ? '#1A2A4A' : on ? 'rgba(255,255,255,0.6)' : T.ink, wordBreak:'break-word' }}>{free ? 'DÖNTŐ' : item.t}</span>""",
"""<span style={{ fontSize:15, lineHeight:1, opacity: on && !free ? 0.3 : 1 }}>{free ? bingoCenter.e : item.e}</span>
                    <span style={{ fontFamily:T.font, fontWeight:800, fontSize:7.6, lineHeight:1.12, textAlign:'center', color: free ? '#1A2A4A' : on ? 'rgba(255,255,255,0.6)' : T.ink, wordBreak:'break-word' }}>{free ? bingoCenter.t : item.t}</span>
                    {!free && <span data-bingo-k={bingoK(item)} style={{ position:'absolute', top:3, right:4, fontFamily:T.font, fontWeight:900, fontSize:8.5, lineHeight:1, color: on ? 'rgba(255,255,255,0.75)' : (bingoK(item) >= 3 ? T.coral : T.inkSoft) }}>{'🍺' + bingoK(item)}</span>}""")
rep("""Koppints a mezőre, ha megtörtént — teljes sor, oszlop vagy átló = BINGÓ! 🍻</div>""",
    """Koppints a mezőre, ha megtörtént / elhangzott, és idd meg a sarkában álló kortyot (🍺1–3). Teljes sor, oszlop vagy átló = BINGÓ — a teli kártya a csúcs! 🍻</div>""")

# Állás: korty + teli kártya
rep("""                  {bingoBoard.map(({ p, n, b }) => (
                    <div key={p.id} style={{ display:'flex', alignItems:'center', gap:8 }}>""",
"""                  {bingoBoard.map(({ p, n, b, k }) => (
                    <div key={p.id} data-bingo-row={p.id} style={{ display:'flex', alignItems:'center', gap:8 }}>""")
rep("""                      {b > 0 && <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11.5, color:T.coral }}>{b}× BINGÓ 🏆</span>}
                      <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11.5, color:T.inkSoft }}>{n}/24</span>""",
"""                      {n >= 24 ? <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11.5, color:T.coral }}>TELI 🎉</span>
                        : b > 0 && <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11.5, color:T.coral }}>{b}× BINGÓ 🏆</span>}
                      <span data-bingo-sips style={{ fontFamily:T.font, fontWeight:900, fontSize:11.5, color:T.ink }}>🍺 {k}</span>
                      <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11.5, color:T.inkSoft }}>{n}/24</span>""")

# ünneplés: teli kártya
rep("""            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:30, color:T.ink, letterSpacing:'0.04em' }}>BINGÓ! 🏆</div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13.5, color:T.inkSoft, textAlign:'center' }}>{celebrate}. sorod jött össze — ezt meg kell ünnepelni! 🍻</div>""",
"""            <div data-bingo-celebrate={celebrate} style={{ fontFamily:T.font, fontWeight:900, fontSize:30, color:T.ink, letterSpacing:'0.04em' }}>{celebrate === 'full' ? 'TELI KÁRTYA! 🎉' : 'BINGÓ! 🏆'}</div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13.5, color:T.inkSoft, textAlign:'center' }}>{celebrate === 'full' ? 'Minden mező kipipálva — összegyűjtötted az egészet!' : celebrate + '. sorod jött össze — ezt meg kell ünnepelni!'} 🍻</div>""")

# kevés tétel: a kártya helyett üzenet (a Bingó ága elején)
rep("""          <React.Fragment>
            {/* Saját sáv */}
            <div style={{ display:'flex', alignItems:'center', gap:9, marginBottom:12 }}>
              <Avatar pr={whoProf} size={30} />
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13.5, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{(whoProf && whoProf.name) || '—'} kártyája</div>""",
"""          bingoTooFew ? (
            <div data-bingo-toofew style={{ background:T.surface, borderRadius:18, padding:'22px 18px', boxShadow:T.shadow, textAlign:'center', fontFamily:T.font }}>
              <div style={{ fontWeight:900, fontSize:16, color:T.ink, marginBottom:6 }}>Még nincs kész a kártya</div>
              <div style={{ fontWeight:700, fontSize:13, color:T.inkSoft, lineHeight:1.5 }}>A szettben {cfgItems.length} tétel van, a kártyához legalább 24 kell. Az admin az Admin → DNR Bingó fülön pótolhatja.</div>
            </div>
          ) : <React.Fragment>
            {/* Saját sáv */}
            <div style={{ display:'flex', alignItems:'center', gap:9, marginBottom:12 }}>
              <Avatar pr={whoProf} size={30} />
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13.5, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{(whoProf && whoProf.name) || '—'} kártyája</div>""")


# ── 3. AdminBingo: szett-állapot ──
rep("""  const [legacy, setLegacy] = React.useState({ enabled: true, mode: 'bingo' });
  const [title, setTitle] = React.useState('VB Bingó');
  const [items, setItems] = React.useState(null);""",
"""  const [legacy, setLegacy] = React.useState({ enabled: true, mode: 'bingo' });
  const [title, setTitle] = React.useState('VB Bingó');
  const [items, setItems] = React.useState(null);
  // v10.473: Bingó-szettek. Az AKTÍV szett mezői (title/titleEmoji/center/items) a config felső
  // szintjén ülnek (a képernyő ezt olvassa), a mentett szettek a `bingoSets`-ben.
  const [titleEmoji, setTitleEmoji] = React.useState('⚽');
  const [center, setCenter] = React.useState(BINGO_PRESETS.foci.center);
  const [setId, setSetId] = React.useState('foci');
  const [sets, setSets] = React.useState({});
  const [round, setRound] = React.useState('');
  const [askSet, setAskSet] = React.useState(null);   // váltás / új kör megerősítése""")
rep("""      setItems((c && Array.isArray(c.items) && c.items.length) ? c.items.map(it => ({ e: it.e || '', t: it.t || '' })) : BINGO_ITEMS.map(it => ({ e: it.e, t: it.t })));
    }).catch(() => { setItems(BINGO_ITEMS.map(it => ({ e: it.e, t: it.t }))); });""",
"""      setItems((c && Array.isArray(c.items) && c.items.length) ? c.items.map(it => ({ e: it.e || '', t: it.t || '', k: bingoK(it) })) : BINGO_PRESETS.foci.items.map(it => ({ ...it })));
      setTitleEmoji((c && typeof c.titleEmoji === 'string') ? c.titleEmoji : '⚽');
      setCenter((c && c.center && c.center.t) ? { e: c.center.e || '', t: c.center.t } : BINGO_PRESETS.foci.center);
      setSetId((c && c.bingoSetId) || 'foci');
      setSets((c && c.bingoSets && typeof c.bingoSets === 'object') ? c.bingoSets : {});
      setRound((c && c.bingoRound) || '');
    }).catch(() => { setItems(BINGO_PRESETS.foci.items.map(it => ({ ...it }))); });""")
rep("""  const addItem = () => { setItems(l => [...l, { e: '⚽', t: '' }]); markDirty(); };""",
    """  const addItem = () => { setItems(l => [...l, { e: '⭐', t: '', k: 1 }]); markDirty(); };""")
rep("""    const cleanItems = (items || []).map(w => ({ e: (w.e || '').trim() || '⚽', t: (w.t || '').trim() })).filter(w => w.t);""",
    """    const cleanItems = (items || []).map(w => ({ e: (w.e || '').trim() || '⭐', t: (w.t || '').trim(), k: bingoK(w) })).filter(w => w.t);
    const cleanCenter = { e: (center.e || '').trim(), t: (center.t || '').trim() || 'BINGÓ' };
    const bTitle = (title || '').trim() || 'Bingó';
    // a mostani szett mentett másolata — szettváltás után innen jön vissza
    const nextSets = Object.assign({}, sets, { [setId]: { name: ((sets[setId] && sets[setId].name) || (BINGO_PRESETS[setId] && BINGO_PRESETS[setId].name) || bTitle), title: bTitle, titleEmoji: (titleEmoji || '').trim(), center: cleanCenter, items: cleanItems } });""")
rep("""title: (title || '').trim() || 'VB Bingó', items: cleanItems,""",
    """title: bTitle, items: cleanItems, titleEmoji: (titleEmoji || '').trim(), center: cleanCenter, bingoSetId: setId, bingoSets: nextSets, bingoRound: round,""")

# szettváltás és új kör — azonnal ment
rep("""  // Alaphelyzet CSAK az adott app adatait nullázza (v10.419)""",
"""  // v10.473: szettváltás — a mostanit elmenti a bingoSets-be, a célt onnan (vagy a presetből)
  // tölti, és ÚJ KÖRT indít: mindenki tiszta kártyát kap (a jelölések a kör alatt ülnek).
  const newRound = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 5);
  const switchSet = id => {
    const cur = buildPayload({});
    const src = (cur.bingoSets[id]) || BINGO_PRESETS[id];
    if (!src) return;
    const nr = newRound();
    setSets(cur.bingoSets); setSetId(id); setRound(nr);
    setTitle(src.title); setTitleEmoji(src.titleEmoji || ''); setCenter(src.center || BINGO_PRESETS.foci.center);
    setItems((src.items || []).map(it => ({ e: it.e || '', t: it.t || '', k: bingoK(it) })));
    persist(Object.assign({}, cur, { bingoSetId: id, bingoRound: nr, title: src.title, titleEmoji: src.titleEmoji || '', center: src.center || BINGO_PRESETS.foci.center, items: (src.items || []).map(it => ({ e: it.e, t: it.t, k: bingoK(it) })) }));
  };
  const startNewRound = () => { const nr = newRound(); setRound(nr); persist(buildPayload({ bingoRound: nr })); };
  // Alaphelyzet CSAK az adott app adatait nullázza (v10.419)""")
rep("""      const d = BINGO_ITEMS.map(it => ({ e: it.e, t: it.t }));
      setTitle('VB Bingó'); setItems(d);
      over = { title: 'VB Bingó', items: d };""",
"""      const d = BINGO_PRESETS.foci.items.map(it => ({ ...it }));
      const nr = newRound();
      setTitle('VB Bingó'); setItems(d); setTitleEmoji('⚽'); setCenter(BINGO_PRESETS.foci.center); setSetId('foci'); setRound(nr);
      over = { title: 'VB Bingó', items: d, titleEmoji: '⚽', center: BINGO_PRESETS.foci.center, bingoSetId: 'foci', bingoRound: nr };""")

# ── 4. Admin felület ──
rep("""          <div style={{ fontFamily:T.font, fontSize:12.5, color:T.sub, marginBottom:12 }}>A kártya 24 mezőt sorsol ki (középen fix DÖNTŐ), ezért legalább 24 mező kell""",
"""          {/* v10.473: szettek — egy koppintás, és mindenki az új szett tiszta kártyáját kapja */}
          <div data-bingo-sets style={{ background:T.surface, borderRadius:14, padding:'12px 14px', boxShadow:T.shadow, marginBottom:12 }}>
            {lbl('Szett')}
            <div style={{ display:'flex', flexWrap:'wrap', gap:7 }}>
              {Array.from(new Set(Object.keys(BINGO_PRESETS).concat(Object.keys(sets)))).map(id => {
                const nm = (sets[id] && sets[id].name) || (BINGO_PRESETS[id] && BINGO_PRESETS[id].name) || id;
                const on = id === setId;
                return <button key={id} data-bingo-set={id} aria-pressed={on} onClick={() => { if (!on) setAskSet({ kind:'set', id, name: nm }); }}
                  style={{ padding:'9px 14px', borderRadius:999, border: on ? 'none' : `1.5px solid ${T.border}`, background: on ? T.mint : 'transparent', color: on ? '#fff' : T.ink, fontFamily:T.font, fontWeight:800, fontSize:13.5, cursor: on ? 'default' : 'pointer' }}>{nm}</button>;
              })}
            </div>
            <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:9, lineHeight:1.45 }}>Váltáskor a mostani szett elmentődik, és mindenki tiszta kártyával indul. A szettek bármikor visszaválthatók.</div>
            <button data-bingo-newround onClick={() => setAskSet({ kind:'round' })} style={{ marginTop:10, padding:'9px 14px', borderRadius:10, border:`1.5px solid ${T.border}`, background:'transparent', color:T.ink, fontFamily:T.font, fontWeight:800, fontSize:13, cursor:'pointer' }}>Új kör — mindenki jelölése nullázódik</button>
          </div>
          {askSet && (
            <ActionModal kicker={askSet.kind === 'set' ? 'Szettváltás: ' + askSet.name : 'Új kör indul'} onClose={() => setAskSet(null)} onSecondary={() => setAskSet(null)} secondaryLabel="Mégse"
              onPrimary={() => { const a = askSet; setAskSet(null); if (a.kind === 'set') switchSet(a.id); else startNewRound(); }} primaryLabel={askSet.kind === 'set' ? 'Váltás' : 'Új kör'} primaryColor={T.mint}>
              Mindenki jelölése nullázódik, és tiszta kártyával indul.{askSet.kind === 'set' ? ' A mostani szett (a szerkesztéseiddel együtt) elmentődik.' : ''}
            </ActionModal>
          )}
          <div style={{ fontFamily:T.font, fontSize:12.5, color:T.sub, marginBottom:12 }}>A kártya 24 mezőt sorsol ki (a közepe az ingyen mező), ezért legalább 24 mező kell""")
rep("""            {lbl('Cím / tematika')}
            <input value={title} onChange={e => { setTitle(e.target.value); markDirty(); }} placeholder="VB Bingó" style={{ ...inpS, width:'100%' }} />""",
"""            {lbl('Cím / tematika')}
            <div style={{ display:'flex', gap:7 }}>
              <input data-bingo-titleemoji value={titleEmoji} onChange={e => { setTitleEmoji(e.target.value); markDirty(); }} placeholder="⚽" aria-label="Cím emoji" style={{ ...inpS, width:52, textAlign:'center', fontSize:17, padding:'8px 4px', flexShrink:0 }} />
              <input value={title} onChange={e => { setTitle(e.target.value); markDirty(); }} placeholder="VB Bingó" style={{ ...inpS, flex:1, minWidth:0 }} />
            </div>
            <div style={{ marginTop:12 }}>{lbl('Középső (ingyen) mező')}</div>
            <div style={{ display:'flex', gap:7 }}>
              <input value={center.e} onChange={e => { setCenter(c => ({ ...c, e: e.target.value })); markDirty(); }} placeholder="🏆" aria-label="Középső mező emoji" style={{ ...inpS, width:52, textAlign:'center', fontSize:17, padding:'8px 4px', flexShrink:0 }} />
              <input data-bingo-centertext value={center.t} onChange={e => { setCenter(c => ({ ...c, t: e.target.value })); markDirty(); }} placeholder="DÖNTŐ" maxLength={12} style={{ ...inpS, flex:1, minWidth:0 }} />
            </div>""")
rep("""                <input value={w.t} onChange={e => updItem(i, 't', e.target.value)} placeholder="Esemény szövege…" style={{ ...inpS, flex:1, minWidth:0, border:`1.5px solid ${(w.t||'').trim() ? T.border : T.coral}` }} />""",
"""                <input value={w.t} onChange={e => updItem(i, 't', e.target.value)} placeholder="Szó / esemény…" style={{ ...inpS, flex:1, minWidth:0, border:`1.5px solid ${(w.t||'').trim() ? T.border : T.coral}` }} />
                {/* v10.473: korty — ennyit iszik, akinek a kártyáján rajta van */}
                <button data-bingo-item-k={i} onClick={() => updItem(i, 'k', bingoK(w) % 3 + 1)} aria-label={'Korty: ' + bingoK(w)} title="Korty (koppintás: 1 → 2 → 3)"
                  style={{ flexShrink:0, minWidth:46, height:36, borderRadius:9, border:`1.5px solid ${T.border}`, background: bingoK(w) >= 3 ? T.coralSoft : T.bg, color: bingoK(w) >= 3 ? T.coral : T.ink, fontFamily:T.font, fontWeight:900, fontSize:13, cursor:'pointer' }}>🍺{bingoK(w)}</button>""")


# ── 5. rugalmas kártyaméret: 24+ tétel → 5×5 (középen ingyen mező), 16–23 → 4×4 (nincs ingyen mező) ──
rep("""const bingoK = it => {""",
"""// v10.473: a kártya mérete a tételek számából jön — a tulajdonos OTP Gála listája 18 szavas.
// 24+ → 5×5, középen az ingyen mező (24 kisorsolt tétel) · 16–23 → 4×4, ingyen mező NÉLKÜL
// (16 kisorsolt tétel) · 16 alatt nincs kártya. Mindenki a teljes listából kap véletlen
// (de a saját azonosítójából stabil) válogatást, így a kártyák különböznek.
function bingoGridOf(n) { return n >= 24 ? { s:5, free:12, need:24 } : n >= 16 ? { s:4, free:-1, need:16 } : null; }
function bingoLinesOf(sz) {
  const L = [], r5 = Array.from({ length: sz }, (_, i) => i);
  for (let r = 0; r < sz; r++) L.push(r5.map(c => r * sz + c));
  for (let c = 0; c < sz; c++) L.push(r5.map(r => r * sz + c));
  L.push(r5.map(i => i * sz + i)); L.push(r5.map(i => i * sz + (sz - 1 - i)));
  return L;
}
const bingoItemIdx = (g, card, c) => card[g.free >= 0 && c > g.free ? c - 1 : c];
const bingoK = it => {""")
rep("""  const bingoTooFew = cfgItems.length > 0 && cfgItems.length < 24;
  const ITEMS = cfgItems.length >= 24 ? cfgItems : BINGO_PRESETS.foci.items;""",
"""  const bingoTooFew = cfgItems.length > 0 && cfgItems.length < 16;
  const ITEMS = cfgItems.length >= 16 ? cfgItems : BINGO_PRESETS.foci.items;
  const grid = bingoGridOf(ITEMS.length);
  const gridLines = bingoLinesOf(grid.s);""")
rep("""    if (c === 12 || !who) return;""", """    if (c === grid.free || !who) return;""")
rep("""  const bingosOf = set => BINGO_LINES.filter(l => l.every(c => c === 12 || set.has(c))).length;""",
    """  const bingosOf = set => gridLines.filter(l => l.every(c => c === grid.free || set.has(c))).length;""")
rep("""set.forEach(c => { if (c !== 12) { const it = ITEMS[cd[c < 12 ? c : c - 1]]; if (it) t += bingoK(it); } }); return t; };
  const myFull = (who && mode === 'bingo') ? myMarks.size >= 24 : false;""",
"""set.forEach(c => { if (c !== grid.free && c < grid.s * grid.s) { const it = ITEMS[bingoItemIdx(grid, cd, c)]; if (it) t += bingoK(it); } }); return t; };
  const myFull = (who && mode === 'bingo') ? myMarks.size >= grid.need : false;""")
rep("""    if (myBingos > prevBingos.current && myMarks.size < 24) {""", """    if (myBingos > prevBingos.current && myMarks.size < grid.need) {""")
rep("""    .sort((a, b) => ((b.n >= 24) - (a.n >= 24)) || (b.b - a.b) || (b.n - a.n) || (b.k - a.k));""",
    """    .sort((a, b) => ((b.n >= grid.need) - (a.n >= grid.need)) || (b.b - a.b) || (b.n - a.n) || (b.k - a.k));""")
rep("""A szettben {cfgItems.length} tétel van, a kártyához legalább 24 kell.""", """A szettben {cfgItems.length} tétel van, a kártyához legalább 16 kell.""")
rep("""{myMarks.size}/24 kipipálva""", """{myMarks.size}/{grid.need} kipipálva""")
rep("""                      {n >= 24 ? <span""", """                      {n >= grid.need ? <span""")
rep("""<span style={{ fontFamily:T.font, fontWeight:800, fontSize:11.5, color:T.inkSoft }}>{n}/24</span>""",
    """<span style={{ fontFamily:T.font, fontWeight:800, fontSize:11.5, color:T.inkSoft }}>{n}/{grid.need}</span>""")
rep("""            <div style={{ display:'grid', gridTemplateColumns:'repeat(5, 1fr)', gap:6 }}>
              {Array.from({ length: 25 }).map((_, c) => {
                const free = c === 12;
                const item = free ? null : ITEMS[card[c < 12 ? c : c - 1]];""",
"""            <div data-bingo-grid={grid.s} style={{ display:'grid', gridTemplateColumns:`repeat(${grid.s}, 1fr)`, gap:6 }}>
              {Array.from({ length: grid.s * grid.s }).map((_, c) => {
                const free = c === grid.free;
                const item = free ? null : ITEMS[bingoItemIdx(grid, card, c)];""")
# 4×4-en nagyobb a mező — nagyobb betű
rep("""<span style={{ fontFamily:T.font, fontWeight:800, fontSize:7.6, lineHeight:1.12, textAlign:'center', color: free ? '#1A2A4A' : on ? 'rgba(255,255,255,0.6)' : T.ink, wordBreak:'break-word' }}>{free ? bingoCenter.t : item.t}</span>""",
    """<span style={{ fontFamily:T.font, fontWeight:800, fontSize: grid.s === 4 ? 10 : 7.6, lineHeight:1.12, textAlign:'center', color: free ? '#1A2A4A' : on ? 'rgba(255,255,255,0.6)' : T.ink, wordBreak:'break-word' }}>{free ? bingoCenter.t : item.t}</span>""")
rep("""<span style={{ fontSize:15, lineHeight:1, opacity: on && !free ? 0.3 : 1 }}>{free ? bingoCenter.e : item.e}</span>""",
    """<span style={{ fontSize: grid.s === 4 ? 20 : 15, lineHeight:1, opacity: on && !free ? 0.3 : 1 }}>{free ? bingoCenter.e : item.e}</span>""")

# admin: 16 a minimum, és kiírja, mekkora kártya lesz
rep("""  const tooFew = validCount < 24;""", """  const tooFew = validCount < 16;""")
rep("""          <div style={{ fontFamily:T.font, fontSize:12.5, color:T.sub, marginBottom:12 }}>A kártya 24 mezőt sorsol ki (a közepe az ingyen mező), ezért legalább 24 mező kell""",
    """          <div data-bingo-gridnote style={{ fontFamily:T.font, fontWeight:800, fontSize:12.5, color:T.ink, marginBottom:6 }}>{validCount >= 24 ? `${validCount} tétel → 5×5-ös kártya (24 sorsolt mező + ingyen közép)` : validCount >= 16 ? `${validCount} tétel → 4×4-es kártya (16 sorsolt mező, nincs ingyen közép)` : `${validCount} tétel — kártyához legalább 16 kell`}</div>
          <div style={{ fontFamily:T.font, fontSize:12.5, color:T.sub, marginBottom:12 }}>24 tételtől 5×5-ös, 16–23 tételnél 4×4-es kártya jár; mindenki a listából kap saját válogatást""")
rep("""Legalább 24 mező kell — jelenleg""", """Legalább 16 mező kell — jelenleg""")

# ── 6. a tulajdonos OTP Gála listája (18 szó, a küldött táblázat szerint) ──
import re
start = s.index("  otp: { name:'OTP Gála',")
end = s.index("    ] },\n};", start) + len("    ] },\n")
s = s[:start] + """  otp: { name:'OTP Gála', title:'OTP Gála Bingó', titleEmoji:'🎤', center:{ e:'🎤', t:'GÁLA' },
    items: [
      { e:'💻', t:'Digitális bankolás', k:1 }, { e:'🌱', t:'Fenntartható növekedés', k:3 }, { e:'🤝', t:'Ügyfeleinkért', k:2 },
      { e:'🥇', t:'Piacvezető', k:2 }, { e:'💡', t:'Innováció', k:1 }, { e:'♻️', t:'Fenntarthatóság', k:3 },
      { e:'🔄', t:'Digitális transzformáció', k:2 }, { e:'✨', t:'Ügyfélélmény', k:1 }, { e:'💰', t:'Bonusz', k:1 },
      { e:'💳', t:'Revolut', k:3 }, { e:'📈', t:'Rekord bevétel', k:2 }, { e:'🏘️', t:'Közösség', k:2 },
      { e:'⭐', t:'Prime', k:1 }, { e:'🧗', t:'Kihívás', k:1 }, { e:'🌍', t:'Külföldi ország', k:1 },
      { e:'🤖', t:'Technológia', k:2 }, { e:'🏦', t:'Bankfiók', k:1 }, { e:'🙊', t:'Elszólás', k:2 },
    ] },
""" + s[end:]

# 4×4: a leghosszabb szó szabja a betűméretet
rep("""fontSize: grid.s === 4 ? 10 : 7.6, lineHeight:1.12""", """fontSize: grid.s === 4 ? bingoCellFont(free ? bingoCenter.t : item.t) : 7.6, lineHeight:1.12""")
rep("""const bingoItemIdx = (g, card, c) =>""", """// 4×4-en a leghosszabb SZÓ szabja a betűméretet — egy hosszú szó („Fenntarthatóság") különben a mező
// közepén kettétörne
const bingoCellFont = t => { const w = Math.max(0, ...String(t || '').split(/\\s+/).map(x => x.length)); return w > 13 ? 8.2 : w > 11 ? 9 : 10; };
const bingoItemIdx = (g, card, c) =>""")
open(P, 'w', encoding='utf-8').write(s)
print('ok')
