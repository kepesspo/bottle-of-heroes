#!/usr/bin/env python3
# v10.216 — MENÜ > Vezérlés akciósor: egységes gombok
#
# A Büntetés gomb v10.215-ben ikon-csak negyzet lett (52x52, fix szeles),
# mig a tobbi harom (Vissza/Ujra/Kovetkezo) ikon+szoveg, flex:1/1/2 aranyban
# — emiatt a Buntetes kilogott a sorbol. Most mind a negy gomb ikon+szoveg,
# egyenlo flex:1 szelessegu.
#
# Hogy ez beferjen, a "Kovetkezo" felirat "Kövi"-re rovidult — ez mar
# amugy is a hivatalos rovid alak (lasd a play-footer sajat Kövi gombjat,
# t('next') = 'Kövi'); a nextBtn kulcs eddig csak itt, a menu-ben elte a
# hosszu valtozatot.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("    nextBtn: 'Következő',", "    nextBtn: 'Kövi',", 'nextBtn rovidites')

sub("""                  <button onClick={() => { setShowMenu(false); setPenaltyOpen(true); }} title="Büntetés — ki igyon?"
                    style={{ width:52, height:52, flexShrink:0, border:'none', borderRadius:16, background:`linear-gradient(135deg, #7C5CC4, #A78BFA)`, color:'#fff', cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', boxShadow:'0 4px 14px rgba(124,92,196,0.44)' }}>
                    <BohIcon name="beer" size={19} />
                  </button>""",
    """                  <button onClick={() => { setShowMenu(false); setPenaltyOpen(true); }}
                    style={{ flex:1, height:52, border:'none', borderRadius:16, background:`linear-gradient(135deg, #7C5CC4, #A78BFA)`, color:'#fff',
                      fontFamily:T.font, fontWeight:800, fontSize:14, cursor:'pointer',
                      display:'flex', alignItems:'center', justifyContent:'center', gap:7,
                      boxShadow:'0 4px 14px rgba(124,92,196,0.44)' }}>
                    <BohIcon name="beer" size={17} /><span>Büntetés</span>
                  </button>""",
    'Buntetes gomb szoveggel + flex:1')

sub("""                  <button onClick={() => { setGameIdx(g=>g+1); setShowMenu(false); }}
                    style={{ flex:2, height:52, border:'none', borderRadius:16,""",
    """                  <button onClick={() => { setGameIdx(g=>g+1); setShowMenu(false); }}
                    style={{ flex:1, height:52, border:'none', borderRadius:16,""",
    'Kovi flex 2 -> 1')

sub("const APP_VERSION = 'v10.215';", "const APP_VERSION = 'v10.216';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — akciosor: 4 egyenlo, egyseges gomb')
