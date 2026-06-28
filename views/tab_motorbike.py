import tkinter as tk
from tkinter import messagebox, ttk
from controllers.motorbike_ctrl import MotorbikeController
from datetime import datetime
import csv
import os

class MotorbikeTabBuilder:
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.ctrl = MotorbikeController()
        self.sort_ascending = True
        self._is_report_opening = False # Khởi tạo cờ chặn dupe chống bấm nhanh
        
        self.top_layout = tk.Frame(self.frame, padx=5, pady=5)
        self.top_layout.pack(fill=tk.BOTH, expand=True)
        
        # --- CHỨC NĂNG BỔ SUNG: KHUNG THỐNG KÊ VẬN HÀNH BÃI XE ---
        self.stat_layout = tk.LabelFrame(self.frame, text=" 📊 THỐNG KÊ HỆ THỐNG (LIVE) ", font=("Arial", 10, "bold"), fg="#002147", padx=10, pady=8)
        self.stat_layout.pack(fill=tk.X, padx=10, pady=5)
        
        self.lbl_stats = tk.Label(self.stat_layout, text="Đang tính toán dữ liệu...", font=("Arial", 11, "bold"), fg="#008080")
        self.lbl_stats.pack(fill=tk.X)
        
        self.bottom_layout = tk.LabelFrame(self.frame, text=" BẢNG THEO DÕI XE MÁY ĐANG ĐỖ (LIVE DATA OBSERVER) ", font=("Arial", 10, "bold"), padx=5, pady=5)
        self.bottom_layout.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)
        
        self.build_top_controls_and_map()
        self.build_bottom_filter_bar()
        self.build_bottom_table()
        self.refresh_ui()

    def update_live_statistics(self):
        """Hàm tự động tính toán tổng số xe đang gửi, tỉ lệ lấp đầy và doanh thu trong ngày"""
        try:
            grid = self.ctrl.get_all_slots()
            total_slots = len(grid) * len(grid[0]) if grid and len(grid) > 0 else 1
            
            # 1. Tính tổng số xe đang gửi
            occupied_slots = 0
            for r in range(len(grid)):
                for c in range(len(grid[0])):
                    if grid[r][c].status == "Occupied":
                        occupied_slots += 1
                        
            # 2. Tính tỉ lệ lấp đầy bãi xe
            fill_rate = (occupied_slots / total_slots) * 100
            
            # 3. Tính tổng doanh thu trong ngày (lọc từ lịch sử xe ra có ngày hôm nay)
            today_str = datetime.now().strftime('%Y-%m-%d')
            today_revenue = 0
            data_history = self.ctrl.get_parking_history() or []
            
            for item in data_history:
                # Kiểm tra định dạng thời gian ra để so sánh ngày
                time_out_str = item.get("time_out", "")
                if today_str in time_out_str:
                    today_revenue += item.get("fee", 0)
            
            # Cập nhật thông số lên giao diện
            stat_text = f"🔄 Xe đang gửi: {occupied_slots} chiếc  |  📈 Tỉ lệ lấp đầy: {fill_rate:.1f}%  |  💰 Doanh thu hôm nay ({datetime.now().strftime('%d/%m')}): {today_revenue:,.0f} VND"
            self.lbl_stats.config(text=stat_text)
        except Exception as e:
            self.lbl_stats.config(text=f"⚠️ Lỗi cập nhật thống kê: {str(e)}")

    def log_to_csv_backup(self, plate, slot_id, time_in, time_out, fee):
        """CHỨC NĂNG BỔ SUNG: Tự động lưu trữ lịch sử xe ra vào dưới dạng file CSV để hậu kiểm"""
        file_name = "parking_history_backup.csv"
        file_exists = os.path.isfile(file_name)
        
        try:
            with open(file_name, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    # Ghi tiêu đề cột nếu file chưa được tạo trước đó
                    writer.writerow(["Biển Số Xe", "Vị Trí Đỗ", "Thời Gian Vào", "Thời Gian Ra", "Doanh Thu (VND)", "Ngày Hậu Kiểm"])
                
                writer.writerow([plate, slot_id, time_in, time_out, f"{fee:.0f}", datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        except Exception as e:
            print(f"Không thể ghi log file CSV backup: {str(e)}")

    def build_top_controls_and_map(self):
        checkin_box = tk.LabelFrame(self.top_layout, text=" CỔNG VÀO (CHECK-IN) ", font=("Arial", 10, "bold"), padx=10, pady=10)
        checkin_box.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        tk.Label(checkin_box, text="Nhập Biển Số Xe Máy:", font=("Arial", 10)).pack(anchor=tk.W, pady=5)
        self.ent_plate = tk.Entry(checkin_box, font=("Arial", 12), width=18)
        self.ent_plate.pack(pady=5)
        
        btn_in = tk.Button(checkin_box, text="XÁC NHẬN VÀO", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), height=2, width=16, command=self.trigger_check_in)
        btn_in.pack(pady=10)
        
        edit_box = tk.LabelFrame(checkin_box, text=" QUẢN TRỊ VIÊN BẢNG ", font=("Arial", 9, "bold"), pady=5, padx=5)
        edit_box.pack(fill=tk.X, pady=10)
        
        tk.Label(edit_box, text="Vị trí chọn:", font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W)
        self.lbl_selected_slot = tk.Label(edit_box, text="Chưa chọn", font=("Arial", 9, "bold"), fg="blue")
        self.lbl_selected_slot.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        tk.Label(edit_box, text="Biển số mới:", font=("Arial", 9)).grid(row=1, column=0, sticky=tk.W)
        self.ent_new_plate = tk.Entry(edit_box, font=("Arial", 10), width=12)
        self.ent_new_plate.grid(row=1, column=1, pady=2)
        
        btn_edit = tk.Button(edit_box, text="SỬA BIỂN SỐ", bg="#FF9800", fg="white", font=("Arial", 9, "bold"), command=self.trigger_edit_table)
        btn_edit.grid(row=2, column=0, columnspan=2, sticky="ew", pady=4)
        
        btn_del = tk.Button(edit_box, text="XÓA CƯỠNG CHẾ", bg="#795548", fg="white", font=("Arial", 9, "bold"), command=self.trigger_delete_table)
        btn_del.grid(row=3, column=0, columnspan=2, sticky="ew", pady=2)
        
        self.map_box = tk.LabelFrame(self.top_layout, text=" SƠ ĐỒ BÃI ĐỖ XE MÁY KHU A (Click ô đỗ để Check-out) ", font=("Arial", 10, "bold"), padx=10, pady=10)
        self.map_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.grid_frame = tk.Frame(self.map_box)
        self.grid_frame.pack(expand=True)

    def build_bottom_filter_bar(self):
        filter_frame = tk.Frame(self.bottom_layout, pady=2)
        filter_frame.pack(fill=tk.X, side=tk.TOP)
        
        tk.Label(filter_frame, text="🔍 Tìm nhanh biển số:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
        self.ent_search = tk.Entry(filter_frame, font=("Arial", 10), width=15)
        self.ent_search.pack(side=tk.LEFT, padx=5)
        self.ent_search.bind("<KeyRelease>", lambda event: self.filter_and_sort_table_data())
        
        self.btn_sort = tk.Button(filter_frame, text="⏳ Sắp xếp: Cũ nhất trước", bg="#008CBA", fg="white", font=("Arial", 9, "bold"), command=self.toggle_sort_order)
        self.btn_sort.pack(side=tk.LEFT, padx=5)
        
        btn_quick_sort = tk.Button(
            filter_frame, 
            text="📊 BÁO CÁO DOANH THU (QUICK SORT)", 
            bg="#9C27B0", 
            fg="white", 
            font=("Arial", 9, "bold"), 
            command=self.open_revenue_report_window
        )
        btn_quick_sort.pack(side=tk.RIGHT, padx=5)

    def build_bottom_table(self):
        columns = ("slot_id", "plate", "time_in")
        self.tree = ttk.Treeview(self.bottom_layout, columns=columns, show="headings", height=6)
        
        self.tree.heading("slot_id", text="Mã Vị Trí Đỗ")
        self.tree.heading("plate", text="Biển Số Xe")
        self.tree.heading("time_in", text="Thời Gian Vào Bãi")
        
        self.tree.column("slot_id", width=120, anchor=tk.CENTER)
        self.tree.column("plate", width=180, anchor=tk.CENTER)
        self.tree.column("time_in", width=250, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_table_row_select)

    def toggle_sort_order(self):
        self.sort_ascending = not self.sort_ascending
        if self.sort_ascending:
            self.btn_sort.config(text="⏳ Sắp xếp: Cũ nhất trước")
        else:
            self.btn_sort.config(text="⏳ Sắp xếp: Mới nhất trước")
        self.filter_and_sort_table_data()

    def filter_and_sort_table_data(self):
        search_keyword = self.ent_search.get().strip().upper()
        grid = self.ctrl.get_all_slots()
        valid_records = []
        
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                slot = grid[r][c]
                if slot.status == "Occupied" and slot.current_vehicle:
                    plate = slot.current_vehicle.license_plate
                    time_str = slot.current_vehicle.check_in_time.strftime('%Y-%m-%d %H:%M:%S')
                    
                    if search_keyword == "" or search_keyword in plate:
                        valid_records.append({
                            "slot_id": slot.slot_id,
                            "plate": plate,
                            "time_obj": slot.current_vehicle.check_in_time, 
                            "time_str": time_str
                        })
                        
        valid_records.sort(key=lambda x: x["time_obj"], reverse=not self.sort_ascending)
        
        self.tree.delete(*self.tree.get_children())
        for item in valid_records:
            self.tree.insert("", tk.END, values=(item["slot_id"], item["plate"], item["time_str"]))

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
        if slot.status == "Empty" or slot.status == "none":
            manual_plate = self.ent_plate.get().strip().upper()
            if manual_plate != "":
                confirm = messagebox.askyesno("Xếp chỗ thủ công", f"Bạn có muốn xếp xe máy [{manual_plate}] vào vị trí [{slot.slot_id}] theo cách thủ công không?")
                if confirm:
                    try:
                        self.ctrl.process_manual_check_in(manual_plate, slot.slot_id)
                        messagebox.showinfo("Thành công", f"Đã xếp xe [{manual_plate}] vào vị trí [{slot.slot_id}] thành công!")
                        self.ent_plate.delete(0, tk.END)
                        self.refresh_ui()
                    except Exception as ex:
                        messagebox.showerror("Lỗi", str(ex))
            else:
                messagebox.showinfo("Thông tin ô đỗ", f"Vị trí {slot.slot_id} hiện đang trống.\n\n👉 ĐỂ XẾP XE THỦ CÔNG:\nBước 1: Nhập biển số xe ở khung bên trái trước.\nBước 2: Click chuột vào ô này để xếp chỗ!")
            return
            
        detail_win = tk.Toplevel(self.frame)
        detail_win.title(f"Chi tiết vị trí: {slot.slot_id}")
        detail_win.geometry("350x220")
        detail_win.grab_set()
        
        plate_target = slot.current_vehicle.license_plate
        time_in_target = slot.current_vehicle.check_in_time.strftime('%Y-%m-%d %H:%M:%S')
        
        msg_info = f"📍 MÃ VỊ TRÍ: {slot.slot_id}\n\n" \
                   f"📝 BIỂN SỐ: {plate_target}\n\n" \
                   f"⏰ THỜI GIAN VÀO:\n{time_in_target}"
                   
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
                
                # --- CHỨC NĂNG BỔ SUNG: Tìm hóa đơn vừa tạo và lưu ngầm vào CSV để hậu kiểm ---
                history = self.ctrl.get_parking_history() or []
                if history:
                    # Lấy bản ghi cuối cùng chính là chiếc xe vừa ra
                    last_bill = history[-1]
                    self.log_to_csv_backup(
                        last_bill.get("plate"), 
                        last_bill.get("slot_id"), 
                        last_bill.get("time_in"), 
                        last_bill.get("time_out"), 
                        last_bill.get("fee", 0)
                    )

                self.refresh_ui()
            except Exception as ex:
                messagebox.showerror("Lỗi", str(ex))

        btn_checkout = tk.Button(detail_win, text="CHECK-OUT (CHO XE RA)", bg="#F44336", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5, command=run_checkout_action)
        btn_checkout.pack(pady=10)

    def on_table_row_select(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return
        row_values = self.tree.item(selected_items[0], 'values')
        if row_values:
            self.lbl_selected_slot.config(text=row_values[0])
            self.ent_new_plate.delete(0, tk.END)
            self.ent_new_plate.insert(0, row_values[1])

    def trigger_edit_table(self):
        slot_id = self.lbl_selected_slot.cget("text")
        new_plate = self.ent_new_plate.get().strip().upper()
        if slot_id == "Chưa chọn":
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dòng xe đang đỗ từ bảng dữ liệu phía dưới trước!")
            return
        try:
            self.ctrl.update_vehicle_plate(slot_id, new_plate)
            messagebox.showinfo("Thành công", f"Đã cập nhật biển số mới thành công cho vị trí {slot_id}!")
            self.lbl_selected_slot.config(text="Chưa chọn")
            self.ent_new_plate.delete(0, tk.END)
            self.refresh_ui()
        except Exception as ex:
            messagebox.showerror("Lỗi", str(ex))

    def trigger_delete_table(self):
        slot_id = self.lbl_selected_slot.cget("text")
        if slot_id == "Chưa chọn":
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dòng xe cần xóa từ bảng dữ liệu phía dưới!")
            return
        confirm = messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn XÓA CƯỠNG CHẾ xe tại vị trí {slot_id} không?\n(Hành động này giải phóng ô đỗ lập tức, không tính phí!)")
        if confirm:
            try:
                self.ctrl.delete_vehicle_force(slot_id)
                messagebox.showinfo("Thành công", f"Đã giải phóng vị trí {slot_id} thành công!")
                self.lbl_selected_slot.config(text="Chưa chọn")
                self.ent_new_plate.delete(0, tk.END)
                self.refresh_ui()
            except Exception as ex:
                messagebox.showerror("Lỗi", str(ex))

    def open_revenue_report_window(self):
        if getattr(self, '_is_report_opening', False):
            return 
            
        self._is_report_opening = True

        data_history = self.ctrl.get_parking_history()
        if not data_history:
            messagebox.showinfo("Thông báo", "Chưa có dữ liệu hóa đơn nào trong lịch sử để thống kê!")
            self._is_report_opening = False 
            return
            
        self.ctrl.quick_sort_history_by_fee(data_history, 0, len(data_history) - 1)
        
        self.report_win = tk.Toplevel(self.frame if hasattr(self, 'frame') else None)
        self.report_win.title("BÁO CÁO THỐNG KÊ DOANH THU CAO NHẤT (QUICK SORT)")
        self.report_win.geometry("750x450")
        self.report_win.grab_set()
        
        def on_close_report():
            self._is_report_opening = False
            self.report_win.destroy()
            
        self.report_win.protocol("WM_DELETE_WINDOW", on_close_report)
        
        top_bar = tk.Frame(self.report_win, pady=5)
        top_bar.pack(fill=tk.X, padx=10)

        total_revenue = sum(item["fee"] for item in data_history)
        total_tickets = len(data_history)
        
        summary_text = f"📈 TỔNG DOANH THU: {total_revenue:,.0f} VND  |  🎫 TỔNG LƯỢT XE: {total_tickets} lượt"
        lbl_summary = tk.Label(top_bar, text=summary_text, font=("Arial", 11, "bold"), fg="purple")
        lbl_summary.pack(side=tk.LEFT, pady=5)
        
        columns = ("id", "plate", "slot", "in", "out", "fee")
        tree_report = ttk.Treeview(self.report_win, columns=columns, show="headings")
        
        tree_report.heading("id", text="STT")
        tree_report.heading("plate", text="Biển Số Xe")
        tree_report.heading("slot", text="Vị Trí Đỗ")
        tree_report.heading("in", text="Thời Gian Vào")
        tree_report.heading("out", text="Thời Gian Ra")
        tree_report.heading("fee", text="Doanh Thu (VND)")
        
        tree_report.column("id", width=50, anchor=tk.CENTER)
        tree_report.column("plate", width=100, anchor=tk.CENTER)
        tree_report.column("slot", width=80, anchor=tk.CENTER)
        tree_report.column("in", width=140, anchor=tk.CENTER)
        tree_report.column("out", width=140, anchor=tk.CENTER)
        tree_report.column("fee", width=120, anchor=tk.CENTER)
        
        tree_report.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def trigger_clear_history():
            confirm = messagebox.askyesno(
                "XÁC NHẬN NGUY HIỂM", 
                "Bạn có chắc chắn muốn XÓA VĨNH VIỄN toàn bộ lịch sử doanh thu và hóa đơn không?\n(Hành động này không thể hoàn tác!)",
                parent=self.report_win
            )
            if confirm:
                try:
                    self.ctrl.clear_all_parking_history()
                    tree_report.delete(*tree_report.get_children())
                    lbl_summary.config(text="📈 TỔNG DOANH THU: 0 VND  |  🎫 TỔNG LƯỢT XE: 0 lượt")
                    self.update_live_statistics() # Cập nhật lại khung thống kê chính về 0
                    messagebox.showinfo("Thành công", "Đã dọn dẹp sạch toàn bộ lịch sử doanh thu!", parent=self.report_win)
                except Exception as ex:
                    messagebox.showerror("Lỗi", f"Không thể xóa dữ liệu: {str(ex)}", parent=self.report_win)

        btn_clear = tk.Button(
            top_bar, 
            text="🗑️ XÓA SẠCH LỊCH SỬ", 
            bg="#D32F2F", 
            fg="white", 
            font=("Arial", 9, "bold"), 
            command=trigger_clear_history
        )
        btn_clear.pack(side=tk.RIGHT, pady=5)
        
        for idx, item in enumerate(data_history, start=1):
            tree_report.insert("", tk.END, values=(
                idx, 
                item["plate"], 
                item["slot_id"], 
                item["time_in"], 
                item["time_out"], 
                f"{item['fee']:,.0f}"
            ))

    def refresh_ui(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
            
        grid = self.ctrl.get_all_slots()
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                slot = grid[r][c]
                bg_color = "#F44336" if slot.status == "Occupied" else "#4CAF50"
                
                btn = tk.Button(self.grid_frame, text=slot.slot_id, bg=bg_color, fg="white", font=("Arial", 9, "bold"), width=12, height=3, command=lambda s=slot: self.on_slot_click(s))
                btn.grid(row=r, column=c, padx=5, pady=5)
                
                if slot.status == "Occupied" and slot.current_vehicle:
                    self.bind_tooltip(btn, f"Biển số: {slot.current_vehicle.license_plate}")

        self.filter_and_sort_table_data()
        self.update_live_statistics() # Kích hoạt cập nhật thông số bãi đỗ thời gian thực

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