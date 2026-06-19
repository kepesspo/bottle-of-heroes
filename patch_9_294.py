#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. PlayersScreen: fetch all-time stats and compute badges
old = """function PlayersScreen({ players, setPlayers, go }) {
  const [editing, setEditing] = useState(null);
  const [secretTaps, setSecretTaps] = useState(0);
  const secretTimerRef = React.useRef(null);"""
new = """function PlayersScreen({ players, setPlayers, go }) {
  const [editing, setEditing] = useState(null);
  const [secretTaps, setSecretTaps] = useState(0);
  const secretTimerRef = React.useRef(null);
  const [allTimeStats, setAllTimeStats] = React.useState({});
  React.useEffect(() => {
    if (typeof window.getAllStats !== 'function') return;
    window.getAllStats().then(st => setAllTimeStats(st || {}));
  }, []);
  const getBadge = (p) => {
    if (!p.profileId) return null;
    const profileIds = players.filter(x => x.profileId).map(x => x.profileId);
    const ranked = [...profileIds].sort((a,b) => (allTimeStats[b]?.totalPoints||0) - (allTimeStats[a]?.totalPoints||0));
    const ri = ranked.indexOf(p.profileId);
    return ri >= 0 && ri < 3 && (allTimeStats[p.profileId]?.totalPoints||0) > 0 ? ['🥇','🥈','🥉'][ri] : null;
  };"""
assert old in html, "FAIL: PlayersScreen"
html = html.replace(old, new, 1)

# ── 2. Update PlayerCard call to use getBadge
old2 = """            <PlayerCard key={p.id} p={p} index={i} onEdit={() => setEditing(p.id)} onRemove={() => removePlayer(p.id)} badge={(() => { const sorted=[...players].sort((a,b)=>b.points-a.points); const ri=sorted.findIndex(x=>x.id===p.id); return p.points>0&&ri<3?['🥇','🥈','🥉'][ri]:null; })()} />"""
new2 = """            <PlayerCard key={p.id} p={p} index={i} onEdit={() => setEditing(p.id)} onRemove={() => removePlayer(p.id)} badge={getBadge(p)} />"""
assert old2 in html, "FAIL: PlayerCard call"
html = html.replace(old2, new2, 1)

html = html.replace("const APP_VERSION = 'v9.293';", "const APP_VERSION = 'v9.294';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.294 — PlayerCard badge mindenkori totalPoints alapján")
