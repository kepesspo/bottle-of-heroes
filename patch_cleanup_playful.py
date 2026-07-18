#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Playful maradványok kitakarítása: az egy-dizájn óta minden isPlayful ág a classic
# értéket veszi fel. Feloldjuk az inline ternáriákat, a pf* konstansokat konkrét
# értékre állítjuk, majd töröljük a felszabaduló deklarációkat. Vizuálisan 0 változás.
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'expected %d, found %d for: %r' % (count, n, old[:80])
    src = src.replace(old, new)

# ── AppBar ──
rep("""    <div className="appbar-shell" style={{ background: bg || T.surface, overflow:'hidden', ...(isPlayful ? { border:`2.5px solid ${T.ink}`, boxShadow:`0 5px 0 ${T.ink}` } : {}) }}>""",
    """    <div className="appbar-shell" style={{ background: bg || T.surface, overflow:'hidden' }}>""")
rep("""            ? <button onClick={onBack} style={{ width:44, height:44, background:'transparent', color:T.ink, cursor:'pointer', display:'grid', placeItems:'center', borderRadius:isPlayful?12:14, flexShrink:0, border: isPlayful?`2px solid ${T.ink}`:'none' }}>{Icon.back(T.ink)}</button>""",
    """            ? <button onClick={onBack} style={{ width:44, height:44, background:'transparent', color:T.ink, cursor:'pointer', display:'grid', placeItems:'center', borderRadius:14, flexShrink:0, border:'none' }}>{Icon.back(T.ink)}</button>""")
rep("""      {!isPlayful && <div style={{ height:2, background:`linear-gradient(90deg, ${T.mint}, ${T.coral})`, opacity:0.7 }} />}""",
    """      <div style={{ height:2, background:`linear-gradient(90deg, ${T.mint}, ${T.coral})`, opacity:0.7 }} />""")

# ── PrimaryButton ──
rep("      width:'100%', minHeight:sz.h, border: isPlayful ? `2.5px solid ${T.ink}` : 'none',",
    "      width:'100%', minHeight:sz.h, border: 'none',")
rep("      borderRadius: isPlayful ? 16 : sz.r, position:'relative', overflow:'hidden',",
    "      borderRadius: sz.r, position:'relative', overflow:'hidden',")
rep("      boxShadow: disabled ? 'none' : (isPlayful ? `0 5px 0 ${T.ink}` : `0 4px 18px ${baseColor}55`),",
    "      boxShadow: disabled ? 'none' : `0 4px 18px ${baseColor}55`,")

# ── SheetOverlay ──
rep("          border: isPlayful ? `2.5px solid ${T.ink}` : 'none',",
    "          border: 'none',")
rep("          boxShadow: isPlayful ? `0 -6px 0 ${T.ink}, 0 -8px 60px rgba(0,0,0,0.28)` : '0 -8px 60px rgba(0,0,0,0.28)',",
    "          boxShadow: '0 -8px 60px rgba(0,0,0,0.28)',")
rep("""            <button onClick={dismiss} style={{ width:32, height:32, borderRadius:10, border: isPlayful ? `2px solid ${T.ink}` : 'none', background:T.bgSoft, color:T.inkSoft, cursor:'pointer', display:'grid', placeItems:'center', flexShrink:0 }}>""",
    """            <button onClick={dismiss} style={{ width:32, height:32, borderRadius:10, border: 'none', background:T.bgSoft, color:T.inkSoft, cursor:'pointer', display:'grid', placeItems:'center', flexShrink:0 }}>""")

# ── StatsScreen pf* konstansok ──
rep("  const pfBorder = isPlayful ? `2px solid ${T.ink}` : 'none';", "  const pfBorder = 'none';")
rep("  const pfShadow = isPlayful ? `0 4px 0 ${T.ink}` : T.shadow;", "  const pfShadow = T.shadow;")

# ── EventLogScreen pf* konstansok ──
rep("  const pfBorderE = isPlayful ? `2px solid ${T.ink}` : null;", "  const pfBorderE = null;")
rep("  const pfShadowE = isPlayful ? `0 4px 0 ${T.ink}` : T.shadow;", "  const pfShadowE = T.shadow;")

# ── PlayersScreen ──
rep("            <PlayerCard key={p.id} p={p} index={i} playful={isPlayful} onEdit={() => setEditing(p.id)} onRemove={() => removePlayer(p.id)} badge={getBadge(p)} />",
    "            <PlayerCard key={p.id} p={p} index={i} onEdit={() => setEditing(p.id)} onRemove={() => removePlayer(p.id)} badge={getBadge(p)} />")
rep("""          <div style={{ background:T.surface, borderRadius:12, boxShadow: isPlayful ? `0 3px 0 ${T.ink}` : T.shadow, border: isPlayful ? `2px solid ${T.ink}` : 'none', padding:'11px 14px', display:'flex', alignItems:'center', gap:10, userSelect:'none' }}>""",
    """          <div style={{ background:T.surface, borderRadius:12, boxShadow: T.shadow, border: 'none', padding:'11px 14px', display:'flex', alignItems:'center', gap:10, userSelect:'none' }}>""")

# ── NetflixTile: isPlayful + tilt teljesen felszabadul ──
rep("""  const isPlayful = useAppDesign() === 'playful';
  const tilt = isPlayful ? [-1.8, 1.5, -1.2, 2, -1.5, 1.3][((g.id||'').charCodeAt(0) + (g.id||'').length) % 6] : 0;
  const diff = DIFFICULTY_META[g.difficulty] || { tone: '#aaa' };""",
    """  const diff = DIFFICULTY_META[g.difficulty] || { tone: '#aaa' };""")

