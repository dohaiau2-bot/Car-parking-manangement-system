import tkinter as tk
from tkinter import messagebox, ttk
from controllers.car_ctrl import CarController

class CarTabBuilder:
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.ctrl = CarController()
        
        # Bố cục giao diện cố định - CHỈ KHỞI TẠO ĐÚNG 1 LẦN DUY NHẤT
        self.top_layout = tk.Frame(self.frame, padx=5, pady=5)
        self.top_layout.pack(fill=tk.BOTH, expand=True)
        
        self.bottom_layout = tk.LabelFrame(self.frame, text=" HÀNG ĐỢI XE ĐANG CHỜ Ở CỔNG VÀO (WAITING QUEUE) ", font=("Arial", 10, "bold"), padx=5, pady=5)
        self.bottom_layout.pack(fill=tk.X, expand=False, padx=10, pady=5)
        
        self.stat_layout = tk.LabelFrame(self.frame, text=" 📊 THỐNG KÊ REAL-TIME & THUẬT TOÁN HẬU KIỂM ", font=("Arial", 10, "bold"), fg="blue", padx=5, pady=5)
        self.stat_layout.pack(fill=tk.X, expand=False, padx=10, pady=5)
        
        # Biến cờ kiểm tra để ngăn chặn mọi hành vi dựng lại nút bấm
        self.widgets_built = False
        
        self.build_top_controls_and_map()
        self.build_bottom_queue_view()
        self.build_statistics_view()
        self.refresh_ui()

    def build_top_controls_and_map(self):
        # BẢNG ĐIỀU KHIỂN CHỨC NĂNG LỘ THIÊN
        checkin_box = tk.LabelFrame(self.top_layout, text=" BẢNG ĐIỀU KHIỂN KHU B ", font=("Arial", 10, "bold"), padx=10, pady=10)
        checkin_box.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        tk.Label(checkin_box, text="Nhập/Chọn Biển Số:", font=("Arial", 10)).pack(anchor=tk.W, pady=2)
        self.ent_plate = tk.Entry(checkin_box, font=("Arial", 12), width=18)
        self.ent_plate.pack(pady=5)
        
        tk.Label(checkin_box, text="Nhập/Chọn Vị Trí (Ví dụ: B-R1C1):", font=("Arial", 9)).pack(anchor=tk.W, pady=2)
        self.ent_slot = tk.Entry(checkin_box, font=("Arial", 11), width=18)
        self.ent_slot.pack(pady=5)
        
        # --- BỘ NÚT BẤM CHỨC NĂNG CỐ ĐỊNH ---
        btn_in = tk.Button(checkin_box, text="➕ CHECK-IN (TỰ ĐỘNG)", bg="#2196F3", fg="white", font=("Arial", 9, "bold"), width=20, command=self.trigger_check_in)
        btn_in.pack(pady=4)

        btn_edit = tk.Button(checkin_box, text="✏️ SỬA BIỂN SỐ XE", bg="#FF9800", fg="white", font=("Arial", 9, "bold"), width=20, command=self.trigger_manual_edit)
        btn_edit.pack(pady=4)
        
        btn_delete = tk.Button(checkin_box, text="🗑️ XÓA KHẨN CẤP (RESET)", bg="#E53935", fg="white", font=("Arial", 9, "bold"), width=20, command=self.trigger_manual_delete)
        btn_delete.pack(pady=4)

        info_lbl = tk.Label(checkin_box, text="ℹ️ Mẹo thao tác nhanh:\nClick vào ô ĐỎ trên sơ đồ\nsẽ tự động điền Biển số\nvà Vị trí vào ô nhập liệu\nđể Sửa hoặc Xóa nhanh!", font=("Arial", 8, "italic"), justify=tk.LEFT, fg="#555")
        info_lbl.pack(pady=10, anchor=tk.W)
        
        # Sơ đồ ma trận bãi xe
        self.map_box = tk.LabelFrame(self.top_layout, text=" SƠ ĐỒ BÃI ĐỖ Ô TÔ KHU B (Tính giá lũy tiến) ", font=("Arial", 10, "bold"), padx=10, pady=10)
        self.map_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.grid_frame = tk.Frame(self.map_box)
        self.grid_frame.pack(expand=True)

    def build_bottom_queue_view(self):
        self.lbl_queue_status = tk.Label(self.bottom_layout, text="Trạng thái hàng đợi: Trống", font=("Arial", 10, "bold"), fg="green")
        self.lbl_queue_status.pack(anchor=tk.W, pady=2)
        self.list_queue_display = tk.Listbox(self.bottom_layout, font=("Arial", 10, "bold"), height=2, bg="#ECEFF1", fg="#37474F")
        self.list_queue_display.pack(fill=tk.X, expand=True, pady=2)

    def build_statistics_view(self):
        # Chống nhân bản thanh điều khiển dưới
        if self.widgets_built:
            return
            
        self.lbl_stats = tk.Label(self.stat_layout, text="Đang tải dữ liệu thống kê...", font=("Arial", 10, "bold"), fg="#E65100")
        self.lbl_stats.pack(side=tk.LEFT, padx=10, pady=5)
        
        # --- NÚT BẤM LỊCH SỬ XUẤT BÃI (ĐÃ FIX CHẶT LỖI GỌI TRỰC TIẾP) ---
        btn_history = tk.Button(self.stat_layout, text="📋 LỊCH SỬ XUẤT BÃI", bg="#00796B", fg="white", font=("Arial", 9, "bold"), command=self.open_history_log_window)
        btn_history.pack(side=tk.RIGHT, padx=5, pady=5)
        
        btn_sort = tk.Button(self.stat_layout, text="⚡ QUICK SORT DOANH THU", bg="#673AB7", fg="white", font=("Arial", 9, "bold"), command=self.open_car_quick_sort_window)
        btn_sort.pack(side=tk.RIGHT, padx=5, pady=5)
        
        btn_csv = tk.Button(self.stat_layout, text="📊 XUẤT CSV", bg="#009688", fg="white", font=("Arial", 9, "bold"), command=lambda: self.trigger_export("csv"))
        btn_csv.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.widgets_built = True

    def open_history_log_window(self):
        """Mở cửa sổ hiển thị lịch sử xe Ô TÔ (ĐÃ SỬA TRIỆT ĐỂ LỖI NHÂN BẢN)"""
        history_data = self.ctrl.get_car_checkout_history()
        
        if not history_data:
            messagebox.showinfo("Thông báo", "Hiện tại hệ thống chưa có lịch sử hóa đơn check-out nào của Ô tô!")
            return
            
        # Ép buộc gắn vào root chính, cô lập hoàn toàn với tab
        root_win = self.frame.winfo_toplevel()
        history_win = tk.Toplevel(root_win)
        history_win.title("LỊCH SỬ XUẤT BÃI Ô TÔ (CAR CHECK-OUT LOGS)")
        history_win.geometry("850x500")
        
        # Khóa tương tác bên ngoài để chống bấm liên tiếp tạo nhiều cửa sổ
        history_win.grab_set()
        
        top_bar = tk.Frame(history_win)
        top_bar.pack(fill=tk.X, padx=10, pady=5)

        lbl_title = tk.Label(top_bar, text="📋 LỊCH SỬ XE Ô TÔ RA VÀO HỆ THỐNG (KHU B)", font=("Arial", 12, "bold"), fg="#004D40")
        lbl_title.pack(side=tk.LEFT, pady=10)
        
        def confirm_and_clear():
            if messagebox.askyesno("Xác nhận xóa sạch", "⚠️ Bạn có chắc chắn muốn XÓA TOÀN BỘ lịch sử xuất bãi của Ô tô?", parent=history_win):
                try:
                    self.ctrl.clear_car_checkout_history()
                    messagebox.showinfo("Thành công", "Đã xóa sạch lịch sử ô tô!", parent=history_win)
                    history_win.destroy()
                    self.refresh_ui() 
                except Exception as ex: 
                    messagebox.showerror("Lỗi", str(ex), parent=history_win)

        btn_clear = tk.Button(top_bar, text="🗑️ XÓA TOÀN BỘ LỊCH SỬ Ô TÔ", bg="#D32F2F", fg="white", font=("Arial", 9, "bold"), padx=10, command=confirm_and_clear)
        btn_clear.pack(side=tk.RIGHT, pady=10)
        
        columns = ("id", "plate", "type", "slot", "in", "out", "fee")
        tree_hist = ttk.Treeview(history_win, columns=columns, show="headings")
        
        tree_hist.heading("id", text="STT")
        tree_hist.heading("plate", text="Biển Số Xe")
        tree_hist.heading("type", text="Loại Xe")
        tree_hist.heading("slot", text="Vị Trí Đỗ")
        tree_hist.heading("in", text="Thời Gian Vào")
        tree_hist.heading("out", text="Thời Gian Ra")
        tree_hist.heading("fee", text="Tiền Phí (VND)")
        
        tree_hist.column("id", width=50, anchor=tk.CENTER)
        tree_hist.column("plate", width=110, anchor=tk.CENTER)
        tree_hist.column("type", width=90, anchor=tk.CENTER)
        tree_hist.column("slot", width=90, anchor=tk.CENTER)
        tree_hist.column("in", width=150, anchor=tk.CENTER)
        tree_hist.column("out", width=150, anchor=tk.CENTER)
        tree_hist.column("fee", width=110, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(history_win, orient=tk.VERTICAL, command=tree_hist.yview)
        tree_hist.configure(yscroll=scrollbar.set)
        
        tree_hist.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10,0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0,10), pady=10)
        
        for idx, row in enumerate(history_data, start=1):
            tree_hist.insert("", tk.END, values=(idx, row[1], "🚗 Ô tô", row[3], row[4], row[5], f"{row[6]:,.0f}"))

    def trigger_check_in(self):
        plate = self.ent_plate.get().strip().upper()
        if not plate:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập biển số ô tô trước!")
            return
        try:
            allocated_slot = self.ctrl.process_check_in(plate)
            messagebox.showinfo("Thành công", f"Xe ô tô [{plate}] vào thành công!\nVị trí tối ưu: {allocated_slot}")
            self.clear_entries()
            self.refresh_ui()
        except Exception as ex:
            messagebox.showwarning("Thông báo bãi xe", str(ex))
            self.clear_entries()
            self.refresh_ui()

    def trigger_manual_edit(self):
        slot_id = self.ent_slot.get().strip().upper()
        new_plate = self.ent_plate.get().strip().upper()
        if not slot_id or not new_plate:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn 1 ô đỗ có xe và nhập biển số mới vào khung!")
            return
        try:
            self.ctrl.update_car_plate(slot_id, new_plate)
            messagebox.showinfo("Thành công", f"Đã sửa biển số tại vị trí {slot_id} thành [{new_plate}]")
            self.clear_entries()
            self.refresh_ui()
        except Exception as ex: messagebox.showerror("Lỗi", str(ex))

    def trigger_manual_delete(self):
        slot_id = self.ent_slot.get().strip().upper()
        if not slot_id:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập hoặc click chọn vị trí cần xóa giải phóng!")
            return
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn XÓA KHẨN CẤP xe tại vị trí {slot_id} mà không tính tiền?"):
            try:
                self.ctrl.force_delete_slot(slot_id)
                messagebox.showinfo("Thành công", f"Đã giải phóng hoàn toàn vị trí {slot_id}")
                self.clear_entries()
                self.refresh_ui()
            except Exception as ex: messagebox.showerror("Lỗi", str(ex))

    def on_slot_click(self, slot):
        self.ent_slot.delete(0, tk.END)
        self.ent_slot.insert(0, slot.slot_id)
        
        if slot.status == "Occupied":
            self.ent_plate.delete(0, tk.END)
            self.ent_plate.insert(0, slot.current_vehicle.license_plate)
            
            if messagebox.askyesno("Check-out", f"Vị trí {slot.slot_id} đang có xe đỗ.\nBạn có muốn thực hiện CHECK-OUT tính tiền lũy tiến không?"):
                try:
                    receipt = self.ctrl.process_check_out(slot.slot_id, must_print_receipt=True)
                    messagebox.showinfo("BIÊN LAI XUẤT BÃI", receipt)
                    self.clear_entries()
                    self.refresh_ui()
                except Exception as ex: messagebox.showerror("Lỗi", str(ex))

    def open_car_quick_sort_window(self):
        conn = self.ctrl.ParkingDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT license_plate, slot_id, check_in_time, check_out_time, fee FROM parking_history WHERE vehicle_type = 'Car'")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            messagebox.showinfo("Thông báo", "Chưa có dữ liệu hóa đơn Ô tô nào để chạy Quick Sort!")
            return

        data_history = [{"plate": r[0], "slot_id": r[1], "time_in": r[2], "time_out": r[3], "fee": r[4]} for r in rows]
        
        from controllers.motorbike_ctrl import MotorbikeController
        m_ctrl = MotorbikeController()
        m_ctrl.quick_sort_history_by_fee(data_history, 0, len(data_history) - 1)

        sort_win = tk.Toplevel(self.frame.winfo_toplevel())
        sort_win.title("THỐNG KÊ DOANH THU Ô TÔ CAO NHẤT (QUICK SORT)")
        sort_win.geometry("700x400")
        sort_win.grab_set()

        lbl = tk.Label(sort_win, text="📊 DANH SÁCH DOANH THU ĐÃ ĐƯỢC SẮP XẾP GIẢM DẦN BẰNG QUICK SORT", font=("Arial", 10, "bold"), fg="purple", pady=10)
        lbl.pack()

        columns = ("id", "plate", "slot", "out", "fee")
        tree = ttk.Treeview(sort_win, columns=columns, show="headings")
        tree.heading("id", text="STT")
        tree.heading("plate", text="Biển Số Ô Tô")
        tree.heading("slot", text="Vị Trí Đỗ")
        tree.heading("out", text="Thời Gian Ra")
        tree.heading("fee", text="Tiền Thu (VND)")
        
        tree.column("id", width=50, anchor=tk.CENTER)
        tree.column("fee", width=120, anchor=tk.CENTER)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for idx, item in enumerate(data_history, start=1):
            tree.insert("", tk.END, values=(idx, item["plate"], item["slot_id"], item["time_out"], f"{item['fee']:,.0f}"))

    def trigger_export(self, file_type):
        try:
            path = self.ctrl.export_history_to_file(file_type)
            messagebox.showinfo("Thành công", f"Đã xuất file báo cáo tại:\n{path}")
        except Exception as ex: messagebox.showerror("Lỗi", str(ex))

    def clear_entries(self):
        self.ent_plate.delete(0, tk.END)
        self.ent_slot.delete(0, tk.END)

    def refresh_ui(self):
        """Hàm refresh CHỈ vẽ lại lưới ô đỗ và cập nhật chuỗi Text chữ, không sinh lại Button"""
        for w in self.grid_frame.winfo_children(): 
            w.destroy()
            
        grid = self.ctrl.get_all_slots()
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                slot = grid[r][c]
                bg_color = "#F44336" if slot.status == "Occupied" else "#4CAF50"
                btn = tk.Button(self.grid_frame, text=slot.slot_id, bg=bg_color, fg="white", font=("Arial", 10, "bold"), width=14, height=4, command=lambda s=slot: self.on_slot_click(s))
                btn.grid(row=r, column=c, padx=8, pady=8)

        waiting_cars = self.ctrl.get_waiting_cars()
        self.list_queue_display.delete(0, tk.END)
        if len(waiting_cars) == 0:
            self.lbl_queue_status.config(text="Trạng thái hàng đợi: Trống (Cổng vào thông suốt)", fg="green")
            self.list_queue_display.insert(tk.END, " Không có xe nào đang xếp hàng chờ ngoài cổng.")
        else:
            self.lbl_queue_status.config(text=f"🚨 CẢNH BÁO: Đang có {len(waiting_cars)} xe ô tô xếp hàng chờ ngoài cổng!", fg="red")
            for idx, plate in enumerate(waiting_cars, start=1):
                self.list_queue_display.insert(tk.END, f"  [Vị trí {idx}]: Xe Ô tô biển số ----> {plate}")

        stats = self.ctrl.get_live_statistics()
        stat_text = f"🚘 Tổng ô tô đang gửi: {stats['occupied']} xe   |   " \
                    f"📈 Tỉ lệ lấp đầy Khu B: {stats['fill_rate']:.1f}%   |   " \
                    f"💰 Tổng doanh thu toàn bãi hôm nay: {stats['revenue']:,.0f} VND"
        self.lbl_stats.config(text=stat_text)