#!/usr/bin/env python3
# v10.226 — a theme-color meta is kövesse a státuszsáv színét
#
# Tünet (a tesztedből): ELSŐ PWA-indításkor barack a státuszsáv, másodszorra
# már jó — ugyanazzal a buildel.
#
# Magyarázat: két, egymástól FÜGGETLEN mechanizmus festi azt a sávot, és eddig
# csak az egyiket állítottuk át.
#
#   1) `apple-mobile-web-app-status-bar-style: black-translucent` esetén a
#      státuszsáv ÁTLÁTSZÓ, és a mögötte lévő weblap-tartalom látszik — ezt
#      javítottuk a v10.225-ben (a gyökér-konténer háttere).
#
#   2) Amíg ez a stílus NEM érvényesül — tipikusan a legelső indításnál,
#      közvetlenül a főképernyőre mentés után —, a státuszsáv NEM átlátszó,
#      és a színét a <meta name="theme-color"> adja. Az pedig fixen a téma
#      háttere volt (#F4C57E, barack), egyetlen helyen beállítva induláskor.
#
# Ezért volt barack az első indításnál és jó a másodiknál: a második
# indításra már az (1)-es ág fut, amit korábban megjavítottunk.
#
# Javítás: a theme-color meta mostantól ugyanazt a statusBarBg értéket kapja,
# mint a festett sáv — így a két ág EGYFORMA színt ad, bármelyik érvényesül.
# (Androidon/Chrome PWA-ban a theme-color eleve a rendszersávot színezi, ott
# ez szintén javulás.)
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""  const statusBarBg = (creatingRoom || screen === 'home' || screen === 'play') ? T.bg : T.surface;
  return (""",
    """  const statusBarBg = (creatingRoom || screen === 'home' || screen === 'play') ? T.bg : T.surface;
  // A <meta name="theme-color"> a MÁSIK út, ahogy a rendszer a státuszsávot
  // színezi: akkor számít, amikor a sáv NEM átlátszó (iOS-en tipikusan a
  // legelső indításnál, amíg a black-translucent stílus nem érvényesül;
  // Androidon mindig). Ha ez eltér a festett sávtól, az első indítás más
  // színt mutat, mint a többi — ezért kötjük ugyanahhoz az értékhez.
  React.useEffect(() => {
    const tc = document.querySelector('meta[name="theme-color"]');
    if (tc) tc.setAttribute('content', statusBarBg);
  }, [statusBarBg]);
  return (""",
    'theme-color kovesse a statusBarBg-t')

sub("const APP_VERSION = 'v10.225';", "const APP_VERSION = 'v10.226';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — theme-color meta a statusBarBg-t koveti')
