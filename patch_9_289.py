#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old = """      {/* Következő kör / Befejezés gomb */}
      {canFinish ? (
        <button onClick={finish} style={{ width:'100%', padding:'15px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow, animation:'popIn .2s' }}>
          🏁 Befejezés
        </button>
      ) : (
        <button onClick={nextRound} style={{ width:'100%', padding:'15px', background:T.bgSoft, color:T.ink, fontFamily:T.font, fontWeight:700, fontSize:15, borderRadius:16, border:'none', cursor:'pointer' }}>
          Következő kör ({round}/{TOTAL_ROUNDS}) →
        </button>
      )}"""
new = """      {/* Következő kör / Befejezés gomb */}
      {!done && (canFinish ? (
        <button onClick={finish} style={{ width:'100%', padding:'15px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow, animation:'popIn .2s' }}>
          🏁 Befejezés
        </button>
      ) : (
        <button onClick={nextRound} style={{ width:'100%', padding:'15px', background:T.bgSoft, color:T.ink, fontFamily:T.font, fontWeight:700, fontSize:15, borderRadius:16, border:'none', cursor:'pointer' }}>
          Következő kör ({round}/{TOTAL_ROUNDS}) →
        </button>
      ))}"""
assert old in html, "FAIL: befejezés gomb"
html = html.replace(old, new, 1)

html = html.replace("const APP_VERSION = 'v9.288';", "const APP_VERSION = 'v9.289';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.289 — KezCsere befejezés gomb eltűnik nyomás után")
