#!/usr/bin/env python3
# v10.288 — Én még soha: a lap EGY szinu (a temabol), a jelveny viszi a szintet
#
# A KERT VALTOZAS
#   Eddig a lap hattere HAROM fix pasztell kozul valt a fuszerszint szerint.
#   Mostantol a lap mindig UGYANAZ az egy szin, es a temabol jon: `T.bgSoft` —
#   ez a jade temaban #CCF0DA, vagyis pontosan az az arnyalat, ami a kuldott
#   kepen olyan jol ult a #B8E8C8-as oldalon. A fuszerszintet csak a bal felso
#   jelveny mondja el, tovabbra is a telitett szinevel.
#
# AMI EBBOL KOVETKEZIK, ES KONNYU ELFELEJTENI
#   A `CARD_INK = '#14202F'` FIX SOTET tinta azert kellett, mert a lap szine
#   temafuggetlen volt: pasztellen a feher olvashatatlan, a `T.ink` viszont a
#   sotet temakban vilagos. Most a lap MAGA is temafuggo (`T.bgSoft`), tehat a
#   tintanak vissza kell allnia `T.ink`-re — kulonben sotet temaban sotet
#   szoveg allna sotet lapon. Ugyanez all a halvany korokre es a peremre:
#   `rgba(20,32,47,...)` helyett `T.ink`-bol szarmaztatott alfa.
#
# A KORTY-OSZTO KET VALTOZASA
#   1. A sor legyen olyan szeles, mint a kerdes-lap. A `maxWidth:DRINK_LIST_W`
#      (296 px) a Buntetes-modalhoz volt igazitva (v10.281) — de a modalban a
#      szulo UGYIS 296 px, tehat a korlat ott felesleges, jatekon belul viszont
#      osszehuzta a sort a lap ala. A korlat elhagyasaval mindket helyen az lesz,
#      ami kell: modalban 296, jatekban teljes szelesseg.
#   2. Kiosztas utan ne csak lezarjon a lista, hanem TUNJENEK EL a leptetok.
#      Eddig a sorok 0.55 opacityvel es `pointerEvents:none`-szal maradtak — ez
#      tiltott gombok sorat hagyta a kepernyon. Helyette egy tomor osszegzo sor
#      all ott, es CSAK azok, akik tenylegesen kaptak kortyot: husz emberes
#      listanal ugyis csak ez az informacio szamit.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─────────────────────────────────────────────────────────────────────────────
# 1. A paletta: csak a jelveny szine marad
# ─────────────────────────────────────────────────────────────────────────────
sub("""  // HOFOK-PALETTA — a Szerencsekerek pasztelljeibol (lasd WHEEL_TONES).
  // Szandekosan FIX, nem a T.* tokenekbol: 8 tema van, de az, hogy mennyire
  // durva a kerdes, nem valtozhat temarol temara.
  //   `bg`    — a lap halvany hattere (a kerek egy-egy cikkelyszine)
  //   `badge` — ugyanaz telitve, a jelvenynek, feher felirattal
  const SPICE = {
    alap:    { label:'ALAP',    emoji:'🌶', bg:'#C9E8D2', badge:'#4FA97F' },
    kozepes: { label:'KÖZEPES', emoji:'🔥', bg:'#F5E0AC', badge:'#D69A2E' },
    vad:     { label:'VAD',     emoji:'🔥', bg:'#F2C4C4', badge:'#D46A6A' },
  };
  const lv = SPICE[card.l] || SPICE.alap;
  // A lap szine temafuggetlen, tehat a tintanak is annak kell lennie: pasztellen
  // a feher olvashatatlan, a `T.ink` viszont a SOTET temakban vilagos.
  const CARD_INK = '#14202F';""",
    """  // FUSZERSZINT — mostantol CSAK a jelvenyen. A lap maga egy szinu.
  // A `badge` szandekosan FIX (nem T.* token): 8 tema van, de az, hogy mennyire
  // durva a kerdes, nem valtozhat temarol temara. A feher felirat mindharmon
  // olvashato.
  const SPICE = {
    alap:    { label:'ALAP',    emoji:'🌶', badge:'#4FA97F' },
    kozepes: { label:'KÖZEPES', emoji:'🔥', badge:'#D69A2E' },
    vad:     { label:'VAD',     emoji:'🔥', badge:'#D46A6A' },
  };
  const lv = SPICE[card.l] || SPICE.alap;""",
    'paletta')

