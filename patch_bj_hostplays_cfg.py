#!/usr/bin/env python3
# v9.811: Blackjack hostPlays config (long-tap), switch gating, host player view fixes
import io

P = 'index.html'
c = io.open(P, encoding='utf-8').read()

def rep(old, new, count=1):
    global c
    assert old in c, 'MISSING ANCHOR: ' + old[:90]
    assert c.count(old) == count, 'ANCHOR COUNT %d != %d: %s' % (c.count(old), count, old[:90])
    c = c.replace(old, new, count)

# ── 1a. BlackjackConfigSheet komponens (KisebbConfigSheet elé) ──
OLD = "function KisebbConfigSheet({ config, setConfig, onClose }) {"
NEW = """function BlackjackConfigSheet({ config, setConfig, onClose }) {
  const hostPlaysOn = config.hostPlays === true;
  return (
    <SheetOverlay onClose={onClose} title="Blackjack beállítások" footer={
      <button onClick={onClose} style={{ width:'100%', padding:'15px', borderRadius:16, background:T.mint, border:'none', color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer', boxShadow:'0 5px 16px -5px rgba(79,194,160,0.6)' }}>{t('busDoneBtn')}</button>
    }>
      <div style={{ padding:'0 18px 8px', display:'flex', flexDirection:'column' }}>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:'13px 0', borderTop:'none' }}>
          <div>
            <span style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>🎮 A host is játszik</span>
            <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:1 }}>A házigazda is beszállhat játékosként a saját telefonján</div>
          </div>
          <Toggle on={hostPlaysOn} onChange={() => setConfig(cf => ({...cf, hostPlays: !hostPlaysOn}))} />
        </div>
      </div>
    </SheetOverlay>
  );
}

function KisebbConfigSheet({ config, setConfig, onClose }) {"""
rep(OLD, NEW)

# ── 1b. GamesScreen state + config kötés ──
rep("  const [buszSheet, setBuszSheet] = useState(false);",
    "  const [buszSheet, setBuszSheet] = useState(false);\n  const [blackjackSheet, setBlackjackSheet] = useState(false);")

rep("""  const zeneConfig = gameMeta?.zeneConfig || {};
  const setZeneConfig = cfg => setGameMeta(m => ({...m, zeneConfig: typeof cfg === 'function' ? cfg(m?.zeneConfig||{}) : cfg}));""",
    """  const zeneConfig = gameMeta?.zeneConfig || {};
  const setZeneConfig = cfg => setGameMeta(m => ({...m, zeneConfig: typeof cfg === 'function' ? cfg(m?.zeneConfig||{}) : cfg}));
  const blackjackConfig = gameMeta?.blackjackConfig || {};
  const setBlackjackConfig = cfg => setGameMeta(m => ({...m, blackjackConfig: typeof cfg === 'function' ? cfg(m?.blackjackConfig||{}) : cfg}));""")

# ── 1c. Long-press elérhetőség: fav lista ──
rep("""                    : g.id==='zene' ? ()=>{ if(!selectedGames.includes('zene')) toggle('zene'); setZeneSheet(true); }
                    : undefined;""",
    """                    : g.id==='zene' ? ()=>{ if(!selectedGames.includes('zene')) toggle('zene'); setZeneSheet(true); }
                    : g.id==='blackjack' ? ()=>{ if(!selectedGames.includes('blackjack')) toggle('blackjack'); setBlackjackSheet(true); }
                    : undefined;""")

# ── 1d. Long-press: netflix + grid nézet (2 azonos ternary) ──
OLD_TERN = " : g.id==='zene' ? ()=>{ if(!selectedGames.includes('zene')) toggle('zene'); setZeneSheet(true); } : undefined} />"
NEW_TERN = " : g.id==='zene' ? ()=>{ if(!selectedGames.includes('zene')) toggle('zene'); setZeneSheet(true); } : g.id==='blackjack' ? ()=>{ if(!selectedGames.includes('blackjack')) toggle('blackjack'); setBlackjackSheet(true); } : undefined} />"
rep(OLD_TERN, NEW_TERN, count=2)

