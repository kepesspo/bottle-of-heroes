# v10.437 — Gender Reveal: az operátor csak feltölt (nincs kamera-gomb)
p = 'app.src.html'
s = open(p, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.436';", "const APP_VERSION = 'v10.437';")
# az operátor a saját fényképezőjével (saját beállításokkal) készít képet, és azt tölti fel —
# az appból nem fotóz. A VENDÉG nézet kamera-gombja marad.
rep("""  const pickRef = React.useRef(null), camRef = React.useRef(null);
  const onFiles = (fl) => {
    const files = revealImageFiles(fl);
    if (!files.length) return;
    setErrs([]);""", """  // v10.437: az operátor NEM fotóz az appból — a saját kamerájával, saját beállításokkal
  // készíti a képet, és csak feltölti. (A vendég nézetben a fotó gomb marad.)
  const pickRef = React.useRef(null);
  const onFiles = (fl) => {
    const files = revealImageFiles(fl);
    if (!files.length) return;
    setErrs([]);""")
rep("""          <div style={{ display:'flex', gap:10 }}>
            <button data-reveal-camera onClick={() => camRef.current && camRef.current.click()} style={bigBtn(true)}><span style={{ fontSize:28 }}>📷</span>Fotó készítése</button>
            <button data-reveal-pick onClick={() => pickRef.current && pickRef.current.click()} style={bigBtn(false)}><span style={{ fontSize:28 }}>🖼️</span>Képek kiválasztása</button>
          </div>
          <input ref={camRef} type="file" accept="image/*" capture="environment" style={{ display:'none' }} onChange={e => { onFiles(e.target.files); e.target.value = ''; }} />
""", """          <div style={{ display:'flex', gap:10 }}>
            <button data-reveal-pick onClick={() => pickRef.current && pickRef.current.click()} style={bigBtn(true)}><span style={{ fontSize:28 }}>🖼️</span>Képek feltöltése</button>
          </div>
""")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
