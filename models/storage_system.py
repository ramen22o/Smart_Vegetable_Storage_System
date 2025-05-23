from models.storage_bin import StorageBin
from models.vegetable import Vegetable
import math
from datetime import datetime
import platform
from collections import deque

# Safety thresholds
MAX_SAFE_TEMP = 15   # °C - Above this is risky
MAX_SAFE_HUMIDITY = 98  # % RH - Above this causes condensation

# Windows notification imports
try:
    if platform.system() == "Windows":
        from plyer import notification
        NOTIFICATIONS_AVAILABLE = True
    else:
        NOTIFICATIONS_AVAILABLE = False
        print("Warning: Windows notifications not available on this platform")
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    print("Warning: plyer library not installed. Install with: pip install plyer")


class StorageSystem:
    def __init__(self):
        self.bins = {}
        # For KNN recommendations
        self.vegetable_profiles = {
            'Tomato': {'optimal_temp': 12, 'optimal_humidity': 85, 'shelf_life': 7},
            'Lettuce': {'optimal_temp': 2, 'optimal_humidity': 95, 'shelf_life': 10},
            'Carrot': {'optimal_temp': 0, 'optimal_humidity': 98, 'shelf_life': 21},
            'Potato': {'optimal_temp': 7, 'optimal_humidity': 90, 'shelf_life': 30},
            'Broccoli': {'optimal_temp': 0, 'optimal_humidity': 95, 'shelf_life': 14}
        }

    def create_bin(self, bin_id, max_capacity, temp, humidity):
        if bin_id in self.bins:
            print(f"❌ Error: Bin {bin_id} already exists!")
            return False
        if not self._is_environment_safe(temp, humidity):
            print(f"🚫 FAILED TO CREATE BIN {bin_id}")
            print(f"   Unsafe Conditions:")
            print(f"   Temperature: {temp}°C | Max Safe: {MAX_SAFE_TEMP}°C")
            print(f"   Humidity: {humidity}% RH | Max Safe: {MAX_SAFE_HUMIDITY}% RH")
            print(f"   Bins must meet both temperature and humidity safety thresholds.")
            return False

        # Environment is safe, proceed with bin creation
        self.bins[bin_id] = StorageBin(bin_id, max_capacity, temp, humidity)
        print(f"✅ Successfully created bin {bin_id}")
        print(f"   Temp: {temp}°C | Humidity: {humidity}% RH | Capacity: {max_capacity} units")
        return True

    def _is_environment_safe(self, temp, humidity):
        """Check if the environment is within safe storage conditions"""
        return temp <= MAX_SAFE_TEMP and humidity <= MAX_SAFE_HUMIDITY

    def get_current_capacity(self, bin_id):
        """Calculate total quantity of all vegetables in the bin"""
        if bin_id not in self.bins:
            return 0
        return sum(veg.quantity for veg in self.bins[bin_id].get_all_vegetables())

    def add_vegetable_to_bin(self, bin_id, vegetable):
        if bin_id not in self.bins:
            print(f"❌ Error: Bin {bin_id} does not exist!")
            return False
        bin_obj = self.bins[bin_id]
        current_capacity = self.get_current_capacity(bin_id)

        # Reject and delete if adding this vegetable would exceed capacity
        if current_capacity + vegetable.quantity > bin_obj.max_capacity:
            print(f"🚫 REJECTED: Cannot add {vegetable.name} (Qty: {vegetable.quantity}) to bin {bin_id}")
            print(f"   Reason: Would exceed capacity ({current_capacity + vegetable.quantity} > {bin_obj.max_capacity})")
            print(f"   Current capacity: {current_capacity}/{bin_obj.max_capacity}")

            # Optional notification
            if NOTIFICATIONS_AVAILABLE:
                try:
                    notification.notify(
                        title=f"Storage Bin {bin_id} - Item Rejected",
                        message=f"Cannot add {vegetable.name} (Qty: {vegetable.quantity})\n"
                                f"Bin is full: {current_capacity}/{bin_obj.max_capacity}",
                        app_name="Vegetable Storage System",
                        timeout=8
                    )
                except Exception:
                    pass

            return False

        # Add vegetable normally
        success = bin_obj.add_vegetable(vegetable)
        if success:
            new_capacity = self.get_current_capacity(bin_id)
            print(f"✅ Successfully added {vegetable.name} (Qty: {vegetable.quantity}) to bin {bin_id}")
            print(f"   Bin capacity: {new_capacity}/{bin_obj.max_capacity}")
        return success

    def remove_vegetable_from_bin(self, bin_id, name):
        if bin_id in self.bins:
            success = self.bins[bin_id].remove_vegetable(name)
            if success:
                print(f"✅ Removed {name} from bin {bin_id}")
            return success
        return False

    def get_bin_status(self, bin_id):
        """Get detailed status of a bin"""
        if bin_id not in self.bins:
            return None
        bin_obj = self.bins[bin_id]
        current_capacity = self.get_current_capacity(bin_id)
        status = {
            'bin_id': bin_id,
            'current_capacity': current_capacity,
            'max_capacity': bin_obj.max_capacity,
            'available_capacity': bin_obj.max_capacity - current_capacity,
            'vegetable_count': len(bin_obj.get_all_vegetables()),
            'at_capacity': current_capacity >= bin_obj.max_capacity
        }
        return status

    def print_bin_status(self, bin_id):
        """Print formatted bin status"""
        status = self.get_bin_status(bin_id)
        if not status:
            print(f"❌ Bin {bin_id} not found!")
            return
        print(f"\n📊 BIN STATUS - {bin_id}")
        print(f"Current Capacity: {status['current_capacity']}/{status['max_capacity']} units")
        print(f"Available Space: {status['available_capacity']} units")
        print(f"Vegetable Items: {status['vegetable_count']} different vegetables")
        print(f"Status: {'🚫 AT CAPACITY' if status['at_capacity'] else '✅ Available'}")

    def get_bin_contents(self, bin_id, sort_by_freshness=False):
        if bin_id not in self.bins:
            return []
        vegetables = self.bins[bin_id].get_all_vegetables()
        if sort_by_freshness:
            return self.quicksort_by_freshness(vegetables)
        return vegetables

    def recommend_storage_conditions(self, vegetable_name):
        if vegetable_name in self.vegetable_profiles:
            return self.vegetable_profiles[vegetable_name]
        similarities = []
        for name, profile in self.vegetable_profiles.items():
            similarity = self._calculate_name_similarity(vegetable_name, name)
            similarities.append((similarity, name, profile))
        similarities.sort(reverse=True, key=lambda x: x[0])
        top_3 = similarities[:3]
        if not top_3:
            return {'optimal_temp': 4, 'optimal_humidity': 90, 'shelf_life': 14}
        total_similarity = sum(sim[0] for sim in top_3)
        avg_temp = sum(sim[0] * sim[2]['optimal_temp'] for sim in top_3) / total_similarity
        avg_humid = sum(sim[0] * sim[2]['optimal_humidity'] for sim in top_3) / total_similarity
        avg_shelf_life = sum(sim[0] * sim[2]['shelf_life'] for sim in top_3) / total_similarity
        return {
            'optimal_temp': round(avg_temp, 1),
            'optimal_humidity': round(avg_humid, 1),
            'shelf_life': round(avg_shelf_life, 1)
        }

    def quicksort_by_freshness(self, vegetables):
        if len(vegetables) <= 1:
            return vegetables
        pivot = vegetables[len(vegetables) // 2]
        left = [x for x in vegetables if x.days_until_expiry() < pivot.days_until_expiry()]
        middle = [x for x in vegetables if x.days_until_expiry() == pivot.days_until_expiry()]
        right = [x for x in vegetables if x.days_until_expiry() > pivot.days_until_expiry()]
        return self.quicksort_by_freshness(left) + middle + self.quicksort_by_freshness(right)

    def _calculate_name_similarity(self, name1, name2):
        set1 = set(name1.lower())
        set2 = set(name2.lower())
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        return len(intersection) / len(union) if union else 0

    def get_all_bin_ids(self):
        return list(self.bins.keys())