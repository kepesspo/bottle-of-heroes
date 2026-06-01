import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Add csapatLosers state to PlayScreen ───────────────────────────────────
html = html.replace(
    '  const [selectedOpponent, setSelectedOpponent] = useState(null);\n  const transRef = React.useRef(false);',
    '  const [selectedOpponent, setSelectedOpponent] = useState(null);\n  const [csapatLosers, setCsapatLosers] = useState(new Set());\n  const transRef = React.useRef(false);',
    1
)

# ── 2. Reset csapatLosers when game advances ──────────────────────────────────
# Find the existing useEffect that resets selectedOpponent on gameIdx change
html = html.replace(
    '  React.useEffect(() => { setSelectedOpponent(null); }, [gameIdx]);',
    '  React.useEffect(() => { setSelectedOpponent(null); setCsapatLosers(new Set()); }, [gameIdx]);',
    1
)

# ── 3. Replace "Ki nyert?" section with card-based multi-select ───────────────
OLD_KINYERT = """      {currentGame.category === 'Csapat' && currentGameId !== 'loverseny' && currentGameId !== 'imposztor' && currentGameId !== 'busz' && currentGameId !== 'kisebb' && currentGameId !== 'ticktak' && currentGameId !== 'szerencse' && currentGameId !== 'kategoria' && currentGameId !== 'collect' && currentGameId !== 'kopapir' && currentGameId !== 'memoria' && currentGameId !== 'kezcsere' && (
        <div style={{ padding:'0 18px 14px', display:'flex', flexDirection:'column', gap:10, alignItems:'center' }}>
          <div style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.08em' }}>Ki nyert?</div>
          <div style={{ display:'flex', flexWrap:'wrap', gap:8, justifyContent:'center' }}>
            {players.map((p, i) => (
              <button key={p.id} onClick={() => !transitioning && advanceTeam(i)} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:4, padding:'8px 12px', border:'none', background:T.surface, borderRadius:14, boxShadow:T.shadow, cursor: transitioning ? 'default' : 'pointer' }}>
                <div style={{ width:44, height:44, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color:'#fff' }}>{p.name.charAt(0).toUpperCase()}</div>
                <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:11, color:T.ink, maxWidth:60, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
              </button>
            ))}
          </div>
        </div>
      )}"""

NEW_KINYERT = """      {currentGame.category === 'Csapat' && currentGameId !== 'loverseny' && currentGameId !== 'imposztor' && currentGameId !== 'busz' && currentGameId !== 'kisebb' && currentGameId !== 'ticktak' && currentGameId !== 'szerencse' && currentGameId !== 'kategoria' && currentGameId !== 'collect' && currentGameId !== 'kopapir' && currentGameId !== 'memoria' && currentGameId !== 'kezcsere' && (
        <div style={{ padding:'0 18px 14px', display:'flex', flexDirection:'column', gap:10 }}>
          <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.08em', textAlign:'center' }}>Ki rontott?</div>
          <div style={{ display:'flex', gap:8, flexWrap:'wrap', justifyContent:'center' }}>
            {players.map(p => {
              const sel = csapatLosers.has(p.id);
              return (
                <div key={p.id} onClick={() => !transitioning && setCsapatLosers(prev => { const s=new Set(prev); sel?s.delete(p.id):s.add(p.id); return s; })} style={{
                  display:'flex', flexDirection:'column', alignItems:'center', gap:6,
                  padding:'10px 14px', borderRadius:14,
                  background: sel ? '#FFF0EE' : T.surface,
                  border:`2px solid ${sel ? '#F87171' : 'transparent'}`,
                  boxShadow:T.shadow, cursor:transitioning?'default':'pointer', minWidth:70,
                }}>
                  <div style={{ width:44, height:44, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:17, color:'#fff' }}>
                    {p.name.charAt(0).toUpperCase()}
                  </div>
                  <div style={{ fontFamily:T.font, fontWeight:600, fontSize:12, color:sel?'#E55':T.ink }}>
                    {p.name}
                  </div>
                </div>
              );
            })}
          </div>
          {csapatLosers.size > 0 ? (
            <button onClick={() => { if(transitioning) return; const dm={}; csapatLosers.forEach(pid=>{dm[pid]=1;}); setCsapatLosers(new Set()); advanceLoverseny(dm); }} style={{ width:'100%', padding:'14px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow, animation:'popIn .2s' }}>
              {csapatLosers.size===1 ? `${players.find(p=>csapatLosers.has(p.id))?.name} iszik — következő játék →` : `${csapatLosers.size} ember iszik — következő játék →`}
            </button>
          ) : (
            <button onClick={() => { if(transitioning) return; advanceLoverseny({}); }} style={{ width:'100%', padding:'14px', background:'rgba(255,255,255,0.6)', color:T.inkSoft, fontFamily:T.font, fontWeight:600, fontSize:15, borderRadius:16, border:`2px solid rgba(0,0,0,0.1)`, cursor:'pointer' }}>
              Senki nem rontott — következő játék →
            </button>
          )}
        </div>
      )}"""

html = html.replace(OLD_KINYERT, NEW_KINYERT, 1)

# ── 4. Version bump ──────────────────────────────────────────────────────────
html = html.replace(
    'Verzió 5.27 · DNR · 2026.06.01 03:00',
    'Verzió 5.28 · DNR · 2026.06.01 04:00',
    1
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done")
