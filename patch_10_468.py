# v10.468 — Gender Reveal: a felirat a kiderült színen is, és „KISFIÚ VAGY KISLÁNY?" a visszaszámláláson
#  - a videó utáni átmenetben (outro) a pasztell szín és a konfetti fölött ott áll a „KISLÁNY!" / „KISFIÚ!"
#  - a szín ehhez tovább marad (2,8 → 5,5 mp, fele ideig teljesen), a felirat vele együtt halványul el
#  - a visszaszámlálás fejléce: „FIÚ VAGY LÁNY?" → „KISFIÚ VAGY KISLÁNY?"
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.467';", "const APP_VERSION = 'v10.468';")

rep("""<div style={{ fontFamily:T.font, fontWeight:800, fontSize:'clamp(16px, 3.4vh, 40px)', letterSpacing:'0.3em', color:'#2F63A8', textAlign:'center' }}>{show.test ? 'PRÓBA-LELEPLEZÉS' : 'FIÚ VAGY LÁNY?'}</div>""",
    """<div data-reveal-question style={{ fontFamily:T.font, fontWeight:800, fontSize:'clamp(16px, 3.4vh, 40px)', letterSpacing:'0.3em', color:'#2F63A8', textAlign:'center', padding:'0 4vw' }}>{show.test ? 'PRÓBA-LELEPLEZÉS' : 'KISFIÚ VAGY KISLÁNY?'}</div>""")

rep("""          <div data-reveal-outro aria-hidden="true" style={{ position:'absolute', inset:0, background:`radial-gradient(circle at 50% 50%, ${R.c2}, ${R.c1} 85%)`, animation:`revealOutroFade ${2.8 * sp}s ease-in-out both` }} />
          <RevealConfettiRain colors={[R.c1, R.c2, '#ffffff', '#FFD54F']} ms={REVEAL_OUTRO_MS * sp} />""",
"""          <div data-reveal-outro aria-hidden="true" style={{ position:'absolute', inset:0, background:`radial-gradient(circle at 50% 50%, ${R.c2}, ${R.c1} 85%)`, animation:`revealOutroFade ${REVEAL_OUTRO_HOLD * sp}s ease-in-out both` }} />
          <RevealConfettiRain colors={[R.c1, R.c2, '#ffffff', '#FFD54F']} ms={REVEAL_OUTRO_MS * sp} />
          {/* v10.468: a kiderült színen a felirat is ott áll — a színnel EGYÜTT halványul el */}
          <div style={{ position:'absolute', inset:0, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:'2vh', pointerEvents:'none', padding:'0 4vw',
            animation:`revealOutroFade ${REVEAL_OUTRO_HOLD * sp}s ease-in-out both` }}>
            <div style={{ fontSize:'min(16vh, 14vw)', animation:'revealPop .8s cubic-bezier(.3,1.6,.5,1) both' }}>{R.emoji}</div>
            <div data-reveal-outroword style={{ fontFamily:T.font, fontWeight:900, fontSize:'min(26vh, 13vw)', whiteSpace:'nowrap', lineHeight:0.95, color:'#fff', textShadow:`0 1.4vh 0 ${R.ink}55, 0 3vh 8vh rgba(0,0,0,0.3)`,
              animation:'revealSlam 1s cubic-bezier(.2,1.5,.4,1) both' }}>{R.word}</div>
          </div>""")

rep("const REVEAL_OUTRO_MS = 7000;      // ms — a feloldódás + konfetti-eső hossza a fal fölött",
    "const REVEAL_OUTRO_MS = 7000;      // ms — a feloldódás + konfetti-eső hossza a fal fölött\n"
    "const REVEAL_OUTRO_HOLD = 5.5;     // mp — v10.468: a szín + a „KISLÁNY!” felirat ennyi alatt oldódik fel (fele ideig teljesen áll)")
rep("@keyframes revealOutroFade { 0% { opacity:1 } 30% { opacity:1 } 100% { opacity:0 } }",
    "@keyframes revealOutroFade { 0% { opacity:1 } 50% { opacity:1 } 100% { opacity:0 } }")

open(P, 'w', encoding='utf-8').write(s)
print('ok')
