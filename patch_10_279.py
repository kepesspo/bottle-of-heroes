#!/usr/bin/env python3
# v10.279 — Én még soha: redesign + a korty-osztó felület egységesítése
#
# A FO PANASZ
#   "Teljesen elter a drink ado felulet. Hasznaljuk a jatekon belul amit mar
#   most letrehoztunk." — a `DrinkDistributor` semmiben nem kovette a
#   `PenaltyModal`-t, amit a v10.272-273-ban egysegesitettunk.
#
# 1. KOZOS SOR: `PlayerDrinkRow`
#    Egy komponens, ket vezerlovel:
#      * 'stepper' — `− [n 🍺] +`  (Buntetes, Ko-papir, Meduza, Zene)
#      * 'toggle'  — NEM / IGEN     (binaris jatek: En meg soha)
#    A sor merete, hattere, avatarja mostantol EGY helyen van definialva, tehat
#    nem tud ujra szetcsuszni. A `PenaltyModal` es a `DrinkDistributor` is ezt
#    hasznalja.
#
# 2. A `DrinkDistributor` megkapja, amit a modal mar tud
#    * legfeljebb 5 sor latszik, onnantol gorget (ugyanaz a 272 px)
#    * a zaro gomb IGY MINDIG a lathato reszen marad — merve: 10 jatekosnal
#      eddig 940 px-nel volt egy 874 px-es kepernyon, tehat kicsuszott
#    * lekerult a pipa a gombrol (a modalrol a v10.273-ban mar levettuk)
#
# 3. EN MEG SOHA — redesign (az "A" valtozat)
#    * a duplan feltett kerdes megszunt: eddig a kepernyo teteje "En meg soha —
#      igaz rad?"-ot irt, a kartya meg "En meg soha nem…"-et. Most csak a kartyan
#      van, a felette levo sor a KOR feladatat mondja.
#    * a kartya alol kikerult az 5 vonasos "fuszer-csik": ugyanazt kodolta, mint
#      a bal felso "🌶 ALAP" jelveny, ES ugy nezett ki, mint egy "2. lap az
#      5-bol" haladasjelzo.
#    * a kartya 219 -> 168 px, hogy a lista is kiferjen a gombbal egyutt
#    * a sorokban KAPCSOLO: az "En meg soha" igaz/hamis kerdes, tehat egy
#      koppintas eleg, nem `+` majd zaras. (A leptetos valtozat egy propnyira
#      van, ha valamikor tort korty kell.)
#
# 4. A PAKLI VEGRE MEG VAN KEVERVE  ← a legnagyobb nyereseg
#    Eddig: `SOHANEM_CARDS[gameIdx % 207]`. A kartya tisztan abbol kovetkezett,
#    hogy hanyadik jatek jon — se keveres, se veletlen kezdopont. Ket kovetkezmeny:
#      * MINDEN parti ugyanazzal a lappal indult (01/207),
#      * egy buli 20-40 jatekot jatszik le, tehat csak az 1-40. lap kerult elo:
#        a 207-bol ~167 gyakorlatilag elerhetetlen volt.
#    Most partinkent sajat, seedelt keveres megy (ugyanaz a xorshift, mint a
#    Collect tablajanal), es a kijelzo a KEVERT pakliban elfoglalt helyet mutatja.
#
# 5. A BANNER KIIRJA A SZAMOT, HA MINDENKI UGYANANNYIT KAP
#    A v10.271-ben a buntetesnel mar igy van. Az "En meg soha" tipikus esete
#    EPPEN ez (aki igent mond, iszik 1-et), tehat eddig folosleges nevsort
#    kaptunk "1 KORTY" helyett.
#
# AMIT NEM CSINALTAM MEG (szandekosan)
#   A "soha nincs pont" kerdest nem nyultam hozza: az `onAdvance(dm, {})` tovabbra
#   is ures pont-terkeppel megy. Ez jatekmenet-donte (pl. aki tartozkodik, kapjon-e
#   pontot), es nem akartam nemán atirni a pontozas jelenteset.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─────────────────────────────────────────────────────────────────────────────
# 1-2. Kozos sor + a DrinkDistributor egysegesitese
# ─────────────────────────────────────────────────────────────────────────────
OLD_DD = """function DrinkDistributor({ players, onFinish, title }) {
  const [drinks, setDrinks] = React.useState({});
  const add = (pid) => setDrinks(d => ({ ...d, [pid]: (d[pid]||0)+1 }));
  const remove = (pid) => setDrinks(d => {
    const cur = d[pid]||0; if (cur<=0) return d;
    const n = {...d}; if (cur===1) delete n[pid]; else n[pid]=cur-1; return n;
  });
  const total = Object.values(drinks).reduce((s,v)=>s+v,0);
  return (
    <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:8 }}>
      {title && (
        <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:2 }}>
          <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.08em' }}>{title}</div>
        </div>
      )}
      {players.map(p => {
        const cnt = drinks[p.id]||0;
        return (
          <div key={p.id} style={{ display:'flex', alignItems:'center', gap:8, padding:'7px 10px', background:T.surface, borderRadius:12, boxShadow:T.shadowPill }}>
            <PlayerAvatar player={p} size={30} />
            <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:13, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
            <div style={{ display:'flex', alignItems:'center', gap:5, flexShrink:0 }}>
              <button onClick={()=>remove(p.id)} disabled={cnt===0}
                style={{ width:26, height:26, borderRadius:7, border:'none', background:cnt>0?T.surfaceMuted:T.surfaceMuted, color:cnt>0?T.inkSoft:T.inkMute, fontFamily:T.font, fontSize:16, fontWeight:700, cursor:cnt>0?'pointer':'default' }}>−</button>
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:cnt>0?T.coral:T.inkMute, minWidth:26, textAlign:'center' }}>{cnt>0?<React.Fragment>{cnt} <BohIcon name="beer" size={12} /></React.Fragment>:'–'}</span>
              <button onClick={(e)=>{ add(p.id); if (window.bohFloat) window.bohFloat(e.currentTarget, `+${(drinks[p.id]||0)+1} 🍺`, T.coral); }}
                style={{ width:26, height:26, borderRadius:7, border:'none', background:T.coral+'22', color:T.coral, fontFamily:T.font, fontSize:16, fontWeight:700, cursor:'pointer' }}>+</button>
            </div>
          </div>
        );
      })}
      <button onClick={()=>onFinish(drinks)} style={{ width:'100%', padding:'12px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:15, borderRadius:14, border:'none', cursor:'pointer', boxShadow:T.shadow, marginTop:2, animation:'popIn .2s' }}>
        {total>0 ? `${total} korty kiosztva ✔` : 'Senki sem iszik ✔'}
      </button>
    </div>
  );
}"""

