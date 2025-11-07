from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models import recipes as model
from sqlalchemy.exc import SQLAlchemyError

def create(db: Session, request):
    item = model.Recipe(**request.dict())
    try:
        db.add(item); db.commit(); db.refresh(item); return item
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def read(db: Session):
    return db.query(model.Recipe).all()

def read_one(db: Session, item_id: int):
    item = db.query(model.Recipe).filter(model.Recipe.id == item_id).first()
    if not item: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    return item

def update(db: Session, request, item_id: int):
    q = db.query(model.Recipe).filter(model.Recipe.id == item_id)
    if not q.first(): raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    q.update(request.dict(exclude_unset=True), synchronize_session=False); db.commit(); return q.first()

def delete(db: Session, item_id: int):
    q = db.query(model.Recipe).filter(model.Recipe.id == item_id)
    if not q.first(): raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    q.delete(synchronize_session=False); db.commit(); return {"deleted": item_id}
