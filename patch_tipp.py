#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# A Bingó felület mód-választóssá válik: Bingó VAGY Tipp bajnokság.
#  - Tipp mód: az admin kérdéseket + opciókat állít be pontértékkel; a játékosok
#    profil alapján tippelnek (Firestore config/tippAnswers), az admin utólag
#    megjelöli a helyes választ (config/bingoConfig.questions[].correct), és
#    pontozott ranglista jön ki. A megválaszolt (feloldott) kérdés zárolódik.
#  - Home banner + AppBar cím/emoji a módhoz igazodik.
#  - Admin: mód-választó + tipp-kérdés szerkesztő (kérdés, opciók, pont, helyes válasz).
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

# ── 1) BingoScreen teljes csere ──
BS_START = 'function BingoScreen({ go }) {'
BS_END = '\n// ── Pub: saját keverés űrlap'
i1 = src.index(BS_START); i2 = src.index(BS_END, i1)

NEW_BS = r'''function BingoScreen({ go }) {
  const [profiles, setProfiles] = React.useState([]);
  const [who, setWho] = React.useState(() => { try { return localStorage.getItem('boh_bingo_who') || null; } catch(e) { return null; } });
  const [marksAll, setMarksAll] = React.useState({});
  const [tippAll, setTippAll] = React.useState({});
  const [loaded, setLoaded] = React.useState(false);
  const [celebrate, setCelebrate] = React.useState(null);
  const [confirmReset, setConfirmReset] = React.useState(false);
  const [cfg, setCfg] = React.useState(null);
  const prevBingos = React.useRef(null);
  const db = (typeof firebase !== 'undefined') ? firebase.firestore() : null;

  React.useEffect(() => {
    if (typeof window.getProfiles === 'function') window.getProfiles().then(ps => setProfiles(ps || [])).catch(() => {});
    if (!db) { setLoaded(true); return; }
    const un = db.collection('config').doc('bingo').onSnapshot(d => { setMarksAll((d && d.exists && d.data()) || {}); setLoaded(true); }, () => setLoaded(true));
    const un2 = db.collection('config').doc('bingoConfig').onSnapshot(d => setCfg((d && d.exists && d.data()) || null), () => {});
    const un3 = db.collection('config').doc('tippAnswers').onSnapshot(d => setTippAll((d && d.exists && d.data()) || {}), () => {});
    return () => { try { un(); } catch(e) {} try { un2(); } catch(e) {} try { un3(); } catch(e) {} };
  }, []);

  const mode = (cfg && cfg.mode === 'tipp') ? 'tipp' : 'bingo';
  const ITEMS = (cfg && Array.isArray(cfg.items) && cfg.items.length >= 24) ? cfg.items : BINGO_ITEMS;
  const bingoTitle = (cfg && cfg.title) ? cfg.title : 'VB Bingó';
  const tippTitle = (cfg && cfg.tippTitle) ? cfg.tippTitle : 'Tippbajnokság';
  const questions = (cfg && Array.isArray(cfg.questions)) ? cfg.questions : [];
  const headTitle = (mode === 'tipp' ? tippTitle : bingoTitle) + (mode === 'tipp' ? ' 🎯' : ' ⚽');

  const pickWho = id => { setWho(id); prevBingos.current = null; setConfirmReset(false); try { localStorage.setItem('boh_bingo_who', id || ''); } catch(e) {} };
  const whoProf = profiles.find(p => p.id === who) || null;

  // ── BINGÓ logika ──
  const card = (who && mode === 'bingo') ? bingoCardFor(who, ITEMS.length) : null;
  const myMarks = new Set(marksAll[who] || []);
  const persistMarks = arr => { if (db && who) db.collection('config').doc('bingo').set({ [who]: arr }, { merge: true }).catch(() => {}); };
  const toggle = c => {
    if (c === 12 || !who) return;
    const n = new Set(myMarks);
    if (n.has(c)) n.delete(c); else n.add(c);
    const arr = Array.from(n).sort((a, b) => a - b);
    setMarksAll(prev => ({ ...prev, [who]: arr }));
    persistMarks(arr);
  };
  const bingosOf = set => BINGO_LINES.filter(l => l.every(c => c === 12 || set.has(c))).length;
  const myBingos = (who && mode === 'bingo') ? bingosOf(myMarks) : 0;
  React.useEffect(() => {
    if (!who || !loaded || mode !== 'bingo') return;
    if (prevBingos.current === null) { prevBingos.current = myBingos; return; }
    if (myBingos > prevBingos.current) {
      setCelebrate(myBingos);
      try { if (typeof window.bohHaptic === 'function') window.bohHaptic('success'); } catch(e) {}
      try { if (typeof window.bohSound === 'function') window.bohSound('zsulli'); } catch(e) {}
    }
    prevBingos.current = myBingos;
  }, [myBingos, who, loaded, mode]);
  const bingoBoard = profiles
    .map(p => ({ p, n: (marksAll[p.id] || []).length, b: bingosOf(new Set(marksAll[p.id] || [])) }))
    .filter(x => x.n > 0)
    .sort((a, b) => (b.b - a.b) || (b.n - a.n));

  // ── TIPP logika ──
  const myTips = tippAll[who] || {};
  const anyResolved = questions.some(q => q.correct != null && q.correct !== '');
  const setTip = (qid, oi) => {
    if (!who) return;
    const q = questions.find(x => x.id === qid);
    if (q && q.correct != null && q.correct !== '') return; // feloldott kérdés zárolt
    setTippAll(prev => ({ ...prev, [who]: { ...(prev[who] || {}), [qid]: oi } }));
    if (db) db.collection('config').doc('tippAnswers').set({ [who]: { [qid]: oi } }, { merge: true }).catch(() => {});
  };
  const scoreOf = pid => {
    const tips = tippAll[pid] || {};
    let pts = 0, correct = 0, resolved = 0;
    questions.forEach(q => {
      if (q.correct == null || q.correct === '') return;
      resolved++;
      if (tips[q.id] === q.correct) { pts += (q.points || 1); correct++; }
    });
    return { pts, correct, resolved };
  };
  const myScore = who ? scoreOf(who) : { pts: 0, correct: 0, resolved: 0 };
  const answeredCount = questions.filter(q => myTips[q.id] != null).length;
  const tippBoard = Object.keys(tippAll)
    .map(pid => ({ p: profiles.find(x => x.id === pid) || { id: pid, name: '?' }, s: scoreOf(pid) }))
    .filter(x => Object.keys(tippAll[x.p.id] || {}).length > 0)
    .sort((a, b) => (b.s.pts - a.s.pts) || (b.s.correct - a.s.correct));
  const tippMedal = {};
  if (anyResolved) tippBoard.filter(x => x.s.pts > 0).slice(0, 3).forEach((x, i) => { tippMedal[x.p.id] = ['🥇','🥈','🥉'][i]; });

  const Avatar = ({ pr, size }) => (
    <div style={{ width:size, height:size, borderRadius:'50%', background:(pr && pr.color) || '#98A2B3', overflow:'hidden', display:'grid', placeItems:'center', flexShrink:0 }}>
      {pr && pr.img ? <img src={pr.img} style={{ width:'100%', height:'100%', objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:size*0.42, color:'#fff' }}>{((pr && pr.name) || '?').charAt(0).toUpperCase()}</span>}
    </div>
  );

  const pickerSub = mode === 'tipp'
    ? 'Válaszd ki magad — add le a tippjeidet a döntő eseményeire, és versenyezz a pontokért!'
    : 'Válaszd ki magad — mindenki saját kártyát kap, és X-elheti, ami a döntőben megtörténik.';

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title={headTitle} onBack={() => go('home')} right={who ? (
        <button onClick={() => pickWho(null)} style={{ border:'none', background:T.surfaceMuted, color:T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:11.5, borderRadius:999, padding:'7px 12px', cursor:'pointer' }}>Váltás</button>
      ) : null} />
      <div style={{ flex:1, overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'14px 16px max(40px, calc(env(safe-area-inset-bottom) + 24px))', maxWidth:560, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>
        {!who ? (
          <div style={{ background:T.surface, borderRadius:20, padding:'24px 18px', boxShadow:T.shadow, textAlign:'center' }}>
            <div style={{ fontSize:42, lineHeight:1, marginBottom:10 }}>{mode === 'tipp' ? '🎯' : '🏆'}</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, marginBottom:5 }}>Ki vagy?</div>
            <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkSoft, lineHeight:1.5, marginBottom:18 }}>{pickerSub}</div>
            {profiles.length ? (
              <div style={{ display:'flex', flexWrap:'wrap', gap:16, justifyContent:'center' }}>
                {profiles.map(pr => (
                  <button key={pr.id} onClick={() => pickWho(pr.id)} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:5, border:'none', background:'transparent', cursor:'pointer', padding:0, WebkitTapHighlightColor:'transparent' }}>
                    <Avatar pr={pr} size={58} />
                    <span style={{ fontFamily:T.font, fontWeight:800, fontSize:12, color:T.ink, maxWidth:70, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{pr.name}</span>
                  </button>
                ))}
              </div>
            ) : (
              <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkMute }}>Nincs profil — hozz létre egyet a Statisztika oldalon.</div>
            )}
          </div>
        ) : mode === 'tipp' ? (
          <React.Fragment>
            {/* Saját sáv */}
            <div style={{ display:'flex', alignItems:'center', gap:9, marginBottom:12 }}>
              <Avatar pr={whoProf} size={30} />
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13.5, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{(whoProf && whoProf.name) || '—'} tippjei</div>
                <div style={{ fontFamily:T.font, fontWeight:700, fontSize:10.5, color:T.inkSoft }}>{answeredCount}/{questions.length} kitöltve{myScore.resolved ? ` · ${myScore.pts} pont (${myScore.correct}/${myScore.resolved})` : ''}</div>
              </div>
            </div>
            {questions.length === 0 ? (
              <div style={{ background:T.surface, borderRadius:18, padding:'26px 18px', boxShadow:T.shadow, textAlign:'center' }}>
                <div style={{ fontSize:38, marginBottom:8 }}>🎯</div>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink, marginBottom:5 }}>Még nincs tippkérdés</div>
                <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkSoft, lineHeight:1.5 }}>Az admin a Bingó fülön tud tippkérdéseket felvenni.</div>
              </div>
            ) : (
              <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
                {questions.map((q, qi) => {
                  const resolved = q.correct != null && q.correct !== '';
                  const myPick = myTips[q.id];
                  const gotIt = resolved && myPick === q.correct;
                  return (
                    <div key={q.id} style={{ background:T.surface, borderRadius:16, padding:'13px 14px', boxShadow:T.shadow }}>
                      <div style={{ display:'flex', alignItems:'flex-start', gap:8, marginBottom:10 }}>
                        <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14.5, color:T.ink, flex:1, minWidth:0, lineHeight:1.3 }}>{qi+1}. {q.q}</span>
                        <span style={{ fontFamily:T.font, fontWeight:800, fontSize:10.5, color:T.mintDeep || T.mint, background:T.mintSoft, borderRadius:999, padding:'3px 9px', flexShrink:0 }}>{q.points || 1} pont</span>
                      </div>
                      <div style={{ display:'flex', flexDirection:'column', gap:7 }}>
                        {(q.options || []).map((opt, oi) => {
                          const sel = myPick === oi;
                          const isCorrect = resolved && q.correct === oi;
                          const selWrong = resolved && sel && !isCorrect;
                          let bg = T.bg, border = `1.5px solid ${T.border}`, col = T.ink;
                          if (isCorrect) { bg = `${T.mint}1f`; border = `2px solid ${T.mint}`; col = T.mintDeep || T.mint; }
                          else if (selWrong) { bg = `${T.coral}18`; border = `2px solid ${T.coral}`; col = T.coral; }
                          else if (sel) { bg = T.mint; border = `2px solid ${T.mint}`; col = '#fff'; }
                          return (
                            <button key={oi} onClick={resolved ? undefined : () => setTip(q.id, oi)} style={{ display:'flex', alignItems:'center', gap:8, textAlign:'left', padding:'11px 13px', borderRadius:12, border, background:bg, color:col, fontFamily:T.font, fontWeight:800, fontSize:13.5, cursor: resolved ? 'default' : 'pointer', WebkitTapHighlightColor:'transparent' }}>
                              <span style={{ flex:1, minWidth:0 }}>{opt}</span>
                              {isCorrect && <span style={{ fontSize:14 }}>✓</span>}
                              {selWrong && <span style={{ fontSize:14 }}>✗</span>}
                              {sel && !resolved && <span style={{ fontSize:12, fontWeight:900 }}>TIPPED</span>}
                            </button>
                          );
                        })}
                      </div>
                      {resolved && (
                        <div style={{ fontFamily:T.font, fontWeight:800, fontSize:11.5, color: gotIt ? (T.mintDeep || T.mint) : T.coral, marginTop:9 }}>
                          {gotIt ? `+${q.points || 1} pont — eltaláltad! ✓` : (myPick != null ? 'Nem talált 🍺' : 'Nem tippeltél')}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
            {/* Tippbajnokság állás */}
            {tippBoard.length > 0 && (
              <div style={{ background:T.surface, borderRadius:16, padding:'12px 14px', boxShadow:T.shadow, marginTop:14 }}>
                <div style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:9 }}>Tippbajnokság állás</div>
                <div style={{ display:'flex', flexDirection:'column', gap:7 }}>
                  {tippBoard.map(({ p, s }) => (
                    <div key={p.id} style={{ display:'flex', alignItems:'center', gap:8 }}>
                      <Avatar pr={p} size={22} />
                      <span style={{ fontFamily:T.font, fontWeight:800, fontSize:12.5, color:T.ink, flex:1, minWidth:0, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{tippMedal[p.id] ? tippMedal[p.id] + ' ' : ''}{p.name}{p.id === who ? ' (te)' : ''}</span>
                      {s.resolved > 0 && <span style={{ fontFamily:T.font, fontWeight:700, fontSize:10.5, color:T.inkMute }}>{s.correct}/{s.resolved}</span>}
                      <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12.5, color:T.coral }}>{s.pts} pont</span>
                    </div>
                  ))}
                </div>
                {!anyResolved && <div style={{ fontFamily:T.font, fontSize:10.5, color:T.inkMute, marginTop:8 }}>A pontok akkor jelennek meg, ahogy az admin megjelöli a helyes válaszokat.</div>}
              </div>
            )}
            {!anyResolved && questions.length > 0 && (
              <div style={{ fontFamily:T.font, fontSize:11, color:T.inkMute, textAlign:'center', marginTop:12, lineHeight:1.5 }}>Tippelj minden kérdésre — a döntő után kiderül, ki a bajnok! 🏆</div>
            )}
          </React.Fragment>
        ) : (
          <React.Fragment>
            {/* Saját sáv */}
            <div style={{ display:'flex', alignItems:'center', gap:9, marginBottom:12 }}>
              <Avatar pr={whoProf} size={30} />
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13.5, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{(whoProf && whoProf.name) || '—'} kártyája</div>
                <div style={{ fontFamily:T.font, fontWeight:700, fontSize:10.5, color:T.inkSoft }}>{myMarks.size}/24 kipipálva{myBingos ? ` · ${myBingos} bingó 🏆` : ''}</div>
              </div>
            </div>
            {/* 5×5 rács */}
            <div style={{ display:'grid', gridTemplateColumns:'repeat(5, 1fr)', gap:6 }}>
              {Array.from({ length: 25 }).map((_, c) => {
                const free = c === 12;
                const item = free ? null : ITEMS[card[c < 12 ? c : c - 1]];
                const on = free || myMarks.has(c);
                return (
                  <button key={c} data-bingo={c} onClick={() => toggle(c)} style={{ position:'relative', aspectRatio:'1', border:'none', borderRadius:12, cursor: free ? 'default' : 'pointer', background: free ? (T.yellow || '#F4C95A') : on ? T.mint : T.surface, boxShadow: on ? 'none' : T.shadow, padding:3, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:2, overflow:'hidden', WebkitTapHighlightColor:'transparent' }}>
                    <span style={{ fontSize:15, lineHeight:1, opacity: on && !free ? 0.3 : 1 }}>{free ? '🏆' : item.e}</span>
                    <span style={{ fontFamily:T.font, fontWeight:800, fontSize:7.6, lineHeight:1.12, textAlign:'center', color: free ? '#1A2A4A' : on ? 'rgba(255,255,255,0.6)' : T.ink, wordBreak:'break-word' }}>{free ? 'DÖNTŐ' : item.t}</span>
                    {on && !free && <span style={{ position:'absolute', inset:0, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:30, color:'#fff', textShadow:'0 2px 6px rgba(0,0,0,0.25)' }}>✕</span>}
                  </button>
                );
              })}
            </div>
            <div style={{ fontFamily:T.font, fontSize:11, color:T.inkMute, textAlign:'center', marginTop:10 }}>Koppints a mezőre, ha megtörtént — teljes sor, oszlop vagy átló = BINGÓ! 🍻</div>
            {/* Állás */}
            {bingoBoard.length > 0 && (
              <div style={{ background:T.surface, borderRadius:16, padding:'12px 14px', boxShadow:T.shadow, marginTop:14 }}>
                <div style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:9 }}>Állás</div>
                <div style={{ display:'flex', flexDirection:'column', gap:7 }}>
                  {bingoBoard.map(({ p, n, b }) => (
                    <div key={p.id} style={{ display:'flex', alignItems:'center', gap:8 }}>
                      <Avatar pr={p} size={22} />
                      <span style={{ fontFamily:T.font, fontWeight:800, fontSize:12.5, color:T.ink, flex:1, minWidth:0, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}{p.id === who ? ' (te)' : ''}</span>
                      {b > 0 && <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11.5, color:T.coral }}>{b}× BINGÓ 🏆</span>}
                      <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11.5, color:T.inkSoft }}>{n}/24</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {/* Újrakezdés */}
            <button onClick={() => { if (confirmReset) { setMarksAll(prev => ({ ...prev, [who]: [] })); persistMarks([]); prevBingos.current = 0; setConfirmReset(false); } else setConfirmReset(true); }} style={{ width:'100%', marginTop:14, padding:'12px 0', borderRadius:13, border:'none', background: confirmReset ? T.coral : T.surfaceMuted, color: confirmReset ? '#fff' : T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:13, cursor:'pointer' }}>{confirmReset ? 'Biztos? A kártyád törlődik!' : 'Kártya újrakezdése'}</button>
          </React.Fragment>
        )}
      </div>
      {/* BINGÓ ünneplés */}
      {celebrate && (
        <div onClick={() => setCelebrate(null)} style={{ position:'fixed', top:'calc(-1 * env(safe-area-inset-top))', left:0, right:0, bottom:'calc(-1 * env(safe-area-inset-bottom))', background:'rgba(14,14,24,0.72)', zIndex:70, display:'flex', alignItems:'center', justifyContent:'center', padding:'calc(env(safe-area-inset-top) + 24px) 24px calc(env(safe-area-inset-bottom) + 24px)', boxSizing:'border-box', animation:'fadeIn .2s' }}>
          <div onClick={e => e.stopPropagation()} style={{ background:T.surface, borderRadius:28, padding:'26px 24px 22px', width:'100%', maxWidth:340, display:'flex', flexDirection:'column', alignItems:'center', gap:10, boxShadow:'0 24px 64px rgba(0,0,0,0.3)', animation:'popIn .3s cubic-bezier(.2,.9,.3,1.3)' }}>
            <BottleHero pose="win" size={72} style={{ animation:'floatBob 2.6s ease-in-out infinite' }} />
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:30, color:T.ink, letterSpacing:'0.04em' }}>BINGÓ! 🏆</div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13.5, color:T.inkSoft, textAlign:'center' }}>{celebrate}. sorod jött össze — ezt meg kell ünnepelni! 🍻</div>
            <button onClick={() => setCelebrate(null)} style={{ marginTop:6, width:'100%', padding:'13px 0', borderRadius:14, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer' }}>Fenékig! 🍻</button>
          </div>
        </div>
      )}
    </div>
  );
}
'''

