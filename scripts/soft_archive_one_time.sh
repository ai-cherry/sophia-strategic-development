#!/usr/bin/env bash
set -euo pipefail

CSV="one_time_inventory_APPROVED.csv"
DEST="archive/one_time_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DEST"

echo "➜ Archiving files..."
# Skip header and read CSV columns
tail -n +2 "$CSV" | while IFS=',' read -r path size age referenced confidence action; do
    if [[ "$action" == "ARCHIVE" || "$action" == "DELETE" ]]; then
        mkdir -p "$DEST/$(dirname "$path")"
        git mv "$path" "$DEST/$path"
    fi
done

git add "$DEST"
git commit -m "chore: archive one-time artefacts (soft delete)"
echo "✅ Archive commit ready – push after review."
