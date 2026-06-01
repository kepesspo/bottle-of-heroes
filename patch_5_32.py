# -*- coding: utf-8 -*-
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Imposztor: remove avatar + "te jössz" from inside dark card ────────────
old1 = (
    "          {/* Player avatar */}\n"
    "          <div style={{ width:54, height:54, borderRadius:'50%', background:pl.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:'#fff', boxShadow:`0 0 0 3px rgba(255,255,255,0.15)` }}>\n"
    "            {pl.name.charAt(0).toUpperCase()}\n"
    "          </div>\n"
    "          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:18, color:'#fff' }}>{pl.name}, te jössz</div>\n"
    "\n"
    "          {/* Eye / reveal area */}"
)
new1 = "          {/* Eye / reveal area */}"
assert old1 in html, "Fix 1 not found"
html = html.replace(old1, new1, 1)

# ── 2. Tapper Btn: show full name inside button, remove external name label ───
# Change first-letter display to full name (smaller font to fit)
old2a = (
    "          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:32, color:'#fff', lineHeight:1 }}>\n"
    "            {player.name.charAt(0).toUpperCase()}\n"
    "          </div>"
)
new2a = (
    "          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:'#fff', lineHeight:1.1, textAlign:'center', padding:'0 8px', wordBreak:'break-word', maxWidth:110 }}>\n"
    "            {player.name}\n"
    "          </div>"
)
assert old2a in html, "Fix 2a not found"
html = html.replace(old2a, new2a, 1)

# Remove the name label below the button
old2b = "        <div style={{ fontFamily:T.font, fontWeight:600, fontSize:13, color:T.ink }}>{player.name}</div>\n      </div>\n    );\n  };"
new2b = "      </div>\n    );\n  };"
assert old2b in html, "Fix 2b not found"
html = html.replace(old2b, new2b, 1)

# ── 3. Tapper: remove "Következő játék →" button, add auto-advance ───────────
# Remove the button
old3_btn = (
    "\n"
    "      {phase === 'done' && result !== null && (\n"
    "        <button onClick={() => {\n"
    "          const dm = {};\n"
    "          if (result === 1) dm[p2.id] = 1;\n"
    "          else if (result === 2) dm[p1.id] = 1;\n"
    "          else if (result === 'both-lose') { dm[p1.id] = 1; dm[p2.id] = 1; }\n"
    "          if(onAdvance) onAdvance(dm);\n"
    "        }} style={{ width:'100%', padding:'14px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow }}>\n"
    "          Következő játék →\n"
    "        </button>\n"
    "      )}"
)
new3_btn = ""
assert old3_btn in html, "Fix 3 button not found"
html = html.replace(old3_btn, new3_btn, 1)

# Add auto-advance useEffect (insert after the gameIdx reset useEffect)
old3_effect = (
    "  React.useEffect(() => {\n"
    "    setPhase('idle'); setP1Hold(false); setP2Hold(false);\n"
    "    setCountdown(5.0); setP1Time(null); setP2Time(null);\n"
    "    phaseRef.current = 'idle';\n"
    "    p1HoldRef.current = false; p2HoldRef.current = false;\n"
    "    p1TimeRef.current = null; p2TimeRef.current = null;\n"
    "    clearInterval(ivRef.current);\n"
    "    return () => clearInterval(ivRef.current);\n"
    "  }, [gameIdx]);"
)
new3_effect = (
    "  React.useEffect(() => {\n"
    "    setPhase('idle'); setP1Hold(false); setP2Hold(false);\n"
    "    setCountdown(5.0); setP1Time(null); setP2Time(null);\n"
    "    phaseRef.current = 'idle';\n"
    "    p1HoldRef.current = false; p2HoldRef.current = false;\n"
    "    p1TimeRef.current = null; p2TimeRef.current = null;\n"
    "    clearInterval(ivRef.current);\n"
    "    return () => clearInterval(ivRef.current);\n"
    "  }, [gameIdx]);\n"
    "\n"
    "  React.useEffect(() => {\n"
    "    if (p1Time === null || p2Time === null) return;\n"
    "    const p1Past = p1Time === -1, p2Past = p2Time === -1;\n"
    "    let r;\n"
    "    if (p1Past && p2Past) r = 'both-lose';\n"
    "    else if (p1Past) r = 2;\n"
    "    else if (p2Past) r = 1;\n"
    "    else if (p1Time < p2Time) r = 1;\n"
    "    else if (p2Time < p1Time) r = 2;\n"
    "    else r = 'draw';\n"
    "    const dm = {};\n"
    "    if (r === 1 && p2) dm[p2.id] = 1;\n"
    "    else if (r === 2 && p1) dm[p1.id] = 1;\n"
    "    else if (r === 'both-lose') { if(p1) dm[p1.id]=1; if(p2) dm[p2.id]=1; }\n"
    "    const t = setTimeout(() => { if(onAdvance) onAdvance(dm); }, 3000);\n"
    "    return () => clearTimeout(t);\n"
    "  }, [p1Time, p2Time]);"
)
assert old3_effect in html, "Fix 3 effect not found"
html = html.replace(old3_effect, new3_effect, 1)

