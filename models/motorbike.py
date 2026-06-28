from datetime import datetime
from models.transportation import PhuongTien

class XeMay(PhuongTien):
    def __init__(self, bien_so, thoi_gian_vao=None):
        super().__init__(bien_so, "Motorbike", thoi_gian_vao)

    def tinh_tien_gui(self, thoi_gian_ra):
        """
        ĐA HÌNH + XỬ LÝ THỜI GIAN THỰC NÂNG CAO:
        - Giá cơ bản: 5,000 VND cho 1 giờ đầu tiên.
        - Mỗi giờ tiếp theo (hoặc block quá hạn): Cộng thêm 2,000 VND/giờ.
        """
        thoi_gian_do = thoi_gian_ra - self.check_in_time
        tong_so_giay = thoi_gian_do.total_seconds()
        
        # Quy đổi ra giờ (Làm tròn lên: ví dụ đỗ 1 tiếng 5 phút tính là 2 tiếng)
        tong_so_gio = int(tong_so_giay // 3600)
        if tong_so_giay % 3600 > 0:
            tong_so_gio += 1
            
        if tong_so_gio <= 1:
            return 5000.0
        else:
            return float(5000.0 + (tong_so_gio - 1) * 2000)

class ViTriDo:
    def __init__(self, ma_vi_tri, hàng, cột, trang_thai="Empty", xe_dang_do=None):
        self.slot_id = ma_vi_tri
        self.row = hàng
        self.col = cột
        self.status = trang_thai          
        self.current_vehicle = xe_dang_do