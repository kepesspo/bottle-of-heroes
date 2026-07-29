// v10.184 — Ország-Város: több szó egy kategóriához (1 / 2 / 3 / bármennyi)
//
// A legfontosabb, hogy az ALAPÉRTELMEZÉS ne változtasson semmit: aki nem nyúl a
// választóhoz, annak a játék pontosan olyan maradjon, mint eddig.
//
// Ami csendben elromolhat:
//   1) a limit nem korlátoz — a 4. szó is pontot ér;
//   2) az önismétlés ("Ausztria, Ausztria") háromszor számít;
//   3) a szavazat-kulcsok összecsúsznak: egy szóra adott X a másik szóra is hat;
//   4) a régi, egyszavas körök elromlanak az új olvasótól.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const stub = fs.readFileSync(__dirname + '/fbstub.js', 'utf8');
const BASE = 'file:///home/user/bottle-of-heroes/index.html';
const SRC = '/home/user/bottle-of-heroes/app.src.html';

const PLAYERS = [
  { id:'a', name:'Anna', color:'#5BA0DB' },
  { id:'b', name:'Béla', color:'#E07A5F' },
  { id:'c', name:'Cili', color:'#A78BFA' },
];

(async () => {
  let fail = 0;
  const ok = (l, c, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 390, height: 1400 } });
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

  // ─── 1) A limit ertelmezese ───
  // A hianyzo ertek 1, nem "barmennyi" — egy regi szoba (vagy egy regebbi
  // kliens) a megszokott jatekot kell hozza.
  console.log('\n===== A LIMIT ÉRTELMEZÉSE =====');
  {
    const r = await p.evaluate(() => ({
      undef: ovfjLimit(undefined), nul: ovfjLimit(null), zero: ovfjLimit(0),
      one: ovfjLimit(1), three: ovfjLimit(3), junk: ovfjLimit('x'), neg: ovfjLimit(-2),
    }));
    ok('hiányzó érték = 1 (a megszokott játék)', r.undef === 1 && r.nul === 1, `${r.undef} / ${r.nul}`);
    ok('a 0 jelenti a "bármennyit"', r.zero === 0, String(r.zero));
    ok('a számok átmennek', r.one === 1 && r.three === 3, `${r.one} / ${r.three}`);
    ok('hibás érték nem old fel korlátot', r.junk === 1 && r.neg === 1, `${r.junk} / ${r.neg}`);
  }

  // ─── 2) A szavak kiolvasasa ───
  console.log('\n===== A SZAVAK KIOLVASÁSA =====');
  {
    const r = await p.evaluate(() => {
      const rec = { orszag: 'Ausztria, Albánia ,Argentína,  ,Andorra', varos: 'Athén' };
      return {
        lim2: ovfjVals(rec, 'orszag', 2),
        lim0: ovfjVals(rec, 'orszag', 0),
        limDef: ovfjVals(rec, 'orszag', undefined),
        single: ovfjVals(rec, 'varos', 3),
        empty: ovfjVals(rec, 'allat', 0),
        noRec: ovfjVals(null, 'orszag', 0),
      };
    });
    ok('a limit tényleg vág', r.lim2.length === 2 && r.lim2[1] === 'Albánia', r.lim2.join(' | '));
    ok('"bármennyi" mindet hozza', r.lim0.length === 4, r.lim0.join(' | '));
    ok('alapból csak az elsőt', r.limDef.length === 1 && r.limDef[0] === 'Ausztria', r.limDef.join(' | '));
    ok('az üres tagok kiesnek, a szóközök lekopnak',
       r.lim0.every(x => x === x.trim() && x.length > 0), JSON.stringify(r.lim0));
    ok('a régi, vessző nélküli válasz változatlan', r.single.length === 1 && r.single[0] === 'Athén', r.single.join(' | '));
    ok('üres kategória / hiányzó rekord nem dob', r.empty.length === 0 && r.noRec.length === 0);
  }

  // ─── 3) Ervenyesseg ───
  console.log('\n===== ÉRVÉNYESSÉG =====');
  {
    const r = await p.evaluate(() => {
      const answers = {
        a: { round:1, orszag:'Ausztria, Albánia, Belgium, Andorra' }, // 3. rossz betu, 4. limiten kivul
        b: { round:1, orszag:'Albánia, Ausztrália' },                 // Albania egyezik Annaval
        c: { round:1, orszag:'Argentína, argentína, Angola' },        // onismetles (kis/nagybetu)
      };
      const V = ovfjBuildValidity(answers, 'A', 1, 3);
      const dump = pid => V(pid, 'orszag').map(x => x.val + ':' + (x.valid ? 'ok' : x.reason));
      return { a: dump('a'), b: dump('b'), c: dump('c'),
               // limit nelkul a 4. szo is bejon
               a0: ovfjBuildValidity(answers, 'A', 1, 0)('a', 'orszag').map(x => x.val) };
    });
    ok('a limiten felüli szó meg sem jelenik', r.a.length === 3, r.a.join(' | '));
    ok('a rossz kezdőbetű kiesik', /Belgium:✗ betű/.test(r.a.join('|')), r.a.join(' | '));
    ok('a két játékos egyező szava mindkettőnél kiesik',
       /Albánia:× egyező/.test(r.a.join('|')) && /Albánia:× egyező/.test(r.b.join('|')),
       r.a.join(' | ') + '  ·  ' + r.b.join(' | '));
    // Enelkul "Ausztria, Ausztria, Ausztria" harom pont lenne.
    ok('az önismétlés csak egyszer ér (kis/nagybetűtől függetlenül)',
       r.c[0].endsWith(':ok') && r.c[1].endsWith(':× ismétlés'), r.c.join(' | '));
    ok('az önismétlés nem teszi "egyezővé" a többiek szavát',
       r.c[2] === 'Angola:ok', r.c.join(' | '));
    ok('"bármennyi" mellett a 4. szó is bejön', r.a0.length === 4, r.a0.join(' | '));
  }

  // ─── 4) A szavazat-kulcsok ───
  // Ha ket szo ugyanazt a kulcsot kapna, egy X mindkettot leszavazna.
  console.log('\n===== A SZAVAZAT-KULCSOK =====');
  {
    const r = await p.evaluate(() => ({
      k0: ovfjVoteKey(1, 'a', 'orszag', 0),
      kNo: ovfjVoteKey(1, 'a', 'orszag'),
      k1: ovfjVoteKey(1, 'a', 'orszag', 1),
      k2: ovfjVoteKey(1, 'a', 'orszag', 2),
    }));
    ok('a 0. szó kulcsa a régi marad (a beérkezett szavazat nem vész el)',
       r.k0 === 'r1_a_orszag' && r.kNo === r.k0, `${r.kNo} / ${r.k0}`);
    ok('a további szavak külön kulcsot kapnak',
       new Set([r.k0, r.k1, r.k2]).size === 3, [r.k0, r.k1, r.k2].join(' · '));
  }

  // ─── 5) A szavazo nezet: szavankent egy sor ───
  console.log('\n===== SZAVANKÉNT EGY SOR =====');
  {
    const mount = (limit) => p.evaluate((lim) => {
      const old = document.getElementById('__m'); if (old) old.remove();
      const r = document.getElementById('root'); if (r) r.style.display = 'none';
      const root = document.createElement('div'); root.id = '__m';
      root.style.cssText = 'position:fixed;inset:0;z-index:1;background:var(--app-bg);overflow:auto;padding:12px';
      document.body.appendChild(root);
      ReactDOM.createRoot(root).render(React.createElement(OVFJVotingView, {
        letter:'A', round:1, myPid:'a', myVotes:{}, tallies:null, onVote:()=>{}, limit: lim,
        players:[{id:'a',name:'Anna',color:'#5BA0DB'},{id:'b',name:'Béla',color:'#E07A5F'}],
        answers:{ a:{round:1,orszag:'Ausztria'}, b:{round:1,orszag:'Albánia, Andorra, Angola'} },
      }));
    }, limit);

    await mount(1); await p.waitForTimeout(900);
    const one = await p.evaluate(() => document.querySelector('#__m').innerText.replace(/\s+/g, ' '));
    ok('1-es limitnél csak az első szó látszik',
       one.includes('Albánia') && !one.includes('Andorra'), (one.match(/Albánia.{0,30}/) || [''])[0]);

    await mount(0); await p.waitForTimeout(900);
    const all = await p.evaluate(() => {
      const card = [...document.querySelectorAll('#__m div')]
        .filter(d => d.textContent.includes('Ország') && d.textContent.includes('Angola'))
        .sort((a, b) => a.textContent.length - b.textContent.length)[0];
      const t = document.querySelector('#__m').innerText;
      return { text: t.replace(/\s+/g, ' '),
               btns: card.querySelectorAll('button').length,
               belaCount: (card.textContent.match(/Béla/g) || []).length };
    });
    ok('"bármennyi" mellett mindhárom szó megjelenik',
       ['Albánia','Andorra','Angola'].every(w => all.text.includes(w)), all.text.slice(0, 90));
    ok('mindhárom szóra külön értékelő gombpár jut', all.btns === 6, (all.btns / 2) + ' gombpár');
    // A nev ismetlese zajos lenne, es a szavak oszlopa is szetesne.
    ok('a nevet csak az első szónál írjuk ki', all.belaCount === 1, all.belaCount + '× "Béla" a kártyán');

    const lefts = await p.evaluate(() => [...document.querySelectorAll('#__m span')]
      .filter(s => /^(Albánia|Andorra|Angola)$/.test(s.textContent.trim()))
      .map(s => Math.round(s.getBoundingClientRect().left)));
    ok('a szavak így is egy oszlopban állnak',
       lefts.length === 3 && new Set(lefts).size === 1, lefts.join(', '));
  }

  // ─── 6) A valaszto ───
  console.log('\n===== A VÁLASZTÓ =====');
  {
    await p.evaluate(() => {
      const old = document.getElementById('__m'); if (old) old.remove();
      const root = document.createElement('div'); root.id = '__m';
      root.style.cssText = 'position:fixed;inset:0;z-index:1;background:var(--app-bg);padding:12px';
      document.body.appendChild(root);
      function H() { const [v, sv] = React.useState(undefined); window.__lim = v;
        return React.createElement(OVFJLimitPicker, { value: v, onChange: sv }); }
      ReactDOM.createRoot(root).render(React.createElement(H));
    });
    await p.waitForTimeout(900);
    const labels = await p.evaluate(() => [...document.querySelectorAll('#__m button')].map(x => x.innerText.trim()));
    ok('négy gomb van: 1, 2, 3, Bármennyi',
       labels.join('|') === '1|2|3|Bármennyi', labels.join(' | '));

    // alapbol az 1 aktiv, meg akkor is, ha meg nem valasztott senki
    const active = () => p.evaluate(() => [...document.querySelectorAll('#__m button')]
      .map(x => getComputedStyle(x).backgroundColor !== 'rgba(0, 0, 0, 0)'));
    ok('alapból az 1 a kijelölt', (await active())[0] === true, JSON.stringify(await active()));

    await p.evaluate(() => [...document.querySelectorAll('#__m button')]
      .find(x => x.innerText.trim() === 'Bármennyi').click());
    await p.waitForTimeout(400);
    ok('a "Bármennyi" 0-t ad vissza', (await p.evaluate(() => window.__lim)) === 0,
       String(await p.evaluate(() => window.__lim)));
    ok('és át is vált rá a kijelölés', (await active())[3] === true, JSON.stringify(await active()));
    ok('a magyarázat is átvált',
       /Vesszővel sorold/.test(await p.evaluate(() => document.querySelector('#__m').innerText)));

    await p.evaluate(() => [...document.querySelectorAll('#__m button')]
      .find(x => x.innerText.trim() === '3').click());
    await p.waitForTimeout(400);
    ok('a 3 gomb 3-at ad vissza', (await p.evaluate(() => window.__lim)) === 3);
  }

  // ─── 7) A kitolto urlap: + gomb, lablec, badge ───
  // Marad a nyolc sor; a sor vegen a pipa helyett + gomb. Ket dolog kritikus:
  //   a) amit a vegen NEM mentett le, az is szamitson (kulonben elveszne az
  //      utolso szo, amit epp gepelt, amikor lejart az ido);
  //   b) a + ne engedjen tullepni a limiten.
  console.log('\n===== A KITÖLTŐ ŰRLAP =====');
  {
    const mountForm = (limit, start) => p.evaluate(([lim, st]) => {
      const old = document.getElementById('__f'); if (old) old.remove();
      const root = document.createElement('div'); root.id = '__f';
      root.style.cssText = 'position:fixed;inset:0;z-index:1;background:var(--app-bg);overflow:auto;padding:12px';
      document.body.appendChild(root);
      function H() {
        const [a, sa] = React.useState(st);
        window.__ans = a;
        return React.createElement(OVFJWritingForm, { letter:'A', remaining:60, localAns:a,
          setLocalAns:sa, submitted:false, onSubmit:()=>{}, doneInfo:null, limit: lim });
      }
      ReactDOM.createRoot(root).render(React.createElement(H));
    }, [limit, start]);

    // az elso sor (Orszag) elemei
    const row = () => p.evaluate(() => {
      const inp = document.querySelectorAll('#__f input')[0];
      const card = inp.closest('div').parentElement.parentElement;
      const chips = [...card.querySelectorAll('button')].filter(x => !/Szó hozzáadása/.test(x.getAttribute('aria-label')||''));
      const plus = [...card.querySelectorAll('button')].find(x => /Szó hozzáadása/.test(x.getAttribute('aria-label')||''));
      return { value: inp.value, disabled: inp.disabled, placeholder: inp.placeholder,
               chips: chips.map(c => c.textContent.trim()),
               plusOn: plus ? !plus.disabled : null, hasPlus: !!plus,
               label: card.querySelector('div').textContent };
    });
    const type = (t) => p.evaluate((txt) => {
      const inp = document.querySelectorAll('#__f input')[0];
      const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
      setter.call(inp, txt);
      inp.dispatchEvent(new Event('input', { bubbles: true }));
    }, t);
    const plus = () => p.evaluate(() => {
      const b = [...document.querySelectorAll('#__f button')]
        .find(x => /Szó hozzáadása/.test(x.getAttribute('aria-label')||''));
      if (b && !b.disabled) b.click();
    });

    // a) 1-es limitnel a MAI urlap: pipa, nincs +, nincs chip
    await mountForm(1, { orszag:'Ausztria' }); await p.waitForTimeout(900);
    let r = await row();
    ok('1-es limitnél nincs + gomb (a mai űrlap)', r.hasPlus === false, JSON.stringify(r.chips));
    ok('1-es limitnél a mező a teljes választ mutatja', r.value === 'Ausztria', r.value);

    // b) tobb szonal: + gomb a sor vegen
    await mountForm(3, {}); await p.waitForTimeout(900);
    r = await row();
    ok('több szónál + gomb van a sor végén', r.hasPlus === true);
    ok('üres mezőnél a + nem aktív', r.plusOn === false);

    await type('Ausztria'); await p.waitForTimeout(300);
    ok('gépelésre aktiválódik a +', (await row()).plusOn === true);

    await plus(); await p.waitForTimeout(400);
    r = await row();
    ok('a + lementi a szót — chipként megjelenik', r.chips.some(c => c.startsWith('Ausztria')), r.chips.join(' | '));
    ok('és a mező kiürül, jöhet a következő', r.value === '', JSON.stringify(r.value));
    ok('a badge 1-et mutat', /1\/3/.test(r.label), r.label);

    // c) a limit betelik
    await type('Albánia'); await p.waitForTimeout(250); await plus(); await p.waitForTimeout(300);
    await type('Angola');  await p.waitForTimeout(250); await plus(); await p.waitForTimeout(400);
    r = await row();
    ok('három szó után a badge 3/3', /3\/3/.test(r.label), r.label);
    ok('a limit felett a + nem enged többet', r.plusOn === false);
    // Ha a mezo nyitva maradna, a negyedik szo csendben elveszne beadaskor.
    ok('és a mező is lezár, hogy ne vesszen el csendben szó', r.disabled === true);
    ok('meg is mondja, miért', /megvan mind/i.test(r.placeholder), r.placeholder);
    ok('a mentett érték vesszős lista', /^Ausztria,\s*Albánia,\s*Angola,?$/.test(
       (await p.evaluate(() => window.__ans)).orszag || ''),
       (await p.evaluate(() => window.__ans)).orszag);

    // d) chip koppintasra kikerul
    await p.evaluate(() => {
      const b = [...document.querySelectorAll('#__f button')].find(x => /Albánia/.test(x.textContent));
      if (b) b.click();
    });
    await p.waitForTimeout(400);
    r = await row();
    ok('a chipre koppintva kikerül a szó', !r.chips.some(c => c.startsWith('Albánia')), r.chips.join(' | '));
    ok('és a mező újra nyílik', r.disabled === false && /2\/3/.test(r.label), r.label);

    // e) A LENYEG: amit nem mentett le, az is szamit
    await type('Argentína'); await p.waitForTimeout(400);
    const raw = (await p.evaluate(() => window.__ans)).orszag;
    const counted = await p.evaluate((v) => ovfjVals({ orszag: v }, 'orszag', 3), raw);
    ok('a le nem mentett szó is beleszámít a beadott válaszba',
       counted.length === 3 && counted[2] === 'Argentína', counted.join(' | '));

    // f) rossz kezdobetu a lableben is latszik
    await mountForm(0, { orszag:'Ausztria, Belgium,' }); await p.waitForTimeout(900);
    const bad = await p.evaluate(() => {
      const b = [...document.querySelectorAll('#__f button')].find(x => /Belgium/.test(x.textContent));
      return b ? getComputedStyle(b).textDecorationLine : 'nincs chip';
    });
    ok('a rossz kezdőbetűs mentett szó át van húzva', /line-through/.test(bad), bad);
    const lbl = (await row()).label;
    ok('"bármennyi" mellett a badge nem ír limitet', !lbl.includes('/'), lbl);
    ok('a badge az érvényes szavakat számolja (a rossz betűs nem számít)',
       /Ország1/.test(lbl), lbl);
  }

  // ─── 8) A ket szabaly, ami a forrasban dol el ───
  // Ez a ketto a komponensen belul, a szavazas lezarasakor fut — kivulrol nem
  // hivhato, ezert a forrasban rogzitjuk. Ha valaki visszaallitja, itt bukik.
  console.log('\n===== A PONTOZÁS KÉT SZABÁLYA =====');
  {
    const src = fs.readFileSync(SRC, 'utf8');
    ok('amire senki nem szavazott, az elfogadott',
       /vals\.length === 0 \|\| yes > no/.test(src),
       (src.match(/if \(vals\.length[^\n]*/) || ['NINCS MEG'])[0]);
    ok('a körönkénti korty be van sapkázva',
       /Math\.min\(CAP, maxRs - \(rs\[p\.id\]\|\|0\)\)/.test(src),
       (src.match(/const CAP = [^\n]*/) || ['NINCS PLAFON'])[0]);
    ok('a beállítás átmegy a vendégnek is (syncRoom)',
       (src.match(/ovfjState: \{[^}]*answerLimit/g) || []).length === 2,
       (src.match(/ovfjState: \{[^}]*answerLimit/g) || []).length + ' hely');
  }

  ok('nincs JS hiba', errs.filter(e => !/ServiceWorker/.test(e)).length === 0, errs.join(' | '));
  await p.close();
  await b.close();
  console.log('\n' + (fail === 0 ? '✅ MINDEN ELLENORZES RENDBEN' : '❌ ' + fail + ' ELLENORZES BUKOTT'));
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
