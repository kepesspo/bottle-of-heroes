# v10.423 — egységes app-ikonok a DNR Games stílusában (make_unified_icons.py)
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)
rep("const APP_VERSION = 'v10.422'", "const APP_VERSION = 'v10.423'")
# a két márka-logó helyett is az egységes (átlátszó) jel
rep("const TORTA_LOGO = 'assets/dnr_torta_logo.png';   // kör alakú, átlátszó hátterű logó (v10.401)",
    "// v10.423: az egységes ikoncsalád átlátszó változata (make_unified_icons.py). A korábbi\n// márka-logók (dnr_torta_logo.png, dnr_pub_logo.png) a repóban maradtak, de nem hivatkozzuk őket.\nconst TORTA_LOGO = 'assets/dnr_torta_mark.png';")
rep("const PUB_LOGO = 'assets/dnr_pub_logo.png';       // kör alakú, átlátszó hátterű logó (v10.422) — a főképernyő-ikon a fehér hátterű dnr_pub_icon.png",
    "const PUB_LOGO = 'assets/dnr_pub_mark.png';")
# nyitóképek: az átlátszó jel (a fehér négyzet a téma-hátteren kilógna)
rep('<img id="splash-events-logo" src="assets/splash_events_logo.png"', '<img id="splash-events-logo" src="assets/dnr_events_mark.png"')
rep("brand={icon:'assets/dnr_events_icon.png', title:'DNR Events'", "brand={icon:'assets/dnr_events_mark.png', title:'DNR Events'")
rep("? {icon:'assets/dnr_torta_logo.png', title:_bt||'DNR a tortán'", "? {icon:'assets/dnr_torta_mark.png', title:_bt||'DNR a tortán'")
rep("? {icon:'assets/dnr_tipp_icon.png', title:'DNR Tipp'", "? {icon:'assets/dnr_tipp_mark.png', title:'DNR Tipp'")
rep(": {icon:'assets/dnr_bingo_icon.png', title:'DNR Bingó'", ": {icon:'assets/dnr_bingo_mark.png', title:'DNR Bingó'")
rep("brand={icon:'assets/dnr_liga_icon.png', title:'DNR Liga'", "brand={icon:'assets/dnr_liga_mark.png', title:'DNR Liga'")
rep("_dkLogo.src = _isBarDeepLink ? 'assets/dnr_pub_logo.png' : 'assets/splash_box_logo.png';",
    "_dkLogo.src = _isBarDeepLink ? 'assets/dnr_pub_mark.png' : 'assets/dnr_box_mark.png';")
# admin: az új ikonok margója a Games-éhez igazodik → ugyanaz a rávágás mindenhol
for k in ('events', 'tipp', 'bingo', 'liga'):
    rep("icon:'assets/dnr_%s_icon.png', zoom:1.9, tabs:" % k, "icon:'assets/dnr_%s_icon.png', zoom:1.25, tabs:" % k)
rep("{ key:'torta', label:'DNR a tortán', icon:TORTA_LOGO, tabs:", "{ key:'torta', label:'DNR a tortán', icon:TORTA_LOGO, zoom:1.25, tabs:")
import re
s, n = re.subn(r"(icon:'assets/dnr_(?:events|tipp|bingo|liga)_icon\.png',\s*)zoom:1\.9 \}", r"\1zoom:1.25 }", s)
assert n == 4, n
rep("  { key:'box',    label:'DNR BOX',     icon:'assets/dnr_box_icon.png' },", "  { key:'box',    label:'DNR BOX',     icon:'assets/dnr_box_icon.png',    zoom:1.25 },")
rep("  { key:'torta',  label:'DNR a tortán', torta:true },", "  { key:'torta',  label:'DNR a tortán', torta:true, zoom:1.25 },")
rep("  { key:'pub',    label:'DNR Pub',     pub:true },", "  { key:'pub',    label:'DNR Pub',     pub:true, zoom:1.25 },")
# központ: minden ikon ugyanabban a kompozícióban → mind a Games méretén áll
rep("""  const ICON_FILL = { jukebox: 1 };
  const circleImg = a => (a.screen === 'home' || a.icon === TORTA_LOGO || a.icon === PUB_LOGO) ? 134 : ICON_FILL[a.screen] ? 160 : 112;""",
"""  // v10.423: az egységes ikoncsalád minden tagja a Games ikon kompozícióját követi
  // (félkör-háttér, talajvonal, azonos margó), tehát mind ugyanakkora a körben.
  const circleImg = () => 134;""")
rep("<img src={a.icon} alt=\"\" style={{ width:circleImg(a), height:circleImg(a), borderRadius: circleImg(a) === 112 ? '28%' : 0 }} />",
    "<img src={a.icon} alt=\"\" style={{ width:circleImg(a), height:circleImg(a) }} />")
open(P, 'w', encoding='utf-8').write(s)
print('OK')
