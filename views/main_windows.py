import tkinter as tk
from tkinter import messagebox, ttk
from controllers.check_in import CheckInController
from controllers.check_out import CheckOutController
from controllers.staticstics import StatisticsController
from exceptions import LotFullError, VehicleNotFoundError

class ParkingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SMART PARKING MANAGEMENT SYSTEM - OBJECT ORIENTED TERM PROJECT")
        self.root.geometry("1050x650")
        
        # Controller bindings sharing atomic operational grid reference
        self.check_in_ctrl = CheckInController()
        self.check_out_ctrl = CheckOutController()
        self.stats_ctrl = StatisticsController()
        
        self.check_out_ctrl.motorbike_lot = self.check_in_ctrl.motorbike_lot
        self.check_out_ctrl.car_lot = self.check_in_ctrl.car_lot
        self.check_out_ctrl.waiting_queue = self.check_in_ctrl.waiting_queue
        
        self.stats_ctrl.motorbike_lot = self.check_in_ctrl.motorbike_lot
        self.stats_ctrl.car_lot = self.check_in_ctrl.car_lot
        self.stats_ctrl.waiting_queue = self.check_in_ctrl.waiting_queue

        self.create_widgets()
        self.refresh_parking_map()
        self.refresh_stats()

    def create_widgets(self):
        # ---- Left Panel: Real-time Visual Map ----
        left_frame = tk.LabelFrame(self.root, text=" VISUAL PARKING LOT MAP ", font=("Arial", 12, "bold"), padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Zone A - Motorbike
        lbl_zone_a = tk.Label(left_frame, text="ZONE A - MOTORBIKES (Green: Empty | Red: Occupied)", font=("Arial", 10, "bold"), fg="blue")
        lbl_zone_a.pack(anchor=tk.W, pady=(0, 5))
        self.frame_zone_a = tk.Frame(left_frame)
        self.frame_zone_a.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Zone B - Car
        lbl_zone_b = tk.Label(left_frame, text="ZONE B - CARS (Green: Empty | Red: Occupied)", font=("Arial", 10, "bold"), fg="darkgreen")
        lbl_zone_b.pack(anchor=tk.W, pady=(0, 5))
        self.frame_zone_b = tk.Frame(left_frame)
        self.frame_zone_b.pack(fill=tk.BOTH, expand=True)

        # ---- Right Panel: Controller Operations & Analytics ----
        right_frame = tk.Frame(self.root, padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Gateway Module (Check-in/Out Interface)
        gate_frame = tk.LabelFrame(right_frame, text=" INBOUND / OUTBOUND GATEWAY ", font=("Arial", 11, "bold"), padx=10, pady=10)
        gate_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(gate_frame, text="License Plate:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ent_plate = tk.Entry(gate_frame, font=("Arial", 11), width=18)
        self.ent_plate.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(gate_frame, text="Vehicle Type:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.cbo_type = ttk.Combobox(gate_frame, values=["Motorbike", "Car"], state="readonly", width=16, font=("Arial", 10))
        self.cbo_type.current(0)
        self.cbo_type.grid(row=1, column=1, pady=5, padx=5)

        btn_in = tk.Button(gate_frame, text="CHECK-IN (GATE)", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.handle_check_in)
        btn_in.grid(row=2, column=0, pady=10, padx=5, sticky=tk.E+tk.W)

        btn_out = tk.Button(gate_frame, text="CHECK-OUT (GATE)", bg="#F44336", fg="white", font=("Arial", 10, "bold"), command=self.handle_check_out)
        btn_out.grid(row=2, column=1, pady=10, padx=5, sticky=tk.E+tk.W)

        # Real-time Telemetry Dashboard
        metrics_frame = tk.LabelFrame(right_frame, text=" LIVE LOT ANALYTICS ", font=("Arial", 11, "bold"), padx=10, pady=10)
        metrics_frame.pack(fill=tk.X, pady=(0, 10))

        self.lbl_total_parked = tk.Label(metrics_frame, text="Total Parked: 0", font=("Arial", 10))
        self.lbl_total_parked.pack(anchor=tk.W, pady=2)
        
        self.lbl_rate = tk.Label(metrics_frame, text="Occupancy Rate: 0%", font=("Arial", 10))
        self.lbl_rate.pack(anchor=tk.W, pady=2)

        self.lbl_revenue = tk.Label(metrics_frame, text="Total Revenue: 0 VND", font=("Arial", 10, "bold"), fg="darkgreen")
        self.lbl_revenue.pack(anchor=tk.W, pady=2)
        
        btn_sort = tk.Button(metrics_frame, text="View Revenue Records (Quick Sort)", bg="#2196F3", fg="white", command=self.show_sorted_revenue)
        btn_sort.pack(fill=tk.X, pady=5)

        # Gate Waiting Buffer List Frame
        queue_frame = tk.LabelFrame(right_frame, text=" GATE WAITING QUEUE ", font=("Arial", 11, "bold"), padx=10, pady=10)
        queue_frame.pack(fill=tk.BOTH, expand=True)

        self.lst_queue = tk.Listbox(queue_frame, font=("Arial", 9), bg="#F5F5F5")
        self.lst_queue.pack(fill=tk.BOTH, expand=True)

    def refresh_parking_map(self):
        for w in self.frame_zone_a.winfo_children(): w.destroy()
        for w in self.frame_zone_b.winfo_children(): w.destroy()

        # Render Motorbike Grid Layout (Zone A)
        for r in range(self.check_in_ctrl.rows):
            for c in range(self.check_in_ctrl.cols):
                slot = self.check_in_ctrl.motorbike_lot[r][c]
                bg_color = "red" if slot.status == "Occupied" else "green"
                btn = tk.Button(self.frame_zone_a, text=slot.slot_id, bg=bg_color, fg="white", width=12, height=3)
                btn.grid(row=r, column=c, padx=5, pady=5)
                
                if slot.status == "Occupied" and slot.current_vehicle:
                    self.bind_hover_tooltip(btn, f"Plate: {slot.current_vehicle.license_plate}\nIn: {slot.current_vehicle.check_in_time.strftime('%H:%M:%S')}")

        # Render Car Grid Layout (Zone B)
        for r in range(self.check_in_ctrl.rows):
            for c in range(self.check_in_ctrl.cols):
                slot = self.check_in_ctrl.car_lot[r][c]
                bg_color = "red" if slot.status == "Occupied" else "green"
                btn = tk.Button(self.frame_zone_b, text=slot.slot_id, bg=bg_color, fg="white", width=12, height=3)
                btn.grid(row=r, column=c, padx=5, pady=5)
                
                if slot.status == "Occupied" and slot.current_vehicle:
                    self.bind_hover_tooltip(btn, f"Plate: {slot.current_vehicle.license_plate}\nIn: {slot.current_vehicle.check_in_time.strftime('%H:%M:%S')}")

    def bind_hover_tooltip(self, widget, text):
        def show(event):
            self.tooltip = tk.Toplevel(self.root)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            lbl = tk.Label(self.tooltip, text=text, background="#FFFFE0", relief="solid", borderwidth=1, font=("Arial", 10), padx=5, pady=5)
            lbl.pack()
            
        def hide(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()

        widget.bind("<Enter>", show)
        widget.bind("<Leave>", hide)

    def refresh_stats(self):
        metrics = self.stats_ctrl.compile_metrics()
        self.lbl_total_parked.config(text=f"Total Vehicles Parked: {metrics['total_parked']} (Motorbikes: {metrics['motorbikes']}, Cars: {metrics['cars']})")
        self.lbl_rate.config(text=f"Occupancy Rate: {metrics['occupancy_rate']}")
        self.lbl_revenue.config(text=f"Total Revenue: {metrics['total_revenue']:,} VND")
        
        self.lst_queue.delete(0, tk.END)
        for i, entry in enumerate(self.check_in_ctrl.waiting_queue.to_list()):
            self.lst_queue.insert(tk.END, f"Queue Pos {i+1}. {entry['license_plate']} ({entry['vehicle_type']})")

    def handle_check_in(self):
        license_plate = self.ent_plate.get().strip().upper()
        vehicle_type = self.cbo_type.get()

        if not license_plate:
            messagebox.showwarning("Warning", "License plate entry cannot be empty!")
            return

        try:
            status, msg = self.check_in_ctrl.process_check_in(license_plate, vehicle_type)
            if status == "Success":
                messagebox.showinfo("Check-In Confirmed", msg)
            else:
                messagebox.showwarning("Duplication Alert", msg)
        except LotFullError as ex:
            messagebox.showwarning("Lot Overflow (LotFullError)", str(ex))
        
        self.ent_plate.delete(0, tk.END)
        self.refresh_parking_map()
        self.refresh_stats()

    def handle_check_out(self):
        license_plate = self.ent_plate.get().strip().upper()

        if not license_plate:
            messagebox.showwarning("Warning", "Please provide a valid license plate for check-out!")
            return

        try:
            fee, msg = self.check_out_ctrl.process_check_out(license_plate)
            # Receipt Print Simulation popup requested by prompt layout specs
            messagebox.showinfo("PRINT SYSTEM RECEIPT", f"--- SMART PARKING PROJECT RECEIPT ---\nPlate: {license_plate}\n{msg}")
        except VehicleNotFoundError as ex:
            messagebox.showerror("Lot Fault (VehicleNotFoundError)", str(ex))

        self.ent_plate.delete(0, tk.END)
        self.refresh_parking_map()
        self.refresh_stats()

    def show_sorted_revenue(self):
        sub_window = tk.Toplevel(self.root)
        sub_window.title("Audit Logging Ledger - Sorted by Quick Sort")
        sub_window.geometry("600x400")

        text_pad = tk.Text(sub_window, font=("Courier New", 10), padx=10, pady=10)
        text_pad.pack(fill=tk.BOTH, expand=True)

        sorted_array = self.stats_ctrl.get_sorted_history()
        
        text_pad.insert(tk.END, f"{'PLATE':<15}{'TYPE':<12}{'SLOT ID':<12}{'FEE REVENUE (VND)':<15}\n")
        text_pad.insert(tk.END, "-" * 55 + "\n")
        
        for entry in sorted_array:
            text_pad.insert(tk.END, f"{entry['license_plate']:<15}{entry['vehicle_type']:<12}{entry['slot_id']:<12}{entry['fee']:<15,}\n")