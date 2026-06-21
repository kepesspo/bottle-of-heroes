#!/usr/bin/env python3
"""v9.411 — SzolancGame teljes UI redesign a Claude design mockup alapján"""

with open('index.html', 'r', encoding='utf-8') as f:
    src = f.read()

# ── 1. SzolancGame csere ──────────────────────────────────────────────────────

OLD = r"""function SzolancGame({ gameIdx, players, onAdvance, onResult, onSetHideFooter }) {
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

  const [S, setS] = React.useState(() => fresh(2, 0));
  const [done, setDone] = React.useState(null);

  React.useEffect(() => { setS(fresh(2, 0)); setDone(null); }, [gameIdx]);

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
        if (onResult) onResult({ correct: false, playerName: curPlayer?.name, drinks: 1, subtitle: (curPlayer?.name || 'Valaki') + ' elrontotta!' });
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
        setTimeout(() => { if (onResult) onResult({ correct: true, playerName: null, drinks: 0 }); setDone({ failName: null }); }, 1200);
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
          {winMsg ? 'Bravo! Elfogytak a szavak!' : 'Valaki elrontotta!'}
        </div>

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
      <div style={{display:'flex',flexDirection:'column',gap:14,overflowY:'auto'}}>
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
      <div style={{display:'flex',flexDirection:'column',gap:14,overflowY:'auto'}}>
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
}"""

