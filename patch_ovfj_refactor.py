#!/usr/bin/env python3
# v9.815 — Orszag-Varos (ovfj) full refactor:
# draw animation, phone-first flow, host plays on own device, 1pt scoring, configurable rounds
import io, re, sys

P = '/home/user/bottle-of-heroes/index.html'
src = io.open(P, encoding='utf-8').read()

def assert_in(s, what):
    assert s in src, 'ANCHOR NOT FOUND: ' + what
def assert_count(s, n, what):
    c = src.count(s)
    assert c == n, 'COUNT MISMATCH (%s): expected %d got %d' % (what, n, c)

# ---------- 1) Version bump ----------
assert_count("'v9.814'", 1, 'version')
src = src.replace("'v9.814'", "'v9.815'")

# ---------- 2) Game description ----------
old_desc = "desc:'Betű kisorsol, mindenki kitölti a 8 kategóriát a saját telefonján. Aki elsőként kész, a többieknek +10 mp. Szavazással dől el ki érvényes — egyedi válasz 10 pt, dupla 5 pt.'"
new_desc = "desc:'Betűsorsolás, mindenki a saját telefonján tölti ki a 8 kategóriát. Aki elsőként kész, a többieknek +10 mp marad. Szavazás dönt — minden érvényes szó 1 pont.'"
assert_count(old_desc, 1, 'ovfj desc')
src = src.replace(old_desc, new_desc)

# ---------- 3) Replace OVFJConfigSheet + OVFJGame + OVFJObserverView wholesale ----------
start_anchor = "function OVFJConfigSheet({ config, setConfig, onClose }) {"
end_anchor = "\nfunction CollectBoomGame({ gameIdx, players, onAdvance, onResult, gameMeta }) {"
assert_count(start_anchor, 1, 'start anchor')
assert_count(end_anchor, 1, 'end anchor')
i0 = src.index(start_anchor)
i1 = src.index(end_anchor)
assert i0 < i1, 'anchor order'

