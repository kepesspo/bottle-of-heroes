# v10.426 — Imposztor: opcionális segítség az imposztornak (a szó kategóriája),
# a játék beállító lapján kapcsolható (gameMeta.imposztorConfig.hint).
f = 'app.src.html'; s = open(f, encoding='utf8').read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:90])
    s = s.replace(old, new)

HINTS = {
 'Gyümölcs':['Banán'], 'Trópusi termés':['Kókusz'], 'Zöldség':['Paradicsom'],
 'Sporthelyszín':['Focipálya','Sportcsarnok','Stadion','Teniszpálya'],
 'Háztartási gép':['Mosógép'], 'Háztartás':['Takarítás'],
 'Közlekedés':['Repülőgép','Autópálya','Kerékpárút','Légiforgalom','Megálló','Vasút','Kalauz','Fogaskerekű','Útlap'],
 'Jármű':['Mentőautó','Bicikli','Hajó','Hintó'],
 'Vendéglátóhely':['Pizzéria','Kávézó','Kínai étterem','Söröző','Palacsintázó','Vendégfogadó'],
 'Nyaralóhely':['Tengerpart','Plázsa','Strandbár','Strandfürdő','Tengerpart bár'],
 'Intézmény':['Könyvtár','Iskola','Postahivatal'], 'Hangszer':['Gitár'],
 'Afrikai állat':['Víziló','Elefánt'], 'Édesség':['Jégkrém','Mézeskalács','Fagylalt','Sütemény','Torta'],
 'Ünnep':['Karácsonyfa','Farsang','Tüzijáték'], 'Játék':['Labda','Labirintus','Trambulin','Ugróiskola'],
 'Növény':['Kaktusz','Almafa','Bambusz','Napraforgó'], 'Szabadidő':['Nyaralás','Utazás'],
 'Természeti jelenség':['Szivárvány','Hurrikán','Naplemente','Időjárás'],
 'Ruházat':['Cipőfűző','Kesztyű','Ruházkodás'],
 'Foglalkozás':['Tűzoltó','Borbély','Éjjeli őr','Kovács','Optikus','Tengerész','Udvarmester','Zoológus',
                'Asztronauta','Detektív','Fényképész','Kapitány','Katona','Kertész','Mentős','Mérnök','Mészáros',
                'Orvos','Pilóta','Postás','Rendőr','Szakács','Szerelő','Tanár','Vadőr','Bébiszitter'],
 'Otthon':['Akvárium','Kert','Fürdőszoba','Szőnyeg','Lépcső'],
 'Sport':['Asztalitenisz','Baseball','Birkózás','Foci','Golf','Hegymászás','Íjász','Jégkorong','Karate',
          'Kosárlabda','Lovagló','Pingpong','Strandfoci','Verseny','Focista'],
 'Szórakozás':['Bábszínház','Cirkusz','Kalandpark','Lunapark','Mozi','Körhinta','Óriáskerék','Zipline'],
 'Madár':['Bagoly','Vadkacsa','Varjú'], 'Arc':['Bajusz'], 'Autózás':['Benzinkút','Parkoló'],
 'Konyha':['Bögrék','Főzés','Recept','Sajtárda','Grillezés','Gasztronómia'],
 'Víz':['Búvár','Folyó','Fürdőzés','Mentőmellény','Óceán','Snorkeling','Úszómedence','Uszoda','Aquapark',
        'Csónakázó tó','Surf','Kikötő','Jachtklub'],
 'Tengeri állat':['Cápa','Delfin','Polip','Rák'], 'Gyerekek':['Csúszda','Gyerekjáték','Bölcsőde','Játszóház','Napközi'],
 'Buli':['Diszkó','Pizsamaparti','Fesztivál'], 'Szokás':['Dohányzás'],
 'Természet':['Dzsungel','Erdő','Vízesés','Vulkán','Puszta','Sivatag'],
 'Vásárlás':['Édességbolt','Szupermarket','Trafik','Régiséges bolt','Vásárcsarnok','Lemezbolt','Kézműves piac'],
 'Épület':['Felhőkarcoló','Palota','Kastély','Piramis','Pajta'], 'Egészség':['Fogorvos','Gyógyszer','Kórház','Trachoma'],
 'Állat':['Gorilla','Majom','Nyúl','Panda','Teknős','Tigris','Dínó','Medvebölcső','Lovasiskola'],
 'Munkahely':['Gyár','Nyomda','Bánya'], 'Ékszer':['Gyöngy'], 'Ital':['Gyümölcslé','Narancslé'],
 'Tárgy':['Hamutartó','Mágnes'], 'Hobbi':['Horgászat','Kézimunka','Kosárfonás','Origami'],
 'Utazás':['Hotelszoba','Safari','Repülőtér','Szálloda'], 'Mozgás':['Jógaóra'], 'Rovar':['Katicabogár'],
 'Szabadtér':['Kemping','Sátortábor','Tábortűz','Természetjárás','Vadkemping','Állatkert'], 'Anyag':['Márvány'],
 'Iskola':['Mértani forma','Oktatás'], 'Kultúra':['Múzeum','Operaház','Galéria','Múzeumkert'],
 'Energia':['Napelem','Erőmű'], 'Nyár':['Naptej'], 'Technika':['Programozás','Robot'],
 'Társasjáték':['Sakk'], 'Hideg':['Sarkvidék'], 'Film':['Sci-fi','Vígjáték'], 'Forgatás':['Filmstúdió'],
 'Város':['Sétálóutca','Szökőkút','Piactér','Urbánus kert'], 'Barkácsolás':['Szerszám'],
 'Erdő':['Vadászat'], 'Pékáru':['Zsemle'], 'Étel':['Pizza'], 'Rajzolás':['Zsírkréta'], 'Tánc':['Balerina'],
 'Mese':['Boszorkány'], 'Templom':['Harangozó'], 'Vadnyugat':['Kovboj'],
 'Cirkusz':['Zsonglőr','Bohóc'], 'Porond':['Cirkuszpor'], 'Növények':['Botanikus kert'], 'Zene':['Hangversenyterem'],
 'Tudomány':['Laborató','Obszervatórium'], 'Tél':['Hóember'],
}
words = {}
for h, ws in HINTS.items():
    for w in ws:
        assert w not in words, ('dupla', w)
        assert h.lower() not in w.lower() and w.lower() not in h.lower(), (h, w)
        words[w] = h
