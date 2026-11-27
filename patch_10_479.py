# v10.479 — új téma: „OTP zöld" (az OTP Gálához). A THEMES-be, a THEME_LIST-be (admin Témák
# választó) és a nyitókép ES5-ös téma-táblájába (a config ELŐTT fut, külön másolat).
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.478';", "const APP_VERSION = 'v10.479';")
rep("""  slate: {
    bg: '#1E2A38', bgSoft: '#263444', bgDeep: '#121C28',""",
"""  // v10.479: OTP zöld — a háttér az OTP márkazöldje (#52AE30). A tinta sötétzöld (a zöld háttéren
  // 5,9:1, fehér kártyán 16:1); az akció-szín (mint) mélyzöld, hogy a fehér felirat olvasható
  // legyen rajta (6:1), és a zöld háttértől is elváljon.
  otp: {
    bg: '#52AE30', bgSoft: '#68BC48', bgDeep: '#3F9122',
    surface: '#FFFFFF', surfaceMuted: '#EAF6E3',
    ink: '#0C2410', inkSoft: '#173F14', inkMute: '#2B5524',
    mint: '#1E7316', mintSoft: '#D6EFCB', mintDeep: '#155A0F',
    coral: '#E05040', coralSoft: '#FFE0DA',
    purple: '#7A50C0', yellow: '#E6B800', yellowText: '#7A6200', blue: '#2F78C0', pink: '#D05090',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900, weightTitle: 800, weightBody: 600,
    letter: '-0.01em', letterDisplay: '-0.02em',
    shadow: '0 5px 0 rgba(10,60,10,0.22), 0 12px 28px rgba(10,60,10,0.18)',
    shadowPill: '0 2px 0 rgba(10,60,10,0.22), 0 2px 6px rgba(10,60,10,0.18)',
    shadowLift: '0 4px 0 rgba(10,60,10,0.10), 0 12px 32px rgba(10,60,10,0.18)',
    playBg: 'linear-gradient(160deg, #52AE30 0%, #3F9122 100%)',
    bgOverlay: 'rgba(6, 40, 10, 0.96)',
  },
  slate: {
    bg: '#1E2A38', bgSoft: '#263444', bgDeep: '#121C28',""")
rep("""  { key:'slate', label:'Mélytenger' },
];""", """  { key:'slate', label:'Mélytenger' },
  { key:'otp',   label:'OTP zöld'   },
];""")
rep("""    midnight: { bg:'#28204A', deep:'#1A1435', ring:'rgba(100,70,220,0.35)', glow:'rgba(130,90,250,0.7)',  ink:'#ECE8FC', inkSoft:'#A898D0' },
  };""", """    midnight: { bg:'#28204A', deep:'#1A1435', ring:'rgba(100,70,220,0.35)', glow:'rgba(130,90,250,0.7)',  ink:'#ECE8FC', inkSoft:'#A898D0' },
    otp:      { bg:'#52AE30', deep:'#3F9122', ring:'rgba(20,90,20,0.35)',   glow:'rgba(30,110,30,0.7)',   ink:'#0C2410', inkSoft:'#173F14' },
  };""")
open(P, 'w', encoding='utf-8').write(s)
print('OK')
