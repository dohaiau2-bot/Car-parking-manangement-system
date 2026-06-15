import os
import json
from models.parking_slot import ParkingSlot
from models.custom_queue import CustomQueue

class BaseParkingManager:
    def __init__(self, rows=3, cols=4):
        self.rows = rows
        self.cols = cols
        
        # 2D arrays simulating parking layouts for Zone A (Motorbikes) and Zone B (Cars)
        self.motorbike_lot = [[ParkingSlot(f"A-{r+1}-{c+1}", "Motorbike") for c in range(cols)] for r in range(rows)]
        self.car_lot = [[ParkingSlot(f"B-{r+1}-{c+1}", "Car") for c in range(cols)] for r in range(rows)]
        
        # Queue managing vehicles waiting at the entrance gate when the lot is full
        self.waiting_queue = CustomQueue()
        
        self.data_file = "data/parking_history.json"
        self.init_storage()
        self.parking_history = self.load_history()

    def init_storage(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)

    def load_history(self):
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def save_history(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.parking_history, f, ensure_ascii=False, indent=4)

    def find_vehicle_by_plate(self, license_plate: str):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.motorbike_lot[r][c].current_vehicle and self.motorbike_lot[r][c].current_vehicle.license_plate == license_plate:
                    return self.motorbike_lot[r][c]
                if self.car_lot[r][c].current_vehicle and self.car_lot[r][c].current_vehicle.license_plate == license_plate:
                    return self.car_lot[r][c]
        return None