# v10.431: Gender Reveal — a jelszót MINDIG bekéri, nem menti el
p = 'app.src.html'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
rep("const APP_VERSION = 'v10.430';", "const APP_VERSION = 'v10.431';")
rep("  const [saved, setSaved] = React.useState(() => revealStore('boh_reveal_pw') || '');",
    "  // ⚠️ A jelszót NEM mentjük (tulajdonosi döntés, v10.431): minden megnyitáskor bekéri.\n"
    "  // Csak a munkamenetre él; a v10.430-ban esetleg eltárolt értéket is töröljük.\n"
    "  const [saved, setSaved] = React.useState('');\n"
    "  React.useEffect(() => { try { localStorage.removeItem('boh_reveal_pw'); } catch(e) {} }, []);")
rep("    if (inp.trim() && inp.trim() === pw) { revealStore('boh_reveal_pw', inp.trim()); setSaved(inp.trim()); setBad(false); setInp(''); }",
    "    if (inp.trim() && inp.trim() === pw) { setSaved(inp.trim()); setBad(false); setInp(''); }")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
