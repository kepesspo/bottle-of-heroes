# v10.360 - Uj csapatjatek: „Csendes árverés" (korty-aukcio)
#
# Az app kisorsol egy nyeremenyt, es MINDENKI TITOKBAN licital kortyot.
# A legmagasabb licit nyer — es annyit iszik, amennyit igert.
#
# ⚠️ A TITKOSSAG A JATEK FELE. Ha barki latja a masik szamat, csak ra tesz
# egyet — akkor nincs dontes, csak sorrend. Ezert korbeadós a telefon:
# atado-lap -> „Én vagyok" -> lepteto -> „Kész", es a kovetkezo atado-lap mar
# semmit nem mutat az elozobol. (Ugyanaz a minta, mint a Farkasos
# szereposztasanal.) A lepteto ezert NEM a kozos `PlayerDrinkRow`: az a sor a
# TELJES mezonyt mutatja egyszerre, itt viszont pontosan egy embert szabad.
#
# ⚠️ A JATEK NEM OSZT PONTOT — mint az Ultimatum. A nyeremeny MAGA a jutalom,
# es azt a tarsasag tartatja be, nem az app: kor-kozi allapotot a `PlayScreen`
# nem tarol, tehat egy „a kovetkezo korben duplan er a pontod" dijat a kod nem
# tudna ervenyesiteni. Ezert minden dij egy MONDAT, amit a jatekosok betartanak.
#
# ⚠️ A NYERTES A BANNER „ISZIK" OLDALAN all. Ez elsore forditottnak latszik,
# de pontosan ezt igerte: annyit iszik, amennyit licitalt. Amit NYERT, az a
# `loseNote`-ban all.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# ── 1. IMGS ─────────────────────────────────────────────────────────────────
sub1(
"""  'mennyi_icon.png': 'assets/mennyi_icon.png',
  'mennyi_banner.png': 'assets/mennyi_banner.png',""",
"""  'mennyi_icon.png': 'assets/mennyi_icon.png',
  'mennyi_banner.png': 'assets/mennyi_banner.png',
  'arveres_icon.png': 'assets/arveres_icon.png',
  'arveres_banner.png': 'assets/arveres_banner.png',""",
'IMGS arveres')

# ── 2. GAMES bejegyzes ──────────────────────────────────────────────────────
# `stake:[0,6]` — az also hatar 0, mert senki nem koteles licitalni; ha mindenki
# 0-t ad, a nyeremeny elvesz es SENKI nem iszik.
sub1(
"""  { id:'csakegyszó', stake:[1,1], name:'Csak Egy Szó',""",
"""  { id:'arveres', stake:[0,6], roundTime:'mid', name:'Csendes árverés',   difficulty:'közepes', category:'Csapat', emoji:'🔨', isNew:true, img:IMGS['arveres_icon.png'], banner:IMGS['arveres_banner.png'], color:'#F5B93B', desc:'Az app kisorsol egy nyereményt — például hogy a következő két körben nem kell innod. Mindenki TITOKBAN licitál 0–6 kortyot: a telefon körbemegy, és senki nem látja a többiek számát. A legmagasabb licit nyeri a nyereményt, és annyit iszik, amennyit ígért. Ha mindenki nullát ad, a nyeremény elvész. Pont nincs — a nyeremény maga a tét.' },
  { id:'csakegyszó', stake:[1,1], name:'Csak Egy Szó',""",
'GAMES arveres')

# ── 3. SCENARIOS ────────────────────────────────────────────────────────────
# `cta: []` — a jatek maga konyvel, tehat a kezi „Vesztettem / Nyertem!" par
# egy masodik, ellentmondo utat nyitna (v10.350).
sub1(
"""  mennyi:    { prompt:'Mondjatok egy tippet — aki közelebb van, nyer!', cta:[] },""",
"""  mennyi:    { prompt:'Mondjatok egy tippet — aki közelebb van, nyer!', cta:[] },
  arveres:   { prompt:'Titkos licit — a legtöbbet ígérő nyer, és issza is!', cta:[] },""",
'SCENARIOS arveres')

