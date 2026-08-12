# v10.335/b — ugyanaz az ujramount-hiba a masik harom helyen
#
# Ahol alkomponens ul a torzsben, JSX-kent hasznaljuk, ES a szulo masodpercnel
# gyakrabban rendereli ujra:
#   • KisebbGame `LargeCard`            — 600 ms
#   • BeerPongObserverView `PlayerChip` — 1000 ms
#   • KoPapirGame `PlayerCard`          — 3000 ms
#
# A KoPapir `PlayerCard`-ja ARNYEKOLTA is a modul-szintu, azonos nevu
# `PlayerCard`-ot (a Jatekosok kepernyoje azt hasznalja) — az atnevezes ezt is
# megszunteti.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, f'{what}: {src.count(old)} talalat'
    src = src.replace(old, new)

# ── 1. Kisebb/Nagyobb: a `LargeCard` csak egy burkolo — kihagyjuk ────────────
# Egysoros wrapper a modul-szintu `KisebbCard` korul. Mivel a torzsben ul,
# minden ujrarenderelesnel uj tipust adott, es ujramountolta a lapot.
sub1("  const LargeCard = ({ card, faceDown }) => <KisebbCard card={card} faceDown={faceDown} remaining={remaining} />;\n\n",
     "", 'LargeCard wrapper torlese')
sub1("        <LargeCard card={currentCard} faceDown={false} />",
     "        <KisebbCard card={currentCard} faceDown={false} remaining={remaining} />",
     'LargeCard hasznalat 1')
sub1("        {shownCard ? <LargeCard card={shownCard} faceDown={false} /> : <LargeCard card={null} faceDown={true} />}",
     "        {shownCard ? <KisebbCard card={shownCard} faceDown={false} remaining={remaining} />\n"
     "                   : <KisebbCard card={null} faceDown={true} remaining={remaining} />}",
     'LargeCard hasznalat 2')

# ── 2. Ko-papir-ollo: `PlayerCard` -> modul-szintu `KoPapirPlayerCard` ───────
KP_OLD = """  const PlayerCard = ({ p, drinks }) => (
    <div style={{ flex:1, background:T.surface, borderRadius:16, padding:'14px 10px', display:'flex', flexDirection:'column', alignItems:'center', gap:6, boxShadow:T.shadow }}>
      <div style={{ width:52, height:52, borderRadius:'50%', background:p?.color||T.coral, display:'grid', placeItems:'center', overflow:'hidden', boxShadow:`0 0 0 3px ${p?.color||T.coral}44` }}>
        {p?.img ? <img src={p.img} style={{ width:52, height:52, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:'#fff' }}>{(p?.name||'?').charAt(0).toUpperCase()}</span>}
      </div>
      <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.ink, textAlign:'center' }}>{p?.name||'?'}</div>
      {drinks !== undefined && (
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color: drinks > 0 ? T.coral : T.mint }}>{drinks > 0 ? <React.Fragment>{drinks} <BohIcon name="beer" size={13} /></React.Fragment> : '😎 0'}</div>
      )}
    </div>
  );

"""
KP_NEW = """// ⚠️ MODUL-SZINTU. A torzsben ulve minden ujrarenderelesnel uj tipust kapott,
// es a React ujramountolta — az avatar `<img>` ujratoltodott. Ez a jatek 3
// masodpercenkent lepteti a kort, tehat lathatoan villogott.
// (Ugyanakkor ARNYEKOLTA is az azonos nevu, modul-szintu `PlayerCard`-ot.)
function KoPapirPlayerCard({ p, drinks }) {
  return (
    <div style={{ flex:1, background:T.surface, borderRadius:16, padding:'14px 10px', display:'flex', flexDirection:'column', alignItems:'center', gap:6, boxShadow:T.shadow }}>
      <div style={{ width:52, height:52, borderRadius:'50%', background:p?.color||T.coral, display:'grid', placeItems:'center', overflow:'hidden', boxShadow:`0 0 0 3px ${p?.color||T.coral}44` }}>
        {p?.img ? <img src={p.img} style={{ width:52, height:52, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:'#fff' }}>{(p?.name||'?').charAt(0).toUpperCase()}</span>}
      </div>
      <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.ink, textAlign:'center' }}>{p?.name||'?'}</div>
      {drinks !== undefined && (
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color: drinks > 0 ? T.coral : T.mint }}>{drinks > 0 ? <React.Fragment>{drinks} <BohIcon name="beer" size={13} /></React.Fragment> : '😎 0'}</div>
      )}
    </div>
  );
}

"""
# a definiciot kivesszuk a torzsbol...
sub1(KP_OLD, "", 'KoPapir PlayerCard kivetele')
# ...es a jatek ELE tesszuk
sub1("function KoPapirGame(", KP_NEW + "function KoPapirGame(", 'KoPapirPlayerCard beszurasa')
for old, new in [
    ("          <PlayerCard p={challenger} drinks={cd} />", "          <KoPapirPlayerCard p={challenger} drinks={cd} />"),
    ("          <PlayerCard p={opponent} drinks={od} />",   "          <KoPapirPlayerCard p={opponent} drinks={od} />"),
    ("        <PlayerCard p={challenger} drinks={totalDrinks[challenger?.id]} />", "        <KoPapirPlayerCard p={challenger} drinks={totalDrinks[challenger?.id]} />"),
    ("        <PlayerCard p={opponent} drinks={totalDrinks[opponent?.id]} />",     "        <KoPapirPlayerCard p={opponent} drinks={totalDrinks[opponent?.id]} />"),
]:
    sub1(old, new, 'KoPapir hasznalat')

# ── 3. Beer Pong observer: `PlayerChip` -> modul-szintu ─────────────────────
BP_OLD = """  const PlayerChip = ({ p: pRaw, highlight }) => {
    const p = hydObs(pRaw);
    return p ? (
      <div style={{ display:'flex', alignItems:'center', gap:8, flex:1, minWidth:0, padding:'8px 10px', borderRadius:12, background: highlight ? `${p.color}22` : T.surfaceMuted, border: highlight ? `2px solid ${p.color}60` : '2px solid transparent' }}>
        <PlayerAvatar player={p} size={32} />
        <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
      </div>
    ) : null;
  };

"""
BP_NEW = """// ⚠️ MODUL-SZINTU. A Beer Pong observer masodpercenkent frissiti az orat,
// tehat a torzsben ulve masodpercenkent ujramountolta volna az avatart.
// A `hydObs` feloldas a HIVASI helyre kerult: itt mar kesz jatekos jon.
function BpObsPlayerChip({ p, highlight }) {
  if (!p) return null;
  return (
    <div style={{ display:'flex', alignItems:'center', gap:8, flex:1, minWidth:0, padding:'8px 10px', borderRadius:12, background: highlight ? `${p.color}22` : T.surfaceMuted, border: highlight ? `2px solid ${p.color}60` : '2px solid transparent' }}>
      <PlayerAvatar player={p} size={32} />
      <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
    </div>
  );
}

"""
sub1(BP_OLD, "", 'BeerPong PlayerChip kivetele')
sub1("function BeerPongObserverView(", BP_NEW + "function BeerPongObserverView(", 'BpObsPlayerChip beszurasa')
sub1("              <PlayerChip p={curMatch.p1} highlight />", "              <BpObsPlayerChip p={hydObs(curMatch.p1)} highlight />", 'BP hasznalat 1')
sub1("              <PlayerChip p={curMatch.p2} highlight />", "              <BpObsPlayerChip p={hydObs(curMatch.p2)} highlight />", 'BP hasznalat 2')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK — patch_10_335b alkalmazva')
