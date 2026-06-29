from data.parking_db import ParkingDB
from models.motorbike import XeMay, ViTriDo
from datetime import datetime
import csv
import json
import os

class MotorbikeController:
    def __init__(self):
        ParkingDB.init_db() 

    def get_all_slots(self):
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM motorbike_slots ORDER BY row_idx, col_idx")
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
                xe = XeMay(plate, in_time)
            grid[r][c] = ViTriDo(slot_id, r, c, status, xe)
        return grid

    def check_duplicate_plate(self, license_plate):
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT slot_id FROM motorbike_slots WHERE status = 'Occupied' AND license_plate = ?", (license_plate,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def process_check_in(self, license_plate):
        if self.check_duplicate_plate(license_plate):
            raise Exception(f"DuplicatePlateError: Xe máy biển số [{license_plate}] đã ở trong bãi xe rồi!")

        grid = self.get_all_slots()
        target_slot = None
        
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                if grid[r][c].status == "Empty":
                    target_slot = grid[r][c]
                    break 
            if target_slot:
                break

        if not target_slot:
            raise Exception("LotFullError: Khu vực xe máy đã hết vị trí trống!")

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
        
        xe_may = XeMay(plate, in_time)
        fee = xe_may.tinh_tien_gui(now)
        
        cursor.execute("""
            INSERT INTO parking_history (license_plate, vehicle_type, slot_id, check_in_time, check_out_time, fee)
            VALUES (?, 'Motorbike', ?, ?, ?, ?)
        """, (plate, slot_id, in_time_str, now_str, fee))
        
        cursor.execute("""
            UPDATE motorbike_slots 
            SET status = 'Empty', license_plate = NULL, check_in_time = NULL
            WHERE slot_id = ?
        """, (slot_id,))
        
        conn.commit()
        conn.close()
        
        receipt_text = f"--- BIÊN LAI THU PHÍ ---\nBiển Số: {plate}\nMã Chỗ: {slot_id}\nVào: {in_time_str}\nRa: {now_str}\nTổng tiền: {fee:,.0f} VND\nTrạng thái: Đã thanh toán."
        return receipt_text
    
    def save_log_to_csv(self, vehicle_data):
     file_exists = os.path.isfile('parking_history_motorbike.csv')
     with open('parking_history_motorbike.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["plate", "in", "out", "fee"])
        if not file_exists: writer.writeheader()
        writer.writerow(vehicle_data)
    
    def process_manual_check_in(self, license_plate, slot_id):
        if self.check_duplicate_plate(license_plate):
            raise Exception(f"DuplicatePlateError: Xe máy biển số [{license_plate}] đã ở trong bãi xe rồi!")

        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT status FROM motorbike_slots WHERE slot_id = ?", (slot_id,))
        result = cursor.fetchone()
        
        if result and result[0] == 'Occupied':
            conn.close()
            raise Exception("Vị trí này vừa có xe khác đỗ vào, vui lòng chọn vị trí khác!")

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE motorbike_slots 
            SET status = 'Occupied', license_plate = ?, check_in_time = ?
            WHERE slot_id = ?
        """, (license_plate, now_str, slot_id))
        
        conn.commit()
        conn.close()
        return slot_id

    def update_vehicle_plate(self, slot_id, new_plate):
        if not new_plate:
            raise Exception("Biển số xe mới không được để trống!")
            
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE motorbike_slots 
            SET license_plate = ? 
            WHERE slot_id = ? AND status = 'Occupied'
        """, (new_plate, slot_id))
        conn.commit()
        conn.close()

    def delete_vehicle_force(self, slot_id):
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE motorbike_slots 
            SET status = 'Empty', license_plate = NULL, check_in_time = NULL 
            WHERE slot_id = ?
        """, (slot_id,))
        conn.commit()
        conn.close()

    def get_parking_history(self):
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, license_plate, slot_id, check_in_time, check_out_time, fee FROM parking_history")
        rows = cursor.fetchall()
        conn.close()
        
        history_list = []
        for item in rows:
            history_list.append({
                "id": item[0],
                "plate": item[1],
                "slot_id": item[2],
                "time_in": item[3],
                "time_out": item[4],
                "fee": item[5]
            })
        return history_list

    def quick_sort_history_by_fee(self, arr, low, high):
        if low < high:
            pivot_idx = self._partition(arr, low, high)
            self.quick_sort_history_by_fee(arr, low, pivot_idx - 1)
            self.quick_sort_history_by_fee(arr, pivot_idx + 1, high)

    def _partition(self, arr, low, high):
        pivot = arr[high]["fee"]
        i = low - 1
        for j in range(low, high):
            if arr[j]["fee"] >= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1
    
    def clear_all_parking_history(self):
        """Xóa toàn bộ lịch sử hóa đơn trong cơ sở dữ liệu"""
        conn = ParkingDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM parking_history")
        conn.commit()
        conn.close()