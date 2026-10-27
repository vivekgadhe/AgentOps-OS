"""Every CHECK, UNIQUE and FOREIGN KEY rule, proven against PostgreSQL.

Each test uses a raw Core INSERT so the database (not Python validation) is the
thing being tested, and ``match=`` names the exact constraint that must fire.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from enum import StrEnum

import pytest
from sqlalchemy import insert
from sqlalchemy.orm import Session

from agentops.db.models import (
    AuditLog,
    AuditOutcome,
    EventLevel,
    ExecutionEvent,
    TaskDependency,
    TaskRun,
    TaskStatus,
    User,
    UserRole,
    WorkflowRun,
    WorkflowStatus,
)
from tests.integration.db.factories import ExpectDbError, Factory

NOW = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


# ----------------------------- users ---------------------------------------
@pytest.mark.parametrize("role", list(UserRole))
def test_every_user_role_is_accepted(role: StrEnum, factory: Factory, orm_session: Session) -> None:
    orm_session.execute(insert(User).values(**factory.user_values(role=role.value)))


def test_unknown_user_role_is_rejected(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    with expect_db_error(match="ck_users_role_valid"):
        orm_session.execute(insert(User).values(**factory.user_values(role="root")))


def test_duplicate_email_is_rejected(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    factory.user(email="dup@example.com")
    with expect_db_error(match="uq_users_email"):
        orm_session.execute(insert(User).values(**factory.user_values(email="dup@example.com")))


def test_uppercase_email_is_rejected_by_the_database(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    with expect_db_error(match="ck_users_email_lowercase"):
        orm_session.execute(insert(User).values(**factory.user_values(email="Mixed@Example.com")))


def test_blank_password_hash_is_rejected(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    with expect_db_error(match="ck_users_password_hash_not_empty"):
        orm_session.execute(insert(User).values(**factory.user_values(password_hash="")))


# ------------------------- workflow_runs -----------------------------------
@pytest.mark.parametrize("status", list(WorkflowStatus))
def test_every_workflow_status_is_accepted(
    status: StrEnum, factory: Factory, orm_session: Session
) -> None:
    owner = factory.user()
    orm_session.execute(
        insert(WorkflowRun).values(**factory.workflow_values(owner.id, status=status.value))
    )


def test_unknown_workflow_status_is_rejected(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    owner = factory.user()
    with expect_db_error(match="ck_workflow_runs_status_valid"):
        orm_session.execute(
            insert(WorkflowRun).values(**factory.workflow_values(owner.id, status="exploded"))
        )


def test_blank_goal_is_rejected(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    owner = factory.user()
    with expect_db_error(match="ck_workflow_runs_goal_not_blank"):
        orm_session.execute(
            insert(WorkflowRun).values(**factory.workflow_values(owner.id, goal="   "))
        )


def test_workflow_cannot_finish_before_it_starts(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    owner = factory.user()
    with expect_db_error(match="ck_workflow_runs_finished_after_started"):
        orm_session.execute(
            insert(WorkflowRun).values(
                **factory.workflow_values(
                    owner.id, started_at=NOW, finished_at=NOW - timedelta(seconds=1)
                )
            )
        )


def test_workflow_requires_an_existing_creator(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    with expect_db_error(match="fk_workflow_runs_created_by_users"):
        orm_session.execute(insert(WorkflowRun).values(**factory.workflow_values(uuid.uuid4())))


# ---------------------------- task_runs ------------------------------------
@pytest.mark.parametrize("status", list(TaskStatus))
def test_every_task_status_is_accepted(
    status: StrEnum, factory: Factory, orm_session: Session
) -> None:
    workflow = factory.workflow()
    orm_session.execute(
        insert(TaskRun).values(**factory.task_values(workflow.id, status=status.value))
    )


@pytest.mark.parametrize(
    ("overrides", "constraint"),
    [
        ({"status": "paused"}, "ck_task_runs_status_valid"),
        ({"attempt_count": -1}, "ck_task_runs_attempts_non_negative"),
        ({"max_attempts": 0}, "ck_task_runs_max_attempts_positive"),
        ({"attempt_count": 4, "max_attempts": 3}, "ck_task_runs_attempts_within_max"),
        ({"timeout_seconds": 0}, "ck_task_runs_timeout_positive"),
        ({"key": "  "}, "ck_task_runs_key_not_blank"),
        ({"name": ""}, "ck_task_runs_name_not_blank"),
        (
            {"started_at": NOW, "finished_at": NOW - timedelta(minutes=1)},
            "ck_task_runs_finished_after_started",
        ),
    ],
)
def test_invalid_task_values_are_rejected(
    overrides: dict[str, object],
    constraint: str,
    factory: Factory,
    orm_session: Session,
    expect_db_error: ExpectDbError,
) -> None:
    workflow = factory.workflow()
    with expect_db_error(match=constraint):
        orm_session.execute(insert(TaskRun).values(**factory.task_values(workflow.id, **overrides)))


def test_task_key_is_unique_within_a_workflow(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    workflow = factory.workflow()
    factory.task(workflow, key="load")
    with expect_db_error(match="uq_task_runs_workflow_run_id_key"):
        orm_session.execute(insert(TaskRun).values(**factory.task_values(workflow.id, key="load")))


def test_same_task_key_is_allowed_in_different_workflows(factory: Factory) -> None:
    factory.task(factory.workflow(), key="load")
    factory.task(factory.workflow(), key="load")


# ------------------------ task_dependencies --------------------------------
def _edge(task: TaskRun, depends_on: TaskRun, workflow_id: uuid.UUID) -> dict[str, object]:
    return {
        "task_id": task.id,
        "depends_on_task_id": depends_on.id,
        "workflow_run_id": workflow_id,
    }


def test_dependency_inside_one_workflow_is_accepted(factory: Factory, orm_session: Session) -> None:
    workflow = factory.workflow()
    first, second = factory.task(workflow, key="a"), factory.task(workflow, key="b")
    orm_session.execute(insert(TaskDependency).values(**_edge(second, first, workflow.id)))


def test_task_cannot_depend_on_itself(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    workflow = factory.workflow()
    task = factory.task(workflow)
    with expect_db_error(match="ck_task_dependencies_no_self_dependency"):
        orm_session.execute(insert(TaskDependency).values(**_edge(task, task, workflow.id)))


def test_duplicate_dependency_edge_is_rejected(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    workflow = factory.workflow()
    first, second = factory.task(workflow, key="a"), factory.task(workflow, key="b")
    orm_session.execute(insert(TaskDependency).values(**_edge(second, first, workflow.id)))
    with expect_db_error(match="pk_task_dependencies"):
        orm_session.execute(insert(TaskDependency).values(**_edge(second, first, workflow.id)))


def test_dependency_cannot_point_at_a_task_of_another_workflow(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    workflow_a, workflow_b = factory.workflow(), factory.workflow()
    task_a, task_b = factory.task(workflow_a), factory.task(workflow_b)
    # The dependency target lives in workflow B but the edge claims workflow A.
    with expect_db_error(match="fk_task_deps_dependency_in_workflow"):
        orm_session.execute(insert(TaskDependency).values(**_edge(task_a, task_b, workflow_a.id)))


def test_dependency_cannot_claim_a_workflow_the_task_is_not_in(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    workflow_a, workflow_b = factory.workflow(), factory.workflow()
    task_a, task_b = factory.task(workflow_a), factory.task(workflow_b)
    # The edge claims workflow B, but the dependent task belongs to workflow A.
    with expect_db_error(match="fk_task_deps_task_in_workflow"):
        orm_session.execute(insert(TaskDependency).values(**_edge(task_a, task_b, workflow_b.id)))


# -------------------------- execution_events -------------------------------
@pytest.mark.parametrize("level", list(EventLevel))
def test_every_event_level_is_accepted(
    level: StrEnum, factory: Factory, orm_session: Session
) -> None:
    workflow = factory.workflow()
    orm_session.execute(
        insert(ExecutionEvent).values(**factory.event_values(workflow.id, level=level.value))
    )


def test_unknown_event_level_is_rejected(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    workflow = factory.workflow()
    with expect_db_error(match="ck_execution_events_level_valid"):
        orm_session.execute(
            insert(ExecutionEvent).values(**factory.event_values(workflow.id, level="trace"))
        )


def test_workflow_level_event_without_a_task_is_accepted(
    factory: Factory, orm_session: Session
) -> None:
    workflow = factory.workflow()
    orm_session.execute(
        insert(ExecutionEvent).values(**factory.event_values(workflow.id, task_run_id=None))
    )


def test_event_cannot_reference_a_task_of_another_workflow(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    workflow_a, workflow_b = factory.workflow(), factory.workflow()
    task_b = factory.task(workflow_b)
    with expect_db_error(match="fk_execution_events_task_in_workflow"):
        orm_session.execute(
            insert(ExecutionEvent).values(
                **factory.event_values(workflow_a.id, task_run_id=task_b.id)
            )
        )


# ----------------------------- audit_logs ----------------------------------
@pytest.mark.parametrize("outcome", list(AuditOutcome))
def test_every_audit_outcome_is_accepted(
    outcome: StrEnum, factory: Factory, orm_session: Session
) -> None:
    orm_session.execute(insert(AuditLog).values(**factory.audit_values(outcome=outcome.value)))


def test_unknown_audit_outcome_is_rejected(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    with expect_db_error(match="ck_audit_logs_outcome_valid"):
        orm_session.execute(insert(AuditLog).values(**factory.audit_values(outcome="maybe")))


def test_audit_actor_must_exist(
    factory: Factory, orm_session: Session, expect_db_error: ExpectDbError
) -> None:
    with expect_db_error(match="fk_audit_logs_actor_user_id_users"):
        orm_session.execute(
            insert(AuditLog).values(**factory.audit_values(actor_user_id=uuid.uuid4()))
        )
