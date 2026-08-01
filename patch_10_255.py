#!/usr/bin/env python3
# v10.255 — Reakció: elsietés = elbukott lehetőség, avatarok, saját ikonok
#
# 1. ELSIETÉS
# Eddig a korai koppintás után a játékos visszakerült az indító képernyőre és
# újrapróbálhatta — vagyis a szabálytalanság ingyen volt, sőt: aki elsiette,
# az kapott egy ingyen "felmérő" kört. Mostantól az elsietés VÉGLEGES: nincs
# újabb próba, az adott játékos elbukta a körét.
#
# Ehhez a null ideje NEM elég jelzés (a "még nem játszott" is null), ezért
# külön p1Foul / p2Foul állapot jelöli. Következmények:
#   - aki elsiette, veszít; a másik nyer (akkor is, ha lassabb lett volna)
#   - ha MINDKETTEN elsietik: nincs győztes, mindketten isznak, pont nincs
#   - az elsietett körből NEM megy statisztika: az nem reakcióidő. A rekordot
#     és az átlagot nem szabad egy szabálytalansággal rontani/javítani.
#
# 2. AVATAROK
# A két kártyán a nevek mellé bekerül a játékos képe. FONTOS: az avatar-doboz
# nem JSX-komponensként van beágyazva, hanem sima függvényhívással — a
# renderen belül definiált komponens minden újrarajzoláskor új azonosságot
# kapna, a React újramountolná a részfát, és a profilkép <img>-je újra
# dekódolódna. Pontosan ez volt a korábban jelentett "ugráló profilkép".
#
# 3. IKONOK
# Az emojik helyett az app saját ikonkészlete (BohIcon):
#   🏆 → trophy (cím), 🥇 → medal1 (győztes), 🏅 → crown (REKORD),
#   📊 → counter (ÁTLAG), 🌍 → party (Mindenki), ⚠️ → cross (elsietés)
# A "★ ÚJ REKORD" csillag marad: az nem emoji, hanem tipográfiai jel, és
# ekkora pirulán egy rajzolt ikon csak masszává mosódna.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1. állapot: elsietés jelölése ──
sub("""  const [startTime, setStartTime] = useState(null);
  const [earlyTap, setEarlyTap] = useState(false);""",
    """  const [startTime, setStartTime] = useState(null);
  // Elsietes: a null ido onmagaban nem eleg jelzes, mert a "meg nem jatszott"
  // is null. Ezert kulon jeloljuk, hogy az adott jatekos ELBUKTA a koret.
  const [p1Foul, setP1Foul] = useState(false);
  const [p2Foul, setP2Foul] = useState(false);""",
    'foul allapot')

# ── 2. avatar + segédek ──
sub("""  const currentPlayer = phase.includes('1') ? challenger : opponent;

  const startWaiting = () => {
    setEarlyTap(false);
    const nextPhase""",
    """  // Avatar-doboz. SIMA FUGGVENY, nem komponens: a renderen belul definialt
  // komponens minden ujrarajzolaskor uj azonossagot kapna, a React
  // ujramountolna a reszfat, es a kep ujra dekodolodna — ez a korabban
  // jelentett "ugralo profilkep". Lasd a ResultBanner Pile-jat ugyanezzel.
  const avatarOf = (p, size) => (
    <div style={{ width:size, height:size, borderRadius:'50%', background:p?.color || '#8894A8',
                  display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0 }}>
      {p?.img
        ? <img src={p.img} alt="" style={{ width:size, height:size, objectFit:'cover', display:'block' }} />
        : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:Math.round(size * 0.44), color:'#fff' }}>
            {(p?.name || '?').charAt(0).toUpperCase()}
          </span>}
    </div>
  );
  const msLabel = v => (v == null ? '—' : v + ' ms');

  const currentPlayer = phase.includes('1') ? challenger : opponent;

  const startWaiting = () => {
    const nextPhase""",
    'avatar seged')

