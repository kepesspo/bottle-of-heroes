#!/usr/bin/env python3
# v10.252 — Reakció Teszt: a végeredményhez odaírjuk a rekordot és az átlagot
#
# MIT KÉRT A FELHASZNÁLÓ
# A "Luca nyert!" képernyőn eddig CSAK a mostani két idő látszott. Egy szám
# önmagában nem mond semmit: a 396 ms jó vagy rossz? Ehhez kell viszonyítás —
# a játékos SAJÁT rekordja és átlaga.
#
# AMI EDDIG HIÁNYZOTT: az ÁTLAG nem volt kiszámolható
# A statisztikában eddig CSAK a `bestReactionTime` (rekord) volt eltárolva.
# Rekordból nem lehet átlagot visszafejteni — ahhoz összeg és darabszám kell.
# Ezért mostantól minden mérés hozzáad a `reactionSum` / `reactionCount`
# mezőkhöz (profilonként és játék-szinten is).
#
# Ez azt jelenti, hogy az átlag a MOSTANI parti óta épül. A rekord viszont a
# régi adatból is megvan, mert az eddig is gyűlt.
#
# A növekményeket NAPLÓZZUK is (statEvents / gameStatEvents), hogy az
# Admin → Partik visszavonás pontos maradjon: az ott futó levonás minden
# szám mezőt visszavesz, tehát az összeg és a darabszám is helyreáll.
# (A rekordot továbbra sem lehet visszaállítani — a korábbi értéke sehol
# nincs eltárolva. Ez így volt eddig is.)
#
# A KIÍRT SZÁMOK a mostani kört MÁR TARTALMAZZÁK — vagyis pont azt mutatják,
# ami a statisztikában is lesz, ha a játékos megnézi. "Új rekord" jelvényt
# csak akkor teszünk ki, ha VOLT korábbi rekord, és most tényleg jobb lett
# (első játéknál nincs mihez képest rekordot dönteni).
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1. a kör ELŐTTI statisztika beolvasása (a rekord-döntéshez ez kell) ──
sub("""  const timerRef = useRef(null);
  const advancedRef = useRef(false);

  useEffect(() => () => clearTimeout(timerRef.current), []);

  const currentPlayer = phase.includes('1') ? challenger : opponent;""",
    """  const timerRef = useRef(null);
  const advancedRef = useRef(false);

  useEffect(() => () => clearTimeout(timerRef.current), []);

  // A KÖR ELŐTTI allas — ehhez kepest tudjuk megmondani, hogy uj rekord-e,
  // es ebbol szamoljuk az atlagot (osszeg + darabszam). Indulaskor olvassuk,
  // mert a kor vegen mar a sajat irasunk is benne lenne.
  const [preStats, setPreStats] = useState({});
  useEffect(() => {
    if (typeof window.getStats !== 'function') return;
    const ids = [challenger?.profileId, opponent?.profileId].filter(Boolean);
    if (!ids.length) return;
    let alive = true;
    Promise.all(ids.map(id => window.getStats(id).catch(() => ({}))))
      .then(list => {
        if (!alive) return;
        const m = {};
        ids.forEach((id, i) => { m[id] = list[i] || {}; });
        setPreStats(m);
      });
    return () => { alive = false; };
  }, [challenger?.profileId, opponent?.profileId]);

  // Rekord + atlag EGY jatekosra, a mostani meressel egyutt — vagyis pont azt
  // mutatjuk, ami a statisztikaban is lesz. Ha nincs profil (alkalmi jatekos),
  // nincs mit mutatni.
  const histOf = (pl, ms) => {
    if (!pl?.profileId || ms == null) return null;
    const s = preStats[pl.profileId];
    if (!s) return null;
    const prevBest = typeof s.bestReactionTime === 'number' ? s.bestReactionTime : null;
    const cnt = typeof s.reactionCount === 'number' ? s.reactionCount : 0;
    const sum = typeof s.reactionSum === 'number' ? s.reactionSum : 0;
    return {
      best: prevBest == null ? ms : Math.min(prevBest, ms),
      avg: Math.round((sum + ms) / (cnt + 1)),
      isRecord: prevBest != null && ms < prevBest,
    };
  };

  const currentPlayer = phase.includes('1') ? challenger : opponent;""",
    'preStats olvasas')

