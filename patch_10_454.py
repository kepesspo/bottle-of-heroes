# v10.454 — „Tippek a vetítőn" kapcsoló a Szülők Vetítő fülén (revealProjector.votes, alap BE).
# Kikapcsolva a vetítőn se a számláló, se a polaroidok tipp-jele nem látszik — a tippek
# az operátornál és a Szülők panelén továbbra is számolódnak.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:140]); s = s.replace(old, new)
rep("const APP_VERSION = 'v10.453';", "const APP_VERSION = 'v10.454';")
# vetítő: a közös dokumentumból olvassa
rep("""  const [showQr, setShowQr] = React.useState(true);""", """  const [showQr, setShowQr] = React.useState(true);
  const [showVotes, setShowVotes] = React.useState(true);""")
rep("""    if (typeof v.qr === 'boolean') setShowQr(v.qr);""", """    if (typeof v.qr === 'boolean') setShowQr(v.qr);
    if (typeof v.votes === 'boolean') setShowVotes(v.votes);""")
rep("""  const meterOn = tally.boy + tally.girl > 0 && !qstate && !show;""", """  const meterOn = showVotes && tally.boy + tally.girl > 0 && !qstate && !show;""")
rep("""z={s.z} isNew={s.isNew} isCur={s.key === seq.cur.key}""", """z={s.z} isNew={s.isNew} isCur={s.key === seq.cur.key} hideVotes={!showVotes}""")
rep("""function RevealBoardCard({ item, g, z, isNew, isCur }) {""", """function RevealBoardCard({ item, g, z, isNew, isCur, hideVotes }) {""")
rep("""  const vs = wish ? [] : revealVotesOf(item);""", """  const vs = (wish || hideVotes) ? [] : revealVotesOf(item);""")
# Szülők → Vetítő fül
rep("""  const qr = v.qr !== false;
  const [msg, flash] = useRevealFlash();""", """  const qr = v.qr !== false;
  const votesOn = v.votes !== false;
  const [msg, flash] = useRevealFlash();""")
rep("""        {rvRow({ label:'Vendég QR-kód a vetítőn', right: rvSwitch(qr, () => revealCtlWrite({ qr: !qr }), 'Vendég QR-kód a vetítőn', { 'data-reveal-ctl-qr': qr ? '1' : '0' }) })}""",
"""        {rvRow({ label:'Vendég QR-kód a vetítőn', right: rvSwitch(qr, () => revealCtlWrite({ qr: !qr }), 'Vendég QR-kód a vetítőn', { 'data-reveal-ctl-qr': qr ? '1' : '0' }) })}
        {rvRow({ label: <span>Tippek a vetítőn<span style={{ display:'block', fontWeight:700, fontSize:12, color:T.inkSoft, marginTop:2 }}>Számláló alul és a jel a polaroidokon</span></span>,
          right: rvSwitch(votesOn, () => revealCtlWrite({ votes: !votesOn }), 'Tippek a vetítőn', { 'data-reveal-ctl-votes': votesOn ? '1' : '0' }) })}""")
open(P, 'w', encoding='utf-8').write(s); print('ok')
