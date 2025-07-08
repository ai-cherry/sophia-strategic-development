import json
import pathlib

root = pathlib.Path("docs")
index = {}

for md in root.rglob("*.md"):
    if "/archive/" in md.as_posix():
        continue
    relative = md.relative_to(root)
    title = md.stem.replace("_", " ").title()
    index[str(relative)] = {"title": title}

output = root / "INDEX.json"
output.write_text(json.dumps(index, indent=2))
print("✅ docs/INDEX.json updated")
