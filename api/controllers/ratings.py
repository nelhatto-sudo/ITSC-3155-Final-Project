from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models import ratings as model
from sqlalchemy.exc import SQLAlchemyError

def create(db: Session, request):
    new_item = model.Rating(**request.dict())
    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def read(db: Session):
    return db.query(model.Rating).all()

def read_one(db: Session, item_id: int):
    item = db.query(model.Rating).filter(model.Rating.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    return item

def update(db: Session, request, item_id: int):
    item = db.query(model.Rating).filter(model.Rating.id == item_id)
    if not item.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    item.update(request.dict(exclude_unset=True), synchronize_session=False)
    db.commit()
    return item.first()

def delete(db: Session, item_id: int):
    item = db.query(model.Rating).filter(model.Rating.id == item_id)
    if not item.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    item.delete(synchronize_session=False)
    db.commit()
    return {"deleted": item_id}