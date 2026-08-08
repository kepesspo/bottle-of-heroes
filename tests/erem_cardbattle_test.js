// v10.326 — Éremdobás korty-száma és a Kártyacsata összehasonlító sora
//
// 1. ÉREMDOBÁS. A játék saját végképernyője bedrótozott „iszik 1-et"-et írt,
//    miközben az `onResult` ÉS a könyvelés is szoroz a nehézséggel — nehéz
//    szinten a banner 3-at mondott, a játék 1-et. Innentől a `drinkMult`
//    propból jön a szám, és a szöveg „N kortyot" (a magyar toldalék
//    számonként más: 1-et / 3-at / 5-öt, a „kortyot" viszont mindegyikkel jó).
//
// 2. KÁRTYACSATA. A kör-sor egyetlen chipben az ÖSSZEGET mutatta: aki két
//    lapot rakott egy körre, annál a 3+4-ből „7" lett — egy nem létező lap.
//    Mostantól minden lerakott lap külön chip, és az összeg pirulában áll
//    mellettük.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const PL = [{ id:'a', name:'Sere', color:'#E07A5F', points:0, drinks:0 },
            { id:'b', name:'Kecsi', color:'#4FC2A0', points:0, drinks:0 },
            { id:'c', name:'Vivi', color:'#A78BFA', points:0, drinks:0 }];

