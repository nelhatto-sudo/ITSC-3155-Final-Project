from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response
from sqlalchemy.exc import SQLAlchemyError

from ..models import order_details as model
from ..models import recipes as recipe_model
from ..models import resources as resource_model

def create(db: Session, request):
    """
    Create an OrderDetail only if there are enough ingredients
    in inventory (Resources) according to the Recipes.

    If any required ingredient is insufficient, raise HTTP 400
    with a clear message.
    """
    # 1) Find recipe rows for this sandwich
    recipes = (
        db.query(recipe_model.Recipe)
        .filter(recipe_model.Recipe.sandwich_id == request.sandwich_id)
        .all()
    )

    if not recipes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No recipe defined for this sandwich; cannot check ingredients.",
        )

    # 2) Check inventory for each ingredient
    insufficient = []
    for recipe in recipes:
        resource = (
            db.query(resource_model.Resource)
            .filter(resource_model.Resource.id == recipe.resource_id)
            .first()
        )

        if not resource:
            insufficient.append(
                {
                    "resource_id": recipe.resource_id,
                    "message": "Recipe references a missing resource.",
                }
            )
            continue

        required_amount = recipe.amount * request.amount
        if resource.amount < required_amount:
            insufficient.append(
                {
                    "resource_name": resource.item,
                    "required": required_amount,
                    "available": resource.amount,
                }
            )

    # 3) If anything is insufficient, abort with a clear error message
    if insufficient:
        parts = []
        for item in insufficient:
            if "resource_name" in item:
                parts.append(
                    f"{item['resource_name']}: required {item['required']}, available {item['available']}"
                )
            else:
                parts.append(item["message"])
        message = "Insufficient ingredients: " + "; ".join(parts)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    # 4) Otherwise, decrement inventory and create the order detail
    try:
        # Decrement resources
        for recipe in recipes:
            resource = (
                db.query(resource_model.Resource)
                .filter(resource_model.Resource.id == recipe.resource_id)
                .first()
            )
            required_amount = recipe.amount * request.amount
            resource.amount -= required_amount

        # Create order detail row
        new_item = model.OrderDetail(
            order_id=request.order_id,
            sandwich_id=request.sandwich_id,
            amount=request.amount,
        )

        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

def read_all(db: Session):
    return db.query(model.OrderDetail).all()

def read_one(db: Session, item_id: int):
    item = (
        db.query(model.OrderDetail)
        .filter(model.OrderDetail.id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Id not found!",
        )
    return item

def update(db: Session, request, item_id: int):
    q = db.query(model.OrderDetail).filter(model.OrderDetail.id == item_id)
    if not q.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Id not found!",
        )
    try:
        q.update(request.dict(exclude_unset=True), synchronize_session=False)
        db.commit()
        return q.first()
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

def delete(db: Session, item_id: int):
    try:
        q = db.query(model.OrderDetail).filter(model.OrderDetail.id == item_id)
        if not q.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Id not found!",
            )
        q.delete(synchronize_session=False)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except SQLAlchemyError as e:
        db.rollback()
        error = str(e.__dict__.get("orig", e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )