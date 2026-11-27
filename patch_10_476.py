# v10.476 — DNR központ: a kör-ikon gyűrűje a KÉP FÖLÖTT. Az `inset box-shadow` a tartalom
# ALÁ festődik, ezért a négyzetes, fehér hátterű ikon (Bingó…) sarkai átlósan eltakarták a gyűrűt.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.475';", "const APP_VERSION = 'v10.476';")
rep("""                      <span style={{ width:160, height:160, borderRadius:'50%', background:'#fff', display:'grid', placeItems:'center', marginTop: a.screen === 'home' ? 0 : 30, boxShadow:'inset 0 0 0 6px rgba(242,169,59,0.35)', overflow:'hidden' }}>
                        <img src={a.icon} alt="" style={{ width:circleImg(a), height:circleImg(a) }} />
                      </span>""",
"""                      <span data-hub-circle style={{ position:'relative', width:160, height:160, borderRadius:'50%', background:'#fff', display:'grid', placeItems:'center', marginTop: a.screen === 'home' ? 0 : 30, overflow:'hidden' }}>
                        <img src={a.icon} alt="" style={{ width:circleImg(a), height:circleImg(a) }} />
                        {/* v10.476: a gyűrű KÜLÖN réteg a kép fölött — `inset box-shadow`-ként a kép
                            alá festődött, és a négyzetes ikon fehér sarkai átlósan kitakarták */}
                        <span data-hub-ring aria-hidden="true" style={{ position:'absolute', inset:0, borderRadius:'50%', boxShadow:'inset 0 0 0 6px rgba(242,169,59,0.35)', pointerEvents:'none' }} />
                      </span>""")
open(P, 'w', encoding='utf-8').write(s)
print('OK')
