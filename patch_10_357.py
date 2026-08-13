# v10.357 - Harom uj paros jatek: IGEN–NEM, ULTIMATUM, MENNYI?
#
# ── IGEN–NEM ────────────────────────────────────────────────────────────────
# Az egyik lat egy szot, a masik legfeljebb 10 igen/nem kerdessel probalja
# kitalalni. KOOPERATIV: talalt -> mindketto pont, nem -> mindketto iszik.
# A szobank a MEGLEVO `MUTASD_SZAVAK` — konkret fonevek, pont erre valok.
# Uj bank helyett ezt hasznaljuk: egy forras, es nem kell 100 szot karbantartani.
#
# ── ULTIMATUM ───────────────────────────────────────────────────────────────
# 6 korty a kalapban. „A" ajanlatot tesz (ki mennyit iszik), „B" elfogadja vagy
# elutasitja. Elutasitas -> MINDKETTEN a felet isszak.
# ⚠️ A visszautasitas KOZOS bukas, nem buntetes: ha csak az ajanlattevo inna,
# „B"-nek mindig megerne visszautasitani, es nem lenne alku.
#
# ── MENNYI? ─────────────────────────────────────────────────────────────────
# Szam-kerdes; mindketten bemondanak egy szamot, a KOZELEBBI nyer.
# ⚠️ Az app NEM keri be a ket tippet. Ket szam-mezo a hoston lassu es hibazos;
# a szamokat ugyis hangosan mondjatok. Az app felfedi a valaszt, es utana
# jelolitek, ki volt kozelebb — ugyanaz a minta, mint az Ujjosszegnel.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# ── 1. GAMES bejegyzesek ────────────────────────────────────────────────────
sub1(
"""  { id:'csakegyszó',""",
"""  { id:'igennem', stake:[1,1], roundTime:'mid', name:'Igen–Nem',            difficulty:'közepes', category:'Páros', emoji:'❓', isNew:true, img:IMGS['igennem_icon.png'], banner:IMGS['igennem_banner.png'], color:'#4FC2A0', desc:'Az egyik játékos lát egy szót, a másik legfeljebb 10 IGEN/NEM kérdéssel próbálja kitalálni. Közösen játszotok: ha megvan a szó, mindketten pontot kaptok — ha elfogynak a kérdések, mindketten isztok. A kérdező nem tippelhet a végtelenségig, ezért a jó kérdés többet ér, mint a szerencse.' },
  { id:'ultimatum', stake:[1,6], roundTime:'fast', name:'Ultimátum',          difficulty:'közepes', category:'Páros', emoji:'⚖️', isNew:true, img:IMGS['ultimatum_icon.png'], banner:IMGS['ultimatum_banner.png'], color:'#F5B93B', desc:'Hat korty van a kalapban. Az egyik játékos ajánlatot tesz, hogy ki mennyit igyon belőle — a másik pedig elfogadja vagy elutasítja. Ha elfogadja, úgy isszátok, ahogy az ajánlat szól. Ha elutasítja, mindketten a kalap felét isszátok. Nem az számít, mi az igazságos, hanem hogy mit fogadnak el.' },
  { id:'mennyi', stake:[1,1], roundTime:'fast', name:'Mennyi?',              difficulty:'közepes', category:'Páros', emoji:'📏', isNew:true, img:IMGS['mennyi_icon.png'], banner:IMGS['mennyi_banner.png'], color:'#5BA0DB', desc:'Jön egy szám-kérdés, amit senki nem tud pontosan. Mindketten bemondtok egy tippet, aztán az app felfedi a választ. Aki közelebb volt, pontot kap — a másik iszik. Nem tudni kell, hanem jól saccolni.' },
  { id:'csakegyszó',""",
'GAMES harom uj jatek')

