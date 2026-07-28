# v10.162 — a Jatekmenet oldal atrendezese + a hangos musorvezeto kivezetese
#
# A visszajelzes: a "Jatekmenet" felirat felesleges a torzsben (a fejlecben mar
# ott van), a beallitasok kapjanak KULON feher dobozokat, a nehezseg/sorrend/
# korok kerulyon egy kozos dobozba, a hangos musorvezeto pedig menjen ki.
#
# A GameSettingsContent eddig egyetlen lapos lista volt, ezert nem lehetett
# csoportokra bontani. Most `group` proppal kerheto belole egy-egy szelet — a
# regi folyamat lapja tovabbra is prop nelkul, egyben rendereli.
import io, re

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# ── 1) hangos musorvezeto: a kapcsolo ──
tts_toggle = """      <ToggleRow
        icon="party"
        label="Hangos műsorvezető"
        value={!!meta.ttsHost}
        onChange={() => {
          const next = !meta.ttsHost;
          setMeta({...meta, ttsHost: next});
          // Bekapcsoláskor egy koppintáson belül megszólal → iOS-en is feloldja a beszédet
          if (next && typeof window.bohSpeak === 'function') window.bohSpeak('Műsorvezető bekapcsolva!');
        }}
        infoKey="ttshost"
"""
i = s.find(tts_toggle)
assert i > 0, 'nincs meg a ttsHost kapcsolo'
j = s.find('/>', s.find('infoText=', i)) + 3
s = s[:i] + s[j:]

# ── 2) a jatek kozbeni hivasok (mind `gameMeta?.ttsHost` ala vannak zarva) ──
# egysoros esetek
one_liners = len(re.findall(r"^\s*if \(gameMeta\?\.ttsHost && typeof window\.bohSpeak === 'function'\).*\n", s, re.M))
s = re.sub(r"^\s*if \(gameMeta\?\.ttsHost && typeof window\.bohSpeak === 'function'\).*\n", '', s, flags=re.M)
assert one_liners == 4, f'egysoros ttsHost hivas: {one_liners} (4 kellene)'

# a hosszabb blokk a kor vegen
block_start = s.find("    if (gameMeta?.ttsHost && typeof window.bohSpeak === 'function') {")
assert block_start > 0, 'nincs meg a kor vegi ttsHost blokk'
block_end = s.find("\n    }\n", block_start) + len("\n    }\n")
s = s[:block_start] + s[block_end:]
assert 'ttsHost' not in s, 'maradt ttsHost hivatkozas'

# ── 3) a bohSpeak segeddel egyutt megy — nem maradhat halott kod ──
sp_start = s.find('window.bohSpeak = (function () {')
assert sp_start > 0
sp_end = s.find('})();\n', sp_start) + len('})();\n')
s = s[:sp_start] + s[sp_end:]
assert 'bohSpeak' not in s, 'maradt bohSpeak hivatkozas'

io.open(P, 'w', encoding='utf-8').write(s)
print('OK — hangos musorvezeto kivezetve (kapcsolo + 5 hivas + a segedfuggveny)')