# ── 1e. Sheet render ──
rep("      {zeneSheet && <ZeneConfigSheet config={zeneConfig} setConfig={setZeneConfig} onClose={() => setZeneSheet(false)} />}",
    "      {zeneSheet && <ZeneConfigSheet config={zeneConfig} setConfig={setZeneConfig} onClose={() => setZeneSheet(false)} />}\n      {blackjackSheet && <BlackjackConfigSheet config={blackjackConfig} setConfig={setBlackjackConfig} onClose={() => setBlackjackSheet(false)} />}")

# ── 2. Switch gomb csak ha hostPlays be van kapcsolva + 3a. footer elrejtés ──
OLD = """  React.useEffect(() => {
    if (onSetBuszSwitch) onSetBuszSwitch(isOnline ? { fn: () => setHostViewMode(m => m === 'host' ? 'player' : 'host'), badge: 0 } : null);
  }, [isOnline]);
  React.useEffect(() => () => { onSetBuszSwitch && onSetBuszSwitch(null); }, []);"""
NEW = """  const bjHostPlaysEnabled = !!(gameMeta?.blackjackConfig?.hostPlays);
  React.useEffect(() => {
    if (onSetBuszSwitch) onSetBuszSwitch((isOnline && bjHostPlaysEnabled) ? { fn: () => setHostViewMode(m => m === 'host' ? 'player' : 'host'), badge: 0 } : null);
  }, [isOnline, gameMeta]);
  React.useEffect(() => () => { onSetBuszSwitch && onSetBuszSwitch(null); }, []);
  React.useEffect(() => {
    if (onSetHideFooter) onSetHideFooter(isOnline && hostViewMode === 'player');
  }, [isOnline, hostViewMode]);
  React.useEffect(() => () => { onSetHideFooter && onSetHideFooter(false); }, []);"""
rep(OLD, NEW)

# ── 3b. Host player nézet: onSwitchToHost átadása ──
rep("    return <BlackjackObserverView room={room} code={roomCode} onLeave={() => setHostViewMode('host')} keepClaimOnUnmount={true} initialPlayerId={hostSelfIdRef.current} onPlayerIdChange={pid => { hostSelfIdRef.current = pid; }} />;",
    "    return <BlackjackObserverView room={room} code={roomCode} onLeave={() => setHostViewMode('host')} keepClaimOnUnmount={true} initialPlayerId={hostSelfIdRef.current} onPlayerIdChange={pid => { hostSelfIdRef.current = pid; }} onSwitchToHost={() => setHostViewMode('host')} />;")

# ── 3c. Observer prop + vissza gomb a claim pickerben ──
rep("function BlackjackObserverView({ room, code, onLeave, keepClaimOnUnmount, initialPlayerId, onPlayerIdChange }) {",
    "function BlackjackObserverView({ room, code, onLeave, keepClaimOnUnmount, initialPlayerId, onPlayerIdChange, onSwitchToHost }) {")

OLD = """      <div style={{ position:'fixed', inset:0, zIndex:200, background:T.bg, display:'flex', flexDirection:'column' }}>
        <div style={{ flexShrink:0, background:T.bg, paddingTop:16, paddingBottom:12 }}>
          <div style={{ textAlign:'center', padding:'0 18px' }}>"""
NEW = """      <div style={{ position:'fixed', inset:0, zIndex:200, background:T.bg, display:'flex', flexDirection:'column' }}>
        <div style={{ flexShrink:0, background:T.bg, paddingTop:16, paddingBottom:12 }}>
          {onSwitchToHost && (
            <div style={{ display:'flex', alignItems:'center', padding:'0 12px', marginBottom:4 }}>
              <button onClick={onSwitchToHost} style={{ width:40, height:40, borderRadius:999, border:'none', background:'transparent', cursor:'pointer', display:'grid', placeItems:'center', flexShrink:0 }}>
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M15 18l-6-6 6-6" stroke={T.inkSoft} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/></svg>
              </button>
            </div>
          )}
          <div style={{ textAlign:'center', padding:'0 18px' }}>"""
rep(OLD, NEW)

# ── Verzióbump ──
rep("const APP_VERSION = 'v9.810';", "const APP_VERSION = 'v9.811';")
assert c.count('v9.811') == 1 and 'v9.810' not in c

io.open(P, 'w', encoding='utf-8').write(c)
print('patch OK')
