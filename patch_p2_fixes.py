#!/usr/bin/env python3
"""P2 audit fixes:
1. Kategória scroll fade-out
2. Memoria responsive card size
3. Tapper hold feedback (already has scale, add brightness)
4. Game lock explanation toast
5. Version bump to v9.583
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

original = html

# ── 1. Version bump ──────────────────────────────────────────────────────────
assert html.count("v9.582") >= 1, "version not found"
html = html.replace("v9.582", "v9.583", 1)

# ── 2. Kategória (OtDolog) scroll fade-out ───────────────────────────────────
OLD_SCROLL = '      <div style={{ display:\'flex\', gap:8, overflowX:\'auto\', WebkitOverflowScrolling:\'touch\', width:\'100%\', paddingBottom:4 }}>\n        {players.map(p => {'
NEW_SCROLL = '      <div style={{ position:\'relative\', width:\'100%\' }}>\n        <div style={{ display:\'flex\', gap:8, overflowX:\'auto\', WebkitOverflowScrolling:\'touch\', width:\'100%\', paddingBottom:4 }}>\n        {players.map(p => {'
assert html.count(OLD_SCROLL) == 1, f"scroll old not found: {html.count(OLD_SCROLL)}"
html = html.replace(OLD_SCROLL, NEW_SCROLL, 1)

# Close the wrapper after the scroll div closes
OLD_SCROLL_CLOSE = '        })}\n      </div>\n\n      {/* Confirm loser or nobody */}'
NEW_SCROLL_CLOSE = '        })}\n        </div>\n        <div style={{ position:\'absolute\', top:0, right:0, bottom:4, width:48, background:`linear-gradient(to right, transparent, ${T.bg})`, pointerEvents:\'none\', borderRadius:\'0 12px 12px 0\' }} />\n      </div>\n\n      {/* Confirm loser or nobody */}'
assert html.count(OLD_SCROLL_CLOSE) == 1, f"scroll close not found: {html.count(OLD_SCROLL_CLOSE)}"
html = html.replace(OLD_SCROLL_CLOSE, NEW_SCROLL_CLOSE, 1)

# ── 3. Memoria responsive grid ───────────────────────────────────────────────
OLD_MEMORIA_GRID = "gridTemplateColumns:'repeat(4,1fr)', gap:7, width:'100%', maxWidth:520"
NEW_MEMORIA_GRID = "gridTemplateColumns:'repeat(auto-fill, minmax(68px, 1fr))', gap:7, width:'100%', maxWidth:520"
assert html.count(OLD_MEMORIA_GRID) == 1, f"memoria grid not found: {html.count(OLD_MEMORIA_GRID)}"
html = html.replace(OLD_MEMORIA_GRID, NEW_MEMORIA_GRID, 1)

# ── 4. Tapper Btn — add brightness on hold ───────────────────────────────────
OLD_TAPPER_BG = "background: released ? `${player.color}66` : player.color,"
NEW_TAPPER_BG = "background: released ? `${player.color}66` : player.color,\n          filter: holding && !released ? 'brightness(1.12)' : 'brightness(1)',"
assert html.count(OLD_TAPPER_BG) == 1, f"tapper bg not found: {html.count(OLD_TAPPER_BG)}"
html = html.replace(OLD_TAPPER_BG, NEW_TAPPER_BG, 1)

# ── 5. Game lock explanation ─────────────────────────────────────────────────
# Add lockToast state in GamesScreen (find the useState block)
OLD_LOCK_STATE = "  const [filterSheet, setFilterSheet] = useState(false);"
NEW_LOCK_STATE = "  const [filterSheet, setFilterSheet] = useState(false);\n  const [lockToast, setLockToast] = React.useState(null);\n  const lockToastRef = React.useRef(null);"
assert html.count(OLD_LOCK_STATE) == 1, f"lock state not found: {html.count(OLD_LOCK_STATE)}"
html = html.replace(OLD_LOCK_STATE, NEW_LOCK_STATE, 1)

# Modify toggle to show toast when locked
OLD_TOGGLE = "  const toggle = id => {\n    if (isLocked(id)) return;"
NEW_TOGGLE = """  const showLockToast = id => {
    const g = GAMES.find(x=>x.id===id);
    if (g?.comingSoon) return;
    let msg = '';
    const soloG = selectedGames.find(sid => ['powerhour','ovfj','farkasos'].includes(sid));
    if (soloG) {
      const soloName = GAMES.find(x=>x.id===soloG)?.name || soloG;
      msg = `A ${soloName} csak egyedül játszható`;
    } else if (buszSelected) {
      msg = 'A Busz nem kombinálható más játékokkal';
    } else if (beerpongSelected) {
      msg = 'A Beer Pong nem kombinálható más játékokkal';
    } else if (soloSelected) {
      msg = 'Ez a játék csak egyedül játszható';
    }
    if (!msg) return;
    if (lockToastRef.current) clearTimeout(lockToastRef.current);
    setLockToast(msg);
    lockToastRef.current = setTimeout(() => setLockToast(null), 2500);
  };
  const toggle = id => {
    if (isLocked(id)) { showLockToast(id); return; }"""
assert html.count(OLD_TOGGLE) == 1, f"toggle not found: {html.count(OLD_TOGGLE)}"
html = html.replace(OLD_TOGGLE, NEW_TOGGLE, 1)

# Add toast UI in GamesScreen return, before the BottomBar
OLD_BOTTOMBAR = "      <BottomBar extra={\n        <button onClick={() => setSheet(true)} style={{"
NEW_BOTTOMBAR = """      {lockToast && (
        <div style={{ position:'fixed', bottom:90, left:'50%', transform:'translateX(-50%)', zIndex:200, pointerEvents:'none',
          background:'rgba(26,42,74,0.88)', backdropFilter:'blur(8px)',
          borderRadius:14, padding:'11px 20px', maxWidth:'calc(100% - 48px)',
          fontFamily:T.font, fontWeight:700, fontSize:13, color:'#fff', textAlign:'center',
          boxShadow:'0 4px 18px rgba(0,0,0,0.22)', whiteSpace:'nowrap',
          animation:'toastIn .18s ease-out',
        }}>
          🔒 {lockToast}
        </div>
      )}
      <BottomBar extra={
        <button onClick={() => setSheet(true)} style={{"""
assert html.count(OLD_BOTTOMBAR) == 1, f"bottombar not found: {html.count(OLD_BOTTOMBAR)}"
html = html.replace(OLD_BOTTOMBAR, NEW_BOTTOMBAR, 1)

# Add toastIn keyframe animation (near other @keyframes)
OLD_KEYFRAME = "@keyframes nextBounce  { 0%,100%{transform:translateY(0) scale(1)} 40%{transform:translateY(-3px) scale(1.04)} 70%{transform:translateY(-1px) scale(1.01)} }"
NEW_KEYFRAME = """@keyframes toastIn { from { opacity:0; transform:translateX(-50%) translateY(8px); } to { opacity:1; transform:translateX(-50%) translateY(0); } }
    @keyframes nextBounce  { 0%,100%{transform:translateY(0) scale(1)} 40%{transform:translateY(-3px) scale(1.04)} 70%{transform:translateY(-1px) scale(1.01)} }"""
assert html.count(OLD_KEYFRAME) >= 1, "nextBounce keyframe not found"
html = html.replace(OLD_KEYFRAME, NEW_KEYFRAME, 1)

assert html != original, "No changes made!"
print(f"Changes made. New length: {len(html)}")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done.")
