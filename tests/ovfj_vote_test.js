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
        onVote: (pid, cat, yes, idx) => setVotes(v => Object.assign({}, v, { [ovfjVoteKey(1, pid, cat, idx || 0)]: yes })),
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

  // ─── 4b) TOBB SZO: mindegyik KULON ertekelheto (v10.303) ───
  // A hiba: a `hostVote`/`submitVote` index NELKUL kepezte a kulcsot, ezert
  // barmelyik szo gombja a 0. szo kulcsara irt. A pontszamitas viszont
  // index-szerint olvas, tehat a 2.+ szavakra "senki nem szavazott" allt, es
  // azok automatikusan elfogadottak lettek.
  console.log('\n===== TÖBB SZÓ: MINDEGYIK KÜLÖN ÉRTÉKELHETŐ =====');
  {
    await p.evaluate(() => {
      const old = document.getElementById('__v'); if (old) old.remove();
      const root = document.createElement('div'); root.id = '__v';
      root.style.cssText = 'position:fixed;inset:0;z-index:1;background:var(--app-bg);overflow:auto;padding:12px';
      document.body.appendChild(root);
      const players = [{ id:'a', name:'Anna', color:'#5BA0DB' }, { id:'c', name:'Cili', color:'#A78BFA' }];
      const answers = { a:{ round:1, orszag:'Ausztria' },
                        c:{ round:1, orszag:'Albánia, Ausztrália, Andorra' } };
      function H() {
        const [votes, setVotes] = React.useState({});
        window.__votes2 = votes;
        return React.createElement(OVFJVotingView, {
          letter:'A', round:1, players, answers, myPid:'a', myVotes:votes, limit:3, tallies:null,
          onVote: (pid, cat, yes, idx) => setVotes(v => Object.assign({}, v, { [ovfjVoteKey(1, pid, cat, idx || 0)]: yes })),
        });
      }
      ReactDOM.createRoot(root).render(React.createElement(H));
    });
    await p.waitForTimeout(900);

    const sorok = await p.evaluate(() => {
      const out = [];
      [...document.querySelectorAll('#__v div')].forEach(d => {
        const sp = [...d.children].filter(x => x.tagName === 'SPAN');
        const w = sp.map(x => (x.innerText || '').trim());
        const hit = ['Albánia','Ausztrália','Andorra'].find(x => w.includes(x));
        if (hit && d.querySelectorAll('button').length === 2) out.push(hit);
      });
      return out;
    });
    ok('mindhárom szónak SAJÁT értékelő gombpárja van',
       sorok.length === 3, sorok.join(', ') || 'egy sem');

    // a MASODIK szo pipajara kattintunk
    const klikk = await p.evaluate(() => {
      const sor = [...document.querySelectorAll('#__v div')].find(d =>
        [...d.children].some(x => x.tagName === 'SPAN' && (x.innerText || '').trim() === 'Ausztrália')
        && d.querySelectorAll('button').length === 2);
      if (!sor) return false;
      sor.querySelector('button[aria-label="Elfogadom"]').click();
      return true;
    });
    await p.waitForTimeout(400);
    const v = await p.evaluate(() => window.__votes2);
    ok('megtaláltuk a második szó sorát', klikk);
    ok('a szavazat a MÁSODIK szó kulcsára ment (nem az elsőére)',
       JSON.stringify(v) === JSON.stringify({ 'r1_c_orszag_1': true }), JSON.stringify(v));

    // es a masodik szo gombja jelolve is van, az elsoe nem
    const jelolt = await p.evaluate(() => {
      const out = {};
      ['Albánia','Ausztrália','Andorra'].forEach(w => {
        const sor = [...document.querySelectorAll('#__v div')].find(d =>
          [...d.children].some(x => x.tagName === 'SPAN' && (x.innerText || '').trim() === w)
          && d.querySelectorAll('button').length === 2);
        const btn = sor && sor.querySelector('button[aria-label="Elfogadom"]');
        out[w] = btn ? getComputedStyle(btn).backgroundColor : null;
      });
      return out;
    });
    ok('csak a második szó gombja jelölt — az elsőé érintetlen',
       jelolt['Ausztrália'] === 'rgb(79, 194, 160)' && jelolt['Albánia'] === 'rgba(0, 0, 0, 0)',
       JSON.stringify(jelolt));
  }

  // ─── 4c) BETUPAROK: ahol ket kezdet is jo (v10.303 digraf, v10.304 ekezet) ───
  // A szabaly EGY iranyu: a RITKABB betu fogadja el a gyakoribbat, forditva nem.
  // Enelkul az egyjegyu/rovid kor beleolvadna a ketjegyube/hosszuba, es a ket
  // kor ugyanaz lenne. A cimke ugyanezt mondja ki ("N / NY", "O / Ó").
  console.log('\n===== BETŰPÁROK =====');
  {
    const eset = await p.evaluate(() => {
      const t = [
        // ketjegyu huzott betu: az egyjegyu kezdet is jo
        ['nyár','NY',true],  ['nap','NY',true],   ['sas','NY',false],
        ['szék','SZ',true],  ['sas','SZ',true],
        // ...de egyjegyunel a digraf NEM
        ['nyár','N',false],  ['nap','N',true],
        ['szék','S',false],  ['sas','S',true],
        // ekezetes betu: az EGGYEL egyszerubb alak is jo (v10.304-305)
        ['óra','Ó',true],    ['ország','Ó',true], ['alma','Ó',false],
        ['ágy','Á',true],    ['alma','Á',true],
        ['ötlet','Ö',true],  ['orr','Ö',true],    // ö -> o
        ['üveg','Ü',true],   ['utca','Ü',true],   // ü -> u
        ['őz','Ő',true],     ['ötlet','Ő',true],  // ő -> ö
        ['űr','Ű',true],     ['üveg','Ű',true],   // ű -> ü
        // ...de a lanc EGY lepeses: Ő alatt az "orr" NEM er
        ['orr','Ő',false],   ['utca','Ű',false],
        // ...es visszafele semmi nem all
        ['óra','O',false],   ['orr','O',true],
        ['ötlet','O',false], ['őz','Ö',false],
        ['üveg','U',false],  ['utca','U',true],
        ['űr','Ü',false],
        ['ágy','A',false],   ['alma','A',true],
      ];
      return t.filter(([w,l,exp]) => ovfjLetterOk(w,l) !== exp).map(([w,l,exp]) => l+'+'+w+' várt:'+exp);
    });
    ok('minden betűpár-eset stimmel', eset.length === 0, eset.join(' | ') || '29 eset rendben');
    const cimke = await p.evaluate(() =>
      ['NY','LY','Ó','Ö','Ő','Ú','Ü','Ű','Á','A','O','U'].map(l => l+'→'+ovfjLetterPair(l)).join(' '));
    ok('a címke mindkét kezdetet kiírja, ahol kettő is jó',
       /NY→N \/ NY/.test(cimke) && /Ó→O \/ Ó/.test(cimke) && /Ö→O \/ Ö/.test(cimke)
       && /Ő→Ö \/ Ő/.test(cimke) && /Ü→U \/ Ü/.test(cimke) && /Ű→Ü \/ Ű/.test(cimke)
       && /A→A /.test(cimke) && /O→O /.test(cimke) && /U→U$/.test(cimke), cimke);
  }

  // ─── 5) EGY forras ───
  // A hoszt es a vendeg ugyanazt a komponenst rendereli — ha ez ketté válna,
  // az egyik oldalon a regi soron maradna.
  console.log('\n===== EGY FORRÁS =====');
  {
    const src = fs.readFileSync(SRC, 'utf8');
    // A lenyeg, hogy EGY definicio legyen — a hivatkozasok szama nott (v10.303
    // ota a host kor vegi "Mit irtak?" panelje is ezt rendereli `readOnly`-val),
    // de attol meg ugyanaz a komponens szolgalja ki mindharom helyet.
    ok('egyetlen szavazó-nézet komponens létezik',
       (src.match(/function OVFJVotingView/g) || []).length === 1,
       (src.match(/function OVFJVotingView/g) || []).length + ' definíció');
    ok('és a host, a vendég ÉS a visszanézés is azt rendereli (nincs másolat)',
       (src.match(/<OVFJVotingView/g) || []).length === 3,
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
