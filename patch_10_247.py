#!/usr/bin/env python3
# v10.247 — "Szoba létrehozása…" képernyő: töltődő edény, három rajzzal
#
# A régi képernyő egy nagy ajtó-PNG + felirat + három pattogó pont volt: sok
# hangsúly egy fél másodperces pillanatra, és az ajtó semmit nem mondott, amit
# a felirat ne mondana el.
#
# Helyette: EGY edény telik meg — a töltés maga a folyamatjelző. Három rajz
# van (korsó / palack / feles-sor), és szobanyitáskor véletlenszerűen sorsolunk
# egyet, hogy egy ilyen rövid képernyő ne koptasson.
#
# Miért SVG és nem kép: éles marad minden kijelzőn, nincs új asszet, a szín az
# app témájából jön (T.ink kontúr), tehát sötét témában is működik.
#
# A töltés SZÁNDÉKOSAN ~18%-ról indul és az első pillanatokban halad a
# leggyorsabban: a képernyő gyakran rövidebb ideig él, mint az animáció, így
# egy villanás is befejezett mozdulatnak látszik, nem félbehagyottnak.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1. keyframe-ek ──
sub("""    @keyframes miniBarIn { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }""",
    """    @keyframes miniBarIn { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }
    /* Szoba-töltés: a szint emelkedése. A kezdőérték nem 0 — lásd patch_10_247.py */
    @keyframes bohFill { 0%{transform:translateY(var(--from))} 76%,100%{transform:translateY(var(--to))} }
    @keyframes bohBubble { 0%{transform:translateY(0);opacity:0} 12%{opacity:.85} 85%{opacity:.1} 100%{transform:translateY(-44px);opacity:0} }
    @keyframes bohShotFill { 0%,4%{transform:translateY(26px)} 16%,100%{transform:translateY(1px)} }""",
    'keyframes')

