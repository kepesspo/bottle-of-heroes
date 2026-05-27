// bottle-theme.jsx — token sets for the two variations + shared utilities

// ─── Variation A — POLISHED ──────────────────────────────────
// Refined original: same warm yellow DNA, tighter type ramp,
// more confident spacing, softer mint/coral.
const THEME_A = {
  id: 'A',
  name: 'Polished',
  bg: '#F4C57E',
  bgSoft: '#F8D69A',
  bgDeep: '#E8B260',
  surface: '#FFFFFF',
  surfaceMuted: '#FBEFD8',
  ink: '#1A2A4A',
  inkSoft: '#4A5878',
  inkMute: '#8A93A8',
  mint: '#4FC2A0',
  mintSoft: '#D9F1E8',
  mintDeep: '#3DA888',
  coral: '#F2A0A0',
  coralSoft: '#FBDADA',
  purple: '#A88AE8',
  yellow: '#F4C95A',
  blue: '#5BA0DB',
  pink: '#E985B8',
  font: '"Nunito", -apple-system, system-ui, sans-serif',
  fontDisplay: '"Nunito", -apple-system, system-ui, sans-serif',
  weightDisplay: 900,
  weightTitle: 800,
  weightBody: 600,
  letter: '-0.01em',
  letterDisplay: '-0.02em',
  shadow: '0 2px 0 rgba(20,30,50,0.04), 0 6px 20px rgba(20,30,50,0.06)',
  shadowLift: '0 4px 0 rgba(20,30,50,0.06), 0 12px 32px rgba(20,30,50,0.10)',
  ring: 'inset 0 0 0 1px rgba(20,30,50,0.06)',
};

// ─── Variation C — SUNSET (sibling of A) ─────────────────────
// Same playful DNA, warmer & more refined: deeper sage mint, terracotta
// coral, cream cards instead of pure white, subtle radial warmth in bg.
const THEME_C = {
  id: 'C',
  name: 'Sunset',
  bg: 'radial-gradient(120% 70% at 50% -10%, #F8D49A 0%, #F1B470 55%, #E29B4F 110%)',
  bgSolid: '#F1B470',
  bgSoft: '#F6CB91',
  bgDeep: '#E29B4F',
  surface: '#FFF6E4',
  surfaceMuted: '#FAE9CB',
  ink: '#23282E',
  inkSoft: '#5A5A5A',
  inkMute: '#9A8E80',
  mint: '#3DA888',
  mintSoft: '#CDE9DC',
  mintDeep: '#2A8870',
  coral: '#E08B6B',
  coralSoft: '#F6D4C2',
  purple: '#A88AE8',
  yellow: '#F0BE4C',
  blue: '#5BA0DB',
  pink: '#D97A95',
  font: '"Nunito", -apple-system, system-ui, sans-serif',
  fontDisplay: '"Nunito", -apple-system, system-ui, sans-serif',
  weightDisplay: 900,
  weightTitle: 800,
  weightBody: 600,
  letter: '-0.01em',
  letterDisplay: '-0.01em',
  shadow: '0 2px 0 rgba(60,40,20,0.04), 0 8px 24px rgba(60,40,20,0.08)',
  shadowLift: '0 4px 0 rgba(60,40,20,0.05), 0 14px 36px rgba(60,40,20,0.12)',
  ring: 'inset 0 0 0 1px rgba(60,40,20,0.06)',
};

// ─── Variation B — BRUTALIST PARTY ───────────────────────────
// Experimental: huge condensed display type, hard offset shadows,
// layered sticker cards, electric accents on warm bg.
const THEME_B = {
  id: 'B',
  name: 'Brutalist Party',
  bg: '#FDE3A7',
  bgSoft: '#FFF1C9',
  bgDeep: '#F4C97A',
  surface: '#FFF9EC',
  surfaceMuted: '#F4E8C8',
  ink: '#0E0E18',
  inkSoft: '#3B3645',
  inkMute: '#8A7E78',
  mint: '#22D096',
  mintSoft: '#B7F0DA',
  mintDeep: '#0E9F70',
  coral: '#FF6B6B',
  coralSoft: '#FFD2D2',
  purple: '#7C3AED',
  yellow: '#FFD23F',
  blue: '#3B82F6',
  pink: '#FF3DA1',
  font: '"Space Grotesk", -apple-system, system-ui, sans-serif',
  fontDisplay: '"Anton", "Archivo Black", "Bebas Neue", Impact, sans-serif',
  weightDisplay: 400,
  weightTitle: 700,
  weightBody: 500,
  letter: '0',
  letterDisplay: '-0.01em',
  shadow: '3px 3px 0 #0E0E18',
  shadowLift: '5px 5px 0 #0E0E18',
  ring: '2px solid #0E0E18',
};

