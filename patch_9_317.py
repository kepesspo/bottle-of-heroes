#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. CRITICAL: EndScreen stats cards — sorted[0] / drunkSorted[0] crash ha üres
old_stats_cards = """            { label:'Pont győztes', icon:'🏆', tone:T.yellow, player:sorted[0], stat:sorted[0].points, statLabel:'pont' },
            { label:'Legtöbb korty', icon:'🍺', tone:T.coral, player:drunkSorted[0], stat:drunkSorted[0].drinks, statLabel:'korty' },"""
new_stats_cards = """            ...(sorted[0] ? [{ label:'Pont győztes', icon:'🏆', tone:T.yellow, player:sorted[0], stat:sorted[0].points, statLabel:'pont' }] : []),
            ...(drunkSorted[0] ? [{ label:'Legtöbb korty', icon:'🍺', tone:T.coral, player:drunkSorted[0], stat:drunkSorted[0].drinks, statLabel:'korty' }] : []),"""
assert old_stats_cards in html, "FAIL: EndScreen stats cards"
html = html.replace(old_stats_cards, new_stats_cards, 1)

# ── 2. HIGH: Division by zero — players.length % 0 az advance függvényekben
# advance (Egyéni)
old_advance = "    setPendingCommit({ newPlayers, fb:success?'win':'lose', newTurn:(turn+1)%players.length, newGameIdx:gameIdx+1, newRound:round+1 });"
new_advance = "    setPendingCommit({ newPlayers, fb:success?'win':'lose', newTurn:(turn+1)%Math.max(players.length,1), newGameIdx:gameIdx+1, newRound:round+1 });"
assert old_advance in html, "FAIL: advance"
html = html.replace(old_advance, new_advance, 1)

# advanceTeam (Csapat)
old_advanceteam = "    commitRound(newPlayers, 'win', (turn+1)%players.length, gameIdx+1, round+1);"
new_advanceteam = "    commitRound(newPlayers, 'win', (turn+1)%Math.max(players.length,1), gameIdx+1, round+1);"
assert old_advanceteam in html, "FAIL: advanceTeam"
html = html.replace(old_advanceteam, new_advanceteam, 1)

# advancePaired (Páros)
old_advancepaired = "    setPendingCommit({ newPlayers, fb:currentPlayerWon?'win':'lose', newTurn:(turn+1)%players.length, newGameIdx:gameIdx+1, newRound:round+1 });"
new_advancepaired = "    setPendingCommit({ newPlayers, fb:currentPlayerWon?'win':'lose', newTurn:(turn+1)%Math.max(players.length,1), newGameIdx:gameIdx+1, newRound:round+1 });"
assert old_advancepaired in html, "FAIL: advancePaired"
html = html.replace(old_advancepaired, new_advancepaired, 1)

# advanceLoverseny
old_advancelv = "    setPendingCommit({ newPlayers, fb, newTurn:(turn+1)%players.length, newGameIdx:gameIdx+1, newRound:round+1 });"
new_advancelv = "    setPendingCommit({ newPlayers, fb, newTurn:(turn+1)%Math.max(players.length,1), newGameIdx:gameIdx+1, newRound:round+1 });"
assert old_advancelv in html, "FAIL: advanceLoverseny"
html = html.replace(old_advancelv, new_advancelv, 1)

# ── 3. HIGH: Kisebb game — sorted bounds check
old_kisebb_sorted = """    const best = sorted[0];
    // Legrosszabb: legtöbb drink
    const worst = sorted[sorted.length - 1];
    const samePlayer = best.id === worst.id;"""
new_kisebb_sorted = """    if (!sorted.length) return null;
    const best = sorted[0];
    // Legrosszabb: legtöbb drink
    const worst = sorted[sorted.length - 1];
    const samePlayer = best.id === worst.id;"""
assert old_kisebb_sorted in html, "FAIL: kisebb sorted"
html = html.replace(old_kisebb_sorted, new_kisebb_sorted, 1)

# ── 4. MEDIUM: commitPending bonus — guard sorted és lastTied
old_bonus_guard = """    if (bonusEnabled && Math.random() < 0.10) {
      const sorted = [...newPlayers].sort((a,b) => (b.points-a.points)||(a.drinks-b.drinks));
      const first = sorted[0];
      const minPoints = sorted[sorted.length - 1].points;
      const lastTied = sorted.filter(p => p.points === minPoints);
      const last = lastTied[Math.floor(Math.random() * lastTied.length)];"""
new_bonus_guard = """    if (bonusEnabled && Math.random() < 0.10 && newPlayers.length >= 2) {
      const sorted = [...newPlayers].sort((a,b) => (b.points-a.points)||(a.drinks-b.drinks));
      const first = sorted[0];
      const minPoints = sorted[sorted.length - 1].points;
      const lastTied = sorted.filter(p => p.points === minPoints);
      if (!lastTied.length) return commitRound(newPlayers, fb, newTurn, newGameIdx, newRound);
      const last = lastTied[Math.floor(Math.random() * lastTied.length)];"""
assert old_bonus_guard in html, "FAIL: bonus guard"
html = html.replace(old_bonus_guard, new_bonus_guard, 1)

# ── 5. MEDIUM: localStorage try/catch — boh_splash
old_splash_ls = """    localStorage.setItem('boh_splash', next ? '1' : '0');"""
new_splash_ls = """    try { localStorage.setItem('boh_splash', next ? '1' : '0'); } catch(e) {}"""
assert old_splash_ls in html, "FAIL: splash localStorage"
html = html.replace(old_splash_ls, new_splash_ls, 1)

# ── 6. PERF: gameProgressGrow — width helyett scaleX (GPU-gyorsított)
old_kf_grow = "    @keyframes gameProgressGrow { from{width:0} to{width:100%} }"
new_kf_grow = "    @keyframes gameProgressGrow { from{transform:scaleX(0)} to{transform:scaleX(1)} }"
assert old_kf_grow in html, "FAIL: gameProgressGrow"
html = html.replace(old_kf_grow, new_kf_grow, 1)

html = html.replace("const APP_VERSION = 'v9.316';", "const APP_VERSION = 'v9.317';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.317 — Bug fixes: EndScreen crash, division by zero, Kisebb guard, bonus guard, localStorage, GPU anim")