src = src[:i1] + NEW_BS + src[i2+1:]

# ── 2) AdminBingo teljes csere (mód-választó + tipp szerkesztő) ──
AB_START = 'function AdminBingo() {'
AB_END = '\nfunction AdminWildcards() {'
j1 = src.index(AB_START); j2 = src.index(AB_END, j1)

NEW_AB = r'''function AdminBingo() {
  const [enabled, setEnabled] = React.useState(true);
  const [mode, setMode] = React.useState('bingo');
  const [title, setTitle] = React.useState('VB Bingó');
  const [items, setItems] = React.useState(null);
  const [tippTitle, setTippTitle] = React.useState('Tippbajnokság');
  const [questions, setQuestions] = React.useState([]);
  const [saving, setSaving] = React.useState(false);
  const [saved, setSaved] = React.useState(false);
  const [dirty, setDirty] = React.useState(false);
  const [confirmReset, setConfirmReset] = React.useState(false);
  React.useEffect(() => {
    (window.getBingoConfig ? window.getBingoConfig() : Promise.resolve(null)).then(c => {
      setEnabled(c ? c.enabled !== false : true);
      setMode((c && c.mode === 'tipp') ? 'tipp' : 'bingo');
      setTitle((c && c.title) || 'VB Bingó');
      setTippTitle((c && c.tippTitle) || 'Tippbajnokság');
      setQuestions((c && Array.isArray(c.questions)) ? c.questions.map(q => ({ id: q.id || ('q_' + Math.random().toString(36).slice(2,8)), q: q.q || '', options: Array.isArray(q.options) ? q.options.slice() : ['',''], points: q.points || 1, correct: (q.correct == null ? null : q.correct) })) : []);
      setItems((c && Array.isArray(c.items) && c.items.length) ? c.items.map(it => ({ e: it.e || '', t: it.t || '' })) : BINGO_ITEMS.map(it => ({ e: it.e, t: it.t })));
    }).catch(() => { setItems(BINGO_ITEMS.map(it => ({ e: it.e, t: it.t }))); });
  }, []);
  const markDirty = () => { setDirty(true); setSaved(false); };

  // bingo mezők
  const updItem = (i, f, v) => { setItems(l => l.map((w, j) => j === i ? { ...w, [f]: v } : w)); markDirty(); };
  const delItem = (i) => { setItems(l => l.filter((_, j) => j !== i)); markDirty(); };
  const addItem = () => { setItems(l => [...l, { e: '⚽', t: '' }]); markDirty(); };
  // tipp kérdések
  const addQ = () => { setQuestions(l => [...l, { id: 'q_' + Date.now().toString(36) + Math.random().toString(36).slice(2,5), q: '', options: ['',''], points: 1, correct: null }]); markDirty(); };
  const updQ = (i, f, v) => { setQuestions(l => l.map((q, j) => j === i ? { ...q, [f]: v } : q)); markDirty(); };
  const delQ = (i) => { setQuestions(l => l.filter((_, j) => j !== i)); markDirty(); };
  const updOpt = (qi, oi, v) => { setQuestions(l => l.map((q, j) => j === qi ? { ...q, options: q.options.map((o, k) => k === oi ? v : o) } : q)); markDirty(); };
  const addOpt = (qi) => { setQuestions(l => l.map((q, j) => j === qi ? { ...q, options: [...q.options, ''] } : q)); markDirty(); };
  const delOpt = (qi, oi) => { setQuestions(l => l.map((q, j) => { if (j !== qi) return q; const options = q.options.filter((_, k) => k !== oi); let correct = q.correct; if (correct != null) { if (correct === oi) correct = null; else if (correct > oi) correct = correct - 1; } return { ...q, options, correct }; })); markDirty(); };
  const setCorrect = (qi, oi) => { setQuestions(l => l.map((q, j) => j === qi ? { ...q, correct: q.correct === oi ? null : oi } : q)); markDirty(); };

  const persist = (payload) => {
    setSaving(true);
    (window.setBingoConfig ? window.setBingoConfig(payload) : Promise.resolve())
      .then(() => { setSaving(false); setDirty(false); setSaved(true); setConfirmReset(false); })
      .catch(() => setSaving(false));
  };
  const buildPayload = (over) => {
    const cleanItems = (items || []).map(w => ({ e: (w.e || '').trim() || '⚽', t: (w.t || '').trim() })).filter(w => w.t);
    const cleanQ = (questions || []).map(q => {
      const opts = (q.options || []).map(o => (o || '').trim()).filter(Boolean);
      let correct = q.correct;
      if (correct != null && correct >= opts.length) correct = null;
      return { id: q.id, q: (q.q || '').trim(), options: opts, points: Math.max(1, parseInt(q.points) || 1), correct: (correct == null ? null : correct) };
    }).filter(q => q.q && q.options.length >= 2);
    return Object.assign({ enabled, mode, title: (title || '').trim() || 'VB Bingó', items: cleanItems, tippTitle: (tippTitle || '').trim() || 'Tippbajnokság', questions: cleanQ }, over || {});
  };
  const save = () => persist(buildPayload());
  const reset = () => {
    const d = BINGO_ITEMS.map(it => ({ e: it.e, t: it.t }));
    setEnabled(true); setMode('bingo'); setTitle('VB Bingó'); setItems(d); setTippTitle('Tippbajnokság'); setQuestions([]);
    persist({ enabled: true, mode: 'bingo', title: 'VB Bingó', items: d, tippTitle: 'Tippbajnokság', questions: [] });
  };

  if (items === null) return <div style={{ textAlign:'center', padding:30, fontFamily:T.font, color:T.sub }}>Betöltés…</div>;
  const validCount = items.filter(w => (w.t || '').trim()).length;
  const tooFew = validCount < 24;
  const validQ = questions.filter(q => (q.q || '').trim() && (q.options || []).filter(o => (o || '').trim()).length >= 2).length;
  const inpS = { boxSizing:'border-box', padding:'9px 11px', borderRadius:10, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:13.5, color:T.ink, outline:'none' };
  return (
    <div style={{ padding:16 }}>
      <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:10 }}>
        <span style={{ fontSize:20, lineHeight:1 }}>{mode === 'tipp' ? '🎯' : '⚽'}</span>
        <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>Bingó / Tipp bajnokság</span>
      </div>

      {/* Mód-választó */}
      <div style={{ display:'flex', gap:8, marginBottom:12 }}>
        {[['bingo','⚽ Bingó'],['tipp','🎯 Tipp bajnokság']].map(([k,l]) => (
          <button key={k} onClick={() => { setMode(k); markDirty(); }} style={{ flex:1, padding:'11px 0', borderRadius:13, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize:13.5, background: mode === k ? T.mint : T.surface, color: mode === k ? '#fff' : T.inkSoft, boxShadow: mode === k ? `0 4px 12px ${T.mint}55` : T.shadow }}>{l}</button>
        ))}
      </div>

      {/* Megjelenítés kapcsoló */}
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', background:T.surface, borderRadius:14, padding:'12px 14px', boxShadow:T.shadow, marginBottom:12 }}>
        <div>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink }}>Megjelenítés a főképernyőn</div>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>{enabled ? 'Látszik a gomb' : 'El van rejtve'}</div>
        </div>
        <Toggle on={enabled} onChange={() => { setEnabled(v => !v); markDirty(); }} />
      </div>

      {mode === 'bingo' ? (
        <React.Fragment>
          <div style={{ fontFamily:T.font, fontSize:12.5, color:T.sub, marginBottom:12 }}>A kártya 24 mezőt sorsol ki (középen fix DÖNTŐ), ezért legalább 24 mező kell — kevesebbnél a beépített lista marad érvényben. <span style={{ fontWeight:800, color: tooFew ? T.coral : T.mint }}>{validCount} mező</span></div>
          <div style={{ background:T.surface, borderRadius:14, padding:'12px 14px', boxShadow:T.shadow, marginBottom:12 }}>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:7 }}>Cím / tematika</div>
            <input value={title} onChange={e => { setTitle(e.target.value); markDirty(); }} placeholder="VB Bingó" style={{ ...inpS, width:'100%' }} />
          </div>
          {tooFew && <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.coral, background:T.coralSoft, borderRadius:10, padding:'8px 12px', marginBottom:10 }}>Legalább 24 mező kell — jelenleg {validCount}.</div>}
          <div style={{ display:'flex', flexDirection:'column', gap:7, marginBottom:12 }}>
            {items.map((w, i) => (
              <div key={i} style={{ display:'flex', gap:7, alignItems:'center', background:T.surface, borderRadius:12, padding:'7px 9px', boxShadow:T.shadow }}>
                <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.inkMute, width:20, textAlign:'center', flexShrink:0 }}>{i+1}</span>
                <input value={w.e} onChange={e => updItem(i, 'e', e.target.value)} placeholder="⚽" style={{ ...inpS, width:46, textAlign:'center', fontSize:17, padding:'8px 4px', flexShrink:0 }} />
                <input value={w.t} onChange={e => updItem(i, 't', e.target.value)} placeholder="Esemény szövege…" style={{ ...inpS, flex:1, minWidth:0, border:`1.5px solid ${(w.t||'').trim() ? T.border : T.coral}` }} />
                <button onClick={() => delItem(i)} style={{ padding:'8px 9px', borderRadius:9, border:'none', background:T.coralSoft, color:T.coral, cursor:'pointer', flexShrink:0, display:'flex', alignItems:'center' }}><BohIcon name="trash" size={13} /></button>
              </div>
            ))}
          </div>
          <button onClick={addItem} style={{ width:'100%', padding:'12px', borderRadius:14, border:`2px dashed ${T.border}`, background:'transparent', fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft, cursor:'pointer', marginBottom:14 }}>+ Új mező</button>
        </React.Fragment>
      ) : (
        <React.Fragment>
          <div style={{ fontFamily:T.font, fontSize:12.5, color:T.sub, marginBottom:12 }}>Vegyél fel tippkérdéseket opciókkal és pontértékkel. A döntő után jelöld meg a <b>helyes választ</b> (a ✓ gombbal) — ekkor a játékosok pontot kapnak, és zárolódik a kérdés. <span style={{ fontWeight:800, color: validQ ? T.mint : T.coral }}>{validQ} érvényes kérdés</span></div>
          <div style={{ background:T.surface, borderRadius:14, padding:'12px 14px', boxShadow:T.shadow, marginBottom:12 }}>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:7 }}>Bajnokság neve</div>
            <input value={tippTitle} onChange={e => { setTippTitle(e.target.value); markDirty(); }} placeholder="Tippbajnokság" style={{ ...inpS, width:'100%' }} />
          </div>
          <div style={{ display:'flex', flexDirection:'column', gap:12, marginBottom:12 }}>
            {questions.map((q, qi) => (
              <div key={q.id} style={{ background:T.surface, borderRadius:14, padding:'12px', boxShadow:T.shadow, borderLeft: (q.correct != null) ? `4px solid ${T.mint}` : '4px solid transparent' }}>
                <div style={{ display:'flex', gap:7, alignItems:'flex-start', marginBottom:9 }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:T.inkMute, marginTop:9 }}>{qi+1}.</span>
                  <textarea value={q.q} onChange={e => updQ(qi, 'q', e.target.value)} placeholder="Kérdés — pl. Ki nyeri a döntőt?" rows={2} style={{ ...inpS, flex:1, minWidth:0, resize:'vertical' }} />
                  <button onClick={() => delQ(qi)} style={{ padding:'8px 9px', borderRadius:9, border:'none', background:T.coralSoft, color:T.coral, cursor:'pointer', flexShrink:0, display:'flex', alignItems:'center', alignSelf:'flex-start', marginTop:2 }}><BohIcon name="trash" size={13} /></button>
                </div>
                <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:9 }}>
                  <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11.5, color:T.inkSoft }}>Pont:</span>
                  <input type="number" min="1" value={q.points} onChange={e => updQ(qi, 'points', Math.max(1, parseInt(e.target.value) || 1))} style={{ ...inpS, width:64 }} />
                  <div style={{ flex:1 }} />
                  <span style={{ fontFamily:T.font, fontWeight:700, fontSize:10.5, color:T.inkMute }}>✓ = helyes válasz</span>
                </div>
                <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
                  {q.options.map((opt, oi) => {
                    const isCorrect = q.correct === oi;
                    return (
                      <div key={oi} style={{ display:'flex', gap:6, alignItems:'center' }}>
                        <button onClick={() => setCorrect(qi, oi)} title="Helyes válasz" style={{ width:34, height:34, borderRadius:9, border: isCorrect ? `2px solid ${T.mint}` : `1.5px solid ${T.border}`, background: isCorrect ? T.mint : 'transparent', color: isCorrect ? '#fff' : T.inkMute, cursor:'pointer', flexShrink:0, fontFamily:T.font, fontWeight:900, fontSize:15, display:'flex', alignItems:'center', justifyContent:'center' }}>✓</button>
                        <input value={opt} onChange={e => updOpt(qi, oi, e.target.value)} placeholder={'Opció ' + (oi+1)} style={{ ...inpS, flex:1, minWidth:0 }} />
                        <button onClick={() => delOpt(qi, oi)} disabled={q.options.length <= 2} style={{ padding:'8px 9px', borderRadius:9, border:'none', background: q.options.length <= 2 ? T.surfaceMuted : T.coralSoft, color: q.options.length <= 2 ? T.inkMute : T.coral, cursor: q.options.length <= 2 ? 'default' : 'pointer', flexShrink:0, display:'flex', alignItems:'center' }}><BohIcon name="trash" size={12} /></button>
                      </div>
                    );
                  })}
                </div>
                <button onClick={() => addOpt(qi)} style={{ marginTop:8, padding:'7px 12px', borderRadius:10, border:`1.5px dashed ${T.border}`, background:'transparent', fontFamily:T.font, fontWeight:800, fontSize:12, color:T.inkSoft, cursor:'pointer' }}>+ Opció</button>
              </div>
            ))}
          </div>
          <button onClick={addQ} style={{ width:'100%', padding:'12px', borderRadius:14, border:`2px dashed ${T.border}`, background:'transparent', fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft, cursor:'pointer', marginBottom:14 }}>+ Új tippkérdés</button>
        </React.Fragment>
      )}

      <div style={{ display:'flex', gap:8, alignItems:'center' }}>
        <button onClick={() => { if (confirmReset) reset(); else setConfirmReset(true); }} disabled={saving} style={{ padding:'11px 14px', borderRadius:12, border:'none', background: confirmReset ? T.coral : T.surfaceMuted, color: confirmReset ? '#fff' : T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:13, cursor:'pointer' }}>{confirmReset ? 'Biztos? Alaphelyzet!' : 'Alaphelyzet'}</button>
        <div style={{ flex:1 }} />
        {saved && !dirty && <span style={{ fontFamily:T.font, fontWeight:800, fontSize:12, color:T.mint }}>Mentve ✓</span>}
        <button onClick={save} disabled={saving || !dirty} style={{ padding:'12px 20px', borderRadius:12, border:'none', background: dirty ? T.mint : T.mintSoft, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14, cursor: dirty ? 'pointer' : 'default', opacity: saving ? 0.6 : 1 }}>Mentés</button>
      </div>
    </div>
  );
}

'''

