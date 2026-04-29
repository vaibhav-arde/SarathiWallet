from fastapi import FastAPI, Request, Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from werkzeug.security import generate_password_hash, check_password_hash
from pydantic import ValidationError
from datetime import datetime

import sqlite3
import os
from database.db import get_db, init_db, seed_db
from models import UserCreate, UserLogin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize and seed the database on startup
    init_db()
    seed_db()
    yield

app = FastAPI(title="Sarathi Wallet", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Session middleware for Flash messages and user state
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-change-in-production")

templates = Jinja2Templates(directory="templates")

# ------------------------------------------------------------------ #
# Database path from project root
# ------------------------------------------------------------------ #

DATABASE_PATH = "SarathiWallet.db"

def get_db_dependency():
    """Returns a SQLite connection for use in routes via Depends."""
    # Importing here to avoid circular dependencies if any, 
    # but since main.py already imports from database.db it's fine.
    from database.db import get_db
    conn = get_db()
    try:
        yield conn
    finally:
        conn.close()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/terms", response_class=HTMLResponse)
async def terms(request: Request):
    return templates.TemplateResponse("terms.html", {"request": request})


@app.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    db: sqlite3.Connection = Depends(get_db_dependency)
):
    """Handle user registration"""
    form_data = await request.form()
    try:
        # Validate input using Pydantic
        user_data = UserCreate(
            name=form_data.get("name"),
            email=form_data.get("email"),
            password=form_data.get("password")
        )
    except ValidationError as e:
        # Return first validation error message
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": e.errors()[0]["msg"]
        })

    cursor = db.cursor()
    
    # Check if email is already taken
    cursor.execute("SELECT id FROM users WHERE email = ?", (user_data.email,))
    if cursor.fetchone():
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Email address already registered"
        })

    # Hash password and insert user
    hashed_password = generate_password_hash(user_data.password)
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (user_data.name, user_data.email, hashed_password)
        )
        db.commit()
    except Exception as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "An error occurred while creating your account. Please try again."
        })

    request.session["success"] = "Registration successful! Please sign in."
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    success = request.session.pop("success", None)
    return templates.TemplateResponse("login.html", {"request": request, "success": success})


@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    db: sqlite3.Connection = Depends(get_db_dependency)
):
    """Handle user login"""
    form_data = await request.form()
    try:
        login_data = UserLogin(
            email=form_data.get("email"),
            password=form_data.get("password")
        )
    except ValidationError:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid email or password"
        })

    cursor = db.cursor()
    cursor.execute("SELECT id, name, password_hash FROM users WHERE email = ?", (login_data.email,))
    user = cursor.fetchone()

    if user and check_password_hash(user["password_hash"], login_data.password):
        request.session["user_id"] = user["id"]
        request.session["user_name"] = user["name"]
        return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Invalid email or password"
    })


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/profile", response_class=HTMLResponse)
async def profile(
    request: Request,
    db: sqlite3.Connection = Depends(get_db_dependency)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    cursor = db.cursor()
    
    # Fetch user details
    cursor.execute("SELECT name, email, created_at FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        # User in session but not in DB? Clear session and redirect.
        request.session.clear()
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # Fetch expenses for the logged-in user
    cursor.execute(
        "SELECT amount, category, date, description FROM expenses WHERE user_id = ? ORDER BY date DESC",
        (user_id,)
    )
    expenses = cursor.fetchall()

    # 1. Compute user_info
    name = user["name"]
    initials = "".join([n[0].upper() for n in name.split() if n])[:2]
    
    # Format member_since: e.g., "2023-10-27 10:00:00" -> "October 2023"
    try:
        # SQLite's datetime('now') returns 'YYYY-MM-DD HH:MM:SS'
        created_at_dt = datetime.strptime(user["created_at"], "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        try:
            # Fallback for just date format if needed
            created_at_dt = datetime.strptime(user["created_at"].split()[0], "%Y-%m-%d")
        except:
            created_at_dt = datetime.now()
    
    member_since = created_at_dt.strftime("%B %Y")

    user_info = {
        "initials": initials,
        "name": name,
        "email": user["email"],
        "member_since": member_since
    }

    # 2. Compute summary_stats and transactions
    total_spent_val = 0
    transactions_count = len(expenses)
    category_totals = {}
    transactions = []

    for exp in expenses:
        amount = exp["amount"]
        total_spent_val += amount
        cat = exp["category"]
        category_totals[cat] = category_totals.get(cat, 0) + amount
        
        transactions.append({
            "date": exp["date"],
            "desc": exp["description"] or "No description",
            "category": cat,
            "amount": f"₹{amount:,.0f}",
            "type": "expense"
        })

    top_category = "N/A"
    if category_totals:
        top_category = max(category_totals, key=category_totals.get)

    summary_stats = {
        "total_spent": f"₹{total_spent_val:,.0f}",
        "transactions_count": transactions_count,
        "top_category": top_category
    }

    # 3. Compute categories
    categories = []
    color_classes = ["mock-bar", "mock-bar-2", "mock-bar-3", "mock-bar-4"]
    
    # Sort categories by amount descending
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    
    for i, (cat_name, cat_amount) in enumerate(sorted_categories):
        percentage = int((cat_amount / total_spent_val * 100)) if total_spent_val > 0 else 0
        categories.append({
            "name": cat_name,
            "amount": f"₹{cat_amount:,.0f}",
            "percentage": percentage,
            "color_class": color_classes[i % len(color_classes)]
        })

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user_info": user_info,
        "summary_stats": summary_stats,
        "transactions": transactions,
        "categories": categories
    })


@app.get("/expenses/add")
async def add_expense():
    return {"message": "Add expense — coming in Step 7"}


@app.get("/expenses/{id}/edit")
async def edit_expense(id: int):
    return {"message": "Edit expense — coming in Step 8"}


@app.get("/expenses/{id}/delete")
async def delete_expense(id: int):
    return {"message": "Delete expense — coming in Step 9"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)
