import sqlite3

# Connect to the database
conn = sqlite3.connect('instance/finance.db')
conn.row_factory = sqlite3.Row  # This enables column access by name
cursor = conn.cursor()

# Get all transactions with user information
cursor.execute("""
    SELECT t.id, t.amount, t.type, t.category, t.description, t.date, 
           u.username, u.preferred_currency 
    FROM 'transaction' t
    JOIN 'user' u ON t.user_id = u.id
    ORDER BY t.date DESC
""")

transactions = cursor.fetchall()

# Display the results
print(f"Found {len(transactions)} transactions:\n")
print("ID | Amount | Type | Category | Description | Date | Username | Currency")
print("-" * 80)

for t in transactions:
    print(f"{t['id']} | {t['amount']} | {t['type']} | {t['category']} | "
          f"{t['description']} | {t['date']} | {t['username']} | {t['preferred_currency']}")

conn.close() 