# ── 3. a korai koppintás elbukja a kört ──
sub("""  const handleTap = () => {
    if (phase === 'waiting1' || phase === 'waiting2') {
      clearTimeout(timerRef.current);
      setEarlyTap(true);
      setPhase(phase.startsWith('waiting1') ? 'intro1' : 'intro2');
      return;
    }""",
    """  const handleTap = () => {
    if (phase === 'waiting1' || phase === 'waiting2') {
      // Elsiette — nincs ujraprobalas, elbukta a koret. Ha visszaengednenk az
      // indito kepernyore, a szabalytalansag ingyen lenne (sot: ingyen felmero kor).
      clearTimeout(timerRef.current);
      if (phase === 'waiting1') { setP1Foul(true); setPhase('done1'); }
      else { setP2Foul(true); setPhase('result'); }
      return;
    }""",
    'elsietes bukas')

# ── 4. eredmény-számítás elsietéssel ──
sub("""  useEffect(() => {
    if (phase !== 'result' || advancedRef.current) return;
    if (p1Ms === null || p2Ms === null) return;
    advancedRef.current = true;
    const p1Name = challenger?.name || 'Kihívó';
    const p2Name = opponent?.name || 'Ellenfél';
    const p1Won = p1Ms <= p2Ms;
    const winner = p1Won ? challenger : opponent;
    const loser  = p1Won ? opponent  : challenger;
    const winMs = Math.min(p1Ms, p2Ms), loseMs = Math.max(p1Ms, p2Ms);
    // Split banner: győztes (kisebb reakcióidő) fent, vesztes (iszik) lent
    onResult && onResult({ winners:[winner], losers:[loser], drinks:1, winNote:`+1 pont · ${winMs}ms`, loseNote:`${loseMs}ms` });
    onAdvance && onAdvance(
      loser  ? {[loser.id]:1}  : {},
      winner ? {[winner.id]:1} : {}
    );""",
    """  useEffect(() => {
    if (phase !== 'result' || advancedRef.current) return;
    // "Kesz" az is, aki elsiette — az is lezart kor, csak ido nelkul.
    if (!(p1Ms !== null || p1Foul) || !(p2Ms !== null || p2Foul)) return;
    advancedRef.current = true;

    if (p1Foul && p2Foul) {
      // Senki nem nyert: pont nincs, de mindketten isznak.
      const both = [challenger, opponent].filter(Boolean);
      onResult && onResult({ winners:[], losers:both, drinks:1, loseNote:'Mindketten elsiették' });
      onAdvance && onAdvance(both.reduce((m, p) => { m[p.id] = 1; return m; }, {}), {});
    } else {
      // Aki elsiette, veszit — akkor is, ha egyebkent gyorsabb lett volna.
      const p1Won = p2Foul || (!p1Foul && p1Ms <= p2Ms);
      const winner = p1Won ? challenger : opponent;
      const loser  = p1Won ? opponent  : challenger;
      const winMs  = p1Won ? p1Ms : p2Ms;
      const loseMs = p1Won ? p2Ms : p1Ms;
      const loseFoul = p1Won ? p2Foul : p1Foul;
      // Split banner: győztes fent, vesztes (iszik) lent
      onResult && onResult({ winners:[winner], losers:[loser], drinks:1,
        winNote:`+1 pont · ${winMs}ms`, loseNote: loseFoul ? 'Elsiette' : `${loseMs}ms` });
      onAdvance && onAdvance(
        loser  ? {[loser.id]:1}  : {},
        winner ? {[winner.id]:1} : {}
      );
    }""",
    'eredmeny elsietessel')

sub("""  }, [phase, p1Ms, p2Ms]);""",
    """  }, [phase, p1Ms, p2Ms, p1Foul, p2Foul]);""",
    'effect fuggoseg')

# ── 5. az intro-kártya "elsiette" jelzése ──
sub("""      {earlyTap && (
        <div style={{ background:'rgba(239,68,68,0.12)', borderRadius:12, padding:'8px 16px', fontFamily:T.font, fontSize:13, color:'#EF4444', fontWeight:700 }}>
          ⚠️ Túl korán koppintottál! Próbáld újra.
        </div>
      )}
""", "", 'earlyTap sav torlese')

