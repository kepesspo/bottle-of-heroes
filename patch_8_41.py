#!/usr/bin/env python3
"""
v8.41:
1. comingSoon játékok a lista végére (hajime, kopapir, szolánc)
2. Ring of Fire: amikor ki van választva, minden más játék lakat ikont kap
"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. Move comingSoon games to end of GAMES list ────────────────────────────
# Extract hajime and kopapir lines, remove them from current position,
# append after the last non-comingSoon entry (before the closing ]

HAJIME_LINE = "  { id:'hajime',    name:'Hajime',                difficulty:'nehéz',   category:'Csapat', emoji:'😆', comingSoon:true, symbol:IMGS['hajime_symbol.png'], img:IMGS['hajime_icon.png'], banner:IMGS['hajime_banner.png'], color:'#FACC15', desc:'Számolj helyesen! El kell kezdeni számolni 1-től és ha 5-tel vagy 7-tel osztható a szám vagy szerepel benne az 5 vagy a 7 akkor \"hajime\"-t kell mondani. Aki eltéveszti az iszik. Egy plusz csavar: minden \"hajime\" után megfordul a kör.' },"
KOPAPIR_LINE = "  { id:'kopapir',   name:'Kő Papír Olló',         difficulty:'nehéz',   category:'Csapat', emoji:'✊', comingSoon:true, symbol:IMGS['kopapir_symbol.png'], img:IMGS['kopapir_icon.png'], banner:IMGS['kopapir_banner.png'], color:'#7C3AED', desc:'Annyi kört kell játszani ahány játékos van. Kell egy kezdő ember aki kihivja a mellette ülőt, ezt a játék választja ki. Ha te nyersz akkor ő iszik és az ő mellette ülővel kell játszania. Ha te vesztesz akkor a te melletted ülővel kell játszanod. Ha döntetlen akkor mind a ketten isztok.' },"

# Remove from current position
assert HAJIME_LINE in content, "hajime line not found"
assert KOPAPIR_LINE in content, "kopapir line not found"
content = content.replace('\n' + HAJIME_LINE, '', 1)
content = content.replace('\n' + KOPAPIR_LINE, '', 1)

# The last game currently is ovfj. Append comingSoon games after it.
OVFJ_LINE = "  { id:'ovfj', name:'Ország-Város', difficulty:'közepes', category:'Csapat', emoji:'🌍', symbol:null, img:IMGS['ovfj_icon.png'], banner:IMGS['ovfj_banner.png'], color:'#22C55E', desc:'Betű kisorsol, mindenki kitölti a 8 kategóriát a saját telefonján. Aki elsőként kész, a többieknek +10 mp. Szavazással dől el ki érvényes — egyedi válasz 10 pt, dupla 5 pt.' },"
assert OVFJ_LINE in content, "ovfj line not found"

# szolánc already has comingSoon — find it and move after ovfj too
SZOLANC_LINE = "  { id:'szolánc',   name:'Szólánc',              difficulty:'közepes', category:'Csapat', emoji:'🔗', symbol:IMGS['szolanc_symbol.png'], img:IMGS['szolanc_icon.png'], banner:null, color:'#F59E0B', comingSoon:true, desc:'Ismételd el a sort, majd told hozzá egy új szót a kategóriából. Aki elront, iszik.' },"

if SZOLANC_LINE in content:
    content = content.replace('\n' + SZOLANC_LINE, '', 1)
    content = content.replace(OVFJ_LINE, OVFJ_LINE + '\n' + HAJIME_LINE + '\n' + KOPAPIR_LINE + '\n' + SZOLANC_LINE, 1)
    print("✓ hajime, kopapir, szolánc moved to end")
else:
    content = content.replace(OVFJ_LINE, OVFJ_LINE + '\n' + HAJIME_LINE + '\n' + KOPAPIR_LINE, 1)
    print("✓ hajime, kopapir moved to end")

# ── 2. isLocked: ringfire solo-only locking ───────────────────────────────────
OLD_LOCKED = """  const isLocked = id => {
    const g = GAMES.find(x=>x.id===id);
    if (g?.comingSoon) return true;
    if (id === 'busz') return otherSelected || beerpongSelected;
    if (id === 'beerpong') return otherSelected || buszSelected;
    return buszSelected || beerpongSelected;
  };"""

NEW_LOCKED = """  const soloSelected = selectedGames.includes('powerhour') || selectedGames.includes('ovfj') || selectedGames.includes('ringfire');
  const ringfireSelected = selectedGames.includes('ringfire');
  const isLocked = id => {
    const g = GAMES.find(x=>x.id===id);
    if (g?.comingSoon) return true;
    // If a solo-only game is selected, lock all others except itself
    if (soloSelected && !selectedGames.includes(id)) return true;
    if (id === 'busz') return otherSelected || beerpongSelected;
    if (id === 'beerpong') return otherSelected || buszSelected;
    return buszSelected || beerpongSelected;
  };"""

assert OLD_LOCKED in content, "isLocked not found"
content = content.replace(OLD_LOCKED, NEW_LOCKED, 1)
print("✓ isLocked: solo-only locking (ringfire/powerhour/ovfj)")

# ── 3. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v8.40';"
NEW_VER = "const APP_VERSION = 'v8.41';"
assert OLD_VER in content
content = content.replace(OLD_VER, NEW_VER, 1)
print("✓ Version → v8.41")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ Saved")
