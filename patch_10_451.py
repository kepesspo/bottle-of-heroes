# v10.451 — Gender Reveal: a belépés KÓD, számbillentyűzettel (jelszómező helyett) — a
# közös belépő ÉS a Szülők kódja. Régi, betűs jelszónál a szövegmező marad (nincs kizárás).
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:140]); s = s.replace(old, new)

rep("const APP_VERSION = 'v10.450';", "const APP_VERSION = 'v10.451';")

# ── közös kódbeíró ─────────────────────────────────────────────────────────────────
rep("""// v10.450: „2 perce" — a beküldés / jóváhagyás ideje (`at`)""", r"""// v10.451: KÓDBEÍRÓ — pöttyök + 3×4 számbillentyűzet. A kód hossza ismert (`expect`), ezért
// az utolsó számjegy után MAGÁTÓL ellenőriz; Enterrel / „OK"-val előbb is lehet. A fizikai
// billentyűzet (laptop a vetítőn) is működik: számok, Backspace, Enter.
// ⚠️ Ha a beállított kód NEM csak számjegy (régi, betűs jelszó), a szövegmező marad — különben
// a billentyűzettel be sem lehetne lépni. Az admin mezője innentől csak számot fogad.
const revealIsNumCode = c => /^\d{1,12}$/.test(String(c || ''));
function RevealCodePad({ title, hint, expect, onOk, badText, inputAttr, badAttr }) {
  const [v, setV] = React.useState('');
  const [bad, setBad] = React.useState(false);
  const numeric = revealIsNumCode(expect), len = String(expect || '').length;
  const check = val => { if (val && val === String(expect)) { setV(''); onOk(); } else { setBad(true); setV(''); } };
  const press = d => { setBad(false); setV(x => (numeric && x.length >= len) ? x : x + d); };
  const back = () => { setBad(false); setV(x => x.slice(0, -1)); };
  const vRef = React.useRef(v); vRef.current = v;
  React.useEffect(() => {
    if (!numeric || v.length !== len) return;
    const t = setTimeout(() => check(v), 140); return () => clearTimeout(t);
  }, [v]);
  React.useEffect(() => {
    if (!numeric) return;
    const k = e => {
      const tg = e.target && e.target.tagName; if (tg === 'INPUT' || tg === 'TEXTAREA') return;
      if (/^\d$/.test(e.key)) { e.preventDefault(); press(e.key); }
      else if (e.key === 'Backspace') { e.preventDefault(); back(); }
      else if (e.key === 'Enter') { e.preventDefault(); if (vRef.current) check(vRef.current); }
    };
    window.addEventListener('keydown', k); return () => window.removeEventListener('keydown', k);
  }, [numeric, expect]);
  const head = (
    <div style={{ textAlign:'center' }}>
      <div style={{ display:'flex', alignItems:'center', gap:8, justifyContent:'center' }}><BohIcon name="lock" size={22} /><span style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink }}>{title}</span></div>
      {hint && <div style={{ fontFamily:T.font, fontSize:13, fontWeight:700, color:T.inkSoft, lineHeight:1.45, marginTop:6 }}>{hint}</div>}
    </div>
  );
  const badLine = bad && <div {...{ [badAttr]: '' }} role="alert" style={{ fontFamily:T.font, fontSize:13, fontWeight:800, color:T.coral, textAlign:'center' }}>{badText}</div>;
  if (!numeric) return (
    <React.Fragment>
      {head}
      <input {...{ [inputAttr]: '' }} type="password" value={v} autoFocus aria-label={title} onChange={e => { setV(e.target.value); setBad(false); }} onKeyDown={e => { if (e.key === 'Enter') check(v.trim()); }}
        style={rvInp({ height:52, fontSize:18, textAlign:'center', borderColor: bad ? T.coral : T.border })} />
      {badLine}
      <PrimaryButton onClick={() => check(v.trim())} disabled={!v.trim()}>Tovább</PrimaryButton>
    </React.Fragment>
  );
  const keyBtn = (label, onClick, attrs, extra) => (
    <button type="button" {...attrs} onClick={onClick} style={{ height:60, borderRadius:18, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize:24, color:T.ink,
      background:T.bgSoft || T.bg, display:'grid', placeItems:'center', WebkitTapHighlightColor:'transparent', touchAction:'manipulation', ...(extra || {}) }}>{label}</button>
  );
  return (
    <React.Fragment>
      {head}
      <div data-reveal-dots data-n={v.length} {...{ [inputAttr]: '' }} aria-label={`${v.length} / ${len} számjegy`} style={{ display:'flex', justifyContent:'center', gap:12, padding:'6px 0 2px', animation: bad ? 'revealShake .35s' : 'none' }}>
        <style>{`@keyframes revealShake { 0%,100% { transform:translateX(0) } 25% { transform:translateX(-8px) } 75% { transform:translateX(8px) } }`}</style>
        {Array.from({ length: Math.min(len, 12) }, (_, i) => (
          <span key={i} style={{ width:16, height:16, borderRadius:'50%', boxSizing:'border-box', border:`2px solid ${bad ? T.coral : i < v.length ? T.mint : T.border}`, background: i < v.length ? T.mint : 'transparent', transition:'background .12s' }} />
        ))}
      </div>
      {badLine}
      <div data-reveal-keypad style={{ display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:10 }}>
        {['1', '2', '3', '4', '5', '6', '7', '8', '9'].map(d => <React.Fragment key={d}>{keyBtn(d, () => press(d), { 'data-reveal-key': d, 'aria-label': d })}</React.Fragment>)}
        <span />
        {keyBtn('0', () => press('0'), { 'data-reveal-key': '0', 'aria-label': '0' })}
        {keyBtn(rvIcon('prev', 22), back, { 'data-reveal-keyback': '', 'aria-label': 'Törlés' }, { background:'transparent', color:T.inkSoft })}
      </div>
    </React.Fragment>
  );
}
// v10.450: „2 perce" — a beküldés / jóváhagyás ideje (`at`)""")

