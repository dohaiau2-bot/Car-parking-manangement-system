from datetime import datetime
from models.transportation import PhuongTien

class XeOTo(PhuongTien):
    def __init__(self, bien_so, thoi_gian_vao=None):
        super().__init__(bien_so, "Car", thoi_gian_vao)

    def tinh_tien_gui(self, thoi_gian_ra):
        """
        ĐA HÌNH NÂNG CAO: Tính giá tiền lũy tiến theo block giờ thực tế cho Ô tô
        """
        thoi_gian_do = thoi_gian_ra - self.check_in_time
        tong_so_giay = thoi_gian_do.total_seconds()
        
        # Đổi ra số giờ (Làm tròn lên block 1 giờ)
        tong_so_gio = int(tong_so_giay // 3600)
        if tong_so_giay % 3600 > 0 or tong_so_giay == 0:
            tong_so_gio += 1
            
        # Áp dụng công thức lũy tiến phân bậc chống chiếm dụng chỗ
        tong_tien = 0.0
        for hour in range(1, tong_so_gio + 1):
            if hour == 1:
                tong_tien += 20000.0  # Giờ đầu tiên 20k
            elif 2 <= hour <= 5:
                tong_tien += 15000.0  # Từ giờ 2-5 giá 15k/h
            else:
                tong_tien += 25000.0  # Từ giờ thứ 6 trở đi tính phí 25k/h
        return float(tong_tien)

# --- ĐÂY LÀ PHẦN THIẾU BỊ LỖI, BẠN BỔ SUNG ĐOẠN NÀY VÀO ---
class ViTriDo:
    """
    Lớp quản lý vị trí đỗ (Parking Slot) theo đúng yêu cầu OOP của Đồ án
    """
    def __init__(self, ma_vi_tri, row_idx, col_idx, trang_thai="Empty", xe_dang_do=None):
        self.slot_id = ma_vi_tri         # Mã vị trí (Ví dụ: B-R1C1)
        self.row_idx = row_idx           # Chỉ số hàng trong ma trận
        self.col_idx = col_idx           # Chỉ số cột trong ma trận
        self.status = trang_thai         # Trạng thái: 'Empty' hoặc 'Occupied'
        self.current_vehicle = xe_dang_do # Đối tượng xe cụ thể đang đỗ (XeOTo)