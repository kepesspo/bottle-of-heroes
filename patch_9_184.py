#!/usr/bin/env python3
"""patch_9_184.py — BeerPong: QR kód gomb + modal a szoba kódhoz"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.183';" in content
content = content.replace("const APP_VERSION = 'v9.183';", "const APP_VERSION = 'v9.184';")

# ── 1. Add qrcodejs CDN script before the main babel script ──
OLD_BABEL_SCRIPT = '<script type="text/babel">'
NEW_BABEL_SCRIPT = '<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>\n<script type="text/babel">'
assert OLD_BABEL_SCRIPT in content, "babel script tag not found"
content = content.replace(OLD_BABEL_SCRIPT, NEW_BABEL_SCRIPT, 1)

# ── 2. Add QRModal component before BeerPongGame ──
OLD_BP_GAME = "function BeerPongGame({ gameIdx, players, onAdvance, onResult, gameMeta, roomCode, initialBpState, onSetHideFooter }) {"
NEW_BP_GAME = """function QRModal({ url, onClose }) {
  const qrRef = React.useRef(null);
  React.useEffect(() => {
    if (!qrRef.current || typeof QRCode === 'undefined') return;
    qrRef.current.innerHTML = '';
    new QRCode(qrRef.current, { text: url, width: 260, height: 260, correctLevel: QRCode.CorrectLevel.M });
  }, [url]);
  return (
    <div onClick={onClose} style={{ position:'fixed', inset:0, zIndex:9999, background:'rgba(0,0,0,0.6)', display:'flex', alignItems:'center', justifyContent:'center', padding:24 }}>
      <div onClick={e => e.stopPropagation()} style={{ background:'#fff', borderRadius:24, padding:28, display:'flex', flexDirection:'column', alignItems:'center', gap:16, boxShadow:'0 20px 60px rgba(0,0,0,0.3)' }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:'#1B2340' }}>Csatlakozás a szobához</div>
        <div ref={qrRef} style={{ borderRadius:12, overflow:'hidden' }} />
        <div style={{ fontFamily:'monospace', fontWeight:700, fontSize:22, color:'#1B2340', letterSpacing:'0.15em' }}>{url.split('room=')[1]}</div>
        <div style={{ fontFamily:T.font, fontSize:12, color:'#94A3B8', textAlign:'center' }}>Szkenneld be a QR kódot vagy írd be a szoba kódot</div>
        <button onClick={onClose} style={{ marginTop:4, padding:'12px 32px', background:'#1B2340', border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:15, cursor:'pointer' }}>Bezár</button>
      </div>
    </div>
  );
}

function BeerPongGame({ gameIdx, players, onAdvance, onResult, gameMeta, roomCode, initialBpState, onSetHideFooter }) {"""
assert OLD_BP_GAME in content, "BeerPongGame not found"
content = content.replace(OLD_BP_GAME, NEW_BP_GAME, 1)

# ── 3. Add showQR state to BeerPongGame ──
OLD_BP_CFG = "  const bpCfg = gameMeta?.beerpongConfig || {};\n  React.useEffect(() => { if (typeof window._bohRequestNotifPermission === 'function') window._bohRequestNotifPermission(); }, []);"
NEW_BP_CFG = """  const bpCfg = gameMeta?.beerpongConfig || {};
  React.useEffect(() => { if (typeof window._bohRequestNotifPermission === 'function') window._bohRequestNotifPermission(); }, []);
  const [showQR, setShowQR] = React.useState(false);
  const joinUrl = roomCode ? (window.location.origin + window.location.pathname + '?room=' + roomCode) : '';"""
assert OLD_BP_CFG in content, "bpCfg not found"
content = content.replace(OLD_BP_CFG, NEW_BP_CFG, 1)

# ── 4. Render QRModal at top of BeerPongGame return ──
# Find the opening of BeerPongGame's main return div (after BeerPongConfetti)
OLD_CONFETTI = "          <BeerPongConfetti />"
NEW_CONFETTI = """          <BeerPongConfetti />
          {showQR && <QRModal url={joinUrl} onClose={() => setShowQR(false)} />}"""
assert OLD_CONFETTI in content, "BeerPongConfetti not found"
content = content.replace(OLD_CONFETTI, NEW_CONFETTI, 1)

# ── 5. Add QR button in VS area (between the two players) ──
OLD_VS = """          {/* VS */}
          <div style={{ display:'flex', alignItems:'center', justifyContent:'center', paddingTop:28, fontFamily:T.font, fontWeight:800, fontSize:16, color:T.inkSoft, flexShrink:0, letterSpacing:'0.06em' }}>VS</div>"""
NEW_VS = """          {/* VS + QR */}
          <div style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', paddingTop:28, gap:10, flexShrink:0 }}>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:16, color:T.inkSoft, letterSpacing:'0.06em' }}>VS</div>
            {roomCode && (
              <button onClick={() => setShowQR(true)} style={{ width:36, height:36, borderRadius:10, border:'none', background:'rgba(20,30,50,0.08)', cursor:'pointer', display:'grid', placeItems:'center', fontSize:18 }} title="QR kód">
                📲
              </button>
            )}
          </div>"""
assert OLD_VS in content, "VS div not found"
content = content.replace(OLD_VS, NEW_VS, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.184 ready")
