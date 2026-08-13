# v10.358 - A KOZOS BohTimer bekotese az utolso harom gyuru helyere
#
# A `BohTimer` v10.329 ota kesz, de eddig csak KET helyen ment (Otdolog sav,
# Busz pill). A tobbi jatek sajat gyurut rajzolt — mind ugyanazt csinalta, csak
# maskepp nezett ki, es 76–100 px magassagot evett a jatek tartalma elol.
#
# Ez a harom maradt (a negyedik, a Finger It gyuruje az Ujjosszeg-atirassal mar
# eltunt v10.356-ban):
#   • Csak Egy Szó  — 100 px gyuru, 15 mp
#   • Ritmus Játék  —  76 px gyuru a fejlec-sorban
#   • Tabu Szó      —  84 px gyuru, kozepen, alatta „másodperc" felirat
#
# ⚠️ A PlayScreen fejlec-gyuruje NEM idozito, hanem a KOR-szamlalo — ahhoz nem
# nyulunk. (`strokeDasharray={circOuter}`, a `stake_test` meri.)
#
# ⚠️ A RITMUSNAL a gyuru egy HAROM ELEMU sor kozepen ult (jatekos-pirula |
# gyuru | pont-pirula). Egy 30 px-es, teljes szelessegu sav nem fer abba a
# sorba, ezert a sor KETTOS elemuve valik, es a sav a sor ALA kerul. A
# `space-between` igy is helyes: a ket pirula a ket szelre megy.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# ── 1. CSAK EGY SZO ─────────────────────────────────────────────────────────
sub1(
"""          <svg width={100} height={100} style={{ flexShrink:0 }}>
            <circle cx={50} cy={50} r={44} fill="none" stroke="rgba(0,0,0,0.08)" strokeWidth={8} />
            <circle cx={50} cy={50} r={44} fill="none" stroke={timeLeft<=5?T.coral:T.mint} strokeWidth={8}
              strokeDasharray={circumference} strokeDashoffset={circumference*(1-pct/100)}
              strokeLinecap="round" transform="rotate(-90 50 50)" style={{ transition:'stroke-dashoffset .9s linear' }}/>
            <text x={50} y={55} textAnchor="middle" fontFamily={T.font} fontWeight={900} fontSize={28} fill={timeLeft<=5?T.coral:T.ink}>{timeLeft}</text>
          </svg>""",
"""          {/* A KOZOS visszaszamlalo (v10.329): 30 px, vizszintes. A regi 100 px-es
              gyuru ennyivel tobbet vett el a szo es a gomb elol. */}
          <BohTimer variant="bar" total={15} left={timeLeft} />""",
'CsakEgySzo idozito')

# a gyuruhoz tartozo szamitasok halottak lettek
sub1("""  const circumference = 2 * Math.PI * 44;\n""", "", 'CsakEgySzo circumference')
sub1("""  const pct = (timeLeft / 15) * 100;\n""", "", 'CsakEgySzo pct')

# ── 2. RITMUS ───────────────────────────────────────────────────────────────
# A gyuru kikerul a haromelemu sorbol, es sav lesz belole a sor ALATT.
sub1(
"""          <svg width={76} height={76} viewBox="0 0 48 48" style={{ flexShrink:0 }}>
            <circle cx={24} cy={24} r={rT} fill="none" stroke="rgba(20,30,50,0.1)" strokeWidth={3.5}/>
            <circle cx={24} cy={24} r={rT} fill="none" stroke={timeLeft <= 5 ? T.coral : T.mint} strokeWidth={3.5}
              strokeDasharray={circT} strokeDashoffset={circT * (1 - timerPctT)}
              strokeLinecap="round" transform="rotate(-90 24 24)" style={{transition:'stroke-dashoffset 0.1s, stroke 0.3s'}}/>
            <text x={24} y={25} textAnchor="middle" fontFamily={T.font} fontWeight={900} fontSize={15} fill={timeLeft <= 5 ? T.coral : T.ink}>{timeLeft}</text>
            <text x={24} y={34} textAnchor="middle" fontFamily={T.font} fontWeight={800} fontSize={7} fill={T.inkSoft}>mp</text>
          </svg>
""",
"""""",
'Ritmus gyuru kivetele')

sub1(
"""              <span style={{ fontFamily:T.font, fontWeight:800, fontSize:8, color:T.inkSoft, letterSpacing:1.2, marginTop:2 }}>PONT</span>
            </div>
          </div>
        </div>
        {/* FIX: entire cell is a <button> for full touch area */}""",
"""              <span style={{ fontFamily:T.font, fontWeight:800, fontSize:8, color:T.inkSoft, letterSpacing:1.2, marginTop:2 }}>PONT</span>
            </div>
          </div>
        </div>
        {/* ⚠️ A KOZOS visszaszamlalo a SOR ALATT all, nem benne: a 30 px-es sav
            teljes szelessegu, es a haromelemu sorban (jatekos | ora | pont)
            osszenyomta volna a ket pirulat. */}
        <BohTimer variant="bar" total={DURATION} left={timeLeft} />
        {/* FIX: entire cell is a <button> for full touch area */}""",
'Ritmus sav a sor alatt')

sub1("""    const rT = 20, circT = 2 * Math.PI * rT;\n""", "", 'Ritmus circT')
sub1("""    const timerPctT = timeLeft / DURATION;\n""", "", 'Ritmus timerPctT')

# ── 3. TABU ─────────────────────────────────────────────────────────────────
sub1(
"""      <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:12 }}>
        <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:2, flexShrink:0 }}>
          <svg width={84} height={84} viewBox="0 0 54 54">
            <circle cx={27} cy={27} r={r} fill="none" stroke={T.inkMute+'33'} strokeWidth={4}/>
            <circle cx={27} cy={27} r={r} fill="none" stroke={timeLeft<=5?T.coral:T.blue} strokeWidth={4}
              strokeDasharray={circ} strokeDashoffset={circ*(1-timerPct)}
              strokeLinecap="round" transform="rotate(-90 27 27)" style={{transition:'stroke-dashoffset .1s linear'}}/>
            <text x={27} y={33} textAnchor="middle" fontFamily={T.font} fontWeight={900} fontSize={19} fill={timeLeft<=5?T.coral:T.ink}>{phase==='done'?'⏰':timeLeft}</text>
          </svg>
          <span style={{ fontFamily:T.font, fontWeight:800, fontSize:12, color:T.inkSoft }}>
            {phase==='done' ? 'Idő lejárt!' : 'másodperc'}
          </span>
        </div>
      </div>""",
"""      {/* A KOZOS visszaszamlalo (v10.329). A „másodperc" felirat kikerult: a
          sav maga irja ki a mertekegyseget („12 mp / 30 mp"). */}
      <BohTimer variant="bar" total={TOTAL} left={phase === 'done' ? 0 : timeLeft} />""",
'Tabu idozito')

sub1("""  const timerPct = timeLeft / TOTAL;\n""", "", 'Tabu timerPct')

sub1("const APP_VERSION = 'v10.357';", "const APP_VERSION = 'v10.358';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_358 alkalmazva')
