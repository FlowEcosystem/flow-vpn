from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update

from src.application.admin.dto import AdminBulkOperationInfo, AdminUsersFilter
from src.application.admin.use_cases import AdminService
from src.infrastructure.database import Database
from src.infrastructure.database.models.admin_bulk_operation import (
    AdminBulkOperation as AdminBulkOperationModel,
)
from src.infrastructure.database.models.user import User as UserModel
from src.infrastructure.database.models.vpn_access_event import (
    VpnAccessEvent as VpnAccessEventModel,
)

from .dto import (
    ADMIN_BULK_ACTION_DELETE,
    ADMIN_BULK_ACTION_DISABLE,
    ADMIN_BULK_ACTION_ISSUE,
    ADMIN_BULK_ACTION_ROLLBACK_DISABLE,
    ADMIN_BULK_ACTION_ROLLBACK_ISSUE,
    BULK_USERS_PAGE_SIZE,
    AdminBulkOperationSnapshot,
)


def get_admin_bulk_action_title(action: str) -> str:
    return {
        ADMIN_BULK_ACTION_ISSUE: "Массовая выдача подписок",
        ADMIN_BULK_ACTION_DISABLE: "Массовое отключение подписок",
        ADMIN_BULK_ACTION_DELETE: "Массовое удаление подписок",
        ADMIN_BULK_ACTION_ROLLBACK_ISSUE: "Откат массовой выдачи",
        ADMIN_BULK_ACTION_ROLLBACK_DISABLE: "Откат массового отключения",
    }.get(action, "Массовая операция")


def can_cancel_admin_bulk_operation(operation: AdminBulkOperationSnapshot) -> bool:
    return operation.status in {"pending", "running"}


def can_rollback_admin_bulk_operation(operation: AdminBulkOperationSnapshot) -> bool:
    return operation.status == "done" and operation.action in {
        ADMIN_BULK_ACTION_ISSUE,
        ADMIN_BULK_ACTION_DISABLE,
    }


def map_admin_bulk_operation(
    operation: AdminBulkOperationModel,
) -> AdminBulkOperationSnapshot:
    return AdminBulkOperationSnapshot(
        id=operation.id,
        admin_telegram_id=operation.admin_telegram_id,
        action=operation.action,
        source_operation_id=operation.source_operation_id,
        target_segment=operation.target_segment,
        source_page=operation.source_page,
        is_global=operation.is_global,
        status=operation.status,
        total_users=operation.total_users,
        processed_users=operation.processed_users,
        affected_accesses=operation.affected_accesses,
        skipped_users=operation.skipped_users,
        failed_users=operation.failed_users,
        target_telegram_ids=tuple(operation.target_telegram_ids),
        message_chat_id=operation.message_chat_id,
        message_id=operation.message_id,
        last_error=operation.last_error,
        created_at=operation.created_at,
        started_at=operation.started_at,
        completed_at=operation.completed_at,
    )


def to_admin_bulk_operation_info(
    operation: AdminBulkOperationModel,
) -> AdminBulkOperationInfo:
    return AdminBulkOperationInfo(
        id=operation.id,
        admin_telegram_id=operation.admin_telegram_id,
        action=operation.action,
        source_operation_id=operation.source_operation_id,
        target_segment=operation.target_segment,
        source_page=operation.source_page,
        is_global=operation.is_global,
        status=operation.status,
        total_users=operation.total_users,
        processed_users=operation.processed_users,
        affected_accesses=operation.affected_accesses,
        skipped_users=operation.skipped_users,
        failed_users=operation.failed_users,
        last_error=operation.last_error,
        created_at=operation.created_at,
        started_at=operation.started_at,
        completed_at=operation.completed_at,
    )


