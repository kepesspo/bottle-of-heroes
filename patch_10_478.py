# v10.478 — OTP Gála: 36 szó (+12, OTP-hez és a gálabeszédekhez kötve). 36 > 24 mező → mindenki egy
# SAJÁT, véletlen 24-et kap, így tényleg számít, kinek a kártyáján van egy szó. pv 2 → 3.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.477';", "const APP_VERSION = 'v10.478';")
rep("""  otp: { name:'OTP Gála', pv:2,""", """  // v10.478: 36 szó → mindenki a 36-ból egy saját 24-et kap (a 24 mezőbe különben MINDENKINEK
  // ugyanaz a 24 kerülne, és a „csak az iszik, akinek a kártyáján van" szabály semmit nem szűrne)
  otp: { name:'OTP Gála', pv:3,""")
rep("""      { e:'👥', t:'Csapatmunka', k:1 }, { e:'♟️', t:'Stratégia', k:1 }, { e:'🙏', t:'Köszönöm a figyelmet', k:1 },
    ] },""",
"""      { e:'👥', t:'Csapatmunka', k:1 }, { e:'♟️', t:'Stratégia', k:1 }, { e:'🙏', t:'Köszönöm a figyelmet', k:1 },
      { e:'🟢', t:'OTP Csoport', k:1 }, { e:'📱', t:'Simple app', k:2 }, { e:'🏠', t:'Lakáshitel', k:2 },
      { e:'📉', t:'Infláció', k:2 }, { e:'💹', t:'Kamat', k:1 }, { e:'🗺️', t:'Régió', k:2 },
      { e:'🏆', t:'Díj', k:1 }, { e:'🎓', t:'Pénzügyi tudatosság', k:3 }, { e:'🚀', t:'Jövő', k:1 },
      { e:'🔗', t:'Partnerség', k:2 }, { e:'📊', t:'Részvényesek', k:3 }, { e:'🌟', t:'Tehetség', k:2 },
    ] },""")
open(P, 'w', encoding='utf-8').write(s)
print('OK')
