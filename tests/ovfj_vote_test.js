// v10.183 — Ország-Város szavazó sor: pipa/X gombok, a kereső a szó bal oldalán
//
// Ket dolog dolhet el csendben:
//   1) a kereso visszacsuszik a ket ertekelo gomb melle — pont az a mellenyulas,
//      ami miatt atrendeztuk (a szavazat azonnal el is megy);
//   2) az ikonok "atrajzolasa" csak a fejlecben tortenik meg, a gombokon marad
//      a rendszer-emoji.
// Ezert a tenyleges GEOMETRIAT merjuk (mi all mitol balra), nem a forrast.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const stub = fs.readFileSync(__dirname + '/fbstub.js', 'utf8');
const BASE = 'file:///home/user/bottle-of-heroes/index.html';
const SRC = '/home/user/bottle-of-heroes/app.src.html';

const PLAYERS = [
  { id:'a', name:'Anna',  color:'#5BA0DB' },
  { id:'b', name:'Béla',  color:'#E07A5F' },
  { id:'c', name:'Cili',  color:'#A78BFA' },
];
// 'A' betus kor. Anna es Cili ervenyes valaszt irt, Bela rosszat (nem A-val kezd).
// A valasz-rekord lapos: { round, orszag, varos, ... }
const ANSWERS = {
  a: { round:1, orszag:'Ausztria', varos:'Amszterdam' },
  b: { round:1, orszag:'Belgium',  varos:'Athén' },   // rossz betu — nem szavazhato
  c: { round:1, orszag:'Albánia',  varos:'' },
};

