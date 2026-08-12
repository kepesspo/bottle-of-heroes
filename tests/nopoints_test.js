// v10.338 — Pontgyűjtés NÉLKÜL: nincs result banner, Állás fül és Büntetés
//
// A „Pontgyűjtés" mód (`gameMeta.modes` → 'points') kikapcsolva a `trackScores`
// hamis, és a könyvelés MEG SEM TÖRTÉNIK: az `advance` / `advancePaired` /
// `advanceTeam` / `advanceLoverseny` mind változatlanul hagyja a játékosokat.
//
// Három felület viszont úgy viselkedett, mintha kerülne:
//   1. a result banner „+1 pont"-ot és korty-számot hirdetett;
//   2. a MENÜ → Állás fül végig nullákat mutatott;
//   3. ⚠️ a Büntetés gomb pedig TÉNYLEG írt a játékosokra (a `givePenalty` nem
//      nézi a `trackScores`-t) — vagyis pontgyűjtés nélkül a büntetés volt az
//      EGYETLEN, ami számolt. Ezt a 4. blokk méri, és ez a legfontosabb: a
//      hiányzó gomb nélkül itt csendben adat keletkezne.
//
// A KONTROLL-BLOKK nem elhagyható: pontgyűjtéssel MINDHÁROM felületnek ott kell
// lennie, különben a teszt egy „mindent elrejtő" regressziót is átengedne.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const PL = [{ id:'a', name:'Sere',  color:'#E07A5F', points:0, drinks:0 },
            { id:'b', name:'Kecsi', color:'#4FC2A0', points:0, drinks:0 },
            { id:'c', name:'Vivi',  color:'#A78BFA', points:0, drinks:0 }];

async function open(b) {
  const p = await b.newPage({ viewport: { width: 402, height: 1000 } });
  p.__errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  return p;
}

// A PlayScreen EGY jatekkal, adott modokkal. `modes:[]` = nincs pontgyujtes.
const mount = (p, modes) => p.evaluate(({ pl, modes }) => {
  const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
  let root = document.getElementById('__p'); if (root) root.remove();
  root = document.createElement('div'); root.id = '__p';
  root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column;overflow:auto';
  document.body.appendChild(root);
  function H() {
    const [ps, setPs] = React.useState(pl);
    window.__players = ps;
    return React.createElement(PlayScreen, {
      go: () => {}, players: ps, setPlayers: setPs, selectedGames: ['erem'], roomCode: null,
      gameMeta: { modes, difficulty: 'mid' },
      setGameMeta: () => {}, setScoreHistory: () => {}, setLastGameRound: () => {} });
  }
  ReactDOM.createRoot(root).render(React.createElement(H));
}, { pl: PL, modes });

const openMenu = p => p.evaluate(() => {
  const x = [...document.querySelectorAll('#__p button')].find(y => /MENÜ/.test(y.textContent || ''));
  if (!x) return 'NINCS'; x.click(); return 'ok';
});
// A menu PORTALBA renderel, ezert a teljes body-t nezzuk (lasd gamectrl_test).
const menuBtns = p => p.evaluate(() => [...document.querySelectorAll('button')]
  .map(x => (x.textContent || '').replace(/\s+/g, ' ').trim()).filter(Boolean));
const hasBanner = p => p.evaluate(() =>
  [...document.querySelectorAll('span')].some(s => /^(Nyertes(ek)?|Isz(ik|nak))$/.test((s.textContent||'').trim())));

