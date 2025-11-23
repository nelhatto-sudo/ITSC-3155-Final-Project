from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from .order_details import OrderDetail


class OrderBase(BaseModel):
    customer_name: str
    customer_email: Optional[str] = None
    order_type: str  # "takeout" / "delivery"
    promo_id: Optional[int] = None


class OrderCreate(OrderBase):
    """
    Input for creating an order.
    Only fields the caller should provide.
    """
    pass


class OrderUpdate(BaseModel):
    """
    Input for updating an order (staff side).
    All fields optional.
    """
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    order_type: Optional[str] = None
    status: Optional[str] = None
    payment_status: Optional[str] = None
    promo_id: Optional[int] = None


class Order(OrderBase):
    """
    Output / DB representation of an order.
    Includes auto-calculated and system-managed fields.
    """
    id: int
    tracking_number: str
    status: str
    order_date: datetime
    subtotal: float
    discount: float
    tax: float
    total: float
    payment_status: str

    class ConfigDict:
        from_attributes = True
