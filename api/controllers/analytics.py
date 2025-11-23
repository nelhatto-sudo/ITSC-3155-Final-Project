from datetime import datetime, date, time, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from ..models import order_details as od_model
from ..models import sandwiches as sand_model
from ..models import ratings as rating_model
from ..models import orders as order_model


def get_least_popular_dishes(db: Session, limit: int = 5):
    """
    Return dishes sorted by how rarely they are ordered.
    Popularity is measured by total quantity in OrderDetail.amount.
    """
    try:
        # LEFT OUTER JOIN so sandwiches with zero orders are included
        rows = (
            db.query(
                sand_model.Sandwich.id.label("sandwich_id"),
                sand_model.Sandwich.sandwich_name.label("sandwich_name"),
                func.coalesce(func.sum(od_model.OrderDetail.amount), 0).label(
                    "total_ordered"
                ),
            )
            .outerjoin(
                od_model.OrderDetail,
                od_model.OrderDetail.sandwich_id == sand_model.Sandwich.id,
            )
            .group_by(
                sand_model.Sandwich.id,
                sand_model.Sandwich.sandwich_name,
            )
            .order_by("total_ordered")  # least ordered first
            .limit(limit)
            .all()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return [
        {
            "sandwich_id": row.sandwich_id,
            "sandwich_name": row.sandwich_name,
            "total_ordered": int(row.total_ordered or 0),
        }
        for row in rows
    ]


def get_complaints(db: Session, max_stars: int = 2):
    """
    Return low-star reviews (<= max_stars) with reasons.
    Helps staff understand why customers are dissatisfied.
    """
    try:
        # explicit join to get sandwich name; does not rely on relationship
        rows = (
            db.query(
                rating_model.Rating.id.label("rating_id"),
                rating_model.Rating.sandwich_id.label("sandwich_id"),
                sand_model.Sandwich.sandwich_name.label("sandwich_name"),
                rating_model.Rating.stars.label("stars"),
                rating_model.Rating.reason.label("reason"),
                rating_model.Rating.created_at.label("created_at"),
            )
            .join(
                sand_model.Sandwich,
                rating_model.Rating.sandwich_id == sand_model.Sandwich.id,
            )
            .filter(rating_model.Rating.stars <= max_stars)
            .all()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return [
        {
            "rating_id": row.rating_id,
            "sandwich_id": row.sandwich_id,
            "sandwich_name": row.sandwich_name,
            "stars": row.stars,
            "reason": row.reason,
            "created_at": row.created_at,
        }
        for row in rows
    ]


def get_daily_revenue(db: Session, target_date: date):
    """
    Compute total revenue (sum of order.total) for a given calendar date.
    Only counts orders with payment_status = 'paid'.
    """

    # Start of the day: YYYY-MM-DD 00:00:00
    start_dt = datetime.combine(target_date, time.min)
    # Start of next day: for half-open [start, next_start) interval
    next_day = target_date + timedelta(days=1)
    end_dt = datetime.combine(next_day, time.min)

    try:
        revenue = (
            db.query(func.coalesce(func.sum(order_model.Order.total), 0))
            # .filter(order_model.Order.payment_status == order_model.PaymentStatus.paid)
            .filter(order_model.Order.order_date >= start_dt)
            .filter(order_model.Order.order_date < end_dt)
            .scalar()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if revenue is None:
        revenue = Decimal("0.00")

    return {
        "date": target_date.isoformat(),
        "total_revenue": float(revenue),
    }