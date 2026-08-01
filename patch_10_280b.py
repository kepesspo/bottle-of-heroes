#!/usr/bin/env python3
# v10.280b — a korty-plafon az ALLAPOTFRISSITOBEN dolgozzon, ne a renderbol
#
# A HIBA
#   Ha gyorsan egymas utan koppintasz a `+`-ra, a plafon atlephet. Mert:
#   a `disabled` es a `tele` orzes a RENDER pillanataban keletkezett ertekbol
#   dolgozik, a React viszont kotegeli az allapotfrissiteseket. Harom gyors
#   koppintas egy kotegbe esik, ahol a gomb meg nincs letiltva es a `tele` meg
#   hamis — mindharom lefut, es 1 helyett 3 korty keletkezik.
#   (Merve: 3 koppintas Kecsire + 1 Tothra -> "2 iszik · 4 korty", pedig
#   1-es plafonnal "2 iszik · 2 korty" a helyes.)
#
# A JAVITAS
#   A plafont a `setDrinks` FUGGVENY-alaku frissiteseben ellenorizzuk, ahol a
#   `d` mindig a legfrissebb allapot — fuggetlenul attol, hany koppintas esett
#   egy kotegbe. A `disabled` marad, de mar csak vizualis jelzes, nem a vedelmi
#   vonal.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""function DrinkDistributor({ players, onFinish, title, max }) {
  const [drinks, setDrinks] = React.useState({});
  const add = (pid) => setDrinks(d => ({ ...d, [pid]: (d[pid]||0)+1 }));""",
    """function DrinkDistributor({ players, onFinish, title, max }) {
  const [drinks, setDrinks] = React.useState({});
  // A plafon ITT dol el, nem a renderben: gyors, egymas utani koppintasok egy
  // React-kotegbe esnek, ahol a gomb meg nincs letiltva. A fuggveny-alaku
  // frissitesben viszont `d` mindig a legfrissebb allapot. Lasd patch_10_280b.py
  const add = (pid) => setDrinks(d => {
    const cur = d[pid]||0;
    if (max != null && cur >= max) return d;
    return { ...d, [pid]: cur+1 };
  });""",
    'add plafon')

open(P, 'w', encoding='utf-8').write(src)
print('OK — a plafon kotegelt koppintasnal is tart')
