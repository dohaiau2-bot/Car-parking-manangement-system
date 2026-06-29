# main.py
import tkinter as tk
from views.main_windows import Dashboard
from data.employee_db import init_db

def main():
    # 0. Khởi tạo Database SQLite dành riêng cho nhân viên trước khi mở ứng dụng
    init_db()

    # 1. Khởi tạo Tkinter gốc
    root = tk.Tk()
    
    # 2. Gọi Dashboard (Hàm gộp tự động nạp Xe máy + Ô tô + Nhân viên)
    app = Dashboard(root)
    
    # 3. Kích hoạt vòng lặp chạy ứng dụng
    root.mainloop()

if __name__ == "__main__":
    main()