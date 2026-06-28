from data.parking_db import ParkingDB
from models.motorbike import XeMay, ViTriDo
from datetime import datetime

class MotorbikeController:
    def __init__(self):
        ParkingDB.init_db() # Đảm bảo DB được khởi tạo khi gọi Controller

    def get_all_slots(self):
        """Lấy danh sách ô đỗ từ SQLite trả về dạng ma trận/mảng 2 chiều phục vụ UI"""
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM motorbike_slots ORDER BY row_idx, col_idx")
        rows_data = cursor.fetchall()
        conn.close()

        # Tìm kích thước ma trận
        max_r = max(x[1] for x in rows_data) + 1
        max_c = max(x[2] for x in rows_data) + 1
        
        # Tạo ma trận trống
        grid = [[None for _ in range(max_c)] for _ in range(max_r)]
        
        for item in rows_data:
            slot_id, r, c, status, plate, in_time_str = item
            xe = None
            if status == "Occupied" and plate:
                in_time = datetime.strptime(in_time_str, "%Y-%m-%d %H:%M:%S")
                xe = XeMay(plate, in_time)
            grid[r][c] = ViTriDo(slot_id, r, c, status, xe)
        return grid

    def process_check_in(self, license_plate):
        """THUẬT TOÁN TÌM KIẾM TUYẾN TÍNH (Linear Search): Tìm vị trí trống gần cổng nhất"""
        grid = self.get_all_slots()
        target_slot = None
        
        # Duyệt tuần tự mảng 2 chiều từ hàng đầu tiên, cột đầu tiên [0][0] (gần cổng nhất)
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                if grid[r][c].status == "Empty":
                    target_slot = grid[r][c]
                    break # Thoát vòng lặp ngay khi tìm thấy vị trí tối ưu gần cổng nhất
            if target_slot:
                break

        if not target_slot:
            raise Exception("LotFullError: Khu vực xe máy đã hết vị trí trống!")

        # Lưu thông tin vào SQLite
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE motorbike_slots 
            SET status = 'Occupied', license_plate = ?, check_in_time = ?
            WHERE slot_id = ?
        """, (license_plate, now_str, target_slot.slot_id))
        conn.commit()
        conn.close()
        return target_slot.slot_id

    def process_check_out(self, slot_id, must_print_receipt=False):
        """Xử lý check-out trực tiếp qua Mã vị trí đỗ (Không cần gõ biển số)"""
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT license_plate, check_in_time FROM motorbike_slots WHERE slot_id = ?", (slot_id,))
        result = cursor.fetchone()
        
        if not result or not result[0]:
            conn.close()
            raise Exception("VehicleNotFoundError: Vị trí này hiện không có xe đỗ!")
            
        plate, in_time_str = result
        in_time = datetime.strptime(in_time_str, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Sử dụng tính chất đa hình của thực thể lớp XeMay để tính tiền
        xe_may = XeMay(plate, in_time)
        fee = xe_may.tinh_tien_gui(now)
        
        # 1. Lưu hóa đơn vào lịch sử hệ thống (Cho bạn C dùng)
        cursor.execute("""
            INSERT INTO parking_history (license_plate, vehicle_type, slot_id, check_in_time, check_out_time, fee)
            VALUES (?, 'Motorbike', ?, ?, ?, ?)
        """, (plate, slot_id, in_time_str, now_str, fee))
        
        # 2. Giải phóng bộ nhớ / Làm trống vị trí đỗ trong SQLite
        cursor.execute("""
            UPDATE motorbike_slots 
            SET status = 'Empty', license_plate = NULL, check_in_time = NULL
            WHERE slot_id = ?
        """, (slot_id,))
        
        conn.commit()
        conn.close()
        
        receipt_text = f"--- BIÊN LAI THU PHÍ ---\nBiển Số: {plate}\nMã Chỗ: {slot_id}\nVào: {in_time_str}\nRa: {now_str}\nTông tiền: {fee:,.0f} VND\nTrạng thái: Đã thanh toán."
        return receipt_text
    
    def process_manual_check_in(self, license_plate, slot_id):
        """CHỨC NĂNG THỦ CÔNG: Cho xe vào chính xác ô đỗ được chọn bằng chuột"""
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        
        # Tiến hành ghi nhận xe vào ô đỗ được chọn
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE motorbike_slots 
            SET status = 'Occupied', license_plate = ?, check_in_time = ?
            WHERE slot_id = ?
        """, (license_plate, now_str, slot_id))
        
        conn.commit()
        conn.close()
        return slot_id
        """CHỨC NĂNG THỦ CÔNG: Cho xe vào chính xác ô đỗ được chọn bằng chuột"""
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        
        # Kiểm tra xem ô đỗ đó hiện tại có thực sự trống không (Tránh xung đột dữ liệu)
        cursor.execute("SELECT status FROM motorbike_slots WHERE slot_id = ?", (slot_id,))
        result = cursor.fetchone()
        
        if result and result[0] == 'Occupied':
            conn.close()
            raise Exception("Vị trí này vừa có xe khác đỗ vào, vui lòng chọn vị trí khác!")

        # Tiến hành ghi nhận xe vào ô đỗ được chọn
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE motorbike_slots 
            SET status = 'Occupied', license_plate = ?, check_in_time = ?
            WHERE slot_id = ?
        """, (license_plate, now_str, slot_id))
        
        conn.commit()
        conn.close()
        return slot_id