#!/usr/bin/env python3
# v10.281 — a korty-oszto gombja eltunik kiosztas utan, es a lista a modallal
#           azonos szelessegu
#
# 1. A GOMB ELTUNIK, ES A SOROK LEZARNAK
#    Eddig a zaro gomb kiosztas utan is ott maradt, es ujra megnyomhato volt:
#    ujra lefutott az `onResult` (a banner megint felugrott) es az `onAdvance`.
#    Most a gomb eltunik, a sorok pedig lezarnak — mert a kiosztas utani
#    modositas UGYIS nem szamitana, es egy szerkesztheto sor ezt hazudna.
#    Helyette egy halk visszaigazolas all ott, hogy a Kovi gomb kovetkezik.
#
#    A tobbkoros jatekoknal (Fingerit, Meduza) a kioszto ket kor kozott
#    lecsatolodik, tehat az allapot magatol nullazodik — ezt megnezve
#    ellenoriztem. A `resetKey` ettol fuggetlenul ott van biztonsagi kotelnek:
#    ha valamelyik jatek egyszer mégis mountolva tartana, a kor valtasakor
#    nullazodik. Alapja a `title`, ami a tobbkoros jatekoknal korönkent valtozik.
#
# 2. AZONOS SZELESSEG A MODALLAL
#    A sor MAGASSAGA mar azonos volt (48 px, merve), a SZELESSEGE nem: a modal
#    340 px-es kartyaja 18 px oldalpaddinggal 304 px tartalmat ad, a jatekban
#    viszont a lista a teljes kepernyot hasznalta (354 px). Most kozos konstans.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""const DRINK_ROW_H = 48, DRINK_ROW_GAP = 8, DRINK_ROWS_VISIBLE = 5;
const DRINK_LIST_MAX = DRINK_ROWS_VISIBLE * DRINK_ROW_H + (DRINK_ROWS_VISIBLE - 1) * DRINK_ROW_GAP;""",
    """const DRINK_ROW_H = 48, DRINK_ROW_GAP = 8, DRINK_ROWS_VISIBLE = 5;
const DRINK_LIST_MAX = DRINK_ROWS_VISIBLE * DRINK_ROW_H + (DRINK_ROWS_VISIBLE - 1) * DRINK_ROW_GAP;
// A modal kartyaja 340 px szeles, 18 px oldalpaddinggal -> 304 px tartalom.
// A jatekon beluli lista is ennyi, kulonben a sor ugyanolyan MAGAS lenne, de
// szelesebb — es pont az egyseges felulet veszne el.
const DRINK_LIST_W = 304;""",
    'szelesseg konstans')

sub("""function DrinkDistributor({ players, onFinish, title, max }) {
  const [drinks, setDrinks] = React.useState({});""",
    """function DrinkDistributor({ players, onFinish, title, max, resetKey }) {
  const [drinks, setDrinks] = React.useState({});
  // Kiosztas utan a gomb eltunik es a sorok lezarnak. Biztonsagi kotel: a
  // tobbkoros jatekoknal a kioszto ket kor kozott lecsatolodik (ellenorizve),
  // de ha valamelyik egyszer mountolva tartana, a `resetKey` valtasa nullaz.
  const [kesz, setKesz] = React.useState(false);
  React.useEffect(() => { setKesz(false); setDrinks({}); }, [resetKey != null ? resetKey : title]);""",
    'kesz allapot')

sub("""    <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:8 }}>
      {title && (
        <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.08em' }}>{title}</div>
      )}
      <div style={{ display:'flex', flexDirection:'column', gap:DRINK_ROW_GAP, maxHeight:DRINK_LIST_MAX, overflowY:'auto' }}>
        {players.map(p => (
          <PlayerDrinkRow key={p.id} p={p} cnt={drinks[p.id]||0} onAdd={add} onRemove={remove} max={max} />
        ))}
      </div>
      <button onClick={()=>onFinish(drinks)} style={{ width:'100%', padding:'13px', background: total>0 ? T.mint : T.surfaceMuted, color: total>0 ? '#fff' : T.inkSoft, fontFamily:T.font, fontWeight:900, fontSize:15, borderRadius:16, border:'none', cursor:'pointer', boxShadow: total>0 ? '0 4px 14px -4px rgba(79,194,160,0.6)' : 'none', marginTop:2 }}>
        {total>0 ? (max === 1 ? `${fo} iszik · ${total} korty` : `${total} korty kiosztva`) : 'Senki sem iszik'}
      </button>
    </div>""",
    """    <div style={{ width:'100%', maxWidth:DRINK_LIST_W, margin:'0 auto', display:'flex', flexDirection:'column', gap:8 }}>
      {title && (
        <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.08em' }}>{title}</div>
      )}
      <div style={{ display:'flex', flexDirection:'column', gap:DRINK_ROW_GAP, maxHeight:DRINK_LIST_MAX, overflowY:'auto',
                    opacity: kesz ? 0.55 : 1, pointerEvents: kesz ? 'none' : undefined, transition:'opacity .2s' }}>
        {players.map(p => (
          <PlayerDrinkRow key={p.id} p={p} cnt={drinks[p.id]||0} onAdd={add} onRemove={remove} max={max} />
        ))}
      </div>
      {kesz ? (
        <div style={{ textAlign:'center', padding:'13px 0 2px', fontFamily:T.font, fontWeight:800, fontSize:13,
                      color:T.inkMute, animation:'bohFadeIn .18s' }}>
          {total>0 ? `${total} korty kiosztva` : 'Senki nem ivott'} — jöhet a Kövi
        </div>
      ) : (
        <button onClick={()=>{ setKesz(true); onFinish(drinks); }} style={{ width:'100%', padding:'13px', background: total>0 ? T.mint : T.surfaceMuted, color: total>0 ? '#fff' : T.inkSoft, fontFamily:T.font, fontWeight:900, fontSize:15, borderRadius:16, border:'none', cursor:'pointer', boxShadow: total>0 ? '0 4px 14px -4px rgba(79,194,160,0.6)' : 'none', marginTop:2 }}>
          {total>0 ? (max === 1 ? `${fo} iszik · ${total} korty` : `${total} korty kiosztva`) : 'Senki sem iszik'}
        </button>
      )}
    </div>""",
    'gomb eltunes + szelesseg')

sub("const APP_VERSION = 'v10.280';", "const APP_VERSION = 'v10.281';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — gomb eltunik, lista 304 px')
