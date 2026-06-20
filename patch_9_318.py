#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Csapat mechanic fix — everyone loses only 1 drink (not diffDrinks)
old_advance_team = "      ? players.map((p,i) => i===winnerIdx ? {...p,points:p.points+1} : {...p,drinks:p.drinks+diffDrinks})"
new_advance_team = "      ? players.map((p,i) => i===winnerIdx ? {...p,points:p.points+1} : {...p,drinks:p.drinks+1})"
assert old_advance_team in html, "FAIL: advanceTeam drinks"
html = html.replace(old_advance_team, new_advance_team, 1)

# ── 2. uveg difficulty: közepes → könnyű
old_uveg = "  { id:'uveg',      roundTime:'fast',  name:'Az üveg',               difficulty:'közepes',"
new_uveg = "  { id:'uveg',      roundTime:'fast',  name:'Az üveg',               difficulty:'könnyű',"
assert old_uveg in html, "FAIL: uveg difficulty"
html = html.replace(old_uveg, new_uveg, 1)

# ── 3. szerencse difficulty: közepes → könnyű
old_szerencse = "  { id:'szerencse', roundTime:'fast',  name:'Szerencsekerék',        difficulty:'közepes',"
new_szerencse = "  { id:'szerencse', roundTime:'fast',  name:'Szerencsekerék',        difficulty:'könnyű',"
assert old_szerencse in html, "FAIL: szerencse difficulty"
html = html.replace(old_szerencse, new_szerencse, 1)

# ── 4. Páros anti-repeat — track recent opponent, exclude from random pick
old_paired_effect = """  useEffect(() => {
    if (currentGame.category !== 'Páros') { setSelectedOpponent(null); return; }
    const others = players.filter((_,i) => i !== turn);
    if (others.length === 0) return;
    setSelectedOpponent(others[Math.floor(Math.random() * others.length)]);
  }, [turn, gameIdx]);"""
new_paired_effect = """  const recentOpponentRef = React.useRef(null);
  useEffect(() => {
    if (currentGame.category !== 'Páros') { setSelectedOpponent(null); return; }
    const others = players.filter((_,i) => i !== turn);
    if (others.length === 0) return;
    const pool = others.length > 1 ? others.filter(p => p.id !== recentOpponentRef.current) : others;
    const pick = pool[Math.floor(Math.random() * pool.length)];
    recentOpponentRef.current = pick.id;
    setSelectedOpponent(pick);
  }, [turn, gameIdx]);"""
assert old_paired_effect in html, "FAIL: paired opponent effect"
html = html.replace(old_paired_effect, new_paired_effect, 1)

# ── 5. Bonus build — redesign: top gives leader extra drinks, last gives lowest +1 point
old_bonus_build = """      const type = Math.random() < 0.5 ? 'top' : 'last';
      const lastDrinks = Math.max(1, last.drinks) * 2;
      // top: pick 3 random OTHER players to receive 1 drink each
      const others = newPlayers.filter(p => p.id !== first.id);
      const recipients = others.length > 0
        ? Array.from({length:3}, () => others[Math.floor(Math.random()*others.length)])
        : [];
      const bonus = type === 'top'
        ? { type:'top', player: first, recipients, drinks: 3 }
        : { type:'last', player: last, drinks: lastDrinks };"""
new_bonus_build = """      const type = Math.random() < 0.5 ? 'top' : 'last';
      // top: leader drinks 2 extra (catch-up: others benefit)
      // last: lowest scorer gets +1 point (comeback mechanic)
      const bonus = type === 'top'
        ? { type:'top', player: first, drinks: 2 }
        : { type:'last', player: last, points: 1 };"""
assert old_bonus_build in html, "FAIL: bonus build"
html = html.replace(old_bonus_build, new_bonus_build, 1)

# ── 6. Bonus apply in dismissBonus — match new structure
old_bonus_apply = """    const updated = newPlayers.map(pl => {
      if (bonus.type === 'top') {
        const extra = (bonus.recipients||[]).filter(r => r.id === pl.id).length;
        return extra > 0 ? {...pl, drinks: pl.drinks + extra} : pl;
      }
      if (bonus.type === 'last' && pl.id === bonus.player.id) return {...pl, drinks: pl.drinks + bonus.drinks};
      return pl;
    });"""
