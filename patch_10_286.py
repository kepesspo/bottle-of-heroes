#!/usr/bin/env python3
# v10.286 — Szólánc: a lánc 12 szóig megy, és a végigvitt sor mindenkinek pontot ér
#
# HOL TARTOTT EDDIG
#   * a lanc 8 szonal ert veget (`chainPool` = ceil(15/2) a kevert listabol),
#   * es a vegigvitt lanc SEMMIT nem ert: a nyero ag `onAdvance({}, {})`-t hivott,
#     ures korty- ES ures pontmappel. Azert hivta meg egyaltalan, hogy a Kovi
#     gomb ne ragadjon be (v10.284) — jutalom nem tartozott hozza.
#
# MIERT KELLETT A SZOLISTAKAT BOVITENI
#   12 szavas lanchoz a 15 szavas listabol 3 csali maradna, es a `decoysFor`
#   minden szinten UGYANAZT a harmat adna vissza. Ket kor utan mindenki tudna,
#   hogy azt a harmat sosem kell nezni — a csali elveszitene az ertelmet.
#   Ezert minden lista 20 szora nott: 12 lanc + 8 csali. A `decoysFor` igy
#   nyolc kozul forog, es a rotacio (len*3+i) % 8 miatt szintenkent mas harmas jon.
#
# A HATAROK VISSZAALLNAK 2-4 / 5-7 / 8+ -RA
#   A v10.285-ben azert huztam ossze oket (2-3 / 4-6 / 7+), mert a lanc 8-nal
#   veget ert, es a felso fokozat egyetlen szintet fedett volna. 12 szonal ez
#   megszunik: a 8+ tier ot szintet fed (8..12), tehat a 3/3/5 osztas kiegyensulyozott.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Fokozatok: a hatarok visszaallnak, a tet marad 1/2/3
# ─────────────────────────────────────────────────────────────────────────────
sub("""// A `korty` mezo miatt EGY SZIN = EGY TET: a lap szine nem csak azt mondja,
// milyen hosszu a sor, hanem azt is, mennyibe kerul elrontani.
// A hatarok 2/3/2-re vannak osztva a het szint (2..8) kozott — a regi 2-4/5-7/8+
// 3/3/1 volt, tehat a felso fokozat egyetlen, szinte sosem elert szintet fedett.
const SZ_TONES = [
  { max: 3,        bg:'#C9E8D2', badge:'#4FA97F', korty: 1 },
  { max: 6,        bg:'#F5E0AC', badge:'#D69A2E', korty: 2 },
  { max: Infinity, bg:'#F2C4C4', badge:'#D46A6A', korty: 3 },
];""",
    """// A `korty` mezo miatt EGY SZIN = EGY TET: a lap szine nem csak azt mondja,
// milyen hosszu a sor, hanem azt is, mennyibe kerul elrontani.
// A tizenegy szint (2..12) felett a 3/3/5 osztas kiegyensulyozott. (A v10.285-ben
// azert volt szukebb, mert a lanc meg 8-nal veget ert, es a felso fokozat
// egyetlen szintet fedett volna.)
const SZ_TONES = [
  { max: 4,        bg:'#C9E8D2', badge:'#4FA97F', korty: 1 },
  { max: 7,        bg:'#F5E0AC', badge:'#D69A2E', korty: 2 },
  { max: Infinity, bg:'#F2C4C4', badge:'#D46A6A', korty: 3 },
];
// Ennyi szonal er veget a lanc. Aki idaig eljut, mindenkinek pontot hoz —
// szandekosan ritka, elerhetetlennek erzodo, de nem lehetetlen jackpot.
const SZ_MAX_LEN = 12;""",
    'fokozatok')

