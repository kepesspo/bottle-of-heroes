// Buli-könyvelés füstteszt
// -------------------------------------------------------------------------
// Minden játékot végigjátszik (generikus "kattints tovább" driverrel), és
// összeveti, amit az eredmény-banner (onResult) ígér azzal, amit a játék
// ténylegesen átad a buli állásának (onAdvance).
//
// A ma javított három hiba mind ebbe a családba tartozott:
//  - a győztes nem kapott pontot (Időpárbaj, Útvesztő)
//  - a Beer Pong eredménye eldobódott a lezárásnál
//
// Minden játéknak van forgatókönyve: amit a generikus driver nem tud
// végigjátszani, arra saját driver van a DRIVERS-ben. Egyetlen játék marad
// kimérhetetlen offline (ovfj) — az ONLINE_ONLY-ban, külön kategóriaként.
//
// Használat:  node ledger_test.js [jatekId ...]
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const stub = fs.readFileSync(__dirname + '/fbstub.js', 'utf8');

const PLAYERS = [
  { id:'a', name:'Anna', color:'#5BA0DB', profileId:'p_a', points:0, drinks:0 },
  { id:'b', name:'Bela', color:'#E07A5F', profileId:'p_b', points:0, drinks:0 },
  { id:'c', name:'Cili', color:'#81B29A', profileId:'p_c', points:0, drinks:0 },
  { id:'d', name:'Dani', color:'#F2CC8F', profileId:'p_d', points:0, drinks:0 },
];

// Gombfeliratok, amikkel egy játék előre halad. Sorrend = prioritás.
const ADVANCE_PATTERNS = [
  'nyert', 'Döntetlen', 'Kész', 'Mehet', 'Indul', 'Indít', 'Start', 'Kezd', 'Tovább',
  'Koppints', 'Most', 'Csenget', 'Nálam', 'Nálad',
  'Megnézem', 'Rendben', 'OK$', 'Vége', 'Befejez', 'Stop', 'Leállít',
  'Igen', 'Nem', 'Iszik', 'Elrontotta', 'Sikerült', 'Nem sikerült',
  'Következő', 'Dobás', 'Pörget', 'Húz', 'Felfed', 'Válasz',
];

// Játékok, amiket offline egyáltalán nem lehet elindítani (online szoba kell).
// Ezeket nem „lefedetlennek", hanem külön kategóriának jelentjük.
const ONLINE_ONLY = { ovfj: 'online szoba kell (a játékosok a telefonjukon írnak/szavaznak)' };

// Játék-specifikus gameMeta. A Busznál a legkisebb engedélyezett pályát
// állítjuk be (a config-lapon is állítható értékek), különben a „nulláról
// újrakezdős" buszút több percig tartana.
const DRIVER_META = {
  busz: { buszConfig: { deckCount:1, cardsPerPlayer:4, pyramidRows:3, busSteps:4, bonusGuess:false } },
};

