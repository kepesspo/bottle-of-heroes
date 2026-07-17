#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# "Bónusz képernyő" mód teljes eltávolítása: mode pill, PlayScreen logika,
# overlay, i18n stringek. (A Busz játék bonusGuess-e NEM érintett!)
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'expected %d, found %d for: %r' % (count, n, old[:80])
    src = src.replace(old, new)

# 1) hu i18n
rep("    bonusEvent: 'Bónusz esemény!',\n", "")
rep("""    modeBonus: 'Bónusz képernyő',
    modeBonusInfo: 'Minden kör végén megjelenik egy rövid összefoglaló: ki nyert pontot és ki iszik.',
""", "")
rep("""    bonusLeaderDrinks: 'A vezető iszik — {n} korty',
    bonusComebackPoints: 'Az utolsó helyen álló visszakapaszkodik — +{n} pont',
""", "")

# 2) en i18n
rep("    bonusEvent: 'Bonus Event!',\n", "")
rep("""    modeBonus: 'Bonus Screen',
    modeBonusInfo: 'A brief summary appears after each round: who scored a point and who drinks.',
""", "")
rep("""    bonusLeaderDrinks: 'The leader drinks — {n} sips',
    bonusComebackPoints: 'Last place makes a comeback — +{n} point',
""", "")

# 3) Mode pill a Játékmenet sheetből
rep("    { id:'bonus',    icon:'gift',     label:t('modeBonus'),    info:t('modeBonusInfo') },\n", "")

# 4) PlayScreen state
rep("  const bonusEnabled = (gameMeta?.modes || []).includes('bonus');\n", "")
rep("""  const [bonusOverlay, setBonusOverlay] = useState(null); // { type, player, drinks } | null
  const bonusPendingRef = React.useRef(null);
""", "")

# 5) commitPending 10%-os bónusz ág
rep("""    // 10% bónusz esély
    if (bonusEnabled && Math.random() < 0.10 && newPlayers.length >= 2) {
      const sorted = [...newPlayers].sort((a,b) => (b.points-a.points)||(a.drinks-b.drinks));
      const first = sorted[0];
      const minPoints = sorted[sorted.length - 1].points;
      const lastTied = sorted.filter(p => p.points === minPoints);
      if (!lastTied.length) return commitRound(newPlayers, fb, newTurn, newGameIdx, newRound);
      const last = lastTied[Math.floor(Math.random() * lastTied.length)];
      const type = Math.random() < 0.5 ? 'top' : 'last';
      // top: leader drinks 2 extra (catch-up: others benefit)
      // last: lowest scorer gets +1 point (comeback mechanic)
      const bonus = type === 'top'
        ? { type:'top', player: first, drinks: 2 }
        : { type:'last', player: last, points: 1 };
      bonusPendingRef.current = {newPlayers, fb, newTurn, newGameIdx, newRound, bonus};
      setPendingCommit(null);
      setBonusOverlay(bonus);
      return;
    }
    setPendingCommit(null);
""", "    setPendingCommit(null);\n")

# 6) dismissBonus függvény
rep("""  const dismissBonus = () => {
    const p = bonusPendingRef.current;
    if (!p) return;
    bonusPendingRef.current = null;
    setBonusOverlay(null);
    // Apply bonus drinks to players
    const { bonus, newPlayers, fb, newTurn, newGameIdx, newRound } = p;
    const updated = newPlayers.map(pl => {
      if (bonus.type === 'top' && pl.id === bonus.player.id) return {...pl, drinks: pl.drinks + bonus.drinks};
      if (bonus.type === 'last' && pl.id === bonus.player.id) return {...pl, points: pl.points + (bonus.points||1)};
      return pl;
    });
    commitRound(updated, fb, newTurn, newGameIdx, newRound);
  };

""", "")

# 7) bonusOverlay JSX
rep("""      {bonusOverlay && (
        <div style={{ position:'fixed', inset:0, background:'rgba(14,14,24,0.72)', zIndex:60, display:'flex', alignItems:'center', justifyContent:'center', padding:28, animation:'fadeIn .2s' }}>
          <div style={{ background:T.surface, borderRadius:28, padding:'32px 28px 28px', width:'100%', maxWidth:340, display:'flex', flexDirection:'column', alignItems:'center', gap:14, boxShadow:'0 24px 64px rgba(0,0,0,0.3)', animation:'popIn .3s cubic-bezier(.2,.9,.3,1.3)' }}>
            <div style={{ fontSize:52, lineHeight:1 }}>{bonusOverlay.type === 'top' ? '😅' : '🌟'}</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink, textAlign:'center', letterSpacing:'-0.02em' }}>{t('bonusEvent')}</div>
            {bonusOverlay.type === 'top' ? (
              <>
                <PlayerAvatar player={bonusOverlay.player} size={52} />
                <div style={{ fontFamily:T.font, fontWeight:800, fontSize:17, color:T.ink }}>{bonusOverlay.player.name} iszik!</div>
                <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', lineHeight:1.5 }}>{t('bonusLeaderDrinks').replace('{n}', bonusOverlay.drinks)}</div>
                <div style={{ display:'flex', gap:8, justifyContent:'center', flexWrap:'wrap' }}>
                  {[].map((r,i) => (
                    <div key={r.id + '_' + i} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:3 }}>
                      <PlayerAvatar player={r} size={38} />
                      <div style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:T.inkSoft }}>{r.name}</div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <>
                <PlayerAvatar player={bonusOverlay.player} size={52} />
                <div style={{ fontFamily:T.font, fontWeight:800, fontSize:17, color:T.ink }}>{bonusOverlay.player.name}</div>
                <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, textAlign:'center', lineHeight:1.5 }}>{t('bonusComebackPoints').replace('{n}', bonusOverlay.points||1)}</div>
              </>
            )}
            <button onClick={dismissBonus} style={{ width:'100%', padding:'16px 0', borderRadius:16, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer', boxShadow:T.shadow, marginTop:4 }}>Értettem, tovább!</button>
          </div>
        </div>
      )}
""", "")

# 8) Verziobump
rep("const APP_VERSION = 'v9.947';", "const APP_VERSION = 'v9.948';")

# Ellenőrzés: PlayScreen-beli bónusz hivatkozás nem maradt (Busz BONUS_ prefix és
# a beerpong/busz bonusGuess szándékosan marad)
assert 'bonusEnabled' not in src
assert 'bonusOverlay' not in src
assert 'dismissBonus' not in src
assert 'modeBonus' not in src

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — bonus mode removed')
