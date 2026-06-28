# main.py
import tkinter as tk
from tkinter import ttk
from views.tab_motorbike import MotorbikeTabBuilder

if __name__ == "__main__":
    root = tk.Tk()
    root.title("HỆ THỐNG QUẢN LÝ BÃI XE - CHẠY THỬ TAB A")
    root.geometry("1000x650")
    
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)
    
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text=" 🛵 KHU VỰC XE MÁY (MEMBER A) ")
    
    # Nhúng phân hệ của bạn A vào Tab 1
    app_tab_a = MotorbikeTabBuilder(tab1)
    
    root.mainloop()