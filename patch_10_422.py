# v10.422 — DNR Pub: az új kerek logó (make_pub_logo.py generálja)
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)
rep("const APP_VERSION = 'v10.421'", "const APP_VERSION = 'v10.422'")
rep("const TORTA_LOGO = 'assets/dnr_torta_logo.png';   // kör alakú, átlátszó hátterű logó (v10.401)",
    "const TORTA_LOGO = 'assets/dnr_torta_logo.png';   // kör alakú, átlátszó hátterű logó (v10.401)\nconst PUB_LOGO = 'assets/dnr_pub_logo.png';       // kör alakú, átlátszó hátterű logó (v10.422) — a főképernyő-ikon a fehér hátterű dnr_pub_icon.png")
rep("  { screen:'bar',     name:'DNR Pub',    icon:'assets/dnr_pub_icon.png',    sub:", "  { screen:'bar',     name:'DNR Pub',    icon:PUB_LOGO,                     sub:")
rep("  { key:'pub',    label:'DNR Pub',     icon:'assets/dnr_pub_icon.png',    zoom:1.9 },", "  { key:'pub',    label:'DNR Pub',     pub:true },")
rep("<img src={r.torta ? TORTA_LOGO : r.icon} alt=\"\"", "<img src={r.torta ? TORTA_LOGO : r.pub ? PUB_LOGO : r.icon} alt=\"\"")
rep("if (!r.icon && !r.torta) return", "if (!r.icon && !r.torta && !r.pub) return")
# központ: a kerek logók (Tortán, Pub) kitöltik a kört, mint a Games
rep("  const circleImg = a => (a.screen === 'home' || a.icon === TORTA_LOGO) ? 134 : ICON_FILL[a.screen] ? 160 : 112;",
    "  const circleImg = a => (a.screen === 'home' || a.icon === TORTA_LOGO || a.icon === PUB_LOGO) ? 134 : ICON_FILL[a.screen] ? 160 : 112;")
# nyitókép (?screen=bar)
rep("_dkLogo.src = _isBarDeepLink ? 'assets/splash_pub_logo.png' : 'assets/splash_box_logo.png';",
    "_dkLogo.src = _isBarDeepLink ? 'assets/dnr_pub_logo.png' : 'assets/splash_box_logo.png';")
open(P, 'w', encoding='utf-8').write(s)
print('OK')
