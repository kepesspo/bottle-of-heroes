with open('index.html', 'r', encoding='utf-8') as f:
    src = f.read()

import re

# ══════════════════════════════════════════════════════
# 1. Add more questions to each category
# ══════════════════════════════════════════════════════

OLD_ALTALANOS_END = "      {q:'Hány hete van egy évnek?', a:['52','48','54','50']},\n    ]},"
NEW_ALTALANOS_END = """      {q:'Hány hete van egy évnek?', a:['52','48','54','50']},
      {q:'Mi a fény sebessége (kb.)?', a:['300 000 km/s','150 000 km/s','500 000 km/s','1 000 000 km/s']},
      {q:'Hány elem van a periódusos rendszerben?', a:['118','100','92','128']},
      {q:'Melyik a világ legmélyebb tava?', a:['Bajkál-tó','Kaszpi-tenger','Nagy-tó','Titicaca-tó']},
      {q:'Hány szemű a normál kocka összes oldalán összesen?', a:['21','18','24','28']},
      {q:'Mi a DNS rövidítés teljes neve (magyarul)?', a:['Dezoxiribonukleinsav','Dinitrogén-sav','Diciklopentadiénsav','Didezoxiribózsav']},
      {q:'Melyik elem vegyjele H?', a:['Hidrogén','Higany','Hélium','Hafnium']},
      {q:'Hány perc van egy napban?', a:['1440','720','2400','1200']},
      {q:'Melyik ország zászlaján van juharlevél?', a:['Kanada','Írország','Svédország','Svájc']},
      {q:'Mi a Naprendszer legnagyobb bolygója?', a:['Jupiter','Szaturnusz','Uránusz','Neptunusz']},
      {q:'Melyik évben találták fel a nyomtatót (Gutenberg)?', a:['1450 körül','1350 körül','1550 körül','1250 körül']},
      {q:'Hány csont van egy felnőtt ember testében?', a:['206','180','220','240']},
      {q:'Mi a legkisebb bolygó a Naprendszerben?', a:['Merkúr','Mars','Vénusz','Plútó']},
      {q:'Melyik állat a leghosszabb élettartamú?', a:['Grönlandi cápa','Teknős','Elefánt','Bálna']},
      {q:'Hány ország van az Európai Unióban?', a:['27','25','30','28']},
    ]},"""

assert OLD_ALTALANOS_END in src
src = src.replace(OLD_ALTALANOS_END, NEW_ALTALANOS_END, 1)

OLD_SPORT_END = "      {q:'Melyik ország olimpiai zászlóján nincs szín?', a:['Japán... valójában egyik sem — Olimpia jelkép 5 színű','Dánia','Svájc','Kanada']},\n    ]},"
NEW_SPORT_END = """      {q:'Melyik ország olimpiai zászlóján nincs szín?', a:['Japán... valójában egyik sem — Olimpia jelkép 5 színű','Dánia','Svájc','Kanada']},
      {q:'Melyik focicsapat nyerte a legtöbb BL-t/Bajnokok Ligáját?', a:['Real Madrid','Barcelona','Bayern München','Liverpool']},
      {q:'Hány játékos van egy röplabda csapatban a pályán?', a:['6','5','7','4']},
      {q:'Ki az örökös rekorder az F1 győzelmekben?', a:['Lewis Hamilton','Michael Schumacher','Ayrton Senna','Sebastian Vettel']},
      {q:'Hány cm magas egy kosárlabdapalánk?', a:['305 cm','280 cm','320 cm','290 cm']},
      {q:'Melyik ország házigazdája a 2024-es nyári olimpiának?', a:['Franciaország','Spanyolország','Olaszország','Görögország']},
      {q:'Ki nyerte a 2024-es Wimbledont (férfi)?', a:['Carlos Alcaraz','Novak Djokovic','Jannik Sinner','Daniil Medvedev']},
      {q:'Hány méteres egy úszómedence olympiai méretű?', a:['50 m','25 m','100 m','75 m']},
      {q:'Melyik csapat nyerte a 2023-as NBA-döntőt?', a:['Denver Nuggets','Miami Heat','LA Lakers','Golden State Warriors']},
      {q:'Hány perc van egy jégkorong mérkőzésen?', a:['60','45','90','75']},
      {q:'Melyik sportban van a Thomas-kupa verseny?', a:['Tollaslabda','Asztalitenisz','Squash','Padel']},
      {q:'Ki a legtöbb gólú játékos a válogatott történetében?', a:['Cristiano Ronaldo','Lionel Messi','Ali Daei','Miroslav Klose']},
      {q:'Hány set nyerésével nyerik meg a Wimbledont (férfi)?', a:['3','2','4','5']},
      {q:'Melyik városban rendezték a 2020-as (2021-es) olimpiát?', a:['Tokió','Párizs','London','Rio de Janeiro']},
      {q:'Mi az asztalitenisz másik neve?', a:['Pingpong','Squash','Badminton','Padel']},
    ]},"""

