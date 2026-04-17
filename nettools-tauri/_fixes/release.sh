#!/usr/bin/env bash
# =============================================================================
# release.sh – NetTools Tauri Release Script
# Liest Version aus Cargo.toml, baut Installer, erstellt GitHub Release
#
# Voraussetzungen:
#   - Git, GitHub CLI (gh), Rust/Cargo, Node.js/npm installiert
#   - gh auth login einmalig ausgeführt
#   - Script liegt im Wurzelverzeichnis des nettools-tauri Repos
#
# Verwendung:
#   ./release.sh              # Version aus Cargo.toml
#   ./release.sh --bump patch # Version erhöhen (patch/minor/major) + Release
#   ./release.sh --dry-run    # Nur anzeigen, nichts pushen
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Farben
# ---------------------------------------------------------------------------
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${BLUE}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }
die()     { error "$*"; exit 1; }

# ---------------------------------------------------------------------------
# Argumente
# ---------------------------------------------------------------------------
BUMP=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --bump)
      BUMP="${2:-}"
      [[ "$BUMP" =~ ^(patch|minor|major)$ ]] || die "--bump erwartet patch, minor oder major"
      shift 2
      ;;
    --dry-run) DRY_RUN=true; shift ;;
    -h|--help)
      echo "Verwendung: $0 [--bump patch|minor|major] [--dry-run]"
      exit 0
      ;;
    *) die "Unbekanntes Argument: $1" ;;
  esac
done

# ---------------------------------------------------------------------------
# Pfade
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CARGO_TOML="$SCRIPT_DIR/src-tauri/Cargo.toml"
TAURI_CONF="$SCRIPT_DIR/src-tauri/tauri.conf.json"

[[ -f "$CARGO_TOML" ]] || die "Cargo.toml nicht gefunden: $CARGO_TOML"
[[ -f "$TAURI_CONF" ]] || die "tauri.conf.json nicht gefunden: $TAURI_CONF"

# ---------------------------------------------------------------------------
# Voraussetzungen prüfen
# ---------------------------------------------------------------------------
info "Prüfe Voraussetzungen…"

for cmd in git gh cargo npm node; do
  command -v "$cmd" &>/dev/null || die "'$cmd' nicht gefunden. Bitte installieren."
done

gh auth status &>/dev/null || die "Nicht bei GitHub eingeloggt. Bitte 'gh auth login' ausführen."

success "Alle Voraussetzungen erfüllt"

# ---------------------------------------------------------------------------
# Version aus Cargo.toml lesen
# ---------------------------------------------------------------------------
read_version() {
  grep -m1 '^version\s*=' "$CARGO_TOML" | sed 's/.*"\(.*\)".*/\1/'
}

# Version erhöhen (semver)
bump_version() {
  local version="$1" part="$2"
  local major minor patch
  IFS='.' read -r major minor patch <<< "$version"
  case "$part" in
    major) major=$((major + 1)); minor=0; patch=0 ;;
    minor) minor=$((minor + 1)); patch=0 ;;
    patch) patch=$((patch + 1)) ;;
  esac
  echo "${major}.${minor}.${patch}"
}

# Version in Cargo.toml und tauri.conf.json schreiben
write_version() {
  local new_ver="$1"
  # Cargo.toml – nur die erste version-Zeile im [package]-Block
  sed -i "0,/^version\s*=/{s/^version\s*=.*/version = \"${new_ver}\"/}" "$CARGO_TOML"
  # tauri.conf.json
  sed -i "s/\"version\": \".*\"/\"version\": \"${new_ver}\"/" "$TAURI_CONF"
}

CURRENT_VERSION="$(read_version)"
[[ -n "$CURRENT_VERSION" ]] || die "Version konnte nicht aus Cargo.toml gelesen werden"

if [[ -n "$BUMP" ]]; then
  NEW_VERSION="$(bump_version "$CURRENT_VERSION" "$BUMP")"
  info "Version: $CURRENT_VERSION → $NEW_VERSION ($BUMP)"
else
  NEW_VERSION="$CURRENT_VERSION"
  info "Version: $NEW_VERSION (aus Cargo.toml)"
fi

TAG="v${NEW_VERSION}"

# ---------------------------------------------------------------------------
# Git-Status prüfen
# ---------------------------------------------------------------------------
info "Prüfe Git-Status…"

# Sicherstellen dass wir in einem Git-Repo sind
git rev-parse --git-dir &>/dev/null || die "Kein Git-Repository gefunden"

# Auf main/master Branch prüfen
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$CURRENT_BRANCH" != "main" && "$CURRENT_BRANCH" != "master" ]]; then
  warn "Aktueller Branch: '$CURRENT_BRANCH' (nicht main/master)"
  read -r -p "Trotzdem fortfahren? [j/N] " CONFIRM
  [[ "$CONFIRM" =~ ^[jJyY]$ ]] || { info "Abgebrochen."; exit 0; }
fi

# Prüfen ob Tag bereits existiert
if git tag --list | grep -q "^${TAG}$"; then
  die "Tag '$TAG' existiert bereits. Bitte Version in Cargo.toml erhöhen oder --bump verwenden."
fi

# Uncommitted changes?
if ! git diff --quiet || ! git diff --cached --quiet; then
  warn "Es gibt uncommitted Änderungen:"
  git status --short
  if [[ -z "$BUMP" ]]; then
    read -r -p "Trotzdem fortfahren (alle Änderungen werden committed)? [j/N] " CONFIRM
    [[ "$CONFIRM" =~ ^[jJyY]$ ]] || { info "Abgebrochen."; exit 0; }
  fi
