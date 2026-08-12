# v10.353 - 5 dolog: a licit UTAN kivalaszthato, KI mondja a szavakat
#
# Eddig a licitalo (a kihivo) mondta a szavakat is. Innentol a licit alatt
# kivalaszthato, hogy ki teljesiti — es a konyveles EZT koveti:
#   • ha osszejon a licit -> a MONDO kap pontot, a masik iszik;
#   • ha nem -> forditva.
# Alapertelmezes a kihivo, tehat aki nem nyul hozza, annak a jatek valtozatlan.
#
# ⚠️ A valaszto a KOZOS `PlayerDrinkRow` `variant='pick'` valtozata, nem uj
# markup (CLAUDE.md „Ki igyon?" szakasz: „Ne irj ujat"). Ugyanaz a sor szolgalja
# ki a Kategoria jatekot is; egy sajat, tomor szines nevgomb-par elcsuszna tole.
#
# ⚠️ A TET-MONDAT is a valasztast koveti. Eddig masodik szemelyben szolt
# („…es te iszol"), ami a kihivora volt szabva — ha az ellenfel mondja a
# szavakat, ez SZO SZERINT az ellenkezojet allitana. Innentol NEVEKKEL beszel.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# ── 1. Allapot: ki mondja ───────────────────────────────────────────────────
sub1(
"""  const [checked, setChecked] = React.useState(() => Array(OTDOLOG_DEF_BID).fill(false));
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    setPhase('ready'); setBid(OTDOLOG_DEF_BID);
    setTimeLeft(otdologWindow(OTDOLOG_DEF_BID, difficulty));
    setChecked(Array(OTDOLOG_DEF_BID).fill(false)); advancedRef.current = false;
  }, [gameIdx, difficulty]);""",
"""  const [checked, setChecked] = React.useState(() => Array(OTDOLOG_DEF_BID).fill(false));
  // KI mondja a szavakat a licit utan. Alapbol a kihivo — aki nem nyul hozza,
  // annak a jatek valtozatlan.
  const [performerId, setPerformerId] = React.useState(challenger?.id || null);
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    setPhase('ready'); setBid(OTDOLOG_DEF_BID);
    setTimeLeft(otdologWindow(OTDOLOG_DEF_BID, difficulty));
    setChecked(Array(OTDOLOG_DEF_BID).fill(false)); advancedRef.current = false;
    setPerformerId(challenger?.id || null);
  }, [gameIdx, difficulty, challenger?.id]);

  // A ket resztvevo, es hogy melyikuk a MONDO. A `other` mindig a masik —
  // a konyveles, a tet-mondat es a banner is ebbol a ket valtozobol dolgozik,
  // igy nem tudnak elcsuszni egymastol.
  const performer = [challenger, opponent].find(x => x && x.id === performerId) || challenger;
  const other = (performer && opponent && performer.id === opponent.id) ? challenger : opponent;""",
'performerId allapot')

# ── 2. A konyveles a MONDO-t koveti ────────────────────────────────────────
sub1(
"""    const winner = correct ? challenger : opponent;
    const loser  = correct ? opponent   : challenger;
    if (winner) pm[winner.id] = 1;
    if (loser)  dm[loser.id]  = 1;
    // Eloszor a BANNER, utana az advance — ez a sorrend minden mas jatekban.
    onResult && onResult({
      winners: winner ? [winner] : [], losers: loser ? [loser] : [], drinks: 1,
      winNote: correct ? `Megvolt mind a ${bid}!` : `${challenger?.name || 'A kihívó'} nem tudta a ${bid}-t`,
    });""",
"""    // ⚠️ A MONDO nyer vagy bukik, nem a licitalo. A ketto alapertelmezesben
    // ugyanaz (a kihivo), de ha az ellenfelre bizzak a szavakat, a pont es a
    // korty vele mozog — kulonben a banner mast allitana, mint ami tortent.
    const winner = correct ? performer : other;
    const loser  = correct ? other     : performer;
    if (winner) pm[winner.id] = 1;
    if (loser)  dm[loser.id]  = 1;
    // Eloszor a BANNER, utana az advance — ez a sorrend minden mas jatekban.
    onResult && onResult({
      winners: winner ? [winner] : [], losers: loser ? [loser] : [], drinks: 1,
      winNote: correct ? `${performer?.name || 'A játékos'} megvolt mind a ${bid}!`
                       : `${performer?.name || 'A játékos'} nem tudta a ${bid}-t`,
    });""",
'konyveles a mondo szerint')

