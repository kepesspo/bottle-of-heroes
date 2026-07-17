#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Hangok + haptika kör:
#  - bohSound: némítás (localStorage boh_snd), új hangok: flip, tick, cheers, wildcard
#  - bohHaptic: rezgés ahol támogatott (Android), kapcsolható (boh_haptic)
#  - bekötések: érem pörgetés kattogás, Mit Választanál 3-2-1 tick, wildcard kártya
#    csengő, csoportos ivászat fanfár, result banner + szabályszegő haptika
#  - Beállítások: Hangeffektek + Rezgés kapcsolók a Splash toggle mellé
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'expected %d, found %d for: %r' % (count, n, old[:90])
    src = src.replace(old, new)

# 1) bohSound: némítás + új hangok
rep("""  return function (name) {
    const c = get(); if (!c) return;
    try {
      if (name === 'win')       { beep(c, 523, 0, 0.15, 0.22); beep(c, 659, 0.12, 0.15, 0.22); beep(c, 784, 0.24, 0.3, 0.26); }
      else if (name === 'lose')  { beep(c, 330, 0, 0.2, 0.24, 'triangle'); beep(c, 247, 0.18, 0.32, 0.24, 'triangle'); }
      else if (name === 'zsulli'){ beep(c, 880, 0, 0.11, 0.2); beep(c, 1108, 0.09, 0.11, 0.2); beep(c, 1318, 0.18, 0.26, 0.24); }
      else if (name === 'szelvihar') { whoosh(c, 0, 1.1, 0.45); }
      else if (name === 'alert') { beep(c, 988, 0, 0.1, 0.26, 'square'); beep(c, 988, 0.16, 0.1, 0.26, 'square'); }
    } catch (e) {}
  };
})();""",
"""  return function (name) {
    try { if (localStorage.getItem('boh_snd') === '0') return; } catch (e) {}
    const c = get(); if (!c) return;
    try {
      if (name === 'win')       { beep(c, 523, 0, 0.15, 0.22); beep(c, 659, 0.12, 0.15, 0.22); beep(c, 784, 0.24, 0.3, 0.26); }
      else if (name === 'lose')  { beep(c, 330, 0, 0.2, 0.24, 'triangle'); beep(c, 247, 0.18, 0.32, 0.24, 'triangle'); }
      else if (name === 'zsulli'){ beep(c, 880, 0, 0.11, 0.2); beep(c, 1108, 0.09, 0.11, 0.2); beep(c, 1318, 0.18, 0.26, 0.24); }
      else if (name === 'szelvihar') { whoosh(c, 0, 1.1, 0.45); }
      else if (name === 'alert') { beep(c, 988, 0, 0.1, 0.26, 'square'); beep(c, 988, 0.16, 0.1, 0.26, 'square'); }
      else if (name === 'flip')  { beep(c, 1150 + Math.random() * 250, 0, 0.035, 0.09, 'square'); }
      else if (name === 'tick')  { beep(c, 1050, 0, 0.07, 0.18, 'square'); }
      else if (name === 'cheers'){ beep(c, 523, 0, 0.12, 0.2); beep(c, 659, 0.1, 0.12, 0.2); beep(c, 784, 0.2, 0.12, 0.22); beep(c, 1046, 0.3, 0.32, 0.26); }
      else if (name === 'wildcard') { beep(c, 740, 0, 0.09, 0.2, 'triangle'); beep(c, 988, 0.08, 0.09, 0.2, 'triangle'); beep(c, 1244, 0.16, 0.24, 0.24, 'triangle'); }
    } catch (e) {}
  };
})();

// Haptika: rezgés ahol a böngésző támogatja (Android Chrome; iOS Safari nem adja ki).
window.bohHaptic = function (kind) {
  try {
    if (localStorage.getItem('boh_haptic') === '0') return;
    if (!navigator.vibrate) return;
    navigator.vibrate(kind === 'success' ? [20, 40, 20] : kind === 'error' ? 60 : 15);
  } catch (e) {}
};""")

# 2) Érem: kattogás minden pörgetési lépésnél
rep("""    const step = () => {
      current = current === 'fej' ? 'iras' : 'fej';
      // squish duration = 42% of current interval, so in/out always fit cleanly
      const squishDur = Math.round(interval * 0.42);""",
"""    const step = () => {
      current = current === 'fej' ? 'iras' : 'fej';
      if (typeof window.bohSound === 'function') window.bohSound('flip');
      // squish duration = 42% of current interval, so in/out always fit cleanly
      const squishDur = Math.round(interval * 0.42);""")

# 3) Mit Választanál: tick az utolsó 3 másodpercben (mindkét időzítőben)
rep("""    clearInterval(ivRef.current);
    const end = Date.now() + TOTAL_SECS * 1000;
    ivRef.current = setInterval(() => {
      const rem = Math.max(0, (end - Date.now()) / 1000);
      setTimeLeft(Math.ceil(rem));
      if (rem <= 0) { clearInterval(ivRef.current); setTimedOut(true); }
    }, 100);
  }, [gameIdx]);""",
"""    clearInterval(ivRef.current);
    const end = Date.now() + TOTAL_SECS * 1000;
    let lastSec = TOTAL_SECS + 1;
    ivRef.current = setInterval(() => {
      const rem = Math.max(0, (end - Date.now()) / 1000);
      const v = Math.ceil(rem);
      if (v !== lastSec && v <= 3 && v > 0 && typeof window.bohSound === 'function') window.bohSound('tick');
      lastSec = v;
      setTimeLeft(v);
      if (rem <= 0) { clearInterval(ivRef.current); setTimedOut(true); }
    }, 100);
  }, [gameIdx]);""")
