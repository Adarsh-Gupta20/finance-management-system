import sqlite3
import sys

def print_help():
    print("Usage:")
    print("  python query_db.py users             - List all users")
    print("  python query_db.py transactions      - List all transactions")
    print("  python query_db.py user <username>   - Find user by username")
    print("  python query_db.py expenses <userid> - List expenses for user")
    print("  python query_db.py income <userid>   - List income for user")
    print("  python query_db.py sql \"<sql query>\" - Run custom SQL query")

def execute_query(query, params=None):
    conn = sqlite3.connect('instance/finance.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("No results found")
            return
            
        # Print column names
        if rows:
            columns = rows[0].keys()
            header = " | ".join(columns)
            print(header)
            print("-" * len(header))
        
        # Print rows
        for row in rows:
            values = [str(row[col]) for col in columns]
            print(" | ".join(values))
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)
        
    command = sys.argv[1].lower()
    
    if command == "users":
        execute_query("SELECT * FROM 'user'")
        
    elif command == "transactions":
        execute_query("SELECT * FROM 'transaction' ORDER BY date DESC")
        
    elif command == "user" and len(sys.argv) >= 3:
        username = sys.argv[2]
        execute_query("SELECT * FROM 'user' WHERE username LIKE ?", ('%'+username+'%',))
        
    elif command == "expenses" and len(sys.argv) >= 3:
        user_id = sys.argv[2]
        execute_query("""
            SELECT date, category, amount, description 
            FROM 'transaction' 
            WHERE user_id = ? AND type = 'expense'
            ORDER BY date DESC
        """, (user_id,))
        
    elif command == "income" and len(sys.argv) >= 3:
        user_id = sys.argv[2]
        execute_query("""
            SELECT date, category, amount, description 
            FROM 'transaction' 
            WHERE user_id = ? AND type = 'income'
            ORDER BY date DESC
        """, (user_id,))
        
    elif command == "sql" and len(sys.argv) >= 3:
        sql_query = sys.argv[2]
        execute_query(sql_query)
        
    else:
        print_help() 