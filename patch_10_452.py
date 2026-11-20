# v10.452 — a vetítő képszámlálója és a várakozó-jelzés EGY kicsi, halk csipben bal alul
# (a szervezőknek szóló visszajelzés, nem a vendégeknek). A Szülői kód admin-mezője figyelmeztet.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:140]); s = s.replace(old, new)
rep("const APP_VERSION = 'v10.451';", "const APP_VERSION = 'v10.452';")
rep("""  const boardH = vp.h - Math.max(meterOn ? vp.h * (1 - REVEAL_METER_ROOM) : 0, qrRoom);""",
    """  // v10.452: a bal alsó szervezői csip helye is fenn van tartva (kicsi — a lapok alig kisebbek)
  const statusRoom = (!qstate && !show) ? Math.round(Math.max(30, vp.h * 0.045)) : 0;
  const boardH = vp.h - Math.max(meterOn ? vp.h * (1 - REVEAL_METER_ROOM) : 0, qrRoom, statusRoom);""")
rep("""  const cornersOn = !qstate && !show;
  const cornerTop = narrow ? 56 : 'max(3vh, 74px)';
  const cornerChip = { position:'absolute', top:cornerTop, zIndex:45, display:'inline-flex', alignItems:'center', gap:'0.8vh', whiteSpace:'nowrap', padding: narrow ? '6px 12px' : '0.9vh 1.4vw', borderRadius:999,
    fontFamily:T.font, fontWeight:900, fontSize:'clamp(13px, 2.2vh, 26px)', boxShadow:'0 0.6vh 1.8vh rgba(60,40,20,0.12)' };""",
"""  const cornersOn = !qstate && !show;""")
i = s.index("      {cornersOn && (\n        <div data-reveal-topm data-reveal-tally")
j = s.index("      {showQr && qrUrl && !qstate && !show && !narrow && (", i)
s = s[:i] + """      {/* v10.452: a SZERVEZŐKNEK szóló halk visszajelzés — bal alul, kicsiben: hány kép van
          kint, és van-e jóváhagyásra váró (akkor egy borostyán szám villan mellette). */}
      {cornersOn && (
        <div data-reveal-tally style={{ position:'absolute', left:'1.2vw', bottom:'1.2vh', zIndex:45, display:'inline-flex', alignItems:'center', gap:6, whiteSpace:'nowrap',
          padding:'3px 9px', borderRadius:999, background:'rgba(255,255,255,0.72)', border:'1px solid #EFE2D2', color:REVEAL_INK, opacity:0.8,
          fontFamily:T.font, fontWeight:800, fontSize:'clamp(10px, 1.3vh, 14px)' }}>
          <span aria-hidden="true">📷</span><span data-reveal-count>{nPhotos} kép</span>
          {nWish > 0 && <React.Fragment><span aria-hidden="true" style={{ opacity:0.35 }}>·</span><span aria-hidden="true">💌</span><span data-reveal-wishcount>{nWish}</span></React.Fragment>}
          {pendingN > 0 && <span data-reveal-pendbadge={pendingN} title={pendingN + ' jóváhagyásra vár'} style={{ display:'inline-flex', alignItems:'center', gap:4, marginLeft:2, color:'#7A4F00' }}>
            <span aria-hidden="true" style={{ opacity:0.35, color:REVEAL_INK }}>·</span>
            <span style={{ minWidth:'1.5em', height:'1.5em', padding:'0 0.35em', boxSizing:'border-box', borderRadius:999, background:'#E0A020', color:'#fff', display:'grid', placeItems:'center', fontWeight:900 }}>{pendingN}</span>vár</span>}
        </div>
      )}
""" + s[j:]
# a Szülői kód: betűs régi kódnál figyelmeztetés (a számbillentyűzet csak számkódnál jön)
rep("""        <input data-admin-reveal-code value={code} inputMode="numeric" onChange={e => setCode(e.target.value.replace(/\\D/g, '').slice(0, 12))} placeholder="pl. 2026" style={inpSt} />""",
    """        <input data-admin-reveal-code value={code} inputMode="numeric" onChange={e => setCode(e.target.value.replace(/\\D/g, '').slice(0, 12))} placeholder="pl. 2026" style={inpSt} />
        {code && !revealIsNumCode(code) && <div style={{ fontFamily:T.font, fontWeight:800, fontSize:12, color:'#A3342C', marginTop:6 }}>A régi szülői kód betűket tartalmaz — adj meg számkódot (csak így jön a számbillentyűzet).</div>}""")
open(P, 'w', encoding='utf-8').write(s); print('ok')
