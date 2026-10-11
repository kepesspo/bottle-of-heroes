# v10.419 — a Bingó, a Tippbajnokság és a DNR a tortán KÜLÖN appok
# (közös mechanika és közös config/bingoConfig doksi, de külön képernyő, ikon,
# láthatóság, admin-fül, deep-link és manifest).
import re
P = 'app.src.html'
s = open(P, encoding='utf-8').read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:120])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.418'", "const APP_VERSION = 'v10.419'")

# ── <head>: alias, ikon, manifest, cím, korai cím ──
rep("bingo:'bingo', events:'events',",
    "bingo:'bingo', tipp:'tipp', tippbajnoksag:'tipp', tippjatek:'tipp', torta:'torta', tortan:'torta', dnratortan:'torta',\n        events:'events',")
rep("""    var isBingo=q.indexOf('screen=bingo')!==-1;
    var isLiga=q.indexOf('screen=liga')!==-1;""",
"""    var isBingo=q.indexOf('screen=bingo')!==-1;
    var isTipp=q.indexOf('screen=tipp')!==-1;
    var isTorta=q.indexOf('screen=torta')!==-1;
    var isLiga=q.indexOf('screen=liga')!==-1;""")
rep("""    } else if(isBingo){""",
"""    } else if(isTipp){
      document.write('<link rel="apple-touch-icon" sizes="1024x1024" href="assets/dnr_tipp_icon.png"/>');
      document.write('<link rel="icon" type="image/png" sizes="512x512" href="assets/dnr_tipp_icon.png"/>');
    } else if(isTorta){
      document.write('<link rel="apple-touch-icon" sizes="1024x1024" href="assets/dnr_torta_icon.png"/>');
      document.write('<link rel="icon" type="image/png" sizes="512x512" href="assets/dnr_torta_icon.png"/>');
    } else if(isBingo){""")
rep("""if(localStorage.getItem('boh_bingo_mode')==='torta') _bIco='assets/dnr_torta_logo.png';""",
    """var _lm=localStorage.getItem('boh_bingo_mode'); if(_lm==='torta') _bIco='assets/dnr_torta_icon.png'; else if(_lm==='tipp') _bIco='assets/dnr_tipp_icon.png';""")
# manifest + apple title (két egysoros szkript)
rep("var bg=q.indexOf('screen=bingo')!==-1;var lg=q.indexOf('screen=liga')!==-1;document.write('<link rel=\"manifest\"",
    "var bg=q.indexOf('screen=bingo')!==-1;var tp=q.indexOf('screen=tipp')!==-1;var tt=q.indexOf('screen=torta')!==-1;var lg=q.indexOf('screen=liga')!==-1;document.write('<link rel=\"manifest\"")
rep("bar?'manifest-bar.json':bg?'manifest-bingo.json'", "bar?'manifest-bar.json':tp?'manifest-tipp.json':tt?'manifest-torta.json':bg?'manifest-bingo.json'")
rep("var bg=q.indexOf('screen=bingo')!==-1;var lg=q.indexOf('screen=liga')!==-1;document.write('<meta name=\"apple-mobile-web-app-title\"",
    "var bg=q.indexOf('screen=bingo')!==-1;var tp=q.indexOf('screen=tipp')!==-1;var tt=q.indexOf('screen=torta')!==-1;var lg=q.indexOf('screen=liga')!==-1;document.write('<meta name=\"apple-mobile-web-app-title\"")
rep("bar?'DNR Pub':bg?'DNR Bingó'", "bar?'DNR Pub':tp?'DNR Tipp':tt?'DNR a tortán':bg?'DNR Bingó'")
rep("""      } else if (location.search.indexOf('screen=bingo') !== -1) {
        document.title = 'DNR Bingó';""",
"""      } else if (location.search.indexOf('screen=tipp') !== -1) {
        document.title = 'DNR Tipp';
        var mtp = document.querySelector('meta[name="apple-mobile-web-app-title"]');
        if (mtp) mtp.setAttribute('content', 'DNR Tipp');
      } else if (location.search.indexOf('screen=torta') !== -1) {
        document.title = 'DNR a tortán';
        var mtt = document.querySelector('meta[name="apple-mobile-web-app-title"]');
        if (mtt) mtt.setAttribute('content', 'DNR a tortán');
      } else if (location.search.indexOf('screen=bingo') !== -1) {
        document.title = 'DNR Bingó';""")

