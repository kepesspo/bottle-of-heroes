#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Toast-generátor: a menüből egy gombra személyre szabott köszöntő/beszólás a
# játékosok adataiból; felugró a kabalával, és a műsorvezető (TTS) fel is olvassa.
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'expected %d, found %d for: %r' % (count, n, old[:80])
    src = src.replace(old, new)

# ── 1) state ──
rep("  const [showMenu, setShowMenu] = useState(false);",
    "  const [showMenu, setShowMenu] = useState(false);\n  const [toastText, setToastText] = useState(null);")

# ── 2) genToast generátor a return elé (advanceLoverseny után) ──
rep("""    setPendingCommit({ newPlayers, fb, newTurn:(turn+1)%Math.max(activePlayers.length,1), newGameIdx:gameIdx+1, newRound:round+1 });
  };

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background: T.bg, paddingBottom:'max(14px, env(safe-area-inset-bottom))' }}>""",
"""    setPendingCommit({ newPlayers, fb, newTurn:(turn+1)%Math.max(activePlayers.length,1), newGameIdx:gameIdx+1, newRound:round+1 });
  };

  // Toast-generátor — a játékosok aktuális állásából gyárt egy köszöntőt/beszólást
  const genToast = () => {
    const act = (players || []).filter(p => p && p.active !== false);
    if (!act.length) return 'Emeljük poharunkat — egészségünkre!';
    const byPts = [...act].sort((a,b) => (b.points||0)-(a.points||0));
    const byDr  = [...act].sort((a,b) => (b.drinks||0)-(a.drinks||0));
    const leader = byPts[0], drunk = byDr[0];
    const rnd = () => act[Math.floor(Math.random()*act.length)];
    const r1 = rnd(), r2 = rnd();
    const opts = [
      'Emeljük poharunkat! ' + leader.name + ' vezet — de az este még fiatal!',
      drunk.name + ' ma már ' + (drunk.drinks||0) + ' kortyot ledöntött. Legenda vagy csak szomjas? Egészségére!',
      r1.name + ', te vagy a társaság lelke. Vagy legalábbis a leghangosabb. Csirió!',
      'Igyunk mindannyian ' + r1.name + ' egészségére — mert megérdemli, és mert úgyis rákényszerítjük!',
      leader.name + ' vezet, ' + drunk.name + ' iszik — mindenki nyer! Egészségünkre!',
      'Koccintsunk arra, hogy holnap már senki sem emlékszik erre a köszöntőre. Fenékig!',
      'Emeljük poharunkat a barátságra, a rossz döntésekre és ' + drunk.name + ' májára!',
      r1.name + ' nélkül sokkal kevesebb baj lenne ma este — pont ezért, csirió!',
      'Egy régi mondás szerint aki utoljára áll, az nyert. ' + r2.name + ', neked szurkolunk! Egészségedre!',
      'Igyunk a mai estére, a holnapi fejfájásra, és arra, hogy ' + leader.name + ' végre veszítsen egyet!',
    ];
    return opts[Math.floor(Math.random()*opts.length)];
  };
  const fireToast = () => {
    const tx = genToast();
    setToastText(tx);
    try { if (typeof window.bohSpeak === 'function') window.bohSpeak(tx); } catch(e) {}
  };

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background: T.bg, paddingBottom:'max(14px, env(safe-area-inset-bottom))' }}>""")

# ── 3) Gomb a menü vezérlés tabjába (add-player után, az akciógombok elé) ──
rep("""                {/* Action buttons — A design: inline icon+text, Következő hangsúlyos */}
                <div style={{ display:'flex', gap:8 }}>
                  <button onClick={() => { undoLast(); setShowMenu(false); }} disabled={!undoRef.current}""",
"""                {/* Koccintó — köszöntő generátor + TTS felolvasás */}
                <button onClick={() => { setShowMenu(false); fireToast(); }} style={{ width:'100%', height:50, border:'none', borderRadius:16, background:`linear-gradient(135deg, ${T.yellow}, ${T.coral})`, color:'#1A2A4A', fontFamily:T.font, fontWeight:900, fontSize:14.5, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8, boxShadow:`0 4px 14px ${T.coral}44` }}>
                  <span style={{ fontSize:18, lineHeight:1 }}>🥂</span><span>Koccintó — mondj egy köszöntőt!</span>
                </button>

                {/* Action buttons — A design: inline icon+text, Következő hangsúlyos */}
                <div style={{ display:'flex', gap:8 }}>
                  <button onClick={() => { undoLast(); setShowMenu(false); }} disabled={!undoRef.current}""")

# ── 4) Toast felugró (a csoportos ivászat overlay elé) ──
rep("""      {groupDrinkOverlay && (""",
"""      {toastText && (
        <div onClick={() => setToastText(null)} style={{ position:'fixed', inset:0, background:'rgba(14,14,24,0.72)', zIndex:60, display:'flex', alignItems:'center', justifyContent:'center', padding:28, animation:'fadeIn .2s' }}>
          <div onClick={e => e.stopPropagation()} style={{ background:T.surface, borderRadius:28, padding:'26px 24px 22px', width:'100%', maxWidth:360, display:'flex', flexDirection:'column', alignItems:'center', gap:12, boxShadow:'0 24px 64px rgba(0,0,0,0.3)', animation:'popIn .3s cubic-bezier(.2,.9,.3,1.3)' }}>
            <BottleHero pose="win" size={68} style={{ filter:'drop-shadow(0 4px 10px rgba(0,0,0,0.18))', animation:'floatBob 2.6s ease-in-out infinite' }} />
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:T.coral, textTransform:'uppercase', letterSpacing:'0.14em' }}>Koccintó 🥂</div>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:18, color:T.ink, textAlign:'center', lineHeight:1.38 }}>{toastText}</div>
            <div style={{ display:'flex', gap:10, width:'100%', marginTop:6 }}>
              <button onClick={fireToast} style={{ flex:1, padding:'13px 0', borderRadius:14, border:'none', background:T.surfaceMuted, color:T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:14, cursor:'pointer' }}>Másikat!</button>
              <button onClick={() => setToastText(null)} style={{ flex:1.4, padding:'13px 0', borderRadius:14, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer' }}>Egészségünkre!</button>
            </div>
          </div>
        </div>
      )}
      {groupDrinkOverlay && (""")

# ── 5) Verziobump ──
rep("const APP_VERSION = 'v9.977';", "const APP_VERSION = 'v9.978';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — toast generator applied')
