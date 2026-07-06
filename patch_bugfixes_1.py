import re
with open('index.html', encoding='utf-8') as f:
    c = f.read()

# ═══ 1. BEER PONG — grp_se csoport beragadás ═══════════════════════════════
# 1a. 2 fős SE csoport: sima 1 meccses RR (a bracket-builder 2 főre rossz TBD-t gyárt)
OLD = "matches: groupType === 'rr' ? buildRRMatches(gp) : buildSEBracket(gp).flat(),"
NEW = "matches: (groupType === 'rr' || gp.length === 2) ? buildRRMatches(gp) : buildSEBracket(gp).flat(),"
assert c.count(OLD) == 2, "bp init sites: %d" % c.count(OLD)
c = c.replace(OLD, NEW, 2)

# 1b. handleGroupConfirm: prelim győztes betöltése a TBD meccsbe + TBD kihagyása
OLD = """        const nm = g.matches.map((mm, i) => i === g.curIdx ? { ...mm, winner, loser, score, draw: isDraw } : mm);
        const nextIdx = nm.findIndex(mm => mm.winner === null && !mm.draw);"""
NEW = """        const nm = g.matches.map((mm, i) => i === g.curIdx ? { ...mm, winner, loser, score, draw: isDraw } : mm);
        // SE csoport: a prelim meccs győztesét betöltjük a következő kör TBD meccsébe
        const curM = nm[g.curIdx];
        if (!isRR && winner && curM && curM.r1slot !== undefined && curM.r1slot !== null) {
          const base = nm.filter(mm => mm.r1slot !== undefined && mm.r1slot !== null).length;
          const ti = base + curM.r1slot;
          if (nm[ti]) {
            const filled = { ...nm[ti], [curM.r1side]: winner };
            filled.tbd = !(filled.p1 && filled.p2);
            nm[ti] = filled;
          }
        }
        const nextIdx = nm.findIndex(mm => mm.winner === null && !mm.draw && mm.p1 && mm.p2);"""
assert OLD in c, "handleGroupConfirm not found"
c = c.replace(OLD, NEW, 1)

# ═══ 2. BUSZ — players[turn] ReferenceError az utolsó lépcsőn ═══════════════
OLD = """        if (typeof window.updateStats === 'function' && players[turn]?.profileId) {
          window.updateStats(players[turn].profileId, {"""
NEW = """        const riderP = players.find(p => p.id === riderId);
        if (typeof window.updateStats === 'function' && riderP?.profileId) {
          window.updateStats(riderP.profileId, {"""
assert OLD in c, "busz stat block not found"
c = c.replace(OLD, NEW, 1)

# ═══ 3. OVFJ — valódi digráf-ellenőrzés ═════════════════════════════════════
OLD = "const OVFJ_LETTERS = ['A','Á','B','C','CS','D','E','É','F','G','GY','H','I','Í','J','K','L','LY','M','N','NY','O','Ó','Ö','Ő','P','R','S','SZ','T','TY','U','Ú','Ü','Ű','V','Z','ZS'];"
NEW = OLD + """
const OVFJ_DIGRAPHS = ['dzs','dz','cs','gy','ly','ny','sz','ty','zs'];
function ovfjLetterOk(value, letter) {
  const s = String(value||'').trim().toLowerCase();
  const l = String(letter||'').toLowerCase();
  if (!s || !l) return false;
  if (!s.startsWith(l)) return false;
  // Egybetűs húzott betűnél a hosszabb digráf nem érvényes (S ≠ Sz, C ≠ Cs, G ≠ Gy…)
  if (l.length === 1 && OVFJ_DIGRAPHS.some(d => d[0] === l && s.startsWith(d))) return false;
  if (l === 'dz' && s.startsWith('dzs')) return false;
  return true;
}"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# 3a. calcScores
OLD = """        // Exclude wrong first letter (digraph-aware)
        const letterL = letter.toLowerCase();
        if (!v.startsWith(letterL)) return;"""
NEW = """        if (!ovfjLetterOk(v, letter)) return; // rossz kezdőbetű (digráf-helyes)"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# 3b. host voting nézet
OLD = "const isWrongLetter = val && !val.toLowerCase().startsWith(letter.toLowerCase());"
NEW = "const isWrongLetter = val && !ovfjLetterOk(val, letter);"
assert OLD in c
c = c.replace(OLD, NEW, 1)

# 3c. host írós form
OLD = "const hwrong = hv.trim().length > 0 && !hv.trim().toLowerCase().startsWith(letter.toLowerCase());"
NEW = "const hwrong = hv.trim().length > 0 && !ovfjLetterOk(hv, letter);"
assert OLD in c
c = c.replace(OLD, NEW, 1)