# ── splash: saját nyitókép a két új appnak ──
rep("""    else if(q.indexOf('screen=bingo')!==-1){
      var _bm=null,_bt=null; try{_bm=localStorage.getItem('boh_bingo_mode');_bt=localStorage.getItem('boh_torta_title');}catch(e){}
      brand=_bm==='torta'
        ? {icon:'assets/dnr_torta_logo.png', title:_bt||'DNR a tortán', tag:'Főz. Vendégül lát. Pontoz.'}
        : {icon:'assets/dnr_bingo_icon.png', title:'DNR Bingó', tag:'Meccs. Buli. Tele.'};
    }""",
"""    else if(q.indexOf('screen=tipp')!==-1||q.indexOf('screen=torta')!==-1||q.indexOf('screen=bingo')!==-1){
      // v10.419: három külön app. A ?screen=bingo csak egy RÉGI, még Tortán/Tipp
      // módban telepített ikonnál mutat mást (boh_bingo_mode = ahova a régi link visz).
      var _bm=null,_bt=null,_tt=null; try{_bm=localStorage.getItem('boh_bingo_mode');_bt=localStorage.getItem('boh_torta_title');_tt=localStorage.getItem('boh_tipp_title');}catch(e){}
      var _k=q.indexOf('screen=tipp')!==-1?'tipp':q.indexOf('screen=torta')!==-1?'torta':(_bm==='torta'||_bm==='tipp')?_bm:'bingo';
      brand=_k==='torta'
        ? {icon:'assets/dnr_torta_logo.png', title:_bt||'DNR a tortán', tag:'Főz. Vendégül lát. Pontoz.'}
        : _k==='tipp'
        ? {icon:'assets/dnr_tipp_icon.png', title:'DNR Tipp', tag:_tt||'Tippelj. Találj. Nyerj.'}
        : {icon:'assets/dnr_bingo_icon.png', title:'DNR Bingó', tag:'Meccs. Buli. Tele.'};
    }""")

# ── Admin: három külön fül ──
rep("['xp','XP & Szint'],['bingo','Bingó'],", "['xp','XP & Szint'],['bingo','Bingó'],['tipp','Tipp'],['torta','Tortán'],")
rep("        {tab === 'bingo' && <AdminBingo />}",
    "        {tab === 'bingo' && <AdminBingo key=\"bingo\" app=\"bingo\" />}\n        {tab === 'tipp'  && <AdminBingo key=\"tipp\"  app=\"tipp\" />}\n        {tab === 'torta' && <AdminBingo key=\"torta\" app=\"torta\" />}")
rep("{ key: 'bingo', label: 'DNR Bingó' }, { key: 'liga', label: 'DNR Liga' },",
    "{ key: 'bingo', label: 'DNR Bingó' }, { key: 'tipp', label: 'DNR Tipp' },\n    { key: 'torta', label: 'DNR a tortán' }, { key: 'liga', label: 'DNR Liga' },")

# ── AdminBingo: a mód RÖGZÍTETT (az app), a láthatóság appokra bontva ──
rep("""function AdminBingo() {
  const [enabled, setEnabled] = React.useState(true);
  const [mode, setMode] = React.useState('bingo');""",
"""function AdminBingo({ app }) {
  // v10.419: a három app (Bingó / Tipp / Tortán) KÜLÖN admin-fület kap — a mód
  // rögzített, nincs többé mód-váltó. A config doksi közös (config/bingoConfig).
  const mode = BINGO_APP_KEYS.includes(app) ? app : 'bingo';
  const [enabled, setEnabled] = React.useState(true);
  const [apps, setApps] = React.useState(null);        // materializált { bingo, tipp, torta } láthatóság
  const [legacy, setLegacy] = React.useState({ enabled: true, mode: 'bingo' });""")
