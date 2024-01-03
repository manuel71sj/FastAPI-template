import functools
import inspect
import logging
import sys
from pprint import pformat
from typing import Any, Union

import orjson
from loguru import logger
from {{cookiecutter.project_name}}.settings import settings

{%- if cookiecutter.otlp_enabled == "True" %}
from opentelemetry.trace import INVALID_SPAN, INVALID_SPAN_CONTEXT, get_current_span

{%- endif %}
from starlette.datastructures import URL

orjson_options = orjson.OPT_NAIVE_UTC
WIDTH = 180


def json_default(value: Any) -> str:
    if isinstance(value, URL):
        return value.__str__()

    return value


def format_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "source": f"{record['file'].name}" f":{record['function']}" f":{record['line']}",  # noqa: WPS221
    }


def serialize(record: dict[str, Any]) -> str:
    subset = format_record(record)
    subset.update(record["extra"])

    return orjson.dumps(subset, option=orjson_options, default=json_default).decode()


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.

    This handler intercepts all log requests and
    passes them to loguru.

    For more info see:
    https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        """
        Propagates logs to loguru.

        :param record: record to log.
        """
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        # frame, depth = logging.currentframe(), 2
        # while frame.f_code.co_filename == logging.__file__:
        #     frame = frame.f_back  # type: ignore
        #     depth += 1
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def record_formatter(record: dict[str, Any]) -> str:  # pragma: no cover
    """
    Formats the record.

    This function formats message
    by adding extra trace information to the record.

    :param record: record information.
    :return: format string.
    """
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
        "| <level>{level: <8}</level> "
        "| <magenta>trace_id={extra[trace_id]}</magenta> "
        "| <blue>span_id={extra[span_id]}</blue> "
        "| <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
        "- <level>{message}</level>\n"
    )

    span = get_current_span()

    record["extra"]["span_id"] = 0
    record["extra"]["trace_id"] = 0
    if span != INVALID_SPAN:
        span_context = span.get_span_context()
        if span_context != INVALID_SPAN_CONTEXT:
            record["extra"]["span_id"] = format(span_context.span_id, "016x")
            record["extra"]["trace_id"] = format(span_context.trace_id, "032x")

    if record["exception"]:
        log_format = f"{log_format}{{exception}}\n"

    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"],
            indent=2,
            compact=True,
            width=WIDTH,
        )
        log_format = f"{log_format}>>    <red>payload={{extra[payload]}}</red>\n"

    return log_format


def file_record_formatter(record: dict[str, Any]) -> str:  # pragma: no cover
    record["serialized"] = serialize(record)
    return "{serialized}\n"


def configure_logging() -> None:  # pragma: no cover
    """Configures logging."""
    intercept_handler = InterceptHandler()

    logging.basicConfig(handlers=[intercept_handler], level=logging.NOTSET)

    for logger_name in logging.root.manager.loggerDict:
        if logger_name.startswith("uvicorn."):
            logging.getLogger(logger_name).handlers = []
        {%- if cookiecutter.enable_taskiq == "True" %}
        if logger_name.startswith("taskiq."):
            logging.getLogger(logger_name).root.handlers = [intercept_handler]
        {%- endif %}

    # change handler for default uvicorn logger
    logging.getLogger("uvicorn").handlers = [intercept_handler]
    logging.getLogger("uvicorn.access").handlers = [intercept_handler]

    # set logs output, level and format
    logger.remove()

    logger.add(
        sys.stdout,
        level=settings.log_level.value,
        format=record_formatter,  # type: ignore
    )

    logger.add(
        "logs/log_{time:YYYY-MM-DD}.log",
        rotation="500 MB",
        retention="10 days",
        compression="zip",
        level=settings.log_level.value,
        format=file_record_formatter,  # type: ignore
    )


def logger_wraps(*, entry=True, exit=True, level="DEBUG"):  # type: ignore
    def wrapper(func) -> Any:  # type: ignore
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):  # type: ignore
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(level, "Entering '{}' (args={}, kwargs={})", name, args, kwargs)
            result = func(*args, **kwargs)
            if exit:
                logger_.log(level, "Exiting '{}' (result={})", name, result)
            return result

        return wrapped

    return wrapper