# ── a közös belépő ─────────────────────────────────────────────────────────────────
rep("""          <div data-reveal-gate style={{ ...card, display:'flex', flexDirection:'column', gap:12 }}>
            <div style={{ display:'flex', alignItems:'center', gap:8, justifyContent:'center' }}><BohIcon name="lock" size={22} /><span style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink }}>Jelszó</span></div>
            <input data-reveal-pw type="password" value={inp} autoFocus onChange={e => { setInp(e.target.value); setBad(false); }} onKeyDown={e => { if (e.key === 'Enter') submit(); }} placeholder="Írd be a jelszót"
              style={{ width:'100%', boxSizing:'border-box', padding:'14px', borderRadius:14, border:`1.5px solid ${bad ? T.coral : T.border}`, background:T.bg, fontFamily:T.font, fontSize:17, fontWeight:700, color:T.ink, textAlign:'center', outline:'none' }} />
            {bad && <div data-reveal-bad style={{ fontFamily:T.font, fontSize:13, fontWeight:800, color:T.coral, textAlign:'center' }}>Hibás jelszó</div>}
            <PrimaryButton onClick={submit} disabled={!inp.trim()}>Belépés</PrimaryButton>
          </div>""", """          <div data-reveal-gate style={{ ...card, display:'flex', flexDirection:'column', gap:14, maxWidth:360 }}>
            <RevealCodePad title="Belépő kód" hint="Ugyanaz a kód a vetítőnek és az operátornak." expect={pw} onOk={() => setSaved(pw)} badText="Hibás kód" inputAttr="data-reveal-pw" badAttr="data-reveal-bad" />
          </div>""")
s = s.replace("""Még nincs jelszó beállítva.<br/>Admin → Gender Reveal""", """Még nincs belépő kód beállítva.<br/>Admin → Gender Reveal""")
# a régi beíró-állapot fölösleges (a kódbeíró a sajátját tartja)
rep("""  const [inp, setInp] = React.useState('');
  const [bad, setBad] = React.useState(false);
  const [role, setRole]""", """  const [role, setRole]""")
