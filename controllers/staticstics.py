from controllers.base_mananger import BaseParkingManager

class StatisticsController(BaseParkingManager):
    def __init__(self, rows=3, cols=4):
        super().__init__(rows, cols)

    def compile_metrics(self):
        active_motorbikes = sum(1 for r in range(self.rows) for c in range(self.cols) if self.motorbike_lot[r][c].status == "Occupied")
        active_cars = sum(1 for r in range(self.rows) for c in range(self.cols) if self.car_lot[r][c].status == "Occupied")
        
        total_parked = active_motorbikes + active_cars
        total_capacity = (self.rows * self.cols) * 2
        occupancy_rate = (total_parked / total_capacity) * 100 if total_capacity > 0 else 0
        
        self.parking_history = self.load_history()
        total_revenue = sum(entry["fee"] for entry in self.parking_history)
        
        return {
            "total_parked": total_parked,
            "total_revenue": total_revenue,
            "occupancy_rate": f"{occupancy_rate:.1f}%",
            "motorbikes": active_motorbikes,
            "cars": active_cars
        }

    # SORTING ALGORITHM: Quick Sort partitioning logs from highest fee revenue down to lowest
    def quick_sort_revenue(self, array):
        if len(array) <= 1:
            return array
        pivot = array[len(array) // 2]
        left = [x for x in array if x["fee"] > pivot["fee"]]
        middle = [x for x in array if x["fee"] == pivot["fee"]]
        right = [x for x in array if x["fee"] < pivot["fee"]]
        return self.quick_sort_revenue(left) + middle + self.quick_sort_revenue(right)

    def get_sorted_history(self):
        self.parking_history = self.load_history()
        return self.quick_sort_revenue(list(self.parking_history))