# v10.420 — Admin appok szerint kategorizálva + a Hirdetmény a DNR központba költözik
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, count=1, src=None):
    global s
    n = s.count(old)
    assert n == count, (n, old[:140])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.419'", "const APP_VERSION = 'v10.420'")

# ── AdminHomeToggles: szakaszokra bontható (only = 'hub' | 'setup' | 'season') ──
a = s.index('function AdminHomeToggles() {')
b = s.index('// A tema-porgeteshez ugyanaz a lista', a)
f = s[a:b]
def frep(old, new, count=1):
    global f
    assert f.count(old) == count, (f.count(old), old[:120]); f = f.replace(old, new)
frep('function AdminHomeToggles() {', """// v10.420: az admin appok szerint kategorizált — a kártya három szakasza három
// helyre megy: 'hub' (Általános → DNR központ), 'setup' (DNR Games → Beállítások),
// 'season' (DNR Liga → Szezonok). `only` nélkül mind a három (régi hívók, tesztek).
function AdminHomeToggles({ only } = {}) {
  const show = k => !only || only === k;""")
SEP = "      <div style={{ height:1, background:`${T.inkMute}22`, margin:'14px 0' }} />\n"
frep(SEP, "      {!only && <div style={{ height:1, background:`${T.inkMute}22`, margin:'14px 0' }} />}\n", 2)
frep("""      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink, marginBottom:4 }}>Főoldal</div>
      <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginBottom:12 }}>Mi jelenjen meg a Bottle of Heroes főoldalán.</div>""",
"""      {show('hub') && (<React.Fragment>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink, marginBottom:4 }}>DNR központ</div>
      <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginBottom:12 }}>Melyik app kártyája jelenjen meg a DNR központban (az app nyitóképernyőjén).</div>""")
frep("""          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>„További DNR" gomb</div>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:2 }}>
            A főoldal alján a nyíllal jelzett felirat, ami a DNR appok listáját nyitja. Kikapcsolva a főoldalról a többi app nem érhető el.
          </div>""",
"""          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>DNR appok a központban</div>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:2 }}>
            Kikapcsolva a központban csak a DNR Games marad — ilyenkor az app egyenesen a Games-szel nyit.
          </div>""")
# a hub-szakasz vége = az első elválasztó előtt
frep("""      {!only && <div style={{ height:1, background:`${T.inkMute}22`, margin:'14px 0' }} />}

      <div style={{ display:'flex', alignItems:'center', gap:12 }}>""",
"""      </React.Fragment>)}
      {!only && <div style={{ height:1, background:`${T.inkMute}22`, margin:'14px 0' }} />}

      {show('setup') && (<React.Fragment>
      <div style={{ display:'flex', alignItems:'center', gap:12 }}>""")
frep("""      {!only && <div style={{ height:1, background:`${T.inkMute}22`, margin:'14px 0' }} />}

      <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>Szezonzáró ablak</div>""",
"""      </React.Fragment>)}
      {!only && <div style={{ height:1, background:`${T.inkMute}22`, margin:'14px 0' }} />}

      {show('season') && (<React.Fragment>
      <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>Szezonzáró ablak</div>""")
frep("""            : 'Nem jelenik meg. A végeredmény a Ligában továbbra is megnézhető.'}
      </div>
    </div>
  );
}""", """            : 'Nem jelenik meg. A végeredmény a Ligában továbbra is megnézhető.'}
      </div>
      </React.Fragment>)}
    </div>
  );
}""")
s = s[:a] + f + s[b:]