assert OLD_SPORT_END in src
src = src.replace(OLD_SPORT_END, NEW_SPORT_END, 1)

OLD_ZENE_END = "      {q:'Ki írta a \"4 Minutes\"-t Madonna-val?', a:['Justin Timberlake','Pharrell Williams','Timbaland','Kanye West']},\n    ]},"
NEW_ZENE_END = """      {q:'Ki írta a \"4 Minutes\"-t Madonna-val?', a:['Justin Timberlake','Pharrell Williams','Timbaland','Kanye West']},
      {q:'Hány tagja volt az originalThe Beatles-nek?', a:['4','3','5','6']},
      {q:'Melyik Taylor Swift album a \"Shake It Off\"?', a:['1989','Red','Folklore','Fearless']},
      {q:'Ki komponálta a Varázsfuvola operát?', a:['Mozart','Bach','Händel','Verdi']},
      {q:'Melyik évben halt meg Freddie Mercury?', a:['1991','1994','1986','1997']},
      {q:'Melyik együttes énekli a \"Smells Like Teen Spirit\"-et?', a:['Nirvana','Pearl Jam','Soundgarden','Pixies']},
      {q:'Ki énekli a \"Rolling in the Deep\"-et?', a:['Adele','Amy Winehouse','Dua Lipa','Beyoncé']},
      {q:'Melyik hangszer a cselló?', a:['Vonós','Fúvós','Ütős','Pengetős']},
      {q:'Ki énekelte a \"Hotel California\"-t?', a:['Eagles','Fleetwood Mac','The Doors','Creedence Clearwater Revival']},
      {q:'Melyik zenekar volt a \"Yellow Submarine\"?', a:['The Beatles','The Rolling Stones','The Who','The Kinks']},
      {q:'Ki énekli az \"Uptown Funk\"-ot?', a:['Bruno Mars','Justin Timberlake','Pharrell Williams','Robin Thicke']},
      {q:'Melyik évben alakult a BTS?', a:['2013','2010','2015','2017']},
      {q:'Mi Eminem polgári neve?', a:['Marshall Mathers','Calvin Broadus','Shawn Carter','Aubrey Graham']},
      {q:'Hány oktávja van egy zongorának (kb.)?', a:['7','5','8','6']},
      {q:'Melyik zenekar a \"Money for Nothing\"?', a:['Dire Straits','Guns N Roses','Aerosmith','ZZ Top']},
    ]},"""

assert OLD_ZENE_END in src
src = src.replace(OLD_ZENE_END, NEW_ZENE_END, 1)

