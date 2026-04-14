from collections.abc import AsyncIterator

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from dishka.integrations.aiogram import AiogramProvider
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.config import Settings
from src.application.account import AccountService
from src.application.admin import AdminBulkOperationsService, AdminService
from src.application.broadcasts import BroadcastsService, BroadcastsUnitOfWork
from src.application.promos import PromoService, PromosUnitOfWork
from src.application.referrals import ReferralsService
from src.application.reviews import ReviewsService, ReviewsUnitOfWork
from src.application.runtime import RuntimeSettingsService, RuntimeSettingsUnitOfWork
from src.application.status import ServiceStatusGateway, StatusService
from src.application.support import SupportService, SupportUnitOfWork
from src.application.users import UsersService, UsersUnitOfWork
from src.application.vpn import VpnAccessUnitOfWork, VpnProvisioningGateway, VpnService
from src.infrastructure.database import Database
from src.infrastructure.providers import (
    MarzbanServiceStatusGateway,
    MarzbanVpnProvisioningGateway,
)
from src.infrastructure.redis import create_redis
from src.infrastructure.repositories import (
    SqlAlchemyBroadcastsRepository,
    SqlAlchemyPromoCodesRepository,
    SqlAlchemyPromoRedemptionsRepository,
    SqlAlchemyReviewsRepository,
    SqlAlchemyRuntimeSettingsRepository,
    SqlAlchemySupportTicketsRepository,
    SqlAlchemyUsersRepository,
    SqlAlchemyVpnAccessEventRepository,
    SqlAlchemyVpnAccessRepository,
)
from src.infrastructure.uow import (
    SqlAlchemyBroadcastsUnitOfWork,
    SqlAlchemyPromosUnitOfWork,
    SqlAlchemyReviewsUnitOfWork,
    SqlAlchemyRuntimeSettingsUnitOfWork,
    SqlAlchemySupportUnitOfWork,
    SqlAlchemyUsersUnitOfWork,
    SqlAlchemyVpnAccessUnitOfWork,
)


class AppProvider(Provider):
    provisioning_gateway = provide(
        source=MarzbanVpnProvisioningGateway,
        provides=VpnProvisioningGateway,
        scope=Scope.APP,
    )
    service_status_gateway = provide(
        source=MarzbanServiceStatusGateway,
        provides=ServiceStatusGateway,
        scope=Scope.APP,
    )
    promo_codes_repository = provide(SqlAlchemyPromoCodesRepository, scope=Scope.REQUEST)
    promo_redemptions_repository = provide(
        SqlAlchemyPromoRedemptionsRepository,
        scope=Scope.REQUEST,
    )
    reviews_repository = provide(SqlAlchemyReviewsRepository, scope=Scope.REQUEST)
    runtime_settings_repository = provide(SqlAlchemyRuntimeSettingsRepository, scope=Scope.REQUEST)
    users_repository = provide(SqlAlchemyUsersRepository, scope=Scope.REQUEST)
    vpn_access_event_repository = provide(SqlAlchemyVpnAccessEventRepository, scope=Scope.REQUEST)
    broadcasts_repository = provide(SqlAlchemyBroadcastsRepository, scope=Scope.REQUEST)
    support_tickets_repository = provide(SqlAlchemySupportTicketsRepository, scope=Scope.REQUEST)
    vpn_access_repository = provide(SqlAlchemyVpnAccessRepository, scope=Scope.REQUEST)
    promos_uow = provide(
        source=SqlAlchemyPromosUnitOfWork,
        provides=PromosUnitOfWork,
        scope=Scope.REQUEST,
    )
    reviews_uow = provide(
        source=SqlAlchemyReviewsUnitOfWork,
        provides=ReviewsUnitOfWork,
        scope=Scope.REQUEST,
    )
    runtime_settings_uow = provide(
        source=SqlAlchemyRuntimeSettingsUnitOfWork,
        provides=RuntimeSettingsUnitOfWork,
        scope=Scope.REQUEST,
    )
    users_uow = provide(
        source=SqlAlchemyUsersUnitOfWork,
        provides=UsersUnitOfWork,
        scope=Scope.REQUEST,
    )
    broadcasts_uow = provide(
        source=SqlAlchemyBroadcastsUnitOfWork,
        provides=BroadcastsUnitOfWork,
        scope=Scope.REQUEST,
    )
    support_uow = provide(
        source=SqlAlchemySupportUnitOfWork,
        provides=SupportUnitOfWork,
        scope=Scope.REQUEST,
    )
    vpn_access_uow = provide(
        source=SqlAlchemyVpnAccessUnitOfWork,
        provides=VpnAccessUnitOfWork,
        scope=Scope.REQUEST,
    )

    # Services
    vpn_service = provide(VpnService, scope=Scope.REQUEST)
    promo_service = provide(PromoService, scope=Scope.REQUEST)
    reviews_service = provide(ReviewsService, scope=Scope.REQUEST)
    broadcasts_service = provide(BroadcastsService, scope=Scope.REQUEST)
    support_service = provide(SupportService, scope=Scope.REQUEST)
    runtime_settings_service = provide(RuntimeSettingsService, scope=Scope.REQUEST)
    admin_service = provide(AdminService, scope=Scope.REQUEST)
    admin_bulk_operations_service = provide(AdminBulkOperationsService, scope=Scope.APP)
    account_service = provide(AccountService, scope=Scope.REQUEST)
    referrals_service = provide(ReferralsService, scope=Scope.REQUEST)
    status_service = provide(StatusService, scope=Scope.REQUEST)
    users_service = provide(UsersService, scope=Scope.REQUEST)

    def __init__(self, *, settings: Settings, database: Database) -> None:
        super().__init__()
        self._settings = settings
        self._database = database

    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        return self._settings

    @provide(scope=Scope.APP)
    def get_database(self) -> Database:
        return self._database

    @provide(scope=Scope.APP)
    def get_redis(self, settings: Settings) -> Redis:
        return create_redis(settings)

    @provide(scope=Scope.REQUEST)
    async def get_session(self, database: Database) -> AsyncIterator[AsyncSession]:
        async with database.session_factory() as session:
            yield session


def create_container(*, settings: Settings, database: Database) -> AsyncContainer:
    return make_async_container(
        AppProvider(settings=settings, database=database),
        AiogramProvider(),
    )
