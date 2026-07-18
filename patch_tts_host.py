#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Hangos műsorvezető (TTS): böngészős beszédszintézis, magyar hanggal.
# Bekapcsolható a Játékmenet sheetről; bekonferálja a kört, wildcardot, eredményt, csoportos ivászatot.
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'expected %d, found %d for: %r' % (count, n, old[:80])
    src = src.replace(old, new)

# ── 1) window.bohSpeak helper a bohHaptic után ──
rep("""window.bohHaptic = function (kind) {
  try {
    if (localStorage.getItem('boh_haptic') === '0') return;
    if (!navigator.vibrate) return;
    navigator.vibrate(kind === 'success' ? [20, 40, 20] : kind === 'error' ? 60 : 15);
  } catch (e) {}
};""",
"""window.bohHaptic = function (kind) {
  try {
    if (localStorage.getItem('boh_haptic') === '0') return;
    if (!navigator.vibrate) return;
    navigator.vibrate(kind === 'success' ? [20, 40, 20] : kind === 'error' ? 60 : 15);
  } catch (e) {}
};

// Hangos műsorvezető — böngészős TTS, lehetőleg magyar hanggal
window.bohSpeak = (function () {
  var voice = null;
  function pick() {
    try {
      var vs = (window.speechSynthesis && window.speechSynthesis.getVoices()) || [];
      voice = vs.filter(function (v) { return /^hu/i.test(v.lang); })[0] || null;
    } catch (e) {}
  }
  try { if (window.speechSynthesis) { window.speechSynthesis.onvoiceschanged = pick; pick(); } } catch (e) {}
  return function (text, opts) {
    try {
      if (!window.speechSynthesis || !text) return;
      var u = new SpeechSynthesisUtterance(String(text));
      u.lang = 'hu-HU';
      if (!voice) pick();
      if (voice) u.voice = voice;
      u.rate = (opts && opts.rate) || 1.03;
      u.pitch = (opts && opts.pitch) || 1.05;
      u.volume = (opts && typeof opts.volume === 'number') ? opts.volume : 1;
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(u);
    } catch (e) {}
  };
})();""")

# ── 2) Toggle a Játékmenet sheet "Egyéb" szekciójába (hydration után) ──
rep("""      <ToggleRow
        icon="drop"
        label={t('hydroBreak')}
        value={!!meta.hydrationReminder}
        onChange={() => setMeta({...meta, hydrationReminder: !meta.hydrationReminder})}
        infoKey="hydration"
        infoText="30 percenként megjelenik egy 'Igyál egy pohár vizet!' értesítés. 60 másodpercig nem lehet eltüntetni — addig a játék szünetel."
      />
    </div>
  );
}""",
"""      <ToggleRow
        icon="drop"
        label={t('hydroBreak')}
        value={!!meta.hydrationReminder}
        onChange={() => setMeta({...meta, hydrationReminder: !meta.hydrationReminder})}
        infoKey="hydration"
        infoText="30 percenként megjelenik egy 'Igyál egy pohár vizet!' értesítés. 60 másodpercig nem lehet eltüntetni — addig a játék szünetel."
      />
      <ToggleRow
        icon="party"
        label="Hangos műsorvezető"
        value={!!meta.ttsHost}
        onChange={() => {
          const next = !meta.ttsHost;
          setMeta({...meta, ttsHost: next});
          // Bekapcsoláskor egy koppintáson belül megszólal → iOS-en is feloldja a beszédet
          if (next && typeof window.bohSpeak === 'function') window.bohSpeak('Műsorvezető bekapcsolva!');
        }}
        infoKey="ttshost"
        infoText="A telefon hangosan bekonferálja a köröket, a wildcardokat és az eredményeket. (A böngésző beszédszintézisét használja — magyar hanggal, ahol elérhető.)"
      />
    </div>
  );
}""")

