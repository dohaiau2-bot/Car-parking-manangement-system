import tkinter as tk
from views.main_windows import Dashboard

def main():
    # 1. Khởi tạo Tkinter gốc
    root = tk.Tk()
    
    # 2. Gọi Dashboard (Hàm gộp tự động nạp Xe máy + Ô tô đã nằm trong này)
    app = Dashboard(root)
    
    # 3. Kích hoạt vòng lặp chạy ứng dụng
    root.mainloop()

if __name__ == "__main__":
    main()