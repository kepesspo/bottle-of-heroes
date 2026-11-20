# v10.453 — a „Visszaszámláló a vetítőn" kapcsoló a Szülők VETÍTŐ fülére költözik
# (a vetítő megjelenését állítja, nem a leleplezést). Az adat ugyanaz: revealConfig.countdownOn.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:140]); s = s.replace(old, new)
rep("const APP_VERSION = 'v10.452';", "const APP_VERSION = 'v10.453';")
rep("""        {rvRow({ icon:'timer', tone:'ok', label:'Visszaszámláló a vetítőn', right: rvSwitch(cdOn, () => saveCfg({ countdownOn: !cdOn }), 'Visszaszámláló a vetítőn', { 'data-reveal-p-countdown':'' }) })}
""", "")
rep("""function RevealProjectorPanel() {
  const ctl = useRevealDoc('revealProjector');""", """function RevealProjectorPanel() {
  const ctl = useRevealDoc('revealProjector');
  // v10.453: a visszaszámláló kapcsolója is itt (a vetítő felső közepén jelenik meg)
  const rcfg = useRevealCfg(), rv = rcfg.v || {};
  const cdOn = rv.countdownOn !== false, hasAt = +(rv.revealAt || 0) > 0;
  const [cdMsg, cdFlash] = useRevealFlash();
  const saveCd = on => { const db = revealDb(); if (db) db.collection('config').doc('revealConfig').set({ countdownOn: on }, { merge:true })
    .then(() => cdFlash('Mentve')).catch(e => cdFlash('Nem sikerült (' + ((e && e.code) || 'hiba') + ')')); };""")
rep("""        {rvRow({ label:'Vendég QR-kód a vetítőn', right: rvSwitch(qr, () => revealCtlWrite({ qr: !qr }), 'Vendég QR-kód a vetítőn', { 'data-reveal-ctl-qr': qr ? '1' : '0' }) })}""",
"""        {rvRow({ label:'Vendég QR-kód a vetítőn', right: rvSwitch(qr, () => revealCtlWrite({ qr: !qr }), 'Vendég QR-kód a vetítőn', { 'data-reveal-ctl-qr': qr ? '1' : '0' }) })}
        {rvRow({ label: <span>Visszaszámláló a vetítőn{!hasAt && <span data-reveal-p-countdownnote style={{ display:'block', fontWeight:700, fontSize:12, color:T.inkSoft, marginTop:2 }}>Időpont nélkül nem látszik (Leleplezés fül)</span>}{cdMsg && <span style={{ display:'block', marginTop:2 }}>{rvMsg(cdMsg)}</span>}</span>,
          right: rvSwitch(cdOn, () => saveCd(!cdOn), 'Visszaszámláló a vetítőn', { 'data-reveal-p-countdown':'' }) })}""")
rep("  const cdOn = v.countdownOn !== false;\n", "")
open(P, 'w', encoding='utf-8').write(s); print('ok')
