from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.reviews import PublicReview, ReviewsOverview
from src.infrastructure.database.models import Review, User


class SqlAlchemyReviewsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_recent(self, limit: int) -> tuple[PublicReview, ...]:
        stmt = (
            select(Review, User.first_name, User.username)
            .join(User, User.id == Review.user_id)
            .order_by(Review.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return tuple(
            PublicReview(
                first_name=first_name,
                username=username,
                rating=review.rating,
                text=review.text,
                created_at=review.created_at,
                is_own=False,
            )
            for review, first_name, username in result.all()
        )

    async def get_by_user_id(self, user_id: object) -> PublicReview | None:
        stmt = (
            select(Review, User.first_name, User.username)
            .join(User, User.id == Review.user_id)
            .where(Review.user_id == user_id)
        )
        result = await self._session.execute(stmt)
        row = result.one_or_none()
        if row is None:
            return None
        review, first_name, username = row
        return PublicReview(
            first_name=first_name,
            username=username,
            rating=review.rating,
            text=review.text,
            created_at=review.created_at,
            is_own=True,
        )

    async def upsert(self, *, user_id: object, rating: int, text: str) -> None:
        stmt = select(Review).where(Review.user_id == user_id)
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing is not None:
            existing.rating = rating
            existing.text = text
        else:
            self._session.add(Review(user_id=user_id, rating=rating, text=text))
        await self._session.flush()

    async def get_overview(
        self,
        limit: int,
        *,
        viewer_user_id: object = None,
    ) -> ReviewsOverview:
        stats_stmt = select(func.count(Review.id), func.avg(Review.rating))
        stats_result = await self._session.execute(stats_stmt)
        total_reviews, average_rating = stats_result.one()

        recent_reviews = await self.list_recent(limit)

        user_review = None
        if viewer_user_id is not None:
            user_review = await self.get_by_user_id(viewer_user_id)

        return ReviewsOverview(
            total_reviews=total_reviews or 0,
            average_rating=float(average_rating or 0),
            recent_reviews=recent_reviews,
            user_review=user_review,
        )