# ── 3) onResult: eredmény bekonferálása ──
rep("""    if (typeof window.bohSound === 'function') {
      const hasW = (res.winners || []).length > 0;
      const hasL = (res.losers || []).length > 0;
      const positive = hasW || (!hasL && scaled === 0 && res.correct !== false);
      window.bohSound(positive ? 'win' : 'lose');
      if (typeof window.bohHaptic === 'function') window.bohHaptic(positive ? 'success' : 'error');
    }""",
"""    if (typeof window.bohSound === 'function') {
      const hasW = (res.winners || []).length > 0;
      const hasL = (res.losers || []).length > 0;
      const positive = hasW || (!hasL && scaled === 0 && res.correct !== false);
      window.bohSound(positive ? 'win' : 'lose');
      if (typeof window.bohHaptic === 'function') window.bohHaptic(positive ? 'success' : 'error');
    }
    if (gameMeta?.ttsHost && typeof window.bohSpeak === 'function') {
      const nm = x => typeof x === 'string' ? x : (x && x.name) || '';
      const wn = (r.winners || []).map(nm).filter(Boolean);
      const ls = (r.losers || []).map(nm).filter(Boolean);
      let say = wcEffect === 'reverse' ? 'Fordított kör! ' : wcEffect === 'double' ? 'Dupla kör! ' : '';
      if (wn.length) say += wn.join(', ') + (wn.length > 1 ? ' nyertek! ' : ' nyert! ');
      if (ls.length) say += ls.join(', ') + (ls.length > 1 ? ' isznak' : ' iszik') + (scaled > 0 ? ' ' + scaled + ' kortyot' : '') + '!';
      else if (!wn.length && r.subtitle) say += r.subtitle;
      if (say.trim()) window.bohSpeak(say);
    }""")

# ── 4) Kör + wildcard bekonferálása a commitRound aktiválásnál ──
rep("""        if (isWildcardRound && wc) {
          setActiveWildcard({ ...wc, round: newRound });
          if (typeof window.bohSound === 'function') window.bohSound('wildcard');
          if (typeof window.bohHaptic === 'function') window.bohHaptic('success');""",
"""        if (isWildcardRound && wc) {
          setActiveWildcard({ ...wc, round: newRound });
          if (typeof window.bohSound === 'function') window.bohSound('wildcard');
          if (typeof window.bohHaptic === 'function') window.bohHaptic('success');
          if (gameMeta?.ttsHost && typeof window.bohSpeak === 'function') window.bohSpeak('Wildcard kör! ' + (wc.text || ''));""")
# lucky bekonferálás
rep("""              setPlayers(prev => prev.map(p => p.id === lucky.id ? { ...p, points: (p.points||0) + 1 } : p));
              setTimeout(() => setGameResult({ winners:[lucky], winNote:'+1 pont', subtitle:`${lucky.name} — Szerencsekör!`, drinks:0, effect:'lucky', ts:Date.now() }), 500);""",
"""              setPlayers(prev => prev.map(p => p.id === lucky.id ? { ...p, points: (p.points||0) + 1 } : p));
              setTimeout(() => setGameResult({ winners:[lucky], winNote:'+1 pont', subtitle:`${lucky.name} — Szerencsekör!`, drinks:0, effect:'lucky', ts:Date.now() }), 500);
              if (gameMeta?.ttsHost && typeof window.bohSpeak === 'function') setTimeout(() => window.bohSpeak('Szerencsekör! ' + lucky.name + ' kapott egy pontot!'), 700);""")
# sima kör (nem wildcard) bekonferálása
rep("""        if (showCounter || isWildcardRound) {
          setRoundPopup({ round: newRound, wildcard: wc, showRound: showCounter, leaving: false });""",
"""        if (showCounter && !isWildcardRound && gameMeta?.ttsHost && typeof window.bohSpeak === 'function') window.bohSpeak(newRound + '. kör');
        if (showCounter || isWildcardRound) {
          setRoundPopup({ round: newRound, wildcard: wc, showRound: showCounter, leaving: false });""")

# ── 5) Csoportos ivászat bekonferálása ──
rep("""      setGroupDrinkOverlay({ drinks });
      if (typeof window.bohSound === 'function') window.bohSound('cheers');
      if (typeof window.bohHaptic === 'function') window.bohHaptic('success');""",
"""      setGroupDrinkOverlay({ drinks });
      if (typeof window.bohSound === 'function') window.bohSound('cheers');
      if (typeof window.bohHaptic === 'function') window.bohHaptic('success');
      if (gameMeta?.ttsHost && typeof window.bohSpeak === 'function') window.bohSpeak('Csoportos ivászat! Mindenki iszik ' + drinks + ' kortyot!');""")

# ── 6) Verziobump ──
rep("const APP_VERSION = 'v9.975';", "const APP_VERSION = 'v9.976';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — TTS host applied')
