#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Tipp bajnokság refaktor: a feleletválasztós kérdés-modell helyett mérkőzés-eredmény
# tippelés (1/2/3/5 pontozás), kezdésig módosítható tipp + kezdés utáni láthatóság,
# automatikus pontszámítás a beírt végeredményből, +25 bónuszok (végső győztes,
# gólkirályt adó csapat), ranglista holtverseny-szabállyal (telitalálat → tippelt meccs),
# és a tabellán játékosra kattintva a tippjei.
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

# ── 1) Modul-szintű pontszámító helperek a BingoScreen elé ──
anchor = 'function BingoScreen({ go }) {'
helpers = r'''function tippOutcome(h, a) { return h > a ? 1 : (h < a ? -1 : 0); }
function tippMatchResolved(m) { return m && m.hs != null && m.hs !== '' && m.as != null && m.as !== ''; }
function tippHasPred(pred) { return !!(pred && pred.h != null && pred.h !== '' && pred.a != null && pred.a !== ''); }
// Normál pontozás: 5 pontos találat, 3 gólkülönbség, 2 egyik csapat gólja, 1 kimenetel, 0 rossz
function tippMatchPts(pred, m) {
  if (!tippHasPred(pred) || !tippMatchResolved(m)) return null;
  const ph = +pred.h, pa = +pred.a, ah = +m.hs, aa = +m.as;
  if (tippOutcome(ph, pa) !== tippOutcome(ah, aa)) return { pts: 0, exact: false };
  if (ph === ah && pa === aa) return { pts: 5, exact: true };
  if ((ph - pa) === (ah - aa)) return { pts: 3, exact: false };
  if (ph === ah || pa === aa) return { pts: 2, exact: false };
  return { pts: 1, exact: false };
}
const TIPP_BONUS_PTS = 25;
function tippFmtKick(iso) {
  if (!iso) return '';
  try { return new Date(iso).toLocaleString('hu-HU', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }); }
  catch (e) { return String(iso); }
}

'''
assert src.count(anchor) == 1
src = src.replace(anchor, helpers + anchor, 1)

# ── 2) BingoScreen tipp-logika csere ──
# a "// ── TIPP logika ──" blokktól (myTips ...) a "const Avatar = " előttig
t_start = '  // ── TIPP logika ──\n  const myTips = tippAll[who] || {};'
t_end = '\n  const Avatar = ({ pr, size }) => ('
i1 = src.index(t_start); i2 = src.index(t_end, i1)