OLD_FILM_END = "      {q:'Ki rendezte a Schindler listáját?', a:['Steven Spielberg','Martin Scorsese','Francis Ford Coppola','Clint Eastwood']},\n    ]},"
NEW_FILM_END = """      {q:'Ki rendezte a Schindler listáját?', a:['Steven Spielberg','Martin Scorsese','Francis Ford Coppola','Clint Eastwood']},
      {q:'Melyik filmben van Forrest Gump?', a:['Forrest Gump (1994)','Cast Away','Philadelphia','The Green Mile']},
      {q:'Melyik sorozatban szerepel Don Draper?', a:['Mad Men','Suits','Breaking Bad','The Americans']},
      {q:'Ki játssza Aragornot a Gyűrűk Urában?', a:['Viggo Mortensen','Orlando Bloom','Elijah Wood','Ian McKellen']},
      {q:'Melyik évben jelent meg a Mátrix (Matrix)?', a:['1999','1997','2001','2003']},
      {q:'Melyik filmstúdió készíti a Marvel filmeket?', a:['Disney/Marvel Studios','Sony','Warner Bros','Universal']},
      {q:'Ki játssza Hermione Grangert a Harry Potter sorozatban?', a:['Emma Watson','Emma Roberts','Keira Knightley','Lily Collins']},
      {q:'Melyik sorozatban van Mike Ross jogász?', a:['Suits','Good Wife','Boston Legal','Ally McBeal']},
      {q:'Melyik filmben mondják a \"May the Force be with you\" mondatot?', a:['Star Wars','Avatar','Star Trek','Dűne']},
      {q:'Ki az első vasember (Iron Man film)?', a:['Robert Downey Jr.','Chris Evans','Mark Ruffalo','Jeremy Renner']},
      {q:'Melyik évben jelent meg a Szépség és a Szörnyeteg (rajzfilm)?', a:['1991','1989','1994','1987']},
      {q:'Melyik sorozatban van Jesse Pinkman?', a:['Breaking Bad','Better Call Saul','The Wire','Ozark']},
      {q:'Ki rendezte a Pulp Fictiont?', a:['Quentin Tarantino','Martin Scorsese','David Fincher','Joel Coen']},
      {q:'Melyik filmben van a \"I see dead people\" mondat?', a:['Hatodik érzék','Szellem','Közel a halálhoz','Rémálom az Elm utcában']},
      {q:'Melyik sorozat a longest-running animated show (USA)?', a:['The Simpsons','Family Guy','South Park','Futurama']},
    ]},"""

assert OLD_FILM_END in src
src = src.replace(OLD_FILM_END, NEW_FILM_END, 1)

OLD_FOLD_END = "      {q:'Mi Magyarország területe km²-ben?', a:['~93 000 km²','~50 000 km²','~120 000 km²','~70 000 km²']},\n    ]},"
NEW_FOLD_END = """      {q:'Mi Magyarország területe km²-ben?', a:['~93 000 km²','~50 000 km²','~120 000 km²','~70 000 km²']},
      {q:'Mi Norvégia fővárosa?', a:['Oslo','Bergen','Stavanger','Trondheim']},
      {q:'Melyik ország legnagyobb szigete Grönland?', a:['Dánia (autonóm)','Norvégia','Izland','Kanada']},
      {q:'Melyik tenger van Magyarország és Olaszország között?', a:['Adriai-tenger','Földközi-tenger','Tirréni-tenger','Jón-tenger']},
      {q:'Mi Dél-Korea fővárosa?', a:['Szöul','Puszan','Incseon','Davegu']},
      {q:'Melyik folyón van Párizs?', a:['Szajna','Loire','Rhône','Garonne']},
      {q:'Mi Mexikó fővárosa?', a:['Mexikóváros','Guadalajara','Monterrey','Tijuana']},
      {q:'Melyik ország fővárosa Nairobi?', a:['Kenya','Tanzánia','Uganda','Etiópia']},
      {q:'Melyik a világ legmagasabb vízesése?', a:['Angel-vízesés','Niagara','Victoria','Iguazú']},
      {q:'Mi Görögország fővárosa?', a:['Athén','Thesszaloniki','Héraklion','Patras']},
      {q:'Melyik óceán a legkisebb?', a:['Jeges-tenger','Indiai-óceán','Atlanti-óceán','Csendes-óceán']},
      {q:'Mi Svédország fővárosa?', a:['Stockholm','Göteborg','Malmö','Uppsala']},
      {q:'Melyik ország fővárosa Pretoria?', a:['Dél-Afrika','Zimbabwe','Zambia','Mozambik']},
      {q:'Mi Törökország legnagyobb városa?', a:['Isztambul','Ankara','Izmir','Bursa']},
      {q:'Melyik ország fővárosa Varsó?', a:['Lengyelország','Csehország','Ausztria','Románia']},
    ]},"""

assert OLD_FOLD_END in src
src = src.replace(OLD_FOLD_END, NEW_FOLD_END, 1)

