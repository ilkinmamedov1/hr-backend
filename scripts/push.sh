#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

echo "GitHub-a göndərilir (ilkinmamedov1/hr-backend)..."

# SSH bağlantısını yoxla
if ssh -q -o BatchMode=yes -o ConnectTimeout=4 -T git@github.com 2>&1 | grep -qi "successfully authenticated"; then
  echo "✓ SSH autentifikasiyası aşkar edildi. SSH ilə göndərilir..."
  git remote set-url origin git@github.com:ilkinmamedov1/hr-backend.git
  git push -u origin main
  echo "✓ Kodlar uğurla GitHub-a göndərildi!"
  exit 0
fi

echo "HTTPS ilə göndərilir (GitHub istifadəçi adı və ya Personal Access Token tələb oluna bilər)..."
git push -u origin main
