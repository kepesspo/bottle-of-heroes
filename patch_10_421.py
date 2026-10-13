# v10.421 — EGY téma-felület az összes apphoz (config/appThemes)
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:140])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.420'", "const APP_VERSION = 'v10.421'")

# ── 1) splash: ugyanaz a feloldás, mint az appban ──
rep("""  var theme  = localStorage.getItem('boh_theme') || 'warm';
  var themes = {""", """  // v10.421: a téma APPONKÉNT jön a config/appThemes-ből (gyorsítótár: boh_app_themes)
  // — ugyanaz a szabály, mint a bohThemeKey() az appban. Nincs mentett beállítás →
  // a régi forrás: Events/Pub/BOX a saját régi témája, a többi az eszköz boh_theme-je.
  var theme = (function(){
    var q = location.search, app = /[?&]room=/.test(q) ? 'games' : 'hub';
    var m = q.match(/[?&]screen=([^&#]+)/), sc = m ? m[1] : '';
    var MAP = { events:'events', calendar:'events', bar:'pub', dnrbox:'box', liga:'liga', bingo:'bingo', tipp:'tipp', torta:'torta', games:'games' };
    if (MAP[sc]) app = MAP[sc];
    var cfg = null; try { cfg = JSON.parse(localStorage.getItem('boh_app_themes') || 'null'); } catch(e) {}
    if (cfg && cfg.apps && cfg.apps[app]) return cfg.apps[app];
    if (cfg && cfg.default) return cfg.default;
    var lg = { events:['boh_events_theme','ice'], pub:['boh_bar_theme','warm'], box:['boh_dnrbox_theme','warm'] }[app];
    try { return lg ? (localStorage.getItem(lg[0]) || lg[1]) : (localStorage.getItem('boh_theme') || 'warm'); } catch(e) { return 'warm'; }
  })();
  var themes = {""")
rep("""    var _spEvTh = localStorage.getItem('boh_events_theme') || 'ice';
    t = themes[_spEvTh] || themes['ice'] || t;
""", "")
rep("""    var _dkTh = localStorage.getItem(_isBarDeepLink ? 'boh_bar_theme' : 'boh_dnrbox_theme') || 'warm';
    t = themes[_dkTh] || t;
""", "")

# ── 2) feloldó + boot-téma ──
rep("""let T = THEMES[localStorage.getItem('boh_theme')] || THEMES['warm'];
if (!T) T = THEMES['warm'];
if (location.search.indexOf('screen=events') !== -1 || location.search.indexOf('screen=calendar') !== -1) { var _evTh = localStorage.getItem('boh_events_theme') || 'ice'; T = THEMES[_evTh] || THEMES['ice']; }
else if (location.search.indexOf('screen=bar') !== -1) { var _barTh = localStorage.getItem('boh_bar_theme') || 'warm'; T = THEMES[_barTh] || THEMES['warm']; }
else if (location.search.indexOf('screen=dnrbox') !== -1) { var _boxTh = localStorage.getItem('boh_dnrbox_theme') || 'warm'; T = THEMES[_boxTh] || THEMES['warm']; }""",
"""// ── EGY téma-forrás minden apphoz (v10.421) ─────────────────────────────────
// config/appThemes = { default: '<téma>', apps: { <app>: '<téma>' } }. Az app vagy a
// közös `default`-ot viseli, vagy (ha az admin külön adott neki) a sajátját.
// ⚠️ Mentett beállítás NÉLKÜL a RÉGI forrás él tovább: az Events/Pub/BOX a saját régi
// admin-témája (eventsTheme/barTheme/dnrboxTheme — a gyorsítótár kulcsaiból), a többi
// az eszköz `boh_theme`-je. Így a frissítés után semmi nem változik, amíg az admin
// a Témák lapon nem dönt — és a régi tesztek `boh_theme`-mel is a választott témát kapják.
const BOH_THEME_APPS = ['hub', 'games', 'events', 'torta', 'tipp', 'bingo', 'box', 'pub', 'liga'];
const BOH_THEME_LEGACY = { events:['boh_events_theme', 'ice'], pub:['boh_bar_theme', 'warm'], box:['boh_dnrbox_theme', 'warm'] };
function bohThemeKey(app, cfg) {
  const ok = k => !!(k && THEMES[k]);
  if (cfg && cfg.apps && ok(cfg.apps[app])) return cfg.apps[app];
  if (cfg && ok(cfg.default)) return cfg.default;
  let k = 'warm';
  try { const lg = BOH_THEME_LEGACY[app]; k = lg ? (localStorage.getItem(lg[0]) || lg[1]) : (localStorage.getItem('boh_theme') || 'warm'); } catch(e) {}
  return ok(k) ? k : 'warm';
}
function bohCachedThemeCfg() { try { return JSON.parse(localStorage.getItem('boh_app_themes') || 'null'); } catch(e) { return null; } }
// Melyik app témáját viseli egy képernyő. Az Admin a központé (onnan nyílik).
function bohAppOfScreen(sc) {
  if (sc === 'hub' || sc === 'admin') return 'hub';
  if (sc === 'log' || sc === 'create') return 'events';
  if (sc === 'bar') return 'pub';
  if (sc === 'jukebox') return 'box';
  if (sc === 'stats') return 'liga';
  if (sc === 'bingo' || sc === 'tipp' || sc === 'torta') return sc;
  return 'games';
}
function bohAppOfUrl() {
  try {
    const q = new URLSearchParams(location.search), sc = q.get('screen') || '';
    if (q.get('room')) return 'games';
    return ({ events:'events', calendar:'events', bar:'pub', dnrbox:'box', liga:'liga', bingo:'bingo', tipp:'tipp', torta:'torta', games:'games' })[sc] || 'hub';
  } catch(e) { return 'hub'; }
}
// A legutóbb látott beállítás (eszközön); a BottleApp és a Témák lap is ezt figyeli.
function useAppThemeCfg() {
  const [c, setC] = React.useState(() => bohCachedThemeCfg());
  React.useEffect(() => {
    if (typeof firebase === 'undefined') return;
    const un = firebase.firestore().collection('config').doc('appThemes').onSnapshot(d => {
      const v = (d && d.exists && d.data()) || null;
      setC(v);
      try { if (v) localStorage.setItem('boh_app_themes', JSON.stringify(v)); else localStorage.removeItem('boh_app_themes'); } catch(e) {}
    }, () => {});
    return () => { try { un(); } catch(e) {} };
  }, []);
  return c;
}

let T = THEMES[bohThemeKey(bohAppOfUrl(), bohCachedThemeCfg())] || THEMES['warm'];""")

