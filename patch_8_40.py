#!/usr/bin/env python3
"""
v8.40:
1. PowerHour → Csapat kategória
2. Ringfire → solo-only (mint powerhour/ovfj)
3. Kopapir + Hajime → disabled (Coming Soon)
4. Rulett → 🔥 helyett ⭐ csillag ikon
5. Loverseny → lóverseny hanghatás indításkor
6. OVFJ observer → foglalt játékos nem választható (már megvolt, de ellenőrzés)
"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. PowerHour category: Egyéni → Csapat ───────────────────────────────────
OLD = "{ id:'powerhour', name:'Power Hour',            difficulty:'nehéz',   category:'Egyéni',"
NEW = "{ id:'powerhour', name:'Power Hour',            difficulty:'nehéz',   category:'Csapat',"
assert OLD in content, "PowerHour category not found"
content = content.replace(OLD, NEW, 1)
print("✓ PowerHour → Csapat")

# ── 2. Ringfire solo-only: add to toggle + selectAll + shuffle exclusions ──────
# toggle
OLD_TOGGLE = """    } else if (id === 'powerhour' || id === 'ovfj') {
      // Power Hour / Ország-Város solo-only
      setSelectedGames([id]);
    } else {
      // Deselect solo-only games if other game added
      setSelectedGames([...selectedGames.filter(x=>x!=='powerhour'&&x!=='ovfj'), id]);
    }"""
NEW_TOGGLE = """    } else if (id === 'powerhour' || id === 'ovfj' || id === 'ringfire') {
      // Power Hour / Ország-Város / Ring of Fire solo-only
      setSelectedGames([id]);
    } else {
      // Deselect solo-only games if other game added
      setSelectedGames([...selectedGames.filter(x=>x!=='powerhour'&&x!=='ovfj'&&x!=='ringfire'), id]);
    }"""
assert OLD_TOGGLE in content, "toggle not found"
content = content.replace(OLD_TOGGLE, NEW_TOGGLE, 1)

OLD_SELECTALL = "const selectAll = () => setSelectedGames(GAMES.filter(g=>g.id!=='busz'&&g.id!=='beerpong'&&g.id!=='powerhour'&&g.id!=='ovfj').map(g=>g.id));"
NEW_SELECTALL = "const selectAll = () => setSelectedGames(GAMES.filter(g=>g.id!=='busz'&&g.id!=='beerpong'&&g.id!=='powerhour'&&g.id!=='ovfj'&&g.id!=='ringfire').map(g=>g.id));"
assert OLD_SELECTALL in content, "selectAll not found"
content = content.replace(OLD_SELECTALL, NEW_SELECTALL, 1)

OLD_SHUFFLE = "    const pool = GAMES.filter(g=>g.id!=='busz'&&g.id!=='beerpong'&&g.id!=='powerhour'&&g.id!=='ovfj');"
NEW_SHUFFLE = "    const pool = GAMES.filter(g=>g.id!=='busz'&&g.id!=='beerpong'&&g.id!=='powerhour'&&g.id!=='ovfj'&&g.id!=='ringfire');"
assert OLD_SHUFFLE in content, "shuffle pool not found"
content = content.replace(OLD_SHUFFLE, NEW_SHUFFLE, 1)
print("✓ Ringfire → solo-only")

# ── 3. Kopapir + Hajime → disabled with Coming Soon label ────────────────────
# Find the game card rendering code where games are displayed
# Games have a disabled/coming-soon state via dnr or a disabled flag
# Easiest: add disabled:true to their GAMES entry and handle in GamesScreen

OLD_KOPAPIR = "  { id:'kopapir',   name:'Kő Papír Olló',         difficulty:'nehéz',   category:'Csapat', emoji:'✊',"
NEW_KOPAPIR = "  { id:'kopapir',   name:'Kő Papír Olló',         difficulty:'nehéz',   category:'Csapat', emoji:'✊', comingSoon:true,"
assert OLD_KOPAPIR in content, "kopapir not found"
content = content.replace(OLD_KOPAPIR, NEW_KOPAPIR, 1)

OLD_HAJIME = "  { id:'hajime',    name:'Hajime',                difficulty:'nehéz',   category:'Csapat', emoji:'😆',"
NEW_HAJIME = "  { id:'hajime',    name:'Hajime',                difficulty:'nehéz',   category:'Csapat', emoji:'😆', comingSoon:true,"
assert OLD_HAJIME in content, "hajime not found"
content = content.replace(OLD_HAJIME, NEW_HAJIME, 1)
print("✓ Kopapir + Hajime → comingSoon:true")

# isLocked: comingSoon games can't be selected
OLD_LOCKED = """  const isLocked = id => {
    if (id === 'busz') return otherSelected || beerpongSelected;"""
NEW_LOCKED = """  const isLocked = id => {
    const g = GAMES.find(x=>x.id===id);
    if (g?.comingSoon) return true;
    if (id === 'busz') return otherSelected || beerpongSelected;"""
assert OLD_LOCKED in content, "isLocked not found"
content = content.replace(OLD_LOCKED, NEW_LOCKED, 1)
print("✓ isLocked handles comingSoon")

# ── 4. Rulett: 🔥 → ⭐ ────────────────────────────────────────────────────────
# Outcome chip
OLD_FIRE_CHIP = """        <div style={{ display:'flex', alignItems:'center', gap:6, background:'rgba(255,255,255,0.7)', borderRadius:24, padding:'6px 14px', boxShadow:'0 1px 6px rgba(0,0,0,0.08)' }}>
          <span style={{ fontSize:16 }}>🔥</span>
          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:'#D05040' }}>1× tűz</span>
        </div>"""
NEW_FIRE_CHIP = """        <div style={{ display:'flex', alignItems:'center', gap:6, background:'rgba(255,255,255,0.7)', borderRadius:24, padding:'6px 14px', boxShadow:'0 1px 6px rgba(0,0,0,0.08)' }}>
          <span style={{ fontSize:16 }}>⭐</span>
          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:'#D05040' }}>1× csillag</span>
        </div>"""
assert OLD_FIRE_CHIP in content, "fire chip not found"
content = content.replace(OLD_FIRE_CHIP, NEW_FIRE_CHIP, 1)

# Card reveal icon
OLD_FIRE_CARD = """{res === 'pia' ? '🍺' : '🔥'}"""
NEW_FIRE_CARD = """{res === 'pia' ? '🍺' : '⭐'}"""
assert OLD_FIRE_CARD in content, "fire card icon not found"
content = content.replace(OLD_FIRE_CARD, NEW_FIRE_CARD, 1)

# Result text
OLD_FIRE_RESULT = """          {result === 'pia' ? '🍺 Pia! Iszol!' : '🔥 Tűz! Megúsztad!'}"""
NEW_FIRE_RESULT = """          {result === 'pia' ? '🍺 Pia! Iszol!' : '⭐ Csillag! Megúsztad!'}"""
assert OLD_FIRE_RESULT in content, "fire result text not found"
content = content.replace(OLD_FIRE_RESULT, NEW_FIRE_RESULT, 1)
print("✓ Rulett 🔥 → ⭐")

# ── 5. Loverseny: horse race sound on startRace ────────────────────────────────
# Add a tiny horse race sound (short crowd noise) using oscillator
OLD_START_RACE = """  const startRace = (finalBets) => {
    setPhase('race');
    posRef.current = [0,0,0,0];"""
NEW_START_RACE = """  const playRaceSound = () => {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const dur = 1.8;
      // Crowd cheer: multiple oscillators at varying freqs + white noise burst
      [220,330,440,550,660].forEach((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(freq + Math.random()*80, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(freq*1.4, ctx.currentTime + dur);
        gain.gain.setValueAtTime(0, ctx.currentTime + i*0.05);
        gain.gain.linearRampToValueAtTime(0.06, ctx.currentTime + i*0.05 + 0.1);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + dur);
        osc.connect(gain); gain.connect(ctx.destination);
        osc.start(ctx.currentTime + i*0.05); osc.stop(ctx.currentTime + dur);
      });
      // Trumpet fanfare: simple melody
      const fanfareNotes = [[659,0],[784,0.15],[880,0.3],[1047,0.45],[880,0.6],[1047,0.75]];
      fanfareNotes.forEach(([freq, t]) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'square';
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0, ctx.currentTime + t);
        gain.gain.linearRampToValueAtTime(0.12, ctx.currentTime + t + 0.04);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + t + 0.14);
        osc.connect(gain); gain.connect(ctx.destination);
        osc.start(ctx.currentTime + t); osc.stop(ctx.currentTime + t + 0.15);
      });
    } catch(e) {}
  };

  const startRace = (finalBets) => {
    setPhase('race');
    playRaceSound();
    posRef.current = [0,0,0,0];"""
assert OLD_START_RACE in content, "startRace not found"
content = content.replace(OLD_START_RACE, NEW_START_RACE, 1)
print("✓ Loverseny race sound added")

# ── 6. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v8.39';"
NEW_VER = "const APP_VERSION = 'v8.40';"
assert OLD_VER in content
content = content.replace(OLD_VER, NEW_VER, 1)
print("✓ Version → v8.40")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ Saved")