// ── Saját driverek ────────────────────────────────────────────────────────
// Amit a generikus kattintgatás nem tud végigjátszani (rácsra rajzolás,
// többfázisú átadás), annak külön forgatókönyv kell.
const DRIVERS = {
  // Útvesztő: csapdalerakás (5 típus, 5 külön mező) → átadás → ugyanez a másik
  // félnek → útvonalrajzolás mindkét oldalon → feltárás-animáció → eredmény
  async utveszto(p) {
    const btn = (re) => p.evaluate((re) => {
      const b = Array.from(document.querySelectorAll('#__g button')).find(x => new RegExp(re).test(x.innerText) && !x.disabled);
      if (b) { b.click(); return b.innerText.trim().slice(0, 24); } return null;
    }, re);
    const cell = (i) => p.evaluate((i) => {
      const g = Array.from(document.querySelectorAll('#__g div')).find(d => getComputedStyle(d).display === 'grid' && d.children.length === 25);
      if (g && g.children[i]) g.children[i].click();
    }, i);
    const txt = () => p.evaluate(() => document.getElementById('__g').innerText);
    const fired = () => p.evaluate(() => window.__adv.length > 0);

    const placeTraps = async () => {
      let idx = 7;
      for (const t of ['Sörcsokor', 'Fal', 'Álom', 'Örvény', 'Teleport']) {
        await btn(t); await p.waitForTimeout(160);
        for (let k = 0; k < 8; k++) {
          await cell(idx); idx++;
          await p.waitForTimeout(150);
          if (new RegExp(t + ' ✓').test(await txt())) break;
        }
      }
    };
    // START=0, END=24 (5×5): felső sor végig, majd a jobb szélső oszlop le
    const drawPath = async () => { for (const i of [0,1,2,3,4,9,14,19,24]) { await cell(i); await p.waitForTimeout(130); } };

    await btn('Kezdés'); await p.waitForTimeout(700);
    await placeTraps();  await btn('Kész'); await p.waitForTimeout(800);
    await placeTraps();  await btn('Kész'); await p.waitForTimeout(800);
    await drawPath();    await btn('Kész'); await p.waitForTimeout(800);
    await drawPath();    await btn('FELTÁRÁS'); await p.waitForTimeout(1500);
    // futás-animáció: a köztes „→ X futása!" gombokat is meg kell nyomni
    for (let i = 0; i < 40; i++) {
      if (await fired()) break;
      await btn('futása|Tovább|Kész|Következő|Rendben|FELTÁRÁS|→');
      await p.waitForTimeout(900);
    }
  },

  // Lóverseny: 4 fogadás (mindenki MÁS lóra, hogy legyen nyertes és vesztes is)
  // → Rajt → a futam ~15 mp alatt lefut
  async loverseny(p) {
    const HORSES = ['Gyorslábú Géza', 'Csülök', 'Remegő Rezső', 'Pálinka Pista'];
    for (let i = 0; i < 4; i++) {
      await p.evaluate((h) => {
        const b = Array.from(document.querySelectorAll('#__g button')).find(x => x.innerText.includes(h));
        if (b) b.click();
      }, HORSES[i % HORSES.length]);
      await p.waitForTimeout(200);
      await p.evaluate(() => {
        const b = Array.from(document.querySelectorAll('#__g button')).find(x => /Következő/.test(x.innerText) && !x.disabled);
        if (b) b.click();
      });
      await p.waitForTimeout(400);
    }
    await p.evaluate(() => {
      const b = Array.from(document.querySelectorAll('#__g button')).find(x => /Rajt/.test(x.innerText) && !x.disabled);
      if (b) b.click();
    });
    // A futam ~20 mp. A végén a NYERTES osztja szét a nyereményt a vesztesek
    // között (+ gombok), és csak a teljes kiosztás után zárul a játék.
    for (let i = 0; i < 60; i++) {
      if (await p.evaluate(() => window.__adv.length > 0)) break;
      await p.evaluate(() => {
        const root = document.getElementById('__g');
        const txt = root.innerText;
        const left = (txt.match(/Még (\d+) korty kiosztható/) || [])[1];
        if (left && +left > 0) {
          const plus = Array.from(root.querySelectorAll('button[aria-label="Egy korttyal több"]')).find(x => !x.disabled);
          if (plus) { plus.click(); return; }
        }
        // „Ki osztom" (v10.294): a teljes kiosztas utan EZ zarja a jatekot —
        // enelkul a driver a keretet elkolti, aztan megall, es a Loverseny
        // „nem jatszhato"-kent bukik ki. A szokoz miatt a `Kioszt` nem fogja.
        const b = Array.from(root.querySelectorAll('button'))
          .find(x => /Tovább|Következő|Rendben|Kész|OK|Vége|Mehet|Kioszt|Ki osztom/.test(x.innerText) && !x.disabled);
        if (b) b.click();
      });
      await p.waitForTimeout(600);
    }
  },

  // Számsor: Start → 1..9 sorban. A számok cursor:pointer divek (nem gombok).
  async szamsor(p) {
    for (let round = 0; round < 6; round++) {
      if (await p.evaluate(() => window.__adv.length > 0)) break;
      await p.evaluate(() => {
        const b = Array.from(document.querySelectorAll('#__g button')).find(x => /Start|Indul|Kezd/.test(x.innerText) && !x.disabled);
        if (b) b.click();
      });
      await p.waitForTimeout(600);
      for (let n = 1; n <= 9; n++) {
        await p.evaluate((n) => {
          const el = Array.from(document.querySelectorAll('#__g div'))
            .find(x => x.innerText.trim() === String(n) && getComputedStyle(x).cursor === 'pointer' && x.getBoundingClientRect().width > 30);
          if (el) el.click();
        }, n);
        await p.waitForTimeout(80);
      }
      await p.waitForTimeout(1000);
      await p.evaluate(() => {
        const b = Array.from(document.querySelectorAll('#__g button')).find(x => /Tovább|Következő|Rendben|Kész|OK/.test(x.innerText) && !x.disabled);
        if (b) b.click();
      });
      await p.waitForTimeout(700);
    }
  },

  // Reakció: Start → várunk, míg a mező zöldre vált, akkor koppintunk
  async reakcio(p) {
    for (let round = 0; round < 6; round++) {
      if (await p.evaluate(() => window.__adv.length > 0)) break;
      await p.evaluate(() => {
        const b = Array.from(document.querySelectorAll('#__g button')).find(x => /Start|Indul|Kezd|Tovább|Következő|Rendben/.test(x.innerText) && !x.disabled);
        if (b) b.click();
      });
      for (let k = 0; k < 90; k++) {
        if (await p.evaluate(() => window.__adv.length > 0)) break;
        await p.waitForTimeout(110);
        const hit = await p.evaluate(() => {
          const el = Array.from(document.querySelectorAll('#__g div,#__g button')).find(x => {
            if (x.getBoundingClientRect().height < 80) return false;
            const m = (getComputedStyle(x).backgroundColor || '').match(/\d+/g);
            return m && +m[1] > 120 && +m[0] < 130; // zöldes
          });
          if (el) { el.click(); return true; }
          return false;
        });
        if (hit) break;
      }
      await p.waitForTimeout(900);
    }
  },

  // Memória: 4×4 rács. Megjegyezzük a felfordított lapokat, és ha van ismert
  // pár, azt játsszuk ki — különben új lapot fordítunk.
  async memoria(p) {
    const seen = {}; // index -> emoji
    const read = () => p.evaluate(() => {
      const g = Array.from(document.querySelectorAll('#__g div')).find(d => getComputedStyle(d).display === 'grid' && d.children.length === 16);
      if (!g) return null;
      return Array.from(g.children).map(c => (c.innerText || '').trim());
    });
    const tap = (i) => p.evaluate((i) => {
      const g = Array.from(document.querySelectorAll('#__g div')).find(d => getComputedStyle(d).display === 'grid' && d.children.length === 16);
      if (g && g.children[i]) g.children[i].click();
    }, i);
    for (let step = 0; step < 90; step++) {
      if (await p.evaluate(() => window.__adv.length > 0)) break;
      const cells = await read();
      if (!cells) { await p.waitForTimeout(400); continue; }
      cells.forEach((v, i) => { if (v && v !== '?') seen[i] = v; });
      const hidden = cells.map((v, i) => [v, i]).filter(([v]) => v === '?').map(([, i]) => i);
      if (!hidden.length) { await p.waitForTimeout(500); continue; }
      // ismert pár a rejtettek közt?
      let pair = null;
      for (const i of hidden) for (const j of hidden) {
        if (i < j && seen[i] && seen[i] === seen[j]) { pair = [i, j]; break; }
        if (pair) break;
      }
      if (pair) { await tap(pair[0]); await p.waitForTimeout(280); await tap(pair[1]); }
      else { await tap(hidden[Math.floor(Math.random() * hidden.length)]); }
      await p.waitForTimeout(320);
    }
  },

  // Beer Pong: meccsről meccsre a bal oldali játékos nyer 3-0-ra, amíg bajnok lesz,
  // majd a "Vége" gomb zárja le a tornát (itt kerül át a pont és a korty a bulira).
  async beerpong(p) {
    const txt = () => p.evaluate(() => document.getElementById('__g').innerText);
    for (let m = 0; m < 10; m++) {
      if (/Bajnok/.test(await txt())) break;
      for (let i = 0; i < 3; i++) {
        await p.evaluate(() => {
          const plus = Array.from(document.querySelectorAll('#__g button')).filter(x => x.innerText.trim() === '+');
          if (plus[0]) plus[0].click();
        });
        await p.waitForTimeout(70);
      }
      await p.waitForTimeout(200);
      const ok = await p.evaluate(() => {
        const b = Array.from(document.querySelectorAll('#__g button')).find(x => /nyert/.test(x.innerText) && !x.disabled);
        if (b) { b.click(); return true; } return false;
      });
      if (!ok) break;
      await p.waitForTimeout(500);
    }
    // bajnok megvan → lezárás
    for (let i = 0; i < 8; i++) {
      if (await p.evaluate(() => window.__adv.length > 0)) break;
      await p.evaluate(() => {
        const b = Array.from(document.querySelectorAll('#__g button')).find(x => /Vége|Lezár|Kész|Tovább/.test(x.innerText) && !x.disabled);
        if (b) b.click();
      });
      await p.waitForTimeout(600);
    }
  },

  // Busz: piramis (lapok felfordítása) → buszra szállás → a buszozók
  // K/N tippjei, amíg mindenki végigér. Rossz tippnél nagy korty-overlay
  // ugrik fel, azt a ✕-szel zárjuk, hogy ne kelljen kivárni a 6 mp-et.
  async busz(p) {
    await p.evaluate(() => {
      const b = Array.from(document.querySelectorAll('#__g button')).find(x => /Játék indítása|Indítás/i.test(x.innerText || ''));
      if (b) b.click();
    });
    await p.waitForTimeout(700);
    for (let i = 0; i < 900; i++) {
      if (await p.evaluate(() => window.__adv.length > 0)) break;
      const did = await p.evaluate(() => {
        const root = document.getElementById('__g');
        const btns = Array.from(root.querySelectorAll('button')).filter(b => !b.disabled);
        const bez = btns.find(b => b.getAttribute('aria-label') === 'Bezárás');
        if (bez) { bez.click(); return 'x'; }               // korty-overlay
        const by = (re) => btns.find(b => re.test((b.innerText || '').trim()));
        const ok = by(/^OK$/); if (ok) { ok.click(); return 'OK'; }   // zsülli
        const nx = by(/Következő lap/); if (nx) { nx.click(); return 'lap'; }
        const bus = by(/Buszra szállás/); if (bus) { bus.click(); return 'buszra'; }
        const g = btns.filter(b => /Kisebb|Nagyobb/.test(b.innerText || ''));
        if (g.length) { g[Math.random() < 0.5 ? 0 : g.length - 1].click(); return 'tipp'; }
        return null;
      });
      await p.waitForTimeout(did === 'tipp' ? 420 : 240);
    }
  },

  // Finger It: 5 kör, mindegyik Start → 3 mp visszaszamlalas → korty-kiosztas.
  // A generikus driver itt elvérzik: a visszaszamlalas alatt NINCS gomb a
  // kepernyon, amitol "beragadtnak" hiszi a kepet es racsmodra valt — vagyis
  // veletlen cellakra kattint a megerosito gomb helyett. Idozites-erzekeny,
  // ezert egy ideig veletlenul atment. A jatek maga hibatlan.
  async fingerit(p) {
    for (let round = 0; round < 8; round++) {
      if (await p.evaluate(() => window.__adv.length > 0)) break;
      // Start
      await p.evaluate(() => {
        const b = Array.from(document.querySelectorAll('#__g button')).find(x => /Start/i.test(x.innerText || '') && !x.disabled);
        if (b) b.click();
      });
      // megvarjuk a kioszto kepernyot (a visszaszamlalas ~3 mp)
      for (let k = 0; k < 30; k++) {
        await p.waitForTimeout(250);
        const ready = await p.evaluate(() => /KI ISZIK/i.test(document.getElementById('__g').innerText || ''));
        if (ready) break;
      }
      // az elso jatekosnak adunk egy kortyot, hogy legyen mit konyvelni
      await p.evaluate(() => {
        const plus = Array.from(document.querySelectorAll('#__g button[aria-label="Egy korttyal több"]')).find(x => !x.disabled);
        if (plus) plus.click();
      });
      await p.waitForTimeout(200);
      await p.evaluate(() => {
        // a + utan a gomb felirata "N korty kiosztva ✔"-re valt, nem "Senki sem iszik ✔"
        const b = Array.from(document.querySelectorAll('#__g button'))
          .find(x => /kiosztva|iszik|Kész|Rendben|Tovább/i.test(x.innerText || '') && !x.disabled);
        if (b) b.click();
      });
      await p.waitForTimeout(500);
    }
  },

  // Időzített bomba: indítás → 15–45 mp múlva csörög → megjelöljük, kinél volt
  async ticktak(p) {
    await p.evaluate(() => {
      const b = Array.from(document.querySelectorAll('#__g button')).find(x => /Indít|Start|Kezd/i.test(x.innerText || ''));
      if (b) b.click();
    });
    for (let i = 0; i < 300; i++) {   // max ~60 mp: a csörgés véletlen időpontú (15–45 mp)
      if (await p.evaluate(() => window.__adv.length > 0)) break;
      const hit = await p.evaluate(() => {
        const root = document.getElementById('__g');
        if (!/CSÖRÖG/i.test(root.innerText || '')) return false;   // még ketyeg
        const b = Array.from(root.querySelectorAll('div[style*="cursor: pointer"]'))
          .find(x => /\b(Anna|Bela|Cili|Dani)\b/.test(x.innerText || ''));
        if (b) { b.click(); return true; }
        return false;
      });
      await p.waitForTimeout(hit ? 600 : 200);
    }
  },

  // Tapper: két játékos EGYSZERRE tartja a saját mezőjét, majd 5 mp-nél
  // közelebb engedik el. Playwright egérrel ez nem megy (egy kurzor), ezért
  // szintetikus PointerEventeket küldünk. A setPointerCapture szintetikus
  // pointerId-re dobna, ezért teszt-oldalon kiütjük.
  async tapper(p) {
    await p.evaluate(() => { Element.prototype.setPointerCapture = function () {}; });
    const send = (idx, type) => p.evaluate(({ idx, type }) => {
      const root = document.getElementById('__g');
      // A nyomva tartott mező scale(0.97)-re ugrik, ezért NEM lehet pontos
      // 110 px-es magasságra szűrni — sávot kell nézni.
      const zones = Array.from(root.querySelectorAll('div')).filter(d => {
        const r = d.getBoundingClientRect();
        return r.height > 95 && r.height < 125 && r.width > 200;
      });
      const z = zones[idx];
      if (!z) return false;
      const r = z.getBoundingClientRect();
      z.dispatchEvent(new PointerEvent(type, { bubbles:true, cancelable:true, pointerId: idx + 1,
        pointerType:'touch', isPrimary:true, clientX: r.left + r.width/2, clientY: r.top + r.height/2 }));
      return true;
    }, { idx, type });

    if (!(await send(0, 'pointerdown'))) return;
    await send(1, 'pointerdown');      // mindkettő nyomva → 5 mp-es visszaszámlálás
    await p.waitForTimeout(4200);
    await send(0, 'pointerup');        // Anna enged el elsőként → ő nyer
    await p.waitForTimeout(250);
    await send(1, 'pointerup');
    await p.waitForTimeout(900);
  },

  // Kártyacsata: a húzás helyett a kattintós utat használjuk (lap kijelölése
  // → körslot kattintás). Két tervezési fázis, majd animált leleplezés.
  async cardbattle(p) {
    const planOne = async () => {
      for (let i = 0; i < 30; i++) {
        // FONTOS: a lap kijelölése és a slot kattintás NEM mehet egy
        // evaluate-be — az assign() a render-closure S.sel-jét olvassa, ami
        // egy szinkron blokkon belül még a régi (null) érték lenne.
        const done = await p.evaluate(() => {
          const root = document.getElementById('__g');
          const hand = Array.from(root.querySelectorAll('div[style*="cursor: grab"]'))
            .filter(d => !d.closest('[data-round-idx]') && d.parentElement && !/cursor: grab/.test(d.parentElement.getAttribute('style') || ''));
          if (!hand.length) return true;
          hand[0].click();
          return false;
        });
        if (done) break;
        await p.waitForTimeout(120);
        await p.evaluate(() => {
          const slots = Array.from(document.querySelectorAll('#__g [data-round-idx]'));
          const s = slots[Math.floor(Math.random() * slots.length)];
          if (s) s.click();
        });
        await p.waitForTimeout(120);
      }
      await p.evaluate(() => {
        const b = Array.from(document.querySelectorAll('#__g button')).find(x => /Kész/.test(x.innerText || ''));
        if (b) b.click();
      });
      await p.waitForTimeout(500);
    };
    await planOne();                                       // P1 tervez
    await p.evaluate(() => {                               // telefon átadása
      const b = Array.from(document.querySelectorAll('#__g button')).find(x => /készen áll/.test(x.innerText || ''));
      if (b) b.click();
    });
    await p.waitForTimeout(500);
    await planOne();                                       // P2 tervez
    // leleplezés: körönként animál, a végén könyvel
    for (let i = 0; i < 40; i++) {
      if (await p.evaluate(() => window.__adv.length > 0)) break;
      await p.evaluate(() => {
        const b = Array.from(document.querySelectorAll('#__g button'))
          .find(x => /Tovább|Következő|Kész|Vége|Rendben/.test(x.innerText || '') && !x.disabled);
        if (b) b.click();
      });
      await p.waitForTimeout(500);
    }
  },

  // Ritmus: 2 × 30 mp ütemre koppintás. Az első körben (Anna) kopogunk a
  // nem-csapda mezőkre, a másodikban nem — így lesz nyertes és vesztes.
  async ritmus(p) {
    const startBtn = () => p.evaluate(() => {
      const b = Array.from(document.querySelectorAll('#__g button'))
        .find(x => /Indul|Start|Kezd|Mehet|Tovább|Következő|Rajt/i.test(x.innerText || '') && !x.disabled);
      if (b) { b.click(); return true; } return false;
    });
    await startBtn();
    // 1. kör — ~32 mp aktív koppintás
    for (let i = 0; i < 330; i++) {
      if (await p.evaluate(() => window.__adv.length > 0)) break;
      await p.evaluate(() => {
        const root = document.getElementById('__g');
        const cell = Array.from(root.querySelectorAll('button, div[style*="cursor: pointer"]'))
          .find(x => { const tx = (x.innerText || '').trim(); return tx.length > 0 && tx.length <= 3 && tx !== '💀'; });
        if (cell) cell.click();
      });
      await p.waitForTimeout(100);
      if (await p.evaluate(() => /készen áll|következik|Kezdés|Indul/i.test(document.getElementById('__g').innerText))) break;
    }
    await startBtn();                 // 2. kör indul — de nem koppintunk
    for (let i = 0; i < 90; i++) {
      if (await p.evaluate(() => window.__adv.length > 0)) break;
      await startBtn();
      await p.waitForTimeout(500);
    }
  },

  // Power Hour: 60 perc, percenként 1 korty. A teszt nem vár egy órát —
  // a másodperces időzítőt felgyorsítjuk (csak az 1000 ms-os intervallumot),
  // így a teljes óra ~15 mp alatt lefut és valódi (nem nulla) korty kerül könyvelésre.
  async powerhour(p) {
    await p.evaluate(() => {
      const si = window.setInterval.bind(window);
      window.setInterval = (fn, ms, ...a) => si(fn, ms === 1000 ? 4 : ms, ...a);
    });
    await p.evaluate(() => {
      const b = Array.from(document.querySelectorAll('#__g button')).find(x => /INDÍTÁS|Indít|Start/i.test(x.innerText || ''));
      if (b) b.click();
    });
    for (let i = 0; i < 120; i++) {
      if (await p.evaluate(() => window.__adv.length > 0)) break;
      await p.waitForTimeout(500);
    }
  },

  // Blackjack: tétek → osztás → mindenki megáll (Passz) → leosztás vége
  async blackjack(p) {
    const click = (re) => p.evaluate((re) => {
      const b = Array.from(document.querySelectorAll('#__g button')).find(x => new RegExp(re).test(x.innerText) && !x.disabled);
      if (b) { b.click(); return b.innerText.replace(/\n/g, '/').trim().slice(0, 24); } return null;
    }, re);
    await click('Lapok osztása');
    await p.waitForTimeout(900);
    // mindenki megáll (Stand), majd az osztó lejátssza a kezét
    for (let i = 0; i < 12; i++) {
      const did = await click('Stand');
      if (!did) break;
      await p.waitForTimeout(650);
    }
    await p.waitForTimeout(1200);
    // Eredmények: mindenki kiszáll — ekkor kerül át a korty/pont a bulira
    for (let i = 0; i < 14; i++) {
      if (await p.evaluate(() => window.__adv.length > 0)) break;
      const did = await click('Kiszáll');
      if (!did) await click('Vége|Lezár|Kész|Tovább');
      await p.waitForTimeout(600);
    }
  },
};

