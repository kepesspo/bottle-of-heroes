#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Fix SorrendTab: use Set comparison for IDs (not ordered join), always render
old_component = """function SorrendTab({ players, setPlayers, turn, setTurn, pendingCommit, setPendingCommit }) {
  // Local copy so UI is always responsive
  const [localOrder, setLocalOrder] = React.useState(players);
  const [saved, setSaved] = React.useState(false);

  // Keep local in sync if players change externally (new round etc)
  const prevPlayersRef = React.useRef(players);
  React.useEffect(() => {
    // Only sync if IDs changed (new player added/removed), not on reorder
    const prevIds = prevPlayersRef.current.map(p=>p.id).join(',');
    const nextIds = players.map(p=>p.id).join(',');
    if (prevIds !== nextIds) {
      setLocalOrder(players);
    }
    prevPlayersRef.current = players;
  }, [players]);"""
new_component = """function SorrendTab({ players, setPlayers, turn, setTurn, pendingCommit, setPendingCommit }) {
  const [localOrder, setLocalOrder] = React.useState(players);
  const [saved, setSaved] = React.useState(false);

  // Only sync from parent if the SET of player IDs changed (add/remove), never on reorder
  const prevIdSetRef = React.useRef(new Set(players.map(p=>p.id)));
  React.useEffect(() => {
    const newSet = new Set(players.map(p=>p.id));
    const prev = prevIdSetRef.current;
    const changed = newSet.size !== prev.size || [...newSet].some(id => !prev.has(id));
    prevIdSetRef.current = newSet;
    if (changed) setLocalOrder(players);
  }, [players]);"""
assert old_component in html, "FAIL: SorrendTab component start"
html = html.replace(old_component, new_component, 1)

# ── 2. Change sorrend div: always render SorrendTab (not conditional), use visibility only
old_sorrend = """              {/* SORREND — standalone component */}
              <div style={{ visibility: menuTab==='sorrend' ? 'visible' : 'hidden', position:'absolute', top:0, left:14, right:14, bottom:0, overflowY:'auto' }}>
                {menuTab==='sorrend' && <SorrendTab players={players} setPlayers={setPlayers} turn={turn} setTurn={setTurn} pendingCommit={pendingCommit} setPendingCommit={setPendingCommit} />}
              </div>"""
new_sorrend = """              {/* SORREND — always mounted, visibility toggled */}
              <div style={{ visibility: menuTab==='sorrend' ? 'visible' : 'hidden', position:'absolute', top:0, left:14, right:14, bottom:0, overflowY:'auto' }}>
                <SorrendTab players={players} setPlayers={setPlayers} turn={turn} setTurn={setTurn} pendingCommit={pendingCommit} setPendingCommit={setPendingCommit} />
              </div>"""
assert old_sorrend in html, "FAIL: sorrend div"
html = html.replace(old_sorrend, new_sorrend, 1)

# ── version bump
html = html.replace("const APP_VERSION = 'v9.281';", "const APP_VERSION = 'v9.282';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.282 — SorrendTab ID-Set sync, always mounted")
