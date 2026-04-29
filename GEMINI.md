# Sarathi Wallet — Personal Finance Tracker

Sarathi Wallet is a modern, lightweight personal finance application designed to help users track every rupee, understand their spending patterns, and take control of their financial life.

## Project Overview

*   **Purpose**: A simple and intuitive expense tracker where users can log transactions, categorize them, and visualize their monthly spending.
*   **Technologies**:
    *   **Backend**: Python with **FastAPI**.
    *   **Frontend**: **Jinja2** templates for server-side rendering.
    *   **Database**: **SQLite** for lightweight, file-based data storage.
    *   **Validation**: **Pydantic** for robust data modeling and request validation.
    *   **Styling**: Vanilla CSS for a clean, customized aesthetic.
*   **Architecture**:
    *   `main.py`: The core FastAPI application, containing route definitions and session middleware.
    *   `models.py`: Defines Pydantic models for Users and Expenses, ensuring data integrity.
    *   `database/db.py`: Handles SQLite connection, schema initialization, and development data seeding.
    *   `templates/`: Contains HTML files (`base.html`, `landing.html`, etc.) using Jinja2 inheritance.
    *   `static/`: Organized into `css/` and `js/` for static assets.

## Building and Running

### Prerequisites
*   Python 3.13+
*   `uv` (recommended for package management)

### Setup & Initialization
1.  **Install dependencies**:
    ```bash
    uv pip install -r requirements.txt
    ```
2.  **Initialize the Database**:
    Run the database utility script to create the schema and seed sample data.
    ```bash
    python database/db.py
    ```

### Running the Application
*   **Development Mode (with auto-reload)**:
    ```bash
    uv run python main.py
    ```
    Alternatively:
    ```bash
    uvicorn main:app --reload --port 5001
    ```
*   The application will be accessible at `http://localhost:5001`.

## Development Conventions

*   **Database**: Always use the `get_db` dependency in `main.py` to handle database connections.
*   **Templates**: Use the `base.html` layout for all pages to maintain design consistency (navbar/footer).
*   **Styling**: 
    *   `static/css/style.css` contains global variables and reset styles.
    *   For page-specific design overhauls (like the Hero section), use dedicated CSS files (e.g., `landing.css`) and include them in the `head` block of the template.
*   **Data Models**: All incoming request data and outgoing responses should be validated using the models defined in `models.py`.
*   **Testing**: (TODO: Add test runner instructions once a test suite is established).

## Roadmap

- [x] **Step 1: Database & Base Templates** — Initial schema and layout.
- [x] **Step 2: User Registration** — Secure account creation with validation and hashing.
- [x] **Step 3: Login & Sessions** — Authentication and protected routes.
- [x] **Step 4: User Profile** — Manage personal details.
- [ ] **Step 5: Expense Dashboard** — Visualize monthly spending.
- [ ] **Step 6: List Expenses** — View and filter transactions.
- [ ] **Step 7: Add Expense** — Create new transaction entries.
- [ ] **Step 8: Edit Expense** — Modify existing transactions.
- [ ] **Step 9: Delete Expense** — Remove transactions.
- [ ] **Step 10: Reports & Analytics** — Advanced charts and insights.
