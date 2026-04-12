from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.reviews import PublicReview, ReviewsOverview
from src.infrastructure.database.models import Review, User


class SqlAlchemyReviewsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_recent(self, limit: int) -> tuple[PublicReview, ...]:
        stmt = (
            select(Review, User.first_name)
            .join(User, User.id == Review.user_id)
            .order_by(Review.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return tuple(
            PublicReview(
                first_name=first_name,
                rating=review.rating,
                text=review.text,
                created_at=review.created_at,
            )
            for review, first_name in result.all()
        )

    async def create(self, *, user_id: object, rating: int, text: str) -> None:
        self._session.add(
            Review(
                user_id=user_id,
                rating=rating,
                text=text,
            )
        )
        await self._session.flush()

    async def get_overview(self, limit: int) -> ReviewsOverview:
        stats_stmt = select(func.count(Review.id), func.avg(Review.rating))
        stats_result = await self._session.execute(stats_stmt)
        total_reviews, average_rating = stats_result.one()
        recent_reviews = await self.list_recent(limit)
        return ReviewsOverview(
            total_reviews=total_reviews or 0,
            average_rating=float(average_rating or 0),
            recent_reviews=recent_reviews,
        )
