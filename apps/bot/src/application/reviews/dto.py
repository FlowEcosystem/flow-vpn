from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class PublicReview:
    first_name: str | None
    rating: int
    text: str
    created_at: datetime


@dataclass(slots=True, frozen=True)
class ReviewsOverview:
    total_reviews: int
    average_rating: float
    recent_reviews: tuple[PublicReview, ...]