sub("""          {[{ p: challenger, ms: p1Ms }, { p: opponent, ms: p2Ms }].map((x, i) => (
            <div key={i} style={{ flex:1, padding:'11px 8px', display:'flex', flexDirection:'column', alignItems:'center', gap:3,
                                  borderLeft: i ? '1.5px solid rgba(20,30,50,0.1)' : 'none' }}>
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize:9.5, color:T.inkSoft, letterSpacing:1.2,
                             textTransform:'uppercase', maxWidth:'100%', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{x.p?.name || '—'}</span>
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color: x.ms == null ? T.inkMute : T.ink, fontVariantNumeric:'tabular-nums' }}>
                {x.ms == null ? '—' : (x.ms/1000).toFixed(2) + ' mp'}
              </span>
            </div>
          ))}""",
    """          {[{ p: challenger, ms: p1Ms, foul: p1Foul }, { p: opponent, ms: p2Ms, foul: p2Foul }].map((x, i) => (
            <div key={i} style={{ flex:1, padding:'11px 8px', display:'flex', flexDirection:'column', alignItems:'center', gap:4,
                                  borderLeft: i ? '1.5px solid rgba(20,30,50,0.1)' : 'none' }}>
              <div style={{ display:'flex', alignItems:'center', gap:6, maxWidth:'100%' }}>
                {avatarOf(x.p, 20)}
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:9.5, color:T.inkSoft, letterSpacing:1.2,
                               textTransform:'uppercase', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{x.p?.name || '—'}</span>
              </div>
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize: x.foul ? 13 : 18,
                             color: x.foul ? T.coral : (x.ms == null ? T.inkMute : T.ink), fontVariantNumeric:'tabular-nums' }}>
                {x.foul ? 'Elsiette' : x.ms == null ? '—' : (x.ms/1000).toFixed(2) + ' mp'}
              </span>
            </div>
          ))}""",
    'intro ket ido')

# ── 6. a done1 képernyő elsietés esetén ──
sub("""  if (phase === 'done1') return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16, padding:'8px 0' }}>
      <div style={{ width:'100%', borderRadius:28, background:'#22C55E', padding:'28px 24px', display:'flex', flexDirection:'column', alignItems:'center', gap:12, boxShadow:'0 8px 32px rgba(34,197,94,0.3)' }}>
        <div style={{ width:80, height:80, borderRadius:'50%', background:'rgba(255,255,255,0.2)', display:'flex', alignItems:'center', justifyContent:'center' }}>
          <div style={{ width:60, height:60, borderRadius:'50%', background:'rgba(255,255,255,0.9)', display:'flex', alignItems:'center', justifyContent:'center' }}>
            <span style={{ fontFamily:'monospace', fontWeight:900, fontSize:18, color:'#22C55E' }}>{p1Ms}ms</span>
          </div>
        </div>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:'#fff' }}>{challenger?.name} reakcióideje ✓</div>
      </div>""",
    """  if (phase === 'done1') return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16, padding:'8px 0' }}>
      <div style={{ width:'100%', borderRadius:28, background: p1Foul ? '#EF4444' : '#22C55E', padding:'28px 24px', display:'flex', flexDirection:'column', alignItems:'center', gap:12, boxShadow:`0 8px 32px ${p1Foul ? 'rgba(239,68,68,0.3)' : 'rgba(34,197,94,0.3)'}` }}>
        <div style={{ width:80, height:80, borderRadius:'50%', background:'rgba(255,255,255,0.2)', display:'flex', alignItems:'center', justifyContent:'center' }}>
          <div style={{ width:60, height:60, borderRadius:'50%', background:'rgba(255,255,255,0.9)', display:'grid', placeItems:'center' }}>
            {p1Foul
              ? <BohIcon name="cross" size={30} />
              : <span style={{ fontFamily:'monospace', fontWeight:900, fontSize:18, color:'#22C55E' }}>{p1Ms}ms</span>}
          </div>
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:8 }}>
          {avatarOf(challenger, 26)}
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:'#fff' }}>
            {p1Foul ? `${challenger?.name || 'Kihívó'} elsiette` : `${challenger?.name} reakcióideje ✓`}
          </div>
        </div>
        {p1Foul && (
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:'rgba(255,255,255,0.85)', textAlign:'center' }}>
            Nincs újabb próba — ezt a kört elbuktad.
          </div>
        )}
      </div>""",
    'done1 elsietessel')

