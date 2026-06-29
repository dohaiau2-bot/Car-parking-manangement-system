# models/employee_model.py
import sqlite3
from collections import deque
from data.employee_db import DB_PATH

class EmployeeModel:
    def __init__(self):
        self.max_capacity_per_shift = 1 # Định mức: 1 người/ca, nếu thêm sẽ vào hàng đợi

    def connect(self):
        return sqlite3.connect(DB_PATH)

    def add_employee(self, emp_id, fullname, phone, email, position):
        """Đăng ký nhân viên mới vào cơ sở dữ liệu"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO employees VALUES (?, ?, ?, ?, ?)",
                (emp_id, fullname, phone, email, position)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def get_all_employees(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT emp_id, fullname FROM employees")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_schedule_grid(self):
        """Lấy toàn bộ lịch trực để hiển thị lên sơ đồ trực quan"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.day_of_week, s.shift, s.emp_id, e.fullname, s.status 
            FROM schedules s
            LEFT JOIN employees e ON s.emp_id = e.emp_id
            WHERE s.status = 'ASSIGNED'
        """)
        rows = cursor.fetchall()
        conn.close()
        
        grid = {}
        for row in rows:
            day, shift, emp_id, name, status = row
            grid[(day, shift)] = {"emp_id": emp_id, "name": name}
        return grid

    def assign_shift(self, day, shift, emp_id):
        """Phân công ca trực. Nếu ca đã đầy, đẩy vào Hàng đợi (Queue)"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # 1. Kiểm tra xem ca này đã có ai trực chưa
        cursor.execute(
            "SELECT emp_id FROM schedules WHERE day_of_week = ? AND shift = ? AND status = 'ASSIGNED'",
            (day, shift)
        )
        assigned = cursor.fetchall()
        
        if len(assigned) < self.max_capacity_per_shift:
            # Ca trực còn trống -> Cho vào trực chính thức
            cursor.execute(
                "INSERT INTO schedules (day_of_week, shift, emp_id, status) VALUES (?, ?, ?, 'ASSIGNED')",
                (day, shift, emp_id)
            )
            conn.commit()
            conn.close()
            return "ASSIGNED"
        else:
            # Thuật toán tối ưu: Sử dụng Hàng đợi (Queue) mô phỏng hàng chờ[cite: 9, 10]
            # Đọc hàng đợi hiện tại từ DB ra để xử lý bằng deque tốc độ cao O(1)[cite: 9]
            cursor.execute(
                "SELECT emp_id FROM schedules WHERE day_of_week = ? AND shift = ? AND status = 'WAITING' ORDER BY id ASC",
                (day, shift)
            )
            waiting_rows = cursor.fetchall()
            
            waiting_queue = deque([r[0] for r in waiting_rows])
            
            # Kiểm tra xem nhân viên này đã nằm trong hàng đợi hoặc ca trực chưa để tránh trùng lặp
            if emp_id in waiting_queue or any(emp_id == x[0] for x in assigned):
                conn.close()
                return "DUPLICATE"
                
            # Thêm vào cuối hàng đợi (Enqueue)[cite: 9]
            waiting_queue.append(emp_id)
            
            cursor.execute(
                "INSERT INTO schedules (day_of_week, shift, emp_id, status) VALUES (?, ?, ?, 'WAITING')",
                (day, shift, emp_id)
            )
            conn.commit()
            conn.close()
            return "QUEUED"

    def get_waiting_list(self, day, shift):
        """Lấy danh sách hàng đợi của ca tương ứng"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.fullname FROM schedules s
            JOIN employees e ON s.emp_id = e.emp_id
            WHERE s.day_of_week = ? AND s.shift = ? AND s.status = 'WAITING'
            ORDER BY s.id ASC
        """, (day, shift))
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows]
    
    def get_employee_info(self, emp_id):
        """Lấy toàn bộ thông tin của 1 nhân viên theo mã"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE emp_id = ?", (emp_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    def update_employee(self, emp_id, fullname, phone, email, position):
        """Cập nhật thông tin nhân viên"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE employees 
            SET fullname = ?, phone = ?, email = ?, position = ? 
            WHERE emp_id = ?
        """, (fullname, phone, email, position, emp_id))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0

    def delete_employee(self, emp_id):
        """Xóa nhân viên (xóa luôn các lịch trực liên quan để tránh lỗi dữ liệu)"""
        conn = self.connect()
        cursor = conn.cursor()
        # Xóa lịch trực trước
        cursor.execute("DELETE FROM schedules WHERE emp_id = ?", (emp_id,))
        # Xóa nhân viên
        cursor.execute("DELETE FROM employees WHERE emp_id = ?", (emp_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0

    def clear_shift(self, day, shift):
        """Hủy ca trực hiện tại. Người đầu tiên trong hàng đợi (Queue) sẽ được đôn lên thay thế"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Xóa người trực chính hiện tại
        cursor.execute(
            "DELETE FROM schedules WHERE day_of_week = ? AND shift = ? AND status = 'ASSIGNED'",
            (day, shift)
        )
        
        # Thuật toán Queue: Lấy người đầu tiên trong hàng đợi ra (Dequeue)[cite: 9]
        cursor.execute(
            "SELECT id, emp_id FROM schedules WHERE day_of_week = ? AND shift = ? AND status = 'WAITING' ORDER BY id ASC LIMIT 1",
            (day, shift)
        )
        next_inline = cursor.fetchone()
        
        if next_inline:
            row_id, emp_id = next_inline
            # Đôn người này lên làm ASSIGNED
            cursor.execute(
                "UPDATE schedules SET status = 'ASSIGNED' WHERE id = ?",
                (row_id,)
            )
            
        conn.commit()
        conn.close()