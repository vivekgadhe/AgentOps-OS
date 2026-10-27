"""Row builders shared by the schema tests (importable, unlike conftest)."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

from alembic.config import Config
from sqlalchemy.engine import URL, Connection
from sqlalchemy.orm import Session

from agentops.db.models import AuditLog, TaskRun, User, WorkflowRun

ExpectDbError = Callable[..., AbstractContextManager[None]]
AlembicConfigFactory = Callable[[Connection], Config]
DisposableDatabaseFactory = Callable[[str], URL]


class Factory:
    """Builds valid rows. ``*_values`` return dicts for Core inserts."""

    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def user_values(**overrides: Any) -> dict[str, Any]:
        values: dict[str, Any] = {
            "id": uuid.uuid4(),
            "email": f"user-{uuid.uuid4().hex[:10]}@example.com",
            "password_hash": "not-a-real-hash",
            "role": "viewer",
        }
        return {**values, **overrides}

    @staticmethod
    def workflow_values(created_by: uuid.UUID, **overrides: Any) -> dict[str, Any]:
        values: dict[str, Any] = {
            "id": uuid.uuid4(),
            "created_by": created_by,
            "goal": "Summarise last quarter's sales",
            "status": "pending",
        }
        return {**values, **overrides}

    @staticmethod
    def task_values(workflow_id: uuid.UUID, **overrides: Any) -> dict[str, Any]:
        values: dict[str, Any] = {
            "id": uuid.uuid4(),
            "workflow_run_id": workflow_id,
            "key": f"t-{uuid.uuid4().hex[:6]}",
            "name": "Load CSV",
            "status": "pending",
        }
        return {**values, **overrides}

    @staticmethod
    def event_values(workflow_id: uuid.UUID, **overrides: Any) -> dict[str, Any]:
        values: dict[str, Any] = {
            "workflow_run_id": workflow_id,
            "event_type": "task.started",
            "level": "info",
            "message": "started",
            "data": {},
        }
        return {**values, **overrides}

    @staticmethod
    def audit_values(**overrides: Any) -> dict[str, Any]:
        values: dict[str, Any] = {
            "action": "workflow.create",
            "resource_type": "workflow_run",
            "outcome": "success",
            "details": {},
        }
        return {**values, **overrides}

    def user(self, **overrides: Any) -> User:
        user = User(**self.user_values(**overrides))
        self.session.add(user)
        self.session.flush()
        return user

    def workflow(self, created_by: User | None = None, **overrides: Any) -> WorkflowRun:
        owner = created_by or self.user()
        workflow = WorkflowRun(**self.workflow_values(owner.id, **overrides))
        self.session.add(workflow)
        self.session.flush()
        return workflow

    def task(self, workflow: WorkflowRun, **overrides: Any) -> TaskRun:
        task = TaskRun(**self.task_values(workflow.id, **overrides))
        self.session.add(task)
        self.session.flush()
        return task

    def audit(self, **overrides: Any) -> AuditLog:
        entry = AuditLog(**self.audit_values(**overrides))
        self.session.add(entry)
        self.session.flush()
        return entry
