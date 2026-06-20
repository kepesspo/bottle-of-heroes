#!/usr/bin/env python3
"""v9.319 — Full English translation: GAMES_EN, missing TR keys, hardcoded string fixes"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ══════════════════════════════════════════════════════════════════════
# 1. Add missing TR keys — hu + en
# ══════════════════════════════════════════════════════════════════════

old_tr_hu_end = "    nowPlaying: 'MOST Ő JÖN',\n    themePlaying: 'MOST ŐK',"
new_tr_hu_end = """    nowPlaying: 'MOST Ő JÖN',
    themePlaying: 'MOST ŐK',
    gameOver: 'Játék vége! 🎉',
    pointsProgress: '📈 Pontok alakulása',
    bonusEvent: 'Bónusz esemény!',
    groupDrink: 'Csoportos Ivászat!',
    groupBtn: '🍻 Csoport',
    startGame: 'Játék indítása!',
    startGameBtn: 'Játék indítása',
    gameplay: 'Játékmenet',
    gameOrder: 'Játéksorrend',
    gameModeSection: 'Játékmód',
    addPlayerBtn: 'Játékos hozzáadása',
    calcPoints: '✓ Pontok kiszámítása',
    noElim: 'Nem esik ki senki',
    noElimSub: 'Játék akkor ér véget ha elfogy a pakli',
    livesLabel: 'Életek',
    livesSub: 'Játékosnak legyen életszáma',
    modePoints: '⭐ Pontgyűjtés',
    modePointsInfo: 'A játékosok minden győztes körnél csillagot kapnak. A legtöbb csillaggal rendelkező játékos nyeri a meccset.',
    modeBonus: '🎁 Bónusz képernyő',
    modeBonusInfo: 'Minden kör végén megjelenik egy rövid összefoglaló: ki nyert pontot és ki iszik.',
    modeGroup: '🍺 Csoportos ivás',
    modeGroupInfo: 'Vesztes esetén az egész csapat iszik egyet, nem csak a vesztes játékos.',
    modeWildcard: '🃏 Wildcard körök',
    modeWildcardInfo: 'Minden 5. kör elején megjelenik egy random különleges szabály (pl. bal kézzel inni, pókerpofa kör).',
    diffEasy: 'Könnyű',
    diffEasyNote: 'Hosszabb időzítők, megbocsátóbb feltételek. Ajánlott új játékosoknak.',
    diffMid: 'Közepes',
    diffMidNote: 'Normál játéksebesség. Alapértelmezett beállítás.',
    diffHard: 'Nehéz',
    diffHardNote: 'Rövidebb időzítők. Gyors reflexek kellenek.',
    diffExtreme: 'Extrém',
    diffExtremeNote: 'Minimális idő, maximum nyomás. Csak a legbátrabbaknak!',
    bonusLeaderDrinks: 'A vezető iszik — {n} korty',
    bonusComebackPoints: 'Az utolsó helyen álló visszakapaszkodik — +{n} pont',
    obsRoundChange: '📡 Körváltás',
    roundWord: 'Kör',
    chooseGames: 'Válassz játékokat a kezdéshez!',
    addPlayersOnboard: 'Játékosok hozzáadása',
    chooseGamesOnboard: 'Játékok kiválasztása',"""
assert old_tr_hu_end in html, "FAIL: TR hu end"
html = html.replace(old_tr_hu_end, new_tr_hu_end, 1)

old_tr_en_end = "    nowPlaying: 'NOW PLAYING',\n    themePlaying: 'PLAYING',"
new_tr_en_end = """    nowPlaying: 'NOW PLAYING',
    themePlaying: 'PLAYING',
    gameOver: 'Game Over! 🎉',
    pointsProgress: '📈 Points Progress',
    bonusEvent: 'Bonus Event!',
    groupDrink: 'Group Drinking!',
    groupBtn: '🍻 Group',
    startGame: 'Start Game!',
    startGameBtn: 'Start Game',
    gameplay: 'Gameplay',
    gameOrder: 'Game Order',
    gameModeSection: 'Game Mode',
    addPlayerBtn: 'Add Player',
    calcPoints: '✓ Calculate Points',
    noElim: 'No elimination',
    noElimSub: 'Game ends when the deck runs out',
    livesLabel: 'Lives',
    livesSub: 'Give players a life count',
    modePoints: '⭐ Point Scoring',
    modePointsInfo: 'Players earn a star for every winning round. The player with the most stars wins the match.',
    modeBonus: '🎁 Bonus Screen',
    modeBonusInfo: 'A brief summary appears after each round: who scored a point and who drinks.',
    modeGroup: '🍺 Group Drinking',
    modeGroupInfo: 'On a loss, the whole team drinks, not just the losing player.',
    modeWildcard: '🃏 Wildcard Rounds',
    modeWildcardInfo: 'Every 5th round begins with a random special rule (e.g. drink with left hand, poker face round).',
    diffEasy: 'Easy',
    diffEasyNote: 'Longer timers, more forgiving conditions. Recommended for new players.',
    diffMid: 'Medium',
    diffMidNote: 'Normal game speed. Default setting.',
    diffHard: 'Hard',
    diffHardNote: 'Shorter timers. Quick reflexes needed.',
    diffExtreme: 'Extreme',
    diffExtremeNote: 'Minimal time, maximum pressure. For the bravest only!',
    bonusLeaderDrinks: 'The leader drinks — {n} sips',
    bonusComebackPoints: 'Last place makes a comeback — +{n} point',
    obsRoundChange: '📡 Round Change',
    roundWord: 'Round',
    chooseGames: 'Choose games to get started!',
    addPlayersOnboard: 'Add Players',
    chooseGamesOnboard: 'Choose Games',"""
assert old_tr_en_end in html, "FAIL: TR en end"
html = html.replace(old_tr_en_end, new_tr_en_end, 1)

# ══════════════════════════════════════════════════════════════════════
# 2. Add GAMES_EN object + tg() helper right after const t = ...
# ══════════════════════════════════════════════════════════════════════

old_after_t = "const t = (key) => TR[LANG]?.[key] || TR['hu'][key] || key;\n\nconst R = "
new_after_t = """const t = (key) => TR[LANG]?.[key] || TR['hu'][key] || key;