NEW_TIPP_LOGIC = r'''  // ── TIPP logika (mérkőzés-eredmény tippelés) ──
  const matches = (cfg && Array.isArray(cfg.matches)) ? cfg.matches : [];
  const teams = (cfg && Array.isArray(cfg.teams)) ? cfg.teams : [];
  const bonusWinner = (cfg && cfg.bonusWinner) || { enabled: false };
  const bonusScorer = (cfg && cfg.bonusScorer) || { enabled: false };
  const [now, setNow] = React.useState(() => Date.now());
  const [detailPid, setDetailPid] = React.useState(null);
  React.useEffect(() => { const iv = setInterval(() => setNow(Date.now()), 20000); return () => clearInterval(iv); }, []);
  const myTip = tippAll[who] || {};
  const matchStarted = m => !!(m.kickoff && now >= new Date(m.kickoff).getTime());
  const bonusLocked = bn => !!((bn.deadline && now >= new Date(bn.deadline).getTime()) || (bn.correct));

  // ── Kódos szerkesztés-védelem (e-mailes) ──
  const requireCode = !!(cfg && cfg.tippRequireCode);
  const mailUrl = (cfg && cfg.tippMailUrl) || '';
  const authRec = who ? tippAuth[who] : null;
  const storedCode = who ? (() => { try { return localStorage.getItem('boh_tipp_code_' + who) || ''; } catch(e) { return ''; } })() : '';
  const unlocked = !requireCode || !!(authRec && authRec.code && storedCode && storedCode.toUpperCase() === String(authRec.code).toUpperCase());
  const genCode = () => { let s = ''; const A = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; for (let i = 0; i < 6; i++) s += A[Math.floor(Math.random() * A.length)]; return s; };
  const sendCodeMail = (to, code) => {
    if (!mailUrl) return Promise.resolve();
    const payload = { to, name: (whoProf && whoProf.name) || '', code, title: tippTitle };
    return fetch(mailUrl, { method: 'POST', mode: 'no-cors', body: JSON.stringify(payload) }).catch(() => {});
  };
  const requestCode = () => {
    const email = gateEmail.trim();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { setGateErr('Adj meg egy érvényes e-mail címet.'); return; }
    if (!mailUrl) { setGateErr('Az e-mail küldés még nincs beállítva (admin).'); return; }
    setGateErr(''); setGateSending(true);
    const code = (authRec && authRec.code) ? authRec.code : genCode();
    const rec = { email, code, at: Date.now() };
    if (db && (!whoProf || whoProf.email !== email)) db.collection('profiles').doc(who).set({ email }, { merge: true }).catch(() => {});
    const done = () => { setGateSending(false); setGateSent(true); };
    if (db) db.collection('config').doc('tippAuth').set({ [who]: rec }, { merge: true }).then(() => sendCodeMail(email, code)).then(done).catch(() => { sendCodeMail(email, code).finally(done); });
    else { sendCodeMail(email, code).finally(done); }
  };
  const submitCode = () => {
    const c = gateCode.trim().toUpperCase();
    if (!authRec || !authRec.code) { setGateErr('Előbb kérj kódot e-mailben.'); return; }
    if (c !== String(authRec.code).toUpperCase()) { setGateErr('Hibás kód.'); return; }
    try { localStorage.setItem('boh_tipp_code_' + who, c); } catch(e) {}
    setGateErr(''); setGateCode(''); setUnlockTick(t => t + 1);
  };
  React.useEffect(() => {
    const em = (authRec && authRec.email) || (whoProf && whoProf.email) || '';
    if (em && !gateEmail) setGateEmail(em);
  }, [who, whoProf && whoProf.email, authRec && authRec.email]);

  const canEdit = who && (!requireCode || unlocked);
  const writeTip = next => {
    setTippAll(prev => ({ ...prev, [who]: next }));
    if (db) db.collection('config').doc('tippAnswers').set({ [who]: next }, { merge: true }).catch(() => {});
  };
  const setScore = (matchId, side, val) => {
    const m = matches.find(x => x.id === matchId);
    if (!canEdit || !m || matchStarted(m)) return; // kezdés után zárolt
    const cur = { ...((myTip.m || {})[matchId] || {}) };
    cur[side] = (val === '' || val == null) ? null : Math.max(0, Math.min(99, parseInt(val) || 0));
    const mObj = { ...(myTip.m || {}), [matchId]: cur };
    writeTip({ ...myTip, m: mObj });
  };
  const setBonus = (kind, team) => {
    const bn = kind === 'winner' ? bonusWinner : bonusScorer;
    if (!canEdit || !bn.enabled || bonusLocked(bn)) return;
    writeTip({ ...myTip, [kind]: (myTip[kind] === team ? null : team) });
  };

  const scoreOf = pid => {
    const t = tippAll[pid] || {};
    const mm = t.m || {};
    let pts = 0, tele = 0, tipped = 0;
    matches.forEach(m => {
      const pred = mm[m.id];
      if (tippHasPred(pred)) tipped++;
      const r = tippMatchPts(pred, m);
      if (r) { pts += r.pts; if (r.exact) tele++; }
    });
    if (bonusWinner.enabled && bonusWinner.correct && t.winner === bonusWinner.correct) pts += TIPP_BONUS_PTS;
    if (bonusScorer.enabled && bonusScorer.correct && t.scorer === bonusScorer.correct) pts += TIPP_BONUS_PTS;
    return { pts, tele, tipped };
  };
  const myScore = who ? scoreOf(who) : { pts: 0, tele: 0, tipped: 0 };
  const anyResolved = matches.some(tippMatchResolved) || !!bonusWinner.correct || !!bonusScorer.correct;
  const standings = profiles
    .map(p => ({ p, s: scoreOf(p.id) }))
    .filter(x => !!tippAll[x.p.id])
    .sort((a, b) => (b.s.pts - a.s.pts) || (b.s.tele - a.s.tele) || (b.s.tipped - a.s.tipped));
  const tippMedal = {};
  if (anyResolved) standings.slice(0, 3).forEach((x, i) => { if (x.s.pts > 0) tippMedal[x.p.id] = ['🥇','🥈','🥉'][i]; });
'''

