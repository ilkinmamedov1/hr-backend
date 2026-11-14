from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.time import ProductionCalendar

FIXED_HOLIDAYS: dict[int, dict[tuple[int, int], str]] = {
    2025: {
        (1, 1): "Yeni il bayramı",
        (1, 2): "Yeni il bayramı",
        (1, 20): "Ümumxalq hüzn günü (20 Yanvar)",
        (3, 8): "Qadınlar günü",
        (3, 20): "Novruz bayramı",
        (3, 21): "Novruz bayramı",
        (3, 22): "Novruz bayramı",
        (3, 23): "Novruz bayramı",
        (3, 24): "Novruz bayramı",
        (3, 30): "Ramazan bayramı",
        (3, 31): "Ramazan bayramı",
        (5, 9): "Faşizm üzərində qələbə günü",
        (5, 28): "Müstəqillik günü",
        (6, 6): "Qurban bayramı",
        (6, 7): "Qurban bayramı",
        (6, 15): "Milli Qurtuluş günü",
        (6, 26): "Azərbaycan Respublikasının Silahlı Qüvvələri günü",
        (11, 8): "Zəfər günü",
        (11, 9): "Dövlət bayrağı günü",
        (12, 31): "Dünya azərbaycanlılarının həmrəyliyi günü",
    },
    2026: {
        (1, 1): "Yeni il bayramı",
        (1, 2): "Yeni il bayramı",
        (1, 20): "Ümumxalq hüzn günü (20 Yanvar)",
        (3, 8): "Qadınlar günü",
        (3, 20): "Novruz bayramı",
        (3, 21): "Novruz bayramı",
        (3, 22): "Novruz bayramı",
        (3, 23): "Novruz bayramı",
        (3, 24): "Novruz bayramı",
        (5, 9): "Faşizm üzərində qələbə günü",
        (5, 26): "Qurban bayramı (təxmini - rəsmi təqvimlə yoxlanılmalıdır)",
        (5, 27): "Qurban bayramı (təxmini - rəsmi təqvimlə yoxlanılmalıdır)",
        (5, 28): "Müstəqillik günü",
        (6, 15): "Milli Qurtuluş günü",
        (6, 26): "Azərbaycan Respublikasının Silahlı Qüvvələri günü",
        (11, 8): "Zəfər günü",
        (11, 9): "Dövlət bayrağı günü",
        (12, 31): "Dünya azərbaycanlılarının həmrəyliyi günü",
    },
    2027: {
        (1, 1): "Yeni il bayramı",
        (1, 2): "Yeni il bayramı",
        (1, 20): "Ümumxalq hüzn günü (20 Yanvar)",
        (3, 8): "Qadınlar günü",
        (3, 20): "Novruz bayramı",
        (3, 21): "Novruz bayramı",
        (3, 22): "Novruz bayramı",
        (3, 23): "Novruz bayramı",
        (3, 24): "Novruz bayramı",
        (5, 9): "Faşizm üzərində qələbə günü",
        (5, 28): "Müstəqillik günü",
        (6, 15): "Milli Qurtuluş günü",
        (6, 26): "Azərbaycan Respublikasının Silahlı Qüvvələri günü",
        (11, 8): "Zəfər günü",
        (11, 9): "Dövlət bayrağı günü",
        (12, 31): "Dünya azərbaycanlılarının həmrəyliyi günü",
    },
}


def generate_year_calendar(db: Session, year: int) -> int:
    db.execute(delete(ProductionCalendar).where(ProductionCalendar.year == year))
    holidays = dict(FIXED_HOLIDAYS.get(year, {}))
    holiday_dates = {date(year, m, d) for (m, d), _ in holidays.items()}

    shifted: dict[date, str] = {}
    for holiday in sorted(holiday_dates):
        if holiday.weekday() >= 5:
            candidate = holiday + timedelta(days=1)
            while (
                candidate.weekday() >= 5
                or candidate in holiday_dates
                or candidate in shifted
            ):
                candidate += timedelta(days=1)
            shifted[candidate] = holidays.get((holiday.month, holiday.day), "Bayram") + " (köçürülmüş)"

    all_holidays = {**holidays, **{k: v for k, v in shifted.items()}}
    holiday_dates |= set(shifted)

    current = date(year, 1, 1)
    rows = 0
    while current.year == year:
        next_day = current + timedelta(days=1)
        is_weekend = current.weekday() >= 5
        description = all_holidays.get((current.month, current.day))
        is_holiday = current in holiday_dates
        pre_holiday = (
            not is_weekend
            and not is_holiday
            and next_day in holiday_dates
        )

        is_mourning = (current.month == 1 and current.day == 20)
        if is_mourning:
            day_type = "MOURNING"
            description = "Ümumxalq hüzn günü (20 Yanvar)"
            norm40 = Decimal("0")
            norm36 = Decimal("0")
        elif is_holiday:
            day_type = "HOLIDAY"
            description = all_holidays.get((current.month, current.day), "Bayram")
            norm40 = Decimal("0")
            norm36 = Decimal("0")
        elif is_weekend:
            day_type = "WEEKEND"
            norm40 = Decimal("0")
            norm36 = Decimal("0")
        elif pre_holiday:
            day_type = "SHORT_WORKDAY"
            is_pre_mourning = (next_day.month == 1 and next_day.day == 20)
            description = "Hüznqabağı qısaldılmış iş günü" if is_pre_mourning else (description or "Bayramqabağı qısaldılmış iş günü")
            norm40 = Decimal("7.00")
            norm36 = Decimal("6.20")
        else:
            day_type = "WORKDAY"
            norm40 = Decimal("8.00")
            norm36 = Decimal("7.20")

        db.add(
            ProductionCalendar(
                cal_date=current,
                year=year,
                month=current.month,
                day_type=day_type,
                norm_hours_40=norm40,
                norm_hours_36=norm36,
                description=description,
            )
        )
        rows += 1
        current = next_day
    db.commit()
    return rows


def get_month_calendar(db: Session, year: int, month: int) -> list[ProductionCalendar]:
    rows = list(
        db.scalars(
            select(ProductionCalendar)
            .where(ProductionCalendar.year == year, ProductionCalendar.month == month)
            .order_by(ProductionCalendar.cal_date)
        )
    )
    if not rows:
        generate_year_calendar(db, year)
        rows = list(
            db.scalars(
                select(ProductionCalendar)
                .where(ProductionCalendar.year == year, ProductionCalendar.month == month)
                .order_by(ProductionCalendar.cal_date)
            )
        )
    return rows


def month_norms(db: Session, year: int, month: int, weekly_hours: float = 40) -> dict:
    rows = get_month_calendar(db, year, month)
    workdays = [r for r in rows if r.day_type in ("WORKDAY", "SHORT_WORKDAY")]
    attribute = "norm_hours_36" if weekly_hours <= 36 else "norm_hours_40"
    norm = sum((Decimal(getattr(r, attribute)) for r in rows), Decimal("0"))
    return {
        "rows": rows,
        "workdays": len(workdays),
        "norm_hours": norm,
        "attribute": attribute,
    }


def is_holiday(db: Session, day: date) -> bool:
    row = db.get(ProductionCalendar, day)
    if row is None:
        get_month_calendar(db, day.year, day.month)
        row = db.get(ProductionCalendar, day)
    return row is not None and row.day_type in ("HOLIDAY", "MOURNING")