rep("""  const startTimer = () => {
    clearInterval(ivRef.current);
    const end = Date.now() + TOTAL_SECS * 1000;
    ivRef.current = setInterval(() => {
      const rem = Math.max(0, (end - Date.now()) / 1000);
      setTimeLeft(Math.ceil(rem));
      if (rem <= 0) {
        clearInterval(ivRef.current);
        setTimedOut(true);
      }
    }, 100);
  };""",
"""  const startTimer = () => {
    clearInterval(ivRef.current);
    const end = Date.now() + TOTAL_SECS * 1000;
    let lastSec = TOTAL_SECS + 1;
    ivRef.current = setInterval(() => {
      const rem = Math.max(0, (end - Date.now()) / 1000);
      const v = Math.ceil(rem);
      if (v !== lastSec && v <= 3 && v > 0 && typeof window.bohSound === 'function') window.bohSound('tick');
      lastSec = v;
      setTimeLeft(v);
      if (rem <= 0) {
        clearInterval(ivRef.current);
        setTimedOut(true);
      }
    }, 100);
  };""")

# 4) Wildcard kártya: csengő + haptika a megjelenéskor
rep("""        if (isWildcardRound && wc) setActiveWildcard({ ...wc, round: newRound });""",
"""        if (isWildcardRound && wc) {
          setActiveWildcard({ ...wc, round: newRound });
          if (typeof window.bohSound === 'function') window.bohSound('wildcard');
          if (typeof window.bohHaptic === 'function') window.bohHaptic('success');
        }""")

# 5) Csoportos ivászat: fanfár + haptika
rep("""      groupDrinkDueRef.current = false;
      const diff = currentGame.difficulty;
      const drinks = diff === 'nehéz' ? 3 : diff === 'közepes' ? 2 : 1;
      setGroupDrinkOverlay({ drinks });""",
"""      groupDrinkDueRef.current = false;
      const diff = currentGame.difficulty;
      const drinks = diff === 'nehéz' ? 3 : diff === 'közepes' ? 2 : 1;
      setGroupDrinkOverlay({ drinks });
      if (typeof window.bohSound === 'function') window.bohSound('cheers');
      if (typeof window.bohHaptic === 'function') window.bohHaptic('success');""")

# 6) Result banner: haptika a meglévő win/lose hang mellé
rep("""    if (typeof window.bohSound === 'function') {
      const hasW = (res.winners || []).length > 0;
      const hasL = (res.losers || []).length > 0;
      const positive = hasW || (!hasL && scaled === 0 && res.correct !== false);
      window.bohSound(positive ? 'win' : 'lose');
    }""",
"""    if (typeof window.bohSound === 'function') {
      const hasW = (res.winners || []).length > 0;
      const hasL = (res.losers || []).length > 0;
      const positive = hasW || (!hasL && scaled === 0 && res.correct !== false);
      window.bohSound(positive ? 'win' : 'lose');
      if (typeof window.bohHaptic === 'function') window.bohHaptic(positive ? 'success' : 'error');
    }""")

# 7) Szabályszegő: haptika
rep("""    try { if (typeof window.bohSound === 'function') window.bohSound('lose'); } catch(e) {}
  };""",
"""    try { if (typeof window.bohSound === 'function') window.bohSound('lose'); } catch(e) {}
    try { if (typeof window.bohHaptic === 'function') window.bohHaptic('error'); } catch(e) {}
  };""")

# 8) Beállítások: Hangeffektek + Rezgés kapcsolók
rep("""  const [splashOn, setSplashOn] = React.useState(() => localStorage.getItem('boh_splash') !== '0');""",
"""  const [splashOn, setSplashOn] = React.useState(() => localStorage.getItem('boh_splash') !== '0');
  const [sndOn, setSndOn] = React.useState(() => { try { return localStorage.getItem('boh_snd') !== '0'; } catch(e) { return true; } });
  const [hapOn, setHapOn] = React.useState(() => { try { return localStorage.getItem('boh_haptic') !== '0'; } catch(e) { return true; } });
  const toggleSnd = () => { const n = !sndOn; setSndOn(n); try { localStorage.setItem('boh_snd', n ? '1' : '0'); } catch(e) {} if (n && typeof window.bohSound === 'function') window.bohSound('zsulli'); };
  const toggleHap = () => { const n = !hapOn; setHapOn(n); try { localStorage.setItem('boh_haptic', n ? '1' : '0'); } catch(e) {} if (n && typeof window.bohHaptic === 'function') window.bohHaptic('success'); };""")
rep("""                <Toggle on={splashOn} onChange={toggleSplash} />
              </div>

            </div>
          </SheetOverlay>
        )}""",
"""                <Toggle on={splashOn} onChange={toggleSplash} />
              </div>
              <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginTop:16 }}>
                <div>
                  <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>Hangeffektek</div>
                  <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>Nyerés, ivás, wildcard és játék hangok</div>
                </div>
                <Toggle on={sndOn} onChange={toggleSnd} />
              </div>
              <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginTop:16 }}>
                <div>
                  <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>Rezgés</div>
                  <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>Fontos eseményeknél — ahol a böngésző támogatja</div>
                </div>
                <Toggle on={hapOn} onChange={toggleHap} />
              </div>

            </div>
          </SheetOverlay>
        )}""")

# 9) Verziobump
rep("const APP_VERSION = 'v9.955';", "const APP_VERSION = 'v9.956';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — sound + haptics applied')