src = src[:i1] + NEW_TIPP_LOGIC + src[i2:]

# ── 3) BingoScreen tipp-render csere ──
r_start = '        ) : mode === \'tipp\' ? (\n          <React.Fragment>'
# a tipp render vége: a bingo branch kezdete
r_end = '        ) : (\n          <React.Fragment>\n            {/* Saját sáv */}\n            <div style={{ display:\'flex\', alignItems:\'center\', gap:9, marginBottom:12 }}>\n              <Avatar pr={whoProf} size={30} />\n              <div style={{ flex:1, minWidth:0 }}>\n                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13.5, color:T.ink, overflow:\'hidden\', textOverflow:\'ellipsis\', whiteSpace:\'nowrap\' }}>{(whoProf && whoProf.name) || \'—\'} kártyája</div>'
j1 = src.index(r_start); j2 = src.index(r_end, j1)

# a kódgate JSX-et változatlanul újrahasznosítjuk — kiemeljük a meglévőből
GATE_JSX = r'''            {requireCode && !unlocked && (
              <div style={{ background:T.surface, borderRadius:16, padding:'14px', boxShadow:T.shadow, marginBottom:12, border:`1.5px solid ${T.coral}44` }}>
                <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:6 }}>
                  <span style={{ fontSize:18, lineHeight:1 }}>🔒</span>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>Kód kell a szerkesztéshez</span>
                </div>
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, lineHeight:1.5, marginBottom:11 }}>Add meg az e-mail címed — küldünk egy egyedi kódot, amivel csak te tudod szerkeszteni a tippjeidet.</div>
                {gateSent && (
                  <div style={{ fontFamily:T.font, fontWeight:800, fontSize:12, color:T.mintDeep || T.mint, background:T.mintSoft, borderRadius:10, padding:'9px 11px', marginBottom:10 }}>✉️ Elküldtük a kódot ide: {gateEmail || (authRec && authRec.email) || ''}. Nézd meg a postafiókod (a Spam mappát is)!</div>
                )}
                <div style={{ display:'flex', gap:7, marginBottom:9 }}>
                  <input value={gateEmail} onChange={e => { setGateEmail(e.target.value); setGateErr(''); }} placeholder="pl. te@email.hu" type="email" style={{ flex:1, minWidth:0, boxSizing:'border-box', padding:'11px 12px', borderRadius:11, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none' }} />
                  <button onClick={requestCode} disabled={gateSending} style={{ padding:'11px 14px', borderRadius:11, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:13, cursor:'pointer', flexShrink:0, opacity: gateSending ? 0.6 : 1 }}>{gateSending ? '…' : (authRec ? 'Újraküldés' : 'Kód kérése')}</button>
                </div>
                <div style={{ display:'flex', alignItems:'center', gap:8, margin:'4px 0 9px' }}>
                  <div style={{ flex:1, height:1, background:T.border }} />
                  <span style={{ fontFamily:T.font, fontWeight:700, fontSize:10.5, color:T.inkMute }}>Már van kódod?</span>
                  <div style={{ flex:1, height:1, background:T.border }} />
                </div>
                <div style={{ display:'flex', gap:7 }}>
                  <input value={gateCode} onChange={e => { setGateCode(e.target.value); setGateErr(''); }} placeholder="6 jegyű kód" maxLength={8} style={{ flex:1, minWidth:0, boxSizing:'border-box', padding:'11px 12px', borderRadius:11, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:15, fontWeight:800, letterSpacing:'0.14em', textTransform:'uppercase', color:T.ink, outline:'none' }} />
                  <button onClick={submitCode} style={{ padding:'11px 18px', borderRadius:11, border:'none', background:T.ink, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:13, cursor:'pointer', flexShrink:0 }}>Feloldás</button>
                </div>
                {gateErr && <div style={{ fontFamily:T.font, fontWeight:700, fontSize:11.5, color:T.coral, marginTop:8 }}>{gateErr}</div>}
              </div>
            )}'''

