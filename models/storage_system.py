from models.storage_bin import StorageBin
from models.vegetable import Vegetable

class StorageSystem:
    def __init__(self):
        self.bins = {}

    def create_bin(self, bin_id, max_capacity, temp, humidity):
        if bin_id in self.bins:
            return False
        self.bins[bin_id] = StorageBin(bin_id, max_capacity, temp, humidity)
        return True

    def add_vegetable_to_bin(self, bin_id, vegetable):
        if bin_id in self.bins:
            return self.bins[bin_id].add_vegetable(vegetable)
        return False

    def remove_vegetable_from_bin(self, bin_id, name):
        if bin_id in self.bins:
            return self.bins[bin_id].remove_vegetable(name)
        return False

    def get_bin_contents(self, bin_id):
        if bin_id in self.bins:
            return self.bins[bin_id].get_all_vegetables()
        return []