OLD_MAG_END = "      {q:'Mi a Trianoni békeszerződés éve?', a:['1920','1918','1919','1921']},\n    ]},"
NEW_MAG_END = """      {q:'Mi a Trianoni békeszerződés éve?', a:['1920','1918','1919','1921']},
      {q:'Ki volt az 1956-os forradalom leverésekor Magyarország miniszterelnöke?', a:['Kádár János','Nagy Imre','Rákosi Mátyás','Hegedüs András']},
      {q:'Melyik évben csatlakozott Magyarország a NATO-hoz?', a:['1999','2004','1995','1991']},
      {q:'Ki volt az első demokratikusan választott magyar miniszterelnök 1990-ben?', a:['Antall József','Göncz Árpád','Orbán Viktor','Horn Gyula']},
      {q:'Melyik évben volt a millecentenárium (1100 éve a honfoglalásnak)?', a:['1996','1999','2000','1994']},
      {q:'Mi a neve a magyar parlament épületének stílusának?', a:['Neogótikus','Barokk','Szecessziós','Neoklasszicista']},
      {q:'Hány megye alkotja Budapestet?', a:['Nem megye, főváros','1','2','3']},
      {q:'Ki volt Mátyás király anyja?', a:['Szilágyi Erzsébet','Cillei Borbála','Beatrix királyné','Mária Terézia']},
      {q:'Melyik városban van a Pécsi székesegyház?', a:['Pécs','Eger','Esztergom','Győr']},
      {q:'Ki alkotta a Himnuszt (szöveg)?', a:['Kölcsey Ferenc','Vörösmarty Mihály','Petőfi Sándor','Arany János']},
      {q:'Melyik évben tartottak Magyarországon először szabad választást a kommunizmus után?', a:['1990','1989','1988','1991']},
      {q:'Mi a neve a Duna legszebb magyarországi részének?', a:['Dunakanyar','Dunántúl','Duna-Tisza köze','Dráva-szög']},
      {q:'Ki volt Ady Endre szerelme, akinek verseket írt?', a:['Léda (Brüll Adél)','Szendrey Júlia','Wesselényi Polixéna','Csinszkának hívták']},
      {q:'Melyik évben rendeztek Magyarországon World Aquatics Championships-t?', a:['2017','2010','2014','2019']},
      {q:'Mi az Esterházy kastély másik neve Fertődön?', a:['Magyar Versailles','Kis Schönbrunn','Arany kastély','Nádor kastély']},
    ]},"""

assert OLD_MAG_END in src
src = src.replace(OLD_MAG_END, NEW_MAG_END, 1)

print("Questions expanded OK")

# ══════════════════════════════════════════════════════
# 2. Remove player name header row + streak chips
# ══════════════════════════════════════════════════════

OLD_HEADER = """        {/* Fejléc sor: játékos + streak chips */}
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
          <div style={{display:'inline-flex',alignItems:'center',gap:8,padding:'5px 12px',background:pColor+'22',borderRadius:999}}>
            <div style={{width:8,height:8,borderRadius:'50%',background:pColor}}/>
            <span style={{fontFamily:T.font,fontWeight:800,fontSize:13,color:T.ink}}>{pName}</span>
          </div>
          {streak > 0 && (
            <div style={{display:'flex',alignItems:'center',gap:6}}>
              <div style={{padding:'4px 10px',background:T.mint+'22',borderRadius:999,fontFamily:T.font,fontWeight:700,fontSize:12,color:T.mint}}>🔥 {streak} helyes</div>
              <div style={{padding:'4px 10px',background:T.coral+'18',borderRadius:999,fontFamily:T.font,fontWeight:700,fontSize:12,color:T.coral}}>{streak+1} ✗</div>
            </div>
          )}
        </div>"""
assert OLD_HEADER in src
src = src.replace(OLD_HEADER, '', 1)
print("Header removed OK")

# ══════════════════════════════════════════════════════
# 3. Wrong answer: don't go to 'done', stay in 'result'
# ══════════════════════════════════════════════════════
OLD_WRONG = """    } else {
      setPhase('result');
      setTimeout(() => {
        setPhase('done');
        const drinks = streak + 1;
        if (onAdvance) onAdvance({[challenger?.id]: drinks});
        if (onResult) onResult({ correct: false, playerName: challenger?.name, drinks, subtitle: (challenger?.name||'Játékos') + ` iszik ${drinks} kortyt` });
      }, 1500);
    }"""
