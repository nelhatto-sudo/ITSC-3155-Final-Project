from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..dependencies.database import get_db
from ..controllers import tags as controller
from ..schemas import tags as schema

router = APIRouter(tags=["Tags"], prefix="/tags")


@router.post("/", response_model=schema.Tag)
def create_tag(request: schema.TagCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


@router.get("/", response_model=list[schema.Tag])
def read_tags(db: Session = Depends(get_db)):
    return controller.read_all(db=db)


@router.get("/{item_id}", response_model=schema.Tag)
def read_tag(item_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db=db, item_id=item_id)


@router.put("/{item_id}", response_model=schema.Tag)
def update_tag(
    item_id: int,
    request: schema.TagUpdate,
    db: Session = Depends(get_db),
):
    return controller.update(db=db, request=request, item_id=item_id)


@router.delete("/{item_id}")
def delete_tag(item_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=item_id)