NEW = r'''function OVFJConfigSheet({ config, setConfig, onClose }) {
  const rounds = config.rounds ?? 5;
  return (
    <SheetOverlay onClose={onClose} title="Ország-Város beállítások" footer={
      <button onClick={onClose} style={{ width:'100%', padding:'15px', borderRadius:16, background:T.mint, border:'none', color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer', boxShadow:'0 5px 16px -5px rgba(79,194,160,0.6)' }}>Kész</button>
    }>
      <div style={{ padding:'0 18px 8px', display:'flex', flexDirection:'column' }}>
        <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, padding:'10px 0 6px' }}>Ország · Város · Fiú · Lány · Növény · Állat · Tárgy · Híresség</div>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:'13px 0' }}>
          <div>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>Körök száma</div>
            <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:1 }}>Ennyi betűt sorsolunk</div>
          </div>
          <div style={{ display:'flex', background:T.surfaceMuted, padding:4, borderRadius:12, gap:3, flexShrink:0 }}>
            {[3,5,8,10].map(n=>(
              <button key={n} onClick={()=>setConfig(c=>({...c,rounds:n}))} style={{ width:42, padding:'8px 4px', borderRadius:9, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:14, background:rounds===n?T.mint:'transparent', color:rounds===n?'#fff':T.inkSoft, transition:'all .15s' }}>{n}</button>
            ))}
          </div>
        </div>
      </div>
    </SheetOverlay>
  );
}

// ═══════════════ ORSZÁG-VÁROS — közös segédek ═══════════════
const OVFJ_DRAW_MS = 4000;
function ovfjVoteKey(round, pid, catKey) { return 'r' + round + '_' + pid + '_' + catKey; }
// Érvényesség: üres / rossz kezdőbetű / egyező (case-insensitive, trim)
function ovfjBuildValidity(answers, letter, round) {
  const recs = Object.values(answers || {}).filter(a => a && a.round === round);
  const dup = {};
  OVFJ_CATS.forEach(cat => {
    const freq = {};
    recs.forEach(a => { const v = String(a[cat.key]||'').trim().toLowerCase(); if (v) freq[v] = (freq[v]||0)+1; });
    dup[cat.key] = new Set(Object.keys(freq).filter(v => freq[v] > 1));
  });
  return (pid, catKey) => {
    const a = (answers||{})[pid];
    const val = String((a && a[catKey]) || '').trim();
    if (!val) return { val, valid:false, reason:'üres' };
    if (!ovfjLetterOk(val, letter)) return { val, valid:false, reason:'✗ betű' };
    if (dup[catKey].has(val.toLowerCase())) return { val, valid:false, reason:'× egyező' };
    return { val, valid:true, reason:null };
  };
}
// Betűsorsoló animáció — drawTs-től lokálisan fut, mindenkinél szinkronban
function OVFJDrawAnim({ letter, drawTs, size }) {
  const s = size || 170;
  const [disp, setDisp] = React.useState('?');
  const [done, setDone] = React.useState(false);
  React.useEffect(() => {
    let raf = null, lastFlip = 0;
    setDone(false);
    const tick = () => {
      const el = Date.now() - (drawTs || Date.now());
      if (el >= OVFJ_DRAW_MS - 400) { setDisp(letter); setDone(true); return; }
      const t = Math.min(1, el / (OVFJ_DRAW_MS - 400));
      const iv = 55 + t * t * 340; // gyorsan pörög, majd lassul
      const now = Date.now();
      if (now - lastFlip >= iv) {
        lastFlip = now;
        setDisp(OVFJ_LETTERS[Math.floor(Math.random() * OVFJ_LETTERS.length)]);
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [drawTs, letter]);
  return (
    <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:16,padding:'26px 0'}}>
      <div style={{width:s,height:s,borderRadius:Math.round(s*0.22),background:done?`linear-gradient(135deg,${T.yellow},${T.coral})`:T.surface,display:'grid',placeItems:'center',boxShadow:done?T.shadowLift:T.shadow,transform:done?'scale(1.08)':'scale(1)',transition:'background .35s, transform .35s'}}>
        <span style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:Math.round(s*0.5),color:done?'#fff':T.inkSoft,lineHeight:1}}>{disp}</span>
      </div>
      <div style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:14,color:done?T.mint:T.inkSoft,letterSpacing:'0.06em',textTransform:'uppercase'}}>{done ? 'Ez a betűd!' : 'Betűsorsolás…'}</div>
    </div>
  );
}
function OVFJAvatar({ p, size }) {
  const s = size || 32;
  return (
    <div style={{width:s,height:s,borderRadius:'50%',background:(p&&p.color)||T.mint,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:Math.round(s*0.4),color:'#fff',flexShrink:0,overflow:'hidden'}}>
      {p && p.img ? <img src={p.img} style={{width:s,height:s,objectFit:'cover'}} /> : String((p&&p.name&&p.name[0])||'?').toUpperCase()}
    </div>
  );
}
// Írás UI — host telefonján és játékos telefonokon ugyanaz
function OVFJWritingForm({ letter, remaining, localAns, setLocalAns, submitted, onSubmit, doneInfo }) {
  const inputRefs = React.useRef([]);
  return (
    <div style={{display:'flex',flexDirection:'column',gap:10,width:'100%'}}>
      <div style={{display:'flex',gap:10,alignItems:'stretch'}}>
        <div style={{flex:'0 0 auto',width:92,minHeight:92,borderRadius:22,background:`linear-gradient(135deg,${T.yellow},${T.coral})`,display:'grid',placeItems:'center',boxShadow:T.shadowLift}}>
          <span style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:50,color:'#fff',lineHeight:1}}>{letter}</span>
        </div>
        <div style={{flex:1,background:remaining!=null&&remaining<=5?T.coralSoft:T.surface,borderRadius:22,padding:'12px 16px',boxShadow:T.shadow,display:'flex',flexDirection:'column',justifyContent:'center',gap:3,transition:'background .3s'}}>
          {remaining != null ? (
            <>
              <div style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:remaining<=5?T.coral:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.08em'}}>Valaki kész — siess!</div>
              <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:36,color:remaining<=5?T.coral:T.ink,lineHeight:1,fontVariantNumeric:'tabular-nums'}}>{remaining}s</div>
            </>
          ) : (
            <>
              <div style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.08em'}}>Írj a betűre!</div>
              <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,lineHeight:1.4}}>Az első kész után mindenkinek 10 mp marad</div>
            </>
          )}
          {doneInfo && <div style={{fontFamily:T.font,fontSize:11,color:T.inkSoft,marginTop:2}}>{doneInfo}</div>}
        </div>
      </div>
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8}}>
        {OVFJ_CATS.map((cat,idx)=>{
          const v = localAns[cat.key]||'';
          const wrong = v.trim().length > 0 && !ovfjLetterOk(v, letter);
          return (
            <div key={cat.key} style={{background:T.surface,borderRadius:16,padding:'10px 12px',boxShadow:submitted?'none':T.shadow,opacity:submitted?0.65:1,display:'flex',flexDirection:'column',gap:4}}>
              <div style={{display:'flex',alignItems:'center',gap:6}}>
                <span style={{fontSize:16,flexShrink:0}}>{cat.emoji}</span>
                <span style={{fontFamily:T.font,fontSize:12,fontWeight:T.weightTitle,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.07em',flex:1,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{cat.label}</span>
                {v.trim() && !wrong && <span style={{fontSize:13}}>✅</span>}
              </div>
              <input
                ref={el=>inputRefs.current[idx]=el}
                type="text"
                value={v}
                onChange={e=>!submitted&&setLocalAns(p=>({...p,[cat.key]:e.target.value}))}
                onKeyDown={e=>{if(e.key==='Enter'&&idx<OVFJ_CATS.length-1)inputRefs.current[idx+1]?.focus();}}
                disabled={submitted}
                placeholder={`${letter}...`}
                style={{width:'100%',boxSizing:'border-box',padding:'5px 0',border:'none',borderBottom:`1.5px solid ${submitted?T.surfaceMuted:wrong?T.coral:T.mint}`,fontFamily:T.font,fontSize:14,fontWeight:T.weightTitle,background:'transparent',color:wrong?T.coral:T.ink,outline:'none',textDecoration:wrong?'line-through':'none'}}
              />
            </div>
          );
        })}
      </div>
      <div style={{position:'sticky',bottom:0,background:T.bg,paddingTop:8,paddingBottom:4,zIndex:10}}>
        {!submitted ? (
          <PrimaryButton onClick={onSubmit}>Kész vagyok! ✏️</PrimaryButton>
        ) : (
          <div style={{textAlign:'center',fontFamily:T.font,fontWeight:T.weightTitle,fontSize:15,color:T.mint,padding:'16px',background:T.mintSoft,borderRadius:16}}>✅ Beadva! Várd a többieket…</div>
        )}
      </div>
    </div>
  );
}
// Szavazó UI — saját válaszok + mások értékelése
function OVFJVotingView({ letter, round, players, answers, myPid, myVotes, onVote, tallies }) {
  const validity = ovfjBuildValidity(answers, letter, round);
  const participants = players.filter(p => answers[p.id] && answers[p.id].round === round);
  const me = participants.find(p => p.id === myPid);
  const others = participants.filter(p => p.id !== myPid);
  return (
    <div style={{display:'flex',flexDirection:'column',gap:10,width:'100%'}}>
      <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:17,color:T.ink,textAlign:'center',letterSpacing:T.letterDisplay}}>„{letter}" — Szavazás 👍👎</div>
      {me && (
        <div style={{background:T.mintSoft,borderRadius:16,padding:'12px 14px'}}>
          <div style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:11,color:T.mint,marginBottom:8,textTransform:'uppercase',letterSpacing:'0.08em'}}>A te válaszaid</div>
          {OVFJ_CATS.map(cat => {
            const vi = validity(myPid, cat.key);
            return (
              <div key={cat.key} style={{display:'flex',alignItems:'center',gap:6,marginBottom:4}}>
                <span style={{fontSize:13,width:20,textAlign:'center',flexShrink:0}}>{cat.emoji}</span>
                <span style={{fontFamily:T.font,fontSize:12,fontWeight:T.weightTitle,color:T.mint,width:66,flexShrink:0,textTransform:'uppercase',letterSpacing:'0.04em'}}>{cat.label}</span>
                <span style={{fontFamily:T.font,fontSize:13,fontWeight:T.weightTitle,flex:1,color:!vi.val?T.inkMute:vi.valid?T.ink:T.coral,textDecoration:vi.val&&!vi.valid?'line-through':'none',opacity:vi.val&&!vi.valid?0.7:1}}>{vi.val||'—'}</span>
                {vi.val && !vi.valid && <span style={{fontFamily:T.font,fontSize:12,fontWeight:T.weightTitle,color:T.coral,flexShrink:0}}>{vi.reason}</span>}
              </div>
            );
          })}
        </div>
      )}
      {others.map(p => (
        <div key={p.id} style={{background:T.surface,borderRadius:18,padding:'12px 14px',boxShadow:T.shadow}}>
          <div style={{display:'flex',alignItems:'center',gap:10,marginBottom:10}}>
            <OVFJAvatar p={p} size={28} />
            <span style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:15,color:T.ink,flex:1}}>{p.name}</span>
          </div>
          {OVFJ_CATS.map(cat => {
            const vi = validity(p.id, cat.key);
            const vk = ovfjVoteKey(round, p.id, cat.key);
            const mv = myVotes[vk];
            const tl = tallies ? (tallies[vk] || {yes:0,no:0}) : null;
            return (
              <div key={cat.key} style={{display:'flex',alignItems:'center',gap:5,marginBottom:6,paddingBottom:5,borderBottom:`1px solid ${T.surfaceMuted}`}}>
                <span style={{fontSize:13,flexShrink:0,width:20,textAlign:'center'}}>{cat.emoji}</span>
                <span style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:T.inkSoft,width:60,flexShrink:0,textTransform:'uppercase',letterSpacing:'0.04em'}}>{cat.label}</span>
                <span style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:13,flex:1,color:!vi.val?T.inkMute:vi.valid?T.ink:T.coral,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap',textDecoration:vi.val&&!vi.valid?'line-through':'none',opacity:vi.val&&!vi.valid?0.7:1}}>{vi.val||'—'}</span>
                {vi.valid ? (
                  <div style={{display:'flex',gap:4,flexShrink:0,alignItems:'center'}}>
                    {tl && <span style={{fontFamily:T.font,fontSize:10,color:T.inkSoft}}>👍{tl.yes} 👎{tl.no}</span>}
                    <a href={`https://www.google.com/search?q=${encodeURIComponent(vi.val)}`} target="_blank" rel="noreferrer" style={{fontSize:14,textDecoration:'none',opacity:0.5,lineHeight:1}}>🔍</a>
                    <button onClick={()=>onVote(p.id,cat.key,true)} style={{width:34,height:32,borderRadius:9,border:`1.5px solid ${mv===true?T.mint:T.surfaceMuted}`,background:mv===true?T.mintSoft:'transparent',cursor:'pointer',fontSize:15,display:'grid',placeItems:'center'}}>👍</button>
                    <button onClick={()=>onVote(p.id,cat.key,false)} style={{width:34,height:32,borderRadius:9,border:`1.5px solid ${mv===false?T.coral:T.surfaceMuted}`,background:mv===false?T.coralSoft:'transparent',cursor:'pointer',fontSize:15,display:'grid',placeItems:'center'}}>👎</button>
                  </div>
                ) : vi.val ? (
                  <span style={{fontFamily:T.font,fontSize:12,fontWeight:T.weightTitle,color:T.coral,flexShrink:0}}>{vi.reason}</span>
                ) : null}
              </div>
            );
          })}
        </div>
      ))}
      {others.length === 0 && <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft,textAlign:'center',padding:'12px 0'}}>Nincs kire szavazni…</div>}
    </div>
  );
}
// Rangsor lista (kör vége / végeredmény)
function OVFJStandings({ players, roundScores, cumScores, myPid, final }) {
  const srtd = [...players].sort((a,b)=>(cumScores?.[b.id]||0)-(cumScores?.[a.id]||0));
  return (
    <div style={{display:'flex',flexDirection:'column',gap:8,width:'100%'}}>
      {srtd.map((p,i)=>{
        const mine = myPid && p.id === myPid;
        return (
          <div key={p.id} style={{display:'flex',alignItems:'center',gap:12,background:mine?T.mintSoft:T.surface,borderRadius:16,padding:final&&i===0?'16px 16px':'12px 16px',boxShadow:T.shadow,border:mine?`2px solid ${T.mint}`:'none'}}>
            <span style={{fontSize:final&&i<3?24:20,minWidth:28,textAlign:'center'}}>{i===0?'🥇':i===1?'🥈':i===2?'🥉':(i+1)+'.'}</span>
            <OVFJAvatar p={p} size={34} />
            <div style={{flex:1,fontFamily:T.font,fontWeight:T.weightTitle,fontSize:15,color:T.ink}}>{p.name}{mine?' (Te)':''}</div>
            {!final && roundScores && <div style={{fontFamily:T.font,fontSize:12,fontWeight:T.weightTitle,color:(roundScores[p.id]||0)>0?T.mint:T.inkSoft}}>+{roundScores[p.id]||0}</div>}
            <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:20,color:i===0?T.coral:T.ink,minWidth:48,textAlign:'right'}}>{cumScores?.[p.id]||0} pt</div>
          </div>
        );
      })}
    </div>
  );
}

// ═══════════════ ORSZÁG-VÁROS — host nézet ═══════════════
function OVFJGame({ players, gameIdx, onAdvance, onResult, roomCode, gameMeta }) {
  const totalRounds = gameMeta?.ovfjConfig?.rounds ?? 5;
  const pl = players || [];
  const sessRef = React.useRef(Date.now());
  const sess = sessRef.current;
  const usedLettersRef = React.useRef([]);
  const drawLetter = () => {
    const available = OVFJ_LETTERS.filter(l => !usedLettersRef.current.includes(l));
    const pool = available.length > 0 ? available : OVFJ_LETTERS;
    const picked = pool[Math.floor(Math.random() * pool.length)];
    usedLettersRef.current = [...usedLettersRef.current, picked];
    return picked;
  };

  // pick → lobby → draw → writing → voting → results → final
  const [phase, setPhase] = React.useState('pick');
  const [hostPid, setHostPid] = React.useState(null);
  const [round, setRound] = React.useState(1);
  const [letter, setLetter] = React.useState(null);
  const [drawTs, setDrawTs] = React.useState(null);
  const [doneAt, setDoneAt] = React.useState(null);
  const [answers, setAnswers] = React.useState({});
  const [votes, setVotes] = React.useState({});
  const [takenIds, setTakenIds] = React.useState([]);
  const [roundScores, setRoundScores] = React.useState({});
  const [cumScores, setCumScores] = React.useState({});
  const [localAns, setLocalAns] = React.useState({});
  const [myVotes, setMyVotes] = React.useState({});
  const [submitted, setSubmitted] = React.useState(false);
  const [showQR, setShowQR] = React.useState(false);
  const [, setTick] = React.useState(0);
  const calcRef = React.useRef(false);
  const localAnsRef = React.useRef({});
  React.useEffect(() => { localAnsRef.current = localAns; }, [localAns]);
  const submittedRef = React.useRef(false);
  React.useEffect(() => { submittedRef.current = submitted; }, [submitted]);

  // Reset a szoba dokumentumban induláskor (új játék / gameIdx váltás)
  React.useEffect(() => {
    if (!roomCode || typeof syncRoom !== 'function') return;
    syncRoom(roomCode, { ovfjTakenIds: [], ovfjState: { sess, phase:'pick', round:1, totalRounds, letter:null, drawTs:null, doneAt:null, hostPid:null } });
  }, []);

  // Host az egyetlen, aki a teljes ovfjState-et írja
  React.useEffect(() => {
    if (!roomCode || typeof syncRoom !== 'function') return;
    syncRoom(roomCode, { ovfjState: { sess, phase, round, totalRounds, letter, drawTs, doneAt, hostPid, answers, roundScores, cumScores } });
  }, [phase, round, letter, drawTs, doneAt, hostPid, answers, roundScores, cumScores]);

  // Telefonos válaszok + szavazatok begyűjtése
  React.useEffect(() => {
    if (!roomCode || typeof subscribeRoom !== 'function') return;
    return subscribeRoom(roomCode, room => {
      if (!room) return;
      setTakenIds(room.ovfjTakenIds || []);
      const na = {}, nv = {};
      Object.entries(room).forEach(([key, val]) => {
        if (!val || typeof val !== 'object') return;
        if (key.startsWith('ovfjA') && val.pid && val.sess === sess && val.round === round) na[val.pid] = val;
        if (key.startsWith('ovfjV') && val.pid && val.sess === sess) {
          Object.entries(val.votes || {}).forEach(([vk, v]) => {
            if (!vk.startsWith('r' + round + '_')) return;
            if (!nv[vk]) nv[vk] = {};
            nv[vk][val.pid] = v;
          });
        }
      });
      if (Object.keys(na).length) setAnswers(prev => ({...prev, ...na}));
      if (Object.keys(nv).length) setVotes(prev => { const m = {...prev}; Object.entries(nv).forEach(([vk, per]) => { m[vk] = {...(m[vk]||{}), ...per}; }); return m; });
    });
  }, [roomCode, round]);

  // Ticker a visszaszámláláshoz
  React.useEffect(() => {
    if (!(phase === 'writing' && doneAt)) return;
    const id = setInterval(() => setTick(t => t + 1), 250);
    return () => clearInterval(id);
  }, [phase, doneAt]);

  // Sorsolás animáció vége → írás
  React.useEffect(() => {
    if (phase !== 'draw' || !drawTs) return;
    const id = setTimeout(() => setPhase('writing'), Math.max(0, drawTs + OVFJ_DRAW_MS - Date.now()));
    return () => clearTimeout(id);
  }, [phase, drawTs]);

  const publishAns = (rec) => {
    setAnswers(prev => ({...prev, [rec.pid]: rec}));
    if (roomCode && typeof syncRoom === 'function') syncRoom(roomCode, { [ovfjAKey(rec.pid)]: rec });
  };
  const makeHostRec = (done) => {
    const r = { pid: hostPid, sess, round, done, doneAt: Date.now() };
    OVFJ_CATS.forEach(c => { r[c.key] = String(localAnsRef.current[c.key]||'').trim(); });
    return r;
  };
  const hostSubmit = () => {
    if (submittedRef.current || !hostPid) return;
    submittedRef.current = true; setSubmitted(true);
    publishAns(makeHostRec(true));
  };
  const endWriting = () => {
    if (hostPid && !submittedRef.current) { submittedRef.current = true; setSubmitted(true); publishAns(makeHostRec(false)); }
    setPhase('voting');
  };

  const claimedPids = React.useMemo(() => {
    const s = new Set(takenIds || []);
    if (hostPid) s.add(hostPid);
    return s;
  }, [takenIds, hostPid]);

  // Első kész → 10 mp visszaszámlálás; mindenki kész → azonnal szavazás
  React.useEffect(() => {
    if (phase !== 'writing') return;
    const expected = pl.filter(p => claimedPids.has(p.id));
    if (expected.length > 0 && expected.every(p => answers[p.id]?.done)) { endWriting(); return; }
    if (!doneAt && Object.values(answers).some(a => a && a.done)) setDoneAt(Date.now());
  }, [answers, phase, claimedPids]);
  React.useEffect(() => {
    if (phase !== 'writing' || !doneAt) return;
    if (Date.now() >= doneAt + 10000) endWriting();
  });

  // Szavazás: host is szavaz
  const hostVote = (targetPid, catKey, v) => {
    if (!hostPid) return;
    const vk = ovfjVoteKey(round, targetPid, catKey);
    const nv = {...myVotes, [vk]: v};
    setMyVotes(nv);
    setVotes(prev => ({...prev, [vk]: {...(prev[vk]||{}), [hostPid]: v}}));
    if (roomCode && typeof syncRoom === 'function') syncRoom(roomCode, { [ovfjVKey(hostPid)]: { pid: hostPid, sess, round, votes: nv } });
  };

  // Pontszámítás: 1 pont minden érvényes szóra, ahol 👍 szigorúan több mint 👎
  const finishVoting = () => {
    if (calcRef.current) return;
    calcRef.current = true;
    const validity = ovfjBuildValidity(answers, letter, round);
    const rs = {};
    pl.forEach(p => { rs[p.id] = 0; });
    pl.filter(p => answers[p.id] && answers[p.id].round === round).forEach(p => {
      OVFJ_CATS.forEach(c => {
        const vi = validity(p.id, c.key);
        if (!vi.valid) return;
        const vm = votes[ovfjVoteKey(round, p.id, c.key)] || {};
        const vals = Object.values(vm);
        const yes = vals.filter(Boolean).length, no = vals.length - yes;
        if (yes > no) rs[p.id] += 1;
      });
    });
    setRoundScores(rs);
    const nc = {...cumScores};
    Object.entries(rs).forEach(([pid, s]) => { nc[pid] = (nc[pid]||0) + s; });
    setCumScores(nc);
    if (onResult) {
      const maxRs = Math.max(0, ...Object.values(rs));
      const drinkParts = pl.filter(p => claimedPids.has(p.id))
        .map(p => ({ p, drinks: maxRs - (rs[p.id]||0) }))
        .filter(({drinks}) => drinks > 0)
        .sort((a,b) => b.drinks - a.drinks);
      if (drinkParts.length > 0) {
        const subtitle = drinkParts.map(({p,drinks}) => `${p.name}: ${drinks} korty`).join(' · ');
        onResult({ correct: false, playerName: null, drinks: drinkParts[0].drinks, subtitle });
      } else {
        onResult({ correct: true, playerName: null, drinks: 0, subtitle: 'Mindenki ugyanannyit kapott!' });
      }
    }
    setPhase('results');
  };

  // Auto-továbblépés, ha minden szavazat beérkezett
  React.useEffect(() => {
    if (phase !== 'voting') return;
    const participants = pl.filter(p => answers[p.id] && answers[p.id].round === round);
    if (participants.length < 2) return;
    const validity = ovfjBuildValidity(answers, letter, round);
    const items = [];
    participants.forEach(p => OVFJ_CATS.forEach(c => { if (validity(p.id, c.key).valid) items.push([p.id, c.key]); }));
    if (items.length === 0) return;
    const all = items.every(([pid, ck]) => {
      const vm = votes[ovfjVoteKey(round, pid, ck)] || {};
      return participants.filter(q => q.id !== pid).every(q => vm[q.id] !== undefined);
    });
    if (all) finishVoting();
  }, [votes, answers, phase]);

  const startRound = () => {
    const nl = drawLetter();
    setLetter(nl); setDrawTs(Date.now()); setDoneAt(null); setPhase('draw');
  };
  const nextRound = () => {
    if (round >= totalRounds) { setPhase('final'); onAdvance && onAdvance({}); return; }
    calcRef.current = false;
    submittedRef.current = false;
    setSubmitted(false); setLocalAns({}); setMyVotes({});
    setAnswers({}); setVotes({}); setRoundScores({}); setDoneAt(null);
    setRound(r => r + 1);
    const nl = drawLetter();
    setLetter(nl); setDrawTs(Date.now()); setPhase('draw');
  };

  const joinUrl = roomCode ? window.location.href.split('?')[0] + '?room=' + roomCode : null;
  const remaining = (phase === 'writing' && doneAt) ? Math.max(0, Math.ceil((doneAt + 10000 - Date.now()) / 1000)) : null;
  const tallies = React.useMemo(() => {
    const t = {};
    Object.entries(votes).forEach(([vk, per]) => {
      const vals = Object.values(per || {});
      t[vk] = { yes: vals.filter(Boolean).length, no: vals.filter(x => !x).length };
    });
    return t;
  }, [votes]);

  if (!roomCode) return (
    <div style={{background:T.surface,borderRadius:18,padding:'20px 18px',boxShadow:T.shadow,fontFamily:T.font,fontSize:14,color:T.inkSoft,textAlign:'center',width:'100%'}}>
      🌍 Az Ország-Város játékhoz online szoba kell — a játékosok a telefonjukon írnak és szavaznak.
    </div>
  );

  // ── HOST: játékosválasztó (host is játszik) ──
  if (phase === 'pick') return (
    <div style={{display:'flex',flexDirection:'column',gap:10,width:'100%'}}>
      <div style={{textAlign:'center',padding:'6px 0 4px'}}>
        <div style={{fontSize:44}}>🌍</div>
        <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:20,color:T.ink,textTransform:'uppercase',letterSpacing:T.letterDisplay,marginTop:4}}>Ki vagy te?</div>
        <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft,marginTop:3}}>A host is játszik — válaszd ki magad!</div>
      </div>
      {pl.map(p => {
        const sel = hostPid === p.id;
        return (
          <button key={p.id} onClick={() => setHostPid(p.id)} style={{display:'flex',alignItems:'center',gap:12,padding:'13px 16px',borderRadius:16,border:`2px solid ${sel?(p.color||T.mint):'transparent'}`,background:sel?`${p.color||T.mint}18`:T.surface,cursor:'pointer',width:'100%',boxShadow:T.shadow,textAlign:'left'}}>
            <OVFJAvatar p={p} size={40} />
            <span style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:16,color:T.ink,flex:1}}>{p.name}</span>
            {sel && <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" fill={p.color||T.mint}/><path d="M7 13l3 3 7-7" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/></svg>}
          </button>
        );
      })}
      <PrimaryButton onClick={() => hostPid && setPhase('lobby')} disabled={!hostPid} style={{marginTop:4}}>
        {hostPid ? `Én vagyok ${pl.find(p=>p.id===hostPid)?.name}!` : 'Válassz nevet'}
      </PrimaryButton>
    </div>
  );

  // ── HOST: lobby ──
  if (phase === 'lobby') return (
    <div style={{display:'flex',flexDirection:'column',gap:12,width:'100%'}}>
      {showQR && joinUrl && <QRModal url={joinUrl} onClose={() => setShowQR(false)} />}
      <div style={{background:T.surface,borderRadius:18,padding:'16px',boxShadow:T.shadow}}>
        <div style={{display:'flex',alignItems:'center',gap:10,marginBottom:8}}>
          <span style={{fontSize:26}}>🌍</span>
          <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:17,color:T.ink,flex:1,letterSpacing:T.letterDisplay}}>Ország-Város</div>
          <span style={{fontFamily:T.font,fontSize:12,fontWeight:T.weightTitle,color:T.mint,background:T.mintSoft,padding:'4px 12px',borderRadius:999}}>{round} / {totalRounds} kör</span>
        </div>
        <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft,lineHeight:1.5}}>Betűt sorsolunk, mindenki a saját telefonján tölti ki a 8 kategóriát. Az első kész után 10 mp marad. Utána 👍/👎 szavazás — minden érvényes szó 1 pont.</div>
        <div style={{display:'flex',flexWrap:'wrap',gap:6,marginTop:10}}>
          {OVFJ_CATS.map(c => (
            <span key={c.key} style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:T.inkSoft,background:T.surfaceMuted,padding:'4px 10px',borderRadius:999}}>{c.emoji} {c.label}</span>
          ))}
        </div>
      </div>
      <button onClick={() => setShowQR(true)} style={{display:'flex',alignItems:'center',justifyContent:'center',gap:10,padding:'14px',borderRadius:18,border:`2px solid ${T.mint}`,background:T.mintSoft,color:T.mint,fontFamily:T.font,fontWeight:T.weightTitle,fontSize:15,cursor:'pointer',boxShadow:T.shadow,width:'100%'}}>
        <span style={{fontSize:20}}>📱</span> QR kód — Csatlakozás
      </button>
      <div style={{background:T.surface,borderRadius:18,padding:'14px 16px',boxShadow:T.shadow}}>
        <div style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.08em',marginBottom:10}}>Csatlakozott játékosok</div>
        <div style={{display:'flex',flexDirection:'column',gap:8}}>
          {pl.map(p => {
            const joined = claimedPids.has(p.id);
            const isHost = p.id === hostPid;
            return (
              <div key={p.id} style={{display:'flex',alignItems:'center',gap:10,opacity:joined?1:0.55}}>
                <OVFJAvatar p={p} size={30} />
                <span style={{fontFamily:T.font,fontSize:14,fontWeight:T.weightTitle,color:T.ink,flex:1}}>{p.name}{isHost?' (Te)':''}</span>
                <span style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:joined?T.mint:T.inkSoft,background:joined?T.mintSoft:T.surfaceMuted,padding:'3px 10px',borderRadius:999}}>{joined ? '✓ Kész' : 'Várakozás…'}</span>
              </div>
            );
          })}
        </div>
      </div>
      <PrimaryButton onClick={startRound}>🎰 Kezdés!</PrimaryButton>
    </div>
  );

  // ── HOST: betűsorsolás ──
  if (phase === 'draw') return (
    <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:8,width:'100%'}}>
      <div style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.12em'}}>{round}. kör / {totalRounds}</div>
      <OVFJDrawAnim letter={letter} drawTs={drawTs} />
    </div>
  );

  // ── HOST: írás (a host is játszik a saját eszközén) ──
  if (phase === 'writing') {
    const expected = pl.filter(p => claimedPids.has(p.id));
    const doneCount = expected.filter(p => answers[p.id]?.done).length;
    return (
      <OVFJWritingForm
        letter={letter}
        remaining={remaining}
        localAns={localAns}
        setLocalAns={setLocalAns}
        submitted={submitted}
        onSubmit={hostSubmit}
        doneInfo={`${doneCount}/${expected.length} játékos kész`}
      />
    );
  }

  // ── HOST: szavazás ──
  if (phase === 'voting') return (
    <div style={{display:'flex',flexDirection:'column',gap:10,width:'100%'}}>
      <OVFJVotingView letter={letter} round={round} players={pl} answers={answers} myPid={hostPid} myVotes={myVotes} onVote={hostVote} tallies={tallies} />
      <button onClick={finishVoting} style={{width:'100%',padding:'13px',borderRadius:14,border:`1.5px solid ${T.coral}`,background:'transparent',color:T.coral,fontFamily:T.font,fontWeight:T.weightTitle,fontSize:14,cursor:'pointer'}}>
        ⏹ Befejezés — eredmények
      </button>
    </div>
  );

  // ── HOST: kör eredménye ──
  if (phase === 'results') return (
    <div style={{display:'flex',flexDirection:'column',gap:10,width:'100%'}}>
      <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:18,color:T.ink,textAlign:'center',letterSpacing:T.letterDisplay}}>{round}. kör vége — „{letter}"</div>
      <OVFJStandings players={pl} roundScores={roundScores} cumScores={cumScores} myPid={hostPid} final={false} />
      <PrimaryButton onClick={nextRound} style={{marginTop:4}}>
        {round >= totalRounds ? '🏁 Végeredmény' : '🎰 Következő betű'}
      </PrimaryButton>
    </div>
  );

  // ── HOST: végeredmény ──
  return (
    <div style={{display:'flex',flexDirection:'column',gap:10,width:'100%'}}>
      <div style={{textAlign:'center',padding:'4px 0'}}>
        <div style={{fontSize:44}}>🏆</div>
        <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:20,color:T.ink,letterSpacing:T.letterDisplay,textTransform:'uppercase',marginTop:2}}>Végeredmény</div>
      </div>
      <OVFJStandings players={pl} cumScores={cumScores} myPid={hostPid} final={true} />
    </div>
  );
}

// ═══════════════ ORSZÁG-VÁROS — játékos (telefon) nézet ═══════════════
function OVFJObserverView({ room, code, myName, onLeave }) {
  const players = room.players || [];
  const ovfj = room.ovfjState || {};
  const taken = room.ovfjTakenIds || [];
  const [myPid, setMyPid] = React.useState(null);
  const [pendingId, setPendingId] = React.useState(null);
  const [localAns, setLocalAns] = React.useState({});
  const [submitted, setSubmitted] = React.useState(false);
  const [myVotes, setMyVotes] = React.useState({});
  const [, setTick] = React.useState(0);
  const lastRoundRef = React.useRef(null);
  const localAnsRef = React.useRef({});
  React.useEffect(() => { localAnsRef.current = localAns; }, [localAns]);
  const submittedRef = React.useRef(false);
  React.useEffect(() => { submittedRef.current = submitted; }, [submitted]);
  const myPidRef = React.useRef(null);
  React.useEffect(() => { myPidRef.current = myPid; }, [myPid]);

  // Hold-to-unlock (foglalt név felszabadítása) — blackjack minta
  const [unlockPressId, setUnlockPressId] = React.useState(null);
  const [unlockProgress, setUnlockProgress] = React.useState(0);
  const unlockTimerRef = React.useRef(null);
  const unlockRafRef = React.useRef(null);
  const unlockStartRef = React.useRef(null);
  const releasePlayer = React.useCallback((pid) => {
    if (!pid || !code) return;
    try { firebase.firestore().collection('rooms').doc(code).update({ ovfjTakenIds: firebase.firestore.FieldValue.arrayRemove(pid) }); } catch(e) {}
  }, [code]);
  React.useEffect(() => () => { releasePlayer(myPidRef.current); }, []);
  React.useEffect(() => () => { cancelAnimationFrame(unlockRafRef.current); clearTimeout(unlockTimerRef.current); }, []);
  const startUnlockPress = (pid) => {
    setUnlockPressId(pid); setUnlockProgress(0);
    unlockStartRef.current = Date.now();
    const tickFn = () => {
      const elapsed = Date.now() - unlockStartRef.current;
      const pct = Math.min(100, (elapsed / 2000) * 100);
      setUnlockProgress(pct);
      if (pct < 100) { unlockRafRef.current = requestAnimationFrame(tickFn); }
    };
    unlockRafRef.current = requestAnimationFrame(tickFn);
    unlockTimerRef.current = setTimeout(() => {
      setUnlockPressId(null); setUnlockProgress(0);
      releasePlayer(pid);
    }, 2000);
  };
  const cancelUnlockPress = () => {
    clearTimeout(unlockTimerRef.current);
    cancelAnimationFrame(unlockRafRef.current);
    setUnlockPressId(null); setUnlockProgress(0);
  };

  const doSync = data => { if (typeof syncRoom === 'function') syncRoom(code, data); };

  // Új kör → lokális state reset
  React.useEffect(() => {
    if (ovfj.round && lastRoundRef.current !== ovfj.round) {
      lastRoundRef.current = ovfj.round;
      setLocalAns({}); setSubmitted(false); setMyVotes({});
      submittedRef.current = false;
    }
  }, [ovfj.round]);

  // Ticker a visszaszámláláshoz
  React.useEffect(() => {
    if (!(ovfj.phase === 'writing' && ovfj.doneAt)) return;
    const id = setInterval(() => setTick(t => t + 1), 250);
    return () => clearInterval(id);
  }, [ovfj.phase, ovfj.doneAt]);

  const buildRec = (done) => {
    const r = { pid: myPid, sess: ovfj.sess, round: ovfj.round, done, doneAt: Date.now() };
    OVFJ_CATS.forEach(c => { r[c.key] = String(localAnsRef.current[c.key]||'').trim(); });
    return r;
  };
  const submitAnswers = (done) => {
    if (submittedRef.current || !myPid) return;
    submittedRef.current = true; setSubmitted(true);
    doSync({ [ovfjAKey(myPid)]: buildRec(done) });
  };

  // Auto-beadás: szavazás fázisra váltáskor (üres válasz is mehet)
  React.useEffect(() => {
    if (ovfj.phase === 'voting' && myPid && !submittedRef.current) submitAnswers(false);
  }, [ovfj.phase, myPid]);

  const remaining = (ovfj.phase === 'writing' && ovfj.doneAt) ? Math.max(0, Math.ceil((ovfj.doneAt + 10000 - Date.now()) / 1000)) : null;
  // Lejárt a 10 mp → automatikus beadás lokálisan is
  React.useEffect(() => {
    if (ovfj.phase === 'writing' && remaining === 0 && myPid && !submittedRef.current) submitAnswers(false);
  });

  const submitVote = (targetPid, catKey, v) => {
    const vk = ovfjVoteKey(ovfj.round, targetPid, catKey);
    const nv = {...myVotes, [vk]: v};
    setMyVotes(nv);
    doSync({ [ovfjVKey(myPid)]: { pid: myPid, sess: ovfj.sess, round: ovfj.round, votes: nv } });
  };

  const answers = React.useMemo(() => {
    const out = {};
    Object.entries(ovfj.answers || {}).forEach(([pid, a]) => { if (a && a.round === ovfj.round) out[pid] = a; });
    return out;
  }, [ovfj.answers, ovfj.round]);

  const pageOuter = {position:'fixed',inset:0,background:T.bg,overflowY:'auto',WebkitOverflowScrolling:'touch',zIndex:50};
  const pageInner = {padding:'12px 20px 40px',minHeight:'100%',boxSizing:'border-box',display:'flex',flexDirection:'column',gap:10};

  // ── Névválasztás (claim, hold-to-unlock) ──
  if (!myPid) {
    const confirmSelection = () => {
      if (!pendingId) return;
      setMyPid(pendingId);
      try { firebase.firestore().collection('rooms').doc(code).update({ ovfjTakenIds: firebase.firestore.FieldValue.arrayUnion(pendingId) }); } catch(e) {}
    };
    const pendingPlayer = pendingId ? players.find(p => p.id === pendingId) : null;
    return (
      <div style={pageOuter}><div style={{...pageInner,gap:8}}>
        <div style={{textAlign:'center',padding:'10px 0 6px'}}>
          <div style={{fontSize:46}}>🌍</div>
          <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:22,color:T.ink,textTransform:'uppercase',letterSpacing:T.letterDisplay,marginTop:6}}>Ki vagy te?</div>
          <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft,marginTop:4}}>Válaszd ki a neved a listából</div>
        </div>
        {players.map(p => {
          const isTaken = taken.includes(p.id) || p.id === ovfj.hostPid;
          const selected = pendingId === p.id;
          const pressing = unlockPressId === p.id;
          return (
            <div key={p.id} style={{position:'relative',borderRadius:16,overflow:'hidden'}}>
              <button
                onClick={!isTaken ? () => setPendingId(p.id) : undefined}
                onMouseDown={isTaken ? () => startUnlockPress(p.id) : undefined}
                onMouseUp={isTaken ? cancelUnlockPress : undefined}
                onMouseLeave={isTaken ? cancelUnlockPress : undefined}
                onTouchStart={isTaken ? (e) => { e.preventDefault(); startUnlockPress(p.id); } : undefined}
                onTouchEnd={isTaken ? cancelUnlockPress : undefined}
                onTouchCancel={isTaken ? cancelUnlockPress : undefined}
                style={{display:'flex',alignItems:'center',gap:12,padding:'14px 16px',background:pressing?`${T.coral}10`:selected?`${p.color||T.mint}18`:T.surface,border:`2px solid ${pressing?T.coral:selected?(p.color||T.mint):isTaken?T.coral+'30':'transparent'}`,borderRadius:16,cursor:isTaken?'default':'pointer',boxShadow:T.shadow,textAlign:'left',width:'100%',opacity:isTaken&&!pressing?0.5:1,transition:'background .15s, border-color .15s',WebkitUserSelect:'none'}}>
                <OVFJAvatar p={p} size={42} />
                <div style={{flex:1}}>
                  <div style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:16,color:T.ink}}>{p.name}</div>
                  <div style={{fontFamily:T.font,fontSize:12,color:isTaken?T.coral:T.inkSoft,marginTop:2}}>{pressing ? '🔓 Tartsd nyomva…' : isTaken ? '🔒 Foglalt' : 'Elérhető'}</div>
                </div>
                {selected && <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" fill={p.color||T.mint}/><path d="M7 13l3 3 7-7" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/></svg>}
              </button>
              {pressing && <div style={{position:'absolute',bottom:0,left:0,height:3,background:T.coral,borderRadius:999,width:`${unlockProgress}%`,transition:'none'}} />}
            </div>
          );
        })}
        <button onClick={confirmSelection} disabled={!pendingId} style={{width:'100%',padding:'15px',borderRadius:16,border:'none',background:pendingId?(pendingPlayer?.color||T.mint):T.surfaceMuted,fontFamily:T.font,fontWeight:900,fontSize:16,color:'#fff',cursor:pendingId?'pointer':'default',marginTop:4}}>
          {pendingPlayer ? `Én vagyok ${pendingPlayer.name}!` : 'Válassz nevet'}
        </button>
      </div></div>
    );
  }

  const myPlayer = players.find(p => p.id === myPid);
  const phase = ovfj.phase, letter = ovfj.letter || '';

  const Hdr = () => (
    <div style={{display:'flex',alignItems:'center',gap:10,marginBottom:4,padding:'8px 0',borderBottom:`1px solid ${T.surfaceMuted}`,flexShrink:0}}>
      <OVFJAvatar p={myPlayer} size={30} />
      <span style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:15,color:T.ink,flex:1}}>{myPlayer?.name}</span>
      <span style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:T.inkSoft,background:T.surfaceMuted,padding:'3px 9px',borderRadius:999}}>{ovfj.round||1}/{ovfj.totalRounds||'?'} kör</span>
      <button onClick={onLeave} style={{padding:'4px 10px',border:'none',background:T.coralSoft,color:T.coral,borderRadius:999,fontFamily:T.font,fontWeight:T.weightTitle,fontSize:11,cursor:'pointer',textTransform:'uppercase',letterSpacing:'0.06em',flexShrink:0}}>{t('leave')}</button>
    </div>
  );

  // ── Várakozás a kezdésre ──
  if (!phase || phase === 'pick' || phase === 'lobby') return (
    <div style={pageOuter}><div style={pageInner}>
      <Hdr />
      <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:18,padding:'40px 0'}}>
        <div style={{width:150,height:150,borderRadius:34,background:T.surfaceMuted,display:'grid',placeItems:'center',boxShadow:T.shadow}}>
          <span style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:84,color:T.inkMute,lineHeight:1}}>?</span>
        </div>
        <div style={{fontFamily:T.font,fontSize:15,fontWeight:T.weightTitle,color:T.inkSoft,textAlign:'center'}}>A betű hamarosan felfedi magát…</div>
        <div style={{display:'flex',flexWrap:'wrap',gap:6,justifyContent:'center',maxWidth:320}}>
          {OVFJ_CATS.map(c => (
            <span key={c.key} style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:T.inkSoft,background:T.surfaceMuted,padding:'4px 10px',borderRadius:999}}>{c.emoji} {c.label}</span>
          ))}
        </div>
      </div>
    </div></div>
  );

  // ── Betűsorsolás ──
  if (phase === 'draw') return (
    <div style={pageOuter}><div style={pageInner}>
      <Hdr />
      <OVFJDrawAnim letter={letter} drawTs={ovfj.drawTs} />
    </div></div>
  );

  // ── Írás ──
  if (phase === 'writing') return (
    <div style={pageOuter}><div style={pageInner}>
      <Hdr />
      <OVFJWritingForm
        letter={letter}
        remaining={remaining}
        localAns={localAns}
        setLocalAns={setLocalAns}
        submitted={submitted}
        onSubmit={() => submitAnswers(true)}
        doneInfo={null}
      />
    </div></div>
  );

  // ── Szavazás ──
  if (phase === 'voting') return (
    <div style={pageOuter}><div style={pageInner}>
      <Hdr />
      <OVFJVotingView letter={letter} round={ovfj.round} players={players} answers={answers} myPid={myPid} myVotes={myVotes} onVote={submitVote} tallies={null} />
    </div></div>
  );

  // ── Kör eredménye ──
  if (phase === 'results') {
    const cum = ovfj.cumScores || {};
    const srtd = [...players].sort((a,b)=>(cum[b.id]||0)-(cum[a.id]||0));
    const rank = srtd.findIndex(p => p.id === myPid) + 1;
    return (
      <div style={pageOuter}><div style={pageInner}>
        <Hdr />
        <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:17,color:T.ink,textAlign:'center',letterSpacing:T.letterDisplay}}>{ovfj.round}. kör vége — „{letter}"</div>
        <div style={{display:'flex',gap:8}}>
          <div style={{flex:1,background:T.mintSoft,borderRadius:18,padding:'14px',textAlign:'center'}}>
            <div style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:T.mint,textTransform:'uppercase',letterSpacing:'0.08em'}}>Ebben a körben</div>
            <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:30,color:T.mint,lineHeight:1.2}}>+{(ovfj.roundScores||{})[myPid]||0}</div>
          </div>
          <div style={{flex:1,background:T.surface,borderRadius:18,padding:'14px',textAlign:'center',boxShadow:T.shadow}}>
            <div style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.08em'}}>Összesen</div>
            <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:30,color:T.ink,lineHeight:1.2}}>{cum[myPid]||0} pt</div>
          </div>
          <div style={{flex:1,background:T.surface,borderRadius:18,padding:'14px',textAlign:'center',boxShadow:T.shadow}}>
            <div style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.08em'}}>Helyezés</div>
            <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:30,color:rank===1?T.coral:T.ink,lineHeight:1.2}}>{rank}. hely</div>
          </div>
        </div>
        <OVFJStandings players={players} roundScores={ovfj.roundScores} cumScores={cum} myPid={myPid} final={false} />
        <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,textAlign:'center'}}>A host indítja a következő betűt…</div>
      </div></div>
    );
  }

  // ── Végeredmény ──
  return (
    <div style={pageOuter}><div style={pageInner}>
      <Hdr />
      <div style={{textAlign:'center',padding:'6px 0'}}>
        <div style={{fontSize:44}}>🏆</div>
        <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:20,color:T.ink,letterSpacing:T.letterDisplay,textTransform:'uppercase',marginTop:2}}>Végeredmény</div>
      </div>
      <OVFJStandings players={players} cumScores={ovfj.cumScores} myPid={myPid} final={true} />
    </div></div>
  );
}
'''

src = src[:i0] + NEW + src[i1:]

io.open(P, 'w', encoding='utf-8').write(src)
print('OK — ovfj refactor applied, version v9.815')
