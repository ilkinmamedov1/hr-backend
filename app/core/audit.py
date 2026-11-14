import contextvars
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

current_user_id: contextvars.ContextVar[int | None] = contextvars.ContextVar(
    "current_user_id", default=None
)
current_ip: contextvars.ContextVar[str | None] = contextvars.ContextVar("current_ip", default=None)


def _jsonable(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    return str(value)


def _snapshot(obj) -> dict:
    data = {}
    for attr in inspect(obj).mapper.column_attrs:
        data[attr.key] = _jsonable(getattr(obj, attr.key, None))
    return data


@event.listens_for(Session, "before_flush")
def _collect_audit_changes(session: Session, flush_context, instances) -> None:
    pending = []

    for obj in session.new:
        if getattr(obj, "__audited__", False):
            pending.append({"obj": obj, "action": "INSERT", "old": None, "new": None})

    for obj in session.dirty:
        if not getattr(obj, "__audited__", False):
            continue
        if not session.is_modified(obj, include_collections=False):
            continue
        state = inspect(obj)
        old_values, new_values = {}, {}
        for attr in state.mapper.column_attrs:
            history = state.attrs[attr.key].history
            if history.has_changes():
                old_values[attr.key] = _jsonable(history.deleted[0] if history.deleted else None)
                new_values[attr.key] = _jsonable(history.added[0] if history.added else None)
        if old_values:
            pending.append({"obj": obj, "action": "UPDATE", "old": old_values, "new": new_values})

    for obj in session.deleted:
        if getattr(obj, "__audited__", False):
            pending.append({"obj": obj, "action": "DELETE", "old": _snapshot(obj), "new": None})

    if pending:
        session.info["_audit_pending"] = pending


@event.listens_for(Session, "after_flush")
def _write_audit_logs(session: Session, flush_context) -> None:
    pending = session.info.pop("_audit_pending", None)
    if not pending:
        return

    from app.models.workflow import AuditLog

    table = AuditLog.__table__
    for item in pending:
        obj = item["obj"]
        record_id = getattr(obj, "id", None)
        if record_id is None:
            continue
        new_values = item["new"]
        if item["action"] == "INSERT":
            new_values = _snapshot(obj)
        session.connection().execute(
            table.insert().values(
                user_id=current_user_id.get(),
                table_name=obj.__tablename__,
                record_id=record_id,
                action=item["action"],
                old_values=item["old"],
                new_values=new_values,
                ip_address=current_ip.get(),
                created_at=datetime.now(timezone.utc),
            )
        )