rep("""      setEnabled(c ? c.enabled !== false : true);
      setMode((c && (c.mode === 'tipp' || c.mode === 'torta')) ? c.mode : 'bingo');""",
"""      const ap = bingoAppsOf(c);
      setApps(ap); setEnabled(ap[mode]);
      setLegacy({ enabled: c ? c.enabled !== false : true, mode: bingoLegacyMode(c) });""")
rep("""    return Object.assign({ enabled, mode, title:""",
    """    return Object.assign({ enabled: legacy.enabled, mode: legacy.mode, apps: apps || bingoAppsOf(null), title:""")
rep("""  const reset = () => {
    const d = BINGO_ITEMS.map(it => ({ e: it.e, t: it.t }));
    setEnabled(true); setMode('bingo'); setTitle('VB Bingó'); setItems(d); setTippTitle('Tippbajnokság'); setTippRequireCode(false); setMatches([]); setTeamsText(''); setBWinner({ enabled:false, deadline:'', correct:'' }); setBScorer({ enabled:false, deadline:'', correct:'' });
    setTortaTitle('DNR a tortán'); setTortaTeams([]); setTortaEvenings([]);
    persist({ enabled: true, mode: 'bingo', title: 'VB Bingó', items: d, tippTitle: 'Tippbajnokság', tippRequireCode: false, tippMailUrl: (tippMailUrl || '').trim(), teams: [], matches: [], bonusWinner: { enabled:false }, bonusScorer: { enabled:false }, questions: [], tortaTitle: 'DNR a tortán', tortaTeams: [], tortaEvenings: [] });
  };""",
"""  // Alaphelyzet CSAK az adott app adatait nullázza (v10.419) — a Bingó fülön nyomott
  // gomb nem törölheti a Tortán csapatait. A láthatóság és a közös kódvédelem marad.
  const reset = () => {
    let over;
    if (mode === 'bingo') {
      const d = BINGO_ITEMS.map(it => ({ e: it.e, t: it.t }));
      setTitle('VB Bingó'); setItems(d);
      over = { title: 'VB Bingó', items: d };
    } else if (mode === 'tipp') {
      setTippTitle('Tippbajnokság'); setMatches([]); setTeamsText(''); setBWinner({ enabled:false, deadline:'', correct:'' }); setBScorer({ enabled:false, deadline:'', correct:'' });
      over = { tippTitle: 'Tippbajnokság', teams: [], matches: [], bonusWinner: { enabled:false }, bonusScorer: { enabled:false }, questions: [] };
    } else {
      setTortaTitle('DNR a tortán'); setTortaTeams([]); setTortaEvenings([]);
      over = { tortaTitle: 'DNR a tortán', tortaTeams: [], tortaEvenings: [] };
    }
    persist(buildPayload(over));
  };""")
rep("""        <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>Bingó / Tipp / DNR a tortán</span>
      </div>
      <div style={{ display:'flex', gap:6, marginBottom:12 }}>
        {[['bingo','⚽ Bingó'],['tipp','🎯 Tipp'],['torta','🍽️ Tortán']].map(([k,l]) => (
          <button key={k} data-bingo-mode={k} onClick={() => { setMode(k); markDirty(); }} style={{ flex:1, padding:'11px 0', borderRadius:13, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize:13, whiteSpace:'nowrap', background: mode === k ? T.mint : T.surface, color: mode === k ? '#fff' : T.inkSoft, boxShadow: mode === k ? `0 4px 12px ${T.mint}55` : T.shadow }}>{l}</button>
        ))}
      </div>""",
"""        <span data-bingo-admin-app={mode} style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{mode === 'torta' ? 'DNR a tortán' : mode === 'tipp' ? 'DNR Tipp — tippbajnokság' : 'DNR Bingó'}</span>
      </div>""")
