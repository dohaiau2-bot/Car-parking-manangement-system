class LotFullError(Exception):
    """Exception raised when no empty slots are available for the vehicle type."""
    def __init__(self, message="The parking lot is full for this vehicle type!"):
        self.message = message
        super().__init__(self.message)

class VehicleNotFoundError(Exception):
    """Exception raised when the requested license plate is not found in the lot."""
    def __init__(self, message="Vehicle with this license plate was not found in the lot!"):
        self.message = message
        super().__init__(self.message)