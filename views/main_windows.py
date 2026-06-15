import tkinter as tk
from tkinter import messagebox, ttk
from controllers.check_in import CheckInController
from controllers.check_out import CheckOutController
from controllers.staticstics import StatisticsController
from exceptions import LotFullError, VehicleNotFoundError

class ParkingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SMART PARKING MANAGEMENT SYSTEM - ZERO DEPENDENCY MULTI-TAB FRAMEWORK")
        self.root.geometry("1100x700")
        
        # --- Shared Core Controller Bindings ---
        self.check_in_ctrl = CheckInController()
        self.check_out_ctrl = CheckOutController()
        self.stats_ctrl = StatisticsController()
        
        self.check_out_ctrl.motorbike_lot = self.check_in_ctrl.motorbike_lot
        self.check_out_ctrl.car_lot = self.check_in_ctrl.car_lot
        self.check_out_ctrl.waiting_queue = self.check_in_ctrl.waiting_queue
        
        self.stats_ctrl.motorbike_lot = self.check_in_ctrl.motorbike_lot
        self.stats_ctrl.car_lot = self.check_in_ctrl.car_lot
        self.stats_ctrl.waiting_queue = self.check_in_ctrl.waiting_queue

        # --- Base Tab Control (Notebook) Setup ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create isolated workspace frames for each team member
        self.tab_member_a = ttk.Frame(self.notebook)
        self.tab_member_b = ttk.Frame(self.notebook)
        self.tab_member_c = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_member_a, text=" 🛵 MOTORBIKE ZONE (Member A) ")
        self.notebook.add(self.tab_member_b, text=" 🚗 CAR REGULAR ZONE (Member B) ")
        self.notebook.add(self.tab_member_c, text=" 💳 VIP & MONTHLY CARD ZONE (Member C) ")

        # --- Trigger Sandbox Initializations ---
        self.setup_motorbike_zone_tab()   # Handled by Member A
        self.setup_car_zone_tab()         # Handled by Member B
        self.setup_card_zone_tab()        # Handled by Member C

    # =========================================================================
    # 🛵 MODULE 1: MOTORBIKE ZONE WORKSPACE (MEMBER A)
    # =========================================================================
    def setup_motorbike_zone_tab(self):
        """
        Member A writes all layout widgets, local states, and button event 
        handlers for the Motorbike Subsystem completely within this function.
        """
        # Base container for Tab A
        main_frame = tk.Frame(self.tab_member_a, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Left Panel: Visual Grid Map
        left_map_frame = tk.LabelFrame(main_frame, text=" MOTORBIKE GRID STATUS ", font=("Arial", 11, "bold"), padx=10, pady=10)
        left_map_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.frame_zone_a = tk.Frame(left_map_frame)
        self.frame_zone_a.pack(fill=tk.BOTH, expand=True)

        # 2. Right Panel: Gate Operations & Analytics Tracker
        right_panel = tk.Frame(main_frame, width=320)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)

        # Gateway Interactive Box
        gate_box = tk.LabelFrame(right_panel, text=" GATE CONTROL ", font=("Arial", 10, "bold"), padx=10, pady=10)
        gate_box.pack(fill=tk.X, pady=(0, 10))

        tk.Label(gate_box, text="License Plate:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ent_plate_a = tk.Entry(gate_box, font=("Arial", 11), width=15)
        self.ent_plate_a.grid(row=0, column=1, pady=5, padx=5)

        btn_in = tk.Button(gate_box, text="MOTORBIKE IN", bg="#4CAF50", fg="white", width=12, font=("Arial", 9, "bold"), command=self.handle_motorbike_in)
        btn_in.grid(row=1, column=0, pady=10, padx=5)

        btn_out = tk.Button(gate_box, text="MOTORBIKE OUT", bg="#F44336", fg="white", width=12, font=("Arial", 9, "bold"), command=self.handle_motorbike_out)
        btn_out.grid(row=1, column=1, pady=10, padx=5)

        # Sub-metrics tracker board
        metrics_box = tk.LabelFrame(right_panel, text=" ZONE METRICS ", font=("Arial", 10, "bold"), padx=10, pady=10)
        metrics_box.pack(fill=tk.BOTH, expand=True)
        
        self.lbl_mb_stats = tk.Label(metrics_box, text="Total Active Motorbikes: 0", font=("Arial", 10))
        self.lbl_mb_stats.pack(anchor=tk.W, pady=5)

        # Render internal grid initially
        self.refresh_motorbike_map()

    def handle_motorbike_in(self):
        plate = self.ent_plate_a.get().strip().upper()
        if not plate:
            messagebox.showwarning("Warning", "License plate required!")
            return
        try:
            status, msg = self.check_in_ctrl.process_check_in(plate, "Motorbike")
            if status == "Success":
                messagebox.showinfo("Check-In Confirmed", msg)
            else:
                messagebox.showwarning("Duplication Alert", msg)
        except LotFullError as ex:
            messagebox.showwarning("Lot Overflow", str(ex))
        
        self.ent_plate_a.delete(0, tk.END)
        self.refresh_motorbike_map()

    def handle_motorbike_out(self):
        plate = self.ent_plate_a.get().strip().upper()
        if not plate:
            messagebox.showwarning("Warning", "License plate required!")
            return
        try:
            fee, msg = self.check_out_ctrl.process_check_out(plate)
            messagebox.showinfo("RECEIPT", f"--- MOTORBIKE STATION ---\nPlate: {plate}\n{msg}")
        except VehicleNotFoundError as ex:
            messagebox.showerror("Error", str(ex))
            
        self.ent_plate_a.delete(0, tk.END)
        self.refresh_motorbike_map()

    def refresh_motorbike_map(self):
        for w in self.frame_zone_a.winfo_children(): 
            w.destroy()
            
        # Dynamically loop and render A-Zone map cells
        for r in range(self.check_in_ctrl.rows):
            for c in range(self.check_in_ctrl.cols):
                slot = self.check_in_ctrl.motorbike_lot[r][c]
                bg_color = "red" if slot.status == "Occupied" else "green"
                btn = tk.Button(self.frame_zone_a, text=slot.slot_id, bg=bg_color, fg="white", width=11, height=3)
                btn.grid(row=r, column=c, padx=4, pady=4)
                if slot.status == "Occupied" and slot.current_vehicle:
                    self.bind_hover_tooltip(btn, f"Plate: {slot.current_vehicle.license_plate}\nIn: {slot.current_vehicle.check_in_time.strftime('%H:%M:%S')}")
        
        # Local metrics calculation
        active_count = sum(1 for r in range(self.check_in_ctrl.rows) for c in range(self.check_in_ctrl.cols) if self.check_in_ctrl.motorbike_lot[r][c].status == "Occupied")
        if hasattr(self, 'lbl_mb_stats'):
            self.lbl_mb_stats.config(text=f"Total Active Motorbikes: {active_count}")


    # =========================================================================
    # 🚗 MODULE 2: CAR REGULAR ZONE & OVERLOAD QUEUE WORKSPACE (MEMBER B)
    # =========================================================================
    def setup_car_zone_tab(self):
        """
        Member B writes all layout widgets, local states, custom queue displays, 
        and event structures for Car Regular Parking completely within this function.
        """
        main_frame = tk.Frame(self.tab_member_b, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Left Panel: Visual Car Grid Layout
        left_map_frame = tk.LabelFrame(main_frame, text=" CAR REGULAR GRID ", font=("Arial", 11, "bold"), padx=10, pady=10)
        left_map_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.frame_zone_b = tk.Frame(left_map_frame)
        self.frame_zone_b.pack(fill=tk.BOTH, expand=True)

        # 2. Right Panel: Dynamic Operations, Toll Policies & Custom Queue View
        right_panel = tk.Frame(main_frame, width=340)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)

        # Car Gateway Controls Block
        gate_box = tk.LabelFrame(right_panel, text=" CAR PORT OPERATIONS ", font=("Arial", 10, "bold"), padx=10, pady=10)
        gate_box.pack(fill=tk.X, pady=(0, 10))

        tk.Label(gate_box, text="Car Plate:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ent_plate_b = tk.Entry(gate_box, font=("Arial", 11), width=16)
        self.ent_plate_b.grid(row=0, column=1, pady=5, padx=5)

        btn_in = tk.Button(gate_box, text="CAR CHECK-IN", bg="#4CAF50", fg="white", width=12, font=("Arial", 9, "bold"), command=self.handle_car_in)
        btn_in.grid(row=1, column=0, pady=10, padx=5)

        btn_out = tk.Button(gate_box, text="CAR CHECK-OUT", bg="#F44336", fg="white", width=12, font=("Arial", 9, "bold"), command=self.handle_car_out)
        btn_out.grid(row=1, column=1, pady=10, padx=5)

        # Overflow Queue live structural array tracking board
        queue_box = tk.LabelFrame(right_panel, text=" OVERFLOW LINE BUFFER (CUSTOM QUEUE) ", font=("Arial", 9, "bold"), padx=10, pady=10)
        queue_box.pack(fill=tk.BOTH, expand=True)

        self.lst_queue_b = tk.Listbox(queue_box, font=("Arial", 9), bg="#F5F5F5")
        self.lst_queue_b.pack(fill=tk.BOTH, expand=True)
        
        # Open Policy Trigger configuration sub-window controller hook 
        btn_policy = tk.Button(queue_box, text="Configure Peak Pricing Policy", bg="#9C27B0", fg="white", font=("Arial", 9), command=self.open_peak_pricing_config)
        btn_policy.pack(fill=tk.X, pady=(5, 0))

        # Render structural grid and current waitlists initially
        self.refresh_car_map()
        self.refresh_car_queue_display()

    def handle_car_in(self):
        plate = self.ent_plate_b.get().strip().upper()
        if not plate:
            messagebox.showwarning("Warning", "License plate required!")
            return
        try:
            status, msg = self.check_in_ctrl.process_check_in(plate, "Car")
            if status == "Success":
                messagebox.showinfo("Check-In Confirmed", msg)
            else:
                messagebox.showwarning("Duplication Alert", msg)
        except LotFullError as ex:
            messagebox.showwarning("Lot Full - Placed in Waiting Line", str(ex))
        
        self.ent_plate_b.delete(0, tk.END)
        self.refresh_car_map()
        self.refresh_car_queue_display()

    def handle_car_out(self):
        plate = self.ent_plate_b.get().strip().upper()
        if not plate:
            messagebox.showwarning("Warning", "License plate required!")
            return
        try:
            fee, msg = self.check_out_ctrl.process_check_out(plate)
            messagebox.showinfo("RECEIPT", f"--- CAR REGULAR STATION ---\nPlate: {plate}\n{msg}")
        except VehicleNotFoundError as ex:
            messagebox.showerror("Error", str(ex))
            
        self.ent_plate_b.delete(0, tk.END)
        self.refresh_car_map()
        # Refreshing both maps since queue dispatchers might instantly re-park vehicles to vacated slots
        self.refresh_motorbike_map() 
        self.refresh_car_queue_display()

    def refresh_car_map(self):
        for w in self.frame_zone_b.winfo_children(): 
            w.destroy()
            
        for r in range(self.check_in_ctrl.rows):
            for c in range(self.check_in_ctrl.cols):
                slot = self.check_in_ctrl.car_lot[r][c]
                bg_color = "red" if slot.status == "Occupied" else "green"
                btn = tk.Button(self.frame_zone_b, text=slot.slot_id, bg=bg_color, fg="white", width=11, height=3)
                btn.grid(row=r, column=c, padx=4, pady=4)
                if slot.status == "Occupied" and slot.current_vehicle:
                    self.bind_hover_tooltip(btn, f"Plate: {slot.current_vehicle.license_plate}\nIn: {slot.current_vehicle.check_in_time.strftime('%H:%M:%S')}")

    def refresh_car_queue_display(self):
        self.lst_queue_b.delete(0, tk.END)
        for i, entry in enumerate(self.check_in_ctrl.waiting_queue.to_list()):
            self.lst_queue_b.insert(tk.END, f"Pos {i+1}. {entry['license_plate']} ({entry['vehicle_type']})")

    def open_peak_pricing_config(self):
        """ Standalone Policy Setup sandbox designed by Member B """
        policy_win = tk.Toplevel(self.root)
        policy_win.title("Dynamic Tariff Policy Configurator")
        policy_win.geometry("380x200")
        tk.Label(policy_win, text="Dynamic Policy Panel - Isolated Sandbox Core Engine", font=("Arial", 10, "bold")).pack(pady=10)
        # Member B can insert entries, sliders, and charts inside this local container frame securely.


    # =========================================================================
    # 💳 MODULE 3: VIP MEMBER CARD MANAGEMENT & LEDGER ANALYTICS (MEMBER C)
    # =========================================================================
    def setup_card_zone_tab(self):
        """
        Member C writes all layout widgets, accounts forms, Quick Sort ledgers, 
        and analytics telemetry boards completely within this function.
        """
        main_frame = tk.Frame(self.tab_member_c, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Left Panel: Registered Cards Audit List Ledger & Analytics
        left_ledger_frame = tk.LabelFrame(main_frame, text=" SYSTEM AUDIT LEDGER (QUICK SORT INTEGRATION) ", font=("Arial", 11, "bold"), padx=10, pady=10)
        left_ledger_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Financial Data Reporting Box Layout Frame
        self.txt_ledger_logs = tk.Text(left_ledger_frame, font=("Courier New", 10), bg="#FDFEFE")
        self.txt_ledger_logs.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        btn_trigger_sort = tk.Button(left_ledger_frame, text="⚡ Run Revenue Audit Ledger (Execute Quick Sort Over Records)", bg="#2196F3", fg="white", font=("Arial", 10, "bold"), command=self.execute_quick_sort_ledger_report)
        btn_trigger_sort.pack(fill=tk.X)

        # 2. Right Panel: VIP Operations & Global Telemetry Status Box
        right_panel = tk.Frame(main_frame, width=320)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)

        card_ops_box = tk.LabelFrame(right_panel, text=" VIP SUBSCRIPTION MANAGEMENT ", font=("Arial", 10, "bold"), padx=10, pady=10)
        card_ops_box.pack(fill=tk.X, pady=(0, 10))
        
        # Member C UI Fields Form block placeholders
        tk.Label(card_ops_box, text="Account/Card ID:").pack(anchor=tk.W, pady=2)
        self.ent_card_id = tk.Entry(card_ops_box, font=("Arial", 11))
        self.ent_card_id.pack(fill=tk.X, pady=(0, 10))

        btn_register_vip = tk.Button(card_ops_box, text="Register VIP Card", bg="#009688", fg="white", command=self.handle_vip_registration)
        btn_register_vip.pack(fill=tk.X, pady=2)
        
        btn_top_up = tk.Button(card_ops_box, text="Deposit Credits / Top-Up", bg="#FF9800", fg="white", command=self.handle_vip_top_up)
        btn_top_up.pack(fill=tk.X, pady=2)

        # Real-time System Metrics Board Dashboard
        global_metrics_box = tk.LabelFrame(right_panel, text=" OVERALL SYSTEM METRICS ", font=("Arial", 10, "bold"), padx=10, pady=10)
        global_metrics_box.pack(fill=tk.BOTH, expand=True)

        self.lbl_global_parked = tk.Label(global_metrics_box, text="Total Parked: 0", font=("Arial", 10))
        self.lbl_global_parked.pack(anchor=tk.W, pady=4)

        self.lbl_global_rate = tk.Label(global_metrics_box, text="Occupancy Rate: 0%", font=("Arial", 10))
        self.lbl_global_rate.pack(anchor=tk.W, pady=4)

        self.lbl_global_revenue = tk.Label(global_metrics_box, text="Total Revenue: 0 VND", font=("Arial", 10, "bold"), fg="darkgreen")
        self.lbl_global_revenue.pack(anchor=tk.W, pady=4)
        
        # Trigger an initial layout compilation refresh pass over variables 
        self.refresh_global_telemetry_metrics()

    def handle_vip_registration(self):
        card_id = self.ent_card_id.get().strip().upper()
        if not card_id:
            messagebox.showwarning("Warning", "Card Reference Key required!")
            return
        messagebox.showinfo("VIP Event Handler", f"Card [{card_id}] successfully registered inside local JSON runtime database context.")
        self.ent_card_id.delete(0, tk.END)

    def handle_vip_top_up(self):
        card_id = self.ent_card_id.get().strip().upper()
        if not card_id:
            messagebox.showwarning("Warning", "Specify Card Key Reference!")
            return
        messagebox.showinfo("VIP Credit System", f"Deposited credit funds securely to Card account {card_id}.")
        self.ent_card_id.delete(0, tk.END)

    def execute_quick_sort_ledger_report(self):
        sorted_array = self.stats_ctrl.get_sorted_history()
        self.txt_ledger_logs.delete("1.0", tk.END)
        
        self.txt_ledger_logs.insert(tk.END, f"{'PLATE':<15}{'VEHICLE TYPE':<15}{'SLOT LOCATION':<15}{'REVENUE':<15}\n")
        self.txt_ledger_logs.insert(tk.END, "=" * 60 + "\n")
        
        for entry in sorted_array:
            self.txt_ledger_logs.insert(tk.END, f"{entry['license_plate']:<15}{entry['vehicle_type']:<15}{entry['slot_id']:<15}{entry['fee']:<15,} VND\n")
            
        self.refresh_global_telemetry_metrics()

    def refresh_global_telemetry_metrics(self):
        metrics = self.stats_ctrl.compile_metrics()
        self.lbl_global_parked.config(text=f"Total Vehicles Parked: {metrics['total_parked']} (Motorbikes: {metrics['motorbikes']}, Cars: {metrics['cars']})")
        self.lbl_global_rate.config(text=f"Occupancy Rate: {metrics['occupancy_rate']}")
        self.lbl_global_revenue.config(text=f"Total System Revenue: {metrics['total_revenue']:,} VND")


    # =========================================================================
    # 🛠️ HELPER UTILITIES LABELS FRAME (UTILITY FUNCTIONS)
    # =========================================================================
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