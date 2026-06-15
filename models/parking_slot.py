from typing import Optional
from models.vehicle import Vehicle

class ParkingSlot:
    def __init__(self, slot_id: str, slot_type: str):
        self.slot_id = slot_id            # e.g., "A-1-1"
        self.slot_type = slot_type        # "Motorbike" or "Car"
        self.status = "Empty"             # "Empty" or "Occupied"
        self.current_vehicle: Optional[Vehicle] = None

    def park_vehicle(self, vehicle: Vehicle):
        self.current_vehicle = vehicle
        self.status = "Occupied"

    def release_slot(self):
        self.current_vehicle = None
        self.status = "Empty"