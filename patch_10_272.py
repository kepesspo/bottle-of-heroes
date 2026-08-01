#!/usr/bin/env python3
# v10.272 — EGY buntetes-FELULET is: kozepre igazitott modal, soronkent − szam +
#
# A v10.271-ben a LOGIKA lett egy (`givePenalty`), de a FELULET meg ketto volt:
#   * Wildcard -> "Szabalyszego?"  : kozepre igazitott modal, soronkent
#     avatar + nev + korso ikon, egy koppintas = 1 korty, tobbet nem lehetett
#     kiosztani, es tobb embert sem lehetett megjelolni;
#   * MENÜ -> Buntetes             : also lap (SheetOverlay), soronkent
#     avatar + nev + `− szam +` leptetovel.
#
# A DONTES (a te valasztasod)
#   A modal marad a forma, a leptetos sor a tartalom. Egyetlen `PenaltyModal`
#   szolgalja ki mindket belepot — a cim, az emoji es a leiras a kulonbseg,
#   semmi mas.
#
# AMIT EZ MEGOLD A KINEZETEN TUL
#   A wildcard-buntetes eddig FIX 1 korty volt egyetlen embernek. Mostantol ott
#   is tobb kortyot es tobb embert lehet megjelolni — ugyanaz a modell, mint a
#   MENÜ-bol. Cserebe a leggyakoribb eset (1 korty 1 embernek) egy koppintassal
#   tobb lett: `+`, majd a zaro gomb.
#
# A `punishWildcard` ezzel folosleges: a modal a teljes terkepet adja at a
# kozos `givePenalty`-nek, ugyanugy, mint a MENÜ-bol jovo ut.
#
# A `menuSheetH` is kivezetheto: azert szuletett, hogy a Buntetes ALSO LAP
# ugyanolyan magas legyen, mint a MENÜ lap. Modalnal ennek nincs ertelme.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─────────────────────────────────────────────────────────────────────────────
# 1. PenaltySheet (also lap) -> PenaltyModal (kozepre igazitott modal)
# ─────────────────────────────────────────────────────────────────────────────
OLD = """// Büntetés lap — mint a DrinkDistributor, de a zaro gomb a SheetOverlay
// FIX footer-jebe kerul, a nevek pedig kulon gorgetheto reszben vannak.
// Igy sok jatekosnal sem kell a lista vegere gorgetni a gombhoz.
function PenaltySheet({ players, onClose, onFinish, height }) {
  const [drinks, setDrinks] = React.useState({});
  const add = (pid) => setDrinks(d => ({ ...d, [pid]: (d[pid]||0)+1 }));
  const remove = (pid) => setDrinks(d => {
    const cur = d[pid]||0; if (cur<=0) return d;
    const n = {...d}; if (cur===1) delete n[pid]; else n[pid]=cur-1; return n;
  });
  const total = Object.values(drinks).reduce((s,v)=>s+v,0);
  return (
    <SheetOverlay onClose={onClose} title="Büntetés — ki igyon?" height={height} footer={
      <button onClick={()=>onFinish(drinks)} style={{ width:'100%', padding:'12px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:15, borderRadius:14, border:'none', cursor:'pointer', boxShadow:T.shadow }}>
        {total>0 ? `${total} korty kiosztva ✔` : 'Senki sem iszik ✔'}
      </button>
    }>
      <div style={{ padding:'0 16px', display:'flex', flexDirection:'column', gap:12 }}>
        <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkSoft, lineHeight:1.5 }}>
          Játékon kívüli korty — wildcard megszegése, fogadás, bármi.
          A kiosztott korty a játékban szerzettel együtt számít.
        </div>
        <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:8 }}>
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
        </div>
      </div>
    </SheetOverlay>
  );
}"""