fi

# ---------------------------------------------------------------------------
# Version bump committen (falls --bump)
# ---------------------------------------------------------------------------
if [[ -n "$BUMP" ]] && ! $DRY_RUN; then
  info "Schreibe neue Version in Dateien…"
  write_version "$NEW_VERSION"
  git add "$CARGO_TOML" "$TAURI_CONF"
  git commit -m "chore: bump version to ${NEW_VERSION}"
  success "Version auf $NEW_VERSION gesetzt"
fi

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
info "Baue Frontend…"
if ! $DRY_RUN; then
  npm install --prefix "$SCRIPT_DIR" 2>&1 | tail -5
  npm run build --prefix "$SCRIPT_DIR" 2>&1 | tail -5
  success "Frontend gebaut"
fi

info "Baue Tauri Installer (Release)…"
if ! $DRY_RUN; then
  cd "$SCRIPT_DIR"
  cargo tauri build 2>&1 | grep -E "Compiling|Finished|Bundling|error\[" | tail -20
  success "Tauri Build abgeschlossen"
fi

# ---------------------------------------------------------------------------
# Installer-Artefakte finden
# ---------------------------------------------------------------------------
BUNDLE_DIR="$SCRIPT_DIR/src-tauri/target/release/bundle"

find_artifacts() {
  local files=()
  # NSIS Installer (.exe)
  while IFS= read -r f; do files+=("$f"); done < <(find "$BUNDLE_DIR/nsis" -name "*.exe" 2>/dev/null || true)
  # MSI Installer
  while IFS= read -r f; do files+=("$f"); done < <(find "$BUNDLE_DIR/msi" -name "*.msi" 2>/dev/null || true)
  printf '%s\n' "${files[@]}"
}

if ! $DRY_RUN; then
  mapfile -t ARTIFACTS < <(find_artifacts)
  if [[ ${#ARTIFACTS[@]} -eq 0 ]]; then
    die "Keine Installer-Artefakte gefunden in $BUNDLE_DIR"
  fi
  info "Gefundene Artefakte:"
  for f in "${ARTIFACTS[@]}"; do
    echo "    $(basename "$f")  ($(du -sh "$f" | cut -f1))"
  done
else
  info "[DRY-RUN] Build-Schritt übersprungen"
  ARTIFACTS=()
fi

# ---------------------------------------------------------------------------
# Source ZIP erstellen
# ---------------------------------------------------------------------------
SOURCE_ZIP="/tmp/nettools-tauri-${NEW_VERSION}-source.zip"
info "Erstelle Source ZIP…"

if ! $DRY_RUN; then
  git archive --format=zip --prefix="nettools-tauri-${NEW_VERSION}/" HEAD \
    -o "$SOURCE_ZIP"
  success "Source ZIP: $SOURCE_ZIP ($(du -sh "$SOURCE_ZIP" | cut -f1))"
fi

# ---------------------------------------------------------------------------
# Alles pushen
# ---------------------------------------------------------------------------
if ! $DRY_RUN; then
  info "Pushe Branch nach origin…"
  git push origin "$CURRENT_BRANCH"

  info "Erstelle und pushe Tag $TAG…"
  git tag -a "$TAG" -m "Release ${NEW_VERSION}"
  git push origin "$TAG"
fi

# ---------------------------------------------------------------------------
# GitHub Release erstellen
# ---------------------------------------------------------------------------
RELEASE_NOTES="## NetTools Suite ${NEW_VERSION}

### Änderungen
$(git log --pretty=format:"- %s" "$(git describe --tags --abbrev=0 HEAD^ 2>/dev/null || git rev-list --max-parents=0 HEAD)"..HEAD 2>/dev/null | grep -v "^- chore: bump version" | head -30 || echo "- Erstes Release")

### Installation
1. \`.exe\` herunterladen und ausführen (empfohlen)
2. Oder \`.msi\` für stille Installation: \`msiexec /i NetToolsSuite_${NEW_VERSION}_x64_en-US.msi /quiet\`

### Systemanforderungen
- Windows 10 / 11 (64-bit)
- Keine weitere Software nötig
"

if $DRY_RUN; then
  echo ""
  echo -e "${BOLD}[DRY-RUN] Würde GitHub Release erstellen:${RESET}"
  echo "  Tag:     $TAG"
  echo "  Titel:   NetTools Suite ${NEW_VERSION}"
  echo "  Assets:  Installer + Source ZIP"
  echo ""
  echo "Release Notes:"
  echo "$RELEASE_NOTES"
  success "Dry-Run abgeschlossen – nichts wurde verändert"
  exit 0
fi

info "Erstelle GitHub Release $TAG…"

# Asset-Argumente für gh release create aufbauen
GH_ASSETS=()
for f in "${ARTIFACTS[@]}"; do
  GH_ASSETS+=("$f")
done
GH_ASSETS+=("$SOURCE_ZIP")

gh release create "$TAG" \
  "${GH_ASSETS[@]}" \
  --title "NetTools Suite ${NEW_VERSION}" \
  --notes "$RELEASE_NOTES" \
  --latest

REPO_URL="$(gh repo view --json url -q .url 2>/dev/null || echo 'dein GitHub Repo')"
success "Release erstellt: ${REPO_URL}/releases/tag/${TAG}"

# ---------------------------------------------------------------------------
# Aufräumen
# ---------------------------------------------------------------------------
rm -f "$SOURCE_ZIP"

echo ""
echo -e "${GREEN}${BOLD}✓ Release ${TAG} erfolgreich veröffentlicht!${RESET}"