NEW_DD = """// ── A korty-oszto sor — EGY komponens, ket vezerlovel (v10.279) ────────────
// Eddig a `DrinkDistributor` es a `PenaltyModal` kulon rajzolta ugyanazt a sort,
// mas magassaggal, mas hatterrel, mas arnyekkal. Mostantol mindketto ezt hasznalja,
// tehat nem tud ujra szetcsuszni. A jobb oldali vezerlo a kulonbseg:
//   * 'stepper' — `− [n 🍺] +`  (Buntetes, Ko-papir, Meduza, Zene)
//   * 'toggle'  — NEM / IGEN     (binaris jatek, pl. En meg soha)
const DRINK_ROW_H = 48, DRINK_ROW_GAP = 8, DRINK_ROWS_VISIBLE = 5;
const DRINK_LIST_MAX = DRINK_ROWS_VISIBLE * DRINK_ROW_H + (DRINK_ROWS_VISIBLE - 1) * DRINK_ROW_GAP;

function PlayerDrinkRow({ p, cnt, onAdd, onRemove, mode }) {
  const on = cnt > 0;
  const stepBtn = (extra) => ({ width:30, height:30, borderRadius:9, border:'none', flexShrink:0,
    fontFamily:T.font, fontSize:17, fontWeight:900, lineHeight:1, display:'grid', placeItems:'center', ...extra });
  return (
    <div onClick={mode === 'toggle' ? (e) => { if (on) onRemove(p.id); else { onAdd(p.id); if (window.bohFloat) window.bohFloat(e.currentTarget, '+1 🍺', T.coral); } } : undefined}
         style={{ flexShrink:0, height:DRINK_ROW_H, display:'flex', alignItems:'center', gap:10, padding:'7px 10px',
                  background: (mode === 'toggle' && on) ? T.coral + '1F' : T.surfaceMuted,
                  borderRadius:14, cursor: mode === 'toggle' ? 'pointer' : 'default', transition:'background .15s' }}>
      <PlayerAvatar player={p} size={34} />
      <div style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink,
                    overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
      {mode === 'toggle' ? (
        <div style={{ flexShrink:0, width:62, height:32, borderRadius:999, position:'relative',
                      background: on ? T.coral : `${T.inkMute}38`, transition:'background .15s' }}>
          <span style={{ position:'absolute', top:0, bottom:0, width:28, display:'grid', placeItems:'center',
                         fontFamily:T.font, fontSize:9, fontWeight:900, letterSpacing:'0.04em',
                         right:4, color:T.inkSoft, opacity: on ? 0 : 1 }}>NEM</span>
          <span style={{ position:'absolute', top:0, bottom:0, width:28, display:'grid', placeItems:'center',
                         fontFamily:T.font, fontSize:9, fontWeight:900, letterSpacing:'0.04em',
                         left:4, color:'#fff', opacity: on ? 1 : 0 }}>IGEN</span>
          <span style={{ position:'absolute', top:3, left: on ? 33 : 3, width:26, height:26, borderRadius:'50%',
                         background:'#fff', boxShadow:'0 1px 3px rgba(0,0,0,0.2)', transition:'left .15s' }} />
        </div>
      ) : (
        <div style={{ display:'flex', alignItems:'center', gap:6, flexShrink:0 }}>
          <button onClick={()=>onRemove(p.id)} disabled={!on}
            style={stepBtn({ background: on ? T.surface : 'transparent', color: on ? T.inkSoft : T.inkMute,
                             boxShadow: on ? T.shadowPill : 'none', cursor: on ? 'pointer' : 'default' })}>−</button>
          <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, minWidth:44, textAlign:'center',
                         color: on ? T.coral : T.inkMute, fontVariantNumeric:'tabular-nums',
                         display:'inline-flex', alignItems:'center', justifyContent:'center', gap:3 }}>
            {on ? <React.Fragment>{cnt}<BohIcon name="beer" size={14} /></React.Fragment> : '–'}
          </span>
          <button onClick={(e)=>{ onAdd(p.id); if (window.bohFloat) window.bohFloat(e.currentTarget, `+${cnt+1} 🍺`, T.coral); }}
            style={stepBtn({ background: T.coral+'22', color:T.coral, cursor:'pointer' })}>+</button>
        </div>
      )}
    </div>
  );
}

// `mode`: 'stepper' (alap) vagy 'toggle'. A lista legfeljebb 5 sort mutat,
// onnantol gorget — igy a zaro gomb SOSEM csuszik a lathato resz ala. (Merve:
// 10 jatekosnal a regi valtozatban 940 px-nel volt, egy 874 px-es kepernyon.)
function DrinkDistributor({ players, onFinish, title, mode }) {
  const [drinks, setDrinks] = React.useState({});
  const add = (pid) => setDrinks(d => ({ ...d, [pid]: (d[pid]||0)+1 }));
  const remove = (pid) => setDrinks(d => {
    const cur = d[pid]||0; if (cur<=0) return d;
    const n = {...d}; if (cur===1) delete n[pid]; else n[pid]=cur-1; return n;
  });
  const total = Object.values(drinks).reduce((s,v)=>s+v,0);
  const fo = Object.values(drinks).filter(v=>v>0).length;
  return (
    <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:8 }}>
      {title && (
        <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.08em' }}>{title}</div>
      )}
      <div style={{ display:'flex', flexDirection:'column', gap:DRINK_ROW_GAP, maxHeight:DRINK_LIST_MAX, overflowY:'auto' }}>
        {players.map(p => (
          <PlayerDrinkRow key={p.id} p={p} cnt={drinks[p.id]||0} onAdd={add} onRemove={remove} mode={mode} />
        ))}
      </div>
      <button onClick={()=>onFinish(drinks)} style={{ width:'100%', padding:'13px', background: total>0 ? T.mint : T.surfaceMuted, color: total>0 ? '#fff' : T.inkSoft, fontFamily:T.font, fontWeight:900, fontSize:15, borderRadius:16, border:'none', cursor:'pointer', boxShadow: total>0 ? '0 4px 14px -4px rgba(79,194,160,0.6)' : 'none', marginTop:2 }}>
        {total>0 ? (mode === 'toggle' ? `${fo} iszik · ${total} korty` : `${total} korty kiosztva`) : 'Senki sem iszik'}
      </button>
    </div>
  );
}"""
sub(OLD_DD, NEW_DD, 'DrinkDistributor')

