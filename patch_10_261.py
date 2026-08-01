#!/usr/bin/env python3
# v10.261 — Szerencsekerék: egy körben egyszer lehet pörgetni
#
# A gomb eddig CSAK pörgés közben volt letiltva (`disabled={phase === 'spinning'}`).
# Amint a kerék megállt, a felirat visszaváltott „PÖRGESS!"-re, és újra lehetett
# nyomni. Ez nem csak kozmetikai hiba volt:
#
#   - az új pörgés kinullázta a kiválasztottat (eltűnt az eredmény-kártya),
#   - és a végén MÉGEGYSZER lefutott az onResult + onAdvance, vagyis a korty
#     kétszer került kiosztásra.
#
# Két helyen zárom le, hogy egyik se maradjon rés:
#   1. a gomb már az eredmény alatt is letiltva („MEGVAN"), és a spin() csak
#      'ready' fázisból indul (nem csak a 'spinning'-et zárja ki),
#   2. az onResult/onAdvance egy ref-fel őrizve fut le EGYSZER — ha bármi
#      mégis újraindítaná a kört, a korty akkor sem osztódik ki kétszer.
#
# Új körnél (gameIdx változás) mindkettő visszaáll.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1. ref az egyszeri kiosztashoz + visszaallitas uj kornel ──
sub("""  const [winner, setWinner] = React.useState(null);
  const timerRef = React.useRef(null);

  React.useEffect(() => {
    setPhase('ready'); setWinner(null); setRotation(0);
  }, [gameIdx]);""",
    """  const [winner, setWinner] = React.useState(null);
  const timerRef = React.useRef(null);
  // A korty EGYSZER osztodik ki egy korben. A gomb letiltasa mellett ez a
  // masodik zar — ha barmi megis ujrainditana a port, itt akkor is elakad.
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    setPhase('ready'); setWinner(null); setRotation(0);
    advancedRef.current = false;
  }, [gameIdx]);""",
    'advancedRef')

# ── 2. a spin csak 'ready' fazisbol indul ──
sub("""  const spin = () => {
    if (phase === 'spinning' || players.length === 0) return;""",
    """  const spin = () => {
    // CSAK a 'ready' fazisbol — a 'result'-bol indulo ujrapörgetes masodszor is
    // kiosztotta volna a kortyot.
    if (phase !== 'ready' || players.length === 0) return;""",
    'spin ready')

sub("""      timerRef.current = setTimeout(() => {
        if (w) {
          onResult && onResult({ correct: false, playerName: w.name, drinks: 1, subtitle: w.name + ' iszik egyet!' });
          onAdvance && onAdvance({ [w.id]: 1 });
        }
      }, 700);""",
    """      timerRef.current = setTimeout(() => {
        if (w && !advancedRef.current) {
          advancedRef.current = true;
          onResult && onResult({ correct: false, playerName: w.name, drinks: 1, subtitle: w.name + ' iszik egyet!' });
          onAdvance && onAdvance({ [w.id]: 1 });
        }
      }, 700);""",
    'egyszeri kiosztas')

# ── 3. a gomb az eredmeny alatt is letiltva ──
sub("""        <button onClick={spin} disabled={phase === 'spinning'}
          style={{ position:'absolute', top:26 * k + R, left:'50%', transform:'translate(-50%,-50%)', zIndex:2,
                   width:Math.round(92 * k), height:Math.round(92 * k), borderRadius:'50%', border:'none', background:T.surface,
                   boxShadow:T.shadow, cursor: phase === 'spinning' ? 'default' : 'pointer',""",
    """        <button onClick={spin} disabled={phase !== 'ready'}
          style={{ position:'absolute', top:26 * k + R, left:'50%', transform:'translate(-50%,-50%)', zIndex:2,
                   width:Math.round(92 * k), height:Math.round(92 * k), borderRadius:'50%', border:'none', background:T.surface,
                   boxShadow:T.shadow, cursor: phase === 'ready' ? 'pointer' : 'default',""",
    'gomb letiltas')

sub("""          <svg width={Math.round(24 * k)} height={Math.round(24 * k)} viewBox="0 0 24 24" fill="none" stroke={T.coral} strokeWidth="2.4"
               strokeLinecap="round" strokeLinejoin="round"
               style={{ animation: phase === 'spinning' ? 'spin 1s linear infinite' : 'none' }}>
            <path d="M20 12a8 8 0 1 1-2.6-5.9" /><path d="M20 4v4.5h-4.5" />
          </svg>
          <span style={{ fontFamily:T.font, fontWeight:900, fontSize:Math.round(11 * k), color:T.coral, letterSpacing:'0.06em' }}>
            {phase === 'spinning' ? 'PÖRÖG…' : 'PÖRGESS!'}
          </span>""",
    """          <svg width={Math.round(24 * k)} height={Math.round(24 * k)} viewBox="0 0 24 24" fill="none"
               stroke={phase === 'result' ? T.inkMute : T.coral} strokeWidth="2.4"
               strokeLinecap="round" strokeLinejoin="round"
               style={{ animation: phase === 'spinning' ? 'spin 1s linear infinite' : 'none' }}>
            <path d="M20 12a8 8 0 1 1-2.6-5.9" /><path d="M20 4v4.5h-4.5" />
          </svg>
          <span style={{ fontFamily:T.font, fontWeight:900, fontSize:Math.round(11 * k),
                         color: phase === 'result' ? T.inkMute : T.coral, letterSpacing:'0.06em' }}>
            {phase === 'spinning' ? 'PÖRÖG…' : phase === 'result' ? 'MEGVAN' : 'PÖRGESS!'}
          </span>""",
    'gomb felirat')

sub("const APP_VERSION = 'v10.260';", "const APP_VERSION = 'v10.261';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — egy korben egyszer lehet porgetni')
