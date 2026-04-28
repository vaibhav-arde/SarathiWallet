import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "expenses.db")


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

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date DATE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def seed_db():
    """Inserts sample data for development."""
    conn = get_db()
    cursor = conn.cursor()

    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    # Insert sample users
    cursor.executemany(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        [
            ("Nitish Kumar", "nitish@example.com", "password123"),
            ("Test User", "test@example.com", "password456"),
        ]
    )

    # Insert sample expenses
    cursor.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        [
            (1, 4500, "Bills", "2026-03-05", "Monthly utilities"),
            (1, 3200, "Food", "2026-03-10", "Groceries and dining"),
            (1, 2050, "Health", "2026-03-15", "Pharmacy and wellness"),
            (1, 1800, "Transport", "2026-03-12", "Fuel and public transport"),
        ]
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    seed_db()
    print("Database initialized and seeded successfully.")
