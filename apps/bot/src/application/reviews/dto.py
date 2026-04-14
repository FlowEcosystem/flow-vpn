from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True, frozen=True)
class PublicReview:
    first_name: str | None
    username: str | None
    rating: int
    text: str
    created_at: datetime
    is_own: bool = field(default=False)


@dataclass(slots=True, frozen=True)
class ReviewsOverview:
    total_reviews: int
    average_rating: float
    recent_reviews: tuple[PublicReview, ...]
    user_review: PublicReview | None = field(default=None)