# ─────────────────────────────────────────────────────────────────────────────
# 2. Szolistak 20 szora — 12 lanc + 8 csali
# ─────────────────────────────────────────────────────────────────────────────
sub("""    { cat:'Gyümölcsök 🍎', words:['alma','körte','szilva','barack','szőlő','dinnye','eper','málna','cseresznye','banán','narancs','citrom','mangó','ananász','kivi'] },
    { cat:'Állatok 🐾',    words:['kutya','macska','ló','tehén','birka','nyúl','egér','róka','farkas','medve','oroszlán','tigris','elefánt','zsiráf','pingvin'] },
    { cat:'Fővárosok 🌍',  words:['Budapest','Berlin','Párizs','London','Róma','Madrid','Varsó','Prága','Bécs','Amszterdam','Bukarest','Athén','Lisszabon','Koppenhága','Stockholm'] },
    { cat:'Ételek 🍕',     words:['gulyás','pizza','hamburger','rántotta','palacsinta','rétes','lángos','fasírt','rakott krumpli','halászlé','töltött káposzta','kürtőskalács','lecsó','savanyúkáposzta','bruschetta'] },
    { cat:'Sportágak ⚽',  words:['foci','kosárlabda','tenisz','úszás','atlétika','birkózás','ökölvívás','vízilabda','röplabda','kézilabda','jégkorong','kerékpár','lovaglás','golf','evezés'] },
    { cat:'Autómárkák 🚗', words:['Toyota','BMW','Mercedes','Audi','Volkswagen','Ford','Opel','Renault','Peugeot','Fiat','Honda','Suzuki','Hyundai','Kia','Tesla'] },
    { cat:'Italok 🍹',     words:['víz','bor','sör','pálinka','kávé','tea','limonádé','cola','whisky','vodka','koktél','gyümölcslé','fröccs','rum','rosé'] },
    { cat:'Magyar városok 🏙️', words:['Pécs','Győr','Miskolc','Debrecen','Eger','Sopron','Veszprém','Kecskemét','Nyíregyháza','Szolnok','Kaposvár','Szombathely','Tatabánya','Érd','Zalaegerszeg'] },
    { cat:'Hangszerek 🎺', words:['zongora','gitár','hegedű','dob','furulya','trombita','szaxofon','bőgő','hárfa','fuvola','ukulele','mandolin','brácsa','cselló','klarinét'] },
    { cat:'Filmek 🎬',     words:['Titanic','Avatar','Inception','Matrix','Gladiátor','Interstellar','Joker','Avengers','Parasite','Tenet','Dune','Oppenheimer','Barbie','Top Gun','Ratatouille'] },""",
    """    { cat:'Gyümölcsök 🍎', words:['alma','körte','szilva','barack','szőlő','dinnye','eper','málna','cseresznye','banán','narancs','citrom','mangó','ananász','kivi','meggy','ribizli','füge','áfonya','datolya'] },
    { cat:'Állatok 🐾',    words:['kutya','macska','ló','tehén','birka','nyúl','egér','róka','farkas','medve','oroszlán','tigris','elefánt','zsiráf','pingvin','teknős','bagoly','mókus','delfin','sündisznó'] },
    { cat:'Fővárosok 🌍',  words:['Budapest','Berlin','Párizs','London','Róma','Madrid','Varsó','Prága','Bécs','Amszterdam','Bukarest','Athén','Lisszabon','Koppenhága','Stockholm','Oslo','Helsinki','Dublin','Pozsony','Zágráb'] },
    { cat:'Ételek 🍕',     words:['gulyás','pizza','hamburger','rántotta','palacsinta','rétes','lángos','fasírt','halászlé','lecsó','pörkölt','bableves','tiramisu','gofri','túrós csusza','kürtőskalács','csirkepaprikás','sült krumpli','rakott krumpli','somlói galuska'] },
    { cat:'Sportágak ⚽',  words:['foci','kosárlabda','tenisz','úszás','atlétika','birkózás','ökölvívás','vízilabda','röplabda','kézilabda','jégkorong','kerékpár','lovaglás','golf','evezés','vívás','torna','síelés','karate','asztalitenisz'] },
    { cat:'Autómárkák 🚗', words:['Toyota','BMW','Mercedes','Audi','Volkswagen','Ford','Opel','Renault','Peugeot','Fiat','Honda','Suzuki','Hyundai','Kia','Tesla','Volvo','Škoda','Mazda','Nissan','Porsche'] },
    { cat:'Italok 🍹',     words:['víz','bor','sör','pálinka','kávé','tea','limonádé','cola','whisky','vodka','koktél','gyümölcslé','fröccs','rum','rosé','pezsgő','tequila','gin','kakaó','szörp'] },
    { cat:'Magyar városok 🏙️', words:['Pécs','Győr','Miskolc','Debrecen','Eger','Sopron','Veszprém','Kecskemét','Nyíregyháza','Szolnok','Kaposvár','Szombathely','Tatabánya','Érd','Zalaegerszeg','Szeged','Békéscsaba','Esztergom','Salgótarján','Székesfehérvár'] },
    { cat:'Hangszerek 🎺', words:['zongora','gitár','hegedű','dob','furulya','trombita','szaxofon','bőgő','hárfa','fuvola','ukulele','mandolin','brácsa','cselló','klarinét','harmonika','citera','oboa','tuba','xilofon'] },
    { cat:'Filmek 🎬',     words:['Titanic','Avatar','Inception','Matrix','Gladiátor','Interstellar','Joker','Avengers','Parasite','Tenet','Dune','Oppenheimer','Barbie','Top Gun','Ratatouille','Rocky','Alien','Shrek','Terminátor','Vasember'] },""",
    'szolistak')

