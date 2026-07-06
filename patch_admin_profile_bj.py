import re
with open('index.html', encoding='utf-8') as f:
    c = f.read()

# ═══ 1. Firebase helperek: comingSoon lista (admin kapcsolható) ═══════════════
OLD = """  window.getHiddenGames = function() {"""
NEW = """  window.getComingSoon = function() {
    return db.collection('config').doc('comingSoonGames').get().then(function(d) {
      return d.exists ? (d.data().ids || []) : null;
    }).catch(function() { return null; });
  };
  window.setComingSoon = function(ids) {
    return db.collection('config').doc('comingSoonGames').set({ ids: ids }).catch(function(e) { console.warn('setComingSoon', e); });
  };
  window.onComingSoon = function(cb) {
    return db.collection('config').doc('comingSoonGames').onSnapshot(function(d) {
      cb(d.exists ? (d.data().ids || []) : null);
    });
  };
  window.getHiddenGames = function() {"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 2. GamesScreen: comingSoon lista alkalmazása a GAMES-re ═════════════════
OLD = """  const [_hiddenGames, _setHiddenGames] = React.useState([]);"""
NEW = """  const [_hiddenGames, _setHiddenGames] = React.useState([]);
  const [, _setCsVer] = React.useState(0);
  React.useEffect(() => {
    if (typeof window.onComingSoon !== 'function') return;
    const unsub = window.onComingSoon(ids => {
      if (ids === null) return;
      GAMES.forEach(g => { g.comingSoon = ids.includes(g.id); });
      _setCsVer(v => v + 1);
    });
    return () => unsub && unsub();
  }, []);"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 3. AdminGames: Élő/Hamarosan kapcsoló ═══════════════════════════════════
OLD = """function AdminGames() {
  const [hidden, setHidden] = React.useState([]);
  const [saving, setSaving] = React.useState(false);"""
NEW = """function AdminGames() {
  const [hidden, setHidden] = React.useState([]);
  const [saving, setSaving] = React.useState(false);
  const [soon, setSoon] = React.useState(null);

  React.useEffect(() => {
    if (typeof window.onComingSoon !== 'function') return;
    const unsub = window.onComingSoon(ids => {
      setSoon(ids !== null ? ids : GAMES.filter(g => g.comingSoon).map(g => g.id));
    });
    return () => unsub && unsub();
  }, []);

  const soonList = soon !== null ? soon : GAMES.filter(g => g.comingSoon).map(g => g.id);
  const isSoon = id => soonList.includes(id);
  function toggleSoon(e, id) {
    e.stopPropagation();
    const next = soonList.includes(id) ? soonList.filter(x => x !== id) : [...soonList, id];
    setSaving(true);
    window.setComingSoon(next).finally(() => setSaving(false));
  }"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# gomb a sorba a szem-toggle elé
OLD = """            <div style={{ flex:1, minWidth:0 }}>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{g.name}</div>
              <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, marginTop:1 }}>{g.category} · {g.difficulty}</div>
            </div>"""
NEW = """            <div style={{ flex:1, minWidth:0 }}>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{g.name}</div>
              <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, marginTop:1 }}>{g.category} · {g.difficulty}</div>
            </div>
            <button onClick={e => toggleSoon(e, g.id)} style={{ flexShrink:0, padding:'6px 10px', borderRadius:999, border:`1.5px solid ${isSoon(g.id) ? '#f59e0b' : T.mint}`, background: isSoon(g.id) ? 'rgba(245,158,11,0.08)' : 'rgba(37,181,114,0.08)', fontFamily:T.font, fontWeight:800, fontSize:11, color: isSoon(g.id) ? '#b45309' : T.mint, cursor:'pointer', whiteSpace:'nowrap' }}>
              {isSoon(g.id) ? '🔒 Hamarosan' : '✅ Élő'}
            </button>"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 4. Játékos szerkesztés lezárásakor profil mentés Firebase-be ═════════════
OLD = """      {editing &&
        <PlayerEditSheet
          player={players.find(p => p.id === editing)}
          onClose={() => setEditing(null)}"""
NEW = """      {editing &&
        <PlayerEditSheet
          player={players.find(p => p.id === editing)}
          onClose={() => {
            const p = players.find(pp => pp.id === editing);
            setEditing(null);
            // Egyedi nevű, profil nélküli játékos → automatikus profil mentés Firebase-be
            if (p && !p.profileId && p.name && p.name.trim() && !/^Játékos \\d+$/.test(p.name.trim()) && typeof window.saveProfile === 'function') {
              const nm = p.name.trim();
              (window.getProfiles ? window.getProfiles() : Promise.resolve([])).then(profs => {
                const ex = (profs || []).find(pr => (pr.name || '').trim().toLowerCase() === nm.toLowerCase() || (pr.nickname || '').trim().toLowerCase() === nm.toLowerCase());
                if (ex) return ex.id;
                return window.saveProfile({ name: nm, color: p.color, img: p.img || null });
              }).then(pid => {
                if (pid) setPlayers(prev => prev.map(pp => pp.id === p.id ? { ...pp, profileId: pid } : pp));
              }).catch(() => {});
            }
          }}"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ 5. Blackjack ikon + banner bekötés ══════════════════════════════════════
OLD = "const IMGS = {"
NEW = """const IMGS = {
  'blackjack_icon.png': 'assets/blackjack_icon.png',
  'blackjack_banner.png': 'assets/blackjack_banner.png',"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

OLD = "{ id:'blackjack', roundTime:'slow',  name:'Blackjack',             difficulty:'közepes', category:'Csapat', emoji:'🂡', symbol:null, img:null, banner:null,"
NEW = "{ id:'blackjack', roundTime:'slow',  name:'Blackjack',             difficulty:'közepes', category:'Csapat', emoji:'🂡', symbol:IMGS['blackjack_icon.png'], img:IMGS['blackjack_icon.png'], banner:IMGS['blackjack_banner.png'],"
assert OLD in c, "blackjack GAMES entry not found"
c = c.replace(OLD, NEW, 1)

c = re.sub(r'v9\.783', 'v9.784', c, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("Done v9.784")
