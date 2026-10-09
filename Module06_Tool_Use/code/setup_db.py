"""Create shop.db: a small, fictional order database for Nimbus Outdoor.

Run once before the demos:  python setup_db.py
Re-running it resets the database (refunds made in class are wiped).
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("shop.db")

CUSTOMERS = [
    ("C-01", "Asha Verma", "asha@example.com"),
    ("C-02", "Rohan Mehta", "rohan@example.com"),
    ("C-03", "Leela Iyer", "leela@example.com"),
]

ORDERS = [  # order_id, customer_id, item, amount_inr, status, ordered_on
    ("NB-1001", "C-01", "Trail backpack 40L", 4999, "delivered", "2026-09-12"),
    ("NB-1002", "C-01", "Rain jacket (M)", 3499, "shipped", "2026-10-02"),
    ("NB-1003", "C-02", "Camping stove", 2799, "delivered", "2026-09-20"),
    ("NB-1004", "C-02", "Headlamp", 899, "processing", "2026-10-06"),
    ("NB-1005", "C-03", "Two-person tent", 12999, "delivered", "2026-08-30"),
    ("NB-1006", "C-03", "Water filter bottle", 1599, "cancelled", "2026-09-28"),
]


def create(db_path=DB_PATH):
    db_path = Path(db_path)
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY, name TEXT, email TEXT UNIQUE);
        CREATE TABLE orders (
            order_id TEXT PRIMARY KEY, customer_id TEXT REFERENCES customers,
            item TEXT, amount_inr INTEGER, status TEXT, ordered_on TEXT);
        CREATE TABLE refunds (
            refund_id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT,
            amount_inr INTEGER, reason TEXT, created_at TEXT);
        """
    )
    conn.executemany("INSERT INTO customers VALUES (?, ?, ?)", CUSTOMERS)
    conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", ORDERS)
    conn.commit()
    conn.close()
    return db_path


if __name__ == "__main__":
    path = create()
    print(f"Created {path.name}: {len(CUSTOMERS)} customers, {len(ORDERS)} orders")
