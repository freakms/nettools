#!/usr/bin/env bash
# =============================================================================
# push_fixes.sh – Fixes pushen + Tag erstellen → GitHub Actions baut Release
#
# Struktur:
#   nettools-tauri/
#   ├── push_fixes.sh            ← dieses Script
#   ├── _fixes/                  ← geänderte Dateien hier ablegen
#   │   ├── scanner.rs
#   │   ├── live_monitor.rs
#   │   ├── Cargo.toml
#   │   ├── ScannerPage.tsx
#   │   └── tauri.conf.json
#   └── .github/workflows/release.yml
#
# Verwendung:
#   ./push_fixes.sh              # patch-Version erhöhen + pushen
#   ./push_fixes.sh --no-bump    # Version so lassen
#   ./push_fixes.sh --dry-run    # nur anzeigen
# =============================================================================

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${BLUE}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
die()     { echo -e "${RED}[ERROR]${RESET} $*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# Argumente
# ---------------------------------------------------------------------------
BUMP=true
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-bump)  BUMP=false; shift ;;
    --dry-run)  DRY_RUN=true; shift ;;
    -h|--help)
      echo "Verwendung: $0 [--no-bump] [--dry-run]"
      exit 0 ;;
    *) die "Unbekanntes Argument: $1" ;;
  esac
done

# ---------------------------------------------------------------------------
# Pfade
# ---------------------------------------------------------------------------
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXES="$REPO/_fixes"
CARGO_TOML="$REPO/src-tauri/Cargo.toml"
TAURI_CONF="$REPO/src-tauri/tauri.conf.json"

[[ -f "$CARGO_TOML" ]] || die "Cargo.toml nicht gefunden – Script im falschen Ordner?"
[[ -d "$FIXES" ]]      || die "_fixes/ Ordner nicht gefunden"

# ---------------------------------------------------------------------------
# Fix-Dateien → Zielpfade
# ---------------------------------------------------------------------------
declare -A FILES=(
  ["$FIXES/scanner.rs"]="$REPO/src-tauri/src/commands/scanner.rs"
  ["$FIXES/live_monitor.rs"]="$REPO/src-tauri/src/commands/live_monitor.rs"
  ["$FIXES/Cargo.toml"]="$REPO/src-tauri/Cargo.toml"
  ["$FIXES/ScannerPage.tsx"]="$REPO/src/pages/ScannerPage.tsx"
  ["$FIXES/tauri.conf.json"]="$REPO/src-tauri/tauri.conf.json"
)

# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------
read_version() {
  grep -m1 '^version\s*=' "$CARGO_TOML" | sed 's/.*"\(.*\)".*/\1/'
}

bump_patch() {
  local major minor patch
  IFS='.' read -r major minor patch <<< "$1"
  echo "${major}.${minor}.$((patch + 1))"
}

write_version() {
  local v="$1"
  sed -i "0,/^version\s*=/{s/^version\s*=.*/version = \"${v}\"/}" "$CARGO_TOML"
  [[ -f "$TAURI_CONF" ]] && sed -i "s/\"version\": \".*\"/\"version\": \"${v}\"/" "$TAURI_CONF"
}

CURRENT="$(read_version)"
[[ -n "$CURRENT" ]] || die "Version konnte nicht aus Cargo.toml gelesen werden"

if $BUMP; then
  NEW="$(bump_patch "$CURRENT")"
else
  NEW="$CURRENT"
fi

TAG="v${NEW}"
info "Version: $CURRENT → $NEW"

# Tag-Konflikt prüfen
if git -C "$REPO" tag --list | grep -q "^${TAG}$"; then
  die "Tag '$TAG' existiert bereits"
fi

# ---------------------------------------------------------------------------
# Fix-Dateien prüfen
# ---------------------------------------------------------------------------
info "Fix-Dateien in _fixes/:"
FOUND=0
for src in "${!FILES[@]}"; do
  if [[ -f "$src" ]]; then
    echo "    ✓ $(basename "$src")"
    FOUND=$((FOUND + 1))
  else
    echo "    – $(basename "$src") (nicht vorhanden, wird übersprungen)"
  fi
done
[[ $FOUND -gt 0 ]] || die "Keine Fix-Dateien in _fixes/ gefunden"

# ---------------------------------------------------------------------------
# Dry-Run
# ---------------------------------------------------------------------------
if $DRY_RUN; then
  echo ""
  echo -e "${BOLD}[DRY-RUN] Würde folgendes tun:${RESET}"
  for src in "${!FILES[@]}"; do
    [[ -f "$src" ]] && echo "    cp _fixes/$(basename "$src") → ${FILES[$src]#$REPO/}"
  done
  echo "    git add . && git commit -m 'fix: nettools suite v${NEW}'"
  echo "    git push origin $(git -C "$REPO" rev-parse --abbrev-ref HEAD)"
  echo "    git tag $TAG && git push origin $TAG"
  echo "    → GitHub Actions baut Windows Installer und erstellt Release"
  echo ""
  success "Dry-Run abgeschlossen – nichts geändert"
  exit 0
fi

# ---------------------------------------------------------------------------
# Dateien kopieren
# ---------------------------------------------------------------------------
info "Kopiere Fix-Dateien…"
for src in "${!FILES[@]}"; do
  if [[ -f "$src" ]]; then
    dest="${FILES[$src]}"
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    success "  $(basename "$src") → ${dest#$REPO/}"
  fi
done

# ---------------------------------------------------------------------------
# Version schreiben
# ---------------------------------------------------------------------------
if $BUMP; then
  info "Schreibe Version $NEW…"
  write_version "$NEW"
fi

# ---------------------------------------------------------------------------
# Commit + Push
# ---------------------------------------------------------------------------
BRANCH="$(git -C "$REPO" rev-parse --abbrev-ref HEAD)"
info "Committe auf Branch '$BRANCH'…"

git -C "$REPO" add .

if git -C "$REPO" diff --cached --quiet; then
  warn "Keine Änderungen zu committen"
else
  git -C "$REPO" commit -m "fix: nettools suite v${NEW}"
  git -C "$REPO" push origin "$BRANCH"
  success "Gepusht"
fi

# ---------------------------------------------------------------------------
# Tag pushen → löst GitHub Actions aus
# ---------------------------------------------------------------------------
info "Erstelle Tag $TAG…"
git -C "$REPO" tag -a "$TAG" -m "Release ${NEW}"
git -C "$REPO" push origin "$TAG"

# ---------------------------------------------------------------------------
# _fixes/ leeren
# ---------------------------------------------------------------------------
rm -f "$FIXES"/*.rs "$FIXES"/*.toml "$FIXES"/*.tsx "$FIXES"/*.json 2>/dev/null || true

echo ""
echo -e "${GREEN}${BOLD}✓ Tag $TAG gepusht!${RESET}"
echo -e "  GitHub Actions baut jetzt den Windows Installer automatisch."
echo -e "  Release: https://github.com/freakms/nettools/releases/tag/${TAG}"
