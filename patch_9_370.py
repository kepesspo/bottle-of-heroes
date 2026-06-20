#!/usr/bin/env python3
"""v9.370 — English: remaining in-game strings"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. HU TR keys ─────────────────────────────────
old_hu_end = """    startGame2: 'Rajt!',
  },"""
new_hu_end = """    startGame2: 'Rajt!',
    busDesc: 'A buszjáték egy különleges kör — kisebb-nagyobb tippeket kell mondani egy 6 lapos sorra. Ha rontasz, előről kezded és iszol.',
    busJoinCode: 'Ezen a kódon csatlakozz',
    busQrSub: 'Szkenneld be a kamerával, egyből a csatlakozó oldalra dob',
    busClose: 'Bezár',
    busReady: 'készen áll',
    busAutoStart: 'Indul automatikusan',
    busWhoAreYou: 'Te ki vagy?',
    busSelectName: 'Válaszd ki a neved — te is játszol',
    busZsulliMsg: 'Mind a 4 db kijött',
    busZsulliDrink: 'Mindenki iszik 1-et!',
    busBoardBtn: '🚌 Buszra szállás →',
    busNextCard: 'Következő lap →',
    busDone: 'Busz kész!',
    busDoneMsg: 'Mindenki teljesítette a buszjáratot!',
    busDrinksDuring: 'Buszozás alatt kapott',
    busSip: 'korty',
    busNowRiding: 'Most megy',
    busStep: 'lépés',
    busStops: 'Buszállomások',
    busDrawn: 'Húzott lapok',
    busLower: '▼ Kisebb',
    busHigher: '▲ Nagyobb',
    busWaitingPre: 'Várjuk',
    busWaitingPost: 'tippjét a saját telefonján…',
    busHostOverride: 'Host beavatkozás — tippelj helyette',
    busUnlucky: 'Szerencsétlen!',
    busUnluckyMsg: 'Az utolsó lapnál hibáztál. Kezd előlről!',
    busGenius: '💡🎉 Zseniális! Leugrott!',
    busFailed: '💡✗ Nem sikerült!',
    busCompleted: '🎉 Teljesítve!',
    busCorrect: '✓ Helyes!',
    busWrong: '✗ Rossz!',
    busSipUnit: 'kortynyi',
    busSettings: 'Busz beállítások',
    busDecks: 'Paklik száma',
    busCardsPerPlayer: 'Lapok/játékos',
    busPyramidRows: 'Piramis sorok',
    busStepsLabel: 'Busz lépések',
    busZsulliToggle: 'Zsülli jelzés',
    busGeniusTip: 'Zseniális tipp',
    busGeniusTipDesc: 'Buszra szállásnál 1 mega-tipp: ha eltalálja azonnal leugrik',
    busHostPlays: '🎮 Host is játszik',
    busHostPlaysSub: 'A host a saját telefonján kártyázik is',
    busDoneBtn: 'Kész',
    rulettDraws: 'húz!',
    rulettDouble: '2× pia',
    rulettStar: '1× csillag',
    rulettSelected: 'VÁLASZTVA',
    rulettDrink: '🍺 Pia! Iszol!',
    rulettSafe: '⭐ Csillag! Megúsztad!',
    rulettChill: 'Nyugi',
    rulettScared: 'Para 😬',
    uvegTap: 'Koppints a pörgetésre 👆',
    uvegDrinks: 'iszik!',
    kategoriaLabel: 'KATEGÓRIA',
    kategoriaWhoFailed: 'Ki nem tudott szót mondani?',
    katNoFail: 'Senki nem rontott ✓',
    katDrinks: 'iszik egyet',
    kezRound: 'KÖR',
    kezMistake: 'RONTÁS',
    kezWhoFailed: 'Ki rontott el?',
    kezFinish: '🏁 Befejezés',
    kezNextRound: 'Következő kör',
    kezNoMistakes: 'Mindenki hibátlan!',
    kezMistakeCount: 'rontás',
    collectChooses: 'választ',
    collectCollected: 'GYŰJTVE',
    mindenkiDrinks: 'iszik egyet',
    mindenkiOrder: 'Sorrend',
    mindenkiNext: 'Kövi',
    mindenkiYourTurn: 'Te jössz — húzz le egy jó kortyot!',
    sohanemBasic: 'ALAP',
    sohanemMedium: 'KÖZEPES',
    sohanemWild: 'VAD',
    sohanemPrefix: 'Én még soha nem…',
    kivagyokHint: 'Tippeld meg a hírességet — aztán fedd fel az aktát.',
    kivagyokReveal: 'Akta felfedése',
    kivagyokKnew: 'Megismertem! 🎉',
    otdologCategory: 'KATEGÓRIA',
    otdologReveal: 'Felfed & Indít',
    otdologAllDone: 'Mind megvan!',
    otdologGo: 'megvan — hajrá!',
    otdologTimeUp: 'Idő lejárt!',
    otdologMark: 'Jelöld be amit kimondottál!',
    ticktakHeld: 'tartotta a tárgyat — iszik egyet',
    ticktakDesc: 'Körbeadjátok a tárgyat! Az időzítő titokban indul — mikor cseng, annál a játékosnál aki épp tartja.',
    ticktakStart: 'Időzítő indítása!',
    ticktakRunning: 'Megy!',
    ticktakPass: 'Adjátok körbe a tárgyat!',
    ticktakBuzz: 'CSÖRÖG! 🔔',
    ticktakWhoheld: 'Kinél volt a tárgy a kezében?',
    eremWins: 'nyert',
    eremOpponentDrinks: 'iszik',
    eremLoses: 'veszített — iszik egyet',
    eremHeads: 'FEJ',
    eremTails: 'ÍRÁS',
    eremFlipping: 'Repül a levegőben…',
    tapperChallenger: 'KIHÍVÓ',
    tapperOpponent: 'ELLENFÉL',
    tapperHold: 'TARTSD',
    tapperTooLate: 'KÉSŐ',
    tapperWaiting: 'Várakozás a másik játékosra…',
    tapperBothFail: 'Mindkettő túlment — mindkettő iszik!',
    tapperDraw: 'Döntetlen!',
    tapperWins: 'nyert!',
    tapperDrinks: 'iszik.',
    anagrammaTimeLeft: 'mp',
    anagrammaWin: 'Megvan! A szó:',
    anagrammaTimeUp: 'Idő lejárt! A szó:',
    memoriaFlips: 'fordít lapot',
    memoriaMatch: 'talált egy párt!',
  },"""
assert old_hu_end in html, "FAIL: hu end"
html = html.replace(old_hu_end, new_hu_end, 1)

# ── 2. EN TR keys ─────────────────────────────────
old_en_end = """    startGame2: 'Start!',
  },"""
new_en_end = """    startGame2: 'Start!',
    busDesc: 'The Bus is a special round — guess higher or lower on a 6-card row. If you get it wrong, start over and drink.',
    busJoinCode: 'Join with this code',
    busQrSub: 'Scan with your camera to go straight to the join page',
    busClose: 'Close',
    busReady: 'ready',
    busAutoStart: 'Starting automatically',
    busWhoAreYou: 'Who are you?',
    busSelectName: "Select your name — you're playing too",
    busZsulliMsg: 'All 4 came out',
    busZsulliDrink: 'Everyone drinks 1!',
    busBoardBtn: '🚌 Board the Bus →',
    busNextCard: 'Next Card →',
    busDone: 'Bus Done!',
    busDoneMsg: 'Everyone completed the bus ride!',
    busDrinksDuring: 'Drinks during bus ride',
    busSip: 'sip',
    busNowRiding: 'Riding now',
    busStep: 'step',
    busStops: 'Bus Stops',
    busDrawn: 'Drawn Cards',
    busLower: '▼ Lower',
    busHigher: '▲ Higher',
    busWaitingPre: 'Waiting for',
    busWaitingPost: 'to guess on their phone…',
    busHostOverride: 'Host override — guess for them',
    busUnlucky: 'Unlucky!',
    busUnluckyMsg: 'Wrong on the last card. Start over!',
    busGenius: '💡🎉 Genius! Jumped off!',
    busFailed: '💡✗ Failed!',
    busCompleted: '🎉 Completed!',
    busCorrect: '✓ Correct!',
    busWrong: '✗ Wrong!',
    busSipUnit: 'sips',
    busSettings: 'Bus Settings',
    busDecks: 'Number of Decks',
    busCardsPerPlayer: 'Cards/Player',
    busPyramidRows: 'Pyramid Rows',
    busStepsLabel: 'Bus Steps',
    busZsulliToggle: 'Jackpot Signal',
    busGeniusTip: 'Genius Tip',
    busGeniusTipDesc: 'At bus boarding, 1 mega-guess: if correct, jump off immediately',
    busHostPlays: '🎮 Host plays too',
    busHostPlaysSub: 'Host also plays cards on their own phone',
    busDoneBtn: 'Done',
    rulettDraws: 'draws!',
    rulettDouble: '2× drink',
    rulettStar: '1× star',
    rulettSelected: 'SELECTED',
    rulettDrink: '🍺 Drink! You drink!',
    rulettSafe: '⭐ Star! You made it!',
    rulettChill: 'Chill',
    rulettScared: 'Nervous 😬',
    uvegTap: 'Tap to spin 👆',
    uvegDrinks: 'drinks!',
    kategoriaLabel: 'CATEGORY',
    kategoriaWhoFailed: 'Who could not say a word?',
    katNoFail: 'No one failed ✓',
    katDrinks: 'drinks one',
    kezRound: 'RND',
    kezMistake: 'MISTAKE',
    kezWhoFailed: 'Who made a mistake?',
    kezFinish: '🏁 Finish',
    kezNextRound: 'Next Round',
    kezNoMistakes: 'Everyone flawless!',
    kezMistakeCount: 'mistake(s)',
    collectChooses: 'chooses',
    collectCollected: 'COLLECTED',
    mindenkiDrinks: 'drinks one',
    mindenkiOrder: 'Order',
    mindenkiNext: 'Next',
    mindenkiYourTurn: "Your turn — take a good sip!",
    sohanemBasic: 'BASIC',
    sohanemMedium: 'MEDIUM',
    sohanemWild: 'WILD',
    sohanemPrefix: 'I have never…',
    kivagyokHint: 'Guess the celebrity — then reveal the file.',
    kivagyokReveal: 'Reveal File',
    kivagyokKnew: 'I knew it! 🎉',
    otdologCategory: 'CATEGORY',
    otdologReveal: 'Reveal & Start',
    otdologAllDone: 'All done!',
    otdologGo: 'done — go!',
    otdologTimeUp: "Time's up!",
    otdologMark: 'Check off what you said!',
    ticktakHeld: 'was holding it — drinks one',
    ticktakDesc: 'Pass the object around! The timer starts secretly — whoever holds it when it rings must drink.',
    ticktakStart: 'Start Timer!',
    ticktakRunning: 'Going!',
    ticktakPass: 'Pass the object around!',
    ticktakBuzz: 'BUZZ! 🔔',
    ticktakWhoheld: 'Who was holding the object?',
    eremWins: 'wins',
    eremOpponentDrinks: 'drinks',
    eremLoses: 'lost — drinks one',
    eremHeads: 'HEADS',
    eremTails: 'TAILS',
    eremFlipping: 'Flying in the air…',
    tapperChallenger: 'CHALLENGER',
    tapperOpponent: 'OPPONENT',
    tapperHold: 'HOLD',
    tapperTooLate: 'TOO LATE',
    tapperWaiting: 'Waiting for the other player…',
    tapperBothFail: 'Both too late — both drink!',
    tapperDraw: 'Draw!',
    tapperWins: 'wins!',
    tapperDrinks: 'drinks.',
    anagrammaTimeLeft: 's',
    anagrammaWin: 'Got it! The word:',
    anagrammaTimeUp: "Time's up! The word:",
    memoriaFlips: 'flips a card',
    memoriaMatch: 'found a pair!',
  },"""
assert old_en_end in html, "FAIL: en end"
html = html.replace(old_en_end, new_en_end, 1)

# ── 3. BUSZ CONFIG ─────────────────────────────────
html = html.replace("{ key:'busSteps',       label:'Busz lépések',        min:4, max:8 },",
                    "{ key:'busSteps',       label:t('busStepsLabel'),    min:4, max:8 },")
html = html.replace("{ key:'decks',          label:'Paklik száma',         min:1, max:4 },",
                    "{ key:'decks',          label:t('busDecks'),          min:1, max:4 },")
html = html.replace("{ key:'cardsPerPlayer', label:'Lapok/játékos',        min:4, max:10 },",
                    "{ key:'cardsPerPlayer', label:t('busCardsPerPlayer'), min:4, max:10 },")
html = html.replace("{ key:'pyramidRows',    label:'Piramis sorok',        min:2, max:7 },",
                    "{ key:'pyramidRows',    label:t('busPyramidRows'),    min:2, max:7 },")
html = html.replace(">Busz beállítások</div>", ">{t('busSettings')}</div>")
html = html.replace(">Zsülli jelzés</span>", ">{t('busZsulliToggle')}</span>")
html = html.replace(">Zseniális tipp</span>", ">{t('busGeniusTip')}</span>")
html = html.replace(">Buszra szállásnál 1 mega-tipp: ha eltalálja azonnal leugrik</div>",
                    ">{t('busGeniusTipDesc')}</div>")
html = html.replace(">🎮 Host is játszik</span>", ">{t('busHostPlays')}</span>")
html = html.replace(">A host a saját telefonján kártyázik is</div>", ">{t('busHostPlaysSub')}</div>")
html = html.replace(
    "boxShadow:'0 5px 16px -5px rgba(79,194,160,0.6)', marginTop:16 }}>Kész</button>",
    "boxShadow:'0 5px 16px -5px rgba(79,194,160,0.6)', marginTop:16 }}>{t('busDoneBtn')}</button>"
)

# ── 4. BUSZ GAME ───────────────────────────────────
html = html.replace(
    "lineHeight:1.5}}>A buszjáték egy különleges kör — kisebb-nagyobb tippeket kell mondani egy 6 lapos sorra. Ha rontasz, előről kezded és iszol.</div>",
    "lineHeight:1.5}}>{t('busDesc')}</div>"
)
html = html.replace(">Ezen a kódon csatlakozz</div>", ">{t('busJoinCode')}</div>")
html = html.replace(">Szkenneld be a kamerával,<br/>egyből a csatlakozó oldalra dob</div>", ">{t('busQrSub')}</div>")
html = html.replace("cursor:'pointer'}}>Bezár</button>", "cursor:'pointer'}}>{t('busClose')}</button>")
html = html.replace(
    ">{isOnline?takenIds.length:players.length} készen áll</div>",
    ">{isOnline?takenIds.length:players.length} {t('busReady')}</div>"
)
html = html.replace(">Indul automatikusan</div>", ">{t('busAutoStart')}</div>")
html = html.replace(">Te ki vagy?</div>", ">{t('busWhoAreYou')}</div>")
html = html.replace(">Válaszd ki a neved — te is játszol</div>", ">{t('busSelectName')}</div>")
html = html.replace(
    "Mind a 4 db <b style={{color:T.mint}}>{zsulliAnim}</b> kijött</div>",
    "{t('busZsulliMsg')} <b style={{color:T.mint}}>{zsulliAnim}</b></div>"
)
html = html.replace(">Mindenki iszik 1-et!</", ">{t('busZsulliDrink')}</")
html = html.replace(">🚌 Buszra szállás →<", ">{t('busBoardBtn')}<")
html = html.replace(">Következő lap →<", ">{t('busNextCard')}<")
html = html.replace(">Busz kész!</", ">{t('busDone')}</")
html = html.replace(">Mindenki teljesítette a buszjáratot!</", ">{t('busDoneMsg')}</")
html = html.replace(">Buszozás alatt kapott</", ">{t('busDrinksDuring')}</")
html = html.replace("> korty</", "> {t('busSip')}</")
html = html.replace(">Most megy<", ">{t('busNowRiding')}<")
html = html.replace(">Buszállomások<", ">{t('busStops')}<")
html = html.replace(">Húzott lapok<", ">{t('busDrawn')}<")
html = html.replace(
    ">⏳ Várjuk <b style={{color:T.ink}}>{currentRider?.name || '?'}</b> tippjét a saját telefonján…<",
    ">⏳ {t('busWaitingPre')} <b style={{color:T.ink}}>{currentRider?.name || '?'}</b> {t('busWaitingPost')}<"
)
html = html.replace(">Host beavatkozás — tippelj helyette<", ">{t('busHostOverride')}<")
html = html.replace(">Szerencsétlen!</", ">{t('busUnlucky')}</")
html = html.replace(">Az utolsó lapnál hibáztál.<br/>Kezd előlről!</", ">{t('busUnluckyMsg')}</")
html = html.replace("'💡🎉 Zseniális! Leugrott!'", "t('busGenius')")
html = html.replace(
    "'💡✗ Nem sikerült! '+(guessResult.drinks||1)+' korty!'",
    "t('busFailed')+' '+(guessResult.drinks||1)+' '+t('busSipUnit')+'!'"
)
html = html.replace("'🎉 Teljesítve!'", "t('busCompleted')")
html = html.replace("'✓ Helyes!'", "t('busCorrect')")
html = html.replace(
    "'✗ Rossz! '+guessResult.drinks+' kortynyi!'",
    "t('busWrong')+' '+guessResult.drinks+' '+t('busSipUnit')+'!'"
)
html = html.replace(
    "sendBusGuess('lower')} style={{flex:1,padding:'14px 0',borderRadius:14,border:'none',background:'#EEF2FF',color:'#4461C2',fontFamily:T.font,fontWeight:900,fontSize:16,cursor:'pointer'}}>▼ Kisebb</button>",
    "sendBusGuess('lower')} style={{flex:1,padding:'14px 0',borderRadius:14,border:'none',background:'#EEF2FF',color:'#4461C2',fontFamily:T.font,fontWeight:900,fontSize:16,cursor:'pointer'}}>{t('busLower')}</button>"
)
html = html.replace(
    "sendBusGuess('higher')} style={{flex:1,padding:'14px 0',borderRadius:14,border:'none',background:'#EEF2FF',color:'#4461C2',fontFamily:T.font,fontWeight:900,fontSize:16,cursor:'pointer'}}>▲ Nagyobb</button>",
    "sendBusGuess('higher')} style={{flex:1,padding:'14px 0',borderRadius:14,border:'none',background:'#EEF2FF',color:'#4461C2',fontFamily:T.font,fontWeight:900,fontSize:16,cursor:'pointer'}}>{t('busHigher')}</button>"
)
html = html.replace(
    "makeHostGuess('lower')} style={{flex:1,padding:'14px 0',borderRadius:14,border:'none',background:'#EEF2FF',color:'#4461C2',fontFamily:T.font,fontWeight:900,fontSize:16,cursor:'pointer'}}>▼ Kisebb</button>",
    "makeHostGuess('lower')} style={{flex:1,padding:'14px 0',borderRadius:14,border:'none',background:'#EEF2FF',color:'#4461C2',fontFamily:T.font,fontWeight:900,fontSize:16,cursor:'pointer'}}>{t('busLower')}</button>"
)
html = html.replace(
    "makeHostGuess('higher')} style={{flex:1,padding:'14px 0',borderRadius:14,border:'none',background:'#EEF2FF',color:'#4461C2',fontFamily:T.font,fontWeight:900,fontSize:16,cursor:'pointer'}}>▲ Nagyobb</button>",
    "makeHostGuess('higher')} style={{flex:1,padding:'14px 0',borderRadius:14,border:'none',background:'#EEF2FF',color:'#4461C2',fontFamily:T.font,fontWeight:900,fontSize:16,cursor:'pointer'}}>{t('busHigher')}</button>"
)
html = html.replace("> lépés<", "> {t('busStep')}<")

# ── 5. RULETT ─────────────────────────────────────
html = html.replace(">{challenger.name} húz!</", ">{challenger.name} {t('rulettDraws')}</")
html = html.replace(">2× pia<", ">{t('rulettDouble')}<")
html = html.replace(">1× csillag<", ">{t('rulettStar')}<")
html = html.replace(">VÁLASZTVA<", ">{t('rulettSelected')}<")
html = html.replace(">🍺 Pia! Iszol!</", ">{t('rulettDrink')}</")
html = html.replace(">⭐ Csillag! Megúsztad!</", ">{t('rulettSafe')}</")
html = html.replace(">Nyugi<", ">{t('rulettChill')}<")
html = html.replace(">Para 😬<", ">{t('rulettScared')}<")

# ── 6. UVEG ───────────────────────────────────────
html = html.replace(">Koppints a pörgetésre 👆<", ">{t('uvegTap')}<")
html = html.replace(">🍺 {winner.name} iszik!</", ">🍺 {winner.name} {t('uvegDrinks')}<")

# ── 7. KATEGORIA ──────────────────────────────────
old_kat = """  const CATS = [
    'Fővárosok','Gyümölcsök','Sportágak','Filmek','Állatok',
    'Autómárkák','Zenekarok','Ételek','Országok','TV-sorozatok',
    'Focicsapatok','Koktélok','Énekes előadók','Játékok','Foglalkozások',
    'Hangszerek','Tánctípusok','Borok','Folyók','Magyar városok',
    'Filmhősök','Ruhamárkák','Könyvek','Olimpiai sportok','Helyek Budapesten',
    'Zöldségek','Sütemények','Filmrendezők','Állatfajok','Csapatjátékok',
  ];"""
new_kat = """  const CATS_HU = [
    'Fővárosok','Gyümölcsök','Sportágak','Filmek','Állatok',
    'Autómárkák','Zenekarok','Ételek','Országok','TV-sorozatok',
    'Focicsapatok','Koktélok','Énekes előadók','Játékok','Foglalkozások',
    'Hangszerek','Tánctípusok','Borok','Folyók','Magyar városok',
    'Filmhősök','Ruhamárkák','Könyvek','Olimpiai sportok','Helyek Budapesten',
    'Zöldségek','Sütemények','Filmrendezők','Állatfajok','Csapatjátékok',
  ];
  const CATS_EN = [
    'Capitals','Fruits','Sports','Movies','Animals',
    'Car Brands','Bands','Foods','Countries','TV Shows',
    'Football Clubs','Cocktails','Solo Artists','Games','Occupations',
    'Instruments','Dance Styles','Wines','Rivers','Hungarian Cities',
    'Movie Heroes','Fashion Brands','Books','Olympic Sports','Places in Budapest',
    'Vegetables','Pastries','Film Directors','Animal Species','Team Sports',
  ];
  const CATS = LANG==='en' ? CATS_EN : CATS_HU;"""
assert old_kat in html, "FAIL: kat categories"
html = html.replace(old_kat, new_kat, 1)

html = html.replace(">KATEGÓRIA<", ">{t('kategoriaLabel')}<", 1)
html = html.replace(">Ki nem tudott szót mondani?<", ">{t('kategoriaWhoFailed')}<")
html = html.replace(">.find(p=>p.id===loserPid)?.name} iszik egyet<",
                    ">.find(p=>p.id===loserPid)?.name} {t('katDrinks')}<")
html = html.replace(">Senki nem rontott ✓<", ">{t('katNoFail')}<")

# ── 8. KEZ CSERE ──────────────────────────────────
html = html.replace(">Mindenki hibátlan!</", ">{t('kezNoMistakes')}</")
html = html.replace("${dm[p.id]} rontás", "${dm[p.id]} ${t('kezMistakeCount')}")
html = html.replace(">KÖR<", ">{t('kezRound')}<")
html = html.replace(">RONTÁS<", ">{t('kezMistake')}<")
html = html.replace(">Ki rontott el?<", ">{t('kezWhoFailed')}<")
html = html.replace(">🏁 Befejezés<", ">{t('kezFinish')}<")
html = html.replace(">Következő kör ({round}/{TOTAL_ROUNDS}) →<",
                    ">{t('kezNextRound')} ({round}/{TOTAL_ROUNDS}) →<")

# ── 9. COLLECT ────────────────────────────────────
html = html.replace(">{currentPlayer?.name} választ<", ">{currentPlayer?.name} {t('collectChooses')}<")
html = html.replace(">GYŰJTVE<", ">{t('collectCollected')}<")

# ── 10. MINDENKI ──────────────────────────────────
html = html.replace("> iszik egyet<", "> {t('mindenkiDrinks')}<")
html = html.replace(">Te jössz — húzz le egy jó kortyot!</", ">{t('mindenkiYourTurn')}</")
html = html.replace(">Kövi<", ">{t('mindenkiNext')}<")
html = html.replace(">Sorrend<", ">{t('mindenkiOrder')}<")

# ── 11. SOHANEM ───────────────────────────────────
html = html.replace(
    "[['ALAP', 'basic'], ['KÖZEPES', 'medium'], ['VAD', 'wild']].map(([label, key])",
    "[[t('sohanemBasic'), 'basic'], [t('sohanemMedium'), 'medium'], [t('sohanemWild'), 'wild']].map(([label, key])"
)
html = html.replace(">Én még soha nem…<", ">{t('sohanemPrefix')}<")

# ── 12. KIVAGYOK ──────────────────────────────────
html = html.replace(">Tippeld meg a hírességet — aztán fedd fel az aktát.<", ">{t('kivagyokHint')}<")
html = html.replace(">Akta felfedése<", ">{t('kivagyokReveal')}<")
html = html.replace(">Megismertem! 🎉<", ">{t('kivagyokKnew')}<")

# ── 13. OT DOLOG ──────────────────────────────────
html = html.replace(">KATEGÓRIA<", ">{t('otdologCategory')}<", 1)  # second occurrence
html = html.replace(">Felfed & Indít<", ">{t('otdologReveal')}<")
html = html.replace(">Mind megvan!</", ">{t('otdologAllDone')}</")
html = html.replace("megvan — hajrá!", "{t('otdologGo')}")
html = html.replace(">Idő lejárt!</", ">{t('otdologTimeUp')}</")
html = html.replace(">Jelöld be amit kimondottál!</", ">{t('otdologMark')}</")

# ── 14. TICKTAK ───────────────────────────────────
html = html.replace("tartotta a tárgyat — iszik egyet", "{t('ticktakHeld')}")
html = html.replace(
    ">Körbeadjátok a tárgyat! Az időzítő titokban indul — mikor cseng, annál a játékosnál aki épp tartja.<",
    ">{t('ticktakDesc')}<"
)
html = html.replace(">Időzítő indítása!</", ">{t('ticktakStart')}</")
html = html.replace(">Megy!</", ">{t('ticktakRunning')}</")
html = html.replace(">Adjátok körbe a tárgyat!</", ">{t('ticktakPass')}</")
html = html.replace(">CSÖRÖG! 🔔<", ">{t('ticktakBuzz')}<")
html = html.replace(">Kinél volt a tárgy a kezében?<", ">{t('ticktakWhoheld')}<")

# ── 15. EREM ──────────────────────────────────────
html = html.replace(
    "`${mLeader?.name||'?'} nyert — ${opponent?.name||'ellenfél'} iszik`",
    "`${mLeader?.name||'?'} ${t('eremWins')} — ${opponent?.name||'?'} ${t('eremOpponentDrinks')}`"
)
html = html.replace(
    "`${mLeader?.name||'?'} veszített — iszik egyet`",
    "`${mLeader?.name||'?'} ${t('eremLoses')}`"
)
html = html.replace(">FEJ<", ">{t('eremHeads')}<")
html = html.replace(">ÍRÁS<", ">{t('eremTails')}<")
html = html.replace(">FEJ LETT<", ">{t('eremHeads')}<")
html = html.replace(">ÍRÁS LETT<", ">{t('eremTails')}<")
html = html.replace(">Repül a levegőben…<", ">{t('eremFlipping')}<")

# ── 16. TAPPER ────────────────────────────────────
html = html.replace(">KIHÍVÓ<", ">{t('tapperChallenger')}<")
html = html.replace(">ELLENFÉL<", ">{t('tapperOpponent')}<")
html = html.replace(">TARTSD<", ">{t('tapperHold')}<")
html = html.replace(">KÉSŐ<", ">{t('tapperTooLate')}<")
html = html.replace(">Várakozás a másik játékosra…<", ">{t('tapperWaiting')}<")
html = html.replace(">Mindkettő túlment — mindkettő iszik!</", ">{t('tapperBothFail')}</")
html = html.replace(">Döntetlen!</", ">{t('tapperDraw')}</")
html = html.replace(
    "`${p1.name} nyert! ${p2.name} iszik.`",
    "`${p1.name} ${t('tapperWins')} ${p2.name} ${t('tapperDrinks')}`"
)
html = html.replace(
    "`${p2.name} nyert! ${p1.name} iszik.`",
    "`${p2.name} ${t('tapperWins')} ${p1.name} ${t('tapperDrinks')}`"
)

# ── 17. ANAGRAMMA ─────────────────────────────────
html = html.replace(">{timeLeft} mp<", ">{timeLeft} {t('anagrammaTimeLeft')}<")
html = html.replace(">Megvan! A szó: {word}<", ">{t('anagrammaWin')} {word}<")
html = html.replace(
    "Idő lejárt! A szó: <strong>{word}</strong>",
    "{t('anagrammaTimeUp')} <strong>{word}</strong>"
)

# ── 18. MEMORIA ───────────────────────────────────
html = html.replace("> fordít lapot<", "> {t('memoriaFlips')}<")
html = html.replace("> talált egy párt!</", "> {t('memoriaMatch')}</")

# ── 19. VERSION ───────────────────────────────────
html = html.replace("const APP_VERSION = 'v9.369';", "const APP_VERSION = 'v9.370';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.370 — all remaining in-game Hungarian strings translated")
