# v10.173 — Ország-Város: "Várjuk meg a kör végét"
#
# Eddig ha valaki keszen lett, a tobbieknek 10 mp maradt — akkor is, ha a
# korido meg boven tartott volna. Uj kapcsolo: hagyjuk lejarni a teljes koridot.
#
# Kozben a szamitas EGY helyre kerult: a hoszt es a vendeg oldala eddig kulon
# masolatban ugyanazt szamolta (56089-56091 es 56303-56305). Ket masolat, ket
# hely, ahol el lehet csuszni.
#
# "Idő nélkül" korido mellett a kapcsolo szandekosan nem valaszthato: ott a
# 10 mp az EGYETLEN lezaro mechanizmus, nelkule a kor sosem erne veget.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# ── 1) kozos szamitas ──
anchor = "// ═══════════════ ORSZÁG-VÁROS — közös segédek ═══════════════\nconst OVFJ_DRAW_MS = 4000;"
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + """
const OVFJ_GRACE_MS = 10000;
// Mennyi ido van meg az irasbol. EGY forras: a hoszt es a vendeg oldala eddig
// kulon masolatban szamolta ugyanezt.
//
// Alapbol az elso "kesz" utan 10 mp marad a tobbieknek. A waitFullTime
// kapcsoloval viszont a teljes korido lejar — ilyenkor a "kesz" csak azt
// jelenti, hogy az illeto mar nem ir tovabb.
//
// Ido nelkuli korideonel a 10 mp az EGYETLEN lezaro mechanizmus, ezert ott a
// kapcsolo nem szamit (a beallito lap nem is engedi bekapcsolni).
function ovfjRemaining({ phase, roundTime, writingStart, doneAt, waitFullTime }) {
  if (phase !== 'writing') return null;
  if (roundTime == null) {
    return doneAt ? Math.max(0, Math.ceil((doneAt + OVFJ_GRACE_MS - Date.now()) / 1000)) : null;
  }
  let deadline = (writingStart != null ? writingStart : Date.now()) + roundTime * 1000;
  if (doneAt && !waitFullTime) deadline = Math.min(deadline, doneAt + OVFJ_GRACE_MS);
  return Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
}""")

# ── 2) hoszt oldal ──
old_host = """  const remaining = (() => {
    if (phase !== 'writing') return null;
    if (roundTime == null) return doneAt ? Math.max(0, Math.ceil((doneAt + 10000 - Date.now()) / 1000)) : null;
    let deadline = (writingStart != null ? writingStart : Date.now()) + roundTime * 1000;
    if (doneAt) deadline = Math.min(deadline, doneAt + 10000);
    return Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
  })();"""
assert s.count(old_host) == 1
s = s.replace(old_host, """  const remaining = ovfjRemaining({ phase, roundTime, writingStart, doneAt, waitFullTime });""")

old_rt = "  const roundTime = gameMeta?.ovfjConfig?.roundTime === undefined ? 90 : gameMeta.ovfjConfig.roundTime;"
assert s.count(old_rt) == 1
s = s.replace(old_rt, old_rt + "\n  const waitFullTime = !!gameMeta?.ovfjConfig?.waitFullTime;")

# ── 3) vendeg oldal ──
old_obs = """  const remaining = (() => {
    if (ovfj.phase !== 'writing') return null;
    if (obsRoundTime == null) return ovfj.doneAt ? Math.max(0, Math.ceil((ovfj.doneAt + 10000 - Date.now()) / 1000)) : null;
    let deadline = (obsWritingStart != null ? obsWritingStart : Date.now()) + obsRoundTime * 1000;
    if (ovfj.doneAt) deadline = Math.min(deadline, ovfj.doneAt + 10000);
    return Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
  })();"""
assert s.count(old_obs) == 1
s = s.replace(old_obs, """  const remaining = ovfjRemaining({ phase: ovfj.phase, roundTime: obsRoundTime,
    writingStart: obsWritingStart, doneAt: ovfj.doneAt, waitFullTime: !!ovfj.waitFullTime });""")

# a vendeg csak akkor tudja, ha at is kuldjuk
old_sync = "    syncRoom(roomCode, { ovfjState: { sess, phase, round, totalRounds, roundTime, letter, drawTs, doneAt, hostPid, answers, roundScores, cumScores } });"
assert s.count(old_sync) == 1
s = s.replace(old_sync, "    syncRoom(roomCode, { ovfjState: { sess, phase, round, totalRounds, roundTime, waitFullTime, letter, drawTs, doneAt, hostPid, answers, roundScores, cumScores } });")

old_sync2 = "    syncRoom(roomCode, { ovfjTakenIds: [], ovfjState: { sess, phase:'pick', round:1, totalRounds, roundTime, letter:null, drawTs:null, doneAt:null, hostPid:null } });"
assert s.count(old_sync2) == 1
s = s.replace(old_sync2, "    syncRoom(roomCode, { ovfjTakenIds: [], ovfjState: { sess, phase:'pick', round:1, totalRounds, roundTime, waitFullTime, letter:null, drawTs:null, doneAt:null, hostPid:null } });")

# ── 4) a lobby leirasa igazodjon ──
old_desc = '''desc="Betűt sorsolunk, mindenki a saját telefonján tölti ki a 8 kategóriát. Az első kész után 10 mp marad, utána szavazás — minden érvényes szó 1 pont."'''
assert s.count(old_desc) == 1
s = s.replace(old_desc, '''desc={"Betűt sorsolunk, mindenki a saját telefonján tölti ki a 8 kategóriát. "
          + (waitFullTime && roundTime != null
              ? "A kör ideje mindig végig lejár, akkor is ha valaki hamarabb végez."
              : "Az első kész után 10 mp marad,")
          + " utána szavazás — minden érvényes szó 1 pont."}''')

assert s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — kozos szamitas + waitFullTime')
