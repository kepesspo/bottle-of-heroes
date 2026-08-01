#!/usr/bin/env python3
# v10.270 — D1: a fejlecben a TET all a jobb felso sarokban, a kor atkoltozik
#           a korvalto kepernyore (es ott vegre a limitet is megmutatja)
#
# MIERT
#   A fejlec 114 px volt: info balra, banner kozepen, es egy LELOGO kapszula
#   jobbra (kor-gyuru + korty + nehezseg-talp). A kapszula miatt a fejlec
#   48 px-szel melyebb volt, mint amennyi tartalom volt benne.
#
#   A korszam a fejlecben ket okbol nem ert sokat:
#     1. a `maxRounds` alapertelmezese `null` (vegtelen), es vegtelen modban a
#        gyuru ivenek nincs jelentese — a roundPct 0, tehat a haladasjelzo,
#        ami a gyuru letjogosultsaga lenne, alapbol nem csinal semmit;
#     2. a fejlec sosem irta ki a nevezot ("KOR 15", nem "15/20"), tehat a szam
#        nem valaszolt arra, hogy hol tartunk.
#   Kozben a korvaltas MAR EDDIG IS bemondasra kerult: 2 masodperces, teljes
#   kepernyos "15. KOR" felirat, alapbol bekapcsolva (showRoundCounter !== false).
#
# MI VALTOZIK
#   1. FEJLEC — a jobb felso sarokban a TET all, a mostani gyuru formanyelveben:
#      54 px-es korong, benne a korty-szam + "KORTY", a nehezseget a GYURU SZINE
#      hordozza (a korabbi szines talp helyett). Semmi nem log le, tehat a
#      paddingBottom:48 is elmarad -> a fejlec ~110 px-rol ~74 px-re fogy, es a
#      banner megtarthatja a teljes meretet.
#   2. KORVALTO KEPERNYO — ha van korlimit, a nagy szam alatt megjelenik egy
#      csik + "20-bol · meg 5 kor". Vegtelen modban valtozatlan (nincs mit
#      mutatni). Ez TOBB, mint amit a fejlec valaha adott.
#
# EGY TUDATOS KIVETEL
#   8 jateknak nincs deklaralt tetje (stake: null — blackjack, busz, beerpong,
#   loverseny, ringfire, powerhour, ovfj, farkasos), mert naluk a korty-szam
#   dinamikus. Naluk a jobb felso sarok a REGI kor-gyurut kapja: ott a kor az
#   egyetlen ertelmes fejlec-adat, es igy egyik jateknal sem marad ures a sarok.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─────────────────────────────────────────────────────────────────────────────
# 1. A fejlec mar nem foglal helyet a lelogo kapszulanak
# ─────────────────────────────────────────────────────────────────────────────
sub("""      {/* ── Top bar ── */}
      {/* A korty-kapszula lelog a gyuru ala. Ha csak "rálógna" a tartalomra,
          letakarna a jatekleirasok jobb veget — ezert a fejlec foglal neki
          helyet. Latvanyban ugyanaz, csak nem takar semmit. */}
      <div style={{ flexShrink:0, display:'flex', alignItems:'center', gap:8, paddingTop:12, paddingBottom: stakeText ? 48 : 6, paddingLeft:16, paddingRight:16, maxWidth:960, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>""",
    """      {/* ── Top bar ── */}
      {/* v10.270: mar semmi nem log le a fejlec ala. A tet a jobb felso sarokban
          egy 54 px-es korongban ul (a nehezseget a gyuru SZINE hordozza), tehat
          nem kell 48 px-et foglalni egy tulnyulo kapszulanak. Lasd patch_10_270.py */}
      <div style={{ flexShrink:0, display:'flex', alignItems:'center', gap:8, paddingTop:12, paddingBottom:6, paddingLeft:16, paddingRight:16, maxWidth:960, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>""",
    'fejlec padding')

