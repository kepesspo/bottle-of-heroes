#!/usr/bin/env python3
# v10.278 — a Collect & Boom tablajan pontosan annyi korty fekszik, amennyi a max
#
# A BEJELENTETT HIBA
#   6×6-os racs, "Max korty: 12". A jatekos +2, +2, +3, +1, +1, +1, +3, +2 =
#   15 kortyot fordított fel, a szamlalo mégis 12/12-n allt meg. A tobblet
#   elveszett: felfedtel egy +3-at, es nem tortent semmi.
#
# AZ OK
#   Ket, egymasrol nem tudo szabaly:
#     * a TABLA feltoltese: `drinkCount = floor(szabad_mezok * 0.5)` darab
#       korty-mezo, 3/2/1 ertekekkel — ez 6×6-nal 32 korty osszerteket jelent;
#     * a POT viszont `Math.min(pot + ertek, MAX_POT)`-tal vag, es a MAX_POT 12.
#   Vagyis a tabla 32-t igert, a jatek 12-t adott. A kulonbseg nemán elveszett,
#   es minel nagyobb a racs, annal nagyobb a szakadek.
#
# A JAVITAS
#   A tablara PONTOSAN MAX_POT osszerteku korty kerul. Az ertekeket 3-2-1
#   ciklusban osztjuk ki, amig el nem fogy a keret — igy megmarad a valtozatossag
#   (nem csupa +1), es a vegosszeg garantaltan stimmel.
#
#   Ezzel a "GYUJTVE n / MAX" kijelzo is igazat mond: ha MINDEN korty-mezot
#   felfedsz, pont a maximumon allsz. A `Math.min(..., MAX_POT)` vagas bent
#   marad ovintezkedesnek, de tobbe nem kell hasznalnia.
#
# MELLEKHATAS, AMIT TUDNI KELL
#   A korty-mezok SZAMA a plafonhoz igazodik, tehat kevesebb lesz, mint eddig:
#     4×4 (max 4)  : 2 mezo   (eddig 7)
#     5×5 (max 8)  : 4 mezo   (eddig 11)
#     6×6 (max 12) : 6 mezo   (eddig 17)
#   A tobbi szabad mezo csillag lesz. Ez kovetkezmenye annak, hogy a plafon
#   4/8/12-re ment le — ha surubb tabla kell, a plafont kell emelni.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""  const grid = React.useMemo(() => {
    const safeCount = TOTAL - BOMB_COUNT;
    const drinkCount = Math.floor(safeCount * 0.5);
    const trueySafeCount = safeCount - drinkCount;
    const cells = [
      ...Array(BOMB_COUNT).fill({type:'bomb'}),
      ...Array(Math.floor(drinkCount/3)).fill({type:'drink',v:3}),
      ...Array(Math.floor(drinkCount/3)).fill({type:'drink',v:2}),
      ...Array(drinkCount - Math.floor(drinkCount/3) - Math.floor(drinkCount/3)).fill({type:'drink',v:1}),
      ...Array(trueySafeCount).fill({type:'safe'}),
    ];""",
    """  const grid = React.useMemo(() => {
    const safeCount = TOTAL - BOMB_COUNT;
    // A tablara PONTOSAN MAX_POT osszerteku korty kerul.
    //
    // Korabban a mezok SZAMA volt megadva (a szabad mezok fele), az ertekek meg
    // 3/2/1 — ez 6×6-nal 32 korty osszerteket jelentett, mikozben a pot 12-nel
    // vag. A tobblet nemán elveszett: felfedtel egy +3-at, es nem tortent semmi.
    // Most a keret a MAX_POT, es 3-2-1 ciklusban osztjuk szet, hogy ne csupa
    // +1 legyen. Igy ha minden korty-mezot felfedsz, pont a maximumon allsz.
    const drinkVals = [];
    let left = MAX_POT;
    while (left > 0) {
      const want = [3, 2, 1][drinkVals.length % 3];
      const v = Math.min(want, left);
      drinkVals.push(v);
      left -= v;
    }
    const trueySafeCount = Math.max(0, safeCount - drinkVals.length);
    const cells = [
      ...Array(BOMB_COUNT).fill({type:'bomb'}),
      ...drinkVals.map(v => ({type:'drink', v})),
      ...Array(trueySafeCount).fill({type:'safe'}),
    ];""",
    'grid feltoltes')

# a MAX_POT-nak szerepelnie kell a useMemo fuggosegei kozott, kulonben
# racsmeret-valtaskor a regi tabla maradna
sub("""  }, [gameIdx, COLS, BOMB_COUNT]);""",
    """  }, [gameIdx, COLS, BOMB_COUNT, MAX_POT]);""",
    'useMemo fuggoseg')

sub("const APP_VERSION = 'v10.277';", "const APP_VERSION = 'v10.278';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — a tabla osszerteke = MAX_POT')
