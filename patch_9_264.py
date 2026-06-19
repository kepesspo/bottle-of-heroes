#!/usr/bin/env python3
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

original = html
changes = []

# ────────────────────────────────────────────
# 1. DARK THEME CONTRAST FIXES
# ────────────────────────────────────────────
# inkSoft: #8A96B8 → #B0BADC (better contrast on dark bg #2C3554)
# inkMute: #4A5278 → #6E789A
old = "    bg: '#2C3554',\n    bgSoft: '#36405F',\n    bgDeep: '#1E2640',\n    surface: '#3D4870',\n    surfaceMuted: '#333D60',\n    ink: '#E8EDF8',\n    inkSoft: '#8A96B8',\n    inkMute: '#4A5278',"
new = "    bg: '#2C3554',\n    bgSoft: '#36405F',\n    bgDeep: '#1E2640',\n    surface: '#3D4870',\n    surfaceMuted: '#333D60',\n    ink: '#EDF1FB',\n    inkSoft: '#B0BADC',\n    inkMute: '#6E789A',"
assert old in html, "FAIL: dark theme contrast"
html = html.replace(old, new, 1)
changes.append("dark theme contrast improved")

# ────────────────────────────────────────────
# 2. PLAYSCREEN GRADIENT BACKGROUND — add playBg to each theme
# ────────────────────────────────────────────
# warm
old = "    shadow: '0 2px 0 rgba(20,30,50,0.04), 0 6px 20px rgba(20,30,50,0.06)',\n    shadowLift: '0 4px 0 rgba(20,30,50,0.06), 0 12px 32px rgba(20,30,50,0.10)',\n  },"
new = "    shadow: '0 2px 0 rgba(20,30,50,0.04), 0 6px 20px rgba(20,30,50,0.06)',\n    shadowLift: '0 4px 0 rgba(20,30,50,0.06), 0 12px 32px rgba(20,30,50,0.10)',\n    playBg: 'linear-gradient(160deg, #F4C57E 0%, #EDAF58 100%)',\n  },"
assert old in html, "FAIL: warm playBg"
html = html.replace(old, new, 1)
changes.append("warm playBg")

# dark
old = "    shadow: '0 2px 0 rgba(0,0,0,0.2), 0 6px 20px rgba(0,0,0,0.3)',\n    shadowLift: '0 4px 0 rgba(0,0,0,0.25), 0 12px 32px rgba(0,0,0,0.4)',\n  },"
new = "    shadow: '0 2px 0 rgba(0,0,0,0.2), 0 6px 20px rgba(0,0,0,0.3)',\n    shadowLift: '0 4px 0 rgba(0,0,0,0.25), 0 12px 32px rgba(0,0,0,0.4)',\n    playBg: 'linear-gradient(160deg, #2C3554 0%, #1A2040 100%)',\n  },"
assert old in html, "FAIL: dark playBg"
html = html.replace(old, new, 1)
changes.append("dark playBg")

# candy
old = "    shadow: '0 2px 0 rgba(180,0,100,0.06), 0 6px 20px rgba(180,0,100,0.10)',\n    shadowLift: '0 4px 0 rgba(180,0,100,0.08), 0 12px 32px rgba(180,0,100,0.15)',\n  },"
new = "    shadow: '0 2px 0 rgba(180,0,100,0.06), 0 6px 20px rgba(180,0,100,0.10)',\n    shadowLift: '0 4px 0 rgba(180,0,100,0.08), 0 12px 32px rgba(180,0,100,0.15)',\n    playBg: 'linear-gradient(160deg, #FFE8F4 0%, #FFD0EC 100%)',\n  },"
assert old in html, "FAIL: candy playBg"
html = html.replace(old, new, 1)
changes.append("candy playBg")

# lavender
old = "    shadow: '0 2px 0 rgba(60,0,180,0.05), 0 6px 20px rgba(60,0,180,0.09)',\n    shadowLift: '0 4px 0 rgba(60,0,180,0.07), 0 12px 32px rgba(60,0,180,0.13)',\n  },"
new = "    shadow: '0 2px 0 rgba(60,0,180,0.05), 0 6px 20px rgba(60,0,180,0.09)',\n    shadowLift: '0 4px 0 rgba(60,0,180,0.07), 0 12px 32px rgba(60,0,180,0.13)',\n    playBg: 'linear-gradient(160deg, #EEE8FF 0%, #DDD0FF 100%)',\n  },"
assert old in html, "FAIL: lavender playBg"
html = html.replace(old, new, 1)
changes.append("lavender playBg")

