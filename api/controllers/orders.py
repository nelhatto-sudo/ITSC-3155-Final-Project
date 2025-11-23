from fastapi import HTTPException, status, Response, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional
from ..models import promotions as promo_model
from ..models import orders as order_model
from ..models import order_details as od_model
from ..models import sandwiches as sand_model
from decimal import Decimal


def recalculate_order_totals(db: Session, order_id: int):
    """
    Recalculate subtotal, discount, tax, and total for a given order.
    Called after creating/updating/deleting order details.
    """

    # 1. Get the order
    order = (
        db.query(order_model.Order)
        .filter(order_model.Order.id == order_id)
        .first()
    )
    if not order:
        return  # or raise exception if you prefer

    # 2. Calculate subtotal: SUM(amount * sandwich.price)
    subtotal = (
        db.query(func.sum(od_model.OrderDetail.amount * sand_model.Sandwich.price))
        .join(sand_model.Sandwich, sand_model.Sandwich.id == od_model.OrderDetail.sandwich_id)
        .filter(od_model.OrderDetail.order_id == order_id)
        .scalar()
    )

    if subtotal is None:
        subtotal = Decimal("0.00")

    subtotal = Decimal(subtotal)

    # 3. Apply promotion if present
    discount = Decimal("0.00")
    if order.promo_id:
        promo = db.query(promo_model.Promotion).filter(promo_model.Promotion.id == order.promo_id).first()
        if promo and promo.is_active:
            if promo.discount_type == "percent":
                discount = subtotal * Decimal(promo.discount_value) / Decimal("100")
            elif promo.discount_type == "amount":
                discount = Decimal(promo.discount_value)

    # 4. Tax (example: 7.5% → change if needed)
    TAX_RATE = Decimal("0.075")
    taxable_amount = subtotal - discount
    tax = taxable_amount * TAX_RATE if taxable_amount > 0 else Decimal("0.00")

    # 5. Total
    total = subtotal - discount + tax

    # 6. Save back into the order
    order.subtotal = subtotal
    order.discount = discount
    order.tax = tax
    order.total = total

    db.commit()

def create(db: Session, request):
    # --- Validate promotion if provided ---
    promo = None
    promo_id = getattr(request, "promo_id", None)

    if promo_id is not None:
        promo = (
            db.query(promo_model.Promotion)
            .filter(promo_model.Promotion.id == promo_id)
            .first()
        )
        if not promo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid promotion ID.",
            )

        now = datetime.utcnow()
        if (not promo.is_active) or (
            promo.expires_at is not None and promo.expires_at < now
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Promotion is expired or inactive.",
            )

    new_item = order_model.Order(
        customer_name=request.customer_name,
        customer_email=request.customer_email,
        order_type=order_model.OrderType(request.order_type),
        promo_id=promo_id,
    )

    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_item


def read(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """
    Return all orders, optionally filtered by order_date range.
    If start_date/end_date are provided, we filter on:
        order_date >= start_date (if given)
        order_date <= end_date   (if given)
    """
    q = db.query(order_model.Order)

    if start_date is not None:
        q = q.filter(order_model.Order.order_date >= start_date)

    if end_date is not None:
        q = q.filter(order_model.Order.order_date <= end_date)

    return q.order_by(order_model.Order.order_date).all()


def read_one(db: Session, item_id):
    try:
        item = db.query(order_model.Order).filter(order_model.Order.id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item


def update(db: Session, item_id, request):
    try:
        item = db.query(order_model.Order).filter(order_model.Order.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        update_data = request.dict(exclude_unset=True)
        item.update(update_data, synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item.first()


def delete(db: Session, item_id):
    try:
        item = db.query(order_model.Order).filter(order_model.Order.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        item.delete(synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
