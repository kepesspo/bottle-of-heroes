# v10.171 — az egyedul futo jatekok kezelese
#
# Hat jatek "egyedul" megy: busz, beerpong, powerhour, ovfj, farkasos,
# blackjack. Eddig SEMMILYEN kulon kezelesuk nem volt — minden beallitas rajuk
# is futott. Ket kulonbozo baj:
#
#  1) A Jatekmenet oldalon a jateksorrend ertelmetlen (egy jatek van), a max
#     korok pedig karos (lasd 2.). A nehezseg es a modok viszont HATNAK, azok
#     maradnak — azok elrejtese valodi kontrollt venne el.
#
#  2) A korlimit ezeknel a jatekoknal a MENET KOZEPEN vagta el a bulit. A Busz
#     ot belso lepesbol all, es mindegyik noveli a korszamlalot; 10 korre
#     allitott limitnel a Busz felbeszakadt volna es jott az Eredmeny kepernyo.
#     Ez a Jatekmenet oldaltol fuggetlenul is hiba volt.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# ── egy forras arrol, mely jatekok futnak egyedul ──
anchor = "// Melyik jateknak van sajat beallito lapja."
assert s.count(anchor) == 1
s = s.replace(anchor, """// Ezek a jatekok egyedul futnak: nem valaszthato melleuk masik. Sajat belso
// lepesekbol allnak, ezert a korlimit es a Jatekmenet oldal is ebbol dolgozik.
//
// MEGJEGYZES: a GamesScreen isLocked() NEM ebbol dolgozik, mert ott a busz es a
// beerpong szabalya aszimmetrikus a masik negyhez kepest (oket akkor sem lehet
// felvenni, ha mar van kivalasztott jatek — a masik negyet igen). Azt a
// viselkedest most nem valtoztatjuk meg.
const SOLO_GAME_IDS = ['busz', 'beerpong', 'powerhour', 'ovfj', 'farkasos', 'blackjack'];
const isSoloGame = (id) => SOLO_GAME_IDS.indexOf(id) !== -1;

""" + anchor)

# ── 1) korlimit: ne vagja el a magaban futo jatekot ──
old_cap = """      const maxRounds = gameMeta?.maxRounds || null;
      if (maxRounds && newRound > maxRounds) {"""
assert s.count(old_cap) == 1
s = s.replace(old_cap, """      const maxRounds = gameMeta?.maxRounds || null;
      // A magukban futo jatekok sajat belso lepesekbol allnak, es azok is
      // noveli a korszamlalot — a korlimit igy a MENET KOZEPEN zarna le a bulit
      // (pl. Busz 10 korre allitott limitnel). Rajuk a limit nem vonatkozik.
      if (maxRounds && newRound > maxRounds && !isSoloGame(currentGameId)) {""")

# ── 2) a Jatekmenet oldal ──
old_sec = """        {/* A "Játékmenet" felirat itt nem kell — a fejlécben már ott van. */}
        <div style={{ ...cardStyle, marginTop:12, padding:'14px 16px' }}>
          <GameSettingsContent meta={gameMeta} setMeta={setGameMeta} group={['difficulty', 'order', 'maxRounds']} />
        </div>
"""
assert s.count(old_sec) == 1
s = s.replace(old_sec, """        {/* A "Játékmenet" felirat itt nem kell — a fejlécben már ott van. */}
        {/* Egyedül futó játéknál a játéksorrend értelmetlen (egy játék van), a
            max körök pedig félbevágná a menetet — mindkettő kimarad. */}
        <div style={{ ...cardStyle, marginTop:12, padding:'14px 16px' }}>
          <GameSettingsContent meta={gameMeta} setMeta={setGameMeta}
            group={soloGame ? ['difficulty'] : ['difficulty', 'order', 'maxRounds']} />
        </div>
""")

# a solo jatek felismerese
old_calc = "  const minutes = Math.max(5, Math.round((selectedGames || []).length * 2.5 / 5) * 5);"
assert s.count(old_calc) == 1
s = s.replace(old_calc, old_calc + """
  // Pontosan egy, magaban futo jatek — ilyenkor mas a kepernyo sulypontja.
  const soloGame = games.length === 1 && isSoloGame(games[0].id) ? games[0] : null;""")

# osszegzo: egy jateknal a NEVE informativabb, mint az "1"
old_sum = """            { v: games.length,          l: 'játék' },"""
assert s.count(old_sum) == 1
s = s.replace(old_sum, """            soloGame ? { v: tg(soloGame, 'name'), l: 'játék', small: true }
                     : { v: games.length, l: 'játék' },""")
old_val = """              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:T.ink, lineHeight:1 }}>{x.v}</div>"""
assert s.count(old_val) == 1
s = s.replace(old_val, """              <div style={{ fontFamily:T.font, fontWeight:900, fontSize: x.small ? 14 : 22, color:T.ink,
                lineHeight: x.small ? 1.2 : 1, paddingTop: x.small ? 4 : 0 }}>{x.v}</div>""")

# wildcard figyelmeztetes a Modok doboz utan
old_tail = """        {[['modes'], ['other']].map((grp, i) => (
          <div key={i} style={{ ...cardStyle, marginTop:12, padding:'14px 16px' }}>
            <GameSettingsContent meta={gameMeta} setMeta={setGameMeta} group={grp} />
          </div>
        ))}"""
assert s.count(old_tail) == 1
s = s.replace(old_tail, """        {[['modes'], ['other']].map((grp, i) => (
          <React.Fragment key={i}>
            <div style={{ ...cardStyle, marginTop:12, padding:'14px 16px' }}>
              <GameSettingsContent meta={gameMeta} setMeta={setGameMeta} group={grp} />
            </div>
            {/* A wildcard kör a menet közepébe is beugrik — egyetlen hosszú
                játéknál ez meglepetés, ezért itt kimondjuk. */}
            {grp[0] === 'modes' && soloGame && (gameMeta?.modes || []).includes('wildcard') && (
              <div style={{ marginTop:8, padding:'10px 13px', borderRadius:12,
                background:`${T.yellow}22`, borderLeft:`3px solid ${T.yellow}`,
                fontFamily:T.font, fontSize:12, color:T.inkSoft, lineHeight:1.55 }}>
                A wildcard kör a <strong style={{ color:T.ink }}>{tg(soloGame, 'name')}</strong> közben is beugrik,
                nem csak játékok között.
              </div>
            )}
          </React.Fragment>
        ))}""")

s = s.replace("const APP_VERSION = 'v10.170';", "const APP_VERSION = 'v10.171';", 1)
assert "v10.171" in s and s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK')
