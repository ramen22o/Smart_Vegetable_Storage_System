class StorageBin:
    def __init__(self, bin_id, max_capacity, temp, humidity):
        self.bin_id = bin_id
        self.max_capacity = max_capacity
        self.temp = temp
        self.humidity = humidity
        self.vegetables = []
    
    def add_vegetable(self, vegetable):
        if len(self.vegetables) >= self.max_capacity:
            return False
        self.vegetables.append(vegetable)
        return True
    
    def remove_vegetable(self, name):
        for i, veg in enumerate(self.vegetables):
            if veg.name == name:
                self.vegetables.pop(i)
                return True
        return False
    
    def get_all_vegetables(self):
        return self.vegetables.copy()