#!/usr/bin/env python3
# v10.199 — Igaz vagy Hamis: a mockup szerinti elrendezés
#
# Eddig a kartya mellett ket kis kor allt (✕ HAMIS / ✓ IGAZ), es a lap oldalain
# 52-52 px ment el rajuk — a kartya emiatt keskeny volt, a hosszabb allitasok
# ot sorba tordeltek. A terv szerint a kartya teljes szeles, a dontes pedig ket
# nagy gomb alatta.
#
# A huzas MEGMARAD: aki megszokta, tovabbra is huzhatja a kartyat. A gombok
# csak lathatova teszik, hogy egyaltalan van dontes — a kis korok mellett ez
# nem volt egyertelmu.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─── a kartya teljes szeles ───
sub("""      <div style={{ position:'relative', width:'100%', paddingLeft:52, paddingRight:52, boxSizing:'border-box' }}>

        {/* HAMIS indicator — left */}
        <div onClick={() => !decided && decide('hamis')} style={{ position:'absolute', left:0, top:'50%', transform:'translateY(-50%)', display:'flex', flexDirection:'column', alignItems:'center', gap:4, cursor: decided ? 'default' : 'pointer', zIndex:10 }}>
          <div style={{ width:42, height:42, borderRadius:'50%', border:`2.5px solid ${T.coral}`, display:'grid', placeItems:'center', background: (dragDir==='hamis'&&dragging) ? `${T.coral}${Math.round(swipeRatio*0.25*255).toString(16).padStart(2,'0')}` : decided==='hamis' ? `${T.coral}2e` : 'transparent', transition:'background .2s' }}>
            <span style={{ color:T.coral, fontWeight:900, fontSize:18, lineHeight:1 }}>✕</span>
          </div>
          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:T.coral, letterSpacing:'0.1em' }}>HAMIS</span>
        </div>

        {/* Card stack (2 background cards) */}""",
    """      <div style={{ position:'relative', width:'100%', boxSizing:'border-box' }}>

        {/* Card stack (2 background cards) */}""",
    'kartya szelesseg + bal jelzo')

sub("""        {/* IGAZ indicator — right */}
        <div onClick={() => !decided && decide('igaz')} style={{ position:'absolute', right:0, top:'50%', transform:'translateY(-50%)', display:'flex', flexDirection:'column', alignItems:'center', gap:4, cursor: decided ? 'default' : 'pointer', zIndex:10 }}>
          <div style={{ width:42, height:42, borderRadius:'50%', border:`2.5px solid ${T.mint}`, display:'grid', placeItems:'center', background: (dragDir==='igaz'&&dragging) ? `${T.mint}40` : decided==='igaz' ? `${T.mint}2e` : 'transparent', transition:'background .2s' }}>
            <span style={{ color:T.mint, fontWeight:900, fontSize:18 }}>✓</span>
          </div>
          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:T.mint, letterSpacing:'0.1em' }}>IGAZ</span>
        </div>
      </div>

    </div>
  );
}""",
    """      </div>

      {/* A dontes ket nagy gombon — a kis korok mellett nem volt egyertelmu,
          hogy egyaltalan donteni kell. A huzas emellett tovabbra is mukodik. */}
      <div style={{ display:'flex', gap:12, width:'100%' }}>
        {[{ k:'igaz', label:'IGAZ', tone:T.mint, mark:'✓' },
          { k:'hamis', label:'HAMIS', tone:T.coral, mark:'✕' }].map(b => (
          <button key={b.k} onClick={() => !decided && decide(b.k)} disabled={!!decided}
            style={{ flex:1, padding:'15px 0', borderRadius:16, border:'none',
                     background: decided && decided !== b.k ? b.tone+'55' : b.tone,
                     color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:16,
                     letterSpacing:'0.06em', cursor: decided ? 'default' : 'pointer',
                     display:'flex', alignItems:'center', justifyContent:'center', gap:9,
                     boxShadow:T.shadow, WebkitTapHighlightColor:'transparent' }}>
            <span style={{ fontSize:17, lineHeight:1 }}>{b.mark}</span>{b.label}
          </button>
        ))}
      </div>

    </div>
  );
}""",
    'jobb jelzo -> gombok')

# ─── a kartya tartalma: ÁLLÍTÁS felirat + korty-pirula ───
sub("""            {/* Statement */}
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:19, color:'#1A2A4A', textAlign:'center', lineHeight:1.45, marginTop:32 }}>
              {item.text}
            </div>""",
    """            {/* Statement */}
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:10, color:T.inkSoft, letterSpacing:1.6, marginTop:30 }}>ÁLLÍTÁS</div>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:19, color:'#1A2A4A', textAlign:'center', lineHeight:1.45, marginTop:14, padding:'0 16px' }}>
              {item.text}
            </div>
            {/* A tet a kartyan — eddig sehol nem latszott, hogy mennyi forog kockan */}
            {!decided && (
              <div style={{ display:'flex', alignItems:'center', gap:7, marginTop:18,
                            background:T.yellow+'26', borderRadius:999, padding:'6px 14px' }}>
                <BohIcon name="beer" size={15} />
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:T.yellowText||T.ink }}>1 KORTY</span>
              </div>
            )}""",
    'allitas + korty')

# a huzas-tipp mar felesleges: ott vannak a gombok
sub("""            {/* Swipe hint */}
            {!decided && (
              <div style={{ position:'absolute', bottom:16, fontFamily:T.font, fontSize:11, color:'rgba(0,0,0,0.22)', letterSpacing:'0.05em' }}>
                — húzd · döntsd el · húzd —
              </div>
            )}""",
    """            {/* Swipe hint — halkan, mert a gombok a fo ut */}
            {!decided && (
              <div style={{ position:'absolute', bottom:14, fontFamily:T.font, fontSize:10.5, color:'rgba(0,0,0,0.2)', letterSpacing:'0.05em' }}>
                húzhatod is
              </div>
            )}""",
    'huzas tipp')

sub("const APP_VERSION = 'v10.198';", "const APP_VERSION = 'v10.199';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — Igaz vagy Hamis a mockup szerint')