# ─────────────────────────────────────────────────────────────────────────────
# 3-5. En meg soha: keveres, kapcsolo, kisebb kartya, nincs duplazott kerdes
# ─────────────────────────────────────────────────────────────────────────────
sub("""function SohanemGame({ gameIdx, players, onAdvance, onResult }) {
  const card = SOHANEM_CARDS[gameIdx % SOHANEM_CARDS.length];
  const cardNum = (gameIdx % SOHANEM_CARDS.length) + 1;
  const total = SOHANEM_CARDS.length;""",
    """function SohanemGame({ gameIdx, players, onAdvance, onResult }) {
  // A PAKLI PARTINKENT MEG VAN KEVERVE.
  // Eddig `SOHANEM_CARDS[gameIdx % 207]` volt: a lap tisztan abbol kovetkezett,
  // hogy hanyadik jatek jon. Ket kovetkezmenye volt — minden parti ugyanazzal a
  // lappal indult (01/207), es mivel egy buli 20-40 jatekot jatszik le, csak az
  // elso ~40 lap kerult valaha elo. A 207-bol ~167 elerhetetlen volt.
  // Ugyanaz a xorshift, mint a Collect tablajanal, csak partinkent egyszer.
  const order = React.useMemo(() => {
    const idx = SOHANEM_CARDS.map((_, i) => i);
    let s = (Date.now() ^ 0x9E3779B9) >>> 0;
    const rng = () => { s^=s<<13; s^=s>>17; s^=s<<5; return s>>>0; };
    for (let i = idx.length-1; i>0; i--) { const j = rng()%(i+1); [idx[i],idx[j]]=[idx[j],idx[i]]; }
    return idx;
  }, []);
  const pos = gameIdx % order.length;
  const card = SOHANEM_CARDS[order[pos]];
  const cardNum = pos + 1;
  const total = SOHANEM_CARDS.length;""",
    'keveres')