# ── 3. A valaszto + a tet-mondat ───────────────────────────────────────────
sub1(
"""            {opponent && (
              <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkSoft, textAlign:'center', marginTop:12, lineHeight:1.45 }}>
                Ha összejön, <strong style={{ color:T.ink }}>{opponent.name}</strong> iszik —<br/>ha nem, ő kap pontot és te iszol.
              </div>
            )}""",
"""            {/* ⚠️ KI MONDJA — a KOZOS `PlayerDrinkRow` `variant='pick'` sora,
                nem uj markup. Ugyanaz a valaszto, amit a Kategoria hasznal. */}
            {opponent && (
              <React.Fragment>
                <div style={{ height:1, background:`${T.inkMute}22`, margin:'14px 0 12px' }} />
                <div style={{ fontFamily:T.font, fontSize:11.5, fontWeight:800, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.12em', textAlign:'center', marginBottom:8 }}>
                  Ki mondja a szavakat?
                </div>
                <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
                  {[challenger, opponent].filter(Boolean).map(pl => (
                    <PlayerDrinkRow key={pl.id} p={pl} cnt={0} variant="pick"
                      selected={performer?.id === pl.id}
                      onPick={(id) => { if (phase === 'ready') setPerformerId(id); }} />
                  ))}
                </div>
                {/* ⚠️ NEVEKKEL, nem masodik szemelyben: a regi „…es te iszol"
                    a kihivora volt szabva, es az ellenfel valasztasa eseten
                    szo szerint az ellenkezojet allitotta volna. */}
                <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkSoft, textAlign:'center', marginTop:12, lineHeight:1.45 }}>
                  Ha összejön, <strong style={{ color:T.ink }}>{performer?.name}</strong> pontot kap
                  és <strong style={{ color:T.ink }}>{other?.name}</strong> iszik — ha nem, fordítva.
                </div>
              </React.Fragment>
            )}""",
'ki mondja valaszto')

# ── 4. Futas kozben is latszik, kire megy a jatek ──────────────────────────
sub1(
"""          <div style={{ fontFamily:T.font, fontSize:14, fontWeight:600, color:T.inkSoft }}>
            {checkedCount>=bid ? '🎉 Mind megvan!' : checkedCount>0 ? `${checkedCount} / ${bid} ${t('otdologGo')}` : phase==='done' ? 'Idő lejárt!' : 'Jelöld be amit kimondottál!'}
          </div>""",
"""          <div style={{ fontFamily:T.font, fontSize:14, fontWeight:600, color:T.inkSoft }}>
            {checkedCount>=bid ? '🎉 Mind megvan!' : checkedCount>0 ? `${checkedCount} / ${bid} ${t('otdologGo')}` : phase==='done' ? 'Idő lejárt!' : 'Jelöld be amit kimondottál!'}
          </div>""",
'jeloles-szoveg (valtozatlan)')

sub1(
"""      {phase !== 'ready' && (
        /* A jelolok KITOLTIK a sort (`1fr`), nem fix 50 px""",
"""      {/* Indulas utan is latszik, KIRE megy a jatek — a valaszto ilyenkor mar
          nincs kint, es a footer pirulaja a PAROST mutatja, nem a mondot. */}
      {phase !== 'ready' && performer && other && (
        <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:8, fontFamily:T.font, fontSize:13, color:T.inkSoft }}>
          <PlayerAvatar player={performer} size={22} />
          <span><strong style={{ color:T.ink }}>{performer.name}</strong> mondja · ha bukik, ő iszik</span>
        </div>
      )}

      {phase !== 'ready' && (
        /* A jelolok KITOLTIK a sort (`1fr`), nem fix 50 px""",
'mondo kijelzese futas kozben')

sub1("const APP_VERSION = 'v10.352';", "const APP_VERSION = 'v10.353';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_353 alkalmazva')