rep("""          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink }}>Megjelenítés a főképernyőn</div>""",
    """          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink }}>Megjelenítés a DNR központban</div>""")
rep("""        <Toggle on={enabled} onChange={() => {
          const nv = !enabled; setEnabled(nv); setVisMsg('mentés…');
          if (typeof firebase === 'undefined') { setVisMsg(''); return; }
          firebase.firestore().collection('config').doc('bingoConfig').set({ enabled: nv }, { merge: true })
            .then(() => setVisMsg('mentve ✓'))
            .catch(e => { setEnabled(!nv); setVisMsg('nem sikerült menteni' + (e && e.code ? ` (${e.code})` : '')); });
        }} />""",
"""        {/* v10.419: appokra bontva — a TELJES apps térkép megy ki (materializálva), így
            egy régi config (enabled + mode) a többi app láthatóságát sem billenti el. */}
        <Toggle on={enabled} onChange={() => {
          const nv = !enabled; const prevApps = apps || bingoAppsOf(null); const nextApps = Object.assign({}, prevApps, { [mode]: nv });
          setEnabled(nv); setApps(nextApps); setVisMsg('mentés…');
          if (typeof firebase === 'undefined') { setVisMsg(''); return; }
          firebase.firestore().collection('config').doc('bingoConfig').set({ apps: nextApps }, { merge: true })
            .then(() => setVisMsg('mentve ✓'))
            .catch(e => { setEnabled(!nv); setApps(prevApps); setVisMsg('nem sikerült menteni' + (e && e.code ? ` (${e.code})` : '')); });
        }} />""")
rep("""          {renderCodeGateAdmin('A pontozáshoz kód kell (e-mailben)', 'Bárki pontozhat kód nélkül')}""",
    """          {renderCodeGateAdmin('A pontozáshoz kód kell (e-mailben) · közös a Tipp appal', 'Bárki pontozhat kód nélkül · közös a Tipp appal')}""")
rep("""          {renderCodeGateAdmin('A tippeléshez kód kell (e-mailben)', 'Bárki tippelhet kód nélkül')}""",
    """          {renderCodeGateAdmin('A tippeléshez kód kell (e-mailben) · közös a Tortán appal', 'Bárki tippelhet kód nélkül · közös a Tortán appal')}""")

# ── BingoScreen: az app adja a módot ──
rep("""function BingoScreen({ go, deepLink }) {
  const [profiles, setProfiles] = React.useState([]);
  const [who, setWho] = React.useState(() => { try { return localStorage.getItem('boh_bingo_who') || null; } catch(e) { return null; } });""",
"""function BingoScreen({ go, deepLink, app }) {
  // v10.419: három külön app UGYANEZZEL a képernyővel. A „Ki vagy?" apponként
  // megjegyezve; az új appok első nyitáskor a régi közös választást veszik át.
  const whoKey = (app === 'tipp' || app === 'torta') ? 'boh_' + app + '_who' : 'boh_bingo_who';
  const [profiles, setProfiles] = React.useState([]);
  const [who, setWho] = React.useState(() => { try { return localStorage.getItem(whoKey) || localStorage.getItem('boh_bingo_who') || null; } catch(e) { return null; } });""")
rep("""  const mode = (cfg && (cfg.mode === 'tipp' || cfg.mode === 'torta')) ? cfg.mode : 'bingo';
  const ITEMS =""",
"""  const mode = bingoScreenMode(app, cfg, deepLink);
  const ITEMS =""")
rep("""try { localStorage.setItem('boh_bingo_who', id || ''); } catch(e) {} };""",
    """try { localStorage.setItem(whoKey, id || ''); } catch(e) {} };""")

