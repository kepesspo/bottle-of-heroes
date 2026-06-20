#!/usr/bin/env python3
"""v9.400 — Kvíz játék: Press Your Luck mechanika, 6 kategória, 120 kérdés"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. GAMES bejegyzés ────────────────────────────────────────────────────────
old_last_game = """  { id:'cardbattle', roundTime:'mid', name:'Kártyacsata', difficulty:'közepes', category:'Páros', emoji:'🃏', symbol:null, img:null, banner:null, color:'#8B5CF6', desc:'Mindkét játékos 5 lapot oszt szét 5 körre (összérték: 25). A magasabb összeget befektető játékos nyeri a kört — döntetnél a tét továbbbgördül. Aki több kört nyer, az győz!' },
];"""

new_last_game = """  { id:'cardbattle', roundTime:'mid', name:'Kártyacsata', difficulty:'közepes', category:'Páros', emoji:'🃏', symbol:null, img:null, banner:null, color:'#8B5CF6', desc:'Mindkét játékos 5 lapot oszt szét 5 körre (összérték: 25). A magasabb összeget befektető játékos nyeri a kört — döntetnél a tét továbbbgördül. Aki több kört nyer, az győz!' },
  { id:'quiz', roundTime:'mid', name:'Kvíz', difficulty:'közepes', category:'Egyéni', emoji:'🧠', symbol:null, img:null, banner:null, color:'#6366F1', desc:'Válaszolj a kérdésekre! Helyes válasz után pontot vehetsz — vagy tovább mersz menni és kortyokat gyűjthetsz osztogatásra. Ha tovább mégy és hibázol, te iszol annyit ahány kördnél vesztetted.' },
];"""

assert old_last_game in html, "FAIL: games array"
html = html.replace(old_last_game, new_last_game, 1)

# ── 2. SCENARIOS bejegyzés ────────────────────────────────────────────────────
old_scenario = """  cardbattle:  { prompt:'', cta:[] },
};"""
new_scenario = """  cardbattle:  { prompt:'', cta:[] },
  quiz:        { prompt:'', cta:[] },
};"""
assert old_scenario in html, "FAIL: scenarios"
html = html.replace(old_scenario, new_scenario, 1)

# ── 3. GameContent: quiz hozzáadása ──────────────────────────────────────────
old_gc = """  if (gameId === 'cardbattle') return <CardBattleGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} />;
  return null;
}"""
new_gc = """  if (gameId === 'cardbattle') return <CardBattleGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} />;
  if (gameId === 'quiz') return <QuizGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} players={players||[]} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} gameMeta={gameMeta} />;
  return null;
}"""
assert old_gc in html, "FAIL: gamecontent"
html = html.replace(old_gc, new_gc, 1)

# ── 4. QuizGame komponens ─────────────────────────────────────────────────────
quiz_component = """
function QuizGame({ gameIdx, challenger, players, onAdvance, onResult, onSetHideFooter, gameMeta }) {
  const QUIZ_DB = {
    altalanos: { label:'Általános 🧠', qs:[
      {q:'Hány oldala van egy kockának?', a:['6','4','8','12']},
      {q:'Mi a Föld legnagyobb óceánja?', a:['Csendes-óceán','Atlanti-óceán','Indiai-óceán','Jeges-tenger']},
      {q:'Hány bolygó van a Naprendszerben?', a:['8','7','9','10']},
      {q:'Mi a világ leghosszabb folyója?', a:['Nílus','Amazonas','Jangce','Mississippi']},
      {q:'Melyik állat a leggyorsabb a szárazföldön?', a:['Gepárd','Oroszlán','Strucc','Antilopе']},
      {q:'Ki festette a Mona Lisát?', a:['Leonardo da Vinci','Michelangelo','Raphael','Botticelli']},
      {q:'Melyik évben volt az első holdra szállás?', a:['1969','1972','1965','1957']},
      {q:'Mi a legkisebb ország a világon?', a:['Vatikán','Monakó','San Marino','Liechtenstein']},
      {q:'Mi a kémiai jele az aranynak?', a:['Au','Ag','Fe','Cu']},
      {q:'Hány szín van a szivárványban?', a:['7','6','5','8']},
      {q:'Mi az emberi test leghosszabb csontja?', a:['Combcsont','Lábszárcsont','Felkarcsont','Gerinc']},
      {q:'Melyik bolygó a Naphoz a legközelebb?', a:['Merkúr','Vénusz','Mars','Föld']},
      {q:'Hány fok van egy egyenes szögben?', a:['180°','90°','270°','360°']},
      {q:'Ki írta a Rómeó és Júliát?', a:['Shakespeare','Dickens','Molière','Dante']},
      {q:'Melyik évben kezdődött az első világháború?', a:['1914','1939','1918','1905']},
      {q:'Mi a világ legmagasabb hegycsúcsa?', a:['Mount Everest','K2','Kilimandzsáró','Mont Blanc']},
      {q:'Hány fogad van egy felnőtt embernek?', a:['32','28','30','36']},
      {q:'Mi az internet protokollja röviden?', a:['HTTP','FTP','HTML','CSS']},
      {q:'Melyik városban van a Colosseum?', a:['Róma','Athén','Párizs','Madrid']},
      {q:'Hány hete van egy évnek?', a:['52','48','54','50']},
    ]},
    sport: { label:'Sport ⚽', qs:[
      {q:'Melyik ország nyerte a 2022-es futball-vb-t?', a:['Argentína','Franciaország','Brazília','Horvátország']},
      {q:'Hány játékos van egy kosárlabda csapatban a pályán?', a:['5','6','4','7']},
      {q:'Melyik teniszversenyt játszák salakos pályán?', a:['Roland Garros','Wimbledon','US Open','Australian Open']},
      {q:'Ki nyerte a legtöbb Grand Slam tornát (férfi)?', a:['Novak Djokovic','Rafael Nadal','Roger Federer','Pete Sampras']},
      {q:'Hány perc egy labdarúgó mérkőzés rendes játékideje?', a:['90','80','100','120']},
      {q:'Ki nyerte a legtöbb olimpiai aranyérmet?', a:['Michael Phelps','Usain Bolt','Mark Spitz','Carl Lewis']},
      {q:'Hány csapat játszik az NFL-ben?', a:['32','28','30','36']},
      {q:'Melyik sport az úszás+kerékpározás+futás kombinációja?', a:['Triatlon','Pentatlon','Biatlon','Duatlon']},
      {q:'Melyik városban van az FC Barcelona stadionja?', a:['Barcelona','Madrid','Valencia','Sevilla']},
      {q:'Ki nyerte a 2023-as Forma-1 világbajnokságot?', a:['Max Verstappen','Lewis Hamilton','Charles Leclerc','Lando Norris']},
      {q:'Hány méteres a 100 méteres sprint?', a:['100','50','200','400']},
      {q:'Melyik városban rendezték az 1896-os első modern olimpiát?', a:['Athén','Párizs','London','Stockholm']},
      {q:'Hány pontot ér egy kosárlabda-mérkőzésen a hárompontos dobás?', a:['3','2','4','1']},
      {q:'Melyik sportban van a Ryder Cup verseny?', a:['Golf','Tenisz','Snooker','Polo']},
      {q:'Melyik városban van a Wembley Stadion?', a:['London','Manchester','Birmingham','Liverpool']},
      {q:'Hány körig tart egy profi bokszmérkőzés?', a:['12','10','15','8']},
      {q:'Melyik sport a Forma-1?', a:['Autóverseny','Motorverseny','Kamionverseny','Rallyverseny']},
      {q:'Ki a legtöbb FIFA Aranylabdát nyert játékos?', a:['Lionel Messi','Cristiano Ronaldo','Ronaldo','Zinedine Zidane']},
      {q:'Hány méteres a 400 méteres atlétika futam?', a:['400','200','800','100']},
      {q:'Melyik ország olimpiai zászlóján nincs szín?', a:['Japán... valójában egyik sem — Olimpia jelkép 5 színű','Dánia','Svájc','Kanada']},
    ]},
    zene: { label:'Zene 🎵', qs:[
      {q:'Ki énekli a "Bohemian Rhapsody"-t?', a:['Freddie Mercury (Queen)','David Bowie','Elton John','Mick Jagger']},
      {q:'Hány billentyű van egy klasszikus zongorán?', a:['88','72','96','80']},
      {q:'Melyik országból való az ABBA?', a:['Svédország','Norvégia','Dánia','Finnország']},
      {q:'Kit hívnak a "Pop királyának"?', a:['Michael Jackson','Elvis Presley','Justin Timberlake','Bruno Mars']},
      {q:'Ki énekelte a "Hello"-t (2015)?', a:['Adele','Beyoncé','Taylor Swift','Rihanna']},
      {q:'Melyik banda énekelte a "Smells Like Teen Spirit"-et?', a:['Nirvana','Pearl Jam','Soundgarden','Alice in Chains']},
      {q:'Ki énekli a "Shape of You"-t?', a:['Ed Sheeran','Sam Smith','Harry Styles','Shawn Mendes']},
      {q:'Melyik évben jelent meg a "Thriller" album?', a:['1982','1979','1985','1980']},
      {q:'Ki komponálta az "Örömódát"?', a:['Beethoven','Mozart','Bach','Haydn']},
      {q:'Melyik zenekar volt a Britpop korszak egyik ikonja?', a:['Oasis','The Rolling Stones','The Beatles','Led Zeppelin']},
      {q:'Ki énekli a "Bad Guy"-t?', a:['Billie Eilish','Ariana Grande','Dua Lipa','Olivia Rodrigo']},
      {q:'Melyik évben oszlott fel a Beatles?', a:['1970','1968','1972','1975']},
      {q:'Ki a "Stairway to Heaven" előadója?', a:['Led Zeppelin','Black Sabbath','Deep Purple','Aerosmith']},
      {q:'Melyik ország nyerte az Eurovíziót 2023-ban?', a:['Svédország','Finnország','Ukrajna','Norvégia']},
      {q:'Ki énekelte a "Rolling in the Deep"-et?', a:['Adele','Amy Winehouse','Duffy','Paloma Faith']},
      {q:'Hány húr van egy klasszikus gitáron?', a:['6','4','7','5']},
      {q:'Melyik zenekar énekelte a "Wonderwall"-t?', a:['Oasis','Blur','Pulp','Radiohead']},
      {q:'Ki "Lady Gaga" polgári neve?', a:['Stefani Germanotta','Stefani Martinez','Ashley Smith','Jennifer Brown']},
      {q:'Melyik műfaj a reggae?', a:['Jamaikai zene','Brazíliai zene','Kubai zene','Trinidadi zene']},
      {q:'Ki írta a "4 Minutes"-t Madonna-val?', a:['Justin Timberlake','Pharrell Williams','Timbaland','Kanye West']},
    ]},
    film: { label:'Film & TV 🎬', qs:[
      {q:'Melyik film nyerte az Oscar-díjat 2020-ban (legjobb film)?', a:['Parasite','1917','Joker','Ford v Ferrari']},
      {q:'Ki játssza Tony Starkot (Iron Man)?', a:['Robert Downey Jr.','Chris Evans','Chris Hemsworth','Mark Ruffalo']},
      {q:'Melyik filmben van a "Hakuna Matata" dal?', a:['Az oroszlánkirály','Dzsungel könyve','Aladdin','A szépség és a szörnyeteg']},
      {q:'Ki rendezte az Inception-t?', a:['Christopher Nolan','Steven Spielberg','James Cameron','Ridley Scott']},
      {q:'Melyik sorozatban van a "Winter is Coming" mondat?', a:['Trónok Harca','The Witcher','Gyűrűk Ura','House of the Dragon']},
      {q:'Ki játssza Hermione Granger-t a Harry Potterben?', a:['Emma Watson','Emma Stone','Keira Knightley','Natalie Portman']},
      {q:'Melyik évben jelent meg az Avatar (James Cameron)?', a:['2009','2007','2011','2005']},
      {q:'Ki a főszereplő a John Wick filmekben?', a:['Keanu Reeves','Tom Cruise','Dwayne Johnson','Ryan Reynolds']},
      {q:'Melyik filmben mondják: "I\'ll be back"?', a:['Terminator','Die Hard','RoboCop','Total Recall']},
      {q:'Melyik streaming platformon van a Stranger Things?', a:['Netflix','HBO','Disney+','Amazon Prime']},
      {q:'Ki rendezte a Titanic-ot?', a:['James Cameron','Ridley Scott','Michael Bay','Peter Jackson']},
      {q:'Melyik filmben van Jack Sparrow?', a:['A Karib-tenger kalózai','Asterix','Patkányok Királyai','Treasure Island']},
      {q:'Hány részes a "Gyűrűk Ura" filmtrilógia?', a:['3','2','4','5']},
      {q:'Ki játssza James Bondot a Casino Royale-ban (2006)?', a:['Daniel Craig','Pierce Brosnan','Roger Moore','Timothy Dalton']},
      {q:'Melyik filmben van a "You shall not pass!" mondat?', a:['Gyűrűk Ura','Harry Potter','Narnia','Eragon']},
      {q:'Melyik sorozatban van Walter White?', a:['Breaking Bad','Ozark','Dexter','The Wire']},
      {q:'Ki hangja Simba-nak az oroszlánkirályban (eredeti)?', a:['Matthew Broderick','Tom Hanks','Will Smith','Eddie Murphy']},
      {q:'Melyik Marvel film a legtöbbet kereső?', a:['Avengers: Endgame','Avatar','Titanic','Star Wars']},
      {q:'Melyik évben jelent meg a Jurassic Park?', a:['1993','1990','1995','1997']},
      {q:'Ki rendezte a Schindler listáját?', a:['Steven Spielberg','Martin Scorsese','Francis Ford Coppola','Clint Eastwood']},
    ]},
    foldrajz: { label:'Földrajz 🌍', qs:[
      {q:'Mi Ausztrália fővárosa?', a:['Canberra','Sydney','Melbourne','Brisbane']},
      {q:'Melyik a világ legnagyobb országa területileg?', a:['Oroszország','Kanada','Kína','USA']},
      {q:'Melyik folyón van Budapest?', a:['Duna','Tisza','Rába','Dráva']},
      {q:'Mi Japán fővárosa?', a:['Tokió','Oszaka','Kioto','Hiroshima']},
      {q:'Melyik az Afrika leghosszabb folyója?', a:['Nílus','Kongó','Niger','Zambézi']},
      {q:'Melyik ország fővárosa Ottawa?', a:['Kanada','Ausztrália','Új-Zéland','Írország']},
      {q:'Melyik hegységben van a Mount Everest?', a:['Himalája','Andok','Alpok','Rocky Mountains']},
      {q:'Melyik tengerbe ömlik a Duna?', a:['Fekete-tenger','Adriai-tenger','Égei-tenger','Káspi-tenger']},
      {q:'Mi Brazília fővárosa?', a:['Brazíliaváros','São Paulo','Rio de Janeiro','Salvador']},
      {q:'Melyik a világ legnépesebb országa?', a:['India','Kína','USA','Indonézia']},
      {q:'Melyik ország fővárosa Reykjavik?', a:['Izland','Norvégia','Svédország','Finnország']},
      {q:'Hány kontinens van?', a:['7','6','5','8']},
      {q:'Melyik városban van a Szabad-szobor?', a:['New York','Washington','Los Angeles','Chicago']},
      {q:'Melyik folyó a világ legbővizűbbje?', a:['Amazonas','Nílus','Jangce','Mississippi']},
      {q:'Mi Egyiptom fővárosa?', a:['Kairó','Alexandria','Luxor','Asszuán']},
      {q:'Melyik ország fővárosa Wellington?', a:['Új-Zéland','Ausztrália','Kanada','Dél-Afrika']},
      {q:'Melyik tenger a világ legsósabb tengere?', a:['Holt-tenger','Káspi-tenger','Vörös-tenger','Perzsa-öböl']},
      {q:'Melyik ország fővárosa Buenos Aires?', a:['Argentína','Chile','Uruguay','Peru']},
      {q:'Melyik hegységben vannak az Alpok?', a:['Európában','Ázsiában','Afrikában','Amerikában']},
      {q:'Mi Magyarország területe km²-ben?', a:['~93 000 km²','~50 000 km²','~120 000 km²','~70 000 km²']},
    ]},
    magyar: { label:'Magyar 🇭🇺', qs:[
      {q:'Ki volt Magyarország első királya?', a:['I. István','I. László','II. András','Mátyás király']},
      {q:'Melyik évben volt a magyar forradalom és szabadságharc?', a:['1848','1956','1919','1867']},
      {q:'Mi a magyar himnusz első sora?', a:['Isten áldd meg a magyart','Fel, fel vitézek a csatára','Hazádnak rendületlenül','Szép Magyarország']},
      {q:'Ki írta az Egri csillagokat?', a:['Gárdonyi Géza','Jókai Mór','Petőfi Sándor','Arany János']},
      {q:'Hány megye van Magyarországon?', a:['19','20','17','22']},
      {q:'Melyik évben csatlakozott Magyarország az EU-hoz?', a:['2004','2007','2002','1999']},
      {q:'Mi a Balaton területe km²-ben?', a:['~600 km²','~400 km²','~800 km²','~1000 km²']},
      {q:'Ki volt "Csongor és Tünde" írója?', a:['Vörösmarty Mihály','Arany János','Petőfi Sándor','Ady Endre']},
      {q:'Melyik évben volt a magyar kiegyezés?', a:['1867','1848','1920','1944']},
      {q:'Mi a rubik-kocka feltalálójának neve?', a:['Rubik Ernő','Puskás Ferenc','Neumann János','Teller Ede']},
      {q:'Melyik folyó alkotja Magyarország keleti határát?', a:['Tisza... valójában Nyírség határ','Duna','Dráva','Rába']},
      {q:'Ki volt az 1956-os forradalom miniszterelnöke?', a:['Nagy Imre','Kádár János','Rákosi Mátyás','Horthy Miklós']},
      {q:'Melyik évben rendeztek olimpiát Magyarországon?', a:['Nem rendeztek','1936','1948','1964']},
      {q:'Ki volt Petőfi Sándor felesége?', a:['Szendrey Júlia','Vörösmarty Mihályné','Arany Jánosné','Erzsébet királyné']},
      {q:'Melyik városban van a Hősök tere?', a:['Budapest','Debrecen','Pécs','Miskolc']},
      {q:'Mi a pálinka alapanyaga?', a:['Gyümölcs','Gabona','Krumpli','Cukor']},
      {q:'Melyik évben alapították Pécset?', a:['Ősidőkben, I. sz. 1-2. sz körül','1000-ben','500-ban','1300-ban']},
      {q:'Ki komponálta a Kodály-módszert?', a:['Kodály Zoltán','Bartók Béla','Liszt Ferenc','Erkel Ferenc']},
      {q:'Melyik város a "Magyar tenger" partján van?', a:['Siófok','Pécs','Győr','Eger']},
      {q:'Mi a Trianoni békeszerződés éve?', a:['1920','1918','1919','1921']},
    ]},
  };

  const enabledCats = React.useMemo(() => {
    const cfg = gameMeta?.quizConfig?.cats;
    if (cfg && cfg.length > 0) return cfg;
    return Object.keys(QUIZ_DB);
  }, [gameMeta]);

  const allQs = React.useMemo(() => {
    const qs = [];
    enabledCats.forEach(k => { if (QUIZ_DB[k]) QUIZ_DB[k].qs.forEach(q => qs.push({...q, cat: QUIZ_DB[k].label})); });
    return qs.sort(() => Math.random() - 0.5);
  }, [gameIdx]);

  const [qIdx, setQIdx] = React.useState(0);
  const [phase, setPhase] = React.useState('question'); // question | result | bank | distribute | done
  const [streak, setStreak] = React.useState(0); // how many correct in a row this turn
  const [shuffled, setShuffled] = React.useState([]);
  const [chosen, setChosen] = React.useState(null); // index of chosen answer
  const [correct, setCorrect] = React.useState(false);
  const [distributeTarget, setDistributeTarget] = React.useState(null);

  const currentQ = allQs[qIdx % allQs.length];

  React.useEffect(() => {
    if (onSetHideFooter) onSetHideFooter(true);
    return () => { if (onSetHideFooter) onSetHideFooter(false); };
  }, []);

  React.useEffect(() => {
    if (!currentQ) return;
    const opts = [...currentQ.a].sort(() => Math.random() - 0.5);
    setShuffled(opts);
    setChosen(null); setCorrect(false); setPhase('question');
  }, [qIdx, gameIdx]);

  React.useEffect(() => { setStreak(0); setQIdx(0); }, [gameIdx]);

  const pName = challenger?.name || 'Játékos';
  const pColor = challenger?.color || T.mint;
  const kortyok = streak; // akkumulált kortyok (= streak - ha már 1+ helyes van)

  const answerQ = (opt) => {
    if (phase !== 'question') return;
    const isCorrect = opt === currentQ.a[0];
    setChosen(opt); setCorrect(isCorrect);
    setPhase('result');
    setTimeout(() => {
      if (isCorrect) {
        setStreak(s => s + 1);
        setPhase('bank');
      } else {
        setPhase('done');
        const drinks = streak + 1;
        if (onAdvance) onAdvance({[challenger?.id]: drinks});
      }
    }, 1000);
  };

  const bankIt = () => {
    // Pont + kortyok szétosztása
    if (onResult) onResult({correct: true});
    if (kortyok > 0) { setPhase('distribute'); }
    else { setPhase('done'); }
  };

  const pushLuck = () => {
    setQIdx(i => i + 1);
  };

  const distribute = (pid) => {
    if (onAdvance) onAdvance({[pid]: kortyok});
    setDistributeTarget(pid);
    setPhase('done');
  };

  // ── Kérdés UI ──
  if (phase === 'question' || phase === 'result') {
    return (
      <div style={{display:'flex',flexDirection:'column',gap:14}}>
        {/* Fejléc */}
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
          <div style={{display:'inline-flex',alignItems:'center',gap:8,padding:'5px 14px',background:pColor+'22',borderRadius:999}}>
            <div style={{width:8,height:8,borderRadius:'50%',background:pColor}} />
            <span style={{fontFamily:T.font,fontWeight:800,fontSize:14,color:T.ink}}>{pName}</span>
          </div>
          <div style={{display:'flex',gap:6,alignItems:'center'}}>
            {streak > 0 && <div style={{padding:'4px 10px',background:T.mint+'22',borderRadius:999,fontFamily:T.font,fontWeight:700,fontSize:12,color:T.mint}}>🔥 {streak} helyes</div>}
            <div style={{fontFamily:T.font,fontSize:11,color:T.inkSoft}}>{currentQ?.cat}</div>
          </div>
        </div>

        {/* Kérdés kártya */}
        <div style={{background:T.surface,borderRadius:20,padding:'20px 18px',boxShadow:T.shadow}}>
          <div style={{fontFamily:T.font,fontWeight:800,fontSize:17,color:T.ink,lineHeight:1.4,textAlign:'center'}}>
            {currentQ?.q}
          </div>
        </div>

        {/* Tét mutató */}
        {streak > 0 && (
          <div style={{display:'flex',gap:8}}>
            <div style={{flex:1,padding:'8px 12px',background:T.mint+'15',borderRadius:12,textAlign:'center',fontFamily:T.font,fontSize:12,color:T.mint,fontWeight:700}}>
              ✓ Bankol: +1 pont, {streak} korty osztani
            </div>
            <div style={{flex:1,padding:'8px 12px',background:T.coral+'15',borderRadius:12,textAlign:'center',fontFamily:T.font,fontSize:12,color:T.coral,fontWeight:700}}>
              ✗ Hibázik: {streak+1} korty iszik
            </div>
          </div>
        )}

        {/* Válaszok */}
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10}}>
          {shuffled.map((opt,i) => {
            const isChosen = chosen === opt;
            const isCorrectOpt = opt === currentQ?.a[0];
            let bg = T.surface, border = T.inkMute+'28', color = T.ink;
            if (phase === 'result' && isChosen && correct) { bg=T.mint+'22'; border=T.mint; color=T.mint; }
            if (phase === 'result' && isChosen && !correct) { bg=T.coral+'22'; border=T.coral; color=T.coral; }
            if (phase === 'result' && !isChosen && isCorrectOpt) { bg=T.mint+'15'; border=T.mint+'88'; color=T.mint; }
            return (
              <button key={i} onClick={()=>answerQ(opt)} disabled={phase==='result'} style={{
                padding:'14px 10px', borderRadius:14, border:'2px solid '+border,
                background:bg, color:color, fontFamily:T.font, fontWeight:700, fontSize:14,
                cursor: phase==='result'?'default':'pointer', transition:'all .15s', textAlign:'center',
                boxShadow: phase==='question' ? T.shadow : 'none',
              }}>{opt}</button>
            );
          })}
        </div>
      </div>
    );
  }

  // ── Bank / Push luck döntés ──
  if (phase === 'bank') {
    const nextDrinks = streak + 1;
    return (
      <div style={{display:'flex',flexDirection:'column',gap:14,alignItems:'center',textAlign:'center'}}>
        <div style={{fontSize:40,animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)'}}>✅</div>
        <div style={{fontFamily:T.font,fontWeight:900,fontSize:20,color:T.mint}}>Helyes!</div>
        <div style={{fontFamily:T.font,fontSize:14,color:T.inkSoft}}>Kategória: {currentQ?.cat}</div>

        {/* Döntés */}
        <div style={{width:'100%',display:'flex',flexDirection:'column',gap:10,marginTop:8}}>
          <button onClick={bankIt} style={{
            padding:'18px', borderRadius:16, border:'none', background:T.mint, color:'#fff',
            fontFamily:T.font, fontWeight:900, fontSize:16, cursor:'pointer',
            boxShadow:'0 5px 16px -5px '+T.mint+'88',
          }}>
            🏦 Pontot kérek{streak>1?' + '+kortyok+' kortyot osztok':''}
          </button>
          <button onClick={pushLuck} style={{
            padding:'16px', borderRadius:16, border:'2px solid '+T.coral+'44',
            background:T.coral+'12', color:T.coral,
            fontFamily:T.font, fontWeight:800, fontSize:15, cursor:'pointer',
          }}>
            🎲 Tovább megyek — {streak+1} kortyt oszthat vs. {nextDrinks} kortyt iszik
          </button>
        </div>

        <div style={{fontFamily:T.font,fontSize:12,color:T.inkMute,marginTop:4}}>
          Jelenlegi sorozat: {streak} helyes kérdés
        </div>
      </div>
    );
  }

  // ── Korty szétosztás ──
  if (phase === 'distribute') {
    const others = players.filter(p => p.id !== challenger?.id);
    return (
      <div style={{display:'flex',flexDirection:'column',gap:14}}>
        <div style={{textAlign:'center'}}>
          <div style={{fontSize:36}}>🍺</div>
          <div style={{fontFamily:T.font,fontWeight:900,fontSize:18,color:T.ink,marginTop:8}}>
            Kinek adod a {kortyok} kortyot?
          </div>
          <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft,marginTop:4}}>
            Választhatsz 1 játékost
          </div>
        </div>
        <div style={{display:'flex',flexDirection:'column',gap:8}}>
          {others.map(p => (
            <button key={p.id} onClick={()=>distribute(p.id)} style={{
              display:'flex', alignItems:'center', gap:12, padding:'14px 16px',
              borderRadius:16, border:'none', background:T.surface, cursor:'pointer',
              boxShadow:T.shadow, fontFamily:T.font, fontWeight:700, fontSize:15, color:T.ink,
            }}>
              <div style={{width:36,height:36,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:15,color:'#fff',flexShrink:0}}>
                {(p.name||'?').charAt(0).toUpperCase()}
              </div>
              {p.name}
              <div style={{marginLeft:'auto',fontFamily:T.font,fontSize:13,color:T.coral,fontWeight:700}}>→ {kortyok} korty 🍺</div>
            </button>
          ))}
        </div>
      </div>
    );
  }

  // ── Done ──
  if (phase === 'done') {
    const failed = !correct && chosen !== null;
    const drinkCount = streak + 1;
    return (
      <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:16,padding:'20px 0',textAlign:'center',animation:'popIn .4s cubic-bezier(.2,.9,.3,1.2)'}}>
        <div style={{fontSize:48}}>{failed ? '😵' : '🏆'}</div>
        {failed ? (
          <>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:20,color:T.coral}}>Hibás válasz!</div>
            <div style={{padding:'12px 20px',background:T.coral+'18',borderRadius:14,border:'1.5px solid '+T.coral+'44',fontFamily:T.font,fontWeight:700,fontSize:16,color:T.coral}}>
              {pName} iszik {drinkCount} kortyot 🍺
            </div>
            <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft}}>
              Helyes válasz: <strong>{currentQ?.a[0]}</strong>
            </div>
          </>
        ) : (
          <>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:20,color:T.mint}}>{pName} bankolt!</div>
            <div style={{padding:'12px 20px',background:T.mint+'18',borderRadius:14,border:'1.5px solid '+T.mint+'44',fontFamily:T.font,fontWeight:700,fontSize:16,color:T.mint}}>
              +1 pont{distributeTarget ? ` · ${kortyok} korty → ${players.find(p=>p.id===distributeTarget)?.name}` : ''}
            </div>
          </>
        )}
        <div style={{fontFamily:T.font,fontSize:12,color:T.inkMute,marginTop:4}}>
          Sorozat: {streak} helyes kérdés
        </div>
      </div>
    );
  }

  return null;
}

