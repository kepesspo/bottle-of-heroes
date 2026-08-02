#!/usr/bin/env python3
# v10.289 — Szólánc: 10 szó maximum, és az első körben csak 1 szó
#
# A játékos tesztelése után elég 10 szó — sokkal jól működik.
# Az első körben azonban 2 szó villant már, ami megzavarja az első lépést.
# Most az első szint 1 szó, és a lánc 10-ig megy.
#
# Az indikátor már dinamikus (MAX_LEN-ből épül), így az automatikusan
# alkalmazkodik. Az első szint nem jelenik meg rajta (szint 2-től kezd),
# mivel az átadás képernyőn csak a jövő szintekre vonatkozik.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("const SZ_MAX_LEN = 12;", "const SZ_MAX_LEN = 10;", 'SZ_MAX_LEN')

sub("""  const [S, setS] = React.useState(() => fresh(2, 0, true));
  const [done, setDone] = React.useState(null);
  React.useEffect(() => { setS(fresh(2, 0, true)); setDone(null); }, [gameIdx]);""",
    """  const [S, setS] = React.useState(() => fresh(1, 0, true));
  const [done, setDone] = React.useState(null);
  React.useEffect(() => { setS(fresh(1, 0, true)); setDone(null); }, [gameIdx]);""",
    'elso kor')

sub("const APP_VERSION = 'v10.288';", "const APP_VERSION = 'v10.289';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — 10 szó maximum, első körben 1 szó')
