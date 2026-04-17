#!/usr/bin/env bash
# =============================================================================
# apply_and_release.sh – NetTools Tauri: Dateien einpflegen + GitHub Release
#
# Dieses Script liegt im Wurzelverzeichnis des nettools-tauri Repos.
# Fix-Dateien werden aus dem _fixes/ Unterordner geholt (ebenfalls im Repo).
#
# Struktur:
#   nettools-tauri/
#   ├── apply_and_release.sh        ← dieses Script
#   ├── _fixes/
#   │   ├── scanner.rs
#   │   ├── live_monitor.rs
#   │   ├── Cargo.toml
#   │   └── ScannerPage.patch.tsx   (optional, manuell anwenden)
#   ├── src-tauri/
#   └── src/
#
# Verwendung:
#   ./apply_and_release.sh           # patch-Version automatisch erhöhen
#   ./apply_and_release.sh --no-bump # Version so lassen wie sie ist
#   ./apply_and_release.sh --dry-run # nur anzeigen, nichts ändern
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
# Pfade – alles relativ zum Script-Verzeichnis (= Repo-Wurzel)
# ---------------------------------------------------------------------------
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXES="$REPO/_fixes"
CARGO_TOML="$REPO/src-tauri/Cargo.toml"
TAURI_CONF="$REPO/src-tauri/tauri.conf.json"

[[ -f "$CARGO_TOML" ]] || die "Cargo.toml nicht gefunden unter $CARGO_TOML\nScript muss im Repo-Wurzelverzeichnis liegen (neben src-tauri/)"
[[ -d "$FIXES" ]]      || die "_fixes/ Ordner nicht gefunden unter $FIXES\nBitte _fixes/ Ordner im Repo anlegen und Fix-Dateien dort ablegen"

# ---------------------------------------------------------------------------
# Fix-Dateien → Ziel-Pfade
# ---------------------------------------------------------------------------
declare -A FILES=(
  ["$FIXES/scanner.rs"]="$REPO/src-tauri/src/commands/scanner.rs"
  ["$FIXES/live_monitor.rs"]="$REPO/src-tauri/src/commands/live_monitor.rs"
  ["$FIXES/Cargo.toml"]="$REPO/src-tauri/Cargo.toml"
  ["$FIXES/ScannerPage.tsx"]="$REPO/src/pages/ScannerPage.tsx"
)

# ---------------------------------------------------------------------------
# Voraussetzungen
# ---------------------------------------------------------------------------
info "Prüfe Voraussetzungen…"
for cmd in git gh cargo npm node; do
  command -v "$cmd" &>/dev/null || die "'$cmd' nicht gefunden"
done
gh auth status &>/dev/null || die "Nicht bei GitHub eingeloggt – bitte 'gh auth login' ausführen"
git -C "$REPO" rev-parse --git-dir &>/dev/null || die "Kein Git-Repository gefunden in $REPO"
success "Voraussetzungen OK"

# ---------------------------------------------------------------------------
# Vorhandene Fix-Dateien anzeigen
# ---------------------------------------------------------------------------
info "Gefundene Fix-Dateien in _fixes/:"
FOUND=0
for src in "${!FILES[@]}"; do
  if [[ -f "$src" ]]; then
    echo "    ✓ $(basename "$src")"
    FOUND=$((FOUND + 1))
  else
    echo "    – $(basename "$src") (nicht vorhanden, wird übersprungen)"
  fi
done
[[ $FOUND -gt 0 ]] || die "Keine Fix-Dateien in $FIXES gefunden"

# ---------------------------------------------------------------------------
# Version lesen + erhöhen
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
  local new_ver="$1"
  sed -i "0,/^version\s*=/{s/^version\s*=.*/version = \"${new_ver}\"/}" "$CARGO_TOML"
  [[ -f "$TAURI_CONF" ]] && sed -i "s/\"version\": \".*\"/\"version\": \"${new_ver}\"/" "$TAURI_CONF"
}

CURRENT_VERSION="$(read_version)"
[[ -n "$CURRENT_VERSION" ]] || die "Version konnte nicht aus Cargo.toml gelesen werden"

if $BUMP; then
  NEW_VERSION="$(bump_patch "$CURRENT_VERSION")"
  info "Version: $CURRENT_VERSION → $NEW_VERSION"
else
  NEW_VERSION="$CURRENT_VERSION"
  info "Version: $NEW_VERSION (unverändert)"
fi

TAG="v${NEW_VERSION}"

if git -C "$REPO" tag --list | grep -q "^${TAG}$"; then
  die "Tag '$TAG' existiert bereits – Version erhöhen oder --no-bump weglassen"
fi

