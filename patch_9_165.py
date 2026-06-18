#!/usr/bin/env python3
"""patch_9_165.py — Mit Választanál: automatikus result banner, nincs gomb"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.164';" in content
content = content.replace("const APP_VERSION = 'v9.164';", "const APP_VERSION = 'v9.165';")

# 1. Add useEffect to auto-fire handleResult after reveal/timeout
OLD_CLEANUP = "  useEffect(() => () => clearInterval(ivRef.current), []);"
NEW_CLEANUP  = """  useEffect(() => () => clearInterval(ivRef.current), []);

  // Auto-fire result after reveal or timeout — no button needed
  useEffect(() => {
    if (revealed && !advancedRef.current) {
      const majorityA = q.statsA >= 50;
      const won = choice ? (choice === 'a' ? majorityA : !majorityA) : false;
      const t = setTimeout(() => handleResult(won), 1200);
      return () => clearTimeout(t);
    }
  }, [revealed]);

  useEffect(() => {
    if (timedOut && !revealed && !advancedRef.current) {
      const t = setTimeout(() => handleResult(false), 800);
      return () => clearTimeout(t);
    }
  }, [timedOut]);"""

assert OLD_CLEANUP in content, "cleanup not found"
content = content.replace(OLD_CLEANUP, NEW_CLEANUP, 1)

# 2. Remove the manual buttons from JSX (timeout "Tovább" + revealed "+1 pont/Iszik" button)
OLD_TIMEOUT_BTN = """        <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginTop:4 }}>{challenger?.name} nem döntött — iszik!</div>
          <button onClick={() => handleResult(false)} style={{ marginTop:12, width:'100%', padding:'14px 0', background:T.coral, border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:16, cursor:'pointer' }}>Tovább</button>"""
NEW_TIMEOUT_BTN = """        <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginTop:4 }}>{challenger?.name} nem döntött — iszik!</div>"""

assert OLD_TIMEOUT_BTN in content, "timeout btn not found"
content = content.replace(OLD_TIMEOUT_BTN, NEW_TIMEOUT_BTN, 1)

OLD_RESULT_BTN = """      {revealed && !timedOut && (
        <div style={{ textAlign:'center', marginTop:4 }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color: won ? T.mint : T.coral }}>
            {won ? '✓ A többséggel értettél egyet!' : '✗ Kisebbségben voltál!'}
          </div>
          <button onClick={() => handleResult(won)} style={{ marginTop:10, width:'100%', padding:'14px 0', background: won ? T.mint : T.coral, border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:16, cursor:'pointer' }}>
            {won ? '+1 pont!' : 'Iszik 1-et!'}
          </button>
        </div>"""
NEW_RESULT_BTN = """      {revealed && !timedOut && (
        <div style={{ textAlign:'center', marginTop:4 }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color: won ? T.mint : T.coral }}>
            {won ? '✓ A többséggel értettél egyet!' : '✗ Kisebbségben voltál!'}
          </div>
        </div>"""

assert OLD_RESULT_BTN in content, "result btn not found"
content = content.replace(OLD_RESULT_BTN, NEW_RESULT_BTN, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.165 ready")
