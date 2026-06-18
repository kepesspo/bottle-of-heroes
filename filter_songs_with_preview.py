#!/usr/bin/env python3
"""
Lekéri a jelenlegi ZENE_SONGS listát az index.html-ből,
ellenőrzi Spotify API-val melyiknek van preview_url,
és visszaírja csak a preview-val rendelkező dalokat.
"""
import re, requests, json, time, sys

CLIENT_ID     = '466b1ac50ffb4a2a866dddbeab9bef80'
CLIENT_SECRET = '9569e6631bd94cb9a155bc28aa49df08'

# ── Token ─────────────────────────────────────────────────────────
resp = requests.post(
    'https://accounts.spotify.com/api/token',
    data={'grant_type': 'client_credentials'},
    auth=(CLIENT_ID, CLIENT_SECRET),
    timeout=15,
)
resp.raise_for_status()
token = resp.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}
print(f'Token OK')

# ── ZENE_SONGS kinyerése index.html-ből ───────────────────────────
with open('index.html', encoding='utf-8') as f:
    content = f.read()

start_idx = content.index('const ZENE_SONGS = [')
end_idx   = content.index('];\n\n// Shuffle once per session', start_idx) + 2
songs_block = content[start_idx:end_idx]
song_lines = [l.strip() for l in songs_block.split('\n') if l.strip().startswith('{')]

print(f'Talált sorok: {len(song_lines)}')

songs = []
for line in song_lines:
    artist_m = re.search(r"artist:'([^']*)'|artist:\"([^\"]*)\"", line)
    title_m  = re.search(r"title:'([^']*)'|title:\"([^\"]*)\"", line)
    sid_m    = re.search(r"spotifyId:'([^']*)'", line)
    start_m  = re.search(r'start:(\d+)', line)
    era_m    = re.search(r"era:'([^']*)'", line)
    genre_m  = re.search(r"genre:'([^']*)'", line)

    if not (artist_m and title_m and sid_m and start_m and era_m and genre_m):
        print(f'SKIP (nem parseable): {line[:80]}')
        continue

    artist = artist_m.group(1) or artist_m.group(2)
    title  = title_m.group(1)  or title_m.group(2)
    songs.append({
        'artist':    artist,
        'title':     title,
        'spotifyId': sid_m.group(1),
        'start':     int(start_m.group(1)),
        'era':       era_m.group(1),
        'genre':     genre_m.group(1),
        '_line':     line,
    })

# Deduplikálás spotifyId szerint (megtartjuk az első előfordulást)
seen = {}
unique = []
for s in songs:
    if s['spotifyId'] not in seen:
        seen[s['spotifyId']] = s
        unique.append(s)
    else:
        print(f"Duplikált spotifyId: {s['spotifyId']} ({s['artist']} — {s['title']})")

print(f'Egyedi dal: {len(unique)}')

# ── Spotify API ellenőrzés (50-esével) ───────────────────────────
has_preview = []
no_preview  = []

ids = [s['spotifyId'] for s in unique]
for i in range(0, len(ids), 50):
    batch_ids = ids[i:i+50]
    batch_songs = unique[i:i+50]

    for attempt in range(3):
        r = requests.get(
            'https://api.spotify.com/v1/tracks',
            headers=headers,
            params={'ids': ','.join(batch_ids), 'market': 'HU'},
            timeout=15,
        )
        if r.status_code == 429:
            wait = int(r.headers.get('Retry-After', 5))
            print(f'Rate limit, várakozás {wait}s...')
            time.sleep(wait)
            continue
        if r.status_code == 401:
            # Token lejárt, újra lekér
            resp2 = requests.post('https://accounts.spotify.com/api/token',
                data={'grant_type': 'client_credentials'}, auth=(CLIENT_ID, CLIENT_SECRET), timeout=15)
            resp2.raise_for_status()
            token = resp2.json()['access_token']
            headers['Authorization'] = f'Bearer {token}'
            continue
        r.raise_for_status()
        break

    tracks = r.json().get('tracks', [])
    for track, song in zip(tracks, batch_songs):
        if track and track.get('preview_url'):
            has_preview.append(song)
        else:
            no_preview.append(song)
            print(f'  NINCS preview: {song["artist"]} — {song["title"]}')
    time.sleep(0.15)

print(f'\n✅ Van preview: {len(has_preview)} dal')
print(f'❌ Nincs preview: {len(no_preview)} dal')

# ── ZENE_SONGS újraírása csak preview-val rendelkező dalokkal ─────
def fmt_line(s):
    # Eredeti sor formátuma alapján, apostróf-safe idézőjelezéssel
    artist = s['artist'].replace("'", "\\'")
    title_raw = s['title']
    # Ha az artist vagy a title tartalmaz aposztrófot, double quote-ot használunk
    if "'" in title_raw:
        title_str = f'"{title_raw}"'
    else:
        title_str = f"'{title_raw}'"
    if "'" in artist:
        artist_str = f'"{artist.replace(chr(92), "")}"'
    else:
        artist_str = f"'{artist}'"
    pad_artist = artist_str.ljust(38)
    pad_title  = title_str.ljust(42)
    return (f"  {{ artist:{pad_artist} title:{pad_title} "
            f"spotifyId:'{s['spotifyId']}', start:{s['start']},  "
            f"era:'{s['era']}',   genre:'{s['genre']}' }},")

new_lines = ['const ZENE_SONGS = [']
# Csoportosítás era szerint
for era_key, era_label in [('classic','Classic (pre-2000)'), ('2000s','2000s'), ('2010s','2010s'), ('2020s','2020s')]:
    era_songs = [s for s in has_preview if s['era'] == era_key]
    if era_songs:
        new_lines.append(f'  // ── {era_label} ─────────────────────────────────────────')
        for s in era_songs:
            new_lines.append(fmt_line(s))

new_block = '\n'.join(new_lines) + '\n]'

# Bumpolja a verziót
ver_m = re.search(r"const APP_VERSION = '(v[\d.]+)'", content)
if ver_m:
    old_ver = ver_m.group(1)
    parts = old_ver.lstrip('v').split('.')
    parts[-1] = str(int(parts[-1]) + 1)
    new_ver = 'v' + '.'.join(parts)
    content = content.replace(f"const APP_VERSION = '{old_ver}'", f"const APP_VERSION = '{new_ver}'")
    print(f'Verzió: {old_ver} → {new_ver}')

# Csere az index.html-ben
new_content = content[:start_idx] + new_block + content[end_idx:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'\nindex.html frissítve: {len(has_preview)} dal maradt (preview nélküli {len(no_preview)} törölve)')

# Mentés JSON-be is referenciaként
with open('songs_with_preview.json', 'w', encoding='utf-8') as f:
    json.dump([{'artist': s['artist'], 'title': s['title'],
                'spotifyId': s['spotifyId'], 'start': s['start'],
                'era': s['era'], 'genre': s['genre']}
               for s in has_preview], f, ensure_ascii=False, indent=2)
print('songs_with_preview.json elmentve')
