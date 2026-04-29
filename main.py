from fastapi import FastAPI, Request, Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from werkzeug.security import generate_password_hash, check_password_hash
from pydantic import ValidationError

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
async def profile(request: Request):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # Hardcoded mock data for Step 4
    user_info = {
        "initials": "JD",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "member_since": "October 2023"
    }

    summary_stats = {
        "total_spent": "₹12,450",
        "transactions_count": 14,
        "top_category": "Food"
    }

    transactions = [
        {"date": "2023-10-25", "desc": "Grocery Run", "category": "Food", "amount": "₹1,200", "type": "expense"},
        {"date": "2023-10-24", "desc": "Petrol", "category": "Transport", "amount": "₹500", "type": "expense"},
        {"date": "2023-10-22", "desc": "Internet Bill", "category": "Utilities", "amount": "₹800", "type": "expense"},
        {"date": "2023-10-20", "desc": "Lunch with team", "category": "Dining", "amount": "₹1,500", "type": "expense"}
    ]

    categories = [
        {"name": "Food", "amount": "₹4,500", "percentage": 60, "color_class": "mock-bar"},
        {"name": "Transport", "amount": "₹2,500", "percentage": 35, "color_class": "mock-bar-2"},
        {"name": "Utilities", "amount": "₹1,800", "percentage": 25, "color_class": "mock-bar-3"},
        {"name": "Dining", "amount": "₹3,650", "percentage": 50, "color_class": "mock-bar-4"}
    ]

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