# ── GameTile ──
rep("""  const isPlayful = useAppDesign() === 'playful';
  const tilt = isPlayful ? [-1.8, 1.5, -1.2, 2, -1.5, 1.3][((g.id||'').charCodeAt(0) + (g.id||'').length) % 6] : 0;""",
    """  const tilt = 0;""")
rep("      boxShadow: isPlayful ? (selected ? `0 4px 0 ${selColor}` : `0 4px 0 ${T.ink}`) : (selected ? `0 8px 22px ${selColor}55` : T.shadow),",
    "      boxShadow: selected ? `0 8px 22px ${selColor}55` : T.shadow,")
rep("      border: selected ? `2.5px solid ${selColor}` : onLongPress ? `2px dashed ${T.purple}` : (isPlayful ? `2.5px solid ${T.ink}` : '2px solid transparent'),",
    "      border: selected ? `2.5px solid ${selColor}` : onLongPress ? `2px dashed ${T.purple}` : '2px solid transparent',")
rep("      transform: isPlayful && !bouncing ? `rotate(${tilt}deg)` : 'none',",
    "      transform: 'none',")

# ── Beer Pong stat kártyák (51754/51800) ──
rep("        <div key={cat.key} style={{background:T.surface,borderRadius:14,padding:'10px 12px',boxShadow:isPlayful?`0 4px 0 ${T.ink}`:T.shadow,border:isPlayful?`2px solid ${T.ink}`:'none',display:'flex',flexDirection:'column',gap:7}}>",
    "        <div key={cat.key} style={{background:T.surface,borderRadius:14,padding:'10px 12px',boxShadow:T.shadow,border:'none',display:'flex',flexDirection:'column',gap:7}}>")
rep("          <div key={p.id} style={{display:'flex',alignItems:'center',gap:12,background:mine?T.mintSoft:T.surface,borderRadius:16,padding:final&&i===0?'16px 16px':'12px 16px',boxShadow:isPlayful?`0 4px 0 ${T.ink}`:T.shadow,border:mine?`2px solid ${T.mint}`:(isPlayful?`2px solid ${T.ink}`:'none')}}>",
    "          <div key={p.id} style={{display:'flex',alignItems:'center',gap:12,background:mine?T.mintSoft:T.surface,borderRadius:16,padding:final&&i===0?'16px 16px':'12px 16px',boxShadow:T.shadow,border:mine?`2px solid ${T.mint}`:'none'}}>")

# ── FavTile ──
rep("        border: selected ? `2.5px solid ${T.mint}` : (isPlayful ? `2.5px solid ${T.ink}` : '2px solid transparent'),",
    "        border: selected ? `2.5px solid ${T.mint}` : '2px solid transparent',")
rep("        boxShadow: isPlayful ? (selected ? `0 4px 0 ${T.mint}` : `0 4px 0 ${T.ink}`) : (selected ? `0 4px 16px ${T.mint}33` : T.shadow),",
    "        boxShadow: selected ? `0 4px 16px ${T.mint}33` : T.shadow,")

# ── EndScreen pf* konstansok ──
rep("  const pfBorderR = isPlayful ? `2px solid ${T.ink}` : 'none';", "  const pfBorderR = 'none';")
rep("  const pfShadowR = isPlayful ? `0 4px 0 ${T.ink}` : T.shadow;", "  const pfShadowR = T.shadow;")

# ── BugReportsCard (56550) ──
rep("    <div style={{ background:T.surface, borderRadius:14, boxShadow: isPlayful ? `0 4px 0 ${T.ink}` : T.shadow, border: isPlayful ? `2px solid ${T.ink}` : 'none', padding:'10px 14px', display:'flex', alignItems:'center', gap:12, position:'relative', overflow:'hidden' }}>",
    "    <div style={{ background:T.surface, borderRadius:14, boxShadow: T.shadow, border: 'none', padding:'10px 14px', display:'flex', alignItems:'center', gap:12, position:'relative', overflow:'hidden' }}>")

# ── HomeScreen: homeDesign state + effekt + isPlayful ──
rep("""  const [homeDesign, setHomeDesign] = React.useState(() => { try { return localStorage.getItem('boh_home_design') || 'classic'; } catch(e) { return 'classic'; } });
  React.useEffect(() => {
    if (typeof window.onHomeDesign === 'function') {
      const unsub = window.onHomeDesign(d => {
        const val = d === 'playful' ? 'playful' : 'classic';
        setHomeDesign(val);
        try { localStorage.setItem('boh_home_design', val); } catch(e) {}
      });
      return () => unsub();
    }
  }, []);
  const isPlayful = homeDesign === 'playful';
""", "")

# ── EventLog decl (van egy egyedi variáns) ──
rep("  const isPlayful = useAppDesign() === 'playful' && !deepLink;\n", "")

# ── Maradék egyforma isPlayful deklarációk törlése (most már mind unused) ──
decl = "  const isPlayful = useAppDesign() === 'playful';\n"
cnt = src.count(decl)
assert cnt >= 5, 'unexpected decl count: %d' % cnt
src = src.replace(decl, "")

# ── Ellenőrzés: nem maradt isPlayful ──
if 'isPlayful' in src:
    for ln, line in enumerate(src.splitlines(), 1):
        if 'isPlayful' in line:
            print('MARADT:', repr(line[:120]))
    raise SystemExit('isPlayful maradt — nem írom ki')

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — isPlayful removed, %d plain decls dropped' % cnt)
