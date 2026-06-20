#!/usr/bin/env python3
"""v9.368 — English: SCENARIOS, Ring of Fire cards, CTA buttons, in-game strings"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Replace SCENARIOS with bilingual version
old_scenarios = """const SCENARIOS = {
  // Egyéni
  anagramma: { prompt:'4 betű → rakj ki egy értelmes szót 5 mp alatt!', cta:[] },
  ringfire:  { prompt:'Húzz egy lapot — csináld meg a leírást!', cta:[] },
  rulett:    { prompt:'Válassz egy poharat — ez a kemény?', cta:[] },
  uveg:      { prompt:'Pörgesd meg az üveget — akire mutat, az iszik.', cta:['Rám mutatott','Másra mutatott'] },
  zene:      { prompt:'Hallgasd meg a részletet — ki az előadó és mi a cím?', cta:['Nem ismertem fel','Felismertem!'] },
  otdolog:   { prompt:'Mondj 5 odaillő szót a megadott időn belül!', cta:['Nem sikerült','Megvan!'] },
  szerencse: { prompt:'Pörgesd meg a kereket — akire mutat, az iszik.', cta:['Rám mutatott','Másra mutatott'] },
  sohanem:   { prompt:'Én még soha — igaz rád?', cta:['Igaz rám — iszom','Nem igaz rám'] },
  mindenki:  { prompt:'', cta:[] },
  beerpong:  { prompt:'', cta:[] },
  powerhour: { prompt:'', cta:[] },
  igazhamis: { prompt:'Igaz vagy hamis az állítás?', cta:[] },
  kivagyok:  { prompt:'Ki van a képen? Tippelj rá az életkorára vagy foglalkozására!', cta:[] },
  // Páros
  erem:      { prompt:'Fej vagy írás — döntsétek el, ki iszik!', cta:[] },
  tapper:    { prompt:'Tegyétek az ujjatokat a gombra — automatikusan elindul. Aki hamarabb engedi el, iszik!', cta:[] },
  szamsor:   { prompt:'', cta:[] },
  reakcio:   { prompt:'', cta:[] },
  ritmus:    { prompt:'', cta:[] },
  mitval:    { prompt:'', cta:[] },
  emojikv:   { prompt:'', cta:[] },
  // Csapat
  busz:      { prompt:'Találd ki a következő lapot — piros vagy fekete?', cta:[] },
  memoria:   { prompt:'Fordíts meg két lapot — találtál párt?', cta:[] },
  ticktak:   { prompt:'A csengő szólt — ki tartotta magánál a tárgyat?', cta:[] },
  kezcsere:  { prompt:'Kéz csere — ki rontott el?', cta:[] },
  kisebb:    { prompt:'Kisebb vagy nagyobb lesz a következő lap?', cta:[] },
  kategoria: { prompt:'Ki nem tudott szót mondani a kategóriában?', cta:[] },
  hajime:    { prompt:'Ki mondott rosszat a hajime körben?', cta:[] },
  kopapir:   { prompt:'Kő-Papír-Olló — ki veszített a körben?', cta:[] },
  fingerit:  { prompt:'Finger it — ki tévesztett?', cta:[] },
  loverseny: { prompt:'Lóverseny — kinek nem jött be a tipp?', cta:[] },
  imposztor: { prompt:'Ki az Imposztor? Mindenki adjon egy tippet a szóra, majd szavazzatok!', cta:[] },
  collect:   { prompt:'Collect & Boom — ki találta a bombát?', cta:[] },
  'idopárbaj': { prompt:'Indítsd el a stoppert és állítsd le a titkos célhoz a lehető legközelebb!', cta:[] },
  'csakegyszó': { prompt:'Magyarázd el egyetlen szóval — megérti a párod?', cta:[] },
  'szolánc':   { prompt:'Mondd el a sort, majd told hozzá az új szót a kategóriából!', cta:[] },
};
const SCENARIO_DEFAULTS = {
  'Egyéni': { prompt:'Siker vagy kudarc?', cta:['Nem sikerült','Sikerült!'] },
  'Csapat': { prompt:'Ki nyert a körben?', cta:[] },
  'Páros':  { prompt:'Válassz ellenfelet!', cta:['Vesztettem','Nyertem!'] },
};"""

new_scenarios = """const SCENARIOS = {
  anagramma: { prompt:'4 betű → rakj ki egy értelmes szót 5 mp alatt!', cta:[] },
  ringfire:  { prompt:'Húzz egy lapot — csináld meg a leírást!', cta:[] },
  rulett:    { prompt:'Válassz egy poharat — ez a kemény?', cta:[] },
  uveg:      { prompt:'Pörgesd meg az üveget — akire mutat, az iszik.', cta:['Rám mutatott','Másra mutatott'] },
  zene:      { prompt:'Hallgasd meg a részletet — ki az előadó és mi a cím?', cta:['Nem ismertem fel','Felismertem!'] },
  otdolog:   { prompt:'Mondj 5 odaillő szót a megadott időn belül!', cta:['Nem sikerült','Megvan!'] },
  szerencse: { prompt:'Pörgesd meg a kereket — akire mutat, az iszik.', cta:['Rám mutatott','Másra mutatott'] },
  sohanem:   { prompt:'Én még soha — igaz rád?', cta:['Igaz rám — iszom','Nem igaz rám'] },
  mindenki:  { prompt:'', cta:[] },
  beerpong:  { prompt:'', cta:[] },
  powerhour: { prompt:'', cta:[] },
  igazhamis: { prompt:'Igaz vagy hamis az állítás?', cta:[] },
  kivagyok:  { prompt:'Ki van a képen? Tippelj rá az életkorára vagy foglalkozására!', cta:[] },
  erem:      { prompt:'Fej vagy írás — döntsétek el, ki iszik!', cta:[] },
  tapper:    { prompt:'Tegyétek az ujjatokat a gombra — automatikusan elindul. Aki hamarabb engedi el, iszik!', cta:[] },
  szamsor:   { prompt:'', cta:[] },
  reakcio:   { prompt:'', cta:[] },
  ritmus:    { prompt:'', cta:[] },
  mitval:    { prompt:'', cta:[] },
  emojikv:   { prompt:'', cta:[] },
  busz:      { prompt:'Találd ki a következő lapot — piros vagy fekete?', cta:[] },
  memoria:   { prompt:'Fordíts meg két lapot — találtál párt?', cta:[] },
  ticktak:   { prompt:'A csengő szólt — ki tartotta magánál a tárgyat?', cta:[] },
  kezcsere:  { prompt:'Kéz csere — ki rontott el?', cta:[] },
  kisebb:    { prompt:'Kisebb vagy nagyobb lesz a következő lap?', cta:[] },
  kategoria: { prompt:'Ki nem tudott szót mondani a kategóriában?', cta:[] },
  hajime:    { prompt:'Ki mondott rosszat a hajime körben?', cta:[] },
  kopapir:   { prompt:'Kő-Papír-Olló — ki veszített a körben?', cta:[] },
  fingerit:  { prompt:'Finger it — ki tévesztett?', cta:[] },
  loverseny: { prompt:'Lóverseny — kinek nem jött be a tipp?', cta:[] },
  imposztor: { prompt:'Ki az Imposztor? Mindenki adjon egy tippet a szóra, majd szavazzatok!', cta:[] },
  collect:   { prompt:'Collect & Boom — ki találta a bombát?', cta:[] },
  'idopárbaj': { prompt:'Indítsd el a stoppert és állítsd le a titkos célhoz a lehető legközelebb!', cta:[] },
  'csakegyszó': { prompt:'Magyarázd el egyetlen szóval — megérti a párod?', cta:[] },
  'szolánc':   { prompt:'Mondd el a sort, majd told hozzá az új szót a kategóriából!', cta:[] },
};
const SCENARIOS_EN = {
  anagramma: { prompt:'4 letters → make a valid word in 5 seconds!', cta:[] },
  ringfire:  { prompt:'Draw a card — follow the rule!', cta:[] },
  rulett:    { prompt:'Choose a cup — is this the one?', cta:[] },
  uveg:      { prompt:'Spin the bottle — whoever it points to drinks.', cta:['Pointed at me','Pointed elsewhere'] },
  zene:      { prompt:'Listen to the clip — who is the artist and what is the song?', cta:["Didn't recognize it",'Got it!'] },
  otdolog:   { prompt:'Name 5 things in the category within the time limit!', cta:["Didn't make it",'Got it!'] },
  szerencse: { prompt:'Spin the wheel — whoever it lands on drinks.', cta:['Landed on me','Landed on someone else'] },
  sohanem:   { prompt:'Never have I ever — is it true for you?', cta:['True for me — I drink','Not true for me'] },
  mindenki:  { prompt:'', cta:[] },
  beerpong:  { prompt:'', cta:[] },
  powerhour: { prompt:'', cta:[] },
  igazhamis: { prompt:'Is the statement true or false?', cta:[] },
  kivagyok:  { prompt:"Who is in the photo? Guess their age or profession!", cta:[] },
  erem:      { prompt:'Heads or tails — decide who drinks!', cta:[] },
  tapper:    { prompt:'Place your finger on the button — it starts automatically. Whoever lifts first drinks!', cta:[] },
  szamsor:   { prompt:'', cta:[] },
  reakcio:   { prompt:'', cta:[] },
  ritmus:    { prompt:'', cta:[] },
  mitval:    { prompt:'', cta:[] },
  emojikv:   { prompt:'', cta:[] },
  busz:      { prompt:'Guess the next card — red or black?', cta:[] },
  memoria:   { prompt:'Flip two cards — did you find a pair?', cta:[] },
  ticktak:   { prompt:'The bell rang — who was holding the object?', cta:[] },
  kezcsere:  { prompt:'Hand swap — who made a mistake?', cta:[] },
  kisebb:    { prompt:'Will the next card be higher or lower?', cta:[] },
  kategoria: { prompt:"Who couldn't name a word in the category?", cta:[] },
  hajime:    { prompt:'Who made a mistake in the Hajime round?', cta:[] },
  kopapir:   { prompt:'Rock Paper Scissors — who lost the round?', cta:[] },
  fingerit:  { prompt:'Finger it — who guessed wrong?', cta:[] },
  loverseny: { prompt:"Horse Racing — whose bet didn't come in?", cta:[] },
  imposztor: { prompt:'Who is the Impostor? Everyone give a clue, then vote!', cta:[] },
  collect:   { prompt:'Collect & Boom — who found the bomb?', cta:[] },
  'idopárbaj': { prompt:'Start the stopwatch and stop it as close to the secret target as possible!', cta:[] },
  'csakegyszó': { prompt:'Explain it in one word — will your partner get it?', cta:[] },
  'szolánc':   { prompt:'Repeat the list, then add a new word from the category!', cta:[] },
};
const SCENARIO_DEFAULTS = {
  'Egyéni': { prompt:'Siker vagy kudarc?', cta:['Nem sikerült','Sikerült!'] },
  'Csapat': { prompt:'Ki nyert a körben?', cta:[] },
  'Páros':  { prompt:'Válassz ellenfelet!', cta:['Vesztettem','Nyertem!'] },
};
const SCENARIO_DEFAULTS_EN = {
  'Egyéni': { prompt:'Success or failure?', cta:["Didn't make it",'Made it!'] },
  'Csapat': { prompt:'Who won the round?', cta:[] },
  'Páros':  { prompt:'Choose an opponent!', cta:['I lost','I won!'] },
};
const ts = (id, cat) => {
  if (LANG === 'en') {
    return SCENARIOS_EN[id] || SCENARIO_DEFAULTS_EN[cat] || SCENARIO_DEFAULTS_EN['Egyéni'];
  }
  return SCENARIOS[id] || SCENARIO_DEFAULTS[cat] || SCENARIO_DEFAULTS['Egyéni'];
};"""

assert old_scenarios in html, "FAIL: SCENARIOS"
html = html.replace(old_scenarios, new_scenarios, 1)

# ── 2. Update the place where SCENARIOS is looked up - find usage
# The SCENARIOS object is used in PlayScreen - find where scenario is resolved
old_scenario_lookup = "const scenario = SCENARIOS[currentGame?.id] || SCENARIO_DEFAULTS[currentGame?.category] || SCENARIO_DEFAULTS['Egyéni'];"
new_scenario_lookup = "const scenario = ts(currentGame?.id, currentGame?.category);"
if old_scenario_lookup in html:
    html = html.replace(old_scenario_lookup, new_scenario_lookup, 1)
else:
    # Try alternative lookup patterns
    print("WARNING: scenario lookup not found with exact string, trying alternative")

# ── 3. Ring of Fire card descriptions (TASKS object with number keys)
old_ringfire_cards = """    '2':  { title:'Choose 🫵',       desc:'Válassz valakit, aki iszik.' },
    '3':  { title:'Me 🙋',           desc:'Te iszol.' },
    '4':  { title:'Whore 💃',        desc:'Összes lány iszik.' },
    '5':  { title:'Thumb Master 👍', desc:'Te leszel a Thumb Master — bármikor ráteheted a hüvelykujjad az asztalra, az utolsó aki követi, iszik.' },
    '6':  { title:'Dicks 🕺',        desc:'Összes fiú iszik.' },
    '7':  { title:'Heaven ☝️',       desc:'Fel kell mutatni az égre — az utolsó aki követi, iszik.' },
    '8':  { title:'Mate 🤝',         desc:'Válassz valakit, aki veled iszik.' },
    '9':  { title:'Rhyme 🎤',        desc:'Mondj egy szót — mindenki sorban rímelt rá. Aki megakad, iszik.' },
    '10': { title:'Categories 🗂️',  desc:'Mondj egy kategóriát — mindenki mond egyet. Aki megakad, iszik.' },
    'J':  { title:'Make a Rule 📜',  desc:'Hozz egy szabályt — aki megszegi, iszik.' },
    'Q':  { title:'Questions ❓',    desc:'Csak kérdésekkel szabad kommunikálni — aki állítást mond, iszik.' },
    'K':  { title:'Pour 👑',         desc:'Önts a poharadból a középső pohárba. Aki az utolsó Királyt húzza, megissza az egészet.' },
    'A':  { title:'Waterfall 🌊',    desc:'Mindenki elkezd inni — senki nem állhat meg amíg az Ász-húzó iszik.' },"""
new_ringfire_cards = """    '2':  { title:'Choose 🫵',       desc:LANG==='en'?'Choose someone to drink.':'Válassz valakit, aki iszik.' },
    '3':  { title:'Me 🙋',           desc:LANG==='en'?'You drink.':'Te iszol.' },
    '4':  { title:'Whore 💃',        desc:LANG==='en'?'All girls drink.':'Összes lány iszik.' },
    '5':  { title:'Thumb Master 👍', desc:LANG==='en'?'You become Thumb Master — put your thumb on the table anytime, the last to follow drinks.':'Te leszel a Thumb Master — bármikor ráteheted a hüvelykujjad az asztalra, az utolsó aki követi, iszik.' },
    '6':  { title:'Dicks 🕺',        desc:LANG==='en'?'All guys drink.':'Összes fiú iszik.' },
    '7':  { title:'Heaven ☝️',       desc:LANG==='en'?'Point up to the sky — the last to follow drinks.':'Fel kell mutatni az égre — az utolsó aki követi, iszik.' },
    '8':  { title:'Mate 🤝',         desc:LANG==='en'?'Choose someone to drink with you.':'Válassz valakit, aki veled iszik.' },
    '9':  { title:'Rhyme 🎤',        desc:LANG==='en'?'Say a word — everyone rhymes in turn. Whoever gets stuck drinks.':'Mondj egy szót — mindenki sorban rímelt rá. Aki megakad, iszik.' },
    '10': { title:'Categories 🗂️',  desc:LANG==='en'?'Name a category — everyone names one. Whoever gets stuck drinks.':'Mondj egy kategóriát — mindenki mond egyet. Aki megakad, iszik.' },
    'J':  { title:'Make a Rule 📜',  desc:LANG==='en'?'Make a rule — whoever breaks it drinks.':'Hozz egy szabályt — aki megszegi, iszik.' },
    'Q':  { title:'Questions ❓',    desc:LANG==='en'?'Only questions allowed — whoever makes a statement drinks.':'Csak kérdésekkel szabad kommunikálni — aki állítást mond, iszik.' },
    'K':  { title:'Pour 👑',         desc:LANG==='en'?'Pour into the center cup. Whoever draws the last King must drink it all.':'Önts a poharadból a középső pohárba. Aki az utolsó Királyt húzza, megissza az egészet.' },
    'A':  { title:'Waterfall 🌊',    desc:LANG==='en'?'Everyone starts drinking — no one can stop until the Ace-drawer stops.':'Mindenki elkezd inni — senki nem állhat meg amíg az Ász-húzó iszik.' },"""
assert old_ringfire_cards in html, "FAIL: ringfire cards"
html = html.replace(old_ringfire_cards, new_ringfire_cards, 1)

# ── 4. Common CTA button translations - "Rám mutatott" etc in CTA rendering
# Find where CTAs are rendered and add bilingual support
# The CTAs come from scenario.cta[] so they'll be translated via ts() above

# ── 5. Key in-game strings - "Nem sikerült" "Sikerült" standalone buttons
html = html.replace(
    """'✗ Nem sikerült'""",
    """(LANG==='en'?"✗ Failed":"✗ Nem sikerült")"""
)

# ── 6. Horse racing strings
old_loverseny1 = """                <div style={{fontFamily:T.font,fontWeight:900,fontSize:14,color:T.ink,marginBottom:2}}>Melyik lóra fogadsz?</div>"""
new_loverseny1 = """                <div style={{fontFamily:T.font,fontWeight:900,fontSize:14,color:T.ink,marginBottom:2}}>{LANG==='en'?'Which horse do you bet on?':'Melyik lóra fogadsz?'}</div>"""
if old_loverseny1 in html:
    html = html.replace(old_loverseny1, new_loverseny1, 1)

old_loverseny2 = """                <div style={{fontFamily:T.font,fontWeight:700,fontSize:13,color:T.inkSoft,marginBottom:8}}>Hány korty a tét?</div>"""
new_loverseny2 = """                <div style={{fontFamily:T.font,fontWeight:700,fontSize:13,color:T.inkSoft,marginBottom:8}}>{LANG==='en'?'How many sips is the bet?':'Hány korty a tét?'}</div>"""
if old_loverseny2 in html:
    html = html.replace(old_loverseny2, new_loverseny2, 1)

# ── 7. "Vesztettem" / "Nyertem" result buttons
old_lost = """>Vesztettem 😔<"""
new_lost = """>{LANG==='en'?'I lost 😔':'Vesztettem 😔'}<"""
if old_lost in html:
    html = html.replace(old_lost, new_lost, 1)

old_won = """>Nyertem! 🎉<"""
new_won = """>{LANG==='en'?'I won! 🎉':'Nyertem! 🎉'}<"""
if old_won in html:
    html = html.replace(old_won, new_won, 1)

# ── 8. Zene game "Nem ismertem" button
old_zene_btn = """>Nem ismertem 🍺<"""
new_zene_btn = """>{LANG==='en'?"Didn't know it 🍺":'Nem ismertem 🍺'}<"""
if old_zene_btn in html:
    html = html.replace(old_zene_btn, new_zene_btn, 1)

# ── 9. Bus game key strings
old_busz_hint = """              <div style={{fontFamily:T.font,fontSize:11,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.09em',marginBottom:2}}>Szobakód</div>"""
new_busz_hint = """              <div style={{fontFamily:T.font,fontSize:11,color:T.inkSoft,textTransform:'uppercase',letterSpacing:'0.09em',marginBottom:2}}>{t('roomCode')}</div>"""
if old_busz_hint in html:
    html = html.replace(old_busz_hint, new_busz_hint, 1)

old_busz_csatlakozas = """          <div style={{fontFamily:T.font,fontSize:12,fontWeight:700,color:T.inkMute,textTransform:'uppercase',letterSpacing:'0.08em',textAlign:'center',marginBottom:8}}>Csatlakozási QR kód</div>"""
new_busz_csatlakozas = """          <div style={{fontFamily:T.font,fontSize:12,fontWeight:700,color:T.inkMute,textTransform:'uppercase',letterSpacing:'0.08em',textAlign:'center',marginBottom:8}}>{LANG==='en'?'Join QR Code':'Csatlakozási QR kód'}</div>"""
if old_busz_csatlakozas in html:
    html = html.replace(old_busz_csatlakozas, new_busz_csatlakozas, 1)

old_busz_select = """            <div style={{fontFamily:T.font,fontWeight:800,fontSize:14,color:T.ink,marginBottom:4}}>Válaszd ki a neved — te is játszol</div>"""
new_busz_select = """            <div style={{fontFamily:T.font,fontWeight:800,fontSize:14,color:T.ink,marginBottom:4}}>{LANG==='en'?"Select your name — you're playing too":'Válaszd ki a neved — te is játszol'}</div>"""
if old_busz_select in html:
    html = html.replace(old_busz_select, new_busz_select, 1)

# "Betöltés..." loading
html = html.replace(
    """>Betöltés…<""",
    """>{LANG==='en'?'Loading…':'Betöltés…'}<"""
)

# ── 10. Common game result messages
html = html.replace("'Nem sikerült'", "(LANG==='en'?\"Didn't make it\":'Nem sikerült')")
html = html.replace("'Sikerült!'", "(LANG==='en'?'Made it!':'Sikerült!')")
html = html.replace("'Megvan!'", "(LANG==='en'?'Got it!':'Megvan!')")
html = html.replace("'Nyertem!'", "(LANG==='en'?'I won!':'Nyertem!')")
html = html.replace("'Vesztettem'", "(LANG==='en'?'I lost':'Vesztettem')")
html = html.replace("'Felismertem!'", "(LANG==='en'?'Got it!':'Felismertem!')")
html = html.replace("'Nem ismertem fel'", "(LANG==='en'?\"Didn't recognize it\":'Nem ismertem fel')")
html = html.replace("'Rám mutatott'", "(LANG==='en'?'Pointed at me':'Rám mutatott')")
html = html.replace("'Másra mutatott'", "(LANG==='en'?'Pointed elsewhere':'Másra mutatott')")
html = html.replace("'Igaz rám — iszom'", "(LANG==='en'?'True for me — I drink':'Igaz rám — iszom')")
html = html.replace("'Nem igaz rám'", "(LANG==='en'?'Not true for me':'Nem igaz rám')")
html = html.replace("'Igaz rám'", "(LANG==='en'?'True for me':'Igaz rám')")

# ── 11. "Ez a játék még fejlesztés alatt áll"
html = html.replace(
    """'Ez a játék még fejlesztés alatt áll. Nemsokára elérhető lesz!'""",
    """(LANG==='en'?'This game is still in development. Coming soon!':'Ez a játék még fejlesztés alatt áll. Nemsokára elérhető lesz!')"""
)

# ── 12. Common UI strings still in Hungarian
html = html.replace('>Bezárás<', '>{LANG===\'en\'?\'Close\':\'Bezárás\'}<')
html = html.replace('>Értem<', '>{LANG===\'en\'?\'Got it\':\'Értem\'}<')

html = html.replace("const APP_VERSION = 'v9.367';", "const APP_VERSION = 'v9.368';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.368 — SCENARIOS_EN, Ring of Fire EN, CTA buttons, in-game strings")
