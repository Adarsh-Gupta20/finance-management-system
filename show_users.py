import sqlite3

# Connect to the database
conn = sqlite3.connect('instance/finance.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get user information with transaction summaries
cursor.execute("""
    SELECT u.id, u.username, u.email, u.preferred_currency,
           COUNT(t.id) as transaction_count,
           SUM(CASE WHEN t.type = 'income' THEN t.amount ELSE 0 END) as total_income,
           SUM(CASE WHEN t.type = 'expense' THEN t.amount ELSE 0 END) as total_expenses
    FROM 'user' u
    LEFT JOIN 'transaction' t ON u.id = t.user_id
    GROUP BY u.id
    ORDER BY u.id
""")

users = cursor.fetchall()

# Display the results
print(f"Found {len(users)} users:\n")
print("ID | Username | Email | Currency | Transactions | Total Income | Total Expenses | Balance")
print("-" * 100)

for u in users:
    total_income = u['total_income'] or 0
    total_expenses = u['total_expenses'] or 0
    balance = total_income - total_expenses
    
    print(f"{u['id']} | {u['username']} | {u['email']} | {u['preferred_currency']} | "
          f"{u['transaction_count']} | {total_income} | {total_expenses} | {balance}")

conn.close() 