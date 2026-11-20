# v10.455 — a titkos rész (eredmény, szülői kód, videó-link, állapot + visszaállítás) az
# admin helyett a SZÜLŐKNÉL. Az adminban csak a belépő kód marad.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:140]); s = s.replace(old, new)
def between(a, b):
    i = s.index(a); j = s.index(b, i); return i, j
rep("const APP_VERSION = 'v10.454';", "const APP_VERSION = 'v10.455';")

# ── a titkos kártya a Szülők Leleplezés fülén ─────────────────────────────────────
rep("""function RevealParentRevealTab({ dock }) {""", r"""// v10.455: TITKOS beállítások a Szülőknél (az adminból költözött). Alapból CSUKVA — az
// Előkészületek „Eredmény" sorára koppintva nyílik. Az eredmény MASZKOLVA („●●● beállítva"),
// csak a 👁 Mutat-tal látszik: aki nem akarja tudni, ne lássa véletlenül.
// Az eredmény koppintásra ment; a videó-link 600 ms késleltetéssel; a szülői kód CSAK a
// „Mentés" gombra (érzékeny: egy félig begépelt kód kizárná a többieket).
const revealIsYoutube = u => /(^|\/\/|\.)(youtube\.com|youtu\.be)\//i.test(String(u || ''));
function RevealSecretCard({ onClose }) {
  const secret = useRevealDoc('revealSecret'), rstate = useRevealDoc('revealState');
  const sec = secret.v || {}, st = rstate.v || {};
  const [peek, setPeek] = React.useState(false);
  const [code, setCode] = React.useState(null);
  const [url, setUrl] = React.useState(null);
  const [msg, flash] = useRevealFlash();
  const codeV = code === null ? (sec.code || '') : code, urlV = url === null ? (sec.videoUrl || '') : url;
  const db = revealDb();
  const save = (patch, m) => { if (db) db.collection('config').doc('revealSecret').set(patch, { merge:true }).then(() => flash(m || 'Mentve')).catch(e => flash('Nem sikerült (' + ((e && e.code) || 'hiba') + ')')); };
  const urlT = React.useRef(null);
  const onUrl = v => { setUrl(v); clearTimeout(urlT.current); urlT.current = setTimeout(() => save({ videoUrl: v.trim() }), 600); };
  React.useEffect(() => () => clearTimeout(urlT.current), []);
  const codeOk = /^\d{4,12}$/.test(codeV), codeChanged = codeV !== (sec.code || '');
  const result = sec.result;
  const lbl = t => <div style={{ fontFamily:T.font, fontSize:11, fontWeight:900, letterSpacing:'0.08em', color:T.inkSoft, textTransform:'uppercase', margin:'14px 0 6px' }}>{t}</div>;
  return (
    <section data-reveal-p-secret style={rvCard({ padding:'12px 16px 16px', borderColor:'#E8D6A8' })}>
      <div style={{ display:'flex', alignItems:'center', gap:10 }}>
        {rvIconBox('lock', 'warn')}
        <div style={{ flex:1, minWidth:0 }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>Titkos beállítások</div>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft }}>Az eredmény rejtve marad, amíg nem kéritek.</div>
        </div>
        {rvMsg(msg, 'data-reveal-p-secretmsg')}
        {onClose && <button type="button" onClick={onClose} aria-label="Bezárás" style={rvBtn('small', { width:36, padding:0 })}>{rvIcon('close', 16)}</button>}
      </div>
      {lbl('Az eredmény')}
      <div style={{ display:'flex', gap:8, alignItems:'center' }}>
        {peek || !result ? ['boy', 'girl'].map(r => (
          <button key={r} type="button" data-reveal-p-result={r} aria-pressed={result === r} onClick={() => save({ result:r })}
            style={rvBtn(result === r ? 'primary' : 'secondary', { flex:1, height:46, fontSize:15, background: result === r ? REVEAL_RESULTS[r].c1 : T.surface })}>{REVEAL_RESULTS[r].emoji} {REVEAL_RESULTS[r].name}</button>
        )) : <div data-reveal-p-masked style={{ flex:1, fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>●●● beállítva</div>}
        {result && <button type="button" data-reveal-p-peek onClick={() => setPeek(p => !p)} style={rvBtn('small', { height:46 })}>{peek ? 'Elrejt' : '👁 Mutat'}</button>}
      </div>
      {lbl('Szülői kód')}
      <div style={{ display:'flex', gap:8 }}>
        <input data-reveal-p-code value={codeV} inputMode="numeric" aria-label="Szülői kód" onChange={e => setCode(e.target.value.replace(/\D/g, '').slice(0, 12))} placeholder="pl. 2026" style={rvInp({ flex:1, minWidth:0 })} />
        <button type="button" data-reveal-p-codesave disabled={!codeOk || !codeChanged} onClick={() => { save({ code: codeV }, 'Kód mentve'); setCode(null); }}
          style={rvBtn('primary', { height:48, padding:'0 16px', fontSize:15, opacity: codeOk && codeChanged ? 1 : 0.45, cursor: codeOk && codeChanged ? 'pointer' : 'default' })}>Mentés</button>
      </div>
      {codeV && !codeOk && <div style={{ fontFamily:T.font, fontWeight:800, fontSize:12, color:'#A3342C', marginTop:6 }}>Legalább 4 számjegy.</div>}
      {lbl('Videó-link (nem kötelező)')}
      <input data-reveal-p-videourl value={urlV} onChange={e => onUrl(e.target.value)} placeholder="https://…/leleplezes.mp4" aria-label="Videó-link" style={rvInp()} />
      {revealIsYoutube(urlV)
        ? <div data-reveal-p-videowarn style={{ fontFamily:T.font, fontWeight:800, fontSize:12, color:'#A3342C', marginTop:6, lineHeight:1.45 }}>YouTube-linket a vetítő nem tud lejátszani. Töltsd fel a videót (Leleplező videó sor), vagy adj meg közvetlen .mp4 linket.</div>
        : rvNote('Közvetlen .mp4 link. Ha van feltöltött videó, az megy helyette. Próbánál soha nincs videó.')}
      <div style={{ display:'flex', alignItems:'center', gap:10, marginTop:14, flexWrap:'wrap' }}>
        <span data-reveal-p-state style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft }}>Állapot: {st.phase === 'reveal' ? (st.test ? 'próba lefutott' : 'leleplezve 🎉') : st.phase === 'armed' ? 'engedélyezve' : 'engedélyre vár'}</span>
        {(st.phase === 'reveal' || st.phase === 'armed') && <button type="button" data-reveal-p-reset onClick={() => { if (db) db.collection('config').doc('revealState').set({ phase:'idle', run: revealToken(), at: Date.now() }).then(() => flash('Visszaállítva')).catch(() => {}); }} style={rvBtn('danger', { height:40 })}>Visszaállítás</button>}
      </div>
    </section>
  );
}
function RevealParentRevealTab({ dock }) {""")
rep("""  const [editWhen, setEditWhen] = React.useState(false);
  const [cfgMsg, flashCfg] = useRevealFlash();""", """  const [editWhen, setEditWhen] = React.useState(false);
  const [secretOpen, setSecretOpen] = React.useState(false);
  const [cfgMsg, flashCfg] = useRevealFlash();""")
