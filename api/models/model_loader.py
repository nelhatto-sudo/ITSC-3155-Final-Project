from datetime import datetime, timedelta

from . import orders, order_details, recipes, sandwiches, resources, promotions, ratings, tags
from .orders import Order, OrderStatus, OrderType, PaymentStatus
from .order_details import OrderDetail
from .sandwiches import Sandwich
from .resources import Resource
from .recipes import Recipe
from .promotions import Promotion
from .ratings import Rating
from .tags import Tag, SandwichTag
from ..dependencies.database import engine, SessionLocal

def index():
    """Drop all tables, recreate them, and seed test data."""
    # 1) DROP ALL TABLES (for testing only)
    ratings.Base.metadata.drop_all(engine)
    order_details.Base.metadata.drop_all(engine)
    orders.Base.metadata.drop_all(engine)
    recipes.Base.metadata.drop_all(engine)
    sandwiches.Base.metadata.drop_all(engine)
    promotions.Base.metadata.drop_all(engine)
    resources.Base.metadata.drop_all(engine)

    # 2) CREATE ALL TABLES (in FK-friendly order)
    resources.Base.metadata.create_all(engine)
    sandwiches.Base.metadata.create_all(engine)
    recipes.Base.metadata.create_all(engine)
    promotions.Base.metadata.create_all(engine)
    orders.Base.metadata.create_all(engine)
    order_details.Base.metadata.create_all(engine)
    ratings.Base.metadata.create_all(engine)
    tags.Base.metadata.create_all(engine)

    # 3) SEED DATA
    seed_initial_data()

def seed_initial_data():
    """
    Insert a small set of test data for all tables.

    This runs only when the sandwiches table is empty, so you can
    safely restart the app without duplicating rows.
    """
    db = SessionLocal()
    try:
        # If we already have sandwiches, assume the DB is seeded.
        if db.query(Sandwich).first():
            return

        # ---------- RESOURCES (inventory items) ----------
        bread = Resource(item="Bread slices", amount=200)
        lettuce = Resource(item="Lettuce", amount=150)
        tomato = Resource(item="Tomato", amount=150)
        cheese = Resource(item="Cheese", amount=100)
        chicken = Resource(item="Chicken breast", amount=80)
        ham = Resource(item="Ham", amount=80)

        db.add_all([bread, lettuce, tomato, cheese, chicken, ham])
        db.commit()
        for r in (bread, lettuce, tomato, cheese, chicken, ham):
            db.refresh(r)

        # ---------- SANDWICHES (menu items) ----------
        club = Sandwich(sandwich_name="Club Sandwich", price=8.50)
        veggie = Sandwich(sandwich_name="Veggie Delight", price=7.00)
        kids_grilled_cheese = Sandwich(sandwich_name="Kids Grilled Cheese", price=5.00)

        db.add_all([club, veggie, kids_grilled_cheese])
        db.commit()
        for s in (club, veggie, kids_grilled_cheese):
            db.refresh(s)

        # ---------- RECIPES (what each sandwich uses) ----------
        recipes_data = [
            # Club Sandwich
            Recipe(sandwich_id=club.id, resource_id=bread.id, amount=2),
            Recipe(sandwich_id=club.id, resource_id=lettuce.id, amount=1),
            Recipe(sandwich_id=club.id, resource_id=tomato.id, amount=1),
            Recipe(sandwich_id=club.id, resource_id=chicken.id, amount=1),

            # Veggie Delight
            Recipe(sandwich_id=veggie.id, resource_id=bread.id, amount=2),
            Recipe(sandwich_id=veggie.id, resource_id=lettuce.id, amount=2),
            Recipe(sandwich_id=veggie.id, resource_id=tomato.id, amount=2),

            # Kids Grilled Cheese
            Recipe(sandwich_id=kids_grilled_cheese.id, resource_id=bread.id, amount=2),
            Recipe(sandwich_id=kids_grilled_cheese.id, resource_id=cheese.id, amount=2),
        ]
        db.add_all(recipes_data)
        db.commit()

        # ---------- PROMOTIONS ----------
        now = datetime.utcnow()
        promo1 = Promotion(
            code="WELCOME10",
            description="10% off first order",
            discount_type="percent",
            discount_value=10.0,
            expires_at=now + timedelta(days=30),
            is_active=True,
        )
        promo2 = Promotion(
            code="5OFF",
            description="$5 off orders over $25",
            discount_type="amount",
            discount_value=5.0,
            expires_at=now + timedelta(days=60),
            is_active=True,
        )
        db.add_all([promo1, promo2])
        db.commit()
        db.refresh(promo1)
        db.refresh(promo2)

        # ---------- ORDERS ----------
        order1 = Order(
            customer_name="Alice Smith",
            customer_email="alice@example.com",
            order_type=OrderType.takeout,
            status=OrderStatus.completed,
            order_date=now - timedelta(days=1),
            subtotal=15.50,
            discount=1.55,
            tax=1.10,
            total=15.05,
            payment_status=PaymentStatus.paid,
            promo_id=promo1.id,
        )
        order2 = Order(
            customer_name="Bob Johnson",
            customer_email="bob@example.com",
            order_type=OrderType.delivery,
            status=OrderStatus.preparing,
            order_date=now,
            subtotal=12.00,
            discount=0.00,
            tax=0.90,
            total=12.90,
            payment_status=PaymentStatus.pending,
            promo_id=None,
        )

        db.add_all([order1, order2])
        db.commit()
        db.refresh(order1)
        db.refresh(order2)

        # ---------- ORDER DETAILS ----------
        order_details_data = [
            # Order 1: 1 Club, 1 Veggie
            OrderDetail(order_id=order1.id, sandwich_id=club.id, amount=1),
            OrderDetail(order_id=order1.id, sandwich_id=veggie.id, amount=1),

            # Order 2: 2 Kids Grilled Cheese
            OrderDetail(order_id=order2.id, sandwich_id=kids_grilled_cheese.id, amount=2),
        ]
        db.add_all(order_details_data)
        db.commit()

        # ---------- RATINGS ----------
        ratings_data = [
            Rating(sandwich_id=club.id, stars=5, reason="Delicious and fresh."),
            Rating(sandwich_id=veggie.id, stars=3, reason="Good but could use more seasoning."),
            Rating(sandwich_id=kids_grilled_cheese.id, stars=4, reason="Kids loved it!"),
        ]
        db.add_all(ratings_data)
        db.commit()

        # ---------- TAGS (food properties / categories) ----------
        # Only insert if table is empty
        if not db.query(Tag).first():
            initial_tags = [
                Tag(name="spicy", display_name="Spicy"),
                Tag(name="mild", display_name="Mild"),
                Tag(name="vegetarian", display_name="Vegetarian"),
                Tag(name="vegan", display_name="Vegan"),
                Tag(name="kids", display_name="Kids"),
                Tag(name="low_fat", display_name="Low Fat"),
                Tag(name="high_protein", display_name="High Protein"),
                Tag(name="gluten_free", display_name="Gluten Free"),
                Tag(name="dairy_free", display_name="Dairy Free"),
            ]
            db.add_all(initial_tags)
            db.commit()
            for t in initial_tags:
                db.refresh(t)
    finally:
        db.close()