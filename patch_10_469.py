# v10.469 — Gender Reveal Szülők: a leleplezés gombjai EGY sorban — nagy fő gomb + két kicsi (Most · Próba)
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.468';", "const APP_VERSION = 'v10.469';")
rep("${tab === 'reveal' ? 220 : 100}px)`", "${tab === 'reveal' ? 170 : 100}px)`")   # a gombsor egy sor lett

rep("""      <div data-reveal-firepanel data-armed={armed ? '1' : '0'} style={{ display:'flex', flexDirection:'column', gap:8, padding:'12px 16px 6px', maxWidth:520, margin:'0 auto', boxSizing:'border-box', borderBottom:`1px solid ${T.border}` }}>
        {!done && future && !armed && <button type="button" data-reveal-arm disabled={!ready} onClick={() => setAsk('arm')} style={rvBtn('primary', ready ? null : { opacity:0.45, cursor:'default' })}>Engedélyezem a leleplezést</button>}
        {(done || !future) && <button type="button" data-reveal-fire disabled={!ready} onClick={() => setAsk('now')} style={rvBtn('primary', ready ? null : { opacity:0.45, cursor:'default' })}>{done ? 'Leleplezés újra' : 'Leleplezés indítása'}</button>}
        <div style={{ display:'flex', gap:8 }}>
          {!done && armed && <button type="button" data-reveal-disarm onClick={disarm} style={rvBtn('secondary', { flex:1 })}>Engedély visszavonása</button>}
          {!done && future && <button type="button" data-reveal-fire disabled={!ready} onClick={() => setAsk('now')} style={rvBtn('secondary', { flex:1, color: ready ? T.ink : T.inkMute })}>Leleplezés most</button>}
          <button type="button" data-reveal-test onClick={() => fire(true)} style={rvBtn('secondary', { flex:1 })}>Próba</button>
        </div>""",
"""      // v10.469: EGY sor — balra a nagy fő gomb (engedélyezés / visszavonás / indítás), mellette két kicsi: Most · Próba
      <div data-reveal-firepanel data-armed={armed ? '1' : '0'} style={{ display:'flex', flexDirection:'column', gap:8, padding:'12px 16px 6px', maxWidth:520, margin:'0 auto', boxSizing:'border-box', borderBottom:`1px solid ${T.border}` }}>
        <div data-reveal-firerow style={{ display:'flex', gap:8, alignItems:'stretch' }}>
          {!done && future && !armed && <button type="button" data-reveal-arm disabled={!ready} onClick={() => setAsk('arm')} style={rvBtn('primary', Object.assign({ flex:1, minWidth:0, padding:'0 12px', lineHeight:1.15, textAlign:'center' }, ready ? null : { opacity:0.45, cursor:'default' }))}>Engedélyezem a leleplezést</button>}
          {!done && future && armed && <button type="button" data-reveal-disarm onClick={disarm} style={rvBtn('secondary', { flex:1, minWidth:0, height:56, padding:'0 12px', lineHeight:1.15, textAlign:'center', fontSize:15 })}>Engedély visszavonása</button>}
          {(done || !future) && <button type="button" data-reveal-fire disabled={!ready} onClick={() => setAsk('now')} style={rvBtn('primary', Object.assign({ flex:1, minWidth:0, padding:'0 12px', lineHeight:1.15, textAlign:'center' }, ready ? null : { opacity:0.45, cursor:'default' }))}>{done ? 'Leleplezés újra' : 'Leleplezés indítása'}</button>}
          {!done && future && <button type="button" data-reveal-fire disabled={!ready} aria-label="Leleplezés most" onClick={() => setAsk('now')} style={rvBtn('secondary', { flexShrink:0, width:76, height:56, color: ready ? T.ink : T.inkMute })}>Most</button>}
          <button type="button" data-reveal-test aria-label="Próba-leleplezés" onClick={() => fire(true)} style={rvBtn('secondary', { flexShrink:0, width:76, height:56 })}>Próba</button>
        </div>""")

open(P, 'w', encoding='utf-8').write(s)
print('ok')