async function page(b) {
  const p = await b.newPage({ viewport: { width: 402, height: 900 } });
  p.__errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  return p;
}

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── 1. ÉREM ──
  // Mindharom szinten: amit a jatek vegkepernyoje kiir, egyezzen azzal, amennyi
  // ténylegesen a jatekosra kerul (a PlayScreen konyvelese szoroz).
  console.log('\n===== 1. EREMDOBAS =====');
  for (const [diff, mult] of [['easy', 1], ['hard', 3], ['extreme', 5]]) {
    const p = await page(b);
    await p.evaluate(({ pl, diff }) => {
      const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
      const root = document.createElement('div'); root.id = '__p';
      root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column;overflow:auto';
      document.body.appendChild(root);
      function H() {
        const [ps, setPs] = React.useState(pl);
        window.__players = ps;
        return React.createElement(PlayScreen, {
          go: () => {}, players: ps, setPlayers: setPs, selectedGames: ['erem'],
          roomCode: null, gameMeta: { modes: [], difficulty: diff }, setGameMeta: () => {},
          setScoreHistory: () => {}, setLastGameRound: () => {},
        });
      }
      ReactDOM.createRoot(root).render(React.createElement(H));
    }, { pl: PL, diff });
    await p.waitForTimeout(2000);
    // FEJ-re kattintunk; a dobas kimenetele veletlen, de a KIIRT szam
    // mindketto agon ugyanaz (1 x mult), es a konyveles is ugyanannyi.
    await p.evaluate(() => {
      const x = [...document.querySelectorAll('#__p button')].find(y => /FEJ/.test(y.innerText || ''));
      if (x) x.click();
    });
    await p.waitForTimeout(4200);
    const txt = await p.evaluate(() => document.getElementById('__p').innerText);
    const m = txt.match(/iszik (\d+) kortyot/);
    ok(!!m, `[${diff}] a végképernyő kiírja a korty-számot`, (txt.match(/iszik[^\n]*/) || ['-'])[0]);
    ok(m && Number(m[1]) === mult, `[${diff}] a kiírt szám = 1 × ${mult}`, m && m[1]);
    // ES a RESULT BANNER ugyanezt mondja — pont ez volt a panasz: a ketto
    // nem egyezett. A banner a jatek kartyajan KIVUL renderel, ezert a teljes
    // oldal szovegebol vonjuk ki a jatek sajat blokkjat.
    // A banner „ISZIK <nev> <N> KORTY" alakban all — ez a szam volt az, ami
    // nem egyezett a jatek sajat vegkepernyojevel.
    const all = await p.evaluate(() => document.body.innerText);
    const bm = all.match(/(\d+)\s*\n\s*KORTY/);
    ok(!!bm, `[${diff}] a result banner kiírja a korty-számot`,
       (all.match(/ISZIK[\s\S]{0,40}KORTY/) || ['-'])[0].replace(/\n/g, ' '));
    ok(bm && Number(bm[1]) === mult, `[${diff}] a banner és a játék UGYANAZT mondja`,
       'jatek=' + (m && m[1]) + ' banner=' + (bm && bm[1]));
    ok(p.__errs.length === 0, `[${diff}] nincs JS hiba`, p.__errs.join(' | '));
    await p.close();
  }

  // ── 2. KÁRTYACSATA ──
  console.log('\n===== 2. KARTYACSATA =====');
  const p = await page(b);
  await p.evaluate((pl) => {
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column;overflow:auto';
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(CardBattleGame, {
      gameIdx: 0, challenger: pl[0], opponent: pl[1],
      onAdvance: () => {}, onResult: () => {}, onSetHideFooter: () => {}, gameMeta: {},
    }));
  }, PL);
  await p.waitForTimeout(1200);
  // A kez lapjai ES a kor-sorok DIV-ek `onclick`-kel, nem <button>-ok —
  // ezert az `[...].filter(x => x.onclick)` a fogodzo. MIND az ot lapot az
  // 1. korre tesszuk: igy all elo pontosan az az eset, ami korabban egyetlen
  // osszeg-chippé olvadt.
  const planAllToRound1 = async () => {
    for (let k = 0; k < 5; k++) {
      const picked = await p.evaluate(() => {
        const el = [...document.querySelectorAll('#__p *')]
          .filter(x => x.onclick && /^([34567])\n\1\n[♠♥♦♣]$/.test((x.innerText || '').trim()))[0];
        if (!el) return false;
        el.click(); return true;
      });
      if (!picked) break;
      await p.waitForTimeout(180);
      await p.evaluate(() => {
        const row = [...document.querySelectorAll('#__p *')]
          .filter(x => x.onclick && /^1\n1\. kör/.test(x.innerText || ''))[0];
        if (row) row.click();
      });
      await p.waitForTimeout(180);
    }
  };
  // A tovabb-gomb felirata fazisonkent mas („Kész" / „Kecsi készen áll"),
  // ezert az UTOLSO gombra kattintunk — az mindharom lapon a tovabblepes.
  const lastBtn = async () => {
    await p.evaluate(() => {
      const x = [...document.querySelectorAll('#__p button')].filter(y => (y.innerText || '').trim());
      if (x.length) x[x.length - 1].click();
    });
    await p.waitForTimeout(800);
  };
  await planAllToRound1();          // 1. jatekos: mind az ot lap az 1. korre
  await lastBtn();                  // Kész
  await lastBtn();                  // atadas
  await planAllToRound1();          // 2. jatekos: ugyanoda
  await lastBtn();                  // Kész → reveal
  await p.waitForTimeout(5200);     // a reveal soronkent animal

  // A kor-soron minden lerakott lap sajat 30 px-es chip. Tiz lap (5+5) es
  // ket osszeg-pirula — a REGI valtozat oldalankent EGY chipet rajzolt „25"-tel.
  const rev = await p.evaluate(() => {
    const chips = [...document.querySelectorAll('#__p div')]
      // egy chip tartalma az ERTEK + a SZINJEL („3♠") — a kor sorszamat viselo
      // cellak (1..5) igy nem szamitanak bele
      .filter(d => /^[34567][♠♥♦♣]$/.test((d.textContent || '').replace(/\s/g, '')));
    const sums = [...document.querySelectorAll('#__p span')]
      .filter(x => /^=\d+$/.test((x.textContent || '').trim())).map(x => x.textContent.trim());
    const txt = document.getElementById('__p').innerText;
    return { chips: chips.length, sums, hasBig: /(^|\n)25(\n|$)/.test(txt) };
  });
  ok(rev.chips === 10, 'mind a tíz lerakott lap külön chipben látszik (5 + 5)', rev.chips);
  ok(rev.sums.length === 2 && rev.sums.every(x => x === '=25'),
     'az összeg pirulában áll mellettük (3+4+5+6+7 = 25)', JSON.stringify(rev.sums));
  ok(!rev.hasBig, 'NINCS önálló „25" lap — az összeg nem lapnak látszik');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.screenshot({ path: ROOT + '/tests/cardbattle_reveal.png' });
  await p.close();

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
