#!/usr/bin/env python3
# v10.228 — a holt-zóna korrekciója MÉRT érték legyen, ne feltételezett
#
# A v10.227 túllőtt: a "Tovább a játékokhoz" gomb kilóg a kijelző aljáról.
# Kimérve a két készülék-képen:
#   - a fejléc/tartalom teteje EGYIK verzióban sem mozdult (fehér sáv 0-129pt)
#   - a gomb alja viszont 777pt-ról ~901pt-ra ment (a kijelző 874pt)
# vagyis a konténer nem +62pt-tal, hanem gyakorlatilag +124pt-tal lett
# magasabb. A feltételezésem tehát — hogy a hiány PONTOSAN
# env(safe-area-inset-top) — hibás; a képletből nem jön ki konzisztensen.
#
# Ezért nem tippelek tovább: a korrekciót FUTÁSIDŐBEN MÉRJÜK a készüléken —
# mennyivel rövidebb a látható terület (window.innerHeight) a fizikai
# kijelzőnél (screen.height). Ez pontosan az a hiány, amit pótolni kell,
# és magától helyes marad akkor is, ha az iOS viselkedése változik.
#
# Csak telepített (standalone) módban aktív; böngészőben 0 marad (ott az
# innerHeight a böngésző-sávok miatt amúgy is kisebb, az nem holt-zóna).
# Felső korlát 200px, hogy egy váratlan érték se tudja szétdobni a layoutot.
#
# Emellé egy apró diagnosztika a Beállítások lap aljára: ha még mindig nem
# stimmel, egyetlen képernyőképből látszanak a VALÓDI számok, ahelyett hogy
# újabb köröket találgatnánk.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─── 1) a fejléc-szkript: mért korrekció a feltételezett env-top helyett ───
sub("""  <!-- Telepitett (standalone) mod jelzese a <html>-en: ettol fugg a --app-vh-fix
       korrekcio, ami a black-translucent PWA alsó holt-zonajat szunteti meg. -->
  <script>(function(){try{var s=window.navigator.standalone===true||(window.matchMedia&&window.matchMedia('(display-mode: standalone)').matches);if(s)document.documentElement.classList.add('pwa-standalone');}catch(e){}})();</script>""",
    """  <!-- Telepitett (standalone) PWA-ban a lathato terulet (innerHeight) rovidebb
       lehet a fizikai kijelzonel (screen.height) - alul holt-zona marad. A
       hianyt MEGMERJUK (nem feltetelezzuk, hogy env-top-tal egyenlo), es
       --app-vh-fix-kent adjuk vissza a teljes kepernyos elemek magassagahoz.
       Bongeszoben 0: ott az innerHeight a bongeszo-savok miatt kisebb, az nem
       holt-zona. -->
  <script>(function(){
    function upd(){
      try{
        var st = window.navigator.standalone===true ||
                 (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches);
        if(st) document.documentElement.classList.add('pwa-standalone');
        else   document.documentElement.classList.remove('pwa-standalone');
        var d = 0;
        if(st && window.screen && window.screen.height)
          d = Math.round(window.screen.height - window.innerHeight);
        if(!(d > 0) || d > 200) d = 0;   // csak pozitiv, ertelmes hiany
        document.documentElement.style.setProperty('--app-vh-fix', d + 'px');
        window.__bohVh = { standalone: !!st, screenH: (window.screen||{}).height,
                           innerH: window.innerHeight, fix: d };
      }catch(e){}
    }
    upd();
    window.addEventListener('resize', upd);
    window.addEventListener('orientationchange', function(){ setTimeout(upd, 250); });
  })();</script>""",
    'mert korrekcio')

# ─── 2) a CSS-ben már ne env-top legyen a class-hoz kötve (JS állítja) ───
sub("""    :root { --app-vh-fix: 0px; }
    html.pwa-standalone { --app-vh-fix: env(safe-area-inset-top); }""",
    """    :root { --app-vh-fix: 0px; }   /* erteket a fejlecben futo szkript meri es allitja be */""",
    'css valtozo alapertek')

# ─── 3) diagnosztika a Beállítások lap aljára ───
sub("""                <Toggle on={sndOn} onChange={toggleSnd} />
              </div>

            </div>
          </SheetOverlay>""",
    """                <Toggle on={sndOn} onChange={toggleSnd} />
              </div>

              {/* Ideiglenes diagnosztika a PWA-s safe-area hibakereseshez.
                  Ha a layout jo, ez kikerul. */}
              {(() => {
                const v = (typeof window !== 'undefined' && window.__bohVh) || {};
                const envTop = (() => { try {
                  const p = document.createElement('div');
                  p.style.cssText = 'position:fixed;top:0;height:env(safe-area-inset-top);visibility:hidden';
                  document.body.appendChild(p);
                  const h = Math.round(p.getBoundingClientRect().height);
                  p.remove(); return h;
                } catch (e) { return '?'; } })();
                return (
                  <div style={{ marginTop:20, paddingTop:12, borderTop:`1px solid ${T.inkMute}22`,
                                fontFamily:'monospace', fontSize:10.5, color:T.inkMute, lineHeight:1.6 }}>
                    {APP_VERSION} · {v.standalone ? 'PWA' : 'böngésző'}<br/>
                    screen={String(v.screenH)} inner={String(v.innerH)} fix={String(v.fix)}px envTop={String(envTop)}px
                  </div>
                );
              })()}

            </div>
          </SheetOverlay>""",
    'diagnosztika')

sub("const APP_VERSION = 'v10.227';", "const APP_VERSION = 'v10.228';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — mert korrekcio + diagnosztika a Beallitasokban')