# ── AdminSettings → csak a valóban mindent érintő rendszer-dolgok; a témák az appjukhoz ──
rep("""function AdminSettings({ setTheme, currentTheme }) {
  return (
    <div style={{ padding:16 }}>
      <ThemeSelector title="Események oldal témája" urlHint="?screen=events" getFn={window.getEventsTheme} setFn={window.setEventsTheme} onFn={window.onEventsTheme} cacheKey="boh_events_theme" defaultKey="ice" />
      <ThemeSelector title="Pub oldal témája" urlHint="?screen=bar" getFn={window.getBarTheme} setFn={window.setBarTheme} onFn={window.onBarTheme} cacheKey="boh_bar_theme" defaultKey="warm" />
      <ThemeSelector title="Box oldal témája" urlHint="?screen=dnrbox" getFn={window.getBoxTheme} setFn={window.setBoxTheme} onFn={window.onBoxTheme} cacheKey="boh_dnrbox_theme" defaultKey="warm" />

      {setTheme && <ThemeCyclerCard setTheme={setTheme} currentTheme={currentTheme} />}

      <AdminPinCard />

      <AdminHomeToggles />

      <div""",
"""// v10.420: az admin APPOK szerint kategorizált. Itt csak az marad, ami MINDEN appot
// érint (admin PIN, kényszerített frissítés); a témák és az app-specifikus kapcsolók
// a saját appjuk kategóriájába költöztek (AdminAppTheme, AdminGamesSettings, Szezonok).
const ADMIN_APP_THEMES = {
  events: { title:'Events témája', urlHint:'?screen=events', get:'getEventsTheme', set:'setEventsTheme', on:'onEventsTheme', cacheKey:'boh_events_theme', defaultKey:'ice' },
  pub:    { title:'Pub témája',    urlHint:'?screen=bar',    get:'getBarTheme',    set:'setBarTheme',    on:'onBarTheme',    cacheKey:'boh_bar_theme',    defaultKey:'warm' },
  box:    { title:'BOX témája',    urlHint:'?screen=dnrbox', get:'getBoxTheme',    set:'setBoxTheme',    on:'onBoxTheme',    cacheKey:'boh_dnrbox_theme', defaultKey:'warm' },
};
function AdminAppTheme({ app }) {
  const c = ADMIN_APP_THEMES[app];
  return (
    <div style={{ padding:16 }}>
      <ThemeSelector title={c.title} urlHint={c.urlHint} getFn={window[c.get]} setFn={window[c.set]} onFn={window[c.on]} cacheKey={c.cacheKey} defaultKey={c.defaultKey} />
    </div>
  );
}
function AdminGamesSettings({ setTheme, currentTheme }) {
  return (
    <div style={{ padding:16 }}>
      <AdminHomeToggles only="setup" />
      {setTheme && <ThemeCyclerCard setTheme={setTheme} currentTheme={currentTheme} />}
    </div>
  );
}
function AdminSettings() {
  return (
    <div style={{ padding:16 }}>
      <AdminPinCard />

      <div""")

# ── AdminScreen: kategóriák appok szerint ──
rep("""  const CATEGORIES = [
    { key:'content', label:'Tartalom', tabs:[
      ['profiles','Profilok'],['events','Események'],['feladatok','Feladatok'],
    ]},
    { key:'game', label:'Játék', tabs:[
      ['games','Játékok'],['wildcards','Wildcard'],['xp','XP & Szint'],['bingo','Bingó'],['tipp','Tipp'],['torta','Tortán'],
    ]},
    { key:'system', label:'Rendszer', tabs:[
      ['growth','Növekedés'],['stats','Statisztika'],['partik','Partik'],['seasons','Szezonok'],['zene','Zene'],['rooms','Szobák'],['message','Hirdetmény'],['settings','Beállítások'],
    ]},
  ];
  const [category, setCategory] = React.useState('content');""",
"""  // v10.420: APPOK szerint kategorizálva (tulajdonosi kérés). Az „Általános" az, ami
  // MINDEN appot érint (profilok, hirdetmény, a központ kapcsolói, rendszer); utána az
  // appok a központ sorrendjében. Egy-fülű appnál az oldalsávon nincs al-elem: maga
  // az app sora a gomb. (Belül marad, mert a TORTA_LOGO később deklarált const.)
  const CATEGORIES = [
    { key:'general', label:'Általános', tabs:[
      ['profiles','Profilok'],['message','Hirdetmény'],['hub','DNR központ'],['settings','Rendszer'],['growth','Növekedés'],['feladatok','Fejlesztés'],
    ]},
    { key:'games', label:'DNR Games', icon:'assets/dnr_games_icon.png', tabs:[
      ['games','Játékok'],['wildcards','Wildcard'],['partik','Partik'],['rooms','Szobák'],['zene','Zene'],['gamesSettings','Beállítások'],
    ]},
    { key:'events', label:'DNR Events', icon:'assets/dnr_events_icon.png', tabs:[['events','Események'],['eventsTheme','Téma']] },
    { key:'torta', label:'DNR a tortán', icon:TORTA_LOGO, tabs:[['torta','DNR a tortán']] },
    { key:'tipp', label:'DNR Tipp', icon:'assets/dnr_tipp_icon.png', tabs:[['tipp','DNR Tipp']] },
    { key:'bingo', label:'DNR Bingó', icon:'assets/dnr_bingo_icon.png', tabs:[['bingo','DNR Bingó']] },
    { key:'box', label:'DNR BOX', icon:'assets/dnr_box_icon.png', tabs:[['boxTheme','Téma']] },
    { key:'pub', label:'DNR Pub', icon:'assets/dnr_pub_icon.png', tabs:[['pubTheme','Téma']] },
    { key:'liga', label:'DNR Liga', icon:'assets/dnr_liga_icon.png', tabs:[['seasons','Szezonok'],['stats','Statisztika'],['xp','XP & Szint']] },
  ];
  const catIcon = (c, size) => c.icon
    ? <img src={c.icon} alt="" style={{ width:size, height:size, borderRadius:'28%', objectFit:'contain', background:'#fff', flexShrink:0 }} />
    : <span style={{ width:size, height:size, borderRadius:'28%', background:DNR_HUB_INK, color:'#fff', display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:Math.round(size * 0.34), letterSpacing:'0.02em', flexShrink:0 }}>DNR</span>;
  const [category, setCategory] = React.useState('general');""")
