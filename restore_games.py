import subprocess
import sys

# Read current index.html
with open('/home/user/bottle-of-heroes/index.html', 'r') as f:
    current = f.read()
print(f"Current index.html: {len(current)} chars")

# Confirm all game functions exist
for name in ['OVFJConfigSheet', 'OVFJObserverView', 'OVFJGame', 'MitValasztanalGame', 'EmojiKvizGame']:
    assert f'function {name}(' in current, f"{name} NOT found in current index.html!"
print("All functions confirmed present in current index.html")

# Check if dispatch lines already exist
if "gameId === 'ovfj'" in current:
    print("Dispatch lines already present, skipping insert")
else:
    # Add dispatch lines after reakcio line
    reakcio_marker = "if (gameId === 'reakcio') return <ReakcioGame"
    reakcio_pos = current.find(reakcio_marker)
    assert reakcio_pos != -1, "reakcio dispatch line not found"

    line_end = current.find('\n', reakcio_pos)
    assert line_end != -1

    dispatch_lines = """
   if (gameId === 'ovfj') return <OVFJGame key={gameIdx} gameIdx={gameIdx} players={players||[]} roomCode={roomCode} gameMeta={gameMeta} onAdvance={onAdvance} onResult={onResult} />;
   if (gameId === 'emojikv') return <EmojiKvizGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} />;
   if (gameId === 'mitval') return <MitValasztanalGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} difficulty={gameMeta?.difficulty} />;"""

    current = current[:line_end] + dispatch_lines + current[line_end:]
    print("Added dispatch lines")

# Version bump
assert 'v9.448' in current, "v9.448 not found in current index.html"
current = current.replace('v9.448', 'v9.449', 1)
print("Version bumped to v9.449")

# Write back
with open('/home/user/bottle-of-heroes/index.html', 'w') as f:
    f.write(current)
print("Written back to index.html")
print("SUCCESS!")