// ─── Game catalog (Hungarian) ────────────────────────────────
// 25 games, each with its own illustration in the bottle-logo style.
// Images served from media.base44.com (same library as the existing app).
const IMG = 'https://media.base44.com/images/public/6a13fd728a0d72caf4de8c08/';
const GAMES = [
  { id: 'busz',       name: 'Busz',                  difficulty: 'nehéz',   category: 'Csapat', emoji: '🚌', img: '',
    color: '#F4A04A', desc: 'Mindenki Tudja' },
  { id: 'memoria',    name: 'Memória',               difficulty: 'nehéz',   category: 'Csapat', emoji: '🧩', img: IMG + 'c08054bde_008-puzzle.png',
    color: '#22D096', desc: 'Egy kategóriába el kell kezdeni mondani szavakat és utána ismételni kell az előzőeket, aki elrontja az iszik. A játék választja ki ki kezd.' },
  { id: 'erem',       name: 'Érem dobás',            difficulty: 'könnyű',  category: 'Páros',  emoji: '🪙', img: IMG + 'b2b517b2a_005-promise.png',
    color: '#F4C95A', desc: 'Az app kiválaszt egy játékost aki kihivhat valakit hogy játsszon vele. A két játékosnak választani kell a Fej és az Írás között. Ez után a kihívó feldobja az érmét és amelyik oldalára esik az a játékos nyert és a másiknak innia kell.' },
  { id: 'ticktak',    name: 'Tick Tak',              difficulty: 'közepes', category: 'Csapat', emoji: '⏰', img: IMG + 'e20faaaa0_048-letter.png',
    color: '#FF6B6B', desc: 'A játék inditásával elindul egy számláló a háttérben, ekkor el kell kezdeni körbeadni egy tárgyat a játékosok között. Mikor az időzitő megszólal annál az embernél akinél épp az adott tárgy van ő vesztett és neki kell a büntetést meginnia.' },
  { id: 'kezcsere',   name: 'Kéz csere',             difficulty: 'nehéz',   category: 'Csapat', emoji: '🤙', img: IMG + '1b1a4e166_041-shaka.png',
    color: '#5BA0DB', desc: 'A játék úgy kezdődik hogy keresztbe rakjátok a kezeteket az asztalon. Egyik egyénileg választott irányba indul a kör.\n1 Koppintás = Abba az irányba megy tovább.\n2 Koppintás = Fordított irányba indul.\n3 Koppintás = A soron következőnek nem szabad koppintania.\nAki ront az iszik.' },
  { id: 'anagramma',  name: 'Anagramma',             difficulty: 'könnyű',  category: 'Egyéni', emoji: '💬', img: IMG + 'c7dd9fd19_018-social-media.png',
    color: '#FF3DA1', desc: 'Az applikáció kisorsol egy játékost aki játszani fog. A Start gombra nyomva megjelenik a képernyőn 4 betű amiből 5 mp alatt egy értelmes magyar szót kell kiraknia. Amennyiben ez nem sikerül úgy innia kell a játékosnak.' },
  { id: 'ringfire',   name: 'Ring of Fire',          difficulty: 'közepes', category: 'Egyéni', emoji: '🔥', img: IMG + '30be0a7f6_022-bracelet.png',
    color: '#F97316', desc: 'Választani kell a kártyák közül és a kártyának a leírását kell megcsinálni.\n2 — Choose: válassz valakit aki iszik\n3 — Me: én iszok\n4 — Whore: összes lány iszik\n5 — Thumb Master: aki kihúzza ő lesz a játékmester\n6 — Dicks: összes fiú iszik\n7 — Heaven: fel kell mutatni az égre\n8 — Mate: válassz valakit aki iszik veled\n9 — Rhyme: rímelni kell\n10 — Categories: kategóriákat kell mondani\nJack — Make a Rule: hozni kell egy szabályt\nQueen — Questions: kérdésekkel kell beszélni\nKing — Pour: össze kell önteni a piákat\nA — Waterfall: addig kell inni amíg az ászt húzó iszik.' },
  { id: 'rulett',     name: 'Orosz Rulett',          difficulty: 'könnyű',  category: 'Egyéni', emoji: '🎯', img: IMG + '00fb8bff7_030-dependable.png',
    color: '#A855F7', desc: 'Három darab kártya közül kell választani. 2 alatt Tűzjáték van, 1 alatt pia. Egyet kell húzni — ha tűzjátékot húzol akkor megúsztál nem kell innod. Ha piát akkor kell. Ezt a játékot csak egy ember játsza.' },
  { id: 'kisebb',     name: 'Kisebb vagy Nagyobb',   difficulty: 'közepes', category: 'Csapat', emoji: '🚩', img: IMG + 'a6501c235_011-friendship.png',
    color: '#EF4444', desc: 'A játék úgy kezdődik hogy az app kiválaszt egy játékost aki a sort fogja kezdeni. Neki meg kell mondania, hogy a következő szám kisebb, vagy nagyobb lesz mint amit a játék kiír. Ez után a következő játékos jön. Minél tovabb megy a játék annál többet kell innia annak aki hibázik.' },
  { id: 'tapper',     name: 'Tapper',                difficulty: 'könnyű',  category: 'Páros',  emoji: '👇', img: IMG + '4d3e02af9_016-best-friend.png',
    color: '#10B981', desc: 'Az app kiválaszt egy játékost aki kihivhat valakit hogy játsszon vele. Mind a két játékosnak a kijelölt pontra kell raknia az egyik ujját. Egy visszaszámláló elindul 5-től és minél közelebb a 0-hoz kell elengednie a gombot. Csak a vesztes iszik.' },
  { id: 'kategoria',  name: 'Kategória',             difficulty: 'nehéz',   category: 'Csapat', emoji: '🗂️', img: IMG + '21cd10e7c_034-chat.png',
    color: '#3B82F6', desc: 'A játék választ egy kategóriát és erre az első embernek kell mondani rá egy szót ami abba a kategóriába beleillik. Ez után a következő játékosnak az előző szónak az utolsó betűjével kell egy szót mondania. Az aki először hibázik az iszik. 5 másodperc a megengedett gondolkodási idő.' },
  { id: 'hajime',     name: 'Hajime',                difficulty: 'nehéz',   category: 'Csapat', emoji: '😆', img: IMG + 'ed7ba4369_013-laugh.png',
    color: '#FACC15', desc: 'Számolj helyesen! El kell kezdeni számolni 1-től és ha 5-tel vagy 7-tel osztható a szám vagy szerepel benne az 5 vagy a 7 akkor "hajime"-t kell mondani. Aki eltéveszti az iszik. Egy plusz csavar: minden "hajime" után megfordul a kör.' },
  { id: 'kopapir',    name: 'Kő Papír Olló',         difficulty: 'nehéz',   category: 'Csapat', emoji: '✊', img: IMG + '717d78f62_026-fist.png',
    color: '#7C3AED', desc: 'Annyi kört kell játszani ahány játékos van. Kell egy kezdő ember aki kihivja a mellette ülőt, ezt a játék választja ki. Ha te nyersz akkor ő iszik és az ő mellette ülővel kell játszania. Ha te vesztesz akkor a te melletted ülővel kell játszanod. Ha döntetlen akkor mind a ketten isztok.' },
  { id: 'fingerit',   name: 'Finger It',             difficulty: 'könnyű',  category: 'Csapat', emoji: '👆', img: IMG + '03d87dd1b_014-sharing.png',
    color: '#06B6D4', desc: 'Minden játékos az asztalra rakja a mutató ujját. Aztán számolni kezd az első ember akit a játék választ ki: 1, 2, 3 — ekkor hirtelen mindenkinek el kell vennie az ujját az asztalról, vagy rajta hagyja. A lényeg hogy pontosan annyi ujj maradjon az asztalon ahány szám be lett mondva. Ha eltalálod akkor mindenki más iszik. Ha nem találod el akkor te iszol.' },
  { id: 'uveg',       name: 'Az üveg',               difficulty: 'közepes', category: 'Egyéni', emoji: '🍾', img: IMG + 'b3ebed6db_012-beer.png',
    color: '#F59E0B', desc: 'Az app kisorsol egy játékost akinek meg kell pörgetnie az üveget. Akire az üveg az asztalnál mutat annak kell innia.' },
  { id: 'zene',       name: 'Zene Felismerés',       difficulty: 'közepes', category: 'Egyéni', emoji: '🎵', img: IMG + 'c6e7b8a7f_021-listener.png',
    color: '#8B5CF6', desc: 'A játékban egy zenét fog a játékos hallani 5 másodpercig. Ez után ki kell találni hogy ki az előadó és mi a szám címe. Ha a kettőből az egyik sikerül akkor nem kell innia. Ha mind a kettőt sikeresen kitalálja akkor kioszthat egy piát. Ha egyiket sem tudja akkor neki kell innia.' },
  { id: 'loverseny',  name: 'Lóverseny',             difficulty: 'közepes', category: 'Csapat', emoji: '🐎', img: IMG + '8892f3ea4_017-origami.png',
    color: '#84CC16', desc: 'Minden játékos 1–3 egységben fogadhat a négy ló egyikére. A versenylovak a Sárga, a Zöld, a Kék és a Piros. Ha az a ló ér be először akire fogadott, akkor annyi piát kioszthat. Ha nem az nyer akire fogadott, akkor a megtett mennyiséget kell elfogyasztania.' },
  { id: 'otdolog',    name: '5 dolog',               difficulty: 'könnyű',  category: 'Egyéni', emoji: '5️⃣', img: IMG + 'fd5a5b716_007-connection.png',
    color: '#EC4899', desc: 'Az app kisorsol egy játékost aki játszani fog. Meg fog jelenni a képernyőn egy kategória. Ebben a kategóriában kell a játékosnak 5 mp alatt 5 odatartozó szót mondania. Amennyiben ez nem sikerül innia kell.' },
  { id: 'szerencse',  name: 'Szerencsekerék',        difficulty: 'közepes', category: 'Egyéni', emoji: '🎡', img: IMG + '955f768b7_006-loyalty.png',
    color: '#14B8A6', desc: 'A játék kiválaszt egy játékost akinek meg kell pörgetnie a szerencsekereket. Akit a szerencsekerék kisorsol annak innia kell.' },
  { id: 'sohanem',    name: 'Én még soha',           difficulty: 'közepes', category: 'Egyéni', emoji: '🙅', img: IMG + '6c2a1444c_002-mad.png',
    color: '#D946EF', desc: 'Jön egy állítás és ha az igaz rád akkor innod kell, ha nem igaz rád akkor nem kell.' },
  { id: 'collect',    name: 'Collect and Boom',      difficulty: 'közepes', category: 'Csapat', emoji: '💣', img: IMG + 'fbae429ac_025-add-friend.png',
    color: '#0EA5E9', desc: 'Az app kisorsol egy játékost aki el fogja kezdeni a kört. A játéktábláról ki kell választania egy cellát. Utána a tőle jobbra ülő fog választani egyet, addig választanak a játékosok ameddig egy bombát találnak — ekkor a játék véget ért és az addig összegyűjtött egységet kell meginnia a vesztesnek.' },
  { id: 'kivagyok',   name: 'Ki Vagyok Én',          difficulty: 'közepes', category: 'Egyéni', emoji: '🕵️', img: IMG + '0be64fa0c_033-reunion.png',
    color: '#F472B6', desc: 'Az app mutat egy híresség fotóját és ki kell találni ki van a képen. Ebben a játékban csak egy játékos vesz részt. Ha pontosan meg tudja mondani a híresség életkorát vagy foglalkozását akkor kioszthat egy piát.' },
  { id: 'mindenki',   name: 'Mindenki Iszik Egyszer',difficulty: 'könnyű',  category: 'Egyéni', emoji: '🍻', img: IMG + '7721960ea_024-friendship-1.png',
    color: '#F4C95A', desc: 'A játék kiválaszt egy játékost akinek innia kell. Ezt az app sorsolja ki, ha elfogyta az emberek akkor előről megy a kör.' },
  { id: 'igazhamis',  name: 'Igaz Hamis',            difficulty: 'könnyű',  category: 'Egyéni', emoji: '🤔', img: IMG + 'f52ad051b_035-friend.png',
    color: '#06B6D4', desc: 'A játékban egy állítás fog megjelenni és el kell dönteni, hogy az igaz, vagy hamis. Ha úgy ítéled meg hogy az állítás igaz, akkor az idő lejárta előtt ezt közölnöd kell a többi játékossal akik ez alapján tudjuk eldönteni, hogy jól válaszoltál-e. Ha nem jó a válaszod akkor sajnos innod kell.' },
];