new_bonus_apply = """    const updated = newPlayers.map(pl => {
      if (bonus.type === 'top' && pl.id === bonus.player.id) return {...pl, drinks: pl.drinks + bonus.drinks};
      if (bonus.type === 'last' && pl.id === bonus.player.id) return {...pl, points: pl.points + (bonus.points||1)};
      return pl;
    });"""
assert old_bonus_apply in html, "FAIL: bonus apply"
html = html.replace(old_bonus_apply, new_bonus_apply, 1)

# ── 7. BonusOverlay JSX — top: leader drinks text; last: lowest gets point text
old_overlay_top_header = """                <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', lineHeight:1.5 }}>A legtöbb pontú játékos<br/>3 kortyt oszt ki:</div>
                <div style={{ display:'flex', gap:8, justifyContent:'center', flexWrap:'wrap' }}>
                  {(bonusOverlay.recipients||[]).map((r,i) => (
                    <div key={r.id + '_' + i} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:3 }}>
                      <div style={{ width:38, height:38, borderRadius:'50%', background:r.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff' }}>{r.name.charAt(0).toUpperCase()}</div>"""
new_overlay_top_header = """                <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', lineHeight:1.5 }}>A vezető iszik — <span style={{ color:T.coral, fontWeight:900 }}>{bonusOverlay.drinks} korty</span><br/>Mindenki más levesz egyet!</div>
                <div style={{ display:'flex', gap:8, justifyContent:'center', flexWrap:'wrap' }}>
                  {[].map((r,i) => (
                    <div key={r.id + '_' + i} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:3 }}>
                      <div style={{ width:38, height:38, borderRadius:'50%', background:r.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff' }}>{r.name.charAt(0).toUpperCase()}</div>"""
assert old_overlay_top_header in html, "FAIL: overlay top header"
html = html.replace(old_overlay_top_header, new_overlay_top_header, 1)

old_overlay_last = """                <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, textAlign:'center', lineHeight:1.5 }}>Az utolsó helyen álló<br/>duplán iszik — <span style={{ color:T.coral, fontWeight:900 }}>{bonusOverlay.drinks} korty</span></div>"""
new_overlay_last = """                <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, textAlign:'center', lineHeight:1.5 }}>Az utolsó helyen álló<br/>visszakapaszkodik — <span style={{ color:T.mint, fontWeight:900 }}>+{bonusOverlay.points||1} pont</span></div>"""
assert old_overlay_last in html, "FAIL: overlay last"
html = html.replace(old_overlay_last, new_overlay_last, 1)

# Also update the top emoji/header to match new meaning
old_overlay_top_emoji = """            <div style={{ fontSize:52, lineHeight:1 }}>{bonusOverlay.type === 'top' ? '🏆' : '😵'}</div>"""
new_overlay_top_emoji = """            <div style={{ fontSize:52, lineHeight:1 }}>{bonusOverlay.type === 'top' ? '😅' : '🌟'}</div>"""
assert old_overlay_top_emoji in html, "FAIL: overlay emoji"
html = html.replace(old_overlay_top_emoji, new_overlay_top_emoji, 1)

old_overlay_top_title = """                <div style={{ fontFamily:T.font, fontWeight:800, fontSize:17, color:T.ink }}>{bonusOverlay.player.name} oszt!</div>"""
new_overlay_top_title = """                <div style={{ fontFamily:T.font, fontWeight:800, fontSize:17, color:T.ink }}>{bonusOverlay.player.name} iszik!</div>"""
assert old_overlay_top_title in html, "FAIL: overlay top title"
html = html.replace(old_overlay_top_title, new_overlay_top_title, 1)

html = html.replace("const APP_VERSION = 'v9.317';", "const APP_VERSION = 'v9.318';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.318 — Gameplay balance: Csapat 1 drink, uveg/szerencse könnyű, Páros anti-repeat, Bonus catch-up redesign")
