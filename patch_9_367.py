#!/usr/bin/env python3
"""v9.367 — English: fix game control panel + play footer + misc strings"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Add missing TR keys
old_hu_end = """    rematchLabel: 'Visszavágó',
  },"""
new_hu_end = """    rematchLabel: 'Visszavágó',
    leader: 'Vezető',
    score: 'Állás',
    order: 'Sorrend',
    controls: 'Vezérlés',
    joinEnabled: 'Csatlakozás engedélyezve',
    nextBtn: 'Következő',
    backBtn: 'Vissza',
    guesses: 'tippel',
    nextRound: 'Következő kör',
    nextLap: 'Következő lap',
    startGame2: 'Rajt!',
  },"""
assert old_hu_end in html, "FAIL: hu end"
html = html.replace(old_hu_end, new_hu_end, 1)

old_en_end = """    rematchLabel: 'Rematch',
  },"""
new_en_end = """    rematchLabel: 'Rematch',
    leader: 'Leader',
    score: 'Score',
    order: 'Order',
    controls: 'Controls',
    joinEnabled: 'Join enabled',
    nextBtn: 'Next',
    backBtn: 'Back',
    guesses: 'guesses',
    nextRound: 'Next Round',
    nextLap: 'Next Card',
    startGame2: 'Start!',
  },"""
assert old_en_end in html, "FAIL: en end"
html = html.replace(old_en_end, new_en_end, 1)

# ── 2. Tab labels — use t() mapped from the internal key
old_tabs = """                {['állás','sorrend','vezérlés'].map(tab => (
                  <button key={tab} onClick={() => setMenuTab(tab)} style={{
                    flex:1, padding:'11px 0', border:'none', borderRadius:10, cursor:'pointer',
                    fontFamily:T.font, fontWeight:800, fontSize:14,
                    background: menuTab===tab ? T.mint : 'transparent',
                    color: menuTab===tab ? '#fff' : T.inkSoft,
                    boxShadow: menuTab===tab ? '0 2px 7px -1px rgba(79,194,160,0.5)' : 'none',
                    transition:'all .15s',
                    textTransform:'capitalize',
                  }}>{tab.charAt(0).toUpperCase()+tab.slice(1)}</button>
                ))}"""
new_tabs = """                {[['állás',t('score')],['sorrend',t('order')],['vezérlés',t('controls')]].map(([tab,label]) => (
                  <button key={tab} onClick={() => setMenuTab(tab)} style={{
                    flex:1, padding:'11px 0', border:'none', borderRadius:10, cursor:'pointer',
                    fontFamily:T.font, fontWeight:800, fontSize:14,
                    background: menuTab===tab ? T.mint : 'transparent',
                    color: menuTab===tab ? '#fff' : T.inkSoft,
                    boxShadow: menuTab===tab ? '0 2px 7px -1px rgba(79,194,160,0.5)' : 'none',
                    transition:'all .15s',
                  }}>{label}</button>
                ))}"""
assert old_tabs in html, "FAIL: tabs"
html = html.replace(old_tabs, new_tabs, 1)

# ── 3. Leader label
old = """                      <div style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:'rgba(14,14,24,0.45)', textTransform:'uppercase', letterSpacing:'0.1em' }}>Vezető</div>"""
new = """                      <div style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:'rgba(14,14,24,0.45)', textTransform:'uppercase', letterSpacing:'0.1em' }}>{t('leader')}</div>"""
assert old in html, "FAIL: vezető"
html = html.replace(old, new, 1)

# ── 4. PONT in leader card
old = """                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:'#1a2236' }}>{mLeader.points} <span style={{ fontSize:11, fontWeight:700 }}>PONT</span></div>"""
new = """                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:'#1a2236' }}>{mLeader.points} <span style={{ fontSize:11, fontWeight:700 }}>{t('pointStat').toUpperCase()}</span></div>"""
assert old in html, "FAIL: pont in leader card"
html = html.replace(old, new, 1)

# ── 5. Szobakód label in control panel
old = """                    <span style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.1em' }}>Szobakód</span>"""
new = """                    <span style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.1em' }}>{t('roomCode')}</span>"""
assert old in html, "FAIL: szobakód"
html = html.replace(old, new, 1)

# ── 6. Csatlakozás engedélyezve
old = """                    <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:15, color:T.ink }}>Csatlakozás engedélyezve</span>"""
new = """                    <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:15, color:T.ink }}>{t('joinEnabled')}</span>"""
assert old in html, "FAIL: csatlakozás engedélyezve"
html = html.replace(old, new, 1)

# ── 7. Play footer Vissza
old = """                    <span style={{ fontSize:17 }}>↩</span><span>Vissza</span>"""
new = """                    <span style={{ fontSize:17 }}>↩</span><span>{t('backBtn')}</span>"""
assert old in html, "FAIL: vissza footer"
html = html.replace(old, new, 1)

# ── 8. Play footer Következő
old = """                    <span style={{ fontSize:17 }}>⏭</span><span>Következő</span>"""
new = """                    <span style={{ fontSize:17 }}>⏭</span><span>{t('nextBtn')}</span>"""
assert old in html, "FAIL: következő footer"
html = html.replace(old, new, 1)

# ── 9. Other Vissza buttons in game flows (bracket/tournament)
html = html.replace(
    """                  <span>←</span><span>Vissza</span>""",
    """                  <span>←</span><span>{t('backBtn')}</span>"""
)

# ── 10. Other standalone Vissza button
old = """            <button onClick={() => setStep(s => s-1)} style={{ flex:1, padding:'13px 0', borderRadius:16, border:`1.5px solid ${T.inkMute}30`, background:T.surface, color:T.inkSoft, fontFamily:T.font, fontWeight:700, fontSize:14, cursor:'pointer' }}>Vissza</button>"""
new = """            <button onClick={() => setStep(s => s-1)} style={{ flex:1, padding:'13px 0', borderRadius:16, border:`1.5px solid ${T.inkMute}30`, background:T.surface, color:T.inkSoft, fontFamily:T.font, fontWeight:700, fontSize:14, cursor:'pointer' }}>{t('backBtn')}</button>"""
assert old in html, "FAIL: vissza step"
html = html.replace(old, new, 1)

# ── 11. "tippel" in game (kisebb/nagyobb)
old = """              {currentPlayer?.name||'?'} tippel"""
new = """              {currentPlayer?.name||'?'} {t('guesses')}"""
assert old in html, "FAIL: tippel"
html = html.replace(old, new, 1)

# ── 12. PONT in stats leaderboard column (line 35078)
old = """                        <div style={{ fontFamily:T.font, fontSize:11, color:T.inkMute, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.08em' }}>PONT</div>"""
new = """                        <div style={{ fontFamily:T.font, fontSize:11, color:T.inkMute, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.08em' }}>{t('pointStat').toUpperCase()}</div>"""
assert old in html, "FAIL: pont stats"
html = html.replace(old, new, 1)

html = html.replace("const APP_VERSION = 'v9.366b';", "const APP_VERSION = 'v9.367';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.367 — game control panel + play footer translations fixed")