# ocean
old = "    shadow: '0 2px 0 rgba(0,60,100,0.06), 0 6px 20px rgba(0,60,100,0.10)',\n    shadowLift: '0 4px 0 rgba(0,60,100,0.08), 0 12px 32px rgba(0,60,100,0.14)',\n  },"
new = "    shadow: '0 2px 0 rgba(0,60,100,0.06), 0 6px 20px rgba(0,60,100,0.10)',\n    shadowLift: '0 4px 0 rgba(0,60,100,0.08), 0 12px 32px rgba(0,60,100,0.14)',\n    playBg: 'linear-gradient(160deg, #E0F4F8 0%, #C0E8F4 100%)',\n  },"
assert old in html, "FAIL: ocean playBg"
html = html.replace(old, new, 1)
changes.append("ocean playBg")

# peach
old = "    shadow: '0 2px 0 rgba(160,60,0,0.06), 0 6px 20px rgba(160,60,0,0.10)',\n    shadowLift: '0 4px 0 rgba(160,60,0,0.08), 0 12px 32px rgba(160,60,0,0.14)',\n  },"
new = "    shadow: '0 2px 0 rgba(160,60,0,0.06), 0 6px 20px rgba(160,60,0,0.10)',\n    shadowLift: '0 4px 0 rgba(160,60,0,0.08), 0 12px 32px rgba(160,60,0,0.14)',\n    playBg: 'linear-gradient(160deg, #FFE8D8 0%, #FFD0BC 100%)',\n  },"
assert old in html, "FAIL: peach playBg"
html = html.replace(old, new, 1)
changes.append("peach playBg")

# lemon
old = "    shadow: '0 2px 0 rgba(80,80,0,0.06), 0 6px 20px rgba(80,80,0,0.10)',\n    shadowLift: '0 4px 0 rgba(80,80,0,0.08), 0 12px 32px rgba(80,80,0,0.14)',\n  },"
new = "    shadow: '0 2px 0 rgba(80,80,0,0.06), 0 6px 20px rgba(80,80,0,0.10)',\n    shadowLift: '0 4px 0 rgba(80,80,0,0.08), 0 12px 32px rgba(80,80,0,0.14)',\n    playBg: 'linear-gradient(160deg, #F8F8D8 0%, #ECECA8 100%)',\n  },"
assert old in html, "FAIL: lemon playBg"
html = html.replace(old, new, 1)
changes.append("lemon playBg")

# coraltheme
old = "    shadow: '0 2px 0 rgba(180,40,0,0.06), 0 6px 20px rgba(180,40,0,0.10)',\n    shadowLift: '0 4px 0 rgba(180,40,0,0.08), 0 12px 32px rgba(180,40,0,0.14)',\n  },"
new = "    shadow: '0 2px 0 rgba(180,40,0,0.06), 0 6px 20px rgba(180,40,0,0.10)',\n    shadowLift: '0 4px 0 rgba(180,40,0,0.08), 0 12px 32px rgba(180,40,0,0.14)',\n    playBg: 'linear-gradient(160deg, #FFE8E0 0%, #FFCCC0 100%)',\n  },"
assert old in html, "FAIL: coraltheme playBg"
html = html.replace(old, new, 1)
changes.append("coraltheme playBg")

# berry
old = "    shadow: '0 2px 0 rgba(100,0,160,0.06), 0 6px 20px rgba(100,0,160,0.10)',\n    shadowLift: '0 4px 0 rgba(100,0,160,0.08), 0 12px 32px rgba(100,0,160,0.14)',\n  },"
new = "    shadow: '0 2px 0 rgba(100,0,160,0.06), 0 6px 20px rgba(100,0,160,0.10)',\n    shadowLift: '0 4px 0 rgba(100,0,160,0.08), 0 12px 32px rgba(100,0,160,0.14)',\n    playBg: 'linear-gradient(160deg, #F0E8F8 0%, #DDD0F0 100%)',\n  },"
assert old in html, "FAIL: berry playBg"
html = html.replace(old, new, 1)
changes.append("berry playBg")