# ─────────────────────────────────────────────────────────────────────────────
# 2. A lap
# ─────────────────────────────────────────────────────────────────────────────
sub("""      {/* ── A HŐFOK-LAP ──
          A lap SZINE a fuszerszint. Igy a tet lathato, mielott elolvasnad: egy
          voros lap felfordulasa onmagaban esemeny. A jelveny nem plusz info,
          hanem megerosites. A halvany korok adnak melyseget a lapos szinnek. */}
      <div style={{ width:'100%', borderRadius:26, padding:'20px 20px 22px', color:CARD_INK,
                    position:'relative', overflow:'hidden', background:lv.bg,
                    /* A hajszalvekony perem a lap SAJAT telitett szinebol jon.
                       Nelkule a KOZEPES lap (#F5E0AC) beleolvad az alapertelmezett
                       meleg tema hattérebe — csak az arnyek valasztana el. */
                    boxShadow:`inset 0 0 0 1.5px ${lv.badge}33, 0 6px 18px -8px rgba(20,30,50,0.30)` }}>
        <span style={{ position:'absolute', width:190, height:190, right:-70, top:-60,
                       borderRadius:'50%', border:'2px solid rgba(20,32,47,0.07)' }} />
        <span style={{ position:'absolute', width:120, height:120, left:-45, bottom:-45,
                       borderRadius:'50%', border:'2px solid rgba(20,32,47,0.07)' }} />""",
    """      {/* ── A KÉRDÉS-LAP ──
          EGY szin, es az a TEMABOL jon (`T.bgSoft`) — igy a lap minden temaban
          ugyanabbol a csaladbol valo arnyalat, mint az oldal. A fuszerszintet
          nem a hatter mondja el, hanem a bal felso jelveny.
          Mivel a lap szine mar temafuggo, a TINTANAK is annak kell lennie:
          a korabbi fix sotet `CARD_INK` sotet temaban sotet szoveget hagyna
          sotet lapon. Ugyanezert szarmazik a perem es a ket halvany kor is
          `T.ink`-bol, nem bedrotozott rgba-bol. */}
      <div style={{ width:'100%', borderRadius:26, padding:'20px 20px 22px', color:T.ink,
                    position:'relative', overflow:'hidden', background:T.bgSoft,
                    boxShadow:`inset 0 0 0 1.5px ${T.ink}12, 0 6px 18px -8px rgba(20,30,50,0.30)` }}>
        <span style={{ position:'absolute', width:190, height:190, right:-70, top:-60,
                       borderRadius:'50%', border:`2px solid ${T.ink}10` }} />
        <span style={{ position:'absolute', width:120, height:120, left:-45, bottom:-45,
                       borderRadius:'50%', border:`2px solid ${T.ink}10` }} />""",
    'lap')

# ─────────────────────────────────────────────────────────────────────────────
# 3. Korty-oszto: teljes szelesseg + kiosztas utan csak az ivok latszanak
# ─────────────────────────────────────────────────────────────────────────────
sub("""const DRINK_LIST_W = 296;""",
    """// A modalban a szulo UGYIS 296 px (340-es lap - 2x22 belso margo), tehat ott
// nem kell korlat; jatekon belul viszont a sor a kerdes-lappal egyenlo szeles.
// Ezert a kioszto nem szab sajat maximumot — a szulo dont. (A konstans csak a
// buntetes-modal merteke maradt, a tesztek hivatkozzak.)
const DRINK_LIST_W = 296;""",
    'DRINK_LIST_W komment')

sub("""    <div style={{ width:'100%', maxWidth:DRINK_LIST_W, margin:'0 auto', display:'flex', flexDirection:'column', gap:8 }}>""",
    """    <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:8 }}>""",
    'kioszto szelesseg')

sub("""      <div style={{ display:'flex', flexDirection:'column', gap:DRINK_ROW_GAP, maxHeight:DRINK_LIST_MAX, overflowY:'auto',
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
      ) : (""",
    """      {/* KIOSZTAS UTAN nem tiltott leptetok sora marad a kepernyon, hanem egy
          tomor osszegzes — es CSAK azok, akik tenylegesen kaptak kortyot.
          Husz emberes listanal a tobbi sor ugyis csak zaj: aki nem ivott, arrol
          nincs mit mondani, es a gorgetes miatt fel sem ferne a kepre. */}
      {kesz ? (
        ivok.length > 0 && (
          <div style={{ display:'flex', flexDirection:'column', gap:DRINK_ROW_GAP,
                        maxHeight:DRINK_LIST_MAX, overflowY:'auto', animation:'bohFadeIn .18s' }}>
            {ivok.map(p => (
              <div key={p.id} style={{ flexShrink:0, height:DRINK_ROW_H, display:'flex', alignItems:'center',
                                       gap:10, padding:'7px 10px', background:T.coralSoft, borderRadius:14 }}>
                <PlayerAvatar player={p} size={34} />
                <div style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink,
                              overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
                <div style={{ display:'flex', alignItems:'center', gap:5, flexShrink:0, fontFamily:T.font,
                              fontWeight:900, fontSize:15, color:T.ink }}>
                  {drinks[p.id]}<BohIcon name="beer" size={17} />
                </div>
              </div>
            ))}
          </div>
        )
      ) : (
      <div style={{ display:'flex', flexDirection:'column', gap:DRINK_ROW_GAP, maxHeight:DRINK_LIST_MAX, overflowY:'auto' }}>
        {players.map(p => (
          <PlayerDrinkRow key={p.id} p={p} cnt={drinks[p.id]||0} onAdd={add} onRemove={remove} max={max} />
        ))}
      </div>
      )}
      {kesz ? (
        <div style={{ textAlign:'center', padding:'13px 0 2px', fontFamily:T.font, fontWeight:800, fontSize:13,
                      color:T.inkMute, animation:'bohFadeIn .18s' }}>
          {total>0 ? `${total} korty kiosztva` : 'Senki nem ivott'} — jöhet a Kövi
        </div>
      ) : (""",
    'kioszto osszegzes')

sub("""  const total = Object.values(drinks).reduce((s,v)=>s+v,0);
  const fo = Object.values(drinks).filter(v=>v>0).length;
  return (
    <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:8 }}>""",
    """  const total = Object.values(drinks).reduce((s,v)=>s+v,0);
  const fo = Object.values(drinks).filter(v=>v>0).length;
  const ivok = players.filter(p => (drinks[p.id]||0) > 0);
  return (
    <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:8 }}>""",
    'ivok')

sub("const APP_VERSION = 'v10.287';", "const APP_VERSION = 'v10.288';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — egy színű lap a témából, teljes szélességű sorok, összegző kiosztás után')