# ── 2. a három rajz ──
ART = r'''
// ── Szoba-töltés illusztrációk ────────────────────────────────────────────────
// Harom rajz, kozos mozdulattal: az edeny megtelik, es EZ a folyamatjelzo.
// Szobanyitaskor sorsolunk egyet (BOH_ROOM_ART_COUNT), hogy ne kopjon el.
// SVG, nem kep: eles marad, nincs uj asszet, a kontur az app T.ink-jebol jon.
const BOH_ROOM_ART_COUNT = 3;
function RoomFillArt({ variant }) {
  const line = T.ink;
  const foam = '#FFFCF3';
  const bubbles = (pts) => pts.map((b, i) => (
    <circle key={i} cx={b[0]} cy={b[1]} r={b[2]} fill="#FFF6DC"
            style={{ opacity:0, animation:`bohBubble 2.6s ${b[3]}s ease-in infinite` }} />
  ));

  // ── 0 · KORSÓ — egyenes fal, vastag D-fül, függőleges bordák ──
  if (variant === 0) return (
    <svg width="min(52vw, 208px)" height="auto" viewBox="0 0 126 152" role="img" aria-label="Töltődő korsó"
         style={{ display:'block', filter:'drop-shadow(0 10px 20px rgba(20,30,50,0.16))' }}>
      <defs>
        <clipPath id="bohKorso"><path d="M30 30 L33 132 Q33 139 41 139 L77 139 Q85 139 85 132 L88 30 Z"/></clipPath>
        <linearGradient id="bohBeer1" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#F7CB63"/><stop offset="1" stopColor="#D98A18"/>
        </linearGradient>
      </defs>
      <path d="M86 56 q26 5 26 25 t-26 25" fill="none" stroke={line} strokeWidth="11" strokeLinecap="round" opacity=".92"/>
      <g clipPath="url(#bohKorso)">
        <rect x="20" y="20" width="80" height="130" fill="#FFFFFF" opacity=".55"/>
        <g style={{ animation:'bohFill 3.4s cubic-bezier(.45,0,.25,1) infinite', '--from':'86px', '--to':'26px' }}>
          <path d="M18 0 q11 7 22 0 t22 0 t22 0 t22 0 v17 H18 Z" fill={foam}/>
          <rect x="18" y="15" width="94" height="190" fill="url(#bohBeer1)"/>
        </g>
        {bubbles([[47,126,2.6,0.1],[60,132,2,0.9],[70,124,2.9,1.6],[54,136,1.7,2.3]])}
        <path d="M45 36 L46 128" stroke="#FFFFFF" strokeWidth="2.5" strokeLinecap="round" opacity=".38"/>
        <path d="M62 36 L62 128" stroke="#FFFFFF" strokeWidth="2.5" strokeLinecap="round" opacity=".3"/>
        <path d="M79 36 L78 128" stroke="#FFFFFF" strokeWidth="2.5" strokeLinecap="round" opacity=".26"/>
        <path d="M37 40 L39 124" stroke="#FFFFFF" strokeWidth="6" strokeLinecap="round" opacity=".55"/>
      </g>
      <path d="M30 30 L33 132 Q33 139 41 139 L77 139 Q85 139 85 132 L88 30 Z"
            fill="none" stroke={line} strokeWidth="5.5" strokeLinejoin="round" opacity=".92"/>
      <ellipse cx="59" cy="30" rx="29" ry="6.5" fill="none" stroke={line} strokeWidth="5.5" opacity=".92"/>
    </svg>
  );

  // ── 1 · PALACK — gyűrűs száj + fogazott koronakupak ──
  if (variant === 1) return (
    <svg width="min(44vw, 176px)" height="auto" viewBox="0 0 106 156" role="img" aria-label="Töltődő palack"
         style={{ display:'block', filter:'drop-shadow(0 10px 20px rgba(20,30,50,0.16))' }}>
      <defs>
        <clipPath id="bohPalack">
          <path d="M46 30 h14 v20 c0 10 4 14 10 21 c6 7 8 12 8 21 v48 q0 10 -10 10 H38 q-10 0 -10 -10 V92 c0 -9 2 -14 8 -21 c6 -7 10 -11 10 -21 Z"/>
        </clipPath>
        <linearGradient id="bohBeer2" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#F7CB63"/><stop offset="1" stopColor="#D07E12"/>
        </linearGradient>
      </defs>
      <g clipPath="url(#bohPalack)">
        <rect x="24" y="24" width="60" height="130" fill="#FFFFFF" opacity=".5"/>
        <g style={{ animation:'bohFill 3.4s cubic-bezier(.45,0,.25,1) infinite', '--from':'80px', '--to':'20px' }}>
          <path d="M20 0 q10 6 20 0 t20 0 t20 0 t20 0 v13 H20 Z" fill={foam}/>
          <rect x="20" y="11" width="70" height="180" fill="url(#bohBeer2)"/>
        </g>
        {bubbles([[44,132,2.4,0.3],[58,138,1.9,1.2],[51,128,2.7,2.1]])}
        <rect x="34" y="104" width="38" height="22" rx="4" fill="#FFFFFF" opacity=".6"/>
        <path d="M37 60 L35 132" stroke="#FFFFFF" strokeWidth="5" strokeLinecap="round" opacity=".5"/>
      </g>
      <rect x="42" y="24" width="22" height="8" rx="2.5" fill={line} opacity=".92"/>
      <path d="M40 20 h26 v-8 a3 3 0 0 0 -3 -3 h-20 a3 3 0 0 0 -3 3 z" fill={line} opacity=".92"/>
      <path d="M40 20 l3.2 4 l3.2 -4 l3.2 4 l3.2 -4 l3.2 4 l3.2 -4 l3.2 4 l3.6 -4 z" fill={line} opacity=".92"/>
      <rect x="43" y="12" width="20" height="2.4" rx="1.2" fill="#FFFFFF" opacity=".3"/>
      <path d="M46 30 h14 v20 c0 10 4 14 10 21 c6 7 8 12 8 21 v48 q0 10 -10 10 H38 q-10 0 -10 -10 V92 c0 -9 2 -14 8 -21 c6 -7 10 -11 10 -21 Z"
            fill="none" stroke={line} strokeWidth="5" strokeLinejoin="round" opacity=".92"/>
    </svg>
  );

  // ── 2 · FELES-SOR — hat stampedli, vastag tömör talppal, balról jobbra ──
  return (
    <svg width="min(80vw, 316px)" height="auto" viewBox="0 0 216 74" role="img" aria-label="Töltődő felesek"
         style={{ display:'block', filter:'drop-shadow(0 10px 20px rgba(20,30,50,0.16))' }}>
      <defs>
        <clipPath id="bohFeles"><path d="M4.5 16 L8 45 h14 L25.5 16 Z"/></clipPath>
        <linearGradient id="bohPal" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#F7D98A"/><stop offset="1" stopColor="#E0A93A"/>
        </linearGradient>
      </defs>
      {[0,1,2,3,4,5].map(i => (
        <g key={i} transform={`translate(${i * 36 + 4},0)`}>
          <g clipPath="url(#bohFeles)">
            <rect x="0" y="10" width="32" height="42" fill="#FFFFFF" opacity=".55"/>
            <g style={{ animation:`bohShotFill 3.6s ${i * 0.2}s cubic-bezier(.45,0,.25,1) infinite` }}>
              <rect x="0" y="20" width="32" height="42" fill="url(#bohPal)"/>
              <rect x="0" y="18.6" width="32" height="2.2" fill={foam}/>
            </g>
            <path d="M9.5 22 L11 40" stroke="#FFFFFF" strokeWidth="2.6" strokeLinecap="round" opacity=".5"/>
          </g>
          <path d="M6 44 h18 l1.5 8 q0 3 -3 3 H7.5 q-3 0 -3 -3 Z" fill={line} opacity=".92"/>
          <path d="M4.5 16 L8 45 h14 L25.5 16" fill="none" stroke={line} strokeWidth="3.6" strokeLinejoin="round" strokeLinecap="round" opacity=".92"/>
          <ellipse cx="15" cy="16" rx="10.5" ry="3.2" fill="none" stroke={line} strokeWidth="3.6" opacity=".92"/>
        </g>
      ))}
    </svg>
  );
}

'''

