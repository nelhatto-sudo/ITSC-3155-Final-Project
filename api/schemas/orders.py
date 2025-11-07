from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from .order_details import OrderDetail


class OrderBase(BaseModel):
    customer_name: str
    customer_email: Optional[str] = None
    order_type: str  # 'takeout' or 'delivery'


class OrderCreate(OrderBase):
    tracking_number: str
    status: Optional[str] = 'placed'
    subtotal: Optional[float] = 0.0
    discount: Optional[float] = 0.0
    tax: Optional[float] = 0.0
    total: Optional[float] = 0.0
    payment_status: Optional[str] = 'pending'
    promo_id: Optional[int] = None


class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    order_type: Optional[str] = None
    tracking_number: Optional[str] = None
    status: Optional[str] = None
    subtotal: Optional[float] = None
    discount: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None
    payment_status: Optional[str] = None
    promo_id: Optional[int] = None


class Order(OrderBase):
    id: int
    tracking_number: str
    status: str
    order_date: Optional[datetime] = None
    subtotal: float
    discount: float
    tax: float
    total: float
    payment_status: str
    promo_id: Optional[int] = None
    order_details: List[OrderDetail] = []
    class ConfigDict:
        from_attributes = True
