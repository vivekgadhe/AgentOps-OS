"""The audit trail must be append-only, and we say plainly where that stops."""

from __future__ import annotations

from sqlalchemy import delete, func, select, text, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from agentops.db.models import AuditLog, User
from tests.integration.db.factories import ExpectDbError, Factory

APPEND_ONLY = "append-only"


def test_inserting_audit_rows_works(factory: Factory) -> None:
    entry = factory.audit(action="user.login", outcome="denied")
    assert entry.id is not None


def test_update_is_blocked(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    entry = factory.audit()
    with expect_db_error(exc=DBAPIError, match=APPEND_ONLY):
        orm_session.execute(
            update(AuditLog).where(AuditLog.id == entry.id).values(outcome="failure")
        )


def test_delete_is_blocked(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    entry = factory.audit()
    with expect_db_error(exc=DBAPIError, match=APPEND_ONLY):
        orm_session.execute(delete(AuditLog).where(AuditLog.id == entry.id))


def test_truncate_is_blocked(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    factory.audit()
    with expect_db_error(exc=DBAPIError, match=APPEND_ONLY):
        orm_session.execute(text("TRUNCATE TABLE audit_logs"))


def test_blocked_mutations_leave_the_row_untouched(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    entry = factory.audit(outcome="success")
    with expect_db_error(exc=DBAPIError, match=APPEND_ONLY):
        orm_session.execute(
            update(AuditLog).where(AuditLog.id == entry.id).values(outcome="failure")
        )
    orm_session.expire_all()
    stored = orm_session.execute(
        select(AuditLog.outcome).where(AuditLog.id == entry.id)
    ).scalar_one()
    assert stored == "success"


def test_user_with_audit_history_cannot_be_deleted(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    user = factory.user()
    factory.audit(actor_user_id=user.id)
    with expect_db_error(match="fk_audit_logs_actor_user_id_users"):
        orm_session.execute(delete(User).where(User.id == user.id))


def test_limitation_table_owner_can_disable_the_trigger(
    factory: Factory, orm_session: Session
) -> None:
    """DOCUMENTED LIMITATION, not a feature.

    The trigger stops application code and ordinary SQL. A database role that
    owns the table (or a superuser) can switch it off. Inside this test the
    change is rolled back with the surrounding transaction (DDL is
    transactional in PostgreSQL), so nothing leaks.
    """
    entry = factory.audit(outcome="success")
    orm_session.execute(text("ALTER TABLE audit_logs DISABLE TRIGGER audit_logs_no_update_delete"))
    orm_session.execute(update(AuditLog).where(AuditLog.id == entry.id).values(outcome="failure"))
    changed = orm_session.execute(
        select(func.count()).select_from(AuditLog).where(AuditLog.outcome == "failure")
    ).scalar_one()
    assert changed >= 1
