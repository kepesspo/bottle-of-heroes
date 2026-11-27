# v10.479 (2. rész) — a Bingó vendég-név mezője ne a téma alapszínét (T.bg) viselje: OTP témán erős
# zöld mező lett belőle a fehér kártyán. Halvány felület-szín (T.surfaceMuted) minden témán jó.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)
rep("""height:46, borderRadius:12, border:`1.5px solid ${T.border}`, background:T.bg, padding:'0 12px', fontFamily:T.font, fontWeight:700, fontSize:15, color:T.ink, outline:'none' }} />""",
    """height:46, borderRadius:12, border:`1.5px solid ${T.border}`, background:T.surfaceMuted || T.surface, padding:'0 12px', fontFamily:T.font, fontWeight:700, fontSize:15, color:T.ink, outline:'none' }} />""")
open(P, 'w', encoding='utf-8').write(s)
print('OK')