assert OLD_WRONG in src
NEW_WRONG = """    } else {
      setPhase('result');
      const drinks = streak + 1;
      setTimeout(() => {
        if (onAdvance) onAdvance({[challenger?.id]: drinks});
        if (onResult) onResult({ correct: false, playerName: challenger?.name, drinks, subtitle: (challenger?.name||'Játékos') + ` iszik ${drinks} kortyt` });
      }, 1500);
    }"""
src = src.replace(OLD_WRONG, NEW_WRONG, 1)
print("Wrong answer phase OK")

# ══════════════════════════════════════════════════════
# 4. bankIt: don't call onResult early, just go to distribute
# ══════════════════════════════════════════════════════
OLD_BANKIT = """  const bankIt = () => {
    if (onResult) onResult({ correct: true, playerName: challenger?.name, drinks: 0, subtitle: kortyok > 0 ? `+1 pont — ${kortyok} kortyt oszt ki!` : '+1 pont!' });
    if (kortyok > 0) {
      const initGifts = {};
      players.filter(p => p.id !== challenger?.id).forEach(p => { initGifts[p.id] = 0; });
      setGifts(initGifts);
      setPhase('distribute');
    } else { setPhase('done'); }
  };"""
assert OLD_BANKIT in src
NEW_BANKIT = """  const bankIt = () => {
    if (kortyok > 0) {
      const initGifts = {};
      players.filter(p => p.id !== challenger?.id).forEach(p => { initGifts[p.id] = 0; });
      setGifts(initGifts);
      setPhase('distribute');
    } else {
      if (onAdvance) onAdvance({});
      if (onResult) onResult({ correct: true, playerName: challenger?.name, drinks: 0, subtitle: '+1 pont!' });
      setPhase('done');
    }
  };"""
src = src.replace(OLD_BANKIT, NEW_BANKIT, 1)
print("bankIt OK")

# ══════════════════════════════════════════════════════
# 5. Remove auto-confirm useEffect (replaced by manual button)
# ══════════════════════════════════════════════════════
OLD_AUTOCONFIRM = """  // Auto-confirm distribute when all kortyok assigned (top-level — no conditional hooks)
  const _distributeTotal = Object.values(gifts).reduce((s,v)=>s+v,0);
  const _distributeRemaining = kortyok - _distributeTotal;
  React.useEffect(() => {
    if (phase !== 'distribute') return;
    if (_distributeRemaining !== 0) return;
    const drinkMap = {};
    Object.entries(gifts).forEach(([pid,n]) => { if(n>0) drinkMap[pid]=n; });
    const t = setTimeout(() => {
      if (onAdvance) onAdvance(drinkMap);
      setPhase('done');
    }, 800);
    return () => clearTimeout(t);
  }, [phase, _distributeRemaining]);"""
assert OLD_AUTOCONFIRM in src
src = src.replace(OLD_AUTOCONFIRM, '', 1)
print("Auto-confirm removed OK")

