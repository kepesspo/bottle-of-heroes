# v10.345 - Az Imposztorrol lekerul a DNR exkluziv jeloles
#
# A jelolo a `GAMES[]` bejegyzesen a `dnr:true` mezo (CLAUDE.md v10.314) — a
# `category` NEM valtozik, az marad `Csapat`. Ket helyre hatott, es mindketto
# magatol kovet:
#   • a Szures „DNR Exkluziv" sora (`f === 'DNR'`),
#   • a jatekkartyan a ★ DNR EXKLUZIV szalag.
#
# A `config/homeConfig.dnrAppsEnabled` kapcsolohoz ennek SEMMI koze: az a
# fooldal alji „TOVABBI DNR" sort kapcsolja.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

OLD = "IMGS['imposztor_banner.png'], dnr:true, color:"
NEW = "IMGS['imposztor_banner.png'], color:"
assert src.count(OLD) == 1, 'imposztor dnr jelolo: %d talalat' % src.count(OLD)
src = src.replace(OLD, NEW)

src = src.replace("const APP_VERSION = 'v10.344';", "const APP_VERSION = 'v10.345';")
assert "v10.345" in src

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_345 alkalmazva')