# ── 4. Érem: auto-advance in doFlip + replace result buttons with display ─────
# Change doFlip to schedule auto-advance after result
old4_flip = (
    "  const doFlip = (choice) => {\n"
    "    setPick(choice);\n"
    "    setPhase('flipping');\n"
    "    setTimeout(() => {\n"
    "      setResult(Math.random() < 0.5 ? 'fej' : 'iras');\n"
    "      setPhase('result');\n"
    "    }, 1600);\n"
    "  };"
)
new4_flip = (
    "  const doFlip = (choice) => {\n"
    "    setPick(choice);\n"
    "    setPhase('flipping');\n"
    "    setTimeout(() => {\n"
    "      const r = Math.random() < 0.5 ? 'fej' : 'iras';\n"
    "      setResult(r);\n"
    "      setPhase('result');\n"
    "      const isCorrect = choice === r;\n"
    "      setTimeout(() => advance(isCorrect), 2500);\n"
    "    }, 1600);\n"
    "  };"
)
assert old4_flip in html, "Fix 4 doFlip not found"
html = html.replace(old4_flip, new4_flip, 1)

# Replace result buttons with outcome display card
old4_result = (
    "      {/* Result actions */}\n"
    "      {phase === 'result' && (\n"
    "        <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:8, animation:'popIn .3s' }}>\n"
    "          <button onClick={() => advance(correct)} style={{ width:'100%', padding:'15px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow }}>\n"
    "            {correct ? '🎉 Eltalálta — megúszta!' : `Nem találta el — ${challenger?.name||'ő'} iszik!`}\n"
    "          </button>\n"
    "          <button onClick={() => advance(!correct)} style={{ width:'100%', padding:'13px', background:'rgba(255,255,255,0.6)', color:T.inkSoft, fontFamily:T.font, fontWeight:600, fontSize:15, borderRadius:16, border:`2px solid rgba(0,0,0,0.1)`, cursor:'pointer' }}>\n"
    "            Következő játékos →\n"
    "          </button>\n"
    "        </div>\n"
    "      )}"
)
new4_result = (
    "      {/* Result display */}\n"
    "      {phase === 'result' && (\n"
    "        <div style={{ width:'100%', padding:'18px 16px', borderRadius:16, animation:'popIn .3s', textAlign:'center',\n"
    "          background: correct ? `${T.mint}18` : `${T.coral}18`,\n"
    "          border: `2px solid ${correct ? T.mint : T.coral}` }}>\n"
    "          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:17, color: correct ? T.mint : T.coral }}>\n"
    "            {correct ? `\U0001f389 Nyertél! ${opponent?.name||'Ellenfél'} iszik.` : `\U0001f605 Nem jött be — te iszol!`}\n"
    "          </div>\n"
    "        </div>\n"
    "      )}"
)
assert old4_result in html, "Fix 4 result not found"
html = html.replace(old4_result, new4_result, 1)

# ── 5. Collect & Boom: change ✓ back to ⭐ for safe cells ─────────────────────
old5 = ": <span style={{fontSize:18}}>✓</span>"
new5 = ": <span style={{fontSize:20}}>⭐</span>"
assert old5 in html, "Fix 5 not found"
html = html.replace(old5, new5, 1)

# ── 6. Version bump ─────────────────────────────────────────────────────────
assert 'Verzió 5.31 · DNR · 2026.06.01 07:00' in html, "Version not found"
html = html.replace(
    'Verzió 5.31 · DNR · 2026.06.01 07:00',
    'Verzió 5.32 · DNR · 2026.06.01 08:00',
    1
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done — v5.32")