# ══════════════════════════════════════════════════════
# 6. Rewrite distribute phase UI: manual confirm + skip + scroll
# ══════════════════════════════════════════════════════
OLD_DISTRIBUTE = """  if (phase === 'distribute') {
    const others = players.filter(p => p.id !== challenger?.id);
    const totalGifted = Object.values(gifts).reduce((s,v)=>s+v,0);
    const remaining = kortyok - totalGifted;
    const confirmGifts = () => {
      const drinkMap = {};
      Object.entries(gifts).forEach(([pid,n]) => { if(n>0) drinkMap[pid]=n; });
      if (onAdvance) onAdvance(drinkMap);
      setPhase('done');
    };
    // auto-confirm: moved to top-level useEffect
    return (
      <div style={{display:'flex',flexDirection:'column',gap:8,overflowY:'auto'}}>
        {/* Fejléc */}
        <div style={{background:T.surface,borderRadius:16,padding:'12px 16px',boxShadow:T.shadow,textAlign:'center'}}>
          <div style={{fontFamily:T.font,fontWeight:900,fontSize:22,color:pColor,lineHeight:1}}>🍺 {kortyok} korty</div>
          <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft,marginTop:3}}>{pName} kiosztja — kire?</div>
          {remaining > 0 && (
            <div style={{fontFamily:T.font,fontSize:12,fontWeight:700,color:T.inkSoft,marginTop:4}}>Még {remaining} korty kiosztható</div>
          )}
          {remaining === 0 && (
            <div style={{fontFamily:T.font,fontSize:12,fontWeight:700,color:T.mint,marginTop:4}}>✓ Minden kiosztva!</div>
          )}
        </div>
        {/* Játékos sorok +/- gombokkal */}
        <div style={{display:'flex',flexDirection:'column',gap:7}}>
          {others.map(p => {
            const given = gifts[p.id] || 0;
            return (
              <div key={p.id} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 12px',background:T.surface,borderRadius:14,boxShadow:T.shadow}}>
                <div style={{width:36,height:36,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:15,color:'#fff',flexShrink:0}}>
                  {(p.name||'?').charAt(0).toUpperCase()}
                </div>
                <div style={{flex:1,minWidth:0}}>
                  <div style={{fontFamily:T.font,fontWeight:700,fontSize:14,color:T.ink,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{p.name}</div>
                  {given > 0 && <div style={{fontFamily:T.font,fontSize:12,color:T.coral,fontWeight:700,marginTop:1}}>+{given} 🍺 kap</div>}
                </div>
                <div style={{display:'flex',alignItems:'center',gap:6,flexShrink:0}}>
                  <button onClick={()=>setGifts(g=>({...g,[p.id]:Math.max(0,(g[p.id]||0)-1)}))} disabled={given<=0}
                    style={{width:32,height:32,borderRadius:9,border:'none',background:given>0?T.coral+'22':T.bgSoft,color:given>0?T.coral:T.inkMute,fontFamily:T.font,fontSize:20,cursor:given>0?'pointer':'default',fontWeight:700,lineHeight:1}}>−</button>
                  <div style={{fontFamily:T.font,fontWeight:800,fontSize:16,color:given>0?T.coral:T.inkMute,minWidth:20,textAlign:'center'}}>{given}</div>
                  <button onClick={()=>{if(remaining>0)setGifts(g=>({...g,[p.id]:(g[p.id]||0)+1}));}} disabled={remaining<=0}
                    style={{width:32,height:32,borderRadius:9,border:'none',background:remaining>0?T.mint+'22':T.bgSoft,color:remaining>0?T.mint:T.inkMute,fontFamily:T.font,fontSize:20,cursor:remaining>0?'pointer':'default',fontWeight:700,lineHeight:1}}>+</button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }"""

