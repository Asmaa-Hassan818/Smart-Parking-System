class vehicle:
    def __init__(self,plate_num,vehicle_type,vehicle_color):
        self.plate_num = plate_num
        self.vehicle_type = vehicle_type
        self.vehicle_color = vehicle_color

    def display_info(self):
        return f"""
        Vehicle Info:
       
        Plate Number : {self.plate_number}
        Type         : {self.vehicle_type}
        Color        : {self.color}
        """
