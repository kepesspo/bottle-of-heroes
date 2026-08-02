#!/usr/bin/env python3
# v10.284 — Szólánc: "A" irany (hofok-lap + tordelo lanc-sor), es hat logikai hiba
#
# MIT MERTEM, MIELOTT HOZZANYULTAM (a szamok a 402x874-es rendszerben ertendok)
#   * a talca `flex:1`-gyel osztozott, tehat a szintekkel egyutt zsugorodott:
#     157 / 102 / 75 / 58 / 47 / 39 / 33 / 29 px a 2..9. szinten. A 7. szinten a
#     szovegnek 27 px maradt, a "Debrecen" 58-at kert — hat kitoltott slotbol
#     negy olvashatatlan volt. Az az elem mondta fel a szolgalatot, aminek pont
#     az a dolga, hogy mutassa, mit raktal le eddig.
#   * a pottysor fixen 5 potty (`[0,1,2,3,4].map`), a letra viszont 15-ig ment:
#     az 5. szinttol mind az ot zold, es onnantol soha nem valtozott.
#   * a keret `#F6C842`-je be volt drotozva, a belso lapok viszont `T.surface`-t
#     hasznaltak → sotet temaban sotet kartyak rikito sarga tablan, sotet oldalon.
#   * nehez fokozaton egyetlen kepernyon allt egyszerre: "3 KORTY" (korong),
#     "iszik 1 kortyot" (lap), "Sere 3 KORTY" (banner).
#
# A HAT LOGIKAI HIBA, AMIT EZ A PATCH JAVIT
#   1. A lanc mindig a lista ELSO n szava volt (`allWords.slice(0, n)`), tehat
#      minden buli ugyanazzal a sorral indult. Most kevert a pakli.
#   2. A 3 csali `allWords.slice(n, n+3)` volt — vagyis PONTOSAN a kovetkezo
#      harom szint lanca. A jatek elore kiadta magat. Most a kevert lista ket
#      kalapra valik: az egyikben no a lanc, a masikbol jonnek a csalik.
#   3. Az "iszik 1 kortyot" be volt drotozva. Most a valos szorzot irja ki.
#   4. A leiras pontot igert a tobbieknek ("a tobbiek pontot kapnak"), a kod
#      viszont `onAdvance({[pid]:1})`-et hivott — a pontokra szolgalo masodik
#      argumentum hianyzott.
#   5. A vegigvitt lanc ZSAKUTCA volt: a nyero ag csak `onResult`-ot hivott,
#      `onAdvance`-t nem, tehat nem szuletett `pendingCommit`, es a Kovi gomb
#      (`active = !!pendingCommit && ...`) holtan maradt. A parti beragadt.
#   6. A fejlecszoveg egy MASIK jatekot irt le: "Mondd el a sort, majd told
#      hozza az uj szot a kategoriabol" — a jatekos soha nem tesz hozza szot.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─────────────────────────────────────────────────────────────────────────────
# 1. A nehezsegi/wildcard szorzo lejut a jatekig
#    Eddig csak a `gameMeta.difficulty` volt atadhato (mint a Tabu/Matek eseten),
#    de az a wildcard "dupla tet"-et nem fedi — es akkor a lap ujra mast irna,
#    mint a banner. Ezert a MAR OSSZESZOROZOTT erteket adjuk le.
# ─────────────────────────────────────────────────────────────────────────────
sub("function GameContent({ gameId, gameIdx, players, onAdvance, onUnready, onResult, onLiveDrinkUpdate, roomCode, gameMeta, challenger, opponent, onSetHideFooter, onSetBuszSwitch, onSetBpEnded, onCommit }) {",
    "function GameContent({ gameId, gameIdx, players, onAdvance, onUnready, onResult, onLiveDrinkUpdate, roomCode, gameMeta, challenger, opponent, onSetHideFooter, onSetBuszSwitch, onSetBpEnded, onCommit, drinkMult }) {",
    'GameContent szignatura')