const GAMES_EN = {
  busz:       { name: 'Bus', desc: "Starting from the bottom of the pyramid card row, cards are flipped one by one. Anyone whose card matches the current card can assign that many sips to another player. Multiple matches in a row multiply the value. If you lie and get caught, you drink double!" },
  imposztor:  { name: 'Impostor', desc: "Someone among you is the Impostor! Everyone gets a secret role — only the Impostor doesn't know the secret word. The others must discuss clues without giving it away. Can you catch the Impostor before they blend in?" },
  memoria:    { name: 'Memory', desc: "Classic memory game with emoji cards. Take turns flipping cards — if you find a pair, you score a point and keep going. The player with the most pairs at the end wins. Losers drink!" },
  erem:       { name: 'Coin Flip', desc: "The app selects a player who can challenge someone else. Both players choose between Heads and Tails. The loser takes a drink." },
  ticktak:    { name: 'Tick Tack', desc: "When the game starts, a hidden timer begins counting down in the background. Start passing an object around the circle. Whoever holds it when the timer hits zero must drink!" },
  kezcsere:   { name: 'Hand Swap', desc: "Everyone crosses their hands on the table. One chosen direction gets tapped in sequence — but the order can reverse at any moment. Whoever makes a mistake drinks!" },
  anagramma:  { name: 'Anagram', desc: "The app selects a player. When they press Start, 4 letters appear on screen. Unscramble them into a word before time runs out. Fail and you drink!" },
  ringfire:   { name: 'Ring of Fire', desc: "Draw a card and follow its rule. Each card value has a special action. The last person to draw a King must drink the accumulated cup!" },
  rulett:     { name: 'Russian Roulette', desc: "Choose from three cards. Two hide fireworks, one hides a drink. Draw one — if you get the drink card, you take a shot. Luck is everything!" },
  kisebb:     { name: 'Higher or Lower', desc: "The app selects a starting player who must predict whether the next number will be higher or lower. The further the chain goes, the more the wrong guesser drinks!" },
  tapper:     { name: 'Tapper', desc: "The app selects a player who can challenge someone. Both place a finger on the spot. A countdown from 5 begins — lift your finger as close to 0 as possible. Only the loser drinks." },
  kategoria:  { name: 'Category', desc: "The game picks a category and the first player says a word in it. The next player continues with a word starting with the last letter. Whoever hesitates or repeats must drink. 5 seconds to think!" },
  fingerit:   { name: 'Finger It', desc: "Everyone places their index finger on the table. The selected player counts: 1, 2, 3 — everyone must either lift or keep their finger. The goal is for exactly as many fingers to remain as the number called. Miss it and you drink!" },
  uveg:       { name: 'Spin the Bottle', desc: "The app selects a player to spin the bottle. Whoever the bottle points to at the table must drink." },
  zene:       { name: 'Music Recognition', desc: "The player hears 5 seconds of a song. They must guess the artist and title. Guess one — no drink. Guess both — assign a drink. Guess neither — drink up!" },
  loverseny:  { name: 'Horse Racing', desc: "Each player bets 1–3 units on one of four horses: Yellow, Green, Blue, or Red. If your horse wins, assign that many drinks. If your horse loses, drink what you bet." },
  otdolog:    { name: '5 Things', desc: "The app selects a player who must name 5 things in the given category within 5 seconds. Fail and you drink." },
  szerencse:  { name: 'Spin the Wheel', desc: "The game selects a player to spin the wheel. Whoever the wheel lands on must drink." },
  sohanem:    { name: 'Never Have I Ever', desc: "A statement appears — if it's true for you, you drink. If it's not, you don't." },
  collect:    { name: 'Collect and Boom', desc: "The app selects a player to start the round. They pick a tile from the board, then the player to their right picks one, and so on — until someone hits a bomb. The loser drinks all the units collected." },
  kivagyok:   { name: 'Who Am I?', desc: "The app shows a celebrity photo and you must identify them. Correctly guess their age or profession and you can assign a drink to someone." },
  mindenki:   { name: 'Everyone Drinks', desc: "The game randomly selects a player who must drink. When everyone has gone, the cycle starts over." },
  beerpong:   { name: 'Beer Pong Tournament', desc: "Single-elimination beer pong tournament. The app generates the bracket, you decide who won — the loser drinks as many sips as the cup difference. Last player standing is the champion!" },
  'idopárbaj': { name: 'Time Duel', desc: "The app hides a random time between 1–30 seconds. Start the stopwatch, then stop it as close to the secret target as possible. Whoever is further off drinks." },
  igazhamis:  { name: 'True or False', desc: "A statement appears and you must decide if it's true or false. Correct — assign a drink. Wrong — drink up." },
  hajime:     { name: 'Hajime', desc: "Count correctly! Start from 1 — but if the number is divisible by 5 or 7, or contains those digits, say 'Hajime!' instead. Whoever makes a mistake drinks." },
  kopapir:    { name: 'Rock Paper Scissors', desc: "Play as many rounds as there are players. A starting player challenges the one next to them, continuing around the circle. The loser of each round drinks." },
  csakegyszó: { name: 'Just One Word', desc: "Explain a word to your partner using only a single word in 15 seconds. If they get it, both score a point. If not, both drink." },
  powerhour:  { name: 'Power Hour', desc: "Spotify tracks switch every 20 seconds for 60 minutes. Every minute a Super Mario sound plays — take a sip! The last one standing is the Power Hour champion." },
  ovfj:       { name: 'Categories', desc: "A letter is drawn and everyone fills in 8 categories on their own phone. The first to finish gives everyone else extra drinks. Points go to unique answers." },
  szolánc:    { name: 'Word Chain', desc: "Repeat the list, then add a new word from the category. Whoever makes a mistake drinks." },
  ritmus:     { name: 'Rhythm Game', desc: "The app selects two players. The first player tries to tap the flashing buttons for 30 seconds. The second faces the same challenge. Higher score wins; the loser drinks." },
  mitval:     { name: 'Would You Rather', desc: "Two options appear and you must choose one out loud. You have 5 seconds to decide. Fail to choose in time and you drink!" },
  meduza:     { name: 'Medusa', desc: "Everyone bows their head and looks at someone in the circle. On 3-2-1, they all look up. If you lock eyes with someone who's also looking at you — both of you drink!" },
  farkasos:   { name: 'Werewolf', desc: "Classic Mafia/Werewolf game. The app secretly assigns roles (Villager, Werewolf, Doctor, Detective). The village must find the werewolves before it's too late." },
  mutasd:     { name: 'Act It Out', desc: "The app selects a player and shows them a word. Act it out in 15 seconds without words or sounds. If the team guesses — everyone else drinks. Fail — the actor drinks." },
  emojikv:    { name: 'Emoji Quiz', desc: "3–4 emojis appear representing a movie, phrase, or expression. Figure out what they mean. Correct — assign a drink. Wrong — drink up." },
  tabu:       { name: 'Taboo', desc: "Team game: one player explains, the other guesses. Success — both get +1 point. Failure — both drink. No using the word itself!" },
  matek:      { name: 'Quick Math', desc: "The app selects a player who has 3 seconds to solve a mental arithmetic problem. Three answer options appear — pick the right one or drink!" },
  reakcio:    { name: 'Reaction Test', desc: "Duel! Both players press the button the moment the screen turns green. The slower one drinks." },
  szamsor:    { name: 'Number Sequence', desc: "Duel! Both players separately tap 1 through 9 in order. The app compares the times — the slower player drinks." },
};
const tg = (game, field) => (LANG === 'en' && GAMES_EN[game?.id]?.[field]) || game?.[field] || '';

