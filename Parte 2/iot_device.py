class IoTDevice:
    def __init__(self, device_id):
        self.device_id = device_id
        self.data = 0

    def generate_data(self):
        # Emulate data generation
        self.data += 1
        return f"Device {self.device_id} - Data: {self.data}"
