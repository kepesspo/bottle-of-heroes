#!/usr/bin/env python3
"""v9.420 — BeerPong Bajnokság modul"""

with open('index.html','r',encoding='utf-8') as f:
    src = f.read()

# ── 1. BeerPongTournamentScreen komponens ──────────────────────────────────────
# Beillesztés: function Root() elé

COMPONENT = r"""
// ─── BEERPONG BAJNOKSÁG ───────────────────────────────────────────────────────
function BeerPongTournamentScreen({ go, players: appPlayers }) {
  const BP      = '#0F1A30';
  const BP2     = '#1A2B4B';
  const BPL     = '#243555';
  const GOLD    = '#F59E0B';
  const SILVER  = '#94A3B8';
  const BRONZE  = '#B45309';
  const BPGREEN = '#10B981';
  const BPRED   = '#EF4444';
  const WHITE   = '#ffffff';
  const font    = T.font;

  const today = new Date().toLocaleDateString('hu-HU',{year:'numeric',month:'long',day:'numeric'});
  const [phase, setPhase]   = React.useState('setup');
  const [tName, setTName]   = React.useState('Beerpong Bajnokság');
  const [tDate]             = React.useState(today);
  const [tPlayers, setTP]   = React.useState([]); // {id,name,color,groupId}
  const [groupMatches, setGM] = React.useState([]);
  const [matchQueue, setMQ] = React.useState([]);
  const [matchIdx, setMI]   = React.useState(0);
  const [c1, setC1]         = React.useState('');
  const [c2, setC2]         = React.useState('');
  const [bracket, setBK]    = React.useState({ semi1:null,semi2:null,third:null,final:null });
  const [bPhase, setBP]     = React.useState('semi1');
  const tableauRef          = React.useRef(null);

  const gp = (id) => tPlayers.find(p=>p.id===id) || {name:'?',color:'#666',id};

  // ── Standings kiszámítás ─────────────────────────────────────────────────
  const calcSt = (gid, matches) => {
    const pids = tPlayers.filter(p=>p.groupId===gid).map(p=>p.id);
    return pids.map(pid => {
      const ms = matches.filter(m=>m.p1id===pid||m.p2id===pid);
      let J=0,Gy=0,D=0,V=0,pp=0,pk=0;
      ms.forEach(m=>{
        const ip1 = m.p1id===pid;
        const mc=ip1?m.cups1:m.cups2, oc=ip1?m.cups2:m.cups1;
        J++;pp+=mc;pk+=oc;
        if(mc>oc)Gy++;else if(mc===oc)D++;else V++;
      });
      return {pid,J,Gy,D,V,pp,pk,pts:Gy*3+D};
    }).sort((a,b)=>b.pts-a.pts||(b.pp-b.pk)-(a.pp-a.pk));
  };

  const genRR = (gid) => {
    const pids = tPlayers.filter(p=>p.groupId===gid).map(p=>p.id);
    const ms=[];
    for(let i=0;i<pids.length;i++)
      for(let j=i+1;j<pids.length;j++)
        ms.push({p1id:pids[i],p2id:pids[j],groupId:gid});
    return ms;
  };

  // ── Setup: játékos hozzáadás appból ──────────────────────────────────────
  const togglePlayer = (p) => {
    setTP(prev => {
      const exists = prev.find(x=>x.id===p.id);
      if(exists) return prev.filter(x=>x.id!==p.id);
      return [...prev,{id:p.id,name:p.name,color:p.color,groupId:'A'}];
    });
  };
  const setGroup = (pid,gid) => setTP(prev=>prev.map(p=>p.id===pid?{...p,groupId:gid}:p));

  const canStart = tPlayers.filter(p=>p.groupId==='A').length>=2 && tPlayers.filter(p=>p.groupId==='B').length>=2;

  const startGroup = () => {
    const aMs=genRR('A'), bMs=genRR('B');
    const q=[];
    const n=Math.max(aMs.length,bMs.length);
    for(let i=0;i<n;i++){if(aMs[i])q.push(aMs[i]);if(bMs[i])q.push(bMs[i]);}
    setMQ(q);setMI(0);setGM([]);setC1('');setC2('');setPhase('group');
  };

  const submitGroup = () => {
    const m=matchQueue[matchIdx];
    const nm=[...groupMatches,{...m,cups1:parseInt(c1)||0,cups2:parseInt(c2)||0}];
    setGM(nm);
    if(matchIdx<matchQueue.length-1){
      setMI(i=>i+1);setC1('');setC2('');
    } else {
      // Calculate bracket seedings
      const stA=calcStWithMatches('A',nm);
      const stB=calcStWithMatches('B',nm);
      setBK({
        semi1:{p1id:stA[0]?.pid,p2id:stB[1]?.pid,cups1:0,cups2:0},
        semi2:{p1id:stB[0]?.pid,p2id:stA[1]?.pid,cups1:0,cups2:0},
        third:null,final:null
      });
      setBP('semi1');setC1('');setC2('');setPhase('bracket');
    }
  };

  const calcStWithMatches = (gid, matches) => {
    const pids=tPlayers.filter(p=>p.groupId===gid).map(p=>p.id);
    return pids.map(pid=>{
      const ms=matches.filter(m=>m.p1id===pid||m.p2id===pid);
      let Gy=0,D=0,pp=0,pk=0;
      ms.forEach(m=>{
        const ip1=m.p1id===pid;
        const mc=ip1?m.cups1:m.cups2,oc=ip1?m.cups2:m.cups1;
        pp+=mc;pk+=oc;
        if(mc>oc)Gy++;else if(mc===oc)D++;
      });
      return{pid,pts:Gy*3+D,diff:pp-pk};
    }).sort((a,b)=>b.pts-a.pts||b.diff-a.diff);
  };

  const submitBracket = () => {
    const cv1=parseInt(c1)||0,cv2=parseInt(c2)||0;
    const m=bracket[bPhase];
    const wid=cv1>=cv2?m.p1id:m.p2id;
    const lid=wid===m.p1id?m.p2id:m.p1id;
    const upd={...m,cups1:cv1,cups2:cv2,winnerId:wid,loserId:lid};
    const nb={...bracket,[bPhase]:upd};
    if(bPhase==='semi1'){setBK(nb);setBP('semi2');}
    else if(bPhase==='semi2'){
      nb.third={p1id:nb.semi1.loserId,p2id:upd.loserId,cups1:0,cups2:0};
      nb.final={p1id:nb.semi1.winnerId,p2id:upd.winnerId,cups1:0,cups2:0};
      setBK(nb);setBP('third');
    }
    else if(bPhase==='third'){setBK(nb);setBP('final');}
    else{setBK(nb);setPhase('tableau');}
    setC1('');setC2('');
  };

  // ── Stílus segédek ────────────────────────────────────────────────────────
  const Card = ({children,style={}}) => (
    <div style={{background:BPL,borderRadius:14,padding:'14px 16px',...style}}>{children}</div>
  );
  const SectionTitle = ({children}) => (
    <div style={{fontFamily:font,fontWeight:700,fontSize:10,color:'rgba(255,255,255,.45)',textTransform:'uppercase',letterSpacing:'.12em',marginBottom:8}}>{children}</div>
  );
  const CupsInput = ({label,val,set,color}) => (
    <div style={{flex:1,display:'flex',flexDirection:'column',alignItems:'center',gap:8}}>
      <div style={{fontFamily:font,fontWeight:800,fontSize:14,color:color||WHITE}}>{label}</div>
      <input type="number" min="0" max="10" value={val} onChange={e=>set(e.target.value)}
        style={{width:72,height:72,borderRadius:16,border:'2px solid '+(color||WHITE)+'44',
          background:'rgba(255,255,255,.08)',color:WHITE,fontFamily:font,fontWeight:900,
          fontSize:32,textAlign:'center',outline:'none'}} />
      <div style={{display:'flex',gap:6}}>
        {[0,1,2,3,4,5,6,7,8,9,10].map(n=>(
          <button key={n} onClick={()=>set(String(n))} style={{
            width:24,height:24,borderRadius:6,border:'none',
            background:String(n)===val?color||WHITE:'rgba(255,255,255,.1)',
            color:String(n)===val?BP:WHITE,fontFamily:font,fontWeight:700,fontSize:11,cursor:'pointer'
          }}>{n}</button>
        ))}
      </div>
    </div>
  );

  const MatchCard = ({m,bpLabel}) => {
    const p1=gp(m.p1id),p2=gp(m.p2id);
    return (
      <div style={{background:BP,borderRadius:14,overflow:'hidden'}}>
        {bpLabel && <div style={{background:GOLD,padding:'4px 12px',fontFamily:font,fontWeight:700,fontSize:11,color:BP}}>{bpLabel}</div>}
        <div style={{padding:'16px 20px',display:'flex',gap:16,alignItems:'center'}}>
          <CupsInput label={p1.name} val={c1} set={setC1} color={p1.color} />
          <div style={{fontFamily:font,fontWeight:900,fontSize:20,color:'rgba(255,255,255,.4)'}}>VS</div>
          <CupsInput label={p2.name} val={c2} set={setC2} color={p2.color} />
        </div>
        <div style={{padding:'0 16px 16px'}}>
          <button onClick={bPhase?submitBracket:submitGroup} disabled={c1===''||c2===''} style={{
            width:'100%',padding:'13px',borderRadius:12,border:'none',
            background:c1===''||c2===''?'rgba(255,255,255,.1)':BPGREEN,
            color:WHITE,fontFamily:font,fontWeight:900,fontSize:15,cursor:'pointer'
          }}>Rögzít →</button>
        </div>
      </div>
    );
  };

  // ── SETUP fázis ────────────────────────────────────────────────────────────
  if(phase==='setup') return (
    <div style={{flex:1,display:'flex',flexDirection:'column',background:BP,color:WHITE,overflowY:'auto'}}>
      <div style={{display:'flex',alignItems:'center',gap:12,padding:'16px 20px',background:BP2,borderBottom:'1px solid rgba(255,255,255,.08)'}}>
        <button onClick={()=>go('home')} style={{width:36,height:36,borderRadius:10,border:'none',background:'rgba(255,255,255,.1)',color:WHITE,fontSize:18,cursor:'pointer'}}>←</button>
        <div style={{fontFamily:font,fontWeight:900,fontSize:18}}>🏆 Bajnokság beállítása</div>
      </div>
      <div style={{padding:'20px 16px',display:'flex',flexDirection:'column',gap:16}}>
        <Card>
          <SectionTitle>Bajnokság neve</SectionTitle>
          <input value={tName} onChange={e=>setTName(e.target.value)}
            style={{width:'100%',padding:'10px 14px',borderRadius:10,border:'1.5px solid rgba(255,255,255,.2)',
              background:'rgba(255,255,255,.07)',color:WHITE,fontFamily:font,fontWeight:700,fontSize:16,outline:'none',boxSizing:'border-box'}}/>
          <div style={{fontFamily:font,fontSize:12,color:'rgba(255,255,255,.4)',marginTop:8}}>{tDate}</div>
        </Card>

        <Card>
          <SectionTitle>Játékosok kiválasztása</SectionTitle>
          <div style={{display:'flex',flexDirection:'column',gap:8}}>
            {appPlayers.map(p=>{
              const sel=tPlayers.find(x=>x.id===p.id);
              return(
                <div key={p.id} style={{display:'flex',alignItems:'center',gap:10,padding:'8px 12px',
                  borderRadius:10,background:sel?p.color+'22':'rgba(255,255,255,.05)',
                  border:'1.5px solid '+(sel?p.color+'88':'transparent'),cursor:'pointer'}}
                  onClick={()=>togglePlayer(p)}>
                  <div style={{width:32,height:32,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:font,fontWeight:900,fontSize:14,color:WHITE}}>
                    {p.name[0]}
                  </div>
                  <span style={{fontFamily:font,fontWeight:700,fontSize:15,flex:1}}>{p.name}</span>
                  {sel && (
                    <div style={{display:'flex',gap:4}}>
                      {['A','B'].map(g=>(
                        <button key={g} onClick={e=>{e.stopPropagation();setGroup(p.id,g);}} style={{
                          width:28,height:28,borderRadius:7,border:'none',cursor:'pointer',
                          background:sel.groupId===g?GOLD:'rgba(255,255,255,.1)',
                          color:sel.groupId===g?BP:WHITE,fontFamily:font,fontWeight:900,fontSize:13
                        }}>{g}</button>
                      ))}
                    </div>
                  )}
                  {!sel && <div style={{width:20,height:20,borderRadius:'50%',border:'2px solid rgba(255,255,255,.2)'}} />}
                </div>
              );
            })}
          </div>
        </Card>

        {tPlayers.length>0 && (
          <Card>
            <SectionTitle>Csoportok összefoglalója</SectionTitle>
            {['A','B'].map(g=>(
              <div key={g} style={{marginBottom:8}}>
                <div style={{fontFamily:font,fontWeight:800,fontSize:13,color:GOLD,marginBottom:4}}>{g} csoport ({tPlayers.filter(p=>p.groupId===g).length} fő)</div>
                {tPlayers.filter(p=>p.groupId===g).map(p=>(
                  <div key={p.id} style={{fontFamily:font,fontSize:13,color:'rgba(255,255,255,.7)',paddingLeft:8}}>· {p.name}</div>
                ))}
              </div>
            ))}
          </Card>
        )}

        <button onClick={startGroup} disabled={!canStart} style={{
          padding:'16px',borderRadius:14,border:'none',
          background:canStart?GOLD:'rgba(255,255,255,.1)',
          color:canStart?BP:WHITE,fontFamily:font,fontWeight:900,fontSize:16,cursor:'pointer'
        }}>{canStart?'🏁 Csoportkör indítása':'Adj hozzá min. 2-2 játékost csoportonként'}</button>
      </div>
    </div>
  );

  // ── CSOPORTKÖR fázis ────────────────────────────────────────────────────────
  if(phase==='group') {
    const m=matchQueue[matchIdx];
    const p1=gp(m.p1id),p2=gp(m.p2id);
    const done=matchIdx/matchQueue.length;
    return(
      <div style={{flex:1,display:'flex',flexDirection:'column',background:BP,color:WHITE,overflowY:'auto'}}>
        <div style={{display:'flex',alignItems:'center',gap:12,padding:'16px 20px',background:BP2,borderBottom:'1px solid rgba(255,255,255,.08)'}}>
          <button onClick={()=>setPhase('setup')} style={{width:36,height:36,borderRadius:10,border:'none',background:'rgba(255,255,255,.1)',color:WHITE,fontSize:18,cursor:'pointer'}}>←</button>
          <div style={{flex:1}}>
            <div style={{fontFamily:font,fontWeight:900,fontSize:16}}>⚔️ Csoportkör</div>
            <div style={{fontFamily:font,fontSize:12,color:'rgba(255,255,255,.5)'}}>{matchIdx+1}. meccs / {matchQueue.length}</div>
          </div>
        </div>
        <div style={{height:4,background:'rgba(255,255,255,.1)'}}>
          <div style={{height:'100%',background:GOLD,width:(done*100)+'%',transition:'width .3s'}} />
        </div>
        <div style={{padding:'20px 16px',display:'flex',flexDirection:'column',gap:16}}>
          <div style={{textAlign:'center',fontFamily:font,fontSize:12,color:GOLD,fontWeight:700,letterSpacing:'.08em',textTransform:'uppercase'}}>
            {m.groupId} csoport · {matchIdx+1}/{matchQueue.length}
          </div>
          <div style={{background:BP2,borderRadius:14,overflow:'hidden'}}>
            <div style={{padding:'20px 16px',display:'flex',gap:12,alignItems:'flex-start'}}>
              <CupsInput label={p1.name} val={c1} set={setC1} color={p1.color} />
              <div style={{fontFamily:font,fontWeight:900,fontSize:22,color:'rgba(255,255,255,.4)',paddingTop:48}}>VS</div>
              <CupsInput label={p2.name} val={c2} set={setC2} color={p2.color} />
            </div>
            <div style={{padding:'0 16px 16px'}}>
              <button onClick={submitGroup} disabled={c1===''||c2===''} style={{
                width:'100%',padding:'14px',borderRadius:12,border:'none',
                background:c1===''||c2===''?'rgba(255,255,255,.1)':BPGREEN,
                color:WHITE,fontFamily:font,fontWeight:900,fontSize:16,cursor:'pointer'
              }}>{matchIdx<matchQueue.length-1?'Rögzít →':'Rögzít + Ágrajz →'}</button>
            </div>
          </div>

          {groupMatches.length>0 && (
            <Card>
              <SectionTitle>Rögzített meccsek</SectionTitle>
              {groupMatches.slice().reverse().map((gm,i)=>{
                const gp1=gp(gm.p1id),gp2=gp(gm.p2id);
                return(
                  <div key={i} style={{display:'flex',alignItems:'center',gap:8,padding:'6px 0',borderBottom:'1px solid rgba(255,255,255,.07)'}}>
                    <div style={{width:8,height:8,borderRadius:'50%',background:GOLD,flexShrink:0}}/>
                    <span style={{fontFamily:font,fontSize:13,flex:1,color:'rgba(255,255,255,.8)'}}>
                      <span style={{color:gp1.color,fontWeight:700}}>{gp1.name}</span>
                      {' '}<span style={{fontWeight:900}}>{gm.cups1}–{gm.cups2}</span>{' '}
                      <span style={{color:gp2.color,fontWeight:700}}>{gp2.name}</span>
                    </span>
                    <span style={{fontFamily:font,fontSize:11,color:'rgba(255,255,255,.4)'}}>{gm.groupId}</span>
                  </div>
                );
              })}
            </Card>
          )}
        </div>
      </div>
    );
  }

  // ── ÁGRAJZ (bracket) fázis ─────────────────────────────────────────────────
  if(phase==='bracket') {
    const bLabels = {semi1:'Elődöntő 1',semi2:'Elődöntő 2',third:'3. helyért',final:'DÖNTŐ'};
    const bOrder = ['semi1','semi2','third','final'];
    const m=bracket[bPhase];
    const p1=gp(m?.p1id),p2=gp(m?.p2id);
    return(
      <div style={{flex:1,display:'flex',flexDirection:'column',background:BP,color:WHITE,overflowY:'auto'}}>
        <div style={{display:'flex',alignItems:'center',gap:12,padding:'16px 20px',background:BP2,borderBottom:'1px solid rgba(255,255,255,.08)'}}>
          <button onClick={()=>setPhase('group')} style={{width:36,height:36,borderRadius:10,border:'none',background:'rgba(255,255,255,.1)',color:WHITE,fontSize:18,cursor:'pointer'}}>←</button>
          <div style={{fontFamily:font,fontWeight:900,fontSize:16}}>🏆 {bLabels[bPhase]}</div>
        </div>
        <div style={{padding:'20px 16px',display:'flex',flexDirection:'column',gap:16}}>
          {/* Lépések */}
          <div style={{display:'flex',gap:6}}>
            {bOrder.map(bp=>{
              const done=bOrder.indexOf(bp)<bOrder.indexOf(bPhase);
              const cur=bp===bPhase;
              return(
                <div key={bp} style={{flex:1,padding:'6px 4px',borderRadius:8,textAlign:'center',
                  background:done?BPGREEN+'33':cur?GOLD+'33':'rgba(255,255,255,.05)',
                  border:'1.5px solid '+(done?BPGREEN:cur?GOLD:'transparent')}}>
                  <div style={{fontFamily:font,fontSize:10,fontWeight:700,color:done?BPGREEN:cur?GOLD:'rgba(255,255,255,.4)'}}>{done?'✓':bLabels[bp]}</div>
                </div>
              );
            })}
          </div>

          {m && (
            <div style={{background:BP2,borderRadius:14,overflow:'hidden'}}>
              <div style={{background:bPhase==='final'?GOLD:BPL,padding:'8px 16px',fontFamily:font,fontWeight:700,fontSize:13,color:bPhase==='final'?BP:GOLD}}>
                {bLabels[bPhase]}
              </div>
              <div style={{padding:'20px 16px',display:'flex',gap:12,alignItems:'flex-start'}}>
                <CupsInput label={p1.name} val={c1} set={setC1} color={p1.color} />
                <div style={{fontFamily:font,fontWeight:900,fontSize:22,color:'rgba(255,255,255,.4)',paddingTop:48}}>VS</div>
                <CupsInput label={p2.name} val={c2} set={setC2} color={p2.color} />
              </div>
              <div style={{padding:'0 16px 16px'}}>
                <button onClick={submitBracket} disabled={c1===''||c2===''} style={{
                  width:'100%',padding:'14px',borderRadius:12,border:'none',
                  background:c1===''||c2===''?'rgba(255,255,255,.1)':bPhase==='final'?GOLD:BPGREEN,
                  color:c1===''||c2===''?WHITE:bPhase==='final'?BP:WHITE,
                  fontFamily:font,fontWeight:900,fontSize:16,cursor:'pointer'
                }}>{bPhase==='final'?'🏆 Tábló megtekintése →':'Rögzít →'}</button>
              </div>
            </div>
          )}

          {/* Kész meccsek */}
          <Card>
            <SectionTitle>Ágrajz állása</SectionTitle>
            {bOrder.filter(bp=>bracket[bp]?.winnerId).map(bp=>{
              const bm=bracket[bp];
              const bp1=gp(bm.p1id),bp2=gp(bm.p2id),bw=gp(bm.winnerId);
              return(
                <div key={bp} style={{display:'flex',alignItems:'center',gap:8,padding:'6px 0',borderBottom:'1px solid rgba(255,255,255,.07)'}}>
                  <span style={{fontFamily:font,fontSize:11,color:GOLD,fontWeight:700,minWidth:80}}>{bLabels[bp]}</span>
                  <span style={{fontFamily:font,fontSize:13,flex:1}}>
                    <span style={{color:bp1.color,fontWeight:700}}>{bp1.name}</span>
                    {' '}<span style={{fontWeight:900}}>{bm.cups1}–{bm.cups2}</span>{' '}
                    <span style={{color:bp2.color,fontWeight:700}}>{bp2.name}</span>
                  </span>
                  <span style={{fontSize:12}}>🏆 {bw.name}</span>
                </div>
              );
            })}
          </Card>
        </div>
      </div>
    );
  }

  // ── TÁBLÓ fázis ────────────────────────────────────────────────────────────
  if(phase==='tableau') {
    const stA=calcSt('A',groupMatches);
    const stB=calcSt('B',groupMatches);
    const winner=gp(bracket.final?.winnerId);
    const second=gp(bracket.final?.loserId);
    const third=gp(bracket.third?.winnerId);
    const fourth=gp(bracket.third?.loserId);
    const others=tPlayers.filter(p=>![winner.id,second.id,third.id,fourth.id].includes(p.id));

    const StRow=({st,rank})=>{
      const p=gp(st.pid);
      return(
        <div style={{display:'flex',alignItems:'center',gap:6,padding:'3px 0',borderBottom:'1px solid rgba(255,255,255,.07)'}}>
          <span style={{fontFamily:font,fontSize:10,color:'rgba(255,255,255,.4)',width:14,textAlign:'right'}}>{rank}</span>
          <div style={{width:16,height:16,borderRadius:'50%',background:p.color,flexShrink:0,display:'grid',placeItems:'center',fontSize:8,fontWeight:900,color:WHITE}}>{p.name[0]}</div>
          <span style={{fontFamily:font,fontSize:11,fontWeight:700,flex:1,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap',color:WHITE}}>{p.name}</span>
          <span style={{fontFamily:font,fontSize:10,color:'rgba(255,255,255,.6)',minWidth:12,textAlign:'center'}}>{st.Gy}</span>
          <span style={{fontFamily:font,fontSize:10,color:'rgba(255,255,255,.4)',minWidth:12,textAlign:'center'}}>{st.D}</span>
          <span style={{fontFamily:font,fontSize:10,color:'rgba(255,255,255,.4)',minWidth:12,textAlign:'center'}}>{st.V}</span>
          <span style={{fontFamily:font,fontSize:10,color:BPGREEN,minWidth:16,textAlign:'center'}}>{st.pp}</span>
          <span style={{fontFamily:font,fontSize:10,color:BPRED,minWidth:16,textAlign:'center'}}>{st.pk}</span>
        </div>
      );
    };

    const MatchRow=({m})=>{
      const mp1=gp(m.p1id),mp2=gp(m.p2id);
      const w1=m.cups1>m.cups2;
      return(
        <div style={{display:'flex',alignItems:'center',gap:4,padding:'2px 0'}}>
          <span style={{fontFamily:font,fontSize:10,color:w1?mp1.color:'rgba(255,255,255,.5)',fontWeight:w1?700:400,flex:1,textAlign:'right',overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{mp1.name}</span>
          <span style={{fontFamily:font,fontSize:10,fontWeight:900,color:WHITE,minWidth:32,textAlign:'center'}}>{m.cups1}–{m.cups2}</span>
          <span style={{fontFamily:font,fontSize:10,color:!w1?mp2.color:'rgba(255,255,255,.5)',fontWeight:!w1?700:400,flex:1,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{mp2.name}</span>
        </div>
      );
    };

    const BracketBox=({m,label,highlight})=>{
      if(!m)return null;
      const bp1=gp(m.p1id),bp2=gp(m.p2id);
      const w1=m.cups1>m.cups2,w2=m.cups2>m.cups1;
      return(
        <div style={{background:highlight?GOLD+'22':BP,borderRadius:10,overflow:'hidden',border:'1px solid '+(highlight?GOLD:'rgba(255,255,255,.1)')}}>
          <div style={{padding:'3px 8px',background:highlight?GOLD+'44':'rgba(255,255,255,.07)',fontFamily:font,fontSize:9,fontWeight:700,color:highlight?GOLD:'rgba(255,255,255,.5)',textTransform:'uppercase',letterSpacing:'.06em'}}>{label}</div>
          <div style={{padding:'6px 8px',display:'flex',flexDirection:'column',gap:4}}>
            <div style={{display:'flex',alignItems:'center',gap:6}}>
              <div style={{width:12,height:12,borderRadius:'50%',background:bp1.color,flexShrink:0}} />
              <span style={{fontFamily:font,fontSize:11,fontWeight:w1?900:400,color:w1?WHITE:'rgba(255,255,255,.5)',flex:1,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{bp1.name}</span>
              <span style={{fontFamily:font,fontSize:12,fontWeight:900,color:w1?WHITE:'rgba(255,255,255,.4)'}}>{m.cups1}</span>
            </div>
            <div style={{display:'flex',alignItems:'center',gap:6}}>
              <div style={{width:12,height:12,borderRadius:'50%',background:bp2.color,flexShrink:0}} />
              <span style={{fontFamily:font,fontSize:11,fontWeight:w2?900:400,color:w2?WHITE:'rgba(255,255,255,.5)',flex:1,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{bp2.name}</span>
              <span style={{fontFamily:font,fontSize:12,fontWeight:900,color:w2?WHITE:'rgba(255,255,255,.4)'}}>{m.cups2}</span>
            </div>
          </div>
        </div>
      );
    };

    return(
      <div style={{flex:1,display:'flex',flexDirection:'column',background:BP,color:WHITE}}>
        {/* Header */}
        <div style={{display:'flex',alignItems:'center',gap:12,padding:'12px 16px',background:BP2,borderBottom:'1px solid rgba(255,255,255,.08)',flexShrink:0}}>
          <button onClick={()=>setPhase('bracket')} style={{width:36,height:36,borderRadius:10,border:'none',background:'rgba(255,255,255,.1)',color:WHITE,fontSize:18,cursor:'pointer'}}>←</button>
          <div style={{fontFamily:font,fontWeight:900,fontSize:16,flex:1}}>📊 Tábló</div>
          <button onClick={()=>{
            if(navigator.share){navigator.share({title:tName,text:`${tName} — ${tDate}\n🥇 ${winner.name}\n🥈 ${second.name}\n🥉 ${third.name}`}).catch(()=>{});}
            else{alert('Készíts képernyőképet a megosztáshoz!');}
          }} style={{padding:'8px 14px',borderRadius:10,border:'none',background:GOLD,color:BP,fontFamily:font,fontWeight:800,fontSize:13,cursor:'pointer'}}>
            📤 Megosztás
          </button>
        </div>

        {/* Tábló tartalom — landscape */}
        <div ref={tableauRef} style={{flex:1,overflowY:'auto',padding:'0'}}>
          {/* App fejléc */}
          <div style={{background:BP2,padding:'10px 16px',display:'flex',alignItems:'center',gap:12,borderBottom:'1px solid rgba(255,255,255,.08)'}}>
            <span style={{fontSize:20}}>🍺</span>
            <div>
              <div style={{fontFamily:font,fontWeight:900,fontSize:14}}>{tName}</div>
              <div style={{fontFamily:font,fontSize:11,color:'rgba(255,255,255,.5)'}}>{tDate} · {tPlayers.length} játékos · 2 csoport + kieséses</div>
            </div>
          </div>

          {/* Három oszlop */}
          <div style={{display:'flex',minHeight:400,gap:0}}>

            {/* BAL — Csoportok */}
            <div style={{width:'30%',minWidth:180,borderRight:'1px solid rgba(255,255,255,.08)',padding:'12px',display:'flex',flexDirection:'column',gap:10}}>
              {['A','B'].map(g=>{
                const st=g==='A'?stA:stB;
                return(
                  <div key={g}>
                    <div style={{fontFamily:font,fontWeight:800,fontSize:11,color:GOLD,marginBottom:4}}>{g} CSOPORT</div>
                    <div style={{display:'flex',gap:4,marginBottom:3,paddingLeft:30}}>
                      {['Gy','D','V','P+','P-'].map(h=>(
                        <span key={h} style={{fontFamily:font,fontSize:9,color:'rgba(255,255,255,.35)',minWidth:16,textAlign:'center'}}>{h}</span>
                      ))}
                    </div>
                    {st.map((s,i)=><StRow key={s.pid} st={s} rank={i+1} />)}
                  </div>
                );
              })}

              <div style={{marginTop:4}}>
                <div style={{fontFamily:font,fontWeight:800,fontSize:11,color:GOLD,marginBottom:6}}>CSOP. MECCSEK</div>
                {groupMatches.map((m,i)=><MatchRow key={i} m={m} />)}
              </div>
            </div>

            {/* JOBB — Ágrajz + Dobogó */}
            <div style={{flex:1,display:'flex',flexDirection:'column'}}>

              {/* ÁGRAJZ */}
              <div style={{flex:'0 0 auto',padding:'12px',borderBottom:'1px solid rgba(255,255,255,.08)'}}>
                <div style={{fontFamily:font,fontWeight:800,fontSize:11,color:GOLD,marginBottom:10}}>ÁGRAJZ</div>
                <div style={{display:'flex',gap:8,alignItems:'flex-start'}}>
                  {/* Bal elődöntők */}
                  <div style={{flex:1,display:'flex',flexDirection:'column',gap:8}}>
                    <BracketBox m={bracket.semi1} label="Elődöntő 1" />
                    <BracketBox m={bracket.semi2} label="Elődöntő 2" />
                  </div>
                  {/* Nyíl */}
                  <div style={{display:'flex',alignItems:'center',fontSize:16,color:'rgba(255,255,255,.3)',paddingTop:24}}>→</div>
                  {/* Döntő */}
                  <div style={{flex:1,display:'flex',flexDirection:'column',gap:8,justifyContent:'center'}}>
                    <BracketBox m={bracket.final} label="DÖNTŐ" highlight={true} />
                    <BracketBox m={bracket.third} label="3. helyért" />
                  </div>
                </div>
              </div>

              {/* DOBOGÓ */}
              <div style={{flex:1,padding:'12px',display:'flex',flexDirection:'column'}}>
                <div style={{fontFamily:font,fontWeight:800,fontSize:11,color:GOLD,marginBottom:10}}>VÉGEREDMÉNY</div>
                <div style={{display:'flex',alignItems:'flex-end',gap:8,flex:1}}>
                  {/* 2. hely */}
                  <div style={{flex:1,display:'flex',flexDirection:'column',alignItems:'center',gap:4}}>
                    <div style={{fontFamily:font,fontSize:9,color:'rgba(255,255,255,.5)'}}>🥈</div>
                    <div style={{width:'100%',background:SILVER+'33',borderRadius:'8px 8px 0 0',height:60,display:'flex',alignItems:'center',justifyContent:'center'}}>
                      <div style={{width:28,height:28,borderRadius:'50%',background:second.color,display:'grid',placeItems:'center',fontFamily:font,fontWeight:900,fontSize:13,color:WHITE}}>{second.name?.[0]}</div>
                    </div>
                    <div style={{fontFamily:font,fontWeight:800,fontSize:11,color:SILVER,textAlign:'center'}}>{second.name}</div>
                  </div>
                  {/* 1. hely */}
                  <div style={{flex:1,display:'flex',flexDirection:'column',alignItems:'center',gap:4}}>
                    <div style={{fontFamily:font,fontSize:9,color:'rgba(255,255,255,.5)'}}>🥇</div>
                    <div style={{width:'100%',background:GOLD+'44',borderRadius:'8px 8px 0 0',height:84,display:'flex',alignItems:'center',justifyContent:'center',border:'1.5px solid '+GOLD+'66'}}>
                      <div style={{width:36,height:36,borderRadius:'50%',background:winner.color,display:'grid',placeItems:'center',fontFamily:font,fontWeight:900,fontSize:16,color:WHITE}}>{winner.name?.[0]}</div>
                    </div>
                    <div style={{fontFamily:font,fontWeight:900,fontSize:13,color:GOLD,textAlign:'center'}}>{winner.name}</div>
                  </div>
                  {/* 3. hely */}
                  <div style={{flex:1,display:'flex',flexDirection:'column',alignItems:'center',gap:4}}>
                    <div style={{fontFamily:font,fontSize:9,color:'rgba(255,255,255,.5)'}}>🥉</div>
                    <div style={{width:'100%',background:BRONZE+'33',borderRadius:'8px 8px 0 0',height:44,display:'flex',alignItems:'center',justifyContent:'center'}}>
                      <div style={{width:24,height:24,borderRadius:'50%',background:third.color,display:'grid',placeItems:'center',fontFamily:font,fontWeight:900,fontSize:11,color:WHITE}}>{third.name?.[0]}</div>
                    </div>
                    <div style={{fontFamily:font,fontWeight:800,fontSize:11,color:BRONZE,textAlign:'center'}}>{third.name}</div>
                  </div>
                </div>
                {/* 4+ helyezések */}
                <div style={{marginTop:10}}>
                  {[fourth,...others].filter(Boolean).map((p,i)=>(
                    <div key={p.id} style={{display:'flex',alignItems:'center',gap:8,padding:'4px 0',borderTop:'1px solid rgba(255,255,255,.06)'}}>
                      <span style={{fontFamily:font,fontSize:11,color:'rgba(255,255,255,.4)',minWidth:16}}>{i+4}.</span>
                      <div style={{width:16,height:16,borderRadius:'50%',background:p.color}} />
                      <span style={{fontFamily:font,fontSize:12,fontWeight:700,color:'rgba(255,255,255,.7)'}}>{p.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
  return null;
}

"""

