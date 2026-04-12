# ruff: noqa: RUF001

from src.application.runtime import AccessMode
from src.application.runtime.ports import RuntimeSettingsUnitOfWork
from src.application.users.ports import UsersUnitOfWork
from src.application.vpn.dto import (
    AcquireVpnAccessOutcome,
    AcquireVpnAccessResult,
    NewVpnAccessData,
    NewVpnAccessEventData,
)
from src.application.vpn.ports import VpnAccessUnitOfWork, VpnProvisioningGateway


class AcquireVpnAccessUseCase:
    def __init__(
        self,
        users_uow: UsersUnitOfWork,
        runtime_settings_uow: RuntimeSettingsUnitOfWork,
        vpn_access_uow: VpnAccessUnitOfWork,
        provisioning_gateway: VpnProvisioningGateway,
    ) -> None:
        self._users_uow = users_uow
        self._runtime_settings_uow = runtime_settings_uow
        self._vpn_access_uow = vpn_access_uow
        self._provisioning_gateway = provisioning_gateway

    async def execute(self, telegram_id: int) -> AcquireVpnAccessResult:
        async with self._users_uow:
            user = await self._users_uow.users.get_by_telegram_id(telegram_id)

        if user is None:
            return AcquireVpnAccessResult(
                outcome=AcquireVpnAccessOutcome.USER_NOT_FOUND,
                message="Профиль не найден. Отправьте /start ещё раз.",
            )

        async with self._runtime_settings_uow:
            access_mode = await self._runtime_settings_uow.settings.get_access_mode()

        if access_mode is AccessMode.BILLING_ENABLED:
            return AcquireVpnAccessResult(
                outcome=AcquireVpnAccessOutcome.BILLING_REQUIRED,
                message=(
                    "Сейчас подключение оформляется по подписке. "
                    "Скоро здесь появится выбор тарифа."
                ),
            )

        async with self._vpn_access_uow:
            existing_access = await self._vpn_access_uow.vpn_accesses.get_by_user_id(user.id)
            if existing_access is not None:
                return AcquireVpnAccessResult(
                    outcome=AcquireVpnAccessOutcome.ACTIVE,
                    access=existing_access,
                )

        try:
            provisioned_access = await self._provisioning_gateway.provision_vless_access(user)
        except ValueError:
            return AcquireVpnAccessResult(
                outcome=AcquireVpnAccessOutcome.PROVIDER_NOT_CONFIGURED,
                message=(
                    "Сейчас выдача доступа временно недоступна. "
                    "Попробуйте чуть позже или напишите в поддержку."
                ),
            )
        except RuntimeError:
            return AcquireVpnAccessResult(
                outcome=AcquireVpnAccessOutcome.PROVIDER_ERROR,
                message=(
                    "Не удалось подготовить подключение прямо сейчас. "
                    "Попробуйте ещё раз немного позже."
                ),
            )

        async with self._vpn_access_uow:
            access = await self._vpn_access_uow.vpn_accesses.create(
                NewVpnAccessData(
                    user_id=user.id,
                    provider=provisioned_access.provider,
                    status=provisioned_access.status,
                    external_username=provisioned_access.external_username,
                    subscription_url=provisioned_access.subscription_url,
                    vless_links=provisioned_access.vless_links,
                    issued_at=provisioned_access.issued_at,
                    expires_at=provisioned_access.expires_at,
                )
            )
            await self._vpn_access_uow.vpn_access_events.create(
                NewVpnAccessEventData(
                    user_id=user.id,
                    access_id=access.id,
                    event_type="issued",
                    actor_telegram_id=user.telegram_id,
                    details={"source": "user_flow"},
                )
            )
            await self._vpn_access_uow.commit()

        return AcquireVpnAccessResult(
            outcome=AcquireVpnAccessOutcome.ACTIVE,
            access=access,
        )
