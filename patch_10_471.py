# v10.471 — Gender Reveal belépés: a számbillentyűzet akkor is jön, ha a kód körül szóköz / sortörés van
#  (a tárolt kódot trimeljük), és a régi, betűs jelszónál a szövegmező fölött megmondja, hol kell számkódra cserélni.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.470';", "const APP_VERSION = 'v10.471';")
rep("const revealIsNumCode = c => /^\\d{1,12}$/.test(String(c || ''));",
    "const revealIsNumCode = c => /^\\d{1,12}$/.test(String(c == null ? '' : c).trim());   // v10.471: szóköz / sortörés nem rontja el")
rep("""function RevealCodePad({ title, hint, expect, onOk, badText, inputAttr, badAttr }) {
  const [v, setV] = React.useState('');
  const [bad, setBad] = React.useState(false);
  const numeric = revealIsNumCode(expect), len = String(expect || '').length;
  const check = val => { if (val && val === String(expect)) { setV(''); onOk(); } else { setBad(true); setV(''); } };""",
"""function RevealCodePad({ title, hint, expect, onOk, badText, inputAttr, badAttr, legacyWhere }) {
  const [v, setV] = React.useState('');
  const [bad, setBad] = React.useState(false);
  // v10.471: a tárolt kódot trimeljük — egy véletlen szóköz miatt ne essen vissza a szövegmezőre
  const code = String(expect == null ? '' : expect).trim();
  const numeric = revealIsNumCode(code), len = code.length;
  const check = val => { if (val && val === code) { setV(''); onOk(); } else { setBad(true); setV(''); } };""")
rep("""  if (!numeric) return (
    <React.Fragment>
      {head}""",
"""  if (!numeric) return (
    <React.Fragment>
      {head}
      {/* v10.471: a betűs kód régi beállítás — megmondjuk, hol lesz belőle számkód (és vele számbillentyűzet) */}
      <div data-reveal-legacypw style={{ fontFamily:T.font, fontSize:12.5, fontWeight:700, lineHeight:1.45, textAlign:'center', color:'#8A5A12', background:'#FFF3D6', borderRadius:12, padding:'8px 12px' }}>
        Ez még a régi, betűs kód. Számbillentyűzethez állíts be számkódot{legacyWhere ? <React.Fragment> itt: <b>{legacyWhere}</b></React.Fragment> : null}.
      </div>""")
rep("""expect={pw} onOk={() => setSaved(pw)} badText="Hibás kód" inputAttr="data-reveal-pw" badAttr="data-reveal-bad" />""",
    """expect={pw} onOk={() => setSaved(pw)} badText="Hibás kód" inputAttr="data-reveal-pw" badAttr="data-reveal-bad" legacyWhere="Admin → Gender Reveal → Belépő kód" />""")
rep("""expect={sec.code} onOk={() => setOk(true)} badText="Hibás kód" inputAttr="data-reveal-code" badAttr="data-reveal-codebad" />""",
    """expect={sec.code} onOk={() => setOk(true)} badText="Hibás kód" inputAttr="data-reveal-code" badAttr="data-reveal-codebad" legacyWhere="Szülők → Leleplezés → Eredmény és kód" />""")
rep("  const pw = (cfg.v && cfg.v.password) || '';", "  const pw = String((cfg.v && cfg.v.password) || '').trim();   // v10.471: trimelve")

open(P, 'w', encoding='utf-8').write(s)
print('ok')