assert '\nfunction Root(' in src, 'Root not found'
src = src.replace('\nfunction Root(', COMPONENT + '\nfunction Root(', 1)

# ── 2. BottleApp: beerpong screen hozzáadása ──────────────────────────────────
OLD_SCREENS = "{screen==='observer' && <ObserverScreen go={go} initialCode={observerInitCode || (!_initRoomConsumedRef.current && _initRoom ? (_initRoomConsumedRef.current = true, _initRoom) : '')} onJoinAsHost={goJoinAsHost} />}"
NEW_SCREENS  = OLD_SCREENS + "\n        {screen==='beerpong' && <BeerPongTournamentScreen go={go} players={players} />}"
assert OLD_SCREENS in src, 'observer screen not found'
src = src.replace(OLD_SCREENS, NEW_SCREENS, 1)

# ── 3. HomeScreen: bajnokság gomb ──────────────────────────────────────────────
# A Quick Game gomb után tegyük
OLD_QGAME = """              <button onClick={onQuickGame} style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center', gap:10, padding:'0 12px', border:'none', background:T.surface, borderRadius:20, cursor:'pointer', boxShadow:T.shadow }}>
                <div style={{ width:36, height:36, borderRadius:'50%', background:T.mintSoft, display:'grid', placeItems:'center', flexShrink:0 }}>
                  <span style={{ fontSize:18 }}>⚡</span>
                </div>
                <div style={{ textAlign:'left' }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.mint, letterSpacing:'-0.01em' }}>Quick Game</div>
                  <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:1 }}>{t('quickGameSub')}</div>
                </div>
              </button>
            </div>"""
