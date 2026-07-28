# v10.160 (d) — Jatekmenet oldal
#
# A het jatek-beallito lap eddig csak hosszu nyomasra nyilt, a jatekmenet pedig
# egy felirat nelkuli fogaskerek mogott ult. Mindketto lathatatlan volt.
# Az uj oldal a jatekvalasztas UTAN jon (mert a jatek-beallitasok csak akkor
# ertelmesek, ha mar tudjuk, mit jatszunk), es egy helyre hozza:
#   jatekmenet · a kivalasztott jatekok sajat beallitasai · kortyolasi limit
# Adminbol kapcsolhato — kikapcsolva minden a regi uton megy.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# ── 1) EGY nyilvantartas: id -> gameMeta kulcs + beallito komponens ──
old_ids = """const GAME_CONFIG_IDS = ['busz', 'beerpong', 'kisebb', 'collect', 'ovfj', 'zene', 'blackjack'];
const hasGameConfig = (id) => GAME_CONFIG_IDS.indexOf(id) !== -1;"""
assert s.count(old_ids) == 1
s = s.replace(old_ids, """// A fuggveny-deklaraciok hoistolodnak, ezert a lapokra itt mar hivatkozhatunk
// akkor is, ha lejjebb vannak definialva.
const GAME_CONFIG_DEFS = {
  busz:      { metaKey:'buszConfig',      Comp: BuszConfigSheet },
  beerpong:  { metaKey:'beerpongConfig',  Comp: BeerPongConfigSheet },
  kisebb:    { metaKey:'kisebbConfig',    Comp: KisebbConfigSheet },
  collect:   { metaKey:'collectConfig',   Comp: CollectBoomConfigSheet },
  ovfj:      { metaKey:'ovfjConfig',      Comp: OVFJConfigSheet },
  zene:      { metaKey:'zeneConfig',      Comp: ZeneConfigSheet },
  blackjack: { metaKey:'blackjackConfig', Comp: BlackjackConfigSheet },
};
const GAME_CONFIG_IDS = Object.keys(GAME_CONFIG_DEFS);
const hasGameConfig = (id) => GAME_CONFIG_IDS.indexOf(id) !== -1;

// Egyetlen helyen mountolja a megnyitott beallito lapot. Enelkul mindket
// kepernyonek hetszer kellene leirnia ugyanazt az accessor-part.
function GameConfigHost({ openId, onClose, gameMeta, setGameMeta, playerCount }) {
  if (!openId || !GAME_CONFIG_DEFS[openId]) return null;
  const { metaKey, Comp } = GAME_CONFIG_DEFS[openId];
  const config = (gameMeta && gameMeta[metaKey]) || {};
  const setConfig = (cfg) => setGameMeta(m => Object.assign({}, m, {
    [metaKey]: typeof cfg === 'function' ? cfg((m && m[metaKey]) || {}) : cfg,
  }));
  return <Comp config={config} setConfig={setConfig} onClose={onClose} playerCount={playerCount} />;
}

// A folyamat lepesjelzoje. Harmadik pont csak akkor, ha a Jatekmenet oldal el.
function StepDots({ active }) {
  const setupFlow = useSetupFlow();
  const dots = [Icon.users, Icon.controller].concat(setupFlow ? [Icon.settings] : []);
  return (
    <div style={{ display:'flex', gap:6, padding:4, background:T.mintSoft, borderRadius:999 }}>
      {dots.map((ic, i) => i + 1 === active ? (
        <div key={i} style={{ width:34, height:34, borderRadius:999, background:T.mint, display:'grid', placeItems:'center' }}>{ic('#fff')}</div>
      ) : (
        <div key={i} style={{ width:34, height:34, display:'grid', placeItems:'center', color:T.mintDeep }}>{ic(T.mintDeep)}</div>
      ))}
    </div>
  );
}""")

# ── 2) lepesjelzo a ket meglevo kepernyon ──
players_dots = """          <div style={{ display:'flex', gap:6, padding:4, background:T.mintSoft, borderRadius:999 }}>
            <div style={{ width:34, height:34, borderRadius:999, background:T.mint, display:'grid', placeItems:'center' }}>{Icon.users('#fff')}</div>
            <div style={{ width:34, height:34, display:'grid', placeItems:'center', color:T.mintDeep }}>{Icon.controller(T.mintDeep)}</div>
          </div>"""
assert s.count(players_dots) == 1
s = s.replace(players_dots, "          <StepDots active={1} />")

games_dots = """            <div style={{ display:'flex', gap:6, padding:4, background:T.mintSoft, borderRadius:999 }}>
              <div style={{ width:34, height:34, display:'grid', placeItems:'center', color:T.mintDeep }}>{Icon.users(T.mintDeep)}</div>
              <div style={{ width:34, height:34, borderRadius:999, background:T.mint, display:'grid', placeItems:'center' }}>{Icon.controller('#fff')}</div>
            </div>"""
assert s.count(games_dots) == 1
s = s.replace(games_dots, "            <StepDots active={2} />")

assert s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — kozos nyilvantartas + lepesjelzo')
