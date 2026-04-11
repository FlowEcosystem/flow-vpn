# Flow VPN

<p align="center">
  <strong>VPN platform monorepo</strong><br />
  Vue web app, Telegram bot, and Docker-based infrastructure in one repository.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/monorepo-apps%20%2B%20infra-111827?style=for-the-badge" alt="Monorepo" />
  <img src="https://img.shields.io/badge/web-Vue-42b883?style=for-the-badge&logo=vuedotjs&logoColor=white" alt="Vue" />
  <img src="https://img.shields.io/badge/bot-aiogram%203-2F80ED?style=for-the-badge&logo=telegram&logoColor=white" alt="Aiogram" />
  <img src="https://img.shields.io/badge/python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12" />
  <img src="https://img.shields.io/badge/package%20manager-PDM-C084FC?style=for-the-badge" alt="PDM" />
  <img src="https://img.shields.io/badge/docker-compose-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Compose" />
</p>

---

## Overview

`Flow VPN` is a compact monorepo with a strict separation between product code and infrastructure:

- `apps/web` contains the future user-facing frontend on Vue
- `apps/bot` contains the Telegram bot on Python + `aiogram`
- `infra/docker` contains environment orchestration for development and production-style deployment

The repo is already prepared as a scalable base: the bot has a runnable starter implementation, Docker is split into `base / dev / prod`, and the project layout is ready for feature growth without turning into a dump of random folders.

## Project Cards

| Area | Role | Stack | Current State |
| --- | --- | --- | --- |
| `apps/web` | User-facing product UI | `Vue` | Scaffold zone, ready for frontend bootstrap |
| `apps/bot` | Telegram interface for onboarding, access flows, notifications | `Python 3.12`, `aiogram 3`, `PDM` | Running starter bot with `/start` and echo flow |
| `infra/docker` | Local and production-style orchestration | `Docker Compose`, `Traefik`, `Postgres`, `Redis` | Base, dev, prod, and monitoring profiles prepared |

## Stack

- Frontend: `Vue`
- Bot: `Python 3.12`, `aiogram 3`, `PDM`, `pydantic-settings`
- Data layer: `Postgres`, `Redis`, `SQLAlchemy`, `Alembic`
- Infra: `Docker Compose`, `Traefik`
- Observability: `Grafana`, `Prometheus`, `Loki`, `Promtail`

## Repository Layout

```text
flow-vpn/
├── apps/
│   ├── bot/
│   │   ├── pyproject.toml
│   │   ├── pdm.lock
│   │   ├── src/
│   │   │   ├── core/
│   │   │   ├── handlers/
│   │   │   ├── keyboards/
│   │   │   ├── middlewares/
│   │   │   ├── repositories/
│   │   │   ├── services/
│   │   │   ├── states/
│   │   │   └── utils/
│   │   └── tests/
│   └── web/
├── infra/
│   └── docker/
│       ├── compose.yml
│       ├── compose.dev.yml
│       ├── compose.prod.yml
│       ├── bot/
│       ├── web/
│       ├── traefik/
│       └── monitoring/
└── README.md
```

## Bot Snapshot

The current Telegram bot is intentionally minimal, but the base is already clean:

- `/start` handler
- text echo handler
- config loading from `.env`
- router-based layout for future feature modules
- dedicated folders for `services`, `repositories`, `middlewares`, `states`, and `utils`

Entrypoint:

```bash
apps/bot/src/main.py
```

## Compose Model

The Docker layer uses a `base + overrides` approach:

- `infra/docker/compose.yml` defines shared services and common wiring
- `infra/docker/compose.dev.yml` adds bind mounts, open ports, and local developer behavior
- `infra/docker/compose.prod.yml` adds reverse proxy, production-style routing, and optional monitoring services

This keeps shared logic in one place and keeps environment-specific behavior explicit.

## Developer Workflow

### 1. Bot-only local run

```bash
cd apps/bot
cp .env.example .env
```

Fill in `BOT_TOKEN`, then run:

```bash
pdm run start
```

### 2. Full local stack in Docker

```bash
docker compose -f infra/docker/compose.yml -f infra/docker/compose.dev.yml up --build
```

This starts:

- `web`
- `bot`
- `postgres`
- `redis`

### 3. Production-style stack

```bash
docker compose -f infra/docker/compose.yml -f infra/docker/compose.prod.yml up --build -d
```

With monitoring:

```bash
docker compose -f infra/docker/compose.yml -f infra/docker/compose.prod.yml --profile monitoring up --build -d
```

## Roadmap

- [x] Define monorepo structure for apps and infra
- [x] Set up Docker Compose base, dev, and prod layers
- [x] Prepare Python bot project on `PDM`
- [x] Add starter `aiogram` bot with `/start` and echo flow
- [ ] Bootstrap the Vue application in `apps/web`
- [ ] Add real bot domains: auth, subscriptions, payments, support
- [ ] Introduce database models and persistence layer
- [ ] Add middleware, FSM flows, and keyboards
- [ ] Harden production config, secrets, and TLS
- [ ] Add CI checks for linting, tests, and compose validation

## Notes

- Only the root Git repository is present; nested `.git` repositories are not used.
- Root `.gitignore` already covers Python caches, virtualenvs, Node artifacts, and local environment files.
- Current production compose is a strong scaffold, not a fully hardened deployment yet.