NEW_QGAME = OLD_QGAME + """
            <button onClick={() => go('beerpong')} style={{ display:'flex', alignItems:'center', gap:12, width:'100%', padding:'12px 16px', background:T.surface, border:'1.5px solid #F59E0B55', borderRadius:18, cursor:'pointer', textAlign:'left', boxShadow:T.shadow, marginTop:8 }}>
              <div style={{ width:36, height:36, borderRadius:10, background:'#F59E0B22', display:'grid', placeItems:'center', flexShrink:0 }}>
                <span style={{ fontSize:20 }}>🏆</span>
              </div>
              <div style={{ flex:1 }}>
                <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:'#F59E0B' }}>Beerpong Bajnokság</div>
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:1 }}>Tábló, ágrajz, eredmények</div>
              </div>
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M7 4l5 5-5 5" stroke={T.inkSoft} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
            </button>"""
assert OLD_QGAME in src, 'quick game btn not found'
src = src.replace(OLD_QGAME, NEW_QGAME, 1)

# ── 4. Version bump ────────────────────────────────────────────────────────────
assert "APP_VERSION = 'v9.419';" in src
src = src.replace("APP_VERSION = 'v9.419';", "APP_VERSION = 'v9.420';", 1)

with open('index.html','w',encoding='utf-8') as f:
    f.write(src)
print('v9.420 OK — BeerPong Bajnokság modul kész')
