from collections.abc import AsyncIterator

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from dishka.integrations.aiogram import AiogramProvider
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.config import Settings
from src.application.account import GetTelegramAccountUseCase
from src.application.admin import (
    DisableAdminVpnAccessUseCase,
    GetAdminDashboardUseCase,
    GetAdminUserDetailUseCase,
    GetAdminUsersOverviewUseCase,
    IssueAdminVpnAccessUseCase,
    ReissueAdminVpnAccessUseCase,
    SearchAdminUsersUseCase,
)
from src.application.promos import (
    ApplyPromoCodeUseCase,
    GetPromoOverviewUseCase,
    PromosUnitOfWork,
)
from src.application.referrals import GetReferralOverviewUseCase
from src.application.reviews import (
    CreateReviewUseCase,
    GetReviewsOverviewUseCase,
    ReviewsUnitOfWork,
)
from src.application.runtime import (
    GetAccessModeUseCase,
    RuntimeSettingsUnitOfWork,
    SetAccessModeUseCase,
)
from src.application.status import GetServiceStatusUseCase, ServiceStatusGateway
from src.application.support import GetSupportOverviewUseCase
from src.application.users import RegisterTelegramUserUseCase, UsersUnitOfWork
from src.application.vpn import (
    AcquireVpnAccessUseCase,
    VpnAccessUnitOfWork,
    VpnProvisioningGateway,
)
from src.infrastructure.database import Database
from src.infrastructure.providers import (
    MarzbanServiceStatusGateway,
    MarzbanVpnProvisioningGateway,
)
from src.infrastructure.repositories import (
    SqlAlchemyPromoCodesRepository,
    SqlAlchemyPromoRedemptionsRepository,
    SqlAlchemyReviewsRepository,
    SqlAlchemyRuntimeSettingsRepository,
    SqlAlchemyUsersRepository,
    SqlAlchemyVpnAccessEventRepository,
    SqlAlchemyVpnAccessRepository,
)
from src.infrastructure.uow import (
    SqlAlchemyPromosUnitOfWork,
    SqlAlchemyReviewsUnitOfWork,
    SqlAlchemyRuntimeSettingsUnitOfWork,
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
    vpn_access_uow = provide(
        source=SqlAlchemyVpnAccessUnitOfWork,
        provides=VpnAccessUnitOfWork,
        scope=Scope.REQUEST,
    )
    acquire_vpn_access = provide(AcquireVpnAccessUseCase, scope=Scope.REQUEST)
    apply_promo_code = provide(ApplyPromoCodeUseCase, scope=Scope.REQUEST)
    create_review = provide(CreateReviewUseCase, scope=Scope.REQUEST)
    get_access_mode = provide(GetAccessModeUseCase, scope=Scope.REQUEST)
    get_promo_overview = provide(GetPromoOverviewUseCase, scope=Scope.REQUEST)
    get_referral_overview = provide(GetReferralOverviewUseCase, scope=Scope.REQUEST)
    get_reviews_overview = provide(GetReviewsOverviewUseCase, scope=Scope.REQUEST)
    get_service_status = provide(GetServiceStatusUseCase, scope=Scope.REQUEST)
    get_support_overview = provide(GetSupportOverviewUseCase, scope=Scope.REQUEST)
    get_telegram_account = provide(GetTelegramAccountUseCase, scope=Scope.REQUEST)
    get_admin_dashboard = provide(GetAdminDashboardUseCase, scope=Scope.REQUEST)
    get_admin_user_detail = provide(GetAdminUserDetailUseCase, scope=Scope.REQUEST)
    get_admin_users_overview = provide(GetAdminUsersOverviewUseCase, scope=Scope.REQUEST)
    disable_admin_vpn_access = provide(DisableAdminVpnAccessUseCase, scope=Scope.REQUEST)
    issue_admin_vpn_access = provide(IssueAdminVpnAccessUseCase, scope=Scope.REQUEST)
    register_telegram_user = provide(RegisterTelegramUserUseCase, scope=Scope.REQUEST)
    reissue_admin_vpn_access = provide(ReissueAdminVpnAccessUseCase, scope=Scope.REQUEST)
    search_admin_users = provide(SearchAdminUsersUseCase, scope=Scope.REQUEST)
    set_access_mode = provide(SetAccessModeUseCase, scope=Scope.REQUEST)

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

    @provide(scope=Scope.REQUEST)
    async def get_session(self, database: Database) -> AsyncIterator[AsyncSession]:
        async with database.session_factory() as session:
            yield session


def create_container(*, settings: Settings, database: Database) -> AsyncContainer:
    return make_async_container(
        AppProvider(settings=settings, database=database),
        AiogramProvider(),
    )