src = src[:j1] + NEW_AB + src[j2+1:]

# ── 3) HomeScreen: mód-érzékeny banner adatok ──
src = src.replace(
"""  const bingoOn = !bingoCfg || bingoCfg.enabled !== false;
  const bingoLabel = (bingoCfg && bingoCfg.title) ? bingoCfg.title : 'VB Bingó';""",
"""  const bingoOn = !bingoCfg || bingoCfg.enabled !== false;
  const bingoMode = (bingoCfg && bingoCfg.mode === 'tipp') ? 'tipp' : 'bingo';
  const bingoLabel = bingoMode === 'tipp'
    ? ((bingoCfg && bingoCfg.tippTitle) ? bingoCfg.tippTitle : 'Tippbajnokság')
    : ((bingoCfg && bingoCfg.title) ? bingoCfg.title : 'VB Bingó');
  const bingoEmoji = bingoMode === 'tipp' ? '🎯' : '⚽';
  const bingoSub = bingoMode === 'tipp' ? 'Tippelj a döntőre — ki lesz a bajnok?' : 'X-eld ki, ami megtörténik a döntőben!';""", 1)

# banner: emoji + subtitle mód szerint
src = src.replace(
"""              <span style={{ fontSize:26, lineHeight:1 }}>⚽</span>
              <span style={{ flex:1, minWidth:0 }}>
                <span style={{ display:'block', fontFamily:T.font, fontWeight:900, fontSize:15.5, color:'#fff' }}>{bingoLabel} 🏆</span>
                <span style={{ display:'block', fontFamily:T.font, fontWeight:700, fontSize:10.5, color:'rgba(255,255,255,0.85)', marginTop:1 }}>X-eld ki, ami megtörténik a döntőben!</span>
              </span>""",
"""              <span style={{ fontSize:26, lineHeight:1 }}>{bingoEmoji}</span>
              <span style={{ flex:1, minWidth:0 }}>
                <span style={{ display:'block', fontFamily:T.font, fontWeight:900, fontSize:15.5, color:'#fff' }}>{bingoLabel} 🏆</span>
                <span style={{ display:'block', fontFamily:T.font, fontWeight:700, fontSize:10.5, color:'rgba(255,255,255,0.85)', marginTop:1 }}>{bingoSub}</span>
              </span>""", 1)

# ── 4) Verziobump ──
assert src.count("const APP_VERSION = 'v9.991';") == 1
src = src.replace("const APP_VERSION = 'v9.991';", "const APP_VERSION = 'v9.992';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — tipp bajnokság mód applied')
