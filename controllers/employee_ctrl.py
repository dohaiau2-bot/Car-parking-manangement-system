# controllers/employee_ctrl.py
from models.employee import EmployeeModel

class EmployeeController:
    def __init__(self):
        self.model = EmployeeModel()

    def register_employee(self, emp_id, fullname, phone, email, position):
        if not emp_id or not fullname:
            return False, "Mã NV và Họ tên không được để trống!"
        
        success = self.model.add_employee(emp_id, fullname, phone, email, position)
        if success:
            return True, "Đăng ký nhân viên thành công!"
        else:
            return False, "Mã nhân viên đã tồn tại!"

    def get_employee_list(self):
        return self.model.get_all_employees()

    def get_schedule_grid(self):
        return self.model.get_schedule_grid()

    def assign_shift(self, day, shift, emp_id):
        if not emp_id:
            return "Vui lòng chọn một nhân viên!"
        
        status = self.model.assign_shift(day, shift, emp_id)
        if status == "ASSIGNED":
            return f"Đã phân công trực tiếp vào ca {shift} - {day}."
        elif status == "QUEUED":
            return f"Ca trực đã đầy! Nhân viên đã được đưa vào Hàng đợi của ca."
        elif status == "DUPLICATE":
            return "Nhân viên này đã có lịch hoặc đang trong hàng chờ ca này!"

    def get_waiting_list(self, day, shift):
        return self.model.get_waiting_list(day, shift)

    def reset_shift(self, day, shift):
        self.model.clear_shift(day, shift)
        return f"Đã giải phóng ca trực. Hàng đợi tự động đôn người tiếp theo!"
    
    def get_employee_info(self, emp_id):
        return self.model.get_employee_info(emp_id)

    def update_employee(self, emp_id, fullname, phone, email, position):
        if not emp_id or not fullname:
            return False, "Mã NV và Họ tên không được để trống!"
        
        success = self.model.update_employee(emp_id, fullname, phone, email, position)
        if success:
            return True, "Cập nhật thông tin nhân viên thành công!"
        else:
            return False, "Không tìm thấy Mã nhân viên trong hệ thống!"

    def delete_employee(self, emp_id):
        if not emp_id:
            return False, "Vui lòng nhập Mã NV cần xóa!"
        
        success = self.model.delete_employee(emp_id)
        if success:
            return True, "Đã xóa nhân viên và toàn bộ lịch trực liên quan!"
        else:
            return False, "Không tìm thấy Mã nhân viên trong hệ thống!"