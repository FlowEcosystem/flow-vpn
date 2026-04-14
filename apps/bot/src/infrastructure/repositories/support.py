import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.support.dto import (
    SupportTicketDetail,
    SupportTicketReplyItem,
    SupportTicketSummary,
)
from src.application.support.ports import SupportStats
from src.infrastructure.database.models.support_ticket import SupportTicket, SupportTicketReply
from src.infrastructure.database.models.user import User


class SqlAlchemySupportTicketsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, user_id: uuid.UUID, message: str) -> uuid.UUID:
        ticket = SupportTicket(user_id=user_id, message=message, status="open")
        self._session.add(ticket)
        await self._session.flush()
        await self._session.refresh(ticket)
        return ticket.id

    async def list_open(self, limit: int) -> tuple[SupportTicketSummary, ...]:
        reply_count_subq = (
            select(
                SupportTicketReply.ticket_id,
                func.count(SupportTicketReply.id).label("reply_count"),
            )
            .group_by(SupportTicketReply.ticket_id)
            .subquery()
        )

        stmt = (
            select(
                SupportTicket,
                User.telegram_id,
                User.first_name,
                User.username,
                func.coalesce(reply_count_subq.c.reply_count, 0).label("reply_count"),
            )
            .join(User, User.id == SupportTicket.user_id)
            .outerjoin(reply_count_subq, reply_count_subq.c.ticket_id == SupportTicket.id)
            .where(SupportTicket.status == "open")
            .order_by(SupportTicket.created_at.asc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return tuple(
            SupportTicketSummary(
                id=ticket.id,
                user_telegram_id=telegram_id,
                user_first_name=first_name,
                user_username=username,
                message=ticket.message,
                status=ticket.status,
                reply_count=int(reply_count),
                created_at=ticket.created_at,
            )
            for ticket, telegram_id, first_name, username, reply_count in result.all()
        )

    async def get_detail(self, ticket_id: uuid.UUID) -> SupportTicketDetail | None:
        stmt = (
            select(SupportTicket, User.telegram_id, User.first_name, User.username)
            .join(User, User.id == SupportTicket.user_id)
            .where(SupportTicket.id == ticket_id)
        )
        result = await self._session.execute(stmt)
        row = result.one_or_none()
        if row is None:
            return None
        ticket, telegram_id, first_name, username = row

        replies_stmt = (
            select(SupportTicketReply)
            .where(SupportTicketReply.ticket_id == ticket_id)
            .order_by(SupportTicketReply.created_at.asc())
        )
        replies_result = await self._session.execute(replies_stmt)
        replies = tuple(
            SupportTicketReplyItem(
                admin_telegram_id=r.admin_telegram_id,
                text=r.text,
                created_at=r.created_at,
            )
            for r in replies_result.scalars().all()
        )

        return SupportTicketDetail(
            id=ticket.id,
            user_telegram_id=telegram_id,
            user_first_name=first_name,
            user_username=username,
            message=ticket.message,
            status=ticket.status,
            replies=replies,
            created_at=ticket.created_at,
        )

    async def close(self, ticket_id: uuid.UUID) -> None:
        stmt = (
            update(SupportTicket)
            .where(SupportTicket.id == ticket_id)
            .values(status="closed")
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def add_reply(
        self,
        *,
        ticket_id: uuid.UUID,
        admin_telegram_id: int,
        text: str,
    ) -> None:
        reply = SupportTicketReply(
            ticket_id=ticket_id,
            admin_telegram_id=admin_telegram_id,
            text=text,
        )
        self._session.add(reply)
        await self._session.flush()

    async def rate(self, ticket_id: uuid.UUID, rating: int) -> bool:
        stmt = (
            update(SupportTicket)
            .where(SupportTicket.id == ticket_id)
            .where(SupportTicket.rating.is_(None))
            .values(rating=rating)
            .returning(SupportTicket.id)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.scalar_one_or_none() is not None

    async def get_stats(self) -> SupportStats:
        stmt = select(
            func.count().filter(SupportTicket.status == "closed").label("closed_count"),
            func.avg(SupportTicket.rating).label("avg_rating"),
            func.count(SupportTicket.rating).label("total_ratings"),
        )
        result = await self._session.execute(stmt)
        row = result.one()
        avg = float(row.avg_rating) if row.avg_rating is not None else None
        return SupportStats(
            closed_count=int(row.closed_count),
            average_rating=avg,
            total_ratings=int(row.total_ratings),
        )
