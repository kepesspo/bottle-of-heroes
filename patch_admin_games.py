import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add 'games' tab to AdminScreen TABS list
OLD1 = "  const TABS = [['profiles','👤','Profilok'],['events','📅','Események'],['db','🗄️','Adatbázis']];"
NEW1 = "  const TABS = [['profiles','👤','Profilok'],['events','📅','Események'],['db','🗄️','Adatbázis'],['games','🎮','Játékok']];"
assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. Add AdminGames render in tab switcher body
OLD2 = "        {tab === 'db'       && <AdminDatabase />}\n      </div>"
NEW2 = "        {tab === 'db'       && <AdminDatabase />}\n        {tab === 'games'    && <AdminGames />}\n      </div>"
assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# 3. Insert AdminGames component before AdminDatabase
ADMIN_GAMES_COMPONENT = '''// ── Admin: Games tab ──────────────────────────────────────────────────────────
const HIDDEN_GAMES_KEY = 'hiddenGames';
function getHiddenGames() {
  try { return JSON.parse(localStorage.getItem(HIDDEN_GAMES_KEY) || '[]'); } catch(e) { return []; }
}
function setHiddenGames(list) {
  localStorage.setItem(HIDDEN_GAMES_KEY, JSON.stringify(list));
}
function AdminGames() {
  const [hidden, setHidden] = React.useState(() => getHiddenGames());

  function toggle(id) {
    const next = hidden.includes(id) ? hidden.filter(x => x !== id) : [...hidden, id];
    setHiddenGames(next);
    setHidden(next);
  }

  function showAll() {
    setHiddenGames([]);
    setHidden([]);
  }

  return (
    <div style={{ padding:'16px' }}>
      {hidden.length > 0 && (
        <button onClick={showAll} style={{ width:'100%', padding:'11px', borderRadius:12, border:'none', background:T.mint, fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', cursor:'pointer', marginBottom:14, WebkitTapHighlightColor:'transparent' }}>
          Összes megjelenítése
        </button>
      )}
      <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:10 }}>
        Rejtett: {hidden.length} / {GAMES.length}
      </div>
      {GAMES.map(g => {
        const isHidden = hidden.includes(g.id);
        return (
          <div key={g.id} onClick={() => toggle(g.id)} style={{ display:'flex', alignItems:'center', gap:12, background:T.surface, borderRadius:14, padding:'10px 14px', marginBottom:8, boxShadow:T.shadow, cursor:'pointer', opacity: isHidden ? 0.45 : 1, WebkitTapHighlightColor:'transparent' }}>
            {g.img ? (
              <img src={g.img} style={{ width:40, height:40, borderRadius:10, objectFit:'cover', flexShrink:0 }} />
            ) : (
              <div style={{ width:40, height:40, borderRadius:10, background:g.color||'#888', flexShrink:0, display:'grid', placeItems:'center' }}>
                <span style={{ fontSize:20 }}>{g.emoji}</span>
              </div>
            )}
            <div style={{ flex:1, minWidth:0 }}>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{g.name}</div>
              <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, marginTop:1 }}>{g.category} · {g.difficulty}</div>
            </div>
            <div style={{ width:36, height:36, borderRadius:10, border:`2px solid ${isHidden ? '#ef4444' : T.mint}`, background: isHidden ? '#fef2f2' : 'rgba(37,181,114,0.08)', display:'grid', placeItems:'center', flexShrink:0 }}>
              {isHidden ? (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={T.mint} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

'''

OLD3 = "// ── Admin: Database tab ──────────────────────────────────────────────────────"
assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, ADMIN_GAMES_COMPONENT + OLD3, 1)

# 4. Filter hidden games in GamesScreen visibleGames line
OLD4 = "  const visibleGames = GAMES.filter(gameMatchesFilter).sort((a,b) => (a.comingSoon?1:0) - (b.comingSoon?1:0));"
NEW4 = "  const _hiddenGames = getHiddenGames();\n  const visibleGames = GAMES.filter(g => !_hiddenGames.includes(g.id)).filter(gameMatchesFilter).sort((a,b) => (a.comingSoon?1:0) - (b.comingSoon?1:0));"
assert OLD4 in content, "OLD4 not found"
content = content.replace(OLD4, NEW4, 1)

# 5. Version bump
content = re.sub(r'v9\.701', 'v9.702', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.702")
