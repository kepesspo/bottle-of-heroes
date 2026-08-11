# v10.333 — Fordított kör: a LEGACY result-alak csendben kimaradt a cserébol
#
# A tunet: Collect & Boom-ban a „Fordított kör" wildcard alatt a KONYVELES
# megfordult (a bombas kapott pontot, a tobbiek ittak), a BANNER viszont a regi
# allast mutatta („Sere csapta fel a bombát! · ISZIK"). Ket kulon allitas ugyanarrol
# a korrol.
#
# Az ok: a PlayScreen onResult-jaban a csere kapuja a `winners`/`losers` tombre
# szurt. A regi (legacy) alak — `{correct, playerName, drinks, subtitle}` — egyiket
# sem viszi, tehat a feltetel hamis volt, es a banner valtozatlanul ment tovabb.
# A konyveles (advance / advancePaired / advanceTeam / advanceLoverseny) MIND
# kezeli a reverse-t, ezert csuszott szet a ketto.
#
# Ez NEM egy jatek hibaja: 34 hivasi hely (~15 jatek) hasznalja a legacy alakot,
# es mind ugyanigy kimaradt.
import io, re

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, f'{what}: {src.count(old)} talalat'
    src = src.replace(old, new)

# ── 1. a kapu: a legacy alakot ELOSZOR normalizaljuk ───────────────────────────
OLD_GATE = """    if (wcEffect === 'reverse' && !res.penalty && ((res.winners||[]).length || (res.losers||[]).length)) {
      const swappedDrinks = (res.drinks ?? 0) || ((res.winners||[]).length ? 1 : 0);
      r = { ...res, winners: res.losers || [], losers: res.winners || [], drinks: swappedDrinks, winNote: '+1 pont', loseNote: '', subtitle: null, correct: undefined };
    }"""
NEW_GATE = """    if (wcEffect === 'reverse' && !res.penalty) {
      // A LEGACY alak (`correct` + `playerName`) nem visz winners/losers tombot.
      // Amig a kapu csak a tombre szurt, 34 hivasi hely (~15 jatek) CSENDBEN
      // kimaradt a cserebol: a konyveles megfordult, a banner nem. Ezert eloszor
      // ugyanugy normalizaljuk, ahogy a banner is teszi renderelesnel.
      let w = res.winners, l = res.losers;
      if (!w && !l && res.playerName) {
        const rp = players.find(p => p.name === res.playerName);
        if (rp) { w = res.correct ? [rp] : []; l = res.correct ? [] : [rp]; }
      }
      if ((w||[]).length || (l||[]).length) {
        const swappedDrinks = (res.drinks ?? 0) || ((w||[]).length ? 1 : 0);
        r = { ...res, winners: l || [], losers: w || [], drinks: swappedDrinks, winNote: '+1 pont', loseNote: '', subtitle: null, correct: undefined };
      }
    }"""
sub1(OLD_GATE, NEW_GATE, 'reverse kapu')

# ── 2. Collect & Boom: teljes alak, es a helyes sorrend ────────────────────────
# A legacy alak itt CSAK a bombast nevezte meg — a tobbiek pontja sehol nem
# latszott, fordított körben pedig eppen ok isznak. Az `onAdvance` ugyanezt a ket
# csoportot mar eddig is kiosztotta, tehat a banner csak utana megy.
#
# A sorrend is javul: `onResult` ELOBB, mint az `onAdvance` (CLAUDE.md v10.318) —
# az advance gameIdx-et valthat, a `useEffect([gameIdx])` pedig setGameResult(null)-t
# hiv, tehat a banner kitorlodhet, mielott megjelenne.
OLD_CB = """    const pm = {};
    players.forEach(p => { if (p.id !== bombPid) pm[p.id] = 1; });
    onAdvance && onAdvance(dm, pm);
    const loserPlayer = players.find(p=>p.id===bombPid);
    onResult && onResult({ correct: false, playerName: loserPlayer?.name, drinks, subtitle: `${loserPlayer?.name} csapta fel a bombát!` });"""
NEW_CB = """    const pm = {};
    players.forEach(p => { if (p.id !== bombPid) pm[p.id] = 1; });
    const loserPlayer = players.find(p=>p.id===bombPid);
    onResult && onResult({ winners: players.filter(p => p.id !== bombPid), losers: [loserPlayer].filter(Boolean),
                           drinks, winNote: '+1 pont', loseNote: `${loserPlayer?.name} csapta fel a bombát!` });
    onAdvance && onAdvance(dm, pm);"""
sub1(OLD_CB, NEW_CB, 'Collect & Boom eredmeny')

# ── 3. verziobump ─────────────────────────────────────────────────────────────
sub1("const APP_VERSION = 'v10.332';", "const APP_VERSION = 'v10.333';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK — patch_10_333 alkalmazva')