class AdminBulkOperationsService:
    def __init__(self, database: Database) -> None:
        self._database = database

    async def collect_target_telegram_ids(
        self,
        *,
        admin: AdminService,
        current_filter: AdminUsersFilter,
        page_size: int = BULK_USERS_PAGE_SIZE,
    ) -> tuple[int, ...]:
        first_page = await admin.get_users_overview(
            page=0,
            page_size=page_size,
            current_filter=current_filter,
        )
        if first_page.total_filtered == 0:
            return ()

        target_telegram_ids = [user.telegram_id for user in first_page.recent_users]
        total_pages = max((first_page.total_filtered - 1) // page_size + 1, 1)
        for page in range(1, total_pages):
            batch = await admin.get_users_overview(
                page=page,
                page_size=page_size,
                current_filter=current_filter,
            )
            target_telegram_ids.extend(user.telegram_id for user in batch.recent_users)
        return tuple(target_telegram_ids)

    async def enqueue_operation(
        self,
        *,
        operation_id: UUID,
        admin_telegram_id: int,
        action: str,
        source_operation_id: UUID | None,
        target_segment: str,
        source_page: int,
        is_global: bool,
        target_telegram_ids: tuple[int, ...],
        message_chat_id: int,
        message_id: int,
    ) -> None:
        async with self._database.session_factory() as session:
            session.add(
                AdminBulkOperationModel(
                    id=operation_id,
                    admin_telegram_id=admin_telegram_id,
                    action=action,
                    source_operation_id=source_operation_id,
                    target_segment=target_segment,
                    source_page=source_page,
                    is_global=is_global,
                    status="pending",
                    total_users=len(target_telegram_ids),
                    processed_users=0,
                    affected_accesses=0,
                    skipped_users=0,
                    failed_users=0,
                    target_telegram_ids=list(target_telegram_ids),
                    message_chat_id=message_chat_id,
                    message_id=message_id,
                )
            )
            await session.commit()

    async def get_operation(
        self,
        operation_id: UUID,
    ) -> AdminBulkOperationSnapshot | None:
        async with self._database.session_factory() as session:
            operation = await session.get(AdminBulkOperationModel, operation_id)
            if operation is None:
                return None
            return map_admin_bulk_operation(operation)

    async def list_recent_operations(
        self,
        limit: int = 8,
    ) -> tuple[AdminBulkOperationInfo, ...]:
        async with self._database.session_factory() as session:
            stmt = (
                select(AdminBulkOperationModel)
                .order_by(AdminBulkOperationModel.created_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            return tuple(to_admin_bulk_operation_info(op) for op in result.scalars().all())

    async def get_next_operation_id(self) -> UUID | None:
        async with self._database.session_factory() as session:
            stmt = (
                select(AdminBulkOperationModel.id)
                .where(AdminBulkOperationModel.status.in_(("pending", "running")))
                .order_by(AdminBulkOperationModel.created_at.asc())
                .limit(1)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def set_operation_running(self, operation_id: UUID) -> None:
        async with self._database.session_factory() as session:
            await session.execute(
                update(AdminBulkOperationModel)
                .where(AdminBulkOperationModel.id == operation_id)
                .values(
                    status="running",
                    started_at=datetime.now(UTC),
                    last_error=None,
                )
            )
            await session.commit()

    async def cancel_operation(self, operation_id: UUID) -> None:
        async with self._database.session_factory() as session:
            operation = await session.get(AdminBulkOperationModel, operation_id)
            if operation is None:
                return

            values: dict[str, object] = {
                "status": "cancelled",
                "completed_at": datetime.now(UTC),
            }
            if operation.started_at is None:
                values["started_at"] = datetime.now(UTC)

            await session.execute(
                update(AdminBulkOperationModel)
                .where(AdminBulkOperationModel.id == operation_id)
                .values(**values)
            )
            await session.commit()

    async def finalize_cancelled_operation(
        self,
        *,
        operation_id: UUID,
        processed_users: int,
        affected_accesses: int,
        skipped_users: int,
        failed_users: int,
    ) -> None:
        async with self._database.session_factory() as session:
            await session.execute(
                update(AdminBulkOperationModel)
                .where(AdminBulkOperationModel.id == operation_id)
                .values(
                    status="cancelled",
                    processed_users=processed_users,
                    affected_accesses=affected_accesses,
                    skipped_users=skipped_users,
                    failed_users=failed_users,
                    completed_at=datetime.now(UTC),
                )
            )
            await session.commit()

    async def is_operation_cancelled(self, operation_id: UUID) -> bool:
        async with self._database.session_factory() as session:
            stmt = select(AdminBulkOperationModel.status).where(
                AdminBulkOperationModel.id == operation_id
            )
            result = await session.execute(stmt)
            status = result.scalar_one_or_none()
            return status == "cancelled"

    async def update_operation_progress(
        self,
        *,
        operation_id: UUID,
        processed_users: int,
        affected_accesses: int,
        skipped_users: int,
        failed_users: int,
    ) -> None:
        async with self._database.session_factory() as session:
            await session.execute(
                update(AdminBulkOperationModel)
                .where(AdminBulkOperationModel.id == operation_id)
                .values(
                    status="running",
                    processed_users=processed_users,
                    affected_accesses=affected_accesses,
                    skipped_users=skipped_users,
                    failed_users=failed_users,
                    last_error=None,
                )
            )
            await session.commit()

    async def complete_operation(
        self,
        *,
        operation_id: UUID,
        processed_users: int,
        affected_accesses: int,
        skipped_users: int,
        failed_users: int,
    ) -> None:
        async with self._database.session_factory() as session:
            await session.execute(
                update(AdminBulkOperationModel)
                .where(AdminBulkOperationModel.id == operation_id)
                .values(
                    status="done",
                    processed_users=processed_users,
                    affected_accesses=affected_accesses,
                    skipped_users=skipped_users,
                    failed_users=failed_users,
                    completed_at=datetime.now(UTC),
                    last_error=None,
                )
            )
            await session.commit()

    async def fail_operation(
        self,
        *,
        operation_id: UUID,
        processed_users: int,
        affected_accesses: int,
        skipped_users: int,
        failed_users: int,
        error_message: str,
    ) -> None:
        async with self._database.session_factory() as session:
            await session.execute(
                update(AdminBulkOperationModel)
                .where(AdminBulkOperationModel.id == operation_id)
                .values(
                    status="failed",
                    processed_users=processed_users,
                    affected_accesses=affected_accesses,
                    skipped_users=skipped_users,
                    failed_users=failed_users,
                    completed_at=datetime.now(UTC),
                    last_error=error_message[:1000],
                )
            )
            await session.commit()

    async def get_bulk_operation_access_ids_for_user(
        self,
        *,
        source_operation_id: UUID,
        telegram_id: int,
        event_type: str,
    ) -> tuple[UUID, ...]:
        async with self._database.session_factory() as session:
            result = await session.execute(
                select(VpnAccessEventModel)
                .join(UserModel, UserModel.id == VpnAccessEventModel.user_id)
                .where(
                    UserModel.telegram_id == telegram_id,
                    VpnAccessEventModel.event_type == event_type,
                )
                .order_by(VpnAccessEventModel.created_at.asc())
            )
            access_ids: list[UUID] = []
            seen: set[UUID] = set()
            for event in result.scalars().all():
                if event.details.get("bulk_operation_id") != str(source_operation_id):
                    continue
                access_id_raw = event.details.get("access_id")
                if not access_id_raw:
                    continue
                try:
                    access_id = UUID(access_id_raw)
                except ValueError:
                    continue
                if access_id in seen:
                    continue
                seen.add(access_id)
                access_ids.append(access_id)
            return tuple(access_ids)

    async def execute_operation_for_user(
        self,
        *,
        admin: AdminService,
        current_operation_id: UUID,
        source_operation_id: UUID | None,
        action: str,
        telegram_id: int,
        admin_telegram_id: int,
    ) -> tuple[int, bool]:
        if action == ADMIN_BULK_ACTION_ISSUE:
            detail = await admin.issue_access(
                telegram_id,
                actor_telegram_id=admin_telegram_id,
                extra_event_details={"bulk_operation_id": str(current_operation_id)},
            )
            return (1, detail is not None)

        if action == ADMIN_BULK_ACTION_DISABLE:
            detail = await admin.get_user_detail(telegram_id)
            if detail is None:
                return 0, False

            active_accesses = [access for access in detail.vpn_accesses if access.status == "active"]
            if not active_accesses:
                return 0, True

            affected = 0
            for access in active_accesses:
                result = await admin.disable_access(
                    access.id,
                    actor_telegram_id=admin_telegram_id,
                    extra_event_details={"bulk_operation_id": str(current_operation_id)},
                )
                if result is None:
                    return affected, False
                affected += 1
            return affected, True

        if action == ADMIN_BULK_ACTION_DELETE:
            detail = await admin.get_user_detail(telegram_id)
            if detail is None:
                return 0, False

            if not detail.vpn_accesses:
                return 0, True

            affected = 0
            for access in detail.vpn_accesses:
                result = await admin.delete_access(
                    access.id,
                    actor_telegram_id=admin_telegram_id,
                    extra_event_details={"bulk_operation_id": str(current_operation_id)},
                )
                if result is None:
                    return affected, False
                affected += 1
            return affected, True

        if action == ADMIN_BULK_ACTION_ROLLBACK_DISABLE:
            if source_operation_id is None:
                return 0, False

            access_ids = await self.get_bulk_operation_access_ids_for_user(
                source_operation_id=source_operation_id,
                telegram_id=telegram_id,
                event_type="disabled_by_admin",
            )
            if not access_ids:
                return 0, True

            affected = 0
            for access_id in access_ids:
                result = await admin.enable_access(
                    access_id,
                    actor_telegram_id=admin_telegram_id,
                    extra_event_details={"bulk_operation_id": str(current_operation_id)},
                )
                if result is None:
                    continue
                affected += 1
            return affected, True

        if action == ADMIN_BULK_ACTION_ROLLBACK_ISSUE:
            if source_operation_id is None:
                return 0, False

            access_ids = await self.get_bulk_operation_access_ids_for_user(
                source_operation_id=source_operation_id,
                telegram_id=telegram_id,
                event_type="issued_by_admin",
            )
            if not access_ids:
                return 0, True

            affected = 0
            for access_id in access_ids:
                result = await admin.delete_access(
                    access_id,
                    actor_telegram_id=admin_telegram_id,
                    extra_event_details={"bulk_operation_id": str(current_operation_id)},
                )
                if result is None:
                    continue
                affected += 1
            return affected, True

        raise ValueError(f"Unknown admin bulk action: {action}")
