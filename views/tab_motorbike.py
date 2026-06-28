import tkinter as tk
from tkinter import messagebox, ttk
from controllers.motorbike_ctrl import MotorbikeController

class MotorbikeTabBuilder:
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.ctrl = MotorbikeController()
        
        # Chia giao diện làm 2 phần: Trên (Điều khiển + Sơ đồ), Dưới (Bảng thông tin xe đang đỗ)
        self.top_layout = tk.Frame(self.frame, padx=5, pady=5)
        self.top_layout.pack(fill=tk.BOTH, expand=True)
        
        self.bottom_layout = tk.LabelFrame(self.frame, text=" BẢNG THEO DÕI XE MÁY ĐANG ĐỖ (LIVE DATA OBSERVER) ", font=("Arial", 10, "bold"), padx=5, pady=5)
        self.bottom_layout.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.build_top_controls_and_map()
        self.build_bottom_table()
        self.refresh_ui()

    def build_top_controls_and_map(self):
        # Bên trái: Khung Check-in nhanh
        checkin_box = tk.LabelFrame(self.top_layout, text=" CỔNG VÀO (CHECK-IN) ", font=("Arial", 10, "bold"), padx=10, pady=10)
        checkin_box.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        tk.Label(checkin_box, text="Nhập Biển Số Xe Máy:", font=("Arial", 10)).pack(anchor=tk.W, pady=5)
        self.ent_plate = tk.Entry(checkin_box, font=("Arial", 12), width=18)
        self.ent_plate.pack(pady=5)
        
        btn_in = tk.Button(checkin_box, text="XÁC NHẬN VÀO", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), height=2, width=16, command=self.trigger_check_in)
        btn_in.pack(pady=10)
        
        # Bên phải: Lưới bản đồ bãi đỗ xe máy
        self.map_box = tk.LabelFrame(self.top_layout, text=" SƠ ĐỒ BÃI ĐỖ XE MÁY KHU A (Click ô đỗ để Check-out) ", font=("Arial", 10, "bold"), padx=10, pady=10)
        self.map_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.grid_frame = tk.Frame(self.map_box)
        self.grid_frame.pack(expand=True)

    def build_bottom_table(self):
        """Bảng chứa thông tin các xe đang đỗ để dễ quan sát khi tìm kiếm/sắp xếp"""
        columns = ("slot_id", "plate", "time_in")
        self.tree = ttk.Treeview(self.bottom_layout, columns=columns, show="headings", height=6)
        
        self.tree.heading("slot_id", text="Mã Vị Trí Đỗ")
        self.tree.heading("plate", text="Biển Số Xe")
        self.tree.heading("time_in", text="Thời Gian Vào Bãi")
        
        self.tree.column("slot_id", width=120, anchor=tk.CENTER)
        self.tree.column("plate", width=180, anchor=tk.CENTER)
        self.tree.column("time_in", width=250, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)

    def trigger_check_in(self):
        plate = self.ent_plate.get().strip().upper()
        if not plate:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập biển số xe máy trước khi Check-in!")
            return
        try:
            allocated_slot = self.ctrl.process_check_in(plate)
            messagebox.showinfo("Thành công", f"Xe máy [{plate}] Check-in thành công!\nVị trí cấp phát tự động: {allocated_slot}")
            self.ent_plate.delete(0, tk.END)
            self.refresh_ui()
        except Exception as ex:
            messagebox.showerror("Lỗi", str(ex))

    def on_slot_click(self, slot):
        """Hành động khi bấm trực tiếp vào ô đỗ: Thủ công (Xanh) hoặc Chi tiết/Check-out (Đỏ)"""
        
        # 1. CHẾ ĐỘ THỦ CÔNG: Bấm vào ô TRỐNG (Màu xanh)
        if slot.status == "Empty" or slot.status == "none":
            # Lấy biển số từ ô nhập liệu xem nhân viên có gõ chữ nào chưa
            manual_plate = self.ent_plate.get().strip().upper()
            
            if manual_plate != "":
                # Nếu có gõ biển số, kích hoạt ngay chế độ xếp chỗ thủ công
                confirm = messagebox.askyesno(
                    "Xếp chỗ thủ công", 
                    f"Bạn có muốn xếp xe máy [{manual_plate}] vào vị trí [{slot.slot_id}] theo cách thủ công không?"
                )
                if confirm:
                    try:
                        # Gọi hàm xử lý thủ công trong Controller
                        self.ctrl.process_manual_check_in(manual_plate, slot.slot_id)
                        messagebox.showinfo("Thành công", f"Đã xếp xe [{manual_plate}] vào vị trí [{slot.slot_id}] thành công!")
                        
                        self.ent_plate.delete(0, tk.END) # Xóa chữ ở ô nhập liệu đi
                        self.refresh_ui()                # Cập nhật lại giao diện lưới và bảng
                    except Exception as ex:
                        messagebox.showerror("Lỗi", str(ex))
            else:
                # Nếu ô nhập liệu đang trống trơn, chỉ hiển thị thông báo trạng thái ô đỗ
                messagebox.showinfo("Thông tin ô đỗ", f"Vị trí {slot.slot_id} hiện đang trống.\n\n👉 ĐỂ XẾP XE THỦ CÔNG:\nBước 1: Nhập biển số xe ở khung bên trái trước.\nBước 2: Click chuột vào ô này để xếp chỗ!")
            return
            
        # 2. CHẾ ĐỘ CHECK-OUT: Bấm vào ô CÓ XE (Màu đỏ)
        detail_win = tk.Toplevel(self.frame)
        detail_win.title(f"Chi tiết vị trí: {slot.slot_id}")
        detail_win.geometry("350x220")
        detail_win.grab_set() # Khóa màn hình chính
        
        msg_info = f"📍 MÃ VỊ TRÍ: {slot.slot_id}\n\n" \
                   f"📝 BIỂN SỐ: {slot.current_vehicle.license_plate}\n\n" \
                   f"⏰ THỜI GIAN VÀO:\n{slot.current_vehicle.check_in_time.strftime('%Y-%m-%d %H:%M:%S')}"
                   
        tk.Label(detail_win, text=msg_info, font=("Arial", 10), justify=tk.LEFT, padx=20, pady=20).pack(anchor=tk.W)
        
        def run_checkout_action():
            detail_win.destroy()
            ans_print = messagebox.askyesno("In Biên Lai", "Bạn có muốn thực hiện in biên lai hóa đơn tính tiền không?")
            try:
                receipt = self.ctrl.process_check_out(slot.slot_id, must_print_receipt=ans_print)
                if ans_print:
                    messagebox.showinfo("HỆ THỐNG IN ẤN", receipt)
                else:
                    messagebox.showinfo("Thành công", "Xe máy ra bãi thành công! (Không in hóa đơn)")
                self.refresh_ui()
            except Exception as ex:
                messagebox.showerror("Lỗi", str(ex))

        btn_checkout = tk.Button(detail_win, text="CHECK-OUT (CHO XE RA)", bg="#F44336", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5, command=run_checkout_action)
        btn_checkout.pack(pady=10)
        """Hành động khi bấm trực tiếp vào ô đỗ: Hiện thông tin chi tiết và lựa chọn check-out"""
        if slot.status == "Empty":
            messagebox.showinfo("Thông tin ô đỗ", f"Vị trí {slot.slot_id} hiện đang trống.\nBạn có thể cho xe máy đỗ vào đây.")
            return
            
        # Nếu ô đỗ có xe, mở cửa sổ Pop-up chi tiết
        detail_win = tk.Toplevel(self.frame)
        detail_win.title(f"Chi tiết vị trí: {slot.slot_id}")
        detail_win.geometry("350x220")
        detail_win.grab_set() # Khóa màn hình chính khi đang xem chi tiết
        
        msg_info = f"📍 MÃ VỊ TRÍ: {slot.slot_id}\n\n" \
                   f"📝 BIỂN SỐ: {slot.current_vehicle.license_plate}\n\n" \
                   f"⏰ THỜI GIAN VÀO:\n{slot.current_vehicle.check_in_time.strftime('%Y-%m-%d %H:%M:%S')}"
                   
        tk.Label(detail_win, text=msg_info, font=("Arial", 10), justify=tk.LEFT, padx=20, pady=20).pack(anchor=tk.W)
        
        def run_checkout_action():
            detail_win.destroy()
            # Hỏi người dùng xem có muốn in hóa đơn không trước khi giải phóng vị trí
            ans_print = messagebox.askyesno("In Biên Lai", "Bạn có muốn thực hiện in biên lai hóa đơn tính tiền không?")
            try:
                receipt = self.ctrl.process_check_out(slot.slot_id, must_print_receipt=ans_print)
                if ans_print:
                    # Giả lập in hóa đơn bằng Pop-up hệ thống
                    messagebox.showinfo("HỆ THỐNG IN ẤN", receipt)
                else:
                    messagebox.showinfo("Thành công", "Xe máy ra bãi thành công! (Không in hóa đơn)")
                self.refresh_ui()
            except Exception as ex:
                messagebox.showerror("Lỗi", str(ex))

        btn_checkout = tk.Button(detail_win, text="CHECK-OUT (CHO XE RA)", bg="#F44336", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5, command=run_checkout_action)
        btn_checkout.pack(pady=10)

    def refresh_ui(self):
        # 1. Vẽ lại lưới bản đồ ô đỗ
        for w in self.grid_frame.winfo_children():
            w.destroy()
            
        grid = self.ctrl.get_all_slots()
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                slot = grid[r][c]
                bg_color = "#F44336" if slot.status == "Occupied" else "#4CAF50" # Đỏ nếu có xe, Xanh nếu trống
                
                btn = tk.Button(self.grid_frame, text=slot.slot_id, bg=bg_color, fg="white", font=("Arial", 9, "bold"), width=12, height=3, command=lambda s=slot: self.on_slot_click(s))
                btn.grid(row=r, column=c, padx=5, pady=5)
                
                if slot.status == "Occupied" and slot.current_vehicle:
                    # Gắn hiệu ứng di chuột hiện biển số (Tooltip) đúng yêu cầu file Word
                    self.bind_tooltip(btn, f"Biển số: {slot.current_vehicle.license_plate}")

        # 2. Cập nhật lại Bảng theo dõi dữ liệu phía dưới
        self.tree.delete(*self.tree.get_children())
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                slot = grid[r][c]
                if slot.status == "Occupied" and slot.current_vehicle:
                    self.tree.insert("", tk.END, values=(slot.slot_id, slot.current_vehicle.license_plate, slot.current_vehicle.check_in_time.strftime('%Y-%m-%d %H:%M:%S')))

    def bind_tooltip(self, widget, text):
        def show(event):
            self.tip = tk.Toplevel(self.frame)
            self.tip.wm_overrideredirect(True)
            self.tip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            tk.Label(self.tip, text=text, background="#FFFFE0", relief="solid", borderwidth=1, padx=5, pady=5).pack()
        def hide(event):
            if hasattr(self, 'tip'): self.tip.destroy()
        widget.bind("<Enter>", show)
        widget.bind("<Leave>", hide)

    