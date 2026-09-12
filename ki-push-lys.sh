#!/bin/bash
# Bruk: bash ~/ki-push-lys.sh 1.0.0
set -e
V=$1
[ -z "$V" ] && { echo "Bruk: ki-push-lys.sh 1.0.0"; exit 1; }
REPO=~/Documents/HomeAssistant/ki-lys
NED=~/Downloads

cd "$NED"
rm -rf "ki-lys-$V" && unzip -oq "ki-lys-$V.zip" -d "ki-lys-$V"
[ -d "$REPO/.git" ] || git clone -q https://github.com/SebastianKristo/ki-lys.git "$REPO"
cp -r "ki-lys-$V/ki-lys/." "$REPO/"

cd "$REPO"
perl -pi -e "s/\"version\": \"[^\"]*\"/\"version\": \"$V\"/" custom_components/ki_lys/manifest.json
git add .
git commit -m "KI Lys v$V" || true
git push origin main
git tag -f "v$V" && git push -f origin "v$V"

NOTAT=""
for f in "$REPO/RELEASE.md" "$NED/ki-lys-$V/ki-lys/RELEASE.md" "$NED/release-ki-lys-$V.md"; do
  [ -f "$f" ] && { NOTAT="$f"; break; }
done
if command -v gh >/dev/null 2>&1; then
  if [ -n "$NOTAT" ]; then
    gh release create "v$V" --title "KI Lys $V" --notes-file "$NOTAT" 2>/dev/null \
      || gh release edit "v$V" --title "KI Lys $V" --notes-file "$NOTAT"
  else
    gh release create "v$V" --title "KI Lys $V" --generate-notes 2>/dev/null || true
  fi
  echo "✓ Release v$V er publisert"
else
  echo "  Lag release manuelt: https://github.com/SebastianKristo/ki-lys/releases/new?tag=v$V"
fi