# ── 4. A JATEK ──────────────────────────────────────────────────────────────
sub1(
"""// ═══════════════ Mennyi? — becslő párbaj ═══════════════""",
"""// ═══════════════ Csendes árverés — korty-aukció ═══════════════
// Az app kisorsol egy nyeremenyt, es mindenki TITOKBAN licital kortyot.
// A legmagasabb licit nyer — es annyit iszik, amennyit igert.
//
// ⚠️ A TITKOSSAG A JATEK FELE: aki latja a masik szamat, csak ra tesz egyet,
// es akkor nincs dontes, csak sorrend. Ezert megy korbe a telefon.
//
// ⚠️ A DIJAK MONDATOK, nem kod. A `PlayScreen` nem tarol kor-kozi allapotot,
// tehat egy „a kovetkezo korben nem iszol" hatast az app nem tudna
// ervenyesiteni — a tarsasag tartatja be. Uj dij felvetelenel EZ a szabaly:
// magaban ertheto, es a tarsasag maga be tudja tartatni.
const ARVERES_MAX_BID = 6;

const ARVERES_DIJAK = [
  'A következő két körben nem kell innod.',
  'Kioszthatsz 3 kortyot — bárkinek, ahogy akarod.',
  'Egyszer bárkit megkérhetsz, hogy igyon helyetted.',
  'A következő játékot kihagyhatod.',
  'A következő körben te választod ki, ki játszik.',
  'Kitalálsz egy szabályt a következő körre — mindenkire vonatkozik.',
  'A következő körben feleannyit iszol, mint amennyit kapnál.',
  'Egyszer visszadobhatsz egy kortyot annak, aki adta.',
];

// Modul-szintu, mert a jatek torzseben minden ujrarendereles ujramountolna
// (v10.335). Itt a lepteto miatt suru a rendereles.
function ArveresDijCard({ dij, compact }) {
  return (
    <div style={{ width:'100%', background:T.surface, borderRadius:20, padding: compact ? '12px 16px' : '18px 20px',
                  boxShadow:T.shadow, boxSizing:'border-box', textAlign:'center' }}>
      <div style={{ fontFamily:T.font, fontSize:11, fontWeight:800, color:T.inkMute,
                    textTransform:'uppercase', letterSpacing:'0.12em' }}>A nyeremény</div>
      <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize: compact ? 16 : 20,
                    color:T.ink, lineHeight:1.25, marginTop:6 }}>{dij}</div>
    </div>
  );
}

function ArveresGame({ gameIdx, players, onAdvance, onResult, drinkMult = 1 }) {
  const pl = (players || []).filter(Boolean);
  const dij = ARVERES_DIJAK[gameIdx % ARVERES_DIJAK.length];
  const [phase, setPhase] = React.useState('intro');   // 'intro' | 'bid' | 'reveal'
  const [idx, setIdx] = React.useState(0);
  const [open, setOpen] = React.useState(false);       // latja-e mar a leptetot
  const [bid, setBid] = React.useState(0);
  const [bids, setBids] = React.useState({});
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    setPhase('intro'); setIdx(0); setOpen(false); setBid(0); setBids({});
    advancedRef.current = false;
  }, [gameIdx]);

  // ⚠️ NYERS szam megy MINDKET csatornara — a `PlayScreen` szoroz (`onResult`
  // maga, az `onAdvance` a konyvelesben). Ha itt is szoroznank, duplan menne fel
  // (v10.299 Loverseny-lecke). A `drinkMult` csak a KIJELZEST skalazza.
  const settle = (all) => {
    if (advancedRef.current) return;
    advancedRef.current = true;
    const top = Math.max(0, ...pl.map(p => all[p.id] || 0));
    const winners = top > 0 ? pl.filter(p => (all[p.id] || 0) === top) : [];
    if (winners.length === 0) {
      // Valodi no-op: nincs mit konyvelni, tehat a legacy alak helyes — nincs
      // mit megforditania a „Fordított kör" wildcardnak sem (v10.354).
      onResult && onResult({ correct:true, playerName:null, drinks:0,
        subtitle:'Senki nem licitált — a nyeremény elveszett.' });
      onAdvance && onAdvance({}, {});
      return;
    }
    // ⚠️ A NYERTES a banner ISZIK-oldalan all, es ez szandekos: pontosan annyit
    // iszik, amennyit igert. Amit nyert, az a `loseNote`-ban all. Pont nincs —
    // a nyeremeny maga a jutalom (mint az Ultimatumnal).
    onResult && onResult({ winners: [], losers: winners, drinks: top,
      loseNote: 'Nyeremény: ' + dij });
    const dm = {}; winners.forEach(p => { dm[p.id] = top; });
    onAdvance && onAdvance(dm, {});
  };

  const wrap = { display:'flex', flexDirection:'column', alignItems:'center', gap:14, width:'100%' };
  const bigBtn = (bg) => ({ width:'100%', minHeight:60, borderRadius:16, border:'none', background:bg,
                            color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16,
                            cursor:'pointer', boxShadow:T.shadow });

  if (phase === 'intro') return (
    <div style={wrap}>
      <ArveresDijCard dij={dij} />
      <div style={{ width:'100%', background:T.surfaceMuted, borderRadius:16, padding:'14px 16px',
                    boxSizing:'border-box', fontFamily:T.font, fontSize:13, color:T.inkSoft,
                    textAlign:'center', lineHeight:1.5 }}>
        A telefon körbemegy. Mindenki <strong style={{ color:T.ink }}>titokban</strong> licitál
        0–{ARVERES_MAX_BID * drinkMult} kortyot. A legtöbbet ígérő nyeri a nyereményt — és annyit iszik.
      </div>
      <button onClick={() => { setPhase('bid'); setIdx(0); setOpen(false); setBid(0); }}
        style={bigBtn(T.mint)}>Licitálás indul</button>
    </div>
  );

  if (phase === 'bid') {
    const cur = pl[idx];
    const step = (d) => setBid(v => Math.max(0, Math.min(ARVERES_MAX_BID, v + d)));
    const done = () => {
      const all = { ...bids, [cur.id]: bid };
      setBids(all);
      if (idx < pl.length - 1) { setIdx(idx + 1); setOpen(false); setBid(0); }
      else { setPhase('reveal'); settle(all); }
    };
    return (
      <div style={wrap}>
        <ArveresDijCard dij={dij} compact />
        <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'18px 18px 20px',
                      boxShadow:T.shadow, boxSizing:'border-box', textAlign:'center' }}>
          {!open ? (
            <React.Fragment>
              <div style={{ fontFamily:T.font, fontSize:12.5, fontWeight:700, color:T.inkSoft }}>Add át a telefont</div>
              <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:8, margin:'14px 0 16px' }}>
                <PlayerAvatar player={cur} size={64} />
                <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:T.ink }}>{cur?.name}</div>
              </div>
              <button onClick={() => { setOpen(true); setBid(0); }} style={bigBtn(T.ink)}>
                Én vagyok {cur?.name}
              </button>
            </React.Fragment>
          ) : (
            <React.Fragment>
              <div style={{ fontFamily:T.font, fontSize:12.5, fontWeight:700, color:T.inkSoft }}>
                Mennyit ígérsz, <strong style={{ color:T.ink }}>{cur?.name}</strong>?
              </div>
              <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:16, margin:'14px 0 10px' }}>
                <button onClick={() => step(-1)} disabled={bid <= 0} aria-label="Egy korttyal kevesebb"
                  style={{ width:48, height:48, borderRadius:'50%', border:'none', background:T.coralSoft,
                           cursor: bid > 0 ? 'pointer' : 'default', opacity: bid > 0 ? 1 : 0.4,
                           display:'grid', placeItems:'center' }}>
                  <BohIcon name="minus" size={22} />
                </button>
                <div style={{ minWidth:92, textAlign:'center' }}>
                  <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:44, color:T.ink, lineHeight:1 }}>{bid * drinkMult}</div>
                  <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkMute,
                                textTransform:'uppercase', letterSpacing:'0.1em' }}>korty</div>
                </div>
                <button onClick={() => step(1)} disabled={bid >= ARVERES_MAX_BID} aria-label="Egy korttyal több"
                  style={{ width:48, height:48, borderRadius:'50%', border:'none', background:T.mintSoft,
                           cursor: bid < ARVERES_MAX_BID ? 'pointer' : 'default', opacity: bid < ARVERES_MAX_BID ? 1 : 0.4,
                           display:'grid', placeItems:'center' }}>
                  <BohIcon name="plus" size={22} />
                </button>
              </div>
              <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginBottom:14 }}>
                Senki ne lássa — utána add tovább a telefont.
              </div>
              <button onClick={done} style={bigBtn(T.mint)}>
                {idx < pl.length - 1 ? 'Kész, jöhet a következő' : 'Kész — felfedés'}
              </button>
            </React.Fragment>
          )}
        </div>
        {/* Haladas: ki adta be mar a licitet. A SZAM sehol nem latszik. */}
        <div style={{ display:'flex', gap:6, flexWrap:'wrap', justifyContent:'center' }}>
          {pl.map((p, i) => (
            <span key={p.id} style={{ padding:'4px 10px', borderRadius:999, fontFamily:T.font, fontSize:11, fontWeight:700,
                                      background: i < idx ? T.mintSoft : i === idx ? T.surfaceMuted : 'transparent',
                                      border: i === idx ? '1.5px solid ' + T.ink + '22' : '1.5px solid transparent',
                                      color: i < idx ? T.mint : T.inkSoft }}>{p.name}</span>
          ))}
        </div>
      </div>
    );
  }

  const top = Math.max(0, ...pl.map(p => bids[p.id] || 0));
  const sorted = [...pl].sort((a, b) => (bids[b.id] || 0) - (bids[a.id] || 0));
  return (
    <div style={wrap}>
      <ArveresDijCard dij={dij} compact />
      <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:6 }}>
        {sorted.map(p => {
          const won = top > 0 && (bids[p.id] || 0) === top;
          return <PlayerDrinkRow key={p.id} p={p} cnt={bids[p.id] || 0} readOnly drinkMult={drinkMult}
            meta={won ? (
              /* ⚠️ „NYERT", nem „NYERTES": a result banner oldal-felirata
                 pontosan „Nyertes" / „Nyertesek", es a ket felulet egyszerre
                 van a kepernyon. Ugyanez a kulonbsegtetel all az Idoparbaj
                 jatekos-kartyajan is. */
              <span style={{ flexShrink:0, padding:'3px 9px', borderRadius:999, background:T.mint, color:'#fff',
                             fontFamily:T.font, fontWeight:900, fontSize:10, letterSpacing:'0.08em' }}>NYERT</span>
            ) : null} />;
        })}
      </div>
      <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', lineHeight:1.5 }}>
        {top > 0 ? 'A nyeremény a legmagasabb licité — és annyit is iszik.'
                 : 'Senki nem licitált, a nyeremény elveszett.'}
      </div>
    </div>
  );
}

// ═══════════════ Mennyi? — becslő párbaj ═══════════════""",
'ArveresGame komponens')