rep("""  const submit = () => {
    if (inp.trim() && inp.trim() === pw) { setSaved(inp.trim()); setBad(false); setInp(''); }
    else setBad(true);
  };
""", "")

# ── a Szülők kódja ─────────────────────────────────────────────────────────────────
rep("""          <div data-reveal-codegate style={rvCard({ maxWidth:440, padding:'22px 20px', display:'flex', flexDirection:'column', gap:12 })}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, textAlign:'center' }}>Szülői kód</div>
            <div style={{ fontFamily:T.font, fontSize:13, fontWeight:700, color:T.inkSoft, textAlign:'center', lineHeight:1.45 }}>Ez nem a közös jelszó — a leleplezést, az időpontot, a Babakvízt, a vetítő és az esemény beállításait a szülők kezelik, ezzel a kóddal.</div>
            <input data-reveal-code type="password" value={code} autoFocus aria-label="Szülői kód" onChange={e => { setCode(e.target.value); setBad(false); }} onKeyDown={e => { if (e.key === 'Enter') tryCode(); }}
              style={rvInp({ height:52, fontSize:18, textAlign:'center', borderColor: bad ? T.coral : T.border })} />
            {bad && <div data-reveal-codebad style={{ fontFamily:T.font, fontSize:13, fontWeight:800, color:T.coral, textAlign:'center' }}>Hibás kód</div>}
            <PrimaryButton onClick={tryCode} disabled={!code.trim()}>Tovább</PrimaryButton>
          </div>""", """          <div data-reveal-codegate style={rvCard({ maxWidth:360, padding:'22px 20px', display:'flex', flexDirection:'column', gap:14, border:'none', boxShadow:T.shadow })}>
            <RevealCodePad title="Szülői kód" hint="Nem a közös belépő kód — ezzel a szülők kezelik a leleplezést és minden beállítást." expect={sec.code} onOk={() => setOk(true)} badText="Hibás kód" inputAttr="data-reveal-code" badAttr="data-reveal-codebad" />
          </div>""")
rep("""  const [code, setCode] = React.useState('');
  const [ok, setOk] = React.useState(false);
  const [bad, setBad] = React.useState(false);""", """  const [ok, setOk] = React.useState(false);""")
rep("""  const tryCode = () => { if (code.trim() === sec.code) setOk(true); else setBad(true); };
""", "")

# ── admin: csak számjegy ───────────────────────────────────────────────────────────
rep("""        {note('Egy jelszó a vetítőnek és az operátornak is — minden megnyitáskor bekéri.')}
        {label('Jelszó')}
        <input data-admin-reveal-pw value={pw} onChange={e => setPw(e.target.value)} placeholder="pl. babavaro" style={inpSt} />""",
"""        {note('Egy kód a vetítőnek és az operátornak is — minden megnyitáskor bekéri, számbillentyűzeten. Csak számjegy (4–8 jegy ajánlott).')}
        {label('Belépő kód')}
        <input data-admin-reveal-pw value={pw} inputMode="numeric" onChange={e => setPw(e.target.value.replace(/\\D/g, '').slice(0, 12))} placeholder="pl. 1234" style={inpSt} />
        {pw && !revealIsNumCode(pw) && <div style={{ fontFamily:T.font, fontWeight:800, fontSize:12, color:'#A3342C', marginTop:6 }}>A régi jelszó betűket tartalmaz — adj meg számkódot.</div>}""")
rep("""        <input data-admin-reveal-code value={code} onChange={e => setCode(e.target.value)} placeholder="pl. 2026" style={inpSt} />""",
    """        <input data-admin-reveal-code value={code} inputMode="numeric" onChange={e => setCode(e.target.value.replace(/\\D/g, '').slice(0, 12))} placeholder="pl. 2026" style={inpSt} />""")
open(P, 'w', encoding='utf-8').write(s); print('ok')
