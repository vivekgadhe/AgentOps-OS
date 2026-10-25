import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from agentops.core.config import Settings
from agentops.db.session import create_db_engine
from agentops.main import create_app

pytestmark = pytest.mark.integration


def test_integration_settings_point_at_the_test_database(integration_settings: Settings) -> None:
    engine = create_db_engine(integration_settings)
    try:
        with engine.connect() as connection:
            database_name = connection.execute(text("SELECT current_database()")).scalar_one()
    finally:
        engine.dispose()
    assert database_name.endswith("_test")


def test_ready_reports_up_against_real_postgres(integration_settings: Settings) -> None:
    with TestClient(create_app(integration_settings)) as client:
        response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "up"}
