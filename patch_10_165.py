# v10.165 — a kortyolasi limit kikerul a Jatekmenet oldalrol
#
# A limit a PROFILRA mentodik, nem a partira. Egy partinkenti kepernyon
# megkerdezni azt sugallja, hogy "ma estere" allitod — kozben tartosan
# atirja a profilt. Ez felrevezeto, es olyat kerdez minden buli elott, amit
# egyszer kell vegigmenni mindenkinel.
#
# A szerkesztes helye valtozatlanul az Admin > Tartalom > Profilok.
# A limit MUKODESE nem valtozik: a jatek tovabbra is figyelmeztet a kor vegen.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# a szekcio
a = s.index('        {withProfile.length > 0 && (')
b = s.index('          </Section>\n        )}\n', a) + len('          </Section>\n        )}\n')
assert 'KORTYOLÁSI' in s[a:b].upper() or 'Kortyolási limit' in s[a:b], s[a:a+200]
s = s[:a] + s[b:]

# a hozza tartozo allapot es betoltes
for frag in [
    "  const [limits, setLimits] = React.useState({});   // profileId -> limit (szam vagy '')\n",
    "  const [limitsLoaded, setLimitsLoaded] = React.useState(false);\n",
    "  const [limitsOpen, setLimitsOpen] = React.useState(false);\n",
    "  const limitCount = withProfile.filter(p => Number(limits[p.profileId]) > 0).length;\n",
    "  const withProfile = (players || []).filter(p => p.profileId);\n",
]:
    assert s.count(frag) == 1, frag[:60]
    s = s.replace(frag, '')

e = s.index('  React.useEffect(() => {\n    if (!withProfile.length')
e2 = s.index('  }, [players]);\n', e) + len('  }, [players]);\n')
s = s[:e] + s[e2:]

w = s.index('  const writeLimit = (profileId, raw) => {')
w2 = s.index('  };\n', w) + len('  };\n')
s = s[:w] + s[w2:]

assert 'limits' not in s[s.index('function SetupScreen'):s.index('function SetupScreen')+4000], 'maradt limit-hivatkozas'

# a Section osszecsukhato aga igy hasznalat nelkul marad — a `title` nelkuli
# valtozatot senki nem hivja tobbe, de a komponens tovabbra is hasznalatban van
# nem, egyik szekcio sem hasznalja mar → nezzuk meg
print('Section hasznalat a SetupScreen-ben:', s[s.index('function SetupScreen'):s.index('function SetupScreen')+6000].count('<Section'))

# a profil-limit iro segedfuggveny csak innen hivodott
sp = s.index('  window.setProfileDrinkLimit = function(profileId, limit) {')
sp2 = s.index('  };\n', s.index('.catch(function(e) { console.warn(\'setProfileDrinkLimit\'', sp)) + len('  };\n')
s = s[:sp] + s[sp2:]
assert 'setProfileDrinkLimit' not in s

s = s.replace("const APP_VERSION = 'v10.164';", "const APP_VERSION = 'v10.165';", 1)
assert "v10.165" in s and s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK')