# ── 3) Events: az egységes feloldásból, az appon BELÜL is (eddig csak deep linken) ──
a = s.index('function useEventsTheme() {')
b = s.index('function EventCalendarView(', a)
s = s[:a] + """// v10.421: az Events témája a KÖZÖS téma-forrásból (bohThemeKey('events')) — és nem
// csak deep linken: a központból nyitva is ugyanez. Eddig az appon belül a Games
// eszköz-témáját viselte, deep linken a sajátját — ugyanaz az app két színben.
function useEventsTheme() {
  const cfg = useAppThemeCfg();
  const th = THEMES[bohThemeKey('events', cfg)] || THEMES['warm'];
  window.__evT = th;
  return th;
}

""" + s[b:]
rep("  const T = deepLink ? evT : (THEMES[localStorage.getItem('boh_theme')] || THEMES['warm']);", "  const T = evT;", 2)

# ── 4) Games főoldal: a saját téma-választó kikerül (a téma az adminból jön) ──
a = s.index("              {/* Theme */}\n              {/* Theme picker — color swatch strips */}")
b = s.index("              {/* Splash screen toggle */}", a)
s = s[:a] + s[b:]

# ── 5) BottleApp: a képernyő appja dönti el a témát ──
rep("""  const [appTheme, setAppTheme] = React.useState(() => localStorage.getItem('boh_theme') || 'warm');
  const handleSetTheme = (name) => {
    localStorage.setItem('boh_theme', name);
    T = THEMES[name];
    setAppTheme(name);
    const bg = T.bg;
    document.documentElement.style.setProperty('--app-bg', bg);
    document.documentElement.style.setProperty('--app-surface', T.surface);
    document.documentElement.style.background = bg;
    document.body.style.background = bg;
  document.documentElement.style.background = bg;
    const tc = document.querySelector('meta[name="theme-color"]');
    if (tc) tc.setAttribute('content', bg);
  };

  React.useEffect(() => {
    document.body.style.background = T.bg;""",
"""  // A téma (v10.421) a KÉPERNYŐ APPJÁBÓL jön (bohAppOfScreen → bohThemeKey), nem az
  // eszközről. A globális T-t itt, a renderelés elején állítjuk, így minden gyerek
  // már az új témával rajzol. A `themePreview` csak az admin téma-pörgetőjé.
  const themeCfg = useAppThemeCfg();
  const [themePreview, setThemePreview] = React.useState(null);
  const appTheme = (themePreview && THEMES[themePreview]) ? themePreview : bohThemeKey(bohAppOfScreen(screen), themeCfg);
  if (T !== THEMES[appTheme]) T = THEMES[appTheme];
  const handleSetTheme = (name) => setThemePreview(name || null);

  React.useEffect(() => {
    document.documentElement.style.setProperty('--app-bg', T.bg);
    document.documentElement.style.setProperty('--app-surface', T.surface);
    document.body.style.background = T.bg;""")