NEW = """// ── Büntetés-modal (v10.272) ──────────────────────────────────────────────
// EGYETLEN felulet a jatekon kivuli korty kiosztasara. Ket helyrol nyilik:
//   * MENÜ -> Buntetes            (cim: "Büntetés — ki igyon?")
//   * Wildcard -> "Szabalyszego?" (cim: "Ki szegte meg a szabályt?", emojival)
// Korabban ez ket kulon felulet volt: egy also lap leptetovel, es egy modal,
// ahol egy koppintas fix 1 kortyot adott EGY embernek. Most mindketto modal,
// es mindkettoben `− szam +` all a nev mellett — tehat a szabalyszegesert is
// lehet 2-3 kortyot adni, vagy tobb embert megjelolni.
function PenaltyModal({ players, title, subtitle, emoji, onClose, onFinish }) {
  const [drinks, setDrinks] = React.useState({});
  const add = (pid) => setDrinks(d => ({ ...d, [pid]: (d[pid]||0)+1 }));
  const remove = (pid) => setDrinks(d => {
    const cur = d[pid]||0; if (cur<=0) return d;
    const n = {...d}; if (cur===1) delete n[pid]; else n[pid]=cur-1; return n;
  });
  const total = Object.values(drinks).reduce((s,v)=>s+v,0);
  const stepBtn = (extra) => ({ width:30, height:30, borderRadius:9, border:'none', flexShrink:0,
    fontFamily:T.font, fontSize:17, fontWeight:900, lineHeight:1, display:'grid', placeItems:'center', ...extra });
  return (
    <div onClick={onClose} style={{ position:'fixed', inset:0, background:'rgba(14,14,24,0.72)', zIndex:60,
                                    display:'flex', alignItems:'center', justifyContent:'center', padding:28, animation:'fadeIn .2s' }}>
      <div onClick={e => e.stopPropagation()}
           style={{ background:T.surface, border:'none', borderRadius:28, padding:'26px 22px 22px', width:'100%', maxWidth:340,
                    boxShadow:'0 24px 64px rgba(0,0,0,0.3)', animation:'popIn .3s cubic-bezier(.2,.9,.3,1.3)' }}>
        {emoji && <div style={{ textAlign:'center', fontSize:34, lineHeight:1, marginBottom:8 }}>{emoji}</div>}
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, textAlign:'center', marginBottom:4 }}>{title}</div>
        {subtitle && <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkSoft, textAlign:'center', marginBottom:14, lineHeight:1.4 }}>{subtitle}</div>}
        <div style={{ display:'flex', flexDirection:'column', gap:8, maxHeight:'42vh', overflowY:'auto' }}>
          {players.map(p => {
            const cnt = drinks[p.id]||0;
            return (
              <div key={p.id} style={{ display:'flex', alignItems:'center', gap:10, padding:'7px 10px',
                                       background:T.surfaceMuted, borderRadius:14 }}>
                <PlayerAvatar player={p} size={34} />
                <div style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink,
                              overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
                {/* − szám + — a te elrendezesed: avatar, nev, a masik oldalon a lepteto */}
                <div style={{ display:'flex', alignItems:'center', gap:6, flexShrink:0 }}>
                  <button onClick={()=>remove(p.id)} disabled={cnt===0}
                    style={stepBtn({ background: cnt>0 ? T.surface : 'transparent',
                                     color: cnt>0 ? T.inkSoft : T.inkMute,
                                     boxShadow: cnt>0 ? T.shadowPill : 'none',
                                     cursor: cnt>0 ? 'pointer' : 'default' })}>−</button>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, minWidth:30, textAlign:'center',
                                 color: cnt>0 ? T.coral : T.inkMute, fontVariantNumeric:'tabular-nums' }}>{cnt>0 ? cnt : '–'}</span>
                  <button onClick={(e)=>{ add(p.id); if (window.bohFloat) window.bohFloat(e.currentTarget, `+${(drinks[p.id]||0)+1} 🍺`, T.coral); }}
                    style={stepBtn({ background: T.coral+'22', color:T.coral, cursor:'pointer' })}>+</button>
                </div>
              </div>
            );
          })}
        </div>
        <button onClick={()=>onFinish(drinks)}
          style={{ width:'100%', marginTop:14, padding:'13px 0', borderRadius:14, border:'none',
                   background: total>0 ? T.mint : T.surfaceMuted, color: total>0 ? '#fff' : T.inkSoft,
                   fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer' }}>
          {total>0 ? `${total} korty kiosztva ✔` : 'Senki sem iszik ✔'}
        </button>
        <button onClick={onClose}
          style={{ width:'100%', marginTop:8, padding:'11px 0', borderRadius:14, border:'none', background:'transparent',
                   color:T.inkMute, fontFamily:T.font, fontWeight:800, fontSize:14, cursor:'pointer' }}>Mégse</button>
      </div>
    </div>
  );
}"""
sub(OLD, NEW, 'PenaltyModal')

# ─────────────────────────────────────────────────────────────────────────────
# 2. A ket belepo ugyanazt a modalt nyitja
# ─────────────────────────────────────────────────────────────────────────────
sub("""      {penaltyOpen && (
        <PenaltySheet players={players || []} onClose={() => setPenaltyOpen(false)} onFinish={applyPenalty}
          height={menuSheetH ? menuSheetH + 'px' : undefined} />
      )}""",
    """      {penaltyOpen && (
        <PenaltyModal players={(players || []).filter(p => p.active !== false)}
          title="Büntetés — ki igyon?"
          subtitle="Játékon kívüli korty — wildcard megszegése, fogadás, bármi. A kiosztott korty a játékban szerzettel együtt számít."
          onClose={() => setPenaltyOpen(false)} onFinish={applyPenalty} />
      )}""",
    'menu belepo')