async function playOne(browser, gameId) {
  const p = await browser.newPage({ viewport: { width: 390, height: 900 } });
  const errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(() => { try { localStorage.setItem('boh_onboarded','1'); } catch(e){} });
  await p.goto('file:///home/user/bottle-of-heroes/index.html', { waitUntil:'domcontentloaded' });
  await p.waitForTimeout(3200);

  await p.evaluate(({ gameId, players, extraMeta }) => {
    window.__adv = []; window.__res = []; window.__live = [];
    const root = document.createElement('div'); root.id='__g';
    root.style.cssText = 'position:fixed;inset:0;overflow:auto;background:#F5D89B;z-index:99999;padding:8px';
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(window.GameContent, {
      gameId, gameIdx: 0, players,
      challenger: players[0], opponent: players[1],
      roomCode: null,
      gameMeta: { modes:['points','drinks'], difficulty:'easy',
                  beerpongConfig:{ tournamentType:'se', matchMinutes:0, visszavago:false, maxCups:10, mode:'egyeni' },
                  ...(extraMeta || {}) },
      onAdvance: (dm, pm, opts) => window.__adv.push({ dm: dm||{}, pm: pm||{}, opts: opts||null }),
      onResult:  (r) => { if (r) window.__res.push({
                    winners: (r.winners||[]).filter(Boolean).map(x=>x.id),
                    losers:  (r.losers ||[]).filter(Boolean).map(x=>x.id),
                    drinks: r.drinks ?? null, winNote: r.winNote || null, correct: r.correct ?? null }); },
      // A Blackjack (es tarsai) NEM az onAdvance-en konyvel, hanem elo korty-
      // frissitessel — ez ugyanugy a buli allasaba ir, tehat szamit.
      onUnready: ()=>{}, onLiveDrinkUpdate: (dm)=>{ if (dm) window.__live.push(dm); }, onSetHideFooter: ()=>{},
      onSetBuszSwitch: ()=>{}, onSetBpEnded: ()=>{}, onCommit: ()=>{},
    }));
  }, { gameId, players: PLAYERS, extraMeta: DRIVER_META[gameId] || null });
  await p.waitForTimeout(900);

  // Ha van saját driver ehhez a játékhoz, azt futtatjuk a generikus helyett
  if (DRIVERS[gameId]) {
    await DRIVERS[gameId](p);
    await p.waitForTimeout(800);
    const o = await p.evaluate(() => ({ adv: window.__adv, res: window.__res, live: window.__live, text: document.getElementById('__g').innerText.slice(0,120) }));
    await p.close();
    return { ...o, clicks: -1, errs };
  }

  // Generikus driver. Ha a képernyő szövege nem változik két kattintás után,
  // ráváltunk a rács-cellákra (Memória, Collect…).
  let clicks = 0, stuck = 0, lastText = '';
  for (let step = 0; step < 44; step++) {
    if (await p.evaluate(() => window.__adv.length > 0)) break;
    const did = await p.evaluate(({ pats, gridMode }) => {
      const root = document.getElementById('__g');
      const clickCells = () => {
        const cells = Array.from(root.querySelectorAll('div,button')).filter(el => {
          const r = el.getBoundingClientRect();
          return r.width >= 16 && r.width <= 80 && Math.abs(r.width - r.height) <= 8 && el.children.length <= 1;
        });
        if (!cells.length) return null;
        cells[Math.floor(Math.random() * cells.length)].click();
        return '#cella';
      };
      if (gridMode) { const c = clickCells(); if (c) return c; }
      const btns = Array.from(root.querySelectorAll('button, [role="button"], div[style*="cursor: pointer"]'))
        .filter(b => { const r = b.getBoundingClientRect(); return r.width > 8 && r.height > 8 && !b.disabled; });
      for (const pat of pats) {
        const rx = new RegExp(pat, 'i');
        const hit = btns.find(b => rx.test((b.innerText||'').trim()));
        if (hit) { hit.click(); return (hit.innerText||'').trim().slice(0,24); }
      }
      const names = ['Anna','Bela','Cili','Dani'];
      const nameHit = btns.find(b => names.includes((b.innerText||'').trim()));
      if (nameHit) { nameHit.click(); return '@' + (nameHit.innerText||'').trim(); }
      if (btns.length) { const t = btns[btns.length-1]; t.click(); return '·' + (t.innerText||'').trim().slice(0,20); }
      return clickCells();
    }, { pats: ADVANCE_PATTERNS, gridMode: stuck >= 2 });
    if (did) clicks++;
    await p.waitForTimeout(did ? 400 : 800);
    const now = await p.evaluate(() => document.getElementById('__g').innerText);
    if (now === lastText) stuck++; else { stuck = 0; lastText = now; }
    if (stuck > 14) break; // tényleg beragadt
  }
  await p.waitForTimeout(1200);

  const out = await p.evaluate(() => ({ adv: window.__adv, res: window.__res, live: window.__live, text: document.getElementById('__g').innerText.slice(0,120) }));
  await p.close();
  return { ...out, clicks, errs };
}

