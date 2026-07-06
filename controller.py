from database import get_connection
import random
import config
from datetime import datetime, timedelta

import utility


def get_user_id(username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    )

    row = cursor.fetchone()

    conn.close()

    return row[0] if row else None


def user_exists(username):
    return get_user_id(username) is not None


def register_user(username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username=?",
        (username,)
    )

    if cursor.fetchone():
        conn.close()
        return f"User '{username}' already exists."

    cursor.execute(
        "INSERT INTO users(username) VALUES(?)",
        (username,)
    )

    conn.commit()
    conn.close()

    return f"User '{username}' registered successfully."


def list_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
                   SELECT username
                   FROM users
                   ORDER BY username
                   """)

    users = [row[0] for row in cursor.fetchall()]

    conn.close()

    return users


def add_expense(title, amount, category, when=None):
    username = config.get_active_user()

    if username is None:
        return "No active user selected. Use set_active_user() first."

    user_id = get_user_id(username)

    if user_id is None:
        return "Active user does not exist. Please register the user first."
    # try:
    #     expense_date = utility.resolve_expense_date(when)
    # except ValueError as e:
    #     return str(e)

    try:
        expense_date = utility.resolve_expense_date(when)
    except ValueError as e:
        return str(e)

    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
                   INSERT INTO expenses(user_id,
                                        title,
                                        amount,
                                        category,
                                        expense_date,
                                        created_at)
                   VALUES (?, ?, ?, ?, ?, ?)
                   """, (
                       user_id,
                       title,
                       amount,
                       category,
                       expense_date,
                       created_at
                   ))

    conn.commit()

    conn.close()

    return f"Expense added successfully for {expense_date}."


def list_expenses():
    username = config.get_active_user()

    if username is None:
        return "No active user selected. Use set_active_user() first."

    user_id = get_user_id(username)

    if user_id is None:
        return "Active user does not exist. Please register the user first."
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
                   SELECT id,
                          title,
                          amount,
                          category,
                          expense_date,
                          created_at
                   FROM expenses
                   WHERE user_id = ?
                   ORDER BY expense_date DESC
                   """, (user_id,))

    rows = cursor.fetchall()

    conn.close()

    expenses = []

    for row in rows:
        expenses.append({
            "id": row[0],
            "title": row[1],
            "amount": row[2],
            "category": row[3],
            "created_at": row[4]
        })

    return expenses


def total_expense():
    user_obj = config.get_active_user()

    if user_obj is None:
        return "No active user selected. Use set_active_user() first."
    user_id = get_user_id(user_obj.username)

    if user_id is None:
        return "Active user does not exist. Please register the user first."
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
                   SELECT SUM(amount)
                   FROM expenses
                   WHERE user_id = ?
                   """, (user_id,))

    total = cursor.fetchone()[0]

    conn.close()

    return total or 0


def delete_expense(expense_id):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id=?",
        (expense_id,)
    )

    conn.commit()

    conn.close()

    return "Expense deleted."


def request_edit_expense(expense_id, title, amount, category):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
                   INSERT INTO expense_edit_requests(expense_id,
                                                     new_title,
                                                     new_amount,
                                                     new_category,
                                                     requested_at)
                   VALUES (?, ?, ?, ?, ?)
                   """, (
                       expense_id,
                       title,
                       amount,
                       category,
                       datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                   ))

    conn.commit()
    conn.close()

    return "Edit request submitted for approval."


def list_pending_requests():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
                   SELECT id,
                          expense_id,
                          new_title,
                          new_amount,
                          new_category,
                          requested_at
                   FROM expense_edit_requests
                   WHERE status = 'Pending'
                   """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def approve_edit(request_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
                   SELECT expense_id,
                          new_title,
                          new_amount,
                          new_category
                   FROM expense_edit_requests
                   WHERE id = ?
                     AND status = 'Pending'
                   """, (request_id,))

    request = cursor.fetchone()

    if request is None:
        conn.close()
        return "No pending request found."

    expense_id, title, amount, category = request

    cursor.execute("""
                   UPDATE expenses
                   SET title=?,
                       amount=?,
                       category=?
                   WHERE id = ?
                   """, (
                       title,
                       amount,
                       category,
                       expense_id
                   ))

    cursor.execute("""
                   UPDATE expense_edit_requests
                   SET status='Approved',
                       approved_at=?
                   WHERE id = ?
                   """, (
                       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                       request_id
                   ))

    conn.commit()
    conn.close()

    return "Expense updated successfully."


def reject_edit(request_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
                   UPDATE expense_edit_requests
                   SET status='Rejected'
                   WHERE id = ?
                   """, (request_id,))

    conn.commit()
    conn.close()

    return "Edit request rejected."


def expense_summary(start_date, end_date):
    username = config.get_active_user()

    if username is None:
        return "No active user selected. Use set_active_user() first."

    user_id = get_user_id(username)

    if user_id is None:
        return "Active user does not exist. Please register the user first."
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
                   SELECT COUNT(*),
                          COALESCE(SUM(amount), 0),
                          COALESCE(AVG(amount), 0)
                   FROM expenses
                   WHERE user_id = ?
                     AND DATE (expense_date) BETWEEN ?
                     AND ?
                   """, (
                       user_id,
                       start_date,
                       end_date
                   ))

    count, total, average = cursor.fetchone()

    cursor.execute("""
                   SELECT category,
                          SUM(amount)
                   FROM expenses
                   WHERE user_id = ?
                     AND DATE (expense_date) BETWEEN ?
                     AND ?
                   GROUP BY category
                   ORDER BY SUM (amount) DESC
                   """, (
                       user_id,
                       start_date,
                       end_date
                   ))

    categories = [
        {
            "category": row[0],
            "amount": row[1]
        }
        for row in cursor.fetchall()
    ]

    conn.close()

    return {
        "username": username,
        "date_range": {
            "from": start_date,
            "to": end_date
        },
        "total_expenses": count,
        "total_amount": round(total, 2),
        "average_per_expense": round(average, 2),
        "category_breakdown": categories
    }


def seed_dummy_expenses():
    username = config.get_active_user()

    if username is None:
        return "No active user selected. Use set_active_user() first."

    user_id = get_user_id(username)

    if user_id is None:
        return "Active user does not exist. Please register the user first."
    titles = [
        "Lunch", "Dinner", "Groceries", "Coffee", "Fuel",
        "Uber", "Bus Ticket", "Medicine", "Internet Bill",
        "Electricity Bill", "Movie", "Books", "Clothes",
        "Shoes", "Gym Fee", "Pizza", "Burger", "Tea",
        "Mobile Recharge", "Stationery"
    ]

    categories = [
        "Food",
        "Transport",
        "Bills",
        "Shopping",
        "Medical",
        "Entertainment",
        "Education"
    ]

    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now()

    for _ in range(20):
        title = random.choice(titles)
        category = random.choice(categories)
        amount = round(random.uniform(100, 5000), 2)

        random_days = random.randint(0, 89)
        expense_date = today - timedelta(days=random_days)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
                       INSERT INTO expenses(user_id,
                                            title,
                                            amount,
                                            category,
                                            expense_date,
                                            created_at)
                       VALUES (?, ?, ?, ?, ?, ?)
                       """, (
                           user_id,
                           title,
                           amount,
                           category,
                           expense_date,
                           created_at
                       ))

    conn.commit()
    conn.close()

    return "20 dummy expenses created successfully."
