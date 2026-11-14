# Azərbaycan HR & Payroll ERP

Excel spesifikasiyasındakı 14 modulu əhatə edən HR, əməkhaqqı, vergi və uyğunluq
sistemi. Backend **Python 3.12 + FastAPI + SQLAlchemy**, verilənlər bazası
**PostgreSQL 16**, UI isə build tələb etməyən **vanilla JS SPA**, orkestrasiya
**Docker Compose** ilə.

## Sürətli başlanğıc (production)

Tələb olunan: Docker Engine 24+ və Docker Compose v2.

```bash
git clone <repo-url> hr-erp
cd hr-erp
./scripts/bootstrap.sh
```

Skript:

1. `.env` yoxdursa təhlükəsiz təsadüfi `SECRET_KEY`, DB şifrəsi və admin şifrəsi yaradır (`chmod 600`);
2. `docker compose up -d --build` ilə stack-i qaldırır;
3. `/health` hazır olana qədər gözləyir;
4. admin e-poçtu və şifrəsini ekrana çıxarır.

Default ünvan: **http://localhost:8000**. Admin şifrəsini ilk girişdən sonra dəyişin.

### Manual konfiqurasiya

```bash
cp .env.example .env
# .env içində POSTGRES_PASSWORD, SECRET_KEY və INITIAL_ADMIN_PASSWORD dəyərlərini dəyişin
docker compose up -d --build
```

`SECRET_KEY` ən azı 32 simvol olmalıdır (`openssl rand -hex 32`).
`ENVIRONMENT=production` olduqda zəif/default `SECRET_KEY` və
`SEED_DEMO=true` ilə başlanğıc bloklanır.

### Demo / development rejimi