# ── 5. Bekotes ──────────────────────────────────────────────────────────────
sub1(
"""  if (gameId === 'mennyi') return <MennyiGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;""",
"""  if (gameId === 'mennyi') return <MennyiGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'arveres') return <ArveresGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} drinkMult={drinkMult} />;""",
'GameContent bekotes')

# ── 6. A „Ki rontott?" panel kizarasa ───────────────────────────────────────
# ⚠️ MERVE, nem feltetelezve: az elso vegigjatszassal a jatek ALATT ott allt a
# „KI RONTOTT? … Senki nem rontott" panel. Az `advanceLoverseny`-t hivja, tehat
# egy MASODIK, ellentmondo utat nyitott a konyveleshez — pontosan az, amit a
# `cta: []` a Paros jatekoknal megsziuntet.
#
# ⚠️ A `cta: []` a CSAPAT jatekokra NEM hat: ott ez a hosszu id-lista dont
# (`sohanem`, `ovfj`, `collect`, `memoria`… mind igy van kizarva). Uj csapat-
# jateknal, ami maga konyvel, MINDKETTOT be kell allitani.
sub1(
"""currentGameId !== 'meduza' && currentGameId !== 'fingerit' && (""",
"""currentGameId !== 'meduza' && currentGameId !== 'fingerit' && currentGameId !== 'arveres' && (""",
'Ki rontott? kizaras')

sub1("const APP_VERSION = 'v10.359';", "const APP_VERSION = 'v10.360';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_360 alkalmazva')
