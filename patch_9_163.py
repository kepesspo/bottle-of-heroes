#!/usr/bin/env python3
"""patch_9_163.py — szamsor/reakcio/ritmus: explicit SCENARIOS cta:[] bejegyzés"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.162';" in content
content = content.replace("const APP_VERSION = 'v9.162';", "const APP_VERSION = 'v9.163';")

OLD_SCENARIOS = "  erem:      { prompt:'Fej vagy írás — döntsétek el, ki iszik!', cta:[] },\n  tapper:    { prompt:'Tegyétek az ujjatokat a gombra — automatikusan elindul. Aki hamarabb engedi el, iszik!', cta:[] },"
NEW_SCENARIOS = """  erem:      { prompt:'Fej vagy írás — döntsétek el, ki iszik!', cta:[] },
  tapper:    { prompt:'Tegyétek az ujjatokat a gombra — automatikusan elindul. Aki hamarabb engedi el, iszik!', cta:[] },
  szamsor:   { prompt:'', cta:[] },
  reakcio:   { prompt:'', cta:[] },
  ritmus:    { prompt:'', cta:[] },"""

assert OLD_SCENARIOS in content, "SCENARIOS not found"
content = content.replace(OLD_SCENARIOS, NEW_SCENARIOS, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.163 ready")