rep("""        {tab === 'growth'   && <AdminGrowth />}
        {tab === 'stats'    && <AdminStats />}
        {tab === 'partik'   && <AdminParties />}
        {tab === 'seasons'  && <AdminSeasons />}
        {tab === 'zene'     && <AdminZene />}
        {tab === 'rooms'    && <AdminRooms />}
        {tab === 'message'  && <AdminMessage />}
        {tab === 'settings' && <AdminSettings setTheme={setTheme} currentTheme={currentTheme} />}""",
"""        {tab === 'growth'   && <AdminGrowth />}
        {tab === 'stats'    && <AdminStats />}
        {tab === 'partik'   && <AdminParties />}
        {tab === 'seasons'  && <React.Fragment><AdminSeasons /><div style={{ padding:'0 16px 16px' }}><AdminHomeToggles only="season" /></div></React.Fragment>}
        {tab === 'zene'     && <AdminZene />}
        {tab === 'rooms'    && <AdminRooms />}
        {tab === 'message'  && <AdminMessage />}
        {tab === 'hub'      && <div style={{ padding:'2px 16px 16px' }}><AdminHomeToggles only="hub" /></div>}
        {tab === 'settings' && <AdminSettings />}
        {tab === 'gamesSettings' && <AdminGamesSettings setTheme={setTheme} currentTheme={currentTheme} />}
        {tab === 'eventsTheme' && <AdminAppTheme app="events" />}
        {tab === 'pubTheme'    && <AdminAppTheme app="pub" />}
        {tab === 'boxTheme'    && <AdminAppTheme app="box" />}""")

# oldalsáv: app-fejléc ikonnal; egy-fülű app = maga a fejléc a gomb
rep("""            {CATEGORIES.map(c => (
              <div key={c.key} style={{ display:'flex', flexDirection:'column', gap:2 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:11, letterSpacing:'0.14em', textTransform:'uppercase', color:T.inkSoft, padding:'0 12px 6px' }}>{c.label}</div>
                {c.tabs.map(([k, label]) => {""",
"""            {CATEGORIES.map(c => c.tabs.length === 1 ? (() => {
              const k = c.tabs[0][0], on = tab === k;
              return (
                <button key={c.key} data-admin-tab={k} data-admin-cat={c.key} aria-current={on ? 'page' : undefined} onClick={() => { setCategory(c.key); setTab(k); }}
                  style={{ display:'flex', alignItems:'center', gap:10, textAlign:'left', padding:'7px 12px 7px 8px', margin:'-7px 0', borderRadius:12, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize:13.5, background: on ? T.surface : 'transparent', color:T.ink, boxShadow: on ? T.shadowPill : 'none' }}>
                  {catIcon(c, 28)}
                  <span style={{ flex:1, minWidth:0 }}>{c.label}</span>
                  {on && <span style={{ width:4, height:16, borderRadius:2, background:T.mint, flexShrink:0 }} />}
                </button>
              );
            })() : (
              <div key={c.key} data-admin-cat={c.key} style={{ display:'flex', flexDirection:'column', gap:2 }}>
                <div style={{ display:'flex', alignItems:'center', gap:10, fontFamily:T.font, fontWeight:900, fontSize:13.5, color:T.ink, padding:'0 12px 6px 8px' }}>
                  {catIcon(c, 28)}
                  <span>{c.label}</span>
                </div>
                {c.tabs.map(([k, label]) => {""")
