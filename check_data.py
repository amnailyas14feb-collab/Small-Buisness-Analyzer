import sqlite3
import pandas as pd

# Connect to your database
conn = sqlite3.connect('finance_analyzer.db')

try:
    print("--- INVENTORY TABLE ---")
    df_inv = pd.read_sql_query("SELECT * FROM inventory_items", conn)
    print(df_inv if not df_inv.empty else "Inventory is currently empty.")
    print("\n--- SALES TABLE ---")
    df_sales = pd.read_sql_query("SELECT * FROM sales", conn)
    print(df_sales if not df_sales.empty else "No sales recorded yet.")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()

#to see finace_analyzer.db fil and see what new entries or sales have been made we can write command
#in terminal which is  =  python check_data.py