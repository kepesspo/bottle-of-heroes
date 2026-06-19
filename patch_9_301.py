#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. BottleApp: onQuickGame függvény
old1 = """  const onStartGame = () => {
    setPlayers([]); setSelectedGames([]); setRoomCode(null);
    setPrev(screen); setScreen('players');
  };"""
new1 = """  const onStartGame = () => {
    setPlayers([]); setSelectedGames([]); setRoomCode(null);
    setPrev(screen); setScreen('players');
  };
  const onQuickGame = () => {
    const FUNNY_NAMES = [
      { name:'Kókuszdió Kenő', color:'#F59E0B' }, { name:'Bubák Bence', color:'#6366F1' },
      { name:'Talpraesett Tomi', color:'#EC4899' }, { name:'Zavaros Zoli', color:'#14B8A6' },
      { name:'Csapzott Csabi', color:'#F97316' }, { name:'Nyúlánk Norbi', color:'#8B5CF6' },
      { name:'Gömbölyű Gábor', color:'#EF4444' }, { name:'Sunyi Sanyi', color:'#10B981' },
      { name:'Lompos Lali', color:'#3B82F6' }, { name:'Rőfös Robi', color:'#F43F5E' },
      { name:'Pislogó Péter', color:'#A3E635' }, { name:'Kancsal Karcsi', color:'#FB923C' },
      { name:'Fapados Feri', color:'#22D3EE' }, { name:'Dagadt Dani', color:'#C084FC' },
      { name:'Hebegő Huba', color:'#F472B6' }, { name:'Topogó Tibi', color:'#4ADE80' },
      { name:'Álmos Ábel', color:'#60A5FA' }, { name:'Nyeszlett Nándor', color:'#FBBF24' },
      { name:'Döcögős Dezső', color:'#34D399' }, { name:'Kapkodó Kinga', color:'#E879F9' },
      { name:'Szelíd Szilárd', color:'#F87171' }, { name:'Botladozó Balázs', color:'#38BDF8' },
      { name:'Nyafka Nóra', color:'#A78BFA' }, { name:'Tétova Tünde', color:'#4FC3A1' },
      { name:'Morgós Márton', color:'#FCD34D' }, { name:'Szuszogó Szabi', color:'#F9A8D4' },
      { name:'Kacskaringós Kende', color:'#6EE7B7' }, { name:'Pufók Panka', color:'#FCA5A5' },
      { name:'Nyakigláb Norbert', color:'#93C5FD' }, { name:'Borzas Béla', color:'#C4B5FD' },
    ];
    const shuffled = [...FUNNY_NAMES].sort(() => Math.random() - 0.5);
    const p1 = { id: 'qg_1', ...shuffled[0], drinks: 0, points: 0 };
    const p2 = { id: 'qg_2', ...shuffled[1], drinks: 0, points: 0 };
    const allGames = GAMES.filter(g => !g.comingSoon && g.id !== 'busz' && g.id !== 'beerpong' && g.id !== 'powerhour' && g.id !== 'ovfj' && g.id !== 'ringfire').map(g => g.id);
    const shuffledGames = [...allGames].sort(() => Math.random() - 0.5);
    setPlayers([p1, p2]);
    setSelectedGames(shuffledGames);
    setScoreHistory([]);
    setRoomCode(null);
    setPrev(screen); setScreen('play');
  };"""
assert old1 in html, "FAIL: onStartGame"
html = html.replace(old1, new1, 1)

# ── 2. HomeScreen: fogadja onQuickGame prop-ot
old2 = """function HomeScreen({ go, onStartGame, setTheme, currentTheme, setLang, currentLang, resumeRoomData, onResume }) {"""
new2 = """function HomeScreen({ go, onStartGame, onQuickGame, setTheme, currentTheme, setLang, currentLang, resumeRoomData, onResume }) {"""
assert old2 in html, "FAIL: HomeScreen signature"
html = html.replace(old2, new2, 1)

