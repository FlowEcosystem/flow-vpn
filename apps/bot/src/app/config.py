from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    bot_proxy: str | None = None
    bot_public_username: str | None = None
    admin_ids_raw: str = ""
    support_url: str | None = None
    support_title: str = "Поддержка Flow VPN"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/flow_vpn"
    database_echo: bool = False
    log_json: bool = False
    redis_url: str = "redis://localhost:6379/0"
    rate_limit_requests: int = 25
    rate_limit_window_seconds: int = 60
    marzban_base_url: str | None = None
    marzban_username: str | None = None
    marzban_password: str | None = None
    marzban_user_prefix: str = "flow"
    marzban_vless_inbounds_raw: str = ""
    marzban_free_access_data_limit_bytes: int = 0
    marzban_free_access_expire_days: int = 0
    yookassa_shop_id: str | None = None
    yookassa_secret_key: str | None = None
    # Сколько рублей стоит 1 Telegram Star (для автоконвертации цен)
    stars_rub_rate: float = 1.8

    @property
    def yookassa_is_configured(self) -> bool:
        return bool(self.yookassa_shop_id and self.yookassa_secret_key)

    @property
    def admin_ids(self) -> frozenset[int]:
        if not self.admin_ids_raw.strip():
            return frozenset()

        values = (
            part.strip()
            for part in self.admin_ids_raw.split(",")
        )
        return frozenset(int(value) for value in values if value)

    def is_admin(self, telegram_user_id: int) -> bool:
        return telegram_user_id in self.admin_ids

    @property
    def marzban_vless_inbounds(self) -> tuple[str, ...]:
        if not self.marzban_vless_inbounds_raw.strip():
            return ()

        values = (
            part.strip()
            for part in self.marzban_vless_inbounds_raw.split(",")
        )
        return tuple(value for value in values if value)

    @property
    def marzban_is_configured(self) -> bool:
        return all(
            (
                self.marzban_base_url,
                self.marzban_username,
                self.marzban_password,
            )
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
