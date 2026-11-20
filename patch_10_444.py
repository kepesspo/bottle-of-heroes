# v10.444 — Gender Reveal Szülők: a jóváhagyott design (négy fül, egy fül = egy képernyő),
# a DNR téma színeivel. Azonnali mentés, közös kártya/sor/kapcsoló/szegmens elemek.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:120]); s = s.replace(old, new)
def cut(start, end):
    """kivágja [start, end) szakaszt (end-et megtartja)"""
    global s
    a = s.index(start); b = s.index(end, a)
    s = s[:a] + s[b:]

rep("const APP_VERSION = 'v10.443'", "const APP_VERSION = 'v10.444'")

# ── régi szülői komponensek ki ──
cut("function RevealVideoCard() {", "function revealCtlWrite(patch) {")
cut("// A vetítő MINDEN beállítása (v10.438): a Szülők nézetben, a szülői kód mögött.\nfunction RevealProjectorPanel() {", "function RevealProjector({ title, cfg, onExit }) {")
cut("function RevealQuizControl() {", "function RevealOperator({ onBack }) {")
cut("function RevealTrigger({ onBack }) {", "// v10.443: két fül (Kép / Üzenet).")

NEW = r'''// ═══ Szülők nézet (v10.444): NÉGY FÜL — egy fül = egy telefon-képernyő ════════════════
// A jóváhagyott design (Gender Reveal – Szülők design). Felül MINDIG az állapot-sáv
// (időpont · engedély · vetítő/kvíz), alul a fül-sáv: Leleplezés · Vetítő · Kvíz · Esemény.
// ⚠️ A színek a DNR TÉMÁBÓL jönnek (T.bg háttér, T.surface kártya, T.border vonal,
// T.mint akció) — csak az állapot-tónusok (RV_TONES) és a leleplezés sötét kártyája fixek,
// mert azok jelentést hordoznak (zöld = kész, borostyán = teendő), ami nem lehet témafüggő.
// ⚠️ Nincs „Mentés" gomb: minden azonnal ment, és mellette „Mentve" villan fel.
// Az építőelemek FÜGGVÉNYEK (rvRow, rvSwitch, rvSeg, rvPill…), nem JSX-komponensek
// (v10.335 — renderenként új azonosság újramountolna).
const RV_TONES = { ok:['#E2F3EC', '#1F6B50', '#2E9E62'], warn:['#FFF1D6', '#7A4F00', '#E0A020'], info:['#EEF4FB', '#2F63A8', '#4F86C6'], bad:['#FBE7E4', '#A3342C', '#C8453B'], pink:['#FCEAF1', '#A8325E', '#F496B4'] };
function rvIcon(n, sz) {
  const p = { width: sz || 16, height: sz || 16, viewBox:'0 0 24 24', fill:'none', stroke:'currentColor', strokeWidth:2.4, strokeLinecap:'round', strokeLinejoin:'round', 'aria-hidden':'true', style:{ display:'block', flexShrink:0 } };
  switch (n) {
    case 'lock': return <svg {...p}><rect x="5" y="11" width="14" height="10" rx="2" /><path d="M8 11V8a4 4 0 0 1 8 0v3" /></svg>;
    case 'cal': return <svg {...p}><rect x="4" y="5" width="16" height="16" rx="2" /><path d="M8 3v4M16 3v4M4 10h16" /></svg>;
    case 'timer': return <svg {...p}><circle cx="12" cy="13" r="8" /><path d="M12 9v4M9 2h6" /></svg>;
    case 'video': return <svg {...p}><rect x="3" y="6" width="13" height="12" rx="2" /><path d="M16 10l5-3v10l-5-3" /></svg>;
    case 'star': return <svg {...p}><path d="M12 3l2.5 5 5.5.8-4 3.9.9 5.5L12 15.6 7.1 18.2 8 12.7 4 8.8 9.5 8z" /></svg>;
    case 'screen': return <svg {...p}><rect x="3" y="4" width="18" height="12" rx="2" /><path d="M8 20h8M12 16v4" /></svg>;
    case 'quiz': return <svg {...p}><circle cx="12" cy="12" r="9" /><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6v.6M12 17h.01" /></svg>;
    case 'list': return <svg {...p}><path d="M4 7h16M4 12h16M4 17h10" /></svg>;
    case 'chev': return <svg {...p}><path d="M9 6l6 6-6 6" /></svg>;
    case 'prev': return <svg {...p}><path d="M15 6l-6 6 6 6" /></svg>;
    case 'qr': return <svg {...p}><rect x="4" y="4" width="6" height="6" rx="1" /><rect x="14" y="4" width="6" height="6" rx="1" /><rect x="4" y="14" width="6" height="6" rx="1" /><path d="M14 14h2v2h-2zM18 18h2v2h-2zM14 18h2" /></svg>;
    case 'gallery': return <svg {...p}><rect x="3" y="5" width="18" height="14" rx="2" /><circle cx="9" cy="10" r="2" /><path d="M21 16l-5-5-8 8" /></svg>;
    case 'download': return <svg {...p}><path d="M12 4v11M7 10l5 5 5-5M5 20h14" /></svg>;
    case 'check': return <svg {...p}><path d="M5 12l5 5 9-10" /></svg>;
    case 'pause': return <svg {...p} fill="currentColor" stroke="none"><rect x="6" y="5" width="4" height="14" rx="1" /><rect x="14" y="5" width="4" height="14" rx="1" /></svg>;
    case 'play': return <svg {...p} fill="currentColor" stroke="none"><path d="M7 5l12 7-12 7z" /></svg>;
    default: return null;
  }
}
function rvCard(extra) { return Object.assign({ width:'100%', background:T.surface, borderRadius:20, border:`1px solid ${T.border}`, boxSizing:'border-box', overflow:'hidden', flexShrink:0 }, extra || {}); }
function rvH(t, right) {
  return <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', gap:10, padding:'12px 16px 8px' }}>
    <h2 style={{ margin:0, fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{t}</h2>{right || null}</div>;
}
function rvNote(t, extra) { return <div style={Object.assign({ fontFamily:T.font, fontSize:12, fontWeight:700, color:T.inkSoft, lineHeight:1.45 }, extra || {})}>{t}</div>; }
function rvInp(extra) { return Object.assign({ width:'100%', boxSizing:'border-box', padding:'0 14px', height:48, borderRadius:12, border:`1.5px solid ${T.border}`, background:T.surface, fontFamily:T.font, fontSize:15, fontWeight:700, color:T.ink, outline:'none' }, extra || {}); }
function rvBtn(kind, extra) {
  const base = { fontFamily:T.font, cursor:'pointer', display:'inline-flex', alignItems:'center', justifyContent:'center', gap:8, boxSizing:'border-box' };
  const k = kind === 'primary' ? { height:56, borderRadius:16, border:'none', background:T.mint, color:'#fff', fontSize:17, fontWeight:900 }
    : kind === 'ghost' ? { height:44, borderRadius:14, border:'none', background:'transparent', color:T.inkSoft, fontSize:14, fontWeight:800 }
    : kind === 'danger' ? { height:44, borderRadius:12, border:'1.5px solid #D9776E', background:T.surface, color:'#A3342C', fontSize:14, fontWeight:900 }
    : kind === 'small' ? { height:36, padding:'0 12px', borderRadius:10, border:`1.5px solid ${T.border}`, background:T.surface, color:T.ink, fontSize:13, fontWeight:800, flexShrink:0 }
    : { height:44, borderRadius:14, border:`1.5px solid ${T.border}`, background:T.surface, color:T.ink, fontSize:14, fontWeight:800 };
  return Object.assign(base, k, extra || {});
}
function rvMsg(m, data) { return m ? <span {...{ [data]: '' }} style={{ display:'inline-flex', alignItems:'center', gap:4, fontFamily:T.font, fontWeight:800, fontSize:12, color:'#1F6B50', whiteSpace:'nowrap' }}>{/^Mentve|^Feltöltve|kész|törölve|kimásolva|letöltve/.test(m) && rvIcon('check', 14)}{m}</span> : null; }
function rvPill(text, tone, data, icon) {
  const c = RV_TONES[tone];
  return <span {...(data || {})} style={{ display:'inline-flex', alignItems:'center', gap:6, height:28, padding:'0 10px', borderRadius:999, flexShrink:0, whiteSpace:'nowrap', fontFamily:T.font, fontWeight:800, fontSize:12,
    background: c ? c[0] : T.surface, color: c ? c[1] : T.ink, border: c ? 'none' : `1px solid ${T.border}`, boxSizing:'border-box' }}>
    {icon ? rvIcon(icon, 14) : c ? <span style={{ width:8, height:8, borderRadius:'50%', background:c[2] }} /> : null}{text}</span>;
}
function rvIconBox(n, tone) { const c = RV_TONES[tone] || RV_TONES.ok; return <span style={{ width:30, height:30, flexShrink:0, borderRadius:10, background:c[0], color:c[1], display:'grid', placeItems:'center' }}>{rvIcon(n)}</span>; }
// egy sor: bal oldalt (ikon +) név, jobb oldalt érték / kapcsoló / szegmens. Ha `onClick`
// van, az egész sor gomb (nyíllal) — ilyenkor a `right` NEM tartalmazhat gombot.
function rvRow(o) {
  const st = { width:'100%', minHeight:52, display:'flex', alignItems:'center', gap:12, padding: o.tight ? '0 12px 0 16px' : '0 16px', border:'none', borderTop: o.first ? 'none' : `1px solid ${T.border}`,
    background:'transparent', fontFamily:T.font, textAlign:'left', color:T.ink, boxSizing:'border-box' };
  const body = <React.Fragment>
    {o.icon ? rvIconBox(o.icon, o.tone) : null}
    <span style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink, lineHeight:1.25 }}>{o.label}</span>
    {o.right || null}
    {o.onClick ? <span style={{ color:T.inkMute || T.inkSoft, display:'flex' }}>{rvIcon('chev')}</span> : null}
  </React.Fragment>;
  return o.onClick ? <button type="button" onClick={o.onClick} style={Object.assign(st, { cursor:'pointer' })} {...(o.data || {})}>{body}</button>
    : <div style={st} {...(o.data || {})}>{body}</div>;
}
function rvSwitch(on, onToggle, label, data) {
  return <button type="button" role="switch" aria-checked={!!on} aria-label={label} onClick={onToggle} {...(data || {})}
    style={{ width:48, height:28, flexShrink:0, borderRadius:999, border:'none', padding:0, cursor:'pointer', position:'relative', background: on ? T.mint : (T.surfaceMuted || T.border), transition:'background .2s' }}>
    <span style={{ position:'absolute', top:3, left: on ? 23 : 3, width:22, height:22, borderRadius:'50%', background:'#fff', boxShadow:'0 1px 3px rgba(0,0,0,0.2)', transition:'left .2s' }} /></button>;
}
function rvSeg(opts, value, onPick, attr, label) {
  return <div role="radiogroup" aria-label={label} style={{ display:'flex', gap:2, padding:3, borderRadius:12, background:T.bgSoft || T.bg, flexShrink:0 }}>
    {opts.map(o => { const on = value === o.v; return <button key={String(o.v)} type="button" role="radio" aria-checked={on} aria-pressed={on} {...{ [attr]: o.v }} onClick={() => onPick(o.v)}
      style={{ minWidth:50, height:34, padding:'0 10px', border:'none', borderRadius:9, cursor:'pointer', fontFamily:T.font, fontSize:13, fontWeight: on ? 900 : 800,
        background: on ? T.surface : 'transparent', color: on ? T.ink : T.inkSoft, boxShadow: on ? '0 1px 3px rgba(0,0,0,0.12)' : 'none' }}>{o.t}</button>; })}
  </div>;
}
function revealToLocalInput(ms) { if (!ms) return ''; const d = new Date(+ms), p2 = n => String(n).padStart(2, '0'); return d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate()) + 'T' + p2(d.getHours()) + ':' + p2(d.getMinutes()); }
function useRevealFlash() { const [m, setM] = React.useState(''); return [m, t => { setM(t); setTimeout(() => setM(''), 2500); }]; }

// ── állapot-sáv (minden fülön ugyanaz) ──
function RevealParentStatus() {
  const cfg = useRevealCfg(), rs = useRevealDoc('revealState'), qd = useRevealDoc('revealQuizState'), ctl = useRevealDoc('revealProjector');
  const at = +((cfg.v || {}).revealAt || 0), st = rs.v || {}, q = qd.v || {}, paused = !!(ctl.v || {}).paused;
  const done = st.phase === 'reveal' && !st.test, armed = st.phase === 'armed';
  return (
    <div data-reveal-pstatus style={{ flexShrink:0, display:'flex', gap:6, padding:'10px 16px', overflowX:'auto', scrollbarWidth:'none' }}>
      {rvPill(at ? revealFmtWhen(at) : 'Nincs időpont', null, null, 'timer')}
      {done ? rvPill('Leleplezve', 'ok') : armed ? rvPill('Engedélyezve', 'ok') : rvPill('Engedélyre vár', 'warn')}
      {q.phase && q.phase !== 'idle' ? rvPill('Kvíz megy', 'info') : paused ? rvPill('Vetítő szünetel', 'warn') : rvPill('Képfolyam megy', 'ok')}
    </div>
  );
}
const REVEAL_PTABS = [['reveal', 'Leleplezés', 'star'], ['proj', 'Vetítő', 'screen'], ['quiz', 'Kvíz', 'quiz'], ['event', 'Esemény', 'list']];
function RevealParentTabs({ tab, onTab }) {
  return (
    <nav aria-label="Szülők fülek" data-reveal-ptabs style={{ flexShrink:0, display:'grid', gridTemplateColumns:'repeat(4, minmax(0, 1fr))', background:T.surface, borderTop:`1px solid ${T.border}`, padding:'4px 6px calc(4px + env(safe-area-inset-bottom))' }}>
      {REVEAL_PTABS.map(([id, label, ic]) => { const on = tab === id; return (
        <button key={id} type="button" data-reveal-ptab={id} aria-current={on ? 'page' : undefined} onClick={() => onTab(id)}
          style={{ minHeight:58, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:4, border:'none', background:'transparent', cursor:'pointer', fontFamily:T.font, fontSize:11, fontWeight: on ? 900 : 800, color: on ? T.mint : T.inkSoft }}>
          <span style={{ width:52, height:30, borderRadius:999, display:'grid', placeItems:'center', background: on ? (T.mintSoft || T.bgSoft) : 'transparent' }}>{rvIcon(ic, 20)}</span>{label}</button>); })}
    </nav>
  );
}

// ── 1. fül: Leleplezés ──
function RevealParentRevealTab() {
  const secret = useRevealDoc('revealSecret');
  const rstate = useRevealDoc('revealState');
  const cfg = useRevealCfg();
  const [ask, setAsk] = React.useState(null);          // null | 'now' | 'arm'
  const [msg, setMsg] = React.useState('');
  const [now, setNow] = React.useState(() => Date.now());
  const [editWhen, setEditWhen] = React.useState(false);
  const [cfgMsg, flashCfg] = useRevealFlash();
  React.useEffect(() => { const iv = setInterval(() => setNow(Date.now()), 1000); return () => clearInterval(iv); }, []);
  const sec = secret.v || {};
  const ready = !!(REVEAL_RESULTS[sec.result] && sec.result !== 'test');
  const st = rstate.v || {};
  const done = st.phase === 'reveal' && !st.test;
  const armed = st.phase === 'armed';
  const v = cfg.v || {};
  const revealAt = +(v.revealAt || 0);
  const future = revealAt > now;
  const cdOn = v.countdownOn !== false;
  const db = revealDb();
  const flash = m => { setMsg(m); setTimeout(() => setMsg(''), 4000); };
  const write = (d, m) => { if (!db) return; db.collection('config').doc('revealState').set(d).then(() => flash(m)).catch(e => setMsg('Nem sikerült (' + ((e && e.code) || 'hiba') + ')')); setAsk(null); };
  const fire = test => {
    if (!test && !ready) return;
    write({ phase:'reveal', run: revealToken(), test: !!test, result: test ? 'test' : sec.result, videoUrl: test ? '' : (sec.videoUrl || ''), at: Date.now() }, test ? 'Próba elindítva a vetítőn' : 'Elindult a leleplezés!');
  };
  const arm = () => { if (ready) write({ phase:'armed', run: revealToken(), at: Date.now() }, 'Engedélyezve — a vetítő az időpontra magától indul'); };
  const disarm = () => write({ phase:'idle', run: revealToken(), at: Date.now() }, 'Engedély visszavonva');
  const saveCfg = patch => { if (db) db.collection('config').doc('revealConfig').set(patch, { merge:true }).then(() => flashCfg('Mentve')).catch(e => flashCfg('Nem sikerült (' + ((e && e.code) || 'hiba') + ')')); };
  const onWhen = val => { const at = val ? Date.parse(val) : 0; if (val && !isFinite(at)) return; saveCfg({ revealAt: at || 0 }); };
  // a nagy visszaszámláló
  const left = Math.max(0, Math.ceil((revealAt - now) / 1000));
  const d = Math.floor(left / 86400), h = Math.floor(left % 86400 / 3600), m = Math.floor(left % 3600 / 60), x = left % 60, p2 = n => String(n).padStart(2, '0');
  const parts = d > 0 ? [[d, 'nap'], [p2(h), 'óra'], [p2(m), 'perc']] : [[p2(h), 'óra'], [p2(m), 'perc'], [p2(x), 'mp']];
  const big = t => <div style={{ position:'relative', fontFamily:T.font, fontWeight:900, fontSize:34, lineHeight:1.05, marginTop:8 }}>{t}</div>;
  return (
    <React.Fragment>
      <section data-reveal-phero style={{ position:'relative', overflow:'hidden', borderRadius:20, padding:'16px 18px', background:REVEAL_NIGHT, color:'#fff', flexShrink:0 }}>
        <div aria-hidden="true" style={{ position:'absolute', right:-30, top:-30, width:120, height:120, borderRadius:'50%', background:REVEAL_PINK, opacity:0.35 }} />
        <div aria-hidden="true" style={{ position:'absolute', right:40, bottom:-50, width:110, height:110, borderRadius:'50%', background:REVEAL_BLUE, opacity:0.3 }} />
        <div style={{ position:'relative', fontFamily:T.font, fontSize:11, fontWeight:900, letterSpacing:'0.16em', opacity:0.75 }}>{done ? 'KIDERÜLT' : 'A NAGY PILLANATIG'}</div>
        {done ? big('Leleplezve!') : future ? (
          <div data-reveal-pcount style={{ position:'relative', display:'flex', alignItems:'flex-end', gap:12, marginTop:8 }}>
            {parts.map(([n, u], i) => (
              <React.Fragment key={u}>
                {i > 0 && <span style={{ fontFamily:T.font, fontSize:30, fontWeight:900, opacity:0.5, paddingBottom:18 }}>:</span>}
                <div style={{ display:'flex', flexDirection:'column', alignItems:'center' }}>
                  <span style={{ fontFamily:T.font, fontSize:42, fontWeight:900, lineHeight:1, fontVariantNumeric:'tabular-nums' }}>{n}</span>
                  <span style={{ fontFamily:T.font, fontSize:11, fontWeight:800, opacity:0.7, marginTop:4 }}>{u}</span>
                </div>
              </React.Fragment>
            ))}
          </div>
        ) : big(revealAt ? (armed ? 'Most indul!' : 'Elérkezett az idő') : 'Nincs időpont')}
        <div style={{ position:'relative', fontFamily:T.font, fontSize:13, fontWeight:700, opacity:0.85, marginTop:10, lineHeight:1.4 }}>
          {done ? 'A vetítőn újra lejátszhatjátok.' : armed ? 'Engedélyezve — a vetítő az időpontra magától indul.' : 'Az eredményt ti sem látjátok — a vetítő mutatja meg mindenkinek egyszerre.'}
        </div>
      </section>

      <section data-reveal-p-schedule style={rvCard()}>
        {rvH('Előkészületek', rvMsg(cfgMsg, 'data-reveal-p-schedmsg'))}
        {rvRow({ first:true, icon:'lock', tone: ready ? 'ok' : 'bad', label:'Eredmény (admin)', right: rvPill(ready ? 'Beállítva' : 'Hiányzik', ready ? 'ok' : 'bad', ready ? null : { 'data-reveal-notready':'' }) })}
        {rvRow({ icon:'cal', tone: revealAt ? 'ok' : 'warn', label:'Időpont', onClick: () => setEditWhen(e => !e), data:{ 'data-reveal-p-whenrow':'' },
          right: <span {...(revealAt ? { 'data-reveal-when':'' } : {})} style={{ fontFamily:T.font, fontSize:14, fontWeight:700, color:T.inkSoft, whiteSpace:'nowrap' }}>{revealAt ? revealFmtWhen(revealAt) : 'Nincs'}</span> })}
        {editWhen && (
          <div style={{ display:'flex', gap:8, alignItems:'center', padding:'0 16px 12px' }}>
            <input data-reveal-p-when type="datetime-local" aria-label="A leleplezés időpontja" defaultValue={revealToLocalInput(revealAt)} onChange={e => onWhen(e.target.value)} style={rvInp({ flex:1, minWidth:0 })} />
            {revealAt > 0 && <button type="button" onClick={() => { saveCfg({ revealAt:0 }); setEditWhen(false); }} style={rvBtn('small')}>Törlés</button>}
          </div>
        )}
        {rvRow({ icon:'timer', tone:'ok', label:'Visszaszámláló a vetítőn', right: rvSwitch(cdOn, () => saveCfg({ countdownOn: !cdOn }), 'Visszaszámláló a vetítőn', { 'data-reveal-p-countdown':'' }) })}
        <RevealVideoRow />
      </section>

      <div style={{ flex:1, minHeight:4 }} />
      <div data-reveal-firepanel data-armed={armed ? '1' : '0'} style={{ display:'flex', flexDirection:'column', gap:8, flexShrink:0 }}>
        {!done && future && !armed && <button type="button" data-reveal-arm disabled={!ready} onClick={() => setAsk('arm')} style={rvBtn('primary', ready ? null : { opacity:0.45, cursor:'default' })}>Engedélyezem a leleplezést</button>}
        {(done || !future) && <button type="button" data-reveal-fire disabled={!ready} onClick={() => setAsk('now')} style={rvBtn('primary', ready ? null : { opacity:0.45, cursor:'default' })}>{done ? 'Leleplezés újra' : 'Leleplezés indítása'}</button>}
        <div style={{ display:'flex', gap:8 }}>
          {!done && armed && <button type="button" data-reveal-disarm onClick={disarm} style={rvBtn('secondary', { flex:1 })}>Engedély visszavonása</button>}
          {!done && future && <button type="button" data-reveal-fire disabled={!ready} onClick={() => setAsk('now')} style={rvBtn('secondary', { flex:1, color: ready ? T.ink : T.inkMute })}>Leleplezés most</button>}
          <button type="button" data-reveal-test onClick={() => fire(true)} style={rvBtn('secondary', { flex:1 })}>Próba</button>
        </div>
        {msg && <div data-reveal-firemsg role="status" style={{ textAlign:'center', fontFamily:T.font, fontWeight:800, fontSize:13, color:'#1F6B50' }}>{msg}</div>}
      </div>
      {ask && (
        <ActionModal kicker={ask === 'arm' ? 'Engedélyezed?' : 'Indulhat?'} onClose={() => setAsk(null)} onSecondary={() => setAsk(null)} secondaryLabel="Még ne"
          onPrimary={() => ask === 'arm' ? arm() : fire(false)} primaryLabel={ask === 'arm' ? 'Engedélyezem' : 'Indulhat!'} primaryColor={T.mint}>
          {ask === 'arm' ? 'A vetítő ' + revealFmtWhen(revealAt) + '-kor magától elindítja a leleplezést. 🎉' : 'A vetítőn most elindul a visszaszámlálás. Mindenki nézzen oda! 🎉'}
        </ActionModal>
      )}
    </React.Fragment>
  );
}
// a leleplező videó sora (feltöltés / csere / törlés). Előnézet SZÁNDÉKOSAN nincs.
function RevealVideoRow() {
  const meta = useRevealDoc('revealVideo');
  const m = meta.v || {};
  const [prog, setProg] = React.useState(null);      // { done, n }
  const [msg, flash] = useRevealFlash();
  const [ask, setAsk] = React.useState(false);
  const ref = React.useRef(null);
  const busy = !!prog || !!m.uploading;
  const pick = f => {
    if (!f) return;
    setProg({ done:0, n:1 });
    revealUploadVideo(f, (done, n) => setProg({ done, n }))
      .then(() => { setProg(null); flash('Feltöltve'); })
      .catch(e => { setProg(null); flash((e && e.message) || 'A feltöltés nem sikerült'); });
  };
  const status = prog ? `Feltöltés… ${prog.done} / ${prog.n}` : m.uploading ? 'Feltöltés folyamatban…' : m.vid ? `${m.name || 'videó'} · ${(m.size / 1048576).toFixed(1)} MB` : `Nincs — max. ${Math.round(REVEAL_VIDEO_MAX / 1048576)} MB, a visszaszámlálás után megy`;
  return (
    <div data-reveal-p-video data-has={m.vid ? '1' : '0'} style={{ display:'flex', alignItems:'center', gap:12, padding:'10px 12px 10px 16px', borderTop:`1px solid ${T.border}` }}>
      {rvIconBox('video', m.vid ? 'ok' : 'warn')}
      <div style={{ flex:1, minWidth:0 }}>
        <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink }}>Leleplező videó</div>
        <div data-reveal-p-videostatus style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>{msg ? <React.Fragment>{rvMsg(msg, 'data-reveal-p-videomsg')}{m.vid && !busy ? ' · ' + status : ''}</React.Fragment> : status}</div>
      </div>
      <button type="button" data-reveal-p-videopick disabled={busy} onClick={() => ref.current && ref.current.click()} style={rvBtn('small', busy ? { opacity:0.5, cursor:'default' } : null)}>{m.vid ? 'Csere' : 'Feltöltés'}</button>
      {m.vid && !busy && <button type="button" data-reveal-p-videodel onClick={() => setAsk(true)} style={rvBtn('small', { color:'#A3342C', borderColor:'#E8B4AE' })}>Törlés</button>}
      <input ref={ref} data-reveal-p-videoinput type="file" accept="video/*" style={{ display:'none' }} onChange={e => { pick(e.target.files && e.target.files[0]); e.target.value = ''; }} />
      {ask && (
        <ActionModal kicker="Videó törlése" onClose={() => setAsk(false)} onSecondary={() => setAsk(false)} secondaryLabel="Mégse"
          onPrimary={() => { setAsk(false); revealDeleteVideo().then(() => flash('Videó törölve')).catch(() => {}); }} primaryLabel="Törlés" primaryColor={T.coral}>
          A leleplezéskor nem lesz videó (csak az admin linkje, ha van).
        </ActionModal>
      )}
    </div>
  );
}

// ── 2. fül: Vetítő (a vetítő MINDEN beállítása — v10.438 óta csak itt) ──
function RevealProjectorPanel() {
  const ctl = useRevealDoc('revealProjector');
  const { list: photos } = useRevealPhotos(false);
  const v = ctl.v || {};
  const secs = REVEAL_SECS.includes(+v.secs) ? +v.secs : 5;
  const slots = REVEAL_SLOT_OPTS.includes(+v.slots) ? +v.slots : 3;
  const paused = !!v.paused;
  const qr = v.qr !== false;
  const [msg, flash] = useRevealFlash();
  const t = revealVoteTally(photos), tot = t.boy + t.girl;
  const nPhoto = photos.filter(x => x.src).length, nWish = photos.filter(x => x.kind === 'wish').length;
  const pol = (l, tp, w, h, r, c) => <div style={{ position:'absolute', left:l, top:tp, width:w, height:h, background:'#fff', boxShadow:'0 4px 12px rgba(60,40,20,0.16)', transform:`rotate(${r}deg)`, padding:'5px 5px 18px', boxSizing:'border-box' }}><div style={{ width:'100%', height:'100%', background:c }} /></div>;
  return (
    <div data-reveal-parentctl style={{ display:'flex', flexDirection:'column', gap:12 }}>
      <section style={rvCard({ padding:12 })}>
        <div aria-hidden="true" style={{ position:'relative', height:124, borderRadius:14, overflow:'hidden', background:REVEAL_PAPER, border:'1px solid #F4EBDF' }}>
          <div style={{ position:'absolute', left:-18, top:-18, width:64, height:64, borderRadius:'50%', background:REVEAL_PINK, opacity:0.45 }} />
          <div style={{ position:'absolute', right:-14, top:-10, width:56, height:56, borderRadius:'50%', background:REVEAL_BLUE, opacity:0.55 }} />
          {pol('12%', 18, '23%', 88, -5, '#C9B8A6')}{pol('38%', 12, '25%', 96, 3, '#9FB7C9')}{pol('65%', 20, '22%', 86, -2, '#D9B7A0')}
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:8, marginTop:10 }}>
          <span style={{ width:8, height:8, borderRadius:'50%', background: paused ? '#E0A020' : '#2E9E62' }} />
          <span style={{ flex:1, fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>{paused ? 'Szünetel' : 'Most a vetítőn'}</span>
          <span data-reveal-ctl-count style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkSoft }}>{nPhoto} kép · {nWish} üzenet</span>
        </div>
      </section>
      <div style={{ display:'flex', gap:8 }}>
        <button type="button" data-reveal-ctl-pause onClick={() => revealCtlWrite({ paused: !paused })} style={rvBtn('secondary', { flex:1, height:56, borderRadius:16, fontSize:16, fontWeight:900, background: paused ? (T.mintSoft || T.surface) : T.surface })}>{rvIcon(paused ? 'play' : 'pause', 18)}{paused ? 'Folytatás' : 'Szünet'}</button>
        <button type="button" data-reveal-ctl-next onClick={() => { revealCtlWrite({ next: revealToken() }); flash('Következő kép'); }} style={rvBtn('primary', { flex:1.5, fontSize:16 })}>Következő kép{rvIcon('chev', 18)}</button>
      </div>
      <section style={rvCard()}>
        {rvRow({ first:true, tight:true, label:'Képváltás', right: rvSeg(REVEAL_SECS.map(n => ({ v:n, t:n + ' mp' })), secs, n => revealCtlWrite({ secs:n }), 'data-reveal-ctl-secs', 'Képváltás') })}
        {rvRow({ tight:true, label:'Polaroidok egyszerre', right: rvSeg(REVEAL_SLOT_OPTS.map(n => ({ v:n, t:String(n) })), slots, n => revealCtlWrite({ slots:n }), 'data-reveal-ctl-slots', 'Polaroidok egyszerre') })}
        {rvRow({ label:'Vendég QR-kód a vetítőn', right: rvSwitch(qr, () => revealCtlWrite({ qr: !qr }), 'Vendég QR-kód a vetítőn', { 'data-reveal-ctl-qr': qr ? '1' : '0' }) })}
      </section>
      {tot > 0 && (
        <section style={rvCard({ padding:'12px 16px 14px' })}>
          <div style={{ display:'flex', alignItems:'baseline', justifyContent:'space-between' }}>
            <h2 style={{ margin:0, fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>Tippek állása</h2>
            <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft }}>{tot} tipp</span>
          </div>
          <div aria-hidden="true" style={{ display:'flex', height:14, borderRadius:999, overflow:'hidden', marginTop:10, background:T.bgSoft }}>
            <div style={{ flex: t.boy, background:REVEAL_BLUE }} /><div style={{ flex: t.girl, background:REVEAL_PINK }} />
          </div>
          <div data-reveal-ctl-tally style={{ display:'flex', justifyContent:'space-between', marginTop:8, fontFamily:T.font, fontSize:13, fontWeight:900 }}>
            <span style={{ color:'#2F63A8' }}>{REVEAL_RESULTS.boy.name} {t.boy}</span><span aria-hidden="true" style={{ opacity:0.3 }}>·</span><span style={{ color:'#A8325E' }}>{t.girl} {REVEAL_RESULTS.girl.name}</span>
          </div>
        </section>
      )}
      {msg && <div data-reveal-ctl-msg style={{ textAlign:'center' }}>{rvMsg(msg, 'data-reveal-ctl-msgtext')}</div>}
    </div>
  );
}

// ── 3. fül: Babakvíz (a lapozó + az ugró-rács MINDIG kint) ──
function RevealQuizControl() {
  const quiz = useRevealDoc('revealQuiz');
  const qdoc = useRevealDoc('revealQuizState');
  const st = qdoc.v || { phase:'idle' };
  const active = !!(st.phase && st.phase !== 'idle');
  const qs = revealQuizQuestions(quiz.v);
  const step = dir => revealQuizWrite(revealQuizStep(st, dir, qs));
  const n = active ? (st.qs || []).length : qs.length, pos = active ? revealQuizPos(st) : -1;
  const solSide = st.phase === 'solcover' || st.phase === 'sol' || st.phase === 'end';
  const [sec, setSec] = React.useState(solSide ? 'sol' : 'q');
  React.useEffect(() => { setSec(solSide ? 'sol' : 'q'); }, [solSide]);
  const [editOpen, setEditOpen] = React.useState(false);
  const cur = active && (st.phase === 'q' || st.phase === 'sol') && st.qs && st.qs[st.idx || 0];
  const where = !active ? `${qs.length} kérdés · papíron` : st.phase === 'cover' ? 'Borító' : st.phase === 'solcover' ? 'Megoldások borító' : st.phase === 'end' ? 'Pontozás'
    : `${st.phase === 'sol' ? 'Megoldás' : 'Kérdés'} ${(st.idx || 0) + 1} / ${n}`;
  const jump = p => revealQuizWrite(revealQuizGoto(st, p, qs));
  const chip = (p, label, wide) => { const on = pos === p, past = active && p < pos;
    return <button key={p} type="button" data-reveal-quiz-jump={p} aria-pressed={on} onClick={() => jump(p)}
      style={{ gridColumn: wide ? 'span 2' : 'auto', height:44, borderRadius:12, cursor:'pointer', fontFamily:T.font, fontSize: wide ? 13 : 14, fontWeight: on ? 900 : 800,
        border: on || past ? 'none' : `1.5px solid ${T.border}`, background: on ? T.mint : past ? (T.bgSoft || T.bg) : T.surface, color: on ? '#fff' : past ? T.inkSoft : T.ink }}>{label}</button>; };
  const base = sec === 'q' ? 0 : 1 + n;
  const sol = st.phase === 'sol';
  return (
    <div data-reveal-quizctl={st.phase || 'idle'} style={{ display:'flex', flexDirection:'column', gap:12, flex:1 }}>
      <section style={rvCard({ padding:'14px 16px' })}>
        <div style={{ display:'flex', alignItems:'center', gap:8 }}>
          {rvPill(active ? 'A VETÍTŐN' : 'NEM FUT', active ? 'info' : null)}
          <span style={{ flex:1 }} />
          <span data-reveal-quiz-where style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft }}>{where}</span>
        </div>
        {cur ? (
          <React.Fragment>
            <p style={{ margin:'10px 0 10px', fontFamily:T.font, fontSize:16, fontWeight:900, lineHeight:1.35, color:T.ink }}>{cur.q}</p>
            <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
              {cur.opts.map((o, i) => { const good = sol && i === cur.ok; return (
                <div key={i} style={{ display:'flex', alignItems:'center', gap:10, fontFamily:T.font, fontSize:13, fontWeight: good ? 900 : 700, color:T.ink, opacity: sol && !good ? 0.45 : 1 }}>
                  <span style={{ width:24, height:24, flexShrink:0, borderRadius:'50%', display:'grid', placeItems:'center', fontWeight:900, fontSize:12, color: good ? '#fff' : REVEAL_INK, background: good ? '#2E9E62' : REVEAL_QUIZ_COLORS[i % 3] }}>{'ABC'[i]}</span>{o}
                </div>); })}
            </div>
          </React.Fragment>
        ) : (
          <div style={{ marginTop:10 }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink }}>{!active ? 'Babakvíz' : st.phase === 'cover' ? 'Babakvíz — borító' : st.phase === 'solcover' ? 'Megoldások — borító' : 'Pontozás'}</div>
            {rvNote(!active ? 'Indítsd el, és lapozz innen — a vetítő követi. Papíron karikáznak (A/B/C).' : st.phase === 'end' ? 'A vetítőn a pontsávok: számoljátok össze a jó válaszokat.' : 'A vetítőn a borító látszik.', { marginTop:4 })}
          </div>
        )}
      </section>
      <div style={{ display:'flex', gap:8 }}>
        {active && <button type="button" data-reveal-quiz-prev aria-label="Előző oldal" disabled={st.phase === 'cover'} onClick={() => step(-1)} style={rvBtn('secondary', { width:64, height:56, borderRadius:16, opacity: st.phase === 'cover' ? 0.4 : 1 })}>{rvIcon('prev', 22)}</button>}
        <button type="button" data-reveal-quiz-next onClick={() => step(1)} style={rvBtn('primary', { flex:1, fontSize:16 })}>{revealQuizNextLabel(st)}</button>
      </div>
      <section data-reveal-quiz-jumps style={rvCard({ padding:'12px 12px 14px' })}>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', gap:8, padding:'0 4px' }}>
          <h2 style={{ margin:0, fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>Ugrás oldalra</h2>
          {rvSeg([{ v:'q', t:'Kérdések' }, { v:'sol', t:'Megoldások' }], sec, setSec, 'data-reveal-quiz-sec', 'Rész')}
        </div>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(6, minmax(0, 1fr))', gap:6, marginTop:12 }}>
          {chip(base, 'Borító', true)}
          {Array.from({ length:n }, (_, i) => chip(base + 1 + i, String(i + 1)))}
          {chip(2 + 2 * n, 'Pontozás', true)}
        </div>
      </section>
      <div style={{ display:'flex', gap:8, marginTop:'auto' }}>
        <button type="button" data-reveal-p-quizeditbtn onClick={() => setEditOpen(true)} style={rvBtn('secondary', { flex:1 })}>Kérdések szerkesztése</button>
        {active && <button type="button" data-reveal-quiz-end onClick={() => revealQuizWrite({ phase:'idle' })} style={rvBtn('ghost', { flex:1 })}>Kvíz befejezése</button>}
      </div>
      {editOpen && (
        // ⚠️ NEM portál: a szülő DOM-jában marad (position:fixed), így a tesztek `#__side`-ből is elérik
        <div data-reveal-p-quizedit style={{ position:'fixed', inset:0, zIndex:7000, display:'flex', flexDirection:'column', background:T.bg }}>
          <div style={{ flexShrink:0, display:'flex', alignItems:'center', gap:8, padding:'calc(10px + env(safe-area-inset-top)) 16px 10px', background:T.surface, borderBottom:`1px solid ${T.border}` }}>
            <div style={{ flex:1, fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink }}>Babakvíz kérdései</div>
            <button type="button" onClick={() => setEditOpen(false)} style={rvBtn('small')}>Kész</button>
          </div>
          <div style={{ flex:1, overflowY:'auto', padding:'14px 16px calc(24px + env(safe-area-inset-bottom))' }}><div style={{ maxWidth:640, margin:'0 auto' }}><RevealQuizEditor /></div></div>
        </div>
      )}
    </div>
  );
}

// ── 4. fül: Esemény (cím, linkek, album, ürítés) ──
function RevealLinksCard() {
  const cfg = useRevealCfg();
  const [title, setTitle] = React.useState('');
  const [init, setInit] = React.useState(false);
  const [askNew, setAskNew] = React.useState(false);
  const [msg, flash] = useRevealFlash();
  const tRef = React.useRef(null);
  React.useEffect(() => { if (cfg.loaded && !init) { setTitle((cfg.v || {}).title || ''); setInit(true); } }, [cfg.loaded]);
  React.useEffect(() => { if (cfg.loaded) revealEnsureKeys(cfg.v || {}); }, [cfg.loaded, cfg.v && cfg.v.guestKey, cfg.v && cfg.v.albumKey]);
  React.useEffect(() => () => clearTimeout(tRef.current), []);
  const db = revealDb();
  const v = cfg.v || {};
  // azonnali mentés, kis késleltetéssel (ne minden betűnél írjon)
  const onTitle = val => { setTitle(val); clearTimeout(tRef.current); tRef.current = setTimeout(() => { if (db) db.collection('config').doc('revealConfig').set({ title: val.trim() }, { merge:true }).then(() => flash('Mentve')).catch(e => flash('Nem sikerült (' + ((e && e.code) || 'hiba') + ')')); }, 450); };
  const newKeys = () => { setAskNew(false); if (db) db.collection('config').doc('revealConfig').set({ guestKey: revealKeyGen(), albumKey: revealKeyGen() }, { merge:true }).then(() => flash('Új linkek kész')).catch(() => {}); };
  const copy = u => { try { navigator.clipboard.writeText(u); flash('Link kimásolva'); } catch(e) {} };
  const linkRow = (label, sub, url, data, icon, tone) => (
    <div style={{ display:'flex', alignItems:'center', gap:12, padding:'10px 12px 10px 16px', borderTop:`1px solid ${T.border}` }}>
      {rvIconBox(icon, tone)}
      <div style={{ flex:1, minWidth:0 }}>
        <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink }}>{label}</div>
        <div {...{ [data]: url || '' }} title={url} style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>{url ? sub : 'Létrehozás…'}</div>
      </div>
      {url && <button type="button" onClick={() => copy(url)} style={rvBtn('small')}>Másol</button>}
    </div>
  );
  return (
    <div data-reveal-p-links style={{ display:'flex', flexDirection:'column', gap:12 }}>
      <section style={rvCard({ padding:'12px 16px 14px' })}>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', gap:8 }}>
          <label htmlFor="rv-ptitle" style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>Az esemény címe</label>
          {rvMsg(msg, 'data-reveal-p-linksmsg')}
        </div>
        <input id="rv-ptitle" data-reveal-p-title value={title} onChange={e => onTitle(e.target.value)} placeholder="Gender Reveal" style={rvInp({ marginTop:8, fontSize:16, fontWeight:800 })} />
        {rvNote('A vetítő üres állapotán és a vendégoldalon látszik.', { marginTop:6 })}
      </section>
      <section style={rvCard()}>
        {rvH('Linkek')}
        {linkRow('Vendég-link', 'Képet és üzenetet küldhetnek · ez a vetítő QR-kódja', revealGuestUrl(v), 'data-reveal-p-guesturl', 'qr', 'info')}
        {linkRow('Galéria-link', 'Csak nézhető · a buli után', revealAlbumUrl(v), 'data-reveal-p-albumurl', 'gallery', 'pink')}
        <button type="button" onClick={() => setAskNew(true)} style={rvBtn('ghost', { width:'100%', borderRadius:0, borderTop:`1px solid ${T.border}`, fontSize:13 })}>Új linkek készítése</button>
      </section>
      {askNew && (
        <ActionModal kicker="Új linkek?" onClose={() => setAskNew(false)} onSecondary={() => setAskNew(false)} secondaryLabel="Mégse"
          onPrimary={newKeys} primaryLabel="Új linkek" primaryColor={T.coral}>
          A mostani vendég-link és QR-kód, valamint a galéria-link megszűnik.
        </ActionModal>
      )}
    </div>
  );
}
function RevealAlbumCard() {
  const [msg, flash] = useRevealFlash();
  const [ask, setAsk] = React.useState(false);
  const [clearing, setClearing] = React.useState(false);
  const { list } = useRevealPhotos(false);
  const db = revealDb();
  const download = () => {
    if (!db) return;
    db.collection('revealPhotos').get().then(snap => {
      const n = revealDownloadAlbum(snap.docs.map(d => Object.assign({ id:d.id }, d.data()))); flash(`Album letöltve (${n} fájl)`);
    }).catch(() => flash('Az album nem sikerült'));
  };
  const clearAll = () => {
    if (!db) return;
    setClearing(true); setAsk(false);
    const wipe = coll => db.collection(coll).get().then(snap => {
      const refs = snap.docs.map(d => d.ref);
      const chunks = []; for (let i = 0; i < refs.length; i += 400) chunks.push(refs.slice(i, i + 400));
      return chunks.reduce((p, ch) => p.then(() => { const bt = db.batch(); ch.forEach(r => bt.delete(r)); return bt.commit(); }), Promise.resolve()).then(() => refs.length);
    });
    wipe('revealPhotos').then(n => wipe('revealQuizAns').then(() => n))
      .then(n => { setClearing(false); flash(`${n} kép és üzenet törölve`); }).catch(() => { setClearing(false); flash('Az ürítés nem sikerült'); });
  };
  return (
    <div data-reveal-p-album style={{ display:'flex', flexDirection:'column', gap:12, flex:1 }}>
      <section style={rvCard({ padding:'12px 16px 14px' })}>
        <div style={{ display:'flex', alignItems:'baseline', justifyContent:'space-between' }}>
          <h2 style={{ margin:0, fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>Album</h2>
          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft }}>{list.filter(p => p.src).length} kép · {list.filter(p => p.kind === 'wish').length} jókívánság</span>
        </div>
        <button type="button" data-reveal-p-zip onClick={download} style={rvBtn('primary', { width:'100%', height:48, fontSize:15, marginTop:10 })}>{rvIcon('download', 18)}Album letöltése (ZIP)</button>
      </section>
      <div style={{ flex:1 }} />
      <section style={{ borderRadius:20, border:'1.5px dashed #E8B4AE', padding:'12px 16px 14px', flexShrink:0 }}>
        <h2 style={{ margin:0, fontFamily:T.font, fontWeight:900, fontSize:13, color:'#A3342C' }}>Veszélyes zóna</h2>
        {rvNote('Előbb töltsétek le az albumot — az ürítés nem vonható vissza.', { marginTop:4 })}
        <button type="button" data-reveal-p-clear disabled={clearing} onClick={() => setAsk(true)} style={rvBtn('danger', { width:'100%', marginTop:10 })}>{clearing ? 'Ürítés…' : 'Képfolyam ürítése'}</button>
      </section>
      {msg && <div data-reveal-p-albummsg role="status" style={{ textAlign:'center', fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft }}>{msg}</div>}
      {ask && (
        <ActionModal kicker="Képfolyam ürítése" onClose={() => setAsk(false)} onSecondary={() => setAsk(false)} secondaryLabel="Mégse"
          onPrimary={clearAll} primaryLabel="Mind törlése" primaryColor={T.coral}>
          Minden képet, üzenetet és kvízválaszt törölsz. Letöltöttétek már az albumot? Ez nem vonható vissza.
        </ActionModal>
      )}
    </div>
  );
}

// ── a Szülők képernyő: kód-kapu, utána a négy fül ──
function RevealTrigger({ onBack }) {
  const secret = useRevealDoc('revealSecret');
  const [code, setCode] = React.useState('');
  const [ok, setOk] = React.useState(false);
  const [bad, setBad] = React.useState(false);
  const [tab, setTab] = React.useState('reveal');
  const sec = secret.v || {};
  const tryCode = () => { if (code.trim() === sec.code) setOk(true); else setBad(true); };
  if (!ok) return (
    <div data-reveal-trigger style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title="Szülők" onBack={onBack} />
      <div style={{ flex:1, overflowY:'auto', display:'flex', flexDirection:'column', alignItems:'center', gap:16, padding:'22px 16px calc(24px + env(safe-area-inset-bottom))' }}>
        {!secret.loaded ? <div style={{ fontFamily:T.font, color:T.inkSoft }}>Betöltés…</div>
        : !sec.code ? <div data-reveal-nocode style={rvCard({ maxWidth:440, padding:'22px 20px', textAlign:'center', fontFamily:T.font, fontSize:14, fontWeight:700, color:T.inkSoft, lineHeight:1.5 })}>Még nincs szülői kód beállítva.<br/>Admin → Gender Reveal</div>
        : (
          <div data-reveal-codegate style={rvCard({ maxWidth:440, padding:'22px 20px', display:'flex', flexDirection:'column', gap:12 })}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, textAlign:'center' }}>Szülői kód</div>
            <div style={{ fontFamily:T.font, fontSize:13, fontWeight:700, color:T.inkSoft, textAlign:'center', lineHeight:1.45 }}>Ez nem a közös jelszó — a leleplezést, az időpontot, a Babakvízt, a vetítő és az esemény beállításait a szülők kezelik, ezzel a kóddal.</div>
            <input data-reveal-code type="password" value={code} autoFocus aria-label="Szülői kód" onChange={e => { setCode(e.target.value); setBad(false); }} onKeyDown={e => { if (e.key === 'Enter') tryCode(); }}
              style={rvInp({ height:52, fontSize:18, textAlign:'center', borderColor: bad ? T.coral : T.border })} />
            {bad && <div data-reveal-codebad style={{ fontFamily:T.font, fontSize:13, fontWeight:800, color:T.coral, textAlign:'center' }}>Hibás kód</div>}
            <PrimaryButton onClick={tryCode} disabled={!code.trim()}>Tovább</PrimaryButton>
          </div>
        )}
      </div>
    </div>
  );
  return (
    <div data-reveal-trigger data-reveal-ptabactive={tab} style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title="Szülők" onBack={onBack} />
      <RevealParentStatus />
      <div data-reveal-pscroll style={{ flex:1, minHeight:0, overflowY:'auto', display:'flex', flexDirection:'column', padding:'2px 16px 14px', boxSizing:'border-box', WebkitOverflowScrolling:'touch' }}>
        <div style={{ flex:'1 0 auto', width:'100%', maxWidth:520, margin:'0 auto', display:'flex', flexDirection:'column', gap:12 }}>
          {tab === 'reveal' && <RevealParentRevealTab />}
          {tab === 'proj' && <RevealProjectorPanel />}
          {tab === 'quiz' && <div data-reveal-parentquiz style={{ display:'flex', flexDirection:'column', flex:1 }}><RevealQuizControl /></div>}
          {tab === 'event' && <React.Fragment><RevealLinksCard /><RevealAlbumCard /></React.Fragment>}
        </div>
      </div>
      <RevealParentTabs tab={tab} onTab={setTab} />
    </div>
  );
}

'''
a = s.index("function rvCard(extra) {")
b = s.index("// ── Admin (v10.439): CSAK a belépés és a titkos rész.")
s = s[:a] + NEW + s[b:]

for gone in ['RevealScheduleCard', 'RevealQuizEditBox', 'RevealVideoCard', 'jumpOpen']:
    assert gone not in s, gone
open(P, 'w', encoding='utf-8').write(s); print('ok')
