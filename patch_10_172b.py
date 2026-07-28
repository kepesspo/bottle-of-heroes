# v10.172 (b) — a wildcard idozitoje
#
# A tartomanybol veletlen idopontot sorsol, es minden kivaltas utan ujrasorsol.
# A megjelenites a MAR MEGLEVO utat hasznalja (roundPopup showRound:false),
# ugyanazt, amit a savra koppintva is latni — nincs uj felulet.
#
# Miert kozvetlenul valt, es nem varja meg a kovetkezo korvaltast: a wildcard
# popup eddig is a jatek KOZBEN jelent meg (a korvaltas Busz kozben is korvaltas),
# tehat ez nem uj fajta megszakitas. Ha kulon "kovetkezo szunetig varunk"
# logikat tennenk be, az a Beer Pongnal — ahol ket korvaltas kozott sok perc van
# — akar el is nyelhetne a wildcardot.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

anchor = "  const [activeWildcard, setActiveWildcard] = useState(null); // {emoji, text, round} — a kör alatt végig látható szabály"
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + """

  // ── Wildcard idozito ──────────────────────────────────────────────
  // Korabban a korszam hozta (newRound % freq). Az nem volt rahuzhato a
  // magukban futo jatekokra: a Busz ~6 korlepest csinal osszesen, a Power Hour
  // meg a sajat 60 perces oraja szerint fut. Az ido minden jatekra ugyanaz.
  const wildcardOn = (gameMeta?.modes || []).includes('wildcard');
  const activeWcRef = React.useRef(null);
  React.useEffect(() => { activeWcRef.current = activeWildcard; }, [activeWildcard]);
  React.useEffect(() => {
    if (!wildcardOn) return;
    const lo = Math.max(1, gameMeta?.wildcardMin || 8);
    const hi = Math.max(lo, gameMeta?.wildcardMax || 15);
    let timer = null;
    const fire = () => {
      const cur = activeWcRef.current;
      const pool = (cur && WILDCARDS.length > 1) ? WILDCARDS.filter(w => w.text !== cur.text) : WILDCARDS;
      if (!pool.length) return;
      const wc = pool[Math.floor(Math.random() * pool.length)];
      setActiveWildcard({ ...wc, ts: Date.now() });
      if (typeof window.bohSound === 'function') window.bohSound('wildcard');
      // A savra koppintva is ez a nezet jon fel — nincs uj felulet.
      setRoundPopup({ round: null, wildcard: wc, showRound: false, leaving: false });
      // Szerencsekor: veletlen aktiv jatekos kap +1 pontot
      if (wc.effect === 'lucky') {
        setPlayers(prev => {
          const act = prev.filter(p => p.active !== false);
          if (!act.length) return prev;
          const lucky = act[Math.floor(Math.random() * act.length)];
          setTimeout(() => setGameResult({ winners:[lucky], winNote:'+1 pont',
            subtitle:`${lucky.name} — Szerencsekör!`, drinks:0, effect:'lucky', ts:Date.now() }), 900);
          return prev.map(p => p.id === lucky.id ? { ...p, points: (p.points || 0) + 1 } : p);
        });
      }
    };
    const schedule = () => {
      const ms = (lo + Math.random() * (hi - lo)) * 60000;
      timer = setTimeout(() => { fire(); schedule(); }, ms);
    };
    schedule();
    return () => { if (timer) clearTimeout(timer); };
  }, [wildcardOn, gameMeta?.wildcardMin, gameMeta?.wildcardMax]);""")

assert s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — idozito beallitva')