# ── DNR_APPS + segédek ──
rep("""  { screen:'bingo',   name:'DNR Bingó',  icon:'assets/dnr_bingo_icon.png',  sub: () => 'Meccs- és bulibingó · tipp bajnokság · DNR a tortán' },""",
"""  { screen:'bingo',   name:'DNR Bingó',  icon:'assets/dnr_bingo_icon.png',  sub: () => 'Meccs- és bulibingó, közös tábla' },
  { screen:'tipp',    name:'DNR Tipp',   icon:'assets/dnr_tipp_icon.png',   sub: () => 'Tippbajnokság · meccseredmények' },
  { screen:'torta',   name:'DNR a tortán', icon:TORTA_LOGO,                 sub: () => 'Főzős vendéglátó-bajnokság · pontozás' },""")
rep("""// Egy DNR app MEGJELENÍTETT alakja. A Bingó app a módja szerint öltözik: Tortán
// módban a „DNR a tortán" logóját és nevét viszi (a lista, a beállítások ÉS a
// főképernyő gombja ugyanazt mutatja). A mód a nyitóképernyőnek is el van téve
// (boh_bingo_mode) — az a config megérkezése ELŐTT fut.
function dnrAppView(app, bingoCfg) {
  if (app.screen !== 'bingo' || !bingoCfg || bingoCfg.mode !== 'torta') return app;
  return Object.assign({}, app, {
    name: bingoCfg.tortaTitle || 'DNR a tortán',
    icon: TORTA_LOGO,
    sub: () => 'Főzős vendéglátó-bajnokság · pontozás',
  });
}
function bohRememberBingoMode(cfg) {
  try {
    const m = (cfg && (cfg.mode === 'tipp' || cfg.mode === 'torta')) ? cfg.mode : 'bingo';
    localStorage.setItem('boh_bingo_mode', m);
    if (m === 'torta') localStorage.setItem('boh_torta_title', (cfg && cfg.tortaTitle) || 'DNR a tortán');
  } catch(e) {}
}
function useBingoCfg() {
  const [c, setC] = React.useState(null);
  React.useEffect(() => {
    if (typeof firebase === 'undefined') return;
    const un = firebase.firestore().collection('config').doc('bingoConfig')
      .onSnapshot(d => { const v = (d && d.exists && d.data()) || null; setC(v); bohRememberBingoMode(v); }, () => {});
    return () => { try { un(); } catch(e) {} };
  }, []);
  return c;
}""",
"""// Egy DNR app MEGJELENÍTETT alakja: a Tortán neve és a Tipp alcíme az admin
// által beállított címből jön (config/bingoConfig).
function dnrAppView(app, bingoCfg) {
  if (!bingoCfg) return app;
  if (app.screen === 'torta' && bingoCfg.tortaTitle) return Object.assign({}, app, { name: bingoCfg.tortaTitle });
  if (app.screen === 'tipp' && bingoCfg.tippTitle) return Object.assign({}, app, { sub: () => bingoCfg.tippTitle + ' · meccseredmények' });
  return app;
}
// ── Bingó / Tipp / Tortán: három KÜLÖN app, közös config-doksival (v10.419) ──
// Régen EGY app volt három móddal (`bingoConfig.mode`), és egyszerre csak egy
// látszott. Most mindhárom saját képernyő (`bingo` / `tipp` / `torta`), és a
// láthatóság appokra bontva a `bingoConfig.apps` térképben él.
// ⚠️ Migráció: ha az `apps` (vagy egy kulcsa) hiányzik, a RÉGI szabály dönt —
// csak a kiválasztott mód appja látszik, és csak ha az `enabled` nem hamis. Így a
// frissítés után pontosan az marad látható, ami addig is látszott.
const BINGO_APP_KEYS = ['bingo', 'tipp', 'torta'];
function bingoLegacyMode(cfg) {
  return (cfg && (cfg.mode === 'tipp' || cfg.mode === 'torta')) ? cfg.mode : 'bingo';
}
function bingoAppOn(cfg, key) {
  if (cfg && cfg.apps && typeof cfg.apps[key] === 'boolean') return cfg.apps[key];
  return (!cfg || cfg.enabled !== false) && bingoLegacyMode(cfg) === key;
}
function bingoAppsOf(cfg) {
  const o = {}; BINGO_APP_KEYS.forEach(k => { o[k] = bingoAppOn(cfg, k); }); return o;
}
// A képernyő módja. Az app dönt; app nélkül (régi hívás) a régi `mode`.
// ⚠️ Régi, telepített ikon: a `?screen=bingo` linkkel indul. Ha ott a Bingó nincs
// bekapcsolva, de a régi mód (pl. Tortán) appja igen, az nyílik — különben a
// frissítés után a telefonon lévő „DNR a tortán" ikon csendben Bingót nyitna.
function bingoScreenMode(app, cfg, deepLink) {
  const lm = bingoLegacyMode(cfg);
  if (!BINGO_APP_KEYS.includes(app)) return lm;
  if (app === 'bingo' && deepLink && cfg && lm !== 'bingo' && !bingoAppOn(cfg, 'bingo') && bingoAppOn(cfg, lm)) return lm;
  return app;
}
// A nyitóképernyő (splash) és az ikon a config ELŐTT fut, ezért a localStorage
// mondja meg nekik: a `?screen=bingo` link hová visz (boh_bingo_mode), és mi a címe.
function bohRememberBingoMode(cfg) {
  try {
    localStorage.setItem('boh_bingo_mode', bingoScreenMode('bingo', cfg, true));
    localStorage.setItem('boh_torta_title', (cfg && cfg.tortaTitle) || 'DNR a tortán');
    localStorage.setItem('boh_tipp_title', (cfg && cfg.tippTitle) || 'Tippbajnokság');
  } catch(e) {}
}
function useBingoCfgDoc() {
  const [c, setC] = React.useState({ v: null, loaded: false });
  React.useEffect(() => {
    if (typeof firebase === 'undefined') { setC({ v: null, loaded: true }); return; }
    const un = firebase.firestore().collection('config').doc('bingoConfig')
      .onSnapshot(d => { const v = (d && d.exists && d.data()) || null; setC({ v, loaded: true }); bohRememberBingoMode(v); }, () => setC(x => ({ v: x.v, loaded: true })));
    return () => { try { un(); } catch(e) {} };
  }, []);
  return c;
}
function useBingoCfg() { return useBingoCfgDoc().v; }""")

