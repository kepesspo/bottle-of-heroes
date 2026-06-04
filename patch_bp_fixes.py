with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Fix sync: add seCurRound + seCurMatch to dependency array ──────────
OLD_DEP = '  }, [seRounds, rrMatches, tsGroups, champion, rrDone, tsPhase]);'
NEW_DEP = '  }, [seRounds, seCurRound, seCurMatch, rrMatches, tsGroups, champion, rrDone, tsPhase]);'
assert OLD_DEP in html, 'sync dep not found'
html = html.replace(OLD_DEP, NEW_DEP, 1)

# ── 2. Drinks = cup difference (not DRINKS_PER_LOSS) ─────────────────────
# SE handleSEConfirm: loser drinks = MAX_CUPS - loser_score (remaining cups)
OLD_SE_DRINK1 = '''    const newDrink = { ...drinkMap };
    if (loser) newDrink[loser.id] = (newDrink[loser.id] || 0) + DRINKS_PER_LOSS;
    setDrinkMap(newDrink);
    setCups1(MAX_CUPS); setCups2(MAX_CUPS);'''
NEW_SE_DRINK1 = '''    const loserScore = cups1 < cups2 ? cups1 : cups2;
    const winnerScore = cups1 < cups2 ? cups2 : cups1;
    const cupDiff = Math.max(1, Math.abs(winnerScore - loserScore));
    const newDrink = { ...drinkMap };
    if (loser) newDrink[loser.id] = (newDrink[loser.id] || 0) + cupDiff;
    setDrinkMap(newDrink);
    setCups1(MAX_CUPS); setCups2(MAX_CUPS);'''
assert OLD_SE_DRINK1 in html, 'SE drink1 not found'
html = html.replace(OLD_SE_DRINK1, NEW_SE_DRINK1, 1)

# RR match drink (line ~36133)
OLD_RR_DRINK = '''    const newDrink = { ...drinkMap };
    if (loser) newDrink[loser.id] = (newDrink[loser.id] || 0) + DRINKS_PER_LOSS;
    setDrinkMap(newDrink);'''
NEW_RR_DRINK = '''    const loserScore2 = cups1 < cups2 ? cups1 : cups2;
    const winnerScore2 = cups1 < cups2 ? cups2 : cups1;
    const cupDiff2 = Math.max(1, Math.abs(winnerScore2 - loserScore2));
    const newDrink = { ...drinkMap };
    if (loser) newDrink[loser.id] = (newDrink[loser.id] || 0) + cupDiff2;
    setDrinkMap(newDrink);'''
assert OLD_RR_DRINK in html, 'RR drink not found'
html = html.replace(OLD_RR_DRINK, NEW_RR_DRINK, 1)

# Group match drink (line ~36200)
OLD_GRP_DRINK = '''    const newDrink = { ...drinkMap };
    if (loser) newDrink[loser.id] = (newDrink[loser.id] || 0) + DRINKS_PER_LOSS;
    setDrinkMap(newDrink);'''
NEW_GRP_DRINK = '''    const loserScore3 = cups1 < cups2 ? cups1 : cups2;
    const winnerScore3 = cups1 < cups2 ? cups2 : cups1;
    const cupDiff3 = Math.max(1, Math.abs(winnerScore3 - loserScore3));
    const newDrink = { ...drinkMap };
    if (loser) newDrink[loser.id] = (newDrink[loser.id] || 0) + cupDiff3;
    setDrinkMap(newDrink);'''
assert OLD_GRP_DRINK in html, 'group drink not found'
html = html.replace(OLD_GRP_DRINK, NEW_GRP_DRINK, 1)

# ── 3. Remove drinksPerLoss config option from BeerPong settings ──────────
OLD_DRINKS_CONFIG = '''    { key:\'drinksPerLoss\', label:\'Vesztes korty\',    val:drinksPerLoss, min:1, max:10, step:1 },'''
NEW_DRINKS_CONFIG = ''
assert OLD_DRINKS_CONFIG in html, 'drinksPerLoss config not found'
html = html.replace(OLD_DRINKS_CONFIG, NEW_DRINKS_CONFIG, 1)

# Also remove the drinksPerLoss const (no longer needed)
OLD_DPL_CONST = '  const drinksPerLoss = config.drinksPerLoss ?? 5;\n'
html = html.replace(OLD_DPL_CONST, '', 1)

# ── 4. Remove the drink info text from game UI (references DRINKS_PER_LOSS)
OLD_DRINK_TEXT = "          A vesztes <span style={{ fontWeight:900 }}>{DRINKS_PER_LOSS} kortyt</span> iszik 🍺"
NEW_DRINK_TEXT = "          A vesztes annyi kortyt iszik, amennyivel több pohara maradt a győztesnek 🍺"
assert OLD_DRINK_TEXT in html, 'drink text not found'
html = html.replace(OLD_DRINK_TEXT, NEW_DRINK_TEXT, 1)

# ── 5. Fix BeerPongObserverView: remove isBP check on curMatch, better fallback ──
# Also fix: show bracket even when seRoundsArr comes fresh by always rendering
# if bp has seRounds key (even if empty array after normalization)
OLD_CUR_MATCH_COND = '        {isBP && curMatch && curMatch.p1 && curMatch.p2 && !bp.champion && ('
NEW_CUR_MATCH_COND = '        {curMatch && curMatch.p1 && curMatch.p2 && !bp.champion && ('
assert OLD_CUR_MATCH_COND in html, 'curMatch cond not found'
html = html.replace(OLD_CUR_MATCH_COND, NEW_CUR_MATCH_COND, 1)

# ── 6. Version bump ───────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v7.24'"
NEW_VER = "const APP_VERSION = 'v7.25'"
assert OLD_VER in html, 'version not found'
html = html.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("done")
