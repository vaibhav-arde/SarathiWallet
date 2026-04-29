from fastapi import FastAPI, Request, Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from werkzeug.security import generate_password_hash
from pydantic import ValidationError

import sqlite3
import os
from database.db import get_db, init_db, seed_db
from models import UserCreate

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
    success = request.session.pop("success", None)
    return templates.TemplateResponse("login.html", {"request": request, "success": success})


@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    db: sqlite3.Connection = Depends(get_db_dependency)
):
    """Handle user login - coming in Step 3"""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Login coming in Step 3"
    })


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.get("/logout")
async def logout():
    return {"message": "Logout — coming in Step 3"}


@app.get("/profile")
async def profile():
    return {"message": "Profile page — coming in Step 4"}


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