# ─────────────────────────────────────────────────────────────────────────────
# 2. A jobb felso slot: TET-korong, ill. kor-gyuru azoknal, ahol nincs tet
# ─────────────────────────────────────────────────────────────────────────────
OLD_CAP = """          const maxRounds = gameMeta?.maxRounds || null;
          const isInfinite = !maxRounds;
          const roundPct = maxRounds ? Math.min(1, (round - 1) / maxRounds) : 0;
          const rOuter = 25, circOuter = +(2 * Math.PI * rOuter).toFixed(1);
          const dashOuter = +(circOuter * roundPct).toFixed(1);
          const rInner = 19, circInner = +(2 * Math.PI * rInner).toFixed(1);
          const ringColor = isInfinite ? T.coral : (roundPct > 0.75 ? T.coral : roundPct > 0.5 ? T.yellow : T.mint);
          // A kapszula LELOG a fejlec ala: a sorban csak 54 px magas helyet
          // foglal, a tobbi tulnyulik. Ezert kell a pozicionalt kontener.
          const capW = stakeText ? 60 : 54;
          return (
            <div style={{ position:'relative', width:capW, height:54, flexShrink:0, zIndex:6 }}>
            <div onClick={stakeText ? () => setStakeInfo(true) : undefined}
                 style={{ position:'absolute', top:0, left:'50%', transform:'translateX(-50%)', width:capW,
                          display:'flex', flexDirection:'column', alignItems:'center',
                          ...(stakeText ? { background:T.surface, borderRadius:'30px 30px 14px 14px',
                                            boxShadow:'0 2px 10px rgba(20,30,50,0.16)', paddingTop:3,
                                            overflow:'hidden', cursor:'pointer' } : {}) }}>
            <div style={{ position:'relative', width:54, height:54, flexShrink:0 }}>"""

NEW_CAP = """          // ── v10.270 · A TET a jobb felso sarokban ──
          // Ha a jateknak van deklaralt tetje, a korong a KORTY-szamot mutatja,
          // es a nehezseget a gyuru szine hordozza. Ha nincs (stake: null — a
          // korty ott dinamikus), visszaesunk a regi kor-gyurure: annal a 8
          // jateknal a kor az egyetlen ertelmes fejlec-adat.
          if (stakeText) {
            const toneStake = wcMult > 1 ? T.yellow : diffMeta.tone;
            // Hosszabb tartomanynal ("10–12") kisebb szamot hasznalunk, hogy
            // ne feszuljon neki a 44 px-es belso koronak.
            const stakeFs = String(stakeText).length > 3 ? 14 : String(stakeText).length > 2 ? 16 : 19;
            return (
              <div onClick={() => setStakeInfo(true)}
                   title={`${diffMeta.label} ×${stakeMult}`}
                   style={{ position:'relative', width:54, height:54, flexShrink:0, cursor:'pointer',
                            filter:'drop-shadow(0 2px 0 rgba(20,30,50,0.10)) drop-shadow(0 2px 6px rgba(20,30,50,0.14))' }}>
                <svg viewBox="0 0 54 54" style={{ position:'absolute', inset:0, width:'100%', height:'100%' }}>
                  <circle cx="27" cy="27" r="25" fill="none" stroke={toneStake} strokeWidth="4" />
                </svg>
                <div style={{ position:'absolute', inset:5, background:T.surface, borderRadius:'50%',
                              display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:1 }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:stakeFs, lineHeight:1,
                                 letterSpacing:'-0.03em', color: wcMult > 1 ? '#8A6A08' : T.ink,
                                 fontVariantNumeric:'tabular-nums' }}>{stakeText}</span>
                  <span style={{ fontFamily:T.font, fontWeight:800, fontSize:7, letterSpacing:'0.1em',
                                 textTransform:'uppercase', color:T.inkMute, lineHeight:1 }}>korty</span>
                </div>
              </div>
            );
          }
          const maxRounds = gameMeta?.maxRounds || null;
          const isInfinite = !maxRounds;
          const roundPct = maxRounds ? Math.min(1, (round - 1) / maxRounds) : 0;
          const rOuter = 25, circOuter = +(2 * Math.PI * rOuter).toFixed(1);
          const dashOuter = +(circOuter * roundPct).toFixed(1);
          const rInner = 19, circInner = +(2 * Math.PI * rInner).toFixed(1);
          const ringColor = isInfinite ? T.coral : (roundPct > 0.75 ? T.coral : roundPct > 0.5 ? T.yellow : T.mint);
          return (
            <div style={{ position:'relative', width:54, height:54, flexShrink:0, zIndex:6 }}>
            <div style={{ position:'absolute', top:0, left:'50%', transform:'translateX(-50%)', width:54,
                          display:'flex', flexDirection:'column', alignItems:'center' }}>
            <div style={{ position:'relative', width:54, height:54, flexShrink:0 }}>"""

