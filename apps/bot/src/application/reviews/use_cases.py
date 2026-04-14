import structlog

from src.application.reviews.dto import ReviewsOverview
from src.application.reviews.ports import ReviewsUnitOfWork
from src.application.users.ports import UsersUnitOfWork

logger = structlog.get_logger(__name__)


class ReviewsService:
    def __init__(
        self,
        users_uow: UsersUnitOfWork,
        reviews_uow: ReviewsUnitOfWork,
    ) -> None:
        self._users_uow = users_uow
        self._reviews_uow = reviews_uow

    async def get_overview(
        self,
        telegram_id: int | None = None,
        *,
        limit: int = 5,
    ) -> ReviewsOverview:
        viewer_user_id = None
        if telegram_id is not None:
            async with self._users_uow:
                user = await self._users_uow.users.get_by_telegram_id(telegram_id)
            if user is not None:
                viewer_user_id = user.id

        async with self._reviews_uow:
            return await self._reviews_uow.reviews.get_overview(
                limit,
                viewer_user_id=viewer_user_id,
            )

    async def create(self, telegram_id: int, *, rating: int, text: str) -> bool:
        if rating < 1 or rating > 5:
            raise ValueError("Оценка должна быть от 1 до 5.")

        normalized = text.strip()
        if normalized and len(normalized) < 3:
            raise ValueError("Слишком короткий текст — напишите хотя бы 3 символа.")

        async with self._users_uow:
            user = await self._users_uow.users.get_by_telegram_id(telegram_id)

        if user is None:
            return False

        async with self._reviews_uow:
            await self._reviews_uow.reviews.upsert(
                user_id=user.id,
                rating=rating,
                text=normalized,
            )
            await self._reviews_uow.commit()

        logger.info("review_submitted", telegram_id=telegram_id, rating=rating)
        return True