# ── 7. eredmény-képernyő: elsietés, avatarok, ikonok ──
sub("""  // result
  const p1Won = p1Ms !== null && p2Ms !== null && p1Ms <= p2Ms;
  const winnerName = p1Won ? (challenger?.name||'Kihívó') : (opponent?.name||'Ellenfél');
  const maxMs = Math.max(p1Ms||0, p2Ms||0, 1);
  const players2 = [{player:challenger, ms:p1Ms, won:p1Won},{player:opponent, ms:p2Ms, won:!p1Won}];
  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16, padding:'8px 0' }}>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:T.mint, textAlign:'center' }}>🏆 {winnerName} nyert!</div>
      {/* Bar chart */}
      <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'20px 16px', boxShadow:T.shadow }}>
        {players2.map(({player, ms, won}, i) => (
          <div key={i} style={{ marginBottom: i === 0 ? 14 : 0 }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:6 }}>
              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>{won ? '🥇 ' : ''}{player?.name || (i===0?'Kihívó':'Ellenfél')}</div>
              <div style={{ fontFamily:'monospace', fontWeight:900, fontSize:20, color: won ? T.mint : T.coral }}>{ms}ms</div>
            </div>
            <div style={{ height:14, borderRadius:7, background:T.surfaceMuted, overflow:'hidden' }}>
              <div style={{
                height:'100%', borderRadius:7,
                background: won ? `linear-gradient(90deg, ${T.mint}, ${T.mintDeep})` : `linear-gradient(90deg, ${T.coral}, #E06060)`,
                width:`${(ms/maxMs)*100}%`,
                transition:'width 0.8s cubic-bezier(.2,.9,.3,1)',
                animation:'gameProgressGrow 0.8s cubic-bezier(.2,.9,.3,1) both',
              }} />
            </div>
          </div>
        ))}
      </div>""",
    """  // result
  const bothFoul = p1Foul && p2Foul;
  const p1Won = !bothFoul && (p2Foul || (!p1Foul && p1Ms !== null && p2Ms !== null && p1Ms <= p2Ms));
  const winnerName = p1Won ? (challenger?.name||'Kihívó') : (opponent?.name||'Ellenfél');
  const maxMs = Math.max(p1Ms||0, p2Ms||0, 1);
  const players2 = [{player:challenger, ms:p1Ms, foul:p1Foul, won:!bothFoul && p1Won},
                    {player:opponent,   ms:p2Ms, foul:p2Foul, won:!bothFoul && !p1Won}];
  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16, padding:'8px 0' }}>
      <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:8, textAlign:'center' }}>
        <BohIcon name={bothFoul ? 'cross' : 'trophy'} size={22} />
        <span style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color: bothFoul ? T.coral : T.mint }}>
          {bothFoul ? 'Mindketten elsiették!' : `${winnerName} nyert!`}
        </span>
      </div>
      {/* Bar chart */}
      <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'20px 16px', boxShadow:T.shadow }}>
        {players2.map(({player, ms, foul, won}, i) => (
          <div key={i} style={{ marginBottom: i === 0 ? 14 : 0 }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', gap:10, marginBottom:6 }}>
              <div style={{ display:'flex', alignItems:'center', gap:8, minWidth:0 }}>
                {avatarOf(player, 26)}
                {won && <BohIcon name="medal1" size={15} />}
                <span style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink,
                               overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{player?.name || (i===0?'Kihívó':'Ellenfél')}</span>
              </div>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize: foul ? 14 : 20, whiteSpace:'nowrap',
                            fontVariantNumeric:'tabular-nums', color: won ? T.mint : T.coral }}>
                {foul ? 'Elsiette' : ms + 'ms'}
              </div>
            </div>
            <div style={{ height:14, borderRadius:7, background:T.surfaceMuted, overflow:'hidden' }}>
              <div style={{
                height:'100%', borderRadius:7,
                background: won ? `linear-gradient(90deg, ${T.mint}, ${T.mintDeep})` : `linear-gradient(90deg, ${T.coral}, #E06060)`,
                width: foul ? '100%' : `${(ms/maxMs)*100}%`,
                transition:'width 0.8s cubic-bezier(.2,.9,.3,1)',
                animation:'gameProgressGrow 0.8s cubic-bezier(.2,.9,.3,1) both',
              }} />
            </div>
          </div>
        ))}
      </div>""",
    'eredmeny kartya')

