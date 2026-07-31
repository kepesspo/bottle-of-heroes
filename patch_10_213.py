#!/usr/bin/env python3
# v10.213 — a T.shadow "osszefolyik" szomszedos, szorosan pakolt soroknal
#
# A T.shadow a NAGY kartyakra van hangolva (5px tomor szel + 12px-re tolt,
# 28px szorasu lagy reteg). Ha ezt kis, szorosan (gap 8px) egymas ala
# rakott soron hasznaljuk, a szomszedos sorok szort arnyeka atlog egymasba
# — pontosan ez lathato a Kviz valaszai kozott (lasd a kepernyokepet) es
# ugyanigy a Buntetes-listaban is.
#
# A T.shadowPill EPP EZT a helyzetet celozza — mar a definiciojanal ott
# a megjegyzes: "Kis elemen [a T.shadow] elszakad a gombtol, es a
# szomszedok szort arnyeka egy savva folyik ossze". Csak eddig nem
# hasznaltuk mindenhol, ahol kellett volna.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─── Kviz valaszsorok ───
sub("""                boxShadow:isResultOrBank?'none':T.shadow,""",
    """                boxShadow:isResultOrBank?'none':T.shadowPill,""",
    'Kviz valaszsorok')

# ─── DrinkDistributor jatekos-sorok ───
sub("""          <div key={p.id} style={{ display:'flex', alignItems:'center', gap:8, padding:'7px 10px', background:T.surface, borderRadius:12, boxShadow:T.shadow }}>
            <PlayerAvatar player={p} size={30} />
            <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:13, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
            <div style={{ display:'flex', alignItems:'center', gap:5, flexShrink:0 }}>
              <button onClick={()=>remove(p.id)} disabled={cnt===0}
                style={{ width:26, height:26, borderRadius:7, border:'none', background:cnt>0?T.surfaceMuted:T.surfaceMuted, color:cnt>0?T.inkSoft:T.inkMute, fontFamily:T.font, fontSize:16, fontWeight:700, cursor:cnt>0?'pointer':'default' }}>−</button>
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:cnt>0?T.coral:T.inkMute, minWidth:26, textAlign:'center' }}>{cnt>0?<React.Fragment>{cnt} <BohIcon name="beer" size={12} /></React.Fragment>:'–'}</span>
              <button onClick={(e)=>{ add(p.id); if (window.bohFloat) window.bohFloat(e.currentTarget, `+${(drinks[p.id]||0)+1} 🍺`, T.coral); }}
                style={{ width:26, height:26, borderRadius:7, border:'none', background:T.coral+'22', color:T.coral, fontFamily:T.font, fontSize:16, fontWeight:700, cursor:'pointer' }}>+</button>
            </div>
          </div>""",
    """          <div key={p.id} style={{ display:'flex', alignItems:'center', gap:8, padding:'7px 10px', background:T.surface, borderRadius:12, boxShadow:T.shadowPill }}>
            <PlayerAvatar player={p} size={30} />
            <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:13, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
            <div style={{ display:'flex', alignItems:'center', gap:5, flexShrink:0 }}>
              <button onClick={()=>remove(p.id)} disabled={cnt===0}
                style={{ width:26, height:26, borderRadius:7, border:'none', background:cnt>0?T.surfaceMuted:T.surfaceMuted, color:cnt>0?T.inkSoft:T.inkMute, fontFamily:T.font, fontSize:16, fontWeight:700, cursor:cnt>0?'pointer':'default' }}>−</button>
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:cnt>0?T.coral:T.inkMute, minWidth:26, textAlign:'center' }}>{cnt>0?<React.Fragment>{cnt} <BohIcon name="beer" size={12} /></React.Fragment>:'–'}</span>
              <button onClick={(e)=>{ add(p.id); if (window.bohFloat) window.bohFloat(e.currentTarget, `+${(drinks[p.id]||0)+1} 🍺`, T.coral); }}
                style={{ width:26, height:26, borderRadius:7, border:'none', background:T.coral+'22', color:T.coral, fontFamily:T.font, fontSize:16, fontWeight:700, cursor:'pointer' }}>+</button>
            </div>
          </div>""",
    'DrinkDistributor sorok')

# ─── PenaltySheet jatekos-sorok ───
sub("""              <div key={p.id} style={{ display:'flex', alignItems:'center', gap:8, padding:'7px 10px', background:T.surface, borderRadius:12, boxShadow:T.shadow }}>""",
    """              <div key={p.id} style={{ display:'flex', alignItems:'center', gap:8, padding:'7px 10px', background:T.surface, borderRadius:12, boxShadow:T.shadowPill }}>""",
    'PenaltySheet sorok')

sub("const APP_VERSION = 'v10.212';", "const APP_VERSION = 'v10.213';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — T.shadow -> T.shadowPill a szorosan pakolt sorokon')
