#!/usr/bin/env python3
# v10.249 — a MENÜ lap megint a saját tartalmához igazodik; a Büntetés hozzá méri magát
#
# MIT RONTOTTAM EL A v10.244-BEN
# A két lapot úgy hoztam egy magasságba, hogy MINDKETTŐRE ráraktam egy fix
# értéket: min(365px, 82vh). A 365-öt Chromiumban mértem (402×874), ott pont
# ennyi volt a MENÜ "vezérlés" fülének tartalma. Készüléken viszont más a
# betűmetrika és a dinamikus betűméret, ott a tartalom MAGASABB — így a MENÜ
# elkezdett görgetni, és alul levágta a gombsort.
#
# Ez pontosan az a hiba, amit magam ellen írtam a docs/safe-area.md-ben: egy
# böngészőben mért szám nem szabály, csak egy készülék pillanatnyi állapota.
#
# A JAVÍTÁS
# A MENÜ megint a saját tartalmához igazodik (nincs rákényszerített magasság,
# marad a 82vh felső korlát). A Büntetés lap pedig nem egy számhoz, hanem a
# MENÜ TÉNYLEGESEN MÉRT magasságához igazodik: a SheetOverlay megméri magát és
# visszaszól. Ez azért működik megbízhatóan, mert a Büntetés CSAK a MENÜ-ből
# nyitható — mire szükség van a számra, már megmértük.
#
# Ha valamiért mégsem lenne mért érték, a Büntetés a saját tartalmához igazodik
# (a 82vh korláttal) — vagyis rosszabb esetben is ugyanaz, mint a v10.244 előtt.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1. a fix szám kikerül, helyette mérés ──
sub("""// A JATEK KOZBENI lapok (MENÜ, Büntetés) egyforma magasak. A mertek a MENÜ
// "vezérlés" fulenek tartalma volt — ezt rogzitjuk, hogy a Buntetes ne a
// jatekosok szamatol fuggjon. Egy szam, egy helyen.
const PLAY_SHEET_H = 'min(365px, 82vh)';

function SheetOverlay({ onClose, children, footer, title, zIndex, height }) {""",
    """function SheetOverlay({ onClose, children, footer, title, zIndex, height, onHeight }) {""",
    'PLAY_SHEET_H torlese')

# ── 2. SheetOverlay: megmeri magat es visszaszol ──
sub("""  const translateY = closing ? '100%' : `${dragY}px`;
  const opacity = closing ? 0 : Math.max(0, 1 - dragY / 300);""",
    """  // A lap megmeri magat, ha kerik. Igy tud egy MASIK lap ugyanolyan magas
  // lenni, anelkul hogy barhova beegetnenk egy szamot — kesziteken mas a
  // betumetrika, ott egy bongeszoben mert ertek levagna a tartalmat.
  // Ketszer merunk: rogton, es egy kepkockaval kesobb (kesoi betu-layout).
  React.useLayoutEffect(() => {
    if (typeof onHeight !== 'function' || height) return;
    let raf = 0;
    const report = () => {
      const el = sheetRef.current;
      if (el) onHeight(Math.round(el.getBoundingClientRect().height));
    };
    report();
    raf = requestAnimationFrame(report);
    return () => cancelAnimationFrame(raf);
  }, [onHeight, height]);

  const translateY = closing ? '100%' : `${dragY}px`;
  const opacity = closing ? 0 : Math.max(0, 1 - dragY / 300);""",
    'SheetOverlay meres')

# ── 3. a MENÜ megint a sajat tartalmahoz igazodik, es megmeri magat ──
sub("""          <SheetOverlay onClose={() => setShowMenu(false)} height={PLAY_SHEET_H}>""",
    """          <SheetOverlay onClose={() => setShowMenu(false)} onHeight={setMenuSheetH}>""",
    'menu lap')

# ── 4. a Buntetes a MERT magassaghoz igazodik ──
sub("""function PenaltySheet({ players, onClose, onFinish }) {""",
    """function PenaltySheet({ players, onClose, onFinish, height }) {""",
    'PenaltySheet szignatura')

sub("""    <SheetOverlay onClose={onClose} title="Büntetés — ki igyon?" height={PLAY_SHEET_H} footer={""",
    """    <SheetOverlay onClose={onClose} title="Büntetés — ki igyon?" height={height} footer={""",
    'PenaltySheet magassag')

sub("""        <PenaltySheet players={players || []} onClose={() => setPenaltyOpen(false)} onFinish={applyPenalty} />""",
    """        <PenaltySheet players={players || []} onClose={() => setPenaltyOpen(false)} onFinish={applyPenalty}
          height={menuSheetH ? menuSheetH + 'px' : undefined} />""",
    'PenaltySheet hasznalat')

sub("""  const [penaltyOpen, setPenaltyOpen] = useState(false);""",
    """  const [penaltyOpen, setPenaltyOpen] = useState(false);
  // A MENÜ lap MERT magassaga — ehhez igazodik a Buntetes lap. A Buntetes csak
  // a MENÜ-bol nyithato, tehat mire kell, mar megvan. Lasd patch_10_249.py
  const [menuSheetH, setMenuSheetH] = useState(null);""",
    'menuSheetH state')

sub("const APP_VERSION = 'v10.248';", "const APP_VERSION = 'v10.249';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — a MENÜ a sajat tartalmahoz, a Buntetes a MERT magassaghoz igazodik')
