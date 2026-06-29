# data/db_manager.py
import sqlite3
import os

DB_PATH = os.path.join("data", "employee_management.db")

def init_db():
    # Đảm bảo thư mục data tồn tại
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Bảng thông tin nhân viên (Mục đăng ký)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        emp_id TEXT PRIMARY KEY,
        fullname TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        position TEXT
    )
    """)
    
    # Bảng quản lý lịch trực (Giống như bãi đỗ xe: theo Ngày và Ca)
    # Status: 'ASSIGNED' hoặc 'WAITING' (Hàng đợi)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day_of_week TEXT NOT NULL,
        shift TEXT NOT NULL,
        emp_id TEXT,
        status TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (emp_id) REFERENCES employees (emp_id)
    )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()