from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

import sqlite3
import os

app = FastAPI(title="Sarathi Wallet")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Session middleware for Flash messages and user state
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-change-in-production")

templates = Jinja2Templates(directory="templates")

# ------------------------------------------------------------------ #
# Database Dependencies                                              #
# ------------------------------------------------------------------ #

DATABASE_PATH = "database/expenses.db"


def get_db():
    """Returns a SQLite connection with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
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


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    db: sqlite3.Connection = Depends(get_db)
):
    """Handle user registration - coming in Step 3"""
    return templates.TemplateResponse("register.html", {
        "request": request,
        "error": "Registration coming in Step 3"
    })


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    db: sqlite3.Connection = Depends(get_db)
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
