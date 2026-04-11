# Flow VPN

<p align="center">
  <strong>Цифровой контур VPN-платформы</strong><br />
  web, Telegram bot и инфраструктура в одном монорепозитории.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/zone-monorepo-0f172a?style=for-the-badge" alt="Monorepo" />
  <img src="https://img.shields.io/badge/web-Vue-00b894?style=for-the-badge&logo=vuedotjs&logoColor=white" alt="Vue" />
  <img src="https://img.shields.io/badge/bot-aiogram%203-0984e3?style=for-the-badge&logo=telegram&logoColor=white" alt="Aiogram" />
  <img src="https://img.shields.io/badge/python-3.12-1f6feb?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12" />
  <img src="https://img.shields.io/badge/pdm-package%20manager-6c5ce7?style=for-the-badge" alt="PDM" />
  <img src="https://img.shields.io/badge/docker-compose-161b22?style=for-the-badge&logo=docker&logoColor=2496ED" alt="Docker Compose" />
</p>

> `Flow VPN` собирается как единая система: интерфейс, бот и infra-слой живут рядом, но не смешиваются.

## Обзор

Репозиторий построен как компактный monorepo с жёстким разделением зон ответственности:

- `apps/web` — будущий пользовательский интерфейс на Vue
- `apps/bot` — Telegram-бот на Python + `aiogram`
- `infra/docker` — локальный и production-style orchestration через Docker Compose

Сейчас это уже не пустой каркас:

- бот запускается и отвечает на `/start`
- есть базовая структура модулей под рост проекта
- Docker-слой разбит на `base / dev / prod`
- заложены `Postgres`, `Redis`, `Traefik` и monitoring-контур

## Контуры Системы

| Контур | Назначение | Стек | Статус |
| --- | --- | --- | --- |
| `apps/web` | Внешний пользовательский слой | `Vue` | зона под bootstrap фронта |
| `apps/bot` | Командный интерфейс: onboarding, доступы, уведомления, support-flows | `Python 3.12`, `aiogram 3`, `PDM` | есть рабочая стартовая база |
| `infra/docker` | Сетевой и сервисный контур проекта | `Docker Compose`, `Traefik`, `Postgres`, `Redis` | dev/prod-оверлеи уже собраны |

## Стек

- Frontend: `Vue`
- Bot: `Python 3.12`, `aiogram 3`, `PDM`, `pydantic-settings`
- Data: `Postgres`, `Redis`, `SQLAlchemy`, `Alembic`
- Infra: `Docker Compose`, `Traefik`
- Observability: `Grafana`, `Prometheus`, `Loki`, `Promtail`

## Структура Репозитория

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

## Bot Layer

Текущий бот минимальный по поведению, но собран правильно по форме:

- `/start` handler
- echo для текстовых сообщений
- загрузка конфигурации из `.env`
- router-based раскладка под будущие feature-модули
- выделенные слои `services`, `repositories`, `middlewares`, `states`, `utils`

Точка входа:

```bash
apps/bot/src/main.py
```

## Docker Topology

Docker-конфигурация построена по схеме `base + overrides`:

- `infra/docker/compose.yml` — общий базовый слой
- `infra/docker/compose.dev.yml` — локальная разработка, bind mounts, открытые порты
- `infra/docker/compose.prod.yml` — reverse proxy, production-style wiring, monitoring profile

Это даёт предсказуемую модель:

- общее описывается один раз
- dev не засоряет prod
- prod не тащит в себя developer-специфику

## Developer Workflow

### 1. Локальный запуск бота

```bash
cd apps/bot
cp .env.example .env
```

Заполни `BOT_TOKEN`, затем запусти:

```bash
pdm run start
```

### 2. Локальный запуск всего контура

```bash
docker compose -f infra/docker/compose.yml -f infra/docker/compose.dev.yml up --build
```

Поднимутся:

- `web`
- `bot`
- `postgres`
- `redis`

### 3. Production-style запуск

```bash
docker compose -f infra/docker/compose.yml -f infra/docker/compose.prod.yml up --build -d
```

С monitoring-профилем:

```bash
docker compose -f infra/docker/compose.yml -f infra/docker/compose.prod.yml --profile monitoring up --build -d
```

## Roadmap

- [x] Собрать monorepo-структуру для `apps` и `infra`
- [x] Разделить Compose на `base / dev / prod`
- [x] Поднять Python bot-проект на `PDM`
- [x] Добавить стартового `aiogram`-бота
- [ ] Забутстрапить Vue-приложение в `apps/web`
- [ ] Вынести реальные bot-домены: auth, subscriptions, payments, support
- [ ] Добавить persistence layer и модели
- [ ] Подключить middleware, FSM-сцены и keyboards
- [ ] Усилить production-конфигурацию: secrets, TLS, hardening
- [ ] Добавить CI на lint, tests и compose validation

## Заметки

- В репозитории используется только корневой Git, вложенные `.git` не применяются.
- Корневой `.gitignore` уже закрывает Python-кэш, virtualenv, Node-артефакты и локальные `.env`.
- Текущий `prod`-compose — это сильная заготовка под деплой, но не финальный hardened production.
