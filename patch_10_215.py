#!/usr/bin/env python3
# v10.215 — MENÜ > Vezérlés fül: helytakarekosabb elrendezes
#
# 1) A "SZOBAKÓD" felirat kikerul a sorbol — a piros pulzalo pont + a kod
#    onmagaban is egyertelmu, a felirat csak helyet foglalt.
#
# 2) A felszabadult helyre (es a kulon, teljes szelessegu "Jatekos
#    hozzaadasa" sor helyere) egy kompakt "+" gomb kerul UGYANEBBE a sorba.
#    Csak akkor, ha van szobakod (online szoba) — offline jatekban marad a
#    korabbi teljes szelessegu trigger, mert ott nincs szobakod-sor, amibe
#    besimulhatna.
#
# 3) A Buntetes gomb lekerul a Vissza melle: a kulon teljes szelessegu lila
#    sor helyett egy ikon-csak gomb az akciosor elejen (Buntetes | Vissza |
#    Ujra | Kovetkezo) — igy egy egesz sornyi magassagot sporolunk.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─── 1+2) Szobakod sor: felirat ki, "+" jatekos-hozzaadas gomb be ───
sub("""                {/* Szobakód + megosztás + toggle — egy sor */}
                {roomCode && (
                  <div style={{ display:'flex', alignItems:'center', gap:10, padding:'12px 16px', background:T.bgSoft, borderRadius:16 }}>
                    <span style={{ width:7, height:7, borderRadius:'50%', background:'#E03A3A', flexShrink:0, animation:'pulse 1.4s infinite' }}/>
                    <span style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.1em' }}>{t('roomCode')}</span>
                    <span style={{ fontFamily:'monospace', fontWeight:700, fontSize:18, color:T.ink, letterSpacing:'0.15em', flex:1, textAlign:'center' }}>{roomCode}</span>
                    <button onClick={() => setShowRoomQR(true)} title="QR kód" style={{ width:40, height:40, borderRadius:12, border:'none', background:T.mint, cursor:'pointer', display:'grid', placeItems:'center', flexShrink:0, color:'#fff', boxShadow:'0 3px 10px -2px '+T.mint }}>
                      <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h6v6H3V3zm2 2v2h2V5H5zm8-2h6v6h-6V3zm2 2v2h2V5h-2zM3 15h6v6H3v-6zm2 2v2h2v-2H5zm10-2h2v2h-2v-2zm4 0h2v2h-2v-2zm-4 4h2v2h-2v-2zm2 2h2v2h-2v-2zm2-2h2v2h-2v-2z"/></svg>
                    </button>
                    <button onClick={() => {
                      const url = `${location.origin}${location.pathname}?room=${roomCode}`;
                      if (navigator.share) { navigator.share({ title:'Bottle of Heroes', text:'Csatlakozz a meccshez!', url }); }
                      else { navigator.clipboard?.writeText(url).then(() => alert('Link másolva! 🔗')).catch(() => alert(url)); }
                    }} style={{ width:34, height:34, borderRadius:10, border:'none', background:'transparent', cursor:'pointer', display:'grid', placeItems:'center', flexShrink:0, color:T.inkSoft }}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
                    </button>
                  </div>
                )}

                {/* Add player — collapsed by default, expands on tap */}
                <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
                  {!menuAddOpen ? (
                    <button onClick={() => setMenuAddOpen(true)} style={{ display:'flex', alignItems:'center', gap:10, padding:'13px 16px', borderRadius:14, border:`1.5px dashed ${T.mint}`, background:'transparent', cursor:'pointer', fontFamily:T.font, fontWeight:700, fontSize:14, color:T.mint }}>
                      <span style={{ fontSize:18, lineHeight:1 }}>＋</span>
                      <span>Játékos hozzáadása</span>
                    </button>
                  ) : (""",
    """                {/* Szobakód sor — felirat nélkül (a pont + kód önmagában egyértelmű),
                    és ide simult be a jatékos-hozzáadás "+" gombja is, hogy ne
                    kelljen érte külön, teljes szélességű sort adni. */}
                {roomCode && (
                  <div style={{ display:'flex', alignItems:'center', gap:10, padding:'12px 16px', background:T.bgSoft, borderRadius:16 }}>
                    <span style={{ width:7, height:7, borderRadius:'50%', background:'#E03A3A', flexShrink:0, animation:'pulse 1.4s infinite' }}/>
                    <span style={{ fontFamily:'monospace', fontWeight:700, fontSize:18, color:T.ink, letterSpacing:'0.15em', flex:1, textAlign:'center' }}>{roomCode}</span>
                    <button onClick={() => setShowRoomQR(true)} title="QR kód" style={{ width:40, height:40, borderRadius:12, border:'none', background:T.mint, cursor:'pointer', display:'grid', placeItems:'center', flexShrink:0, color:'#fff', boxShadow:'0 3px 10px -2px '+T.mint }}>
                      <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h6v6H3V3zm2 2v2h2V5H5zm8-2h6v6h-6V3zm2 2v2h2V5h-2zM3 15h6v6H3v-6zm2 2v2h2v-2H5zm10-2h2v2h-2v-2zm4 0h2v2h-2v-2zm-4 4h2v2h-2v-2zm2 2h2v2h-2v-2zm2-2h2v2h-2v-2z"/></svg>
                    </button>
                    <button onClick={() => {
                      const url = `${location.origin}${location.pathname}?room=${roomCode}`;
                      if (navigator.share) { navigator.share({ title:'Bottle of Heroes', text:'Csatlakozz a meccshez!', url }); }
                      else { navigator.clipboard?.writeText(url).then(() => alert('Link másolva! 🔗')).catch(() => alert(url)); }
                    }} style={{ width:34, height:34, borderRadius:10, border:'none', background:'transparent', cursor:'pointer', display:'grid', placeItems:'center', flexShrink:0, color:T.inkSoft }}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
                    </button>
                    {!menuAddOpen && (
                      <button onClick={() => setMenuAddOpen(true)} title="Játékos hozzáadása" style={{ width:34, height:34, borderRadius:10, border:`1.5px dashed ${T.mint}`, background:'transparent', cursor:'pointer', display:'grid', placeItems:'center', flexShrink:0, color:T.mint, fontSize:19, fontWeight:800, lineHeight:1 }}>＋</button>
                    )}
                  </div>
                )}

                {/* Add player — offline jatekban (nincs szobakod-sor) itt a teljes
                    szelessegu trigger; online szobaban a trigger mar a szobakod
                    soraban van, itt csak a kinyitott urlap jelenik meg. */}
                <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
                  {!menuAddOpen ? (
                    !roomCode && (
                    <button onClick={() => setMenuAddOpen(true)} style={{ display:'flex', alignItems:'center', gap:10, padding:'13px 16px', borderRadius:14, border:`1.5px dashed ${T.mint}`, background:'transparent', cursor:'pointer', fontFamily:T.font, fontWeight:700, fontSize:14, color:T.mint }}>
                      <span style={{ fontSize:18, lineHeight:1 }}>＋</span>
                      <span>Játékos hozzáadása</span>
                    </button>
                    )
                  ) : (""",
    'szobakod sor + jatekos hozzaadas')

