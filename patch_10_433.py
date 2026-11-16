# v10.433: Gender Reveal — polaroid-fal (több kép egyszerre), papíros Babakvíz a PDF
# 20 kérdésével, a videó a visszaszámlálás után indul, telefonos vetítő; DNR admin PIN.
import sys
p = 'app.src.html'
s = open(p, encoding='utf-8').read()
a = s.index('// ── Gender Reveal: élő képvetítő kivetítőre (v10.430')
b = s.index('// ── Pub: saját keverés űrlap (új / szerkesztés)')
block = open(sys.argv[1] if len(sys.argv) > 1 else 'patch_10_433_reveal.jsx', encoding='utf-8').read()
s = s[:a] + block + s[b:]
def rep(x, y):
    global s
    assert s.count(x) == 1, x[:70]
    s = s.replace(x, y)
rep("const APP_VERSION = 'v10.432';", "const APP_VERSION = 'v10.433';")
# A DNR központ admin-belépője (tulajdonosi kérés)
rep("    if (pinVal === '199509') { setPinVal(''); onOk(); }",
    "    if (pinVal === DNR_ADMIN_PIN) { setPinVal(''); onOk(); }")
rep("function AdminPinModal({ onOk, onClose }) {",
    "// A DNR központ admin-gombjának belépő kódja (v10.433-tól 202703).\nconst DNR_ADMIN_PIN = '202703';\nfunction AdminPinModal({ onOk, onClose }) {")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