const DIFFICULTY_META = {
  'könnyű':  { label: 'Könnyű',  tone: '#22D096' },
  'közepes': { label: 'Közepes', tone: '#F4C95A' },
  'nehéz':   { label: 'Nehéz',   tone: '#FF6B6B' },
};
const CATEGORY_META = {
  'Egyéni': { label: 'Egyéni', icon: '👤' },
  'Páros':  { label: 'Páros',  icon: '🤝' },
  'Csapat': { label: 'Csapat', icon: '👥' },
};

const PLAYER_COLORS = [
  '#4FC2A0', // mint
  '#E985B8', // pink
  '#F4C95A', // yellow
  '#5BA0DB', // blue
  '#1A2A4A', // navy
  '#F2A0A0', // coral
  '#A88AE8', // purple
  '#F97316', // orange
  '#10B981', // green
  '#EF4444', // red
];

const INITIAL_PLAYERS = [
  { id: 'p1', name: 'Márkó', color: '#4FC2A0', drinks: 0, points: 0 },
  { id: 'p2', name: 'Sanyi', color: '#E985B8', drinks: 0, points: 0 },
  { id: 'p3', name: 'Tibi',  color: '#F4C95A', drinks: 0, points: 0 },
  { id: 'p4', name: 'Réka',  color: '#5BA0DB', drinks: 0, points: 0 },
  { id: 'p5', name: 'Márk',  color: '#1A2A4A', drinks: 0, points: 0 },
];