# ─── 3) Buntetes: teljes szelessegu sor helyett ikon-gomb a Vissza mellett ───
sub("""                {/* Büntetés — korty kiosztása játékon kívül (wildcard-szegés,
                    fogadás, bármi). Az itt kiosztott korty ugyanoda kerül, mint
                    a játékban szerzett, tehát a parti végén a statisztikába is. */}
                <button onClick={() => { setShowMenu(false); setPenaltyOpen(true); }} style={{ width:'100%', height:50, border:'none', borderRadius:16, background:`linear-gradient(135deg, #7C5CC4, #A78BFA)`, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14.5, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8, boxShadow:'0 4px 14px rgba(124,92,196,0.44)' }}>
                  <BohIcon name="beer" size={18} /><span>Büntetés — ki igyon?</span>
                </button>

                {/* Action buttons — A design: inline icon+text, Következő hangsúlyos */}
                <div style={{ display:'flex', gap:8 }}>
                  <button onClick={() => { undoLast(); setShowMenu(false); }} disabled={!undoRef.current}""",
    """                {/* Action buttons — Büntetés (ikon-csak, korty kiosztása játékon
                    kívül — wildcard-szegés, fogadás, bármi — az itt kiosztott korty
                    ugyanoda kerül, mint a játékban szerzett) a Vissza mellett, hogy
                    ne kelljen érte külön sort adni; Következő hangsúlyos */}
                <div style={{ display:'flex', gap:8 }}>
                  <button onClick={() => { setShowMenu(false); setPenaltyOpen(true); }} title="Büntetés — ki igyon?"
                    style={{ width:52, height:52, flexShrink:0, border:'none', borderRadius:16, background:`linear-gradient(135deg, #7C5CC4, #A78BFA)`, color:'#fff', cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', boxShadow:'0 4px 14px rgba(124,92,196,0.44)' }}>
                    <BohIcon name="beer" size={19} />
                  </button>
                  <button onClick={() => { undoLast(); setShowMenu(false); }} disabled={!undoRef.current}""",
    'buntetes gomb athelyezese')

sub("const APP_VERSION = 'v10.214';", "const APP_VERSION = 'v10.215';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — Vezerles ful: kompaktabb szobakod sor + Buntetes a Vissza mellett')