rep("""                      {label}
                    </button>
                  );
                })}
              </div>
            ))}
          </nav>""", """                      {label}
                    </button>
                  );
                })}
              </div>
            ))}
          </nav>""")
# a lap fejléce: egy-fülű appnál az app neve, különben „App · Fül"
rep("""            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:T.ink, padding:'8px 16px 4px' }}>{(activeCategory.tabs.find(([k]) => k === tab) || [])[1]}</div>""",
"""            <div data-admin-title style={{ display:'flex', alignItems:'center', gap:12, fontFamily:T.font, fontWeight:900, fontSize:22, color:T.ink, padding:'8px 16px 4px' }}>
              {catIcon(activeCategory, 34)}
              <span>{activeCategory.tabs.length === 1 ? activeCategory.label : <React.Fragment><span style={{ color:T.inkSoft }}>{activeCategory.label} · </span>{(activeCategory.tabs.find(([k]) => k === tab) || [])[1]}</React.Fragment>}</span>
            </div>""")
# telefon: görgethető app-sáv ikonnal + al-fülek csak több fülnél
rep("""        {/* Fix kategória-sáv — mindig 3 elem, nem görgethető */}
        <div style={{ padding:'10px 16px 0', width:'100%', maxWidth:ADMIN_BODY_MAX, margin:'0 auto', boxSizing:'border-box' }}>
          <div style={{ display:'flex', background:T.surface, borderRadius:16, padding:4, gap:4, boxShadow:T.shadow }}>
            {CATEGORIES.map(c => (
              <button key={c.key} onClick={() => selectCategory(c.key)} style={{ flex:1, padding:'10px 0', borderRadius:12, border:'none', fontFamily:T.font, fontWeight:900, fontSize:13.5, cursor:'pointer', background: category===c.key ? T.mint : 'transparent'""",
"""        {/* App-sáv (v10.420): kilenc kategória nem fér egy sorba — vízszintesen görget,
            minden app az ikonjával. A kiválasztott kártya tömör menta. */}
        <div style={{ padding:'10px 16px 0', width:'100%', maxWidth:ADMIN_BODY_MAX, margin:'0 auto', boxSizing:'border-box' }}>
          <div data-admin-catbar style={{ display:'flex', background:T.surface, borderRadius:16, padding:4, gap:4, boxShadow:T.shadow, overflowX:'scroll', scrollbarWidth:'none', WebkitOverflowScrolling:'touch' }}>
            {CATEGORIES.map(c => (
              <button key={c.key} data-admin-cat={c.key} onClick={() => selectCategory(c.key)} style={{ flexShrink:0, display:'flex', alignItems:'center', gap:7, whiteSpace:'nowrap', padding:'7px 12px 7px 7px', borderRadius:12, border:'none', fontFamily:T.font, fontWeight:900, fontSize:13, cursor:'pointer', background: category===c.key ? T.mint : 'transparent'""")
open(P, 'w', encoding='utf-8').write(s)
print('OK part 1')

# ── part 2: telefonos app-sáv ikonnal, al-fülek csak több fülnél ──
s = open(P, encoding='utf-8').read()
rep("""              <button key={c.key} data-admin-cat={c.key} onClick={() => selectCategory(c.key)} style={{""",
    """              <button key={c.key} data-admin-cat={c.key} onClick={e => { selectCategory(c.key); try { e.currentTarget.scrollIntoView({ inline:'center', block:'nearest', behavior:'smooth' }); } catch(err) {} }} style={{""")
rep("""transition:'all .2s', WebkitTapHighlightColor:'transparent' }}>
                {c.label}
              </button>""", """transition:'all .2s', WebkitTapHighlightColor:'transparent' }}>
                {catIcon(c, 26)}
                {c.label}
              </button>""")
rep("""        {/* Dinamikus al-sáv — a kiválasztott kategória elemei, szükség esetén görgethető */}
        <div style={{ padding:'14px 16px 14px', width:'100%', maxWidth:ADMIN_BODY_MAX, margin:'0 auto', boxSizing:'border-box' }}>
          <div style={{ display:'flex', gap:8, overflowX:'auto',""",
"""        {/* Dinamikus al-sáv — a kiválasztott app fülei; egy-fülű appnál nincs mit választani */}
        {activeCategory.tabs.length > 1 ? (
        <div style={{ padding:'14px 16px 14px', width:'100%', maxWidth:ADMIN_BODY_MAX, margin:'0 auto', boxSizing:'border-box' }}>
          <div data-admin-subtabs style={{ display:'flex', gap:8, overflowX:'auto',""")
