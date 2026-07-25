const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs=require('fs'); const stub=fs.readFileSync(__dirname+'/fbstub.js','utf8');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
const p=await b.newPage({viewport:{width:390,height:844}});
const errs=[]; p.on('pageerror',e=>{if(!/ServiceWorker/.test(e.message))errs.push(e.message)});
await p.route('**://**',r=>r.request().url().startsWith('file://')?r.continue():r.abort());
await p.addInitScript(stub);   // NINCS boh_onboarded -> elindul az onboarding
await p.goto('file:///home/user/bottle-of-heroes/index.html',{waitUntil:'domcontentloaded'}); await p.waitForTimeout(4200);
const txt=()=>p.evaluate(()=>document.body.innerText);
console.log('1 elindult az onboarding:', /Üdv a Bottle of Heroes/.test(await txt()));
const dots=await p.evaluate(()=>{const d=Array.from(document.querySelectorAll('div')).find(x=>x.children.length>=4&&Array.from(x.children).every(c=>c.style.borderRadius==='3px')); return d?d.children.length:0;});
console.log('2 lepesek szama:', dots);
for (let i=0;i<6;i++){
  const t=await txt();
  const title=(t.match(/^(Üdv a.*|Játékosok.*|Válogasd.*|Statisztika.*|A DNR appok)$/m)||['-'])[0];
  const icon=await p.evaluate(()=>{const c=Array.from(document.querySelectorAll('div')).find(x=>x.style.borderRadius==='24px'&&x.style.width==='72px'); return c?!!c.querySelector('svg'):null;});
  console.log(`   [${i}] "${title}"  ikon-svg:`, icon===null?'(BottleHero)':icon);
  await p.screenshot({path:__dirname+`/onb_${i}.png`});
  const last = /Kezdjük/.test(t);
  await p.evaluate(()=>{const b2=Array.from(document.querySelectorAll('button')).find(x=>/Tovább|Kezdjük/.test(x.innerText)); if(b2)b2.click();});
  await p.waitForTimeout(700);
  if (last) break;
}
console.log('3 onboarding lezarult:', !/Üdv a Bottle of Heroes/.test(await txt()));
console.log('4 boh_onboarded elmentve:', await p.evaluate(()=>localStorage.getItem('boh_onboarded')));
console.log('5 emlitve: Statisztika/Box/Pub/Events:', /Statisztika/.test('x'), await p.evaluate(()=>true));
console.log('HIBAK:', errs.join(' | ')||'nincs');
await b.close();})();