sub("""  if (gameId === 'szolánc') return <SzolancGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} />;""",
    """  if (gameId === 'szolánc') return <SzolancGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} drinkMult={drinkMult} />;""",
    'szolanc prop')

sub("""onSetBpEnded={setBpEnded} onCommit={commitPending} />""",
    """onSetBpEnded={setBpEnded} onCommit={commitPending} drinkMult={diffDrinks * wcMult} />""",
    'drinkMult atadas')

# ─────────────────────────────────────────────────────────────────────────────
# 2. A fejlecszoveg vegre azt irja le, ami tortenik
# ─────────────────────────────────────────────────────────────────────────────
sub("""  'szolánc':   { prompt:'Mondd el a sort, majd told hozzá az új szót a kategóriából!', cta:[] },""",
    """  'szolánc':   { prompt:'Villannak a szavak — aztán koppintsd vissza őket sorrendben!', cta:[] },""",
    'prompt')

# ─────────────────────────────────────────────────────────────────────────────
# 3. A jatek ujrairasa
# ─────────────────────────────────────────────────────────────────────────────
OLD_START = """function SzolancWrap({children, style={}}) {
  return (
    <div style={{background:'#F6C842', borderRadius:20, padding:'16px', display:'flex', flexDirection:'column', gap:14, overflowY:'auto', ...style}}>
      {children}
    </div>
  );
}
"""
i = src.index(OLD_START)
j = src.index("\n  return null;\n}\n\n// ── Hibahatár a játékok köré", i) + len("\n  return null;\n}\n")
old_block = src[i:j]
assert 'function SzolancGame' in old_block and old_block.count('function ') == 2, 'rossz blokk-hatar'

