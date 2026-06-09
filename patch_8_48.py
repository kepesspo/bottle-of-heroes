#!/usr/bin/env python3
"""v8.48: Beer Pong crash-fix — 5 null/undefined guard javítás"""

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

fixes = [
    (
        "      const br = buildSEBracket(tp);\n      setSeRounds(br); setSeCurRound(0);\n      const firstPending = br[0].findIndex(m => m.winner === null);\n      setSeCurMatch(firstPending >= 0 ? firstPending : 0);",
        "      const br = buildSEBracket(tp);\n      setSeRounds(br); setSeCurRound(0);\n      const firstPending = br.length > 0 ? br[0].findIndex(m => m.winner === null) : -1;\n      setSeCurMatch(firstPending >= 0 ? firstPending : 0);"
    ),
    (
        "            setSeRounds(br); setSeCurRound(0);\n            setSeCurMatch(br[0].findIndex(mm => mm.winner === null));",
        "            setSeRounds(br); setSeCurRound(0);\n            const fp = br.length > 0 ? br[0].findIndex(mm => mm.winner === null) : -1;\n            setSeCurMatch(fp >= 0 ? fp : 0);"
    ),
    (
        "  const handleSEConfirm = (rounds, curRound, curMatch, setCB) => {\n    const match = rounds[curRound][curMatch];",
        "  const handleSEConfirm = (rounds, curRound, curMatch, setCB) => {\n    if (!rounds[curRound]?.[curMatch]) return;\n    const match = rounds[curRound][curMatch];"
    ),
    (
        "  const handleGroupConfirm = () => {\n    const grp = tsGroups[viewGroup];\n    const isRR = TOURNAMENT.startsWith('grp_rr');\n    const m = grp.matches[grp.curIdx];",
        "  const handleGroupConfirm = () => {\n    const grp = tsGroups[viewGroup];\n    if (!grp || grp.done) return;\n    const isRR = TOURNAMENT.startsWith('grp_rr');\n    const m = grp.matches[grp.curIdx];\n    if (!m) return;"
    ),
    (
        "      const br = buildSEBracket(ep);\n      setSeRounds(br); setSeCurRound(0);\n      const fp = br[0].findIndex(m => m.winner === null);\n      setSeCurMatch(fp >= 0 ? fp : 0);",
        "      const br = buildSEBracket(ep);\n      setSeRounds(br); setSeCurRound(0);\n      const fp = br.length > 0 ? br[0].findIndex(m => m.winner === null) : -1;\n      setSeCurMatch(fp >= 0 ? fp : 0);"
    ),
    ("const APP_VERSION = 'v8.47';", "const APP_VERSION = 'v8.48';"),
]

for old, new in fixes:
    assert old in c, f"NOT FOUND: {old[:60]}"
    c = c.replace(old, new, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("v8.48 saved")
