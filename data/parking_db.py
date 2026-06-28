import sqlite3
import os

class ParkingDB:
    @staticmethod
    def get_connection():
        # Tạo thư mục data nếu chưa có
        os.makedirs("data", exist_ok=True)
        return sqlite3.connect("data/parking.db")

    @staticmethod
    def init_db(rows=3, cols=5):
        """Khởi tạo cấu trúc cơ sở dữ liệu bãi xe máy"""
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        
        # 1. Bảng lưu trạng thái các ô đỗ của Xe Máy
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS motorbike_slots (
                slot_id TEXT PRIMARY KEY,
                row_idx INTEGER,
                col_idx INTEGER,
                status TEXT,
                license_plate TEXT,
                check_in_time TEXT
            )
        ''')
        
        # 2. Bảng lưu lịch sử hóa đơn (Bạn C sẽ dùng bảng này để chạy Quick Sort)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parking_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_plate TEXT,
                vehicle_type TEXT,
                slot_id TEXT,
                check_in_time TEXT,
                check_out_time TEXT,
                fee REAL
            )
        ''')
        
        # Tạo dữ liệu các ô đỗ ban đầu nếu bảng trống (Ví dụ: Lưới 3 hàng x 5 cột = 15 chỗ)
        cursor.execute("SELECT COUNT(*) FROM motorbike_slots")
        if cursor.fetchone()[0] == 0:
            for r in range(rows):
                for c in range(cols):
                    slot_id = f"M-{r+1:02d}-{c+1:02d}" # Ví dụ: M-01-01
                    cursor.execute(
                        "INSERT INTO motorbike_slots VALUES (?, ?, ?, 'Empty', NULL, NULL)",
                        (slot_id, r, c)
                    )
        conn.commit()
        conn.close()