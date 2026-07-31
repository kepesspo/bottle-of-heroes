#!/usr/bin/env python3
# v10.197 — Tapper: a mockup szerinti elrendezés
#
# Eddig a jatekos neve kozepen allt a szines tablan, semmi mas. A terv szerint:
#   - bal oldalt kor alaku avatar, mellette balra zarva a nev es a "TARTSD"
#   - alatta pont-sor, ami a visszaszamlalas allasat mutatja
#   - a lap aljan tipp-doboz
#
# A pontok nem dekoraciok: eddig CSAK a kozepso 5.0 → 0.0 szam mutatta, hol
# tart a varakozas, azt viszont a sajat tablajarol nem latja az ember, mert a
# hüvelykujja alatt van.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:'#fff', lineHeight:1.1, textAlign:'center', padding:'0 12px', wordBreak:'break-word' }}>
          {player.name}
        </div>
        {!released && (
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:'rgba(255,255,255,0.85)', letterSpacing:'0.06em' }}>
            {phase === 'idle' ? 'TARTSD' : 'TARTSD!'}
          </div>
        )}
        {released && (
          <div style={{
            background:'rgba(0,0,0,0.22)', borderRadius:8, padding:'4px 14px',
            fontFamily:'monospace', fontWeight:900, fontSize:20, color:'#fff',
            letterSpacing:'0.04em',
          }}>
            {timeVal === -1 ? '✗ KÉSŐ' : `${(timeVal * 1000).toFixed(0)}ms`}
          </div>
        )}""",
    """        {/* Avatar + név balra zárva — a saját tábláját mindenki felismeri,
            anélkül hogy a nevet kellene elolvasnia. */}
        <div style={{ width:64, height:64, borderRadius:'50%', flexShrink:0, overflow:'hidden',
                      background:'rgba(255,255,255,0.28)', border:'3px solid rgba(255,255,255,0.9)',
                      display:'grid', placeItems:'center' }}>
          {player.img
            ? <img src={player.img} alt="" style={{ width:'100%', height:'100%', objectFit:'cover' }} />
            : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:26, color:'#fff' }}>{(player.name||'?').charAt(0).toUpperCase()}</span>}
        </div>
        <div style={{ flex:1, minWidth:0, display:'flex', flexDirection:'column', gap:5 }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:21, color:'#fff', lineHeight:1.1,
                        overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>
            {player.name}
          </div>
          {!released ? (
            <>
              <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:'rgba(255,255,255,0.85)', letterSpacing:'0.08em' }}>
                {phase === 'idle' ? 'TARTSD' : 'TARTSD!'}
              </div>
              {/* A visszaszamlalas allasa a sajat tablan: a kozepso szam a
                  hüvelykujj alatt van, onnan nem latszik. */}
              <div style={{ display:'flex', gap:6, marginTop:2 }}>
                {Array.from({ length: 10 }).map((_, i) => {
                  const done = phase === 'counting' && i < Math.round((1 - countdown / 5) * 10);
                  return <span key={i} style={{ width:9, height:9, borderRadius:'50%',
                    background:'#fff', opacity: done ? 0.95 : 0.32, transition:'opacity .12s' }} />;
                })}
              </div>
            </>
          ) : (
            <div style={{
              alignSelf:'flex-start', background:'rgba(0,0,0,0.22)', borderRadius:9, padding:'5px 14px',
              fontFamily:'monospace', fontWeight:900, fontSize:19, color:'#fff', letterSpacing:'0.04em',
            }}>
              {timeVal === -1 ? '✗ KÉSŐ' : `${(timeVal * 1000).toFixed(0)}ms`}
            </div>
          )}
        </div>""",
    'Btn tartalom')

# a tabla vizszintes elrendezes lesz
sub("""          width:'100%', height:110, borderRadius:18,
          background: released ? `${player.color}66` : player.color,""",
    """          width:'100%', minHeight:118, borderRadius:22, boxSizing:'border-box', padding:'14px 18px',
          background: released ? `${player.color}66` : player.color,""",
    'Btn doboz')
sub("""          display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:4,
          cursor:'pointer', userSelect:'none', WebkitUserSelect:'none', touchAction:'none',""",
    """          display:'flex', flexDirection:'row', alignItems:'center', gap:16,
          cursor:'pointer', userSelect:'none', WebkitUserSelect:'none', touchAction:'none',""",
    'Btn irany')

sub("const APP_VERSION = 'v10.196';", "const APP_VERSION = 'v10.197';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — Tapper tablak a mockup szerint')
