import sqlite3
import os
from werkzeug.security import generate_password_hash

# DATABASE_PATH in the project root as per database_spec.md
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "SarathiWallet.db")


def get_db():
    """Returns a SQLite connection with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Creates all tables using CREATE TABLE IF NOT EXISTS."""
    conn = get_db()
    cursor = conn.cursor()

    # Users table as per schema A
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Expenses table as per schema B
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def seed_db():
    """Inserts sample data for development."""
    conn = get_db()
    cursor = conn.cursor()

    # Check if data already exists to prevent duplication
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    # 1. Insert demo user
    hashed_password = generate_password_hash("demo123")
    cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@SarathiWallet.com", hashed_password)
    )
    user_id = cursor.lastrowid

    # 2. Insert 8 sample expenses across categories (Fixed List)
    # Categories: Food, Transport, Bills, Health, Entertainment, Shopping, Other
    sample_expenses = [
        (user_id, 450.00, "Food", "2026-04-01", "Dinner at Cafe"),
        (user_id, 1200.00, "Transport", "2026-04-02", "Monthly transit pass"),
        (user_id, 2500.00, "Bills", "2026-04-05", "Internet and Electric"),
        (user_id, 800.00, "Health", "2026-04-07", "Vitamin supplements"),
        (user_id, 1500.00, "Entertainment", "2026-04-10", "Movie and snacks"),
        (user_id, 3200.00, "Shopping", "2026-04-12", "New sneakers"),
        (user_id, 500.00, "Other", "2026-04-15", "Gift for friend"),
        (user_id, 650.00, "Food", "2026-04-18", "Grocery run"),
    ]

    cursor.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        sample_expenses
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    seed_db()
    print("Database initialized and seeded successfully.")