# ice
old = "    shadow: '0 2px 0 rgba(0,40,100,0.06), 0 6px 20px rgba(0,40,100,0.10)',\n    shadowLift: '0 4px 0 rgba(0,40,100,0.08), 0 12px 32px rgba(0,40,100,0.14)',\n  },"
new = "    shadow: '0 2px 0 rgba(0,40,100,0.06), 0 6px 20px rgba(0,40,100,0.10)',\n    shadowLift: '0 4px 0 rgba(0,40,100,0.08), 0 12px 32px rgba(0,40,100,0.14)',\n    playBg: 'linear-gradient(160deg, #E8F4FF 0%, #D0E8FF 100%)',\n  },"
assert old in html, "FAIL: ice playBg"
html = html.replace(old, new, 1)
changes.append("ice playBg")

# Apply playBg to PlayScreen outer container
old = "    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg }}>\n\n      {/* ── Top bar ── */}"
new = "    <div style={{ flex:1, display:'flex', flexDirection:'column', background: T.playBg || T.bg }}>\n\n      {/* ── Top bar ── */}"
assert old in html, "FAIL: PlayScreen outer bg"
html = html.replace(old, new, 1)
changes.append("PlayScreen gradient background applied")

# ────────────────────────────────────────────
# 3. UNDO STATE + FOOTER UNDO BUTTON
# ────────────────────────────────────────────
# Add canUndo state after pendingCommit state
old = "  const [pendingCommit, setPendingCommit] = useState(null);\n  const [hostBurst, setHostBurst] = useState(null);"
new = "  const [pendingCommit, setPendingCommit] = useState(null);\n  const [canUndo, setCanUndo] = useState(false);\n  const [hostBurst, setHostBurst] = useState(null);"
assert old in html, "FAIL: canUndo state"
html = html.replace(old, new, 1)
changes.append("canUndo state added")

# Set canUndo when saving undo state
old = "    undoRef.current = { players, turn, gameIdx, round };\n    transRef.current = true;"
new = "    undoRef.current = { players, turn, gameIdx, round };\n    setCanUndo(true);\n    transRef.current = true;"
assert old in html, "FAIL: setCanUndo(true)"
html = html.replace(old, new, 1)
changes.append("setCanUndo(true) in commitRound")

# Clear canUndo when undoLast clears undoRef
old = "    undoRef.current = null;\n    setPlayers(p); setTurn(t); setGameIdx(g); setRound(r);"
new = "    undoRef.current = null;\n    setCanUndo(false);\n    setPlayers(p); setTurn(t); setGameIdx(g); setRound(r);"
assert old in html, "FAIL: setCanUndo(false)"
html = html.replace(old, new, 1)
changes.append("setCanUndo(false) in undoLast")

# Footer: swap MENÜ button with undo-aware version
old = """        {/* Menu btn — flex:1 */}
        <button onClick={() => setShowMenu(true)} style={{ flex:1, borderRadius:999, border:'none', background:'transparent', cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:3, padding:'8px 0', minWidth:0 }}>
          <div style={{ width:32, height:32, display:'grid', placeItems:'center' }}>{Icon.menu(T.inkSoft)}</div>
          <span style={{ color:T.inkMute, fontSize:9, fontFamily:T.font, fontWeight:700, letterSpacing:'0.06em', lineHeight:1 }}>{t('menu')}</span>
        </button>"""
new = """        {/* Menu / Undo btn — flex:1 */}
        <button onClick={() => canUndo ? undoLast() : setShowMenu(true)} style={{ flex:1, borderRadius:999, border:'none', background: canUndo ? `${T.coral}18` : 'transparent', cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:3, padding:'8px 0', minWidth:0, transition:'background .2s' }}>
          <div style={{ width:32, height:32, display:'grid', placeItems:'center' }}>{canUndo ? <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={T.coral} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 7v6h6"/><path d="M3 13C5 7 12 4 18 8s7 13 2 17"/></svg> : Icon.menu(T.inkSoft)}</div>
          <span style={{ color: canUndo ? T.coral : T.inkMute, fontSize:9, fontFamily:T.font, fontWeight:700, letterSpacing:'0.06em', lineHeight:1 }}>{canUndo ? 'VISSZA' : t('menu')}</span>
        </button>"""
assert old in html, "FAIL: footer undo button"
html = html.replace(old, new, 1)
changes.append("footer undo/menu button")

# ────────────────────────────────────────────
# 4. OFFLINE SESSION SAVE + RESUME OFFER
# ────────────────────────────────────────────
# Save session to localStorage in commitRound (after setPlayers)
old = "    setPlayers(newPlayers);\n    if (fb==='win') { setScorePulse(true);"
new = """    setPlayers(newPlayers);
    try { localStorage.setItem('boh_session', JSON.stringify({ players: newPlayers, turn: newTurn, gameIdx: newGameIdx, round: newRound, selectedGames, gameMeta })); } catch(e) {}
    if (fb==='win') { setScorePulse(true);"""