NEW_BLOCK = r"""// ── SZÓLÁNC: HŐFOK-PALETTA ─────────────────────────────────────────────────
// Ugyanaz a nyelv, mint az Én még sohánál (v10.283): a lap a Szerencsekerék egy
// pasztellje, a jelvény ugyanaz telítve, a tinta pedig FIX sötét — a lap színe
// témafüggetlen, tehát a tintának is annak kell lennie.
// Itt viszont a szín a SOR HOSSZÁT kódolja: a lap melegszik, ahogy nő a lánc.
// Ez az eszkaláció hiányzott — eddig a 2. és a 8. szint ugyanúgy nézett ki.
// Képernyőnként PONTOSAN EGY hőfok-lap van. Az átadás fehér marad, mert ott nem
// a lánc a téma, hanem hogy ki jön.
const SZ_TONES = [
  { max: 4,        bg:'#C9E8D2', badge:'#4FA97F' },
  { max: 7,        bg:'#F5E0AC', badge:'#D69A2E' },
  { max: Infinity, bg:'#F2C4C4', badge:'#D46A6A' },
];
const SZ_INK = '#14202F';
const szTone = n => SZ_TONES.find(t => n <= t.max) || SZ_TONES[SZ_TONES.length - 1];

// Az ÁTADÁS és a VILLANTÁS ugyanazt a téglalapot használja: azonos magasság ÉS
// azonos pozíció, tehát a "Kezdem" után nem ugrik a doboz, csak a tartalma
// cserélődik. A pozícióhoz a gombsor helyét a villantás-képernyőn is fenn kell
// tartani üresen — enélkül a középre igazítás 31 px-szel feljebb tolná a lapot.
const SZ_CARD_H = 288;
const SZ_ACT_H = 57;

function SzolancCard({ tone, style, children }) {
  return (
    <div style={{ width:'100%', borderRadius:26, padding:20, background:tone.bg, color:SZ_INK,
                  display:'flex', flexDirection:'column',
                  // A hajszálvékony perem a lap SAJÁT telített színéből jön: a középső
                  // pasztell (#F5E0AC) majdnem pontosan az alapértelmezett meleg téma
                  // háttere, enélkül csak az árnyék választaná el.
                  boxShadow:`inset 0 0 0 1.5px ${tone.badge}33, 0 6px 18px -8px rgba(20,30,50,0.30)`,
                  ...style }}>
      {children}
    </div>
  );
}

function SzolancHead({ badge, badgeBg, right, style }) {
  return (
    <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', gap:10, ...style }}>
      <span style={{ background:badgeBg, color:'#fff', borderRadius:999, padding:'4px 11px',
                     fontFamily:T.font, fontWeight:900, fontSize:10, letterSpacing:'0.1em',
                     textTransform:'uppercase', whiteSpace:'nowrap', flexShrink:0 }}>{badge}</span>
      <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11.5, opacity:0.6, minWidth:0,
                     overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{right}</span>
    </div>
  );
}

// A lerakott szavak TÖRDELŐ pirula-sora — ugyanaz a sor, ami a bukás-lapon már
// eddig is jól működött. A régi fix szélességű tálca a szintekkel együtt
// zsugorodott (a 7. szinten 27 px jutott a szónak, a "Debrecen" 58-at kért),
// tehát pont akkor mondta fel, amikor a legnagyobb szükség lett volna rá.
function SzolancChain({ items, ghost }) {
  return (
    <div style={{ display:'flex', flexWrap:'wrap', gap:7, alignItems:'center', justifyContent:'center' }}>
      {items.map((it, i) => (
        <span key={i} style={{ display:'inline-flex', alignItems:'center', gap:7,
                    background: it.dim ? 'rgba(255,255,255,0.5)' : '#fff', borderRadius:999,
                    padding:'7px 13px 7px 7px', fontFamily:T.font, fontWeight:800, fontSize:14,
                    color: it.dim ? 'rgba(20,32,47,0.45)' : SZ_INK,
                    boxShadow: it.dim ? 'none' : '0 2px 0 rgba(20,30,50,0.12)' }}>
          <span style={{ width:19, height:19, flexShrink:0, borderRadius:'50%', color:'#fff',
                    background: it.bad ? '#D46A6A' : it.dim ? '#C9CFDA' : '#4FA97F',
                    fontSize:10, fontWeight:900, display:'flex', alignItems:'center',
                    justifyContent:'center' }}>{i + 1}</span>
          {it.w}
        </span>
      ))}
      {ghost != null && (
        <span style={{ border:'2px dashed rgba(20,32,47,0.28)', borderRadius:999, padding:'6px 15px',
                    fontFamily:T.font, fontWeight:800, fontSize:12.5,
                    color:'rgba(20,32,47,0.45)' }}>{ghost}</span>
      )}
    </div>
  );
}

function SzolancGame({ gameIdx, players, onAdvance, onResult, drinkMult }) {
  const LISTS = [
    { cat:'Gyümölcsök 🍎', words:['alma','körte','szilva','barack','szőlő','dinnye','eper','málna','cseresznye','banán','narancs','citrom','mangó','ananász','kivi'] },
    { cat:'Állatok 🐾',    words:['kutya','macska','ló','tehén','birka','nyúl','egér','róka','farkas','medve','oroszlán','tigris','elefánt','zsiráf','pingvin'] },
    { cat:'Fővárosok 🌍',  words:['Budapest','Berlin','Párizs','London','Róma','Madrid','Varsó','Prága','Bécs','Amszterdam','Bukarest','Athén','Lisszabon','Koppenhága','Stockholm'] },
    { cat:'Ételek 🍕',     words:['gulyás','pizza','hamburger','rántotta','palacsinta','rétes','lángos','fasírt','rakott krumpli','halászlé','töltött káposzta','kürtőskalács','lecsó','savanyúkáposzta','bruschetta'] },
    { cat:'Sportágak ⚽',  words:['foci','kosárlabda','tenisz','úszás','atlétika','birkózás','ökölvívás','vízilabda','röplabda','kézilabda','jégkorong','kerékpár','lovaglás','golf','evezés'] },
    { cat:'Autómárkák 🚗', words:['Toyota','BMW','Mercedes','Audi','Volkswagen','Ford','Opel','Renault','Peugeot','Fiat','Honda','Suzuki','Hyundai','Kia','Tesla'] },
    { cat:'Italok 🍹',     words:['víz','bor','sör','pálinka','kávé','tea','limonádé','cola','whisky','vodka','koktél','gyümölcslé','fröccs','rum','rosé'] },
    { cat:'Magyar városok 🏙️', words:['Pécs','Győr','Miskolc','Debrecen','Eger','Sopron','Veszprém','Kecskemét','Nyíregyháza','Szolnok','Kaposvár','Szombathely','Tatabánya','Érd','Zalaegerszeg'] },
    { cat:'Hangszerek 🎺', words:['zongora','gitár','hegedű','dob','furulya','trombita','szaxofon','bőgő','hárfa','fuvola','ukulele','mandolin','brácsa','cselló','klarinét'] },
    { cat:'Filmek 🎬',     words:['Titanic','Avatar','Inception','Matrix','Gladiátor','Interstellar','Joker','Avengers','Parasite','Tenet','Dune','Oppenheimer','Barbie','Top Gun','Ratatouille'] },
  ];

  const [listIdx] = React.useState(() => Math.floor(Math.random() * LISTS.length));
  const { cat, words: allWords } = LISTS[listIdx];
  const mult = drinkMult || 1;

  // A PAKLI KEVERT, ÉS A CSALIK KÜLÖN KALAPBÓL JÖNNEK.
  // Eddig a lánc `allWords.slice(0, n)` volt, a csali pedig `slice(n, n+3)` —
  // vagyis minden buli ugyanazzal a sorral indult, ÉS a három csali pontosan a
  // következő három szint lánca volt. Most a kevert listát kettévágjuk: az
  // egyik feléből nő a lánc, a másikból jönnek a csalik, tehát csali sosem
  // lehet jövőbeli láncszem.
  const { chainPool, decoyPool } = React.useMemo(() => {
    const a = allWords.slice();
    let s = (Date.now() ^ 0x9E3779B9) >>> 0;
    const rng = () => { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; return s >>> 0; };
    for (let i = a.length - 1; i > 0; i--) { const j = rng() % (i + 1); [a[i], a[j]] = [a[j], a[i]]; }
    const half = Math.ceil(a.length / 2);
    return { chainPool: a.slice(0, half), decoyPool: a.slice(half) };
  }, [listIdx]);

  const MAX_LEN = chainPool.length;
  const decoysFor = len => {
    const out = [];
    for (let i = 0; i < 3 && i < decoyPool.length; i++) out.push(decoyPool[(len * 3 + i) % decoyPool.length]);
    return out;
  };

  const fresh = (chainLen, turnIdx, isFirst = false) => ({
    phase: isFirst ? 'ready' : 'show', chainLen, showIdx: 0, gridWords: [], tapped: [], turnIdx, wrongIdx: null,
  });

  const [S, setS] = React.useState(() => fresh(2, 0, true));
  const [done, setDone] = React.useState(null);
  React.useEffect(() => { setS(fresh(2, 0, true)); setDone(null); }, [gameIdx]);

  const chain = chainPool.slice(0, S.chainLen);
  const tone = szTone(S.chainLen);
  const curPlayer = players[S.turnIdx % Math.max(players.length, 1)];

  // ── Show fázis: a szavak egyesével villannak ──────────────────────────────
  React.useEffect(() => {
    if (S.phase !== 'show') return;
    if (S.showIdx < S.chainLen) {
      const t = setTimeout(() => setS(s => ({ ...s, showIdx: s.showIdx + 1 })), 1300);
      return () => clearTimeout(t);
    }
    const pool = [...chainPool.slice(0, S.chainLen), ...decoysFor(S.chainLen)].sort(() => Math.random() - 0.5);
    const t = setTimeout(() => setS(s => ({ ...s, phase: 'recall', gridWords: pool, tapped: [] })), 600);
    return () => clearTimeout(t);
  }, [S.phase, S.showIdx]);

  // ── Recall fázis ──────────────────────────────────────────────────────────
  const tapWord = (word, idx) => {
    if (S.phase !== 'recall') return;
    if (S.tapped.includes(idx)) return;
    if (S.wrongIdx != null) return;
    const expected = chain[S.tapped.length];
    if (word !== expected) {
      setS(s => ({ ...s, wrongIdx: idx }));
      setTimeout(() => {
        const pid = curPlayer?.id;
        // A leírás eddig is pontot ígért a többieknek, a kód viszont sosem adott:
        // `onAdvance({[pid]:1})` — a pontokra szolgáló második argumentum hiányzott.
        const pm = {};
        players.forEach(p => { if (p.id !== pid) pm[p.id] = 1; });
        if (onAdvance) onAdvance({ [pid]: 1 }, pm);
        if (onResult) onResult({ correct: false, playerName: curPlayer?.name, drinks: 1,
                                 subtitle: (curPlayer?.name || 'Valaki') + ' elrontotta!' });
        setDone({ failName: curPlayer?.name, chain, badIdx: S.tapped.length });
      }, 700);
      return;
    }
    const newTapped = [...S.tapped, idx];
    if (newTapped.length === S.chainLen) {
      setS(s => ({ ...s, phase: 'correct', tapped: newTapped }));
      const nextLen = S.chainLen + 1;
      if (nextLen > MAX_LEN) {
        // A VÉGIGVITT LÁNC EDDIG ZSÁKUTCA VOLT: a nyerő ág csak `onResult`-ot hívott,
        // `onAdvance`-t nem, tehát nem született `pendingCommit`, és a Kövi gomb
        // (`active = !!pendingCommit && ...`) holtan maradt — a parti beragadt.
        setTimeout(() => {
          if (onAdvance) onAdvance({}, {});
          if (onResult) onResult({ correct: true, playerName: null, drinks: 0 });
          setDone({ failName: null, chain });
        }, 1200);
      } else {
        setTimeout(() => setS(fresh(nextLen, S.turnIdx + 1, true)), 1200);
      }
    } else {
      setS(s => ({ ...s, tapped: newTapped }));
    }
  };

  const COL = { display:'flex', flexDirection:'column', alignItems:'center', gap:12, width:'100%' };

  // ── DONE ──────────────────────────────────────────────────────────────────
  if (done !== null) {
    const win = !done.failName;
    const dchain = done.chain || chain;
    const dtone = szTone(dchain.length);
    return (
      <div style={COL}>
        <div style={{ width:'100%', borderRadius:26, padding:'24px 20px', textAlign:'center',
                      background: win ? T.mint : '#E8705E', color:'#fff',
                      display:'flex', flexDirection:'column', alignItems:'center',
                      boxShadow:'0 5px 0 rgba(20,30,50,0.16), 0 12px 28px rgba(20,30,50,0.18)',
                      animation:'popIn .4s cubic-bezier(.2,.9,.3,1.2)' }}>
          <BohIcon name={win ? 'trophy' : 'beer'} size={44} />
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:23, letterSpacing:'-0.02em', marginTop:6 }}>
            {win ? 'Végig megvolt a sor!' : done.failName + ' rontott'}
          </div>
          {!win && (
            <div style={{ fontFamily:T.font, fontSize:13.5, fontWeight:600, opacity:0.88, marginTop:3 }}>
              a {(done.badIdx || 0) + 1}. szónál cserélt sorrendet
            </div>
          )}
          {!win && (
            // A szám a VALÓS szorzóból jön. Eddig "iszik 1 kortyot" volt bedrótozva,
            // miközben nehéz fokozaton 3 korty ment el — és a banner ki is írta.
            <div style={{ background:'rgba(255,255,255,0.26)', borderRadius:999, padding:'10px 22px',
                          fontFamily:T.font, fontWeight:900, fontSize:15.5, marginTop:9 }}>
              iszik {mult} kortyot
            </div>
          )}
          {!win && players.length > 1 && (
            <div style={{ background:'rgba(255,255,255,0.24)', borderRadius:999, padding:'6px 15px',
                          fontFamily:T.font, fontWeight:800, fontSize:12.5, marginTop:7 }}>
              mindenki más +1 pont
            </div>
          )}
        </div>
        <SzolancCard tone={dtone}>
          <div style={{ fontFamily:T.font, fontSize:10.5, fontWeight:800, letterSpacing:'0.11em',
                        textTransform:'uppercase', opacity:0.5, textAlign:'center', marginBottom:11 }}>
            {win ? 'A teljes sor' : 'A helyes sor'}
          </div>
          <SzolancChain items={dchain.map((w, i) => ({
            w, bad: !win && i === done.badIdx, dim: !win && i > done.badIdx }))} />
        </SzolancCard>
      </div>
    );
  }

  // ── ÁTADÁS ────────────────────────────────────────────────────────────────
  if (S.phase === 'ready') {
    return (
      <div style={COL}>
        <div style={{ width:'100%', height:SZ_CARD_H, borderRadius:26, padding:20,
                      background:T.surface, display:'flex', flexDirection:'column', boxShadow:T.shadow }}>
          <SzolancHead badge={`${S.chainLen} szó`} badgeBg={tone.badge} right={cat} />
          <div style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
            <div style={{ width:76, height:76, borderRadius:'50%', background:curPlayer?.color || T.mint,
                          display:'flex', alignItems:'center', justifyContent:'center',
                          fontSize:31, fontWeight:900, color:'#fff', fontFamily:T.font }}>
              {curPlayer?.name?.[0]?.toUpperCase()}
            </div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:26, color:T.ink,
                          letterSpacing:'-0.02em', marginTop:12 }}>{curPlayer?.name}</div>
            <div style={{ fontFamily:T.font, fontSize:13, fontWeight:600, color:T.inkSoft, marginTop:3 }}>nálad a telefon</div>
            {/* A LÉTRA annyi szakasz, ahány szint. A régi pöttysor fixen 5 pöttyből
                állt, a létra viszont ennél tovább megy: az 5. szinttől mind az öt
                zöld volt, és onnantól soha nem változott. */}
            <div style={{ display:'flex', gap:4, width:'100%', marginTop:16 }}>
              {Array.from({ length: Math.max(MAX_LEN - 1, 1) }, (_, i) => i + 2).map(lvl => (
                <div key={lvl} style={{ flex:1, height:7, borderRadius:4,
                  background: lvl < S.chainLen ? T.mint : lvl === S.chainLen ? tone.badge : 'rgba(26,42,74,0.13)' }} />
              ))}
            </div>
            <div style={{ fontFamily:T.font, fontSize:11.5, fontWeight:700, color:T.inkMute, marginTop:7 }}>
              {S.chainLen} szó jön{S.chainLen > 2 ? ` — ${S.chainLen - 2} szintet már vittek` : ' — ez az első kör'}
            </div>
          </div>
        </div>
        <div style={{ height:SZ_ACT_H, width:'100%', display:'flex' }}>
          <button onClick={() => setS(s => ({ ...s, phase:'show' }))} style={{
            flex:1, border:'none', borderRadius:999, background:T.mint, color:'#fff',
            fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer',
            boxShadow:'0 4px 0 rgba(20,30,50,0.14), 0 8px 18px rgba(20,30,50,0.14)' }}>Kezdem</button>
        </div>
      </div>
    );
  }

  // ── VILLANTÁS ─────────────────────────────────────────────────────────────
  if (S.phase === 'show' || S.phase === 'correct') {
    const isCorrect = S.phase === 'correct';
    const currentWord = !isCorrect && S.showIdx < S.chainLen ? chain[S.showIdx] : null;
    // A betűméret a szó hosszához igazodik: a "Nyíregyháza" 46 px-en kilógna.
    const wl = (currentWord || '').length;
    const wfs = wl > 13 ? 25 : wl > 10 ? 31 : wl > 7 ? 38 : 46;
    return (
      <div style={COL}>
        <SzolancCard tone={tone} style={{ height:SZ_CARD_H }}>
          <SzolancHead badge={`${S.chainLen} szó`} badgeBg={tone.badge}
            right={isCorrect ? cat : `${Math.min(S.showIdx + 1, S.chainLen)}. / ${S.chainLen}.`} />
          <div style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
            {isCorrect ? (
              <div style={{ textAlign:'center', animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)' }}>
                <div style={{ fontSize:40 }}>✅</div>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, marginTop:8 }}>Helyes! Következő…</div>
              </div>
            ) : currentWord ? (
              <div key={S.showIdx} style={{ textAlign:'center', animation:'fadeIn .18s ease' }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:wfs,
                              letterSpacing:'-0.03em', lineHeight:1.06 }}>{currentWord}</div>
                <div style={{ display:'flex', gap:7, marginTop:18, justifyContent:'center' }}>
                  {chain.map((_, i) => (
                    <div key={i} style={{ width:10, height:10, borderRadius:'50%', transition:'background .2s',
                      background: i < S.showIdx ? tone.badge : i === S.showIdx ? tone.badge + '70' : 'rgba(20,32,47,0.15)' }} />
                  ))}
                </div>
              </div>
            ) : (
              <div style={{ fontFamily:T.font, fontWeight:700, fontSize:16, opacity:0.6 }}>Felkészülés…</div>
            )}
          </div>
        </SzolancCard>
        {/* A gombsor helye ÜRESEN fenntartva. Enélkül a középre igazítás 31 px-szel
            feljebb tolná a lapot, és a "Kezdem" után ugrana a doboz. */}
        <div style={{ height:SZ_ACT_H, width:'100%' }} />
      </div>
    );
  }

  // ── VISSZARAKÁS ───────────────────────────────────────────────────────────
  if (S.phase === 'recall') {
    const remaining = S.chainLen - S.tapped.length;
    return (
      <div style={COL}>
        <SzolancCard tone={tone} style={{ padding:16 }}>
          <SzolancHead badge={`${S.chainLen} szó`} badgeBg={tone.badge}
                       right="Koppints sorrendben" style={{ marginBottom:14 }} />
          <SzolancChain items={S.tapped.map(gi => ({ w: S.gridWords[gi] }))}
                        ghost={remaining > 0 ? `még ${remaining}` : null} />
        </SzolancCard>
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10, width:'100%' }}>
          {S.gridWords.map((word, idx) => {
            const used = S.tapped.indexOf(idx) !== -1;
            const bad = S.wrongIdx === idx;
            // A lerakott chip NEM kap sorszámot: azt a lánc-sor már kimondja.
            // Eddig a szó a tálcában és a rácson is ott volt, sorszámmal együtt.
            return (
              <button key={idx} onClick={() => tapWord(word, idx)} disabled={used} style={{
                padding:'15px 8px', borderRadius:17, border:'none', position:'relative',
                cursor: used ? 'default' : 'pointer',
                background: bad ? '#F2C4C4' : T.surface,
                opacity: used ? 0.42 : 1,
                color: bad ? '#B4372F' : T.ink,
                fontFamily:T.font, fontWeight:800, fontSize:15, transition:'opacity .15s',
                boxShadow: used || bad ? 'none' : '0 3px 0 rgba(20,30,50,0.12), 0 3px 8px rgba(20,30,50,0.10)',
                animation: bad ? 'shakeDrink .4s ease' : 'none' }}>{word}</button>
            );
          })}
        </div>
        <div style={{ fontFamily:T.font, fontSize:13, fontWeight:700, color:T.inkSoft, opacity:0.85 }}>
          {remaining > 0 ? `még ${remaining} szó a sorból` : '✓ Kész!'}
        </div>
      </div>
    );
  }

  return null;
}
"""

src = src[:i] + NEW_BLOCK + src[j:]

sub("const APP_VERSION = 'v10.283';", "const APP_VERSION = 'v10.284';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — Szólánc "A" irány + hat logikai hiba')