// Az Eremdobas: „Fej"/„Írás" valasztas, majd a dobas -> eredmeny.
const playErem = async (p) => {
  for (let i = 0; i < 25; i++) {
    const did = await p.evaluate(() => {
      const bs = [...document.querySelectorAll('#__p button')]
        .filter(x => /Fej|Írás|Dobás|Dobjuk|Feldobom|Tovább/i.test(x.textContent || '') && !x.disabled);
      if (!bs.length) return false;
      bs[0].click(); return true;
    });
    if (!did) await p.waitForTimeout(400);
    await p.waitForTimeout(350);
    if (await hasBanner(p)) return true;
  }
  return false;
};

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── 1. KONTROLL: pontgyujtessel MINDHAROM felulet ott van ──
  console.log('\n===== 1. KONTROLL — PONTGYUJTESSEL MINDEN OTT VAN =====');
  let p = await open(b);
  await mount(p, ['points']);
  await p.waitForTimeout(1500);
  await openMenu(p); await p.waitForTimeout(700);
  const ctl = await menuBtns(p);
  ok(ctl.some(x => /^Állás$/.test(x)), 'van „Állás" fül', ctl.filter(x => x.length < 14).join(' | '));
  ok(ctl.some(x => /Büntetés/.test(x)), 'van „Büntetés" gomb');
  // ⚠️ Ez a sor teszi ERTELMESSE a 3. blokkot: bizonyitja, hogy a hajto
  // tenyleg vegigjatssza a kort. Nelkule a „nincs banner" akkor is atmenne,
  // ha a jatek el sem indult volna.
  await mount(p, ['points']);
  await p.waitForTimeout(1200);
  ok(await playErem(p), 'kontroll: pontgyűjtéssel a banner FELJÖN — a hajtó működik');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  // ── 2. PONTGYUJTES NELKUL: nincs Allas ful, nincs Buntetes ──
  console.log('\n===== 2. PONTGYUJTES NELKUL — A MENU =====');
  p = await open(b);
  await mount(p, []);
  await p.waitForTimeout(1500);
  await openMenu(p); await p.waitForTimeout(700);
  const off = await menuBtns(p);
  ok(!off.some(x => /^Állás$/.test(x)), 'NINCS „Állás" fül', off.filter(x => x.length < 14).join(' | '));
  ok(!off.some(x => /Büntetés/.test(x)), 'NINCS „Büntetés" gomb a menüben', off.filter(x => /Bünt/.test(x)).join(','));
  ok(off.some(x => /Szerkesztés/.test(x)) && off.some(x => /Vezérlés/i.test(x)),
     'a másik két fül viszont megmaradt', off.filter(x => x.length < 14).join(' | '));
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));

  // ── 3. PONTGYUJTES NELKUL: nincs result banner ──
  console.log('\n===== 3. PONTGYUJTES NELKUL — A BANNER =====');
  await p.evaluate(() => {
    const x = [...document.querySelectorAll('button')].find(y => /Kilépés|Bezár|✕/.test(y.textContent || ''));
    // a menut a hatterre kattintva zarjuk
    document.querySelectorAll('div').forEach(d => {});
    if (x) return;
  });
  await mount(p, []);   // tiszta lap, menu nelkul
  await p.waitForTimeout(1200);
  const played = await playErem(p);
  ok(!played, 'a kör lezárult, de NINCS eredmény-banner', played ? 'MÉGIS FELJÖTT' : 'nincs');
  const acc0 = await p.evaluate(() => (window.__players || []).map(x => x.points + '/' + x.drinks).join(' '));
  ok(acc0 === '0/0 0/0 0/0', 'és tényleg semmi nem került fel (kontroll)', acc0);
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  // ── 4. ⚠️ A LENYEG: a buntetes NEM keletkeztethet adatot ──
  // A `givePenalty` nem nezi a `trackScores`-t, tehat ha a gomb kint maradna,
  // pontgyujtes nelkul EZ lenne az egyetlen, ami szamol.
  console.log('\n===== 4. A BUNTETES NEM KELETKEZTET ADATOT =====');
  p = await open(b);
  await mount(p, []);
  await p.waitForTimeout(1500);
  await openMenu(p); await p.waitForTimeout(700);
  const clicked = await p.evaluate(() => {
    const x = [...document.querySelectorAll('button')].find(y => /Büntetés/.test(y.textContent || ''));
    if (!x) return 'nincs gomb';
    x.click(); return 'kattintva';
  });
  ok(clicked === 'nincs gomb', 'a MENÜBEN nincs Büntetés gomb', clicked);
  await p.waitForTimeout(600);
  const acc = await p.evaluate(() => (window.__players || []).map(x => x.points + '/' + x.drinks).join(' '));
  ok(acc === '0/0 0/0 0/0', 'a menün keresztül semmi nem került fel', acc);

  // ── 5. ⚠️ A BUNTETES viszont MUKODIK, es VAN bannere ──
  // A wildcard-savi „Szabalyszego?" belepo pontgyujtes nelkul is kint van
  // (v10.341, tulajdonosi dontes: kezreesobb ott). Ha a banner elmaradna, a
  // jatekos kiosztana harom kortyot, es semmi visszajelzest nem kapna rola.
  console.log('\n===== 5. A BUNTETES MUKODIK, ES VAN BANNERE =====');
  const fsrc = fs.readFileSync(ROOT + '/app.src.html', 'utf8');
  ok(!/\{trackScores && \(\s*<button onClick=\{\(\) => setWcPunishOpen/.test(fsrc),
     'a „Szabályszegő?" belépő NINCS pontgyűjtéshez kötve');
  ok(/if \(!trackScores && !res\.penalty\)/.test(fsrc),
     'a banner-kapu átengedi a büntetést (különben néma lenne a kiosztás)');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
