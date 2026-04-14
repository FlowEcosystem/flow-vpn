from types import SimpleNamespace

import httpx
import pytest

from src.app.config import Settings
from src.infrastructure.providers.marzban import MarzbanVpnProvisioningGateway


class FakeMarzbanClient:
    def __init__(self) -> None:
        self.created_usernames: list[str] = []
        self._create_attempt = 0

    async def __aenter__(self) -> "FakeMarzbanClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def post(self, url: str, *, data=None, headers=None, json=None) -> httpx.Response:
        request = httpx.Request("POST", f"https://marzban.local{url}")
        if url == "/api/admin/token":
            return httpx.Response(200, request=request, json={"access_token": "token"})

        if url == "/api/user":
            self._create_attempt += 1
            assert json is not None
            self.created_usernames.append(json["username"])
            if self._create_attempt == 1:
                return httpx.Response(409, request=request, json={"detail": "already exists"})

            return httpx.Response(
                200,
                request=request,
                json={
                    "username": json["username"],
                    "status": "active",
                    "subscription_url": "https://example.com/sub",
                    "links": ["vless://example"],
                    "created_at": "2026-04-12T17:43:18Z",
                    "expire": 0,
                },
            )

        raise AssertionError(f"Unexpected POST {url}")


@pytest.fixture
def marzban_settings() -> Settings:
    return Settings(
        bot_token="token",
        marzban_base_url="https://marzban.local",
        marzban_username="admin",
        marzban_password="secret",
    )


def test_build_username_uses_telegram_username_and_subscription_number(
    marzban_settings: Settings,
) -> None:
    gateway = MarzbanVpnProvisioningGateway(marzban_settings.model_copy())
    user = SimpleNamespace(username="Flow.User", telegram_id=875272633)

    username = gateway._build_username(user, 3)

    assert username == "flow_user_3"
    assert len(username) <= 32


def test_build_username_falls_back_to_telegram_id_when_username_missing(
    marzban_settings: Settings,
) -> None:
    gateway = MarzbanVpnProvisioningGateway(marzban_settings.model_copy())
    user = SimpleNamespace(username=None, telegram_id=875272633)

    username = gateway._build_username(user, 2)

    assert username == "tg_875272633_2"
    assert len(username) <= 32


@pytest.mark.asyncio
async def test_provision_retries_with_new_username_after_conflict(
    monkeypatch: pytest.MonkeyPatch,
    marzban_settings: Settings,
) -> None:
    fake_client = FakeMarzbanClient()
    gateway = MarzbanVpnProvisioningGateway(marzban_settings)
    user = SimpleNamespace(username="flow.user", telegram_id=875272633)

    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: fake_client)
    monkeypatch.setattr(
        "src.infrastructure.providers.marzban.uuid4",
        lambda: SimpleNamespace(hex="deadbeefcafebaad"),
    )

    access = await gateway.provision_vless_access(user, 2)

    assert access.external_username == fake_client.created_usernames[-1]
    assert len(fake_client.created_usernames) == 2
    assert fake_client.created_usernames[0] == "flow_user_2"
    assert fake_client.created_usernames[1] == "flow_user_2_deadbe"