assert OLD_DISTRIBUTE in src
NEW_DISTRIBUTE = """  if (phase === 'distribute') {
    const others = players.filter(p => p.id !== challenger?.id);
    const totalGifted = Object.values(gifts).reduce((s,v)=>s+v,0);
    const remaining = kortyok - totalGifted;
    const confirmGifts = () => {
      const drinkMap = {};
      Object.entries(gifts).forEach(([pid,n]) => { if(n>0) drinkMap[pid]=n; });
      if (onAdvance) onAdvance(drinkMap);
      const names = Object.entries(gifts).filter(([,n])=>n>0)
        .map(([pid,n]) => { const p=players.find(x=>x.id===pid); return `${p?.name||'?'} iszik ${n} kortyt`; });
      if (onResult) onResult({ correct: true, playerName: challenger?.name, drinks: 0,
        subtitle: names.length > 0 ? names.join(' · ') : `${pName} kiosztotta a kortyokat` });
      setPhase('done');
    };
    const skipGifts = () => {
      if (onAdvance) onAdvance({});
      if (onResult) onResult({ correct: true, playerName: challenger?.name, drinks: 0, subtitle: `${pName} bankolt — ${kortyok} korty!` });
      setPhase('done');
    };
    return (
      <div style={{display:'flex',flexDirection:'column',gap:8,maxHeight:'60vh',overflowY:'auto'}}>
        {/* Fejléc */}
        <div style={{background:T.surface,borderRadius:16,padding:'12px 16px',boxShadow:T.shadow,textAlign:'center',flexShrink:0}}>
          <div style={{fontFamily:T.font,fontWeight:900,fontSize:22,color:pColor,lineHeight:1}}>🍺 {kortyok} korty</div>
          <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft,marginTop:3}}>{pName} kiosztja — kire?</div>
          {remaining > 0 && (
            <div style={{fontFamily:T.font,fontSize:12,fontWeight:700,color:T.inkSoft,marginTop:4}}>Még {remaining} korty kiosztható</div>
          )}
          {remaining === 0 && (
            <div style={{fontFamily:T.font,fontSize:12,fontWeight:700,color:T.mint,marginTop:4}}>✓ Minden kiosztva!</div>
          )}
        </div>
        {/* Játékos sorok */}
        <div style={{display:'flex',flexDirection:'column',gap:7,overflowY:'auto'}}>
          {others.map(p => {
            const given = gifts[p.id] || 0;
            return (
              <div key={p.id} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 12px',background:T.surface,borderRadius:14,boxShadow:T.shadow,flexShrink:0}}>
                <div style={{width:36,height:36,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:15,color:'#fff',flexShrink:0}}>
                  {(p.name||'?').charAt(0).toUpperCase()}
                </div>
                <div style={{flex:1,minWidth:0}}>
                  <div style={{fontFamily:T.font,fontWeight:700,fontSize:14,color:T.ink,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{p.name}</div>
                  {given > 0 && <div style={{fontFamily:T.font,fontSize:12,color:T.coral,fontWeight:700,marginTop:1}}>+{given} 🍺 kap</div>}
                </div>
                <div style={{display:'flex',alignItems:'center',gap:6,flexShrink:0}}>
                  <button onClick={()=>setGifts(g=>({...g,[p.id]:Math.max(0,(g[p.id]||0)-1)}))} disabled={given<=0}
                    style={{width:32,height:32,borderRadius:9,border:'none',background:given>0?T.coral+'22':T.bgSoft,color:given>0?T.coral:T.inkMute,fontFamily:T.font,fontSize:20,cursor:given>0?'pointer':'default',fontWeight:700,lineHeight:1}}>−</button>
                  <div style={{fontFamily:T.font,fontWeight:800,fontSize:16,color:given>0?T.coral:T.inkMute,minWidth:20,textAlign:'center'}}>{given}</div>
                  <button onClick={()=>{if(remaining>0)setGifts(g=>({...g,[p.id]:(g[p.id]||0)+1}));}} disabled={remaining<=0}
                    style={{width:32,height:32,borderRadius:9,border:'none',background:remaining>0?T.mint+'22':T.bgSoft,color:remaining>0?T.mint:T.inkMute,fontFamily:T.font,fontSize:20,cursor:remaining>0?'pointer':'default',fontWeight:700,lineHeight:1}}>+</button>
                </div>
              </div>
            );
          })}
        </div>
        {/* Confirm + Skip gombok */}
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,flexShrink:0,paddingTop:4}}>
          <button onClick={skipGifts} style={{
            padding:'13px 8px',borderRadius:14,
            border:'2px solid '+T.inkMute+'33',background:T.bgSoft,color:T.inkSoft,
            fontFamily:T.font,fontWeight:800,fontSize:13,cursor:'pointer',
          }}>Kihagyom</button>
          <button onClick={confirmGifts} style={{
            padding:'13px 8px',borderRadius:14,border:'none',
            background: totalGifted > 0 ? T.mint : T.bgSoft,
            color: totalGifted > 0 ? '#fff' : T.inkMute,
            fontFamily:T.font,fontWeight:900,fontSize:13,cursor:'pointer',
            boxShadow: totalGifted > 0 ? '0 4px 14px -4px '+T.mint+'88' : 'none',
          }}>Mentés ✓</button>
        </div>
      </div>
    );
  }"""

src = src.replace(OLD_DISTRIBUTE, NEW_DISTRIBUTE, 1)
print("Distribute UI OK")

# ══════════════════════════════════════════════════════
# 7. Version bump
# ══════════════════════════════════════════════════════
m = re.search(r"APP_VERSION = 'v([\d.]+)'", src)
if m:
    parts = m.group(1).split('.')
    nv = f"{parts[0]}.{int(parts[1])+1}"
    src = src.replace(m.group(0), f"APP_VERSION = 'v{nv}'", 1)
    print(f"Version → v{nv}")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)

print('ALL OK')
