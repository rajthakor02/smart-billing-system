from datetime import datetime
import sqlite3
from database import get_connection

def get_products():
    from database import get_connection
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, price, stock
        FROM products
        WHERE is_deleted = 0
    """)

    products = cursor.fetchall()
    conn.close()
    return products

def add_product(name, price, stock):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE name=? AND is_deleted=0", (name,))
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return "EXISTS"
    cursor.execute("INSERT INTO products(name, price, stock) VALUES (?,?,?)",
                   (name, price, stock))
    conn.commit()
    conn.close()

def save_invoice(customer, total):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO invoices(customer, total, date) VALUES (?,?,?)",
                   (customer, total, datetime.now()))
    conn.commit()
    conn.close()
def reduce_stock(product_id, qty):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET stock = stock - ? WHERE id = ?",
        (qty, product_id)
    )
    conn.commit()
    conn.close()
def get_current_stock(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0]
    return 0
def save_sale(product_id, product_name, qty, total_price):
    conn = get_connection()
    cursor = conn.cursor()

    from datetime import datetime
    date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        INSERT INTO sales (product_id, product_name, quantity, total_price, date)
        VALUES (?, ?, ?, ?, ?)
    """, (product_id, product_name, qty, total_price, date))

    conn.commit()
    conn.close()
def update_product(product_id, new_name, new_price, new_stock):
    from database import get_connection
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET name = ?, price = ?, stock = ?
        WHERE id = ?
    """, (new_name, new_price, new_stock, product_id))

    conn.commit()
    conn.close()
def delete_product(product_id):
    from database import get_connection
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET is_deleted = 1
        WHERE id = ?
    """, (product_id,))

    conn.commit()
    conn.close()
def restore_product(product_id):
    from database import get_connection
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET is_deleted = 0
        WHERE id = ?
    """, (product_id,))

    conn.commit()
    conn.close()
def get_deleted_products():
    from database import get_connection
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, price, stock
        FROM products
        WHERE is_deleted = 1
    """)

    products = cursor.fetchall()
    conn.close()
    return products
def get_total_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products WHERE is_deleted=0")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_total_sales_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sales")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_total_revenue():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(total) FROM sales")
    total = cursor.fetchone()[0]
    conn.close()
    return total if total else 0


def get_low_stock_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id,name,stock
        FROM products
        WHERE stock < 5 AND is_deleted=0
    """)
    data = cursor.fetchall()
    conn.close()
    return data