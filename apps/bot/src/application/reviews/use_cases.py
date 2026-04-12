from src.application.reviews.dto import ReviewsOverview
from src.application.reviews.ports import ReviewsUnitOfWork
from src.application.users import UsersUnitOfWork


class GetReviewsOverviewUseCase:
    def __init__(self, reviews_uow: ReviewsUnitOfWork) -> None:
        self._reviews_uow = reviews_uow

    async def execute(self, *, limit: int = 5) -> ReviewsOverview:
        async with self._reviews_uow:
            return await self._reviews_uow.reviews.get_overview(limit)


class CreateReviewUseCase:
    def __init__(
        self,
        users_uow: UsersUnitOfWork,
        reviews_uow: ReviewsUnitOfWork,
    ) -> None:
        self._users_uow = users_uow
        self._reviews_uow = reviews_uow

    async def execute(self, telegram_id: int, *, rating: int, text: str) -> bool:
        normalized_text = text.strip()
        if rating < 1 or rating > 5:
            raise ValueError("Оценка должна быть от 1 до 5.")
        if len(normalized_text) < 8:
            raise ValueError("Отзыв получился слишком коротким.")

        async with self._users_uow:
            user = await self._users_uow.users.get_by_telegram_id(telegram_id)

        if user is None:
            return False

        async with self._reviews_uow:
            await self._reviews_uow.reviews.create(
                user_id=user.id,
                rating=rating,
                text=normalized_text,
            )
            await self._reviews_uow.commit()
            return True
