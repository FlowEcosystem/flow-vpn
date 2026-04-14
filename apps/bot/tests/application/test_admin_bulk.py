from uuid import uuid4

from src.application.admin import (
    ADMIN_BULK_ACTION_ISSUE,
    AdminBulkOperationsService,
    AdminUsersFilter,
)
from src.application.users import UserSummary
from tests.application.test_admin_vpn import (
    FakeProvisioningGateway,
    FakeUsersOverviewUnitOfWork,
    FakeVpnAccessUnitOfWork,
    make_admin_service,
)
from tests.conftest import FakeUsersUnitOfWork, build_user


async def test_collect_target_telegram_ids_collects_all_pages() -> None:
    users = tuple(
        UserSummary(
            id=build_user(telegram_id=1000 + index).id,
            telegram_id=1000 + index,
            username=f"user{index}",
            first_name=f"User {index}",
            last_name=None,
            is_premium=False,
            has_vpn_access=index % 2 == 0,
            created_at=build_user(telegram_id=1000 + index).created_at,
        )
        for index in range(55)
    )
    admin = make_admin_service(
        FakeUsersOverviewUnitOfWork(users),
        FakeVpnAccessUnitOfWork(),
        FakeProvisioningGateway(),
    )
    service = AdminBulkOperationsService(database=object())  # type: ignore[arg-type]

    target_ids = await service.collect_target_telegram_ids(
        admin=admin,
        current_filter=AdminUsersFilter.ALL,
    )

    assert len(target_ids) == 55
    assert target_ids[0] == 1000
    assert target_ids[-1] == 1054


async def test_execute_operation_for_user_issue_passes_bulk_operation_id() -> None:
    user = build_user()
    admin = make_admin_service(
        FakeUsersUnitOfWork(user),
        FakeVpnAccessUnitOfWork(),
        FakeProvisioningGateway(),
    )
    service = AdminBulkOperationsService(database=object())  # type: ignore[arg-type]
    operation_id = uuid4()

    affected, ok = await service.execute_operation_for_user(
        admin=admin,
        current_operation_id=operation_id,
        source_operation_id=None,
        action=ADMIN_BULK_ACTION_ISSUE,
        telegram_id=user.telegram_id,
        admin_telegram_id=999,
    )

    assert (affected, ok) == (1, True)
    event = admin._vpn_access_uow.vpn_access_events.created[-1]  # type: ignore[attr-defined]
    assert event.details["bulk_operation_id"] == str(operation_id)
    assert "access_id" in event.details
