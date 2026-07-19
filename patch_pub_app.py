#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# DNR Pub önálló appként: ?screen=bar deep link — saját ikon, manifest és cím
# (mint az Events/Box), a boot közvetlenül a Pub képernyőre visz, vissza-gomb nélkül.
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'expected %d, found %d for: %r' % (count, n, old[:80])
    src = src.replace(old, new)

# ── 1) Ikon-választó a headben ──
rep("""    var isBox=q.indexOf('screen=dnrbox')!==-1;
    if(isEv){""",
"""    var isBox=q.indexOf('screen=dnrbox')!==-1;
    var isBar=q.indexOf('screen=bar')!==-1;
    if(isEv){""")

rep("""    } else if(isBox){
      document.write('<link rel="apple-touch-icon" sizes="1024x1024" href="assets/dnr_box_icon.png"/>');
      document.write('<link rel="icon" type="image/png" sizes="512x512" href="assets/dnr_box_icon.png"/>');
    } else {""",
"""    } else if(isBox){
      document.write('<link rel="apple-touch-icon" sizes="1024x1024" href="assets/dnr_box_icon.png"/>');
      document.write('<link rel="icon" type="image/png" sizes="512x512" href="assets/dnr_box_icon.png"/>');
    } else if(isBar){
      document.write('<link rel="apple-touch-icon" sizes="1024x1024" href="assets/dnr_pub_icon.png"/>');
      document.write('<link rel="icon" type="image/png" sizes="512x512" href="assets/dnr_pub_icon.png"/>');
    } else {""")

# ── 2) Manifest-választó ──
rep("""var box=q.indexOf('screen=dnrbox')!==-1;document.write('<link rel="manifest" href="'+(ev?'manifest-events.json':box?'manifest-dnrbox.json':'manifest.json')+'"/>');""",
"""var box=q.indexOf('screen=dnrbox')!==-1;var bar=q.indexOf('screen=bar')!==-1;document.write('<link rel="manifest" href="'+(ev?'manifest-events.json':box?'manifest-dnrbox.json':bar?'manifest-bar.json':'manifest.json')+'"/>');""")

# ── 3) apple-mobile-web-app-title ──
rep("""var box=q.indexOf('screen=dnrbox')!==-1;document.write('<meta name="apple-mobile-web-app-title" content="'+(ev?'DNR Events':box?'DNR BOX':'Bottle of Heroes')+'"/>');""",
"""var box=q.indexOf('screen=dnrbox')!==-1;var bar=q.indexOf('screen=bar')!==-1;document.write('<meta name="apple-mobile-web-app-title" content="'+(ev?'DNR Events':box?'DNR BOX':bar?'DNR Pub':'Bottle of Heroes')+'"/>');""")

# ── 4) Korai cím-felülírás (Safari "Add to Home Screen" ezt olvassa) ──
rep("""      } else if (location.search.indexOf('screen=dnrbox') !== -1) {
        document.title = 'DNR BOX';
        var mb = document.querySelector('meta[name="apple-mobile-web-app-title"]');
        if (mb) mb.setAttribute('content', 'DNR BOX');
      }""",
"""      } else if (location.search.indexOf('screen=dnrbox') !== -1) {
        document.title = 'DNR BOX';
        var mb = document.querySelector('meta[name="apple-mobile-web-app-title"]');
        if (mb) mb.setAttribute('content', 'DNR BOX');
      } else if (location.search.indexOf('screen=bar') !== -1) {
        document.title = 'DNR Pub';
        var mp = document.querySelector('meta[name="apple-mobile-web-app-title"]');
        if (mp) mp.setAttribute('content', 'DNR Pub');
      }""")

# ── 5) Boot routing: ?screen=bar → Pub képernyő, onboarding kihagyva ──
rep("""  const _jukebox = _initScreen === 'dnrbox';
  const [screen, setScreen] = useState(() => _initRoom ? 'observer' : _jukebox ? 'jukebox' : _deepLink ? 'log' : 'home');""",
"""  const _jukebox = _initScreen === 'dnrbox';
  const _barApp = _initScreen === 'bar';
  const [screen, setScreen] = useState(() => _initRoom ? 'observer' : _jukebox ? 'jukebox' : _barApp ? 'bar' : _deepLink ? 'log' : 'home');""")

rep("    try { return !localStorage.getItem('boh_onboarded') && !_initRoom && !_deepLink && !_jukebox; } catch(e) { return false; }",
    "    try { return !localStorage.getItem('boh_onboarded') && !_initRoom && !_deepLink && !_jukebox && !_barApp; } catch(e) { return false; }")

# ── 6) Router: deepLink prop ──
rep("{screen==='bar'      && <BarScreen      go={go} />}",
    "{screen==='bar'      && <BarScreen      go={go} deepLink={_barApp} />}")

# ── 7) BarScreen: önálló app módban nincs vissza-gomb a főnézetben ──
rep("function BarScreen({ go }) {",
    "function BarScreen({ go, deepLink }) {")

rep("""      <AppBar title={view === 'recipes' ? 'Receptek' : 'Pub'} onBack={() => { if (view === 'recipes') setView('own'); else go('home'); }} />""",
"""      <AppBar title={view === 'recipes' ? 'Receptek' : (deepLink ? 'DNR Pub' : 'Pub')} onBack={deepLink && view !== 'recipes' ? null : () => { if (view === 'recipes') setView('own'); else go('home'); }} />""")

# ── 8) Verziobump ──
rep("const APP_VERSION = 'v9.984';", "const APP_VERSION = 'v9.985';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — DNR Pub standalone app applied')
