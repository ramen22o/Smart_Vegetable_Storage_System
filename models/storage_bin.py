class StorageBin:
    def __init__(self, bin_id, max_capacity, current_temperature, current_humidity):
        self.bin_id = bin_id
        self.max_capacity = max_capacity
        self.current_temperature = current_temperature
        self.current_humidity = current_humidity
        self.contents = []

    def add_vegetable(self, vegetable):
        if len(self.contents) < self.max_capacity:
            self.contents.append(vegetable)
            return True
        return False

    def remove_vegetable(self, name):
        for veg in self.contents:
            if veg.name == name:
                self.contents.remove(veg)
                return True
        return False

    def get_all_vegetables(self):
        return self.contents