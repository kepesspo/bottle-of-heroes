# v10.430: Gender Reveal — élő képvetítő kivetítőre (jelszó, vetítő, operátor, admin)
import sys
p = 'app.src.html'
s = open(p, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (old[:80], n)
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.429';", "const APP_VERSION = 'v10.430';")
# 1) ?screen= aliasok
rep("        events:'events', esemenyek:'events', calendar:'calendar',\n",
    "        events:'events', esemenyek:'events', calendar:'calendar',\n"
    "        reveal:'reveal', genderreveal:'reveal', 'gender-reveal':'reveal', gender:'reveal', vetito:'reveal', kivetito:'reveal',\n")
# 2) ikon, manifest, cím
rep("    var isLiga=q.indexOf('screen=liga')!==-1;\n    if(isEv){",
    "    var isLiga=q.indexOf('screen=liga')!==-1;\n    var isReveal=q.indexOf('screen=reveal')!==-1;\n    if(isReveal){\n"
    "      document.write('<link rel=\"apple-touch-icon\" sizes=\"1024x1024\" href=\"assets/dnr_reveal_app.png\"/>');\n"
    "      document.write('<link rel=\"icon\" type=\"image/png\" sizes=\"512x512\" href=\"assets/dnr_reveal_app.png\"/>');\n"
    "    } else if(isEv){")
rep("var lg=q.indexOf('screen=liga')!==-1;document.write('<link rel=\"manifest\" href=\"'+(ev?",
    "var lg=q.indexOf('screen=liga')!==-1;var rv=q.indexOf('screen=reveal')!==-1;document.write('<link rel=\"manifest\" href=\"'+(rv?'manifest-reveal.json':ev?")
rep("""      } else if (location.search.indexOf('screen=liga') !== -1) {
        document.title = 'DNR Liga';""",
"""      } else if (location.search.indexOf('screen=reveal') !== -1) {
        document.title = 'Gender Reveal';
        var mrv = document.querySelector('meta[name="apple-mobile-web-app-title"]');
        if (mrv) mrv.setAttribute('content', 'Gender Reveal');
      } else if (location.search.indexOf('screen=liga') !== -1) {
        document.title = 'DNR Liga';""")
# 3) nyitókép
rep("""    else if(q.indexOf('screen=liga')!==-1)
      brand={icon:'assets/dnr_liga_mark.png', title:'DNR Liga', tag:'Ranglista. Szezonok. Szintek.'};""",
"""    else if(q.indexOf('screen=liga')!==-1)
      brand={icon:'assets/dnr_liga_mark.png', title:'DNR Liga', tag:'Ranglista. Szezonok. Szintek.'};
    else if(q.indexOf('screen=reveal')!==-1)
      brand={icon:'assets/dnr_reveal_mark.png', title:'Gender Reveal', tag:'Fiú vagy lány?'};""")
# 4) téma: saját app
rep("bingo:'bingo', tipp:'tipp', torta:'torta', games:'games' };\n    if (MAP[sc]) app = MAP[sc];",
    "bingo:'bingo', tipp:'tipp', torta:'torta', games:'games', reveal:'reveal' };\n    if (MAP[sc]) app = MAP[sc];")
rep("const BOH_THEME_APPS = ['hub', 'games', 'events', 'torta', 'tipp', 'bingo', 'box', 'pub', 'liga'];",
    "const BOH_THEME_APPS = ['hub', 'games', 'events', 'torta', 'tipp', 'bingo', 'box', 'pub', 'liga', 'reveal'];")
rep("  if (sc === 'bingo' || sc === 'tipp' || sc === 'torta') return sc;\n  return 'games';",
    "  if (sc === 'bingo' || sc === 'tipp' || sc === 'torta' || sc === 'reveal') return sc;\n  return 'games';")
rep("bingo:'bingo', tipp:'tipp', torta:'torta', games:'games' })[sc] || 'hub';",
    "bingo:'bingo', tipp:'tipp', torta:'torta', games:'games', reveal:'reveal' })[sc] || 'hub';")
rep("  { key:'liga',   label:'DNR Liga',    icon:'assets/dnr_liga_app.png',   zoom:1.25 },\n];",
    "  { key:'liga',   label:'DNR Liga',    icon:'assets/dnr_liga_app.png',   zoom:1.25 },\n  { key:'reveal', label:'Gender Reveal', icon:'assets/dnr_reveal_app.png', zoom:1.25 },\n];")
# 5) DNR központ + admin lista
rep("  { screen:'stats',   name:'DNR Liga',   icon:'assets/dnr_liga_app.png',   sub: c => c.liga ? `Ranglista · ${c.liga}` : 'Ranglista, szezonok, szintek' },\n];",
    "  { screen:'stats',   name:'DNR Liga',   icon:'assets/dnr_liga_app.png',   sub: c => c.liga ? `Ranglista · ${c.liga}` : 'Ranglista, szezonok, szintek' },\n"
    "  { screen:'reveal',  name:'Gender Reveal', icon:'assets/dnr_reveal_app.png', sub: () => 'Élő képvetítő kivetítőre' },\n];")
rep("  const HUB_ORDER = ['log', 'torta', 'tipp', 'bingo', 'jukebox', 'bar', 'stats'];",
    "  const HUB_ORDER = ['log', 'torta', 'tipp', 'bingo', 'jukebox', 'bar', 'stats', 'reveal'];")
# 6) Admin kategória
rep("    { key:'liga', label:'DNR Liga', icon:'assets/dnr_liga_app.png', zoom:1.25, tabs:[['seasons','Szezonok'],['stats','Statisztika'],['xp','XP & Szint']] },\n  ];",
    "    { key:'liga', label:'DNR Liga', icon:'assets/dnr_liga_app.png', zoom:1.25, tabs:[['seasons','Szezonok'],['stats','Statisztika'],['xp','XP & Szint']] },\n"
    "    { key:'reveal', label:'Gender Reveal', icon:'assets/dnr_reveal_app.png', zoom:1.25, tabs:[['reveal','Gender Reveal']] },\n  ];")
rep("        {tab === 'torta' && <AdminBingo key=\"torta\" app=\"torta\" />}\n",
    "        {tab === 'torta' && <AdminBingo key=\"torta\" app=\"torta\" />}\n        {tab === 'reveal' && <AdminReveal />}\n")
rep("    { key: 'torta', label: 'DNR a tortán' }, { key: 'liga', label: 'DNR Liga' },\n",
    "    { key: 'torta', label: 'DNR a tortán' }, { key: 'liga', label: 'DNR Liga' },\n    { key: 'reveal', label: 'Gender Reveal' },\n")
# 7) BottleApp
rep("  const _ligaApp = _initScreen === 'liga';\n",
    "  const _ligaApp = _initScreen === 'liga';\n  const _revealApp = _initScreen === 'reveal';\n")
rep("_tortaApp ? 'torta' : _ligaApp ? 'stats' : _deepLink ? 'log'",
    "_tortaApp ? 'torta' : _revealApp ? 'reveal' : _ligaApp ? 'stats' : _deepLink ? 'log'")
rep("!_tippApp && !_tortaApp && !_ligaApp; } catch(e) { return false; }",
    "!_tippApp && !_tortaApp && !_ligaApp && !_revealApp; } catch(e) { return false; }")
rep("  const HUB_APP_SCREENS = ['log', 'create', 'jukebox', 'bar', 'bingo', 'tipp', 'torta', 'stats', 'admin', 'observer'];",
    "  const HUB_APP_SCREENS = ['log', 'create', 'jukebox', 'bar', 'bingo', 'tipp', 'torta', 'reveal', 'stats', 'admin', 'observer'];")
rep("  const order = ['hub','home','stats','bingo','tipp','torta','bar','log','jukebox','create','admin',",
    "  const order = ['hub','home','stats','bingo','tipp','torta','reveal','bar','log','jukebox','create','admin',")
rep("        {screen==='torta'    && <BingoScreen    key=\"torta\" app=\"torta\" go={go} deepLink={_tortaApp} />}\n",
    "        {screen==='torta'    && <BingoScreen    key=\"torta\" app=\"torta\" go={go} deepLink={_tortaApp} />}\n"
    "        {screen==='reveal'   && <RevealScreen   go={go} deepLink={_revealApp} />}\n")
rep("                 : _q.indexOf('screen=liga')   !== -1 ? 'liga'\n",
    "                 : _q.indexOf('screen=liga')   !== -1 ? 'liga'\n                 : _q.indexOf('screen=reveal') !== -1 ? 'reveal'\n")
# 8) A komponensek — a Pub űrlapja elé (a canvasToCompressedURL már fent van)
block = open(sys.argv[1], encoding='utf-8').read()
rep("// ── Pub: saját keverés űrlap (új / szerkesztés)", block + "\n// ── Pub: saját keverés űrlap (új / szerkesztés)")
rep("    const t = setTimeout(() => advRef.current(), secs * 1000);",
    "    // teszt-fogódzó: window.__revealSpeed (pl. 0.05) az egész ütemet skálázza\n    const t = setTimeout(() => advRef.current(), secs * 1000 * ((typeof window !== 'undefined' && window.__revealSpeed) || 1));")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