const R = """
assert old_after_t in html, "FAIL: after t insert"
html = html.replace(old_after_t, new_after_t, 1)

# ══════════════════════════════════════════════════════════════════════
# 3. Replace game name/desc display points with tg()
# ══════════════════════════════════════════════════════════════════════

# Game list card name (line 35060)
old_gname1 = "<div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{g.name}</div>"
new_gname1 = "<div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{tg(g,'name')}</div>"
assert old_gname1 in html, "FAIL: gname1"
html = html.replace(old_gname1, new_gname1, 1)

# Game card name (line 36349)
old_gname2 = "<div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color: selected ? T.mintDeep : T.ink, lineHeight:1.2 }}>{g.name}</div>"
new_gname2 = "<div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color: selected ? T.mintDeep : T.ink, lineHeight:1.2 }}>{tg(g,'name')}</div>"
assert old_gname2 in html, "FAIL: gname2"
html = html.replace(old_gname2, new_gname2, 1)

# Game grid name (line 36396)
old_gname3 = "<div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:12, color:T.ink, textAlign:'center', lineHeight:1.15, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis', maxWidth:'100%' }}>{g.name}</div>"
new_gname3 = "<div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:12, color:T.ink, textAlign:'center', lineHeight:1.15, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis', maxWidth:'100%' }}>{tg(g,'name')}</div>"
assert old_gname3 in html, "FAIL: gname3"
html = html.replace(old_gname3, new_gname3, 1)

# Game info popup name (line 36489)
old_gname4 = "<div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:24, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay, lineHeight:1.05 }}>{game.name}</div>"
new_gname4 = "<div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:24, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay, lineHeight:1.05 }}>{tg(game,'name')}</div>"
assert old_gname4 in html, "FAIL: gname4"
html = html.replace(old_gname4, new_gname4, 1)

# Game card desc snippet (line 36350)
old_gdesc1 = "<div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:2 }}>{g.desc?.slice(0,48)}…</div>"
new_gdesc1 = "<div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:2 }}>{tg(g,'desc')?.slice(0,48)}…</div>"
assert old_gdesc1 in html, "FAIL: gdesc1"
html = html.replace(old_gdesc1, new_gdesc1, 1)

# Game info popup desc (line 36505)
old_gdesc2 = "<div style={{ fontFamily:T.font, fontSize:14.5, lineHeight:1.75, color:T.ink, fontWeight:500, whiteSpace:'pre-line', marginBottom:18, opacity:0.82 }}>{game.desc}</div>"
new_gdesc2 = "<div style={{ fontFamily:T.font, fontSize:14.5, lineHeight:1.75, color:T.ink, fontWeight:500, whiteSpace:'pre-line', marginBottom:18, opacity:0.82 }}>{tg(game,'desc')}</div>"
assert old_gdesc2 in html, "FAIL: gdesc2"
html = html.replace(old_gdesc2, new_gdesc2, 1)

# PlayScreen header name (line 46095)
old_gname5 = "<div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>{currentGame.name}</div>"
new_gname5 = "<div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>{tg(currentGame,'name')}</div>"
assert old_gname5 in html, "FAIL: gname5"
html = html.replace(old_gname5, new_gname5, 1)

# Observer current game name (line 50135)
old_gname6 = "<div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:18, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay, marginTop:2 }}>{currentGame.name}</div>"
new_gname6 = "<div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:18, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay, marginTop:2 }}>{tg(currentGame,'name')}</div>"
assert old_gname6 in html, "FAIL: gname6"
html = html.replace(old_gname6, new_gname6, 1)

# History stats game name lookup (line 47910)
old_gname7 = "return g ? (g.name || id) : id; }).join(', ') || '—';"
new_gname7 = "return g ? (tg(g,'name') || id) : id; }).join(', ') || '—';"
assert old_gname7 in html, "FAIL: gname7"
html = html.replace(old_gname7, new_gname7, 1)

# ══════════════════════════════════════════════════════════════════════
# 4. Replace hardcoded Hungarian UI strings with t()
# ══════════════════════════════════════════════════════════════════════

# "Játék vége! 🎉" AppBar title
old_gameover_appbar = 'title="Játék vége! 🎉"'
new_gameover_appbar = "title={t('gameOver')}"
assert old_gameover_appbar in html, "FAIL: gameover appbar"
html = html.replace(old_gameover_appbar, new_gameover_appbar, 1)

# "Játék vége!" in game component
old_gameover_inline = ">Játék vége!</div>"
new_gameover_inline = ">{t('gameOver').replace(' 🎉','')}</div>"
assert old_gameover_inline in html, "FAIL: gameover inline"
html = html.replace(old_gameover_inline, new_gameover_inline, 1)

# "📈 Pontok alakulása"
old_points_progress = ">📈 Pontok alakulása</div>"
new_points_progress = ">{t('pointsProgress')}</div>"
assert old_points_progress in html, "FAIL: points progress"
html = html.replace(old_points_progress, new_points_progress, 1)

# "Bónusz esemény!"
old_bonus_event = ">Bónusz esemény!</div>"
new_bonus_event = ">{t('bonusEvent')}</div>"
assert old_bonus_event in html, "FAIL: bonus event"
html = html.replace(old_bonus_event, new_bonus_event, 1)

# "Csoportos Ivászat!"
old_group_drink = ">Csoportos Ivászat!</div>"
new_group_drink = ">{t('groupDrink')}</div>"
assert old_group_drink in html, "FAIL: group drink"
html = html.replace(old_group_drink, new_group_drink, 1)

# "🍻 Csoport" group button
old_group_btn = ">🍻 Csoport</button>"
new_group_btn = ">{t('groupBtn')}</button>"
assert old_group_btn in html, "FAIL: group btn"
html = html.replace(old_group_btn, new_group_btn, 1)

# "Játék indítása! ({selectedGames.length})"
old_start_game = "<span>Játék indítása! ({selectedGames.length})</span>"
new_start_game = "<span>{t('startGame')} ({selectedGames.length})</span>"
assert old_start_game in html, "FAIL: start game btn"
html = html.replace(old_start_game, new_start_game, 1)

# "Játék indítása" (initGame button)
old_start_game2 = ">Játék indítása</PrimaryButton>"
new_start_game2 = ">{t('startGameBtn')}</PrimaryButton>"
assert old_start_game2 in html, "FAIL: start game btn2"
html = html.replace(old_start_game2, new_start_game2, 1)

# "Játékos hozzáadása" button
old_add_player_btn = ">Játékos hozzáadása</span>"
new_add_player_btn = ">{t('addPlayerBtn')}</span>"
assert old_add_player_btn in html, "FAIL: add player btn"
html = html.replace(old_add_player_btn, new_add_player_btn, 1)

# "✓ Pontok kiszámítása"
old_calc_points = ">✓ Pontok kiszámítása</PrimaryButton>"
new_calc_points = ">{t('calcPoints')}</PrimaryButton>"
assert old_calc_points in html, "FAIL: calc points"
html = html.replace(old_calc_points, new_calc_points, 1)

# "Játékmód" section header
old_gamemode_section = ">Játékmód</div>"
new_gamemode_section = ">{t('gameModeSection')}</div>"
assert old_gamemode_section in html, "FAIL: gamemode section"
html = html.replace(old_gamemode_section, new_gamemode_section, 1)

# "Játékmenet" section header
old_gameplay_section = ">Játékmenet</div>"
new_gameplay_section = ">{t('gameplay')}</div>"
assert old_gameplay_section in html, "FAIL: gameplay section"
html = html.replace(old_gameplay_section, new_gameplay_section, 1)

# "Játéksorrend" section header
old_gameorder_section = ">Játéksorrend</div>"
new_gameorder_section = ">{t('gameOrder')}</div>"
assert old_gameorder_section in html, "FAIL: game order section"
html = html.replace(old_gameorder_section, new_gameorder_section, 1)

# ══════════════════════════════════════════════════════════════════════
# 5. Game modes and diffs arrays — use t() for labels/info/notes
# ══════════════════════════════════════════════════════════════════════

old_modes = """  const modes = [
    { id:'points',   label:'⭐ Pontgyűjtés',    info:'A játékosok minden győztes körnél csillagot kapnak. A legtöbb csillaggal rendelkező játékos nyeri a meccset.' },
    { id:'bonus',    label:'🎁 Bónusz képernyő', info:'Minden kör végén megjelenik egy rövid összefoglaló: ki nyert pontot és ki iszik.' },
    { id:'group',    label:'🍺 Csoportos ivás',  info:'Vesztes esetén az egész csapat iszik egyet, nem csak a vesztes játékos.' },
    { id:'wildcard', label:'🃏 Wildcard körök',  info:'Minden 5. kör elején megjelenik egy random különleges szabály (pl. bal kézzel inni, pókerpofa kör).' },
  ];
  const diffs = [
    { id:'easy',    label:'Könnyű',  note:'Hosszabb időzítők, megbocsátóbb feltételek. Ajánlott új játékosoknak.' },
    { id:'mid',     label:'Közepes', note:'Normál játéksebesség. Alapértelmezett beállítás.' },
    { id:'hard',    label:'Nehéz',   note:'Rövidebb időzítők. Gyors reflexek kellenek.' },
    { id:'extreme', label:'Extrém',  note:'Minimális idő, maximum nyomás. Csak a legbátrabbaknak!' },
  ];"""
new_modes = """  const modes = [
    { id:'points',   label:t('modePoints'),   info:t('modePointsInfo') },
    { id:'bonus',    label:t('modeBonus'),    info:t('modeBonusInfo') },
    { id:'group',    label:t('modeGroup'),    info:t('modeGroupInfo') },
    { id:'wildcard', label:t('modeWildcard'), info:t('modeWildcardInfo') },
  ];
  const diffs = [
    { id:'easy',    label:t('diffEasy'),    note:t('diffEasyNote') },
    { id:'mid',     label:t('diffMid'),     note:t('diffMidNote') },
    { id:'hard',    label:t('diffHard'),    note:t('diffHardNote') },
    { id:'extreme', label:t('diffExtreme'), note:t('diffExtremeNote') },
  ];"""
assert old_modes in html, "FAIL: modes/diffs"
html = html.replace(old_modes, new_modes, 1)

# ══════════════════════════════════════════════════════════════════════
# 6. Row labels for "Nem esik ki senki" and "Életek"
# ══════════════════════════════════════════════════════════════════════

old_noelim = 'label="Nem esik ki senki" sub="Játék akkor ér véget ha elfogy a pakli"'
new_noelim = "label={t('noElim')} sub={t('noElimSub')}"
assert old_noelim in html, "FAIL: noElim row"
html = html.replace(old_noelim, new_noelim, 1)

old_lives = 'label="Életek" sub="Játékosnak legyen életszáma"'
new_lives = "label={t('livesLabel')} sub={t('livesSub')}"
assert old_lives in html, "FAIL: lives row"
html = html.replace(old_lives, new_lives, 1)

# ══════════════════════════════════════════════════════════════════════
# 7. BonusOverlay — leader drinks / comeback text
# ══════════════════════════════════════════════════════════════════════

old_bonus_leader = "<div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', lineHeight:1.5 }}>A vezető iszik — <span style={{ color:T.coral, fontWeight:900 }}>{bonusOverlay.drinks} korty</span><br/>Mindenki más levesz egyet!</div>"
new_bonus_leader = "<div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', lineHeight:1.5 }}>{t('bonusLeaderDrinks').replace('{n}', bonusOverlay.drinks)}</div>"
assert old_bonus_leader in html, "FAIL: bonus leader"
html = html.replace(old_bonus_leader, new_bonus_leader, 1)

old_bonus_last = "<div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, textAlign:'center', lineHeight:1.5 }}>Az utolsó helyen álló<br/>visszakapaszkodik — <span style={{ color:T.mint, fontWeight:900 }}>+{bonusOverlay.points||1} pont</span></div>"
new_bonus_last = "<div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, textAlign:'center', lineHeight:1.5 }}>{t('bonusComebackPoints').replace('{n}', bonusOverlay.points||1)}</div>"
assert old_bonus_last in html, "FAIL: bonus last"
html = html.replace(old_bonus_last, new_bonus_last, 1)

# ══════════════════════════════════════════════════════════════════════
# 8. Observer round popup text
# ══════════════════════════════════════════════════════════════════════

old_obs_round = """            <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft, letterSpacing:'0.12em', textTransform:'uppercase', marginBottom:4 }}>📡 Körváltás</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:48, color:T.ink, lineHeight:1 }}>{obsRoundPopup.round}.</div>
            <div style={{ fontFamily:T.font, fontSize:14, fontWeight:700, color:T.inkSoft, marginTop:4 }}>Kör</div>"""
new_obs_round = """            <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft, letterSpacing:'0.12em', textTransform:'uppercase', marginBottom:4 }}>{t('obsRoundChange')}</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:48, color:T.ink, lineHeight:1 }}>{obsRoundPopup.round}.</div>
            <div style={{ fontFamily:T.font, fontSize:14, fontWeight:700, color:T.inkSoft, marginTop:4 }}>{t('roundWord')}</div>"""
assert old_obs_round in html, "FAIL: obs round"
html = html.replace(old_obs_round, new_obs_round, 1)

# ══════════════════════════════════════════════════════════════════════
# 9. Empty state "Válassz játékokat a kezdéshez!"
# ══════════════════════════════════════════════════════════════════════

old_choose_games = ">Válassz játékokat a kezdéshez!</div>"
new_choose_games = ">{t('chooseGames')}</div>"
assert old_choose_games in html, "FAIL: choose games empty"
html = html.replace(old_choose_games, new_choose_games, 1)

html = html.replace("const APP_VERSION = 'v9.318';", "const APP_VERSION = 'v9.319';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.319 — Full English translation: GAMES_EN, 35 TR keys, hardcoded string fixes")
