# v10.347c - A chipek felirata NEM torhet ket sorba
#
# ⚠️ EZ MAS HIBA, MINT AMIRE SZAMITOTTAM, es a merés forditotta meg.
#
# Amit hittem: a szuk chip LEVAGJA a feliratot. Amit a meres mutatott: a
# felirat KETTOTORIK. „Szuro (1)" 69 px szeles egy sorban, de a gomb csak 60-at
# kap 390 px-en — es mivel a szoveg TORHET, a `1fr` oszlop `auto` minimuma nem
# 69, hanem a leghosszabb SZO (~35 px). Az oszlop tehat boldogan zsugorodik, a
# felirat meg „Szuro" / „(1)" alakban ket sorba all a 44 px-es gombon.
#
# Ezert nem fogta meg a `scrollWidth` alapu ellenorzes sem: nem lett tulcsordulas,
# csak tordeles.
#
# Ket kovetkezmenye:
#   1. `whiteSpace:'nowrap'` MINDEN chipre — ettol a `1fr` oszlop `auto`
#      minimuma a TELJES felirat lesz, tehat nem tud a felirat ala zsugorodni;
#   2. a DNR belso margoja 11 -> 9 px, hogy a 390 px-es tores-pontnal legyen
#      tartalek (a legrosszabb eset igy 347 px, a sor 358).
#
# A „Veletlen" 90 px-es min-contentje azert szamit ennyire, mert `1fr` oszlopok
# EGYENLOEN osztoznak: amit a Veletlen a sajat reszen felul elvisz, azt a masik
# haromtol veszi el. Ez a sor tenyleges szuk keresztmetszete.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

sub1(
"""      minHeight:44, padding: isDnr ? '0 11px' : '0 6px', background:bg, color:fg, border: isDnr ? `1.5px solid ${DNR_GOLD}` : 'none',""",
"""      minHeight:44, padding: isDnr ? '0 9px' : '0 6px', background:bg, color:fg, border: isDnr ? `1.5px solid ${DNR_GOLD}` : 'none',""",
'DNR belso margo')

sub1(
"""      letterSpacing: isDnr ? '0.09em' : undefined, whiteSpace: isDnr ? 'nowrap' : undefined,""",
"""      letterSpacing: isDnr ? '0.09em' : undefined,
      // ⚠️ `nowrap` MINDEN chipre. Nelkule a racs `1fr` oszlopanak `auto`
      // minimuma a leghosszabb SZO (a „Szuro (1)"-nel ~35 px), nem a teljes
      // felirat — az oszlop tehat a felirat ala zsugorodik, es a szoveg ket
      // sorba all a 44 px-es gombon. A `nowrap` a teljes feliratot teszi
      // minimumma, igy a racs nem tudja osszenyomni.
      whiteSpace:'nowrap',""",
'nowrap minden chipre')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_347c alkalmazva')