"""

# Beillesztés a PlayScreen function elé (CardBattleGame + QuizGame)
card_battle_component = """
function CardBattleGame({ gameIdx, challenger, opponent, onAdvance, onResult, onSetHideFooter }) {
  const VALS = [3,4,5,6,7]; // összesen 25
  const NR = 5;

  const fresh = () => ({
    phase: 'p1_plan', // p1_plan | handoff | p2_plan | reveal | done
    p1Plan: Array.from({length:NR},()=>[]),
    p2Plan: Array.from({length:NR},()=>[]),
    p1Hand: [...VALS],
    p2Hand: [...VALS],
    sel: null,
    rev: 0,
  });

  const [S, setS] = React.useState(fresh);
  React.useEffect(() => { setS(fresh()); }, [gameIdx]);
  React.useEffect(() => {
    if (onSetHideFooter) onSetHideFooter(true);
    return () => { if (onSetHideFooter) onSetHideFooter(false); };
  }, []);

  const isP1 = S.phase === 'p1_plan';
  const hand = isP1 ? S.p1Hand : S.p2Hand;
  const plan = isP1 ? S.p1Plan : S.p2Plan;
  const hk = isP1 ? 'p1Hand' : 'p2Hand';
  const pk = isP1 ? 'p1Plan' : 'p2Plan';
  const curPlayer = isP1 ? challenger : opponent;
  const pName = curPlayer?.name || (isP1 ? '1. játékos' : '2. játékos');
  const pColor = curPlayer?.color || (isP1 ? T.mint : T.coral);

  const assign = (ri) => {
    if (S.sel === null) return;
    const v = hand[S.sel];
    setS(s => ({...s, [hk]: s[hk].filter((_,i)=>i!==s.sel), [pk]: s[pk].map((r,i)=>i===ri?[...r,v]:r), sel:null}));
  };

  const remove = (ri, ci) => {
    const v = plan[ri][ci];
    setS(s => ({...s, [hk]: [...s[hk],v].sort((a,b)=>a-b), [pk]: s[pk].map((r,i)=>i===ri?r.filter((_,j)=>j!==ci):r)}));
  };

  const allIn = hand.length === 0;

  const results = React.useMemo(() => {
    let pot=0, p1W=0, p2W=0;
    const rounds = S.p1Plan.map((p1c, i) => {
      const p1s = p1c.reduce((a,b)=>a+b,0);
      const p2s = (S.p2Plan[i]||[]).reduce((a,b)=>a+b,0);
      pot++;
      let w=null, gained=0;
      if (p1s>p2s) { w='p1'; gained=pot; p1W+=pot; pot=0; }
      else if (p2s>p1s) { w='p2'; gained=pot; p2W+=pot; pot=0; }
      return {p1s,p2s,w,gained,p1W,p2W,carry:pot};
    });
    return {rounds, p1W, p2W};
  }, [S.p1Plan, S.p2Plan]);

  React.useEffect(() => {
    if (S.phase !== 'done') return;
    const {p1W, p2W} = results;
    if (onResult) {
      if (p1W > p2W) onResult({correct: true});
      else if (p2W > p1W) onResult({correct: false});
    }
  }, [S.phase]);

  if (S.phase === 'p1_plan' || S.phase === 'p2_plan') {
    const totalLeft = hand.reduce((a,b)=>a+b,0);
    return (
      <div style={{display:'flex',flexDirection:'column',gap:10}}>
        <div style={{textAlign:'center',padding:'4px 0 6px'}}>
          <div style={{display:'inline-flex',alignItems:'center',gap:8,padding:'6px 18px',background:pColor+'22',borderRadius:999}}>
            <div style={{width:10,height:10,borderRadius:'50%',background:pColor,flexShrink:0}} />
            <span style={{fontFamily:T.font,fontWeight:800,fontSize:15,color:T.ink}}>{pName} tervez</span>
          </div>
          <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,marginTop:4}}>
            {totalLeft > 0 ? `Még ${totalLeft} pont kiosztható` : '✓ Minden lap kiosztva'}
          </div>
        </div>
        {plan.map((cards, ri) => (
          <div key={ri} onClick={() => assign(ri)} style={{
            display:'flex', alignItems:'center', gap:10, padding:'10px 14px',
            background: S.sel!==null ? pColor+'15' : T.surface,
            borderRadius:14, border: S.sel!==null ? '2px dashed '+pColor : '2px solid transparent',
            boxShadow: T.shadow, cursor: S.sel!==null ? 'pointer' : 'default',
            transition:'background .12s, border .12s', minHeight:52,
          }}>
            <div style={{fontFamily:T.font,fontWeight:700,fontSize:12,color:T.inkSoft,minWidth:48}}>{ri+1}. kör</div>
            <div style={{flex:1,display:'flex',flexWrap:'wrap',gap:6,alignItems:'center'}}>
              {cards.map((v,ci) => (
                <div key={ci} onClick={e=>{e.stopPropagation();remove(ri,ci);}} style={{
                  width:36,height:36,borderRadius:10,background:pColor,color:'#fff',
                  display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:16,
                  cursor:'pointer',boxShadow:'0 2px 6px '+pColor+'44',flexShrink:0,
                }}>{v}</div>
              ))}
              {cards.length===0 && <span style={{fontFamily:T.font,fontSize:12,color:T.inkMute}}>Koppints ide</span>}
            </div>
            <div style={{fontFamily:T.font,fontWeight:800,fontSize:14,color:cards.length?T.ink:T.inkMute,minWidth:24,textAlign:'right'}}>
              {cards.length ? cards.reduce((a,b)=>a+b,0) : ''}
            </div>
          </div>
        ))}
        <div style={{marginTop:6}}>
          <div style={{fontFamily:T.font,fontSize:11,fontWeight:700,color:T.inkMute,textTransform:'uppercase',letterSpacing:'0.1em',marginBottom:8}}>Kézben</div>
          <div style={{display:'flex',gap:10,flexWrap:'wrap'}}>
            {hand.map((v,i) => (
              <div key={i} onClick={() => setS(s=>({...s,sel:s.sel===i?null:i}))} style={{
                width:48,height:64,borderRadius:12,
                background: S.sel===i ? pColor : T.surface,
                color: S.sel===i ? '#fff' : T.ink,
                border: S.sel===i ? '2px solid '+pColor : '2px solid '+T.inkMute+'30',
                display:'flex',alignItems:'center',justifyContent:'center',
                fontFamily:T.font,fontWeight:900,fontSize:22,
                boxShadow: S.sel===i ? '0 4px 14px '+pColor+'55' : T.shadow,
                cursor:'pointer',transition:'all .15s',
                transform: S.sel===i ? 'translateY(-8px) scale(1.08)' : 'none',
              }}>{v}</div>
            ))}
            {allIn && <div style={{fontFamily:T.font,fontSize:13,fontWeight:700,color:T.mint,display:'flex',alignItems:'center'}}>✓ Minden lap kiosztva!</div>}
          </div>
        </div>
        {allIn && (
          <button onClick={() => setS(s=>({...s, phase: isP1?'handoff':'reveal', sel:null}))} style={{
            marginTop:8,padding:'15px',borderRadius:16,border:'none',
            background:pColor,color:'#fff',fontFamily:T.font,fontWeight:900,fontSize:17,
            cursor:'pointer',boxShadow:'0 5px 16px -5px '+pColor+'88',
          }}>Kész →</button>
        )}
      </div>
    );
  }

  if (S.phase === 'handoff') {
    const p2Name = opponent?.name || '2. játékos';
    const p2Color = opponent?.color || T.coral;
    return (
      <div style={{display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',gap:20,padding:'32px 20px',minHeight:300,textAlign:'center'}}>
        <div style={{fontSize:52}}>🔄</div>
        <div style={{fontFamily:T.font,fontWeight:900,fontSize:22,color:T.ink}}>Add át a telefont!</div>
        <div style={{fontFamily:T.font,fontSize:15,color:T.inkSoft,maxWidth:260,lineHeight:1.6}}>
          <span style={{fontWeight:800,color:p2Color}}>{p2Name}</span> most tervezi meg a lapjait.<br/>
          <span style={{color:challenger?.color||T.mint,fontWeight:700}}>{challenger?.name||'1. játékos'}</span> ne nézze!
        </div>
        <button onClick={() => setS(s=>({...s,phase:'p2_plan'}))} style={{
          padding:'15px 40px',borderRadius:16,border:'none',
          background:p2Color,color:'#fff',fontFamily:T.font,fontWeight:900,fontSize:16,
          cursor:'pointer',boxShadow:'0 5px 16px -5px '+p2Color+'88',
        }}>{p2Name} készen áll →</button>
      </div>
    );
  }

  if (S.phase === 'reveal') {
    const {rounds} = results;
    const p1Name = challenger?.name || '1. játékos';
    const p2Name = opponent?.name || '2. játékos';
    const p1Color = challenger?.color || T.mint;
    const p2Color = opponent?.color || T.coral;
    const cur = rounds[S.rev] || rounds[rounds.length-1];
    return (
      <div style={{display:'flex',flexDirection:'column',gap:12}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'center',gap:28,padding:'4px 0 8px'}}>
          <div style={{textAlign:'center'}}>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:30,color:p1Color,fontVariantNumeric:'tabular-nums'}}>{cur.p1W}</div>
            <div style={{fontFamily:T.font,fontSize:11,color:T.inkSoft}}>{p1Name}</div>
          </div>
          <div style={{fontFamily:T.font,fontSize:16,color:T.inkMute,fontWeight:700}}>KÖR</div>
          <div style={{textAlign:'center'}}>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:30,color:p2Color,fontVariantNumeric:'tabular-nums'}}>{cur.p2W}</div>
            <div style={{fontFamily:T.font,fontSize:11,color:T.inkSoft}}>{p2Name}</div>
          </div>
        </div>
        <div style={{display:'flex',flexDirection:'column',gap:8}}>
          {rounds.slice(0,S.rev+1).map((r,i) => {
            const win1=r.w==='p1', win2=r.w==='p2', tie=!r.w;
            return (
              <div key={i} style={{
                display:'flex',alignItems:'center',gap:8,padding:'10px 12px',
                background: win1?p1Color+'18':win2?p2Color+'18':T.surfaceMuted,
                borderRadius:14, border:'1.5px solid '+(win1?p1Color+'44':win2?p2Color+'44':T.inkMute+'20'),
                animation: i===S.rev ? 'popIn .35s cubic-bezier(.2,.9,.3,1.2)' : 'none',
              }}>
                <div style={{fontFamily:T.font,fontWeight:700,fontSize:11,color:T.inkSoft,minWidth:38}}>{i+1}. kör</div>
                <div style={{flex:1,display:'flex',alignItems:'center',gap:4,flexWrap:'wrap'}}>
                  {(S.p1Plan[i]||[]).map((v,j)=>(
                    <span key={j} style={{padding:'2px 7px',background:p1Color,color:'#fff',borderRadius:7,fontFamily:T.font,fontWeight:800,fontSize:13}}>{v}</span>
                  ))}
                  <span style={{fontFamily:T.font,fontSize:11,color:p1Color,fontWeight:700}}>({r.p1s})</span>
                </div>
                <div style={{fontSize:18,flexShrink:0}}>{win1?'🏆':win2?'🏆':tie&&r.carry>1?'🎯':'🤝'}</div>
                <div style={{flex:1,display:'flex',alignItems:'center',justifyContent:'flex-end',gap:4,flexWrap:'wrap-reverse'}}>
                  <span style={{fontFamily:T.font,fontSize:11,color:p2Color,fontWeight:700}}>({r.p2s})</span>
                  {(S.p2Plan[i]||[]).map((v,j)=>(
                    <span key={j} style={{padding:'2px 7px',background:p2Color,color:'#fff',borderRadius:7,fontFamily:T.font,fontWeight:800,fontSize:13}}>{v}</span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
        {cur.carry > 0 && !cur.w && S.rev < NR-1 && (
          <div style={{textAlign:'center',fontFamily:T.font,fontSize:13,color:T.inkSoft,padding:'2px 0'}}>
            🎯 Döntetlen — {cur.carry} kör tétje vándorol tovább
          </div>
        )}
        {S.rev < NR-1 ? (
          <button onClick={()=>setS(s=>({...s,rev:s.rev+1}))} style={{
            padding:'14px',borderRadius:16,border:'none',background:T.surface,color:T.ink,
            fontFamily:T.font,fontWeight:800,fontSize:15,cursor:'pointer',boxShadow:T.shadow,marginTop:4,
          }}>Következő kör →</button>
        ) : (
          <button onClick={()=>setS(s=>({...s,phase:'done'}))} style={{
            padding:'14px',borderRadius:16,border:'none',background:T.mint,color:'#fff',
            fontFamily:T.font,fontWeight:900,fontSize:15,cursor:'pointer',
            boxShadow:'0 4px 14px rgba(79,194,160,0.5)',marginTop:4,
          }}>Eredmény →</button>
        )}
      </div>
    );
  }

  if (S.phase === 'done') {
    const {p1W, p2W} = results;
    const p1Name = challenger?.name || '1. játékos';
    const p2Name = opponent?.name || '2. játékos';
    const p1Color = challenger?.color || T.mint;
    const p2Color = opponent?.color || T.coral;
    const winName = p1W>p2W ? p1Name : p2W>p1W ? p2Name : null;
    const winColor = p1W>p2W ? p1Color : p2W>p1W ? p2Color : T.inkSoft;
    return (
      <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:16,padding:'20px 0',textAlign:'center',animation:'popIn .4s cubic-bezier(.2,.9,.3,1.2)'}}>
        <div style={{fontSize:52}}>{winName?'🏆':'🤝'}</div>
        <div style={{fontFamily:T.font,fontWeight:900,fontSize:24,color:winColor}}>
          {winName ? winName+' nyerte!' : 'Döntetlen!'}
        </div>
        <div style={{display:'flex',gap:36,marginTop:4}}>
          <div style={{textAlign:'center'}}>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:36,color:p1Color}}>{p1W}</div>
            <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,marginTop:2}}>{p1Name}</div>
          </div>
          <div style={{fontFamily:T.font,fontSize:28,color:T.inkMute,display:'flex',alignItems:'center'}}>–</div>
          <div style={{textAlign:'center'}}>
            <div style={{fontFamily:T.font,fontWeight:900,fontSize:36,color:p2Color}}>{p2W}</div>
            <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,marginTop:2}}>{p2Name}</div>
          </div>
        </div>
        <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft,marginTop:4}}>
          {winName ? 'A vesztes iszik 🍺' : 'Mindenki iszik 🍻'}
        </div>
      </div>
    );
  }

  return null;
}
"""

old_gc_fn = "\nfunction PlayScreen("
assert old_gc_fn in html, "FAIL: PlayScreen fn"
html = html.replace(old_gc_fn, card_battle_component + quiz_component + "\nfunction PlayScreen(", 1)

html = html.replace("const APP_VERSION = 'v9.399';", "const APP_VERSION = 'v9.400';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.400 — Kvíz játék: Press Your Luck, 6 kategória, 120 kérdés")