sub("""              <span />
              <span style={head}>🏅 Rekord</span>
              <span style={head}>📊 Átlag</span>""",
    """              <span />
              <span style={head}><BohIcon name="crown" size={13} /> Rekord</span>
              <span style={head}><BohIcon name="counter" size={13} /> Átlag</span>""",
    'fejlec ikonok')

sub("""        const head = { fontFamily:T.font, fontWeight:900, fontSize:10.5, letterSpacing:0.8, textTransform:'uppercase',
                       color:T.inkMute, textAlign:'right', minWidth:78 };""",
    """        const head = { fontFamily:T.font, fontWeight:900, fontSize:10.5, letterSpacing:0.8, textTransform:'uppercase',
                       color:T.inkMute, minWidth:78, display:'flex', alignItems:'center', justifyContent:'flex-end', gap:5 };""",
    'fejlec stilus')

sub("""                  <span style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink,
                                 overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>
                    {x.player?.name || (i === 0 ? 'Kihívó' : 'Ellenfél')}
                  </span>""",
    """                  <span style={{ display:'flex', alignItems:'center', gap:8, minWidth:0 }}>
                    {avatarOf(x.player, 26)}
                    <span style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink,
                                   overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>
                      {x.player?.name || (i === 0 ? 'Kihívó' : 'Ellenfél')}
                    </span>
                  </span>""",
    'jatekos nev avatarral')

sub("""                  <span style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft,
                                 overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>
                    🌍 Mindenki
                  </span>
                  <span style={{ ...num, fontSize:17, color: g.isRecord ? T.mint : T.inkSoft }}>{g.best} ms</span>
                  <span style={{ ...num, fontSize:17, color:T.inkSoft }}>{g.avg} ms</span>""",
    """                  <span style={{ display:'flex', alignItems:'center', gap:8, minWidth:0 }}>
                    <span style={{ width:26, height:26, borderRadius:'50%', background:T.surfaceMuted,
                                   display:'grid', placeItems:'center', flexShrink:0 }}>
                      <BohIcon name="party" size={15} />
                    </span>
                    <span style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft,
                                   overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>Mindenki</span>
                  </span>
                  <span style={{ ...num, fontSize:17, color: g.isRecord ? T.mint : T.inkSoft }}>{msLabel(g.best)}</span>
                  <span style={{ ...num, fontSize:17, color:T.inkSoft }}>{msLabel(g.avg)}</span>""",
    'mindenki sor')

sub("""                    <span style={{ ...num, color: x.h.isRecord ? T.mint : T.ink }}>{x.h.best} ms</span>""",
    """                    <span style={{ ...num, color: x.h.isRecord ? T.mint : T.ink }}>{msLabel(x.h.best)}</span>""",
    'rekord ertek')

sub("""                  <span style={{ ...num, color:T.inkSoft }}>{x.h.avg} ms</span>""",
    """                  <span style={{ ...num, color:T.inkSoft }}>{msLabel(x.h.avg)}</span>""",
    'atlag ertek')

