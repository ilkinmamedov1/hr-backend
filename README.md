# Azərbaycan HR & Payroll ERP Platforması

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-54%20passed%20(100%25)-success.svg)](./tests)
[![Labor Code](https://img.shields.io/badge/AR%20Əmək%20Məcəlləsi-Tam%20Uyğun-red.svg)](https://e-qanun.az)

Azərbaycan Respublikasının **Əmək Məcəlləsi**, **Vergi Məcəlləsi** (qeyri-neft/özəl və neft-qaz/dövlət sektorları fərqi ilə), **"Sosial sığorta haqqında"** və **"İşsizlikdən sığorta haqqında"** qanunlarına tam uyğunlaşdırılmış, 14 modulu (M01–M14) əhatə edən milli Enterprise Kadr və Əməkhaqqı ERP Platforması.

Sistem xarici asılılıq olmadan, build prosesi tələb etməyən müasir vanilla JS SPA istifadəçi interfeysi, yüksək performanslı asinxron FastAPI backend və PostgreSQL 16 verilənlər bazası ilə təchiz edilmişdir.

---

## 🚀 1 Komandaya Quraşdırma və Başlatma (Quickstart)

Sistemi qaldırmaq üçün repozitoriyanı klonlayıb birbaşa `./start.sh` və ya `make up` icra etməyiniz kifayətdir:

```bash
# 1. Repozitoriyanı klonlayın
git clone https://github.com/ilkinmamedov1/hr-backend.git
cd hr-backend

# 2. 1 komandaya sistemi işə salın
./start.sh
```

*(Və ya `make` istifadə edirsinizsə: `make up`)*

### Bu skript nə edir?
1. `.env` faylını avtomatik aşkar edir və ya təhlükəsiz gizli açarlarla (`SECRET_KEY`, DB şifrələri) yaradır.
2. PostgreSQL 16 və FastAPI konteynerlərini Docker vasitəsilə başladır.
3. Azərbaycan Respublikasının istehsalat təqvimi (bayram və matəm günləri), vergi şkalaları və demo məlumatları bazaya seed edir.
4. Server hazır olduqda birbaşa giriş linkini və istifadəçi hesablarını terminala təqdim edir.

🌐 **Veb İnterfeys:** [http://localhost:8000](http://localhost:8000)  
📚 **İnteraktiv API Sənədləri (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)  
🗄 **Verilənlər Bazası (Adminer - dev):** [http://localhost:8080](http://localhost:8080)

---

## 🔑 Demo Giriş Hesabları

Giriş ekranında sürətli keçid üçün hazır çiplər mövcuddur. Həmçinin aşağıdakı rekvizitlərlə daxil ola bilərsiniz:

| Rol | E-poçt | Şifrə | Səlahiyyət Əhatəsi |
|:---|:---|:---|:---|
| **Superadmin** | `admin@hr.local` | `Admin123!` | Bütün modullar, sistem sazlamaları, demo idarəsi və audit |
| **HR Direktoru** | `hr@hr.local` | `Hr12345!` | Ştat, kadr əmrləri, müqavilələr, məzuniyyət və tabel təsdiqi |
| **Mühasib** | `accountant@hr.local` | `Acc12345!` | Əməkhaqqı (Payroll), vergi/DSMF, kəsintilər, dövlət hesabatları |
| **Departament Rəhbəri** | `manager@hr.local` | `Mgr12345!` | MSS (Komandam), məzuniyyət və ezamiyyət təsdiqləri |
| **İşçi** | `employee@hr.local` | `Emp12345!` | ESS (Şəxsi Kabinet), arayış (PDF), məzuniyyət sorğusu, maaş vərəqəsi |

---

## 📋 Əhatə Olunan 14 Əsas Modul (M01 – M14)

```
┌────────────────────────────────────────────────────────────────────────┐
│                   AZƏRBAYCAN HR & PAYROLL ERP MEMARLIĞI                │
├───────────────────┬───────────────────┬────────────────────────────────┤
│   Kadr və Ştat    │   İş Vaxtı & İcazə│      Əməkhaqqı & Dövlət        │
│   ────────────    │   ────────────    │      ──────────────────        │
│   M01 Struktur    │   M04 Təqvim & ƏMAS│      M07 Payroll Hesablama     │
│   M02 İşçi Şəxsi  │   M05 Tabel (T-13)│      M04 Vahid Bəyannamə       │
│   M03 Müqavilələr │   M05 Növbəli İş  │      M07 Fərdi Kəsintilər      │
│   M03 Kadr Əmrləri│   M06 Məzuniyyət  │      M08 Ezamiyyət Hesabatı    │
├───────────────────┼───────────────────┼────────────────────────────────┤
│  İşə Qəbul & İTM  │    SƏTƏM & İnkişaf│     Kabinetlər & Təhlükəsizlik │
│  ───────────────  │    ────────────── │     ────────────────────────── │
│  M09 Rekrutinq    │    M11 SƏTƏM İcazə│     M14 ESS (İşçi Kabineti)    │
│  M10 Onboarding   │    M12 Təlim-İnkişaf│   M14 MSS (Rəhbər Kabineti)  │
│  M10 Offboarding  │    M13 KPI Qiymət │     M14 Təsdiq Mərkəzi & Audit │
└───────────────────┴───────────────────┴────────────────────────────────┘
```

### M01 · Təşkilati Struktur və Ştat Cədvəli
* İyerarxik bölmə/şöbə ağacı, xərc mərkəzləri (Cost Center).
* Vəzifələr, dərəcələr (Grade level 1–10), minimum/maksimum maaş diapazonu.
* Ştat vahidləri, təsdiq olunmuş vakansiyalar, zərərli iş şəraiti əlavələri (AR ƏM m.137).

### M02 · Kadr Uçotu və İşçilərin Şəxsi İşi
* Fərdi məlumatlar: FİN kod, şəxsiyyət vəsiqəsi, ünvan, əlaqə.
* Hərbi qeydiyyat və **Hərbi Uçot Forma T-2** rəsmi dövlət hesabatı generasiyası.
* Əcnəbi işçilər üçün Dövlət Miqrasiya Xidməti (DMX) iş və yaşamaq icazələri uçotu, bitmə xəbərdarlıqları.
* Vergi güzəştləri (AR VM m.102: şəhid ailəsi, müharibə veteranı, himayəsində uşaq olanlar).
* Təhsil, sertifikatlar, ailə tərkibi və ümumi sığorta stajı.

### M03 · Əmək Müqavilələri və Kadr Əmrləri
* Müddətli və müddətsiz əmək müqavilələri, sınaq müddəti (3 aya qədər).
* Əlavə razılaşmalar (vəzifə, maaş, rejim dəyişiklikləri).
* **Rəsmi Kadr Əmrləri:** İxtisaslaşmış tiplər (İşə qəbul, Xitam, Məzuniyyət, Ezamiyyət, Mükafat, Cərimə, Növbə).
* **1 Kliklə Rəsmi PDF Generasiyası:** AR kargüzarlıq standartlarına uyğun qanuni əsaslandırmalı (AR ƏM maddəsi) əmr sənədləri.
* Mülki-hüquqi xidmət müqavilələri (VÖEN-li və VÖEN-siz icraçılar, 14%/25% gəlir vergisi və 25% DSMF tutulması).

### M04 · İstehsalat Təqvimi və Dövlət Uyğunluğu (Compliance)
* Nazirlər Kabinetinin illik qərarına uyğun avtomatik formalaşan 5 və 6 günlük təqvim.
* Rəsmi bayramlar, ümumxalq hüzn günü (20 Yanvar), səsvermə günləri və iş günü hesab edilməyən günlər öncəsi 1 saat qısaldılmış iş günləri (AR ƏM m.108).
* **Vahid Bəyannamə (Dövlət Vergi Xidməti):** Muzdlu işlə əlaqədar gəlir vergisi, DSMF, İTS və işsizlik üzrə rüblük/aylıq bəyannamə ixracı (CSV formatında BTP sisteminə idxal üçün).
* **ƏMAS İnteqrasiyası:** Əmək Müqaviləsi Bildirişləri üzrə sinxronizasiya növbəsi və status loqları.

### M05 · İş Vaxtının Uçotu, Növbəli İş Qrafikləri və Tabel (T-13)
* **Geniş Növbəli Qrafik İdarəsi:**
  * **3 Növbəli Fasiləsiz İstehsalat:** 1-ci (08:00–16:00), 2-ci (16:00–00:00), 3-cü (00:00–08:00).
  * **12 Saatlıq Növbəli Xidmət:** Gündüz (08:00–20:00) / Gecə (20:00–08:00), gün aşırı və ya 2 gün ev.
  * **24 Saatlıq Sutkalıq Növbə:** 1 sutka (24 saat) iş, 3 sutka (72 saat) istirahət.
  * **Standart 5/6 günlük rejimlər.**
* **T-13 Aylıq Tabel Matrisi:**
  * Ayın 1-dən 31-dək hər bir günün rəngli statusu (İş, Gecə, Bayram, Məzuniyyət, Xəstəlik, Ezamiyyət, Qayıb).
  * Hər gün üzrə canlı turniket vuruşlarına (giriş/çıxış) baxış və birbaşa əl ilə düzəliş (manual override) imkanı.
  * Tabelin təsdiqi və kilidlənməsi (LOCKED statusunda dəyişiklik bloklanır).
* **Turniket və Biometrik Davamiyyət Monitorinqi:**
  * Cihaz və kart loqlarının canlı monitorinqi, gecikmə dəqiqələri, ofisdə olma indikatorları.
  * Turniket CSV idxalı və sınaq simulyasiyası.

### M06 · Məzuniyyət, Xəstəlik və İcazələr
* Əsas əmək məzuniyyəti (21 və 30 gün) və staja görə əlavə məzuniyyət (m.116).
* Məzuniyyət növləri: Təhsil, Hamiləlik və doğuş (140 gün), Uşağa qulluq, Ödənişsiz icazə.
* **Xəstəlik Vərəqələri (Əmək qabiliyyətinin müvəqqəti itirilməsi):** NK-nın 189 nömrəli qərarı ilə ilk 14 günün işəgötürən tərəfindən, qalan günlərin DSMF tərəfindən hesablanması.
* Ay ərzində 3 saatadək qısamüddətli icazələrin qeydiyyatı.

### M07 · Əməkhaqqı Hesablaması (Payroll)
* **Gross-dan Net-ə 100% AR Qanunvericiliyinə Uyğun Hesablama:**
  * **Gəlir Vergisi:** Qeyri-neft/özəl sektorda 8000 AZN-dək 0%, 8000-dən yuxarı 14%; Neft-qaz sektorunda 2500 AZN-dək 14%, 2500-dən yuxarı 25%.
  * **DSMF (Məcburi Dövlət Sosial Sığortası):** İşçi tərəfindən 200 AZN-dək 3%, 200-dən yuxarı 10%; İşəgötürən tərəfindən 200 AZN-dək 22%, 200-dən yuxarı 15%.
  * **İcbari Tibbi Sığorta (İTS):** İşçi və işəgötürən tərəfindən 8000 AZN-dək 2%, 8000-dən yuxarı 0.5%.
  * **İşsizlikdən Sığorta:** Hər iki tərəfdən 0.5%.
* **Əlavələr və Kəsintilər:**
  * Gecə saatları üçün əlavə haqq (m.106: saatlıq tarifin ən azı 20%-i).
  * İstirahət və bayram günlərində iş (m.164: 2 qat əməkhaqqı).
  * İş vaxtından artıq iş (Overtime, m.165: 2 qat əməkhaqqı).
  * Turniket gecikmə cərimələri və icra sənədləri (aliment/məhkəmə) üzrə fərdi kəsintilər.
* **Hesablama Vərəqəsi (Payslip PDF):** İşçiyə təqdim olunan rəsmi ətraflı maaş vərəqəsinin PDF ixracı.

### M08 · Ezamiyyətlər
* Ölkədaxili və xarici ezamiyyət əmrləri, avans hesabatları, mehmanxana və gündəlik xərclər (NK normativləri).

### M09 – M10 · İşə Qəbul, Onboarding və Offboarding
* Kanban lövhəsi (Müraciət, İlkin baxış, Müsahibə, Təklif, Qəbul, İmtina).
* Avtomatlaşdırılmış **İş Təklifi Məktubu (Offer Letter PDF)** generasiyası.
* Onboarding tapşırıqları və sınaq müddəti monitorinqi.
* Offboarding (İşdən ayrılma) bypass-siz yoxlama vərəqəsi (Clearance Checklist) və son haqq-hesabın (istifadə edilməmiş məzuniyyət kompensasiyası daxil) ilkin kalkulyatoru.

### M11 – M13 · SƏTƏM, Təlimlər və KPI
* Əməyin təhlükəsizliyi təlimatlandırmaları (Giriş, İlkin, Təkrar), Fərdi Mühafizə Vasitələri (FMV) verilməsi və qəza aktları.
* Daxili və xarici təlimlər, iştirakçılar və sertifikatlar.
* Fərdi və departament KPI qiymətləndirmələri.

### M14 · Şəxsi Kabinet (ESS), Rəhbər Kabineti (MSS) və Sistem İnzibatçılığı
* **ESS:** İşçinin şəxsi profili, qalıq məzuniyyət günləri, elektron məzuniyyət sorğusu göndərməsi, maaş vərəqələri və **Rəsmi İş Yerindən Arayış PDF** sənədini 1 kliklə yükləməsi.
* **MSS:** Menecerin öz tabeliyində olan komanda üzvlərinə baxışı və təsdiq mərkəzi.
* **Audit Jurnalı:** Sistemdə icra edilən bütün CREATE/UPDATE/DELETE əməliyyatlarının köhnə və yeni dəyərlər fərqi (diff) və IP ünvanı ilə qeydiyyatı.

---

## ⚙️ Real İstehsalat Rejiminə Keçid və Demo Təmizlənməsi

Sistemi real şirkət bazasında tətbiq etməyə başladıqda bütün sınaq məlumatlarını silmək olduqca asandır:

1. **Superadmin** hesabı ilə daxil olun.
2. Sol menyudan **"Sistem və İnzibatçılıq"** -> **"Sistem və Demo İdarəsi"** ([`#/s/system-settings`](http://localhost:8000/#/s/system-settings)) səhifəsinə keçin (və ya yuxarı sağdakı profilinizə klikləyin).
3. **"Giriş ekranında demo hesabları gizlət"** düyməsini sıxaraq giriş ekranındakı demo düymələri söndürün.
4. **"🗑️ Demo Məlumatları Tam Sil və Real Rejimə Keç"** düyməsini sıxın və təsdiq edin.

> [!NOTE]
> Demo məlumatlar təmizlənərkən bütün sınaq işçiləri, müqavilələr, kadr əmrləri və əməkhaqqı cədvəlləri silinir. Lakin **şirkət rekvizitləri**, **təşkilati struktur**, **AR istehsalat təqvimi**, **vergi dərəcələri** və **Superadmin hesabı** toxunulmaz saxlanılır. Baza təmiz vəziyyətdə real işə hazır olur.

---

## 🛠 Əmrlər Cədvəli (Makefile Shortcuts)

| Əmr | Təsvir |
|:---|:---|
| `make up` / `./start.sh` | Bütün stack-i 1 komandaya işə salır |
| `make dev` | Debug və inkişaf rejimində qaldırır (Swagger + Adminer aktiv) |
| `make test` | Bütün 54 unit və inteqrasiya testini icra edir |
| `make down` | Bütün konteynerləri təhlükəsiz dayandırır |
| `make restart` | Konteynerləri yenidən başladır |
| `make logs` | Canlı server loqlarını izləyir |
| `make clean` | Keş və müvəqqəti test fayllarını təmizləyir |

---

## 🔒 Təhlükəsizlik və Standartlar

* **JWT Tokenlər:** `HS256` şifrələmə, `HttpOnly` / Bearer formatı, avtomatik sessiya idarəsi.
* **Şifrələmə:** `bcrypt` alqoritmi ilə duzlanmış (salted) şifrə heşləməsi.
* **SQL Injection Müdafiəsi:** Bütün sorğular SQLAlchemy 2.0 ORM və parametrləşdirilmiş sorğularla icra edilir.
* **Brute-Force Müdafiəsi:** Hər IP və istifadəçi üzrə login limitləri (15 dəqiqədə maks. 10 cəhd).
* **HTTP Təhlükəsizlik Başlıqları:** `Content-Security-Policy`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`.
* **RBAC (Rol Əsaslı Giriş Nəzarəti):** 6 fərqli rol üzrə icazələrin qat-qat yoxlanılması.
