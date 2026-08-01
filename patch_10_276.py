#!/usr/bin/env python3
# v10.276 — a tet-korong ne hazudjon a konfiguralhato jatekoknal
#
# A BEJELENTETT HIBA
#   Collect and Boom, 5×5 racs, Nehez (×3): a korong "3–9 KORTY"-ot irt, a
#   jatekos viszont 24 kortyot kapott.
#
# AZ OK
#   A `stake` a v10.257 ota DEKLARALT konstans — beirt szam, nem a jatek
#   logikajabol szarmaztatva. Amig minden jatek fix kortyot osztott, ez mukodott.
#   A halmozo/konfiguralhato jatekoknal viszont szuksegszeruen hazudik:
#   a Collect potja `Math.min(pot + cellaertek, MAX_POT)`-ig no, es a MAX_POT a
#   RACSMERETTOL fugg (10 / 15 / 20). 5×5-nel tehat a valodi tartomany 1–15,
#   nem 1–3 — ×3 nehezseggel 3–45, nem 3–9.
#
# A MEGOLDAS: a `stake` lehet FUGGVENY is
#   Uj, opcionalis `stakeOf(gameMeta)` mezo a jateknal. Ha van, a tet-korong
#   ebbol szamol; ha nincs, marad a regi `stake` par. Igy csak az az egy-ket
#   jatek valtozik, ahol tenyleg kell.
#
# MELYIK JATEKNAL MI LETT
#
#   VAN VALODI FELSO HATAR -> pontos szarmaztatas:
#     * collect    — a kod `Math.min(..., MAX_POT)`-tal vag. A hatar
#                    racsmeretenkent 10/15/20. Ez ELERHETO ertek.
#     * cardbattle — a korty a gyozelmi kulonbseg, ami legfeljebb a KOROK
#                    SZAMA lehet (ha az egyik fel mindent visz). Ez is elerheto.
#
#   NINCS FELSO HATAR -> a szam helyett INKABB SEMMI (stake: null):
#     * meduza  — a koronkenti kortyot EMBER osztja ki (DrinkDistributor),
#                 korlat nelkul, es ez halmozodik a korokon at;
#     * kisebb  — a pot `+1` VAGY `×2` a sorozat-modtol fuggoen, tehat
#                 exponencialisan no; csak a pakli hossza korlatozza;
#     * ritmus  — a korty a ket pontszam kulonbsege egy idozitett jatekban,
#                 ahol a pontszam a koppintasok szama. Nincs felso hatar.
#     * utveszto— a vesztes a bejart csapdak ara + 2. Elmeleti maximum
#                 letezik (3 × csapdaszam + 2), de az annyira messze van a
#                 tipikustol, hogy kiirva UJ torzitas lenne.
#
#   Ezeknel a korong most a KOR-gyurut mutatja (ez a v10.270 ota mukodo
#   tartalek a tet nelkuli jatekoknal). Jobb semmit mutatni, mint rossz szamot.
#   Ha kesobb kapnak valodi plafont — ugy, ahogy a Collect-nek van MAX_POT-ja —,
#   egy `stakeOf` sorral visszakerulnek.
#
# EGY FORRAS A MAX_POT-NAK
#   A `MAX_POT_MAP` eddig KETSZER volt leirva (a config-lapon es a jatekban),
#   ugyanazokkal a szamokkal. Most egy kozos `COLLECT_MAX_POT` van, amit a
#   config-lap, a jatek ES a tet-korong is ebbol olvas — kulonben harom helyen
#   kellene kezzel szinkronban tartani.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─────────────────────────────────────────────────────────────────────────────
# 1. EGY forras a Collect plafonjanak (eddig ketszer volt leirva)
# ─────────────────────────────────────────────────────────────────────────────
sub("""const WILDCARD_RANGES = [""",
    """// A Collect & Boom potja HARD CAP-pel no: `Math.min(pot + cellaertek, MAX_POT)`.
// Ez a plafon racsmeretenkent. EGY forras: a config-lap, a jatek es a
// tet-korong (`stakeOf`) is innen olvassa — kulonben harom helyen kellene
// kezzel szinkronban tartani.
const COLLECT_MAX_POT = { 4: 10, 5: 15, 6: 20 };

const WILDCARD_RANGES = [""",
    'COLLECT_MAX_POT')

sub("""  const MAX_POT_MAP = { 4: 10, 5: 15, 6: 20 };
  const Stepper = ({ value, min, max, onChange }) => (""",
    """  const MAX_POT_MAP = COLLECT_MAX_POT;
  const Stepper = ({ value, min, max, onChange }) => (""",
    'config lap MAX_POT')

sub("""  const MAX_POT_MAP = { 4: 10, 5: 15, 6: 20 };
  const MAX_POT = MAX_POT_MAP[COLS] ?? 10;""",
    """  const MAX_POT_MAP = COLLECT_MAX_POT;
  const MAX_POT = MAX_POT_MAP[COLS] ?? 10;""",
    'jatek MAX_POT')

# ─────────────────────────────────────────────────────────────────────────────
# 2. A tet-korong tudjon fuggvenybol is szamolni
# ─────────────────────────────────────────────────────────────────────────────
sub("""  const stakeBase = trackScores ? (currentGame?.stake || null) : null;""",
    """  // A `stake` lehet fix par VAGY fuggveny (`stakeOf`). A konfiguralhato,
  // halmozo jatekoknal a fix szam hazudik: a Collect potja a racsmerettol
  // fuggo MAX_POT-ig no, a Kartyacsatae a korok szamaig. Lasd patch_10_276.py
  const stakeBase = !trackScores ? null
    : (typeof currentGame?.stakeOf === 'function'
        ? (currentGame.stakeOf(gameMeta || {}) || null)
        : (currentGame?.stake || null));""",
    'stakeOf hasznalat')

# ─────────────────────────────────────────────────────────────────────────────
# 3. A ket jatek, aminek VAN valodi plafonja
# ─────────────────────────────────────────────────────────────────────────────
sub("""{ id:'collect', stake:[1,3],   roundTime:'mid',""",
    """{ id:'collect', stake:[1,3], stakeOf:(m)=>[1, COLLECT_MAX_POT[m?.collectConfig?.gridSize ?? 4] ?? 10],   roundTime:'mid',""",
    'collect stakeOf')

import re
m = re.search(r"\{ id:'cardbattle', stake:\[1,3\],", src)
assert m, 'cardbattle stake nem talalhato'
src = src.replace("{ id:'cardbattle', stake:[1,3],",
                  "{ id:'cardbattle', stake:[1,3], stakeOf:(m)=>[1, m?.cardbattleConfig?.rounds || 5],", 1)

# ─────────────────────────────────────────────────────────────────────────────
# 4. Amiknek NINCS plafonjuk: inkabb semmi, mint rossz szam
# ─────────────────────────────────────────────────────────────────────────────
for gid, regi in [('meduza', '[1,3]'), ('kisebb', '[1,4]'), ('ritmus', '[1,3]'), ('utveszto', '[1,1]')]:
    old = "{ id:'%s', stake:%s," % (gid, regi)
    assert src.count(old) == 1, '%s: %d talalat' % (gid, src.count(old))
    src = src.replace(old, "{ id:'%s', stake:null," % gid, 1)

sub("const APP_VERSION = 'v10.275';", "const APP_VERSION = 'v10.276';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — collect/cardbattle szarmaztatva, 4 hatartalan jatek stake:null')