OLD_WC = """      {wcPunishOpen && activeWildcard && (
        <div onClick={() => setWcPunishOpen(false)} style={{ position:'fixed', inset:0, background:'rgba(14,14,24,0.72)', zIndex:60, display:'flex', alignItems:'center', justifyContent:'center', padding:28, animation:'fadeIn .2s' }}>
          <div onClick={e => e.stopPropagation()} style={{ background: T.surface, border:'none', borderRadius: 28, padding:'26px 22px 22px', width:'100%', maxWidth:340, boxShadow:'0 24px 64px rgba(0,0,0,0.3)', animation:'popIn .3s cubic-bezier(.2,.9,.3,1.3)' }}>
            <div style={{ textAlign:'center', fontSize:34, lineHeight:1, marginBottom:8 }}>{activeWildcard.emoji}</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, textAlign:'center', marginBottom:4 }}>Ki szegte meg a szabályt?</div>
            <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkSoft, textAlign:'center', marginBottom:14, lineHeight:1.4 }}>{activeWildcard.text}</div>
            <div style={{ display:'flex', flexDirection:'column', gap:8, maxHeight:'42vh', overflowY:'auto' }}>
              {players.filter(p => p.active !== false).map(p => (
                <button key={p.id} onClick={() => punishWildcard(p.id)} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 14px', borderRadius:14, border:'none', background: T.surfaceMuted, boxShadow: 'none', cursor:'pointer', textAlign:'left' }}>
                  <PlayerAvatar player={p} size={36} />
                  <span style={{ flex:1, fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</span>
                  <BohIcon name="beer" size={16} />
                </button>
              ))}
            </div>
            <button onClick={() => setWcPunishOpen(false)} style={{ width:'100%', marginTop:12, padding:'12px 0', borderRadius:14, border: 'none', background: T.surfaceMuted, color:T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:14, cursor:'pointer' }}>Mégse</button>
          </div>
        </div>
      )}"""
sub(OLD_WC,
    """      {wcPunishOpen && activeWildcard && (
        <PenaltyModal players={(players || []).filter(p => p.active !== false)}
          emoji={activeWildcard.emoji}
          title="Ki szegte meg a szabályt?"
          subtitle={activeWildcard.text}
          onClose={() => setWcPunishOpen(false)} onFinish={applyWcPunish} />
      )}""",
    'wildcard belepo')

# ─────────────────────────────────────────────────────────────────────────────
# 3. punishWildcard(pid) -> applyWcPunish(map): ugyanaz a szerzodes, mint a MENÜ-e
# ─────────────────────────────────────────────────────────────────────────────
sub("""  // A szabalyszeges is buntetes — ugyanazt az utat jarja, csak fix 1 kortyot
  // oszt. A regi kulon Toast helyett ugyanugy a result banner jon, ami tobbet
  // mutat: avatar, nev, korty-szam. Lasd patch_10_271.py
  const punishWildcard = (pid) => {
    setWcPunishOpen(false);
    givePenalty({ [pid]: 1 }, { note: 'Szabályszegés' });
  };""",
    """  // A szabalyszeges is buntetes — ugyanaz a modal, ugyanaz a szerzodes
  // ({ playerId: korty }), csak mas cim. Lasd patch_10_272.py
  const applyWcPunish = (assigned) => {
    setWcPunishOpen(false);
    givePenalty(assigned, { note: 'Szabályszegés' });
  };""",
    'applyWcPunish')

# ─────────────────────────────────────────────────────────────────────────────
# 4. menuSheetH kivezetese — csak az also lap magassagahoz kellett
# ─────────────────────────────────────────────────────────────────────────────
sub("""  // A MENÜ lap MERT magassaga — ehhez igazodik a Buntetes lap. A Buntetes csak
  // a MENÜ-bol nyithato, tehat mire kell, mar megvan. Lasd patch_10_249.py
  const [menuSheetH, setMenuSheetH] = useState(null);
""", "", 'menuSheetH state')

sub("""          <SheetOverlay onClose={() => setShowMenu(false)} onHeight={setMenuSheetH}>""",
    """          <SheetOverlay onClose={() => setShowMenu(false)}>""",
    'menuSheetH prop')

sub("const APP_VERSION = 'v10.271';", "const APP_VERSION = 'v10.272';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — egy PenaltyModal, soronkent − szam +')
