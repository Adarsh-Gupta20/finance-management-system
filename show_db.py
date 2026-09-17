import sqlite3
import os

# Check if database file exists
db_path = 'instance/finance.db'
if not os.path.exists(db_path):
    db_path = 'finance.db'  # Try root directory
    if not os.path.exists(db_path):
        print(f"Database file not found. Please run the app first.")
        exit(1)

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get list of tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Database Tables:")
for table in tables:
    print(f"- {table[0]}")

# Show table contents
for table in tables:
    table_name = table[0]
    print(f"\nContents of table '{table_name}':")
    cursor.execute(f"PRAGMA table_info('{table_name}');")
    columns = cursor.fetchall()
    print("Columns:", [col[1] for col in columns])
    
    cursor.execute(f"SELECT * FROM '{table_name}' LIMIT 5;")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

conn.close() 