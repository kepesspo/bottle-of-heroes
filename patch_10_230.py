#!/usr/bin/env python3
# v10.230 — a korrekció csak a KONKRÉT iOS-hibára aktiválódjon (device-független)
#
# Jogos kérdés: "ez minden készüléken jó lesz?" — a v10.229 úgy, ahogy volt,
# NEM. A screen.height a fizikai kijelzőt adja, ami csak teljes képernyős
# appnál egyezik az ablak magasságával. iPad Split View / Stage Manager,
# Android multi-window, fekvő tájolás esetén rossz értéket adott volna; a
# 200px-es korlát csak durva védőháló volt.
#
# Ezért mostantól ALÁÍRÁS-ELLENŐRZÉS dönt: a korrekciót csak akkor
# alkalmazzuk, ha a hiány PONTOSAN a felső safe-area méretével egyezik —
#     screen.height - innerHeight  ==  env(safe-area-inset-top)
# mert ez az iOS black-translucent holt-zóna egyedi ujjlenyomata (a webnézet
# a kijelző tetejétől indul, de a layout-viewport a státuszsáv magasságával
# rövidebb). Minden más helyzetben — ablakos mód, osztott képernyő, fekvő
# tájolás, Android, böngésző — az aláírás nem áll, korrekció sincs, és marad
# a szokásos 100dvh.
#
# Így a javítás célzott: ott hat, ahol a hiba van, máshol egyáltalán nem tud
# elrontani semmit.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""        // Telepitett modban a teljes kepernyos magassag = a FIZIKAI kijelzo
        // magassaga. Abszolut, mert ertek: nem fugg attol, hogy az iOS mit ert
        // 100dvh alatt (az verziorol verziora mast adott). Bongeszoben nem
        // allitjuk be -> a CSS 100dvh tartalek lep eletbe, ott az a helyes.
        var sh = (window.screen && window.screen.height) || 0;
        var ok = st && sh > 0 && sh >= window.innerHeight && sh - window.innerHeight <= 200;
        if(ok) document.documentElement.style.setProperty('--app-h', sh + 'px');
        else   document.documentElement.style.removeProperty('--app-h');
        window.__bohVh = { standalone: !!st, screenH: sh, innerH: window.innerHeight,
                           appH: ok ? sh : null };""",
    """        // A felso safe-area tenyleges merete (probaelem, mert JS-bol nem
        // olvashato kozvetlenul).
        var envTop = 0;
        try{
          var pr = document.createElement('div');
          pr.style.cssText = 'position:fixed;top:0;left:0;width:0;visibility:hidden;height:env(safe-area-inset-top)';
          document.documentElement.appendChild(pr);
          envTop = Math.round(pr.getBoundingClientRect().height);
          pr.parentNode.removeChild(pr);
        }catch(e){}

        // ALAIRAS-ELLENORZES. Az iOS black-translucent holt-zona egyedi
        // ujjlenyomata: a webnezet a kijelzo tetejetol indul, de a
        // layout-viewport PONTOSAN a statuszsav magassagaval rovidebb, igy
        // alul ugyanannyi hasznalhato keppont kimarad. Csak ekkor korrigalunk.
        // Ablakos mod / osztott kepernyo / fekvo tajolas / Android / bongeszo:
        // az alairas nem all -> nincs korrekcio, marad a 100dvh.
        var sh = (window.screen && window.screen.height) || 0;
        var deficit = sh - window.innerHeight;
        var ok = st && envTop > 0 && deficit > 0 && Math.abs(deficit - envTop) <= 2;
        if(ok) document.documentElement.style.setProperty('--app-h', sh + 'px');
        else   document.documentElement.style.removeProperty('--app-h');
        window.__bohVh = { standalone: !!st, screenH: sh, innerH: window.innerHeight,
                           envTop: envTop, deficit: deficit, appH: ok ? sh : null };""",
    'alairas-ellenorzes')

# a diagnosztika mutassa az aláírás-egyezést is
sub("""                    screen={String(v.screenH)} inner={String(v.innerH)} 100dvh={String(dvh)}<br/>
                    appH={String(v.appH)} envTop={String(envTop)} envBot={String(envBot)}""",
    """                    screen={String(v.screenH)} inner={String(v.innerH)} 100dvh={String(dvh)}<br/>
                    hiány={String(v.deficit)} envTop={String(envTop)} envBot={String(envBot)}<br/>
                    korrekció={v.appH ? 'BE (' + v.appH + 'px)' : 'KI'}""",
    'diagnosztika alairas')

sub("const APP_VERSION = 'v10.229';", "const APP_VERSION = 'v10.230';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — korrekcio csak a konkret iOS-alairasra')
