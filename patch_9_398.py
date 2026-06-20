#!/usr/bin/env python3
"""v9.398 — Kártyacsata játék: pre-selection, 5 kör, pot mechanic, felfedés animáció"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. GAMES bejegyzés ────────────────────────────────────────────────────────
old_last_game = """  { id:'szamsor',  roundTime:'fast', name:'Szám Sorrend',     difficulty:'közepes', category:'Páros',  emoji:'🔢', img:IMGS['szamsor_icon.png'], symbol:IMGS['szamsor_symbol.png'], color:'#3B82F6', desc:'Párbaj! Mindkét játékos külön koppintja sorrendben 1-től 9-ig a számokat. Az app összehasonlítja az időt — a lassabb iszik.' },
];"""

new_last_game = """  { id:'szamsor',  roundTime:'fast', name:'Szám Sorrend',     difficulty:'közepes', category:'Páros',  emoji:'🔢', img:IMGS['szamsor_icon.png'], symbol:IMGS['szamsor_symbol.png'], color:'#3B82F6', desc:'Párbaj! Mindkét játékos külön koppintja sorrendben 1-től 9-ig a számokat. Az app összehasonlítja az időt — a lassabb iszik.' },
  { id:'cardbattle', roundTime:'mid', name:'Kártyacsata', difficulty:'közepes', category:'Páros', emoji:'🃏', symbol:null, img:null, banner:null, color:'#8B5CF6', desc:'Mindkét játékos 5 lapot oszt szét 5 körre (összérték: 25). A magasabb összeget befektető játékos nyeri a kört — döntetnél a tét továbbbgördül. Aki több kört nyer, az győz!' },
];"""

assert old_last_game in html, "FAIL: games array"
html = html.replace(old_last_game, new_last_game, 1)

# ── 2. SCENARIOS bejegyzés ────────────────────────────────────────────────────
old_scenario = """  'szolánc':   { prompt:'Mondd el a sort, majd told hozzá az új szót a kategóriából!', cta:[] },
};"""

new_scenario = """  'szolánc':   { prompt:'Mondd el a sort, majd told hozzá az új szót a kategóriából!', cta:[] },
  cardbattle:  { prompt:'', cta:[] },
};"""

assert old_scenario in html, "FAIL: scenarios"
html = html.replace(old_scenario, new_scenario, 1)

# ── 3. CardBattleGame komponens ───────────────────────────────────────────────
old_gamecontent_if = """  if (gameId === 'fingerit') return <FingeritGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;
  return null;
}"""

new_gamecontent_if = """  if (gameId === 'fingerit') return <FingeritGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;
  if (gameId === 'cardbattle') return <CardBattleGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} />;
  return null;
}"""

assert old_gamecontent_if in html, "FAIL: gamecontent if"
html = html.replace(old_gamecontent_if, new_gamecontent_if, 1)

# ── 4. CardBattleGame komponens kód ──────────────────────────────────────────
card_battle_component = """
function CardBattleGame({ gameIdx, challenger, opponent, onAdvance, onResult, onSetHideFooter }) {
  const VALS = [3,4,5,6,7]; // összesen 25
  const NR = 5;

  const fresh = () => ({
    phase: 'p1_plan', // p1_plan | handoff | p2_plan | reveal | done
    p1Plan: Array.from({length:NR},()=>[]),
    p2Plan: Array.from({length:NR},()=>[]),
    p1Hand: [...VALS],
    p2Hand: [...VALS],
    sel: null,
    rev: 0,
  });

  const [S, setS] = React.useState(fresh);
  React.useEffect(() => { setS(fresh()); }, [gameIdx]);
  React.useEffect(() => {
    if (onSetHideFooter) onSetHideFooter(true);
    return () => { if (onSetHideFooter) onSetHideFooter(false); };
  }, []);

  const isP1 = S.phase === 'p1_plan';
  const hand = isP1 ? S.p1Hand : S.p2Hand;
  const plan = isP1 ? S.p1Plan : S.p2Plan;
  const hk = isP1 ? 'p1Hand' : 'p2Hand';
  const pk = isP1 ? 'p1Plan' : 'p2Plan';
  const curPlayer = isP1 ? challenger : opponent;
  const pName = curPlayer?.name || (isP1 ? '1. játékos' : '2. játékos');
  const pColor = curPlayer?.color || (isP1 ? T.mint : T.coral);

  const assign = (ri) => {
    if (S.sel === null) return;
    const v = hand[S.sel];
    setS(s => ({...s, [hk]: s[hk].filter((_,i)=>i!==s.sel), [pk]: s[pk].map((r,i)=>i===ri?[...r,v]:r), sel:null}));
  };

  const remove = (ri, ci) => {
    const v = plan[ri][ci];
    setS(s => ({...s, [hk]: [...s[hk],v].sort((a,b)=>a-b), [pk]: s[pk].map((r,i)=>i===ri?r.filter((_,j)=>j!==ci):r)}));
  };

  const allIn = hand.length === 0;

  // Eredmény számítás
  const results = React.useMemo(() => {
    let pot=0, p1W=0, p2W=0;
    const rounds = S.p1Plan.map((p1c, i) => {
      const p1s = p1c.reduce((a,b)=>a+b,0);
      const p2s = (S.p2Plan[i]||[]).reduce((a,b)=>a+b,0);
      pot++;
      let w=null, gained=0;
      if (p1s>p2s) { w='p1'; gained=pot; p1W+=pot; pot=0; }
      else if (p2s>p1s) { w='p2'; gained=pot; p2W+=pot; pot=0; }
      return {p1s,p2s,w,gained,p1W,p2W,carry:pot};
    });
    return {rounds, p1W, p2W};
  }, [S.p1Plan, S.p2Plan]);

  // onResult hívás a 'done' fázisban
  React.useEffect(() => {
    if (S.phase !== 'done') return;
    const {p1W, p2W} = results;
    if (onResult) {
      if (p1W > p2W) onResult({correct: true});
      else if (p2W > p1W) onResult({correct: false});
    }
  }, [S.phase]);

  // ── Tervezés fázis ──
  if (S.phase === 'p1_plan' || S.phase === 'p2_plan') {
    const totalLeft = hand.reduce((a,b)=>a+b,0);
    return (
      <div style={{display:'flex',flexDirection:'column',gap:10}}>
        <div style={{textAlign:'center',padding:'4px 0 6px'}}>
          <div style={{display:'inline-flex',alignItems:'center',gap:8,padding:'6px 18px',background:pColor+'22',borderRadius:999}}>
            <div style={{width:10,height:10,borderRadius:'50%',background:pColor,flexShrink:0}} />
            <span style={{fontFamily:T.font,fontWeight:800,fontSize:15,color:T.ink}}>{pName} tervez</span>
          </div>
          <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,marginTop:4}}>
            {totalLeft > 0 ? `Még ${totalLeft} pont kiosztható` : '✓ Minden lap kiosztva'}
          </div>
        </div>

        {plan.map((cards, ri) => (
          <div key={ri} onClick={() => assign(ri)} style={{
            display:'flex', alignItems:'center', gap:10, padding:'10px 14px',
            background: S.sel!==null ? pColor+'15' : T.surface,
            borderRadius:14, border: S.sel!==null ? '2px dashed '+pColor : '2px solid transparent',
            boxShadow: T.shadow, cursor: S.sel!==null ? 'pointer' : 'default',
            transition:'background .12s, border .12s', minHeight:52,
          }}>
            <div style={{fontFamily:T.font,fontWeight:700,fontSize:12,color:T.inkSoft,minWidth:48}}>{ri+1}. kör</div>
            <div style={{flex:1,display:'flex',flexWrap:'wrap',gap:6,alignItems:'center'}}>
              {cards.map((v,ci) => (
                <div key={ci} onClick={e=>{e.stopPropagation();remove(ri,ci);}} style={{
                  width:36,height:36,borderRadius:10,background:pColor,color:'#fff',
                  display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:16,
                  cursor:'pointer',boxShadow:'0 2px 6px '+pColor+'44',flexShrink:0,
                }}>{v}</div>
              ))}
              {cards.length===0 && <span style={{fontFamily:T.font,fontSize:12,color:T.inkMute}}>Koppints ide</span>}
            </div>
            <div style={{fontFamily:T.font,fontWeight:800,fontSize:14,color:cards.length?T.ink:T.inkMute,minWidth:24,textAlign:'right'}}>
              {cards.length ? cards.reduce((a,b)=>a+b,0) : ''}
            </div>
          </div>
        ))}

        <div style={{marginTop:6}}>
          <div style={{fontFamily:T.font,fontSize:11,fontWeight:700,color:T.inkMute,textTransform:'uppercase',letterSpacing:'0.1em',marginBottom:8}}>Kézben</div>
          <div style={{display:'flex',gap:10,flexWrap:'wrap'}}>
            {hand.map((v,i) => (
              <div key={i} onClick={() => setS(s=>({...s,sel:s.sel===i?null:i}))} style={{
                width:48,height:64,borderRadius:12,
                background: S.sel===i ? pColor : T.surface,
                color: S.sel===i ? '#fff' : T.ink,
                border: S.sel===i ? '2px solid '+pColor : '2px solid '+T.inkMute+'30',
                display:'flex',alignItems:'center',justifyContent:'center',
                fontFamily:T.font,fontWeight:900,fontSize:22,
                boxShadow: S.sel===i ? '0 4px 14px '+pColor+'55' : T.shadow,
                cursor:'pointer',transition:'all .15s',
                transform: S.sel===i ? 'translateY(-8px) scale(1.08)' : 'none',
              }}>{v}</div>
            ))}
            {allIn && <div style={{fontFamily:T.font,fontSize:13,fontWeight:700,color:T.mint,display:'flex',alignItems:'center'}}>✓ Minden lap kiosztva!</div>}
          </div>
        </div>

        {allIn && (
          <button onClick={() => setS(s=>({...s, phase: isP1?'handoff':'reveal', sel:null}))} style={{
            marginTop:8,padding:'15px',borderRadius:16,border:'none',
            background:pColor,color:'#fff',fontFamily:T.font,fontWeight:900,fontSize:17,
            cursor:'pointer',boxShadow:'0 5px 16px -5px '+pColor+'88',
          }}>Kész →</button>
        )}
      </div>
    );
  }

  // ── Átadás fázis ──
  if (S.phase === 'handoff') {
    const p2Name = opponent?.name || '2. játékos';
    const p2Color = opponent?.color || T.coral;
    return (
      <div style={{display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:20,padding:'32px 20px',minHeight:300,textAlign:'center'}}>
        <div style={{fontSize:52}}>🔄</div>
        <div style={{fontFamily:T.font,fontWeight:900,fontSize:22,color:T.ink}}>Add át a telefont!</div>
        <div style={{fontFamily:T.font,fontSize:15,color:T.inkSoft,maxWidth:260,lineHeight:1.6}}>
          <span style={{fontWeight:800,color:p2Color}}>{p2Name}</span> most tervezi meg a lapjait.<br/>
          <span style={{color:challenger?.color||T.mint,fontWeight:700}}>{challenger?.name||'1. játékos'}</span> ne nézze!
        </div>
        <button onClick={() => setS(s=>({...s,phase:'p2_plan'}))} style={{
          padding:'15px 40px',borderRadius:16,border:'none',
          background:p2Color,color:'#fff',fontFamily:T.font,fontWeight:900,fontSize:16,
          cursor:'pointer',boxShadow:'0 5px 16px -5px '+p2Color+'88',
        }}>{p2Name} készen áll →</button>
      </div>
    );
  }

  // ── Felfedés fázis ──
  if (S.phase === 'reveal') {
    const {rounds} = results;
    const p1Name = challenger?.name || '1. játékos';
    const p2Name = opponent?.name || '2. játékos';
    const p1Color = challenger?.color || T.mint;
    const p2Color = opponent?.color || T.coral;
    const cur = rounds[S.rev] || rounds[rounds.length-1];
    return (
      <div style={{display:'flex',flexDirection:'column',gap:12}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'center',gap:28,padding:'4px 0 8px'}}>
          <div style={{textAlign:'center'}}>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:30,color:p1Color,fontVariantNumeric:'tabular-nums'}}>{cur.p1W}</div>
            <div style={{fontFamily:T.font,fontSize:11,color:T.inkSoft}}>{p1Name}</div>
          </div>
          <div style={{fontFamily:T.font,fontSize:16,color:T.inkMute,fontWeight:700}}>KÖR</div>
          <div style={{textAlign:'center'}}>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:30,color:p2Color,fontVariantNumeric:'tabular-nums'}}>{cur.p2W}</div>
            <div style={{fontFamily:T.font,fontSize:11,color:T.inkSoft}}>{p2Name}</div>
          </div>
        </div>

        <div style={{display:'flex',flexDirection:'column',gap:8}}>
          {rounds.slice(0,S.rev+1).map((r,i) => {
            const win1=r.w==='p1', win2=r.w==='p2', tie=!r.w;
            return (
              <div key={i} style={{
                display:'flex',alignItems:'center',gap:8,padding:'10px 12px',
                background: win1?p1Color+'18':win2?p2Color+'18':T.surfaceMuted,
                borderRadius:14, border:'1.5px solid '+(win1?p1Color+'44':win2?p2Color+'44':T.inkMute+'20'),
                animation: i===S.rev ? 'popIn .35s cubic-bezier(.2,.9,.3,1.2)' : 'none',
              }}>
                <div style={{fontFamily:T.font,fontWeight:700,fontSize:11,color:T.inkSoft,minWidth:38}}>{i+1}. kör</div>
                <div style={{flex:1,display:'flex',alignItems:'center',gap:4,flexWrap:'wrap'}}>
                  {(S.p1Plan[i]||[]).map((v,j)=>(
                    <span key={j} style={{padding:'2px 7px',background:p1Color,color:'#fff',borderRadius:7,fontFamily:T.font,fontWeight:800,fontSize:13}}>{v}</span>
                  ))}
                  <span style={{fontFamily:T.font,fontSize:11,color:p1Color,fontWeight:700}}>({r.p1s})</span>
                </div>
                <div style={{fontSize:18,flexShrink:0}}>{win1?'🏆':win2?'🏆':tie&&r.carry>1?'🎯':'🤝'}</div>
                <div style={{flex:1,display:'flex',alignItems:'center',justifyContent:'flex-end',gap:4,flexWrap:'wrap-reverse'}}>
                  <span style={{fontFamily:T.font,fontSize:11,color:p2Color,fontWeight:700}}>({r.p2s})</span>
                  {(S.p2Plan[i]||[]).map((v,j)=>(
                    <span key={j} style={{padding:'2px 7px',background:p2Color,color:'#fff',borderRadius:7,fontFamily:T.font,fontWeight:800,fontSize:13}}>{v}</span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {cur.carry > 0 && !cur.w && S.rev < NR-1 && (
          <div style={{textAlign:'center',fontFamily:T.font,fontSize:13,color:T.inkSoft,padding:'2px 0'}}>
            🎯 Döntetlen — {cur.carry} kör tétje vándorol tovább
          </div>
        )}

        {S.rev < NR-1 ? (
          <button onClick={()=>setS(s=>({...s,rev:s.rev+1}))} style={{
            padding:'14px',borderRadius:16,border:'none',background:T.surface,color:T.ink,
            fontFamily:T.font,fontWeight:800,fontSize:15,cursor:'pointer',boxShadow:T.shadow,marginTop:4,
          }}>Következő kör →</button>
        ) : (
          <button onClick={()=>setS(s=>({...s,phase:'done'}))} style={{
            padding:'14px',borderRadius:16,border:'none',background:T.mint,color:'#fff',
            fontFamily:T.font,fontWeight:900,fontSize:15,cursor:'pointer',
            boxShadow:'0 4px 14px rgba(79,194,160,0.5)',marginTop:4,
          }}>Eredmény →</button>
        )}
      </div>
    );
  }

  // ── Eredmény fázis ──
  if (S.phase === 'done') {
    const {p1W, p2W} = results;
    const p1Name = challenger?.name || '1. játékos';
    const p2Name = opponent?.name || '2. játékos';
    const p1Color = challenger?.color || T.mint;
    const p2Color = opponent?.color || T.coral;
    const winName = p1W>p2W ? p1Name : p2W>p1W ? p2Name : null;
    const winColor = p1W>p2W ? p1Color : p2W>p1W ? p2Color : T.inkSoft;
    return (
      <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:16,padding:'20px 0',textAlign:'center',animation:'popIn .4s cubic-bezier(.2,.9,.3,1.2)'}}>
        <div style={{fontSize:52}}>{winName?'🏆':'🤝'}</div>
        <div style={{fontFamily:T.font,fontWeight:900,fontSize:24,color:winColor}}>
          {winName ? winName+' nyerte!' : 'Döntetlen!'}
        </div>
        <div style={{display:'flex',gap:36,marginTop:4}}>
          <div style={{textAlign:'center'}}>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:36,color:p1Color}}>{p1W}</div>
            <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,marginTop:2}}>{p1Name}</div>
          </div>
          <div style={{fontFamily:T.font,fontSize:28,color:T.inkMute,display:'flex',alignItems:'center'}}>–</div>
          <div style={{textAlign:'center'}}>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:36,color:p2Color}}>{p2W}</div>
            <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,marginTop:2}}>{p2Name}</div>
          </div>
        </div>
        <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft,marginTop:4}}>
          {winName ? 'A vesztes iszik 🍺' : 'Mindenki iszik 🍻'}
        </div>
      </div>
    );
  }

  return null;
}
"""

# Beillesztés a GameContent function elé
old_gamecontent_fn = "\nfunction GameContent("
assert old_gamecontent_fn in html, "FAIL: gamecontent fn"
html = html.replace(old_gamecontent_fn, card_battle_component + "\nfunction GameContent(", 1)

html = html.replace("const APP_VERSION = 'v9.397';", "const APP_VERSION = 'v9.398';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.398 — Kártyacsata játék implementálva")
