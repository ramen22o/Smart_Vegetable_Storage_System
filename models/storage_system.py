from models.storage_bin import StorageBin
from models.vegetable import Vegetable
from collections import deque
import math
from datetime import datetime

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
    
    # Existing methods
    def create_bin(self, bin_id, max_capacity, temp, humidity):
        if bin_id in self.bins:
            return False
        self.bins[bin_id] = StorageBin(bin_id, max_capacity, temp, humidity)
        return True

    # Modified with FIFO implementation
    def add_vegetable_to_bin(self, bin_id, vegetable):
        if bin_id not in self.bins:
            return False
        
        bin = self.bins[bin_id]
        if len(bin.get_all_vegetables()) >= bin.max_capacity:
            # FIFO removal - get and remove the oldest vegetable
            oldest = None
            for veg in bin.get_all_vegetables():
                if oldest is None or veg.added_date < oldest.added_date:
                    oldest = veg
            if oldest:
                bin.remove_vegetable(oldest.name)
        
        return bin.add_vegetable(vegetable)

    def remove_vegetable_from_bin(self, bin_id, name):
        if bin_id in self.bins:
            return self.bins[bin_id].remove_vegetable(name)
        return False

    # Modified with QuickSort implementation
    def get_bin_contents(self, bin_id, sort_by_freshness=False):
        if bin_id not in self.bins:
            return []
        
        vegetables = self.bins[bin_id].get_all_vegetables()
        if sort_by_freshness:
            return self.quicksort_by_freshness(vegetables)
        return vegetables

    # KNN implementation for storage recommendations
    def recommend_storage_conditions(self, vegetable_name):
        if vegetable_name in self.vegetable_profiles:
            return self.vegetable_profiles[vegetable_name]
        
        # Find 3 most similar vegetables (KNN with k=3)
        similarities = []
        for name, profile in self.vegetable_profiles.items():
            # In a real implementation, we'd use actual vegetable features
            # For now, we'll use a simple name similarity (placeholder)
            similarity = self._calculate_name_similarity(vegetable_name, name)
            similarities.append((similarity, name, profile))
        
        # Sort by similarity and get top 3
        similarities.sort(reverse=True, key=lambda x: x[0])
        top_3 = similarities[:3]
        
        if not top_3:
            return {'optimal_temp': 4, 'optimal_humidity': 90, 'shelf_life': 14}  # Default
        
        # Calculate weighted averages based on similarity
        total_similarity = sum(sim[0] for sim in top_3)
        avg_temp = sum(sim[0] * sim[2]['optimal_temp'] for sim in top_3) / total_similarity
        avg_humid = sum(sim[0] * sim[2]['optimal_humidity'] for sim in top_3) / total_similarity
        avg_shelf_life = sum(sim[0] * sim[2]['shelf_life'] for sim in top_3) / total_similarity
        
        return {
            'optimal_temp': round(avg_temp, 1),
            'optimal_humidity': round(avg_humid, 1),
            'shelf_life': round(avg_shelf_life, 1)
        }

    # QuickSort implementation for sorting by freshness
    def quicksort_by_freshness(self, vegetables):
        if len(vegetables) <= 1:
            return vegetables
        
        pivot = vegetables[len(vegetables) // 2]
        left = [x for x in vegetables if x.days_until_expiry() < pivot.days_until_expiry()]
        middle = [x for x in vegetables if x.days_until_expiry() == pivot.days_until_expiry()]
        right = [x for x in vegetables if x.days_until_expiry() > pivot.days_until_expiry()]
        
        return self.quicksort_by_freshness(left) + middle + self.quicksort_by_freshness(right)

    # Helper methods
    def _calculate_name_similarity(self, name1, name2):
        """Simple similarity measure between two vegetable names (placeholder)"""
        set1 = set(name1.lower())
        set2 = set(name2.lower())
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        return len(intersection) / len(union) if union else 0

    def get_all_bin_ids(self):
        return list(self.bins.keys())