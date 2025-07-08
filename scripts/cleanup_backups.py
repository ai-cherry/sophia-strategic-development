import argparse
import datetime
import json
import pathlib
import shutil

ROOT = pathlib.Path(".").resolve()
TS = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
backup_manifest = []

def should_delete(p: pathlib.Path) -> bool:
    return (
        ".backup" in p.name
        or p.name.endswith("_backup")
        or p.name.endswith("_backup.py")
    )

def main(dry: bool) -> None:
    for path in ROOT.rglob("*"):
        if should_delete(path):
            backup_manifest.append(str(path))
            if not dry:
                if path.is_file():
                    path.unlink()
                else:
                    shutil.rmtree(path)
    if backup_manifest:
        manifest_file = ROOT / f"reports/backups_removed_{TS}.json"
        manifest_file.write_text(json.dumps(backup_manifest, indent=2))
        action = "Would remove" if dry else "Removed"
        print(f"{action} {len(backup_manifest)} items. See {manifest_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="List items only")
    main(parser.parse_args().dry_run)