// Tiny inline icons (stroked, monoline-ish — matches the playful icon vibe).
const Icon = {
  back: (c='currentColor') => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <path d="M15 6l-6 6 6 6" stroke={c} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  close: (c='currentColor') => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
      <path d="M6 6l12 12M18 6L6 18" stroke={c} strokeWidth="2.5" strokeLinecap="round"/>
    </svg>
  ),
  plus: (c='currentColor') => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <path d="M12 5v14M5 12h14" stroke={c} strokeWidth="2.5" strokeLinecap="round"/>
    </svg>
  ),
  check: (c='currentColor') => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <path d="M5 12l5 5L20 7" stroke={c} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  user: (c='currentColor') => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="8" r="3.5" stroke={c} strokeWidth="2"/>
      <path d="M5 20c1.5-3.5 4-5 7-5s5.5 1.5 7 5" stroke={c} strokeWidth="2" strokeLinecap="round"/>
    </svg>
  ),
  users: (c='currentColor') => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <circle cx="9" cy="9" r="3" stroke={c} strokeWidth="2"/>
      <circle cx="17" cy="10" r="2.5" stroke={c} strokeWidth="2"/>
      <path d="M3 19c1-3 3-4.5 6-4.5s5 1.5 6 4.5M16 16c2 .3 4 1.5 5 3.5" stroke={c} strokeWidth="2" strokeLinecap="round"/>
    </svg>
  ),
  controller: (c='currentColor') => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <path d="M7 9h10a5 5 0 015 5v0a4 4 0 01-4 4h-1l-2-2H9l-2 2H6a4 4 0 01-4-4v0a5 5 0 015-5z" stroke={c} strokeWidth="2"/>
      <path d="M9 13v-1M9 13v1M8 13h2M15 13h.01M17 14h.01" stroke={c} strokeWidth="2" strokeLinecap="round"/>
    </svg>
  ),
  info: (c='currentColor') => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="9" stroke={c} strokeWidth="2"/>
      <path d="M12 11v6M12 8v.01" stroke={c} strokeWidth="2.5" strokeLinecap="round"/>
    </svg>
  ),
  beer: (c='currentColor') => (
    <svg width="20" height="22" viewBox="0 0 24 26" fill="none">
      <path d="M5 7h11v15a2 2 0 01-2 2H7a2 2 0 01-2-2V7z" stroke={c} strokeWidth="2" strokeLinejoin="round"/>
      <path d="M16 10h2.5a2.5 2.5 0 010 5H16" stroke={c} strokeWidth="2"/>
      <path d="M8 11v8M11 11v8M5 5c1-2 3-2 4-1s2 1 3 0 3-1 4 1" stroke={c} strokeWidth="2" strokeLinecap="round"/>
    </svg>
  ),
  dice: (c='currentColor') => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <rect x="4" y="4" width="16" height="16" rx="3" stroke={c} strokeWidth="2"/>
      <circle cx="9" cy="9" r="1.3" fill={c}/>
      <circle cx="15" cy="15" r="1.3" fill={c}/>
      <circle cx="15" cy="9" r="1.3" fill={c}/>
      <circle cx="9" cy="15" r="1.3" fill={c}/>
    </svg>
  ),
  trash: (c='currentColor') => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <path d="M4 7h16M9 7V5a2 2 0 012-2h2a2 2 0 012 2v2M6 7l1 13a2 2 0 002 2h6a2 2 0 002-2l1-13" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  shuffle: (c='currentColor') => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <path d="M16 4l4 4-4 4M16 12l4 4-4 4M4 8h4l8 8h4M4 16h4l2-2M14 10l2-2h4" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  trophy: (c='currentColor') => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
      <path d="M7 4h10v5a5 5 0 01-10 0V4z" stroke={c} strokeWidth="2" strokeLinejoin="round"/>
      <path d="M7 6H4v2a3 3 0 003 3M17 6h3v2a3 3 0 01-3 3M9 17h6l1 4H8l1-4zM10 14v3M14 14v3" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  star: (c='currentColor') => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill={c}>
      <path d="M12 2l2.9 6.9L22 10l-5.5 4.8L18.2 22 12 18l-6.2 4 1.7-7.2L2 10l7.1-1.1L12 2z"/>
    </svg>
  ),
  settings: (c='currentColor') => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="3" stroke={c} strokeWidth="2"/>
      <path d="M19.4 15a1.7 1.7 0 00.3 1.8l.1.1a2 2 0 11-2.8 2.8l-.1-.1a1.7 1.7 0 00-1.8-.3 1.7 1.7 0 00-1 1.5V21a2 2 0 01-4 0v-.1a1.7 1.7 0 00-1-1.5 1.7 1.7 0 00-1.8.3l-.1.1a2 2 0 11-2.8-2.8l.1-.1a1.7 1.7 0 00.3-1.8 1.7 1.7 0 00-1.5-1H3a2 2 0 010-4h.1a1.7 1.7 0 001.5-1 1.7 1.7 0 00-.3-1.8l-.1-.1a2 2 0 112.8-2.8l.1.1a1.7 1.7 0 001.8.3h0a1.7 1.7 0 001-1.5V3a2 2 0 014 0v.1a1.7 1.7 0 001 1.5 1.7 1.7 0 001.8-.3l.1-.1a2 2 0 112.8 2.8l-.1.1a1.7 1.7 0 00-.3 1.8v0a1.7 1.7 0 001.5 1H21a2 2 0 010 4h-.1a1.7 1.7 0 00-1.5 1z" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  flame: (c='currentColor') => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <path d="M12 2c1 4 5 5 5 10a5 5 0 11-10 0c0-2 1-3 2-4 0 2 1 3 2 3 0-3-1-5 1-9z" stroke={c} strokeWidth="2" strokeLinejoin="round"/>
    </svg>
  ),
};

Object.assign(window, { THEME_A, THEME_B, THEME_C, GAMES, DIFFICULTY_META, CATEGORY_META, PLAYER_COLORS, INITIAL_PLAYERS, Icon });
