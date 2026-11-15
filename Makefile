.PHONY: help up dev down restart test logs clean

help:
	@echo "Azərbaycan HR & Payroll ERP İdarəetmə Əmrləri:"
	@echo "  make up       - Sistemi 1 komandaya qaldırır (Docker və ya lokal)"
	@echo "  make dev      - Development rejimində qaldırır (Adminer + Swagger aktiv)"
	@echo "  make down     - Bütün konteynerləri dayandırır"
	@echo "  make restart  - Sistemi yenidən başladır"
	@echo "  make test     - Bütün test paketini icra edir (54 test)"
	@echo "  make logs     - Server loqlarına bərabər baxır"
	@echo "  make clean    - Keş və müvəqqəti faylları təmizləyir"

up:
	./start.sh

dev:
	./start.sh --dev

down:
	docker compose down

restart:
	docker compose restart

test:
	.venv/bin/pytest -v

logs:
	docker compose logs -f

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
