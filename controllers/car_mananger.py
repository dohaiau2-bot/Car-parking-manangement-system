class CarManager:
    def __init__(self):
        # Danh sách lưu trữ các đối tượng xe đang đỗ trong bãi (Khu B)
        # Để chạy được Binary Search, danh sách này PHẢI luôn được sắp xếp theo biển số xe
        self.active_cars = [] 

    def add_car_to_index(self, new_car):
        """Khi có xe check-in thành công, chèn xe vào vị trí đúng để giữ mảng luôn sắp xếp"""
        self.active_cars.append(new_car)
        # Sắp xếp lại theo biển số xe (Tận dụng TimSort của Python hoặc tự viết hàm chèn)
        self.active_cars.sort(key=lambda x: x.license_plate)

    def remove_car_from_index(self, license_plate):
        """Khi xe check-out, xóa xe ra khỏi danh sách index"""
        car_to_remove = self.binary_search_car(license_plate)
        if car_to_remove:
            self.active_cars.remove(car_to_remove)

    def binary_search_car(self, target_plate):
        """
        THUẬT TOÁN TÌM KIẾM NHỊ PHÂN (BINARY SEARCH) - ĐỘ PHỨC TẠP O(log N)
        Tìm kiếm đối tượng xe trong bãi dựa trên Biển số xe nhập vào.
        """
        low = 0
        high = len(self.active_cars) - 1

        while low <= high:
            mid = (low + high) // 2
            mid_plate = self.active_cars[mid].license_plate

            if mid_plate == target_plate:
                return self.active_cars[mid]  # Tìm thấy xe, trả về đối tượng xe
            elif mid_plate < target_plate:
                low = mid + 1  # Thu hẹp phạm vi sang nửa bên phải
            else:
                high = mid - 1  # Thu hẹp phạm vi sang nửa bên trái

        return None  # Không tìm thấy xe trong bãi