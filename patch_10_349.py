# v10.349 - A DNR jatekok CSAK a DNR feluleten, es a Kedvencek szekcio kikerul
#
# Ket valtozas, es a masodik az elsobol kovetkezik.
#
# 1. A DNR EXKLUZIV JATEKOK KIKERULNEK A NORMAL LISTABOL. Eddig ket helyen
#    alltak: a DNR feluleten ES a sajat kategoria-szekciojukban (mind az ot
#    `Csapat`). Innentol a kategoria-szekciok `isDnrGame`-mel szurnek — a DNR
#    jatekokhoz egyetlen ut vezet, a DNR gomb.
#
# 2. A KEDVENCEK SZEKCIO MEGSZUNIK. A lista bedrotozva `['beerpong','busz']`
#    volt — MINDKETTO DNR jatek, tehat az elso valtozas utan a szekcio pont
#    azokat ismetelte volna meg, amiket az elozo pontban vettunk ki.
#    A `FavTile` komponens MARAD: a DNR szekcio azt hasznalja.
#
# ⚠️ EBBOL KOVETKEZIK A SZURES „DNR Exkluziv" SORANAK HALALA. Ha a DNR jatekok
# nincsenek a normal listaban, az a szuro URES listat adna — nem szukitene,
# hanem kiuritene a kepernyot. A sor ezert kikerul a `FILTER_CATS`-bol es a
# `gameMatchesFilter`-bol. Innentol EGY belepo van a DNR jatekokhoz (a gomb),
# es az egyben az alapertelmezett nezet is (v10.348).
#
# Az `isDnrGame` tovabbra is egy forras, csak mar ket MASIK helyet szolgal ki:
# a DNR szekciot es a kategoria-szekciok kizarasat.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# ── 1. A Kedvencek szekcio kikerul ──────────────────────────────────────────
sub1(
"""        {/* ── Kedvencek szekció ── */}
        {!hasFilter && !dnrMode && (() => {
          const FAVS = ['beerpong','busz'];
          const favGames = FAVS.map(id => GAMES.find(g => g.id === id)).filter(Boolean);
          return (
            <div style={{ marginBottom:18 }}>
              <div style={{ display:'flex', alignItems:'center', gap:6, marginBottom:10 }}>
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.12em' }}>Kedvencek</span>
              </div>
              <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
                {favGames.map(g => {
                  const isSelected = selectedGames.includes(g.id);
                  const locked = isLocked(g.id);
                  const dim = locked || (anySelected && !isSelected);
                  const longPress = longPressFor(g.id);
                  return (
                    <FavTile key={g.id} g={g} selected={isSelected} dim={dim} locked={locked}
                      onClick={() => toggle(g.id)} onInfo={() => setInfo(g.id)} onLongPress={longPress} />
                  );
                })}
              </div>
            </div>
          );
        })()}

""",
"""        {/* A KEDVENCEK szekcio megszunt (v10.349). A listaja bedrotozva
            `['beerpong','busz']` volt — mindketto DNR jatek, tehat a DNR
            felulet bevezetese utan pont azokat ismetelte volna meg, amik a
            kategoria-szekciokbol is kikerultek. A `FavTile` komponens MARAD:
            a DNR szekcio sorai abbol epulnek. */}

""",
'Kedvencek szekcio torlese')

# ── 2. A kategoria-szekciokbol kiesnek a DNR jatekok ────────────────────────
sub1(
"""          const sectionGames = visibleGames.filter(g => g.category === key);""",
"""          // ⚠️ `!isDnrGame`: a DNR exkluziv jatekok CSAK a DNR feluleten
          // allnak. Nelkule mind az ot ott lenne a `Csapat` szekcioban is,
          // ket kulonbozo alakban ugyanaz a jatek.
          const sectionGames = visibleGames.filter(g => g.category === key && !isDnrGame(g));""",
'kategoria-szekciok szurese')

# ── 3. A Szures „DNR Exkluziv" sora kikerul (ures listat adna) ──────────────
sub1(
"""  { k:'DNR',     l:'DNR Exkluzív', tone:'#8B5CF6', ic:(c)=><svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M6 3h12l4 6-10 12L2 9l4-6z" stroke={c} strokeWidth="2" strokeLinejoin="round"/><path d="M2 9h20M9 3l-1.5 6L12 21l4.5-12L15 3" stroke={c} strokeWidth="1.4" strokeLinejoin="round" opacity=".7"/></svg> },
""",
"""  // ⚠️ NINCS „DNR Exkluziv" sor (v10.349): a DNR jatekok kikerultek a normal
  // listabol, tehat ez a szuro URES listat adna — nem szukitene a kepernyot,
  // hanem kiuritene. A DNR jatekokhoz egyetlen ut vezet: a szurosor DNR gombja
  // (ami egyben az alapertelmezett nezet is).
""",
'FILTER_CATS DNR sor')

sub1(
"""    const catFilters = activeFilters.filter(f => ['Egyéni','Páros','Csapat','DNR','Önálló'].includes(f));""",
"""    const catFilters = activeFilters.filter(f => ['Egyéni','Páros','Csapat','Önálló'].includes(f));""",
'catFilters lista')

sub1(
"""      f === 'DNR'    ? isDnrGame(g) :
""",
"""""",
'gameMatchesFilter DNR ag')

sub1("const APP_VERSION = 'v10.348';", "const APP_VERSION = 'v10.349';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_349 alkalmazva')
