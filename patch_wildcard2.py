#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Wildcard körök 2.0:
#  - aktív wildcard szabály a teljes kör alatt látható sávban (top bar alatt)
#  - "Szabályszegő?" gomb → játékosválasztó → +1 korty (toast + hang + room sync)
#  - gyakoriság-beállítás a Játékmenet sheetben (3/5/7/10 körönként, alap 5)
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'expected %d, found %d for: %r' % (count, n, old[:90])
    src = src.replace(old, new)

# 1) i18n info szövegek
rep("    modeWildcardInfo: 'Minden 5. kör elején megjelenik egy random különleges szabály (pl. bal kézzel inni, pókerpofa kör).',",
    "    modeWildcardInfo: 'Megadott körönként megjelenik egy random különleges szabály (pl. bal kézzel inni, pókerpofa kör). A szabály a teljes kör alatt látható marad, és a szabályszegőnek egy koppintással kortyot oszthatsz.',")
rep("    modeWildcardInfo: 'Every 5th round begins with a random special rule (e.g. drink with left hand, poker face round).',",
    "    modeWildcardInfo: 'Every Nth round begins with a random special rule (e.g. drink with left hand, poker face round). The rule stays visible for the whole round, and rule-breakers can be given a sip with one tap.',")

# 2) Gyakoriság-választó a Játékmenet sheet wildcard pillje alá
rep("""              <InfoBox id={m.id} text={m.info} />
            </div>
          );
        })}
      </div>""",
"""              <InfoBox id={m.id} text={m.info} />
              {m.id === 'wildcard' && on && (
                <div style={{ display:'flex', alignItems:'center', gap:8, marginTop:8, padding:'10px 12px', background:T.surfaceMuted, borderRadius:12 }}>
                  <span style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft, flex:1 }}>Hányadik körönként?</span>
                  <div style={{ display:'flex', gap:4 }}>
                    {[3,5,7,10].map(n => {
                      const sel = (meta.wildcardFreq || 5) === n;
                      return <button key={n} onClick={() => setMeta({...meta, wildcardFreq:n})} style={{ width:38, padding:'8px 0', borderRadius:10, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:13, background: sel?T.mint:T.surface, color: sel?'#fff':T.inkSoft, transition:'all .15s' }}>{n}</button>;
                    })}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>""")

# 3) PlayScreen state
rep("  const [roundPopup, setRoundPopup] = useState(null); // {round, wildcard, leaving}",
"""  const [roundPopup, setRoundPopup] = useState(null); // {round, wildcard, leaving}
  const [activeWildcard, setActiveWildcard] = useState(null); // {emoji, text, round} — a kör alatt végig látható szabály
  const [wcPunishOpen, setWcPunishOpen] = useState(false);
  const [wcToast, setWcToast] = useState(null); // {name}""")

# 4) Körváltás: gyakoriság + aktív wildcard követés
rep("""        const isWildcardRound = gameMeta?.modes?.includes('wildcard') && newRound % 5 === 0;
        const wc = isWildcardRound ? WILDCARDS[Math.floor(Math.random() * WILDCARDS.length)] : null;""",
"""        const wcFreq = gameMeta?.wildcardFreq || 5;
        const isWildcardRound = gameMeta?.modes?.includes('wildcard') && newRound % wcFreq === 0;
        const wc = isWildcardRound ? WILDCARDS[Math.floor(Math.random() * WILDCARDS.length)] : null;
        if (isWildcardRound && wc) setActiveWildcard({ ...wc, round: newRound });
        else setActiveWildcard(null);""")

# 5) punishWildcard a commitPending mellé
rep("""  const commitPending = () => {
    if (!pendingCommit || transitioning) return;
    const {newPlayers, fb, newTurn, newGameIdx, newRound} = pendingCommit;
    setPendingCommit(null);
    commitRound(newPlayers, fb, newTurn, newGameIdx, newRound);
  };""",
"""  const commitPending = () => {
    if (!pendingCommit || transitioning) return;
    const {newPlayers, fb, newTurn, newGameIdx, newRound} = pendingCommit;
    setPendingCommit(null);
    commitRound(newPlayers, fb, newTurn, newGameIdx, newRound);
  };

  const punishWildcard = (pid) => {
    const upd = playersRef.current.map(p => p.id === pid ? { ...p, drinks: (p.drinks || 0) + 1 } : p);
    setPlayers(upd);
    if (roomCode && typeof syncRoom === 'function') syncRoom(roomCode, { players: upd, turn, gameIdx, round });
    const pl = upd.find(p => p.id === pid);
    setWcPunishOpen(false);
    setWcToast({ name: pl ? pl.name : '?' });
    setTimeout(() => setWcToast(null), 2000);
    try { if (typeof window.bohSound === 'function') window.bohSound('lose'); } catch(e) {}
  };""")