// A banner (onResult) és a könyvelés (onAdvance) egyezésének ellenőrzése
function check(gameId, r) {
  const problems = [];
  if (ONLINE_ONLY[gameId]) return { status:'CSAK_ONLINE', problems, note: ONLINE_ONLY[gameId] };
  const live = r.live || [];
  if (!r.adv.length && !live.length) return { status:'NEM_JATSZHATO', problems,
    note: r.clicks < 0 ? 'a saját driver sem jutott el a könyvelésig' : `${r.clicks} kattintás után sem könyvelt` };
  const pm = {}, dm = {};
  r.adv.forEach(a => {
    Object.entries(a.pm).forEach(([k,v]) => pm[k] = (pm[k]||0) + v);
    Object.entries(a.dm).forEach(([k,v]) => dm[k] = (dm[k]||0) + v);
  });
  // elo korty-konyveles (onLiveDrinkUpdate) — ugyanugy a buli allasaba megy
  live.forEach(m => Object.entries(m).forEach(([k,v]) => dm[k] = (dm[k]||0) + v));
  const res = r.res.filter(x => x.winners.length || x.losers.length);
  res.forEach(x => {
    // győztest hirdet + pontot ígér -> kapjon is pontot
    const promisesPoint = x.winNote && /pont/i.test(x.winNote);
    if (x.winners.length && promisesPoint) {
      const missing = x.winners.filter(id => !(pm[id] > 0));
      if (missing.length) problems.push(`a banner "${x.winNote}"-ot ígér ${x.winners.join(',')}-nak, de a pontok: ${JSON.stringify(pm)}`);
    }
    // vesztest hirdet + kortyot ígér -> kapjon is kortyot
    if (x.losers.length && (x.drinks == null || x.drinks > 0)) {
      const missing = x.losers.filter(id => !(dm[id] > 0));
      if (missing.length) problems.push(`a banner ${x.losers.join(',')}-t iszásra ítéli, de a kortyok: ${JSON.stringify(dm)}`);
    }
  });
  Object.entries(pm).forEach(([k,v]) => { if (v < 0) problems.push(`negatív pont: ${k}=${v}`); });
  // Külön regresszió-őr: a Busz offline is végigosztott kortyokat a buszúton
  // (v10.145-ig ezek eltűntek — csak a profil-statba mentek, a buli állásába nem).
  if (gameId === 'busz' && !Object.keys(dm).length) {
    problems.push('a buszút kortyai nem kerültek a buli állásába (offline eldobott korty-térkép)');
  }
  return { status: problems.length ? 'HIBA' : 'OK', problems, pm, dm, nRes: res.length };
}

