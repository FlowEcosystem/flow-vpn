import logging
import sys

import structlog


def setup_logging(*, json_logs: bool = False) -> None:
    """Configure structlog + stdlib logging.

    In dev (json_logs=False): colored human-readable output.
    In prod (json_logs=True): JSON per line — ready for Grafana Loki via promtail/alloy.

    All logs (structlog-native and aiogram/sqlalchemy stdlib) go through the same
    ProcessorFormatter so every line has the same schema.
    """
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    final_renderer: structlog.types.Processor = (
        structlog.processors.JSONRenderer() if json_logs else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        # Pre-chain runs on records that come from stdlib loggers (aiogram, sqlalchemy, etc.)
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            final_renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    # aiogram logs every handled update at INFO — too noisy for prod
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)
