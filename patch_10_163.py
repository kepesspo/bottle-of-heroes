# v10.163 — "A JÁTÉKOK BEÁLLÍTÁSAI" felirat kikerul
#
# Ugyanaz az indok, mint a "Jatekmenet" feliratnal: a jatek-sorok magukert
# beszelnek (nev + "Beallitasok megnyitasa" + nyil), a fejlec csak helyet vitt.
# A magyarazo alcim is megy vele — fejlec nelkul egy magaban allo magyarazo
# mondat rosszabb, mint a semmi, es ugyanazt mondja, amit a sorok.
#
# Az URES eset szovege MARAD: ha egyetlen kivalasztott jateknak sincs sajat
# beallitasa, azt meg kell mondani, kulonben a felhasznalo hianyt gyanit.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

old = """        <Section title="A játékok beállításai"
          sub={configurable.length
            ? 'Ezeknek a kiválasztott játékoknak van saját beállítása.'
            : undefined}>
          {configurable.length === 0 ? ("""
new = """        {/* Fejléc nélkül: a játék-sorok magukért beszélnek. */}
        <div style={{ marginTop:12 }}>
          {configurable.length === 0 ? ("""
assert s.count(old) == 1
s = s.replace(old, new)

# a szekcio zarasa
old_end = """              ))}
            </div>
          )}
        </Section>"""
new_end = """              ))}
            </div>
          )}
        </div>"""
assert s.count(old_end) == 1
s = s.replace(old_end, new_end)

s = s.replace("const APP_VERSION = 'v10.162';", "const APP_VERSION = 'v10.163';", 1)
assert "v10.163" in s and s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK')
