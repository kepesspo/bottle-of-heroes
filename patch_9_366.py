#!/usr/bin/env python3
"""v9.366 — English translation: replace hardcoded Hungarian strings with t() calls"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Add missing keys to TR['hu'] and TR['en']

old_hu_end = """    chooseGames: 'Válassz játékokat a kezdéshez!',
    addPlayersOnboard: 'Játékosok hozzáadása',
    chooseGamesOnboard: 'Játékok kiválasztása',
  },"""
new_hu_end = """    chooseGames: 'Válassz játékokat a kezdéshez!',
    addPlayersOnboard: 'Játékosok hozzáadása',
    chooseGamesOnboard: 'Játékok kiválasztása',
    splashSub: 'Betöltési animáció indításkor',
    noPlayersTitle: 'Nincs még játékos!',
    noPlayersSub: 'Koppints ide és add hozzá az első játékost',
    continueToGames: 'Tovább a játékokhoz',
    go: 'Mehet',
    inOrder: 'Sorban',
    maxRoundsLabel: 'Max körök',
    other: 'Egyéb',
    roundCounter: '🔢 Körszámláló',
    hydroBreak: '💧 Hidratációs szünet',
    joinToggle: '📱 Csatlakozás',
    leave: 'Kilépés',
    again: 'Újra',
    newGame: 'Új meccs',
    mainMenu: 'Főmenü',
    pointWinner: 'Pont győztes',
    mostDrinks: 'Legtöbb korty',
    pointStat: 'pont',
    drinkStat: 'korty',
    alcoholUnits: 'Becsült alkohol egységek',
    observer: 'Megfigyelő',
    history: 'Előzmény',
    recentRooms: 'Korábbi szobák',
    noRecentRooms: 'Még nincs korábbi szoba',
    enterHostCode: 'Add meg a házigazda szobakódját.',
    controlFromDevice: 'Irányítsd a játékot egy másik készülékről.',
    enterHostPin: 'Add meg a 4 jegyű Host PIN kódot.',
    rematchLabel: 'Visszavágó',
  },"""
assert old_hu_end in html, "FAIL: hu end"
html = html.replace(old_hu_end, new_hu_end, 1)

old_en_end = """    chooseGames: 'Choose games to get started!',
    addPlayersOnboard: 'Add Players',
    chooseGamesOnboard: 'Choose Games',
  },"""
new_en_end = """    chooseGames: 'Choose games to get started!',
    addPlayersOnboard: 'Add Players',
    chooseGamesOnboard: 'Choose Games',
    splashSub: 'Loading animation on startup',
    noPlayersTitle: 'No players yet!',
    noPlayersSub: 'Tap here to add the first player',
    continueToGames: 'Continue to Games',
    go: 'Go',
    inOrder: 'In Order',
    maxRoundsLabel: 'Max Rounds',
    other: 'Other',
    roundCounter: '🔢 Round Counter',
    hydroBreak: '💧 Hydration Break',
    joinToggle: '📱 Join',
    leave: 'Leave',
    again: 'Again',
    newGame: 'New Game',
    mainMenu: 'Main Menu',
    pointWinner: 'Point Winner',
    mostDrinks: 'Most Drinks',
    pointStat: 'pt',
    drinkStat: 'drinks',
    alcoholUnits: 'Estimated Alcohol Units',
    observer: 'Observer',
    history: 'History',
    recentRooms: 'Recent Rooms',
    noRecentRooms: 'No recent rooms yet',
    enterHostCode: 'Enter the host\'s room code.',
    controlFromDevice: 'Control the game from another device.',
    enterHostPin: 'Enter the 4-digit Host PIN.',
    rematchLabel: 'Rematch',
  },"""
assert old_en_end in html, "FAIL: en end"
html = html.replace(old_en_end, new_en_end, 1)

# ── 2. Settings splash subtitle
old = """                  <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>Betöltési animáció indításkor</div>"""
new = """                  <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>{t('splashSub')}</div>"""
assert old in html, "FAIL: splash sub"
html = html.replace(old, new, 1)

# ── 3. Players empty state
old = """              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, marginBottom:4 }}>Nincs még játékos!</div>
              <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft }}>Koppints ide és add hozzá az első játékost</div>"""
new = """              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, marginBottom:4 }}>{t('noPlayersTitle')}</div>
              <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft }}>{t('noPlayersSub')}</div>"""
assert old in html, "FAIL: no players"
html = html.replace(old, new, 1)

# ── 4. Min players banner (hardcoded fallback)
old = """              {secretTaps > 0 ? `${secretTaps}/5…` : 'Legalább 2 játékos kell. Adj hozzá még valakit!'}"""
new = """              {secretTaps > 0 ? `${secretTaps}/5…` : t('minPlayers')}"""
assert old in html, "FAIL: min players banner"
html = html.replace(old, new, 1)

# ── 5. Continue to games button
old = """        <PrimaryButton disabled={players.length < 2} onClick={() => go('games')}>Tovább a játékokhoz</PrimaryButton>"""
new = """        <PrimaryButton disabled={players.length < 2} onClick={() => go('games')}>{t('continueToGames')}</PrimaryButton>"""
assert old in html, "FAIL: continueToGames"
html = html.replace(old, new, 1)

# ── 6. Player edit "Mehet" button
old = """          <PrimaryButton onClick={onClose} disabled={!player.name.trim()}>Mehet</PrimaryButton>"""
new = """          <PrimaryButton onClick={onClose} disabled={!player.name.trim()}>{t('go')}</PrimaryButton>"""
assert old in html, "FAIL: mehet"
html = html.replace(old, new, 1)

# ── 7. Game order "Sorban"
old = """        {[{key:'sorban',label:'Sorban'},{key:'random',label:'Random'}].map(o => {"""
new = """        {[{key:'sorban',label:t('inOrder')},{key:'random',label:t('randomGames')}].map(o => {"""
assert old in html, "FAIL: sorban"
html = html.replace(old, new, 1)

# ── 8. Max körök label
old = """      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:12, letterSpacing:'0.13em', textTransform:'uppercase', color:T.inkMute, margin:'20px 0 8px' }}>Max körök</div>"""
new = """      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:12, letterSpacing:'0.13em', textTransform:'uppercase', color:T.inkMute, margin:'20px 0 8px' }}>{t('maxRoundsLabel')}</div>"""
assert old in html, "FAIL: max körök"
html = html.replace(old, new, 1)

# ── 9. Egyéb label
old = """      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:12, letterSpacing:'0.13em', textTransform:'uppercase', color:T.inkMute, margin:'20px 0 4px' }}>Egyéb</div>"""
new = """      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:12, letterSpacing:'0.13em', textTransform:'uppercase', color:T.inkMute, margin:'20px 0 4px' }}>{t('other')}</div>"""
assert old in html, "FAIL: egyéb"
html = html.replace(old, new, 1)

# ── 10. Nehézségi szint label
old = """      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:12, letterSpacing:'0.13em', textTransform:'uppercase', color:T.inkMute, margin:'20px 0 8px' }}>Nehézségi szint</div>"""
new = """      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:12, letterSpacing:'0.13em', textTransform:'uppercase', color:T.inkMute, margin:'20px 0 8px' }}>{t('difficulty')}</div>"""
assert old in html, "FAIL: nehézségi szint"
html = html.replace(old, new, 1)

# ── 11. Toggle labels
html = html.replace('label="🔢 Körszámláló"', 'label={t(\'roundCounter\')}', 1)
html = html.replace('label="💧 Hidratációs szünet"', 'label={t(\'hydroBreak\')}', 1)
html = html.replace('label="📱 Csatlakozás"', 'label={t(\'joinToggle\')}', 1)

# ── 12. Settings "Kész" buttons → t('done')
html = html.replace(
    """<button onClick={onDone} style={{ width:'100%', padding:'15px', borderRadius:16, background:T.mint, border:'none', color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer', boxShadow:'0 5px 16px -5px rgba(79,194,160,0.6)', marginTop:20 }}>Kész</button>""",
    """<button onClick={onDone} style={{ width:'100%', padding:'15px', borderRadius:16, background:T.mint, border:'none', color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer', boxShadow:'0 5px 16px -5px rgba(79,194,160,0.6)', marginTop:20 }}>{t('done')}</button>""",
    1
)

# ── 13. Round popup "Kör"
old = """<div style={{ fontFamily:T.font, fontWeight:900, fontSize:64, color:'#fff', lineHeight:1, textShadow:'0 4px 24px rgba(0,0,0,0.4)', letterSpacing:'-0.02em' }}>{roundPopup.round}. Kör</div>"""
new = """<div style={{ fontFamily:T.font, fontWeight:900, fontSize:64, color:'#fff', lineHeight:1, textShadow:'0 4px 24px rgba(0,0,0,0.4)', letterSpacing:'-0.02em' }}>{roundPopup.round}. {t('roundWord')}</div>"""
assert old in html, "FAIL: round popup kör"
html = html.replace(old, new, 1)

# ── 14. Play footer "Újra" and "Kilépés"
old = """                    <span style={{ fontSize:17 }}>🔄</span><span>Újra</span>"""
new = """                    <span style={{ fontSize:17 }}>🔄</span><span>{t('again')}</span>"""
assert old in html, "FAIL: újra"
html = html.replace(old, new, 1)

old = """                  <span>🏁</span><span>Kilépés</span>"""
new = """                  <span>🏁</span><span>{t('leave')}</span>"""
assert old in html, "FAIL: kilépés footer"
html = html.replace(old, new, 1)

# ── 15. Kilépés buttons (multiple locations)
html = html.replace(
    """>Kilépés</button>""",
    """>{t('leave')}</button>"""
)

# ── 16. EndScreen buttons
old = """          <button onClick={resetGame} style={{ flex:1, minHeight:56, border:`2px solid ${T.inkMute}`, background:'transparent', color:T.ink, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, borderRadius:999, cursor:'pointer' }}>Új meccs</button>"""
new = """          <button onClick={resetGame} style={{ flex:1, minHeight:56, border:`2px solid ${T.inkMute}`, background:'transparent', color:T.ink, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, borderRadius:999, cursor:'pointer' }}>{t('newGame')}</button>"""
assert old in html, "FAIL: új meccs"
html = html.replace(old, new, 1)

old = """          <button onClick={() => go('home')} style={{ flex:1, minHeight:56, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, borderRadius:999, cursor:'pointer', boxShadow:T.shadow }}>Főmenü</button>"""
new = """          <button onClick={() => go('home')} style={{ flex:1, minHeight:56, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, borderRadius:999, cursor:'pointer', boxShadow:T.shadow }}>{t('mainMenu')}</button>"""
assert old in html, "FAIL: főmenü"
html = html.replace(old, new, 1)

# ── 17. EndScreen stats card labels
old = """            ...(sorted[0] ? [{ label:'Pont győztes', icon:'🏆', tone:T.yellow, player:sorted[0], stat:sorted[0].points, statLabel:'pont' }] : []),
            ...(drunkSorted[0] ? [{ label:'Legtöbb korty', icon:'🍺', tone:T.coral, player:drunkSorted[0], stat:drunkSorted[0].drinks, statLabel:'korty' }] : []),"""
new = """            ...(sorted[0] ? [{ label:t('pointWinner'), icon:'🏆', tone:T.yellow, player:sorted[0], stat:sorted[0].points, statLabel:t('pointStat') }] : []),
            ...(drunkSorted[0] ? [{ label:t('mostDrinks'), icon:'🍺', tone:T.coral, player:drunkSorted[0], stat:drunkSorted[0].drinks, statLabel:t('drinkStat') }] : []),"""
assert old in html, "FAIL: stats cards"
html = html.replace(old, new, 1)

# ── 18. Alcohol units label
old = """                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>Becsült alkohol egységek</div>"""
new = """                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>{t('alcoholUnits')}</div>"""
assert old in html, "FAIL: alcohol units"
html = html.replace(old, new, 1)

# ── 19. Join screen strings
old = """            <span>👀</span>Megfigyelő"""
new = """            <span>👀</span>{t('observer')}"""
assert old in html, "FAIL: megfigyelő"
html = html.replace(old, new, 1)

old = """          <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11, letterSpacing:'0.08em', textTransform:'uppercase' }}>Előzmény</span>"""
new = """          <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11, letterSpacing:'0.08em', textTransform:'uppercase' }}>{t('history')}</span>"""
assert old in html, "FAIL: előzmény"
html = html.replace(old, new, 1)

old = """            <div style={{ textAlign:'center', fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, padding:'14px 0 12px', textTransform:'uppercase', letterSpacing:'-0.01em' }}>Korábbi szobák</div>"""
new = """            <div style={{ textAlign:'center', fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, padding:'14px 0 12px', textTransform:'uppercase', letterSpacing:'-0.01em' }}>{t('recentRooms')}</div>"""
assert old in html, "FAIL: korábbi szobák"
html = html.replace(old, new, 1)

old = """              <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', padding:'20px 0' }}>Még nincs korábbi szoba</div>"""
new = """              <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', padding:'20px 0' }}>{t('noRecentRooms')}</div>"""
assert old in html, "FAIL: no recent rooms"
html = html.replace(old, new, 1)

old = """          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay }}>
            {phase === 'pin' ? '🔐 Host PIN' : 'Szoba kód'}
          </div>
          <div style={{ marginTop:4, fontFamily:T.font, fontSize:12, fontWeight:600, color:T.inkSoft, lineHeight:1.4 }}>
            {phase === 'pin' ? 'Add meg a 4 jegyű Host PIN kódot.' : joinMode === 'host' ? 'Irányítsd a játékot egy másik készülékről.' : 'Add meg a házigazda szobakódját.'}
          </div>"""
new = """          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay }}>
            {phase === 'pin' ? '🔐 Host PIN' : t('roomCode')}
          </div>
          <div style={{ marginTop:4, fontFamily:T.font, fontSize:12, fontWeight:600, color:T.inkSoft, lineHeight:1.4 }}>
            {phase === 'pin' ? t('enterHostPin') : joinMode === 'host' ? t('controlFromDevice') : t('enterHostCode')}
          </div>"""
assert old in html, "FAIL: szoba kód"
html = html.replace(old, new, 1)

# ── 20. Visszavágó label
old = """              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>Visszavágó</div>"""
new = """              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>{t('rematchLabel')}</div>"""
assert old in html, "FAIL: visszavágó"
html = html.replace(old, new, 1)

# ── 21. Sorrend frissítve
old = """      {saved && <div style={{ textAlign:'center', fontFamily:T.font, fontSize:13, fontWeight:700, color:T.mint, padding:'4px 0' }}>✓ Sorrend frissítve</div>}"""
new = """      {saved && <div style={{ textAlign:'center', fontFamily:T.font, fontSize:13, fontWeight:700, color:T.mint, padding:'4px 0' }}>✓ {LANG==='en'?'Order updated':'Sorrend frissítve'}</div>}"""
assert old in html, "FAIL: sorrend frissítve"
html = html.replace(old, new, 1)

html = html.replace("const APP_VERSION = 'v9.365';", "const APP_VERSION = 'v9.366';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.366 — English translation: all major hardcoded Hungarian strings replaced with t() calls")
