# v10.167 — a Netflix-nezet kivezetese a Jatekok oldalrol
#
# "kb soha nem hasznaltuk". A racsos nezet volt az alapertelmezes, a Netflix
# csak akkor jott elo, ha valaki egyszer atkapcsolta. Ket parhuzamos elrendezes
# ket kulon csempe-komponenssel — minden kartya-valtoztatast ketszer kellett
# elvegezni, es epp ilyenbol szuletnek az elcsuszasok.
#
# Akinel a boh_games_view 'netflix'-en ragadt, az mostantol a racsot kapja:
# a kapcsolo es az allapot is megszunik, nincs mit beolvasni.
import io, re

P = 'app.src.html'
lines = io.open(P, encoding='utf-8').read().split('\n')

def cut(first_marker, last_marker, why, start_at=0):
    """Sorokat vag ki az ELSO olyan blokkbol, ami a ket jelolo koze esik."""
    a = next(i for i in range(start_at, len(lines)) if first_marker in lines[i])
    b = next(i for i in range(a, len(lines)) if last_marker in lines[i])
    seg = lines[a:b + 1]
    del lines[a:b + 1]
    print(f'  {why}: {len(seg)} sor ({a + 1}-{b + 1})')
    return len(seg)

# 1) allapot + kapcsolo-fuggveny
cut('const [viewMode, setViewMode] = useState', '  });', 'viewMode állapot')

# 2) a nezetvalto gomb a fejlecben
cut('{/* View mode toggle */}', '            </button>', 'nézetváltó gomb')

# 3) a netflix render-ag
cut("{!isCollapsed && viewMode === 'netflix' && (", '              )}', 'netflix render-ág')

s = '\n'.join(lines)

# 4) a racs-ag mar az egyetlen — a felteteles burok felesleges
old_grid = "              {!isCollapsed && viewMode === 'grid' && ("
assert s.count(old_grid) == 1
s = s.replace(old_grid, "              {!isCollapsed && (")
s = s.replace('              {/* Játékok — viewMode alapján */}\n', '')

# 5) a NetflixTile komponens
a = s.index('function NetflixTile({ g, selected, dim, locked, onClick, onInfo, onLongPress }) {')
b = s.index('\n}\n', a) + len('\n}\n')
seg = s[a:b]
assert 'NetflixTile' in seg and seg.count('\nfunction ') == 0, 'a vagas tulnyulik'
print(f'  NetflixTile: {seg.count(chr(10))} sor')
s = s[:a] + s[b:]

# 6) a csak ehhez tartozo CSS
css = '    .netflix-scroll::-webkit-scrollbar { display:none; }\n'
assert s.count(css) == 1
s = s.replace(css, '')

assert 'viewMode' not in s and 'NetflixTile' not in s and 'netflix' not in s and 'boh_games_view' not in s, \
    'maradt hivatkozas'

s = s.replace("const APP_VERSION = 'v10.166';", "const APP_VERSION = 'v10.167';", 1)
assert "v10.167" in s
io.open(P, 'w', encoding='utf-8').write(s)
print('OK')
