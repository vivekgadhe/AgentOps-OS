"""ORM behaviour against the real, migrated test database."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import delete, func, insert, select, text
from sqlalchemy.orm import Session

from agentops.db.models import (
    ExecutionEvent,
    TaskDependency,
    TaskRun,
    User,
    WorkflowRun,
)
from tests.integration.db.factories import ExpectDbError, Factory


def test_session_is_bound_to_a_test_database(orm_session: Session) -> None:
    name = orm_session.execute(text("SELECT current_database()")).scalar_one()
    assert str(name).endswith("_test")


def test_user_email_is_normalised_to_lowercase(factory: Factory) -> None:
    user = factory.user(email="  Alice@Example.COM ")
    assert user.email == "alice@example.com"


def test_timestamps_are_timezone_aware(factory: Factory, orm_session: Session) -> None:
    user = factory.user()
    orm_session.refresh(user)
    assert user.created_at.tzinfo is not None
    assert user.updated_at.tzinfo is not None


def test_explicit_timestamp_round_trips_as_the_same_instant(
    factory: Factory, orm_session: Session
) -> None:
    started = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
    workflow = factory.workflow(started_at=started)
    orm_session.refresh(workflow)
    assert workflow.started_at is not None
    assert workflow.started_at == started
    assert workflow.started_at.utcoffset() is not None


def test_task_server_defaults_are_applied(factory: Factory, orm_session: Session) -> None:
    task = factory.task(factory.workflow())
    orm_session.refresh(task)
    assert (task.attempt_count, task.max_attempts, task.timeout_seconds) == (0, 3, 300)


def test_python_none_is_stored_as_sql_null_not_json_null(
    factory: Factory, orm_session: Session
) -> None:
    workflow = factory.workflow(plan=None)
    is_sql_null = orm_session.execute(
        text("SELECT plan IS NULL FROM workflow_runs WHERE id = :id"),
        {"id": workflow.id},
    ).scalar_one()
    assert is_sql_null is True


def test_json_payload_round_trips(factory: Factory, orm_session: Session) -> None:
    payload = {"steps": [{"tool": "csv.load", "args": {"path": "sales.csv"}}]}
    workflow = factory.workflow(plan=payload)
    orm_session.expire(workflow)
    assert workflow.plan == payload


def test_event_ids_increase(factory: Factory, orm_session: Session) -> None:
    workflow = factory.workflow()
    first = ExecutionEvent(**factory.event_values(workflow.id))
    second = ExecutionEvent(**factory.event_values(workflow.id))
    orm_session.add_all([first, second])
    orm_session.flush()
    assert second.id > first.id


def test_deleting_a_workflow_cascades_to_its_children(
    factory: Factory, orm_session: Session
) -> None:
    workflow = factory.workflow()
    first = factory.task(workflow, key="a")
    second = factory.task(workflow, key="b")
    orm_session.execute(
        insert(TaskDependency).values(
            task_id=second.id,
            depends_on_task_id=first.id,
            workflow_run_id=workflow.id,
        )
    )
    orm_session.execute(
        insert(ExecutionEvent).values(**factory.event_values(workflow.id, task_run_id=first.id))
    )
    workflow_id = workflow.id
    orm_session.expunge_all()

    orm_session.execute(delete(WorkflowRun).where(WorkflowRun.id == workflow_id))

    for model, column in (
        (TaskRun, TaskRun.workflow_run_id),
        (TaskDependency, TaskDependency.workflow_run_id),
        (ExecutionEvent, ExecutionEvent.workflow_run_id),
    ):
        remaining = orm_session.execute(
            select(func.count()).select_from(model).where(column == workflow_id)
        ).scalar_one()
        assert remaining == 0, model.__name__


def test_a_user_with_workflows_cannot_be_deleted(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    user = factory.user()
    factory.workflow(created_by=user)
    with expect_db_error(match="fk_workflow_runs_created_by_users"):
        orm_session.execute(delete(User).where(User.id == user.id))
