#!/usr/bin/env python3
# v9.821: OVFJ kör-idő beállítás (1/1.5/2 perc / idő nélkül) + eredmény banner törlése új körnél
import io

PATH = "index.html"
with io.open(PATH, encoding="utf-8") as f:
    c = f.read()

edits = []

# ── 1. Config: roundTime const ──
OLD1 = "function OVFJConfigSheet({ config, setConfig, onClose }) {\n  const rounds = config.rounds ?? 5;"
NEW1 = ("function OVFJConfigSheet({ config, setConfig, onClose }) {\n  const rounds = config.rounds ?? 5;\n"
        "  const roundTime = config.roundTime === undefined ? 90 : config.roundTime;")
edits.append((OLD1, NEW1))

# ── 2. Config: add "Kör ideje" segmented control after "Körök száma" row ──
OLD2 = """            {[3,5,8,10].map(n=>(
              <button key={n} onClick={()=>setConfig(c=>({...c,rounds:n}))} style={{ width:42, padding:'8px 4px', borderRadius:9, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:14, background:rounds===n?T.mint:'transparent', color:rounds===n?'#fff':T.inkSoft, transition:'all .15s' }}>{n}</button>
            ))}
          </div>
        </div>
      </div>"""
NEW2 = """            {[3,5,8,10].map(n=>(
              <button key={n} onClick={()=>setConfig(c=>({...c,rounds:n}))} style={{ width:42, padding:'8px 4px', borderRadius:9, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:14, background:rounds===n?T.mint:'transparent', color:rounds===n?'#fff':T.inkSoft, transition:'all .15s' }}>{n}</button>
            ))}
          </div>
        </div>
        <div style={{ padding:'13px 0', borderTop:`1px solid ${T.surfaceMuted}` }}>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>Kör ideje</div>
          <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:1 }}>Mennyi idő van az íráskor</div>
          <div style={{ display:'flex', background:T.surfaceMuted, padding:4, borderRadius:12, gap:3, marginTop:8 }}>
            {[{v:60,l:'1 perc'},{v:90,l:'1:30'},{v:120,l:'2 perc'},{v:null,l:'Idő nélkül'}].map(o=>{
              const sel = roundTime===o.v;
              return (<button key={String(o.v)} onClick={()=>setConfig(c=>({...c,roundTime:o.v}))} style={{ flex:1, padding:'8px 4px', borderRadius:9, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:12, background:sel?T.mint:'transparent', color:sel?'#fff':T.inkSoft, transition:'all .15s', whiteSpace:'nowrap' }}>{o.l}</button>);
            })}
          </div>
        </div>
      </div>"""
edits.append((OLD2, NEW2))

# ── 3. Shared time formatter helper (before OVFJDrawAnim) ──
OLD3 = "// Betűsorsoló animáció — drawTs-től lokálisan fut, mindenkinél szinkronban\nfunction OVFJDrawAnim({ letter, drawTs, size }) {"
NEW3 = ("function ovfjFmtTime(sec) { if (sec == null) return ''; if (sec >= 60) { const m = Math.floor(sec/60), s = sec%60; return m + ':' + String(s).padStart(2,'0'); } return sec + 's'; }\n"
        "// Betűsorsoló animáció — drawTs-től lokálisan fut, mindenkinél szinkronban\nfunction OVFJDrawAnim({ letter, drawTs, size }) {")
edits.append((OLD3, NEW3))

# ── 4. WritingForm: show full countdown label + MM:SS when remaining set ──
OLD4 = """          {remaining != null ? (
            <>
              <div style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:remaining<=5?T.coral:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.08em'}}>Valaki kész — siess!</div>
              <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:36,color:remaining<=5?T.coral:T.ink,lineHeight:1,fontVariantNumeric:'tabular-nums'}}>{remaining}s</div>
            </>
          ) : ("""
NEW4 = """          {remaining != null ? (
            <>
              <div style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:remaining<=5?T.coral:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.08em'}}>Hátralévő idő</div>
              <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:36,color:remaining<=5?T.coral:T.ink,lineHeight:1,fontVariantNumeric:'tabular-nums'}}>{ovfjFmtTime(remaining)}</div>
            </>
          ) : ("""
edits.append((OLD4, NEW4))

# ── 5. Host: reset ovfjState init includes roundTime ──
OLD5 = "    syncRoom(roomCode, { ovfjTakenIds: [], ovfjState: { sess, phase:'pick', round:1, totalRounds, letter:null, drawTs:null, doneAt:null, hostPid:null } });"
NEW5 = "    syncRoom(roomCode, { ovfjTakenIds: [], ovfjState: { sess, phase:'pick', round:1, totalRounds, roundTime, letter:null, drawTs:null, doneAt:null, hostPid:null } });"
edits.append((OLD5, NEW5))

# ── 6. Host: roundTime const near totalRounds ──
OLD6 = "  const totalRounds = gameMeta?.ovfjConfig?.rounds ?? 5;"
NEW6 = ("  const totalRounds = gameMeta?.ovfjConfig?.rounds ?? 5;\n"
        "  const roundTime = gameMeta?.ovfjConfig?.roundTime === undefined ? 90 : gameMeta.ovfjConfig.roundTime;")
edits.append((OLD6, NEW6))

# ── 7. Host: write roundTime into ovfjState sync ──
OLD7 = ("    syncRoom(roomCode, { ovfjState: { sess, phase, round, totalRounds, letter, drawTs, doneAt, hostPid, answers, roundScores, cumScores } });\n"
        "  }, [phase, round, letter, drawTs, doneAt, hostPid, answers, roundScores, cumScores]);")
