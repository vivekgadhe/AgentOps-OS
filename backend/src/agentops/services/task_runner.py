"""Isolated execution boundary for registered task handlers."""

from __future__ import annotations

import multiprocessing
from collections.abc import Callable
from multiprocessing.connection import Connection
from typing import Any

TaskHandler = Callable[[dict[str, Any]], dict[str, Any]]


class TaskTimeoutError(TimeoutError):
    """Raised when a task exceeds its allowed execution time."""


def _run_handler(
    connection: Connection,
    handler: TaskHandler,
    input_data: dict[str, Any],
) -> None:
    """Execute a handler in a child process and return its result."""
    try:
        result = handler(input_data)

        if not isinstance(result, dict):
            raise TypeError("Task handler must return a dictionary")

        connection.send(("success", result))
    except Exception as exc:
        try:
            connection.send(
                (
                    "error",
                    {
                        "type": type(exc).__name__,
                        "message": str(exc),
                    },
                )
            )
        except (BrokenPipeError, EOFError, OSError):
            pass
    finally:
        connection.close()


def _stop_process(process: Any) -> None:
    """Stop a child process safely and wait for it to exit."""
    # process.start() may fail before a child process exists.
    if process.pid is None:
        return

    if not process.is_alive():
        process.join(timeout=0)
        return

    process.terminate()
    process.join(timeout=2)

    if process.is_alive():
        process.kill()
        process.join(timeout=2)


def run_task(
    handler: TaskHandler,
    input_data: dict[str, Any],
    timeout_seconds: int,
) -> dict[str, Any]:
    """Run a handler in a separate process with a hard timeout."""
    if timeout_seconds < 1:
        raise ValueError("timeout_seconds must be at least 1")

    context = multiprocessing.get_context("spawn")
    receive_connection, send_connection = context.Pipe(duplex=False)

    process = context.Process(
        target=_run_handler,
        args=(send_connection, handler, input_data),
        daemon=True,
    )

    try:
        process.start()
        send_connection.close()

        if not receive_connection.poll(timeout_seconds):
            _stop_process(process)
            raise TaskTimeoutError(f"Task exceeded its {timeout_seconds}-second timeout")

        try:
            status, payload = receive_connection.recv()
        except EOFError as exc:
            process.join(timeout=2)
            raise RuntimeError(
                f"Task process exited without returning a result (exit code: {process.exitcode})"
            ) from exc

        process.join(timeout=2)

        if process.is_alive():
            _stop_process(process)

        if status == "error":
            raise RuntimeError(f"Handler failed ({payload['type']}): {payload['message']}")

        if status != "success" or not isinstance(payload, dict):
            raise RuntimeError("Task process returned an invalid result")

        return payload

    finally:
        receive_connection.close()
        send_connection.close()
        _stop_process(process)
