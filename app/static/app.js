(function () {
  'use strict';

  var API = '/api/v1';
  var MONTHS = ['Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'İyun', 'İyul', 'Avqust', 'Sentyabr', 'Oktyabr', 'Noyabr', 'Dekabr'];
  var MONTHS_SHORT = ['Yan', 'Fev', 'Mar', 'Apr', 'May', 'İyn', 'İyl', 'Avq', 'Sen', 'Okt', 'Noy', 'Dek'];

  var VALUE_LABELS = {
    ACTIVE: 'Aktiv', INACTIVE: 'Deaktiv', ON_LEAVE: 'Məzuniyyətdə', SUSPENDED: 'Dayandırılıb',
    TERMINATED: 'Xitam', DRAFT: 'Qaralama', CALCULATED: 'Hesablanıb', APPROVED: 'Təsdiqlənib',
    PAID: 'Ödənilib', PENDING: 'Gözləyir', REJECTED: 'Rədd edilib', CANCELLED: 'Ləğv edilib',
    COMPLETED: 'Tamamlanıb', OPEN: 'Açıq', CLOSED: 'Bağlı', LOCKED: 'Kilidlənib', SYNCED: 'Sinxron',
    QUEUED: 'Növbədə', SENT: 'Göndərilib', FAILED: 'Uğursuz', SIGNED: 'İmzalanıb',
    NEW: 'Yeni', CALL: 'Zəng', INTERVIEW: 'Müsahibə', TASK: 'Tapşırıq', OFFER: 'Təklif',
    HIRED: 'İşə qəbul', REGISTERED: 'Qeydiyyatda', ATTENDED: 'İştirak edib', ABSENT: 'Gəlməyib',
    DONE: 'Tamamlanıb', IN_PROGRESS: 'İcradadır', WAIVED: 'Bağışlanıb',
    EARNING: 'Gəlir komponenti', DEDUCTION: 'Tutulma', REGULAR: 'Adi', BONUS: 'Bonus', FINAL: 'Yekun',
    WORKDAY: 'İş günü', WEEKEND: 'İstirahət', HOLIDAY: 'Bayram', MOURNING: 'Matəm',
    SHORT_WORKDAY: 'Qısa gün', MAIN: 'Əsas', PART_TIME: 'Yarım ştat', CONTRACT: 'Müqavilə',
    INDEFINITE: 'Müddətsiz', FIXED_TERM: 'Müddətli', MONTHLY: 'Aylıq', HOURLY: 'Saatlıq',
    NON_OIL_PRIVATE: 'Neft-qaz olmayan özəl', OIL_PUBLIC: 'Neft-qaz / dövlət',
    SINGLE: 'Subay', MARRIED: 'Evli', DIVORCED: 'Boşanmış', WIDOWED: 'Dul',
    M: 'Kişi', F: 'Qadın', IN: 'Giriş', OUT: 'Çıxış',
    SUPERADMIN: 'Superadmin', HR_DIRECTOR: 'HR direktoru', HR_SPECIALIST: 'HR mütəxəssisi',
    ACCOUNTANT: 'Mühasib', DEPT_MANAGER: 'Departament rəhbəri', EMPLOYEE: 'İşçi',
    INTERNAL: 'Daxili', EXTERNAL: 'Xarici', ONLINE: 'Onlayn',
    LOW: 'Aşağı', MEDIUM: 'Orta', HIGH: 'Yüksək', CRITICAL: 'Kritik',
    FIT: 'Yararlı', RESTRICTED: 'Məhdudiyyətlə', UNFIT: 'Yararsız',
    ID_CARD: 'Şəxsiyyət vəsiqəsi', PASSPORT: 'Pasport', MILITARY: 'Hərbi', DIPLOMA: 'Diplom',
    MEDICAL: 'Tibbi', OTHER: 'Digər', CHILD: 'Uşaq', SPOUSE: 'Həyat yoldaşı', PARENT: 'Valideyn',
    SIBLING: 'Qardaş/bacı', INSERT: 'Əlavə etmə', UPDATE: 'Dəyişiklik', DELETE: 'Silmə',
    LEAVE_REQUEST: 'Məzuniyyət sorğusu', BUSINESS_TRIP: 'Ezamiyyət',
    WORK_PERMIT: 'İş icazəsi', RESIDENCE_PERMIT: 'Yaşayış icazəsi', TEMPORARY: 'Müvəqqəti',
    SECONDARY: 'Orta', BACHELOR: 'Bakalavr', MASTER: 'Magistr', PHD: 'Fəlsəfə doktoru',
    STANDARD_5: 'Standart 5 günlük', SHIFT: 'Növbəli', FLEXIBLE: 'Çevik',
    PLANNED: 'Planlaşdırılıb', ONGOING: 'Davam edir', SUBMITTED: 'Təqdim edilib', ACCEPTED: 'Qəbul edilib',
    HIRE: 'İşə qəbul', TRANSFER: 'Köçürmə', LEAVE: 'Məzuniyyət', DISCIPLINARY: 'İntizam',
    SYNC: 'Sinxronlaşdırma', CREATE: 'Yaratma',
    UNIFIED_DECLARATION: 'Vahid bəyannamə', ISB: 'İşsizlik sığortası', STATISTICS: 'Statistika',
    ON_HOLD: 'Dayandırılıb', INTRO: 'Giriş', REPEAT: 'Təkrar', TARGETED: 'Hədəfli',
    MINOR_INJURY: 'Yüngül xəsarət', SERIOUS_INJURY: 'Ağır xəsarət', FATALITY: 'Ölüm',
    NEAR_MISS: 'Təhlükəli hal', PROPERTY_DAMAGE: 'Əmlaka ziyan',
    ANNUAL: 'Əmək məzuniyyəti', ANNUAL_EXTRA: 'Əlavə məzuniyyət', MATERNITY: 'Hamiləlik və doğuş',
    CHILD_CARE: 'Uşağa qulluq', EDUCATION: 'Təhsil', UNPAID: 'Ödənişsiz', SICK: 'Xəstəlik',
    SOCIAL: 'Sosial', BASE: 'Əsas əməkhaqqı', OVERTIME: 'İş vaxtından artıq', NIGHT: 'Gecə',
    VACATION: 'Məzuniyyət', BONUS_KPI: 'KPI bonusu', ALLOWANCE: 'Fərdi əlavə', ALIMONY: 'Aliment',
    ADVANCE: 'Avans', EXECUTION: 'İcra sənədi'
  };

  var ICONS = {
    dashboard: '<rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/>',
    users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    user: '<circle cx="12" cy="7" r="4"/><path d="M5 21v-2a7 7 0 0 1 14 0v2"/>',
    building: '<path d="M3 21h18M5 21V7l7-4 7 4v14M9 9h1M14 9h1M9 13h1M14 13h1M9 17h1M14 17h1"/>',
    tree: '<path d="M12 3v6M6 21v-4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v4M12 9v6"/><rect x="3" y="17" width="6" height="4" rx="1"/><rect x="15" y="17" width="6" height="4" rx="1"/><rect x="9" y="3" width="6" height="6" rx="1"/>',
    briefcase: '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 12h18"/>',
    grid: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    file: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M9 13h6M9 17h6"/>',
    percent: '<path d="M19 5 5 19"/><circle cx="7" cy="7" r="2.5"/><circle cx="17" cy="17" r="2.5"/>',
    family: '<circle cx="9" cy="7" r="3"/><path d="M3 21v-2a6 6 0 0 1 12 0v2"/><circle cx="18" cy="9" r="2.2"/><path d="M16 21v-1.5a4 4 0 0 1 5-3.8"/>',
    graduation: '<path d="M22 10 12 5 2 10l10 5 10-5z"/><path d="M6 12v5c0 1.5 2.7 3 6 3s6-1.5 6-3v-5M22 10v6"/>',
    shield: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18"/>',
    contract: '<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M10 11h5M10 15h5M10 19h3"/>',
    stamp: '<path d="M12 3a3 3 0 0 1 3 3c0 2-1 3-1 5h-4c0-2-1-3-1-5a3 3 0 0 1 3-3zM8 14h8l1 5H7zM5 22h14"/>',
    report: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 17v-3M12 17v-6M16 17v-4"/>',
    sync: '<path d="M21 12a9 9 0 0 1-15 6.7L3 16M3 12a9 9 0 0 1 15-6.7L21 8"/><path d="M3 21v-5h5M21 3v5h-5"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    'calendar-grid': '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4M16 3v4M3 10h18M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01"/>',
    'calendar-user': '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4M16 3v4M3 10h18"/><circle cx="12" cy="15" r="2"/><path d="M9 19a3 3 0 0 1 6 0"/>',
    palmtree: '<path d="M12 21v-8M8 21h8"/><path d="M12 13c-4 0-7-2-7-4 3 0 5 1 7 4zM12 13c4 0 7-2 7-4-3 0-5 1-7 4zM12 13c-1-4 0-7 2-9 1 3 0 6-2 9z"/>',
    scale: '<path d="M12 3v18M7 21h10M5 7h14M5 7l-3 7h6zM19 7l-3 7h6z"/>',
    hourglass: '<path d="M6 3h12M6 21h12M7 3c0 5 5 6 5 9s-5 4-5 9M17 3c0 5-5 6-5 9s5 4 5 9"/>',
    coins: '<ellipse cx="9" cy="6" rx="5" ry="3"/><path d="M4 6v4c0 1.7 2.2 3 5 3s5-1.3 5-3V6"/><path d="M4 10v4c0 1.7 2.2 3 5 3 1 0 2-.2 2.8-.5"/><ellipse cx="16" cy="15" rx="4.5" ry="2.6"/><path d="M11.5 15v4c0 1.5 2 2.6 4.5 2.6s4.5-1.1 4.5-2.6v-4"/>',
    plane: '<path d="M2 12l20-7-7 20-3-8-10-5z"/>',
    receipt: '<path d="M6 2h12v20l-3-2-3 2-3-2-3 2z"/><path d="M9 7h6M9 11h6M9 15h4"/>',
    megaphone: '<path d="M3 11v2a1 1 0 0 0 1 1h2l4 4V6L6 10H4a1 1 0 0 0-1 1zM14 8a5 5 0 0 1 0 8M17 5a9 9 0 0 1 0 14"/>',
    'user-search': '<circle cx="10" cy="7" r="4"/><path d="M3 21v-2a6 6 0 0 1 10-4.5"/><circle cx="18" cy="17" r="3"/><path d="m21 20-2-2"/>',
    inbox: '<path d="M4 4h16l2 10v4a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-4z"/><path d="M2 14h5l2 3h6l2-3h5"/>',
    checklist: '<path d="M9 5h11M9 12h11M9 19h11M4 5l1.2 1.2L7 4M4 12l1.2 1.2L7 11M4 19l1.2 1.2L7 18"/>',
    logout: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>',
    target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/>',
    presentation: '<path d="M3 4h18M4 4v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4M12 16v5M8 21h8"/>',
    certificate: '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 10h4M8 13h3M17 4v12M15 16l2 4 2-4"/>',
    safety: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    health: '<path d="M20.8 5.6a5.5 5.5 0 0 0-7.8 0L12 6.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 22l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/>',
    helmet: '<path d="M4 15a8 8 0 0 1 16 0M2 15h20v3H2zM9 6a5 5 0 0 1 6 0"/>',
    alert: '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0zM12 9v4M12 17h.01"/>',
    wallet: '<path d="M20 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0 0 4h15v14H5a2 2 0 0 1-2-2V5"/><path d="M16 13h.01"/>',
    check: '<path d="M20 6 9 17l-5-5"/>',
    list: '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
    dot: '<circle cx="12" cy="12" r="4"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    refresh: '<path d="M21 12a9 9 0 0 1-15 6.7L3 16M3 12a9 9 0 0 1 15-6.7L21 8"/><path d="M3 21v-5h5M21 3v5h-5"/>',
    edit: '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
    trash: '<path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6M10 11v5M14 11v5"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    download: '<path d="M12 3v12M7 10l5 5 5-5M5 21h14"/>',
    'arrow-left': '<path d="M19 12H5M12 19l-7-7 7-7"/>',
    calendar: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4M16 3v4M3 10h18"/>',
    chart: '<path d="M3 3v18h18M7 15l4-4 3 3 5-6"/>',
    'log-in': '<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3"/>',
    close: '<path d="M18 6 6 18M6 6l12 12"/>'
  };

  var STATUS_KIND = {
    ACTIVE: 'success', APPROVED: 'success', PAID: 'success', COMPLETED: 'success', DONE: 'success',
    SYNCED: 'success', ACCEPTED: 'success', HIRED: 'success', ATTENDED: 'success', SIGNED: 'success',
    FIT: 'success', LOW: 'success',
    CALCULATED: 'info', OPEN: 'info', NEW: 'info', SENT: 'info', SUBMITTED: 'info',
    IN_PROGRESS: 'info', ONGOING: 'info', INTERVIEW: 'info', OFFER: 'info', TASK: 'info', CALL: 'info',
    WORKDAY: 'info',
    PENDING: 'warning', QUEUED: 'warning', PLANNED: 'warning', REGISTERED: 'warning', MEDIUM: 'warning',
    SHORT_WORKDAY: 'warning',
    DRAFT: 'neutral', LOCKED: 'neutral', ON_HOLD: 'neutral', INACTIVE: 'neutral', WAIVED: 'neutral',
    WEEKEND: 'neutral', MOURNING: 'neutral',
    REJECTED: 'danger', CANCELLED: 'danger', TERMINATED: 'danger', FAILED: 'danger', ABSENT: 'danger',
    UNFIT: 'danger', CRITICAL: 'danger', HIGH: 'danger', HOLIDAY: 'danger'
  };

  var state = {
    token: localStorage.getItem('hr_token') || null,
    user: readJSON(localStorage.getItem('hr_user')),
    meta: null,
    entityMap: {},
    entityRows: {},
    lookups: {},
    entityState: {},
    leaveFilter: 'ALL',
    timesheetYear: '',
    timesheetMonth: '',
    calendarYear: null,
    calendarMonth: null,
    complianceYear: null,
    complianceMonth: null,
    reportsDays: 60,
    onboardingEmployee: null,
    systemInfo: null,
    renderSeq: 0,
    activeGroup: null
  };

  function readJSON(value) {
    try { return value ? JSON.parse(value) : null; } catch (err) { return null; }
  }

  function $(selector, root) {
    return (root || document).querySelector(selector);
  }

  function $$(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  function esc(value) {
    return String(value === null || value === undefined ? '' : value)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function icon(name, className) {
    return '<svg class="' + (className || '') + '" viewBox="0 0 24 24" aria-hidden="true">' + (ICONS[name] || ICONS.dot) + '</svg>';
  }

  function pad(value) { return String(value).padStart(2, '0'); }

  function fmtDate(value) {
    if (!value) return '—';
    var date = new Date(value);
    if (isNaN(date.getTime())) return esc(value);
    return pad(date.getDate()) + '.' + pad(date.getMonth() + 1) + '.' + date.getFullYear();
  }

  function fmtDateTime(value) {
    if (!value) return '—';
    var date = new Date(value);
    if (isNaN(date.getTime())) return esc(value);
    return fmtDate(value) + ' ' + pad(date.getHours()) + ':' + pad(date.getMinutes());
  }

  function fmtNumber(value, digits) {
    if (value === null || value === undefined || value === '') return '—';
    var number = Number(value);
    if (isNaN(number)) return esc(value);
    var places = digits === undefined ? 2 : digits;
    try {
      return number.toLocaleString('az-AZ', { minimumFractionDigits: places, maximumFractionDigits: places });
    } catch (err) {
      return number.toFixed(places);
    }
  }

  function fmtMoney(value) {
    if (value === null || value === undefined || value === '') return '—';
    return fmtNumber(value, 2) + ' ₼';
  }

  function fmtShortMoney(value) {
    var number = Number(value) || 0;
    if (Math.abs(number) >= 1000000) return (number / 1000000).toFixed(1) + 'M';
    if (Math.abs(number) >= 1000) return (number / 1000).toFixed(1) + 'k';
    return String(Math.round(number));
  }

  function humanize(value) {
    if (value === null || value === undefined || value === '') return '—';
    if (VALUE_LABELS[value]) return VALUE_LABELS[value];
    var text = String(value).replace(/_/g, ' ').toLowerCase();
    return text.charAt(0).toUpperCase() + text.slice(1);
  }

  function initials(name) {
    var parts = String(name || '?').trim().split(/\s+/);
    return (parts[0].charAt(0) + (parts.length > 1 ? parts[parts.length - 1].charAt(0) : '')).toUpperCase();
  }

  function badge(value, kind) {
    var level = kind || STATUS_KIND[value] || 'neutral';
    return '<span class="badge ' + level + '">' + esc(humanize(value)) + '</span>';
  }

  function equals(a, b) { return String(a) === String(b); }

  function todayLabel() {
    var now = new Date();
    return now.getDate() + ' ' + MONTHS[now.getMonth()] + ' ' + now.getFullYear();
  }

  function toast(message, kind, detail) {
    var root = $('#toast-root');
    var el = document.createElement('div');
    el.className = 'toast ' + (kind || '');
    el.innerHTML = '<div>' + esc(message) + (detail ? '<small>' + esc(detail) + '</small>' : '') + '</div>';
    root.appendChild(el);
    setTimeout(function () {
      el.style.opacity = '0';
      el.style.transform = 'translateY(6px)';
      el.style.transition = 'all .2s';
      setTimeout(function () { el.remove(); }, 220);
    }, kind === 'error' ? 6500 : 4200);
  }

  function closeModal() { $('#modal-root').innerHTML = ''; }

  function openModal(options) {
    var root = $('#modal-root');
    var footer = options.footer ? '<div class="modal-foot">' + options.footer + '</div>' : '';
    root.innerHTML = '<div class="modal-backdrop" data-modal-backdrop><div class="modal ' + (options.size || '') + '" role="dialog" aria-modal="true">' +
      '<div class="modal-head"><div><h2>' + esc(options.title) + '</h2>' +
      (options.subtitle ? '<p>' + esc(options.subtitle) + '</p>' : '') +
      '</div><button class="modal-close" type="button" data-act="modal-close" aria-label="Bağla">&times;</button></div>' +
      '<div class="modal-body">' + options.body + '</div>' + footer + '</div></div>';
    return root.firstElementChild;
  }

  function setHeader(title, subtitle) {
    $('#page-title').textContent = title;
    $('#page-subtitle').textContent = subtitle || '';
  }

  function loadingHTML(text) {
    return '<div class="card card-pad"><div class="loading-line"></div><p class="hint mt-12">' + esc(text || 'Yüklənir...') + '</p></div>';
  }

  function errorCard(message) {
    return '<div class="alert danger"><div><strong>Xəta:</strong> ' + esc(message || 'Naməlum xəta') + '</div></div>';
  }

  function emptyState(title, text) {
    return '<div class="empty-state"><div class="empty-icon">' + icon('inbox') + '</div><strong>' + esc(title) + '</strong><p>' + esc(text || '') + '</p></div>';
  }

  async function api(path, options) {
    options = options || {};
    var headers = Object.assign({}, options.headers || {});
    if (state.token) headers.Authorization = 'Bearer ' + state.token;
    var body;
    if (options.form) {
      headers['Content-Type'] = 'application/x-www-form-urlencoded';
      body = new URLSearchParams(options.form).toString();
    } else if (options.body !== undefined) {
      headers['Content-Type'] = 'application/json';
      body = JSON.stringify(options.body);
    }
    var response = await fetch(API + path, { method: options.method || 'GET', headers: headers, body: body });
    if (response.status === 401 && state.token) {
      forceLogout('Sessiyanın müddəti bitdi. Yenidən daxil olun.');
      throw new Error('Sessiya bitdi');
    }
    var text = await response.text();
    var data = null;
    if (text) {
      try { data = JSON.parse(text); } catch (err) { data = text; }
    }
    if (!response.ok) {
      var detail = data && data.detail ? data.detail : (response.statusText || 'Sorğu uğursuz oldu');
      if (typeof detail !== 'string') detail = JSON.stringify(detail);
      var error = new Error(detail);
      error.status = response.status;
      throw error;
    }
    return data;
  }

  async function downloadFile(path, filename) {
    var response = await fetch(API + path, { headers: state.token ? { Authorization: 'Bearer ' + state.token } : {} });
    if (!response.ok) {
      var message = 'Fayl yüklənmədi';
      try {
        var data = await response.json();
        if (data && data.detail) message = data.detail;
      } catch (err) { }
      throw new Error(message);
    }
    var blob = await response.blob();
    var url = URL.createObjectURL(blob);
    var link = document.createElement('a');
    link.href = url;
    link.download = filename || 'export';
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1200);
  }

  function normalizeList(data) {
    if (Array.isArray(data)) return { items: data, total: data.length };
    return { items: (data && data.items) || [], total: data && data.total !== undefined ? data.total : ((data && data.items) || []).length };
  }

  var LOOKUP_PATHS = { users: '/auth/users' };

  async function getLookup(ref, refresh) {
    if (!state.lookups[ref] || refresh) {
      var data = await api((LOOKUP_PATHS[ref] || '/' + ref) + '?limit=500');
      state.lookups[ref] = normalizeList(data).items;
    }
    return state.lookups[ref];
  }

  async function ensureLookups(refs) {
    var unique = Array.from(new Set(refs.filter(Boolean)));
    await Promise.all(unique.map(function (ref) {
      return getLookup(ref).catch(function () { return []; });
    }));
  }

  function findLookup(ref, id) {
    var list = state.lookups[ref] || [];
    for (var i = 0; i < list.length; i += 1) {
      if (equals(list[i].id, id)) return list[i];
    }
    return null;
  }

  function refLabel(ref, id) {
    if (id === null || id === undefined || id === '') return '—';
    var row = findLookup(ref, id);
    if (!row) return '#' + id;
    switch (ref) {
      case 'employees':
        return [row.last_name, row.first_name].filter(Boolean).join(' ') + (row.pin_code ? ' · ' + row.pin_code : '');
      case 'organizations': return row.name || row.short_name || ('#' + id);
      case 'departments': return row.name || row.code || ('#' + id);
      case 'positions': return row.title || ('#' + id);
      case 'staffing': return 'Ştat #' + row.id + (row.base_salary !== undefined && row.base_salary !== null ? ' · ' + fmtNumber(row.base_salary, 0) + ' ₼' : '');
      case 'contracts': return row.contract_number || ('Müqavilə #' + id);
      case 'leave-types': return row.name || row.code || ('#' + id);
      case 'payroll-components': return row.name || row.code || ('#' + id);
      case 'trips': return (row.destination_city || 'Ezamiyyət') + ' · #' + id;
      case 'vacancies': return row.title || ('Vakansiya #' + id);
      case 'candidates': return row.full_name || ('Namizəd #' + id);
      case 'trainings': return row.title || ('Təlim #' + id);
      case 'hr-orders': return row.order_number || ('Əmr #' + id);
      case 'timesheets': return (row.year || '') + '-' + pad(row.month || 0) + ' · #' + id;
      case 'payroll-runs': return (row.period_year || '') + '-' + pad(row.period_month || 0) + ' · #' + id;
      case 'users': return row.full_name || row.email || ('#' + id);
      default: return row.name || row.title || row.full_name || row.code || ('#' + id);
    }
  }

  function fieldByName(entity, name) {
    var fields = entity.fields || [];
    for (var i = 0; i < fields.length; i += 1) {
      if (fields[i].name === name) return fields[i];
    }
    return null;
  }

  function renderCell(entity, row, name) {
    var field = fieldByName(entity, name);
    var value = row[name];
    if (value === null || value === undefined || value === '') return '<span class="soft">—</span>';
    if (name === 'status' || name === 'stage' || name === 'decision' || name === 'day_type' || name === 'severity' || name === 'result' || name === 'direction') {
      return badge(value);
    }
    if (field && field.type === 'boolean') return value ? badge('Bəli', 'success') : badge('Xeyr', 'neutral');
    if (field && field.ref) return esc(refLabel(field.ref, value));
    if (field && field.type === 'date') return esc(fmtDate(value));
    if (field && field.type === 'datetime') return esc(fmtDateTime(value));
    if (field && field.type === 'time') return esc(String(value).slice(0, 5));
    if (field && field.type === 'json') {
      var jsonText = typeof value === 'string' ? value : JSON.stringify(value);
      return '<span class="mono truncate" title="' + esc(jsonText) + '">' + esc(jsonText) + '</span>';
    }
    if (field && (field.type === 'number' || field.type === 'integer')) {
      if (/(salary|amount|gross|net|fund|balance|advance|expense|cost|budget|allowance|limit|tax|dsmf|its|unemployment|price)/i.test(name)) {
        return esc(fmtMoney(value));
      }
      return esc(fmtNumber(value, field.type === 'integer' ? 0 : 2));
    }
    if (name === 'gender') return esc(humanize(value));
    if (name === 'pin_code' || name === 'voen' || name === 'ssn' || name === 'iban' || name === 'bank_iban') {
      return '<span class="mono">' + esc(value) + '</span>';
    }
    if (typeof value === 'object') {
      var text = JSON.stringify(value);
      return '<span class="mono truncate" title="' + esc(text) + '">' + esc(text) + '</span>';
    }
    var str = String(value);
    return esc(str.length > 90 ? str.slice(0, 87) + '...' : str);
  }

  function moduleTitle(code) {
    if (!state.meta) return '';
    for (var i = 0; i < state.meta.modules.length; i += 1) {
      if (state.meta.modules[i].code === code) return state.meta.modules[i].title;
    }
    return code;
  }

  function buildSidebar() {
    var nav = $('#sidebar-nav');
    if (!nav) return;
    var html = '';

    // If regular employee
    if (state.user && state.user.role === 'EMPLOYEE') {
      html += '<div class="nav-section-title">Şəxsi Kabinet</div><div class="nav-items">';
      html += navLink('#/s/ess', 'Şəxsi kabinetim', 'user');
      html += '<button type="button" class="nav-item nav-action-btn" data-act="ess-reference-pdf">' +
        '<span class="nav-icon">' + icon('download') + '</span><span>İş yerindən arayış (PDF)</span></button>';
      html += '<button type="button" class="nav-item nav-action-btn" data-act="ess-new-leave">' +
        '<span class="nav-icon">' + icon('palmtree') + '</span><span>Məzuniyyət sorğusu</span></button>';
      html += '</div>';
      nav.innerHTML = html;
      bindSidebarFilter();
      return;
    }

    var sections = [
      {
        title: 'Əsas Panel',
        items: [
          { type: 'screen', key: 'dashboard', label: 'İcmal', icon: 'dashboard' },
          { type: 'screen', key: 'approvals', label: 'Təsdiq mərkəzi', icon: 'check' },
          { type: 'screen', key: 'structure', label: 'Təşkilat strukturu', icon: 'tree' }
        ]
      },
      {
        title: 'Kadr və Ştat',
        items: [
          { type: 'entity', key: 'employees', label: 'İşçilər', icon: 'users' },
          { type: 'entity', key: 'hr-orders', label: 'Kadr əmrləri', icon: 'stamp' },
          { type: 'entity', key: 'contracts', label: 'Əmək müqavilələri', icon: 'contract' },
          { type: 'entity', key: 'staffing', label: 'Ştat cədvəli', icon: 'grid' },
          { type: 'screen', key: 'reports', label: 'Müddət xəbərdarlıqları', icon: 'alert' }
        ]
      },
      {
        title: 'İş Vaxtı və Məzuniyyət',
        items: [
          { type: 'screen', key: 'timesheets', label: 'Tabel (T-13)', icon: 'clock' },
          { type: 'screen', key: 'attendance', label: 'Turniket və Davamiyyət', icon: 'log-in' },
          { type: 'screen', key: 'work-schedules', label: 'İş qrafikləri (Növbəli)', icon: 'calendar-grid' },
          { type: 'screen', key: 'leave-requests', label: 'Məzuniyyət sorğuları', icon: 'palmtree' },
          { type: 'screen', key: 'sick-leaves', label: 'Xəstəlik vərəqələri', icon: 'health' },
          { type: 'screen', key: 'production-calendar', label: 'İstehsalat təqvimi', icon: 'calendar-grid' }
        ]
      },
      {
        title: 'Əməkhaqqı və Dövlət',
        items: [
          { type: 'screen', key: 'payroll-runs', label: 'Əməkhaqqı hesablaması', icon: 'wallet' },
          { type: 'entity', key: 'employee-pay-components', label: 'Fərdi kəsinti və əlavələr', icon: 'percent' },
          { type: 'screen', key: 'compliance', label: 'Dövlət hesabatları', icon: 'report' },
          { type: 'entity', key: 'emas-sync-logs', label: 'ƏMAS logları', icon: 'sync' }
        ]
      },
      {
        title: 'İşə Qəbul və Ezamiyyət',
        items: [
          { type: 'screen', key: 'recruitment', label: 'İşə qəbul (Kanban)', icon: 'user-search' },
          { type: 'screen', key: 'onboarding', label: 'Onboarding idarəsi', icon: 'checklist' },
          { type: 'entity', key: 'trips', label: 'Ezamiyyətlər', icon: 'plane' },
          { type: 'screen', key: 'mss', label: 'MSS · Komandam', icon: 'users' }
        ]
      },
      {
        title: 'Sistem və İnzibatçılıq',
        items: [
          { type: 'screen', key: 'ess', label: 'Şəxsi kabinet (ESS)', icon: 'user' },
          { type: 'screen', key: 'users', label: 'İstifadəçilər', icon: 'shield' },
          { type: 'screen', key: 'audit', label: 'Audit jurnalı', icon: 'list' },
          { type: 'screen', key: 'system-settings', label: 'Sistem və Demo İdarəsi', icon: 'settings' }
        ]
      }
    ];

    var usedKeys = {};

    sections.forEach(function (sec) {
      var visibleItems = sec.items.filter(function (it) {
        if (it.type === 'screen') {
          return hasScreen(it.key);
        } else {
          return !!state.entityMap[it.key];
        }
      });
      if (!visibleItems.length) return;
      html += '<div class="nav-section-title">' + esc(sec.title) + '</div><div class="nav-items">';
      visibleItems.forEach(function (it) {
        usedKeys[it.key] = true;
        var href = it.type === 'screen' ? '#/s/' + it.key : '#/entity/' + it.key;
        html += navLink(href, it.label, it.icon);
      });
      html += '</div>';
    });

    // Secondary / configuration entities
    var otherEntities = (state.meta.entities || []).filter(function (ent) {
      return !usedKeys[ent.key];
    });

    if (otherEntities.length && roleIn(['SUPERADMIN', 'HR_DIRECTOR', 'HR_SPECIALIST', 'ACCOUNTANT'])) {
      var isCurrentInOther = location.hash.startsWith('#/entity/') && otherEntities.some(function (e) {
        return location.hash === '#/entity/' + e.key;
      });
      html += '<details class="nav-group extra-tables-group"' + (isCurrentInOther ? ' open' : '') + '>' +
        '<summary><span class="nav-icon">' + icon('grid') + '</span>' +
        '<span>Bütün cədvəllər (Konfiqurasiya)</span><span class="chev">›</span></summary>' +
        '<div class="nav-items">';
      otherEntities.forEach(function (ent) {
        html += navLink('#/entity/' + ent.key, ent.label, ent.icon);
      });
      html += '</div></details>';
    }

    nav.innerHTML = html;
    bindSidebarFilter();
  }

  function bindSidebarFilter() {
    var input = $('#sidebar-filter');
    if (!input) return;
    input.oninput = function () {
      var q = (this.value || '').toLowerCase().trim();
      var nav = $('#sidebar-nav');
      if (!nav) return;
      var items = nav.querySelectorAll('.nav-item');
      var titles = nav.querySelectorAll('.nav-section-title');
      var extra = nav.querySelector('.extra-tables-group');

      if (!q) {
        items.forEach(function (el) { el.classList.remove('filter-hidden'); });
        titles.forEach(function (el) { el.classList.remove('filter-hidden'); });
        if (extra) {
          extra.classList.remove('filter-hidden');
          extra.removeAttribute('open');
        }
        return;
      }

      items.forEach(function (el) {
        var text = el.textContent.toLowerCase();
        var match = text.indexOf(q) >= 0;
        el.classList.toggle('filter-hidden', !match);
      });

      var sections = nav.querySelectorAll('.nav-items');
      sections.forEach(function (sec) {
        var visibleCount = sec.querySelectorAll('.nav-item:not(.filter-hidden)').length;
        var prev = sec.previousElementSibling;
        if (prev && prev.classList.contains('nav-section-title')) {
          prev.classList.toggle('filter-hidden', visibleCount === 0);
        }
      });

      if (extra) {
        var extraVisible = extra.querySelectorAll('.nav-item:not(.filter-hidden)').length > 0;
        extra.classList.toggle('filter-hidden', !extraVisible);
        if (extraVisible) extra.setAttribute('open', '');
      }
    };
  }

  function navLink(href, label, iconName) {
    var active = location.hash === href;
    return '<a class="nav-item' + (active ? ' active' : '') + '" href="' + href + '">' +
      '<span class="nav-icon">' + icon(iconName) + '</span><span>' + esc(label) + '</span></a>';
  }

  function roleIn(roles) {
    return !!(state.user && roles && roles.indexOf(state.user.role) >= 0);
  }

  function screenInfo(screenKey) {
    if (!state.meta) return null;
    for (var i = 0; i < state.meta.screens.length; i += 1) {
      if (state.meta.screens[i].key === screenKey) return state.meta.screens[i];
    }
    return null;
  }

  function hasScreen(screenKey) {
    return !!screenInfo(screenKey);
  }

  function canManage(screenKey) {
    var info = screenInfo(screenKey);
    return !!(info && roleIn(info.manage_roles));
  }

  function canWriteEntity(entity) {
    return !!(entity && roleIn(entity.permissions && entity.permissions.write_roles));
  }

  function canDeleteEntity(entity) {
    return !!(entity && roleIn(entity.permissions && entity.permissions.delete_roles));
  }

  function isHrWriter() {
    return roleIn(['SUPERADMIN', 'HR_DIRECTOR', 'HR_SPECIALIST']);
  }

  function isPayrollRole() {
    return roleIn(['SUPERADMIN', 'HR_DIRECTOR', 'ACCOUNTANT']);
  }

  function canPreviewSettlement() {
    return roleIn(['SUPERADMIN', 'HR_DIRECTOR', 'HR_SPECIALIST', 'ACCOUNTANT']);
  }

  function canApproveTrips() {
    return roleIn(['SUPERADMIN', 'HR_DIRECTOR', 'HR_SPECIALIST', 'DEPT_MANAGER']);
  }

  function localToday() {
    var now = new Date();
    return now.getFullYear() + '-' + pad(now.getMonth() + 1) + '-' + pad(now.getDate());
  }

  function defaultRouteForUser() {
    return state.user && state.user.role === 'EMPLOYEE' ? '#/s/ess' : '#/s/dashboard';
  }

  function showLogin() {
    $('#loading-screen').classList.add('hidden');
    $('#app-shell').classList.add('hidden');
    $('#login-screen').classList.remove('hidden');
    var email = $('#login-email');
    if (email) setTimeout(function () { email.focus(); }, 40);
  }

  function showApp() {
    $('#loading-screen').classList.add('hidden');
    $('#login-screen').classList.add('hidden');
    $('#app-shell').classList.remove('hidden');
    if (state.user) {
      $('#user-name').textContent = state.user.full_name || state.user.email || 'İstifadəçi';
      $('#user-role').textContent = humanize(state.user.role);
      $('#user-avatar').textContent = initials(state.user.full_name || state.user.email);
      var topbarActions = $('.topbar-quick-actions');
      if (topbarActions) {
        topbarActions.classList.toggle('hidden', !isHrWriter());
      }
      var userBox = $('.user-box');
      if (userBox) {
        userBox.setAttribute('data-act', 'user-profile-dialog');
        userBox.setAttribute('title', 'İstifadəçi Profili və Sazlamalar');
      }
    }
    $('#today-label').textContent = todayLabel();
    buildSidebar();
  }

  function clearSession() {
    state.token = null;
    state.user = null;
    state.meta = null;
    state.entityMap = {};
    state.entityRows = {};
    state.lookups = {};
    localStorage.removeItem('hr_token');
    localStorage.removeItem('hr_user');
  }

  function forceLogout(message) {
    clearSession();
    $('#app-shell').classList.add('hidden');
    showLogin();
    var error = $('#login-error');
    if (error) {
      error.textContent = message;
      error.classList.remove('hidden');
    }
  }

  function closeMobileSidebar() { document.body.classList.remove('sidebar-open'); }

  async function loadMeta() {
    state.meta = await api('/meta/entities');
    state.entityMap = {};
    state.meta.entities.forEach(function (entity) { state.entityMap[entity.key] = entity; });
  }

  async function login(event) {
    event.preventDefault();
    var button = $('#login-submit');
    var errorBox = $('#login-error');
    errorBox.classList.add('hidden');
    button.disabled = true;
    button.textContent = 'Daxil olunur...';
    try {
      var data = await api('/auth/login', {
        method: 'POST',
        form: { username: $('#login-email').value.trim(), password: $('#login-password').value }
      });
      state.token = data.access_token;
      state.user = data.user;
      localStorage.setItem('hr_token', state.token);
      localStorage.setItem('hr_user', JSON.stringify(state.user));
      await loadMeta();
      showApp();
      if (!location.hash || location.hash === '#') {
        location.hash = defaultRouteForUser();
      } else {
        route();
      }
    } catch (err) {
      errorBox.textContent = err.message;
      errorBox.classList.remove('hidden');
    } finally {
      button.disabled = false;
      button.textContent = 'Daxil ol';
    }
  }

  function logout() {
    clearSession();
    history.replaceState(null, '', location.pathname);
    $('#app-shell').classList.add('hidden');
    showLogin();
  }

  async function route() {
    if (!state.token) return;
    if (!state.meta) {
      try { await loadMeta(); } catch (err) { forceLogout(err.message); return; }
    }
    closeMobileSidebar();
    var raw = location.hash.replace(/^#\/?/, '');
    var parts = raw.split('/').filter(Boolean);
    var kind = parts[0] || 's';
    var key = parts[1];
    var extra = parts[2];
    if (state.user && state.user.role === 'EMPLOYEE' && !(kind === 's' && key === 'ess')) {
      if (location.hash !== '#/s/ess') { location.hash = '#/s/ess'; return; }
    }
    if (kind === 's' && key === 'payroll-run' && extra && !hasScreen('payroll-runs')) {
      location.hash = defaultRouteForUser();
      return;
    }
    if (kind === 's' && key === 'employee' && extra && !state.entityMap.employees) {
      location.hash = defaultRouteForUser();
      return;
    }
    var seq = ++state.renderSeq;
    try {
      if (kind === 'entity') {
        var entity = state.entityMap[key];
        if (!entity) {
          location.hash = defaultRouteForUser();
          return;
        }
        state.activeGroup = entity.module;
        buildSidebar();
        await renderEntity(key);
      } else {
        if (!key) key = 'dashboard';
        if (key === 'payroll-run' && extra) {
          state.activeGroup = 'M07';
          buildSidebar();
          await renderPayrollRun(extra);
        } else if (key === 'employee' && extra) {
          state.activeGroup = 'M02';
          buildSidebar();
          await renderEmployeeProfileScreen(extra);
        } else {
          var screen = screenInfo(key);
          if (!screen) {
            location.hash = defaultRouteForUser();
            return;
          }
          state.activeGroup = screen.module;
          buildSidebar();
          await renderScreen(key);
        }
      }
      if (seq === state.renderSeq) window.scrollTo(0, 0);
    } catch (err) {
      if (seq === state.renderSeq) {
        setHeader('Xəta', 'Səhifə yüklənmədi');
        $('#view').innerHTML = errorCard(err.message);
      }
    }
  }

  async function renderScreen(key) {
    switch (key) {
      case 'dashboard': return renderDashboard();
      case 'payroll-runs': return renderPayrollRuns();
      case 'leave-requests': return renderLeaveRequests();
      case 'sick-leaves': return renderSickLeaves();
      case 'timesheets': return renderTimesheets();
      case 'attendance': return renderAttendance();
      case 'work-schedules': return renderWorkSchedules();
      case 'production-calendar': return renderProductionCalendar();
      case 'structure': return renderStructure();
      case 'reports': return renderReports();
      case 'compliance': return renderCompliance();
      case 'recruitment': return renderRecruitment();
      case 'onboarding': return renderOnboarding();
      case 'approvals': return renderApprovals();
      case 'mss': return renderMss();
      case 'users': return renderUsers();
      case 'audit': return renderAudit();
      case 'system-settings': return renderSystemSettings();
      case 'ess': return renderEss();
      default:
        setHeader('Səhifə tapılmadı', '');
        $('#view').innerHTML = errorCard('Bu səhifə mövcud deyil');
    }
  }

  async function renderEntity(key) {
    var entity = state.entityMap[key];
    if (!entity) throw new Error('Siyahı tapılmadı');
    var saved = state.entityState[key] || { skip: 0, limit: 25, q: '' };
    state.entityState[key] = saved;
    setHeader(entity.label, moduleTitle(entity.module) + ' modulu');
    $('#view').innerHTML = loadingHTML(entity.label + ' yüklənir...');

    var listFields = entity.list_fields.map(function (name) { return fieldByName(entity, name); }).filter(Boolean);
    await ensureLookups(listFields.map(function (field) { return field.ref; }));

    var query = '?skip=' + saved.skip + '&limit=' + saved.limit;
    if (saved.q) query += '&q=' + encodeURIComponent(saved.q);
    var normalized = normalizeList(await api(entity.path + query));
    state.entityRows[key] = normalized.items;
    var canWrite = canWriteEntity(entity);
    var canDelete = canDeleteEntity(entity);

    var rows = normalized.items.map(function (row) {
      var cells = entity.list_fields.map(function (name) {
        return '<td>' + renderCell(entity, row, name) + '</td>';
      }).join('');
      var actions = '';
      if (key === 'employees') {
        actions += '<button class="btn sm ghost" type="button" data-act="employee-profile" data-id="' + row.id + '">Profil</button>';
        actions += '<button class="btn sm ghost" type="button" data-act="employee-reference-pdf" data-id="' + row.id + '">' + icon('download') + 'Arayış</button>';
        if (canPreviewSettlement()) actions += '<button class="btn sm ghost" type="button" data-act="settlement-preview" data-id="' + row.id + '">Haqq-hesab</button>';
      }
      if (key === 'hr-orders') {
        actions += '<button class="btn sm ghost" type="button" data-act="order-pdf" data-id="' + row.id + '">' + icon('download') + 'Əmr PDF</button>';
      }
      if (key === 'contracts') actions += '<button class="btn sm ghost" type="button" data-act="contract-detail" data-id="' + row.id + '">Detal</button>';
      if (key === 'service-contracts' && roleIn(['SUPERADMIN', 'HR_DIRECTOR', 'HR_SPECIALIST', 'ACCOUNTANT'])) {
        actions += '<button class="btn sm ghost" type="button" data-act="service-tax" data-id="' + row.id + '">Vergi hesabı</button>';
      }
      if (key === 'applications' && roleIn(['SUPERADMIN', 'HR_DIRECTOR', 'HR_SPECIALIST', 'DEPT_MANAGER'])) {
        actions += '<button class="btn sm ghost" type="button" data-act="application-manage" data-id="' + row.id + '">İdarə et</button>';
        actions += '<button class="btn sm ghost" type="button" data-act="offer-letter-pdf" data-id="' + row.id + '">' + icon('download') + 'Təklif</button>';
      }
      if (key === 'trips') {
        if (canApproveTrips() && row.status === 'PENDING') actions += '<button class="btn sm primary" type="button" data-act="trip-action" data-id="' + row.id + '" data-op="approve">Təsdiqlə</button>';
        if (roleIn(['SUPERADMIN', 'HR_DIRECTOR', 'HR_SPECIALIST', 'ACCOUNTANT']) && row.status === 'APPROVED') {
          actions += '<button class="btn sm primary" type="button" data-act="trip-action" data-id="' + row.id + '" data-op="complete">Tamamla</button>';
        }
      }
      if (key === 'emas-sync-logs' && canWrite && row.emas_status !== 'SYNCED') {
        actions += '<button class="btn sm primary" type="button" data-act="emas-sync" data-id="' + row.id + '">Sinxronlaşdır</button>';
      }
      if (canWrite) actions += '<button class="btn sm ghost" type="button" data-act="entity-edit" data-key="' + esc(key) + '" data-id="' + row.id + '">' + icon('edit') + '</button>';
      if (canDelete) actions += '<button class="btn sm danger" type="button" data-act="entity-delete" data-key="' + esc(key) + '" data-id="' + row.id + '">' + icon('trash') + '</button>';
      var rowAttr = canWrite ? ' class="clickable" data-act="entity-edit" data-key="' + esc(key) + '" data-id="' + row.id + '"' : '';
      return '<tr' + rowAttr + '>' + cells +
        '<td class="actions">' + actions + '</td></tr>';
    }).join('');

    var headerCells = entity.list_fields.map(function (name) {
      var field = fieldByName(entity, name);
      return '<th>' + esc(field ? field.label : name) + '</th>';
    }).join('');

    var from = normalized.total ? saved.skip + 1 : 0;
    var to = saved.skip + normalized.items.length;
    var hasPrev = saved.skip > 0;
    var hasNext = normalized.items.length >= saved.limit && (normalized.total ? to < normalized.total : true);
    var workflowActions = '';
    if (key === 'leave-balances' && canWrite) {
      workflowActions += '<button class="btn ghost" type="button" data-act="leave-balance-init">' + icon('calendar') + 'Balans hesabla</button>';
    }
    if (key === 'emas-sync-logs' && canWrite) {
      workflowActions += '<button class="btn ghost" type="button" data-act="emas-queue">' + icon('sync') + 'Növbəyə sal</button>';
    }

    $('#view').innerHTML =
      '<div class="page-toolbar">' +
      '<form class="search-box" id="entity-search-form"><input id="entity-q" type="search" placeholder="Axtar..." value="' + esc(saved.q) + '"><button class="btn ghost" type="submit">' + icon('search') + 'Axtar</button></form>' +
      '<div class="toolbar-actions">' +
      workflowActions +
      '<button class="btn ghost" type="button" data-act="entity-csv" data-key="' + esc(key) + '">' + icon('download') + 'CSV</button>' +
      '<button class="btn ghost" type="button" data-act="entity-refresh">' + icon('refresh') + 'Yenilə</button>' +
      (canWrite ? '<button class="btn primary" type="button" data-act="entity-create" data-key="' + esc(key) + '">' + icon('plus') + 'Yeni qeyd</button>' : '') +
      '</div></div>' +
      '<div class="card table-card">' +
      (normalized.items.length ? '<div class="table-wrap"><table class="data"><thead><tr>' + headerCells + '<th></th></tr></thead><tbody>' + rows + '</tbody></table></div>' : emptyState('Qeyd yoxdur', canWrite ? 'Yeni qeyd yaratmaq üçün sağ üstdəki düymədən istifadə edin.' : 'Bu bölmədə yalnız baxış icazəniz var.')) +
      '<div class="table-footer"><span>' + from + '–' + to + ' / ' + normalized.total + ' qeyd</span>' +
      '<div class="pager">' +
      '<button class="btn sm ghost" type="button" data-act="entity-page" data-key="' + esc(key) + '" data-dir="-1"' + (hasPrev ? '' : ' disabled') + '>Əvvəlki</button>' +
      '<button class="btn sm ghost" type="button" data-act="entity-page" data-key="' + esc(key) + '" data-dir="1"' + (hasNext ? '' : ' disabled') + '>Növbəti</button>' +
      '</div></div></div>';

    var form = $('#entity-search-form');
    if (form) {
      form.addEventListener('submit', function (event) {
        event.preventDefault();
        saved.q = $('#entity-q').value.trim();
        saved.skip = 0;
        renderEntity(key).catch(function (err) { toast(err.message, 'error'); });
      });
    }
  }

  function formFieldHTML(entity, field, value) {
    var id = 'f-' + field.name;
    var label = '<span>' + esc(field.label) + (field.required ? ' <span class="req">*</span>' : '') + '</span>';
    var classes = 'field';
    var wide = field.type === 'text' || field.type === 'json' || ['notes', 'description', 'address', 'requirements', 'reason', 'purpose', 'service_description'].indexOf(field.name) >= 0;
    if (wide) classes += ' span-2';
    var required = field.required ? ' required' : '';
    var maxLength = field.max_length ? ' maxlength="' + field.max_length + '"' : '';
    if (field.type === 'boolean') {
      return '<label class="field check' + (wide ? ' span-2' : '') + '"><input id="' + id + '" type="checkbox" name="' + esc(field.name) + '"' + (value ? ' checked' : '') + '>' +
        '<span>' + esc(field.label) + '</span></label>';
    }
    if (field.choices && field.choices.length) {
      var options = '<option value="">— seçin —</option>' + field.choices.map(function (choice) {
        return '<option value="' + esc(choice) + '"' + (equals(value, choice) ? ' selected' : '') + '>' + esc(humanize(choice)) + '</option>';
      }).join('');
      return '<label class="' + classes + '" for="' + id + '">' + label +
        '<select id="' + id + '" name="' + esc(field.name) + '"' + required + '>' + options + '</select></label>';
    }
    if (field.ref) {
      var list = state.lookups[field.ref] || [];
      var refOptions = '<option value="">— seçin —</option>' + list.map(function (row) {
        return '<option value="' + esc(row.id) + '"' + (equals(value, row.id) ? ' selected' : '') + '>' + esc(refLabel(field.ref, row.id)) + '</option>';
      }).join('');
      return '<label class="' + classes + '" for="' + id + '">' + label +
        '<select id="' + id + '" name="' + esc(field.name) + '"' + required + '>' + refOptions + '</select></label>';
    }
    if (field.type === 'json') {
      var jsonValue = value === null || value === undefined ? '' : (typeof value === 'string' ? value : JSON.stringify(value, null, 2));
      return '<label class="' + classes + '" for="' + id + '">' + label +
        '<textarea id="' + id + '" name="' + esc(field.name) + '" rows="6" class="mono"' + required + ' placeholder="{}">' + esc(jsonValue) + '</textarea></label>';
    }
    if (field.type === 'text') {
      return '<label class="' + classes + '" for="' + id + '">' + label +
        '<textarea id="' + id + '" name="' + esc(field.name) + '" rows="3"' + required + maxLength + '>' + esc(value || '') + '</textarea></label>';
    }
    var type = 'text';
    var step = '';
    var inputValue = value === null || value === undefined ? '' : value;
    if (field.type === 'date') { type = 'date'; inputValue = value ? String(value).slice(0, 10) : ''; }
    else if (field.type === 'datetime') {
      type = 'datetime-local';
      if (value) {
        var date = new Date(value);
        inputValue = isNaN(date.getTime()) ? String(value).slice(0, 16) : date.getFullYear() + '-' + pad(date.getMonth() + 1) + '-' + pad(date.getDate()) + 'T' + pad(date.getHours()) + ':' + pad(date.getMinutes());
      }
    }
    else if (field.type === 'time') { type = 'time'; inputValue = value ? String(value).slice(0, 5) : ''; }
    else if (field.type === 'number') { type = 'number'; step = ' step="any"'; }
    else if (field.type === 'integer') { type = 'number'; step = ' step="1"'; }
    return '<label class="' + classes + '" for="' + id + '">' + label +
      '<input id="' + id + '" name="' + esc(field.name) + '" type="' + type + '" value="' + esc(inputValue) + '"' + required + maxLength + step + '></label>';
  }

  async function openEntityForm(key, id) {
    var entity = state.entityMap[key];
    if (!entity) return;
    if (!canWriteEntity(entity)) { toast('Bu bölmədə dəyişiklik etmək icazəniz yoxdur', 'error'); return; }
    var editable = entity.fields.filter(function (field) { return !field.readonly; });
    await ensureLookups(editable.map(function (field) { return field.ref; }));
    var row = null;
    if (id) row = await api(entity.path + '/' + id);
    var fieldsHTML = editable.map(function (field) {
      var value = row ? row[field.name] : (field.default !== null && field.default !== undefined ? field.default : '');
      if (!row && field.name === 'organization_id' && !value && state.user && state.user.organization_id) value = state.user.organization_id;
      return formFieldHTML(entity, field, value);
    }).join('');
    openModal({
      title: row ? entity.label + ' — redaktə' : entity.label + ' — yeni qeyd',
      subtitle: moduleTitle(entity.module) + ' modulu',
      size: 'wide',
      body: '<form id="entity-form" class="form-grid" autocomplete="off">' + fieldsHTML + '</form>',
      footer: '<button class="btn ghost" type="button" data-act="modal-close">İmtina</button>' +
        '<button class="btn primary" type="submit" form="entity-form">' + icon('check') + 'Yadda saxla</button>'
    });
    $('#entity-form').addEventListener('submit', async function (event) {
      event.preventDefault();
      var form = event.target;
      var payload = {};
      try {
        editable.forEach(function (field) {
          var input = form.elements.namedItem(field.name);
          if (!input) return;
          if (field.type === 'boolean') { payload[field.name] = input.checked; return; }
          var value = input.value;
          if (value === '') { payload[field.name] = null; return; }
          if (field.type === 'number') value = Number(value);
          else if (field.type === 'integer') value = parseInt(value, 10);
          else if (field.type === 'json') {
            try { value = JSON.parse(value); } catch (err) { throw new Error(field.label + ': düzgün JSON deyil'); }
          }
          payload[field.name] = value;
        });
        await api(entity.path + (row ? '/' + row.id : ''), { method: row ? 'PATCH' : 'POST', body: payload });
        closeModal();
        toast(row ? 'Qeyd yeniləndi' : 'Qeyd yaradıldı', 'success');
        await renderEntity(key);
      } catch (err) { toast(err.message, 'error'); }
    });
  }

  function settlementHTML(data) {
    if (!data) return '<p class="hint">Hesablama nəticəsi yoxdur.</p>';
    return '<dl class="mini-dl">' +
      '<div><dt>İstifadə edilməmiş məzuniyyət</dt><dd>' + esc(fmtNumber(data.unused_vacation_days, 1)) + ' gün</dd></div>' +
      '<div><dt>Orta günlük əməkhaqqı</dt><dd>' + esc(fmtMoney(data.average_daily_wage)) + '</dd></div>' +
      '<div><dt>Məzuniyyət kompensasiyası</dt><dd>' + esc(fmtMoney(data.vacation_compensation)) + '</dd></div>' +
      '<div><dt>Orta aylıq əməkhaqqı</dt><dd>' + esc(fmtMoney(data.average_monthly_wage)) + '</dd></div>' +
      '<div><dt>İşdən çıxarma müavinəti</dt><dd>' + esc(fmtMoney(data.severance_pay)) + '</dd></div>' +
      '<div><dt><strong>Ümumi ödəniş</strong></dt><dd><strong>' + esc(fmtMoney(data.total_compensation)) + '</strong></dd></div>' +
      '</dl>';
  }

  async function openContractDetail(id) {
    await ensureLookups(['employees', 'staffing']);
    var results = await Promise.all([
      api('/contracts/' + id),
      api('/contracts/' + id + '/amendments').catch(function () { return []; }),
      api('/contracts/' + id + '/leave-balances').catch(function () { return []; })
    ]);
    var contract = results[0];
    var amendments = results[1] || [];
    var balances = results[2] || [];
    var canWrite = canWriteEntity(state.entityMap.contracts);
    var isActive = contract.status === 'ACTIVE';
    var employeeName = refLabel('employees', contract.employee_id);
    var staffingOptions = (state.lookups.staffing || []).map(function (row) {
      return '<option value="' + row.id + '"' + (equals(contract.staffing_id, row.id) ? ' selected' : '') + '>' + esc(refLabel('staffing', row.id)) + '</option>';
    }).join('');
    var amendmentRows = amendments.map(function (row) {
      return '<tr><td class="mono">' + esc(row.amendment_no) + '</td><td>' + esc(fmtDate(row.effective_date)) + '</td>' +
        '<td class="num">' + esc(fmtMoney(row.old_salary)) + '</td><td class="num">' + esc(fmtMoney(row.new_salary)) + '</td>' +
        '<td>' + esc(row.reason || '—') + '</td></tr>';
    }).join('');
    var balanceRows = balances.map(function (row) {
      return '<tr><td>' + esc(fmtDate(row.work_year_start)) + ' — ' + esc(fmtDate(row.work_year_end)) + '</td>' +
        '<td class="num">' + esc(fmtNumber(row.entitled_base_days, 1)) + '</td>' +
        '<td class="num">' + esc(fmtNumber(row.entitled_extra_days, 1)) + '</td>' +
        '<td class="num">' + esc(fmtNumber(row.used_days, 1)) + '</td>' +
        '<td class="num strong">' + esc(fmtNumber(row.remaining_days, 1)) + '</td></tr>';
    }).join('');
    var amendForm = canWrite && isActive
      ? '<section class="card card-pad span-2"><div class="card-head"><div><h2>Müqaviləyə düzəliş</h2><p class="muted">Əməkhaqqı, ştat və ya bitmə tarixi dəyişikliyi</p></div></div>' +
        '<form id="contract-amend-form" class="form-grid">' +
        '<label class="field"><span>Qüvvəyə minmə <span class="req">*</span></span><input type="date" name="effective_date" value="' + localToday() + '" required></label>' +
        '<label class="field"><span>Yeni əməkhaqqı</span><input type="number" step="0.01" name="new_salary" value="' + esc(contract.gross_salary) + '"></label>' +
        '<label class="field span-2"><span>Yeni ştat vahidi</span><select name="new_staffing_id"><option value="">— dəyişməz —</option>' + staffingOptions + '</select></label>' +
        '<label class="field"><span>Yeni bitmə tarixi</span><input type="date" name="new_end_date"></label>' +
        '<label class="field"><span>Səbəb</span><input type="text" name="reason"></label>' +
        '</form></section>'
      : '';
    var terminateForm = canWrite && isActive
      ? '<section class="card card-pad span-2"><div class="card-head"><div><h2>Müqavilənin xitamı</h2><p class="muted">Xitam əmri yaradılır və son haqq-hesab hesablanır</p></div></div>' +
        '<form id="contract-terminate-form" class="form-grid">' +
        '<label class="field"><span>Xitam tarixi <span class="req">*</span></span><input type="date" name="termination_date" value="' + localToday() + '" required></label>' +
        '<label class="field"><span>Əmək Məcəlləsi maddəsi</span><input type="text" name="labor_code_article" placeholder="məsələn 68"></label>' +
        '<label class="field span-2"><span>Səbəb</span><select name="reason"><option value="">— seçin —</option><option value="STAFF_REDUCTION">İşçi sayının ixtisarı</option><option value="LIQUIDATION">Müəssisənin ləğvi</option><option value="AGREEMENT">Tərəflərin razılığı</option><option value="OTHER">Digər</option></select></label>' +
        '</form></section>'
      : '';
    var terminationInfo = contract.termination_date
      ? '<div class="alert warning span-2">Müqavilə ' + esc(fmtDate(contract.termination_date)) + ' tarixində xitam edilib' + (contract.termination_article ? ' (maddə ' + esc(contract.termination_article) + ')' : '') + '.</div>'
      : '';
    openModal({
      title: 'Müqavilə ' + (contract.contract_number || '#' + contract.id),
      subtitle: employeeName,
      size: 'wide',
      body: '<div class="dash-grid">' +
        '<section class="card card-pad"><div class="card-head"><div><h2>Müqavilə məlumatı</h2></div></div>' +
        '<dl class="mini-dl"><div><dt>Status</dt><dd>' + badge(contract.status) + '</dd></div>' +
        '<div><dt>Növ</dt><dd>' + esc(humanize(contract.contract_type)) + '</dd></div>' +
        '<div><dt>İş növü</dt><dd>' + esc(humanize(contract.work_type)) + '</dd></div>' +
        '<div><dt>Brutto əməkhaqqı</dt><dd>' + esc(fmtMoney(contract.gross_salary)) + '</dd></div>' +
        '<div><dt>Ştat vahidi</dt><dd>' + esc(refLabel('staffing', contract.staffing_id)) + '</dd></div>' +
        '<div><dt>Başlama</dt><dd>' + esc(fmtDate(contract.start_date)) + '</dd></div>' +
        '<div><dt>Bitmə</dt><dd>' + esc(contract.end_date ? fmtDate(contract.end_date) : 'Müddətsiz') + '</dd></div>' +
        '<div><dt>İllik məzuniyyət</dt><dd>' + esc(contract.annual_leave_days || '—') + ' gün</dd></div></dl></section>' +
        '<section class="card card-pad"><div class="card-head"><div><h2>Məzuniyyət balansı</h2></div></div>' +
        (balances.length ? '<dl class="mini-dl">' + balances.slice(0, 4).map(function (row) {
          return '<div><dt>' + esc(fmtDate(row.work_year_start)) + ' — ' + esc(fmtDate(row.work_year_end)) + '</dt><dd>' + esc(fmtNumber(row.remaining_days, 1)) + ' gün</dd></div>';
        }).join('') + '</dl>' : '<p class="hint">Balans hələ hesablanmayıb.</p>') +
        (canWrite && isActive ? '<button class="btn ghost block mt-12" type="button" data-act="leave-balance-init" data-id="' + contract.id + '" data-detail="1">' + icon('calendar') + 'Balansı hesabla</button>' : '') +
        '</section></div>' +
        terminationInfo +
        '<div class="dash-grid">' +
        '<section class="card table-card span-2"><div class="card-head pad"><div><h2>Düzəlişlər</h2><p class="muted">' + amendments.length + ' qeyd</p></div></div>' +
        (amendments.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>№</th><th>Tarix</th><th class="num">Köhnə</th><th class="num">Yeni</th><th>Səbəb</th></tr></thead><tbody>' + amendmentRows + '</tbody></table></div>' : emptyState('Düzəliş yoxdur', '')) +
        '</section>' +
        '<section class="card table-card span-2"><div class="card-head pad"><div><h2>Məzuniyyət balansları</h2><p class="muted">' + balances.length + ' iş ili</p></div></div>' +
        (balances.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>İş ili</th><th class="num">Baza</th><th class="num">Əlavə</th><th class="num">İstifadə</th><th class="num">Qalıq</th></tr></thead><tbody>' + balanceRows + '</tbody></table></div>' : emptyState('Balans yoxdur', '')) +
        '</section></div>' +
        amendForm + terminateForm,
      footer: '<button class="btn ghost" type="button" data-act="modal-close">Bağla</button>' +
        (canWrite && isActive ? '<button class="btn danger" type="submit" form="contract-terminate-form">Xitam et</button>' : '') +
        (canWrite && isActive ? '<button class="btn primary" type="submit" form="contract-amend-form">' + icon('check') + 'Düzəlişi yaz</button>' : '')
    });
    var amendFormEl = $('#contract-amend-form');
    if (amendFormEl) {
      amendFormEl.addEventListener('submit', async function (event) {
        event.preventDefault();
        var form = event.target;
        try {
          var payload = {
            effective_date: form.elements.effective_date.value || null,
            new_salary: form.elements.new_salary.value ? Number(form.elements.new_salary.value) : null,
            new_staffing_id: form.elements.new_staffing_id.value ? Number(form.elements.new_staffing_id.value) : null,
            new_end_date: form.elements.new_end_date.value || null,
            reason: form.elements.reason.value || null
          };
          await api('/contracts/' + contract.id + '/amendments', { method: 'POST', body: payload });
          toast('Müqavilə düzəlişi yaradıldı', 'success');
          await renderEntity('contracts');
          await openContractDetail(contract.id);
        } catch (err) { toast(err.message, 'error'); }
      });
    }
    var terminateFormEl = $('#contract-terminate-form');
    if (terminateFormEl) {
      terminateFormEl.addEventListener('submit', async function (event) {
        event.preventDefault();
        var form = event.target;
        if (!window.confirm('Müqavilə xitam edilsin? Bu əməliyyat geri qaytarılmır.')) return;
        try {
          var result = await api('/contracts/' + contract.id + '/terminate', {
            method: 'POST',
            body: {
              termination_date: form.elements.termination_date.value,
              labor_code_article: form.elements.labor_code_article.value || null,
              reason: form.elements.reason.value || null
            }
          });
          toast('Müqavilə xitam edildi', 'success');
          await renderEntity('contracts');
          openModal({
            title: 'Xitam nəticəsi',
            subtitle: employeeName,
            body: '<div class="alert info">Xitam əmri yaradıldı. Aşağıdakı hesablama son haqq-hesab üçün ilkin məlumatdır.</div>' +
              '<div class="card card-pad mt-12">' + settlementHTML(result.settlement) + '</div>',
            footer: '<button class="btn primary" type="button" data-act="modal-close">Bağla</button>'
          });
        } catch (err) { toast(err.message, 'error'); }
      });
    }
  }

  async function openServiceTax(contractId) {
    var results = await Promise.all([
      api('/service-contracts/' + contractId),
      api('/service-contracts/' + contractId + '/tax-preview')
    ]);
    var contract = results[0];
    var preview = results[1];
    openModal({
      title: 'Xidməti müqavilə vergi hesabı',
      subtitle: contract.contract_number || contract.contractor_name,
      body: '<div class="alert info">Hesablama müqavilədə göstərilən tutulma faizləri əsasında aparılır.</div>' +
        '<div class="card card-pad mt-12"><dl class="mini-dl">' +
        '<div><dt>Podratçı</dt><dd>' + esc(contract.contractor_name || '—') + '</dd></div>' +
        '<div><dt>Müqavilə məbləği</dt><dd>' + esc(fmtMoney(preview.amount)) + '</dd></div>' +
        '<div><dt>Ödəmə mənbəyində vergi</dt><dd>' + esc(fmtMoney(preview.withholding_tax)) + '</dd></div>' +
        '<div><dt>DSMF</dt><dd>' + esc(fmtMoney(preview.dsmf)) + '</dd></div>' +
        '<div><dt><strong>Podratçıya net</strong></dt><dd><strong>' + esc(fmtMoney(preview.net_to_contractor)) + '</strong></dd></div>' +
        '</dl></div>',
      footer: '<button class="btn primary" type="button" data-act="modal-close">Bağla</button>'
    });
  }

  async function refreshApplicationsView() {
    if (location.hash === '#/s/recruitment') await renderRecruitment();
    else await renderEntity('applications');
  }

  async function openApplicationManage(id) {
    await ensureLookups(['vacancies', 'candidates', 'staffing']);
    var application = await api('/applications/' + id);
    var vacancy = findLookup('vacancies', application.vacancy_id);
    var candidate = findLookup('candidates', application.candidate_id);
    var candidateName = candidate ? candidate.full_name : ('Namizəd #' + application.candidate_id);
    var stageOptions = ['NEW', 'CALL', 'INTERVIEW', 'TASK', 'OFFER', 'HIRED', 'REJECTED'].map(function (stage) {
      return '<option value="' + stage + '"' + (application.stage === stage ? ' selected' : '') + '>' + esc(humanize(stage)) + '</option>';
    }).join('');
    var staffingOptions = (state.lookups.staffing || []).map(function (row) {
      var selected = vacancy && equals(vacancy.staffing_id, row.id);
      return '<option value="' + row.id + '"' + (selected ? ' selected' : '') + '>' + esc(refLabel('staffing', row.id)) + '</option>';
    }).join('');
    var suggestedSalary = vacancy ? (vacancy.salary_max || vacancy.salary_min || '') : '';
    var hireSection = '';
    if (isHrWriter() && application.stage !== 'HIRED') {
      hireSection = '<section class="card card-pad span-2"><div class="card-head"><div><h2>İşə qəbul</h2><p class="muted">İşçi, aktiv müqavilə və onboarding checklist yaradılacaq</p></div></div>' +
        '<form id="application-hire-form" class="form-grid">' +
        '<label class="field"><span>FİN <span class="req">*</span></span><input type="text" name="pin_code" maxlength="7" required placeholder="7 simvol"></label>' +
        '<label class="field"><span>Ştat vahidi <span class="req">*</span></span><select name="staffing_id" required><option value="">— seçin —</option>' + staffingOptions + '</select></label>' +
        '<label class="field"><span>Müqavilə №</span><input type="text" name="contract_number" placeholder="Avtomatik"></label>' +
        '<label class="field"><span>Müqavilə növü</span><select name="contract_type"><option value="INDEFINITE">Müddətsiz</option><option value="FIXED_TERM">Müddətli</option></select></label>' +
        '<label class="field"><span>Başlama tarixi <span class="req">*</span></span><input type="date" name="start_date" value="' + localToday() + '" required></label>' +
        '<label class="field"><span>Bitmə tarixi</span><input type="date" name="end_date"></label>' +
        '<label class="field"><span>Brutto əməkhaqqı <span class="req">*</span></span><input type="number" step="0.01" name="gross_salary" value="' + esc(suggestedSalary) + '" required></label>' +
        '<div class="alert info span-2">Onboarding üçün 5 standart tapşırıq avtomatik yaradılacaq.</div>' +
        '</form></section>';
    }
    openModal({
      title: 'Müraciət idarəsi',
      subtitle: candidateName + (vacancy ? ' · ' + vacancy.title : ''),
      size: 'wide',
      body: '<div class="dash-grid">' +
        '<section class="card card-pad"><div class="card-head"><div><h2>Namizəd</h2></div></div>' +
        '<dl class="mini-dl"><div><dt>Ad Soyad</dt><dd>' + esc(candidateName) + '</dd></div>' +
        '<div><dt>Telefon</dt><dd>' + esc(candidate && candidate.phone ? candidate.phone : '—') + '</dd></div>' +
        '<div><dt>E-poçt</dt><dd>' + esc(candidate && candidate.email ? candidate.email : '—') + '</dd></div>' +
        '<div><dt>Təcrübə</dt><dd>' + esc(candidate && candidate.experience_years !== undefined ? candidate.experience_years + ' il' : '—') + '</dd></div></dl></section>' +
        '<section class="card card-pad"><div class="card-head"><div><h2>Vakansiya</h2></div></div>' +
        '<dl class="mini-dl"><div><dt>Vəzifə</dt><dd>' + esc(vacancy ? vacancy.title : '#' + application.vacancy_id) + '</dd></div>' +
        '<div><dt>Status</dt><dd>' + badge(vacancy ? vacancy.status : 'CLOSED') + '</dd></div>' +
        '<div><dt>Müraciət mərhələsi</dt><dd>' + badge(application.stage) + '</dd></div>' +
        (application.hired_employee_id ? '<div><dt>İşçi</dt><dd><a class="strong-link" href="#/s/employee/' + application.hired_employee_id + '" data-act="modal-close"># ' + application.hired_employee_id + ' profil</a></dd></div>' : '') +
        '</dl></section>' +
        '<section class="card card-pad span-2"><div class="card-head"><div><h2>Mərhələ və qiymətləndirmə</h2></div></div>' +
        '<form id="application-stage-form" class="form-grid">' +
        '<label class="field"><span>Mərhələ</span><select name="stage">' + stageOptions + '</select></label>' +
        '<label class="field"><span>Bal (0–100)</span><input type="number" name="score" min="0" max="100" step="1" value="' + esc(application.score === null || application.score === undefined ? '' : application.score) + '"></label>' +
        '<label class="field span-2"><span>Qeydlər</span><textarea name="notes" rows="2">' + esc(application.notes || '') + '</textarea></label>' +
        '</form></section></div>' + hireSection,
      footer: '<button class="btn ghost" type="button" data-act="modal-close">Bağla</button>' +
        '<button class="btn ghost" type="button" data-act="offer-letter-pdf" data-id="' + id + '">' + icon('download') + 'İş təklifi (PDF)</button>' +
        '<button class="btn ghost" type="submit" form="application-stage-form">' + icon('check') + 'Mərhələni saxla</button>' +
        (hireSection ? '<button class="btn primary" type="submit" form="application-hire-form">' + icon('user-search') + 'İşə qəbul et</button>' : '')
    });
    $('#application-stage-form').addEventListener('submit', async function (event) {
      event.preventDefault();
      var form = event.target;
      try {
        await api('/applications/' + id + '/stage', {
          method: 'PATCH',
          body: {
            stage: form.elements.stage.value,
            score: form.elements.score.value ? Number(form.elements.score.value) : null,
            notes: form.elements.notes.value || null
          }
        });
        toast('Müraciət yeniləndi', 'success');
        await refreshApplicationsView();
        await openApplicationManage(id);
      } catch (err) { toast(err.message, 'error'); }
    });
    var hireForm = $('#application-hire-form');
    if (hireForm) {
      hireForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        var form = event.target;
        var button = $('button[form="application-hire-form"]');
        if (button) button.disabled = true;
        try {
          var result = await api('/applications/' + id + '/hire', {
            method: 'POST',
            body: {
              pin_code: form.elements.pin_code.value.trim(),
              staffing_id: Number(form.elements.staffing_id.value),
              contract_number: form.elements.contract_number.value || null,
              contract_type: form.elements.contract_type.value,
              start_date: form.elements.start_date.value,
              end_date: form.elements.end_date.value || null,
              gross_salary: Number(form.elements.gross_salary.value)
            }
          });
          closeModal();
          toast('İşçi yaradıldı: ' + [result.employee.last_name, result.employee.first_name].filter(Boolean).join(' '), 'success');
          await refreshApplicationsView();
        } catch (err) {
          toast(err.message, 'error');
          if (button) button.disabled = false;
        }
      });
    }
  }

  async function tripAction(id, operation) {
    var labels = { approve: 'Ezamiyyət təsdiqlənsin?', complete: 'Ezamiyyət tamamlanmış kimi qeyd edilsin?' };
    if (!window.confirm(labels[operation] || 'Əməliyyat icra edilsin?')) return;
    try {
      await api('/trips/' + id + '/' + operation, { method: 'POST' });
      toast('Ezamiyyət yeniləndi', 'success');
      await renderEntity('trips');
    } catch (err) { toast(err.message, 'error'); }
  }

  async function openLeaveBalanceInit(contractId, fromDetail) {
    await ensureLookups(['contracts']);
    var contracts = state.lookups.contracts || [];
    if (!contracts.length) { toast('Aktiv müqavilə tapılmadı', 'error'); return; }
    var options = contracts.map(function (contract) {
      return '<option value="' + contract.id + '"' + (contractId && equals(contractId, contract.id) ? ' selected' : (contractId ? '' : (contract.status === 'ACTIVE' ? ' selected' : ''))) + '>' +
        esc(refLabel('contracts', contract.id) + ' · ' + (contract.status || '')) + '</option>';
    }).join('');
    openModal({
      title: 'Məzuniyyət balansını hesabla',
      subtitle: 'Müqavilə üzrə iş illəri üçün balans yaradılır',
      body: '<form id="leave-balance-init-form" class="form-grid">' +
        '<label class="field span-2"><span>Müqavilə <span class="req">*</span></span><select name="contract_id" required>' + options + '</select></label>' +
        '<label class="field span-2"><span>Hesablama tarixi</span><input type="date" name="as_of" value="' + localToday() + '"></label>' +
        '</form>',
      footer: '<button class="btn ghost" type="button" data-act="modal-close">İmtina</button>' +
        '<button class="btn primary" type="submit" form="leave-balance-init-form">' + icon('calendar') + 'Hesabla</button>'
    });
    $('#leave-balance-init-form').addEventListener('submit', async function (event) {
      event.preventDefault();
      var form = event.target;
      var selectedContract = Number(form.elements.contract_id.value);
      try {
        var result = await api('/leave-balances/initialize', {
          method: 'POST',
          body: { contract_id: selectedContract, as_of: form.elements.as_of.value || null }
        });
        closeModal();
        toast((result.length || 0) + ' balans sətri hesablandı', 'success');
        if (fromDetail) await openContractDetail(selectedContract);
        else await renderEntity('leave-balances');
      } catch (err) { toast(err.message, 'error'); }
    });
  }

  async function openEmasQueueForm() {
    openModal({
      title: 'ƏMAS növbəsinə sal',
      subtitle: 'Yeni sinxronizasiya tapşırığı',
      body: '<form id="emas-queue-form" class="form-grid">' +
        '<label class="field"><span>Obyekt növü</span><select name="entity_type"><option value="EMPLOYEE">İşçi</option><option value="CONTRACT">Müqavilə</option><option value="LEAVE_REQUEST">Məzuniyyət sorğusu</option><option value="BUSINESS_TRIP">Ezamiyyət</option><option value="ORDER">Kadr əmri</option></select></label>' +
        '<label class="field"><span>Obyekt ID <span class="req">*</span></span><input type="number" name="entity_id" min="1" step="1" required></label>' +
        '<label class="field span-2"><span>Əməliyyat</span><select name="action_type"><option value="SYNC">Sinxronlaşdırma</option><option value="CREATE">Yaratma</option><option value="UPDATE">Dəyişiklik</option><option value="DELETE">Silmə</option></select></label>' +
        '</form>',
      footer: '<button class="btn ghost" type="button" data-act="modal-close">İmtina</button>' +
        '<button class="btn primary" type="submit" form="emas-queue-form">' + icon('sync') + 'Növbəyə sal</button>'
    });
    $('#emas-queue-form').addEventListener('submit', async function (event) {
      event.preventDefault();
      var form = event.target;
      try {
        await api('/compliance/emas/queue', {
          method: 'POST',
          body: {
            entity_type: form.elements.entity_type.value,
            entity_id: Number(form.elements.entity_id.value),
            action_type: form.elements.action_type.value
          }
        });
        closeModal();
        toast('Sinxronizasiya növbəyə salındı', 'success');
        await renderEntity('emas-sync-logs');
      } catch (err) { toast(err.message, 'error'); }
    });
  }

  async function syncEmasLog(id) {
    if (!window.confirm('Bu log sinxronlaşdırılmış kimi qeyd edilsin?')) return;
    try {
      await api('/compliance/emas/' + id + '/mark-synced', { method: 'POST', body: {} });
      toast('Log sinxronlaşdırıldı', 'success');
      await renderEntity('emas-sync-logs');
    } catch (err) { toast(err.message, 'error'); }
  }

  async function openFinalSettlement(employeeId) {
    await ensureLookups(['employees']);
    openModal({
      title: 'Son haqq-hesab',
      subtitle: refLabel('employees', employeeId),
      body: '<div class="alert info">Bu ilkin hesablamadır. Müqavilə xitam edildikdə son məbləğ yenidən hesablanır.</div>' +
        '<form id="settlement-preview-form" class="form-grid mt-12">' +
        '<label class="field"><span>Xitam tarixi <span class="req">*</span></span><input type="date" name="termination_date" value="' + localToday() + '" required></label>' +
        '<label class="field"><span>Səbəb</span><select name="reason"><option value="">— seçin —</option><option value="STAFF_REDUCTION">İşçi sayının ixtisarı</option><option value="LIQUIDATION">Müəssisənin ləğvi</option><option value="AGREEMENT">Tərəflərin razılığı</option><option value="OTHER">Digər</option></select></label>' +
        '</form>',
      footer: '<button class="btn ghost" type="button" data-act="modal-close">İmtina</button>' +
        '<button class="btn primary" type="submit" form="settlement-preview-form">' + icon('wallet') + 'Hesabla</button>'
    });
    $('#settlement-preview-form').addEventListener('submit', async function (event) {
      event.preventDefault();
      var form = event.target;
      try {
        var query = '?termination_date=' + encodeURIComponent(form.elements.termination_date.value);
        if (form.elements.reason.value) query += '&reason=' + encodeURIComponent(form.elements.reason.value);
        var result = await api('/employees/' + employeeId + '/final-settlement-preview' + query);
        openModal({
          title: 'Son haqq-hesab',
          subtitle: refLabel('employees', employeeId),
          body: '<div class="alert info">Xitam tarixi: ' + esc(fmtDate(result.termination_date)) + '</div>' +
            '<div class="card card-pad mt-12">' + settlementHTML(result) + '</div>',
          footer: '<button class="btn primary" type="button" data-act="modal-close">Bağla</button>'
        });
      } catch (err) { toast(err.message, 'error'); }
    });
  }

  function csvCell(value) {
    var text = String(value === null || value === undefined ? '' : value).replace(/"/g, '""');
    return '"' + text + '"';
  }

  function exportEntityCSV(key) {
    var entity = state.entityMap[key];
    var rows = state.entityRows[key] || [];
    if (!entity || !rows.length) { toast('CSV üçün məlumat yoxdur', 'error'); return; }
    var headers = entity.list_fields.map(function (name) {
      var field = fieldByName(entity, name);
      return field ? field.label : name;
    });
    var lines = [headers.map(csvCell).join(';')];
    rows.forEach(function (row) {
      lines.push(entity.list_fields.map(function (name) {
        var field = fieldByName(entity, name);
        var value = row[name];
        if (field && field.ref) return refLabel(field.ref, value);
        if (value === null || value === undefined) return '';
        if (typeof value === 'object') return JSON.stringify(value);
        return String(value);
      }).map(csvCell).join(';'));
    });
    var blob = new Blob(['\uFEFF' + lines.join('\r\n')], { type: 'text/csv;charset=utf-8' });
    var url = URL.createObjectURL(blob);
    var link = document.createElement('a');
    link.href = url;
    link.download = key + '.csv';
    link.click();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  function quickLinksHTML() {
    var items = [
      { entity: 'employees', icon: 'users', label: 'İşçilər (Kadrlar)' },
      { entity: 'hr-orders', icon: 'stamp', label: 'Kadr əmrləri (PDF)' },
      { screen: 'payroll-runs', icon: 'wallet', label: 'Əməkhaqqı hesabla' },
      { screen: 'timesheets', icon: 'clock', label: 'Tabel (T-13)' },
      { screen: 'leave-requests', icon: 'palmtree', label: 'Məzuniyyətlər' },
      { screen: 'compliance', icon: 'report', label: 'Dövlət hesabatları' },
      { screen: 'recruitment', icon: 'user-search', label: 'İşə qəbul (Kanban)' },
      { screen: 'approvals', icon: 'check', label: 'Təsdiqlər' }
    ];
    return items.filter(function (item) {
      return item.screen ? hasScreen(item.screen) : !!state.entityMap[item.entity];
    }).map(function (item) {
      var href = item.screen ? '#/s/' + item.screen : '#/entity/' + item.entity;
      return '<a class="quick-link" href="' + href + '"><span class="q-icon">' + icon(item.icon) + '</span><span>' + esc(item.label) + '</span></a>';
    }).join('');
  }

  async function renderDashboard() {
    setHeader('İcmal', 'Əməkhaqqı və kadr göstəriciləri');
    $('#view').innerHTML = loadingHTML('İcmal hazırlanır...');
    var results = await Promise.all([
      api('/analytics/dashboard'),
      api('/analytics/payroll-trend?months=12').catch(function () { return []; })
    ]);
    var dash = results[0];
    var trend = results[1] || [];
    var latest = dash.latest_payroll;
    var userName = (state.user && state.user.full_name) || (state.user && state.user.email) || 'İstifadəçi';

    var pendingItems = [];
    if (dash.pending_leave_requests > 0) {
      pendingItems.push('<a href="#/s/leave-requests" class="alert-chip amber">' + icon('palmtree') + ' ' + dash.pending_leave_requests + ' məzuniyyət təsdiq gözləyir</a>');
    }
    if (dash.expiring_documents_60d > 0) {
      pendingItems.push('<a href="#/s/reports" class="alert-chip rose">' + icon('file') + ' ' + dash.expiring_documents_60d + ' sənədin müddəti bitir</a>');
    }
    if (dash.expiring_permits_60d > 0) {
      pendingItems.push('<a href="#/s/reports" class="alert-chip slate">' + icon('globe') + ' ' + dash.expiring_permits_60d + ' miqrasiya icazəsi bitir</a>');
    }

    var alertBannerHTML = pendingItems.length ? (
      '<div class="action-alert-banner">' +
      '<span class="alert-icon">🔔</span>' +
      '<div><strong>Diqqət tələb edən məsələlər:</strong> ' + pendingItems.join(' ') + '</div>' +
      '</div>'
    ) : '';

    var welcomeBannerHTML =
      '<div class="welcome-banner card">' +
      '<div class="welcome-copy">' +
      '<span class="welcome-badge">HR & Payroll İdarəetmə Paneli</span>' +
      '<h2>Xoş gəlmisiniz, ' + esc(userName) + ' 👋</h2>' +
      '<p class="muted">Təşkilat üzrə kadr, iş vaxtı, əməkhaqqı və qanunvericilik uyğunluğu göstəriciləri bir baxışda.</p>' +
      '</div>' +
      '<div class="welcome-actions">' +
      (isHrWriter() ? '<button class="btn primary" type="button" data-act="quick-new-order">' + icon('stamp') + 'Yeni Əmr</button>' : '') +
      (isHrWriter() ? '<button class="btn ghost" type="button" data-act="quick-new-employee">' + icon('users') + 'Yeni İşçi</button>' : '') +
      (hasScreen('leave-requests') ? '<a class="btn ghost" href="#/s/leave-requests">' + icon('palmtree') + 'Məzuniyyətlər</a>' : '') +
      (hasScreen('payroll-runs') ? '<a class="btn ghost" href="#/s/payroll-runs">' + icon('wallet') + 'Əməkhaqqı</a>' : '') +
      '</div></div>';

    var kpis = [
      { label: 'Aktiv işçilər', value: fmtNumber(dash.headcount, 0), hint: 'cari işçi sayı', icon: 'users', tone: 'teal', href: state.entityMap.employees ? '#/entity/employees' : null },
      { label: 'Son əməkhaqqı fondu', value: latest ? fmtMoney(latest.total_net) : '—', hint: latest ? latest.period + ' · net' : 'hesablama yoxdur', icon: 'wallet', tone: 'blue', href: hasScreen('payroll-runs') ? '#/s/payroll-runs' : null },
      { label: 'Gözləyən məzuniyyət', value: fmtNumber(dash.pending_leave_requests, 0), hint: 'təsdiq gözləyir', icon: 'hourglass', tone: 'amber', href: hasScreen('leave-requests') ? '#/s/leave-requests' : null },
      { label: 'Kadr dövriyyəsi', value: fmtNumber(dash.annual_turnover_pct, 1) + '%', hint: 'son 12 ay', icon: 'chart', tone: 'violet', href: hasScreen('reports') ? '#/s/reports' : null },
      { label: 'Bitən sənədlər', value: fmtNumber(dash.expiring_documents_60d, 0), hint: '60 gün ərzində', icon: 'file', tone: 'rose', href: hasScreen('reports') ? '#/s/reports' : null },
      { label: 'Bitən icazələr', value: fmtNumber(dash.expiring_permits_60d, 0), hint: 'miqrasiya · 60 gün', icon: 'globe', tone: 'slate', href: hasScreen('reports') ? '#/s/reports' : null }
    ];

    var kpiHTML = kpis.map(function (kpi) {
      var content = '<span class="stat-icon">' + icon(kpi.icon) + '</span>' +
        '<span class="stat-copy"><span class="stat-label">' + esc(kpi.label) + '</span>' +
        '<strong class="stat-value">' + esc(kpi.value) + '</strong>' +
        '<span class="stat-hint">' + esc(kpi.hint) + '</span></span>';
      return kpi.href
        ? '<a class="stat-card tone-' + kpi.tone + '" href="' + kpi.href + '">' + content + '</a>'
        : '<div class="stat-card tone-' + kpi.tone + '">' + content + '</div>';
    }).join('');

    var trendMax = 1;
    trend.forEach(function (point) { trendMax = Math.max(trendMax, Number(point.net) || 0, Number(point.gross) || 0); });
    var trendBars = trend.length ? trend.map(function (point) {
      var grossHeight = Math.max(4, Math.round(((Number(point.gross) || 0) / trendMax) * 100));
      var netHeight = Math.max(4, Math.round(((Number(point.net) || 0) / trendMax) * 100));
      return '<div class="bar-pair" title="' + esc(point.period + ' · bruto ' + fmtMoney(point.gross) + ' · net ' + fmtMoney(point.net)) + '">' +
        '<div class="bars"><span class="bar gross" style="height:' + grossHeight + '%"></span><span class="bar net" style="height:' + netHeight + '%"></span></div>' +
        '<span class="bar-label">' + esc(String(point.period || '').slice(2)) + '</span></div>';
    }).join('') : emptyState('Trend yoxdur', 'Hesablanmış əməkhaqqı dövrləri yoxdur.');

    var gender = dash.gender_distribution || {};
    var female = Number(gender.F || 0);
    var male = Number(gender.M || 0);
    var other = Object.keys(gender).reduce(function (sum, key) {
      return sum + (key !== 'F' && key !== 'M' ? Number(gender[key]) || 0 : 0);
    }, 0);
    var genderTotal = female + male + other;
    var femalePct = genderTotal ? Math.round((female / genderTotal) * 100) : 0;
    var malePct = genderTotal ? Math.round((male / genderTotal) * 100) : 0;
    var donut = genderTotal
      ? 'conic-gradient(#0f9d8f 0 ' + femalePct + '%, #2f6fed ' + femalePct + '% ' + (femalePct + malePct) + '%, #cbd5e1 ' + (femalePct + malePct) + '% 100%)'
      : 'conic-gradient(#e2e8f0 0 100%)';

    var departments = dash.departments || [];
    var deptMax = 1;
    departments.forEach(function (dept) { deptMax = Math.max(deptMax, Number(dept.headcount) || 0); });
    var deptHTML = departments.length ? departments.map(function (dept) {
      var width = Math.max(3, Math.round(((Number(dept.headcount) || 0) / deptMax) * 100));
      return '<div class="dept-row"><div class="dept-line"><span>' + esc(dept.name) + '</span><strong>' + esc(dept.headcount) + '</strong></div>' +
        '<div class="progress"><span style="width:' + width + '%"></span></div></div>';
    }).join('') : '<p class="hint">Departament məlumatı yoxdur</p>';

    var ages = dash.age_distribution || {};
    var ageMax = 1;
    Object.keys(ages).forEach(function (key) { ageMax = Math.max(ageMax, Number(ages[key]) || 0); });
    var ageHTML = Object.keys(ages).map(function (key) {
      return '<div class="dept-row"><div class="dept-line"><span>' + esc(key) + '</span><strong>' + esc(ages[key]) + '</strong></div>' +
        '<div class="progress blue"><span style="width:' + Math.max(2, Math.round(((Number(ages[key]) || 0) / ageMax) * 100)) + '%"></span></div></div>';
    }).join('') || '<p class="hint">Yaş məlumatı yoxdur</p>';

    $('#view').innerHTML =
      welcomeBannerHTML +
      alertBannerHTML +
      '<div class="stat-grid">' + kpiHTML + '</div>' +
      '<section class="card card-pad" style="margin-bottom: 20px;"><div class="card-head" style="border:none; padding: 0 0 14px 0;"><div><h2>Sürətli əməliyyatlar</h2><p class="muted">Ən çox istifadə edilən əsas modullar</p></div></div>' +
      '<div class="quick-grid">' + quickLinksHTML() + '</div></section>' +
      '<div class="dash-grid">' +
      '<section class="card card-pad span-2"><div class="card-head"><div><h2>Əməkhaqqı fondu dinamikası</h2><p class="muted">Aylıq bruto və net məbləğlər</p></div>' +
      '<div class="legend"><span><i class="dot gross"></i>Bruto</span><span><i class="dot net"></i>Net</span></div></div>' +
      '<div class="bar-chart">' + trendBars + '</div></section>' +
      '<section class="card card-pad"><div class="card-head"><div><h2>Son hesablama</h2><p class="muted">Payroll statusu</p></div></div>' +
      (latest ? '<div class="latest-payroll"><div class="latest-period">' + esc(latest.period) + '</div>' + badge(latest.status) +
        '<dl class="mini-dl"><div><dt>Bruto</dt><dd>' + esc(fmtMoney(latest.total_gross)) + '</dd></div>' +
        '<div><dt>Net</dt><dd>' + esc(fmtMoney(latest.total_net)) + '</dd></div></dl>' +
        '<a class="btn ghost block" href="#/s/payroll-runs">Hesablamalara keç ' + icon('arrow-left') + '</a></div>'
        : '<p class="hint">Hələ hesablama aparılmayıb.</p>') + '</section>' +
      '<section class="card card-pad"><div class="card-head"><div><h2>Cins bölgüsü</h2><p class="muted">Aktiv işçilər</p></div></div>' +
      '<div class="donut-wrap"><div class="donut" style="background:' + donut + '"><span class="donut-center"><strong>' + esc(genderTotal) + '</strong><small>işçi</small></span></div>' +
      '<div class="donut-legend"><span><i class="dot female"></i>Qadın · ' + esc(female) + '</span><span><i class="dot male"></i>Kişi · ' + esc(male) + '</span>' +
      (other ? '<span><i class="dot other"></i>Digər · ' + esc(other) + '</span>' : '') + '</div></div></section>' +
      '<section class="card card-pad"><div class="card-head"><div><h2>Departamentlər</h2><p class="muted">İşçi sayına görə</p></div></div>' + deptHTML + '</section>' +
      '<section class="card card-pad"><div class="card-head"><div><h2>Yaş qrupları</h2><p class="muted">Aktiv işçilər</p></div></div>' + ageHTML + '</section>' +
      '</div>';
  }

  async function renderPayrollRuns() {
    setHeader('Əməkhaqqı hesablamaları', 'Aylıq payroll dövrləri və statusları');
    $('#view').innerHTML = loadingHTML('Hesablamalar yüklənir...');
    var runs = await api('/payroll-runs?limit=100');
    if (!Array.isArray(runs)) runs = normalizeList(runs).items;
    var canManagePayroll = canManage('payroll-runs');

    var rows = runs.map(function (run) {
      var actions = '<a class="btn sm ghost" href="#/s/payroll-run/' + run.id + '">Aç</a>';
      if (canManagePayroll && run.status === 'DRAFT') {
        actions += '<button class="btn sm primary" type="button" data-act="payroll-action" data-id="' + run.id + '" data-op="calculate">Hesabla</button>';
      } else if (canManagePayroll && run.status === 'CALCULATED') {
        actions += '<button class="btn sm primary" type="button" data-act="payroll-action" data-id="' + run.id + '" data-op="approve">Təsdiqlə</button>';
      } else if (canManagePayroll && run.status === 'APPROVED') {
        actions += '<button class="btn sm primary" type="button" data-act="payroll-action" data-id="' + run.id + '" data-op="pay">Ödə</button>';
      }
      if (canManagePayroll && (run.status === 'DRAFT' || run.status === 'CALCULATED')) {
        actions += '<button class="btn sm danger" type="button" data-act="payroll-delete" data-id="' + run.id + '">' + icon('trash') + '</button>';
      }
      return '<tr><td><a class="strong-link" href="#/s/payroll-run/' + run.id + '">' + esc(run.period_year) + '-' + pad(run.period_month) + '</a></td>' +
        '<td>' + esc(humanize(run.run_type)) + '</td><td>' + badge(run.status) + '</td>' +
        '<td class="num">' + esc(fmtMoney(run.total_gross)) + '</td>' +
        '<td class="num">' + esc(fmtMoney(run.total_net)) + '</td>' +
        '<td class="num">' + esc(fmtMoney(run.total_income_tax)) + '</td>' +
        '<td class="actions">' + actions + '</td></tr>';
    }).join('');

    $('#view').innerHTML =
      '<div class="page-toolbar"><div class="toolbar-info"><strong>' + runs.length + '</strong> hesablama dövrü</div>' +
      '<div class="toolbar-actions"><button class="btn ghost" type="button" data-act="payroll-refresh">' + icon('refresh') + 'Yenilə</button>' +
      (canManagePayroll ? '<button class="btn primary" type="button" data-act="payroll-new">' + icon('plus') + 'Yeni hesablama</button>' : '') + '</div></div>' +
      '<div class="card table-card">' +
      (runs.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>Dövr</th><th>Növ</th><th>Status</th><th class="num">Bruto</th><th class="num">Net</th><th class="num">Gəlir vergisi</th><th></th></tr></thead><tbody>' + rows + '</tbody></table></div>'
        : emptyState('Hesablama yoxdur', 'Yeni hesablama yaratmaq üçün sağ üstdəki düymədən istifadə edin.')) +
      '</div>';
  }

  async function openPayrollCreate() {
    await ensureLookups(['organizations']);
    var now = new Date();
    var year = now.getFullYear();
    var month = now.getMonth() + 1;
    var orgs = state.lookups.organizations || [];
    var orgOptions = orgs.map(function (org) {
      var selected = state.user && equals(state.user.organization_id, org.id);
      return '<option value="' + org.id + '"' + (selected ? ' selected' : '') + '>' + esc(org.name) + '</option>';
    }).join('');
    var monthOptions = MONTHS.map(function (name, index) {
      return '<option value="' + (index + 1) + '"' + (index + 1 === month ? ' selected' : '') + '>' + esc(name) + '</option>';
    }).join('');
    openModal({
      title: 'Yeni əməkhaqqı hesablaması',
      subtitle: 'Dövr və təşkilat seçin',
      body: '<form id="payroll-create-form" class="form-grid">' +
        '<label class="field span-2"><span>Təşkilat <span class="req">*</span></span><select name="organization_id" required>' + orgOptions + '</select></label>' +
        '<label class="field"><span>İl <span class="req">*</span></span><input type="number" name="period_year" min="2000" max="2100" value="' + year + '" required></label>' +
        '<label class="field"><span>Ay <span class="req">*</span></span><select name="period_month" required>' + monthOptions + '</select></label>' +
        '<label class="field"><span>Hesablama növü</span><select name="run_type"><option value="REGULAR">Adi</option><option value="BONUS">Bonus</option><option value="FINAL">Yekun</option></select></label>' +
        '<label class="field check span-2"><input type="checkbox" name="auto_calculate" checked><span>Yaradıldıqdan sonra avtomatik hesabla</span></label>' +
        '<label class="field span-2"><span>Qeydlər</span><textarea name="notes" rows="2"></textarea></label>' +
        '</form>',
      footer: '<button class="btn ghost" type="button" data-act="modal-close">İmtina</button>' +
        '<button class="btn primary" type="submit" form="payroll-create-form">' + icon('check') + 'Yarat</button>'
    });
    $('#payroll-create-form').addEventListener('submit', async function (event) {
      event.preventDefault();
      var form = event.target;
      var button = event.submitter || $('button[form="payroll-create-form"]');
      if (button) button.disabled = true;
      try {
        var payload = {
          organization_id: Number(form.elements.organization_id.value),
          period_year: Number(form.elements.period_year.value),
          period_month: Number(form.elements.period_month.value),
          run_type: form.elements.run_type.value,
          notes: form.elements.notes.value || null
        };
        var run = await api('/payroll-runs', { method: 'POST', body: payload });
        if (form.elements.auto_calculate.checked) {
          await api('/payroll-runs/' + run.id + '/calculate', { method: 'POST' });
          toast('Hesablama yaradıldı və hesablandı', 'success');
        } else {
          toast('Hesablama yaradıldı', 'success');
        }
        closeModal();
        await renderPayrollRuns();
      } catch (err) {
        toast(err.message, 'error');
        if (button) button.disabled = false;
      }
    });
  }

  async function payrollAction(id, operation) {
    var labels = { calculate: 'Hesablama aparılsın?', approve: 'Hesablama təsdiqlənsin?', pay: 'Əməkhaqqı ödənilmiş kimi qeyd edilsin?' };
    if (!window.confirm(labels[operation] || 'Əməliyyat icra edilsin?')) return;
    try {
      await api('/payroll-runs/' + id + '/' + operation, { method: 'POST' });
      toast('Əməliyyat uğurla tamamlandı', 'success');
      await route();
    } catch (err) { toast(err.message, 'error'); }
  }

  async function payrollDelete(id) {
    if (!window.confirm('Bu hesablama silinsin?')) return;
    try {
      await api('/payroll-runs/' + id, { method: 'DELETE' });
      toast('Hesablama silindi', 'success');
      await renderPayrollRuns();
    } catch (err) { toast(err.message, 'error'); }
  }

  async function renderPayrollRun(runId) {
    $('#view').innerHTML = loadingHTML('Hesablama yüklənir...');
    var results = await Promise.all([
      api('/payroll-runs/' + runId),
      api('/payroll-runs/' + runId + '/items')
    ]);
    var run = results[0];
    var items = results[1] || [];
    setHeader(run.period_year + ' · ' + MONTHS[run.period_month - 1], 'Əməkhaqqı hesablaması #' + run.id);
    await ensureLookups(['organizations']);

    var totalEmployer = items.reduce(function (sum, item) {
      return sum + (Number(item.dsmf_employer) || 0) + (Number(item.its_employer) || 0) + (Number(item.unemployment_org) || 0);
    }, 0);
    var totalDeductions = items.reduce(function (sum, item) {
      return sum + (Number(item.income_tax) || 0) + (Number(item.dsmf_employee) || 0) + (Number(item.its_employee) || 0) + (Number(item.unemployment_emp) || 0) + (Number(item.other_deductions) || 0);
    }, 0);

    var canManagePayroll = canManage('payroll-runs');
    var actions = '';
    if (canManagePayroll && run.status === 'DRAFT') actions += '<button class="btn primary" type="button" data-act="payroll-action" data-id="' + run.id + '" data-op="calculate">' + icon('refresh') + 'Hesabla</button>';
    if (canManagePayroll && run.status === 'CALCULATED') actions += '<button class="btn primary" type="button" data-act="payroll-action" data-id="' + run.id + '" data-op="approve">' + icon('check') + 'Təsdiqlə</button>';
    if (canManagePayroll && run.status === 'APPROVED') actions += '<button class="btn primary" type="button" data-act="payroll-action" data-id="' + run.id + '" data-op="pay">' + icon('wallet') + 'Ödə</button>';
    if (items.length) {
      actions += '<button class="btn ghost" type="button" data-act="payroll-export" data-id="' + run.id + '" data-format="bank">' + icon('download') + 'Bank reyestri</button>';
      actions += '<button class="btn ghost" type="button" data-act="payroll-export" data-id="' + run.id + '" data-format="gl">' + icon('download') + 'Mühasibat exportu</button>';
    }

    var rows = items.map(function (item) {
      return '<tr><td><span class="strong-link" data-act="payroll-item-details" data-id="' + item.id + '" style="cursor:pointer">' + esc(item.employee_name) + '</span><div class="sub">' + esc(item.pin_code || '') + '</div></td>' +
        '<td class="num">' + esc(item.worked_days) + '</td>' +
        '<td class="num">' + esc(fmtMoney(item.gross_total)) + '</td>' +
        '<td class="num">' + esc(fmtMoney(item.income_tax)) + '</td>' +
        '<td class="num">' + esc(fmtMoney(item.dsmf_employee)) + '</td>' +
        '<td class="num">' + esc(fmtMoney(item.its_employee)) + '</td>' +
        '<td class="num">' + esc(fmtMoney(item.unemployment_emp)) + '</td>' +
        '<td class="num">' + (Number(item.other_deductions) > 0 ? '<span class="badge danger">-' + esc(fmtMoney(item.other_deductions)) + '</span>' : '—') + '</td>' +
        '<td class="num strong">' + esc(fmtMoney(item.net_payable)) + '</td>' +
        '<td class="actions">' +
        '<button class="btn sm ghost" type="button" data-act="payroll-item-details" data-id="' + item.id + '">Detallar</button>' +
        '<button class="btn sm ghost" type="button" data-act="payslip" data-id="' + item.id + '">PDF</button>' +
        '</td></tr>';
    }).join('');

    $('#view').innerHTML =
      '<div class="page-toolbar"><div class="toolbar-info"><a class="back-link" href="#/s/payroll-runs">' + icon('arrow-left') + 'Hesablamalar</a>' +
      '<span class="ml-12">' + badge(run.status) + '</span><span class="muted ml-12">' + esc(refLabel('organizations', run.organization_id)) + '</span></div>' +
      '<div class="toolbar-actions">' + actions + '</div></div>' +
      '<div class="stat-grid compact">' +
      '<div class="stat-card tone-teal"><span class="stat-icon">' + icon('coins') + '</span><span class="stat-copy"><span class="stat-label">İşçi sayı</span><strong class="stat-value">' + items.length + '</strong></span></div>' +
      '<div class="stat-card tone-blue"><span class="stat-icon">' + icon('wallet') + '</span><span class="stat-copy"><span class="stat-label">Bruto fond</span><strong class="stat-value">' + esc(fmtMoney(run.total_gross)) + '</strong></span></div>' +
      '<div class="stat-card tone-violet"><span class="stat-icon">' + icon('receipt') + '</span><span class="stat-copy"><span class="stat-label">Net ödəniş</span><strong class="stat-value">' + esc(fmtMoney(run.total_net)) + '</strong></span></div>' +
      '<div class="stat-card tone-amber"><span class="stat-icon">' + icon('percent') + '</span><span class="stat-copy"><span class="stat-label">Tutulmalar</span><strong class="stat-value">' + esc(fmtMoney(totalDeductions)) + '</strong></span></div>' +
      '<div class="stat-card tone-slate"><span class="stat-icon">' + icon('building') + '</span><span class="stat-copy"><span class="stat-label">İşəgötürən yükü</span><strong class="stat-value">' + esc(fmtMoney(totalEmployer)) + '</strong></span></div>' +
      '</div>' +
      '<div class="card table-card">' +
      (items.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>İşçi</th><th class="num">Gün</th><th class="num">Bruto</th><th class="num">Gəlir vergisi</th><th class="num">DSMF</th><th class="num">İTS</th><th class="num">İşsizlik</th><th class="num">Kəsintilər</th><th class="num">Net</th><th></th></tr></thead><tbody>' + rows + '</tbody></table></div>'
        : emptyState('Sətir yoxdur', 'Hesablama aparıldıqdan sonra işçi sətirləri görünəcək.')) +
      '</div>';
  }

  async function openPayrollItemBreakdownModal(itemId) {
    try {
      var item = await api('/payroll-items/' + itemId);
      var details = item.details || [];
      var earnings = details.filter(function (d) { return d.direction === 'EARNING'; });
      var deductions = details.filter(function (d) { return d.direction === 'DEDUCTION'; });

      var earningsRows = earnings.map(function (d) {
        return '<div class="breakdown-row"><span class="label">' + esc(d.calc_formula_note || d.component_code) + '</span><span class="val text-success">+' + esc(fmtMoney(d.amount)) + '</span></div>';
      }).join('');

      var taxRows = '<div class="breakdown-row"><span class="label">Gəlir vergisi (AR VM m. 101/102)</span><span class="val text-danger">-' + esc(fmtMoney(item.income_tax)) + '</span></div>' +
        '<div class="breakdown-row"><span class="label">DSMF (işçi 3% / 10%)</span><span class="val text-danger">-' + esc(fmtMoney(item.dsmf_employee)) + '</span></div>' +
        '<div class="breakdown-row"><span class="label">İcbari Tibbi Sığorta (İTS 2%)</span><span class="val text-danger">-' + esc(fmtMoney(item.its_employee)) + '</span></div>' +
        '<div class="breakdown-row"><span class="label">İşsizlikdən sığorta (0.5%)</span><span class="val text-danger">-' + esc(fmtMoney(item.unemployment_emp)) + '</span></div>';

      var deductionRows = deductions.map(function (d) {
        return '<div class="breakdown-row"><span class="label">' + esc(d.calc_formula_note || d.component_code) + '</span><span class="val text-danger">-' + esc(fmtMoney(d.amount)) + '</span></div>';
      }).join('') || '<div class="breakdown-row"><span class="muted">Əlavə fərdi kəsinti yoxdur</span><span class="val">0.00 ₼</span></div>';

      var employerRows = '<div class="breakdown-row"><span class="label">DSMF (işəgötürən 22%)</span><span class="val">' + esc(fmtMoney(item.dsmf_employer)) + '</span></div>' +
        '<div class="breakdown-row"><span class="label">İcbari Tibbi Sığorta (2%)</span><span class="val">' + esc(fmtMoney(item.its_employer)) + '</span></div>' +
        '<div class="breakdown-row"><span class="label">İşsizlikdən sığorta (0.5%)</span><span class="val">' + esc(fmtMoney(item.unemployment_org)) + '</span></div>';

      openModal({
        title: item.employee_name,
        subtitle: 'Əməkhaqqı Hesablama Vərəqəsi · PIN: ' + esc(item.pin_code || '') + ' · İşlənmiş gün: ' + item.worked_days,
        size: 'lg',
        body: '<div class="breakdown-summary-banner">' +
          '<div class="net-col"><span>Ödəniləcək Xalis Məbləğ (Net)</span><strong>' + esc(fmtMoney(item.net_payable)) + '</strong></div>' +
          '<div><div style="font-size:12px;opacity:.9">Ümumi Bruto: <strong>' + esc(fmtMoney(item.gross_total)) + '</strong></div>' +
          '<div style="font-size:12px;opacity:.9">Vergi və tutulmalar cəmi: <strong>-' + esc(fmtMoney(Number(item.income_tax) + Number(item.dsmf_employee) + Number(item.its_employee) + Number(item.unemployment_emp) + Number(item.other_deductions))) + '</strong></div></div>' +
          '</div>' +
          '<div class="breakdown-grid">' +
          '<div class="breakdown-box earnings"><h4>' + icon('coins') + ' Qazanclar (Bruto)</h4>' + (earningsRows || '<div class="muted">Məlumat yoxdur</div>') + '</div>' +
          '<div class="breakdown-box taxes"><h4>' + icon('receipt') + ' Dövlət Tutulmaları</h4>' + taxRows + '</div>' +
          '<div class="breakdown-box deductions"><h4>' + icon('alert') + ' Kəsintilər və Cərimələr</h4>' + deductionRows + '</div>' +
          '<div class="breakdown-box employer"><h4>' + icon('building') + ' İşəgötürən Xərcləri</h4>' + employerRows + '</div>' +
          '</div>',
        footer: '<button class="btn ghost" type="button" data-act="modal-close">Bağla</button>' +
          '<button class="btn primary" type="button" data-act="payslip" data-id="' + item.id + '">' + icon('download') + 'PDF Hesablama vərəqəsi</button>'
      });
    } catch (err) { toast(err.message, 'error'); }
  }

  async function downloadPayslip(itemId) {
    try {
      await downloadFile('/payroll-items/' + itemId + '/payslip.pdf', 'payslip-' + itemId + '.pdf');
    } catch (err) { toast(err.message, 'error'); }
  }

  async function exportPayroll(runId, format) {
    try {
      if (format === 'bank') await downloadFile('/payroll-runs/' + runId + '/bank-register.csv', 'bank-register-' + runId + '.csv');
      else await downloadFile('/payroll-runs/' + runId + '/gl-export.csv', 'gl-export-' + runId + '.csv');
    } catch (err) { toast(err.message, 'error'); }
  }

  async function renderLeaveRequests() {
    setHeader('Məzuniyyət sorğuları', 'Sorğuların yaradılması və təsdiqi');
    $('#view').innerHTML = loadingHTML('Sorğular yüklənir...');
    await ensureLookups(['employees', 'leave-types']);
    var query = '/leave-requests?limit=300';
    if (state.leaveFilter !== 'ALL') query += '&status=' + state.leaveFilter;
    var rowsData = await api(query);
    if (!Array.isArray(rowsData)) rowsData = normalizeList(rowsData).items;

    var tabs = ['ALL', 'PENDING', 'APPROVED', 'REJECTED', 'CANCELLED'].map(function (status) {
      return '<button class="tab' + (state.leaveFilter === status ? ' active' : '') + '" type="button" data-act="leave-filter" data-status="' + status + '">' +
        esc(status === 'ALL' ? 'Hamısı' : humanize(status)) + '</button>';
    }).join('');

    var canManageLeave = canManage('leave-requests');
    var rows = rowsData.map(function (row) {
      var actions = '';
      if (canManageLeave && row.status === 'PENDING') {
        actions += '<button class="btn sm primary" type="button" data-act="leave-approve" data-id="' + row.id + '">Təsdiqlə</button>';
        actions += '<button class="btn sm danger" type="button" data-act="leave-reject" data-id="' + row.id + '">Rədd et</button>';
      } else if (canManageLeave && row.status === 'APPROVED') {
        actions += '<button class="btn sm ghost" type="button" data-act="leave-cancel" data-id="' + row.id + '">Ləğv et</button>';
      }
      return '<tr><td><span class="strong-link">' + esc(row.employee_name || refLabel('employees', row.employee_id)) + '</span><div class="sub">' + esc(row.pin_code || '') + '</div></td>' +
        '<td>' + esc(row.leave_type || '—') + '</td>' +
        '<td>' + esc(fmtDate(row.start_date)) + ' — ' + esc(fmtDate(row.end_date)) + '</td>' +
        '<td class="num">' + esc(row.calendar_days) + '</td>' +
        '<td class="num">' + esc(row.paid_days) + '</td>' +
        '<td>' + badge(row.status) + '</td>' +
        '<td class="actions">' + actions + '</td></tr>';
    }).join('');

    $('#view').innerHTML =
      '<div class="page-toolbar"><div class="tabs">' + tabs + '</div>' +
      '<div class="toolbar-actions"><button class="btn ghost" type="button" data-act="leave-refresh">' + icon('refresh') + 'Yenilə</button>' +
      (canManageLeave ? '<button class="btn primary" type="button" data-act="leave-new">' + icon('plus') + 'Yeni sorğu</button>' : '') + '</div></div>' +
      '<div class="card table-card">' +
      (rowsData.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>İşçi</th><th>Növ</th><th>Dövr</th><th class="num">Təqvim günü</th><th class="num">Ödənişli gün</th><th>Status</th><th></th></tr></thead><tbody>' + rows + '</tbody></table></div>'
        : emptyState('Sorğu yoxdur', 'Seçilmiş status üzrə məzuniyyət sorğusu tapılmadı.')) +
      '</div>';
  }

  async function openLeaveCreate() {
    await ensureLookups(['employees', 'leave-types']);
    var employees = state.lookups.employees || [];
    var leaveTypes = state.lookups['leave-types'] || [];
    var employeeOptions = employees.map(function (employee) {
      return '<option value="' + employee.id + '">' + esc([employee.last_name, employee.first_name].filter(Boolean).join(' ') + ' · ' + (employee.pin_code || '')) + '</option>';
    }).join('');
    var typeOptions = leaveTypes.map(function (type) {
      return '<option value="' + type.id + '">' + esc(type.name) + (type.is_paid ? '' : ' (ödənişsiz)') + '</option>';
    }).join('');
    openModal({
      title: 'Yeni məzuniyyət sorğusu',
      subtitle: 'İşçi və dövr seçin',
      body: '<form id="leave-create-form" class="form-grid">' +
        '<label class="field span-2"><span>İşçi <span class="req">*</span></span><select name="employee_id" required>' + employeeOptions + '</select></label>' +
        '<label class="field span-2"><span>Məzuniyyət növü <span class="req">*</span></span><select name="leave_type_id" required>' + typeOptions + '</select></label>' +
        '<label class="field"><span>Başlama tarixi <span class="req">*</span></span><input type="date" name="start_date" required></label>' +
        '<label class="field"><span>Bitmə tarixi <span class="req">*</span></span><input type="date" name="end_date" required></label>' +
        '<label class="field span-2"><span>Səbəb</span><textarea name="reason" rows="2"></textarea></label>' +
        '</form>',
      footer: '<button class="btn ghost" type="button" data-act="modal-close">İmtina</button>' +
        '<button class="btn primary" type="submit" form="leave-create-form">' + icon('check') + 'Yarat</button>'
    });
    $('#leave-create-form').addEventListener('submit', async function (event) {
      event.preventDefault();
      var form = event.target;
      try {
        await api('/leave-requests', {
          method: 'POST',
          body: {
            employee_id: Number(form.elements.employee_id.value),
            leave_type_id: Number(form.elements.leave_type_id.value),
            start_date: form.elements.start_date.value,
            end_date: form.elements.end_date.value,
            reason: form.elements.reason.value || null
          }
        });
        closeModal();
        toast('Sorğu yaradıldı', 'success');
        await renderLeaveRequests();
      } catch (err) { toast(err.message, 'error'); }
    });
  }

  async function decideLeave(id, operation) {
    var labels = { approve: 'Sorğu təsdiqlənsin?', reject: 'Sorğu rədd edilsin?', cancel: 'Sorğu ləğv edilsin?' };
    if (!window.confirm(labels[operation])) return;
    try {
      await api('/leave-requests/' + id + '/' + operation, { method: 'POST', body: {} });
      toast('Sorğu yeniləndi', 'success');
      await renderLeaveRequests();
    } catch (err) { toast(err.message, 'error'); }
  }

  async function renderSickLeaves() {
    setHeader('Xəstəlik vərəqələri', 'Bülletenlər və müavinət hesablamaları');
    $('#view').innerHTML = loadingHTML('Bülletenlər yüklənir...');
    var rowsData = await api('/sick-leaves?limit=300');
    if (!Array.isArray(rowsData)) rowsData = normalizeList(rowsData).items;
    var canManageSick = canManage('sick-leaves');
    var rows = rowsData.map(function (row) {
      return '<tr><td><span class="strong-link">' + esc(row.employee_name || ('#' + row.employee_id)) + '</span><div class="sub">' + esc(row.pin_code || '') + '</div></td>' +
        '<td class="mono">' + esc(row.bulletin_number) + '</td>' +
        '<td>' + esc(fmtDate(row.start_date)) + ' — ' + esc(fmtDate(row.end_date)) + '</td>' +
        '<td class="num">' + esc(row.total_days) + '</td>' +
        '<td class="num">' + esc(fmtMoney(row.calculated_amount)) + '</td>' +
        '<td>' + badge(row.status) + '</td>' +
        '<td class="actions">' + (canManageSick && row.status === 'ACTIVE' ? '<button class="btn sm ghost" type="button" data-act="sick-cancel" data-id="' + row.id + '">Ləğv et</button>' : '') + '</td></tr>';
    }).join('');
    $('#view').innerHTML =
      '<div class="page-toolbar"><div class="toolbar-info"><strong>' + rowsData.length + '</strong> bülleten</div>' +
      '<div class="toolbar-actions"><button class="btn ghost" type="button" data-act="sick-refresh">' + icon('refresh') + 'Yenilə</button>' +
      (canManageSick ? '<button class="btn primary" type="button" data-act="sick-new">' + icon('plus') + 'Yeni bülleten</button>' : '') + '</div></div>' +
      '<div class="card table-card">' +
      (rowsData.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>İşçi</th><th>Bülleten №</th><th>Dövr</th><th class="num">Gün</th><th class="num">Müavinət</th><th>Status</th><th></th></tr></thead><tbody>' + rows + '</tbody></table></div>'
        : emptyState('Bülleten yoxdur', 'Yeni xəstəlik vərəqəsi əlavə edin.')) +
      '</div>';
  }

  async function openSickCreate() {
    await ensureLookups(['employees']);
    var employees = state.lookups.employees || [];
    var options = employees.map(function (employee) {
      return '<option value="' + employee.id + '">' + esc([employee.last_name, employee.first_name].filter(Boolean).join(' ') + ' · ' + (employee.pin_code || '')) + '</option>';
    }).join('');
    openModal({
      title: 'Yeni xəstəlik vərəqəsi',
      subtitle: 'Bülleten məlumatlarını daxil edin',
      body: '<form id="sick-create-form" class="form-grid">' +
        '<label class="field span-2"><span>İşçi <span class="req">*</span></span><select name="employee_id" required>' + options + '</select></label>' +
        '<label class="field span-2"><span>Bülleten nömrəsi <span class="req">*</span></span><input type="text" name="bulletin_number" required></label>' +
        '<label class="field"><span>Başlama tarixi <span class="req">*</span></span><input type="date" name="start_date" required></label>' +
        '<label class="field"><span>Bitmə tarixi <span class="req">*</span></span><input type="date" name="end_date" required></label>' +
        '<label class="field span-2"><span>Qeydlər</span><textarea name="notes" rows="2"></textarea></label>' +
        '</form>',
      footer: '<button class="btn ghost" type="button" data-act="modal-close">İmtina</button>' +
        '<button class="btn primary" type="submit" form="sick-create-form">' + icon('check') + 'Hesabla və yarat</button>'
    });
    $('#sick-create-form').addEventListener('submit', async function (event) {
      event.preventDefault();
      var form = event.target;
      try {
        await api('/sick-leaves', {
          method: 'POST',
          body: {
            employee_id: Number(form.elements.employee_id.value),
            bulletin_number: form.elements.bulletin_number.value.trim(),
            start_date: form.elements.start_date.value,
            end_date: form.elements.end_date.value,
            notes: form.elements.notes.value || null
          }
        });
        closeModal();
        toast('Bülleten yaradıldı və hesablandı', 'success');
        await renderSickLeaves();
      } catch (err) { toast(err.message, 'error'); }
    });
  }

  async function cancelSick(id) {
    if (!window.confirm('Bülleten ləğv edilsin?')) return;
    try {
      await api('/sick-leaves/' + id + '/cancel', { method: 'POST' });
      toast('Bülleten ləğv edildi', 'success');
      await renderSickLeaves();
    } catch (err) { toast(err.message, 'error'); }
  }

  function currentPeriod() {
    var now = new Date();
    return { year: now.getFullYear(), month: now.getMonth() + 1 };
  }

  async function renderTimesheets() {
    var period = currentPeriod();
    if (!state.timesheetYear) state.timesheetYear = period.year;
    if (!state.timesheetMonth) state.timesheetMonth = period.month;
    if (!state.timesheetMode) state.timesheetMode = 'matrix'; // default to T-13 matrix view

    setHeader('Tabel (T-13)', 'Aylıq iş vaxtı uçotu və turniket davamiyyəti');
    $('#view').innerHTML = loadingHTML('Tabel yüklənir...');
    await ensureLookups(['employees', 'organizations']);

    var yearOptions = '';
    var nowYear = new Date().getFullYear();
    for (var y = nowYear + 1; y >= nowYear - 3; y -= 1) {
      yearOptions += '<option value="' + y + '"' + (Number(state.timesheetYear) === y ? ' selected' : '') + '>' + y + '</option>';
    }
    var monthOptions = MONTHS.map(function (name, index) {
      return '<option value="' + (index + 1) + '"' + (Number(state.timesheetMonth) === index + 1 ? ' selected' : '') + '>' + esc(name) + '</option>';
    }).join('');

    var canManageTimesheet = canManage('timesheets');
    var isMatrix = state.timesheetMode === 'matrix';

    var toolbarHTML =
      '<div class="page-toolbar">' +
      '<form class="filter-row" id="timesheet-filter">' +
      '<select name="year">' + yearOptions + '</select><select name="month">' + monthOptions + '</select>' +
      '<button class="btn ghost" type="submit">' + icon('refresh') + 'Göstər</button>' +
      '</form>' +
      '<div class="tab-pill-group">' +
      '<button class="tab-pill' + (isMatrix ? ' active' : '') + '" type="button" data-act="timesheet-mode" data-mode="matrix">' + icon('calendar-grid') + 'T-13 Günbəgün (1-31)</button>' +
      '<button class="tab-pill' + (!isMatrix ? ' active' : '') + '" type="button" data-act="timesheet-mode" data-mode="summary">' + icon('list') + 'Aylıq İcmal</button>' +
      '</div>' +
      '<div class="toolbar-actions">' +
      (canManageTimesheet ? '<button class="btn ghost" type="button" data-act="turnstile-import">' + icon('download') + 'Turniket İdxal</button>' : '') +
      (canManageTimesheet ? '<button class="btn ghost" type="button" data-act="turnstile-simulate">' + icon('sync') + 'Turniket Simulyasiyası</button>' : '') +
      (canManageTimesheet ? '<button class="btn primary" type="button" data-act="timesheet-generate">' + icon('calendar') + 'Tabel yarat</button>' : '') +
      '</div></div>';

    if (isMatrix) {
      try {
        var matrixData = await api('/timesheets/matrix?year=' + state.timesheetYear + '&month=' + state.timesheetMonth);
        var calDays = matrixData.calendar_days || [];
        var employees = matrixData.employees || [];

        var dayHeaders = calDays.map(function (d) {
          var isWeekend = d.weekday === 'Ş' || d.weekday === 'B';
          return '<th class="t13-day-col' + (isWeekend ? ' weekend' : '') + '" title="' + esc(d.date + ' (' + (d.description || d.weekday) + ')') + '">' +
            '<div>' + d.day + '</div><div style="font-size:9px;opacity:.7">' + esc(d.weekday) + '</div></th>';
        }).join('');

        var matrixRows = employees.map(function (emp) {
          var actions = '';
          if (canManageTimesheet && emp.status === 'OPEN') actions += '<button class="btn sm primary" type="button" data-act="timesheet-approve" data-id="' + emp.timesheet_id + '">Təsdiqlə</button>';
          if (canManageTimesheet && emp.status === 'APPROVED') actions += '<button class="btn sm ghost" type="button" data-act="timesheet-lock" data-id="' + emp.timesheet_id + '">Kilidlə</button>';
          actions += '<button class="btn sm ghost" type="button" data-act="timesheet-daily" data-id="' + emp.timesheet_id + '" title="Gündəlik giriş-çıxış və düzəliş">Detallar</button>';

          var dailyCells = calDays.map(function (d) {
            var rec = (emp.daily_records || {})[d.date];
            var isWeekend = d.weekday === 'Ş' || d.weekday === 'B';
            if (!rec) {
              return '<td class="' + (isWeekend ? 'weekend' : '') + '">—</td>';
            }
            var badgeClass = 't13-badge';
            if (rec.code === 'İ') badgeClass += ' work';
            else if (rec.code === 'M') badgeClass += ' leave';
            else if (rec.code === 'X') badgeClass += ' sick';
            else if (rec.code === 'EZ') badgeClass += ' trip';
            else if (rec.code === 'B') badgeClass += ' holiday';
            else if (rec.code === 'İQ') badgeClass += ' rest';
            else if (rec.code === 'Q') badgeClass += ' absent';

            if (rec.is_manual_override) badgeClass += ' manual';

            var displayVal = rec.code === 'İ' ? (rec.worked_hours > 0 ? rec.worked_hours : '8') : rec.code;
            var tooltip = (rec.type_label || '') + (rec.punch_in ? ' | Giriş: ' + rec.punch_in + ' Çıxış: ' + (rec.punch_out || '—') : '') + (rec.late_minutes > 0 ? ' | ⚠️ ' + rec.late_minutes + ' dəq gecikmə' : '') + (rec.notes ? ' | Qeyd: ' + rec.notes : '');

            return '<td class="' + (isWeekend ? 'weekend' : '') + '">' +
              '<span class="' + badgeClass + '" data-act="timesheet-daily" data-id="' + emp.timesheet_id + '" data-day="' + d.date + '" title="' + esc(tooltip) + '">' +
              esc(displayVal) + '</span></td>';
          }).join('');

          return '<tr>' +
            '<td class="sticky-emp"><span class="strong-link" data-act="timesheet-daily" data-id="' + emp.timesheet_id + '" style="cursor:pointer">' + esc(emp.name) + '</span>' +
            '<div class="sub">' + esc(emp.position || emp.pin_code || '') + '</div></td>' +
            dailyCells +
            '<td class="sticky-total num">' + emp.worked_days + '/' + emp.planned_days + '</td>' +
            '<td class="sticky-total num">' + fmtNumber(emp.regular_hours, 1) + '</td>' +
            '<td class="sticky-total num">' + (emp.overtime_hours > 0 ? fmtNumber(emp.overtime_hours, 1) : '—') + '</td>' +
            '<td class="sticky-total actions">' + actions + '</td>' +
            '</tr>';
        }).join('');

        $('#view').innerHTML = toolbarHTML +
          '<div class="t13-matrix-container">' +
          (employees.length ?
            '<table class="t13-table"><thead><tr>' +
            '<th class="sticky-emp">İşçi / Vəzifə</th>' +
            dayHeaders +
            '<th class="sticky-total">İş Günü</th><th class="sticky-total">Normal S.</th><th class="sticky-total">Əlavə S.</th><th class="sticky-total">Əməliyyat</th>' +
            '</tr></thead><tbody>' + matrixRows + '</tbody></table>'
            : emptyState('Tabel tapılmadı', 'Seçilmiş ay üçün "Tabel yarat" düyməsini sıxın.')) +
          '</div>' +
          '<div style="margin-top:12px;display:flex;align-items:center;gap:12px;font-size:11px;color:var(--muted);flex-wrap:wrap">' +
          '<span><strong>Şərti işarələr:</strong></span>' +
          '<span><span class="t13-badge work">8</span> İş günü</span>' +
          '<span><span class="t13-badge leave">M</span> Məzuniyyət</span>' +
          '<span><span class="t13-badge sick">X</span> Xəstəlik</span>' +
          '<span><span class="t13-badge trip">EZ</span> Ezamiyyət</span>' +
          '<span><span class="t13-badge rest">İQ</span> İstirahət</span>' +
          '<span><span class="t13-badge holiday">B</span> Bayram</span>' +
          '<span><span class="t13-badge absent">Q</span> Qayıb</span>' +
          '<span><span class="t13-badge work manual">8</span> Əl ilə təsdiq</span>' +
          '</div>';

      } catch (err) {
        toast(err.message, 'error');
        $('#view').innerHTML = toolbarHTML + errorCard(err.message);
      }
    } else {
      // Summary list mode
      var data = await api('/timesheets?limit=500&year=' + state.timesheetYear + '&month=' + state.timesheetMonth);
      var normalized = normalizeList(data);
      var rowsData = normalized.items;
      var rows = rowsData.map(function (row) {
        var actions = '';
        if (canManageTimesheet && row.status === 'OPEN') actions += '<button class="btn sm primary" type="button" data-act="timesheet-approve" data-id="' + row.id + '">Təsdiqlə</button>';
        if (canManageTimesheet && row.status === 'APPROVED') actions += '<button class="btn sm ghost" type="button" data-act="timesheet-lock" data-id="' + row.id + '">Kilidlə</button>';
        actions += '<button class="btn sm ghost" type="button" data-act="timesheet-daily" data-id="' + row.id + '">Detallar</button>';
        return '<tr><td><span class="strong-link" data-act="timesheet-daily" data-id="' + row.id + '" style="cursor:pointer">' + esc(refLabel('employees', row.employee_id)) + '</span></td>' +
          '<td class="num">' + esc(row.planned_days) + '</td><td class="num">' + esc(row.worked_days) + '</td>' +
          '<td class="num">' + esc(fmtNumber(row.regular_hours, 1)) + '</td>' +
          '<td class="num">' + esc(fmtNumber(row.overtime_hours, 1)) + '</td>' +
          '<td class="num">' + esc(fmtNumber(row.night_hours, 1)) + '</td>' +
          '<td class="num">' + esc(row.vacation_days) + '</td><td class="num">' + esc(row.sick_days) + '</td>' +
          '<td>' + badge(row.status) + '</td><td class="actions">' + actions + '</td></tr>';
      }).join('');

      $('#view').innerHTML = toolbarHTML +
        '<div class="card table-card">' +
        (rowsData.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>İşçi</th><th class="num">Plan gün</th><th class="num">İşlənmiş</th><th class="num">Normal saat</th><th class="num">Əlavə</th><th class="num">Gecə</th><th class="num">Məzuniyyət</th><th class="num">Xəstəlik</th><th>Status</th><th></th></tr></thead><tbody>' + rows + '</tbody></table></div>'
          : emptyState('Tabel yoxdur', 'Seçilmiş dövr üçün tabel yaradın.')) +
        '<div class="table-footer"><span>' + normalized.total + ' sətir</span></div></div>';
    }

    $('#timesheet-filter').addEventListener('submit', function (event) {
      event.preventDefault();
      state.timesheetYear = Number(event.target.elements.year.value);
      state.timesheetMonth = Number(event.target.elements.month.value);
      renderTimesheets().catch(function (err) { toast(err.message, 'error'); });
    });
  }

  async function openEmployeeDailyAttendanceModal(timesheetId, highlightDay) {
    try {
      var data = await api('/timesheets/' + timesheetId + '/daily');
      var dailyMap = data.daily_records || {};
      var daysList = Object.keys(dailyMap).sort().map(function (k) { return dailyMap[k]; });

      var totalLateMins = daysList.reduce(function (sum, d) { return sum + (Number(d.late_minutes) || 0); }, 0);
      var canManageTimesheet = canManage('timesheets');

      var dayRows = daysList.map(function (d) {
        var isHighlighted = highlightDay && d.date === highlightDay;
        var lateBadge = d.late_minutes > 0 ? '<span class="badge warning" title="Gecikmə">⚠️ +' + d.late_minutes + ' dəq</span>' : '—';
        var overrideBadge = d.is_manual_override ? '<span class="badge neutral" title="Əl ilə redaktə edilib">✏️ Əl ilə</span>' : '';
        var statusBadge = '<span class="t13-badge ' + (d.code === 'İ' ? 'work' : (d.code === 'M' ? 'leave' : (d.code === 'X' ? 'sick' : (d.code === 'EZ' ? 'trip' : (d.code === 'B' ? 'holiday' : 'rest'))))) + '">' + esc(d.code) + '</span>';

        var editBtn = canManageTimesheet ?
          '<button class="btn sm ghost" type="button" data-act="daily-override-prompt" data-sheet="' + timesheetId + '" data-day="' + d.date + '" data-hours="' + d.worked_hours + '" data-code="' + d.code + '" data-notes="' + esc(d.notes || '') + '">Düzəliş</button>' : '';

        return '<tr' + (isHighlighted ? ' style="background:#fef3c7"' : '') + '>' +
          '<td><strong>' + esc(d.date) + '</strong> <span class="muted">(' + esc(d.weekday) + ')</span></td>' +
          '<td>' + statusBadge + ' ' + esc(d.type_label || '') + '</td>' +
          '<td class="num mono">' + (d.punch_in ? '<span style="color:#059669">● ' + esc(d.punch_in) + '</span>' : '<span class="muted">—</span>') + '</td>' +
          '<td class="num mono">' + (d.punch_out ? '<span style="color:#2563eb">● ' + esc(d.punch_out) + '</span>' : '<span class="muted">—</span>') + '</td>' +
          '<td class="num">' + lateBadge + '</td>' +
          '<td class="num strong">' + esc(fmtNumber(d.worked_hours, 1)) + 's</td>' +
          '<td>' + (d.notes ? '<span class="sub" style="color:var(--text)">' + esc(d.notes) + '</span> ' : '') + overrideBadge + '</td>' +
          '<td class="actions">' + editBtn + '</td>' +
          '</tr>';
      }).join('');

      openModal({
        title: data.employee_name + ' · Gündəlik Davamiyyət Kartı',
        subtitle: data.year + ' ' + MONTHS[data.month - 1] + ' · PIN: ' + esc(data.pin_code || '') + ' · Status: ' + data.status,
        size: 'lg',
        body: '<div class="stat-grid compact mb-16">' +
          '<div class="stat-card tone-blue"><span class="stat-icon">' + icon('clock') + '</span><span class="stat-copy"><span class="stat-label">İşlənmiş Saat</span><strong class="stat-value">' + fmtNumber(data.regular_hours, 1) + 's</strong></span></div>' +
          '<div class="stat-card tone-teal"><span class="stat-icon">' + icon('check') + '</span><span class="stat-copy"><span class="stat-label">İşlənmiş Gün</span><strong class="stat-value">' + data.worked_days + '/' + data.planned_days + '</strong></span></div>' +
          '<div class="stat-card tone-amber"><span class="stat-icon">' + icon('alert') + '</span><span class="stat-copy"><span class="stat-label">Cəmi Gecikmə</span><strong class="stat-value">' + (totalLateMins > 0 ? totalLateMins + ' dəq' : '0') + '</strong></span></div>' +
          '</div>' +
          '<div class="table-wrap" style="max-height:420px;overflow-y:auto"><table class="data"><thead><tr>' +
          '<th>Tarix</th><th>Status</th><th class="num">Giriş (IN)</th><th class="num">Çıxış (OUT)</th><th class="num">Gecikmə</th><th class="num">Faktiki saat</th><th>Qeyd</th><th></th>' +
          '</tr></thead><tbody>' + dayRows + '</tbody></table></div>',
        footer: '<button class="btn ghost" type="button" data-act="modal-close">Bağla</button>'
      });
    } catch (err) { toast(err.message, 'error'); }
  }

  async function openDailyOverrideModal(timesheetId, dayStr, currentHours, currentCode, currentNotes) {
    openModal({
      title: 'Günün saatına düzəliş et',
      subtitle: dayStr + ' tarixi üçün təsdiq',
      body: '<form id="daily-override-form" class="form-grid">' +
        '<label class="field"><span>İşlənmiş saat <span class="req">*</span></span>' +
        '<input type="number" step="0.5" min="0" max="24" name="worked_hours" value="' + (currentHours || 8) + '" required></label>' +
        '<label class="field"><span>Status kodu <span class="req">*</span></span>' +
        '<select name="code">' +
        '<option value="İ"' + (currentCode === 'İ' ? ' selected' : '') + '>İ · İş günü</option>' +
        '<option value="M"' + (currentCode === 'M' ? ' selected' : '') + '>M · Məzuniyyət</option>' +
        '<option value="X"' + (currentCode === 'X' ? ' selected' : '') + '>X · Xəstəlik</option>' +
        '<option value="EZ"' + (currentCode === 'EZ' ? ' selected' : '') + '>EZ · Ezamiyyət</option>' +
        '<option value="Q"' + (currentCode === 'Q' ? ' selected' : '') + '>Q · Qayıb</option>' +
        '<option value="İQ"' + (currentCode === 'İQ' ? ' selected' : '') + '>İQ · İstirahət</option>' +
        '</select></label>' +
        '<label class="field span-2"><span>Səbəb / İzah qeydi</span>' +
        '<input type="text" name="notes" placeholder="Məs: Kartı evdə unudub, icazəli olub" value="' + esc(currentNotes || '') + '"></label>' +
        '</form>',
      footer: '<button class="btn ghost" type="button" data-act="modal-close">İmtina</button>' +
        '<button class="btn primary" type="submit" form="daily-override-form">' + icon('check') + 'Yadda saxla</button>'
    });

    $('#daily-override-form').addEventListener('submit', async function (event) {
      event.preventDefault();
      var form = event.target;
      try {
        await api('/timesheets/' + timesheetId + '/daily-override', {
          method: 'POST',
          body: JSON.stringify({
            day: dayStr,
            worked_hours: Number(form.elements.worked_hours.value),
            code: form.elements.code.value,
            notes: form.elements.notes.value
          })
        });
        toast('Günün məlumatı yeniləndi', 'success');
        closeModal();
        await renderTimesheets();
        await openEmployeeDailyAttendanceModal(timesheetId, dayStr);
      } catch (err) { toast(err.message, 'error'); }
    });
  }

  async function simulateTurnstileAction() {
    if (!window.confirm(state.timesheetYear + ' / ' + MONTHS[state.timesheetMonth - 1] + ' dövrü üçün bütün aktiv işçilərə avtomatik turniket giriş-çıxış vuruşları (punch logs) yaradılsın?')) return;
    try {
      var res = await api('/attendance/simulate-turnstile?year=' + state.timesheetYear + '&month=' + state.timesheetMonth, { method: 'POST' });
      toast(res.message, 'success');
      await renderTimesheets();
    } catch (err) { toast(err.message, 'error'); }
  }

  async function openTurnstileImportModal() {
    openModal({
      title: 'Turniket loqlarını idxal et (CSV)',
      subtitle: 'Turniket cihazından ixrac edilmiş fayl və ya mətn',
      size: 'lg',
      body: '<form id="turnstile-import-form" class="form-grid">' +
        '<div class="span-2" style="font-size:12px;color:var(--muted);background:var(--surface-2);padding:10px;border-radius:8px">' +
        '<strong>Tələb olunan CSV formatı:</strong> <code>pin_code,punch_time,direction,device_id</code><br>' +
        'Nümunə:<br><code>1234567,2026-11-15 08:52:00,IN,TURNSTILE-01</code><br><code>1234567,2026-11-15 18:05:00,OUT,TURNSTILE-02</code>' +
        '</div>' +
        '<label class="field span-2"><span>CSV Mətni <span class="req">*</span></span>' +
        '<textarea name="csv_text" rows="8" style="font-family:var(--font-mono);font-size:12px" required placeholder="pin_code,punch_time,direction,device_id&#10;1234567,2026-11-15 08:55:00,IN,GATE-01"></textarea></label>' +
        '</form>',
      footer: '<button class="btn ghost" type="button" data-act="modal-close">İmtina</button>' +
        '<button class="btn primary" type="submit" form="turnstile-import-form">' + icon('download') + 'İdxal et</button>'
    });

    $('#turnstile-import-form').addEventListener('submit', async function (event) {
      event.preventDefault();
      var form = event.target;
      try {
        var res = await api('/attendance/import-csv', {
          method: 'POST',
          body: JSON.stringify({ csv_text: form.elements.csv_text.value })
        });
        closeModal();
        toast(res.message, 'success');
        await renderTimesheets();
      } catch (err) { toast(err.message, 'error'); }
    });
  }

  async function renderAttendance() {
    setHeader('Turniket və Davamiyyət', 'Biometrik / Kart turniket loqları və canlı monitorinq');
    $('#view').innerHTML = loadingHTML('Turniket məlumatları yüklənir...');
    await ensureLookups(['employees']);

    try {
      var results = await Promise.all([
        api('/attendance/today-summary'),
        api('/attendance?limit=100')
      ]);
      var summary = results[0];
      var logs = normalizeList(results[1]).items;

      var canManageTimesheet = canManage('timesheets');
      var actions = '';
      if (canManageTimesheet) {
        actions += '<button class="btn ghost" type="button" data-act="turnstile-import">' + icon('download') + 'Turniket CSV İdxal</button>';
        actions += '<button class="btn primary" type="button" data-act="turnstile-simulate">' + icon('sync') + 'Turniket Simulyasiyası</button>';
      }

      var employeeRows = (summary.employees || []).map(function (emp) {
        var statusBadge = emp.is_inside ? '<span class="badge success">● Ofisdədir (Giriş)</span>' : (emp.first_in ? '<span class="badge neutral">Çıxıb</span>' : '<span class="badge danger">Gəlməyib</span>');
        var lateBadge = emp.is_late ? '<span class="badge warning">⚠️ +' + emp.late_minutes + ' dəq</span>' : (emp.first_in ? '<span class="badge success">Vaxtında</span>' : '—');
        return '<tr>' +
          '<td><strong>' + esc(emp.name) + '</strong><div class="sub">' + esc(emp.pin_code || '') + '</div></td>' +
          '<td class="num mono">' + (emp.first_in ? esc(emp.first_in) : '—') + '</td>' +
          '<td class="num mono">' + (emp.last_out ? esc(emp.last_out) : '—') + '</td>' +
          '<td class="num">' + lateBadge + '</td>' +
          '<td>' + statusBadge + '</td>' +
          '</tr>';
      }).join('');

      var logRows = logs.slice(0, 50).map(function (log) {
        var dirBadge = log.direction === 'IN' ? '<span class="badge success">GİRİŞ (IN)</span>' : '<span class="badge info">ÇIXIŞ (OUT)</span>';
        return '<tr>' +
          '<td class="mono">' + fmtDateTime(log.punch_time) + '</td>' +
          '<td>' + esc(refLabel('employees', log.employee_id)) + '</td>' +
          '<td>' + dirBadge + '</td>' +
          '<td class="sub">' + esc(log.device_id || 'TURNIKET') + '</td>' +
          '<td>' + (log.is_manual ? '<span class="badge neutral">Əl ilə</span>' : '<span class="badge success">Cihaz</span>') + '</td>' +
          '</tr>';
      }).join('');

      $('#view').innerHTML =
        '<div class="page-toolbar">' +
        '<div class="toolbar-info"><span class="badge info">Bugün: ' + esc(summary.date) + '</span></div>' +
        '<div class="toolbar-actions">' + actions + '</div></div>' +
        '<div class="stat-grid compact mb-16">' +
        '<div class="stat-card tone-teal"><span class="stat-icon">' + icon('users') + '</span><span class="stat-copy"><span class="stat-label">Cəmi İşçi</span><strong class="stat-value">' + summary.total_employees + '</strong></span></div>' +
        '<div class="stat-card tone-blue"><span class="stat-icon">' + icon('check') + '</span><span class="stat-copy"><span class="stat-label">Gələnlər</span><strong class="stat-value">' + summary.present_count + '</strong></span></div>' +
        '<div class="stat-card tone-amber"><span class="stat-icon">' + icon('alert') + '</span><span class="stat-copy"><span class="stat-label">Gecikənlər</span><strong class="stat-value">' + summary.late_count + '</strong></span></div>' +
        '<div class="stat-card tone-slate"><span class="stat-icon">' + icon('close') + '</span><span class="stat-copy"><span class="stat-label">Gəlməyənlər</span><strong class="stat-value">' + summary.absent_count + '</strong></span></div>' +
        '</div>' +
        '<div class="grid grid-2 gap-16">' +
        '<div class="card table-card"><header class="card-head"><h3>Bugünkü Davamiyyət Monitorinqi</h3></header>' +
        '<div class="table-wrap"><table class="data"><thead><tr><th>İşçi</th><th class="num">İlk Giriş</th><th class="num">Son Çıxış</th><th class="num">Gecikmə</th><th>Status</th></tr></thead><tbody>' + (employeeRows || '<tr><td colspan="5" class="text-center">Məlumat yoxdur</td></tr>') + '</tbody></table></div></div>' +
        '<div class="card table-card"><header class="card-head"><h3>Son Turniket Vuruşları (Punch Logs)</h3></header>' +
        '<div class="table-wrap"><table class="data"><thead><tr><th>Tarix / Vaxt</th><th>İşçi</th><th>İstiqamət</th><th>Cihaz</th><th>Mənbə</th></tr></thead><tbody>' + (logRows || '<tr><td colspan="5" class="text-center">Loq tapılmadı</td></tr>') + '</tbody></table></div></div>' +
        '</div>';

    } catch (err) { toast(err.message, 'error'); }
  }

  async function renderWorkSchedules() {
    setHeader('İş Qrafikləri və Növbəlilik İdarəsi', 'Növbəli iş rejimləri (2 növbəli, 3 növbəli, 12 və 24 saatlıq), rotasiya və təyinatlar');
    $('#view').innerHTML = loadingHTML('İş qrafikləri yüklənir...');
    await ensureLookups(['organizations', 'employees']);

    try {
      var schedules = await api('/work-schedules/overview');
      var canManageSchedules = canManage('work-schedules') || isHrWriter();

      var shiftCount = schedules.filter(function (s) { return s.schedule_type.indexOf('SHIFT_') === 0; }).length;
      var standardCount = schedules.length - shiftCount;
      var totalAssigned = schedules.reduce(function (sum, s) { return sum + (s.assigned_count || 0); }, 0);

      var scheduleCards = schedules.map(function (s) {
        var typeLabels = {
          SHIFT_3: '3 Növbəli (8 saat)',
          SHIFT_12: '12 Saatlıq Növbə',
          SHIFT_24: '24 Saatlıq Sutkalıq',
          SHIFT_2: '2 Növbəli',
          STANDARD_5: 'Standart 5 Günlük',
          STANDARD_6: 'Standart 6 Günlük',
          CUSTOM: 'Fərdi Qrafik'
        };
        var typeTones = {
          SHIFT_3: 'info',
          SHIFT_12: 'warning',
          SHIFT_24: 'danger',
          SHIFT_2: 'info',
          STANDARD_5: 'success',
          STANDARD_6: 'success',
          CUSTOM: 'neutral'
        };
        var typeLabel = typeLabels[s.schedule_type] || s.schedule_type;
        var tone = typeTones[s.schedule_type] || 'neutral';

        var shiftsHtml = (s.shifts || []).map(function (sh) {
          var nightBadge = sh.night_hours ? ' <span class="badge warning" style="font-size:10px;padding:1px 5px">Gecə: ' + sh.night_hours + 's</span>' : '';
          var breakInfo = sh.break_minutes ? ' (' + sh.break_minutes + ' dəq fasilə)' : '';
          return '<div class="shift-chip">' +
            '<span class="shift-chip-name">' + esc(sh.name) + breakInfo + '</span>' +
            '<div style="display:flex;align-items:center;gap:6px">' +
            nightBadge +
            '<span class="shift-chip-hours">' + esc(sh.start) + ' - ' + esc(sh.end) + '</span>' +
            '</div></div>';
        }).join('');

        if (!shiftsHtml) {
          shiftsHtml = '<div class="sub">Standart qrafik qaydaları tətbiq olunur</div>';
        }

        var actions = '';
        if (canManageSchedules) {
          actions += '<button class="btn sm primary" type="button" data-act="work-schedule-assign" data-id="' + s.id + '" data-name="' + esc(s.name) + '">' + icon('users') + 'İşçiləri Təyin Et</button>';
          actions += '<button class="btn sm ghost" type="button" data-act="work-schedule-edit" data-id="' + s.id + '">' + icon('edit') + 'Düzəliş</button>';
          if (!s.is_default) {
            actions += '<button class="btn sm ghost danger" type="button" data-act="work-schedule-delete" data-id="' + s.id + '" title="Qrafiki sil">' + icon('trash') + '</button>';
          }
        }

        return '<div class="schedule-card">' +
          '<div class="schedule-card-head">' +
            '<div>' +
              '<div class="schedule-card-title">' + esc(s.name) + '</div>' +
              '<div class="schedule-card-badges">' +
                badge(typeLabel, tone) +
                (s.is_default ? '<span class="badge success">★ Əsas Qrafik</span>' : '') +
                '<span class="badge neutral">⏱ ' + s.weekly_hours + ' saat/həftə</span>' +
              '</div>' +
            '</div>' +
          '</div>' +
          '<div class="schedule-card-body">' +
            (s.rotation_pattern ? '<div style="font-size:12px;color:var(--text-soft)"><strong>Rotasiya:</strong> ' + esc(s.rotation_pattern) + '</div>' : '') +
            '<div class="shift-chips-list">' + shiftsHtml + '</div>' +
            '<div class="sub" style="margin-top:6px">👥 <strong>' + s.assigned_count + '</strong> işçi təyin edilib</div>' +
          '</div>' +
          '<div class="schedule-card-foot">' + actions + '</div>' +
        '</div>';
      }).join('');

      var toolbarActions = '';
      if (canManageSchedules) {
        toolbarActions += '<button class="btn ghost" type="button" data-act="work-schedule-preset">' + icon('sync') + '⚡ Şablonlardan Seç</button>';
        toolbarActions += '<button class="btn primary" type="button" data-act="work-schedule-new">' + icon('plus') + 'Yeni İş Qrafiki</button>';
      }

      $('#view').innerHTML =
        '<div class="page-toolbar">' +
          '<div class="toolbar-info"><span class="badge info">Cəmi: ' + schedules.length + ' iş qrafiki</span></div>' +
          '<div class="toolbar-actions">' + toolbarActions + '</div>' +
        '</div>' +
        '<div class="stat-grid compact mb-16">' +
          '<div class="stat-card tone-teal"><span class="stat-icon">' + icon('calendar-grid') + '</span><span class="stat-copy"><span class="stat-label">Cəmi Qrafik</span><strong class="stat-value">' + schedules.length + '</strong></span></div>' +
          '<div class="stat-card tone-blue"><span class="stat-icon">' + icon('clock') + '</span><span class="stat-copy"><span class="stat-label">Növbəli Rejimlər</span><strong class="stat-value">' + shiftCount + '</strong></span></div>' +
          '<div class="stat-card tone-slate"><span class="stat-icon">' + icon('grid') + '</span><span class="stat-copy"><span class="stat-label">Standart Qrafiklər</span><strong class="stat-value">' + standardCount + '</strong></span></div>' +
          '<div class="stat-card tone-violet"><span class="stat-icon">' + icon('users') + '</span><span class="stat-copy"><span class="stat-label">Qrafikdəki İşçilər</span><strong class="stat-value">' + totalAssigned + '</strong></span></div>' +
        '</div>' +
        '<div class="schedule-cards-grid">' +
          (scheduleCards || emptyState('İş qrafiki tapılmadı', 'Yuxarıdakı düymələrlə yeni qrafik yarada və ya standart şablonlardan əlavə edə bilərsiniz.')) +
        '</div>';
    } catch (err) {
      toast(err.message, 'error');
    }
  }

  async function openWorkScheduleModal(id) {
    await ensureLookups(['organizations']);
    var schedule = null;
    if (id) {
      schedule = await api('/work-schedules/' + id);
    }
    var rules = (schedule && schedule.shift_rules_json) || {};
    var shifts = rules.shifts || [
      { name: '1-ci Növbə', start: '08:00', end: '16:00', break_minutes: 60, night_hours: 0 }
    ];

    var orgs = state.lookups.organizations || [];
    var orgOptions = orgs.map(function (o) {
      var sel = schedule ? equals(schedule.organization_id, o.id) : (state.user && equals(state.user.organization_id, o.id));
      return '<option value="' + o.id + '"' + (sel ? ' selected' : '') + '>' + esc(o.name) + '</option>';
    }).join('');

    var types = [
      { value: 'SHIFT_3', label: '3 Növbəli Fasiləsiz İstehsalat (8 saatlıq)' },
      { value: 'SHIFT_12', label: '12 Saatlıq Növbə (Gündüz / Gecə)' },
      { value: 'SHIFT_24', label: '24 Saatlıq Sutkalıq Növbə (1 gün iş / 3 gün ev)' },
      { value: 'SHIFT_2', label: '2 Növbəli İstehsalat / Satış (Səhər / Axşam)' },
      { value: 'STANDARD_5', label: 'Standart 5 Günlük İş Həftəsi (40 saat)' },
      { value: 'STANDARD_6', label: 'Standart 6 Günlük İş Həftəsi (40 saat)' },
      { value: 'CUSTOM', label: 'Xüsusi / Fərdi Qrafik' }
    ];

    var typeOptions = types.map(function (t) {
      var sel = schedule && schedule.schedule_type === t.value;
      return '<option value="' + t.value + '"' + (sel ? ' selected' : '') + '>' + esc(t.label) + '</option>';
    }).join('');

    function renderShiftRows(shiftsList) {
      return shiftsList.map(function (sh, idx) {
        return '<tr data-shift-row="' + idx + '">' +
          '<td><input type="text" class="shift-inp-name" value="' + esc(sh.name || '') + '" placeholder="Növbə adı" required></td>' +
          '<td><input type="time" class="shift-inp-start" value="' + esc(sh.start || '08:00') + '" required></td>' +
          '<td><input type="time" class="shift-inp-end" value="' + esc(sh.end || '16:00') + '" required></td>' +
          '<td><input type="number" class="shift-inp-break" value="' + (sh.break_minutes != null ? sh.break_minutes : 60) + '" min="0" max="300" style="width:70px"></td>' +
          '<td><input type="number" class="shift-inp-night" value="' + (sh.night_hours != null ? sh.night_hours : 0) + '" min="0" max="24" step="0.5" style="width:70px"></td>' +
          '<td><button type="button" class="btn sm ghost danger shift-btn-del" title="Sil">×</button></td>' +
          '</tr>';
      }).join('');
    }

    openModal({
      title: schedule ? 'İş Qrafikini Redaktə Et' : 'Yeni İş Qrafiki',
      subtitle: 'Növbə saatları, fasilələr və rotasiya qaydaları',
      size: 'large',
      body: '<form id="work-schedule-form" class="form-grid">' +
        '<label class="field span-2"><span>Təşkilat <span class="req">*</span></span><select name="organization_id" required>' + orgOptions + '</select></label>' +
        '<label class="field span-2"><span>Qrafikin Adı <span class="req">*</span></span><input type="text" name="name" value="' + esc(schedule ? schedule.name : '') + '" placeholder="məs: 3 Növbəli İstehsalat Qrafiki" required></label>' +
        '<label class="field"><span>Qrafik Tipi <span class="req">*</span></span><select name="schedule_type">' + typeOptions + '</select></label>' +
        '<label class="field"><span>Həftəlik Norma Saatı <span class="req">*</span></span><input type="number" name="weekly_hours" value="' + (schedule ? schedule.weekly_hours : 40) + '" step="0.5" min="1" max="168" required></label>' +
        '<label class="field span-2"><span>Rotasiya Qaydası / Təsviri</span><input type="text" name="rotation_pattern" value="' + esc(rules.rotation_pattern || '') + '" placeholder="məs: Həftəlik rotasiya (Səhər -> Axşam -> Gecə -> İstirahət)"></label>' +
        '<div class="field span-2 check"><input type="checkbox" name="is_default"' + (schedule && schedule.is_default ? ' checked' : '') + '><span>Təşkilat üzrə əsas (default) qrafik kimi təyin edilsin</span></div>' +
        '<div class="span-2" style="margin-top:10px">' +
          '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">' +
            '<strong>Növbələr və İş Saatları</strong>' +
            '<button type="button" class="btn sm ghost" id="btn-add-shift">' + icon('plus') + 'Növbə Əlavə Et</button>' +
          '</div>' +
          '<div class="table-wrap"><table class="dynamic-shifts-table"><thead><tr><th>Növbə Adı</th><th>Başlama</th><th>Bitmə</th><th>Fasilə (dəq)</th><th>Gecə Saatı</th><th></th></tr></thead>' +
          '<tbody id="shifts-tbody">' + renderShiftRows(shifts) + '</tbody></table></div>' +
        '</div>' +
        '</form>',
      footer: '<button class="btn ghost" type="button" data-act="modal-close">İmtina</button>' +
        '<button class="btn primary" type="submit" form="work-schedule-form">' + icon('check') + 'Yadda Saxla</button>'
    });

    var tbody = $('#shifts-tbody');
    $('#btn-add-shift').addEventListener('click', function () {
      var rowCount = tbody.querySelectorAll('tr').length;
      var tr = document.createElement('tr');
      tr.setAttribute('data-shift-row', rowCount);
      tr.innerHTML = '<td><input type="text" class="shift-inp-name" value="' + (rowCount + 1) + '-ci Növbə" placeholder="Növbə adı" required></td>' +
        '<td><input type="time" class="shift-inp-start" value="08:00" required></td>' +
        '<td><input type="time" class="shift-inp-end" value="16:00" required></td>' +
        '<td><input type="number" class="shift-inp-break" value="60" min="0" max="300" style="width:70px"></td>' +
        '<td><input type="number" class="shift-inp-night" value="0" min="0" max="24" step="0.5" style="width:70px"></td>' +
        '<td><button type="button" class="btn sm ghost danger shift-btn-del" title="Sil">×</button></td>';
      tbody.appendChild(tr);
    });

    tbody.addEventListener('click', function (e) {
      if (e.target.closest('.shift-btn-del')) {
        var row = e.target.closest('tr');
        if (tbody.querySelectorAll('tr').length > 1) {
          row.remove();
        } else {
          toast('Ən azı 1 növbə olmalıdır', 'error');
        }
      }
    });

    $('#work-schedule-form').addEventListener('submit', async function (e) {
      e.preventDefault();
      var form = e.target;
      var rows = tbody.querySelectorAll('tr');
      var shiftsData = [];
      rows.forEach(function (r) {
        shiftsData.push({
          name: r.querySelector('.shift-inp-name').value.trim(),
          start: r.querySelector('.shift-inp-start').value,
          end: r.querySelector('.shift-inp-end').value,
          break_minutes: Number(r.querySelector('.shift-inp-break').value) || 0,
          night_hours: Number(r.querySelector('.shift-inp-night').value) || 0
        });
      });

      var payload = {
        organization_id: Number(form.elements.organization_id.value),
        name: form.elements.name.value.trim(),
        schedule_type: form.elements.schedule_type.value,
        weekly_hours: Number(form.elements.weekly_hours.value),
        is_default: form.elements.is_default.checked,
        shift_rules_json: {
          shifts: shiftsData,
          rotation_pattern: form.elements.rotation_pattern.value.trim(),
          night_bonus_pct: 0.20
        }
      };

      try {
        if (schedule) {
          await api('/work-schedules/' + schedule.id, { method: 'PUT', body: payload });
          toast('İş qrafiki yeniləndi', 'success');
        } else {
          await api('/work-schedules', { method: 'POST', body: payload });
          toast('Yeni iş qrafiki yaradıldı', 'success');
        }
        closeModal();
        await renderWorkSchedules();
      } catch (err) {
        toast(err.message, 'error');
      }
    });
  }

  async function openSchedulePresetsModal() {
    try {
      var presets = await api('/work-schedules/presets');
      var cardsHtml = presets.map(function (p) {
        var shiftsHtml = (p.shift_rules_json.shifts || []).map(function (s) {
          return '<div style="font-size:11px;color:var(--text-soft)">• ' + esc(s.name) + ': <strong class="mono">' + esc(s.start) + ' - ' + esc(s.end) + '</strong>' + (s.night_hours ? ' (Gecə: ' + s.night_hours + 's)' : '') + '</div>';
        }).join('');

        return '<div class="preset-card">' +
          '<div>' +
            '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">' +
              '<h4>' + esc(p.name) + '</h4>' +
              '<span class="badge info font-xs">' + p.schedule_type + '</span>' +
            '</div>' +
            '<p style="margin-bottom:8px">' + esc(p.description) + '</p>' +
            '<div style="font-size:11.5px;color:var(--muted);margin-bottom:6px"><strong>Rotasiya:</strong> ' + esc(p.rotation_pattern) + '</div>' +
            '<div style="background:var(--surface-2);border-radius:8px;padding:8px;margin-top:6px">' + shiftsHtml + '</div>' +
          '</div>' +
          '<div style="margin-top:12px">' +
            '<button class="btn sm primary w-full btn-apply-preset" type="button" data-preset="' + esc(p.key) + '">' + icon('plus') + 'Bu Şablonu Tətbiq Et</button>' +
          '</div>' +
        '</div>';
      }).join('');

      openModal({
        title: 'Standart İş Qrafiki Şablonları',
        subtitle: 'AR Əmək Məcəlləsinə tam uyğunlaşdırılmış 2-növbəli, 3-növbəli, 12 və 24 saatlıq şablonlar',
        size: 'large',
        body: '<div class="preset-grid">' + cardsHtml + '</div>',
        footer: '<button class="btn ghost" type="button" data-act="modal-close">Bağla</button>'
      });

      document.querySelectorAll('.btn-apply-preset').forEach(function (btn) {
        btn.addEventListener('click', async function () {
          var pkey = btn.getAttribute('data-preset');
          var selectedPreset = presets.find(function (p) { return p.key === pkey; });
          if (!selectedPreset) return;

          try {
            var orgId = state.user && state.user.organization_id ? state.user.organization_id : 1;
            var payload = {
              organization_id: orgId,
              name: selectedPreset.name,
              schedule_type: selectedPreset.schedule_type,
              weekly_hours: selectedPreset.weekly_hours,
              is_default: false,
              shift_rules_json: selectedPreset.shift_rules_json
            };
            await api('/work-schedules', { method: 'POST', body: payload });
            closeModal();
            toast('Şablon əsasında iş qrafiki yaradıldı: ' + selectedPreset.name, 'success');
            await renderWorkSchedules();
          } catch (err) {
            toast(err.message, 'error');
          }
        });
      });
    } catch (err) {
      toast(err.message, 'error');
    }
  }

  async function openScheduleAssignmentModal(scheduleId, scheduleName) {
    await ensureLookups(['employees']);
    var allEmployees = state.lookups.employees || [];

    async function loadAndRender() {
      var assignments = await api('/work-schedules/' + scheduleId + '/assignments');
      var assignedEmpIds = assignments.map(function (a) { return a.employee_id; });

      var rows = assignments.map(function (a) {
        return '<tr>' +
          '<td><strong>' + esc(a.full_name) + '</strong><div class="sub">FIN: ' + esc(a.pin_code) + '</div></td>' +
          '<td class="mono">' + esc(a.effective_from) + '</td>' +
          '<td class="mono">' + esc(a.effective_to || 'Davam edir') + '</td>' +
          '<td><button type="button" class="btn sm ghost danger btn-remove-assign" data-assign-id="' + a.id + '">Sil</button></td>' +
          '</tr>';
      }).join('');

      var unassignedEmps = allEmployees.filter(function (e) {
        return assignedEmpIds.indexOf(e.id) === -1;
      });

      var empOptions = unassignedEmps.map(function (e) {
        return '<option value="' + e.id + '">' + esc([e.last_name, e.first_name].filter(Boolean).join(' ')) + ' (FIN: ' + esc(e.pin_code || '') + ')</option>';
      }).join('');

      var modalHtml =
        '<div style="margin-bottom:16px">' +
          '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">' +
            '<strong>Cari Təyin Edilmiş İşçilər (' + assignments.length + ')</strong>' +
          '</div>' +
          '<div class="table-wrap"><table class="data"><thead><tr><th>İşçi</th><th>Başlama Tarixi</th><th>Bitmə Tarixi</th><th></th></tr></thead>' +
          '<tbody>' + (rows || '<tr><td colspan="4" class="text-center">Bu qrafikə hələ heç bir işçi təyin edilməyib</td></tr>') + '</tbody></table></div>' +
        '</div>' +
        '<form id="assign-employee-form" class="card card-pad" style="background:var(--surface-2);border:1px solid var(--line)">' +
          '<h4 style="margin:0 0 10px;font-size:13px">Qrafikə Yeni İşçi Təyin Et</h4>' +
          '<div class="form-grid">' +
            '<label class="field span-2"><span>İşçi Seçin <span class="req">*</span></span><select name="employee_id" required>' +
              '<option value="">— İşçi seçin —</option>' + empOptions +
            '</select></label>' +
            '<label class="field"><span>Qüvvəyə Minmə Tarixi <span class="req">*</span></span><input type="date" name="effective_from" value="' + localToday() + '" required></label>' +
            '<label class="field"><span>Bitmə Tarixi (istəyə görə)</span><input type="date" name="effective_to"></label>' +
          '</div>' +
          '<div style="margin-top:12px;display:flex;justify-content:flex-end">' +
            '<button type="submit" class="btn primary">' + icon('check') + 'Qrafikə Təyin Et</button>' +
          '</div>' +
        '</form>';

      openModal({
        title: 'İşçilərin Qrafikə Təyini',
        subtitle: esc(scheduleName),
        size: 'large',
        body: modalHtml,
        footer: '<button class="btn ghost" type="button" data-act="modal-close">Bağla</button>'
      });

      document.querySelectorAll('.btn-remove-assign').forEach(function (btn) {
        btn.addEventListener('click', async function () {
          var assignId = btn.getAttribute('data-assign-id');
          if (!window.confirm('İşçinin bu qrafikdən təyinatı silinsin?')) return;
          try {
            await api('/work-schedules/' + scheduleId + '/assignments/' + assignId, { method: 'DELETE' });
            toast('Təyinat silindi', 'success');
            await loadAndRender();
            await renderWorkSchedules();
          } catch (err) {
            toast(err.message, 'error');
          }
        });
      });

      var form = $('#assign-employee-form');
      if (form) {
        form.addEventListener('submit', async function (e) {
          e.preventDefault();
          var empId = Number(form.elements.employee_id.value);
          if (!empId) {
            toast('Zəhmət olmasa işçi seçin', 'error');
            return;
          }
          var payload = {
            employee_ids: [empId],
            effective_from: form.elements.effective_from.value,
            effective_to: form.elements.effective_to.value || null
          };
          try {
            await api('/work-schedules/' + scheduleId + '/assign', { method: 'POST', body: payload });
            toast('İşçi qrafikə uğurla təyin edildi', 'success');
            await loadAndRender();
            await renderWorkSchedules();
          } catch (err) {
            toast(err.message, 'error');
          }
        });
      }
    }

    try {
      await loadAndRender();
    } catch (err) {
      toast(err.message, 'error');
    }
  }

  async function openTimesheetGenerate() {
    await ensureLookups(['organizations']);
    var orgs = state.lookups.organizations || [];
    var orgOptions = orgs.map(function (org) {
      var selected = state.user && equals(state.user.organization_id, org.id);
      return '<option value="' + org.id + '"' + (selected ? ' selected' : '') + '>' + esc(org.name) + '</option>';
    }).join('');
    var monthOptions = MONTHS.map(function (name, index) {
      return '<option value="' + (index + 1) + '"' + (Number(state.timesheetMonth) === index + 1 ? ' selected' : '') + '>' + esc(name) + '</option>';
    }).join('');
    openModal({
      title: 'Tabel yarat',
      subtitle: 'Bütün aktiv müqavilələr üzrə aylıq tabel',
      body: '<form id="timesheet-generate-form" class="form-grid">' +
        '<label class="field span-2"><span>Təşkilat <span class="req">*</span></span><select name="organization_id" required>' + orgOptions + '</select></label>' +
        '<label class="field"><span>İl <span class="req">*</span></span><input type="number" name="year" value="' + state.timesheetYear + '" min="2000" max="2100" required></label>' +
        '<label class="field"><span>Ay <span class="req">*</span></span><select name="month" required>' + monthOptions + '</select></label>' +
        '</form>',
      footer: '<button class="btn ghost" type="button" data-act="modal-close">İmtina</button>' +
        '<button class="btn primary" type="submit" form="timesheet-generate-form">' + icon('check') + 'Yarat</button>'
    });
    $('#timesheet-generate-form').addEventListener('submit', async function (event) {
      event.preventDefault();
      var form = event.target;
      try {
        var result = await api('/timesheets/generate?year=' + form.elements.year.value + '&month=' + form.elements.month.value + '&organization_id=' + form.elements.organization_id.value, { method: 'POST' });
        state.timesheetYear = Number(form.elements.year.value);
        state.timesheetMonth = Number(form.elements.month.value);
        closeModal();
        toast((result.generated || 0) + ' tabel sətri yaradıldı', 'success');
        await renderTimesheets();
      } catch (err) { toast(err.message, 'error'); }
    });
  }

  async function timesheetAction(id, operation) {
    var labels = { approve: 'Tabel təsdiqlənsin?', lock: 'Tabel kilidlənsin? Kilidləndikdən sonra dəyişiklik mümkün olmayacaq.' };
    if (!window.confirm(labels[operation])) return;
    try {
      await api('/timesheets/' + id + '/' + operation, { method: 'POST' });
      toast('Tabel yeniləndi', 'success');
      await renderTimesheets();
    } catch (err) { toast(err.message, 'error'); }
  }

  async function renderApprovals() {
    setHeader('Təsdiq mərkəzi', 'Gözləyən təsdiq addımları');
    $('#view').innerHTML = loadingHTML('Təsdiqlər yüklənir...');
    var rowsData = await api('/approvals/pending');
    if (!Array.isArray(rowsData)) rowsData = normalizeList(rowsData).items;
    var canDecideApproval = canManage('approvals');
    var rows = rowsData.map(function (row) {
      return '<tr><td>' + badge(row.entity_type) + '</td><td class="mono">#' + esc(row.entity_id) + '</td>' +
        '<td class="num">' + esc(row.step_order) + '</td>' +
        '<td>' + esc(refLabel('users', row.approver_id)) + '</td>' +
        '<td>' + esc(fmtDateTime(row.created_at)) + '</td>' +
        '<td class="actions">' + (canDecideApproval ? '<button class="btn sm primary" type="button" data-act="approval-decide" data-id="' + row.id + '" data-decision="APPROVED">Təsdiqlə</button>' +
        '<button class="btn sm danger" type="button" data-act="approval-decide" data-id="' + row.id + '" data-decision="REJECTED">Rədd et</button>' : '') + '</td></tr>';
    }).join('');
    $('#view').innerHTML =
      '<div class="page-toolbar"><div class="toolbar-info"><strong>' + rowsData.length + '</strong> gözləyən təsdiq</div>' +
      '<div class="toolbar-actions"><button class="btn ghost" type="button" data-act="approvals-refresh">' + icon('refresh') + 'Yenilə</button></div></div>' +
      '<div class="card table-card">' +
      (rowsData.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>Obyekt</th><th>ID</th><th class="num">Addım</th><th>Təsdiqləyən</th><th>Yaradıldı</th><th></th></tr></thead><tbody>' + rows + '</tbody></table></div>'
        : emptyState('Gözləyən təsdiq yoxdur', 'Bütün təsdiq addımları tamamlanıb.')) +
      '</div>';
  }

  async function decideApproval(id, decision) {
    var comment = window.prompt(decision === 'APPROVED' ? 'Təsdiq qeydi (istəyə bağlı):' : 'Rədd səbəbi (istəyə bağlı):', '');
    if (comment === null) return;
    try {
      await api('/approvals/' + id + '/decide', { method: 'POST', body: { decision: decision, comment: comment || null } });
      toast(decision === 'APPROVED' ? 'Təsdiqləndi' : 'Rədd edildi', 'success');
      await renderApprovals();
    } catch (err) { toast(err.message, 'error'); }
  }

  async function renderUsers() {
    setHeader('İstifadəçilər', 'Sistemə giriş hesabları və rollar');
    $('#view').innerHTML = loadingHTML('İstifadəçilər yüklənir...');
    var results = await Promise.all([api('/auth/users'), api('/auth/roles').catch(function () { return []; })]);
    var users = results[0] || [];
    var roles = results[1] || [];
    var canManageUsers = canManage('users');
    var rows = users.map(function (user) {
      return '<tr><td><div class="user-cell"><span class="avatar sm">' + esc(initials(user.full_name || user.email)) + '</span><div><span class="strong-link">' + esc(user.full_name) + '</span><div class="sub">' + esc(user.email) + '</div></div></div></td>' +
        '<td>' + badge(user.role, 'info') + '</td>' +
        '<td>' + esc(refLabel('organizations', user.organization_id)) + '</td>' +
        '<td>' + esc(user.employee_id ? '#' + user.employee_id : '—') + '</td>' +
        '<td>' + (user.is_active ? badge('ACTIVE') : badge('INACTIVE')) + '</td>' +
        '<td>' + esc(user.last_login_at ? fmtDateTime(user.last_login_at) : '—') + '</td>' +
        '<td class="actions">' + (canManageUsers ? '<button class="btn sm ghost" type="button" data-act="user-edit" data-id="' + user.id + '">' + icon('edit') + '</button>' +
        '<button class="btn sm ghost" type="button" data-act="user-reset" data-id="' + user.id + '">Şifrə</button>' : '') + '</td></tr>';
    }).join('');
    state.roleOptions = roles;
    $('#view').innerHTML =
      '<div class="page-toolbar"><div class="toolbar-info"><strong>' + users.length + '</strong> istifadəçi</div>' +
      '<div class="toolbar-actions"><button class="btn ghost" type="button" data-act="users-refresh">' + icon('refresh') + 'Yenilə</button>' +
      (canManageUsers ? '<button class="btn primary" type="button" data-act="user-new">' + icon('plus') + 'Yeni istifadəçi</button>' : '') + '</div></div>' +
      '<div class="card table-card">' +
      (users.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>İstifadəçi</th><th>Rol</th><th>Təşkilat</th><th>İşçi</th><th>Status</th><th>Son giriş</th><th></th></tr></thead><tbody>' + rows + '</tbody></table></div>'
        : emptyState('İstifadəçi yoxdur', '')) + '</div>';
  }

  async function openUserForm(id) {
    var roles = state.roleOptions && state.roleOptions.length ? state.roleOptions : ['SUPERADMIN', 'HR_DIRECTOR', 'HR_SPECIALIST', 'ACCOUNTANT', 'DEPT_MANAGER', 'EMPLOYEE'];
    await ensureLookups(['organizations', 'employees']);
    var user = null;
    if (id) {
      var users = await api('/auth/users');
      for (var i = 0; i < users.length; i += 1) if (equals(users[i].id, id)) { user = users[i]; break; }
    }
    var roleOptions = roles.map(function (role) {
      return '<option value="' + esc(role) + '"' + (user && user.role === role ? ' selected' : '') + '>' + esc(humanize(role)) + '</option>';
    }).join('');
    var orgs = state.lookups.organizations || [];
    var orgOptions = '<option value="">— seçin —</option>' + orgs.map(function (org) {
      return '<option value="' + org.id + '"' + (user && equals(user.organization_id, org.id) ? ' selected' : '') + '>' + esc(org.name) + '</option>';
    }).join('');
    var employees = state.lookups.employees || [];
    var employeeOptions = '<option value="">— yoxdur —</option>' + employees.map(function (employee) {
      return '<option value="' + employee.id + '"' + (user && equals(user.employee_id, employee.id) ? ' selected' : '') + '>' + esc([employee.last_name, employee.first_name].filter(Boolean).join(' ') + ' · ' + (employee.pin_code || '')) + '</option>';
    }).join('');
    openModal({
      title: user ? 'İstifadəçini redaktə et' : 'Yeni istifadəçi',
      subtitle: user ? user.email : 'Sistemə giriş hesabı',
      body: '<form id="user-form" class="form-grid">' +
        (user ? '' : '<label class="field span-2"><span>E-poçt <span class="req">*</span></span><input type="email" name="email" required></label>') +
        '<label class="field span-2"><span>Ad Soyad <span class="req">*</span></span><input type="text" name="full_name" value="' + esc(user ? user.full_name : '') + '" required></label>' +
        (user ? '' : '<label class="field span-2"><span>Şifrə <span class="req">*</span></span><input type="password" name="password" minlength="6" required></label>') +
        '<label class="field"><span>Rol</span><select name="role">' + roleOptions + '</select></label>' +
        (user ? '<label class="field check"><input type="checkbox" name="is_active"' + (user.is_active ? ' checked' : '') + '><span>Aktiv</span></label>' : '') +
        '<label class="field span-2"><span>Təşkilat</span><select name="organization_id">' + orgOptions + '</select></label>' +
        '<label class="field span-2"><span>Bağlı işçi</span><select name="employee_id">' + employeeOptions + '</select></label>' +
        '</form>',
      footer: '<button class="btn ghost" type="button" data-act="modal-close">İmtina</button>' +
        '<button class="btn primary" type="submit" form="user-form">' + icon('check') + 'Yadda saxla</button>'
    });
    $('#user-form').addEventListener('submit', async function (event) {
      event.preventDefault();
      var form = event.target;
      try {
        var payload = {
          full_name: form.elements.full_name.value.trim(),
          role: form.elements.role.value,
          organization_id: form.elements.organization_id.value ? Number(form.elements.organization_id.value) : null,
          employee_id: form.elements.employee_id.value ? Number(form.elements.employee_id.value) : null
        };
        if (user) {
          payload.is_active = form.elements.is_active.checked;
          await api('/auth/users/' + user.id, { method: 'PATCH', body: payload });
        } else {
          payload.email = form.elements.email.value.trim();
          payload.password = form.elements.password.value;
          await api('/auth/users', { method: 'POST', body: payload });
        }
        closeModal();
        toast('İstifadəçi yadda saxlanıldı', 'success');
        await renderUsers();
      } catch (err) { toast(err.message, 'error'); }
    });
  }

  async function resetUserPassword(id) {
    var password = window.prompt('Yeni şifrə (minimum 6 simvol):', '');
    if (password === null) return;
    if (password.length < 6) { toast('Şifrə ən azı 6 simvol olmalıdır', 'error'); return; }
    try {
      await api('/auth/users/' + id + '/reset-password', { method: 'POST', body: { new_password: password } });
      toast('Şifrə yeniləndi', 'success');
    } catch (err) { toast(err.message, 'error'); }
  }

  async function renderAudit() {
    setHeader('Audit jurnalı', 'Sistemdə aparılan son əməliyyatlar');
    $('#view').innerHTML = loadingHTML('Jurnal yüklənir...');
    var rowsData = await api('/audit-logs?limit=300');
    if (!Array.isArray(rowsData)) rowsData = normalizeList(rowsData).items;
    await ensureLookups(['users']);
    var rows = rowsData.map(function (row) {
      var payload = '';
      if (row.old_values || row.new_values) {
        var diff = [];
        if (row.old_values) diff.push('köhnə: ' + JSON.stringify(row.old_values));
        if (row.new_values) diff.push('yeni: ' + JSON.stringify(row.new_values));
        payload = '<details class="inline-details"><summary>Detallar</summary><pre class="code-block">' + esc(diff.join('\n')) + '</pre></details>';
      }
      return '<tr><td class="nowrap">' + esc(fmtDateTime(row.created_at)) + '</td>' +
        '<td>' + esc(refLabel('users', row.user_id) || '—') + '</td>' +
        '<td>' + badge(row.action, row.action === 'DELETE' ? 'danger' : (row.action === 'CREATE' || row.action === 'INSERT' ? 'success' : 'info')) + '</td>' +
        '<td><span class="mono">' + esc(row.table_name) + '</span></td>' +
        '<td class="mono">' + esc(row.record_id === null || row.record_id === undefined ? '—' : '#' + row.record_id) + '</td>' +
        '<td>' + payload + '</td></tr>';
    }).join('');
    $('#view').innerHTML =
      '<div class="page-toolbar"><div class="toolbar-info"><strong>' + rowsData.length + '</strong> son əməliyyat</div>' +
      '<div class="toolbar-actions"><button class="btn ghost" type="button" data-act="audit-refresh">' + icon('refresh') + 'Yenilə</button></div></div>' +
      '<div class="card table-card">' +
      (rowsData.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>Vaxt</th><th>İstifadəçi</th><th>Əməliyyat</th><th>Cədvəl</th><th>Qeyd</th><th></th></tr></thead><tbody>' + rows + '</tbody></table></div>'
        : emptyState('Jurnal boşdur', 'Hələ heç bir əməliyyat qeydə alınmayıb.')) +
      '</div>';
  }

  async function renderSystemSettings() {
    setHeader('Sistem və Demo İdarəsi', 'Məlumat bazası, demo rejimi və real istehsalata keçid sazlamaları');
    if (!roleIn(['SUPERADMIN'])) {
      $('#view').innerHTML = errorCard('Bu bölmə yalnız sistem administratoru (SUPERADMIN) üçün əlçatandır.');
      return;
    }
    $('#view').innerHTML = loadingHTML('Sistem sazlamaları yüklənir...');

    try {
      await loadSystemInfo();
      var demoEnabled = state.systemInfo && state.systemInfo.demo_enabled;

      var statusNotice = demoEnabled
        ? '<div class="alert warn mb-16"><div style="font-size:13px"><strong>⚡ Demo Rejimi Aktivdir:</strong> Giriş ekranında demo hesab düymələri (Superadmin, HR, Mühasib və s.) aktivdir və sistem sınaq məlumatları ilə işləyir.</div></div>'
        : '<div class="alert info mb-16"><div style="font-size:13px"><strong>✓ Real İstehsalat Rejimi:</strong> Demo düymələr söndürülüb. İstifadəçilər yalnız öz real e-poçt və şifrələri ilə daxil ola bilər.</div></div>';

      $('#view').innerHTML =
        statusNotice +
        '<div class="grid grid-2 gap-16">' +
          '<div class="card card-pad">' +
            '<header class="card-head" style="margin-bottom:14px"><h3>Giriş Ekranı və Demo Rejimi</h3></header>' +
            '<p style="font-size:13px;color:var(--text-soft);margin-bottom:16px;line-height:1.5">' +
              'Giriş ekranında nümayiş olunan sürətli giriş çiplərini (Superadmin, HR Direktoru, Mühasib və s.) idarə edin. ' +
              'Sistem real istifadəyə verildikdə bu düymələri gizlədərək giriş ekranını tam peşəkar rejimə keçirə bilərsiniz.' +
            '</p>' +
            '<div style="background:var(--surface-2);border:1px solid var(--line);border-radius:10px;padding:14px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between">' +
              '<div><strong>Demo Giriş Düymələri</strong><div class="sub">Giriş səhifəsindəki rollar qutusu</div></div>' +
              '<span class="badge ' + (demoEnabled ? 'success' : 'neutral') + '">' + (demoEnabled ? 'GÖSTƏRİLİR' : 'GİZLƏDİLİB') + '</span>' +
            '</div>' +
            '<button class="btn ' + (demoEnabled ? 'ghost danger' : 'primary') + '" type="button" data-act="system-toggle-demo">' +
              (demoEnabled ? 'Giriş ekranında demo hesabları gizlət' : 'Giriş ekranında demo hesabları aktiv et') +
            '</button>' +
          '</div>' +
          '<div class="danger-zone-card">' +
            '<h3>' + icon('trash') + 'Demo Verilənləri Təmizləmə (Real Rejimə Keçid)</h3>' +
            '<p style="font-size:12.5px;color:#7f1d1d;line-height:1.5;margin-bottom:14px">' +
              'Bu əməliyyat sistemdəki bütün sınaq və demo qeydlərini (işçilər, əmək müqavilələri, kadr əmrləri, tabel saatları, turniket loqları və əməkhaqqı cədvəlləri) tam təmizləyir.<br><br>' +
              '<strong>Saxlanılacaq əsas məlumatlar:</strong><br>' +
              '• Şirkət rekvizitləri və strukturu (departamentlər, vəzifələr)<br>' +
              '• İstehsalat təqvimi (AR rəsmi bayram və iş günləri)<br>' +
              '• Vergi və sosial sığorta dərəcələri soraqçası<br>' +
              '• Məzuniyyət və əməkhaqqı komponentləri<br>' +
              '• Sistem Administratoru hesabı (Cari istifadəçiniz)<br><br>' +
              'Təmizləmədən sonra sistem təmiz real iş rejiminə keçəcək və demo düymələr avtomatik yığışdırılacaq.' +
            '</p>' +
            '<button class="btn danger" type="button" data-act="system-wipe-demo">' + icon('trash') + 'Demo Məlumatları Tam Sil və Real Rejimə Keç</button>' +
          '</div>' +
        '</div>';
    } catch (err) {
      toast(err.message, 'error');
    }
  }

  async function toggleDemoModeAction() {
    var currentlyEnabled = state.systemInfo && state.systemInfo.demo_enabled;
    var newStatus = !currentlyEnabled;
    try {
      await api('/system/toggle-demo-mode', {
        method: 'POST',
        body: { enabled: newStatus }
      });
      await loadSystemInfo();
      toast(newStatus ? 'Demo rejimi aktiv edildi' : 'Demo rejimi söndürüldü (Giriş ekranında gizlədildi)', 'success');
      await renderSystemSettings();
    } catch (err) {
      toast(err.message, 'error');
    }
  }

  async function confirmAndWipeDemoData() {
    openModal({
      title: '⚠️ Demo Məlumatları Təmizləmə',
      subtitle: 'Real istehsalat rejiminə keçid təsdiqi',
      body: '<div class="alert danger mb-16">' +
        '<strong>Diqqət! Bu əməliyyat geri qaytarıla bilməz!</strong><br>' +
        'Bütün sınaq işçiləri, əmək müqavilələri, kadr əmrləri, tabel qeydləri, turniket loqları və əməkhaqqı hesablamaları verilənlər bazasından həmişəlik silinəcək.' +
      '</div>' +
      '<p style="font-size:13px;line-height:1.5;margin-bottom:14px">' +
        'Təmizləmədən sonra şirkət strukturu, AR istehsalat təqvimi və Administrator hesabınız saxlanılacaq. ' +
        'Giriş ekranındakı demo düymələr söndürüləcək və sistem təmiz real iş üçün hazır olacaq.' +
      '</p>' +
      '<label class="field check" style="padding-top:8px">' +
        '<input type="checkbox" id="chk-confirm-wipe"><span>Bəli, bütün demo məlumatların silinməsini və real rejimə keçidi təsdiq edirəm</span>' +
      '</label>',
      footer: '<button class="btn ghost" type="button" data-act="modal-close">İmtina</button>' +
        '<button class="btn danger" type="button" id="btn-execute-wipe" disabled>' + icon('trash') + 'Bazasını Təmizlə və Real Rejimə Keç</button>'
    });

    var chk = $('#chk-confirm-wipe');
    var btn = $('#btn-execute-wipe');
    if (chk && btn) {
      chk.addEventListener('change', function () {
        btn.disabled = !chk.checked;
      });
      btn.addEventListener('click', async function () {
        btn.disabled = true;
        btn.textContent = 'Təmizlənir...';
        try {
          var result = await api('/system/wipe-demo-data', { method: 'POST' });
          closeModal();
          toast(result.message || 'Demo məlumatları tam təmizləndi! Sistem real rejimə keçdi.', 'success');
          await loadSystemInfo();
          await loadMeta();
          location.hash = '#/s/dashboard';
        } catch (err) {
          toast(err.message, 'error');
          btn.disabled = false;
          btn.textContent = 'Bazasını Təmizlə və Real Rejimə Keç';
        }
      });
    }
  }

  async function openUserProfileDialog() {
    var user = state.user || {};
    var isSuper = user.role === 'SUPERADMIN';
    openModal({
      title: 'İstifadəçi Profili',
      subtitle: esc(user.email || ''),
      body: '<div class="profile-head card card-pad" style="margin-bottom:14px">' +
        '<div class="avatar" style="width:48px;height:48px;font-size:18px">' + esc(initials(user.full_name || user.email)) + '</div>' +
        '<div style="flex:1">' +
          '<h3 style="margin:0 0 4px">' + esc(user.full_name || 'İstifadəçi') + '</h3>' +
          '<div style="display:flex;gap:6px">' +
            badge(user.role || 'USER', 'info') +
            (isSuper ? '<span class="badge success">Tam İnzibatçı</span>' : '') +
          '</div>' +
        '</div>' +
      '</div>' +
      '<div class="kv">' +
        '<div><span>E-poçt</span><strong>' + esc(user.email || '—') + '</strong></div>' +
        '<div><span>Rol</span><strong>' + esc(humanize(user.role)) + '</strong></div>' +
        '<div><span>Təşkilat</span><strong>' + esc(refLabel('organizations', user.organization_id)) + '</strong></div>' +
        '<div><span>Status</span><strong>' + (user.is_active ? 'Aktiv' : 'Deaktiv') + '</strong></div>' +
      '</div>' +
      (isSuper ? '<div style="margin-top:16px;background:var(--surface-2);border:1px solid var(--line);border-radius:10px;padding:12px 14px;display:flex;align-items:center;justify-content:space-between">' +
        '<div><strong>Sistem və Demo İdarəsi</strong><div class="sub">Demo rejimi və verilənlər bazası sazlamaları</div></div>' +
        '<a class="btn sm primary" href="#/s/system-settings" onclick="closeModal()">' + icon('settings') + 'İdarə Et</a>' +
      '</div>' : ''),
      footer: '<button class="btn ghost" type="button" data-act="modal-close">Bağla</button>'
    });
  }

  function ensureCompliancePeriod() {
    if (state.complianceYear) return;
    var now = new Date();
    var month = now.getMonth() + 1;
    var year = now.getFullYear();
    if (month === 1) { year -= 1; month = 12; } else { month -= 1; }
    state.complianceYear = year;
    state.complianceMonth = month;
  }

  async function renderCompliance() {
    ensureCompliancePeriod();
    setHeader('Dövlət hesabatları', 'Vahid bəyannamə, İSB və ƏMAS');
    $('#view').innerHTML = loadingHTML('Hesabatlar hazırlanır...');
    var year = state.complianceYear;
    var month = state.complianceMonth;
    var query = '?year=' + year + '&month=' + month;
    var results = await Promise.all([
      api('/compliance/unified-declaration' + query).catch(function (err) { return { error: err.message }; }),
      api('/compliance/isb-report' + query).catch(function (err) { return null; })
    ]);
    var declaration = results[0];
    var isb = results[1];
    var declarationRows = Array.isArray(declaration) ? declaration : [];
    var yearOptions = '';
    var nowYear = new Date().getFullYear();
    for (var y = nowYear + 1; y >= nowYear - 4; y -= 1) {
      yearOptions += '<option value="' + y + '"' + (Number(year) === y ? ' selected' : '') + '>' + y + '</option>';
    }
    var monthOptions = MONTHS.map(function (name, index) {
      return '<option value="' + (index + 1) + '"' + (Number(month) === index + 1 ? ' selected' : '') + '>' + esc(name) + '</option>';
    }).join('');
    var isbHTML = '';
    if (isb) {
      isbHTML = '<div class="stat-grid compact">' +
        '<div class="stat-card tone-blue"><span class="stat-copy"><span class="stat-label">İşçi sayı</span><strong class="stat-value">' + esc(isb.headcount) + '</strong></span></div>' +
        '<div class="stat-card tone-teal"><span class="stat-copy"><span class="stat-label">Bruto fond</span><strong class="stat-value">' + esc(fmtMoney(isb.payroll_fund_gross)) + '</strong></span></div>' +
        '<div class="stat-card tone-violet"><span class="stat-copy"><span class="stat-label">Net fond</span><strong class="stat-value">' + esc(fmtMoney(isb.payroll_fund_net)) + '</strong></span></div>' +
        '<div class="stat-card tone-amber"><span class="stat-copy"><span class="stat-label">DSMF</span><strong class="stat-value">' + esc(fmtMoney(isb.dsmf_total)) + '</strong></span></div>' +
        '<div class="stat-card tone-slate"><span class="stat-copy"><span class="stat-label">İTS</span><strong class="stat-value">' + esc(fmtMoney(isb.its_total)) + '</strong></span></div>' +
        '<div class="stat-card tone-rose"><span class="stat-copy"><span class="stat-label">İşsizlik sığortası</span><strong class="stat-value">' + esc(fmtMoney(isb.unemployment_total)) + '</strong></span></div>' +
        '</div>';
    } else {
      isbHTML = '<div class="alert warning">Bu dövr üçün İSB hesabatı mövcud deyil — əvvəlcə əməkhaqqı hesablaması aparılmalıdır.</div>';
    }
    var tableHead = '';
    var tableRows = '';
    if (declarationRows.length) {
      var keys = Object.keys(declarationRows[0]);
      tableHead = keys.map(function (key) { return '<th>' + esc(key) + '</th>'; }).join('');
      tableRows = declarationRows.map(function (row) {
        return '<tr>' + keys.map(function (key) {
          var value = row[key];
          var numeric = /Brutto|vergi|DSMF|İTS|İşsizlik|Netto/i.test(key);
          return '<td class="' + (numeric ? 'num' : '') + '">' + esc(numeric ? fmtMoney(value) : (value || '—')) + '</td>';
        }).join('') + '</tr>';
      }).join('');
    }
    $('#view').innerHTML =
      '<div class="page-toolbar"><form class="filter-row" id="compliance-filter">' +
      '<input type="number" name="year" min="2000" max="2100" value="' + year + '">' +
      '<select name="month">' + monthOptions + '</select>' +
      '<button class="btn ghost" type="submit">' + icon('refresh') + 'Göstər</button></form>' +
      '<div class="toolbar-actions">' +
      '<button class="btn ghost" type="button" data-act="compliance-military-export">' + icon('download') + 'Hərbi uçot (T-2) CSV</button>' +
      '<button class="btn ghost" type="button" data-act="compliance-export" data-year="' + year + '" data-month="' + month + '">' + icon('download') + 'Vahid bəyannamə CSV</button></div></div>' +
      '<section class="card card-pad"><div class="card-head"><div><h2>İSB göstəriciləri</h2><p class="muted">' + esc(year + '-' + pad(month)) + ' dövrü üzrə</p></div></div>' + isbHTML + '</section>' +
      '<section class="card table-card"><div class="card-head pad"><div><h2>Vahid bəyannamə sətirləri</h2><p class="muted">' + declarationRows.length + ' işçi sətri</p></div></div>' +
      (declarationRows.length ? '<div class="table-wrap"><table class="data"><thead><tr>' + tableHead + '</tr></thead><tbody>' + tableRows + '</tbody></table></div>'
        : emptyState('Bəyannamə boşdur', 'Seçilmiş dövr üçün əməkhaqqı hesablaması yoxdur.')) + '</section>';
    $('#compliance-filter').addEventListener('submit', function (event) {
      event.preventDefault();
      state.complianceYear = Number(event.target.elements.year.value);
      state.complianceMonth = Number(event.target.elements.month.value);
      renderCompliance().catch(function (err) { toast(err.message, 'error'); });
    });
  }

  async function renderReports() {
    setHeader('Müddət xəbərdarlıqları', 'Bitmə tarixi yaxınlaşan sənəd və icazələr');
    $('#view').innerHTML = loadingHTML('Xəbərdarlıqlar yüklənir...');
    var days = state.reportsDays;
    var results = await Promise.all([
      api('/employees/expiring-documents?days=' + days).catch(function (err) { return { error: err.message }; }),
      api('/employees/expiring-permits?days=' + days).catch(function (err) { return { error: err.message }; })
    ]);
    var documents = Array.isArray(results[0]) ? results[0] : [];
    var permits = Array.isArray(results[1]) ? results[1] : [];
    var docError = results[0] && results[0].error;
    var permitError = results[1] && results[1].error;
    var docRows = documents.map(function (row) {
      var expiry = new Date(row.expiry_date);
      var remaining = Math.ceil((expiry.getTime() - Date.now()) / 86400000);
      return '<tr><td><a class="strong-link" href="#/s/employee/' + row.employee_id + '">' + esc(row.employee_name) + '</a><div class="sub">' + esc(row.pin_code || '') + '</div></td>' +
        '<td>' + esc(humanize(row.doc_type)) + '</td><td class="mono">' + esc(row.doc_number || '—') + '</td>' +
        '<td class="nowrap">' + esc(fmtDate(row.expiry_date)) + '</td>' +
        '<td>' + (remaining < 0 ? badge('Vaxtı keçib', 'danger') : badge(remaining + ' gün', remaining <= 14 ? 'danger' : (remaining <= 30 ? 'warning' : 'info'))) + '</td></tr>';
    }).join('');
    var permitRows = permits.map(function (row) {
      var expiry = new Date(row.expiry_date);
      var remaining = Math.ceil((expiry.getTime() - Date.now()) / 86400000);
      return '<tr><td><a class="strong-link" href="#/s/employee/' + row.employee_id + '">' + esc(row.employee_name) + '</a><div class="sub">' + esc(row.pin_code || '') + '</div></td>' +
        '<td>' + esc(humanize(row.permit_type)) + '</td><td class="mono">' + esc(row.permit_number || '—') + '</td>' +
        '<td>' + esc(row.country || '—') + '</td>' +
        '<td class="nowrap">' + esc(fmtDate(row.expiry_date)) + '</td>' +
        '<td>' + (remaining < 0 ? badge('Vaxtı keçib', 'danger') : badge(remaining + ' gün', remaining <= 14 ? 'danger' : (remaining <= 30 ? 'warning' : 'info'))) + '</td></tr>';
    }).join('');
    var daysOptions = [30, 60, 90, 180].map(function (value) {
      return '<button class="tab' + (days === value ? ' active' : '') + '" type="button" data-act="reports-days" data-days="' + value + '">' + value + ' gün</button>';
    }).join('');
    $('#view').innerHTML =
      '<div class="page-toolbar"><div class="tabs">' + daysOptions + '</div>' +
      '<div class="toolbar-actions"><button class="btn ghost" type="button" data-act="reports-refresh">' + icon('refresh') + 'Yenilə</button></div></div>' +
      '<section class="card table-card"><div class="card-head pad"><div><h2>Bitən sənədlər</h2><p class="muted">' + documents.length + ' sənəd</p></div></div>' +
      (docError ? errorCard(docError) : (documents.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>İşçi</th><th>Sənəd növü</th><th>Nömrə</th><th>Bitmə tarixi</th><th>Qalıq</th></tr></thead><tbody>' + docRows + '</tbody></table></div>'
        : emptyState('Bitən sənəd yoxdur', 'Seçilmiş müddətdə bitən sənəd tapılmadı.'))) + '</section>' +
      '<section class="card table-card"><div class="card-head pad"><div><h2>Bitən icazələr</h2><p class="muted">' + permits.length + ' icazə</p></div></div>' +
      (permitError ? errorCard(permitError) : (permits.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>İşçi</th><th>İcazə növü</th><th>Nömrə</th><th>Ölkə</th><th>Bitmə tarixi</th><th>Qalıq</th></tr></thead><tbody>' + permitRows + '</tbody></table></div>'
        : emptyState('Bitən icazə yoxdur', 'Seçilmiş müddətdə bitən icazə tapılmadı.'))) + '</section>';
  }

  async function renderStructure() {
    setHeader('Təşkilat strukturu', 'Departament ierarxiyası və ştat vakansiyaları');
    $('#view').innerHTML = loadingHTML('Struktur yüklənir...');
    await ensureLookups(['organizations', 'employees']);
    var organizationId = state.user && state.user.organization_id;
    if (!organizationId) {
      var orgs = state.lookups.organizations || [];
      organizationId = orgs.length ? orgs[0].id : null;
    }
    if (!organizationId) {
      $('#view').innerHTML = emptyState('Təşkilat tapılmadı', 'Struktur məlumatı üçün təşkilat tələb olunur.');
      return;
    }
    var query = '?organization_id=' + organizationId;
    var results = await Promise.all([
      api('/departments/tree' + query),
      api('/staffing/vacancies' + query)
    ]);
    var roots = results[0] || [];
    var staffing = results[1] || [];
    var departmentCount = 0;
    function countNodes(nodes) {
      nodes.forEach(function (node) {
        departmentCount += 1;
        countNodes(node.children || []);
      });
    }
    countNodes(roots);
    var approved = staffing.reduce(function (sum, row) { return sum + (Number(row.approved_headcount) || 0); }, 0);
    var filled = staffing.reduce(function (sum, row) { return sum + (Number(row.filled_headcount) || 0); }, 0);
    var vacant = staffing.reduce(function (sum, row) { return sum + (Number(row.vacant_headcount) || 0); }, 0);
    function nodeHTML(node) {
      return '<li><div class="org-node"><div><strong>' + esc(node.name) + '</strong>' +
        '<span class="sub">' + esc(node.code || '') + (node.head_employee_id ? ' · ' + esc(refLabel('employees', node.head_employee_id)) : '') + '</span></div>' +
        badge(node.is_active ? 'Aktiv' : 'Deaktiv', node.is_active ? 'success' : 'neutral') + '</div>' +
        ((node.children || []).length ? '<ul>' + node.children.map(nodeHTML).join('') + '</ul>' : '') +
        '</li>';
    }
    var treeHTML = roots.length
      ? '<ul class="org-tree">' + roots.map(nodeHTML).join('') + '</ul>'
      : emptyState('Departament yoxdur', 'Təşkilat üçün departament yaradın.');
    var staffingRows = staffing.map(function (row) {
      return '<tr><td>' + esc(row.department_name || '—') + '</td><td>' + esc(row.position_title || '—') + '</td>' +
        '<td class="num">' + esc(row.approved_headcount) + '</td><td class="num">' + esc(row.filled_headcount) + '</td>' +
        '<td class="num strong">' + esc(row.vacant_headcount) + '</td>' +
        '<td class="num">' + esc(fmtMoney(row.base_salary)) + '</td></tr>';
    }).join('');
    $('#view').innerHTML =
      '<div class="page-toolbar"><div class="toolbar-info"><strong>' + departmentCount + '</strong> departament · <strong>' + staffing.length + '</strong> ştat vahidi</div>' +
      '<div class="toolbar-actions">' +
      (state.entityMap.departments ? '<a class="btn ghost" href="#/entity/departments">Departamentlər</a>' : '') +
      (state.entityMap.staffing ? '<a class="btn ghost" href="#/entity/staffing">Ştat cədvəli</a>' : '') +
      (state.entityMap.vacancies ? '<a class="btn primary" href="#/entity/vacancies">' + icon('user-search') + 'Vakansiyalar</a>' : '') +
      '</div></div>' +
      '<div class="stat-grid compact">' +
      '<div class="stat-card tone-blue"><span class="stat-copy"><span class="stat-label">Departamentlər</span><strong class="stat-value">' + departmentCount + '</strong></span></div>' +
      '<div class="stat-card tone-teal"><span class="stat-copy"><span class="stat-label">Təsdiqlənmiş ştat</span><strong class="stat-value">' + fmtNumber(approved, 0) + '</strong></span></div>' +
      '<div class="stat-card tone-violet"><span class="stat-copy"><span class="stat-label">Tutulmuş</span><strong class="stat-value">' + fmtNumber(filled, 0) + '</strong></span></div>' +
      '<div class="stat-card tone-amber"><span class="stat-copy"><span class="stat-label">Vakansiya</span><strong class="stat-value">' + fmtNumber(vacant, 0) + '</strong></span></div>' +
      '</div>' +
      '<div class="dash-grid">' +
      '<section class="card card-pad"><div class="card-head"><div><h2>Departament ierarxiyası</h2><p class="muted">' + esc(refLabel('organizations', organizationId)) + '</p></div></div>' + treeHTML + '</section>' +
      '<section class="card table-card"><div class="card-head pad"><div><h2>Ştat vakansiyaları</h2><p class="muted">Aktiv ştat vahidləri üzrə</p></div></div>' +
      (staffing.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>Departament</th><th>Vəzifə</th><th class="num">Təsdiq</th><th class="num">Tutulub</th><th class="num">Vakant</th><th class="num">Baza maaş</th></tr></thead><tbody>' + staffingRows + '</tbody></table></div>'
        : emptyState('Ştat yoxdur', 'Aktiv ştat vahidi tapılmadı.')) + '</section></div>';
  }

  async function renderMss() {
    setHeader('MSS · Komandam', 'Rəhbərlik etdiyiniz departamentin işçiləri');
    if (!state.user || !state.user.employee_id) {
      $('#view').innerHTML = emptyState('Komanda əlçatan deyil', 'Bu hesab işçi profili ilə əlaqələndirilməyib. MSS yalnız departament rəhbərləri üçün işləyir.');
      return;
    }
    $('#view').innerHTML = loadingHTML('Komanda yüklənir...');
    var team;
    try {
      team = await api('/mss/team');
    } catch (err) {
      $('#view').innerHTML = errorCard(err.message);
      return;
    }
    team = team || [];
    var rows = team.map(function (member) {
      var name = member.name || ('İşçi #' + member.employee_id);
      var nameHTML = state.entityMap.employees
        ? '<a class="strong-link" href="#/s/employee/' + member.employee_id + '">' + esc(name) + '</a>'
        : '<strong>' + esc(name) + '</strong>';
      return '<tr><td>' + nameHTML + '<div class="sub mono">' + esc(member.pin_code || '') + '</div></td>' +
        '<td>' + esc(member.phone || '—') + '</td><td>' + esc(member.email || '—') + '</td></tr>';
    }).join('');
    $('#view').innerHTML =
      '<div class="page-toolbar"><div class="toolbar-info"><strong>' + team.length + '</strong> komanda üzvü</div></div>' +
      '<div class="card table-card">' +
      (team.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>İşçi</th><th>Telefon</th><th>E-poçt</th></tr></thead><tbody>' + rows + '</tbody></table></div>'
        : emptyState('Komanda yoxdur', 'Bu istifadəçinin rəhbərlik etdiyi departamentdə aktiv işçi tapılmadı.')) + '</div>';
  }

  function ensureCalendarPeriod() {
    if (state.calendarYear) return;
    var now = new Date();
    state.calendarYear = now.getFullYear();
    state.calendarMonth = now.getMonth() + 1;
  }

  async function renderProductionCalendar() {
    ensureCalendarPeriod();
    setHeader('İstehsalat təqvimi', 'İş günləri, bayramlar və iş vaxtı normaları');
    $('#view').innerHTML = loadingHTML('Təqvim yüklənir...');
    var year = state.calendarYear;
    var month = state.calendarMonth;
    var data = await api('/production-calendar/month?year=' + year + '&month=' + month);
    var days = data.days || [];
    var byDate = {};
    days.forEach(function (day) { byDate[String(day.cal_date).slice(0, 10)] = day; });
    var first = new Date(year, month - 1, 1);
    var offset = (first.getDay() + 6) % 7;
    var totalDays = new Date(year, month, 0).getDate();
    var todayISO = new Date().toISOString().slice(0, 10);
    var weekdays = ['B.e', 'Ç.a', 'Çər', 'C.a', 'Cümə', 'Şən', 'Baz'];
    var canManageCalendar = canManage('production-calendar');
    var cells = weekdays.map(function (name) { return '<div class="cal-head">' + name + '</div>'; }).join('');
    for (var blank = 0; blank < offset; blank += 1) cells += '<div class="cal-cell muted-cell"></div>';
    for (var dayNumber = 1; dayNumber <= totalDays; dayNumber += 1) {
      var iso = year + '-' + pad(month) + '-' + pad(dayNumber);
      var row = byDate[iso] || { day_type: 'WORKDAY', norm_hours_40: 8 };
      var dayClass = row.day_type === 'HOLIDAY' ? 'holiday' : (row.day_type === 'WEEKEND' || row.day_type === 'MOURNING' ? 'weekend' : (row.day_type === 'SHORT_WORKDAY' ? 'short' : ''));
      var isToday = iso === todayISO;
      var dayHTML = '<span class="cal-num">' + dayNumber + '</span>' +
        (row.day_type !== 'WORKDAY' ? '<span class="cal-tag">' + esc(humanize(row.day_type)) + '</span>' : '') +
        (row.description ? '<span class="cal-note">' + esc(row.description) + '</span>' : '');
      cells += canManageCalendar
        ? '<button type="button" class="cal-cell ' + dayClass + (isToday ? ' today' : '') + '" data-act="calendar-edit" data-date="' + iso + '">' + dayHTML + '</button>'
        : '<div class="cal-cell ' + dayClass + (isToday ? ' today' : '') + '">' + dayHTML + '</div>';
    }
    $('#view').innerHTML =
      '<div class="page-toolbar"><div class="calendar-nav">' +
      '<button class="btn ghost icon-btn" type="button" data-act="calendar-shift" data-dir="-1">' + icon('arrow-left') + '</button>' +
      '<strong>' + esc(MONTHS[month - 1] + ' ' + year) + '</strong>' +
      '<button class="btn ghost icon-btn" type="button" data-act="calendar-shift" data-dir="1">' + icon('arrow-left') + '</button>' +
      '<button class="btn ghost sm" type="button" data-act="calendar-today">Bu ay</button></div>' +
      '<div class="toolbar-actions">' + (canManageCalendar ? '<button class="btn ghost" type="button" data-act="calendar-generate" data-year="' + year + '">' + icon('calendar') + 'İli yenilə</button>' : '') + '</div></div>' +
      '<div class="stat-grid compact">' +
      '<div class="stat-card tone-teal"><span class="stat-copy"><span class="stat-label">İş günləri</span><strong class="stat-value">' + esc(data.workdays) + '</strong></span></div>' +
      '<div class="stat-card tone-blue"><span class="stat-copy"><span class="stat-label">40 saat norması</span><strong class="stat-value">' + esc(fmtNumber(data.norm_hours_40, 1)) + ' saat</strong></span></div>' +
      '<div class="stat-card tone-violet"><span class="stat-copy"><span class="stat-label">36 saat norması</span><strong class="stat-value">' + esc(fmtNumber(data.norm_hours_36, 1)) + ' saat</strong></span></div>' +
      '</div>' +
      '<div class="card card-pad"><div class="calendar-grid">' + cells + '</div>' +
      '<div class="calendar-legend"><span><i class="legend-dot work"></i>İş günü</span><span><i class="legend-dot short"></i>Qısa gün</span><span><i class="legend-dot weekend"></i>İstirahət</span><span><i class="legend-dot holiday"></i>Bayram / matəm</span></div></div>';
  }

  async function openCalendarEdit(iso) {
    var data = await api('/production-calendar/month?year=' + state.calendarYear + '&month=' + state.calendarMonth);
    var row = null;
    (data.days || []).forEach(function (day) { if (String(day.cal_date).slice(0, 10) === iso) row = day; });
    if (!row) { toast('Gün tapılmadı', 'error'); return; }
    var typeOptions = ['WORKDAY', 'SHORT_WORKDAY', 'WEEKEND', 'HOLIDAY', 'MOURNING'].map(function (type) {
      return '<option value="' + type + '"' + (row.day_type === type ? ' selected' : '') + '>' + esc(humanize(type)) + '</option>';
    }).join('');
    openModal({
      title: fmtDate(iso),
      subtitle: 'İstehsalat təqvimi günü',
      body: '<form id="calendar-edit-form" class="form-grid">' +
        '<label class="field span-2"><span>Gün növü</span><select name="day_type">' + typeOptions + '</select></label>' +
        '<label class="field"><span>40 saat norması</span><input type="number" step="0.5" name="norm_hours_40" value="' + esc(row.norm_hours_40) + '"></label>' +
        '<label class="field"><span>36 saat norması</span><input type="number" step="0.5" name="norm_hours_36" value="' + esc(row.norm_hours_36) + '"></label>' +
        '<label class="field span-2"><span>Qeyd</span><input type="text" name="description" value="' + esc(row.description || '') + '"></label>' +
        '</form>',
      footer: '<button class="btn ghost" type="button" data-act="modal-close">İmtina</button>' +
        '<button class="btn primary" type="submit" form="calendar-edit-form">' + icon('check') + 'Yadda saxla</button>'
    });
    $('#calendar-edit-form').addEventListener('submit', async function (event) {
      event.preventDefault();
      var form = event.target;
      try {
        await api('/production-calendar/' + iso, {
          method: 'PATCH',
          body: {
            day_type: form.elements.day_type.value,
            norm_hours_40: Number(form.elements.norm_hours_40.value),
            norm_hours_36: Number(form.elements.norm_hours_36.value),
            description: form.elements.description.value || null
          }
        });
        closeModal();
        toast('Təqvim günü yeniləndi', 'success');
        await renderProductionCalendar();
      } catch (err) { toast(err.message, 'error'); }
    });
  }

  async function shiftCalendar(direction) {
    var month = state.calendarMonth + Number(direction);
    var year = state.calendarYear;
    if (month < 1) { month = 12; year -= 1; }
    if (month > 12) { month = 1; year += 1; }
    state.calendarMonth = month;
    state.calendarYear = year;
    await renderProductionCalendar();
  }

  async function generateCalendarYear(year) {
    if (!window.confirm(year + ' ili üçün təqvim yenidən yaradılsın?')) return;
    try {
      var result = await api('/production-calendar/generate?year=' + year, { method: 'POST' });
      toast((result.generated_days || 0) + ' gün yaradıldı', 'success');
      await renderProductionCalendar();
    } catch (err) { toast(err.message, 'error'); }
  }

  async function renderRecruitment() {
    setHeader('İşə qəbul lövhəsi', 'Namizəd müraciətlərinin mərhələlər üzrə idarəsi');
    $('#view').innerHTML = loadingHTML('Müraciətlər yüklənir...');
    await ensureLookups(['vacancies', 'candidates']);
    var applications = normalizeList(await api('/applications?limit=500')).items;
    var stages = ['NEW', 'CALL', 'INTERVIEW', 'TASK', 'OFFER', 'HIRED', 'REJECTED'];
    var canMove = canManage('recruitment');
    var grouped = {};
    stages.forEach(function (stage) { grouped[stage] = []; });
    applications.forEach(function (application) {
      (grouped[application.stage] || grouped.NEW).push(application);
    });
    var columns = stages.map(function (stage) {
      var cards = grouped[stage].map(function (application) {
        var candidate = findLookup('candidates', application.candidate_id);
        var vacancy = findLookup('vacancies', application.vacancy_id);
        var stageIndex = stages.indexOf(application.stage);
        var actions = '<button class="btn sm ghost" type="button" data-act="application-manage" data-id="' + application.id + '">İdarə et</button>';
        if (canMove && application.stage !== 'HIRED' && application.stage !== 'REJECTED' && stageIndex >= 0 && stageIndex < stages.indexOf('OFFER')) {
          actions += '<button class="btn sm primary" type="button" data-act="application-quick-stage" data-id="' + application.id + '" data-stage="' + stages[stageIndex + 1] + '">Növbəti</button>';
        }
        if (canMove && application.stage !== 'HIRED' && application.stage !== 'REJECTED') {
          actions += '<button class="btn sm danger" type="button" data-act="application-quick-stage" data-id="' + application.id + '" data-stage="REJECTED">Rədd</button>';
        }
        return '<article class="kanban-card">' +
          '<div class="kanban-card-head"><strong>' + esc(candidate ? candidate.full_name : 'Namizəd #' + application.candidate_id) + '</strong>' +
          (application.score !== null && application.score !== undefined ? '<span class="badge info">' + esc(application.score) + '</span>' : '') + '</div>' +
          '<p class="muted">' + esc(vacancy ? vacancy.title : 'Vakansiya #' + application.vacancy_id) + '</p>' +
          '<div class="kanban-meta"><span>' + esc(fmtDate(application.applied_at)) + '</span>' +
          (application.hired_employee_id ? '<a href="#/s/employee/' + application.hired_employee_id + '">İşçi #' + application.hired_employee_id + '</a>' : '') + '</div>' +
          '<div class="kanban-actions">' + actions + '</div></article>';
      }).join('');
      return '<section class="kanban-column"><header><span>' + esc(humanize(stage)) + '</span><strong>' + grouped[stage].length + '</strong></header>' +
        '<div class="kanban-list">' + (cards || '<p class="kanban-empty">Müraciət yoxdur</p>') + '</div></section>';
    }).join('');
    var active = applications.filter(function (row) { return row.stage !== 'HIRED' && row.stage !== 'REJECTED'; }).length;
    var hired = applications.filter(function (row) { return row.stage === 'HIRED'; }).length;
    $('#view').innerHTML =
      '<div class="page-toolbar"><div class="toolbar-info"><strong>' + applications.length + '</strong> müraciət · <strong>' + active + '</strong> aktiv · <strong>' + hired + '</strong> işə qəbul</div>' +
      '<div class="toolbar-actions"><button class="btn ghost" type="button" data-act="recruitment-refresh">' + icon('refresh') + 'Yenilə</button>' +
      (canWriteEntity(state.entityMap.applications) ? '<button class="btn primary" type="button" data-act="entity-create" data-key="applications">' + icon('plus') + 'Yeni müraciət</button>' : '') +
      '</div></div>' +
      '<div class="kanban">' + columns + '</div>';
  }

  async function quickMoveApplication(id, stage) {
    try {
      await api('/applications/' + id + '/stage', { method: 'PATCH', body: { stage: stage } });
      toast('Müraciət mərhələsi yeniləndi', 'success');
      await renderRecruitment();
    } catch (err) { toast(err.message, 'error'); }
  }

  async function renderOnboarding() {
    setHeader('Onboarding idarəsi', 'İşə qəbul sonrası tapşırıqlar');
    $('#view').innerHTML = loadingHTML('Tapşırıqlar yüklənir...');
    await ensureLookups(['employees']);
    var results = await Promise.all([
      api('/onboarding-tasks?limit=500'),
      api('/offboarding-clearances?limit=500').catch(function () { return []; })
    ]);
    var tasks = normalizeList(results[0]).items;
    var clearances = normalizeList(results[1] || []).items;
    var counts = { total: tasks.length, PENDING: 0, IN_PROGRESS: 0, DONE: 0 };
    tasks.forEach(function (task) { if (counts[task.status] !== undefined) counts[task.status] += 1; });
    var offboardingCounts = { PENDING: 0, IN_PROGRESS: 0, DONE: 0 };
    clearances.forEach(function (row) { if (offboardingCounts[row.status] !== undefined) offboardingCounts[row.status] += 1; });
    var canManageOnboarding = canManage('onboarding');
    var rows = tasks.map(function (task) {
      var actions = '';
      if (canManageOnboarding && task.status === 'PENDING') actions += '<button class="btn sm primary" type="button" data-act="onboarding-status" data-id="' + task.id + '" data-status="IN_PROGRESS">Başla</button>';
      if (canManageOnboarding && task.status === 'IN_PROGRESS') actions += '<button class="btn sm primary" type="button" data-act="onboarding-status" data-id="' + task.id + '" data-status="DONE">Tamamla</button>';
      if (canManageOnboarding) actions += '<button class="btn sm ghost" type="button" data-act="onboarding-edit" data-id="' + task.id + '">' + icon('edit') + '</button>';
      return '<tr><td><a class="strong-link" href="#/s/employee/' + task.employee_id + '">' + esc(refLabel('employees', task.employee_id)) + '</a></td>' +
        '<td>' + esc(task.title) + '</td>' +
        '<td>' + badge(task.category, 'info') + '</td>' +
        '<td>' + esc(task.assignee || '—') + '</td>' +
        '<td class="nowrap">' + esc(task.due_date ? fmtDate(task.due_date) : '—') + '</td>' +
        '<td>' + badge(task.status) + '</td>' +
        '<td class="actions">' + actions + '</td></tr>';
    }).join('');
    var clearanceRows = clearances.map(function (row) {
      var actions = '';
      if (canManageOnboarding && row.status === 'PENDING') actions += '<button class="btn sm primary" type="button" data-act="offboarding-status" data-id="' + row.id + '" data-status="IN_PROGRESS">Başla</button>';
      if (canManageOnboarding && row.status !== 'DONE') actions += '<button class="btn sm ghost" type="button" data-act="offboarding-status" data-id="' + row.id + '" data-status="DONE">Tamamla</button>';
      return '<tr><td><a class="strong-link" href="#/s/employee/' + row.employee_id + '">' + esc(refLabel('employees', row.employee_id)) + '</a></td>' +
        '<td>' + esc(row.department) + '</td><td>' + esc(row.item) + '</td>' +
        '<td>' + badge(row.status) + '</td>' +
        '<td class="actions">' + actions + '</td></tr>';
    }).join('');
    $('#view').innerHTML =
      '<div class="page-toolbar"><div class="toolbar-info"><strong>' + counts.total + '</strong> tapşırıq · <strong>' + clearances.length + '</strong> offboarding bəndi</div>' +
      '<div class="toolbar-actions">' + (canManageOnboarding ? '<button class="btn ghost" type="button" data-act="onboarding-checklist">' + icon('checklist') + 'Checklist yarat</button>' +
      '<button class="btn ghost" type="button" data-act="offboarding-checklist">' + icon('logout') + 'Offboarding yarat</button>' +
      '<button class="btn primary" type="button" data-act="onboarding-new">' + icon('plus') + 'Yeni tapşırıq</button>' : '') + '</div></div>' +
      '<div class="stat-grid compact">' +
      '<div class="stat-card tone-amber"><span class="stat-copy"><span class="stat-label">Onboarding gözləyir</span><strong class="stat-value">' + counts.PENDING + '</strong></span></div>' +
      '<div class="stat-card tone-blue"><span class="stat-copy"><span class="stat-label">Onboarding icradadır</span><strong class="stat-value">' + counts.IN_PROGRESS + '</strong></span></div>' +
      '<div class="stat-card tone-teal"><span class="stat-copy"><span class="stat-label">Onboarding tamamlanıb</span><strong class="stat-value">' + counts.DONE + '</strong></span></div>' +
      '<div class="stat-card tone-rose"><span class="stat-copy"><span class="stat-label">Offboarding gözləyir</span><strong class="stat-value">' + offboardingCounts.PENDING + '</strong></span></div>' +
      '</div>' +
      '<div class="card table-card">' +
      (tasks.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>İşçi</th><th>Tapşırıq</th><th>Kateqoriya</th><th>Məsul</th><th>Son tarix</th><th>Status</th><th></th></tr></thead><tbody>' + rows + '</tbody></table></div>'
        : emptyState('Onboarding tapşırığı yoxdur', 'İşçi üçün standart checklist yaradın.')) + '</div>' +
      '<div class="card table-card">' +
      '<div class="card-head pad"><div><h2>Offboarding təmizlikləri</h2><p class="muted">Təhvil-təslim və son hesablaşma bəndləri</p></div></div>' +
      (clearances.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>İşçi</th><th>Bölmə</th><th>Bənd</th><th>Status</th><th></th></tr></thead><tbody>' + clearanceRows + '</tbody></table></div>'
        : emptyState('Offboarding bəndi yoxdur', 'Standart checklist yaratmaq üçün yuxarıdakı düymədən istifadə edin.')) + '</div>';
  }

  async function openOnboardingChecklist() {
    await ensureLookups(['employees']);
    var employees = state.lookups.employees || [];
    var options = employees.map(function (employee) {
      return '<option value="' + employee.id + '">' + esc([employee.last_name, employee.first_name].filter(Boolean).join(' ') + ' · ' + (employee.pin_code || '')) + '</option>';
    }).join('');
    openModal({
      title: 'Onboarding checklist yarat',
      subtitle: 'Standart HR / IT tapşırıqları əlavə olunacaq',
      body: '<form id="onboarding-checklist-form" class="form-grid">' +
        '<label class="field span-2"><span>İşçi <span class="req">*</span></span><select name="employee_id" required>' + options + '</select></label>' +
        '<div class="alert info span-2">Standart checklist: əmək müqaviləsi, şirkət emaili, iş yeri və texnika, mentor təyini.</div>' +
        '</form>',
      footer: '<button class="btn ghost" type="button" data-act="modal-close">İmtina</button>' +
        '<button class="btn primary" type="submit" form="onboarding-checklist-form">' + icon('check') + 'Yarat</button>'
    });
    $('#onboarding-checklist-form').addEventListener('submit', async function (event) {
      event.preventDefault();
      try {
        var result = await api('/onboarding/' + event.target.elements.employee_id.value + '/checklist', { method: 'POST', body: {} });
        closeModal();
        toast((result.length || 0) + ' tapşırıq yaradıldı', 'success');
        await renderOnboarding();
      } catch (err) { toast(err.message, 'error'); }
    });
  }

  async function openOffboardingChecklist() {
    await ensureLookups(['employees']);
    var employees = state.lookups.employees || [];
    var options = employees.map(function (employee) {
      return '<option value="' + employee.id + '">' + esc(refLabel('employees', employee.id)) + '</option>';
    }).join('');
    openModal({
      title: 'Offboarding checklist yarat',
      subtitle: 'Standart təhvil-təslim bəndləri əlavə olunacaq',
      body: '<form id="offboarding-checklist-form" class="form-grid">' +
        '<label class="field span-2"><span>İşçi <span class="req">*</span></span><select name="employee_id" required>' + options + '</select></label>' +
        '<div class="alert info span-2">Bəndlər: ərizə, müqavilənin xitamı, təhvil-təslim aktı, İT avadanlıqları, giriş kartı, maddi sərvətlər və son əməkhaqqı. Mövcud bəndlər təkrarlanmır.</div>' +
        '</form>',
      footer: '<button class="btn ghost" type="button" data-act="modal-close">İmtina</button>' +
        '<button class="btn primary" type="submit" form="offboarding-checklist-form">' + icon('check') + 'Yarat</button>'
    });
    $('#offboarding-checklist-form').addEventListener('submit', async function (event) {
      event.preventDefault();
      try {
        var result = await api('/offboarding/' + event.target.elements.employee_id.value + '/checklist', { method: 'POST', body: {} });
        closeModal();
        toast((result.length || 0) + ' offboarding bəndi yaradıldı', 'success');
        await renderOnboarding();
      } catch (err) { toast(err.message, 'error'); }
    });
  }

  async function setOffboardingStatus(id, status) {
    try {
      await api('/offboarding-clearances/' + id, { method: 'PATCH', body: { status: status } });
      toast('Status yeniləndi', 'success');
      await renderOnboarding();
    } catch (err) { toast(err.message, 'error'); }
  }

  async function openOnboardingTaskForm(id) {
    await ensureLookups(['employees']);
    var task = id ? await api('/onboarding-tasks/' + id) : null;
    var employees = state.lookups.employees || [];
    var employeeOptions = employees.map(function (employee) {
      return '<option value="' + employee.id + '"' + (task && equals(task.employee_id, employee.id) ? ' selected' : '') + '>' +
        esc([employee.last_name, employee.first_name].filter(Boolean).join(' ') + ' · ' + (employee.pin_code || '')) + '</option>';
    }).join('');
    var categories = ['HR', 'IT', 'TRAINING', 'SECURITY', 'OTHER'];
    var categoryOptions = categories.map(function (category) {
      return '<option value="' + category + '"' + (task && task.category === category ? ' selected' : '') + '>' + esc(humanize(category)) + '</option>';
    }).join('');
    var statuses = ['PENDING', 'IN_PROGRESS', 'DONE'];
    var statusOptions = statuses.map(function (status) {
      return '<option value="' + status + '"' + (task && task.status === status ? ' selected' : '') + '>' + esc(humanize(status)) + '</option>';
    }).join('');
    openModal({
      title: task ? 'Tapşırığı redaktə et' : 'Yeni onboarding tapşırığı',
      subtitle: task ? ('#' + task.id) : '',
      body: '<form id="onboarding-task-form" class="form-grid">' +
        '<label class="field span-2"><span>İşçi <span class="req">*</span></span><select name="employee_id" required>' + employeeOptions + '</select></label>' +
        '<label class="field span-2"><span>Tapşırıq <span class="req">*</span></span><input type="text" name="title" value="' + esc(task ? task.title : '') + '" required></label>' +
        '<label class="field"><span>Kateqoriya</span><select name="category">' + categoryOptions + '</select></label>' +
        '<label class="field"><span>Status</span><select name="status">' + statusOptions + '</select></label>' +
        '<label class="field"><span>Məsul şəxs</span><input type="text" name="assignee" value="' + esc(task ? (task.assignee || '') : '') + '"></label>' +
        '<label class="field"><span>Son tarix</span><input type="date" name="due_date" value="' + esc(task && task.due_date ? String(task.due_date).slice(0, 10) : '') + '"></label>' +
        '<label class="field span-2"><span>Qeydlər</span><textarea name="notes" rows="2">' + esc(task ? (task.notes || '') : '') + '</textarea></label>' +
        '</form>',
      footer: '<button class="btn ghost" type="button" data-act="modal-close">İmtina</button>' +
        '<button class="btn primary" type="submit" form="onboarding-task-form">' + icon('check') + 'Yadda saxla</button>'
    });
    $('#onboarding-task-form').addEventListener('submit', async function (event) {
      event.preventDefault();
      var form = event.target;
      try {
        var payload = {
          employee_id: Number(form.elements.employee_id.value),
          title: form.elements.title.value.trim(),
          category: form.elements.category.value,
          status: form.elements.status.value,
          assignee: form.elements.assignee.value || null,
          due_date: form.elements.due_date.value || null,
          notes: form.elements.notes.value || null
        };
        await api('/onboarding-tasks' + (task ? '/' + task.id : ''), { method: task ? 'PATCH' : 'POST', body: payload });
        closeModal();
        toast('Tapşırıq yadda saxlanıldı', 'success');
        await renderOnboarding();
      } catch (err) { toast(err.message, 'error'); }
    });
  }

  async function setOnboardingStatus(id, status) {
    try {
      await api('/onboarding-tasks/' + id, { method: 'PATCH', body: { status: status } });
      toast('Status yeniləndi', 'success');
      await renderOnboarding();
    } catch (err) { toast(err.message, 'error'); }
  }

  async function renderEss() {
    setHeader('ESS · Şəxsi kabinet', 'İşçi self-service məlumatları');
    if (!state.user || !state.user.employee_id) {
      $('#view').innerHTML = '<div class="card card-pad"><div class="empty-state"><div class="empty-icon">' + icon('user') + '</div>' +
        '<strong>Şəxsi kabinet əlçatan deyil</strong><p>Bu hesab işçi profili ilə əlaqələndirilməyib.</p>' +
        '<p class="hint">ESS yalnız işçi profili ilə əlaqələndirilmiş istifadəçilər üçün işləyir. Admin hesabı ilə daxil olmusunuzsa, işçi hesabı ilə yoxlayın.</p></div></div>';
      return;
    }
    $('#view').innerHTML = loadingHTML('Şəxsi kabinet yüklənir...');
    var me;
    try {
      me = await api('/ess/me');
    } catch (err) {
      $('#view').innerHTML = '<div class="card card-pad"><div class="empty-state"><div class="empty-icon">' + icon('user') + '</div>' +
        '<strong>Şəxsi kabinet əlçatan deyil</strong><p>' + esc(err.message) + '</p>' +
        '<p class="hint">ESS yalnız işçi profili ilə əlaqələndirilmiş istifadəçilər üçün işləyir. Admin hesabı ilə daxil olmusunuzsa, işçi hesabı ilə yoxlayın.</p></div></div>';
      return;
    }
    var results = await Promise.all([
      api('/ess/payslips').catch(function () { return []; }),
      api('/ess/leave-requests').catch(function () { return []; }),
      api('/ess/timesheets').catch(function () { return []; })
    ]);
    var payslips = results[0] || [];
    var leaves = results[1] || [];
    var timesheets = results[2] || [];
    var employee = me.employee || {};
    var contract = me.contract;
    var balances = me.leave_balances || [];
    var name = [employee.last_name, employee.first_name, employee.father_name].filter(Boolean).join(' ');
    var payslipRows = payslips.map(function (item) {
      return '<tr><td>' + esc(item.period) + '</td><td>' + badge(item.run_status) + '</td>' +
        '<td class="num">' + esc(fmtMoney(item.gross_total)) + '</td>' +
        '<td class="num">' + esc(fmtMoney(item.net_payable)) + '</td>' +
        '<td class="actions"><button class="btn sm ghost" type="button" data-act="ess-payslip" data-id="' + item.id + '">PDF</button></td></tr>';
    }).join('');
    var leaveRows = leaves.map(function (row) {
      return '<tr><td>' + esc(fmtDate(row.start_date)) + ' — ' + esc(fmtDate(row.end_date)) + '</td>' +
        '<td class="num">' + esc(row.calendar_days) + '</td>' +
        '<td>' + badge(row.status) + '</td>' +
        '<td class="actions">' + (row.status === 'PENDING' || row.status === 'APPROVED' ? '<button class="btn sm ghost" type="button" data-act="ess-cancel-leave" data-id="' + row.id + '">Ləğv et</button>' : '') + '</td></tr>';
    }).join('');
    var timesheetRows = timesheets.map(function (row) {
      return '<tr><td>' + esc(row.year) + '-' + pad(row.month) + '</td><td class="num">' + esc(row.worked_days) + '</td>' +
        '<td class="num">' + esc(fmtNumber(row.regular_hours, 1)) + '</td><td class="num">' + esc(fmtNumber(row.overtime_hours, 1)) + '</td>' +
        '<td>' + badge(row.status) + '</td></tr>';
    }).join('');
    var balanceCards = balances.length ? balances.map(function (balance) {
      return '<div class="balance-card"><span class="balance-period">' + esc(fmtDate(balance.work_year_start)) + ' — ' + esc(fmtDate(balance.work_year_end)) + '</span>' +
        '<strong>' + esc(fmtNumber(balance.remaining_days, 1)) + ' gün</strong>' +
        '<span class="hint">' + esc(fmtNumber(balance.used_days, 1)) + ' / ' + esc(fmtNumber((Number(balance.entitled_base_days) || 0) + (Number(balance.entitled_extra_days) || 0), 1)) + ' istifadə</span></div>';
    }).join('') : '<p class="hint">Məzuniyyət balansı yoxdur</p>';
    var contractHTML = contract
      ? '<dl class="mini-dl"><div><dt>Müqavilə №</dt><dd>' + esc(contract.contract_number || '—') + '</dd></div>' +
        '<div><dt>Növ</dt><dd>' + esc(humanize(contract.contract_type)) + '</dd></div>' +
        '<div><dt>Brutto əməkhaqqı</dt><dd>' + esc(fmtMoney(contract.gross_salary)) + '</dd></div>' +
        '<div><dt>Başlama</dt><dd>' + esc(fmtDate(contract.start_date)) + '</dd></div>' +
        '<div><dt>Status</dt><dd>' + badge(contract.status) + '</dd></div></dl>'
      : '<p class="hint">Aktiv müqavilə tapılmadı</p>';
    $('#view').innerHTML =
      '<div class="profile-head card card-pad"><div class="profile-identity">' +
      '<span class="avatar xl">' + esc(initials(name)) + '</span>' +
      '<div><h2>' + esc(name) + '</h2><p class="muted">' + esc(humanize(employee.status)) + ' · FİN ' + esc(employee.pin_code || '—') + '</p></div></div>' +
      '<div class="toolbar-actions">' +
      '<button class="btn ghost" type="button" data-act="ess-reference-pdf">' + icon('download') + 'İş yerindən arayış (PDF)</button>' +
      '<button class="btn primary" type="button" data-act="ess-new-leave">' + icon('palmtree') + 'Məzuniyyət sorğusu</button></div></div>' +
      '<div class="dash-grid">' +
      '<section class="card card-pad"><div class="card-head"><div><h2>Şəxsi məlumatlar</h2></div></div>' +
      '<dl class="mini-dl"><div><dt>Doğum tarixi</dt><dd>' + esc(fmtDate(employee.birth_date)) + '</dd></div>' +
      '<div><dt>Telefon</dt><dd>' + esc(employee.phone || '—') + '</dd></div>' +
      '<div><dt>E-poçt</dt><dd>' + esc(employee.email || '—') + '</dd></div>' +
      '<div><dt>Ünvan</dt><dd>' + esc(employee.address || '—') + '</dd></div>' +
      '<div><dt>Bank / IBAN</dt><dd>' + esc(employee.bank_name || '—') + '<br><span class="mono">' + esc(employee.bank_iban || '') + '</span></dd></div></dl></section>' +
      '<section class="card card-pad"><div class="card-head"><div><h2>Əmək müqaviləsi</h2></div></div>' + contractHTML + '</section>' +
      '<section class="card card-pad span-2"><div class="card-head"><div><h2>Məzuniyyət balansı</h2><p class="muted">İş illəri üzrə qalıq günlər</p></div></div><div class="balance-grid">' + balanceCards + '</div></section>' +
      '<section class="card table-card span-2"><div class="card-head pad"><div><h2>Əməkhaqqı vərəqələri</h2></div></div>' +
      (payslips.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>Dövr</th><th>Status</th><th class="num">Bruto</th><th class="num">Net</th><th></th></tr></thead><tbody>' + payslipRows + '</tbody></table></div>'
        : emptyState('Vərəqə yoxdur', 'Hesablanmış əməkhaqqı vərəqəsi yoxdur.')) + '</section>' +
      '<section class="card table-card"><div class="card-head pad"><div><h2>Məzuniyyət sorğularım</h2></div></div>' +
      (leaves.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>Dövr</th><th class="num">Gün</th><th>Status</th><th></th></tr></thead><tbody>' + leaveRows + '</tbody></table></div>'
        : emptyState('Sorğu yoxdur', '')) + '</section>' +
      '<section class="card table-card"><div class="card-head pad"><div><h2>Tabel məlumatlarım</h2></div></div>' +
      (timesheets.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>Dövr</th><th class="num">İşlənmiş</th><th class="num">Normal saat</th><th class="num">Əlavə</th><th>Status</th></tr></thead><tbody>' + timesheetRows + '</tbody></table></div>'
        : emptyState('Tabel yoxdur', '')) + '</section>' +
      '</div>';
  }

  async function openEssLeaveCreate() {
    await ensureLookups(['leave-types']);
    var leaveTypes = state.lookups['leave-types'] || [];
    var options = leaveTypes.map(function (type) {
      return '<option value="' + type.id + '">' + esc(type.name) + '</option>';
    }).join('');
    openModal({
      title: 'Məzuniyyət sorğusu',
      subtitle: 'ESS vasitəsilə sorğu göndərin',
      body: '<form id="ess-leave-form" class="form-grid">' +
        '<label class="field span-2"><span>Məzuniyyət növü <span class="req">*</span></span><select name="leave_type_id" required>' + options + '</select></label>' +
        '<label class="field"><span>Başlama tarixi <span class="req">*</span></span><input type="date" name="start_date" required></label>' +
        '<label class="field"><span>Bitmə tarixi <span class="req">*</span></span><input type="date" name="end_date" required></label>' +
        '<label class="field span-2"><span>Səbəb</span><textarea name="reason" rows="2"></textarea></label>' +
        '</form>',
      footer: '<button class="btn ghost" type="button" data-act="modal-close">İmtina</button>' +
        '<button class="btn primary" type="submit" form="ess-leave-form">' + icon('check') + 'Göndər</button>'
    });
    $('#ess-leave-form').addEventListener('submit', async function (event) {
      event.preventDefault();
      var form = event.target;
      try {
        await api('/ess/leave-requests', {
          method: 'POST',
          body: {
            leave_type_id: Number(form.elements.leave_type_id.value),
            start_date: form.elements.start_date.value,
            end_date: form.elements.end_date.value,
            reason: form.elements.reason.value || null
          }
        });
        closeModal();
        toast('Sorğu göndərildi', 'success');
        await renderEss();
      } catch (err) { toast(err.message, 'error'); }
    });
  }

  async function essCancelLeave(id) {
    if (!window.confirm('Məzuniyyət sorğusu ləğv edilsin?')) return;
    try {
      await api('/ess/leave-requests/' + id + '/cancel', { method: 'POST' });
      toast('Sorğu ləğv edildi', 'success');
      await renderEss();
    } catch (err) { toast(err.message, 'error'); }
  }

  function employeeProfileHTML(profile) {
    var employee = profile.employee || {};
    var contract = profile.contract;
    var balances = profile.leave_balances || [];
    var documents = profile.documents || [];
    var family = profile.family_members || [];
    var name = [employee.last_name, employee.first_name, employee.father_name].filter(Boolean).join(' ');
    var balanceRows = balances.map(function (balance) {
      return '<tr><td>' + esc(fmtDate(balance.work_year_start)) + ' — ' + esc(fmtDate(balance.work_year_end)) + '</td>' +
        '<td class="num">' + esc(fmtNumber(balance.entitled_base_days, 1)) + '</td>' +
        '<td class="num">' + esc(fmtNumber(balance.entitled_extra_days, 1)) + '</td>' +
        '<td class="num">' + esc(fmtNumber(balance.used_days, 1)) + '</td>' +
        '<td class="num strong">' + esc(fmtNumber(balance.remaining_days, 1)) + '</td></tr>';
    }).join('');
    var documentRows = documents.map(function (document) {
      return '<tr><td>' + esc(humanize(document.doc_type)) + '</td><td class="mono">' + esc(document.doc_number || '—') + '</td>' +
        '<td>' + esc(fmtDate(document.issue_date)) + '</td><td>' + esc(fmtDate(document.expiry_date)) + '</td></tr>';
    }).join('');
    var familyRows = family.map(function (member) {
      return '<tr><td>' + esc(member.full_name) + '</td><td>' + esc(humanize(member.relation)) + '</td>' +
        '<td>' + esc(fmtDate(member.birth_date)) + '</td><td>' + (member.is_dependent ? badge('Bəli', 'success') : badge('Xeyr', 'neutral')) + '</td></tr>';
    }).join('');
    var contractHTML = contract
      ? '<dl class="mini-dl"><div><dt>Müqavilə №</dt><dd>' + esc(contract.contract_number || '—') + '</dd></div>' +
        '<div><dt>Növ</dt><dd>' + esc(humanize(contract.contract_type)) + '</dd></div>' +
        '<div><dt>Vəzifə</dt><dd>' + esc(contract.position || '—') + '</dd></div>' +
        '<div><dt>Departament</dt><dd>' + esc(contract.department || '—') + '</dd></div>' +
        '<div><dt>Brutto</dt><dd>' + esc(fmtMoney(contract.gross_salary)) + '</dd></div>' +
        '<div><dt>Başlama</dt><dd>' + esc(fmtDate(contract.start_date)) + '</dd></div>' +
        '<div><dt>Status</dt><dd>' + badge(contract.status) + '</dd></div></dl>'
      : '<p class="hint">Müqavilə məlumatı yoxdur</p>';
    return '<div class="profile-head card card-pad"><div class="profile-identity">' +
      '<span class="avatar xl">' + esc(initials(name)) + '</span>' +
      '<div><h2>' + esc(name) + '</h2><p class="muted">' + esc(employee.pin_code || '') + ' · ' + esc(humanize(employee.status)) + '</p></div></div>' +
      '<div class="profile-tags">' + badge(employee.gender || 'M') + badge(employee.marital_status || 'SINGLE') + '</div></div>' +
      '<div class="dash-grid">' +
      '<section class="card card-pad"><div class="card-head"><div><h2>Şəxsi məlumat</h2></div></div>' +
      '<dl class="mini-dl"><div><dt>FİN</dt><dd class="mono">' + esc(employee.pin_code || '—') + '</dd></div>' +
      '<div><dt>SSN</dt><dd class="mono">' + esc(employee.ssn || '—') + '</dd></div>' +
      '<div><dt>Doğum tarixi</dt><dd>' + esc(fmtDate(employee.birth_date)) + '</dd></div>' +
      '<div><dt>Vətəndaşlıq</dt><dd>' + esc(employee.citizenship || '—') + '</dd></div>' +
      '<div><dt>Telefon</dt><dd>' + esc(employee.phone || '—') + '</dd></div>' +
      '<div><dt>E-poçt</dt><dd>' + esc(employee.email || '—') + '</dd></div>' +
      '<div><dt>Ünvan</dt><dd>' + esc(employee.address || '—') + '</dd></div>' +
      '<div><dt>ŞV / bitmə</dt><dd>' + esc(employee.id_card_number || '—') + ' · ' + esc(fmtDate(employee.id_card_expiry_date)) + '</dd></div>' +
      '<div><dt>Bank</dt><dd>' + esc(employee.bank_name || '—') + '</dd></div>' +
      '<div><dt>IBAN</dt><dd class="mono">' + esc(employee.bank_iban || '—') + '</dd></div>' +
      '<div><dt>Sığorta stajı</dt><dd>' + esc(fmtNumber(employee.total_insurance_tenure_years, 1)) + ' il</dd></div></dl></section>' +
      '<section class="card card-pad"><div class="card-head"><div><h2>Əmək müqaviləsi</h2></div></div>' + contractHTML + '</section>' +
      '<section class="card table-card span-2"><div class="card-head pad"><div><h2>Məzuniyyət balansı</h2></div></div>' +
      (balances.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>İş ili</th><th class="num">Baza gün</th><th class="num">Əlavə</th><th class="num">İstifadə</th><th class="num">Qalıq</th></tr></thead><tbody>' + balanceRows + '</tbody></table></div>'
        : emptyState('Balans yoxdur', '')) + '</section>' +
      '<section class="card table-card"><div class="card-head pad"><div><h2>Sənədlər</h2></div></div>' +
      (documents.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>Növ</th><th>Nömrə</th><th>Verilmə</th><th>Bitmə</th></tr></thead><tbody>' + documentRows + '</tbody></table></div>'
        : emptyState('Sənəd yoxdur', '')) + '</section>' +
      '<section class="card table-card"><div class="card-head pad"><div><h2>Ailə üzvləri</h2></div></div>' +
      (family.length ? '<div class="table-wrap"><table class="data"><thead><tr><th>Ad Soyad</th><th>Qohumluq</th><th>Doğum tarixi</th><th>Asılı</th></tr></thead><tbody>' + familyRows + '</tbody></table></div>'
        : emptyState('Ailə üzvü yoxdur', '')) + '</section>' +
      '</div>';
  }

  async function openEmployeeProfile(id) {
    try {
      var profile = await api('/employees/' + id + '/profile');
      openModal({
        title: 'İşçi profili',
        subtitle: [profile.employee.last_name, profile.employee.first_name].filter(Boolean).join(' '),
        size: 'wide',
        body: employeeProfileHTML(profile),
        footer: '<a class="btn ghost" href="#/s/employee/' + id + '" data-act="modal-close">Tam səhifə</a>' +
          '<button class="btn ghost" type="button" data-act="employee-reference-pdf" data-id="' + id + '">' + icon('download') + 'Arayış (PDF)</button>' +
          (canPreviewSettlement() ? '<button class="btn ghost" type="button" data-act="settlement-preview" data-id="' + id + '">' + icon('wallet') + 'Son haqq-hesab</button>' : '') +
          '<button class="btn primary" type="button" data-act="modal-close">Bağla</button>'
      });
    } catch (err) { toast(err.message, 'error'); }
  }

  async function renderEmployeeProfileScreen(id) {
    setHeader('İşçi profili', 'Tam kadr kartı');
    $('#view').innerHTML = loadingHTML('Profil yüklənir...');
    var profile = await api('/employees/' + id + '/profile');
    var employee = profile.employee;
    setHeader([employee.last_name, employee.first_name].filter(Boolean).join(' '), 'FİN ' + (employee.pin_code || '—'));
    $('#view').innerHTML = '<div class="page-toolbar"><div class="toolbar-info"><a class="back-link" href="#/entity/employees">' + icon('arrow-left') + 'İşçilər</a></div>' +
      '<div class="toolbar-actions">' +
      '<button class="btn ghost" type="button" data-act="employee-reference-pdf" data-id="' + id + '">' + icon('download') + 'Arayış (PDF)</button>' +
      (canPreviewSettlement() ? '<button class="btn ghost" type="button" data-act="settlement-preview" data-id="' + id + '">' + icon('wallet') + 'Son haqq-hesab</button>' : '') +
      '<a class="btn ghost" href="#/entity/employees">Bütün işçilər</a></div></div>' + employeeProfileHTML(profile);
  }

  document.addEventListener('click', async function (event) {
    var trigger = event.target.closest('[data-act]');
    if (!trigger) return;
    var act = trigger.getAttribute('data-act');
    var id = trigger.getAttribute('data-id');
    var key = trigger.getAttribute('data-key');
    try {
      switch (act) {
        case 'logout':
          logout();
          return;
        case 'modal-close':
          closeModal();
          return;
        case 'quick-new-order':
          await openEntityForm('hr-orders');
          return;
        case 'quick-new-employee':
          await openEntityForm('employees');
          return;
        case 'entity-create':
          await openEntityForm(key);
          return;
        case 'entity-edit':
          event.preventDefault();
          await openEntityForm(key, Number(id));
          return;
        case 'entity-delete': {
          if (!window.confirm('Bu qeyd silinsin?')) return;
          var entity = state.entityMap[key];
          await api(entity.path + '/' + id, { method: 'DELETE' });
          toast('Qeyd silindi', 'success');
          await renderEntity(key);
          return;
        }
        case 'entity-refresh':
          await renderEntity(key);
          return;
        case 'entity-page': {
          var saved = state.entityState[key];
          var next = saved.skip + Number(trigger.getAttribute('data-dir')) * saved.limit;
          saved.skip = Math.max(0, next);
          await renderEntity(key);
          return;
        }
        case 'entity-csv':
          exportEntityCSV(key);
          return;
        case 'employee-profile':
          await openEmployeeProfile(id);
          return;
        case 'contract-detail':
          await openContractDetail(Number(id));
          return;
        case 'service-tax':
          await openServiceTax(Number(id));
          return;
        case 'application-manage':
          await openApplicationManage(Number(id));
          return;
        case 'trip-action':
          await tripAction(id, trigger.getAttribute('data-op'));
          return;
        case 'leave-balance-init':
          await openLeaveBalanceInit(id ? Number(id) : null, trigger.getAttribute('data-detail') === '1');
          return;
        case 'emas-queue':
          await openEmasQueueForm();
          return;
        case 'emas-sync':
          await syncEmasLog(id);
          return;
        case 'settlement-preview':
          await openFinalSettlement(Number(id));
          return;
        case 'recruitment-refresh':
          await renderRecruitment();
          return;
        case 'application-quick-stage':
          await quickMoveApplication(id, trigger.getAttribute('data-stage'));
          return;
        case 'offboarding-checklist':
          await openOffboardingChecklist();
          return;
        case 'offboarding-status':
          await setOffboardingStatus(id, trigger.getAttribute('data-status'));
          return;
        case 'payroll-new':
          await openPayrollCreate();
          return;
        case 'payroll-refresh':
          await renderPayrollRuns();
          return;
        case 'payroll-action':
          await payrollAction(id, trigger.getAttribute('data-op'));
          return;
        case 'payroll-delete':
          await payrollDelete(id);
          return;
        case 'payroll-export':
          await exportPayroll(id, trigger.getAttribute('data-format'));
          return;
        case 'payslip':
          await downloadPayslip(id);
          return;
        case 'leave-filter':
          state.leaveFilter = trigger.getAttribute('data-status');
          await renderLeaveRequests();
          return;
        case 'leave-new':
          await openLeaveCreate();
          return;
        case 'leave-refresh':
          await renderLeaveRequests();
          return;
        case 'leave-approve':
          await decideLeave(id, 'approve');
          return;
        case 'leave-reject':
          await decideLeave(id, 'reject');
          return;
        case 'leave-cancel':
          await decideLeave(id, 'cancel');
          return;
        case 'sick-new':
          await openSickCreate();
          return;
        case 'sick-refresh':
          await renderSickLeaves();
          return;
        case 'sick-cancel':
          await cancelSick(id);
          return;
        case 'timesheet-generate':
          await openTimesheetGenerate();
          return;
        case 'timesheet-approve':
          await timesheetAction(id, 'approve');
          return;
        case 'timesheet-lock':
          await timesheetAction(id, 'lock');
          return;
        case 'timesheet-mode':
          state.timesheetMode = trigger.getAttribute('data-mode');
          await renderTimesheets();
          return;
        case 'timesheet-daily':
          await openEmployeeDailyAttendanceModal(id, trigger.getAttribute('data-day'));
          return;
        case 'daily-override-prompt':
          await openDailyOverrideModal(
            trigger.getAttribute('data-sheet'),
            trigger.getAttribute('data-day'),
            trigger.getAttribute('data-hours'),
            trigger.getAttribute('data-code'),
            trigger.getAttribute('data-notes')
          );
          return;
        case 'turnstile-simulate':
          await simulateTurnstileAction();
          return;
        case 'turnstile-import':
          await openTurnstileImportModal();
          return;
        case 'payroll-item-details':
          await openPayrollItemBreakdownModal(id);
          return;
        case 'approvals-refresh':
          await renderApprovals();
          return;
        case 'approval-decide':
          await decideApproval(id, trigger.getAttribute('data-decision'));
          return;
        case 'users-refresh':
          await renderUsers();
          return;
        case 'user-new':
          await openUserForm(null);
          return;
        case 'user-edit':
          await openUserForm(Number(id));
          return;
        case 'user-reset':
          await resetUserPassword(id);
          return;
        case 'audit-refresh':
          await renderAudit();
          return;
        case 'reports-days':
          state.reportsDays = Number(trigger.getAttribute('data-days'));
          await renderReports();
          return;
        case 'reports-refresh':
          await renderReports();
          return;
        case 'compliance-export':
          await downloadFile('/compliance/unified-declaration?year=' + trigger.getAttribute('data-year') + '&month=' + trigger.getAttribute('data-month') + '&format=csv', 'vahid-beyanname-' + trigger.getAttribute('data-year') + '-' + pad(trigger.getAttribute('data-month')) + '.csv');
          return;
        case 'calendar-shift':
          await shiftCalendar(trigger.getAttribute('data-dir'));
          return;
        case 'calendar-today': {
          var now = new Date();
          state.calendarYear = now.getFullYear();
          state.calendarMonth = now.getMonth() + 1;
          await renderProductionCalendar();
          return;
        }
        case 'calendar-edit':
          await openCalendarEdit(trigger.getAttribute('data-date'));
          return;
        case 'calendar-generate':
          await generateCalendarYear(trigger.getAttribute('data-year'));
          return;
        case 'onboarding-checklist':
          await openOnboardingChecklist();
          return;
        case 'onboarding-new':
          await openOnboardingTaskForm(null);
          return;
        case 'onboarding-edit':
          await openOnboardingTaskForm(Number(id));
          return;
        case 'onboarding-status':
          await setOnboardingStatus(id, trigger.getAttribute('data-status'));
          return;
        case 'ess-new-leave':
          await openEssLeaveCreate();
          return;
        case 'ess-cancel-leave':
          await essCancelLeave(id);
          return;
        case 'ess-payslip':
          await downloadFile('/ess/payslips/' + id + '/pdf', 'payslip-' + id + '.pdf');
          return;
        case 'ess-reference-pdf':
          await downloadFile('/ess/reference.pdf', 'is-yerinden-arayis.pdf');
          return;
        case 'employee-reference-pdf':
          await downloadFile('/employees/' + id + '/reference.pdf', 'arayis-' + id + '.pdf');
          return;
        case 'order-pdf':
          await downloadFile('/hr-orders/' + id + '/order.pdf', 'emr-' + id + '.pdf');
          return;
        case 'offer-letter-pdf':
          await downloadFile('/applications/' + id + '/offer-letter.pdf', 'offer-letter-' + id + '.pdf');
          return;
        case 'compliance-military-export':
          await downloadFile('/compliance/military-report' + (state.user && state.user.organization_id ? '?organization_id=' + state.user.organization_id : ''), 'herbi-ucot-t2.csv');
          return;
        case 'work-schedule-new':
          await openWorkScheduleModal(null);
          return;
        case 'work-schedule-edit':
          await openWorkScheduleModal(Number(id));
          return;
        case 'work-schedule-delete': {
          if (!window.confirm('Bu iş qrafiki silinsin?')) return;
          await api('/work-schedules/' + id, { method: 'DELETE' });
          toast('İş qrafiki silindi', 'success');
          await renderWorkSchedules();
          return;
        }
        case 'work-schedule-preset':
          await openSchedulePresetsModal();
          return;
        case 'work-schedule-assign':
          await openScheduleAssignmentModal(Number(id), trigger.getAttribute('data-name'));
          return;
        case 'system-toggle-demo':
          await toggleDemoModeAction();
          return;
        case 'system-wipe-demo':
          await confirmAndWipeDemoData();
          return;
        case 'user-profile-dialog':
          await openUserProfileDialog();
          return;
        default:
          return;
      }
    } catch (err) {
      toast(err.message, 'error');
    }
  });

  document.addEventListener('click', function (event) {
    if (event.target && event.target.hasAttribute && event.target.hasAttribute('data-modal-backdrop')) closeModal();
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && $('#modal-root').innerHTML) closeModal();
  });

  async function loadSystemInfo() {
    try {
      state.systemInfo = await api('/system/info');
    } catch (err) {
      state.systemInfo = { demo_enabled: false, docs_enabled: true };
    }
    var demoBox = document.querySelector('.demo-box');
    if (demoBox) demoBox.classList.toggle('hidden', !state.systemInfo.demo_enabled);
    document.querySelectorAll('[data-docs-link]').forEach(function (link) {
      link.classList.toggle('hidden', !state.systemInfo.docs_enabled);
    });
  }

  async function boot() {
    await loadSystemInfo();
    if (state.token) {
      try {
        state.user = await api('/auth/me');
        localStorage.setItem('hr_user', JSON.stringify(state.user));
        await loadMeta();
        showApp();
        if (!location.hash || location.hash === '#') {
          location.hash = defaultRouteForUser();
        } else {
          route();
        }
        return;
      } catch (err) {
        clearSession();
      }
    }
    showLogin();
  }

  $('#login-form').addEventListener('submit', login);
  $$('.demo-chip').forEach(function (chip) {
    chip.addEventListener('click', function () {
      var parts = String(chip.getAttribute('data-demo') || '').split('|');
      $('#login-email').value = parts[0] || '';
      $('#login-password').value = parts[1] || '';
      $('#login-form').requestSubmit();
    });
  });
  $('#menu-toggle').addEventListener('click', function () { document.body.classList.toggle('sidebar-open'); });
  $('#sidebar-overlay').addEventListener('click', closeMobileSidebar);
  window.addEventListener('hashchange', function () { route(); });

  boot();
})();