# ── 3. HomeScreen: Quick Game gomb hozzáadása a két meglévő gomb alá
old3 = """          <div style={{ display:'flex', gap:12, width:'100%' }}>
            <button onClick={onStartGame || (() => go('players'))} style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', gap:14, padding:'24px 12px 20px', border:'none', background:T.mint, borderRadius:20, cursor:'pointer', boxShadow:`0 6px 24px ${T.mint}55` }}>
              <div style={{ width:64, height:64, borderRadius:'50%', background:'rgba(255,255,255,0.25)', display:'grid', placeItems:'center' }}>
                <svg width="28" height="28" viewBox="0 0 24 24" fill="white"><polygon points="5,3 19,12 5,21"/></svg>
              </div>
              <div>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:'#fff', letterSpacing:'-0.01em' }}>{t('play')}</div>
                <div style={{ fontFamily:T.font, fontSize:12, color:'rgba(255,255,255,0.75)', marginTop:3 }}>{t('newRound')}</div>
              </div>
            </button>
            <button onClick={() => go('observer')} style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', gap:14, padding:'24px 12px 20px', border:'none', background:T.surface, borderRadius:20, cursor:'pointer', boxShadow:T.shadow }}>
              <div style={{ width:64, height:64, borderRadius:'50%', background:`${T.coral}18`, display:'grid', placeItems:'center' }}>
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke={T.coral} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
              </div>
              <div>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.coral, letterSpacing:'-0.01em' }}>{t('join')}</div>
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:3 }}>{t('enterCode')}</div>
              </div>
            </button>
          </div>"""
new3 = """          <div style={{ display:'flex', gap:12, width:'100%' }}>
            <button onClick={onStartGame || (() => go('players'))} style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', gap:14, padding:'24px 12px 20px', border:'none', background:T.mint, borderRadius:20, cursor:'pointer', boxShadow:`0 6px 24px ${T.mint}55` }}>
              <div style={{ width:64, height:64, borderRadius:'50%', background:'rgba(255,255,255,0.25)', display:'grid', placeItems:'center' }}>
                <svg width="28" height="28" viewBox="0 0 24 24" fill="white"><polygon points="5,3 19,12 5,21"/></svg>
              </div>
              <div>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:'#fff', letterSpacing:'-0.01em' }}>{t('play')}</div>
                <div style={{ fontFamily:T.font, fontSize:12, color:'rgba(255,255,255,0.75)', marginTop:3 }}>{t('newRound')}</div>
              </div>
            </button>
            <button onClick={() => go('observer')} style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', gap:14, padding:'24px 12px 20px', border:'none', background:T.surface, borderRadius:20, cursor:'pointer', boxShadow:T.shadow }}>
              <div style={{ width:64, height:64, borderRadius:'50%', background:`${T.coral}18`, display:'grid', placeItems:'center' }}>
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke={T.coral} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
              </div>
              <div>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.coral, letterSpacing:'-0.01em' }}>{t('join')}</div>
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:3 }}>{t('enterCode')}</div>
              </div>
            </button>
          </div>
          <button onClick={onQuickGame} style={{ width:'100%', display:'flex', alignItems:'center', justifyContent:'center', gap:16, padding:'24px 12px 20px', border:'none', background:T.surface, borderRadius:20, cursor:'pointer', boxShadow:T.shadow }}>
            <div style={{ width:64, height:64, borderRadius:'50%', background:'#F59E0B22', display:'grid', placeItems:'center', flexShrink:0 }}>
              <span style={{ fontSize:30 }}>⚡</span>
            </div>
            <div style={{ textAlign:'left' }}>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:'#F59E0B', letterSpacing:'-0.01em' }}>Quick Game</div>
              <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:3 }}>2 véletlenszerű játékos, összes játék</div>
            </div>
          </button>"""
assert old3 in html, "FAIL: home action buttons"
html = html.replace(old3, new3, 1)

# ── 4. Pass onQuickGame to HomeScreen
old4 = """        {screen==='home'     && <HomeScreen     go={go} onStartGame={onStartGame} setTheme={handleSetTheme} currentTheme={appTheme} setLang={handleSetLang} currentLang={appLang} resumeRoomData={resumeRoomData} onResume={goResume} />}"""
new4 = """        {screen==='home'     && <HomeScreen     go={go} onStartGame={onStartGame} onQuickGame={onQuickGame} setTheme={handleSetTheme} currentTheme={appTheme} setLang={handleSetLang} currentLang={appLang} resumeRoomData={resumeRoomData} onResume={goResume} />}"""
assert old4 in html, "FAIL: HomeScreen render"
html = html.replace(old4, new4, 1)

html = html.replace("const APP_VERSION = 'v9.299';", "const APP_VERSION = 'v9.301';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.301 — Quick Game gomb főképernyőn, 2 vicces véletlenszerű játékos, összes játék")