# ── 8. az elsietett kör NEM ronthatja el a rekordot/átlagot ──
# (a bump/times mar most is kiszuri a null idot — itt csak a megjelenitest
#  igazitjuk: aki elsiette, annak a KORABBI allasat mutatjuk, a mostani kor
#  nelkul. Igy nem tunik el a sora, de nem is hazudunk neki uj rekordot.)
sub("""  const histOf = (pl, ms) => {
    if (!pl?.profileId || ms == null) return null;
    const s = preStats[pl.profileId];
    if (!s) return null;
    const prevBest = typeof s.bestReactionTime === 'number' ? s.bestReactionTime : null;
    const cnt = typeof s.reactionCount === 'number' ? s.reactionCount : 0;
    const sum = typeof s.reactionSum === 'number' ? s.reactionSum : 0;
    return {
      best: prevBest == null ? ms : Math.min(prevBest, ms),
      avg: Math.round((sum + ms) / (cnt + 1)),
      isRecord: prevBest != null && ms < prevBest,
    };
  };""",
    """  const histOf = (pl, ms) => {
    if (!pl?.profileId) return null;
    const s = preStats[pl.profileId];
    if (!s) return null;
    const prevBest = typeof s.bestReactionTime === 'number' ? s.bestReactionTime : null;
    const cnt = typeof s.reactionCount === 'number' ? s.reactionCount : 0;
    const sum = typeof s.reactionSum === 'number' ? s.reactionSum : 0;
    // Elsietes eseten NINCS ervenyes ido: a korabbi allast mutatjuk valtozatlanul.
    if (ms == null) {
      if (prevBest == null && cnt === 0) return null;
      return { best: prevBest, avg: cnt ? Math.round(sum / cnt) : null, isRecord: false, fresh: cnt <= 1 };
    }
    return {
      best: prevBest == null ? ms : Math.min(prevBest, ms),
      avg: Math.round((sum + ms) / (cnt + 1)),
      isRecord: prevBest != null && ms < prevBest,
      fresh: cnt === 0,
    };
  };""",
    'histOf elsietessel')

sub("""        const fresh = hist.some(x => x.h.avg === x.h.best && x.h.best === x.ms) || (g && g.fresh);""",
    """        const fresh = hist.some(x => x.h.fresh) || (g && g.fresh);""",
    'fresh feltetel')

# a mindenkori sor akkor is szoljon, ha ebben a korben nem szuletett ervenyes ido
sub("""  const globalHist = () => {
    if (!preGame) return null;
    const times = [p1Ms, p2Ms].filter(x => x != null);
    if (!times.length) return null;
    const fastest = Math.min(...times);
    const prevBest = typeof preGame.bestReactionTime === 'number' ? preGame.bestReactionTime : null;
    const cnt = typeof preGame.reactionCount === 'number' ? preGame.reactionCount : 0;
    const sum = typeof preGame.reactionSum === 'number' ? preGame.reactionSum : 0;
    return {""",
    """  const globalHist = () => {
    if (!preGame) return null;
    const times = [p1Ms, p2Ms].filter(x => x != null);
    const prevBest = typeof preGame.bestReactionTime === 'number' ? preGame.bestReactionTime : null;
    const cnt = typeof preGame.reactionCount === 'number' ? preGame.reactionCount : 0;
    const sum = typeof preGame.reactionSum === 'number' ? preGame.reactionSum : 0;
    // Ha ebben a korben egy ervenyes ido sem szuletett (mindketten elsiettek),
    // a korabbi allas akkor is ervenyes — csak nem valtozik tole.
    if (!times.length) {
      if (prevBest == null && cnt === 0) return null;
      return { best: prevBest, avg: cnt ? Math.round(sum / cnt) : null, isRecord: false, fresh: cnt <= 1 };
    }
    const fastest = Math.min(...times);
    return {""",
    'globalHist elsietessel')

sub("const APP_VERSION = 'v10.254';", "const APP_VERSION = 'v10.255';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — elsietes = bukas, avatarok, sajat ikonok')
