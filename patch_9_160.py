#!/usr/bin/env python3
"""patch_9_160.py — RitmusGame: trap emoji (-1 pont ha megnyomják)"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.159';" in content
content = content.replace("const APP_VERSION = 'v9.159';", "const APP_VERSION = 'v9.160';")

# 1. Add TRAP_EMOJI constant and trap logic in spawnNext
OLD_EMOJIS = "  const EMOJIS = ['🎯','⭐','🔥','💎','🎵','🍀','⚡','🎪','🦋','🎸','🎲','🚀'];"
NEW_EMOJIS  = """  const EMOJIS = ['🎯','⭐','🔥','💎','🎵','🍀','⚡','🎪','🦋','🎸','🎲','🚀'];
  const TRAP_EMOJI = '💀';
  const TRAP_CHANCE = 0.2; // 20% chance"""
assert OLD_EMOJIS in content, "EMOJIS not found"
content = content.replace(OLD_EMOJIS, NEW_EMOJIS, 1)

# 2. spawnNext: sometimes spawn trap
OLD_SPAWN_EMOJI = """    const pos = Math.floor(Math.random() * GRID);
    const emoji = EMOJIS[Math.floor(Math.random() * EMOJIS.length)];
    setActiveBtn({ pos, emoji });"""
NEW_SPAWN_EMOJI = """    const pos = Math.floor(Math.random() * GRID);
    const isTrap = Math.random() < TRAP_CHANCE;
    const emoji = isTrap ? TRAP_EMOJI : EMOJIS[Math.floor(Math.random() * EMOJIS.length)];
    setActiveBtn({ pos, emoji, isTrap });"""
assert OLD_SPAWN_EMOJI in content, "spawn emoji not found"
content = content.replace(OLD_SPAWN_EMOJI, NEW_SPAWN_EMOJI, 1)

# 3. handleTap: trap gives -1 instead of +1
OLD_HANDLE_TAP = """  const handleTap = (pos) => {
    if (!activeBtn || activeBtn.pos !== pos) return;
    // Correct tap
    clearTimeout(btnTimerRef.current);
    setActiveBtn(null);
    scoreRef.current += 1;
    setCurrentScore(scoreRef.current);
    // Spawn next immediately after short gap
    spawnTimerRef.current = setTimeout(spawnNext, 100);
  };"""
NEW_HANDLE_TAP = """  const handleTap = (pos) => {
    if (!activeBtn || activeBtn.pos !== pos) return;
    clearTimeout(btnTimerRef.current);
    const wasTrap = activeBtn.isTrap;
    setActiveBtn(wasTrap ? { pos, emoji:'💥', isTrap:true, flash:true } : null);
    if (wasTrap) {
      scoreRef.current = Math.max(0, scoreRef.current - 1);
      setCurrentScore(scoreRef.current);
      // brief flash then clear
      spawnTimerRef.current = setTimeout(() => { setActiveBtn(null); setTimeout(spawnNext, 80); }, 300);
    } else {
      setActiveBtn(null);
      scoreRef.current += 1;
      setCurrentScore(scoreRef.current);
      spawnTimerRef.current = setTimeout(spawnNext, 100);
    }
  };"""
assert OLD_HANDLE_TAP in content, "handleTap not found"
content = content.replace(OLD_HANDLE_TAP, NEW_HANDLE_TAP, 1)

# 4. Grid rendering: trap gets coral/red background
OLD_GRID_ACTIVE = """                style={{ height:72, borderRadius:16, background: isActive ? T.mint : T.surfaceMuted, border: isActive ? `3px solid ${T.mint}` : '3px solid transparent', display:'grid', placeItems:'center', cursor:'pointer', transition:'background .06s', boxShadow: isActive ? `0 0 18px ${T.mint}88` : 'none' }}>
                {isActive && <span style={{ fontSize:30, animation:'popIn .1s' }}>{activeBtn.emoji}</span>}"""
NEW_GRID_ACTIVE = """                style={{ height:72, borderRadius:16, background: isActive ? (activeBtn.isTrap ? T.coral : T.mint) : T.surfaceMuted, border: isActive ? `3px solid ${activeBtn.isTrap ? T.coral : T.mint}` : '3px solid transparent', display:'grid', placeItems:'center', cursor:'pointer', transition:'background .06s', boxShadow: isActive ? `0 0 18px ${activeBtn.isTrap ? T.coral : T.mint}88` : 'none' }}>
                {isActive && <span style={{ fontSize:30, animation:'popIn .1s' }}>{activeBtn.emoji}</span>}"""
assert OLD_GRID_ACTIVE in content, "grid active not found"
content = content.replace(OLD_GRID_ACTIVE, NEW_GRID_ACTIVE, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.160 ready")