sub("""// ── AdminScreen ────────────────────────────────────────────────────────────────""",
    ART + """// ── AdminScreen ────────────────────────────────────────────────────────────────""",
    'RoomFillArt komponens')

# ── 3. a képernyő cseréje ──
sub("""              <img src="assets/room_door.png" alt=""
                style={{ width:'min(62vw, 260px)', maxHeight:'44vh', objectFit:'contain',
                         display:'block', userSelect:'none',
                         filter:'drop-shadow(0 10px 22px rgba(20,30,50,0.16))',
                         animation:'roomDoorIn .5s cubic-bezier(.2,.85,.3,1.05)' }}
                draggable="false" />
              <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay, textAlign:'center' }}>Szoba létrehozása…</div>
              <div style={{ display:'flex', gap:6 }}>{[0,1,2].map(i => <span key={i} style={{ width:10, height:10, borderRadius:'50%', background:T.mint, animation:`dotBounce 1.2s ${i*0.15}s infinite ease-in-out` }}/>)}</div>""",
    """              <RoomFillArt variant={roomArtVariant} />
              <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay, textAlign:'center', marginTop:6 }}>Töltjük a szobát</div>
              <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', marginTop:-8 }}>Mindjárt kész</div>""",
    'kepernyo tartalma')

# ── 4. a sorsolás ──
sub("""  const [creatingRoom, setCreatingRoom] = React.useState(false);""",
    """  const [creatingRoom, setCreatingRoom] = React.useState(false);
  // Melyik toltodo edeny jojjon? Minden szobanyitasnal ujra sorsolunk, hogy egy
  // ilyen rovid kepernyo ne kopjon el annak, aki sokat nyit szobat.
  const [roomArtVariant, setRoomArtVariant] = React.useState(() => Math.floor(Math.random() * BOH_ROOM_ART_COUNT));
  React.useEffect(() => {
    if (creatingRoom) setRoomArtVariant(Math.floor(Math.random() * BOH_ROOM_ART_COUNT));
  }, [creatingRoom]);""",
    'sorsolas')

sub("const APP_VERSION = 'v10.246';", "const APP_VERSION = 'v10.247';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — toltodo edeny harom rajzzal, sorsolva')