# ── 2. összeg + darabszám írása, naplózással ──
sub("""    if (typeof window.incrementStats === 'function') {
      if (challenger?.profileId && p1Ms != null) window.incrementStats(challenger.profileId, {}, { bestReactionTime: p1Ms });
      if (opponent?.profileId && p2Ms != null) window.incrementStats(opponent.profileId, {}, { bestReactionTime: p2Ms });
    }
    if (typeof window.incrementGameStats === 'function') {
      const bestMs = Math.min(p1Ms ?? Infinity, p2Ms ?? Infinity);
      if (bestMs < Infinity) window.incrementGameStats('reakcio', {}, { bestReactionTime: bestMs });
    }""",
    """    if (typeof window.incrementStats === 'function') {
      // Az ATLAGHOZ osszeg + darabszam kell — a rekordbol nem szamolhato vissza.
      // Naplozzuk is, hogy az Admin/Partik visszavonas pontos maradjon.
      const bump = (pl, ms) => {
        if (!pl?.profileId || ms == null) return;
        const inc = { reactionSum: ms, reactionCount: 1 };
        window.incrementStats(pl.profileId, inc, { bestReactionTime: ms });
        if (typeof window.logStatEvent === 'function') window.logStatEvent(pl.profileId, inc);
      };
      bump(challenger, p1Ms);
      bump(opponent, p2Ms);
    }
    if (typeof window.incrementGameStats === 'function') {
      const bestMs = Math.min(p1Ms ?? Infinity, p2Ms ?? Infinity);
      const times = [p1Ms, p2Ms].filter(x => x != null);
      if (bestMs < Infinity) {
        // A jatek-szintu atlagba MINDKET ido beleszamit, nem csak a gyorsabb.
        const gInc = { reactionSum: times.reduce((a, b) => a + b, 0), reactionCount: times.length };
        window.incrementGameStats('reakcio', gInc, { bestReactionTime: bestMs });
        if (typeof window.logGameStatEvent === 'function') window.logGameStatEvent('reakcio', gInc);
      }
    }""",
    'osszeg + darabszam iras')

# ── 3. a végeredmény-képernyőn: rekord + átlag a sáv alatt ──
sub("""            <div style={{ height:14, borderRadius:7, background:T.surfaceMuted, overflow:'hidden' }}>
              <div style={{
                height:'100%', borderRadius:7,
                background: won ? `linear-gradient(90deg, ${T.mint}, ${T.mintDeep})` : `linear-gradient(90deg, ${T.coral}, #E06060)`,
                width:`${(ms/maxMs)*100}%`,
                transition:'width 0.8s cubic-bezier(.2,.9,.3,1)',
                animation:'gameProgressGrow 0.8s cubic-bezier(.2,.9,.3,1) both',
              }} />
            </div>
          </div>
        ))}
      </div>""",
    """            <div style={{ height:14, borderRadius:7, background:T.surfaceMuted, overflow:'hidden' }}>
              <div style={{
                height:'100%', borderRadius:7,
                background: won ? `linear-gradient(90deg, ${T.mint}, ${T.mintDeep})` : `linear-gradient(90deg, ${T.coral}, #E06060)`,
                width:`${(ms/maxMs)*100}%`,
                transition:'width 0.8s cubic-bezier(.2,.9,.3,1)',
                animation:'gameProgressGrow 0.8s cubic-bezier(.2,.9,.3,1) both',
              }} />
            </div>
            {/* Viszonyitas: egy szam onmagaban nem mond semmit. A rekord es az
                atlag MAR TARTALMAZZA a mostani kort — vagyis ugyanaz, mint ami
                a statisztikaban lesz. Profil nelkuli jatekosnal nincs sor. */}
            {(() => {
              const h = histOf(player, ms);
              if (!h) return null;
              return (
                <div style={{ display:'flex', alignItems:'center', gap:8, marginTop:7, flexWrap:'wrap' }}>
                  {h.isRecord && (
                    <span style={{ fontFamily:T.font, fontWeight:900, fontSize:10, letterSpacing:0.6, textTransform:'uppercase',
                                   color:'#fff', background:T.mint, borderRadius:999, padding:'3px 8px' }}>★ Új rekord</span>
                  )}
                  <span style={{ fontFamily:T.font, fontWeight:700, fontSize:11.5, color:T.inkMute, letterSpacing:0.2 }}>
                    Rekord <b style={{ color:T.inkSoft, fontVariantNumeric:'tabular-nums' }}>{h.best} ms</b>
                  </span>
                  <span style={{ width:3, height:3, borderRadius:'50%', background:T.inkMute, opacity:0.6 }} />
                  <span style={{ fontFamily:T.font, fontWeight:700, fontSize:11.5, color:T.inkMute, letterSpacing:0.2 }}>
                    Átlag <b style={{ color:T.inkSoft, fontVariantNumeric:'tabular-nums' }}>{h.avg} ms</b>
                  </span>
                </div>
              );
            })()}
          </div>
        ))}
      </div>
      {/* Az atlag a mostani frissites ota gyulik — a rekord a regi adatbol is
          megvan. Ezt egyszer megmondjuk, hogy ne tunjon hibanak. */}
      {players2.some(x => { const h = histOf(x.player, x.ms); return h && h.avg === h.best && h.best === x.ms; }) && (
        <div style={{ fontFamily:T.font, fontSize:11, color:T.inkMute, textAlign:'center', marginTop:-6 }}>
          Az átlag most kezdett gyűlni — több kör után lesz beszédes.
        </div>
      )}""",
    'rekord + atlag kiiras')

sub("const APP_VERSION = 'v10.251';", "const APP_VERSION = 'v10.252';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — rekord + atlag a Reakcio vegeredmenyen')