rep("""        {rvRow({ first:true, icon:'lock', tone: ready ? 'ok' : 'bad', label:'Eredmény (admin)', right: rvPill(ready ? 'Beállítva' : 'Hiányzik', ready ? 'ok' : 'bad', ready ? null : { 'data-reveal-notready':'' }) })}""",
    """        {rvRow({ first:true, icon:'lock', tone: ready ? 'ok' : 'bad', label:'Eredmény és kód', onClick: () => setSecretOpen(o => !o), data:{ 'data-reveal-p-secretrow':'' },
          right: rvPill(ready ? 'Beállítva' : 'Hiányzik', ready ? 'ok' : 'bad', ready ? null : { 'data-reveal-notready':'' }) })}""")
# a titkos kártya az Előkészületek UTÁN (csak ha nyitva)
i, j = between("      <section data-reveal-p-schedule style={rvCard()}>", "</section>")
j = j + len("</section>")
s = s[:j] + "\n      {secretOpen && <RevealSecretCard onClose={() => setSecretOpen(false)} />}" + s[j:]

# ── kód nélkül: a Szülők maguk állítják be az elsőt ────────────────────────────────
rep("""        : !sec.code ? <div data-reveal-nocode style={rvCard({ maxWidth:440, padding:'22px 20px', textAlign:'center', fontFamily:T.font, fontSize:14, fontWeight:700, color:T.inkSoft, lineHeight:1.5 })}>Még nincs szülői kód beállítva.<br/>Admin → Gender Reveal</div>""",
"""        : !sec.code ? (
          // v10.455: a szülői kódot már nem az admin adja — az ELSŐ belépő állítja be
          <div data-reveal-nocode style={rvCard({ maxWidth:360, padding:'22px 20px', display:'flex', flexDirection:'column', gap:12, border:'none', boxShadow:T.shadow })}>
            <div style={{ textAlign:'center' }}>
              <div style={{ display:'flex', alignItems:'center', gap:8, justifyContent:'center' }}><BohIcon name="lock" size={22} /><span style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink }}>Szülői kód beállítása</span></div>
              <div style={{ fontFamily:T.font, fontSize:13, fontWeight:700, color:T.inkSoft, lineHeight:1.45, marginTop:6 }}>Még nincs szülői kód. Adjátok meg most (legalább 4 számjegy) — ezzel léptek be legközelebb.</div>
            </div>
            <input data-reveal-p-newcode value={newCode} inputMode="numeric" autoFocus aria-label="Új szülői kód" onChange={e => setNewCode(e.target.value.replace(/\\D/g, '').slice(0, 12))} placeholder="pl. 2026" style={rvInp({ height:52, fontSize:20, textAlign:'center', letterSpacing:4 })} />
            <PrimaryButton onClick={() => { const c = newCode; const db = revealDb(); if (!db || !/^\\d{4,12}$/.test(c)) return; db.collection('config').doc('revealSecret').set({ code:c }, { merge:true }).then(() => setOk(true)).catch(() => {}); }}
              disabled={!/^\\d{4,12}$/.test(newCode)}>Kód mentése</PrimaryButton>
          </div>
        )""")