# ── Központ ──
rep("""  const bingoCfg = useBingoCfg();
  const homeCfg = useHomeCfgDoc();
  const live = useDnrLiveInfo();
  const hc = homeCfg.v;
  const master = !hc || hc.dnrAppsEnabled !== false;
  const bingoOn = !bingoCfg || bingoCfg.enabled !== false;
  const others = master ? DNR_APPS.filter(a => dnrAppEnabled(hc, a.screen) && (a.screen !== 'bingo' || bingoOn)).map(a => dnrAppView(a, bingoCfg)) : [];""",
"""  const bingoDoc = useBingoCfgDoc();
  const bingoCfg = bingoDoc.v;
  const homeCfg = useHomeCfgDoc();
  const live = useDnrLiveInfo();
  const hc = homeCfg.v;
  const master = !hc || hc.dnrAppsEnabled !== false;
  // Bingó / Tipp / Tortán: KÉT kapcsoló, és bármelyik elég az elrejtéshez — a
  // `homeConfig.dnrApps.<app>` (Beállítások) és a `bingoConfig.apps.<app>` (az app
  // saját admin-füle). Betöltés előtt ezek nem látszanak (ne villanjon fel egy app).
  const others = master ? DNR_APPS.filter(a => dnrAppEnabled(hc, a.screen) && (!BINGO_APP_KEYS.includes(a.screen) || (bingoDoc.loaded && bingoAppOn(bingoCfg, a.screen)))).map(a => dnrAppView(a, bingoCfg)) : [];""")
