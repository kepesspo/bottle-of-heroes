#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Wildcard UI "B" variáns: krém kártyalap kemény navy kontúrral (playful stílus)
# a gradient helyett — popup kártya, kör alatti sáv, szabályszegő-választó.
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'expected %d, found %d for: %r' % (count, n, old[:90])
    src = src.replace(old, new)

# 1) i18n: kártya-emoji ki a labelből (a pill maga adja a stílust)
rep("    wildcardRound: '🃏 WILDCARD KÖR',", "    wildcardRound: 'WILDCARD KÖR',")
rep("    wildcardRound: '🃏 WILDCARD ROUND',", "    wildcardRound: 'WILDCARD ROUND',")

# 2) Popup kártya
rep("""                <div style={{ background:'linear-gradient(135deg,#FFE066,#FF6B35)', borderRadius:24, padding:'20px 24px', boxShadow:'0 8px 40px rgba(0,0,0,0.4), 0 0 0 3px rgba(255,255,255,0.2)', border:'2px dashed rgba(255,255,255,0.5)', position:'relative', overflow:'visible' }}>
                  {/* Floating drink icons around card */}
                  <div style={{ position:'absolute', top:-16, left:-10, fontSize:24, animation:'floatBob 2.0s 0.1s ease-in-out infinite', pointerEvents:'none' }}>🍹</div>
                  <div style={{ position:'absolute', top:-14, right:-8, fontSize:22, animation:'floatBob 1.8s 0.45s ease-in-out infinite', pointerEvents:'none' }}>🥃</div>
                  <div style={{position:'absolute', bottom:-12, left:10, animation:'floatBob 2.2s 0.3s ease-in-out infinite', pointerEvents:'none'}}><BohIcon name="beer" size={18} /></div>
                  <div style={{ position:'absolute', bottom:-10, right:14, fontSize:18, animation:'floatBob 1.9s 0.65s ease-in-out infinite', pointerEvents:'none' }}>🥂</div>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:'rgba(0,0,0,0.5)', textTransform:'uppercase', letterSpacing:'0.18em', marginBottom:10 }}>{t('wildcardRound')}</div>
                  <div style={{ fontSize:48, marginBottom:12, animation:'wobble 2.5s ease-in-out infinite' }}>{roundPopup.wildcard.emoji}</div>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:'#1A0A00', lineHeight:1.4 }}>{roundPopup.wildcard.text}</div>
                </div>
                <div style={{ marginTop:14, fontFamily:T.font, fontSize:13, fontWeight:700, color:'rgba(255,255,255,0.7)', background:'rgba(255,255,255,0.12)', borderRadius:20, padding:'8px 20px', display:'inline-block' }}>{t('tapToContinue')}</div>""",
"""                <div style={{ background:T.surfaceMuted, border:`2.5px solid ${T.ink}`, borderRadius:24, padding:'22px 22px 24px', boxShadow:`0 6px 0 ${T.ink}`, position:'relative', overflow:'visible' }}>
                  <div style={{ position:'absolute', top:10, left:14, fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink, lineHeight:1, pointerEvents:'none' }}>♦</div>
                  <div style={{ position:'absolute', bottom:10, right:14, fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink, lineHeight:1, transform:'rotate(180deg)', pointerEvents:'none' }}>♦</div>
                  <div style={{ display:'inline-block', fontFamily:T.font, fontWeight:900, fontSize:11, color:T.ink, textTransform:'uppercase', letterSpacing:'0.16em', background:T.yellow, border:`2px solid ${T.ink}`, borderRadius:999, padding:'5px 12px' }}>{t('wildcardRound')}</div>
                  <div style={{ fontSize:42, margin:'14px 0 10px', animation:'wobble 2.5s ease-in-out infinite' }}>{roundPopup.wildcard.emoji}</div>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, lineHeight:1.35 }}>{roundPopup.wildcard.text}</div>
                </div>
                <div style={{ marginTop:14, fontFamily:T.font, fontSize:13, fontWeight:700, color:'rgba(255,255,255,0.8)', background:'rgba(26,42,74,0.35)', borderRadius:20, padding:'8px 20px', display:'inline-block' }}>{t('tapToContinue')}</div>""")