NEW = r"""function SzolancGame({ gameIdx, players, onAdvance, onResult, onSetHideFooter }) {
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

  const SZ_BG    = '#F6C842';
  const SZ_CARD  = '#ffffff';
  const SZ_GREEN = '#4CAF50';
  const SZ_RED   = '#E85C4A';
  const SZ_DOT_OFF = '#D1D5DB';

  const [listIdx] = React.useState(() => Math.floor(Math.random() * LISTS.length));
  const { cat, words: allWords } = LISTS[listIdx];

  const fresh = (chainLen, turnIdx, isFirst=false) => {
    const chain = allWords.slice(0, chainLen);
    return { phase: isFirst ? 'ready' : 'show', chain, showIdx:0, gridWords:[], tapped:[], turnIdx, wrongIdx:null };
  };

  const [S, setS] = React.useState(() => fresh(2, 0, true));
  const [done, setDone] = React.useState(null);

  React.useEffect(() => { setS(fresh(2, 0, true)); setDone(null); }, [gameIdx]);

  const curPlayer = players[S.turnIdx % players.length];

  // ── Show fázis: szavak villogása ──────────────────────────────────────────
  React.useEffect(() => {
    if (S.phase !== 'show') return;
    if (S.showIdx < S.chain.length) {
      const t = setTimeout(() => setS(s => ({...s, showIdx: s.showIdx + 1})), 1300);
      return () => clearTimeout(t);
    }
    // chain + 3 csali, megkeverve
    const decoys = allWords.slice(S.chain.length, S.chain.length + 3);
    const pool = [...S.chain, ...decoys].sort(() => Math.random() - 0.5);
    const t = setTimeout(() => setS(s => ({...s, phase:'recall', gridWords:pool, tapped:[]})), 600);
    return () => clearTimeout(t);
  }, [S.phase, S.showIdx]);

  // ── Recall fázis: koppintás kezelése ─────────────────────────────────────
  const tapWord = (word, idx) => {
    if (S.phase !== 'recall') return;
    if (S.tapped.includes(idx)) return;
    const expected = S.chain[S.tapped.length];
    if (word !== expected) {
      setS(s => ({...s, wrongIdx: idx}));
      setTimeout(() => {
        const pid = curPlayer?.id;
        if (onAdvance) onAdvance({[pid]: 1});
        if (onResult) onResult({ correct: false, playerName: curPlayer?.name, drinks: 1, subtitle: (curPlayer?.name || 'Valaki') + ' elrontotta!' });
        setDone({ failName: curPlayer?.name, correctChain: S.chain });
      }, 700);
      return;
    }
    const newTapped = [...S.tapped, idx];
    if (newTapped.length === S.chain.length) {
      setS(s => ({...s, phase:'correct', tapped: newTapped}));
      const nextTurnIdx = S.turnIdx + 1;
      const nextChainLen = S.chain.length + 1;
      if (nextChainLen > allWords.length) {
        setTimeout(() => { if (onResult) onResult({ correct: true, playerName: null, drinks: 0 }); setDone({ failName: null }); }, 1200);
      } else {
        setTimeout(() => setS(fresh(nextChainLen, nextTurnIdx)), 1200);
      }
    } else {
      setS(s => ({...s, tapped: newTapped}));
    }
  };

  // ── Közös wrapper: arany háttér ───────────────────────────────────────────
  const Wrap = ({children, style={}}) => (
    <div style={{background:SZ_BG, borderRadius:20, padding:'16px', display:'flex', flexDirection:'column', gap:14, overflowY:'auto', ...style}}>
      {children}
    </div>
  );

  // ── DONE képernyő ─────────────────────────────────────────────────────────
  if (done !== null) {
    const win = !done.failName;
    const correctChain = done.correctChain || S.chain;
    return (
      <Wrap>
        <div style={{
          background: win ? SZ_GREEN : SZ_RED,
          borderRadius:20, padding:'24px 16px', textAlign:'center',
          display:'flex', flexDirection:'column', alignItems:'center', gap:10,
          animation:'popIn .4s cubic-bezier(.2,.9,.3,1.2)',
        }}>
          <div style={{fontSize:44}}>{win ? '🏆' : '🍺'}</div>
          <div style={{fontFamily:T.font,fontWeight:900,fontSize:22,color:'#fff'}}>
            {win ? 'Bravo! Elfogytak a szavak!' : done.failName + ' rontott'}
          </div>
          {!win && <div style={{fontFamily:T.font,fontSize:14,color:'rgba(255,255,255,.85)'}}>felcserélte a sorrendet</div>}
          {!win && (
            <div style={{
              background:'rgba(255,255,255,.25)', borderRadius:999,
              padding:'10px 22px', fontFamily:T.font, fontWeight:800,
              fontSize:15, color:'#fff', marginTop:4,
            }}>iszik 1 kortyot</div>
          )}
        </div>
        {!win && (
          <div style={{background:'rgba(255,255,255,.75)', borderRadius:16, padding:'14px 16px'}}>
            <div style={{fontFamily:T.font,fontSize:11,fontWeight:700,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.1em',marginBottom:10,textAlign:'center'}}>
              A HELYES SOR
            </div>
            <div style={{display:'flex',flexWrap:'wrap',gap:6,alignItems:'center',justifyContent:'center'}}>
              {correctChain.map((w,i) => (
                <React.Fragment key={i}>
                  <div style={{background:'#fff',borderRadius:999,padding:'6px 14px',fontFamily:T.font,fontWeight:700,fontSize:14,color:T.ink,boxShadow:'0 1px 4px rgba(0,0,0,.1)'}}>
                    {w}
                  </div>
                  {i < correctChain.length-1 && <span style={{color:T.inkSoft,fontSize:14}}>→</span>}
                </React.Fragment>
              ))}
            </div>
          </div>
        )}
      </Wrap>
    );
  }

  // ── READY fázis ───────────────────────────────────────────────────────────
  if (S.phase === 'ready') {
    return (
      <Wrap>
        <div style={{background:SZ_CARD,borderRadius:20,padding:'24px 16px',display:'flex',flexDirection:'column',alignItems:'center',gap:12}}>
          <div style={{
            width:72,height:72,borderRadius:'50%',
            background:curPlayer?.color||T.mint,
            display:'flex',alignItems:'center',justifyContent:'center',
            fontSize:28,fontWeight:900,color:'#fff',fontFamily:T.font,
          }}>
            {curPlayer?.name?.[0]?.toUpperCase()}
          </div>
          <div style={{fontFamily:T.font,fontWeight:900,fontSize:22,color:T.ink}}>{curPlayer?.name}</div>
          <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft}}>te jössz</div>
          <div style={{background:'#FEF3C7',borderRadius:999,padding:'9px 20px',fontFamily:T.font,fontWeight:700,fontSize:15,color:T.ink}}>
            {cat}
          </div>
          <div style={{display:'flex',gap:6,marginTop:2}}>
            {[0,1,2,3,4].map(i => (
              <div key={i} style={{width:10,height:10,borderRadius:'50%',background:i<S.chain.length?SZ_GREEN:SZ_DOT_OFF}} />
            ))}
          </div>
          <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft,textAlign:'center'}}>
            {S.chain.length}. szint — {S.chain.length} szót kell visszamondani
          </div>
        </div>
        <button onClick={() => setS(s=>({...s,phase:'show'}))} style={{
          background:'rgba(255,255,255,.92)',border:'none',borderRadius:999,
          padding:'14px',fontFamily:T.font,fontWeight:900,fontSize:17,color:T.ink,
          cursor:'pointer',boxShadow:'0 4px 14px rgba(0,0,0,.15)',width:'100%',
        }}>▶ Indítás</button>
      </Wrap>
    );
  }

  // ── SHOW fázis UI ─────────────────────────────────────────────────────────
  if (S.phase === 'show' || S.phase === 'correct') {
    const currentWord = S.phase === 'show' && S.showIdx < S.chain.length ? S.chain[S.showIdx] : null;
    const isCorrect = S.phase === 'correct';
    const wordNum = Math.min(S.showIdx + 1, S.chain.length);
    return (
      <Wrap>
        <div style={{
          background:SZ_CARD, borderRadius:20,
          padding:'32px 24px', display:'flex', flexDirection:'column',
          alignItems:'center', justifyContent:'center', minHeight:190, gap:16,
        }}>
          {isCorrect ? (
            <div style={{textAlign:'center',animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)'}}>
              <div style={{fontSize:40}}>✅</div>
              <div style={{fontFamily:T.font,fontWeight:900,fontSize:18,color:SZ_GREEN,marginTop:8}}>Helyes! Következő…</div>
            </div>
          ) : currentWord ? (
            <div key={S.showIdx} style={{textAlign:'center',animation:'popIn .25s cubic-bezier(.2,.9,.3,1.1)'}}>
              <div style={{fontFamily:T.font,fontWeight:900,fontSize:42,color:T.ink,letterSpacing:'-0.02em'}}>{currentWord}</div>
              <div style={{display:'flex',gap:7,marginTop:18,justifyContent:'center'}}>
                {S.chain.map((_,i) => (
                  <div key={i} style={{
                    width:9,height:9,borderRadius:'50%',
                    background: i<S.showIdx ? SZ_GREEN : i===S.showIdx ? '#F59E0B' : SZ_DOT_OFF,
                    transition:'background .2s',
                  }} />
                ))}
              </div>
            </div>
          ) : (
            <div style={{fontFamily:T.font,fontWeight:700,fontSize:16,color:T.inkSoft}}>Felkészülés…</div>
          )}
        </div>
        {!isCorrect && currentWord && (
          <div style={{display:'flex',justifyContent:'center'}}>
            <div style={{background:'rgba(255,255,255,.75)',borderRadius:999,padding:'8px 18px',display:'flex',alignItems:'center',gap:6}}>
              <span style={{fontSize:14}}>⏱</span>
              <span style={{fontFamily:T.font,fontWeight:700,fontSize:13,color:T.ink}}>{wordNum}. szó · {S.chain.length}-ból</span>
            </div>
          </div>
        )}
      </Wrap>
    );
  }

  // ── RECALL fázis UI ───────────────────────────────────────────────────────
  if (S.phase === 'recall') {
    const remaining = S.chain.length - S.tapped.length;
    return (
      <Wrap>
        <div style={{fontFamily:T.font,fontWeight:700,fontSize:14,color:T.ink,textAlign:'center'}}>
          Koppints a szavakra a helyes sorrendben!
        </div>

        {/* Sorrend tálca */}
        <div style={{display:'flex',gap:8}}>
          {S.chain.map((_,i) => {
            const slotGridIdx = S.tapped[i];
            const word = slotGridIdx !== undefined ? S.gridWords[slotGridIdx] : null;
            return (
              <div key={i} style={{
                flex:1, minWidth:0, padding:'8px 6px', borderRadius:14,
                background: word ? 'rgba(255,255,255,.95)' : 'rgba(255,255,255,.4)',
                border: word ? 'none' : '2px dashed rgba(255,255,255,.7)',
                textAlign:'center', boxShadow: word ? '0 2px 8px rgba(0,0,0,.1)' : 'none',
              }}>
                <div style={{fontFamily:T.font,fontSize:11,fontWeight:700,color:T.inkSoft,marginBottom:2}}>{i+1}.</div>
                {word ? (
                  <div style={{fontFamily:T.font,fontSize:13,fontWeight:800,color:T.ink,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>
                    {word}
                  </div>
                ) : (
                  <div style={{fontSize:15}}>🔒</div>
                )}
              </div>
            );
          })}
        </div>

        {/* Szó grid — 2 oszlop */}
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10}}>
          {S.gridWords.map((word,idx) => {
            const tappedOrder = S.tapped.indexOf(idx);
            const isTapped = tappedOrder !== -1;
            const isWrong = S.wrongIdx === idx;
            return (
              <button key={idx} onClick={() => tapWord(word,idx)} disabled={isTapped} style={{
                padding:'14px 8px', borderRadius:14, border:'none',
                cursor: isTapped ? 'default' : 'pointer',
                background: isWrong ? SZ_RED+'28' : isTapped ? SZ_GREEN+'20' : SZ_CARD,
                boxShadow: isTapped||isWrong ? 'none' : '0 2px 8px rgba(0,0,0,.12)',
                fontFamily:T.font, fontWeight:800, fontSize:15,
                color: isTapped ? SZ_GREEN : isWrong ? SZ_RED : T.ink,
                transition:'all .15s', position:'relative',
                animation: isWrong ? 'shakeDrink .4s ease' : 'none',
              }}>
                {isTapped && (
                  <div style={{
                    position:'absolute',top:-7,right:-7,
                    width:20,height:20,borderRadius:'50%',
                    background:SZ_GREEN,color:'#fff',
                    display:'flex',alignItems:'center',justifyContent:'center',
                    fontSize:10,fontWeight:900,fontFamily:T.font,
                  }}>{tappedOrder+1}</div>
                )}
                {word}
              </button>
            );
          })}
        </div>

        <div style={{fontFamily:T.font,fontSize:13,color:T.ink,textAlign:'center',fontWeight:600,opacity:.75}}>
          {remaining > 0 ? `Még ${remaining} szó a sorból` : '✓ Kész!'}
        </div>
      </Wrap>
    );
  }

  return null;
}"""

assert OLD in src, 'SzolancGame OLD not found!'
src = src.replace(OLD, NEW, 1)

# ── 2. Verzióbump ─────────────────────────────────────────────────────────────
assert "const APP_VERSION = 'v9.410';" in src
src = src.replace("const APP_VERSION = 'v9.410';", "const APP_VERSION = 'v9.411';", 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)

print('v9.411 OK — SzolancGame redesigned')
