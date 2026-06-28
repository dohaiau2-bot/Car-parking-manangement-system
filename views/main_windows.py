import tkinter as tk
from tkinter import ttk
from views.tab_motorbike import MotorbikeTabBuilder
from views.tab_car import CarTabBuilder

class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("ĐỒ ÁN: HỆ THỐNG QUẢN LÝ BÃI XE THÔNG MINH")
        self.root.geometry("1100x700") # Cấu hình kích thước tối ưu cho cả 2 tab
        
        # 1. Thanh Tiêu Đề Chính (Header) của Hệ Thống
        self.header_frame = tk.Frame(self.root, bg="#1E88E5", pady=12)
        self.header_frame.pack(fill=tk.X)
        
        self.lbl_title = tk.Label(
            self.header_frame, 
            text="📊 HỆ THỐNG QUẢN LÝ BÃI XE THÔNG MINH - DASHBOARD", 
            font=("Arial", 14, "bold"), 
            fg="white", 
            bg="#1E88E5"
        )
        self.lbl_title.pack()

        # 2. Bộ Khung Chứa Tab (Notebook)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 3. GỌI HÀM GỘP ĐỂ NẠP CÁC TAB CHỨC NĂNG
        self.setup_all_parking_tabs()

    def setup_all_parking_tabs(self):
        """Hàm gộp chính phụ trách khởi tạo và nhúng các tab vào Dashboard"""
        
        # --- TAB 1: QUẢN LÝ XE MÁY (KHU A) ---
        self.tab_motorbike = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_motorbike, text=" 🏍️ QUẢN LÝ XE MÁY (KHU A) ")
        self.app_tab_a = MotorbikeTabBuilder(self.tab_motorbike)
        
        # --- TAB 2: QUẢN LÝ Ô TÔ (KHU B) ---
        self.tab_car = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_car, text=" 🚗 QUẢN LÝ Ô TÔ (KHU B) ")
        self.app_tab_b = CarTabBuilder(self.tab_car)