rep("""                {label}
              </button>
            ))}
          </div>
        </div>
          <div style={{ flex:1, overflowY:'auto' }}>""", """                {label}
              </button>
            ))}
          </div>
        </div>
        ) : <div style={{ height:8, flexShrink:0 }} />}
          <div style={{ flex:1, overflowY:'auto' }}>""")
open(P, 'w', encoding='utf-8').write(s)
print('OK part 2')

# ── part 3: a Hirdetmény a DNR KÖZPONTBA költözik (eddig a Games főoldalán állt) ──
s = open(P, encoding='utf-8').read()
rep("""  const [announcement, setAnnouncement] = React.useState(null);
  React.useEffect(() => {
    if (typeof window.onAnnouncement === 'function') {
      const unsub = window.onAnnouncement(d => {
        const ok = d && d.active && d.title && (!d.until || new Date(d.until + 'T23:59:59') >= new Date()) ? d : null;
        if (ok && typeof window._bohAnnounceNotif === 'function') window._bohAnnounceNotif(ok);
        setAnnouncement(ok);
      });
      return () => unsub();
    }
  }, []);
  const toggleSplash""", """  const toggleSplash""")
a = s.index("          {announcement && (\n            <div style={{ width:'100%', maxWidth:360")
b = s.index("          )}\n", a) + len("          )}\n")
s = s[:a] + s[b:]
rep("""function DnrHubScreen({ onOpen }) {""", """// ── Hirdetmény (v10.420) ────────────────────────────────────────────────────
// MINDEN appot érint, ezért a DNR KÖZPONTBAN áll (eddig a DNR Games főoldalán volt,
// és aki egyenesen egy másik appot nyitott, sosem látta). A sáv bezárható: a bezárás
// a TARTALOMRA szól (cím + szöveg), tehát egy új hirdetmény megint előjön.
function useAnnouncement() {
  const [a, setA] = React.useState(null);
  React.useEffect(() => {
    if (typeof window.onAnnouncement !== 'function') return;
    const unsub = window.onAnnouncement(d => {
      const ok = d && d.active && d.title && (!d.until || new Date(d.until + 'T23:59:59') >= new Date()) ? d : null;
      if (ok && typeof window._bohAnnounceNotif === 'function') window._bohAnnounceNotif(ok);
      setA(ok);
    });
    return () => { try { unsub(); } catch(e) {} };
  }, []);
  return a;
}
function HubAnnouncement() {
  const a = useAnnouncement();
  const key = a ? (a.title || '') + '|' + (a.body || '') : '';
  const [closed, setClosed] = React.useState(() => { try { return localStorage.getItem('boh_ann_closed') || ''; } catch(e) { return ''; } });
  if (!a || closed === key) return null;
  const close = () => { setClosed(key); try { localStorage.setItem('boh_ann_closed', key); } catch(e) {} };
  return (
    <div data-hub-announcement role="status" style={{ flexShrink:0, display:'flex', alignItems:'flex-start', gap:10, background:T.accent, borderRadius:16, padding:'10px 8px 10px 14px', boxShadow:`0 4px 16px ${T.accent}55`, maxWidth:560, width:'100%', alignSelf:'center', boxSizing:'border-box' }}>
      <span aria-hidden="true" style={{ fontSize:18, lineHeight:1.2 }}>📣</span>
      <div style={{ flex:1, minWidth:0 }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13.5, color:'#fff', lineHeight:1.3, display:'-webkit-box', WebkitLineClamp:1, WebkitBoxOrient:'vertical', overflow:'hidden', wordBreak:'break-word' }}>{a.title}</div>
        {a.body && <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:'rgba(255,255,255,0.92)', marginTop:2, lineHeight:1.35, display:'-webkit-box', WebkitLineClamp:2, WebkitBoxOrient:'vertical', overflow:'hidden', wordBreak:'break-word' }}>{a.body}</div>}
      </div>
      <button data-hub-announcement-close aria-label="Hirdetmény bezárása" onClick={close}
        style={{ width:30, height:30, flexShrink:0, borderRadius:10, border:'none', background:'rgba(255,255,255,0.22)', color:'#fff', display:'grid', placeItems:'center', cursor:'pointer', WebkitTapHighlightColor:'transparent' }}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="3" strokeLinecap="round" aria-hidden="true"><path d="M18 6L6 18M6 6l12 12"/></svg>
      </button>
    </div>
  );
}
function DnrHubScreen({ onOpen }) {""")
rep("""          <HubGreeting />
""", """          <HubGreeting />
          <HubAnnouncement />
""")
rep("""<div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>Hirdetmény a főoldalon</div>""",
    """<div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>Hirdetmény a DNR központban</div>""")
