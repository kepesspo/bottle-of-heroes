#!/usr/bin/env python3
"""v9.399 — Szólánc: teljes átírás — villogó szavak + grid visszamondás"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. comingSoon eltávolítása a szolánc bejegyzésből ────────────────────────
old_szolanc_game = """  { id:'szolánc',   name:'Szólánc',              difficulty:'közepes', category:'Csapat', emoji:'🔗', symbol:IMGS['szolanc_symbol.png'], img:IMGS['szolanc_icon.png'], banner:IMGS['szolanc_banner.png'], color:'#F59E0B', comingSoon:true, desc:'Ismételd el a sort, majd told hozzá egy új szót a kategóriából. Aki elront, iszik.' },"""
new_szolanc_game = """  { id:'szolánc',   name:'Szólánc',              difficulty:'közepes', category:'Csapat', emoji:'🔗', symbol:IMGS['szolanc_symbol.png'], img:IMGS['szolanc_icon.png'], banner:IMGS['szolanc_banner.png'], color:'#F59E0B', desc:'Minden körben egy szóval több villog fel a képernyőn. Sorrendben vissza kell koppintani a szavakat. Aki elront, iszik — a többiek pontot kapnak.' },"""

assert old_szolanc_game in html, "FAIL: szolanc game entry"
html = html.replace(old_szolanc_game, new_szolanc_game, 1)

# ── 2. Teljes SzolancGame komponens csere ────────────────────────────────────
old_component_start = "function SzolancGame({ gameIdx, players, onAdvance, onResult }) {"
old_component_end_marker = "  if (gameId === 'szolánc') return <SzolancGame"

# Find start and end
start_idx = html.index(old_component_start)
end_idx = html.index(old_component_end_marker)

old_component = html[start_idx:end_idx]

new_component = """function SzolancGame({ gameIdx, players, onAdvance, onResult, onSetHideFooter }) {
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

  const fresh = (chainLen, turnIdx) => {
    const chain = allWords.slice(0, chainLen);
    return { phase:'show', chain, showIdx:0, gridWords:[], tapped:[], turnIdx, wrongIdx:null };
  };

  const [S, setS] = React.useState(() => fresh(1, 0));
  const [done, setDone] = React.useState(null); // { failName, failColor, failPid }

  React.useEffect(() => { setS(fresh(1, 0)); setDone(null); }, [gameIdx]);
  React.useEffect(() => {
    if (onSetHideFooter) onSetHideFooter(true);
    return () => { if (onSetHideFooter) onSetHideFooter(false); };
  }, []);

  const curPlayer = players[S.turnIdx % players.length];

  // ── Show fázis: szavak villogása ──────────────────────────────────────────
  React.useEffect(() => {
    if (S.phase !== 'show') return;
    if (S.showIdx < S.chain.length) {
      const t = setTimeout(() => setS(s => ({...s, showIdx: s.showIdx + 1})), 1300);
      return () => clearTimeout(t);
    }
    // Minden szó megjelent → grid
    const shuffled = [...S.chain].sort(() => Math.random() - 0.5);
    const t = setTimeout(() => setS(s => ({...s, phase:'recall', gridWords:shuffled, tapped:[]})), 600);
    return () => clearTimeout(t);
  }, [S.phase, S.showIdx]);

  // ── Recall fázis: koppintás kezelése ─────────────────────────────────────
  const tapWord = (word, idx) => {
    if (S.phase !== 'recall') return;
    if (S.tapped.includes(idx)) return;
    const expected = S.chain[S.tapped.length];
    if (word !== expected) {
      // HIBÁS
      setS(s => ({...s, wrongIdx: idx}));
      setTimeout(() => {
        const pid = curPlayer?.id;
        if (onAdvance) onAdvance({[pid]: 1});
        setDone({ failName: curPlayer?.name, failColor: curPlayer?.color, failPid: pid });
      }, 700);
      return;
    }
    const newTapped = [...S.tapped, idx];
    if (newTapped.length === S.chain.length) {
      // HELYES — következő kör
      setS(s => ({...s, phase:'correct', tapped: newTapped}));
      const nextTurnIdx = S.turnIdx + 1;
      const nextChainLen = S.chain.length + 1;
      if (nextChainLen > allWords.length) {
        // Elfogytak a szavak — mindenki nyert
        setTimeout(() => setDone({ failName: null }), 1200);
      } else {
        setTimeout(() => setS(fresh(nextChainLen, nextTurnIdx)), 1200);
      }
    } else {
      setS(s => ({...s, tapped: newTapped}));
    }
  };

  // ── DONE képernyő ─────────────────────────────────────────────────────────
  if (done !== null) {
    const winMsg = !done.failName;
    return (
      <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:16,padding:'24px 0',textAlign:'center',animation:'popIn .4s cubic-bezier(.2,.9,.3,1.2)'}}>
        <div style={{fontSize:52}}>{winMsg ? '🏆' : '😵'}</div>
        <div style={{fontFamily:T.font,fontWeight:900,fontSize:22,color:winMsg?T.mint:T.coral}}>
          {winMsg ? 'Bravo! Elfogytak a szavak!' : `${done.failName} elrontotta!`}
        </div>
        {!winMsg && (
          <div style={{display:'flex',flexDirection:'column',gap:8,width:'100%'}}>
            <div style={{padding:'12px 16px',borderRadius:14,background:T.coral+'18',border:'1.5px solid '+T.coral+'44',fontFamily:T.font,fontWeight:700,fontSize:15,color:T.coral}}>
              🍺 {done.failName} iszik egyet
            </div>
            <div style={{padding:'12px 16px',borderRadius:14,background:T.mint+'18',border:'1.5px solid '+T.mint+'44',fontFamily:T.font,fontWeight:700,fontSize:15,color:T.mint}}>
              ⭐ A többiek pontot kapnak
            </div>
          </div>
        )}
        <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft,marginTop:4}}>
          Elért szint: {S.chain.length} szó · {cat}
        </div>
      </div>
    );
  }

  // ── Show fázis UI ─────────────────────────────────────────────────────────
  if (S.phase === 'show' || S.phase === 'correct') {
    const currentWord = S.phase === 'show' && S.showIdx < S.chain.length ? S.chain[S.showIdx] : null;
    const isCorrect = S.phase === 'correct';
    return (
      <div style={{display:'flex',flexDirection:'column',gap:14}}>
        {/* Fejléc */}
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'4px 0'}}>
          <div style={{display:'inline-flex',alignItems:'center',gap:8,padding:'5px 14px',background:curPlayer?.color+'22'||T.mint+'22',borderRadius:999}}>
            <div style={{width:8,height:8,borderRadius:'50%',background:curPlayer?.color||T.mint}} />
            <span style={{fontFamily:T.font,fontWeight:800,fontSize:14,color:T.ink}}>{curPlayer?.name}</span>
          </div>
          <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft}}>{cat}</div>
        </div>

        {/* Szó megjelenítő */}
        <div style={{
          minHeight:120, borderRadius:20, background:T.surface, boxShadow:T.shadow,
          display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center',
          padding:'24px', gap:12,
        }}>
          {isCorrect ? (
            <div style={{textAlign:'center',animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)'}}>
              <div style={{fontSize:36}}>✅</div>
              <div style={{fontFamily:T.font,fontWeight:900,fontSize:18,color:T.mint,marginTop:8}}>Helyes! Következő…</div>
            </div>
          ) : currentWord ? (
            <div key={S.showIdx} style={{textAlign:'center',animation:'popIn .25s cubic-bezier(.2,.9,.3,1.1)'}}>
              <div style={{fontFamily:T.font,fontWeight:900,fontSize:32,color:T.ink,letterSpacing:'-0.02em'}}>{currentWord}</div>
              <div style={{display:'flex',gap:6,marginTop:14,justifyContent:'center'}}>
                {S.chain.map((_,i) => (
                  <div key={i} style={{width:8,height:8,borderRadius:'50%',background:i<=S.showIdx?T.mint:T.surfaceMuted,transition:'background .2s'}} />
                ))}
              </div>
            </div>
          ) : (
            <div style={{textAlign:'center'}}>
              <div style={{fontFamily:T.font,fontWeight:700,fontSize:16,color:T.inkSoft}}>Felkészülés…</div>
            </div>
          )}
        </div>

        {/* Lánc előnézet */}
        <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,textAlign:'center'}}>
          {S.chain.length}. szint — {S.chain.length} szót kell visszamondani
        </div>
      </div>
    );
  }

  // ── Recall fázis UI ───────────────────────────────────────────────────────
  if (S.phase === 'recall') {
    const cols = S.gridWords.length <= 4 ? 2 : S.gridWords.length <= 9 ? 3 : 4;
    return (
      <div style={{display:'flex',flexDirection:'column',gap:14}}>
        {/* Fejléc */}
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'4px 0'}}>
          <div style={{display:'inline-flex',alignItems:'center',gap:8,padding:'5px 14px',background:curPlayer?.color+'22'||T.mint+'22',borderRadius:999}}>
            <div style={{width:8,height:8,borderRadius:'50%',background:curPlayer?.color||T.mint}} />
            <span style={{fontFamily:T.font,fontWeight:800,fontSize:14,color:T.ink}}>{curPlayer?.name} — sorrendben!</span>
          </div>
          <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft}}>{S.tapped.length}/{S.chain.length}</div>
        </div>

        {/* Haladás */}
        <div style={{height:4,borderRadius:4,background:T.surfaceMuted,overflow:'hidden'}}>
          <div style={{height:'100%',borderRadius:4,background:T.mint,width:(S.tapped.length/S.chain.length*100)+'%',transition:'width .2s'}} />
        </div>

        {/* Grid */}
        <div style={{display:'grid',gridTemplateColumns:`repeat(${cols},1fr)`,gap:10}}>
          {S.gridWords.map((word, idx) => {
            const tappedOrder = S.tapped.indexOf(idx);
            const isTapped = tappedOrder !== -1;
            const isWrong = S.wrongIdx === idx;
            return (
              <button key={idx} onClick={() => tapWord(word, idx)} disabled={isTapped} style={{
                padding:'14px 8px', borderRadius:14, border:'none', cursor: isTapped?'default':'pointer',
                background: isWrong ? T.coral+'33' : isTapped ? T.mint+'22' : T.surface,
                boxShadow: isTapped||isWrong ? 'none' : T.shadow,
                fontFamily:T.font, fontWeight:800, fontSize:15, color: isTapped?T.mint:isWrong?T.coral:T.ink,
                transition:'all .15s',
                transform: isWrong ? 'scale(0.95)' : 'none',
                position:'relative',
                animation: isWrong ? 'shakeDrink .4s ease' : 'none',
              }}>
                {isTapped && (
                  <div style={{position:'absolute',top:4,right:6,fontFamily:T.font,fontSize:10,fontWeight:900,color:T.mint}}>
                    {tappedOrder+1}
                  </div>
                )}
                {word}
              </button>
            );
          })}
        </div>

        <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,textAlign:'center'}}>
          Koppints a szavakra sorrendben
        </div>
      </div>
    );
  }

  return null;
}

"""

html = html[:start_idx] + new_component + html[end_idx:]

# ── 3. GameContent: onSetHideFooter átadása ───────────────────────────────────
old_gc = "  if (gameId === 'szolánc') return <SzolancGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;"
new_gc = "  if (gameId === 'szolánc') return <SzolancGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} />;"

assert old_gc in html, "FAIL: gamecontent szolánc"
html = html.replace(old_gc, new_gc, 1)

html = html.replace("const APP_VERSION = 'v9.398';", "const APP_VERSION = 'v9.399';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.399 — Szólánc teljes átírás: villogó szavak + grid visszamondás")
