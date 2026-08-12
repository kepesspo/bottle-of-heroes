# v10.338 - Pontgyujtes NELKUL: nincs result banner, nincs Allas ful, nincs Buntetes
#
# A "Pontgyujtes" mod (`gameMeta.modes` -> 'points') kikapcsolva a `trackScores`
# hamis, es a konyveles MEG SEM TORTENIK: az `advance` / `advancePaired` /
# `advanceTeam` / `advanceLoverseny` mind valtozatlanul hagyja a jatekosokat.
# Se pont, se korty nem kerul fel.
#
# Harom felulet viszont ugy viselkedett, mintha kerulne:
#   1. a result banner "+1 pont"-ot es korty-szamot hirdetett;
#   2. a MENU -> Allas ful vegig nullakat mutatott;
#   3. a Buntetes gomb pedig TENYLEG irt a jatekosokra (`givePenalty` nem nezi a
#      `trackScores`-t) - vagyis pontgyujtes nelkul a buntetes volt az EGYETLEN,
#      ami szamolt. Ez onmagaban ellentmondas volt.
#
# Ugyanezert kerul ki a wildcard-sav "Szabalyszego?" gombja is: az ugyanazt a
# `PenaltyModal`-t nyitja, ugyanazzal a kovetkezmennyel.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# --- 1. a result banner ------------------------------------------------------
sub1(
"""  const onResult = (res) => {
    if (!res) { setGameResult(null); return; }
    let r = res;""",
"""  const onResult = (res) => {
    if (!res) { setGameResult(null); return; }
    // Pontgyujtes nelkul nincs mit hirdetni: a `trackScores` hamis, tehat a
    // konyveles meg sem tortenik. A banner "+1 pont"-ot es korty-szamot igerne,
    // amibol semmi nem kerul fel. A kapu ITT van, es nem lentebb: igy a hang, a
    // konfetti es a nezoknek kuldott `gameEvent` is elmarad.
    if (!trackScores) { setGameResult(null); return; }
    let r = res;""",
'result banner kapu')

# --- 2. a MENU "Allas" fule --------------------------------------------------
sub1(
"                {[['állás',t('score')],['szerkesztés','Szerkesztés'],['vezérlés',t('controls')]].map(([tab,label]) => (",
"""                {[...(trackScores ? [['állás',t('score')]] : []), ['szerkesztés','Szerkesztés'], ['vezérlés',t('controls')]].map(([tab,label]) => (""",
'menu fulsor')

sub1(
"""              <div style={{ visibility: menuTab==='állás' ? 'visible' : 'hidden', position:'absolute', top:0, left:14, right:14, bottom:0, overflowY:'auto' }}>
                <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
                  {mSorted.map((p,i) => <LeaderRow key={p.id||i} p={p} rank={i+1} maxScore={mMaxScore} showScores={true} overLimit={isOverLimit(p)} />)}
                  <div style={{ height:8 }} />
                </div>
              </div>""",
"""              {trackScores && (
              <div style={{ visibility: menuTab==='állás' ? 'visible' : 'hidden', position:'absolute', top:0, left:14, right:14, bottom:0, overflowY:'auto' }}>
                <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
                  {mSorted.map((p,i) => <LeaderRow key={p.id||i} p={p} rank={i+1} maxScore={mMaxScore} showScores={true} overLimit={isOverLimit(p)} />)}
                  <div style={{ height:8 }} />
                </div>
              </div>
              )}""",
'allas ful tartalma')

# A jatekos-hozzaadas utan a lap az Allas fulre ugrott. Pontgyujtes nelkul az
# nem letezik - ott a Szerkesztes az ertelmes celallomas.
src = src.replace("setMenuAddOpen(false); setMenuTab('állás');",
                  "setMenuAddOpen(false); setMenuTab(trackScores ? 'állás' : 'szerkesztés');")
assert "setMenuTab(trackScores ? 'állás' : 'szerkesztés')" in src

# --- 3. a Buntetes gomb ------------------------------------------------------
sub1(
"""                <div style={{ display:'flex', gap:8 }}>
                  <button onClick={() => { setShowMenu(false); setPenaltyOpen(true); }}
                    style={{ flex:1, height:76, border:'none', borderRadius:18, background:'#7C5CC41f', color:'#7C5CC4',
                      fontFamily:T.font, fontWeight:800, fontSize:12, cursor:'pointer',
                      display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:6 }}>
                    <BohIcon name="beer" size={21} /><span>Büntetés</span>
                  </button>""",
"""                <div style={{ display:'flex', gap:8 }}>
                  {/* Pontgyujtes nelkul a buntetes lenne az EGYETLEN, ami tenyleg
                      felkerul a jatekosokra (a `givePenalty` nem nezi a
                      `trackScores`-t) - miközben a jatekok maguk semmit nem
                      konyvelnek. Ezert itt nincs gomb. */}
                  {trackScores && (
                  <button onClick={() => { setShowMenu(false); setPenaltyOpen(true); }}
                    style={{ flex:1, height:76, border:'none', borderRadius:18, background:'#7C5CC41f', color:'#7C5CC4',
                      fontFamily:T.font, fontWeight:800, fontSize:12, cursor:'pointer',
                      display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:6 }}>
                    <BohIcon name="beer" size={21} /><span>Büntetés</span>
                  </button>
                  )}""",
'buntetes gomb')

# --- 4. a wildcard-sav "Szabalyszego?" gombja ugyanaz a felulet ---------------
sub1(
"""            <button onClick={() => setWcPunishOpen(true)} style={{ flexShrink:0, border:'none', borderRadius:10, background: T.ink, color: inkIsLight() ? (T.yellowText||T.yellow) : T.yellow, fontFamily:T.font, fontWeight:900, fontSize:11.5, padding: '8px 10px', cursor:'pointer', display:'flex', alignItems:'center', gap:5 }}>
              <BohIcon name="beer" size={13} />Szabályszegő?
            </button>""",
"""            {/* Ugyanazt a `PenaltyModal`-t nyitja, mint a MENU -> Buntetes,
                tehat pontgyujtes nelkul ugyanugy kimarad. */}
            {trackScores && (
            <button onClick={() => setWcPunishOpen(true)} style={{ flexShrink:0, border:'none', borderRadius:10, background: T.ink, color: inkIsLight() ? (T.yellowText||T.yellow) : T.yellow, fontFamily:T.font, fontWeight:900, fontSize:11.5, padding: '8px 10px', cursor:'pointer', display:'flex', alignItems:'center', gap:5 }}>
              <BohIcon name="beer" size={13} />Szabályszegő?
            </button>
            )}""",
'szabalyszego gomb')

sub1("const APP_VERSION = 'v10.337';", "const APP_VERSION = 'v10.338';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_338 alkalmazva')
