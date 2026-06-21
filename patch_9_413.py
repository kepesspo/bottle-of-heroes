#!/usr/bin/env python3
"""v9.413 — CardBattleGame teljes UI redesign"""

with open('index.html', 'r', encoding='utf-8') as f:
    src = f.read()

# Az OLD a teljes CardBattleGame függvény (első sortól az utolsó return null;-ig)
OLD_START = 'function CardBattleGame({ gameIdx, challenger, opponent, onAdvance, onResult, onSetHideFooter }) {'
OLD_END   = '''  return null;
}

function QuizGame('''

assert OLD_START in src, 'CardBattleGame start not found'
assert OLD_END in src, 'CardBattleGame end not found'

idx_start = src.index(OLD_START)
idx_end   = src.index(OLD_END)
OLD = src[idx_start:idx_end]

NEW = r"""function CardBattleGame({ gameIdx, challenger, opponent, onAdvance, onResult, onSetHideFooter }) {
  const VALS = [3,4,5,6,7];
  const NR = 5;

  const CB_BG    = '#F6C842';
  const CB_GREEN = '#4CAF50';
  const CB_RED   = '#E85C4A';
  const CB_BLUE  = '#3B82F6';

  const fresh = () => ({
    phase: 'p1_plan',
    p1Plan: Array.from({length:NR},()=>[]),
    p2Plan: Array.from({length:NR},()=>[]),
    p1Hand: [...VALS],
    p2Hand: [...VALS],
    sel: null,
  });

  const [S, setS] = React.useState(fresh);
  const dragRef = React.useRef(null);
  const [ghost, setGhost] = React.useState(null);
  const [dropHover, setDropHover] = React.useState(null);
  React.useEffect(() => { setS(fresh()); }, [gameIdx]);

  const isP1    = S.phase === 'p1_plan';
  const hand    = isP1 ? S.p1Hand : S.p2Hand;
  const plan    = isP1 ? S.p1Plan : S.p2Plan;
  const hk      = isP1 ? 'p1Hand' : 'p2Hand';
  const pk      = isP1 ? 'p1Plan' : 'p2Plan';
  const pName   = (isP1 ? challenger : opponent)?.name || (isP1 ? '1. játékos' : '2. játékos');
  const pColor  = (isP1 ? challenger : opponent)?.color || (isP1 ? T.mint : T.coral);
  const p1Name  = challenger?.name || '1. játékos';
  const p2Name  = opponent?.name   || '2. játékos';
  const p1Color = challenger?.color || T.mint;
  const p2Color = opponent?.color   || T.coral;

  const assign = (ri) => {
    if (S.sel === null) return;
    if (plan[ri].length > 0) return; // már van lap a körben
    const v = hand[S.sel];
    setS(s => ({...s, [hk]: s[hk].filter((_,i)=>i!==s.sel), [pk]: s[pk].map((r,i)=>i===ri?[v]:r), sel:null}));
  };

  const results = React.useMemo(() => {
    let p1W=0, p2W=0;
    const rounds = S.p1Plan.map((p1c, i) => {
      const p1s = (p1c[0]||0);
      const p2s = (S.p2Plan[i]?.[0]||0);
      let w=null;
      if (p1s>p2s)  { w='p1'; p1W++; }
      else if (p2s>p1s) { w='p2'; p2W++; }
      return {p1s, p2s, w};
    });
    return {rounds, p1W, p2W};
  }, [S.p1Plan, S.p2Plan]);

  React.useEffect(() => {
    if (S.phase !== 'done') return;
    const {p1W, p2W} = results;
    const p1id = challenger?.id;
    const p2id = opponent?.id;
    const diff = Math.abs(p1W - p2W);
    if (p1W > p2W) {
      if (onAdvance) onAdvance({[p2id]: diff}, {[p1id]: 1});
      if (onResult) onResult({ correct: true, playerName: p1Name, drinks: 0, subtitle: p1Name + ' nyerte a meccset!' });
    } else if (p2W > p1W) {
      if (onAdvance) onAdvance({[p1id]: diff}, {[p2id]: 1});
      if (onResult) onResult({ correct: false, playerName: p2Name, drinks: 0, subtitle: p2Name + ' nyerte a meccset!' });
    } else {
      if (onAdvance) onAdvance({[p1id]: 1, [p2id]: 1}, {});
      if (onResult) onResult({ correct: false, playerName: null, drinks: 1, subtitle: 'Döntetlen — mindenki iszik!' });
    }
  }, [S.phase]);

  // kártya chip vizuál
  const CardChip = ({value, color, dim=false}) => (
    <div style={{
      width:42, height:56, borderRadius:11,
      background:'#fff', border:'2px solid '+(dim ? color+'55' : color),
      display:'flex', alignItems:'center', justifyContent:'center',
      fontFamily:T.font, fontWeight:900, fontSize:22, color: dim ? color+'88' : color,
      boxShadow: dim ? 'none' : '0 2px 8px rgba(0,0,0,.13)',
      position:'relative', flexShrink:0, userSelect:'none',
      opacity: dim ? 0.4 : 1,
    }}>
      <span style={{position:'absolute',top:4,left:6,fontSize:9,fontWeight:900,opacity:.6}}>{value}</span>
      {value}
      <span style={{position:'absolute',bottom:4,right:6,fontSize:9,fontWeight:900,opacity:.6,transform:'rotate(180deg)'}}>{value}</span>
    </div>
  );

  // ── PLAN fázis ────────────────────────────────────────────────────────────
  if (S.phase === 'p1_plan' || S.phase === 'p2_plan') {
    const allIn = hand.length === 0;

    const onCardPointerDown = (e, i, v) => {
      e.preventDefault();
      e.currentTarget.setPointerCapture(e.pointerId);
      dragRef.current = { cardIdx: i, value: v };
      setGhost({ x: e.clientX, y: e.clientY, value: v });
      setDropHover(null);
    };
    const onCardPointerMove = (e) => {
      if (!dragRef.current) return;
      setGhost(g => g ? {...g, x:e.clientX, y:e.clientY} : null);
      const els = document.elementsFromPoint(e.clientX, e.clientY);
      const slot = els.find(el => el.dataset && el.dataset.roundIdx !== undefined);
      setDropHover(slot ? parseInt(slot.dataset.roundIdx) : null);
    };
    const onCardPointerUp = (e) => {
      if (!dragRef.current) { setGhost(null); return; }
      const { cardIdx, value, fromSlot, fromRi, fromCi } = dragRef.current;
      dragRef.current = null;
      const els = document.elementsFromPoint(e.clientX, e.clientY);
      const slot = els.find(el => el.dataset && el.dataset.roundIdx !== undefined);
      if (slot) {
        const ri = parseInt(slot.dataset.roundIdx);
        if (fromSlot) {
          setS(s => ({...s, [pk]: s[pk].map((r,i) => {
            if (i===fromRi && i===ri) return r;
            if (i===fromRi) return r.filter((_,j)=>j!==fromCi);
            if (i===ri && r.length===0) return [value];
            return r;
          }), sel:null}));
        } else {
          setS(s => {
            if (s[pk][ri].length > 0) return s; // foglalt
            return {...s, [hk]: s[hk].filter((_,i)=>i!==cardIdx), [pk]: s[pk].map((r,i)=>i===ri?[value]:r), sel:null};
          });
        }
      }
      setGhost(null); setDropHover(null);
    };
    const onSlotCardPointerDown = (e, ri, ci, v) => {
      e.preventDefault(); e.stopPropagation();
      e.currentTarget.setPointerCapture(e.pointerId);
      dragRef.current = { cardIdx:-1, value:v, fromSlot:true, fromRi:ri, fromCi:ci };
      setGhost({ x:e.clientX, y:e.clientY, value:v });
      setDropHover(null);
    };

    return (
      <div style={{background:CB_BG,borderRadius:20,padding:'14px',display:'flex',flexDirection:'column',gap:12,touchAction:'none'}}
           onPointerMove={onCardPointerMove} onPointerUp={onCardPointerUp}>

        {/* Ghost */}
        {ghost && (
          <div style={{position:'fixed',left:ghost.x-21,top:ghost.y-28,pointerEvents:'none',zIndex:9999,transform:'scale(1.18)'}}>
            <CardChip value={ghost.value} color={pColor} />
          </div>
        )}

        {/* Fejléc */}
        <div style={{textAlign:'center'}}>
          <div style={{display:'inline-flex',alignItems:'center',gap:8,padding:'7px 18px',background:'rgba(255,255,255,.85)',borderRadius:999,boxShadow:'0 2px 8px rgba(0,0,0,.1)'}}>
            <div style={{width:9,height:9,borderRadius:'50%',background:pColor}} />
            <span style={{fontFamily:T.font,fontWeight:800,fontSize:15,color:T.ink}}>{pName} tervez</span>
          </div>
          <div style={{fontFamily:T.font,fontSize:12,color:T.ink,opacity:.7,marginTop:5,fontWeight:600}}>
            {hand.length > 0 ? `Még ${hand.length} lap a kézben` : '✓ Minden lap kiosztva'}
          </div>
        </div>

        {/* Körslotok */}
        {plan.map((cards, ri) => {
          const isHov = dropHover === ri;
          const card = cards[0];
          const isDraggingCard = ghost && dragRef.current?.fromSlot && dragRef.current?.fromRi===ri;
          return (
            <div key={ri} data-round-idx={ri} onClick={()=>assign(ri)} style={{
              display:'flex', alignItems:'center', gap:12, padding:'10px 14px',
              background:'#fff',
              borderRadius:16,
              border: isHov ? '2px solid '+pColor : card ? '2px solid transparent' : '2px dashed rgba(0,0,0,.15)',
              boxShadow:'0 2px 10px rgba(0,0,0,.08)',
              cursor: S.sel!==null ? 'pointer' : 'default',
              transition:'border .1s,box-shadow .1s',
              minHeight:62,
            }}>
              <div style={{fontFamily:T.font,fontWeight:700,fontSize:13,color:T.inkSoft,minWidth:42}}>{ri+1}. kör</div>
              <div style={{flex:1,display:'flex',alignItems:'center',gap:8,pointerEvents:'none'}}>
                {card !== undefined ? (
                  <div onPointerDown={e=>onSlotCardPointerDown(e,ri,0,card)} style={{pointerEvents:'all',touchAction:'none',cursor:'grab'}}>
                    <CardChip value={card} color={pColor} dim={isDraggingCard} />
                  </div>
                ) : (
                  <span style={{fontFamily:T.font,fontSize:13,color:T.inkMute,pointerEvents:'none'}}>Húzz ide</span>
                )}
              </div>
            </div>
          );
        })}

        {/* Kéz kártyái */}
        <div style={{marginTop:4}}>
          <div style={{fontFamily:T.font,fontSize:11,fontWeight:700,color:'rgba(0,0,0,.45)',textTransform:'uppercase',letterSpacing:'.08em',marginBottom:8}}>Kézben</div>
          <div style={{display:'flex',gap:10,flexWrap:'wrap'}}>
            {hand.map((v,i) => (
              <div key={i}
                onPointerDown={e=>onCardPointerDown(e,i,v)}
                onClick={()=>setS(s=>({...s,sel:s.sel===i?null:i}))}
                style={{cursor:'grab',touchAction:'none',opacity:ghost?0.6:1,
                  transform: S.sel===i ? 'translateY(-6px) scale(1.08)' : 'none',
                  transition:'transform .15s',
                }}>
                <CardChip value={v} color={pColor} />
              </div>
            ))}
            {allIn && <div style={{fontFamily:T.font,fontSize:13,fontWeight:700,color:CB_GREEN,display:'flex',alignItems:'center'}}>✓ Kész</div>}
          </div>
        </div>

        {allIn && (
          <button onClick={()=>setS(s=>({...s,phase:isP1?'handoff':'reveal',sel:null}))} style={{
            marginTop:4,padding:'15px',borderRadius:16,border:'none',
            background:pColor,color:'#fff',fontFamily:T.font,fontWeight:900,fontSize:16,
            cursor:'pointer',boxShadow:'0 5px 16px -5px '+pColor+'88',
          }}>Kész →</button>
        )}
      </div>
    );
  }

  // ── HANDOFF ───────────────────────────────────────────────────────────────
  if (S.phase === 'handoff') {
    return (
      <div style={{background:CB_BG,borderRadius:20,padding:'28px 20px',display:'flex',flexDirection:'column',alignItems:'center',gap:20,textAlign:'center'}}>
        <div style={{fontSize:52}}>🔄</div>
        <div style={{fontFamily:T.font,fontWeight:900,fontSize:22,color:T.ink}}>Add át a telefont!</div>
        <div style={{background:'rgba(255,255,255,.8)',borderRadius:16,padding:'14px 20px',fontFamily:T.font,fontSize:14,color:T.ink,lineHeight:1.6}}>
          <span style={{fontWeight:800,color:p2Color}}>{p2Name}</span> most tervezi a lapjait.<br/>
          <span style={{fontWeight:700,color:p1Color}}>{p1Name}</span> ne nézze!
        </div>
        <button onClick={()=>setS(s=>({...s,phase:'p2_plan'}))} style={{
          padding:'15px 36px',borderRadius:16,border:'none',
          background:p2Color,color:'#fff',fontFamily:T.font,fontWeight:900,fontSize:16,
          cursor:'pointer',boxShadow:'0 5px 16px -5px '+p2Color+'88',
        }}>{p2Name} készen áll →</button>
      </div>
    );
  }

  // ── REVEAL ────────────────────────────────────────────────────────────────
  if (S.phase === 'reveal') {
    const {rounds, p1W, p2W} = results;
    return (
      <div style={{background:CB_BG,borderRadius:20,padding:'14px',display:'flex',flexDirection:'column',gap:12,overflowY:'auto'}}>
        {/* Összesítő */}
        <div style={{background:'rgba(255,255,255,.85)',borderRadius:16,padding:'10px 16px',textAlign:'center'}}>
          <div style={{fontFamily:T.font,fontWeight:900,fontSize:22,color:T.ink,display:'flex',alignItems:'center',justifyContent:'center',gap:10}}>
            <span style={{color:p1Color}}>{p1Name}</span>
            <span style={{fontSize:20}}>{p1W} — {p2W}</span>
            <span style={{color:p2Color}}>{p2Name}</span>
          </div>
          <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,marginTop:2}}>A sávok átfordulnak, körönt</div>
        </div>

        {/* Oszlopfejléc */}
        <div style={{display:'flex',alignItems:'center',padding:'0 14px'}}>
          <div style={{flex:1,fontFamily:T.font,fontWeight:800,fontSize:13,color:p1Color}}>{p1Name}</div>
          <div style={{fontFamily:T.font,fontSize:11,fontWeight:700,color:T.inkSoft,width:36,textAlign:'center'}}>vs</div>
          <div style={{flex:1,fontFamily:T.font,fontWeight:800,fontSize:13,color:p2Color,textAlign:'right'}}>{p2Name}</div>
        </div>

        {/* Körlista */}
        {rounds.map((r,i) => {
          const win1=r.w==='p1', win2=r.w==='p2', tie=!r.w;
          const rowBg = win1 ? p1Color+'18' : win2 ? p2Color+'18' : 'rgba(255,255,255,.6)';
          const icon  = win1 ? '🏆' : win2 ? '×' : '🤝';
          const iconColor = win2 ? CB_RED : T.inkSoft;
          return (
            <div key={i} style={{
              display:'flex',alignItems:'center',gap:8,padding:'8px 12px',
              background:rowBg, borderRadius:14,
              border:'1.5px solid '+(win1?p1Color+'44':win2?p2Color+'44':'rgba(0,0,0,.08)'),
              animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)',
              animationDelay:(i*.06)+'s', animationFillMode:'both',
            }}>
              <div style={{fontFamily:T.font,fontWeight:700,fontSize:11,color:T.inkSoft,width:18}}>{i+1}</div>
              <div style={{flex:1,display:'flex',justifyContent:'flex-start'}}>
                {r.p1s>0 ? <CardChip value={r.p1s} color={p1Color} /> : <div style={{width:42,height:56,borderRadius:11,background:'rgba(0,0,0,.06)',border:'2px dashed rgba(0,0,0,.1)'}} />}
              </div>
              <div style={{fontFamily:T.font,fontSize:win2?18:20,fontWeight:900,color:iconColor,width:28,textAlign:'center'}}>{icon}</div>
              <div style={{flex:1,display:'flex',justifyContent:'flex-end'}}>
                {r.p2s>0 ? <CardChip value={r.p2s} color={p2Color} /> : <div style={{width:42,height:56,borderRadius:11,background:'rgba(0,0,0,.06)',border:'2px dashed rgba(0,0,0,.1)'}} />}
              </div>
            </div>
          );
        })}

        <button onClick={()=>setS(s=>({...s,phase:'done'}))} style={{
          marginTop:4,padding:'15px',borderRadius:16,border:'none',
          background:CB_GREEN,color:'#fff',fontFamily:T.font,fontWeight:900,fontSize:16,
          cursor:'pointer',boxShadow:'0 5px 16px -5px '+CB_GREEN+'88',
        }}>Eredmény →</button>
      </div>
    );
  }

  // ── DONE ──────────────────────────────────────────────────────────────────
  if (S.phase === 'done') {
    const {p1W, p2W} = results;
    const tie = p1W === p2W;
    const winName  = p1W>p2W ? p1Name : p2W>p1W ? p2Name : null;
    const loseName = p1W>p2W ? p2Name : p2W>p1W ? p1Name : null;
    const diff = Math.abs(p1W - p2W);
    return (
      <div style={{background:CB_BG,borderRadius:20,padding:'14px',display:'flex',flexDirection:'column',gap:14}}>
        {/* Eredmény kártya */}
        <div style={{
          background: tie ? T.inkSoft : CB_GREEN,
          borderRadius:20,padding:'24px 16px',
          display:'flex',flexDirection:'column',alignItems:'center',gap:10,
          animation:'popIn .4s cubic-bezier(.2,.9,.3,1.2)',textAlign:'center',
        }}>
          <div style={{fontSize:44}}>🃏</div>
          <div style={{fontFamily:T.font,fontWeight:900,fontSize:24,color:'#fff'}}>
            {winName ? winName+' nyert!' : 'Döntetlen!'}
          </div>
          <div style={{fontFamily:T.font,fontSize:13,color:'rgba(255,255,255,.85)'}}>
            {winName ? `${p1W} : ${p2W} a megnyert körökben` : 'Mindenki egyforma!'}
          </div>
          {loseName && (
            <div style={{
              background:'rgba(255,255,255,.25)',borderRadius:999,
              padding:'10px 22px',fontFamily:T.font,fontWeight:800,fontSize:15,color:'#fff',marginTop:4,
            }}>🎴 {loseName} iszik {diff} kortyot</div>
          )}
          {tie && (
            <div style={{
              background:'rgba(255,255,255,.25)',borderRadius:999,
              padding:'10px 22px',fontFamily:T.font,fontWeight:800,fontSize:15,color:'#fff',marginTop:4,
            }}>🍺 Mindenki iszik 1 kortyot</div>
          )}
        </div>

        {/* Végeredmény */}
        <div style={{background:'rgba(255,255,255,.8)',borderRadius:16,padding:'14px 20px'}}>
          <div style={{fontFamily:T.font,fontSize:11,fontWeight:700,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'.1em',textAlign:'center',marginBottom:10}}>VÉGEREDMÉNY</div>
          <div style={{display:'flex',alignItems:'center',justifyContent:'center',gap:16}}>
            <div style={{textAlign:'center'}}>
              <div style={{fontFamily:T.font,fontWeight:900,fontSize:38,color:p1Color}}>{p1W}</div>
              <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft}}>{p1Name}</div>
            </div>
            <div style={{fontFamily:T.font,fontSize:26,color:T.inkMute,fontWeight:700}}>:</div>
            <div style={{textAlign:'center'}}>
              <div style={{fontFamily:T.font,fontWeight:900,fontSize:38,color:p2Color}}>{p2W}</div>
              <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft}}>{p2Name}</div>
            </div>
          </div>
        </div>

        {/* Visszavágó */}
        <button onClick={()=>setS(fresh())} style={{
          padding:'15px',borderRadius:16,border:'none',
          background:CB_BLUE,color:'#fff',fontFamily:T.font,fontWeight:900,fontSize:16,
          cursor:'pointer',boxShadow:'0 5px 16px -5px '+CB_BLUE+'88',
        }}>Visszavágó ▶</button>
      </div>
    );
  }

  return null;
}

"""

src = src[:idx_start] + NEW + src[idx_end:]

# verzióbump
assert "const APP_VERSION = 'v9.412';" in src
src = src.replace("const APP_VERSION = 'v9.412';", "const APP_VERSION = 'v9.413';", 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)

print('v9.413 OK — CardBattleGame redesigned')