rep("""  const [ok, setOk] = React.useState(false);""", """  const [ok, setOk] = React.useState(false);
  const [newCode, setNewCode] = React.useState('');""")

# ── admin: csak a belépő kód ───────────────────────────────────────────────────────
i, j = between("      <div data-admin-reveal-secret style={box}>", "\n    </div>\n  );\n}\n\n// ── Pub: saját keverés")
s = s[:i].rstrip(' ') + s[j+1:]
rep("""        {h('👶 A többi beállítás a Szülőknél van')}
        {note('A cím, a vendég- és galéria-link, a leleplezés időpontja, a visszaszámláló, a vetítő beállításai, a Babakvíz kérdései, az album és az ürítés a Gender Reveal app „Szülők" szerepében állítható — a szülői kóddal. Itt csak a belépés és a titkos eredmény marad.')}""",
    """        {h('👶 Minden más a Szülőknél van')}
        {note('Az eredmény, a szülői kód, a videó, az időpont, a vetítő, a Babakvíz, a linkek és az album a Gender Reveal app „Szülők" szerepében állítható. Itt csak a közös belépő kód marad.')}""")
# az admin halott állapota (eredmény, kód, videó, peek, állapot) ki
i = s.index('function AdminReveal() {'); j = s.index('  const label = t =>', i)
s = s[:i] + "function AdminReveal() {\n  const cfg = useRevealCfg();\n  const [pw, setPw] = React.useState('');\n  const [init, setInit] = React.useState(false);\n  const [msg, setMsg] = React.useState('');\n  React.useEffect(() => { if (cfg.loaded && !init) { setPw((cfg.v || {}).password || ''); setInit(true); } }, [cfg.loaded]);\n  const flash = (set, m) => { set(m); setTimeout(() => set(''), 2500); };\n  const db = revealDb();\n  const save = () => {\n    if (!db) return;\n    const v = cfg.v || {};\n    // a vendég- és album-kulcs az első mentéskor keletkezik, utána változatlan\n    db.collection('config').doc('revealConfig').set({ password: pw.trim(), guestKey: v.guestKey || revealKeyGen(), albumKey: v.albumKey || revealKeyGen() }, { merge:true })\n      .then(() => flash(setMsg, 'Mentve ✓')).catch(e => flash(setMsg, 'Nem sikerült menteni (' + ((e && e.code) || 'hiba') + ')'));\n  };\n" + s[j:]
rep("  if (!cfg.loaded) return <div style={{ textAlign:'center', padding:32, color:T.sub, fontFamily:T.font }}>Betöltés…</div>;\n  const st = rstate.v || {};\n", "  if (!cfg.loaded) return <div style={{ textAlign:'center', padding:32, color:T.sub, fontFamily:T.font }}>Betöltés…</div>;\n")
rep('    case \'expand\': return <svg {...p}><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" /></svg>;', '    case \'expand\': return <svg {...p}><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" /></svg>;\n    case \'close\': return <svg {...p}><path d="M6 6l12 12M18 6L6 18" /></svg>;')
open(P, 'w', encoding='utf-8').write(s); print('ok')