```bash
cp .env.example .env
# .env içində: ENVIRONMENT=development, SEED_DEMO=true, ENABLE_DOCS=true
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

Development rejimində:

- UI: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Adminer: http://localhost:8080
- PostgreSQL (yalnız localhost): `localhost:5433`, `hr` / `.env`-dəki şifrə

Demo hesablar yalnız `SEED_DEMO=true` olduqda yaradılır:

| Rol | E-poçt | Şifrə |
|---|---|---|
| SUPERADMIN | admin@hr.local | Admin123! |
| HR_DIRECTOR | hr@hr.local | Hr12345! |
| ACCOUNTANT | accountant@hr.local | Acc12345! |
| DEPT_MANAGER | manager@hr.local | Mgr12345! |
| EMPLOYEE | employee@hr.local | Emp12345! |

## Konfiqurasiya

Bütün dəyərlər `.env` və ya mühit dəyişənləri ilə verilir:

| Dəyişən | Default | Qeyd |
|---|---|---|
| `ENVIRONMENT` | `production` (compose) | `production` və ya `development` |
| `APP_PORT` | `8000` | Xarici port |
| `POSTGRES_USER` / `POSTGRES_DB` | `hr` / `hr_erp` | DB adı |
| `POSTGRES_PASSWORD` | — (məcburi) | Güclü təsadüfi dəyər |
| `SECRET_KEY` | — (məcburi) | JWT imzalama açarı, 32+ simvol |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `480` | Token müddəti |
| `AUTO_SEED` | `true` | İlk başlanğıcda seed |
| `SEED_DEMO` | `false` | Demo məlumat və demo istifadəçilər |
| `INITIAL_ADMIN_EMAIL` | `admin@hr.local` | İlk superadmin |
| `INITIAL_ADMIN_PASSWORD` | boş | Boşdursa təsadüfi şifrə logda göstərilir |
| `ENABLE_DOCS` | `false` (compose) | `/docs`, `/redoc`, `/openapi.json` |
| `CORS_ORIGINS` | boş | Vergüllə ayrılmış icazəli origin-lər |
| `ALLOWED_HOSTS` | boş | Vergüllə ayrılmış host siyahısı |
| `LOGIN_MAX_ATTEMPTS` / `LOGIN_WINDOW_MINUTES` | `10` / `15` | Login rate limit |
| `MAX_REQUEST_BYTES` | `2000000` | Maksimum sorğu ölçüsü |
| `TIMEZONE` | `Asia/Baku` | Tətbiq saat qurşağı |

## Modullar

| Modul | Əhatə |
|---|---|
| M01 | Təşkilati struktur, departamentlər, vəzifələr, ştat cədvəli, vakansiyalar |
| M02 | İşçi kartı, şəxsi iş, sənədlər, vergi güzəştləri, ailə, təhsil, hərbi uçot, miqrasiya |
| M03 | Əmək müqavilələri, əlavə razılaşmalar, kadr əmrləri, xidməti müqavilələr |
| M04 | İstehsalat təqvimi, dövlət hesabatları, ƏMAS sinxronizasiyası, uyğunluq |
| M05 | Turniket davamiyyəti, iş qrafikləri, fərdi qrafiklər, aylıq tabel (T-13) |
| M06 | Məzuniyyət növləri, balanslar, sorğular, saatlıq icazələr, xəstəlik vərəqələri |
| M07 | Əməkhaqqı komponentləri, fərdi əlavə/tutulmalar, vergi/sosial dərəcələri, payroll run |
| M08 | Ezamiyyətlər, avans və xərc hesabatları |
| M09 | Vakansiya, namizəd, kanban müraciətlər, işə qəbul, onboarding |
| M10 | Onboarding checklist və offboarding clearance |
| M11 | KPI / OKR qiymətləndirmə və payroll bonus sinxronizasiyası |
| M12 | Təlimlər, iştirakçılar, sertifikatlar |
| M13 | SƏTƏM təlimatları, tibbi müayinə, bədbəxt hadisələr, FMV uçotu |
| M14 | Auth/RBAC, təsdiq zənciri, audit jurnalı, analitika, MSS, ESS self-service, PDF/CSV eksport |

### UI iş axınları

Generic CRUD cədvəllərindən əlavə aşağıdakı əməliyyat ekranları mövcuddur:

- **M01 Təşkilat strukturu:** departament ierarxiyası və ştat vakansiyaları;
- **M03 Müqavilələr:** müqavilə detalları, düzəlişlər, məzuniyyət balansı,
  xitam və son haqq-hesab; xidməti müqavilə üzrə vergi preview;
- **M04 ƏMAS:** sinxronizasiya növbəsi və logların sinxronlaşdırılması;
- **M08 Ezamiyyətlər:** təsdiq və tamamlama;
- **M09 İşə qəbul:** mərhələli Kanban lövhəsi, müraciətin idarəsi və işə qəbul;
- **M10 Onboarding / Offboarding:** standart checklist-lər və təmizlik statusları;
- **M14 MSS:** departament rəhbərinin komanda siyahısı.

## Əsas biznes məntiqi

- **Gəlir vergisi (neft-qaz olmayan özəl sektor):** 8000 AZN-ə qədər 0%, sonra 14%.
- **Gəlir vergisi (neft-qaz və dövlət sektoru):** 2500 AZN-ə qədər 14%, sonra 25%.
- **DSMF:** işçi 200 AZN-ə qədər 3%, sonra 10%; işəgötürən 200 AZN-ə qədər 22%, sonra 15%.
- **İTS:** 8000 AZN-ə qədər 2%, sonra 0.5% (işçi və işəgötürən).
- **İşsizlik sığortası:** işçi və işəgötürən hər biri 0.5%.
- Məzuniyyət: baza 21 gün, vəzifə üzrə fərqli ola bilər; staj, uşaqlar və zərərli
  şərait üçün əlavə günlər; bayram günləri ödənişli məzuniyyət günlərinə sayılmır.
- Xəstəlik vərəqəsi: sığorta stajı <8 il — 60%, 8–12 il — 80%, 12+ il — 100%;
  ilk 14 gün işəgötürən, qalanı DSMF.
- Tabel: turniketin ilk giriş/son çıxışı, 1 saat nahar fasiləsi, gecə 22:00–06:00,
  iş saatından artıq və bayram saatları ayrıca hesablanır.
- Payroll run statusları: `DRAFT → CALCULATED → APPROVED → PAID`.
  Təsdiqlənmiş/ödənilmiş run dəyişdirilə bilməz; təkrar hesablama idempotentdir.
- Təsdiq zənciri məzuniyyət və ezamiyyətlərə bağlıdır.
- Audit: `__audited__ = True` modellərdə INSERT/UPDATE/DELETE əməliyyatları
  istifadəçi, IP və köhnə/yeni dəyərlərlə `audit_logs` cədvəlinə yazılır.
- Çoxşirkətli məhdudiyyət: `SUPERADMIN`-dən başqa istifadəçilər yalnız öz
  təşkilatlarının məlumatlarını görür; tabel, əməkhaqqı, məzuniyyət, ezamiyyət,
  müqavilə, işə qəbul, analitika və uşaq cədvəlləri təşkilat sərhədini yoxlayır.

## Təhlükəsizlik

- Şifrələr `scrypt` ilə hash olunur; JWT `SECRET_KEY` ilə imzalanır.
- Şifrə dəyişikliyi/reset `token_version`-u artırır və köhnə tokenləri ləğv edir.
- Login üçün IP/e-poçt üzrə rate limit var (default 10 cəhd / 15 dəqiqə).
- `HR_DIRECTOR` yalnız öz təşkilatında `SUPERADMIN` olmayan istifadəçiləri idarə edə bilər.
- Bütün cavablara `CSP`, `X-Frame-Options`, `nosniff`, `Referrer-Policy` başlıqları əlavə olunur.
- Production-da `SEED_DEMO=false`, `ENABLE_DOCS=false`, güclü `SECRET_KEY` və HTTPS istifadə edin.
- DB portu default olaraq host-a açılmır; Adminer yalnız development compose faylındadır.
- Container non-root istifadəçi ilə, read-only fayl sistemi və `no-new-privileges` ilə işləyir.
- Ətraflı yoxlama siyahısı: [SECURITY.md](SECURITY.md).

## Testlər

```bash
docker compose exec api pytest
# və ya host-da:
pip install -r requirements.txt
pytest
```

Testlər hesablama məntiqi, RBAC/meta filtrasiyası, təşkilat sərhədləri,
auth, API təhlükəsizliyi, müqavilə/son haqq-hesab, ƏMAS və offboarding
workflow-larını əhatə edir. GitHub Actions
`.github/workflows/ci.yml` hər push/PR-da testləri və Docker build-i işlədir.

## Faydalı endpoint-lər

| Endpoint | Təsvir |
|---|---|
| `POST /api/v1/auth/login` | JWT token (form: username, password) |
| `GET /api/v1/meta/entities` | Rol üzrə filtrlənmiş metadata |
| `GET /api/v1/system/info` | Public sistem/demo/docs məlumatı |
| `GET /health` | DB daxil health check |
| `GET /api/v1/analytics/dashboard` | HR dashboard göstəriciləri |
| `POST /api/v1/timesheets/generate?year=&month=&organization_id=` | T-13 tabel yaratma |
| `POST /api/v1/payroll-runs/{id}/calculate` | Əməkhaqqı hesabla |
| `POST /api/v1/payroll-runs/{id}/approve` | Təsdiqlə |
| `POST /api/v1/payroll-runs/{id}/pay` | Ödənildi kimi qeyd et |
| `GET /api/v1/payroll-runs/{id}/items` | Hesablama sətirləri |
| `GET /api/v1/payroll-items/{id}/payslip.pdf` | PDF hesab-vergi vərəqəsi |
| `GET /api/v1/payroll-runs/{id}/bank-register.csv` | Bank reyestri |
| `GET /api/v1/payroll-runs/{id}/gl-export.csv` | Mühasibat GL eksportu |
| `GET /api/v1/compliance/unified-declaration` | Vahid bəyannamə |
| `GET /api/v1/compliance/isb-report` | İşsizlik sığortası hesabatı |
| `GET /api/v1/departments/tree` | Departament ierarxiyası |
| `GET /api/v1/staffing/vacancies` | Ştat vakansiyaları |
| `GET /api/v1/contracts/{id}/amendments` | Müqavilə düzəlişləri |
| `POST /api/v1/contracts/{id}/amendments` | Yeni müqavilə düzəlişi |
| `POST /api/v1/contracts/{id}/terminate` | Müqavilənin xitamı + son haqq-hesab |
| `POST /api/v1/leave-balances/initialize` | Müqavilə üzrə balans yaratma |
| `GET /api/v1/employees/{id}/final-settlement-preview` | Son haqq-hesab preview |
| `GET /api/v1/service-contracts/{id}/tax-preview` | Xidməti müqavilə vergi hesabı |
| `POST /api/v1/trips/{id}/approve` | Ezamiyyəti təsdiqlə |
| `POST /api/v1/trips/{id}/complete` | Ezamiyyəti tamamla |
| `POST /api/v1/compliance/emas/queue` | ƏMAS növbəsinə sal |
| `POST /api/v1/compliance/emas/{id}/mark-synced` | ƏMAS logunu sinxronlaşdır |
| `POST /api/v1/applications/{id}/stage` | Müraciətin mərhələsini dəyiş |
| `POST /api/v1/applications/{id}/hire` | Namizədi işə qəbul et |
| `GET /api/v1/offboarding/{id}` | İşçinin offboarding bəndləri |
| `POST /api/v1/offboarding/{id}/checklist` | Standart offboarding checklist |
| `GET /api/v1/mss/team` | Rəhbərin komanda siyahısı |
| `GET /api/v1/approvals/pending` | Gözləyən təsdiqlər |
| `POST /api/v1/approvals/{id}/decide` | Təsdiq/rədd qərarı |
| `GET /api/v1/audit-logs` | Audit jurnalı (yalnız SUPERADMIN) |
| `GET /api/v1/ess/me` | İşçinin öz profili |
| `GET /api/v1/ess/payslips` | İşçinin öz hesab-vergi vərəqələri |
| `POST /api/v1/ess/leave-requests` | İşçinin məzuniyyət sorğusu |

## Layihə strukturu

```text
hr-erp/
├── app/
│   ├── api/                     # CRUD, RBAC, 14 modul router-ləri
│   ├── core/                    # config, DB, security, audit
│   ├── models/                  # SQLAlchemy modelləri
│   ├── services/                # payroll, leave, timesheet, export, workflow
│   ├── static/                  # Vanilla JS SPA
│   ├── seed.py                  # İstinad + demo məlumatlar
│   └── main.py                  # FastAPI tətbiqi
├── db/init.sql                  # PostgreSQL extension-ları
├── scripts/bootstrap.sh         # Bir komandalı deploy
├── scripts/entrypoint.sh        # DB gözləmə + uvicorn
├── tests/                       # Hesablama, RBAC və təhlükəsizlik testləri
├── .github/workflows/ci.yml     # GitHub Actions CI
├── docker-compose.yml           # Production stack
├── docker-compose.dev.yml       # Development override
├── Dockerfile
├── SECURITY.md
└── requirements.txt
```

## Ehtiyat nüsxə və sıfırlama

```bash
# Backup
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > hr_erp_backup.sql

# Demo bazanı tam sıfırlamaq (bütün məlumat silinir!)
docker compose down -v
./scripts/bootstrap.sh
```

## Məhdudiyyətlər

- Sxem yeniləmələri hazırda `create_all` + kiçik uyğunluq DDL ilə idarə olunur;
  tam miqrasiya sistemi (Alembic) hələ qoşulmayıb.
- ƏMAS, bank və dövlət portalı inteqrasiyaları eksport/növbə səviyyəsindədir;
  xarici API çağırışları yoxdur.
- CV, sənəd skanı və digər fayl yükləmələri hazırda UI-də yoxdur; `cv_url`,
  `file_path` və `photo_path` sahələri yalnız metadata saxlayır.
- İstehsalat təqvimində 2025–2027 üçün Ramazan/Qurban tarixləri təxminidir;
  rəsmi tarixlərlə `production_calendar` cədvəlindən düzəldin.
- Production-da HTTPS-i reverse proxy (Caddy, Nginx, Traefik) ilə təmin edin;
  TLS bu stack daxilində yoxdur.
