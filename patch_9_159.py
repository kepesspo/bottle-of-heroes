#!/usr/bin/env python3
"""patch_9_159.py — RitmusGame: gyorsul a spawn az idő előrehaladtával"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.158';" in content
content = content.replace("const APP_VERSION = 'v9.158';", "const APP_VERSION = 'v9.159';")

# 1. Add startTimeRef
OLD_END_REF = "  const endTimeRef = useRef(0);\n  const isP2Ref = useRef(false);"
NEW_END_REF  = "  const endTimeRef = useRef(0);\n  const startTimeRef = useRef(0);\n  const isP2Ref = useRef(false);"
assert OLD_END_REF in content, "endTimeRef not found"
content = content.replace(OLD_END_REF, NEW_END_REF, 1)

# 2. spawnNext: visibleMs based on elapsed progress (slow→fast)
OLD_SPAWN = """  const spawnNext = () => {
    if (Date.now() >= endTimeRef.current) return;
    const pos = Math.floor(Math.random() * GRID);
    const emoji = EMOJIS[Math.floor(Math.random() * EMOJIS.length)];
    setActiveBtn({ pos, emoji });
    // Button visible 380–580ms then disappears, next spawns immediately after
    const visibleMs = 380 + Math.random() * 200;
    btnTimerRef.current = setTimeout(() => {
      setActiveBtn(null);
      // 80ms gap between buttons
      spawnTimerRef.current = setTimeout(spawnNext, 80);
    }, visibleMs);
  };"""

NEW_SPAWN = """  const spawnNext = () => {
    if (Date.now() >= endTimeRef.current) return;
    const pos = Math.floor(Math.random() * GRID);
    const emoji = EMOJIS[Math.floor(Math.random() * EMOJIS.length)];
    setActiveBtn({ pos, emoji });
    // Progress 0→1 over DURATION seconds — button gets faster as time passes
    const elapsed = Date.now() - startTimeRef.current;
    const progress = Math.min(1, elapsed / (DURATION * 1000));
    // visible: 750ms at start → 200ms at end
    const visibleMs = Math.max(200, 750 - progress * 550) + Math.random() * 80;
    // gap: 120ms at start → 40ms at end
    const gapMs = Math.max(40, 120 - progress * 80);
    btnTimerRef.current = setTimeout(() => {
      setActiveBtn(null);
      spawnTimerRef.current = setTimeout(spawnNext, gapMs);
    }, visibleMs);
  };"""

assert OLD_SPAWN in content, "spawnNext not found"
content = content.replace(OLD_SPAWN, NEW_SPAWN, 1)

# 3. Store startTime when round starts
OLD_END_ASSIGN = "    endTimeRef.current = endTime;"
NEW_END_ASSIGN  = "    endTimeRef.current = endTime;\n    startTimeRef.current = Date.now();"
assert OLD_END_ASSIGN in content, "endTime assign not found"
content = content.replace(OLD_END_ASSIGN, NEW_END_ASSIGN, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.159 ready")
