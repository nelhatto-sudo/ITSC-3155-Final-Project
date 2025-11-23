# api/routers/customer_service.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..dependencies.database import get_db
from ..schemas import orders as order_schema
from ..schemas import sandwiches as sandwich_schema
from ..controllers import orders as orders_controller
from ..controllers import sandwiches as sandwiches_controller

router = APIRouter(
    prefix="/customer",
    tags=["Customer Service"],
)

@router.get("/orders/track/{tracking_number}", response_model=order_schema.Order)
def track_order(tracking_number: str, db: Session = Depends(get_db)):
    return orders_controller.read_by_tracking_number(db=db, tracking_number=tracking_number)

@router.get("/menu/search", response_model=list[sandwich_schema.Sandwich])
def search_menu(tag: str | None = None, db: Session = Depends(get_db)):
    return sandwiches_controller.search_by_tag(db=db, tag_name=tag)
