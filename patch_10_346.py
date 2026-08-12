# v10.346 - A Kisebb / Nagyobb-rol lekerul a DNR exkluziv jeloles
#
# Ugyanaz a jelolo, mint az Imposztornal (v10.345): a `GAMES[]` bejegyzesen a
# `dnr:true` mezo. A `category` NEM valtozik (marad `Csapat`), es az
# `observer:true` sem — az a telefonos nezet, semmi koze a DNR-hez.
#
# Ket helyre hatott, es mindketto magatol koveti a mezot:
#   • a Szures „DNR Exkluziv" sora (`f === 'DNR'`),
#   • a jatekkartyan a ★ DNR EXKLUZIV szalag.
#
# ⚠️ A `kisebb` bejegyzes TOBBSOROS (a `stakeOf:(m)=>{ ... }` miatt), tehat a
# `dnr:true` NEM a `{ id:'kisebb'` sorban van — soralapu kereses elvetene.
# Ezert a horgony a banner + jelolo + observer harmas.
#
# A `config/homeConfig.dnrAppsEnabled` kapcsolohoz ennek SEMMI koze: az a
# fooldal alji „TOVABBI DNR" sort kapcsolja.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

OLD = "IMGS['kisebb_banner.png'], dnr:true, observer:true, color:"
NEW = "IMGS['kisebb_banner.png'], observer:true, color:"
assert src.count(OLD) == 1, 'kisebb dnr jelolo: %d talalat' % src.count(OLD)
src = src.replace(OLD, NEW)

# a marado kor: blackjack, beerpong, powerhour, ovfj (+ a busz, ami azonositoval
# van bedrotozva a szuroben)
assert src.count('dnr:true') == 8, 'maradt dnr:true: %d' % src.count('dnr:true')

src = src.replace("const APP_VERSION = 'v10.345';", "const APP_VERSION = 'v10.346';")
assert "v10.346" in src

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_346 alkalmazva')
