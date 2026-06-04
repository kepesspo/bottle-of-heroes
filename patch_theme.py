with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

orig = html

# 1. Replace const T with THEMES + let T
old = """const T = {
  bg: '#F4C57E',
  bgSoft: '#F8D69A',
  bgDeep: '#E8B260',
  surface: '#FFFFFF',
  surfaceMuted: '#FBEFD8',
  ink: '#1A2A4A',
  inkSoft: '#4A5878',
  inkMute: '#8A93A8',
  mint: '#4FC2A0',
  mintSoft: '#D9F1E8',
  mintDeep: '#3DA888',
  coral: '#F2A0A0',
  coralSoft: '#FBDADA',
  purple: '#A88AE8',
  yellow: '#F4C95A',
  blue: '#5BA0DB',
  pink: '#E985B8',
  font: '"Nunito", -apple-system, system-ui, sans-serif',
  weightDisplay: 900,
  weightTitle: 800,
  weightBody: 600,
  letter: '-0.01em',
  letterDisplay: '-0.02em',
  shadow: '0 2px 0 rgba(20,30,50,0.04), 0 6px 20px rgba(20,30,50,0.06)',
  shadowLift: '0 4px 0 rgba(20,30,50,0.06), 0 12px 32px rgba(20,30,50,0.10)',
};"""

new = """const THEMES = {
  warm: {
    bg: '#F4C57E',
    bgSoft: '#F8D69A',
    bgDeep: '#E8B260',
    surface: '#FFFFFF',
    surfaceMuted: '#FBEFD8',
    ink: '#1A2A4A',
    inkSoft: '#4A5878',
    inkMute: '#8A93A8',
    mint: '#4FC2A0',
    mintSoft: '#D9F1E8',
    mintDeep: '#3DA888',
    coral: '#F2A0A0',
    coralSoft: '#FBDADA',
    purple: '#A88AE8',
    yellow: '#F4C95A',
    blue: '#5BA0DB',
    pink: '#E985B8',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900,
    weightTitle: 800,
    weightBody: 600,
    letter: '-0.01em',
    letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(20,30,50,0.04), 0 6px 20px rgba(20,30,50,0.06)',
    shadowLift: '0 4px 0 rgba(20,30,50,0.06), 0 12px 32px rgba(20,30,50,0.10)',
  },
  dark: {
    bg: '#181C2E',
    bgSoft: '#202540',
    bgDeep: '#0F1220',
    surface: '#252B3E',
    surfaceMuted: '#1E2338',
    ink: '#E8EDF8',
    inkSoft: '#8A96B8',
    inkMute: '#4A5278',
    mint: '#4FC2A0',
    mintSoft: '#1A3D35',
    mintDeep: '#3DA888',
    coral: '#F28080',
    coralSoft: '#3D1A1A',
    purple: '#A88AE8',
    yellow: '#F4C95A',
    blue: '#5BA0DB',
    pink: '#E985B8',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900,
    weightTitle: 800,
    weightBody: 600,
    letter: '-0.01em',
    letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(0,0,0,0.2), 0 6px 20px rgba(0,0,0,0.3)',
    shadowLift: '0 4px 0 rgba(0,0,0,0.25), 0 12px 32px rgba(0,0,0,0.4)',
  },
};

let T = THEMES[localStorage.getItem('boh_theme') || 'warm'];"""

assert old in html, "T object not found"
html = html.replace(old, new, 1)

# 2. Update HomeScreen signature
old = "function HomeScreen({ go, mode, setMode, onStartGame }) {"
new = "function HomeScreen({ go, mode, setMode, onStartGame, setTheme, currentTheme }) {"
assert old in html
html = html.replace(old, new, 1)

# 3. Add theme toggle button inside HomeScreen - after the version badge div, before home-actions
old = """        <div className="home-actions">
          <div style={{ display:'flex', padding:6, background:T.surface, borderRadius:999, boxShadow:T.shadow }}>"""
new = """        {/* Theme toggle button */}
        <div style={{ position:'absolute', top:14, right:18, zIndex:10 }}>
          <button onClick={() => setTheme && setTheme(currentTheme === 'warm' ? 'dark' : 'warm')}
            style={{ width:42, height:42, borderRadius:'50%', border:'none', background:T.surface, boxShadow:T.shadow, cursor:'pointer', display:'grid', placeItems:'center', fontSize:20 }}>
            {currentTheme === 'dark' ? '☀️' : '🌙'}
          </button>
        </div>
        <div className="home-actions">
          <div style={{ display:'flex', padding:6, background:T.surface, borderRadius:999, boxShadow:T.shadow }}>"""
assert old in html, "home-actions not found"
html = html.replace(old, new, 1)

# Make the home screen wrapper relative for positioning
old = '    <div style={{ flex:1, display:\'flex\', flexDirection:\'column\', background:T.bg }}>\n      {showInstall && <InstallModal onClose={() => setShowInstall(false)} />}\n      <div className="home-inner">'
new = '    <div style={{ flex:1, display:\'flex\', flexDirection:\'column\', background:T.bg, position:\'relative\' }}>\n      {showInstall && <InstallModal onClose={() => setShowInstall(false)} />}\n      <div className="home-inner">'
assert old in html, "home wrapper not found"
html = html.replace(old, new, 1)

# 4. Add theme state to BottleApp
old = """  const [roomCode, setRoomCode] = React.useState(null);
  const [creatingRoom, setCreatingRoom] = React.useState(false);
  const roomUnsubRef = React.useRef(null);"""
new = """  const [appTheme, setAppTheme] = React.useState(() => localStorage.getItem('boh_theme') || 'warm');
  const handleSetTheme = (name) => {
    localStorage.setItem('boh_theme', name);
    T = THEMES[name];
    setAppTheme(name);
  };

  const [roomCode, setRoomCode] = React.useState(null);
  const [creatingRoom, setCreatingRoom] = React.useState(false);
  const roomUnsubRef = React.useRef(null);"""
assert old in html, "roomCode state not found"
html = html.replace(old, new, 1)

# 5. Pass theme props to HomeScreen
old = "        {screen==='home'     && <HomeScreen     go={go} mode={mode} setMode={setMode} onStartGame={onStartGame} />}"
new = "        {screen==='home'     && <HomeScreen     go={go} mode={mode} setMode={setMode} onStartGame={onStartGame} setTheme={handleSetTheme} currentTheme={appTheme} />}"
assert old in html
html = html.replace(old, new, 1)

# 6. Also sync T in the outer app div (so bg color updates)
old = "    <div style={{ minHeight:'100dvh', width:'100%', position:'relative', fontFamily:T.font, color:T.ink, WebkitFontSmoothing:'antialiased', overflow:'hidden', background:T.bg }}>"
new = "    <div style={{ minHeight:'100dvh', width:'100%', position:'relative', fontFamily:T.font, color:T.ink, WebkitFontSmoothing:'antialiased', overflow:'hidden', background:T.bg }} data-theme={appTheme}>"
assert old in html
html = html.replace(old, new, 1)

assert html != orig
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("done")
