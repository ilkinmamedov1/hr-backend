#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker tapılmadı. Əvvəlcə Docker Engine/Desktop quraşdırın." >&2
  exit 1
fi

random_hex() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex "$1"
  else
    head -c "$1" /dev/urandom | od -An -tx1 | tr -d ' \n'
  fi
}

if [ ! -f .env ]; then
  umask 077
  DB_PASSWORD="$(random_hex 16)"
  SECRET_KEY="$(random_hex 32)"
  ADMIN_PASSWORD="$(random_hex 12)"
  cat > .env <<ENV
COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME:-hr-erp}
ENVIRONMENT=production
APP_PORT=${APP_PORT:-8000}
POSTGRES_USER=hr
POSTGRES_DB=hr_erp
POSTGRES_PASSWORD=${DB_PASSWORD}
SECRET_KEY=${SECRET_KEY}
ACCESS_TOKEN_EXPIRE_MINUTES=480
AUTO_SEED=true
SEED_DEMO=false
INITIAL_ADMIN_EMAIL=${INITIAL_ADMIN_EMAIL:-admin@hr.local}
INITIAL_ADMIN_PASSWORD=${ADMIN_PASSWORD}
INITIAL_ADMIN_NAME=Sistem Administratoru
ENABLE_DOCS=false
CORS_ORIGINS=
ALLOWED_HOSTS=
LOGIN_MAX_ATTEMPTS=10
LOGIN_WINDOW_MINUTES=15
MAX_REQUEST_BYTES=2000000
TIMEZONE=Asia/Baku
ENV
  echo ".env yaradıldı (icazələr 600)."
else
  echo "Mövcud .env istifadə olunur."
fi

set -a
# shellcheck disable=SC1091
. ./.env
set +a

docker compose up -d --build

echo "API hazır olana qədər gözlənilir..."
for _ in $(seq 1 60); do
  if curl -fsS "http://localhost:${APP_PORT:-8000}/health" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

if ! curl -fsS "http://localhost:${APP_PORT:-8000}/health" >/dev/null 2>&1; then
  echo "API vaxtında hazır olmadı. Loglara baxın: docker compose logs api" >&2
  exit 1
fi

cat <<INFO

HR ERP işə düşdü: http://localhost:${APP_PORT:-8000}
Admin e-poçtu: ${INITIAL_ADMIN_EMAIL}
Admin şifrəsi: ${INITIAL_ADMIN_PASSWORD}
(Nümunə: ${POSTGRES_USER}/${POSTGRES_DB})

Şifrəni daxil olduqdan sonra dəyişin. Konfiqurasiya: .env
INFO
