# v10.470 — Gender Reveal Szülők: „A nagy pillanatig" kártya fele akkora magas — egy sor:
#  balra a felirat + egy rövid mondat, jobbra a visszaszámláló
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.469';", "const APP_VERSION = 'v10.470';")

rep("""  const big = t => <div style={{ position:'relative', fontFamily:T.font, fontWeight:900, fontSize:34, lineHeight:1.05, marginTop:8 }}>{t}</div>;""",
    """  const big = t => <div style={{ position:'relative', fontFamily:T.font, fontWeight:900, fontSize:20, lineHeight:1.1, textAlign:'right' }}>{t}</div>;""")

rep("""      <section data-reveal-phero style={{ position:'relative', overflow:'hidden', borderRadius:20, padding:'14px 18px', background:REVEAL_NIGHT, color:'#fff', flexShrink:0 }}>
        <div aria-hidden="true" style={{ position:'absolute', right:-30, top:-30, width:120, height:120, borderRadius:'50%', background:REVEAL_PINK, opacity:0.35 }} />
        <div aria-hidden="true" style={{ position:'absolute', right:40, bottom:-50, width:110, height:110, borderRadius:'50%', background:REVEAL_BLUE, opacity:0.3 }} />
        <div style={{ position:'relative', fontFamily:T.font, fontSize:11, fontWeight:900, letterSpacing:'0.16em', opacity:0.75 }}>{done ? 'KIDERÜLT' : 'A NAGY PILLANATIG'}</div>
        {done ? big('Leleplezve!') : future ? (
          <div data-reveal-pcount style={{ position:'relative', display:'flex', alignItems:'flex-end', gap:12, marginTop:8 }}>
            {parts.map(([n, u], i) => (
              <React.Fragment key={u}>
                {i > 0 && <span style={{ fontFamily:T.font, fontSize:30, fontWeight:900, opacity:0.5, paddingBottom:18 }}>:</span>}
                <div style={{ display:'flex', flexDirection:'column', alignItems:'center' }}>
                  <span style={{ fontFamily:T.font, fontSize:38, fontWeight:900, lineHeight:1, fontVariantNumeric:'tabular-nums' }}>{n}</span>
                  <span style={{ fontFamily:T.font, fontSize:11, fontWeight:800, opacity:0.7, marginTop:4 }}>{u}</span>
                </div>
              </React.Fragment>
            ))}
          </div>
        ) : big(revealAt ? (armed ? 'Most indul!' : 'Elérkezett az idő') : 'Nincs időpont')}
        <div style={{ position:'relative', fontFamily:T.font, fontSize:12.5, fontWeight:700, opacity:0.85, marginTop:8, lineHeight:1.4 }}>
          {done ? 'A vetítőn újra lejátszhatjátok.' : armed ? 'Engedélyezve — a vetítő az időpontra magától indul.' : 'A vetítő mutatja meg mindenkinek egyszerre.'}
        </div>
      </section>""",
"""      {/* v10.470: fele akkora — EGY sor: balra a felirat + rövid mondat, jobbra a visszaszámláló */}
      <section data-reveal-phero style={{ position:'relative', overflow:'hidden', borderRadius:16, padding:'10px 16px', background:REVEAL_NIGHT, color:'#fff', flexShrink:0, display:'flex', alignItems:'center', gap:12 }}>
        <div aria-hidden="true" style={{ position:'absolute', right:-30, top:-40, width:76, height:76, borderRadius:'50%', background:REVEAL_PINK, opacity:0.25 }} />
        <div aria-hidden="true" style={{ position:'absolute', left:'42%', bottom:-46, width:64, height:64, borderRadius:'50%', background:REVEAL_BLUE, opacity:0.25 }} />
        <div style={{ position:'relative', flex:1, minWidth:0 }}>
          <div style={{ fontFamily:T.font, fontSize:10.5, fontWeight:900, letterSpacing:'0.14em', opacity:0.75, whiteSpace:'nowrap' }}>{done ? 'KIDERÜLT' : 'A NAGY PILLANATIG'}</div>
          <div style={{ fontFamily:T.font, fontSize:12, fontWeight:700, opacity:0.85, marginTop:3, lineHeight:1.3 }}>
            {done ? 'A vetítőn újra lejátszható.' : armed ? 'Engedélyezve · magától indul.' : 'A vetítő mutatja meg.'}
          </div>
        </div>
        {done ? big('Leleplezve!') : future ? (
          <div data-reveal-pcount style={{ position:'relative', display:'flex', alignItems:'flex-start', gap:4, flexShrink:0 }}>
            {parts.map(([n, u], i) => (
              <React.Fragment key={u}>
                {i > 0 && <span style={{ fontFamily:T.font, fontSize:22, fontWeight:900, lineHeight:1, opacity:0.5 }}>:</span>}
                <div style={{ display:'flex', flexDirection:'column', alignItems:'center', minWidth:30 }}>
                  <span style={{ fontFamily:T.font, fontSize:24, fontWeight:900, lineHeight:1, fontVariantNumeric:'tabular-nums' }}>{n}</span>
                  <span style={{ fontFamily:T.font, fontSize:9.5, fontWeight:800, opacity:0.7, marginTop:2 }}>{u}</span>
                </div>
              </React.Fragment>
            ))}
          </div>
        ) : big(revealAt ? (armed ? 'Most indul!' : 'Elérkezett az idő') : 'Nincs időpont')}
      </section>""")

open(P, 'w', encoding='utf-8').write(s)
print('ok')
