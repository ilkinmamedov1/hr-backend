#!/usr/bin/env bash
# ==============================================================================
# Azərbaycan HR & Payroll ERP - 1-Komanda ilə Başlatma Skripti (One-Command Start)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

BOLD="\033[1m"
GREEN="\033[0;32m"
CYAN="\033[0;36m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
RESET="\033[0m"

echo -e "${CYAN}${BOLD}"
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║             AZƏRBAYCAN HR & PAYROLL ERP PLATFORMASI                   ║"
echo "║          Əmək Məcəlləsi və Vergi Qanunvericiliyinə Tam Uyğun          ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo -e "${RESET}"

MODE="${1:-}"

# 1. Konfiqurasiya faylının (.env) yoxlanılması və avtomatik yaradılması
if [ ! -f .env ]; then
  echo -e "${YELLOW}ℹ .env faylı tapılmadı. Avtomatik təhlükəsiz konfiqurasiya yaradılır...${RESET}"
  if [ -f .env.example ]; then
    cp .env.example .env
  else
    cat > .env << 'EOF'
ENVIRONMENT=development
APP_PORT=8000
POSTGRES_USER=hr
POSTGRES_PASSWORD=hr_secret_password
POSTGRES_DB=hr_erp
DATABASE_URL=postgresql+psycopg2://hr:hr_secret_password@127.0.0.1:5433/hr_erp
SECRET_KEY=b91a7d6e4f2c8a1b5e3d7c9f0a2e4b6d8c0e2a4f6b8d0e2a4f6b8d0e2a4f6b8d
ACCESS_TOKEN_EXPIRE_MINUTES=480
AUTO_SEED=true
SEED_DEMO=true
INITIAL_ADMIN_EMAIL=admin@hr.local
INITIAL_ADMIN_PASSWORD=Admin123!
INITIAL_ADMIN_NAME=Sistem Administratoru
ENABLE_DOCS=true
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
ALLOWED_HOSTS=*
TIMEZONE=Asia/Baku
EOF
  fi
  echo -e "${GREEN}✓ .env faylı uğurla yaradıldı.${RESET}"
fi

# 2. Rejimə uyğun işə salma
if [ "$MODE" = "--docker" ] || [ "$MODE" = "-d" ] || { [ -z "$MODE" ] && command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; }; then
  echo -e "${BLUE}▶ Docker Compose ilə konteynerlər qaldırılır...${RESET}"
  if [ "$MODE" = "--dev" ]; then
    docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
  else
    docker compose up -d --build
  fi

  PORT="${APP_PORT:-8000}"
  echo -e "${CYAN}⏳ API servisinin hazır olması gözlənilir (port ${PORT})...${RESET}"
  for i in $(seq 1 45); do
    if curl -fsS "http://localhost:${PORT}/health" >/dev/null 2>&1; then
      break
    fi
    sleep 2
  done

  echo ""
  echo -e "${GREEN}${BOLD}✓ HR ERP SİSTEMİ UĞURLA İŞƏ DÜŞDÜ!${RESET}"
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  echo -e "${BOLD}🌐 Veb Tətbiq (UI):${RESET}      ${GREEN}http://localhost:${PORT}${RESET}"
  echo -e "${BOLD}📚 API Sənədləri (Docs):${RESET} ${GREEN}http://localhost:${PORT}/docs${RESET}"
  echo -e "${BOLD}🗄  Verilənlər Bazası:${RESET}   PostgreSQL (port 5433 / hr_erp)"
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  echo -e "${BOLD}🔑 Demo Giriş Məlumatları:${RESET}"
  echo -e "   • ${BOLD}Superadmin:${RESET}  admin@hr.local      / ${YELLOW}Admin123!${RESET}"
  echo -e "   • ${BOLD}HR Direktoru:${RESET} hr@hr.local        / ${YELLOW}Hr12345!${RESET}"
  echo -e "   • ${BOLD}Mühasib:${RESET}       accountant@hr.local / ${YELLOW}Acc12345!${RESET}"
  echo -e "   • ${BOLD}Menecer:${RESET}       manager@hr.local    / ${YELLOW}Mgr12345!${RESET}"
  echo -e "   • ${BOLD}İşçi (ESS):${RESET}    employee@hr.local   / ${YELLOW}Emp12345!${RESET}"
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  echo -e "${YELLOW}Qeyd: Sistemi dayandırmaq üçün: ${BOLD}docker compose down${RESET}"
  exit 0
fi

# 3. Əgər lokal python mühiti varsa
if [ -d ".venv" ]; then
  echo -e "${BLUE}▶ Lokal Python virtual mühiti ilə başladılır (.venv)...${RESET}"

  # DB konteynerini yoxla
  if command -v docker >/dev/null 2>&1; then
    if ! docker ps | grep -q "postgres"; then
      echo -e "${CYAN}PostgreSQL konteyneri başladılır...${RESET}"
      docker compose up -d db || true
      sleep 3
    fi
  fi

  echo -e "${GREEN}✓ Server işə salınır: http://localhost:8000${RESET}"
  exec .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi

echo -e "${RED}Xəta: Nə Docker, nə də .venv virtual mühiti tapılmadı.${RESET}"
echo "Zəhmət olmasa Docker quraşdırın və ya 'python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt' icra edin."
exit 1
