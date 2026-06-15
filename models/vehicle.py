from abc import ABC, abstractmethod
from datetime import datetime
import math

class Vehicle(ABC):
    def __init__(self, license_plate, vehicle_type):
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type
        self.check_in_time = datetime.now()  # Captures real-time check-in timestamp

    @abstractmethod
    def calculate_fee(self, check_out_time: datetime) -> int:
        """Virtual method that must be overridden by subclasses"""
        pass

class Motorbike(Vehicle):
    def __init__(self, license_plate):
        super().__init__(license_plate, "Motorbike")

    def calculate_fee(self, check_out_time: datetime) -> int:
        # Motorbikes are charged a flat rate per turn: 5,000 VND
        return 5000

class Car(Vehicle):
    def __init__(self, license_plate):
        super().__init__(license_plate, "Car")

    def calculate_fee(self, check_out_time: datetime) -> int:
        # Cars are charged progressively per hour: 25,000 VND for 1st hour, +10,000 VND each subsequent hour
        duration = check_out_time - self.check_in_time
        hours = math.ceil(duration.total_seconds() / 3600)  # Ceil to nearest hour
        
        if hours <= 0:
            hours = 1
            
        first_hour_rate = 25000
        subsequent_hour_rate = 10000
        
        return first_hour_rate + (hours - 1) * subsequent_hour_rate