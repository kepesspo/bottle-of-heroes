# v10.347b - A chip-sor NEM fer ki ot felirattal minden telefonon (mert)
#
# ⚠️ MERT, nem ranezesre. A chipek termeszetes (min-content) szelessege:
#     Osszes 55 · Torles 50 · Veletlen 90 · Szuro 47 · DNR 55  + 4 x 8 px res
#   = 329 px szuro nelkul, es 351 px, ha a Szurore rakerul a szamlalo
#     („Szuro (2)" = 69 px, a szam MINDEGY, egyjegyunel mindig 69).
#
#   A rendelkezesre allo sor a kepernyo - 32 px belso margo:
#     360 px -> 328   375 px -> 343   390 px -> 358   402 px -> 370
#
#   Tehat 390 px-tol felfele belefer a legrosszabb eset is; 375 es 360 px-en
#   NEM. A regi (negy chipes) sor kifert, ezert ez REGRESSZIO lenne: 360 px-en
#   a „Szuro (2)" felirata csendben levagodott (a gomb `scrollWidth`-je nem no,
#   ezert a puszta „kilog-e a sorbol" meres sem fogta volna meg).
#
# A megoldas nem a betumeret csokkentese, hanem TORDELES: 390 px alatt a DNR a
# teljes szelesseget kapja a sor ALATT (`grid-column:1/-1`). Ott meg feltunobb
# is, es a negy regi chip pontosan ugy all, ahogy eddig.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# ── 1. A sor CSS-be kerul, hogy media query-t tudjon vinni ──────────────────
sub1(
"""    .grid-players { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }""",
"""    /* Jatekvalaszto szurosor: Osszes | Torles | Veletlen | Szuro | DNR.
       ⚠️ Ot felirat 390 px alatt NEM fer ki (a legrosszabb eset — szamlalos
       „Szuro (2)" — 351 px min-contentet ker, egy 375 px-es telefon sora 343).
       Ezert keskeny kepernyon a DNR a sor ALA kerul, teljes szelessegben; a
       negy regi chip igy pontosan ugy all, ahogy a DNR gomb elott allt. */
    .chipbar { display:grid; grid-template-columns:repeat(4,1fr); gap:8px; }
    .chipbar > .chip-dnr { grid-column:1 / -1; }
    @media (min-width:390px) {
      .chipbar { grid-template-columns:repeat(4,1fr) auto; }
      .chipbar > .chip-dnr { grid-column:auto; }
    }

    .grid-players { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }""",
'chipbar CSS')

sub1(
"""      {/* ⚠️ A DNR oszlopa `auto`, nem `1fr`: pontosan annyi helyet kap,
          amennyit a felirata ker. Ot egyenlo oszlopnal 360 px-en a „Veletlen"
          (90 px min-content, kockaikonnal) kiszorult volna a sorbol. */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr) auto', gap:8 }}>""",
"""      {/* Az elrendezes a `.chipbar` osztalyban van (media query kell hozza) —
          390 px-tol a DNR az otodik oszlop, alatta a sor ala kerul. */}
      <div className="chipbar">""",
'chipbar hasznalata')

sub1(
"""        <Chip label="DNR" tone="dnr" active={dnrMode} onClick={toggleDnrMode} testId="dnr" />""",
"""        <Chip label="DNR" tone="dnr" active={dnrMode} onClick={toggleDnrMode} testId="dnr" className="chip-dnr" />""",
'DNR chip osztaly')

sub1(
"""function Chip({ label, active, onClick, tone, icon, disabled, testId }) {""",
"""function Chip({ label, active, onClick, tone, icon, disabled, testId, className }) {""",
'Chip className prop')

sub1(
"""    <button onClick={disabled ? undefined : onClick} data-chip={testId} aria-pressed={isDnr ? !!active : undefined} style={{""",
"""    <button onClick={disabled ? undefined : onClick} data-chip={testId} className={className} aria-pressed={isDnr ? !!active : undefined} style={{""",
'Chip className atadasa')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_347b alkalmazva')
