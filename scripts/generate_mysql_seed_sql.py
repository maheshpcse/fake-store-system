"""Generate SQLyog-friendly MySQL seed SQL from the MongoDB JSON exports."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import bcrypt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "MongoDB collections"
OUTPUT = ROOT / "MySQL DB schemas" / "02_seed_all_data.sql"


def load(name: str) -> list[dict[str, Any]]:
    return json.loads((SOURCE / name).read_text(encoding="utf-8-sig"))


def mongo_id(row: dict[str, Any]) -> str | None:
    value = row.get("_id")
    return value.get("$oid") if isinstance(value, dict) else None


def date_value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, dict):
        value = value.get("$date")
    if not value:
        return None
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed.strftime("%Y-%m-%d %H:%M:%S")


def sql(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("\\", "\\\\").replace("'", "''") + "'"


def insert(table: str, columns: list[str], rows: list[list[Any]]) -> str:
    if not rows:
        return ""
    values = ",\n".join(
        "    (" + ", ".join(sql(value) for value in row) + ")" for row in rows
    )
    return (
        f"INSERT INTO {table} ({', '.join(columns)}) VALUES\n"
        f"{values};\n"
    )


def main() -> None:
    users = load("fake_store.user.json")
    addresses = load("fake_store.addresses.json")
    categories = load("fake_store.categories.json")
    products = load("fake_store.product.json")
    carts = load("fake_store.cart.json")
    source_cart_items = load("fake_store.cart_items.json")
    wishlists = load("fake_store.wishlists.json")
    orders = load("fake_store.orders.json")
    order_items = load("fake_store.order_items.json")
    payments = load("fake_store.payments.json")
    reviews = load("fake_store.reviews.json")
    coupons = load("fake_store.coupons.json")

    product_by_id = {row["id"]: row for row in products}
    category_id_by_name = {row["name"]: row["id"] for row in categories}

    cart_records = list(carts)
    existing_cart_keys = {(row["id"], row["userId"]) for row in cart_records}
    for item in source_cart_items:
        key = (item["cartId"], item["userId"])
        if key not in existing_cart_keys:
            cart_records.append(
                {
                    "_id": None,
                    "id": item["cartId"],
                    "userId": item["userId"],
                    "date": date_value(item.get("addedAt")),
                    "products": [],
                }
            )
            existing_cart_keys.add(key)

    cart_records.sort(key=lambda row: (row["id"], row["userId"]))
    cart_pk_by_legacy_user = {
        (row["id"], row["userId"]): index
        for index, row in enumerate(cart_records, start=1)
    }

    normalized_cart_items: list[dict[str, Any]] = []
    seen_cart_products: set[tuple[int, int]] = set()
    for item in sorted(source_cart_items, key=lambda row: row["id"]):
        cart_pk = cart_pk_by_legacy_user[(item["cartId"], item["userId"])]
        normalized_cart_items.append(
            {
                "id": item["id"],
                "mongo_id": mongo_id(item),
                "cart_id": cart_pk,
                "user_id": item["userId"],
                "product_id": item["productId"],
                "title": item["title"],
                "price": item["price"],
                "quantity": item["quantity"],
                "added_at": date_value(item.get("addedAt")),
            }
        )
        seen_cart_products.add((cart_pk, item["productId"]))

    next_cart_item_id = max((row["id"] for row in normalized_cart_items), default=0) + 1
    for cart in cart_records:
        cart_pk = cart_pk_by_legacy_user[(cart["id"], cart["userId"])]
        for nested_item in cart.get("products", []):
            key = (cart_pk, nested_item["productId"])
            if key in seen_cart_products:
                continue
            product = product_by_id[nested_item["productId"]]
            normalized_cart_items.append(
                {
                    "id": next_cart_item_id,
                    "mongo_id": None,
                    "cart_id": cart_pk,
                    "user_id": cart["userId"],
                    "product_id": nested_item["productId"],
                    "title": product["title"],
                    "price": product["price"],
                    "quantity": nested_item["quantity"],
                    "added_at": date_value(cart.get("date")),
                }
            )
            next_cart_item_id += 1
            seen_cart_products.add(key)

    statements = [
        "-- Generated from MongoDB collections by scripts/generate_mysql_seed_sql.py.",
        "-- WARNING: this resets local Fake Store data before inserting the sample records.",
        "USE fake_store;",
        "SET NAMES utf8mb4;",
        "SET FOREIGN_KEY_CHECKS = 0;",
        "TRUNCATE TABLE audit_logs;",
        "TRUNCATE TABLE file_processing_logs;",
        "TRUNCATE TABLE payments;",
        "TRUNCATE TABLE payment_report_stage;",
        "TRUNCATE TABLE payment_report_batches;",
        "TRUNCATE TABLE reviews;",
        "TRUNCATE TABLE order_items;",
        "TRUNCATE TABLE orders;",
        "TRUNCATE TABLE coupons;",
        "TRUNCATE TABLE wishlist_items;",
        "TRUNCATE TABLE wishlists;",
        "TRUNCATE TABLE cart_items;",
        "TRUNCATE TABLE carts;",
        "TRUNCATE TABLE products;",
        "TRUNCATE TABLE categories;",
        "TRUNCATE TABLE addresses;",
        "TRUNCATE TABLE refresh_tokens;",
        "TRUNCATE TABLE user_roles;",
        "TRUNCATE TABLE roles;",
        "TRUNCATE TABLE users;",
        "SET FOREIGN_KEY_CHECKS = 1;",
        "START TRANSACTION;",
        insert(
            "roles",
            ["id", "name", "description"],
            [
                [1, "customer", "Regular store customer"],
                [2, "admin", "Store administrator"],
            ],
        ),
    ]

    user_rows = []
    for row in sorted(users, key=lambda item: item["id"]):
        password_hash = bcrypt.hashpw(
            row["password"].encode("utf-8"), bcrypt.gensalt(rounds=12)
        ).decode("utf-8")
        address = row.get("address", {})
        geolocation = address.get("geolocation", {})
        user_rows.append(
            [
                row["id"],
                mongo_id(row),
                row["email"],
                row["username"],
                password_hash,
                row["name"]["firstname"],
                row["name"]["lastname"],
                row.get("phone"),
                address.get("street"),
                address.get("number"),
                address.get("city"),
                address.get("zipcode"),
                geolocation.get("lat"),
                geolocation.get("long"),
                True,
            ]
        )
    statements.append(
        insert(
            "users",
            [
                "id",
                "mongo_id",
                "email",
                "username",
                "password_hash",
                "first_name",
                "last_name",
                "phone",
                "street",
                "street_number",
                "city",
                "zipcode",
                "latitude",
                "longitude",
                "is_active",
            ],
            user_rows,
        )
    )
    statements.append(
        insert(
            "user_roles",
            ["user_id", "role_id"],
            [[row["id"], 1] for row in sorted(users, key=lambda item: item["id"])],
        )
    )

    statements.append(
        insert(
            "addresses",
            [
                "id",
                "mongo_id",
                "user_id",
                "label",
                "full_name",
                "phone",
                "street",
                "city",
                "state",
                "zipcode",
                "country",
                "is_default",
                "created_at",
            ],
            [
                [
                    row["id"],
                    mongo_id(row),
                    row["userId"],
                    row["label"],
                    row["fullName"],
                    row.get("phone"),
                    row["street"],
                    row["city"],
                    row.get("state"),
                    row["zipcode"],
                    row["country"],
                    row.get("isDefault", False),
                    date_value(row.get("createdAt")),
                ]
                for row in sorted(addresses, key=lambda item: item["id"])
            ],
        )
    )
    statements.append(
        insert(
            "categories",
            ["id", "mongo_id", "name", "description", "image", "is_active", "created_at"],
            [
                [
                    row["id"],
                    mongo_id(row),
                    row["name"],
                    row.get("description"),
                    row.get("image"),
                    row.get("isActive", True),
                    date_value(row.get("createdAt")),
                ]
                for row in sorted(categories, key=lambda item: item["id"])
            ],
        )
    )
    statements.append(
        insert(
            "products",
            [
                "id",
                "mongo_id",
                "category_id",
                "title",
                "description",
                "price",
                "image",
                "rating_rate",
                "rating_count",
                "stock_quantity",
                "is_active",
            ],
            [
                [
                    row["id"],
                    mongo_id(row),
                    category_id_by_name[row["category"]],
                    row["title"],
                    row.get("description"),
                    row["price"],
                    row.get("image"),
                    row.get("rating", {}).get("rate", 0),
                    row.get("rating", {}).get("count", 0),
                    100,
                    True,
                ]
                for row in sorted(products, key=lambda item: item["id"])
            ],
        )
    )
    statements.append(
        insert(
            "carts",
            ["id", "mongo_id", "legacy_id", "user_id", "status", "cart_date"],
            [
                [
                    cart_pk_by_legacy_user[(row["id"], row["userId"])],
                    mongo_id(row),
                    row["id"],
                    row["userId"],
                    "active",
                    date_value(row.get("date")),
                ]
                for row in cart_records
            ],
        )
    )
    statements.append(
        insert(
            "cart_items",
            [
                "id",
                "mongo_id",
                "cart_id",
                "user_id",
                "product_id",
                "title",
                "price",
                "quantity",
                "added_at",
            ],
            [
                [
                    row["id"],
                    row["mongo_id"],
                    row["cart_id"],
                    row["user_id"],
                    row["product_id"],
                    row["title"],
                    row["price"],
                    row["quantity"],
                    row["added_at"],
                ]
                for row in normalized_cart_items
            ],
        )
    )
    statements.append(
        insert(
            "wishlists",
            ["id", "mongo_id", "user_id"],
            [
                [row["id"], mongo_id(row), row["userId"]]
                for row in sorted(wishlists, key=lambda item: item["id"])
            ],
        )
    )
    wishlist_items = []
    for wishlist in sorted(wishlists, key=lambda item: item["id"]):
        for product in wishlist.get("products", []):
            wishlist_items.append(
                [
                    wishlist["id"],
                    product["productId"],
                    date_value(product.get("addedAt")),
                ]
            )
    statements.append(
        insert(
            "wishlist_items",
            ["wishlist_id", "product_id", "added_at"],
            wishlist_items,
        )
    )
    statements.append(
        insert(
            "coupons",
            [
                "id",
                "mongo_id",
                "code",
                "discount_type",
                "discount_value",
                "min_order_amount",
                "max_discount",
                "usage_limit",
                "used_count",
                "is_active",
                "valid_from",
                "valid_until",
            ],
            [
                [
                    row["id"],
                    mongo_id(row),
                    row["code"],
                    row["type"],
                    row["value"],
                    row["minOrderAmount"],
                    row.get("maxDiscount"),
                    row.get("usageLimit"),
                    row.get("usedCount", 0),
                    row.get("isActive", True),
                    date_value(row["validFrom"]),
                    date_value(row["validUntil"]),
                ]
                for row in sorted(coupons, key=lambda item: item["id"])
            ],
        )
    )
    statements.append(
        insert(
            "orders",
            [
                "id",
                "mongo_id",
                "user_id",
                "address_id",
                "status",
                "total_amount",
                "discount",
                "final_amount",
                "currency",
                "payment_method",
                "ordered_at",
                "delivered_at",
            ],
            [
                [
                    row["id"],
                    mongo_id(row),
                    row["userId"],
                    row["addressId"],
                    row["status"],
                    row["totalAmount"],
                    row.get("discount", 0),
                    row["finalAmount"],
                    "USD",
                    row["paymentMethod"],
                    date_value(row["orderedAt"]),
                    date_value(row.get("deliveredAt")),
                ]
                for row in sorted(orders, key=lambda item: item["id"])
            ],
        )
    )
    statements.append(
        insert(
            "order_items",
            ["id", "mongo_id", "order_id", "product_id", "title", "price", "quantity", "subtotal"],
            [
                [
                    row["id"],
                    mongo_id(row),
                    row["orderId"],
                    row["productId"],
                    row["title"],
                    row["price"],
                    row["quantity"],
                    row["subtotal"],
                ]
                for row in sorted(order_items, key=lambda item: item["id"])
            ],
        )
    )
    statements.append(
        insert(
            "payments",
            [
                "id",
                "mongo_id",
                "legacy_id",
                "order_id",
                "user_id",
                "method",
                "card_last4",
                "amount",
                "currency",
                "status",
                "transaction_id",
                "paid_at",
            ],
            [
                [
                    row["id"],
                    mongo_id(row),
                    row["id"],
                    row["orderId"],
                    row["userId"],
                    row["method"],
                    row.get("cardLast4"),
                    row["amount"],
                    row.get("currency", "USD"),
                    row["status"],
                    row["transactionId"],
                    date_value(row.get("paidAt")),
                ]
                for row in sorted(payments, key=lambda item: item["id"])
            ],
        )
    )
    statements.append(
        insert(
            "reviews",
            [
                "id",
                "mongo_id",
                "product_id",
                "user_id",
                "rating",
                "title",
                "comment",
                "is_verified_purchase",
                "created_at",
            ],
            [
                [
                    row["id"],
                    mongo_id(row),
                    row["productId"],
                    row["userId"],
                    row["rating"],
                    row["title"],
                    row["comment"],
                    row.get("isVerifiedPurchase", False),
                    date_value(row.get("createdAt")),
                ]
                for row in sorted(reviews, key=lambda item: item["id"])
            ],
        )
    )
    statements.extend(
        [
            "COMMIT;",
            "SET FOREIGN_KEY_CHECKS = 1;",
            "",
        ]
    )
    OUTPUT.write_text("\n\n".join(item for item in statements if item), encoding="utf-8")
    print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()

