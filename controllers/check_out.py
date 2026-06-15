from controllers.base_mananger import BaseParkingManager
from models.vehicle import Motorbike, Car
from exceptions import VehicleNotFoundError
from datetime import datetime

class CheckOutController(BaseParkingManager):
    def __init__(self, rows=3, cols=4):
        super().__init__(rows, cols)

    def process_check_out(self, license_plate: str):
        slot = self.find_vehicle_by_plate(license_plate)
        
        if not slot:
            raise VehicleNotFoundError(f"License plate {license_plate} not found in the system!")
        
        vehicle = slot.current_vehicle
        check_out_time = datetime.now()
        fee = vehicle.calculate_fee(check_out_time)
        
        # Log to structural record file
        log_entry = {
            "license_plate": vehicle.license_plate,
            "vehicle_type": vehicle.vehicle_type,
            "slot_id": slot.slot_id,
            "check_in_time": vehicle.check_in_time.strftime("%Y-%m-%d %H:%M:%S"),
            "check_out_time": check_out_time.strftime("%Y-%m-%d %H:%M:%S"),
            "fee": fee
        }
        self.parking_history.append(log_entry)
        self.save_history()
        
        # Memory Management: Dereference vehicle object and reset slot status to Empty
        released_type = vehicle.vehicle_type
        slot.release_slot()
        
        # QUEUE DISPATCHER: If queue has matching vehicle type, pull it directly into this slot
        queue_msg = ""
        if not self.waiting_queue.is_empty():
            current = self.waiting_queue.front
            prev = None
            while current:
                waiting_vehicle = current.data
                if waiting_vehicle["vehicle_type"] == released_type:
                    # Remove node manually from Linked List
                    if prev is None:
                        self.waiting_queue.dequeue()
                    else:
                        prev.next = current.next
                        if current == self.waiting_queue.rear:
                            self.waiting_queue.rear = prev
                        self.waiting_queue.size -= 1
                    
                    # Automate Check-In execution for waiting vehicle
                    next_vehicle = Motorbike(waiting_vehicle["license_plate"]) if released_type == "Motorbike" else Car(waiting_vehicle["license_plate"])
                    slot.park_vehicle(next_vehicle)
                    queue_msg = f"\n[Queue] Vehicle {waiting_vehicle['license_plate']} from waiting line has been auto-parked into slot {slot.slot_id}."
                    break
                prev = current
                current = current.next

        return fee, f"Payment successfully cleared! Total Fee: {fee:,} VND.{queue_msg}"