# ---------------------------------------------------------------------------
# Dry-Run
# ---------------------------------------------------------------------------
if $DRY_RUN; then
  echo ""
  echo -e "${BOLD}[DRY-RUN] Würde folgendes tun:${RESET}"
  for src in "${!FILES[@]}"; do
    [[ -f "$src" ]] && echo "    cp _fixes/$(basename "$src") → ${FILES[$src]#$REPO/}"
  done
  echo "    git add . && git commit && git push"
  echo "    git tag $TAG && gh release create $TAG"
  echo ""
  success "Dry-Run abgeschlossen – nichts geändert"
  exit 0
fi

# ---------------------------------------------------------------------------
# 1. Dateien kopieren
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
# 2. Version schreiben
# ---------------------------------------------------------------------------
if $BUMP; then
  info "Schreibe Version $NEW_VERSION…"
  write_version "$NEW_VERSION"
fi

# ---------------------------------------------------------------------------
# 3. Build
# ---------------------------------------------------------------------------
info "Baue Frontend…"
npm install --prefix "$REPO" 2>&1 | tail -3
npm run build --prefix "$REPO" 2>&1 | tail -3
success "Frontend gebaut"

info "Baue Tauri Installer…"
cd "$REPO"
cargo tauri build 2>&1 | grep -E "Compiling|Finished|Bundling|error" | tail -20
success "Tauri Build abgeschlossen"

# ---------------------------------------------------------------------------
# 4. Artefakte + Source ZIP
# ---------------------------------------------------------------------------
BUNDLE_DIR="$REPO/src-tauri/target/release/bundle"
mapfile -t ARTIFACTS < <(
  find "$BUNDLE_DIR/nsis" -name "*.exe" 2>/dev/null || true
  find "$BUNDLE_DIR/msi"  -name "*.msi" 2>/dev/null || true
)
[[ ${#ARTIFACTS[@]} -gt 0 ]] || die "Keine Installer in $BUNDLE_DIR gefunden"

info "Installer:"
for f in "${ARTIFACTS[@]}"; do
  echo "    $(basename "$f")  ($(du -sh "$f" | cut -f1))"
done

SOURCE_ZIP="/tmp/nettools-tauri-${NEW_VERSION}-source.zip"
git -C "$REPO" archive --format=zip \
  --prefix="nettools-tauri-${NEW_VERSION}/" HEAD \
  -o "$SOURCE_ZIP"
success "Source ZIP: $(du -sh "$SOURCE_ZIP" | cut -f1)"

# ---------------------------------------------------------------------------
# 5. Git commit + push
# ---------------------------------------------------------------------------
BRANCH="$(git -C "$REPO" rev-parse --abbrev-ref HEAD)"
info "Committe auf Branch '$BRANCH'…"

git -C "$REPO" add .
git -C "$REPO" commit -m "fix: scanner ICMP performance + bug fixes v${NEW_VERSION}"
git -C "$REPO" push origin "$BRANCH"
success "Gepusht"

# ---------------------------------------------------------------------------
# 6. Tag + Release
# ---------------------------------------------------------------------------
info "Erstelle Tag $TAG und GitHub Release…"
git -C "$REPO" tag -a "$TAG" -m "Release ${NEW_VERSION}"
git -C "$REPO" push origin "$TAG"

RELEASE_NOTES="## NetTools Suite ${NEW_VERSION}

### Änderungen
$(git -C "$REPO" log --pretty=format:"- %s" \
    "$(git -C "$REPO" describe --tags --abbrev=0 HEAD^ 2>/dev/null \
       || git -C "$REPO" rev-list --max-parents=0 HEAD)"..HEAD 2>/dev/null \
  | grep -v "^- fix: bump\|^- chore:" | head -20 \
  || echo "- Performance-Fix Scanner")

### Was ist neu
- Scanner: ICMP direkt statt ping.exe – bis zu 10x schneller
- Semaphore-Bug behoben – Rate-Limiting funktioniert jetzt korrekt
- Hostname-Auflösung bei Eingabe von Hostnamen
- Warnung bei großen Netzen
- Live Progress-Bar beim Scannen

### Installation
\`.exe\` herunterladen und ausführen.
"

gh release create "$TAG" \
  "${ARTIFACTS[@]}" \
  "$SOURCE_ZIP" \
  --title "NetTools Suite ${NEW_VERSION}" \
  --notes "$RELEASE_NOTES" \
  --latest

rm -f "$SOURCE_ZIP"

# _fixes/ leeren nach erfolgreichem Release
rm -f "$FIXES"/*.rs "$FIXES"/*.toml "$FIXES"/*.tsx 2>/dev/null || true

REPO_URL="$(gh repo view --json url -q .url 2>/dev/null || echo '')"
echo ""
echo -e "${GREEN}${BOLD}✓ Release ${TAG} erfolgreich veröffentlicht!${RESET}"
[[ -n "$REPO_URL" ]] && echo -e "  ${REPO_URL}/releases/tag/${TAG}"