# 3d. observer írós nézet
OLD = "const wrongLetter = v.trim().length > 0 && !v.trim().toLowerCase().startsWith(letter.toLowerCase());"
NEW = "const wrongLetter = v.trim().length > 0 && !ovfjLetterOk(v, letter);"
assert OLD in c
c = c.replace(OLD, NEW, 1)

# 3e. voteableItems: rossz betűs válasz nem szavazható → nem akad be az auto-pontozás
OLD = """        const val = (answers[p.id]?.[cat.key]||'').trim();
        if (!val || dm[cat.key].has(val.toLowerCase())) return;
        voteableItems.push({pid: p.id, catKey: cat.key});"""
NEW = """        const val = (answers[p.id]?.[cat.key]||'').trim();
        if (!val || dm[cat.key].has(val.toLowerCase())) return;
        if (!ovfjLetterOk(val, letter)) return; // rossz kezdőbetű — nem kell rá szavazni
        voteableItems.push({pid: p.id, catKey: cat.key});"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# 3f. observer szavazásnál a rossz betűs válasz is érvénytelenként jelenjen meg
OLD = """                const vk = `${p.id}_${cat.key}`, mv = myVotes[vk];
                const dup = isDup(cat.key, val);"""
NEW = """                const vk = `${p.id}_${cat.key}`, mv = myVotes[vk];
                const dup = isDup(cat.key, val) || (!!val && !ovfjLetterOk(val, letter));"""
assert OLD in c, "observer vote dup not found"
c = c.replace(OLD, NEW, 1)

# ═══ 4. OVFJ observer — előző kör válaszai ne csússzanak át ═════════════════
OLD = """      // Keep previous answers as defaults for new round
      const prev = lastRoundRef.current ? {...prevLocalAnsRef.current} : {};
      lastRoundRef.current = ovfj.round;
      setLocalAns(prev); setSubmitted(false); setMyVotes({});"""
NEW = """      lastRoundRef.current = ovfj.round;
      setLocalAns({}); setSubmitted(false); setMyVotes({});"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 5. SZÓLÁNC — hibás érintés után zárolt tábla (dupla advance ellen) ═════
OLD = """  const tapWord = (word, idx) => {
    if (S.phase !== 'recall') return;
    if (S.tapped.includes(idx)) return;
    const expected = S.chain[S.tapped.length];"""
NEW = """  const tapWord = (word, idx) => {
    if (S.phase !== 'recall') return;
    if (S.tapped.includes(idx)) return;
    if (S.wrongIdx != null) return; // hibás érintés után zárolva
    const expected = S.chain[S.tapped.length];"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 6. BLACKJACK — robusztusság ════════════════════════════════════════════
# 6a. tét írás mezőszintű merge-dzsel (ne csapja felül egymást két játékos)
OLD = """  const setMyBet = (v) => bjWrite(code, { ...bj, bets: { ...bj.bets, [playerId]: Math.max(1, Math.min(10, v)) } });
  const confirmBet = () => bjWrite(code, { ...bj, betsDone: { ...bj.betsDone, [playerId]: true } });"""
NEW = """  const setMyBet = (v) => { if (typeof syncRoom === 'function') syncRoom(code, { bjState: { bets: { [playerId]: Math.max(1, Math.min(10, v)) } } }); };
  const confirmBet = () => { if (typeof syncRoom === 'function') syncRoom(code, { bjState: { betsDone: { [playerId]: true } } }); };"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# 6b. host átveheti a beragadt játékos körét online is
OLD = "              {isTurn && !isOnline && ("
NEW = "              {isTurn && ("
assert OLD in c
c = c.replace(OLD, NEW, 1)
OLD = "📱 A telefonján gondolkodik…"
NEW = "📱 A telefonján is léphet — vagy üsd le itt helyette"
assert OLD in c
c = c.replace(OLD, NEW, 1)

# 6c. pakli-kifogyás: automatikus újrakeverés
OLD = """function bjCardValue(rank) {"""
NEW = """function bjPop(deck) {
  if (!deck.length) bjNewDeck().forEach(cd => deck.push(cd)); // elfogyott a pakli — újrakeverés
  return deck.pop();
}
function bjCardValue(rank) {"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

OLD = "  const card = deck.pop();"
assert c.count(OLD) == 2
c = c.replace(OLD, "  const card = bjPop(deck);", 2)

OLD = """    (state.participants || []).forEach(pid => hands[pid].push(deck.pop()));
    dealerHand.push(deck.pop());"""
NEW = """    (state.participants || []).forEach(pid => hands[pid].push(bjPop(deck)));
    dealerHand.push(bjPop(deck));"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

OLD = "    while (bjScore(dealerHand) < 17) dealerHand.push(deck.pop());"
NEW = "    while (bjScore(dealerHand) < 17) dealerHand.push(bjPop(deck));"
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ verzióbump ═════════════════════════════════════════════════════════════
c = re.sub(r'v9\.782', 'v9.783', c, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("Done v9.783")
