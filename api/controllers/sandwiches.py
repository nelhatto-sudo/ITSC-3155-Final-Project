from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models import sandwiches as model
from ..models.tags import Tag, SandwichTag

def _set_sandwich_tags(db: Session, sandwich: model.Sandwich, tag_ids: list[int]) -> None:
    # ensure tags exist
    if tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        if len(tags) != len(set(tag_ids)):
            raise HTTPException(
                status_code=400,
                detail="One or more tag_ids do not exist.",
            )

    sandwich.sandwich_tags.clear()  # remove old links

    for tid in tag_ids:
        link = SandwichTag(sandwich_id=sandwich.id, tag_id=tid)
        sandwich.sandwich_tags.append(link)

def create(db: Session, request):
    data = request.dict()
    tag_ids = data.pop("tag_ids", []) or []

    sandwich = model.Sandwich(**data)
    db.add(sandwich)
    db.commit()
    db.refresh(sandwich)

    if tag_ids:
        _set_sandwich_tags(db, sandwich, tag_ids)
        db.commit()
        db.refresh(sandwich)

    return sandwich

def read(db: Session):
    return db.query(model.Sandwich).all()

def read_one(db: Session, item_id: int):
    item = db.query(model.Sandwich).filter(model.Sandwich.id == item_id).first()
    if not item: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    return item

def update(db: Session, request, item_id: int):
    sandwich = db.query(model.Sandwich).filter(model.Sandwich.id == item_id).first()
    if not sandwich:
        raise HTTPException(status_code=404, detail="Id not found!")

    data = request.dict(exclude_unset=True)
    tag_ids = data.pop("tag_ids", None)

    if data:
        for k, v in data.items():
            setattr(sandwich, k, v)
        db.commit()
        db.refresh(sandwich)

    if tag_ids is not None:
        _set_sandwich_tags(db, sandwich, tag_ids or [])
        db.commit()
        db.refresh(sandwich)

    return sandwich

def delete(db: Session, item_id: int):
    q = db.query(model.Sandwich).filter(model.Sandwich.id == item_id)
    if not q.first(): raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    q.delete(synchronize_session=False); db.commit(); return {"deleted": item_id}