assert old in html, "FAIL: session save in commitRound"
html = html.replace(old, new, 1)
changes.append("session save in commitRound")

# Add resumeOffer state and check on mount
old = "  const [pendingCommit, setPendingCommit] = useState(null);\n  const [canUndo, setCanUndo] = useState(false);"
new = """  const [pendingCommit, setPendingCommit] = useState(null);
  const [canUndo, setCanUndo] = useState(false);
  const [resumeOffer, setResumeOffer] = useState(() => {
    try {
      const s = localStorage.getItem('boh_session');
      if (!s) return null;
      const d = JSON.parse(s);
      if (!d.players?.length || !d.selectedGames?.length) return null;
      return d;
    } catch(e) { return null; }
  });"""
assert old in html, "FAIL: resumeOffer state"
html = html.replace(old, new, 1)
changes.append("resumeOffer state added")

# Clear session on Kilépés (go end)
old = "<button onClick={() => { setShowMenu(false); saveCurrentGameStats(); if (setLastGameRound) setLastGameRound(round); go('end'); }} style={{ width:'100%', minHeight:52, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:15, borderRadius:14, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>\n                  <span>🏁</span><span>Kilépés</span>"
new = "<button onClick={() => { setShowMenu(false); saveCurrentGameStats(); if (setLastGameRound) setLastGameRound(round); try { localStorage.removeItem('boh_session'); } catch(e) {} go('end'); }} style={{ width:'100%', minHeight:52, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:15, borderRadius:14, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>\n                  <span>🏁</span><span>Kilépés</span>"
assert old in html, "FAIL: clear session on kilépés"
html = html.replace(old, new, 1)
changes.append("clear session on kilépés")

# Add resume offer UI just before the top bar in PlayScreen return
old = "      {/* ── Top bar ── */}\n      <div style={{ flexShrink:0, display:'flex', alignItems:'center', gap:8, padding:`10px 16px 6px`"
new = """      {/* ── Resume offer ── */}
      {resumeOffer && (
        <div style={{ position:'fixed', inset:0, zIndex:150, background:'rgba(14,14,24,0.6)', display:'flex', alignItems:'flex-end', justifyContent:'center', padding:'0 16px 32px' }}>
          <div style={{ background:T.surface, borderRadius:20, padding:'20px 20px 16px', width:'100%', maxWidth:400, boxShadow:'0 24px 64px rgba(0,0,0,0.3)', animation:'popIn .3s cubic-bezier(.2,.9,.3,1.3)' }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, marginBottom:6 }}>Folytatod az előző menetet?</div>
            <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginBottom:16 }}>{resumeOffer.players?.length} játékos · {resumeOffer.round}. kör · {resumeOffer.selectedGames?.length} játék</div>
            <div style={{ display:'flex', gap:10 }}>
              <button onClick={() => { const d = resumeOffer; setResumeOffer(null); setPlayers(d.players); setTurn(d.turn); setGameIdx(d.gameIdx); setRound(d.round); }} style={{ flex:2, padding:'13px 0', borderRadius:16, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:15, cursor:'pointer' }}>Folytatás</button>
              <button onClick={() => { setResumeOffer(null); try { localStorage.removeItem('boh_session'); } catch(e) {} }} style={{ flex:1, padding:'13px 0', borderRadius:16, border:`1.5px solid ${T.inkMute}30`, background:T.surface, color:T.inkSoft, fontFamily:T.font, fontWeight:700, fontSize:14, cursor:'pointer' }}>Új</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Top bar ── */}
      <div style={{ flexShrink:0, display:'flex', alignItems:'center', gap:8, padding:`10px 16px 6px`"""
assert old in html, "FAIL: resume offer UI"
html = html.replace(old, new, 1)
changes.append("resume offer UI")

# ────────────────────────────────────────────
# VERSION BUMP
# ────────────────────────────────────────────
old = "const APP_VERSION = 'v9.263';"
new = "const APP_VERSION = 'v9.264';"
assert old in html, "FAIL: version bump"
html = html.replace(old, new, 1)
changes.append("version bump v9.264")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Done! {len(changes)} changes applied:")
for c in changes:
    print(f"  ✓ {c}")