NEW7 = ("    syncRoom(roomCode, { ovfjState: { sess, phase, round, totalRounds, roundTime, letter, drawTs, doneAt, hostPid, answers, roundScores, cumScores } });\n"
        "  }, [phase, round, letter, drawTs, doneAt, hostPid, answers, roundScores, cumScores]);")
edits.append((OLD7, NEW7))

# ── 8. Host: ticker runs whenever a timer is active (roundTime set) or someone done ──
OLD8 = """  // Ticker a visszaszámláláshoz
  React.useEffect(() => {
    if (!(phase === 'writing' && doneAt)) return;
    const id = setInterval(() => setTick(t => t + 1), 250);
    return () => clearInterval(id);
  }, [phase, doneAt]);"""
NEW8 = """  // Ticker a visszaszámláláshoz (teljes kör-idő vagy \"valaki kész\" gyorsító)
  React.useEffect(() => {
    if (!(phase === 'writing' && (roundTime != null || doneAt))) return;
    const id = setInterval(() => setTick(t => t + 1), 250);
    return () => clearInterval(id);
  }, [phase, doneAt, roundTime]);"""
edits.append((OLD8, NEW8))

# ── 9. Host: remaining computation (full timer capped by 10s once someone done) ──
OLD9 = "  const remaining = (phase === 'writing' && doneAt) ? Math.max(0, Math.ceil((doneAt + 10000 - Date.now()) / 1000)) : null;"
NEW9 = """  const writingStart = drawTs != null ? drawTs + OVFJ_DRAW_MS : null;
  const remaining = (() => {
    if (phase !== 'writing') return null;
    if (roundTime == null) return doneAt ? Math.max(0, Math.ceil((doneAt + 10000 - Date.now()) / 1000)) : null;
    let deadline = (writingStart != null ? writingStart : Date.now()) + roundTime * 1000;
    if (doneAt) deadline = Math.min(deadline, doneAt + 10000);
    return Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
  })();"""
edits.append((OLD9, NEW9))

# ── 10. Host: end-writing trigger — fire when remaining hits 0 (either timer) ──
OLD10 = """  React.useEffect(() => {
    if (phase !== 'writing' || !doneAt) return;
    if (Date.now() >= doneAt + 10000) endWriting();
  });"""
NEW10 = """  React.useEffect(() => {
    if (phase !== 'writing') return;
    if ((roundTime != null || doneAt) && remaining === 0) endWriting();
  });"""
edits.append((OLD10, NEW10))

# ── 11. Host: clear result banner when starting next round ──
OLD11 = """  const nextRound = () => {
    if (round >= totalRounds) { setPhase('final'); onAdvance && onAdvance({}); return; }
    calcRef.current = false;"""
NEW11 = """  const nextRound = () => {
    if (round >= totalRounds) { setPhase('final'); onAdvance && onAdvance({}); return; }
    onResult && onResult(null);
    calcRef.current = false;"""
edits.append((OLD11, NEW11))

# ── 12. Observer: ticker runs for full timer too ──
OLD12 = """  // Ticker a visszaszámláláshoz
  React.useEffect(() => {
    if (!(ovfj.phase === 'writing' && ovfj.doneAt)) return;
    const id = setInterval(() => setTick(t => t + 1), 250);
    return () => clearInterval(id);
  }, [ovfj.phase, ovfj.doneAt]);"""
NEW12 = """  // Ticker a visszaszámláláshoz (teljes kör-idő vagy \"valaki kész\" gyorsító)
  React.useEffect(() => {
    const rt = ovfj.roundTime === undefined ? 90 : ovfj.roundTime;
    if (!(ovfj.phase === 'writing' && (rt != null || ovfj.doneAt))) return;
    const id = setInterval(() => setTick(t => t + 1), 250);
    return () => clearInterval(id);
  }, [ovfj.phase, ovfj.doneAt, ovfj.roundTime]);"""
edits.append((OLD12, NEW12))

# ── 13. Observer: remaining computation mirrors host ──
OLD13 = "  const remaining = (ovfj.phase === 'writing' && ovfj.doneAt) ? Math.max(0, Math.ceil((ovfj.doneAt + 10000 - Date.now()) / 1000)) : null;"
NEW13 = """  const obsRoundTime = ovfj.roundTime === undefined ? 90 : ovfj.roundTime;
  const obsWritingStart = ovfj.drawTs != null ? ovfj.drawTs + OVFJ_DRAW_MS : null;
  const remaining = (() => {
    if (ovfj.phase !== 'writing') return null;
    if (obsRoundTime == null) return ovfj.doneAt ? Math.max(0, Math.ceil((ovfj.doneAt + 10000 - Date.now()) / 1000)) : null;
    let deadline = (obsWritingStart != null ? obsWritingStart : Date.now()) + obsRoundTime * 1000;
    if (ovfj.doneAt) deadline = Math.min(deadline, ovfj.doneAt + 10000);
    return Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
  })();"""
edits.append((OLD13, NEW13))

# ── 14. Version bump ──
OLD14 = "const APP_VERSION = 'v9.820';"
NEW14 = "const APP_VERSION = 'v9.821';"
edits.append((OLD14, NEW14))

for i, (o, n) in enumerate(edits, 1):
    assert o in c, f"edit {i} OLD not found"
    assert c.count(o) == 1, f"edit {i} OLD not unique ({c.count(o)})"
    c = c.replace(o, n)

with io.open(PATH, "w", encoding="utf-8") as f:
    f.write(c)

print(f"OK — {len(edits)} edits applied")