(async () => {
  let fail = 0;
  const ok = (l, c, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 390, height: 1200 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`
    try { localStorage.setItem('boh_onboarded','1'); } catch(e){}
    ['profiles','stats','game_stats','statEvents','gameStatEvents','seasons','usage','config']
      .forEach(k => window.__fbStore[k] = {});
  `);
  await p.goto(BASE, { waitUntil: 'domcontentloaded', timeout: 90000 });
  await p.waitForTimeout(3600);

  // A szavazo nezet kozvetlenul — a hoszt es a vendeg is EZT rendereli.
  await p.evaluate(([players, answers]) => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const root = document.createElement('div'); root.id = '__v';
    root.style.cssText = 'position:fixed;inset:0;z-index:1;background:var(--app-bg);overflow:auto;padding:12px';
    document.body.appendChild(root);
    function H() {
      const [votes, setVotes] = React.useState({});
      window.__votes = votes;
      return React.createElement(OVFJVotingView, {
        letter: 'A', round: 1, players, answers, myPid: 'a', myVotes: votes,
        tallies: { [ovfjVoteKey(1, 'c', 'orszag')]: { yes: 2, no: 0 } },
        onVote: (pid, cat, yes) => setVotes(v => Object.assign({}, v, { [ovfjVoteKey(1, pid, cat)]: yes })),
      });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
  }, [PLAYERS, ANSWERS]);
  await p.waitForTimeout(1200);

  // ─── 1) Nincs tobb rendszer-emoji a soron ───
  console.log('\n===== SAJÁT RAJZ, NEM EMOJI =====');
  {
    const txt = await p.evaluate(() => document.querySelector('#__v').innerText);
    const found = ['👍','👎','🔍'].filter(e => txt.includes(e));
    ok('a szavazó nézetben nincs rendszer-emoji', found.length === 0,
       found.length ? 'maradt: ' + found.join(' ') : 'egy sem');
    const svgs = await p.evaluate(() => document.querySelectorAll('#__v button svg').length);
    ok('a gombokon rajzolt ikon van', svgs >= 4, svgs + ' SVG a gombokon');
  }

  // ─── 2) A kereso a szo BAL oldalan all ───
  // Ez a valtoztatas lenyege: korabban a ket ertekelo gomb koze volt szorulva.
  console.log('\n===== A KERESŐ HELYE =====');
  {
    // Az a sor kell, ahol EGYUTT van kereso es ertekelo gomb — a sajat sorodon
    // csak kereso van, azon nem latszana a szetvalasztas.
    const geo = await p.evaluate(() => {
      const row = [...document.querySelectorAll('#__v div')]
        .filter(d => d.querySelector('a[href*="google.com/search"]') && d.querySelector('button'))
        .sort((a, b) => a.textContent.length - b.textContent.length)[0];
      if (!row) return null;
      const l = row.querySelector('a[href*="google.com/search"]');
      const word = [...row.querySelectorAll('span')].find(s => getComputedStyle(s).flexGrow === '1');
      const btns = [...row.querySelectorAll('button')];
      const x = e => e.getBoundingClientRect().left;
      return {
        word: word && word.textContent,
        search: x(l),
        wordX: word ? x(word) : null,
        btns: btns.map(x),
        gapToFirstBtn: btns.length ? Math.round(x(btns[0]) - l.getBoundingClientRect().right) : null,
      };
    });
    ok('van kereső link a soron', geo !== null);
    ok('a kereső a szótól balra van', geo && geo.search < geo.wordX,
       geo && `kereső x=${Math.round(geo.search)} · „${geo.word}" x=${Math.round(geo.wordX)}`);
    ok('a szó és az értékelő gombok is a keresőtől jobbra vannak',
       geo && geo.btns.every(x => x > geo.search), geo && geo.btns.map(Math.round).join(', '));
    // A tavolsag a lenyeg: emiatt nyultak mellé.
    ok('a kereső és az első értékelő gomb között van hely', geo && geo.gapToFirstBtn > 40,
       geo && geo.gapToFirstBtn + 'px');
  }

  // ─── 3) A szavak egy oszlopban allnak ───
  // A kereso helye akkor is megmarad, ha nincs mit keresni — kulonben a sajat
  // sorod szava beljebb csuszna, mint a tobbieke.
  console.log('\n===== A SZAVAK OSZLOPA =====');
  {
    const lefts = await p.evaluate(() => {
      const card = [...document.querySelectorAll('#__v div')]
        .find(d => d.textContent.includes('Ausztria') && d.textContent.includes('Ország'));
      return [...card.querySelectorAll('span')]
        .filter(s => /^(Ausztria|Belgium|Albánia)$/.test(s.textContent.trim()))
        .map(s => Math.round(s.getBoundingClientRect().left));
    });
    ok('mindhárom szó ugyanott kezdődik', lefts.length === 3 && new Set(lefts).size === 1,
       lefts.join(', '));
  }

  // ─── 4) A gombok tenyleg szavaznak, es latszik a valasztas ───
  console.log('\n===== A SZAVAZÁS =====');
  {
    const before = await p.evaluate(() => {
      const btn = document.querySelectorAll('#__v button')[0];
      return getComputedStyle(btn).backgroundColor;
    });
    await p.evaluate(() => document.querySelectorAll('#__v button')[0].click());
    await p.waitForTimeout(400);
    const after = await p.evaluate(() => {
      const btn = document.querySelectorAll('#__v button')[0];
      return { bg: getComputedStyle(btn).backgroundColor,
               ink: getComputedStyle(btn.querySelector('svg')).stroke };
    });
    const v = await p.evaluate(() => window.__votes);
    ok('a pipa gomb elfogadásra szavaz', Object.values(v)[0] === true, JSON.stringify(v));
    ok('a választás látszik is a gombon', after.bg !== before && after.bg !== 'rgba(0, 0, 0, 0)',
       `${before} → ${after.bg}`);
    ok('a kijelölt gombon fehér a rajz', after.ink === 'rgb(255, 255, 255)', after.ink);

    // az X ugyanabban a sorban a masik iranyba szavaz
    await p.evaluate(() => document.querySelectorAll('#__v button')[1].click());
    await p.waitForTimeout(400);
    const v2 = await p.evaluate(() => window.__votes);
    ok('az X elutasításra szavaz', Object.values(v2)[0] === false, JSON.stringify(v2));
  }

  // ─── 5) EGY forras ───
  // A hoszt es a vendeg ugyanazt a komponenst rendereli — ha ez ketté válna,
  // az egyik oldalon a regi soron maradna.
  console.log('\n===== EGY FORRÁS =====');
  {
    const src = fs.readFileSync(SRC, 'utf8');
    ok('a host és a vendég ugyanazt a nézetet használja',
       (src.match(/<OVFJVotingView/g) || []).length === 2,
       (src.match(/<OVFJVotingView/g) || []).length + ' hivatkozás');
    ok('a szavazó nézetben nincs több emoji a forrásban sem',
       !/Szavazás 👍👎/.test(src));
  }

  ok('nincs JS hiba', errs.filter(e => !/ServiceWorker/.test(e)).length === 0, errs.join(' | '));
  await p.close();
  await b.close();
  console.log('\n' + (fail === 0 ? '✅ MINDEN ELLENORZES RENDBEN' : '❌ ' + fail + ' ELLENORZES BUKOTT'));
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
