# v10.478 (2. rész) — ha a Bingó-lista HOSSZA változik, a Mentés új kört indít: a kártya-elrendezés a
# tételszámból jön, tehát a futó kör pipái más szavakra csúsznának át.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("""  const [cardStyle, setCardStyle] = React.useState('icon'); // v10.477: kártya-kinézet""",
    """  const [cardStyle, setCardStyle] = React.useState('icon'); // v10.477: kártya-kinézet
  const [roundN, setRoundN] = React.useState(0);   // v10.478: a futó kör tételszáma (a kártya ebből épül)""")
rep("""      setItems((c && Array.isArray(c.items) && c.items.length) ? c.items.map(it => ({ e: it.e || '', t: it.t || '', k: bingoK(it) })) : BINGO_PRESETS.foci.items.map(it => ({ ...it })));""",
    """      setItems((c && Array.isArray(c.items) && c.items.length) ? c.items.map(it => ({ e: it.e || '', t: it.t || '', k: bingoK(it) })) : BINGO_PRESETS.foci.items.map(it => ({ ...it })));
      setRoundN((c && Array.isArray(c.items) && c.items.length) ? c.items.filter(it => (it.t || '').trim()).length : BINGO_PRESETS.foci.items.length);""")
rep("""  const persist = (payload) => {
    setSaving(true); setSaveErr('');""",
    """  const persist = (payload) => {
    setSaving(true); setSaveErr('');
    if (payload && Array.isArray(payload.items)) setRoundN(payload.items.length);""")
rep("""  const save = () => persist(buildPayload());""",
"""  // ⚠️ v10.478: a kártya-elrendezés a TÉTELSZÁMBÓL jön (bingoCardFor), tehát ha a lista hossza
  // változik, a futó kör pipái más szavakra csúsznának át — ilyenkor a Mentés új kört indít.
  // Egy elírt szó javítása (azonos darabszám) a helyén cseréli a szót, a pipák maradnak.
  const save = () => {
    if (mode === 'bingo' && roundN && validCount !== roundN) { const nr = newRound(); setRound(nr); persist(buildPayload({ bingoRound: nr })); }
    else persist(buildPayload());
  };""")
# figyelmeztetés a Mentés előtt
rep("""{validCount >= 24 ? `${validCount} tétel → 5×5-ös kártya (24 sorsolt mező + ingyen közép)` : validCount >= 16 ? `${validCount} tétel → 4×4-es kártya (16 sorsolt mező, nincs ingyen közép)` : `${validCount} tétel — kártyához legalább 16 kell`}</div>""",
    """{validCount >= 24 ? `${validCount} tétel → 5×5-ös kártya (24 sorsolt mező + ingyen közép)` : validCount >= 16 ? `${validCount} tétel → 4×4-es kártya (16 sorsolt mező, nincs ingyen közép)` : `${validCount} tétel — kártyához legalább 16 kell`}</div>
          {roundN > 0 && validCount !== roundN && <div data-bingo-newround-note style={{ fontFamily:T.font, fontWeight:700, fontSize:11.5, color:T.coral, marginBottom:6, lineHeight:1.4 }}>A tételek száma változott ({roundN} → {validCount}) — mentéskor új kör indul, mindenki új kártyát kap.</div>}""")
open(P, 'w', encoding='utf-8').write(s)
print('OK')