NEW_TIPP_RENDER = r'''        ) : mode === 'tipp' ? (
          <React.Fragment>
            {/* Saját sáv */}
            <div style={{ display:'flex', alignItems:'center', gap:9, marginBottom:12 }}>
              <Avatar pr={whoProf} size={30} />
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13.5, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{(whoProf && whoProf.name) || '—'} tippjei</div>
                <div style={{ fontFamily:T.font, fontWeight:700, fontSize:10.5, color:T.inkSoft }}>{myScore.tipped}/{matches.length} tippelve · {myScore.pts} pont{myScore.tele ? ` · ${myScore.tele}× telitalálat 🎯` : ''}{requireCode && (unlocked ? ' · 🔓' : ' · 🔒')}</div>
              </div>
            </div>
''' + GATE_JSX + r'''
            {/* Plusz pontok — végső győztes / gólkirály csapat */}
            {(bonusWinner.enabled || bonusScorer.enabled) && (
              <div style={{ background:T.surface, borderRadius:16, padding:'13px 14px', boxShadow:T.shadow, marginBottom:12 }}>
                <div style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:9 }}>Plusz pontok · +{TIPP_BONUS_PTS} / találat</div>
                {[['winner','🏆 Végső győztes', bonusWinner],['scorer','⚽ Gólkirályt adó csapat', bonusScorer]].filter(([k,l,bn]) => bn.enabled).map(([k,l,bn]) => {
                  const locked = bonusLocked(bn);
                  const myPick = myTip[k] || null;
                  const opts = (bn.teams && bn.teams.length) ? bn.teams : teams;
                  return (
                    <div key={k} style={{ marginBottom:6 }}>
                      <div style={{ display:'flex', alignItems:'center', gap:6, marginBottom:6 }}>
                        <span style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.ink }}>{l}</span>
                        {locked && bn.correct && <span style={{ fontFamily:T.font, fontWeight:800, fontSize:10.5, color:T.mintDeep || T.mint }}>helyes: {bn.correct}</span>}
                      </div>
                      <div style={{ display:'flex', flexWrap:'wrap', gap:6 }}>
                        {opts.map(tm => {
                          const sel = myPick === tm;
                          const isCorrect = locked && bn.correct === tm;
                          const selWrong = locked && sel && bn.correct && !isCorrect;
                          let bg = T.bg, border = `1.5px solid ${T.border}`, col = T.ink;
                          if (isCorrect) { bg = `${T.mint}1f`; border = `2px solid ${T.mint}`; col = T.mintDeep || T.mint; }
                          else if (selWrong) { bg = `${T.coral}18`; border = `2px solid ${T.coral}`; col = T.coral; }
                          else if (sel) { bg = T.mint; border = `2px solid ${T.mint}`; col = '#fff'; }
                          return <button key={tm} onClick={locked ? undefined : () => setBonus(k, tm)} disabled={!canEdit && !locked} style={{ padding:'8px 12px', borderRadius:999, border, background:bg, color:col, fontFamily:T.font, fontWeight:800, fontSize:12.5, cursor: locked ? 'default' : 'pointer' }}>{tm}{sel && !locked ? ' ✓' : ''}{isCorrect ? ' ✓' : ''}</button>;
                        })}
                        {opts.length === 0 && <span style={{ fontFamily:T.font, fontSize:11.5, color:T.inkMute }}>Az admin még nem adott meg csapatokat.</span>}
                      </div>
                      {locked && !bn.correct && <div style={{ fontFamily:T.font, fontSize:10.5, color:T.inkMute, marginTop:5 }}>Lezárva — a torna végén derül ki.</div>}
                    </div>
                  );
                })}
              </div>
            )}
            {/* Mérkőzések */}
            {matches.length === 0 ? (
              <div style={{ background:T.surface, borderRadius:18, padding:'26px 18px', boxShadow:T.shadow, textAlign:'center' }}>
                <div style={{ fontSize:38, marginBottom:8 }}>🎯</div>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink, marginBottom:5 }}>Még nincs mérkőzés</div>
                <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkSoft, lineHeight:1.5 }}>Az admin a Bingó fülön (Tipp mód) tud mérkőzéseket felvenni.</div>
              </div>
            ) : (
              <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
                {matches.map((m, mi) => {
                  const started = matchStarted(m);
                  const resolved = tippMatchResolved(m);
                  const pred = (myTip.m || {})[m.id] || {};
                  const myPts = tippMatchPts(pred, m);
                  const editable = canEdit && !started;
                  return (
                    <div key={m.id} style={{ background:T.surface, borderRadius:16, padding:'13px 14px', boxShadow:T.shadow, borderLeft: myPts && myPts.exact ? `4px solid ${T.mint}` : '4px solid transparent' }}>
                      <div style={{ display:'flex', alignItems:'center', gap:6, marginBottom:3 }}>
                        <span style={{ fontFamily:T.font, fontWeight:700, fontSize:10.5, color:T.inkMute }}>{tippFmtKick(m.kickoff)}</span>
                        {m.knockout && <span style={{ fontFamily:T.font, fontWeight:800, fontSize:9.5, color:T.coral, background:T.coralSoft, borderRadius:999, padding:'1px 7px' }}>kieséses</span>}
                        <div style={{ flex:1 }} />
                        {!started ? <span style={{ fontFamily:T.font, fontWeight:700, fontSize:10, color:T.mintDeep || T.mint }}>nyitva</span> : <span style={{ fontFamily:T.font, fontWeight:700, fontSize:10, color:T.inkMute }}>🔒 lezárva</span>}
                      </div>
                      <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                        <span style={{ flex:1, textAlign:'right', fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink, minWidth:0, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{m.home}</span>
                        {editable ? (
                          <div style={{ display:'flex', alignItems:'center', gap:4, flexShrink:0 }}>
                            <input value={pred.h != null ? pred.h : ''} onChange={e => setScore(m.id, 'h', e.target.value)} inputMode="numeric" style={{ width:38, textAlign:'center', boxSizing:'border-box', padding:'7px 2px', borderRadius:9, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink, outline:'none' }} />
                            <span style={{ fontFamily:T.font, fontWeight:900, color:T.inkMute }}>:</span>
                            <input value={pred.a != null ? pred.a : ''} onChange={e => setScore(m.id, 'a', e.target.value)} inputMode="numeric" style={{ width:38, textAlign:'center', boxSizing:'border-box', padding:'7px 2px', borderRadius:9, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink, outline:'none' }} />
                          </div>
                        ) : (
                          <div style={{ display:'flex', alignItems:'center', gap:6, flexShrink:0, background:T.bg, borderRadius:9, padding:'5px 12px' }}>
                            <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color: tippHasPred(pred) ? T.ink : T.inkMute }}>{tippHasPred(pred) ? `${pred.h} : ${pred.a}` : '– : –'}</span>
                          </div>
                        )}
                        <span style={{ flex:1, textAlign:'left', fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink, minWidth:0, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{m.away}</span>
                      </div>
                      {resolved && (
                        <div style={{ display:'flex', alignItems:'center', gap:8, marginTop:8, paddingTop:8, borderTop:`1px solid ${T.inkMute}1f` }}>
                          <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11.5, color:T.inkSoft }}>Végeredmény: <b style={{ color:T.ink }}>{m.hs} : {m.as}</b></span>
                          <div style={{ flex:1 }} />
                          {myPts ? <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color: myPts.pts > 0 ? (T.mintDeep || T.mint) : T.coral }}>{myPts.exact ? 'Telitalálat! ' : ''}+{myPts.pts} pont</span> : <span style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:T.inkMute }}>nem tippeltél</span>}
                        </div>
                      )}
                      {started && (() => {
                        const others = standings.filter(x => x.p.id !== who && tippHasPred((tippAll[x.p.id] || {}).m ? (tippAll[x.p.id].m || {})[m.id] : null));
                        if (!others.length) return null;
                        return (
                          <div style={{ marginTop:8, paddingTop:8, borderTop:`1px solid ${T.inkMute}1f`, display:'flex', flexDirection:'column', gap:5 }}>
                            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:10, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.05em' }}>A többiek tippjei</div>
                            {others.map(x => { const pr2 = (tippAll[x.p.id].m || {})[m.id]; const rp = tippMatchPts(pr2, m); return (
                              <div key={x.p.id} style={{ display:'flex', alignItems:'center', gap:7 }}>
                                <Avatar pr={x.p} size={18} />
                                <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.ink, flex:1, minWidth:0, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{x.p.name}</span>
                                <span style={{ fontFamily:T.font, fontWeight:800, fontSize:12.5, color:T.inkSoft }}>{pr2.h} : {pr2.a}</span>
                                {rp && <span style={{ fontFamily:T.font, fontWeight:800, fontSize:10.5, color: rp.pts>0?(T.mintDeep||T.mint):T.inkMute }}>+{rp.pts}</span>}
                              </div>
                            ); })}
                          </div>
                        );
                      })()}
                    </div>
                  );
                })}
              </div>
            )}
            <div style={{ fontFamily:T.font, fontSize:10.5, color:T.inkMute, textAlign:'center', marginTop:10, lineHeight:1.5 }}>Pontozás: 5 = pontos eredmény · 3 = gólkülönbség · 2 = egyik csapat gólja · 1 = kimenetel. Kezdésig módosíthatsz; a többiek tippjei kezdés után látszanak.</div>
            {/* Tabella */}
            {standings.length > 0 && (
              <div style={{ background:T.surface, borderRadius:16, padding:'12px 14px', boxShadow:T.shadow, marginTop:14 }}>
                <div style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:9 }}>Tabella · koppints valakire a tippjeiért</div>
                <div style={{ display:'flex', flexDirection:'column', gap:4 }}>
                  {standings.map(({ p, s }, i) => (
                    <button key={p.id} onClick={() => setDetailPid(p.id)} style={{ display:'flex', alignItems:'center', gap:8, border:'none', background: p.id === who ? T.mintSoft : 'transparent', borderRadius:10, padding:'6px 8px', cursor:'pointer', textAlign:'left', WebkitTapHighlightColor:'transparent' }}>
                      <span style={{ fontFamily:T.font, fontWeight:800, fontSize:12, color:T.inkMute, width:18, textAlign:'center', flexShrink:0 }}>{tippMedal[p.id] || (i+1)}</span>
                      <Avatar pr={p} size={22} />
                      <span style={{ fontFamily:T.font, fontWeight:800, fontSize:12.5, color:T.ink, flex:1, minWidth:0, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}{p.id === who ? ' (te)' : ''}</span>
                      {s.tele > 0 && <span style={{ fontFamily:T.font, fontWeight:700, fontSize:10, color:T.inkMute }}>{s.tele}🎯</span>}
                      <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12.5, color:T.coral }}>{s.pts}</span>
                    </button>
                  ))}
                </div>
                <div style={{ fontFamily:T.font, fontSize:10, color:T.inkMute, marginTop:8 }}>Holtversenynél a telitalálatok, majd a tippelt meccsek száma dönt.</div>
              </div>
            )}
'''

