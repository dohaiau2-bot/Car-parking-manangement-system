from datetime import datetime

class PhuongTien:
    def __init__(self, bien_so, loai_xe, thoi_gian_vao=None):
        self.license_plate = bien_so
        self.vehicle_type = loai_xe
        self.check_in_time = thoi_gian_vao if thoi_gian_vao else datetime.now()

    def tinh_tien_gui(self, thoi_gian_ra):
        """Phương thức ảo / trừu tượng"""
        pass