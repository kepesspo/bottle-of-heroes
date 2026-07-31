#!/usr/bin/env python3
# v10.217 — MENÜ akciósor: makett szerinti csempe-stílus (ikon fent, felirat
# lent), a komponensek sorrendje/helye változatlan
#
# Eddig a 4 gomb egy vizszintes sorban ikon+szoveg volt egymas mellett —
# ebbe a hosszabb szavak ("Büntetés", "Következő") csak roviditve fertek
# be. A makett szerint a gombok magasabb, negyzetesebb csempek: az ikon
# FENT, a felirat ALATTA — igy a teljes szo kifer roviditett alak nelkul.
#
# A csempek pasztell, akcio-szinu hattert kapnak (mint a makett), a szoveg
# szine kovet — Buntetes lila, Ujra T.ink/T.bgSoft (valtozatlan), Kovetkezo
# menta. A Vissza tiltott/aktiv allapota valtozatlan logikaval.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("    nextBtn: 'Kövi',", "    nextBtn: 'Következő',", 'nextBtn vissza a teljes alakra')

sub("""                {/* Action buttons — Büntetés (ikon-csak, korty kiosztása játékon
                    kívül — wildcard-szegés, fogadás, bármi — az itt kiosztott korty
                    ugyanoda kerül, mint a játékban szerzett) a Vissza mellett, hogy
                    ne kelljen érte külön sort adni; Következő hangsúlyos */}
                <div style={{ display:'flex', gap:8 }}>
                  <button onClick={() => { setShowMenu(false); setPenaltyOpen(true); }}
                    style={{ flex:1, height:52, border:'none', borderRadius:16, background:`linear-gradient(135deg, #7C5CC4, #A78BFA)`, color:'#fff',
                      fontFamily:T.font, fontWeight:800, fontSize:14, cursor:'pointer',
                      display:'flex', alignItems:'center', justifyContent:'center', gap:7,
                      boxShadow:'0 4px 14px rgba(124,92,196,0.44)' }}>
                    <BohIcon name="beer" size={17} /><span>Büntetés</span>
                  </button>
                  <button onClick={() => { undoLast(); setShowMenu(false); }} disabled={!undoRef.current}
                    style={{ flex:1, height:52, border:'none', borderRadius:16,
                      background: undoRef.current ? T.bgSoft : T.surfaceMuted,
                      color: undoRef.current ? T.ink : T.inkMute,
                      fontFamily:T.font, fontWeight:800, fontSize:14,
                      cursor: undoRef.current ? 'pointer' : 'default',
                      display:'flex', alignItems:'center', justifyContent:'center', gap:7,
                      opacity: undoRef.current ? 1 : 0.5 }}>
                    <BohIcon name="back" size={17} /><span>{t('backBtn')}</span>
                  </button>
                  <button onClick={() => { setPendingCommit(null); setGameRestartKey(k=>k+1); setShowMenu(false); }}
                    style={{ flex:1, height:52, border:'none', borderRadius:16,
                      background:T.bgSoft, color:T.ink,
                      fontFamily:T.font, fontWeight:800, fontSize:14, cursor:'pointer',
                      display:'flex', alignItems:'center', justifyContent:'center', gap:7 }}>
                    <BohIcon name="redo" size={17} /><span>{t('again')}</span>
                  </button>
                  <button onClick={() => { setGameIdx(g=>g+1); setShowMenu(false); }}
                    style={{ flex:1, height:52, border:'none', borderRadius:16,
                      background:T.mint, color:'#fff',
                      fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer',
                      display:'flex', alignItems:'center', justifyContent:'center', gap:8,
                      boxShadow:`0 4px 14px ${T.mint}44` }}>
                    <BohIcon name="next" size={17} /><span>{t('nextBtn')}</span>""",
    """                {/* Action buttons — csempe-stílus (ikon fent, felirat lent), hogy a
                    teljes szavak ("Büntetés", "Következő") is kiférjenek rövidítés
                    nélkül. Büntetés: korty kiosztása játékon kívül (wildcard-szegés,
                    fogadás, bármi) — az itt kiosztott korty ugyanoda kerül, mint a
                    játékban szerzett. */}
                <div style={{ display:'flex', gap:8 }}>
                  <button onClick={() => { setShowMenu(false); setPenaltyOpen(true); }}
                    style={{ flex:1, height:76, border:'none', borderRadius:18, background:'#7C5CC41f', color:'#7C5CC4',
                      fontFamily:T.font, fontWeight:800, fontSize:12, cursor:'pointer',
                      display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:6 }}>
                    <BohIcon name="beer" size={21} /><span>Büntetés</span>
                  </button>
                  <button onClick={() => { undoLast(); setShowMenu(false); }} disabled={!undoRef.current}
                    style={{ flex:1, height:76, border:'none', borderRadius:18,
                      background: undoRef.current ? T.bgSoft : T.surfaceMuted,
                      color: undoRef.current ? T.ink : T.inkMute,
                      fontFamily:T.font, fontWeight:800, fontSize:12,
                      cursor: undoRef.current ? 'pointer' : 'default',
                      display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:6,
                      opacity: undoRef.current ? 1 : 0.5 }}>
                    <BohIcon name="back" size={21} /><span>{t('backBtn')}</span>
                  </button>
                  <button onClick={() => { setPendingCommit(null); setGameRestartKey(k=>k+1); setShowMenu(false); }}
                    style={{ flex:1, height:76, border:'none', borderRadius:18,
                      background:T.bgSoft, color:T.ink,
                      fontFamily:T.font, fontWeight:800, fontSize:12, cursor:'pointer',
                      display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:6 }}>
                    <BohIcon name="redo" size={21} /><span>{t('again')}</span>
                  </button>
                  <button onClick={() => { setGameIdx(g=>g+1); setShowMenu(false); }}
                    style={{ flex:1, height:76, border:'none', borderRadius:18,
                      background:T.mint+'1f', color:T.mintDeep||T.mint,
                      fontFamily:T.font, fontWeight:900, fontSize:12, cursor:'pointer',
                      display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:6 }}>
                    <BohIcon name="next" size={21} /><span>{t('nextBtn')}</span>""",
    'akciosor csempe-stilus')

sub("const APP_VERSION = 'v10.216';", "const APP_VERSION = 'v10.217';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — akciosor csempe-stilussal, teljes szavakkal')
