import json
import logging

from agentops.core.context import request_id_var
from agentops.core.logging import ContextFilter, JsonFormatter


def test_json_formatter_includes_context_and_extra_fields() -> None:
    token = request_id_var.set("req-12345678")
    try:
        record = logging.LogRecord("test", logging.INFO, __file__, 1, "hello %s", ("world",), None)
        ContextFilter().filter(record)
        record.status_code = 200
        output = json.loads(JsonFormatter().format(record))
    finally:
        request_id_var.reset(token)

    assert output["message"] == "hello world"
    assert output["level"] == "INFO"
    assert output["request_id"] == "req-12345678"
    assert output["status_code"] == 200
    assert "user_id" not in output  # unset context fields are omitted, not null