# ── 2. SCENARIOS — mindharom MAGA konyvel (ures cta) ────────────────────────
sub1(
"""  fingerit:  { prompt:'Egyszerre mutassatok ujjakat — és mondjátok be az összeget!', cta:[] },""",
"""  fingerit:  { prompt:'Egyszerre mutassatok ujjakat — és mondjátok be az összeget!', cta:[] },
  igennem:   { prompt:'Tíz igen/nem kérdés — közösen nyertek vagy isztok!', cta:[] },
  ultimatum: { prompt:'Tegyél ajánlatot — de csak akkor ér valamit, ha elfogadják!', cta:[] },
  mennyi:    { prompt:'Mondjatok egy tippet — aki közelebb van, nyer!', cta:[] },""",
'SCENARIOS harom uj jatek')

# ── 3. Szam-kerdesek a MENNYI?-hez ──────────────────────────────────────────
sub1(
"""// ═══════════════ Chicken — kockázat-lépcső ═══════════════""",
"""// A „Mennyi?" szam-kerdesei. ⚠️ Mind KEREK, ellenorizheto teny — a jatek
// lenyege a becsles, nem a talalgatas: ha a valasz vitathato, a kor vitaba
// fullad ahelyett, hogy eldolne.
const MENNYI_KERDESEK = [
  { q:'Hány csontja van egy felnőtt embernek?', n:206, u:'db' },
  { q:'Hány billentyű van egy zongorán?', n:88, u:'db' },
  { q:'Hány mezőből áll egy sakktábla?', n:64, u:'db' },
  { q:'Hány méter magas az Eiffel-torony?', n:330, u:'m' },
  { q:'Hány lapból áll egy francia kártyapakli (joker nélkül)?', n:52, u:'db' },
  { q:'Hány csillag van az EU zászlaján?', n:12, u:'db' },
  { q:'Hány foga van egy felnőtt embernek (bölcsességfoggal)?', n:32, u:'db' },
  { q:'Hány megye van Magyarországon?', n:19, u:'db' },
  { q:'Hány kerülete van Budapestnek?', n:23, u:'db' },
  { q:'Hány ország tagja az ENSZ-nek?', n:193, u:'db' },
  { q:'Hány méter magas a Mount Everest?', n:8849, u:'m' },
  { q:'Hány hét van egy évben?', n:52, u:'db' },
  { q:'Hány másodperc egy óra?', n:3600, u:'mp' },
  { q:'Hány nap van egy szökőévben?', n:366, u:'nap' },
  { q:'Hány ember járt eddig a Holdon?', n:12, u:'fő' },
  { q:'Hány csontból áll az emberi kéz?', n:27, u:'db' },
  { q:'Hány húrja van egy gitárnak?', n:6, u:'db' },
  { q:'Hány dominó van egy dupla-hatos készletben?', n:28, u:'db' },
  { q:'Hány sakkfigura áll a táblán a játszma elején?', n:32, u:'db' },
  { q:'Hány pontot ér a bika közepe a dartsban?', n:50, u:'pont' },
  { q:'Hány kilométer egy maratoni táv (kerekítve)?', n:42, u:'km' },
  { q:'Hány perc egy focimeccs hosszabbítás nélkül?', n:90, u:'perc' },
  { q:'Hány gyűrű van az olimpiai zászlón?', n:5, u:'db' },
  { q:'Hány fekete billentyű van egy zongorán?', n:36, u:'db' },
  { q:'Hány fokos a víz forráspontja Celsiusban?', n:100, u:'°C' },
  { q:'Hány fok egy háromszög szögeinek összege?', n:180, u:'fok' },
  { q:'Hány liter vér van egy felnőtt emberben (kerekítve)?', n:5, u:'liter' },
  { q:'Hány csík van az USA zászlaján?', n:13, u:'db' },
  { q:'Hány bolygó van a Naprendszerben?', n:8, u:'db' },
  { q:'Hány centiméter egy láb (foot)?', n:30, u:'cm' },
  { q:'Hány négyzet van egy Rubik-kocka egy oldalán?', n:9, u:'db' },
  { q:'Hány jégkorongozó van a pályán csapatonként (kapussal)?', n:6, u:'fő' },
  { q:'Hány perc egy NBA-negyed?', n:12, u:'perc' },
  { q:'Hány éves korban lesz valaki nagykorú Magyarországon?', n:18, u:'év' },
  { q:'Hány billentyűs egy szabványos számítógép-billentyűzet?', n:104, u:'db' },
  { q:'Hány oldala van egy focilabda fekete foltjának?', n:5, u:'db' },
];
(()=>{ for(let i=MENNYI_KERDESEK.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [MENNYI_KERDESEK[i],MENNYI_KERDESEK[j]]=[MENNYI_KERDESEK[j],MENNYI_KERDESEK[i]]; } })();

// ═══════════════ Chicken — kockázat-lépcső ═══════════════""",
'MENNYI kerdesbank')