# ── 6) Admin: EGY Témák lap; a Pub/BOX/Events Téma-fül megszűnt ──
rep("""['profiles','Profilok'],['message','Hirdetmény'],['hub','DNR központ'],['settings','Rendszer'],""",
    """['profiles','Profilok'],['message','Hirdetmény'],['hub','DNR központ'],['themes','Témák'],['settings','Rendszer'],""")
rep("""    { key:'events', label:'DNR Events', icon:'assets/dnr_events_icon.png', zoom:1.9, tabs:[['events','Események'],['eventsTheme','Téma']] },""",
    """    { key:'events', label:'DNR Events', icon:'assets/dnr_events_icon.png', zoom:1.9, tabs:[['events','Események']] },""")
rep("""    { key:'box', label:'DNR BOX', icon:'assets/dnr_box_icon.png', tabs:[['boxTheme','Téma']] },
    { key:'pub', label:'DNR Pub', icon:'assets/dnr_pub_icon.png', zoom:1.9, tabs:[['pubTheme','Téma']] },
""", "")
rep("""        {tab === 'eventsTheme' && <AdminAppTheme app="events" />}
        {tab === 'pubTheme'    && <AdminAppTheme app="pub" />}
        {tab === 'boxTheme'    && <AdminAppTheme app="box" />}""",
    """        {tab === 'themes'   && <AdminThemes setTheme={setTheme} />}""")
rep("""        {tab === 'gamesSettings' && <AdminGamesSettings setTheme={setTheme} currentTheme={currentTheme} />}""",
    """        {tab === 'gamesSettings' && <AdminGamesSettings />}""")

