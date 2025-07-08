#!/usr/bin/env bash
set -euo pipefail

TS=$(date +%Y%m%d_%H%M%S)
OUT="reports/hygiene_inventory_${TS}.csv"

# Header for CSV
echo "path,category,todo_count,last_commit" > "$OUT"

git ls-files | while read -r f; do
  cat_type="normal"
  [[ $f == *".backup"* ]] && cat_type="backup_file"
  [[ $f == */*_backup_* || $f == *_backup/ ]] && cat_type="backup_dir"
  [[ $(grep -E -c "TODO: Implement file decomposition" "$f" || true) -gt 0 ]] && cat_type="todo_file"
  [[ $(grep -E -c "DEPRECATED" "$f" || true) -gt 0 ]] && cat_type="deprecated"
  if [[ $cat_type != "normal" ]]; then
    todos=$(grep -c "TODO" "$f" || true)
    last=$(git log -1 --format="%cs" -- "$f" || true)
    echo "$f,$cat_type,$todos,$last" >> "$OUT"
  fi
done

echo "✅  Inventory written to $OUT"
