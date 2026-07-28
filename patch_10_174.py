# v10.174 — a legtobbet jatszott jatekok elore, kategorian belul
#
# Az adat mar megvolt: minden jatek vegen no a game_stats/{id}.playCount.
# Eddig senki nem hasznalta a jatekvalasztonal — a lista a GAMES tomb
# sorrendjeben allt, azaz gyakorlatilag a felvetel sorrendjeben.
#
# A sorrendet localStorage-bol vesszuk az ELSO festeskor, es a friss szamokat
# csak a kovetkezo megnyitasra alkalmazzuk. Kulonben a lista egy masodperccel a
# megnyitas utan atrendezodne a kez alatt — pont amikor az ember mar nyulna
# egy kartya fele.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# ── a szamlalok betoltese ──
hook = "  const [filterSheet, setFilterSheet] = useState(false);"
assert s.count(hook) == 1
s = s.replace(hook, hook + """
  // Hanyszor jatszottuk az egyes jatekokat (game_stats/{id}.playCount).
  // Az ELSO festeshez a legutobb latott szamokat hasznaljuk, a friss adatot
  // csak elmentjuk — igy a lista nem rendezodik at a kez alatt.
  const PLAYCOUNT_KEY = 'boh_playcounts';
  const [playCounts] = useState(() => {
    try { return JSON.parse(localStorage.getItem(PLAYCOUNT_KEY) || '{}') || {}; } catch (e) { return {}; }
  });
  React.useEffect(() => {
    if (typeof window.getAllGameStats !== 'function') return;
    window.getAllGameStats().then(all => {
      const counts = {};
      Object.keys(all || {}).forEach(id => {
        const n = all[id] && all[id].playCount;
        if (typeof n === 'number' && n > 0) counts[id] = n;
      });
      try { localStorage.setItem(PLAYCOUNT_KEY, JSON.stringify(counts)); } catch (e) {}
    }, () => {});
  }, []);""")

# ── a rendezes ──
old = "  const visibleGames = GAMES.filter(g => !_hiddenGames.includes(g.id)).filter(gameMatchesFilter).sort((a,b) => (a.comingSoon?1:0) - (b.comingSoon?1:0));"
assert s.count(old) == 1
s = s.replace(old, """  // Sorrend: eloszor a hamarosan-erkezok hatra, aztan a legtobbet jatszottak
  // elore. A sort stabil, ezert az azonos jatszottsaguak (jellemzoen a meg
  // sosem jatszottak, 0-val) a GAMES tomb eredeti sorrendjeben maradnak.
  const visibleGames = GAMES.filter(g => !_hiddenGames.includes(g.id)).filter(gameMatchesFilter)
    .sort((a, b) => (a.comingSoon ? 1 : 0) - (b.comingSoon ? 1 : 0)
                 || (playCounts[b.id] || 0) - (playCounts[a.id] || 0));""")

s = s.replace("const APP_VERSION = 'v10.173';", "const APP_VERSION = 'v10.174';", 1)
assert "v10.174" in s and s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK')
