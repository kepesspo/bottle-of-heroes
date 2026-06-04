with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Add useWindowWidth hook (before BracketView) ──────────────────────
OLD_HOOK = 'function BracketView({ seRoundsArr, seCurRound, seCurMatch }) {'
NEW_HOOK = '''function useWindowWidth() {
  const [w, setW] = React.useState(typeof window !== 'undefined' ? window.innerWidth : 375);
  React.useEffect(() => {
    const h = () => setW(window.innerWidth);
    window.addEventListener('resize', h);
    return () => window.removeEventListener('resize', h);
  }, []);
  return w;
}

function BracketView({ seRoundsArr, seCurRound, seCurMatch }) {'''
assert OLD_HOOK in html, 'BracketView not found'
html = html.replace(OLD_HOOK, NEW_HOOK, 1)

# ── 2. BeerPongObserverView: two-column on wide ───────────────────────────
# Add hook call at top of function
OLD_BP_TOP = '''function BeerPongObserverView({ room, code, onLeave }) {
  const bp = room.bpState || {};'''
NEW_BP_TOP = '''function BeerPongObserverView({ room, code, onLeave }) {
  const winW = useWindowWidth();
  const isWide = winW >= 768;
  const bp = room.bpState || {};'''
assert OLD_BP_TOP in html, 'BeerPongObserverView top not found'
html = html.replace(OLD_BP_TOP, NEW_BP_TOP, 1)

# Replace the scroll container to use row on wide, wrapping content in two columns
OLD_BP_SCROLL = '''      <div style={{ flex:1, minHeight:0, overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'8px 16px 24px', display:'flex', flexDirection:'column', gap:12 }}>'''
NEW_BP_SCROLL = '''      <div style={{ flex:1, minHeight:0, overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'8px 16px 24px', display:'flex', flexDirection: isWide ? 'row' : 'column', gap:12, alignItems:'flex-start' }}>
        <div style={{ flex:1, minWidth:0, display:'flex', flexDirection:'column', gap:12 }}>'''
assert OLD_BP_SCROLL in html, 'BP scroll container not found'
html = html.replace(OLD_BP_SCROLL, NEW_BP_SCROLL, 1)

# Close left column before drinks leaderboard and open right column
OLD_BP_DRINKS_START = '''        {/* Drinks leaderboard */}
        {players.length > 0 && ('''
NEW_BP_DRINKS_START = '''        </div>
        {/* Right column: Drinks leaderboard */}
        <div style={{ flex: isWide ? '0 0 200px' : undefined, width: isWide ? 200 : undefined, display:'flex', flexDirection:'column', gap:12 }}>
        {players.length > 0 && ('''
assert OLD_BP_DRINKS_START in html, 'BP drinks start not found'
html = html.replace(OLD_BP_DRINKS_START, NEW_BP_DRINKS_START, 1)

# Close right column at end of scroll div
OLD_BP_SCROLL_END = '''      </div>
    </div>
  );
}

function ObserverStatus'''
NEW_BP_SCROLL_END = '''        </div>
      </div>
    </div>
  );
}

function ObserverStatus'''
assert OLD_BP_SCROLL_END in html, 'BP scroll end not found'
html = html.replace(OLD_BP_SCROLL_END, NEW_BP_SCROLL_END, 1)

# ── 3. ObserverWatching: CSS grid on wide ────────────────────────────────
# Add hook call at top
OLD_OW_TOP = '''function ObserverWatching({ code, observerName, onLeave }) {
  const [room, setRoom] = useState(null);'''
NEW_OW_TOP = '''function ObserverWatching({ code, observerName, onLeave }) {
  const winW = useWindowWidth();
  const [room, setRoom] = useState(null);'''
assert OLD_OW_TOP in html, 'ObserverWatching top not found'
html = html.replace(OLD_OW_TOP, NEW_OW_TOP, 1)

# Replace the outer scroll+content div with a CSS grid-aware wrapper
OLD_OW_SCROLL = '''      <div style={{ flex:1, display:'flex', flexDirection:'column', padding:'12px 18px 12px', gap:12, overflowY:'auto' }}>'''
NEW_OW_SCROLL = '''      <div style={{ flex:1, minHeight:0, overflowY:'auto', WebkitOverflowScrolling:'touch' }}>
      <div style={{ padding:'12px 18px 12px', display: (winW >= 768 && currentGameId === 'beerpong' && room.bpState) ? 'grid' : 'flex', gridTemplateColumns: '1fr 260px', flexDirection:'column', gap:12 }}>'''
assert OLD_OW_SCROLL in html, 'OW scroll not found'
html = html.replace(OLD_OW_SCROLL, NEW_OW_SCROLL, 1)