# minden szóhoz kell tipp — a bank forrásából ellenőrizve
import re
a = s.index('const IMPOSZTOR_SZAVAK = ['); b = s.index('];', a)
bank = set(re.findall(r"'([^']+)'", s[a:b]))
missing = bank - set(words); extra = set(words) - bank
assert not missing and not extra, (missing, extra)

lines = []
for h, ws in HINTS.items():
    lines.append('  ' + ', '.join("'%s':'%s'" % (w, h) for w in ws) + ',')
tbl = ("\n// Imposztor-segítség (v10.426): a szó KATEGÓRIÁJA — „picit közelebb\", de nem árulja el.\n"
       "// Minden IMPOSZTOR_SZAVAK szóhoz kell egy (az imposztor_hint_test őrzi). Új szónál ide is.\n"
       "const IMPOSZTOR_TIPPEK = {\n" + '\n'.join(lines) + "\n};\n")
rep("const IMPOSZTOR_SZAVAK_SHUFFLED = (() => {", tbl + "\nconst IMPOSZTOR_SZAVAK_SHUFFLED = (() => {")

# a játék: gameMeta prop, hint
rep("function ImposztorGame({ gameIdx, players, onAdvance, onResult, roomCode }) {\n  const online = !!roomCode;",
    "function ImposztorGame({ gameIdx, players, onAdvance, onResult, roomCode, gameMeta }) {\n  const online = !!roomCode;\n"
    "  // v10.426: Imposztor-segítség — ha be van kapcsolva, az imposztor a szó kategóriáját kapja\n"
    "  const hintOn = !!(gameMeta && gameMeta.imposztorConfig && gameMeta.imposztorConfig.hint);")
