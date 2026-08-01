#!/usr/bin/env python3
# v10.254 — Reakció: a viszonyítás-kártyára bekerül a MINDENKORI csúcs is
#
# A saját rekord mellé kell egy sor, ami mindenkire vonatkozik: a játék
# örökranglistás legjobbja és átlaga, függetlenül attól, ki játszik éppen.
#
# AZ ADAT MÁR GYŰLIK: a `game_stats/reakcio` doksiban ott a `bestReactionTime`
# (régóta), és a v10.252 óta a `reactionSum` / `reactionCount` is — abba
# MINDKÉT idő beleszámít, nem csak a gyorsabbé. Tehát csak be kell olvasni.
#
# Egy hiányzó darab volt: nem volt EGY játék statisztikáját olvasó függvény,
# csak a teljes kollekciót lehúzó `getAllGameStats`. Egyetlen sor kedvéért 24
# doksit beolvasni pazarlás, ezért mellé kerül a `getGameStats(gameId)` —
# ugyanaz a minta, mint a profiloknál a `getStats(profileId)`.
#
# A sor a többi alatt van, vékony elválasztóval, mert más fajta: nem egy
# játékosról szól. A szám mentazöld lesz, ha ez a kör MEGDÖNTÖTTE a csúcsot.
#
# Ha egyik játékosnak sincs profilja, a kártya eddig elmaradt — mostantól a
# mindenkori sor miatt akkor is megjelenik, mert az attól még érvényes.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1. egy játék statisztikájának olvasása (a teljes kollekció helyett) ──
sub("""  window.getAllGameStats = function() {""",
    """  // EGY jatek statisztikaja. Eddig csak a teljes kollekciot lehuzo
  // getAllGameStats letezett — egyetlen ertek kedveert az pazarlas.
  window.getGameStats = function(gameId) {
    return coll('game_stats').doc(gameId).get().then(function(d) {
      return d.exists ? expandDotKeys(d.data()) : {};
    }).catch(function() { return {}; });
  };
  window.getAllGameStats = function() {""",
    'getGameStats')

# ── 2. a kör ELŐTTI játék-statisztika beolvasása ──
sub("""    return () => { alive = false; };
  }, [challenger?.profileId, opponent?.profileId]);""",
    """    return () => { alive = false; };
  }, [challenger?.profileId, opponent?.profileId]);

  // A jatek MINDENKORI allasa (mindenki eredmenyebol), szinten a kor ELOTT.
  const [preGame, setPreGame] = useState(null);
  useEffect(() => {
    if (typeof window.getGameStats !== 'function') return;
    let alive = true;
    window.getGameStats('reakcio').catch(() => ({})).then(g => { if (alive) setPreGame(g || {}); });
    return () => { alive = false; };
  }, []);

  // A mindenkori csucs es atlag — a mostani kor MINDKET idejevel egyutt,
  // ugyanugy, mint a jatekos sorainal.
  const globalHist = () => {
    if (!preGame) return null;
    const times = [p1Ms, p2Ms].filter(x => x != null);
    if (!times.length) return null;
    const fastest = Math.min(...times);
    const prevBest = typeof preGame.bestReactionTime === 'number' ? preGame.bestReactionTime : null;
    const cnt = typeof preGame.reactionCount === 'number' ? preGame.reactionCount : 0;
    const sum = typeof preGame.reactionSum === 'number' ? preGame.reactionSum : 0;
    return {
      best: prevBest == null ? fastest : Math.min(prevBest, fastest),
      avg: Math.round((sum + times.reduce((a, b) => a + b, 0)) / (cnt + times.length)),
      isRecord: prevBest != null && fastest < prevBest,
      fresh: cnt === 0,
    };
  };""",
    'preGame olvasas')

# ── 3. a kártyára kerül a mindenkori sor ──
sub("""      {(() => {
        const hist = players2.map(x => ({ ...x, h: histOf(x.player, x.ms) })).filter(x => x.h);
        if (!hist.length) return null;
        const fresh = hist.some(x => x.h.avg === x.h.best && x.h.best === x.ms);""",
    """      {(() => {
        const hist = players2.map(x => ({ ...x, h: histOf(x.player, x.ms) })).filter(x => x.h);
        const g = globalHist();
        // A mindenkori sor akkor is ervenyes, ha egyik jatekosnak sincs profilja
        if (!hist.length && !g) return null;
        const fresh = hist.some(x => x.h.avg === x.h.best && x.h.best === x.ms) || (g && g.fresh);""",
    'kartya feltetel')

sub("""                  <span style={{ ...num, color:T.inkSoft }}>{x.h.avg} ms</span>
                </React.Fragment>
              ))}
            </div>""",
    """                  <span style={{ ...num, color:T.inkSoft }}>{x.h.avg} ms</span>
                </React.Fragment>
              ))}
              {/* Mindenkori csucs — mas fajta sor, ezert vekony elvalaszto elozi
                  meg. Az elvalasztot EGY, harom hasabot atfogo elem adja, mert
                  cellankenti felso keret nem allna egy vonalba. */}
              {g && (
                <React.Fragment>
                  {!!hist.length && (
                    <span style={{ gridColumn:'1 / -1', height:1, background:`${T.inkMute}33`, margin:'2px 0' }} />
                  )}
                  <span style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft,
                                 overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>
                    🌍 Mindenki
                  </span>
                  <span style={{ ...num, fontSize:17, color: g.isRecord ? T.mint : T.inkSoft }}>{g.best} ms</span>
                  <span style={{ ...num, fontSize:17, color:T.inkSoft }}>{g.avg} ms</span>
                </React.Fragment>
              )}
            </div>""",
    'mindenkori sor')

sub("const APP_VERSION = 'v10.253';", "const APP_VERSION = 'v10.254';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — mindenkori csucs a kartyan')
