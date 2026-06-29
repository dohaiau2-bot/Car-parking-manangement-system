# views/tab_employee.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.employee_ctrl import EmployeeController

class EmployeeTabBuilder:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.ctrl = EmployeeController()
        
        self.days = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
        self.shifts = ["Sáng", "Chiều"]
        self.cell_buttons = {} # Lưu trữ các widget nút ca trực để cập nhật màu sắc
        
        self.init_ui()
        self.refresh_schedule_view()

    def init_ui(self):
        # Thiết lập bố cục chia đôi màn hình: Trái (Đăng ký & Điều khiển) - Phải (Sơ đồ lịch trực)
        left_frame = tk.Frame(self.parent, width=350, padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        right_frame = tk.LabelFrame(self.parent, text=" 📅 SƠ ĐỒ PHÂN CA TRỰC NHÂN VIÊN ", font=("Arial", 11, "bold"), padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ----------------- PHẦN 1: ĐĂNG KÝ NHÂN VIÊN -----------------
        reg_frame = tk.LabelFrame(left_frame, text=" 📝 ĐĂNG KÝ NHÂN VIÊN MỚI ", font=("Arial", 10, "bold"), padx=10, pady=10)
        reg_frame.pack(fill=tk.X, pady=5)

        tk.Label(reg_frame, text="Mã nhân viên:").grid(row=0, column=0, sticky='w', pady=2)
        self.ent_id = tk.Entry(reg_frame, width=25)
        self.ent_id.grid(row=0, column=1, pady=2)

        tk.Label(reg_frame, text="Họ và Tên:").grid(row=1, column=0, sticky='w', pady=2)
        self.ent_name = tk.Entry(reg_frame, width=25)
        self.ent_name.grid(row=1, column=1, pady=2)

        tk.Label(reg_frame, text="Số điện thoại:").grid(row=2, column=0, sticky='w', pady=2)
        self.ent_phone = tk.Entry(reg_frame, width=25)
        self.ent_phone.grid(row=2, column=1, pady=2)

        tk.Label(reg_frame, text="Email:").grid(row=3, column=0, sticky='w', pady=2)
        self.ent_email = tk.Entry(reg_frame, width=25)
        self.ent_email.grid(row=3, column=1, pady=2)

        tk.Label(reg_frame, text="Chức vụ:").grid(row=4, column=0, sticky='w', pady=2)
        self.ent_pos = tk.Entry(reg_frame, width=25)
        self.ent_pos.grid(row=4, column=1, pady=2)

        action_frame = tk.Frame(reg_frame)
        action_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky='we')

        btn_reg = tk.Button(action_frame, text="➕ Thêm", bg="#2ECC71", fg="white", font=("Arial", 10, "bold"), command=self.handle_register)
        btn_reg.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        btn_update = tk.Button(action_frame, text="🔄 Sửa", bg="#F39C12", fg="white", font=("Arial", 10, "bold"), command=self.handle_update)
        btn_update.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        btn_del = tk.Button(action_frame, text="🗑️ Xóa", bg="#E74C3C", fg="white", font=("Arial", 10, "bold"), command=self.handle_delete)
        btn_del.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # ----------------- PHẦN 2: PHÂN CÔNG CA TRỰC -----------------
        assign_frame = tk.LabelFrame(left_frame, text=" 🛠️ CÔNG CỤ ĐIỀU HÀNH CA ", font=("Arial", 10, "bold"), padx=10, pady=10)
        assign_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        tk.Label(assign_frame, text="1. Chọn Nhân Viên:").pack(anchor='w', pady=2)
        self.cbo_employees = ttk.Combobox(assign_frame, state="readonly", width=28)
        self.cbo_employees.pack(fill=tk.X, pady=2)
        self.cbo_employees.bind("<<ComboboxSelected>>", self.on_employee_selected)
        self.refresh_employee_combobox()

        tk.Label(assign_frame, text="2. Thao tác Ca (Chọn ca trên Sơ đồ trước):").pack(anchor='w', pady=10)
        
        self.lbl_selected_slot = tk.Label(assign_frame, text="Đang chọn: Chưa chọn ca", fg="blue", font=("Arial", 10, "italic"))
        self.lbl_selected_slot.pack(anchor='w', pady=2)

        self.btn_submit_shift = tk.Button(assign_frame, text="🚀 Phân Vào Ca / Xếp Hàng Đợi", bg="#1E88E5", fg="white", state=tk.DISABLED, command=self.handle_assign)
        self.btn_submit_shift.pack(fill=tk.X, pady=4)

        self.btn_clear_shift = tk.Button(assign_frame, text="♻️ Giải Phóng Ca (Đôn hàng đợi)", bg="#E67E22", fg="white", state=tk.DISABLED, command=self.handle_clear)
        self.btn_clear_shift.pack(fill=tk.X, pady=4)
        
        # Danh sách hiển thị hàng chờ của ca đang chọn
        tk.Label(assign_frame, text="👥 Hàng đợi (Queue) của ca đang chọn:").pack(anchor='w', pady=5)
        self.lst_queue = tk.Listbox(assign_frame, height=5, bg="#F8F9F9")
        self.lst_queue.pack(fill=tk.BOTH, expand=True)

        # ----------------- PHẦN 3: SƠ ĐỒ LỊCH TRỰC TRỰC QUAN (BÊN PHẢI) -----------------
        # Tạo lưới Grid giống bãi đỗ xe[cite: 10]
        for col_idx, day in enumerate(self.days):
            lbl_day = tk.Label(right_frame, text=day, font=("Arial", 10, "bold"), width=12, borderwidth=1, relief="solid", bg="#EAEDED")
            lbl_day.grid(row=0, column=col_idx+1, padx=2, pady=5)

        for row_idx, shift in enumerate(self.shifts):
            lbl_shift = tk.Label(right_frame, text=f"Ca {shift}", font=("Arial", 10, "bold"), height=4, borderwidth=1, relief="solid", bg="#EAEDED", width=10)
            lbl_shift.grid(row=row_idx+1, column=0, padx=5, pady=2)

        # Tạo ma trận nút đại diện cho các ca trực
        self.selected_day = None
        self.selected_shift = None

        for c_idx, day in enumerate(self.days):
            for r_idx, shift in enumerate(self.shifts):
                btn = tk.Button(
                    right_frame, 
                    text="Trống", 
                    bg="#2ECC71", # Mặc định màu xanh là trống[cite: 10]
                    fg="white", 
                    font=("Arial", 9),
                    relief="groove",
                    command=lambda d=day, s=shift: self.on_slot_click(d, s)
                )
                btn.grid(row=r_idx+1, column=c_idx+1, sticky="nsew", padx=3, pady=3)
                self.cell_buttons[(day, shift)] = btn

        # Cấu hình co giãn các ô trong Grid giao diện bãi đỗ xe
        for i in range(len(self.days) + 1):
            right_frame.grid_columnconfigure(i, weight=1)
        for j in range(len(self.shifts) + 1):
            right_frame.grid_rowconfigure(j, weight=1)

    def refresh_employee_combobox(self):
        employees = self.ctrl.get_employee_list()
        # Định dạng chuỗi hiển thị: "MaNV - TenNV"
        self.employee_map = {f"{emp[0]} - {emp[1]}": emp[0] for emp in employees}
        self.cbo_employees['values'] = list(self.employee_map.keys())

    def refresh_schedule_view(self):
        """Quét DB để cập nhật trạng thái màu sắc Đỏ/Xanh của sơ đồ trực quan[cite: 10]"""
        grid_data = self.ctrl.get_schedule_grid()
        
        for (day, shift), btn in self.cell_buttons.items():
            if (day, shift) in grid_data:
                info = grid_data[(day, shift)]
                btn.config(bg="#E74C3C", text=f"🔒 {info['name']}") # Đầy lịch đổi sang màu đỏ[cite: 10]
            else:
                btn.config(bg="#2ECC71", text="🟢 Trống") # Ca trống giữ màu xanh[cite: 10]
                
        # Cập nhật danh sách hàng đợi trực quan nếu đang chọn một ca cụ thể
        if self.selected_day and self.selected_shift:
            self.update_queue_listbox(self.selected_day, self.selected_shift)

    def update_queue_listbox(self, day, shift):
        self.lst_queue.delete(0, tk.END)
        q_list = self.ctrl.get_waiting_list(day, shift)
        for idx, name in enumerate(q_list):
            self.lst_queue.insert(tk.END, f"Thứ {idx+1}: {name}")

    def on_slot_click(self, day, shift):
        self.selected_day = day
        self.selected_shift = shift
        self.lbl_selected_slot.config(text=f"Đang chọn: Ca {shift} ({day})", fg="#D35400")
        
        # Kích hoạt các nút hành động điều phối
        self.btn_submit_shift.config(state=tk.NORMAL)
        self.btn_clear_shift.config(state=tk.NORMAL)
        
        self.update_queue_listbox(day, shift)

    def handle_register(self):
        emp_id = self.ent_id.get().strip()
        name = self.ent_name.get().strip()
        phone = self.ent_phone.get().strip()
        email = self.ent_email.get().strip()
        pos = self.ent_pos.get().strip()

        success, msg = self.ctrl.register_employee(emp_id, name, phone, email, pos)
        if success:
            messagebox.showinfo("Thành công", msg)
            self.refresh_employee_combobox()
            # Xóa form đăng ký sau khi tạo xong
            self.ent_id.delete(0, tk.END)
            self.ent_name.delete(0, tk.END)
            self.ent_phone.delete(0, tk.END)
            self.ent_email.delete(0, tk.END)
            self.ent_pos.delete(0, tk.END)
        else:
            messagebox.showerror("Lỗi", msg)

    def clear_form(self):
        """Hàm tiện ích để dọn dẹp form"""
        self.ent_id.config(state=tk.NORMAL) # Mở khóa nếu đang bị khóa
        self.ent_id.delete(0, tk.END)
        self.ent_name.delete(0, tk.END)
        self.ent_phone.delete(0, tk.END)
        self.ent_email.delete(0, tk.END)
        self.ent_pos.delete(0, tk.END)

    def on_employee_selected(self, event):
        """Tự động đổ dữ liệu lên Form khi chọn nhân viên ở Combobox"""
        selected_emp_text = self.cbo_employees.get()
        if selected_emp_text:
            emp_id = self.employee_map[selected_emp_text]
            info = self.ctrl.get_employee_info(emp_id) # (emp_id, fullname, phone, email, pos)
            
            if info:
                self.clear_form()
                self.ent_id.insert(0, info[0])
                self.ent_id.config(state="readonly") # Khóa mã NV lại không cho sửa khi Update
                
                self.ent_name.insert(0, info[1])
                self.ent_phone.insert(0, info[2] if info[2] else "")
                self.ent_email.insert(0, info[3] if info[3] else "")
                self.ent_pos.insert(0, info[4] if info[4] else "")

    def handle_update(self):
        emp_id = self.ent_id.get().strip()
        name = self.ent_name.get().strip()
        phone = self.ent_phone.get().strip()
        email = self.ent_email.get().strip()
        pos = self.ent_pos.get().strip()

        success, msg = self.ctrl.update_employee(emp_id, name, phone, email, pos)
        if success:
            messagebox.showinfo("Thành công", msg)
            self.refresh_employee_combobox() # Cập nhật lại list combobox (nếu có đổi tên)
            self.refresh_schedule_view() # Tên trên lịch trực cũng sẽ tự nhảy sang tên mới
            self.clear_form()
        else:
            messagebox.showerror("Lỗi", msg)

    def handle_delete(self):
        emp_id = self.ent_id.get().strip()
        if not emp_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hoặc nhập Mã NV cần xóa!")
            return

        confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa nhân viên {emp_id}?\nToàn bộ lịch trực của người này sẽ bị hủy bỏ!")
        if confirm:
            success, msg = self.ctrl.delete_employee(emp_id)
            if success:
                messagebox.showinfo("Thành công", msg)
                self.refresh_employee_combobox()
                self.refresh_schedule_view() # Xóa luôn khỏi sơ đồ lịch
                self.clear_form()
                self.cbo_employees.set('') # Xóa chữ trên combobox
            else:
                messagebox.showerror("Lỗi", msg)

    def handle_assign(self):
        selected_emp_text = self.cbo_employees.get()
        if not selected_emp_text:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên cần phân công ca trực!")
            return
            
        emp_id = self.employee_map[selected_emp_text]
        msg = self.ctrl.assign_shift(self.selected_day, self.selected_shift, emp_id)
        
        messagebox.showinfo("Thông báo điều phối", msg)
        self.refresh_schedule_view()

    def handle_clear(self):
        msg = self.ctrl.reset_shift(self.selected_day, self.selected_shift)
        messagebox.showinfo("Đã cập nhật", msg)
        self.refresh_schedule_view()