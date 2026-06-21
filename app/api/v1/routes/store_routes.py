from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter(tags=["store"])


class UserUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=2, max_length=100)
    last_name: str | None = Field(default=None, min_length=2, max_length=100)
    username: str | None = Field(default=None, min_length=3, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=40)


class AddressCreate(BaseModel):
    label: str = Field(default="home", max_length=50)
    full_name: str = Field(min_length=2, max_length=200)
    phone: str | None = Field(default=None, max_length=40)
    street: str = Field(min_length=2, max_length=255)
    city: str = Field(min_length=2, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    zipcode: str = Field(min_length=2, max_length=30)
    country: str = Field(min_length=2, max_length=100)
    latitude: float | None = None
    longitude: float | None = None
    is_default: bool = False


def rows(result: Any) -> list[dict[str, Any]]:
    return [dict(row) for row in result.mappings().all()]


def one_or_404(result: Any, detail: str) -> dict[str, Any]:
    record = result.mappings().first()
    if record is None:
        raise HTTPException(status_code=404, detail=detail)
    return dict(record)


@router.get("/users")
def list_users(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    return rows(
        db.execute(
            text(
                """
                SELECT id, mongo_id, email, username, first_name, last_name,
                       phone, city, zipcode, is_active, created_at
                FROM users
                ORDER BY id
                LIMIT :limit OFFSET :offset
                """
            ),
            {"limit": limit, "offset": offset},
        )
    )


@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    return one_or_404(
        db.execute(
            text(
                """
                SELECT id, mongo_id, email, username, first_name, last_name,
                       phone, street, street_number, city, zipcode,
                       latitude, longitude, is_active, created_at, updated_at
                FROM users
                WHERE id = :user_id
                """
            ),
            {"user_id": user_id},
        ),
        "User not found",
    )


@router.patch("/users/{user_id}")
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="You may update only your own profile")
    values = payload.model_dump(exclude_unset=True)
    if not values:
        return get_user(user_id, db)
    assignments = ", ".join(f"{column} = :{column}" for column in values)
    values["user_id"] = user_id
    try:
        result = db.execute(
            text(f"UPDATE users SET {assignments} WHERE id = :user_id"),
            values,
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email or username already exists") from exc
    return get_user(user_id, db)


@router.get("/users/{user_id}/addresses")
def list_user_addresses(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> list[dict[str, Any]]:
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="You may view only your own addresses")
    return rows(
        db.execute(
            text(
                """
                SELECT id, user_id, label, full_name, phone, street, city,
                       state, zipcode, country, latitude, longitude,
                       is_default, created_at, updated_at
                FROM addresses
                WHERE user_id = :user_id
                ORDER BY is_default DESC, id
                """
            ),
            {"user_id": user_id},
        )
    )


@router.post("/users/{user_id}/addresses", status_code=201)
def create_user_address(
    user_id: int,
    payload: AddressCreate,
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="You may add only your own addresses")
    address_id = db.scalar(text("SELECT COALESCE(MAX(id), 0) + 1 FROM addresses"))
    values = payload.model_dump()
    values.update({"id": address_id, "user_id": user_id})
    if payload.is_default:
        db.execute(
            text("UPDATE addresses SET is_default = FALSE WHERE user_id = :user_id"),
            {"user_id": user_id},
        )
    db.execute(
        text(
            """
            INSERT INTO addresses (
                id, user_id, label, full_name, phone, street, city, state,
                zipcode, country, latitude, longitude, is_default
            ) VALUES (
                :id, :user_id, :label, :full_name, :phone, :street, :city,
                :state, :zipcode, :country, :latitude, :longitude, :is_default
            )
            """
        ),
        values,
    )
    db.commit()
    return one_or_404(
        db.execute(
            text(
                """
                SELECT id, user_id, label, full_name, phone, street, city,
                       state, zipcode, country, latitude, longitude,
                       is_default, created_at, updated_at
                FROM addresses WHERE id = :address_id
                """
            ),
            {"address_id": address_id},
        ),
        "Address not found",
    )


@router.get("/categories")
def list_categories(
    active_only: bool = True,
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    query = """
        SELECT id, mongo_id, name, description, image, is_active, created_at
        FROM categories
    """
    if active_only:
        query += " WHERE is_active = TRUE"
    query += " ORDER BY id"
    return rows(db.execute(text(query)))


@router.get("/products")
def list_products(
    category: str | None = None,
    search: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    conditions = ["p.is_active = TRUE"]
    parameters: dict[str, Any] = {"limit": limit, "offset": offset}
    if category:
        conditions.append("c.name = :category")
        parameters["category"] = category
    if search:
        conditions.append("(p.title LIKE :search OR p.description LIKE :search)")
        parameters["search"] = f"%{search}%"
    return rows(
        db.execute(
            text(
                f"""
                SELECT p.id, p.mongo_id, p.title, p.description, p.price,
                       p.image, p.rating_rate, p.rating_count,
                       p.stock_quantity, c.id AS category_id,
                       c.name AS category
                FROM products AS p
                JOIN categories AS c ON c.id = p.category_id
                WHERE {" AND ".join(conditions)}
                ORDER BY p.id
                LIMIT :limit OFFSET :offset
                """
            ),
            parameters,
        )
    )


@router.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    return one_or_404(
        db.execute(
            text(
                """
                SELECT p.id, p.mongo_id, p.title, p.description, p.price,
                       p.image, p.rating_rate, p.rating_count,
                       p.stock_quantity, p.is_active,
                       c.id AS category_id, c.name AS category
                FROM products AS p
                JOIN categories AS c ON c.id = p.category_id
                WHERE p.id = :product_id
                """
            ),
            {"product_id": product_id},
        ),
        "Product not found",
    )


@router.get("/products/{product_id}/reviews")
def list_product_reviews(
    product_id: int,
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    return rows(
        db.execute(
            text(
                """
                SELECT r.id, r.rating, r.title, r.comment,
                       r.is_verified_purchase, r.created_at,
                       u.id AS user_id, u.username, u.first_name, u.last_name
                FROM reviews AS r
                JOIN users AS u ON u.id = r.user_id
                WHERE r.product_id = :product_id
                ORDER BY r.created_at DESC
                """
            ),
            {"product_id": product_id},
        )
    )


@router.get("/carts/user/{user_id}")
def get_user_carts(user_id: int, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    carts = rows(
        db.execute(
            text(
                """
                SELECT id, legacy_id, user_id, status, cart_date
                FROM carts
                WHERE user_id = :user_id
                ORDER BY cart_date DESC, id DESC
                """
            ),
            {"user_id": user_id},
        )
    )
    for cart in carts:
        cart["items"] = rows(
            db.execute(
                text(
                    """
                    SELECT ci.id, ci.product_id, ci.title, ci.price,
                           ci.quantity, ci.added_at,
                           (ci.price * ci.quantity) AS subtotal
                    FROM cart_items AS ci
                    WHERE ci.cart_id = :cart_id
                    ORDER BY ci.id
                    """
                ),
                {"cart_id": cart["id"]},
            )
        )
    return carts


@router.get("/wishlists/user/{user_id}")
def get_user_wishlist(user_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    wishlist = one_or_404(
        db.execute(
            text("SELECT id, user_id, created_at FROM wishlists WHERE user_id = :user_id"),
            {"user_id": user_id},
        ),
        "Wishlist not found",
    )
    wishlist["items"] = rows(
        db.execute(
            text(
                """
                SELECT wi.id, wi.added_at, p.id AS product_id, p.title,
                       p.price, p.image, c.name AS category
                FROM wishlist_items AS wi
                JOIN products AS p ON p.id = wi.product_id
                JOIN categories AS c ON c.id = p.category_id
                WHERE wi.wishlist_id = :wishlist_id
                ORDER BY wi.added_at DESC
                """
            ),
            {"wishlist_id": wishlist["id"]},
        )
    )
    return wishlist


@router.get("/orders")
def list_orders(
    user_id: int | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    condition = "WHERE o.user_id = :user_id" if user_id is not None else ""
    return rows(
        db.execute(
            text(
                f"""
                SELECT o.id, o.user_id, o.address_id, o.status,
                       o.total_amount, o.discount, o.final_amount,
                       o.currency, o.payment_method, o.ordered_at,
                       o.delivered_at
                FROM orders AS o
                {condition}
                ORDER BY o.ordered_at DESC
                LIMIT :limit OFFSET :offset
                """
            ),
            {"user_id": user_id, "limit": limit, "offset": offset},
        )
    )


@router.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    order = one_or_404(
        db.execute(
            text(
                """
                SELECT id, user_id, address_id, status, total_amount,
                       discount, final_amount, currency, payment_method,
                       ordered_at, delivered_at
                FROM orders
                WHERE id = :order_id
                """
            ),
            {"order_id": order_id},
        ),
        "Order not found",
    )
    order["items"] = rows(
        db.execute(
            text(
                """
                SELECT id, product_id, title, price, quantity, subtotal
                FROM order_items
                WHERE order_id = :order_id
                ORDER BY id
                """
            ),
            {"order_id": order_id},
        )
    )
    return order


@router.get("/payments")
def list_payments(
    user_id: int | None = None,
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    condition = "WHERE user_id = :user_id" if user_id is not None else ""
    return rows(
        db.execute(
            text(
                f"""
                SELECT id, order_id, user_id, method, card_last4, amount,
                       currency, status, transaction_id, paid_at
                FROM payments
                {condition}
                ORDER BY id
                """
            ),
            {"user_id": user_id},
        )
    )


@router.get("/coupons/{code}")
def get_coupon(code: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    return one_or_404(
        db.execute(
            text(
                """
                SELECT id, code, discount_type, discount_value,
                       min_order_amount, max_discount, usage_limit,
                       used_count, is_active, valid_from, valid_until
                FROM coupons
                WHERE code = :code
                """
            ),
            {"code": code.upper()},
        ),
        "Coupon not found",
    )
