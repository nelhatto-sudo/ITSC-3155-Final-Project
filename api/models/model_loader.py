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
        now = datetime.utcnow()

        order1 = Order(
            customer_name="Alice Smith",
            customer_phone="555-123-4567",
            delivery_address="123 Main St",
            order_type=OrderType.takeout,
            status=OrderStatus.completed,
            order_date=now - timedelta(days=3),
            subtotal=15.50,  # 1 Club + 1 Veggie
            discount=1.55,  # 10% off (WELCOME10)
            tax=1.40,
            total=15.35,
            payment_status=PaymentStatus.paid,
            promo_id=promo1.id,
        )

        order2 = Order(
            customer_name="Bob Johnson",
            customer_phone="555-987-6543",
            delivery_address="45 Oak Ave, Apt 2B",
            order_type=OrderType.delivery,
            status=OrderStatus.out_for_delivery,
            order_date=now - timedelta(days=2),
            subtotal=10.00,  # 2 Kids Grilled Cheese
            discount=0.00,
            tax=0.80,
            total=10.80,
            payment_status=PaymentStatus.paid,
            promo_id=None,
        )

        order3 = Order(
            customer_name="Carla Nguyen",
            customer_phone="555-555-1212",
            delivery_address="789 Elm St",
            order_type=OrderType.delivery,
            status=OrderStatus.preparing,
            order_date=now - timedelta(days=1),
            subtotal=17.00,  # 1 Club + 1 Veggie
            discount=5.00,  # $5 off (5OFF)
            tax=1.20,
            total=13.20,
            payment_status=PaymentStatus.pending,
            promo_id=promo2.id,
        )

        order4 = Order(
            customer_name="David Lee",
            customer_phone="555-222-3333",
            delivery_address="22 Maple Dr",
            order_type=OrderType.takeout,
            status=OrderStatus.ready,
            order_date=now - timedelta(hours=6),
            subtotal=8.50,  # 1 Club
            discount=0.00,
            tax=0.70,
            total=9.20,
            payment_status=PaymentStatus.pending,
            promo_id=None,
        )

        order5 = Order(
            customer_name="Emily Carter",
            customer_phone="555-444-8888",
            delivery_address="901 Pine St",
            order_type=OrderType.delivery,
            status=OrderStatus.canceled,
            order_date=now - timedelta(hours=12),
            subtotal=14.00,  # 2 Veggie
            discount=0.00,
            tax=0.00,  # canceled, ignore tax/total in analytics if you want
            total=0.00,
            payment_status=PaymentStatus.failed,
            promo_id=None,
        )

        order6 = Order(
            customer_name="Frank Miller",
            customer_phone="555-777-9999",
            delivery_address="310 Oak Blvd",
            order_type=OrderType.delivery,
            status=OrderStatus.completed,
            order_date=now,
            subtotal=20.50,  # 1 Club + 1 Veggie + 1 Kids
            discount=2.05,  # 10% off (WELCOME10)
            tax=1.85,
            total=20.30,
            payment_status=PaymentStatus.paid,
            promo_id=promo1.id,
        )

        db.add_all([order1, order2, order3, order4, order5, order6])
        db.commit()
        for o in (order1, order2, order3, order4, order5, order6):
            db.refresh(o)

        # ---------- ORDER DETAILS ----------
        order_details_data = [
            # Order 1: 1 Club, 1 Veggie
            OrderDetail(order_id=order1.id, sandwich_id=club.id, amount=1),
            OrderDetail(order_id=order1.id, sandwich_id=veggie.id, amount=1),

            # Order 2: 2 Kids Grilled Cheese
            OrderDetail(order_id=order2.id, sandwich_id=kids_grilled_cheese.id, amount=2),

            # Order 3: 1 Club, 1 Veggie
            OrderDetail(order_id=order3.id, sandwich_id=club.id, amount=1),
            OrderDetail(order_id=order3.id, sandwich_id=veggie.id, amount=1),

            # Order 4: 1 Club
            OrderDetail(order_id=order4.id, sandwich_id=club.id, amount=1),

            # Order 5: 2 Veggie (canceled order)
            OrderDetail(order_id=order5.id, sandwich_id=veggie.id, amount=2),

            # Order 6: 1 Club, 1 Veggie, 1 Kids
            OrderDetail(order_id=order6.id, sandwich_id=club.id, amount=1),
            OrderDetail(order_id=order6.id, sandwich_id=veggie.id, amount=1),
            OrderDetail(order_id=order6.id, sandwich_id=kids_grilled_cheese.id, amount=1),
        ]
        db.add_all(order_details_data)
        db.commit()

        # ---------- RATINGS ----------
        ratings_data = [
            # Club Sandwich – mostly positive, one complaint
            Rating(sandwich_id=club.id, stars=5, reason="Perfect balance of flavors and very fresh ingredients."),
            Rating(sandwich_id=club.id, stars=4, reason="Tasty and filling, bread was slightly toasted more than I like."),
            Rating(sandwich_id=club.id, stars=5, reason="My go-to lunch, generous portion size."),
            Rating(sandwich_id=club.id, stars=2, reason="Bread was soggy and the chicken was a bit dry this time."),

            # Veggie Delight – mixed reviews, some specific complaints
            Rating(sandwich_id=veggie.id, stars=4, reason="Very fresh veggies, light but satisfying."),
            Rating(sandwich_id=veggie.id, stars=3, reason="Good overall, but could use more seasoning and sauce."),
            Rating(sandwich_id=veggie.id, stars=5, reason="Great vegetarian option, loved the crunch and flavor."),
            Rating(sandwich_id=veggie.id, stars=2, reason="Too bland for my taste and the lettuce was wilted."),
            Rating(sandwich_id=veggie.id, stars=1, reason="Almost no dressing, very dry and not enjoyable."),

            # Kids Grilled Cheese – generally positive, one mild issue
            Rating(sandwich_id=kids_grilled_cheese.id, stars=5, reason="Kids loved it, cheese was perfectly melted."),
            Rating(sandwich_id=kids_grilled_cheese.id, stars=4, reason="Great for children, could be cut into smaller pieces."),
            Rating(sandwich_id=kids_grilled_cheese.id, stars=3, reason="Good, but the crust was a little too crunchy for the kids."),
        ]
        db.add_all(ratings_data)
        db.commit()
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