rep("  const word = IMPOSZTOR_SZAVAK_SHUFFLED[wordIdx];\n",
    "  const word = IMPOSZTOR_SZAVAK_SHUFFLED[wordIdx];\n  const impHint = hintOn ? (IMPOSZTOR_TIPPEK[word] || null) : null;\n")
rep("roles[p.id] = { imp, word: imp ? null : word }; });",
    "roles[p.id] = { imp, word: imp ? null : word, hint: imp ? impHint : null }; });")
rep("  }, [online, gameIdx, impostorIndices.join(',')]);",
    "  }, [online, gameIdx, impostorIndices.join(','), impHint]);")
rep("""                  <div style={{ fontFamily:T.font, fontWeight:800, fontSize:22, color:T.coral, letterSpacing:'0.05em' }}>IMPOSZTOR</div>
                </div>""",
"""                  <div style={{ fontFamily:T.font, fontWeight:800, fontSize:22, color:T.coral, letterSpacing:'0.05em' }}>IMPOSZTOR</div>
                  {impHint && <ImposztorHint hint={impHint} />}
                </div>""")
rep("""                <div style={{ fontFamily:T.font, fontSize:12.5, color:'rgba(255,255,255,0.6)' }}>Nem tudod a szót — blöffölj!</div>""",
"""                <div style={{ fontFamily:T.font, fontSize:12.5, color:'rgba(255,255,255,0.6)' }}>Nem tudod a szót — blöffölj!</div>
                {myRole.hint && <ImposztorHint hint={myRole.hint} />}""")
# közös tipp-csip (modul-szintű, host és telefon ugyanazt rajzolja)
rep("function ImposztorGame({ gameIdx,", """// Az imposztor tippje — a host körbeadós lapja ÉS a telefon ugyanezt rajzolja.
function ImposztorHint({ hint }) {
  return (
    <div data-imp-hint style={{ marginTop:10, display:'inline-flex', flexDirection:'column', alignItems:'center', gap:2, padding:'8px 14px', borderRadius:12, background:'rgba(255,255,255,0.10)', border:'1.5px dashed rgba(255,255,255,0.35)' }}>
      <span style={{ fontFamily:T.font, fontWeight:800, fontSize:10.5, letterSpacing:'0.1em', color:'rgba(255,255,255,0.55)' }}>💡 SEGÍTSÉG</span>
      <span style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:'#fff' }}>{hint}</span>
    </div>
  );
}

function ImposztorGame({ gameIdx,""")
rep("if (gameId === 'imposztor') return <ImposztorGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} roomCode={roomCode} />;",
    "if (gameId === 'imposztor') return <ImposztorGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} roomCode={roomCode} gameMeta={gameMeta} />;")

# beállító lap
rep("function RitmusConfigSheet({ config, setConfig, onClose }) {", """function ImposztorConfigSheet({ config, setConfig, onClose }) {
  return (
    <CfgSheet title="Imposztor beállítások" onClose={onClose}
      subtitle="Mindenki tudja a titkos szót — csak az imposztor nem. Tippeljetek, aztán szavazzatok.">
      <CfgRow label="Imposztor-segítség" hint="Az imposztor megkapja a szó kategóriáját (pl. Banán → Gyümölcs), így könnyebb blöffölni"
        options={[{ v:false, l:'Ki' }, { v:true, l:'Be' }]}
        value={!!config.hint} onPick={v => setConfig(c => ({ ...c, hint: v }))} />
    </CfgSheet>
  );
}

function RitmusConfigSheet({ config, setConfig, onClose }) {""")
rep("  quiz:       { metaKey:'quizConfig',       Comp: QuizConfigSheet },\n};",
    "  quiz:       { metaKey:'quizConfig',       Comp: QuizConfigSheet },\n  imposztor:  { metaKey:'imposztorConfig',  Comp: ImposztorConfigSheet },\n};")
rep("const APP_VERSION = 'v10.425';", "const APP_VERSION = 'v10.426';")
open(f, 'w', encoding='utf8').write(s)
print('ok', len(words))
