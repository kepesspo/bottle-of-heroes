# v10.480 — az OTP Gála szett címéről lekerül a 🎤 (tulajdonosi kérés). pv 3 → 4: szettváltáskor a
# friss (mikrofon nélküli) preset jön; a már aktív szetten az „Alap lista visszatöltése" + Mentés hozza.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)
rep("const APP_VERSION = 'v10.479';", "const APP_VERSION = 'v10.480';")
rep("""  otp: { name:'OTP Gála', pv:3, title:'OTP Gála Bingó', titleEmoji:'🎤',""",
    """  otp: { name:'OTP Gála', pv:4, title:'OTP Gála Bingó', titleEmoji:'',""")
open(P, 'w', encoding='utf-8').write(s)
print('OK')