open(P, 'w', encoding='utf-8').write(s)
print('OK part 3')

# ── part 4: kivágott ikonok, görgethető oldalsáv, dupla emoji nélküli hirdetmény ──
s = open(P, encoding='utf-8').read()
for k, z in [("'assets/dnr_games_icon.png'", 1.25), ("'assets/dnr_events_icon.png'", 1.9), ("'assets/dnr_tipp_icon.png'", 1.9),
             ("'assets/dnr_bingo_icon.png'", 1.9), ("'assets/dnr_pub_icon.png'", 1.9), ("'assets/dnr_liga_icon.png'", 1.9)]:
    rep("icon:%s, tabs:" % k, "icon:%s, zoom:%s, tabs:" % (k, z))
rep("""  const catIcon = (c, size) => c.icon
    ? <img src={c.icon} alt="" style={{ width:size, height:size, borderRadius:'28%', objectFit:'contain', background:'#fff', flexShrink:0 }} />""",
"""  // A négyzetes app-ikonokon a rajz a kép közepén ül, nagy fehér margóval — kicsiben
  // alig látszana, ezért a `zoom` rávág (a kerek Tortán/BOX logó kitölti a helyét).
  const catIcon = (c, size) => c.icon
    ? <span style={{ width:size, height:size, borderRadius:'28%', overflow:'hidden', background:'#fff', flexShrink:0, display:'grid', placeItems:'center' }}>
        <img src={c.icon} alt="" style={{ width:size * (c.zoom || 1), height:size * (c.zoom || 1), maxWidth:'none', objectFit:'contain' }} />
      </span>""")
rep("""<nav data-admin-nav aria-label="Admin menü" style={{ position:'sticky', top:0, width:236, flexShrink:0, padding:'18px 10px 32px 8px', boxSizing:'border-box', display:'flex', flexDirection:'column', gap:18 }}>""",
    """<nav data-admin-nav aria-label="Admin menü" style={{ position:'sticky', top:0, maxHeight:'calc(var(--app-h, 100dvh) - 80px)', overflowY:'auto', scrollbarWidth:'thin', width:236, flexShrink:0, padding:'18px 10px 32px 8px', boxSizing:'border-box', display:'flex', flexDirection:'column', gap:14 }}>""")
rep("""      <span aria-hidden="true" style={{ fontSize:18, lineHeight:1.2 }}>📣</span>""",
    """      {/* a sablonok címe többnyire emojival indul — ott a 📣 dupla jel lenne */}
      {!((a.title || '').codePointAt(0) > 0x2100) && <span aria-hidden="true" style={{ fontSize:18, lineHeight:1.2 }}>📣</span>}""")
open(P, 'w', encoding='utf-8').write(s)
print('OK part 4')

# ── part 5: az al-fülek az app neve alá húzva, tömörebben ──
s = open(P, encoding='utf-8').read()
rep("style={{ textAlign:'left', padding:'9px 12px', borderRadius:10, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight: on ? 900 : 700, fontSize:14,",
    "style={{ textAlign:'left', padding:'7px 12px 7px 30px', borderRadius:10, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight: on ? 900 : 700, fontSize:13.5,")
open(P, 'w', encoding='utf-8').write(s)
print('OK part 5')

# ── part 6: a rávágott ikon KÖZÉPRE (a túllógó grid-elem a bal felső sarokhoz igazodott) ──
s = open(P, encoding='utf-8').read()
rep("""    ? <span style={{ width:size, height:size, borderRadius:'28%', overflow:'hidden', background:'#fff', flexShrink:0, display:'grid', placeItems:'center' }}>
        <img src={c.icon} alt="" style={{ width:size * (c.zoom || 1), height:size * (c.zoom || 1), maxWidth:'none', objectFit:'contain' }} />""",
"""    ? <span style={{ position:'relative', width:size, height:size, borderRadius:'28%', overflow:'hidden', background:'#fff', flexShrink:0, display:'inline-block' }}>
        <img src={c.icon} alt="" style={{ position:'absolute', left:'50%', top:'50%', transform:'translate(-50%, -50%)', width:size * (c.zoom || 1), height:size * (c.zoom || 1), maxWidth:'none', objectFit:'contain' }} />""")
open(P, 'w', encoding='utf-8').write(s)
print('OK part 6')
