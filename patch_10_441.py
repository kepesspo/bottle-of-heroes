# v10.441 — Gender Reveal operátor: egy képernyőre fér (telefonon nincs függőleges görgetés).
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:120]); s = s.replace(old, new)

rep("const APP_VERSION = 'v10.440'", "const APP_VERSION = 'v10.441'")
# a feltöltő gomb: vékony, egysoros (ikon a felirat mellett, nem fölötte)
rep("""  const bigBtn = (primary) => ({ flex:1, minWidth:0, padding:'18px 10px', borderRadius:18, border: primary ? 'none' : `2px solid ${T.mint}`, cursor:'pointer',
    background: primary ? T.mint : T.surface, color: primary ? '#fff' : T.mint, fontFamily:T.font, fontWeight:900, fontSize:16, display:'flex', flexDirection:'column', alignItems:'center', gap:6 });""",
"""  const bigBtn = (primary) => ({ flex:1, minWidth:0, padding:'13px 10px', borderRadius:16, border: primary ? 'none' : `2px solid ${T.mint}`, cursor:'pointer',
    background: primary ? T.mint : T.surface, color: primary ? '#fff' : T.mint, fontFamily:T.font, fontWeight:900, fontSize:16, display:'flex', flexDirection:'row', alignItems:'center', justifyContent:'center', gap:10 });""")
rep("""style={bigBtn(true)}><span style={{ fontSize:28 }}>🖼️</span>Képek feltöltése</button>""",
    """style={bigBtn(true)}><span style={{ fontSize:22, lineHeight:1 }}>🖼️</span>Képek feltöltése</button>""")
# ⚠️ v10.441: egy képernyő. A görgő terület oszlop-flex, a belső oszlop legalább
# akkora, mint ő (flex '1 0 auto'), és a lapozó a maradékot kapja — a kép magassága a
# kijelzőhöz igazodik (nem fix 46vh), így a tipp-gombok és a ‹ › mindig látszanak.
# Ha mégsem fér ki (hosszú „Jóváhagyásra vár" lista), görget — a lapozó min. 360 px.
rep("""      <div style={{ flex:1, overflowY:'auto', padding:'16px 16px calc(24px + env(safe-area-inset-bottom))', WebkitOverflowScrolling:'touch' }}>
        <div style={{ maxWidth:720, margin:'0 auto', display:'flex', flexDirection:'column', gap:14 }}>
          <div style={{ display:'flex', gap:10 }}>
            <button data-reveal-pick""",
"""      <div data-reveal-opscroll style={{ flex:1, minHeight:0, overflowY:'auto', display:'flex', flexDirection:'column', padding:'12px 16px calc(12px + env(safe-area-inset-bottom))', boxSizing:'border-box', WebkitOverflowScrolling:'touch' }}>
        <div style={{ flex:'1 0 auto', width:'100%', maxWidth:720, margin:'0 auto', display:'flex', flexDirection:'column', gap:10 }}>
          <div style={{ display:'flex', gap:10 }}>
            <button data-reveal-pick""")
rep("""          <div style={{ display:'flex', alignItems:'baseline', justifyContent:'space-between', marginTop:4 }}>""",
    """          <div style={{ display:'flex', alignItems:'baseline', justifyContent:'space-between' }}>""")
rep("""            <div data-reveal-slider style={{ display:'flex', flexDirection:'column', gap:10 }}>""",
    """            <div data-reveal-slider style={{ flex:'1 1 0', minHeight:360, display:'flex', flexDirection:'column', gap:8 }}>""")
rep("""                style={{ display:'flex', overflowX:'auto', overflowY:'hidden', scrollSnapType:'x mandatory', WebkitOverflowScrolling:'touch', scrollbarWidth:'none', margin:'0 -4px' }}>""",
    """                style={{ flex:'1 1 0', minHeight:0, display:'flex', alignItems:'stretch', overflowX:'auto', overflowY:'hidden', scrollSnapType:'x mandatory', WebkitOverflowScrolling:'touch', scrollbarWidth:'none', margin:'0 -4px' }}>""")
rep("""data-idx={i} style={{ flex:'0 0 100%', boxSizing:'border-box', padding:'0 4px', scrollSnapAlign:'center' }}>
                    <div style={{ borderRadius:18, overflow:'hidden', background:T.surface, boxShadow:T.shadow }}>""",
    """data-idx={i} style={{ flex:'0 0 100%', boxSizing:'border-box', padding:'0 4px 6px', scrollSnapAlign:'center', display:'flex' }}>
                    <div style={{ flex:1, minWidth:0, display:'flex', flexDirection:'column', borderRadius:18, overflow:'hidden', background:T.surface, boxShadow:T.shadow }}>""")
rep("""<div data-reveal-slidehead style={{ display:'flex', alignItems:'center', gap:8, padding:'10px 12px' }}>""",
    """<div data-reveal-slidehead style={{ flexShrink:0, display:'flex', alignItems:'center', gap:8, padding:'8px 12px' }}>""")
rep("""                      <div style={{ position:'relative', height:'clamp(220px, 46vh, 460px)', background:T.bg }}>""",
    """                      <div data-reveal-slideimg style={{ position:'relative', flex:'1 1 0', minHeight:120, background:T.bg }}>""")
open(P, 'w', encoding='utf-8').write(s); print('ok')
