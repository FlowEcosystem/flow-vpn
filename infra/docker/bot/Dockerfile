FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PDM_CHECK_UPDATE=false \
    PDM_USE_VENV=false

WORKDIR /app

RUN python -m pip install --upgrade pip && \
    pip install "pdm[locked]>=2.26,<2.27"

COPY apps/bot/ ./

RUN if [ -f pyproject.toml ]; then \
      pdm install --prod --no-self; \
    fi

CMD ["sh", "-c", "if [ -f src/main.py ]; then pdm run alembic upgrade head && pdm run python -m src.main; else echo 'apps/bot has no src/main.py yet'; sleep infinity; fi"]