sub("""  const handleFinish = (dm) => {
    const drinkersNow = (players||[]).filter(p => dm[p.id] > 0);
    if (drinkersNow.length === 0) onResult && onResult({ correct:true, playerName:null, drinks:0, subtitle:'Mindenki tartózkodott ✓' });
    else onResult && onResult({ losers: drinkersNow, loseNote: drinkersNow.map(p=>`${p.name} ${dm[p.id]}🍺`).join(', ') });
    onAdvance && onAdvance(dm, {});
  };""",
    """  const handleFinish = (dm) => {
    const drinkersNow = (players||[]).filter(p => dm[p.id] > 0);
    if (drinkersNow.length === 0) onResult && onResult({ correct:true, playerName:null, drinks:0, subtitle:'Mindenki tartózkodott ✓' });
    else {
      // Ha mindenki UGYANANNYIT kap — az "En meg soha" tipikus esete, hiszen aki
      // igent mond, iszik egyet —, van egyetlen igaz szam, tehat a banner kiirja.
      // Ugyanaz a szabaly, mint a buntetesnel (v10.271). Eltero osszegnel marad a
      // nevenkenti felsorolas, mert olyan EGY szam nincs, ami igaz lenne.
      const amounts = drinkersNow.map(p => dm[p.id]);
      const uniform = amounts.every(v => v === amounts[0]);
      onResult && onResult(uniform
        ? { losers: drinkersNow, drinks: amounts[0] }
        : { losers: drinkersNow, loseNote: drinkersNow.map(p=>`${p.name} ${dm[p.id]}🍺`).join(', ') });
    }
    onAdvance && onAdvance(dm, {});
  };""",
    'uniform banner')

# a kartya kisebb, hogy a lista is kiferjen a gombbal
sub("""      <div style={{ position:'relative', width:'100%', paddingTop:'62%' }}>""",
    """      {/* 62% -> 48%: a lista es a zaro gomb is elfer alatta gorgetes nelkul */}
      <div style={{ position:'relative', width:'100%', paddingTop:'48%' }}>""",
    'kartya meret')

# a fuszer-csik ugyanazt kodolta, mint a bal felso jelveny, es haladasjelzonek latszott
sub("""          <div style={{ display:'flex', gap:3 }}>
            {['alap','alap','kozepes','kozepes','vad'].map((l,i) => {
              const lvls=['alap','kozepes','vad'];
              const lit = lvls.indexOf(l) <= lvls.indexOf(card.l);
              const bc = l==='vad'?T.coral:l==='kozepes'?T.yellow:T.mint;
              return <div key={i} style={{ width:20, height:6, borderRadius:4, background:lit?bc:`${T.inkMute}28` }} />;
            })}
          </div>
""", "", 'fuszer csik')

# a kepernyo teteje ne tegye fel ugyanazt a kerdest, amit a kartya
sub("""  sohanem:   { prompt:'Én még soha — igaz rád?', cta:[('Igaz rám — iszom'),('Nem igaz rám')] },""",
    """  sohanem:   { prompt:'Olvasd fel — aztán jelöld, kire igaz', cta:[('Igaz rám — iszom'),('Nem igaz rám')] },""",
    'prompt')

sub("""        <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.08em', marginBottom:8 }}>Kire igaz?</div>
        <DrinkDistributor players={players||[]} onFinish={handleFinish} />""",
    """        <DrinkDistributor players={players||[]} onFinish={handleFinish} mode="toggle" title="Kire igaz?" />""",
    'toggle mod')

sub("const APP_VERSION = 'v10.278';", "const APP_VERSION = 'v10.279';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — kozos sor, egyseges oszto, kevert pakli, kapcsolo')