a = s.index("const THEME_OPTIONS = THEME_LIST.map(")
b = s.index("function AdminGamesSettings(", a)
s = s[:a] + """// ── Admin → Általános → Témák (v10.421) ───────────────────────────────────────
// EGY felület az összes app témájához. Fent a KÖZÖS téma, alatta minden app egy
// sora: „Közös" (követi a fentit) vagy egy saját téma. Minden koppintás AZONNAL ment
// (config/appThemes), a teljes alakot írja ki — így egy régi, mentetlen állapot
// (lásd bohThemeKey) az első mentéskor pontosan úgy kerül be, ahogy látszott.
const ADMIN_THEME_APP_ROWS = [
  { key:'hub',    label:'DNR központ', sub:'és az Admin' },
  { key:'games',  label:'DNR Games',   icon:'assets/dnr_games_icon.png',  zoom:1.25 },
  { key:'events', label:'DNR Events',  icon:'assets/dnr_events_icon.png', zoom:1.9 },
  { key:'torta',  label:'DNR a tortán', torta:true },
  { key:'tipp',   label:'DNR Tipp',    icon:'assets/dnr_tipp_icon.png',   zoom:1.9 },
  { key:'bingo',  label:'DNR Bingó',   icon:'assets/dnr_bingo_icon.png',  zoom:1.9 },
  { key:'box',    label:'DNR BOX',     icon:'assets/dnr_box_icon.png' },
  { key:'pub',    label:'DNR Pub',     icon:'assets/dnr_pub_icon.png',    zoom:1.9 },
  { key:'liga',   label:'DNR Liga',    icon:'assets/dnr_liga_icon.png',   zoom:1.9 },
];
function bohMaterializeThemeCfg(cfg) {
  const def = (cfg && cfg.default && THEMES[cfg.default]) ? cfg.default : bohThemeKey('games', null);
  const apps = {};
  if (cfg && cfg.default && THEMES[cfg.default]) {
    Object.keys((cfg && cfg.apps) || {}).forEach(k => { if (THEMES[cfg.apps[k]]) apps[k] = cfg.apps[k]; });
  } else {
    // régi állapot: ami a közöstől eltér, az app saját témája lesz
    BOH_THEME_APPS.forEach(k => { const v = bohThemeKey(k, cfg); if (v !== def) apps[k] = v; });
  }
  return { default: def, apps };
}
function ThemeSwatchCard({ k, on, onPick, attr }) {
  const sw = themeSwatch(k);
  const label = (THEME_LIST.find(x => x.key === k) || {}).label || k;
  return (
    <button {...attr} aria-pressed={on} onClick={onPick} style={{ padding:0, borderRadius:14, cursor:'pointer', overflow:'hidden', border: on ? `2.5px solid ${T.mint}` : `2px solid ${T.inkMute}22`, boxShadow: on ? `0 3px 12px ${T.mint}55` : T.shadowPill, background:'transparent', display:'flex', flexDirection:'column', minWidth:0 }}>
      <span style={{ display:'block', height:40, background:sw.bg, position:'relative' }}>
        <span style={{ position:'absolute', bottom:5, left:7, right:7, height:14, background:sw.surface, borderRadius:4, opacity:0.92 }} />
        <span style={{ position:'absolute', top:6, right:8, width:9, height:9, borderRadius:'50%', background:sw.accent }} />
      </span>
      <span style={{ display:'block', padding:'6px 2px 7px', background: on ? T.mintSoft : T.surfaceMuted, fontFamily:T.font, fontWeight:800, fontSize:10.5, color: on ? T.mintDeep : T.inkSoft, whiteSpace:'nowrap', textAlign:'center' }}>{label}</span>
    </button>
  );
}
function AdminThemes({ setTheme }) {
  const cfg = useAppThemeCfg();
  const [local, setLocal] = React.useState(null);
  const [msg, setMsg] = React.useState('');
  const cur = local || bohMaterializeThemeCfg(cfg);
  const write = next => {
    setLocal(next); setMsg('mentés…');
    try { localStorage.setItem('boh_app_themes', JSON.stringify(next)); } catch(e) {}
    if (typeof firebase === 'undefined') { setMsg(''); return; }
    firebase.firestore().collection('config').doc('appThemes').set(next)
      .then(() => setMsg('mentve ✓'))
      .catch(e => setMsg('nem sikerült menteni' + (e && e.code ? ` (${e.code})` : '')));
  };
  const setDefault = k => write({ default: k, apps: { ...cur.apps } });
  const setApp = (app, k) => { const apps = { ...cur.apps }; if (k) apps[app] = k; else delete apps[app]; write({ default: cur.default, apps }); };
  const nOwn = Object.keys(cur.apps).length;
  const label = k => (THEME_LIST.find(x => x.key === k) || {}).label || k;
  const icon = r => {
    const size = 32;
    if (!r.icon && !r.torta) return <span style={{ width:size, height:size, borderRadius:'28%', background:DNR_HUB_INK, color:'#fff', display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:11, flexShrink:0 }}>DNR</span>;
    return (
      <span style={{ position:'relative', width:size, height:size, borderRadius:'28%', overflow:'hidden', background:'#fff', flexShrink:0, display:'inline-block' }}>
        <img src={r.torta ? TORTA_LOGO : r.icon} alt="" style={{ position:'absolute', left:'50%', top:'50%', transform:'translate(-50%, -50%)', width:size * (r.zoom || 1), height:size * (r.zoom || 1), maxWidth:'none' }} />
      </span>
    );
  };
  const card = { background:T.surface, borderRadius:16, padding:16, boxShadow:T.shadow, marginBottom:14 };
  return (
    <div data-admin-themes style={{ padding:16 }}>
      <div style={card}>
        <div style={{ display:'flex', alignItems:'baseline', justifyContent:'space-between', gap:10 }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>Közös téma</div>
          {msg && <div style={{ fontFamily:T.font, fontWeight:800, fontSize:11.5, color: /nem sikerült/.test(msg) ? T.coral : T.mint }}>{msg}</div>}
        </div>
        <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, margin:'3px 0 12px' }}>Minden app ezt viseli, hacsak alább nem kap sajátot. Minden telefonon ugyanaz — a téma nem eszközönkénti beállítás.</div>
        <div style={{ display:'grid', gridTemplateColumns:`repeat(${THEME_LIST.length}, minmax(0,1fr))`, gap:6 }}>
          {THEME_LIST.map(x => <ThemeSwatchCard key={x.key} k={x.key} on={cur.default === x.key} onPick={() => setDefault(x.key)} attr={{ 'data-theme-default': x.key }} />)}
        </div>
      </div>

      <div style={card}>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', gap:10, marginBottom:4 }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>Appok</div>
          {nOwn > 0 && (
            <button data-theme-reset onClick={() => write({ default: cur.default, apps: {} })}
              style={{ border:'none', background:'transparent', color:T.mintDeep, fontFamily:T.font, fontWeight:800, fontSize:12, cursor:'pointer', padding:'4px 0' }}>Mindenhol a közös</button>
          )}
        </div>
        <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginBottom:6 }}>{nOwn === 0 ? 'Minden app a közös témát viseli.' : `${nOwn} app saját témával.`}</div>
        {ADMIN_THEME_APP_ROWS.map((r, i) => {
          const own = cur.apps[r.key];
          const eff = own || cur.default;
          return (
            <div key={r.key} data-theme-app={r.key} style={{ padding:'12px 0', borderTop: i ? `1px solid ${T.inkMute}22` : 'none' }}>
              <div style={{ display:'flex', alignItems:'center', gap:11 }}>
                {icon(r)}
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink }}>{r.label}{r.sub && <span style={{ fontWeight:700, fontSize:11.5, color:T.inkMute }}> · {r.sub}</span>}</div>
                  <div data-theme-eff style={{ fontFamily:T.font, fontWeight:700, fontSize:11.5, color: own ? T.mintDeep : T.inkMute, marginTop:1 }}>{own ? 'Saját: ' + label(own) : 'Közös: ' + label(cur.default)}</div>
                </div>
                <span aria-hidden="true" style={{ width:30, height:22, borderRadius:7, background:themeSwatch(eff).bg, boxShadow:`inset 0 0 0 1.5px ${T.inkMute}33`, position:'relative', flexShrink:0 }}>
                  <span style={{ position:'absolute', top:4, right:4, width:6, height:6, borderRadius:'50%', background:themeSwatch(eff).accent }} />
                </span>
              </div>
              <div style={{ display:'flex', alignItems:'center', gap:6, marginTop:9, paddingLeft:43, flexWrap:'wrap' }}>
                <button data-theme-pick="" aria-pressed={!own} onClick={() => setApp(r.key, null)}
                  style={{ height:28, padding:'0 11px', borderRadius:999, border: !own ? `2px solid ${T.mint}` : `1.5px solid ${T.inkMute}44`, background: !own ? T.mintSoft : 'transparent', color: !own ? T.mintDeep : T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:11.5, cursor:'pointer' }}>Közös</button>
                {THEME_LIST.map(x => {
                  const on = own === x.key, sw = themeSwatch(x.key);
                  return (
                    <button key={x.key} data-theme-pick={x.key} aria-pressed={on} aria-label={label(x.key)} title={label(x.key)} onClick={() => setApp(r.key, x.key)}
                      style={{ width:28, height:28, borderRadius:'50%', padding:0, cursor:'pointer', background:sw.bg, border: on ? `2.5px solid ${T.mint}` : `1.5px solid ${T.inkMute}44`, boxShadow: on ? `0 0 0 2px ${T.surface}, 0 0 0 4px ${T.mint}` : 'none', position:'relative' }}>
                      <span style={{ position:'absolute', left:'50%', top:'50%', width:9, height:9, marginLeft:-4.5, marginTop:-4.5, borderRadius:'50%', background:sw.accent }} />
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {setTheme && <ThemeCyclerCard setTheme={setTheme} />}
    </div>
  );
}
""" + s[b:]
rep("""function AdminGamesSettings({ setTheme, currentTheme }) {
  return (
    <div style={{ padding:16 }}>
      <AdminHomeToggles only="setup" />
      {setTheme && <ThemeCyclerCard setTheme={setTheme} currentTheme={currentTheme} />}
    </div>
  );
}""", """function AdminGamesSettings() {
  return (
    <div style={{ padding:16 }}>
      <AdminHomeToggles only="setup" />
    </div>
  );
}""")
# a pörgető csak ELŐNÉZET: leállításkor nem egy témát állít vissza, hanem elengedi
rep("""function ThemeCyclerCard({ setTheme, currentTheme }) {""", """function ThemeCyclerCard({ setTheme }) {""")
rep("""      setCycling(false);
      if (savedRef.current) setTheme(savedRef.current);
    } else {
      savedRef.current = currentTheme;
      setIdx(0);""", """      setCycling(false);
      setTheme(null);   // v10.421: az előnézet elengedése — a beállított (app-) téma jön vissza
    } else {
      setIdx(0);""")
open(P, 'w', encoding='utf-8').write(s)
print('OK')

# ── utólag: a téma-kártya felirata telefonon is kifér ──
s = open(P, encoding='utf-8').read()
rep("fontWeight:800, fontSize:10.5, color: on ? T.mintDeep : T.inkSoft, whiteSpace:'nowrap', textAlign:'center' }}>{label}</span>",
    "fontWeight:800, fontSize:'clamp(8.5px, 2.5vw, 10.5px)', letterSpacing:'-0.02em', color: on ? T.mintDeep : T.inkSoft, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis', textAlign:'center' }}>{label}</span>")
open(P, 'w', encoding='utf-8').write(s)
