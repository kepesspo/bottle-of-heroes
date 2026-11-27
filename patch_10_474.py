# v10.474 — DNR Bingó / OTP Gála: 24 szó (a tavalyi 18 + 6 új) → 5×5-ös kártya, középen „OTP Gála 2027”.
# A preset verziót kap (`pv`): a régebbi verzióból mentett szett-másolat helyett a friss preset töltődik be,
# és az adminban „Alap lista visszatöltése" gomb tölti be kézzel is.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.473';", "const APP_VERSION = 'v10.474';")

rep("""  otp: { name:'OTP Gála', title:'OTP Gála Bingó', titleEmoji:'🎤', center:{ e:'🎤', t:'GÁLA' },""",
    """  // v10.474: a tavalyi Gála 18 szava (a tulajdonos táblázata) + 6 új → 24 → 5×5, középen „OTP Gála 2027".
  // `pv` = a preset verziója: ha egy korábbi verzióból mentett másolat ül a bingoSets-ben, váltáskor a
  // friss preset jön (a 18 szavas másolat különben örökre bent ragadna).
  otp: { name:'OTP Gála', pv:2, title:'OTP Gála Bingó', titleEmoji:'🎤', center:{ e:'🥂', t:'OTP Gála 2027' },""")
rep("""      { e:'🤖', t:'Technológia', k:2 }, { e:'🏦', t:'Bankfiók', k:1 }, { e:'🙊', t:'Elszólás', k:2 },
    ] },""",
"""      { e:'🤖', t:'Technológia', k:2 }, { e:'🏦', t:'Bankfiók', k:1 }, { e:'🙊', t:'Elszólás', k:2 },
      { e:'🧠', t:'Mesterséges intelligencia', k:3 }, { e:'🛡️', t:'Kiberbiztonság', k:2 }, { e:'🤲', t:'Bizalom', k:2 },
      { e:'👥', t:'Csapatmunka', k:1 }, { e:'♟️', t:'Stratégia', k:1 }, { e:'🙏', t:'Köszönöm a figyelmet', k:1 },
    ] },""")

# admin: pv a szettben, frissebb preset elsőbbsége, kézi visszatöltés
rep("""  const [round, setRound] = React.useState('');""",
    """  const [round, setRound] = React.useState('');
  const [setPv, setSetPv] = React.useState(0);       // v10.474: az aktív szett preset-verziója""")
rep("""      setRound((c && c.bingoRound) || '');""",
    """      setRound((c && c.bingoRound) || '');
      { const sid = (c && c.bingoSetId) || 'foci', sv = c && c.bingoSets && c.bingoSets[sid]; setSetPv((sv && sv.pv) || 0); }""")
rep("""center: cleanCenter, items: cleanItems } });""",
    """center: cleanCenter, items: cleanItems, pv: setPv } });""")
rep("""    const src = (cur.bingoSets[id]) || BINGO_PRESETS[id];
    if (!src) return;""",
"""    const saved = cur.bingoSets[id], pre = BINGO_PRESETS[id];
    // ⚠️ egy RÉGEBBI preset-verzióból mentett másolat helyett a friss preset jön (v10.474)
    const src = (saved && !(pre && (saved.pv || 0) < (pre.pv || 0))) ? saved : (pre || saved);
    if (!src) return;
    setSetPv(src.pv || 0);""")
rep("""  const startNewRound = () => { const nr = newRound(); setRound(nr); persist(buildPayload({ bingoRound: nr })); };""",
"""  const startNewRound = () => { const nr = newRound(); setRound(nr); persist(buildPayload({ bingoRound: nr })); };
  // v10.474: a beépített szett alap listájának visszatöltése (a szerkesztőbe — a Mentés viszi ki)
  const loadPreset = () => {
    const pre = BINGO_PRESETS[setId]; if (!pre) return;
    setTitle(pre.title); setTitleEmoji(pre.titleEmoji || ''); setCenter(pre.center); setSetPv(pre.pv || 0);
    setItems(pre.items.map(it => ({ ...it }))); markDirty();
  };""")
rep("""            <button data-bingo-newround onClick={() => setAskSet({ kind:'round' })}""",
    """            {BINGO_PRESETS[setId] && <button data-bingo-preset onClick={loadPreset} style={{ marginTop:10, marginRight:8, padding:'9px 14px', borderRadius:10, border:`1.5px solid ${T.border}`, background:'transparent', color:T.ink, fontFamily:T.font, fontWeight:800, fontSize:13, cursor:'pointer' }}>Alap lista visszatöltése</button>}
            <button data-bingo-newround onClick={() => setAskSet({ kind:'round' })}""")
rep("""placeholder="DÖNTŐ" maxLength={12}""", """placeholder="DÖNTŐ" maxLength={20}""")

# a váltás rögtön a betöltött szettet is elmenti (a verziójával) — nem csak a következő Mentés
rep("""    setSets(cur.bingoSets); setSetId(id); setRound(nr);""",
    """    const srcSnap = { name: src.name || (pre && pre.name) || src.title, title: src.title, titleEmoji: src.titleEmoji || '', center: src.center || BINGO_PRESETS.foci.center, items: (src.items || []).map(it => ({ e: it.e, t: it.t, k: bingoK(it) })), pv: src.pv || 0 };
    const nextSets = Object.assign({}, cur.bingoSets, { [id]: srcSnap });
    setSets(nextSets); setSetId(id); setRound(nr);""")
rep("""    persist(Object.assign({}, cur, { bingoSetId: id, bingoRound: nr,""",
    """    persist(Object.assign({}, cur, { bingoSets: nextSets, bingoSetId: id, bingoRound: nr,""")
open(P, 'w', encoding='utf-8').write(s)
print('ok')
