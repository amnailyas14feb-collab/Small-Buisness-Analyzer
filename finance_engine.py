# finance_engine.py
"""
CONSOLIDATED FINANCE ENGINE
This file contains the core logic for the Small Business Finance Analyzer:
1. Data Models (Classes)
2. Database Management (SQLite)
3. Data Import/Export (CSV)
4. Business Managers (Inventory, Cash Flow, Financial Analysis)
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Type, TypeVar, Dict
import os

# ==========================================
# SECTION 1: DATA MODELS
# ==========================================

class InventoryItem:
    def __init__(self, item_id: str, name: str, description: str, unit_cost: float, unit_price: float, stock_quantity: int, reorder_level: int, last_updated: Optional[datetime] = None):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.unit_cost = unit_cost
        self.unit_price = unit_price
        self.stock_quantity = stock_quantity
        self.reorder_level = reorder_level
        self.last_updated = last_updated if last_updated else datetime.now()

    def __repr__(self):
        return f"InventoryItem(ID: {self.item_id}, Name: {self.name}, Stock: {self.stock_quantity})"

class Sale:
    def __init__(self, sale_id: str, item_id: str, quantity: int, sale_price_per_unit: float, sale_date: datetime):
        self.sale_id = sale_id
        self.item_id = item_id
        self.quantity = quantity
        self.sale_price_per_unit = sale_price_per_unit
        self.sale_date = sale_date
        self.total_amount = quantity * sale_price_per_unit

    def __repr__(self):
        return f"Sale(ID: {self.sale_id}, Item: {self.item_id}, Qty: {self.quantity}, Total: {self.total_amount:.2f})"

class Purchase:
    def __init__(self, purchase_id: str, item_id: str, quantity: int, purchase_price_per_unit: float, purchase_date: datetime, supplier: Optional[str] = None):
        self.purchase_id = purchase_id
        self.item_id = item_id
        self.quantity = quantity
        self.purchase_price_per_unit = purchase_price_per_unit
        self.purchase_date = purchase_date
        self.supplier = supplier
        self.total_amount = quantity * purchase_price_per_unit

    def __repr__(self):
        return f"Purchase(ID: {self.purchase_id}, Item: {self.item_id}, Qty: {self.quantity}, Total: {self.total_amount:.2f})"

class Expense:
    def __init__(self, expense_id: str, category: str, amount: float, expense_date: datetime, description: Optional[str] = None):
        self.expense_id = expense_id
        self.category = category
        self.amount = amount
        self.expense_date = expense_date
        self.description = description

    def __repr__(self):
        return f"Expense(ID: {self.expense_id}, Category: {self.category}, Amount: {self.amount:.2f}, Date: {self.expense_date.strftime('%Y-%m-%d')})"

class CashTransaction:
    def __init__(self, transaction_id: str, transaction_type: str, amount: float, transaction_date: datetime, description: Optional[str] = None, related_id: Optional[str] = None):
        self.transaction_id = transaction_id
        self.transaction_type = transaction_type
        self.amount = amount
        self.transaction_date = transaction_date
        self.description = description
        self.related_id = related_id

    def __repr__(self):
        return f"CashTransaction(ID: {self.transaction_id}, Type: {self.transaction_type}, Amount: {self.amount:.2f}, Date: {self.transaction_date.strftime('%Y-%m-%d')})"

# ==========================================
# SECTION 2: DATABASE MANAGEMENT
# ==========================================

DATABASE_NAME = 'finance_analyzer.db'

def connect_db():
    return sqlite3.connect(DATABASE_NAME)

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory_items (item_id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT, unit_cost REAL NOT NULL, unit_price REAL NOT NULL, stock_quantity INTEGER NOT NULL, reorder_level INTEGER NOT NULL, last_updated TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS sales (sale_id TEXT PRIMARY KEY, item_id TEXT NOT NULL, quantity INTEGER NOT NULL, sale_price_per_unit REAL NOT NULL, sale_date TEXT NOT NULL, total_amount REAL NOT NULL, FOREIGN KEY (item_id) REFERENCES inventory_items (item_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS purchases (purchase_id TEXT PRIMARY KEY, item_id TEXT NOT NULL, quantity INTEGER NOT NULL, purchase_price_per_unit REAL NOT NULL, purchase_date TEXT NOT NULL, supplier TEXT, total_amount REAL NOT NULL, FOREIGN KEY (item_id) REFERENCES inventory_items (item_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (expense_id TEXT PRIMARY KEY, category TEXT NOT NULL, amount REAL NOT NULL, expense_date TEXT NOT NULL, description TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS cash_transactions (transaction_id TEXT PRIMARY KEY, transaction_type TEXT NOT NULL, amount REAL NOT NULL, transaction_date TEXT NOT NULL, description TEXT, related_id TEXT)''')
    conn.commit()
    conn.close()

def save_inventory_item(item: InventoryItem):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''INSERT OR REPLACE INTO inventory_items VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                   (item.item_id, item.name, item.description, item.unit_cost, item.unit_price, item.stock_quantity, item.reorder_level, item.last_updated.isoformat()))
    conn.commit()
    conn.close()

def save_sale(sale: Sale):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''INSERT OR REPLACE INTO sales VALUES (?, ?, ?, ?, ?, ?)''', (sale.sale_id, sale.item_id, sale.quantity, sale.sale_price_per_unit, sale.sale_date.isoformat(), sale.total_amount))
    conn.commit()
    conn.close()

def save_purchase(purchase: Purchase):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''INSERT OR REPLACE INTO purchases VALUES (?, ?, ?, ?, ?, ?, ?)''', (purchase.purchase_id, purchase.item_id, purchase.quantity, purchase.purchase_price_per_unit, purchase.purchase_date.isoformat(), purchase.supplier, purchase.total_amount))
    conn.commit()
    conn.close()

def save_expense(expense: Expense):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''INSERT OR REPLACE INTO expenses VALUES (?, ?, ?, ?, ?)''', (expense.expense_id, expense.category, expense.amount, expense.expense_date.isoformat(), expense.description))
    conn.commit()
    conn.close()

def save_cash_transaction(transaction: CashTransaction):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''INSERT OR REPLACE INTO cash_transactions VALUES (?, ?, ?, ?, ?, ?)''', (transaction.transaction_id, transaction.transaction_type, transaction.amount, transaction.transaction_date.isoformat(), transaction.description, transaction.related_id))
    conn.commit()
    conn.close()

def load_all_records(model_class: Type) -> List:
    conn = connect_db()
    cursor = conn.cursor()
    if model_class == InventoryItem:
        cursor.execute("SELECT * FROM inventory_items")
        return [InventoryItem(r[0], r[1], r[2], r[3], r[4], r[5], r[6], datetime.fromisoformat(r[7])) for r in cursor.fetchall()]
    elif model_class == Sale:
        cursor.execute("SELECT * FROM sales")
        return [Sale(r[0], r[1], r[2], r[3], datetime.fromisoformat(r[4])) for r in cursor.fetchall()]
    elif model_class == Purchase:
        cursor.execute("SELECT * FROM purchases")
        return [Purchase(r[0], r[1], r[2], r[3], datetime.fromisoformat(r[4]), r[5]) for r in cursor.fetchall()]
    elif model_class == Expense:
        cursor.execute("SELECT * FROM expenses")
        return [Expense(r[0], r[1], r[2], datetime.fromisoformat(r[3]), r[4]) for r in cursor.fetchall()]
    elif model_class == CashTransaction:
        cursor.execute("SELECT * FROM cash_transactions")
        return [CashTransaction(r[0], r[1], r[2], datetime.fromisoformat(r[3]), r[4], r[5]) for r in cursor.fetchall()]
    conn.close()
    return []

def get_record_by_id(model_class: Type, record_id: str):
    conn = connect_db()
    cursor = conn.cursor()
    if model_class == InventoryItem:
        cursor.execute("SELECT * FROM inventory_items WHERE item_id = ?", (record_id,))
        r = cursor.fetchone()
        return InventoryItem(r[0], r[1], r[2], r[3], r[4], r[5], r[6], datetime.fromisoformat(r[7])) if r else None
    # Add other models if needed
    conn.close()
    return None

# ==========================================
# SECTION 3: DATA MANAGEMENT (CSV)
# ==========================================

T = TypeVar('T', InventoryItem, Sale, Purchase, Expense, CashTransaction)

def load_data_from_csv(file_path: str, model_class: Type[T]) -> List[T]:
    try:
        df = pd.read_csv(file_path)
        data_list = []
        for _, row in df.iterrows():
            if model_class == InventoryItem:
                data_list.append(InventoryItem(str(row['item_id']), row['name'], row['description'], float(row['unit_cost']), float(row['unit_price']), int(row['stock_quantity']), int(row['reorder_level'])))
            elif model_class == Sale:
                data_list.append(Sale(str(row['sale_id']), str(row['item_id']), int(row['quantity']), float(row['sale_price_per_unit']), datetime.strptime(row['sale_date'], '%Y-%m-%d %H:%M:%S')))
            # Add other models as needed
        return data_list
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return []

def export_data_to_csv(file_path: str, model_class: Type[T]):
    try:
        all_records = load_all_records(model_class)
        if all_records:
            pd.DataFrame([obj.__dict__ for obj in all_records]).to_csv(file_path, index=False)
            print(f"Exported to {file_path}")
    except Exception as e:
        print(f"Error exporting CSV: {e}")

# ==========================================
# SECTION 4: BUSINESS MANAGERS
# ==========================================

class InventoryManager:
    def __init__(self): create_tables()
    def update_inventory_after_sale(self, sale: Sale):
        item = get_record_by_id(InventoryItem, sale.item_id)
        if item and item.stock_quantity >= sale.quantity:
            item.stock_quantity -= sale.quantity
            save_inventory_item(item)
    def calculate_total_inventory_value(self) -> float:
        return sum(item.stock_quantity * item.unit_cost for item in load_all_records(InventoryItem))

class CashFlowManager:
    def __init__(self): create_tables()
    def record_cash_transaction(self, t_type: str, amount: float, date: datetime, desc: str = None, rel_id: str = None):
        t_id = f"CT-{int(datetime.now().timestamp())}"
        save_cash_transaction(CashTransaction(t_id, t_type, amount, date, desc, rel_id))
    def get_cash_flow_statement(self, start_date: datetime, end_date: datetime) -> dict:
        txs = load_all_records(CashTransaction)
        inflows = sum(t.amount for t in txs if start_date <= t.transaction_date <= end_date and t.transaction_type == "inflow")
        outflows = sum(t.amount for t in txs if start_date <= t.transaction_date <= end_date and t.transaction_type == "outflow")
        return {"total_inflows": inflows, "total_outflows": outflows, "net_cash_flow": inflows - outflows}

class FinancialAnalyzer:
    def __init__(self): create_tables()
    def calculate_gross_profit_margin(self, start_date: datetime, end_date: datetime) -> float:
        sales = [s for s in load_all_records(Sale) if start_date <= s.sale_date <= end_date]
        revenue = sum(s.total_amount for s in sales)
        cogs = sum(get_record_by_id(InventoryItem, s.item_id).unit_cost * s.quantity for s in sales if get_record_by_id(InventoryItem, s.item_id))
        return ((revenue - cogs) / revenue * 100) if revenue > 0 else 0.0
