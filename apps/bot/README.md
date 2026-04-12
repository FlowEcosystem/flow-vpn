# Flow VPN Bot

Telegram bot for Flow VPN.

Current responsibility of the bot:
- user onboarding and authentication entrypoints;
- subscription and payment-related flows;
- VPN access delivery and account lifecycle actions;
- notifications, reminders, and support routing.

Current technical state:
- `aiogram 3` as transport layer;
- `dishka` for dependency injection;
- `SQLAlchemy + asyncpg + PostgreSQL` for persistence;
- `Alembic` for schema migrations;
- `UnitOfWork` boundary for transactional use cases;
- config-based admin access via `ADMIN_IDS_RAW`;
- layered structure: `app / application / infrastructure / presentation`.

The project is managed with PDM and targets Python 3.12.