# ─────────────────────────────────────────────────────────────────────────────
# 3. A pakli kettevagasa mar nem felezes, hanem a 12-es lanchoz igazodik
# ─────────────────────────────────────────────────────────────────────────────
sub("""    const half = Math.ceil(a.length / 2);
    return { chainPool: a.slice(0, half), decoyPool: a.slice(half) };""",
    """    // A vagas NEM felezes: a lanc `SZ_MAX_LEN`-ig no, a maradek a csalie.
    // A `- 3` garantalja, hogy legalabb harom csali maradjon akkor is, ha egy
    // lista valaha rovidebb lenne 15 szonal.
    const hatar = Math.min(SZ_MAX_LEN, Math.max(2, a.length - 3));
    return { chainPool: a.slice(0, hatar), decoyPool: a.slice(hatar) };""",
    'pakli vagas')

# ─────────────────────────────────────────────────────────────────────────────
# 4. A vegigvitt lanc mindenkinek pontot er
# ─────────────────────────────────────────────────────────────────────────────
sub("""        setTimeout(() => {
          if (onAdvance) onAdvance({}, {});
          if (onResult) onResult({ correct: true, playerName: null, drinks: 0 });
          setDone({ failName: null, chain });
        }, 1200);""",
    """        setTimeout(() => {
          // A vegigvitt lanc MINDENKINEK pontot er. Eddig `onAdvance({}, {})` allt
          // itt: ures korty- ES ures pontmap — a hivas csak azert volt benne, hogy
          // a Kovi gomb ne ragadjon be (v10.284). Jutalom nem tartozott hozza,
          // tehat a jatek legnehezebb kimenetele semmit nem ert.
          const pm = {};
          players.forEach(p => { pm[p.id] = 1; });
          if (onAdvance) onAdvance({}, pm);
          if (onResult) onResult({ correct: true, winners: players, drinks: 0,
                                   winNote: '+1 pont mindenkinek' });
          setDone({ failName: null, chain });
        }, 1200);""",
    'nyeremeny')

sub("""            {win ? 'Végig megvolt a sor!' : done.failName + ' rontott'}
          </div>""",
    """            {win ? `Megvan mind a ${SZ_MAX_LEN}!` : done.failName + ' rontott'}
          </div>""",
    'nyero cim')

sub("""          {!win && players.length > 1 && (
            <div style={{ background:'rgba(255,255,255,0.24)', borderRadius:999, padding:'6px 15px',
                          fontFamily:T.font, fontWeight:800, fontSize:12.5, marginTop:7 }}>
              mindenki más +1 pont
            </div>
          )}""",
    """          {!win && players.length > 1 && (
            <div style={{ background:'rgba(255,255,255,0.24)', borderRadius:999, padding:'6px 15px',
                          fontFamily:T.font, fontWeight:800, fontSize:12.5, marginTop:7 }}>
              mindenki más +1 pont
            </div>
          )}
          {win && (
            <div style={{ background:'rgba(255,255,255,0.26)', borderRadius:999, padding:'10px 22px',
                          fontFamily:T.font, fontWeight:900, fontSize:15.5, marginTop:9 }}>
              mindenki +1 pont
            </div>
          )}""",
    'nyero pirula')

# ─────────────────────────────────────────────────────────────────────────────
# 5. A leiras is mondja el, hogy van jackpot
# ─────────────────────────────────────────────────────────────────────────────
sub("""desc:'Minden körben egy szóval több villog fel a képernyőn. Sorrendben vissza kell koppintani a szavakat. Aki elront, iszik — a többiek pontot kapnak.' }""",
    """desc:'Minden körben egy szóval több villog fel a képernyőn. Sorrendben vissza kell koppintani a szavakat. Aki elront, iszik — a többiek pontot kapnak. Ha a sor eléri a 12 szót, mindenki nyer egy pontot.' }""",
    'desc')

sub("const APP_VERSION = 'v10.285';", "const APP_VERSION = 'v10.286';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — 12 szavas lánc, jackpot, 2-4/5-7/8+ fokozatok')
