import sqlite3
import datetime
import logging
import os
from typing import Optional, Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_file: str = "customer_service.db"):
        self.db_file = db_file
        logger.info(f"Initializing database at {self.db_file}")
        
        if os.path.exists(self.db_file):
            try:
                os.remove(self.db_file)
                logger.info(f"Deleted existing database: {self.db_file}")
            except Exception as e:
                logger.error(f"Error deleting database: {e}")
        
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        logger.info("Creating tables...")
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_email TEXT,
            order_date TEXT,
            total_amount REAL,
            status TEXT
        )
        ''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS product_issues (
            issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            issue_type TEXT,
            solution TEXT
        )
        ''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS store_info (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        ''')

        logger.info("Inserting mock orders data...")
        orders = [
            ("R-98765", "customer1@example.com", "2024-03-01", 149.99, "delivered"),
            ("R-11223", "customer2@example.com", "2024-02-15", 79.99, "delivered"),
            ("R-44556", "customer3@example.com", "2024-01-20", 199.99, "delivered")
        ]
        c.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", orders)

        logger.info("Inserting mock product issues data...")
        issues = [
            ("Toaster", "not working", "1. Check if the power cord is properly plugged in\n2. Test the outlet with another device\n3. Check if the lever is stuck"),
            ("Coffee Maker", "leaking", "1. Check if the water reservoir is properly seated\n2. Inspect the seal for damage\n3. Clean the valve"),
            ("Blender", "not blending", "1. Ensure the jar is properly locked\n2. Check blade assembly\n3. Verify speed settings")
        ]
        c.executemany("INSERT INTO product_issues (product_name, issue_type, solution) VALUES (?, ?, ?)", issues)

        logger.info("Inserting mock store info data...")
        store_info = [
            ("weekend_hours", "Saturday: 10AM-6PM, Sunday: 12PM-5PM"),
            ("contact_email", "support@example.com"),
            ("phone", "1-800-420-4567")
        ]
        c.executemany("INSERT INTO store_info VALUES (?, ?)", store_info)

        conn.commit()
        conn.close()
        logger.info("Database initialization completed")

    def check_refund_eligibility(self, order_id: str) -> Dict:
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        c.execute("SELECT order_date, total_amount, status FROM orders WHERE order_id = ?", (order_id,))
        result = c.fetchone()
        conn.close()

        if not result:
            return {
                "eligible": False,
                "reason": "Order not found",
                "details": None
            }

        order_date, total_amount, status = result
        order_date = datetime.datetime.strptime(order_date, "%Y-%m-%d")
        days_since_order = (datetime.datetime.now() - order_date).days

        if days_since_order > 30:
            return {
                "eligible": False,
                "reason": "Order is more than 30 days old",
                "details": {
                    "order_date": order_date.strftime("%Y-%m-%d"),
                    "days_since_order": days_since_order
                }
            }

        return {
            "eligible": True,
            "reason": "Order is eligible for refund",
            "details": {
                "order_date": order_date.strftime("%Y-%m-%d"),
                "total_amount": total_amount,
                "status": status
            }
        }

    def get_product_solution(self, product_name: str, issue_type: Optional[str] = None) -> Dict:
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        if issue_type:
            c.execute("""
                SELECT solution 
                FROM product_issues 
                WHERE LOWER(product_name) LIKE LOWER(?) 
                AND LOWER(issue_type) LIKE LOWER(?)
            """, (f"%{product_name}%", f"%{issue_type}%"))
        else:
            c.execute("""
                SELECT solution 
                FROM product_issues 
                WHERE LOWER(product_name) LIKE LOWER(?)
            """, (f"%{product_name}%",))

        result = c.fetchone()
        conn.close()

        if not result:
            return {
                "found": False,
                "message": "No solution found for this product/issue",
                "solution": None
            }

        return {
            "found": True,
            "message": "Solution found",
            "solution": result[0]
        }

    def get_store_info(self, key: str) -> str:
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        c.execute("SELECT value FROM store_info WHERE key = ?", (key,))
        result = c.fetchone()
        conn.close()

        return result[0] if result else "Information not found" 