(async () => {
  const only = process.argv.slice(2);
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  // játéklista az appból
  const p0 = await browser.newPage({ viewport:{ width:390, height:844 } });
  await p0.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p0.addInitScript(stub);
  await p0.addInitScript(() => { try { localStorage.setItem('boh_onboarded','1'); } catch(e){} });
  await p0.goto('file:///home/user/bottle-of-heroes/index.html', { waitUntil:'domcontentloaded' });
  await p0.waitForTimeout(3500);
  let ids = await p0.evaluate(() => (window.GAMES||[]).map(g => g.id));
  await p0.close();
  if (only.length) ids = ids.filter(x => only.includes(x));
  console.log(`${ids.length} játék\n`);

  const buckets = { OK: [], HIBA: [], NEM_JATSZHATO: [], CSAK_ONLINE: [], CRASH: [] };
  for (const id of ids) {
    let r, c;
    try { r = await playOne(browser, id); c = check(id, r); }
    catch (e) { buckets.CRASH.push([id, e.message]); console.log(`  ${id.padEnd(14)} CRASH ${e.message.slice(0,60)}`); continue; }
    if (r.errs.length) c.problems.push('konzolhiba: ' + r.errs[0].slice(0,70));
    if (r.errs.length && c.status === 'OK') c.status = 'HIBA';
    buckets[c.status].push([id, c]);
    const tag = c.status === 'OK' ? '✓' : c.status === 'HIBA' ? '✗' : '–';
    console.log(`  ${tag} ${id.padEnd(14)} ${c.status.padEnd(14)} pont=${JSON.stringify(c.pm||{})} korty=${JSON.stringify(c.dm||{})}${c.note ? '  ' + c.note : ''}`);
    c.problems.forEach(pr => console.log(`      → ${pr}`));
  }

  console.log(`\n==== ÖSSZEGZÉS ====`);
  console.log(`  OK:            ${buckets.OK.length}`);
  console.log(`  HIBA:          ${buckets.HIBA.length}  ${buckets.HIBA.map(x=>x[0]).join(', ')}`);
  console.log(`  nem játszható: ${buckets.NEM_JATSZHATO.length}  ${buckets.NEM_JATSZHATO.map(x=>x[0]).join(', ')}`);
  console.log(`  csak online:   ${buckets.CSAK_ONLINE.length}  ${buckets.CSAK_ONLINE.map(x=>x[0]).join(', ')}`);
  console.log(`  crash:         ${buckets.CRASH.length}  ${buckets.CRASH.map(x=>x[0]).join(', ')}`);
  await browser.close();
  process.exit(buckets.HIBA.length ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(2); });
