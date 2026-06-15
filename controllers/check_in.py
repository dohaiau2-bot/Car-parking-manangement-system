from controllers.base_mananger import BaseParkingManager
from models.vehicle import Motorbike, Car
from models.parking_slot import ParkingSlot
from exceptions import LotFullError
from datetime import datetime

class CheckInController(BaseParkingManager):
    def __init__(self, rows=3, cols=4):
        super().__init__(rows, cols)

    # SEARCH ALGORITHM: Sequentially scan the grid to find the closest available slot to the entrance
    def find_empty_slot(self, vehicle_type: str) -> ParkingSlot:
        target_lot = self.motorbike_lot if vehicle_type == "Motorbike" else self.car_lot
        for r in range(self.rows):
            for c in range(self.cols):
                if target_lot[r][c].status == "Empty":
                    return target_lot[r][c]
        return None

    def process_check_in(self, license_plate: str, vehicle_type: str):
        if self.find_vehicle_by_plate(license_plate):
            return "Duplicate", f"Vehicle {license_plate} is already inside the parking lot!"

        empty_slot = self.find_empty_slot(vehicle_type)
        new_vehicle = Motorbike(license_plate) if vehicle_type == "Motorbike" else Car(license_plate)
        
        if empty_slot:
            empty_slot.park_vehicle(new_vehicle)
            return "Success", f"Allocated Slot: {empty_slot.slot_id} successfully!"
        else:
            # If full, automatically forward to the custom Linked-List Queue
            self.waiting_queue.enqueue({
                "license_plate": license_plate, 
                "vehicle_type": vehicle_type, 
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            raise LotFullError(f"{vehicle_type} lot is full! Vehicle {license_plate} has been placed into the waiting queue.")