rep("""  React.useEffect(() => { if (homeCfg.loaded && others.length === 0) onOpen('home'); }, [homeCfg.loaded, others.length]);""",
    """  React.useEffect(() => { if (homeCfg.loaded && bingoDoc.loaded && others.length === 0) onOpen('home'); }, [homeCfg.loaded, bingoDoc.loaded, others.length]);""")
rep("""  // A Bingó / „DNR a tortán" a HARMADIK kártya (v10.413, tulajdonosi kérés) — a
  // DNR_APPS sorrendje (admin lista) nem változik, csak a központé.
  const HUB_ORDER = ['log', 'bingo', 'jukebox', 'bar', 'stats'];""",
"""  // A „DNR a tortán" a HARMADIK kártya (v10.413, tulajdonosi kérés), utána a Tipp és
  // a Bingó (v10.419) — a DNR_APPS sorrendje (admin lista) nem változik, csak a központé.
  const HUB_ORDER = ['log', 'torta', 'tipp', 'bingo', 'jukebox', 'bar', 'stats'];""")

# ── BottleApp: útvonalak ──
rep("""  const _bingoApp = _initScreen === 'bingo';
  const _ligaApp""", """  const _bingoApp = _initScreen === 'bingo';
  const _tippApp = _initScreen === 'tipp';
  const _tortaApp = _initScreen === 'torta';
  const _ligaApp""")
rep("""_bingoApp ? 'bingo' : _ligaApp ? 'stats'""", """_bingoApp ? 'bingo' : _tippApp ? 'tipp' : _tortaApp ? 'torta' : _ligaApp ? 'stats'""")
rep("""!_barApp && !_bingoApp && !_ligaApp;""", """!_barApp && !_bingoApp && !_tippApp && !_tortaApp && !_ligaApp;""")
rep("""const HUB_APP_SCREENS = ['log', 'create', 'jukebox', 'bar', 'bingo', 'stats', 'admin', 'observer'];""",
    """const HUB_APP_SCREENS = ['log', 'create', 'jukebox', 'bar', 'bingo', 'tipp', 'torta', 'stats', 'admin', 'observer'];""")
rep("""  const order = ['hub','home','stats','bingo','bar',""", """  const order = ['hub','home','stats','bingo','tipp','torta','bar',""")
rep("""        {screen==='bingo'    && <BingoScreen    go={go} deepLink={_bingoApp} />}""",
"""        {screen==='bingo'    && <BingoScreen    key="bingo" app="bingo" go={go} deepLink={_bingoApp} />}
        {screen==='tipp'     && <BingoScreen    key="tipp"  app="tipp"  go={go} deepLink={_tippApp} />}
        {screen==='torta'    && <BingoScreen    key="torta" app="torta" go={go} deepLink={_tortaApp} />}""")
rep("""                 : _q.indexOf('screen=bingo')  !== -1 ? 'bingo'""",
"""                 : _q.indexOf('screen=bingo')  !== -1 ? 'bingo'
                 : _q.indexOf('screen=tipp')   !== -1 ? 'tipp'
                 : _q.indexOf('screen=torta')  !== -1 ? 'torta'""")

# ── szövegek: az admin-fül neve a hivatkozásokban ──
rep("az Admin → Bingó → Alkalmak alatt törölhető.", "az Admin → Tortán → Alkalmak alatt törölhető.")
rep("Az admin a Bingó fülön (DNR a tortán mód) tudja felvenni a csapatokat és az alkalmakat.", "Az admin a Tortán fülön tudja felvenni a csapatokat és az alkalmakat.")
rep("Az admin a Bingó fülön (Tipp mód) tud mérkőzéseket felvenni.", "Az admin a Tipp fülön tud mérkőzéseket felvenni.")

open(P, 'w', encoding='utf-8').write(s)
print('OK')
