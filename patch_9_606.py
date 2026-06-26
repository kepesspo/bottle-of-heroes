#!/usr/bin/env python3
"""
v9.606 — Körváltás overlay redesign:
- Páros: teljes képernyős VS split (bal/jobb szín, avatar, VS badge)
- Egyéni: teljes képernyős játékos szín + nagy avatar
- Csapat: sötét gradiens + nagy sör + játékosok
"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

assert html.count('v9.605') >= 1
html = html.replace('v9.605', 'v9.606', 1)

OLD = """      {/* Round transition popup */}
      {roundPopup && (
        <div onClick={() => { setRoundPopup(null); }} style={{ position:'fixed', inset:0, zIndex:9998, background:`linear-gradient(to bottom, ${T.bg} 0%, ${T.bgOverlay} 45%)`, display:'flex', alignItems:'center', justifyContent:'center' }}>
          <div style={{ position:'absolute', left:'50%', top:'50%', animation: roundPopup.leaving ? 'roundPopOut 0.5s ease-in forwards' : 'roundPopIn 0.5s cubic-bezier(.2,.9,.3,1.2) forwards', textAlign:'center', width:'88%', maxWidth:340 }}>
            {roundPopup.showRound && (() => {
              const curP = players[turn % players.length];
              const cat = currentGame?.category;
              return (
                <div style={{ marginBottom: roundPopup.wildcard ? 20 : 0 }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:64, color:'#fff', lineHeight:1, textShadow:'0 4px 24px rgba(0,0,0,0.4)', letterSpacing:'-0.02em' }}>{roundPopup.round}. {t('roundWord')}</div>
                  <div style={{ marginTop:28 }}>
                    {cat === 'Csapat' ? (
                      <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:10, background:'rgba(255,255,255,0.15)', backdropFilter:'blur(8px)', borderRadius:20, padding:'14px 28px', border:'1.5px solid rgba(255,255,255,0.25)' }}>
                        <span style={{ fontSize:22 }}>🍺</span>
                        <span style={{ fontFamily:T.font, fontWeight:800, fontSize:18, color:'#fff' }}>{t('everyonePlays')}</span>
                      </div>
                    ) : cat === 'Páros' && curP && selectedOpponent ? (
                      <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:16, background:'rgba(255,255,255,0.15)', backdropFilter:'blur(8px)', borderRadius:20, padding:'16px 24px', border:'1.5px solid rgba(255,255,255,0.25)' }}>
                        <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:6 }}>
                          <div style={{ width:44, height:44, borderRadius:'50%', background:curP.color, display:'grid', placeItems:'center', overflow:'hidden', boxShadow:'0 2px 8px rgba(0,0,0,0.3)' }}>
                            {curP.img ? <img src={curP.img} style={{ width:44, height:44, objectFit:'cover', borderRadius:'50%' }} /> : <span style={{ fontSize:20 }}>👤</span>}
                          </div>
                          <span style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:'#fff', maxWidth:90, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{curP.name}</span>
                        </div>
                        <span style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:'rgba(255,255,255,0.6)' }}>VS</span>
                        <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:6 }}>
                          <div style={{ width:44, height:44, borderRadius:'50%', background:selectedOpponent.color, display:'grid', placeItems:'center', overflow:'hidden', boxShadow:'0 2px 8px rgba(0,0,0,0.3)' }}>
                            {selectedOpponent.img ? <img src={selectedOpponent.img} style={{ width:44, height:44, objectFit:'cover', borderRadius:'50%' }} /> : <span style={{ fontSize:20 }}>👤</span>}
                          </div>
                          <span style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:'#fff', maxWidth:90, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{selectedOpponent.name}</span>
                        </div>
                      </div>
                    ) : curP ? (
                      <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:12, background:'rgba(255,255,255,0.15)', backdropFilter:'blur(8px)', borderRadius:20, padding:'16px 28px', border:'1.5px solid rgba(255,255,255,0.25)' }}>
                        <div style={{ width:44, height:44, borderRadius:'50%', background:curP.color, display:'grid', placeItems:'center', overflow:'hidden', boxShadow:'0 2px 8px rgba(0,0,0,0.3)' }}>
                          {curP.img ? <img src={curP.img} style={{ width:44, height:44, objectFit:'cover', borderRadius:'50%' }} /> : <span style={{ fontSize:20 }}>👤</span>}
                        </div>
                        <span style={{ fontFamily:T.font, fontWeight:800, fontSize:20, color:'#fff' }}>{curP.name} játéka</span>
                      </div>
                    ) : null}
                  </div>
                </div>
              );
            })()}
            {roundPopup.wildcard && (
              <>
                <div style={{ background:'linear-gradient(135deg,#FFE066,#FF6B35)', borderRadius:24, padding:'20px 24px', boxShadow:'0 8px 40px rgba(0,0,0,0.4), 0 0 0 3px rgba(255,255,255,0.2)', border:'2px dashed rgba(255,255,255,0.5)', position:'relative', overflow:'visible' }}>
                  {/* Floating drink icons around card */}
                  <div style={{ position:'absolute', top:-16, left:-10, fontSize:24, animation:'floatBob 2.0s 0.1s ease-in-out infinite', pointerEvents:'none' }}>🍹</div>
                  <div style={{ position:'absolute', top:-14, right:-8, fontSize:22, animation:'floatBob 1.8s 0.45s ease-in-out infinite', pointerEvents:'none' }}>🥃</div>
                  <div style={{ position:'absolute', bottom:-12, left:10, fontSize:20, animation:'floatBob 2.2s 0.3s ease-in-out infinite', pointerEvents:'none' }}>🍺</div>
                  <div style={{ position:'absolute', bottom:-10, right:14, fontSize:18, animation:'floatBob 1.9s 0.65s ease-in-out infinite', pointerEvents:'none' }}>🥂</div>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:'rgba(0,0,0,0.5)', textTransform:'uppercase', letterSpacing:'0.18em', marginBottom:10 }}>{t('wildcardRound')}</div>
                  <div style={{ fontSize:48, marginBottom:12, animation:'wobble 2.5s ease-in-out infinite' }}>{roundPopup.wildcard.emoji}</div>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:'#1A0A00', lineHeight:1.4 }}>{roundPopup.wildcard.text}</div>
                </div>
                <div style={{ marginTop:14, fontFamily:T.font, fontSize:13, fontWeight:700, color:'rgba(255,255,255,0.7)', background:'rgba(255,255,255,0.12)', borderRadius:20, padding:'8px 20px', display:'inline-block' }}>{t('tapToContinue')}</div>
              </>
            )}
          </div>
        </div>
      )}"""

NEW = """      {/* Round transition popup */}
      {roundPopup && (() => {
        const curP = players[turn % players.length];
        const cat = currentGame?.category;
        const isPáros = cat === 'Páros' && curP && selectedOpponent;
        const isCsapat = cat === 'Csapat';
        return (
          <div onClick={() => { setRoundPopup(null); }} style={{ position:'fixed', inset:0, zIndex:9998, display:'flex', flexDirection:'column' }}>
            {roundPopup.showRound && (
              isPáros ? (
                /* ── Páros: teljes képernyős VS split ── */
                <div style={{ flex:1, position:'relative', display:'flex', overflow:'hidden' }}>
                  {/* Bal fél */}
                  <div style={{ position:'absolute', inset:0, left:0, right:'45%', background:curP.color, clipPath:'polygon(0 0,100% 0,85% 100%,0 100%)', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', paddingRight:40 }}>
                    <div style={{ width:110, height:110, borderRadius:'50%', background:'rgba(0,0,0,0.18)', display:'grid', placeItems:'center', overflow:'hidden', boxShadow:'0 8px 32px rgba(0,0,0,0.45)', border:'4px solid rgba(255,255,255,0.35)' }}>
                      {curP.img ? <img src={curP.img} style={{ width:110, height:110, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:48, color:'#fff' }}>{(curP.name||'?').charAt(0).toUpperCase()}</span>}
                    </div>
                    <span style={{ marginTop:18, fontFamily:T.font, fontWeight:900, fontSize:18, color:'#fff', textShadow:'0 2px 8px rgba(0,0,0,0.5)', maxWidth:140, textAlign:'center', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{curP.name}</span>
                  </div>
                  {/* Jobb fél */}
                  <div style={{ position:'absolute', inset:0, left:'55%', right:0, background:selectedOpponent.color, clipPath:'polygon(15% 0,100% 0,100% 100%,0 100%)', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', paddingLeft:40 }}>
                    <div style={{ width:110, height:110, borderRadius:'50%', background:'rgba(0,0,0,0.18)', display:'grid', placeItems:'center', overflow:'hidden', boxShadow:'0 8px 32px rgba(0,0,0,0.45)', border:'4px solid rgba(255,255,255,0.35)' }}>
                      {selectedOpponent.img ? <img src={selectedOpponent.img} style={{ width:110, height:110, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:48, color:'#fff' }}>{(selectedOpponent.name||'?').charAt(0).toUpperCase()}</span>}
                    </div>
                    <span style={{ marginTop:18, fontFamily:T.font, fontWeight:900, fontSize:18, color:'#fff', textShadow:'0 2px 8px rgba(0,0,0,0.5)', maxWidth:140, textAlign:'center', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{selectedOpponent.name}</span>
                  </div>
                  {/* VS badge */}
                  <div style={{ position:'absolute', left:'50%', top:'50%', transform:'translate(-50%,-50%)', width:58, height:58, borderRadius:'50%', background:'#fff', display:'grid', placeItems:'center', boxShadow:'0 4px 24px rgba(0,0,0,0.45)', zIndex:3 }}>
                    <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:'#111', letterSpacing:'0.04em' }}>VS</span>
                  </div>
                  {/* Kör szám */}
                  <div style={{ position:'absolute', top:28, left:'50%', transform:'translateX(-50%)', background:'rgba(0,0,0,0.38)', backdropFilter:'blur(8px)', borderRadius:20, padding:'6px 22px', zIndex:3 }}>
                    <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', letterSpacing:'0.1em', textTransform:'uppercase' }}>{roundPopup.round}. {t('roundWord')}</span>
                  </div>
                  {/* Érintsd meg */}
                  <div style={{ position:'absolute', bottom:28, left:'50%', transform:'translateX(-50%)', zIndex:3 }}>
                    <span style={{ fontFamily:T.font, fontSize:13, fontWeight:700, color:'rgba(255,255,255,0.75)' }}>{t('tapToContinue')}</span>
                  </div>
                </div>
              ) : isCsapat ? (
                /* ── Csapat: sötét gradiens + sör + mindenki ── */
                <div style={{ flex:1, position:'relative', background:'linear-gradient(160deg,#1e1b4b 0%,#2d2570 55%,#4c1d95 100%)', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:18 }}>
                  <div style={{ position:'absolute', top:28, left:'50%', transform:'translateX(-50%)', background:'rgba(255,255,255,0.12)', backdropFilter:'blur(8px)', borderRadius:20, padding:'6px 22px' }}>
                    <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:'rgba(255,255,255,0.9)', letterSpacing:'0.1em', textTransform:'uppercase' }}>{roundPopup.round}. {t('roundWord')}</span>
                  </div>
                  <div style={{ fontSize:72, animation:'wobble 2s ease-in-out infinite', lineHeight:1 }}>🍺</div>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:26, color:'#fff', textAlign:'center', lineHeight:1.2, textShadow:'0 2px 12px rgba(0,0,0,0.4)' }}>{t('everyonePlays')}</div>
                  <div style={{ display:'flex', justifyContent:'center', marginTop:4 }}>
                    {players.slice(0,8).map((p,i) => (
                      <div key={p.id} style={{ width:38, height:38, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', overflow:'hidden', border:'2.5px solid rgba(255,255,255,0.4)', marginLeft:i?-10:0, boxShadow:'0 2px 10px rgba(0,0,0,0.4)', zIndex:8-i }}>
                        {p.img ? <img src={p.img} style={{ width:38, height:38, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff' }}>{(p.name||'?').charAt(0).toUpperCase()}</span>}
                      </div>
                    ))}
                  </div>
                  <div style={{ position:'absolute', bottom:28, left:'50%', transform:'translateX(-50%)' }}>
                    <span style={{ fontFamily:T.font, fontSize:13, fontWeight:700, color:'rgba(255,255,255,0.65)' }}>{t('tapToContinue')}</span>
                  </div>
                </div>
              ) : curP ? (
                /* ── Egyéni: játékos szín + nagy avatar ── */
                <div style={{ flex:1, position:'relative', background:`linear-gradient(160deg,${curP.color}BB 0%,${curP.color} 100%)`, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:16 }}>
                  <div style={{ position:'absolute', top:28, left:'50%', transform:'translateX(-50%)', background:'rgba(0,0,0,0.3)', backdropFilter:'blur(8px)', borderRadius:20, padding:'6px 22px' }}>
                    <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', letterSpacing:'0.1em', textTransform:'uppercase' }}>{roundPopup.round}. {t('roundWord')}</span>
                  </div>
                  <div style={{ width:120, height:120, borderRadius:'50%', background:'rgba(0,0,0,0.18)', display:'grid', placeItems:'center', overflow:'hidden', boxShadow:'0 10px 40px rgba(0,0,0,0.4)', border:'4px solid rgba(255,255,255,0.4)' }}>
                    {curP.img ? <img src={curP.img} style={{ width:120, height:120, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:54, color:'#fff' }}>{(curP.name||'?').charAt(0).toUpperCase()}</span>}
                  </div>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:28, color:'#fff', textShadow:'0 2px 12px rgba(0,0,0,0.35)', textAlign:'center' }}>{curP.name}</div>
                  <div style={{ background:'rgba(255,255,255,0.22)', backdropFilter:'blur(8px)', borderRadius:16, padding:'9px 26px', border:'1px solid rgba(255,255,255,0.3)' }}>
                    <span style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff' }}>Te játszol! 🎮</span>
                  </div>
                  <div style={{ position:'absolute', bottom:28, left:'50%', transform:'translateX(-50%)' }}>
                    <span style={{ fontFamily:T.font, fontSize:13, fontWeight:700, color:'rgba(255,255,255,0.75)' }}>{t('tapToContinue')}</span>
                  </div>
                </div>
              ) : null
            )}
            {roundPopup.wildcard && (
              <div style={{ position:'absolute', inset:0, zIndex:4, background:'rgba(0,0,0,0.65)', backdropFilter:'blur(6px)', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }} onClick={e => e.stopPropagation()}>
                <div style={{ textAlign:'center', width:'88%', maxWidth:340, animation: roundPopup.leaving ? 'roundPopOut 0.5s ease-in forwards' : 'roundPopIn 0.5s cubic-bezier(.2,.9,.3,1.2) forwards' }}>
                  <div style={{ background:'linear-gradient(135deg,#FFE066,#FF6B35)', borderRadius:24, padding:'20px 24px', boxShadow:'0 8px 40px rgba(0,0,0,0.4), 0 0 0 3px rgba(255,255,255,0.2)', border:'2px dashed rgba(255,255,255,0.5)', position:'relative', overflow:'visible' }}>
                    <div style={{ position:'absolute', top:-16, left:-10, fontSize:24, animation:'floatBob 2.0s 0.1s ease-in-out infinite', pointerEvents:'none' }}>🍹</div>
                    <div style={{ position:'absolute', top:-14, right:-8, fontSize:22, animation:'floatBob 1.8s 0.45s ease-in-out infinite', pointerEvents:'none' }}>🥃</div>
                    <div style={{ position:'absolute', bottom:-12, left:10, fontSize:20, animation:'floatBob 2.2s 0.3s ease-in-out infinite', pointerEvents:'none' }}>🍺</div>
                    <div style={{ position:'absolute', bottom:-10, right:14, fontSize:18, animation:'floatBob 1.9s 0.65s ease-in-out infinite', pointerEvents:'none' }}>🥂</div>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:'rgba(0,0,0,0.5)', textTransform:'uppercase', letterSpacing:'0.18em', marginBottom:10 }}>{t('wildcardRound')}</div>
                    <div style={{ fontSize:48, marginBottom:12, animation:'wobble 2.5s ease-in-out infinite' }}>{roundPopup.wildcard.emoji}</div>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:'#1A0A00', lineHeight:1.4 }}>{roundPopup.wildcard.text}</div>
                  </div>
                  <div onClick={() => setRoundPopup(null)} style={{ marginTop:14, fontFamily:T.font, fontSize:13, fontWeight:700, color:'rgba(255,255,255,0.7)', background:'rgba(255,255,255,0.12)', borderRadius:20, padding:'8px 20px', display:'inline-block', cursor:'pointer' }}>{t('tapToContinue')}</div>
                </div>
              </div>
            )}
          </div>
        );
      })()}"""

assert html.count(OLD) == 1, f"roundPopup block: {html.count(OLD)}"
html = html.replace(OLD, NEW, 1)
print("OK: körváltás overlay redesign")

print(f"Final size: {len(html):,} chars")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written OK.")