# 3) Kör alatti sáv
rep("""          <div style={{ display:'flex', alignItems:'center', gap:10, background:'linear-gradient(135deg,#FFE066,#FF6B35)', borderRadius:14, padding:'8px 12px', boxShadow:'0 3px 12px rgba(255,107,53,0.35)', animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)' }}>
            <span style={{ fontSize:22, flexShrink:0, lineHeight:1 }}>{activeWildcard.emoji}</span>
            <div onClick={() => setRoundPopup({ round: activeWildcard.round, wildcard: activeWildcard, showRound: false, leaving: false })} style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:800, fontSize:12, lineHeight:1.3, color:'#1A0A00', display:'-webkit-box', WebkitLineClamp:2, WebkitBoxOrient:'vertical', overflow:'hidden', cursor:'pointer' }}>{activeWildcard.text}</div>
            <button onClick={() => setWcPunishOpen(true)} style={{ flexShrink:0, border:'none', borderRadius:10, background:'rgba(26,10,0,0.82)', color:'#FFE066', fontFamily:T.font, fontWeight:900, fontSize:11.5, padding:'8px 10px', cursor:'pointer', display:'flex', alignItems:'center', gap:5 }}>
              <BohIcon name="beer" size={13} />Szabályszegő?
            </button>
          </div>""",
"""          <div style={{ display:'flex', alignItems:'center', gap:10, background:T.surfaceMuted, border:`2px solid ${T.ink}`, borderRadius:14, padding:'7px 12px', boxShadow:`0 3px 0 ${T.ink}`, animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)' }}>
            <span style={{ fontSize:22, flexShrink:0, lineHeight:1 }}>{activeWildcard.emoji}</span>
            <div onClick={() => setRoundPopup({ round: activeWildcard.round, wildcard: activeWildcard, showRound: false, leaving: false })} style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:800, fontSize:12, lineHeight:1.3, color:T.ink, display:'-webkit-box', WebkitLineClamp:2, WebkitBoxOrient:'vertical', overflow:'hidden', cursor:'pointer' }}>{activeWildcard.text}</div>
            <button onClick={() => setWcPunishOpen(true)} style={{ flexShrink:0, border:`2px solid ${T.ink}`, borderRadius:10, background:T.yellow, color:T.ink, fontFamily:T.font, fontWeight:900, fontSize:11.5, padding:'6px 10px', cursor:'pointer', display:'flex', alignItems:'center', gap:5 }}>
              <BohIcon name="beer" size={13} />Szabályszegő?
            </button>
          </div>""")

# 4) Szabályszegő-választó ugyanebben a stílusban
rep("""          <div onClick={e => e.stopPropagation()} style={{ background:T.surface, borderRadius:28, padding:'26px 22px 22px', width:'100%', maxWidth:340, boxShadow:'0 24px 64px rgba(0,0,0,0.3)', animation:'popIn .3s cubic-bezier(.2,.9,.3,1.3)' }}>""",
"""          <div onClick={e => e.stopPropagation()} style={{ background:T.surfaceMuted, border:`2.5px solid ${T.ink}`, borderRadius:24, padding:'26px 22px 22px', width:'100%', maxWidth:340, boxShadow:`0 6px 0 ${T.ink}`, animation:'popIn .3s cubic-bezier(.2,.9,.3,1.3)' }}>""")
rep("""                <button key={p.id} onClick={() => punishWildcard(p.id)} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 14px', borderRadius:14, border:'none', background:T.surfaceMuted, cursor:'pointer', textAlign:'left' }}>""",
"""                <button key={p.id} onClick={() => punishWildcard(p.id)} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 14px', borderRadius:14, border:`2px solid ${T.ink}`, background:T.surface, boxShadow:`0 2px 0 ${T.ink}`, cursor:'pointer', textAlign:'left' }}>""")
rep("""            <button onClick={() => setWcPunishOpen(false)} style={{ width:'100%', marginTop:12, padding:'12px 0', borderRadius:14, border:'none', background:T.surfaceMuted, color:T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:14, cursor:'pointer' }}>Mégse</button>""",
"""            <button onClick={() => setWcPunishOpen(false)} style={{ width:'100%', marginTop:12, padding:'12px 0', borderRadius:14, border:`2px solid ${T.ink}55`, background:'transparent', color:T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:14, cursor:'pointer' }}>Mégse</button>""")

# 5) Verziobump
rep("const APP_VERSION = 'v9.953';", "const APP_VERSION = 'v9.954';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — wildcard B design applied')