# Add gridColumn:1 to live banner
OLD_OW_BANNER = '''        {/* live banner */}
        <div style={{ display:\'flex\', alignItems:\'center\', justifyContent:\'space-between\', padding:\'10px 14px\', borderRadius:14, background:T.surface, boxShadow:T.shadow }}>'''
NEW_OW_BANNER = '''        {/* live banner */}
        <div style={{ gridColumn: (winW >= 768 && currentGameId === \'beerpong\' && room.bpState) ? 1 : undefined, display:\'flex\', alignItems:\'center\', justifyContent:\'space-between\', padding:\'10px 14px\', borderRadius:14, background:T.surface, boxShadow:T.shadow }}>'''
assert OLD_OW_BANNER in html, 'OW banner not found'
html = html.replace(OLD_OW_BANNER, NEW_OW_BANNER, 1)

# Add gridColumn:1 to current game card
OLD_OW_GAMECARDWRAP = '''        {/* current game */}
        <div style={{ background:T.surface, borderRadius:18, boxShadow:T.shadow, padding:\'14px 14px\', display:\'flex\', alignItems:\'center\', gap:12 }}>'''
NEW_OW_GAMECARDWRAP = '''        {/* current game */}
        <div style={{ gridColumn: (winW >= 768 && currentGameId === \'beerpong\' && room.bpState) ? 1 : undefined, background:T.surface, borderRadius:18, boxShadow:T.shadow, padding:\'14px 14px\', display:\'flex\', alignItems:\'center\', gap:12 }}>'''
assert OLD_OW_GAMECARDWRAP in html, 'OW game card not found'
html = html.replace(OLD_OW_GAMECARDWRAP, NEW_OW_GAMECARDWRAP, 1)

# BeerPong state block: assign to right column (gridColumn:2, gridRow: 1/span 3)
OLD_OW_BP = '''        {/* Beer Pong live state */}
        {currentGameId === \'beerpong\' && room.bpState && (() => {
          const bp = room.bpState;'''
NEW_OW_BP = '''        {/* Beer Pong live state */}
        {currentGameId === \'beerpong\' && room.bpState && (() => {
          const _bpIsWide = winW >= 768;
          const bp = room.bpState;'''
assert OLD_OW_BP in html, 'OW BP block not found'
html = html.replace(OLD_OW_BP, NEW_OW_BP, 1)

# The BP block renders a wrapping div — add gridColumn/gridRow to it
OLD_OW_BP_DIV = '''            <div style={{ background:T.surface, borderRadius:18, boxShadow:T.shadow, padding:\'14px 14px\', display:\'flex\', flexDirection:\'column\', gap:10 }}>
              <div style={{ display:\'flex\', alignItems:\'center\', justifyContent:\'space-between\' }}>
                <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, letterSpacing:\'0.1em\', textTransform:\'uppercase\' }}>🏓 Beer Pong'''
NEW_OW_BP_DIV = '''            <div style={{ gridColumn: _bpIsWide ? 2 : undefined, gridRow: _bpIsWide ? \'1 / span 3\' : undefined, background:T.surface, borderRadius:18, boxShadow:T.shadow, padding:\'14px 14px\', display:\'flex\', flexDirection:\'column\', gap:10 }}>
              <div style={{ display:\'flex\', alignItems:\'center\', justifyContent:\'space-between\' }}>
                <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, letterSpacing:\'0.1em\', textTransform:\'uppercase\' }}>🏓 Beer Pong'''
assert OLD_OW_BP_DIV in html, 'OW BP wrapper div not found'
html = html.replace(OLD_OW_BP_DIV, NEW_OW_BP_DIV, 1)

# Add gridColumn:1 to leaderboard section
OLD_OW_LEADER = '''        {/* leaderboard */}
        <div style={{ display:\'flex\', flexDirection:\'column\', gap:6 }}>'''
NEW_OW_LEADER = '''        {/* leaderboard */}
        <div style={{ gridColumn: (winW >= 768 && currentGameId === \'beerpong\' && room.bpState) ? 1 : undefined, display:\'flex\', flexDirection:\'column\', gap:6 }}>'''
assert OLD_OW_LEADER in html, 'OW leaderboard not found'
html = html.replace(OLD_OW_LEADER, NEW_OW_LEADER, 1)

# Close the grid wrapper div
OLD_OW_SCROLL_END = '''      </div>

      {/* Megfigyelő panel */}'''
NEW_OW_SCROLL_END = '''      </div>
      </div>

      {/* Megfigyelő panel */}'''
assert OLD_OW_SCROLL_END in html, 'OW scroll end not found'
html = html.replace(OLD_OW_SCROLL_END, NEW_OW_SCROLL_END, 1)

# ── 4. Version bump ──────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v7.23'"
NEW_VER = "const APP_VERSION = 'v7.24'"
assert OLD_VER in html, 'version not found'
html = html.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("done")