# ── 4. A harom komponens ────────────────────────────────────────────────────
sub1(
"""// ═══════════════ Ujjösszeg (Morra) — páros blöff ═══════════════""",
"""// ═══════════════ Igen–Nem — 10 kérdés ═══════════════
// KOOPERATIV: az egyik latja a szot, a masik kerdez. Talalt -> mindketto pont,
// nem -> mindketto iszik. A szobank a MEGLEVO `MUTASD_SZAVAK` (konkret fonevek)
// — uj bank helyett egy forrast hasznalunk.
const IGENNEM_MAX_Q = 10;

function IgenNemGame({ gameIdx, challenger, opponent, onAdvance, onResult }) {
  const word = MUTASD_SZAVAK[(gameIdx * 7) % MUTASD_SZAVAK.length];
  const [phase, setPhase] = React.useState('ready');   // 'ready' | 'run' | 'done'
  const [left, setLeft] = React.useState(IGENNEM_MAX_Q);
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    setPhase('ready'); setLeft(IGENNEM_MAX_Q); advancedRef.current = false;
  }, [gameIdx, challenger?.id]);

  const finish = (guessed) => {
    if (advancedRef.current) return;
    advancedRef.current = true;
    setPhase('done');
    const both = [challenger, opponent].filter(Boolean);
    onResult && onResult(guessed
      ? { winners: both, losers: [], drinks: 0, winNote: '+1 pont', loseNote: `A szó: ${word}` }
      : { winners: [], losers: both, drinks: 1, loseNote: `A szó ${word} volt — mindketten isztok.` });
    const dm = {}, pm = {};
    both.forEach(p => { if (guessed) pm[p.id] = 1; else dm[p.id] = 1; });
    onAdvance && onAdvance(dm, pm);
  };

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16, width:'100%' }}>
      <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'18px', textAlign:'center', boxShadow:T.shadow, boxSizing:'border-box' }}>
        <div style={{ fontFamily:T.font, fontSize:12, fontWeight:800, color:T.inkSoft, letterSpacing:'0.08em', textTransform:'uppercase', marginBottom:6 }}>
          {phase === 'ready' ? `${challenger?.name || 'A kihívó'} nézi meg a szót` : 'A szó'}
        </div>
        {phase === 'ready' ? (
          /* A szo REJTVE marad, amig el nem indul: a kerdezo kulonben
             belelathatna, es nem lenne mit kitalalni. */
          <div style={{ height:34, borderRadius:8, background:'repeating-linear-gradient(-45deg,#e0e4f0,#e0e4f0 4px,#d0d4e4 4px,#d0d4e4 8px)' }}/>
        ) : (
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:30, color:T.ink, lineHeight:1.1 }}>{word}</div>
        )}
      </div>

      {phase === 'ready' ? (
        <React.Fragment>
          <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'16px 18px', boxShadow:T.shadow, boxSizing:'border-box', fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', lineHeight:1.5 }}>
            <strong style={{ color:T.ink }}>{opponent?.name || 'Az ellenfél'}</strong> kérdez, legfeljebb {IGENNEM_MAX_Q}-szer —
            csak <strong style={{ color:T.ink }}>igen</strong> vagy <strong style={{ color:T.ink }}>nem</strong> a válasz.
            Ha megvan a szó, <strong style={{ color:T.ink }}>mindketten pontot kaptok</strong>.
          </div>
          <button onClick={() => setPhase('run')} style={{ width:148, height:148, borderRadius:'50%', background:T.mint, border:'none', cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:4, boxShadow:T.shadow }}>
            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:36, color:'#fff', lineHeight:1 }}>▶</div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:'rgba(255,255,255,0.85)' }}>Felfed & Indít</div>
          </button>
        </React.Fragment>
      ) : phase === 'run' ? (
        <React.Fragment>
          <div style={{ display:'flex', alignItems:'baseline', gap:8 }}>
            <span style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:56, color: left <= 3 ? T.coral : T.ink, lineHeight:1 }}>{left}</span>
            <span style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft }}>kérdés maradt</span>
          </div>
          <button onClick={() => { const n = left - 1; setLeft(n); if (n <= 0) finish(false); }}
            disabled={left <= 0}
            style={{ width:'100%', minHeight:60, borderRadius:16, border:'none', background:T.surfaceMuted, color:T.ink, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, cursor:'pointer', boxShadow:T.shadow }}>
            Elment egy kérdés
          </button>
          <button onClick={() => finish(true)} style={{ width:'100%', minHeight:60, borderRadius:16, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, cursor:'pointer', boxShadow:T.shadow }}>
            Kitalálta!
          </button>
        </React.Fragment>
      ) : (
        <div style={{ fontFamily:T.font, fontWeight:800, fontSize:16, color:T.ink }}>Vége!</div>
      )}
    </div>
  );
}

// ═══════════════ Ultimátum — alkudozás ═══════════════
// ⚠️ A VISSZAUTASITAS KOZOS BUKAS, nem buntetes. Ha csak az ajanlattevo inna,
// „B"-nek MINDIG megerne visszautasitani, es nem lenne mirol alkudni.
const ULTIMATUM_POT = 6;

function UltimatumGame({ gameIdx, challenger, opponent, onAdvance, onResult, drinkMult = 1 }) {
  const [phase, setPhase] = React.useState('offer');   // 'offer' | 'answer' | 'done'
  const [give, setGive] = React.useState(Math.floor(ULTIMATUM_POT / 2)); // ennyit iszik az ELLENFEL
  const advancedRef = React.useRef(false);
  const mine = ULTIMATUM_POT - give;

  React.useEffect(() => {
    setPhase('offer'); setGive(Math.floor(ULTIMATUM_POT / 2)); advancedRef.current = false;
  }, [gameIdx, challenger?.id]);

  // ⚠️ NYERS szamok mennek ki — a PlayScreen szoroz. A `loseNote`-ban viszont a
  // MAR SZORZOTT szam all, kulonben a banner szoveg mast mondana, mint a szam.
  const settle = (accepted) => {
    if (advancedRef.current) return;
    advancedRef.current = true;
    setPhase('done');
    const half = Math.ceil(ULTIMATUM_POT / 2);
    const parts = accepted
      ? [{ p: challenger, n: mine }, { p: opponent, n: give }]
      : [{ p: challenger, n: half }, { p: opponent, n: half }];
    const drinkers = parts.filter(x => x.p && x.n > 0);
    const same = drinkers.length > 0 && drinkers.every(x => x.n === drinkers[0].n);
    onResult && onResult({
      winners: [], losers: drinkers.map(x => x.p),
      drinks: drinkers.length ? Math.max(...drinkers.map(x => x.n)) : 0,
      loseNote: accepted
        ? (same ? 'Az ajánlat áll.' : drinkers.map(x => `${x.p.name}: ${x.n * drinkMult}`).join(' · '))
        : 'Elutasítva — a kalap fele mindkettőtöknek.',
    });
    const dm = {}; drinkers.forEach(x => { dm[x.p.id] = x.n; });
    onAdvance && onAdvance(dm, {});
  };

  const step = (d) => setGive(v => Math.max(0, Math.min(ULTIMATUM_POT, v + d)));

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16, width:'100%' }}>
      <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'16px 18px', textAlign:'center', boxShadow:T.shadow, boxSizing:'border-box' }}>
        <div style={{ fontFamily:T.font, fontSize:11.5, fontWeight:800, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.12em' }}>A kalapban</div>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:8, marginTop:4 }}>
          <span style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:46, color:T.coral, lineHeight:1 }}>{ULTIMATUM_POT * drinkMult}</span>
          <BohIcon name="beer" size={24} />
        </div>
      </div>

      {phase === 'offer' ? (
        <React.Fragment>
          <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'16px 18px', boxShadow:T.shadow, boxSizing:'border-box' }}>
            <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', marginBottom:12 }}>
              <strong style={{ color:T.ink }}>{challenger?.name || 'A kihívó'}</strong> ajánlata
            </div>
            <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:16 }}>
              <button onClick={() => step(-1)} disabled={give <= 0} aria-label="Eggyel kevesebb"
                style={{ width:48, height:48, borderRadius:'50%', border:'none', background:T.coralSoft, cursor: give > 0 ? 'pointer' : 'default', opacity: give > 0 ? 1 : 0.4, display:'grid', placeItems:'center' }}>
                <BohIcon name="minus" size={22} />
              </button>
              <div style={{ minWidth:110, textAlign:'center' }}>
                <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:40, color:T.ink, lineHeight:1 }}>{give * drinkMult}</div>
                <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.1em' }}>{opponent?.name || 'neki'}</div>
              </div>
              <button onClick={() => step(1)} disabled={give >= ULTIMATUM_POT} aria-label="Eggyel több"
                style={{ width:48, height:48, borderRadius:'50%', border:'none', background:T.mintSoft, cursor: give < ULTIMATUM_POT ? 'pointer' : 'default', opacity: give < ULTIMATUM_POT ? 1 : 0.4, display:'grid', placeItems:'center' }}>
                <BohIcon name="plus" size={22} />
              </button>
            </div>
            <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkSoft, textAlign:'center', marginTop:12, lineHeight:1.45 }}>
              Marad neked: <strong style={{ color:T.ink }}>{mine * drinkMult} 🍺</strong>
            </div>
          </div>
          <button onClick={() => setPhase('answer')} style={{ width:'100%', minHeight:60, borderRadius:16, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, cursor:'pointer', boxShadow:T.shadow }}>
            Ez az ajánlatom
          </button>
        </React.Fragment>
      ) : phase === 'answer' ? (
        <React.Fragment>
          <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'16px 18px', boxShadow:T.shadow, boxSizing:'border-box', fontFamily:T.font, fontSize:14, color:T.ink, textAlign:'center', lineHeight:1.6 }}>
            <strong>{opponent?.name || 'Az ellenfél'}</strong>, rád {give * drinkMult} 🍺 jut,
            a másikra {mine * drinkMult} 🍺.<br/>
            <span style={{ fontSize:12.5, color:T.inkSoft }}>Ha elutasítod, {Math.ceil(ULTIMATUM_POT / 2) * drinkMult} 🍺 jut MINDKETTŐTÖKNEK.</span>
          </div>
          <button onClick={() => settle(true)} style={{ width:'100%', minHeight:60, borderRadius:16, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, cursor:'pointer', boxShadow:T.shadow }}>
            Elfogadom
          </button>
          <button onClick={() => settle(false)} style={{ width:'100%', minHeight:60, borderRadius:16, border:'none', background:T.coral, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, cursor:'pointer', boxShadow:T.shadow }}>
            Elutasítom
          </button>
        </React.Fragment>
      ) : (
        <div style={{ fontFamily:T.font, fontWeight:800, fontSize:16, color:T.ink }}>Vége!</div>
      )}
    </div>
  );
}

// ═══════════════ Mennyi? — becslő párbaj ═══════════════
// ⚠️ Az app NEM keri be a ket tippet. Ket szam-mezo a hoston lassu es hibazos,
// a szamokat pedig ugyis hangosan mondjatok — az app felfedi a valaszt, es
// utana jelolitek, ki volt kozelebb (ugyanaz a minta, mint az Ujjosszegnel).
function MennyiGame({ gameIdx, challenger, opponent, onAdvance, onResult }) {
  const k = MENNYI_KERDESEK[gameIdx % MENNYI_KERDESEK.length];
  const [revealed, setRevealed] = React.useState(false);
  const advancedRef = React.useRef(false);

  React.useEffect(() => { setRevealed(false); advancedRef.current = false; }, [gameIdx, challenger?.id]);

  const pick = (winner) => {
    if (advancedRef.current) return;
    advancedRef.current = true;
    const loser = winner && winner.id === challenger?.id ? opponent : challenger;
    onResult && onResult({
      winners: winner ? [winner] : [], losers: loser ? [loser] : [], drinks: 1,
      winNote: '+1 pont', loseNote: `A helyes válasz: ${k.n} ${k.u}`,
    });
    const dm = {}, pm = {};
    if (loser)  dm[loser.id]  = 1;
    if (winner) pm[winner.id] = 1;
    onAdvance && onAdvance(dm, pm);
  };

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16, width:'100%' }}>
      <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'20px 18px', textAlign:'center', boxShadow:T.shadow, boxSizing:'border-box' }}>
        <div style={{ fontFamily:T.font, fontSize:11.5, fontWeight:800, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.12em', marginBottom:8 }}>A kérdés</div>
        <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:21, color:T.ink, lineHeight:1.3 }}>{k.q}</div>
      </div>

      {!revealed ? (
        <React.Fragment>
          <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', lineHeight:1.5 }}>
            Mondjatok egy-egy tippet — aztán jöhet a felfedés.
          </div>
          <button onClick={() => setRevealed(true)} style={{ width:148, height:148, borderRadius:'50%', background:T.mint, border:'none', cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:4, boxShadow:T.shadow }}>
            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:34, color:'#fff', lineHeight:1 }}>?</div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:'rgba(255,255,255,0.85)' }}>Felfedés</div>
          </button>
        </React.Fragment>
      ) : (
        <React.Fragment>
          <div style={{ width:'100%', background:T.mintSoft, borderRadius:20, padding:'18px', textAlign:'center', boxSizing:'border-box' }}>
            <div style={{ fontFamily:T.font, fontSize:11.5, fontWeight:800, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.12em' }}>A helyes válasz</div>
            <div style={{ display:'flex', alignItems:'baseline', justifyContent:'center', gap:8, marginTop:4 }}>
              <span style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:46, color:T.ink, lineHeight:1, animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)' }}>{k.n}</span>
              <span style={{ fontFamily:T.font, fontWeight:800, fontSize:16, color:T.inkSoft }}>{k.u}</span>
            </div>
          </div>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft }}>Ki volt közelebb?</div>
          {[challenger, opponent].filter(Boolean).map(pl => (
            <button key={pl.id} onClick={() => pick(pl)} style={{ width:'100%', minHeight:56, borderRadius:16, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, cursor:'pointer', boxShadow:T.shadow }}>
              {pl.name}
            </button>
          ))}
        </React.Fragment>
      )}
    </div>
  );
}

// ═══════════════ Ujjösszeg (Morra) — páros blöff ═══════════════""",
'harom komponens')

# ── 5. Bekotes ──────────────────────────────────────────────────────────────
sub1(
"""  if (gameId === 'chicken') return <ChickenGame""",
"""  if (gameId === 'igennem') return <IgenNemGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'ultimatum') return <UltimatumGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} drinkMult={drinkMult} />;
  if (gameId === 'mennyi') return <MennyiGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'chicken') return <ChickenGame""",
'GameContent harom uj jatek')

sub1("const APP_VERSION = 'v10.356';", "const APP_VERSION = 'v10.357';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_357 alkalmazva')
