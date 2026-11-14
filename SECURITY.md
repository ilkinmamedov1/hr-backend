# Təhlükəsizlik siyasəti

## Dəstəklənən versiya

Təhlükəsizlik düzəlişləri yalnız ən son `main` budağına tətbiq olunur.

## Zəiflik bildirişi

Zəifliyi açıq GitHub issue kimi paylaşmayın. Layihə sahibinə birbaşa
müraciət edin və aşağıdakı məlumatları göndərin:

- təsir olunan endpoint/modul;
- təkrar yaratma addımları;
- gözlənilən və faktiki nəticə;
- mümkünsə PoC sorğusu (məxfi məlumatları çıxararaq).

## Production yoxlama siyahısı

- `.env` faylını `scripts/bootstrap.sh` ilə yaradın və ya dəyərləri manual doldurun.
- `ENVIRONMENT=production`, `SEED_DEMO=false`, güclü `SECRET_KEY` və DB şifrəsi istifadə edin.
- `ENABLE_DOCS=false` saxlayın və ya `/docs` ünvanını reverse proxy səviyyəsində bağlayın.
- HTTPS-i reverse proxy (Caddy/Nginx/Traefik) ilə təmin edin.
- `APP_PORT` və DB portunu yalnız lazım olan interfeysə bind edin.
- `docker compose logs api` və audit jurnalını mütəmadi yoxlayın.
- `hr_erp_pgdata` volume-u üçün ehtiyat nüsxə (backup) qurun.
