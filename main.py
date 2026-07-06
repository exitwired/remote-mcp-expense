from fastmcp import FastMCP

import config
import database
import controller
from pathlib import Path

database.init_db()
mcp = FastMCP("Expense Tracker")

BASE_DIR = Path(__file__).resolve().parent
CATEGORIES_FILE = BASE_DIR / "categories.json"

@mcp.tool()
def register_user(username: str) -> str:
    """
    Register a new user in the expense tracker.
    """
    return controller.register_user(username)


@mcp.tool()
def list_users() -> list[str]:
    """
    List all registered users.
    """
    return controller.list_users()


@mcp.tool()
def add_expense(title: str, amount: float, category: str, when: str | None = None,):
    """ Add a new expense.
        IMPORTANT:
        - The username must refer to an existing registered user.
        - Never invent or assume a username.
        - If the user has not provided one, ask for it before calling this tool.
        - If the tool returns USER_NOT_FOUND, ask the user to provide a valid username or register one.
         IMPORTANT:
            - Convert relative dates such as "today", "yesterday",
              "last Friday", "3 days ago" into YYYY-MM-DD before
              calling this tool.
        when:
            Optional date expression exactly as provided by the user.
            Examples:
            - today
            - yesterday
            - last Friday
            - 3 days ago
            - 2026-07-04
            - July 4 2026
            - and so on....

            If omitted, today's date is used.
    """
    return controller.add_expense(
        title,
        amount,
        category,
        when
    )


@mcp.tool()
def list_expenses():
    """ List all expenses for a user.
        IMPORTANT:
        - The username must refer to an existing registered user.
        - Never invent or assume a username.
        - If the user has not provided one, ask for it before calling this tool.
        - If the tool returns USER_NOT_FOUND, ask the user to provide a valid username or register one.
     """
    return controller.list_expenses()


@mcp.tool()
def total_expense():
    """ Calculate total expenses.
        IMPORTANT:
        - The username must refer to an existing registered user.
        - Never invent or assume a username.
        - If the user has not provided one, ask for it before calling this tool.
        - If the tool returns USER_NOT_FOUND, ask the user to provide a valid username or register one.
    """
    return controller.total_expense()

@mcp.tool()
def set_active_user(username: str) -> str:
    """ Set the active user.
        Set the active user for the expense tracker.
        Call this tool before adding, editing, deleting, listing, or summarizing expenses.
        The username must already be registered.
    """
    return config.set_active_user(username)


@mcp.tool()
def delete_expense(expense_id: int):
    """ Delete an expense by ID. """
    return controller.delete_expense(expense_id)


@mcp.tool()
def request_edit_expense(
        expense_id: int,
        title: str,
        amount: float,
        category: str,
):
    """Submit an expense edit for approval."""
    return controller.request_edit_expense(
        expense_id,
        title,
        amount,
        category,
    )


@mcp.tool()
def list_pending_requests():
    """List all pending expense edit requests."""
    return controller.list_pending_requests()


@mcp.tool()
def approve_edit(request_id: int):
    """Approve a pending expense edit request."""
    return controller.approve_edit(request_id)


@mcp.tool()
def reject_edit(request_id: int):
    """Reject a pending expense edit request."""
    return controller.reject_edit(request_id)


@mcp.tool()
def seed_dummy_expenses():
    """
    Create 20 random dummy expenses over the last 90 days.

    IMPORTANT:
    - The username must refer to an existing registered user.
    - Never invent or assume a username.
    - If the user has not provided one, ask for it before calling this tool.
    - If the tool returns USER_NOT_FOUND, ask the user to provide a valid username or register one.
    """
    return controller.seed_dummy_expenses()


@mcp.tool()
def expense_summary(
        username: str,
        start_date: str,
        end_date: str,
):
    """
    Generate an expense summary for a user within a date range.

    Dates must be in YYYY-MM-DD format.
    """
    return controller.expense_summary(
        username,
        start_date,
        end_date,
    )


@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    if not CATEGORIES_FILE.exists():
        raise FileNotFoundError(f"{CATEGORIES_FILE} not found")

    return CATEGORIES_FILE.read_text(encoding="utf-8")

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