# 6) Aktív wildcard sáv a top bar és a görgethető tartalom közé
rep("""        })()}
      </div>

      {/* ── Scrollable content ── */}""",
"""        })()}
      </div>

      {/* ── Aktív wildcard szabály sáv ── */}
      {activeWildcard && (
        <div style={{ flexShrink:0, maxWidth:960, width:'100%', margin:'0 auto', boxSizing:'border-box', padding:'2px 16px 6px' }}>
          <div style={{ display:'flex', alignItems:'center', gap:10, background:'linear-gradient(135deg,#FFE066,#FF6B35)', borderRadius:14, padding:'8px 12px', boxShadow:'0 3px 12px rgba(255,107,53,0.35)', animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)' }}>
            <span style={{ fontSize:22, flexShrink:0, lineHeight:1 }}>{activeWildcard.emoji}</span>
            <div style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:800, fontSize:12, lineHeight:1.3, color:'#1A0A00', display:'-webkit-box', WebkitLineClamp:2, WebkitBoxOrient:'vertical', overflow:'hidden' }}>{activeWildcard.text}</div>
            <button onClick={() => setWcPunishOpen(true)} style={{ flexShrink:0, border:'none', borderRadius:10, background:'rgba(26,10,0,0.82)', color:'#FFE066', fontFamily:T.font, fontWeight:900, fontSize:11.5, padding:'8px 10px', cursor:'pointer', display:'flex', alignItems:'center', gap:5 }}>
              <BohIcon name="beer" size={13} />Szabályszegő?
            </button>
          </div>
        </div>
      )}

      {/* ── Scrollable content ── */}""")

# 7) Szabályszegő-választó overlay + toast (a csoportos ivás overlay elé)
rep("""      {showBpConfig && <BeerPongConfigSheet""",
"""      {wcPunishOpen && activeWildcard && (
        <div onClick={() => setWcPunishOpen(false)} style={{ position:'fixed', inset:0, background:'rgba(14,14,24,0.72)', zIndex:60, display:'flex', alignItems:'center', justifyContent:'center', padding:28, animation:'fadeIn .2s' }}>
          <div onClick={e => e.stopPropagation()} style={{ background:T.surface, borderRadius:28, padding:'26px 22px 22px', width:'100%', maxWidth:340, boxShadow:'0 24px 64px rgba(0,0,0,0.3)', animation:'popIn .3s cubic-bezier(.2,.9,.3,1.3)' }}>
            <div style={{ textAlign:'center', fontSize:34, lineHeight:1, marginBottom:8 }}>{activeWildcard.emoji}</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, textAlign:'center', marginBottom:4 }}>Ki szegte meg a szabályt?</div>
            <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkSoft, textAlign:'center', marginBottom:14, lineHeight:1.4 }}>{activeWildcard.text}</div>
            <div style={{ display:'flex', flexDirection:'column', gap:8, maxHeight:'42vh', overflowY:'auto' }}>
              {players.filter(p => p.active !== false).map(p => (
                <button key={p.id} onClick={() => punishWildcard(p.id)} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 14px', borderRadius:14, border:'none', background:T.surfaceMuted, cursor:'pointer', textAlign:'left' }}>
                  <PlayerAvatar player={p} size={36} />
                  <span style={{ flex:1, fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</span>
                  <BohIcon name="beer" size={16} />
                </button>
              ))}
            </div>
            <button onClick={() => setWcPunishOpen(false)} style={{ width:'100%', marginTop:12, padding:'12px 0', borderRadius:14, border:'none', background:T.surfaceMuted, color:T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:14, cursor:'pointer' }}>Mégse</button>
          </div>
        </div>
      )}
      {wcToast && (
        <div style={{ position:'fixed', bottom:96, left:'50%', transform:'translateX(-50%)', zIndex:260, pointerEvents:'none', background:'rgba(26,42,74,0.92)', borderRadius:14, padding:'11px 20px', fontFamily:T.font, fontWeight:800, fontSize:14, color:'#fff', whiteSpace:'nowrap', animation:'toastIn .18s ease-out', display:'flex', alignItems:'center', gap:6 }}>
          {wcToast.name} iszik 1-et! <BohIcon name="beer" size={16} />
        </div>
      )}
      {showBpConfig && <BeerPongConfigSheet""")

# 8) Verziobump
rep("const APP_VERSION = 'v9.951';", "const APP_VERSION = 'v9.952';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — wildcard 2.0 applied')
