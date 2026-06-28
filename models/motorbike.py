from datetime import datetime

class PhuongTien:
    def __init__(self, bien_so, loai_xe, thoi_gian_vao=None):
        self.license_plate = bien_so
        self.vehicle_type = loai_xe
        self.check_in_time = thoi_gian_vao if thoi_gian_vao else datetime.now()

    def tinh_tien_gui(self, thoi_gian_ra):
        """Phương thức ảo / trừu tượng"""
        pass

class XeMay(PhuongTien):
    def __init__(self, bien_so, thoi_gian_vao=None):
        super().__init__(bien_so, "Motorbike", thoi_gian_vao)

    def tinh_tien_gui(self, thoi_gian_ra):
        """ĐA HÌNH: Tính giá cố định theo lượt theo yêu cầu file Word"""
        return 5000.0  # Giá cố định 5,000 VND / lượt gửi xe máy

class ViTriDo:
    def __init__(self, ma_vi_tri, hàng, cột, trang_thai="Empty", xe_dang_do=None):
        self.slot_id = ma_vi_tri
        self.row = hàng
        self.col = cột
        self.status = trang_thai          # "Empty" hoặc "Occupied"
        self.current_vehicle = xe_dang_do  # Đối tượng XeMay nếu có