src = src[:j1] + NEW_TIPP_RENDER + src[j2:]

# ── 4) Játékos-részletek overlay a BINGÓ ünneplés elé ──
cele_anchor = '      {/* BINGÓ ünneplés */}'
DETAIL_OVERLAY = r'''      {/* Tabella — játékos tippjei */}
      {detailPid && (() => {
        const dp = profiles.find(x => x.id === detailPid) || { id: detailPid, name: '?' };
        const dt = tippAll[detailPid] || {};
        const ds = scoreOf(detailPid);
        const mine = detailPid === who;
        return (
          <div onClick={() => setDetailPid(null)} style={{ position:'fixed', top:'calc(-1 * env(safe-area-inset-top))', left:0, right:0, bottom:'calc(-1 * env(safe-area-inset-bottom))', background:'rgba(14,14,24,0.72)', zIndex:70, display:'flex', alignItems:'center', justifyContent:'center', padding:'calc(env(safe-area-inset-top) + 20px) 20px calc(env(safe-area-inset-bottom) + 20px)', boxSizing:'border-box', animation:'fadeIn .2s' }}>
            <div onClick={e => e.stopPropagation()} style={{ background:T.bg, borderRadius:24, padding:'18px', width:'100%', maxWidth:420, maxHeight:'86vh', overflowY:'auto', WebkitOverflowScrolling:'touch', boxSizing:'border-box', animation:'popIn .25s cubic-bezier(.2,.9,.3,1.2)' }}>
              <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:12 }}>
                <Avatar pr={dp} size={38} />
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink }}>{dp.name}{mine ? ' (te)' : ''}</div>
                  <div style={{ fontFamily:T.font, fontWeight:700, fontSize:11.5, color:T.inkSoft }}>{ds.pts} pont · {ds.tele}× telitalálat · {ds.tipped} tipp</div>
                </div>
                <button onClick={() => setDetailPid(null)} style={{ border:'none', background:T.surfaceMuted, color:T.inkSoft, width:32, height:32, borderRadius:'50%', cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize:14, flexShrink:0 }}>✕</button>
              </div>
              {(bonusWinner.enabled || bonusScorer.enabled) && (
                <div style={{ background:T.surface, borderRadius:12, padding:'10px 12px', boxShadow:T.shadow, marginBottom:10, display:'flex', flexDirection:'column', gap:5 }}>
                  {[['winner','🏆 Végső győztes', bonusWinner],['scorer','⚽ Gólkirály-csapat', bonusScorer]].filter(([k,l,bn]) => bn.enabled).map(([k,l,bn]) => {
                    const locked = bonusLocked(bn);
                    const show = mine || locked;
                    const pick = dt[k];
                    const ok = bn.correct && pick === bn.correct;
                    return <div key={k} style={{ display:'flex', alignItems:'center', gap:6, fontFamily:T.font, fontSize:12 }}>
                      <span style={{ fontWeight:800, color:T.inkSoft }}>{l}:</span>
                      <span style={{ fontWeight:800, color: bn.correct ? (ok ? (T.mintDeep||T.mint) : T.coral) : T.ink }}>{show ? (pick || '—') : '🔒'}</span>
                      {locked && bn.correct && <span style={{ fontWeight:700, fontSize:10.5, color: ok ? (T.mintDeep||T.mint) : T.inkMute }}>{ok ? `+${TIPP_BONUS_PTS}` : ''}</span>}
                    </div>;
                  })}
                </div>
              )}
              <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
                {matches.map(m => {
                  const started = matchStarted(m);
                  const show = mine || started;
                  const pred = (dt.m || {})[m.id];
                  const rp = tippMatchPts(pred, m);
                  return (
                    <div key={m.id} style={{ display:'flex', alignItems:'center', gap:8, background:T.surface, borderRadius:11, padding:'8px 11px', boxShadow:T.shadow }}>
                      <span style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:700, fontSize:12, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{m.home} – {m.away}</span>
                      <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color: show ? (tippHasPred(pred) ? T.ink : T.inkMute) : T.inkMute }}>{show ? (tippHasPred(pred) ? `${pred.h}:${pred.a}` : '–:–') : '🔒'}</span>
                      {tippMatchResolved(m) && <span style={{ fontFamily:T.font, fontWeight:700, fontSize:10.5, color:T.inkMute }}>({m.hs}:{m.as})</span>}
                      {show && rp && <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color: rp.pts>0?(T.mintDeep||T.mint):T.inkMute, minWidth:26, textAlign:'right' }}>+{rp.pts}</span>}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        );
      })()}
      {/* BINGÓ ünneplés */}'''
assert src.count(cele_anchor) == 1
src = src.replace(cele_anchor, DETAIL_OVERLAY, 1)

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — tipp match model (BingoScreen) applied')
