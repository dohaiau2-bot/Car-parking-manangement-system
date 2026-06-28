from data.parking_db import ParkingDB
from models.car import XeOTo, ViTriDo
from datetime import datetime
import json
import csv
import os

class CustomWaitingQueue:
    """Tự cài đặt Hàng đợi (Queue) bằng mảng động phục vụ luồng xe chờ"""
    def __init__(self):
        self.queue_data = []

    def enqueue(self, license_plate):
        if license_plate not in self.queue_data:
            self.queue_data.append(license_plate)

    def dequeue(self):
        if self.is_empty():
            return None
        return self.queue_data.pop(0) # FIFO: Vào trước ra trước

    def is_empty(self):
        return len(self.queue_data) == 0

    def size(self):
        return len(self.queue_data)

    def get_all(self):
        return list(self.queue_data)


class CarController:
    # Biến Class Static để giữ hàng đợi ô tô chờ trong bộ nhớ RAM của hệ thống
    waiting_queue = CustomWaitingQueue()

    def __init__(self):
        ParkingDB.init_db()
        self._ensure_car_slots_table()

    def _ensure_car_slots_table(self):
        """Khởi tạo bảng cấu trúc ma trận Khu B cho ô tô nếu chưa có"""
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS car_slots (
                slot_id TEXT PRIMARY KEY,
                row_idx INTEGER,
                col_idx INTEGER,
                status TEXT,
                license_plate TEXT,
                check_in_time TEXT
            )
        """)
        # Tạo sẵn ma trận Khu B kích thước 3 hàng x 4 cột ô tô
        cursor.execute("SELECT COUNT(*) FROM car_slots")
        if cursor.fetchone()[0] == 0:
            for r in range(3):
                for c in range(4):
                    slot_id = f"B-R{r+1}C{c+1}"
                    cursor.execute("INSERT INTO car_slots VALUES (?, ?, ?, 'Empty', NULL, NULL)", (slot_id, r, c))
            conn.commit()
        conn.close()

    def get_all_slots(self):
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM car_slots ORDER BY row_idx, col_idx")
        rows_data = cursor.fetchall()
        conn.close()

        max_r = max(x[1] for x in rows_data) + 1
        max_c = max(x[2] for x in rows_data) + 1
        grid = [[None for _ in range(max_c)] for _ in range(max_r)]
        
        for item in rows_data:
            slot_id, r, c, status, plate, in_time_str = item
            xe = None
            if status == "Occupied" and plate:
                in_time = datetime.strptime(in_time_str, "%Y-%m-%d %H:%M:%S")
                xe = XeOTo(plate, in_time)
            grid[r][c] = ViTriDo(slot_id, r, c, status, xe)
        return grid

    def check_duplicate_plate(self, license_plate):
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT slot_id FROM car_slots WHERE status = 'Occupied' AND license_plate = ?", (license_plate,))
        res = cursor.fetchone()
        conn.close()
        return res is not None

    def process_check_in(self, license_plate):
        """THUẬT TOÁN TỐI ƯU MỚI: Cấp phát vị trí dựa trên khoảng cách Manhattan"""
        if self.check_duplicate_plate(license_plate):
            raise Exception(f"DuplicateError: Ô tô biển số [{license_plate}] đã ở trong bãi xe Khu B!")

        grid = self.get_all_slots()
        gate_r, gate_c = 0, 0 # Giả định Cổng vào đặt tại tọa độ góc [0][0]
        
        best_slot = None
        min_distance = float('inf')

        # Duyệt toán bộ ma trận để tính toán khoảng cách hình học tối ưu ngắn nhất đến cổng
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                if grid[r][c].status == "Empty":
                    # Công thức khoảng cách Manhattan: |x1 - x2| + |y1 - y2|
                    distance = abs(r - gate_r) + abs(c - gate_c)
                    if distance < min_distance:
                        min_distance = distance
                        best_slot = grid[r][c]

        # Xử lý trường hợp bãi xe đầy bằng cấu trúc Hàng đợi (Queue)
        if not best_slot:
            self.waiting_queue.enqueue(license_plate)
            raise Exception(f"LotFullError: Khu B đã hết chỗ! Xe [{license_plate}] được xếp tự động vào HÀNG ĐỢI CHỜ (Vị trí số: {self.waiting_queue.size()})")

        # Lưu thông tin xe vào ô đỗ tối ưu đã tìm được
        self._write_slot_checkin(best_slot.slot_id, license_plate)
        return best_slot.slot_id

    def _write_slot_checkin(self, slot_id, license_plate):
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE car_slots SET status = 'Occupied', license_plate = ?, check_in_time = ? WHERE slot_id = ?
        """, (license_plate, now_str, slot_id))
        conn.commit()
        conn.close()

    def process_check_out(self, slot_id, must_print_receipt=False):
        """Hàm xử lý xe ra bãi + Tự động giải phóng luồng xe chờ trong Hàng đợi"""
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT license_plate, check_in_time FROM car_slots WHERE slot_id = ?", (slot_id,))
        result = cursor.fetchone()
        
        if not result or not result[0]:
            conn.close()
            raise Exception("VehicleNotFoundError: Vị trí Khu B này không có ô tô đỗ!")
            
        plate, in_time_str = result
        in_time = datetime.strptime(in_time_str, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Sử dụng tính đa hình để tính tiền lũy tiến cho Ô tô
        xe_oto = XeOTo(plate, in_time)
        fee = xe_oto.tinh_tien_gui(now)
        
        # Ghi lịch sử hóa đơn chung vào parking_history để Quick Sort thống kê doanh thu chung
        cursor.execute("""
            INSERT INTO parking_history (license_plate, vehicle_type, slot_id, check_in_time, check_out_time, fee)
            VALUES (?, 'Car', ?, ?, ?, ?)
        """, (plate, slot_id, in_time_str, now_str, fee))
        
        # Đưa trạng thái ô đỗ về rỗng
        cursor.execute("UPDATE car_slots SET status = 'Empty', license_plate = NULL, check_in_time = NULL WHERE slot_id = ?", (slot_id,))
        conn.commit()
        conn.close()
        
        # LUỒNG TỰ ĐỘNG CỦA HÀNG ĐỢI QUEUE: Nếu có xe đang xếp hàng chờ, cho xe đó vào ô trống vừa mở lập tức
        next_car_plate = self.waiting_queue.dequeue()
        queue_msg = ""
        if next_car_plate:
            self._write_slot_checkin(slot_id, next_car_plate)
            queue_msg = f"\n\n🔄 HÀNG ĐỢI DI CHUYỂN: Xe ô tô [{next_car_plate}] ở đầu hàng đợi đã được tự động xếp vào vị trí {slot_id} vừa trống!"

        receipt_text = f"--- BIÊN LAI Ô TÔ KHU B ---\nBiển Số: {plate}\nMã Vị Trí: {slot_id}\nThời gian vào: {in_time_str}\nThời gian ra: {now_str}\nTổng tiền lũy tiến: {fee:,.0f} VND.{queue_msg}"
        return receipt_text

    def process_manual_check_in(self, license_plate, slot_id):
        if self.check_duplicate_plate(license_plate):
            raise Exception(f"DuplicateError: Ô tô biển số [{license_plate}] đã ở trong bãi rồi!")
        self._write_slot_checkin(slot_id, license_plate)

    def get_waiting_cars(self):
        return self.waiting_queue.get_all()
    
    def update_car_plate(self, slot_id, new_plate):
        """SỬA: Cập nhật lại biển số xe bị nhập sai tại vị trí đỗ"""
        if not new_plate:
            raise Exception("Biển số mới không được để trống!")
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE car_slots SET license_plate = ? WHERE slot_id = ?", (new_plate.upper(), slot_id))
        conn.commit()
        conn.close()

    def force_delete_slot(self, slot_id):
        """XÓA: Giải phóng nhanh vị trí đỗ (Không tính tiền, không lưu doanh thu)"""
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE car_slots SET status = 'Empty', license_plate = NULL, check_in_time = NULL WHERE slot_id = ?", (slot_id,))
        conn.commit()
        conn.close()
        
        # Đẩy xe tiếp theo trong hàng đợi vào nếu có
        next_car_plate = self.waiting_queue.dequeue()
        if next_car_plate:
            self._write_slot_checkin(slot_id, next_car_plate)

    def get_live_statistics(self):
        """THỐNG KÊ: Tính toán các thông số thời gian thực cho Khu B và doanh thu tổng"""
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        
        # 1. Đếm tổng số ô đỗ ô tô
        cursor.execute("SELECT COUNT(*) FROM car_slots")
        total_slots = cursor.fetchone()[0] or 1 # Tránh chia cho 0
        
        # 2. Đếm số ô đang có xe đỗ
        cursor.execute("SELECT COUNT(*) FROM car_slots WHERE status = 'Occupied'")
        occupied_slots = cursor.fetchone()[0]
        
        # Tỉ lệ lấp đầy
        fill_rate = (occupied_slots / total_slots) * 100
        
        # 3. Tính tổng doanh thu trong ngày hôm nay (Car + Motorbike từ bảng lịch sử chung)
        today_str = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT SUM(fee) FROM parking_history WHERE check_out_time LIKE ?", (f"{today_str}%",))
        today_revenue = cursor.fetchone()[0] or 0.0
        
        conn.close()
        return {
            "occupied": occupied_slots,
            "fill_rate": fill_rate,
            "revenue": today_revenue
        }

    def export_history_to_file(self, file_type="csv"):
        """LƯU TRỮ FILE: Xuất toàn bộ lịch sử hệ thống ra file CSV hoặc JSON phục vụ hậu kiểm"""
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM parking_history ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            raise Exception("Chưa có dữ liệu lịch sử nào trong database để xuất file!")

        # Tạo thư mục exports nếu chưa có
        if not os.path.exists("exports"):
            os.makedirs("exports")
            
        filename = f"exports/parking_history_backup.{file_type}"
        
        if file_type == "csv":
            with open(filename, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["STT", "Biển Số", "Loại Xe", "Mã Vị Trí", "Thời Gian Vào", "Thời Gian Ra", "Tiền Gửi (VND)"])
                writer.writerows(rows)
        else: # Xuất file JSON
            data_list = []
            for r in rows:
                data_list.append({
                    "id": r[0], "license_plate": r[1], "vehicle_type": r[2],
                    "slot_id": r[3], "check_in_time": r[4], "check_out_time": r[5], "fee": r[6]
                })
            with open(filename, mode='w', encoding='utf-8') as f:
                json.dump(data_list, f, indent=4, ensure_ascii=False)
                
        return filename
    def get_car_checkout_history(self):
        """Lấy danh sách lịch sử CHỈ DÀNH RIÊNG CHO Ô TÔ đã check-out"""
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        # Thêm điều kiện WHERE vehicle_type = 'Car' để lọc bỏ xe máy
        cursor.execute("""
            SELECT id, license_plate, vehicle_type, slot_id, check_in_time, check_out_time, fee 
            FROM parking_history 
            WHERE vehicle_type = 'Car' 
            ORDER BY check_out_time DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def clear_car_checkout_history(self):
        """XÓA SẠCH: Xóa toàn bộ dữ liệu lịch sử xuất bãi của riêng Ô tô"""
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        # Chỉ xóa các bản ghi thuộc loại xe Car
        cursor.execute("DELETE FROM parking_history WHERE vehicle_type = 'Car'")
        conn.commit()
        conn.close()