sub(OLD_CAP, NEW_CAP, 'tet-korong')

# ── a regi, lelogo tet-blokk (korty-szam + szines talp) mar nem kell:
#    a kor-gyuru aganal per definicionem nincs stakeText.
OLD_FOOT = """            {/* ── a TÉT: korty-szam + a nehezseg szines talpon ── */}
            {stakeText && (
              <React.Fragment>
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, lineHeight:1.1, letterSpacing:'-0.03em',
                               color: wcMult > 1 ? '#8A6A08' : T.ink, fontVariantNumeric:'tabular-nums' }}>{stakeText}</span>
                <span style={{ fontFamily:T.font, fontWeight:800, fontSize:7.5, letterSpacing:'0.1em',
                               textTransform:'uppercase', color:T.inkMute, lineHeight:1 }}>korty</span>
                <span style={{ width:'100%', textAlign:'center', marginTop:3, padding:'4px 2px 4.5px',
                               background: wcMult > 1 ? T.yellow : diffMeta.tone, color:'#12233C',
                               fontFamily:T.font, fontWeight:900, fontSize:7.5, letterSpacing:'0.02em',
                               textTransform:'uppercase', lineHeight:1, fontVariantNumeric:'tabular-nums' }}>
                  {diffMeta.label} ×{stakeMult}
                </span>
              </React.Fragment>
            )}
            </div>"""
sub(OLD_FOOT, """            </div>""", 'regi lelogo talp')

# ─────────────────────────────────────────────────────────────────────────────
# 3. Korvalto kepernyo: ha van korlimit, mutassuk meg, hol tartunk
# ─────────────────────────────────────────────────────────────────────────────
sub("""                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:64, color:'#fff', lineHeight:1, textShadow:'0 4px 24px rgba(0,0,0,0.4)', letterSpacing:'-0.02em' }}>{roundPopup.round}. {t('roundWord')}</div>""",
    """                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:64, color:'#fff', lineHeight:1, textShadow:'0 4px 24px rgba(0,0,0,0.4)', letterSpacing:'-0.02em' }}>{roundPopup.round}. {t('roundWord')}</div>
                  {/* v10.270 · A korszam kikerult a fejlecbol, tehat a HALADAS itt
                      jelenik meg — de csak ha van mihez merni. Vegtelen modban
                      (ez az alapertek) nincs mit mutatni, ilyenkor semmi nem valtozik. */}
                  {(() => {
                    const mr = gameMeta?.maxRounds || null;
                    if (!mr) return null;
                    const left = Math.max(0, mr - roundPopup.round);
                    const pct = Math.max(0, Math.min(1, roundPopup.round / mr));
                    return (
                      <div style={{ marginTop:14, display:'inline-flex', flexDirection:'column', alignItems:'center', gap:8,
                                    background:'rgba(255,255,255,0.16)', border:'1.5px solid rgba(255,255,255,0.28)',
                                    borderRadius:16, padding:'10px 18px', backdropFilter:'blur(8px)' }}>
                        <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, letterSpacing:'0.1em',
                                       textTransform:'uppercase', color:'rgba(255,255,255,0.85)' }}>
                          <b style={{ color:'#fff' }}>{mr}</b>-ból{left > 0 ? <React.Fragment> · még <b style={{ color:'#fff' }}>{left}</b> kör</React.Fragment> : ' · ez az utolsó'}
                        </span>
                        <div style={{ width:190, maxWidth:'100%', height:7, borderRadius:4, background:'rgba(255,255,255,0.28)', overflow:'hidden' }}>
                          <div style={{ width:(pct * 100) + '%', height:'100%', borderRadius:4, background:'#fff', transition:'width .4s ease' }} />
                        </div>
                      </div>
                    );
                  })()}""",
    'korlimit a popupon')

sub("const APP_VERSION = 'v10.269';", "const APP_VERSION = 'v10.270';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — D1: tet-korong a fejlecben, korlimit a korvalto kepernyon')
