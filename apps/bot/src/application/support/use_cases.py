import uuid

import structlog

from src.app.config import Settings
from src.application.support.dto import SupportOverview, SupportTicketDetail, SupportTicketSummary
from src.application.support.ports import SupportUnitOfWork
from src.application.users.ports import UsersUnitOfWork

logger = structlog.get_logger(__name__)


class SupportService:
    def __init__(
        self,
        settings: Settings,
        users_uow: UsersUnitOfWork,
        support_uow: SupportUnitOfWork,
    ) -> None:
        self._settings = settings
        self._users_uow = users_uow
        self._support_uow = support_uow

    async def get_overview(self) -> SupportOverview:
        async with self._support_uow as uow:
            stats = await uow.tickets.get_stats()
        return SupportOverview(
            support_url=self._settings.support_url,
            support_title=self._settings.support_title,
            closed_tickets_count=stats.closed_count,
            average_support_rating=stats.average_rating,
            total_support_ratings=stats.total_ratings,
        )

    async def create_ticket(self, telegram_id: int, *, message: str) -> uuid.UUID | None:
        async with self._users_uow:
            user = await self._users_uow.users.get_by_telegram_id(telegram_id)

        if user is None:
            return None

        async with self._support_uow as uow:
            ticket_id = await uow.tickets.create(user_id=user.id, message=message)
            await uow.commit()

        logger.info("support_ticket_created", telegram_id=telegram_id, ticket_id=str(ticket_id))
        return ticket_id

    async def list_open_tickets(self, limit: int = 30) -> tuple[SupportTicketSummary, ...]:
        async with self._support_uow as uow:
            return await uow.tickets.list_open(limit)

    async def get_ticket_detail(self, ticket_id: uuid.UUID) -> SupportTicketDetail | None:
        async with self._support_uow as uow:
            return await uow.tickets.get_detail(ticket_id)

    async def reply_to_ticket(
        self,
        ticket_id: uuid.UUID,
        *,
        admin_telegram_id: int,
        text: str,
    ) -> SupportTicketDetail | None:
        async with self._support_uow as uow:
            detail = await uow.tickets.get_detail(ticket_id)
            if detail is None:
                return None
            await uow.tickets.add_reply(
                ticket_id=ticket_id,
                admin_telegram_id=admin_telegram_id,
                text=text,
            )
            await uow.commit()

        logger.info(
            "support_ticket_replied",
            ticket_id=str(ticket_id),
            admin_telegram_id=admin_telegram_id,
        )

        async with self._support_uow as uow:
            return await uow.tickets.get_detail(ticket_id)

    async def rate_ticket(
        self,
        telegram_id: int,
        ticket_id: uuid.UUID,
        rating: int,
    ) -> bool:
        """Rate a support ticket. Returns False if ticket not found, not owned, or already rated."""
        async with self._users_uow:
            user = await self._users_uow.users.get_by_telegram_id(telegram_id)
        if user is None:
            return False

        async with self._support_uow as uow:
            detail = await uow.tickets.get_detail(ticket_id)
            if detail is None or detail.user_telegram_id != telegram_id:
                return False
            rated = await uow.tickets.rate(ticket_id, rating)
            if rated:
                await uow.commit()

        logger.info(
            "support_ticket_rated",
            telegram_id=telegram_id,
            ticket_id=str(ticket_id),
            rating=rating,
        )
        return rated

    async def close_ticket(self, ticket_id: uuid.UUID) -> bool:
        async with self._support_uow as uow:
            detail = await uow.tickets.get_detail(ticket_id)
            if detail is None:
                return False
            await uow.tickets.close(ticket_id)
            await uow.commit()
        logger.info("support_ticket_closed", ticket_id=str(ticket_id))
        return True
