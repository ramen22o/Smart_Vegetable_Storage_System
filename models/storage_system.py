from models.storage_bin import StorageBin
from models.vegetable import Vegetable
import math
from datetime import datetime
import platform
from collections import deque

# Safety thresholds
MAX_SAFE_TEMP = 15   # °C (59°F) - Above this is risky)
MAX_SAFE_HUMIDITY = 98  # % RH - Above this causes condensation)

# Windows message box imports
try:
    if platform.system() == "Windows":
        import ctypes
        from ctypes import wintypes
        MSGBOX_AVAILABLE = True
    else:
        MSGBOX_AVAILABLE = False
        print("Warning: Windows message boxes not available on this platform")
except ImportError:
    MSGBOX_AVAILABLE = False
    print("Warning: ctypes library not available")

# Message box constants
MB_OK = 0x0
MB_ICONERROR = 0x10
MB_ICONWARNING = 0x30
MB_ICONINFORMATION = 0x40
MB_TOPMOST = 0x40000


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

    def _show_message_box(self, title, message, icon_type=MB_ICONERROR):
        """Show Windows message box popup"""
        if MSGBOX_AVAILABLE:
            try:
                # Use MessageBoxW for Unicode support
                ctypes.windll.user32.MessageBoxW(
                    None,  # Parent window handle (None = desktop)
                    message,  # Message text
                    title,  # Title
                    icon_type | MB_OK | MB_TOPMOST  # Icon + OK button + stay on top
                )
                return True
            except Exception as e:
                print(f"Message box error: {e}")
                print(f"{title}: {message}")
                return False
        else:
            print(f"{title}: {message}")
            return False

    def create_bin(self, bin_id, max_capacity, temp, humidity):
        # Check if environment exceeds safety thresholds FIRST
        if not self._is_environment_safe(temp, humidity):
            self._show_safety_alert(bin_id, temp, humidity, "create")
            print(f"🚫 FAILED TO CREATE BIN {bin_id}")
            print(f"   Unsafe Conditions:")
            print(f"   Temperature: {temp}°C ({temp * 9/5 + 32:.1f}°F) | Max Safe: {MAX_SAFE_TEMP}°C ({MAX_SAFE_TEMP * 9/5 + 32:.1f}°F)")
            print(f"   Humidity: {humidity}% RH | Max Safe: {MAX_SAFE_HUMIDITY}% RH")
            print(f"   Bins must meet both temperature and humidity safety thresholds.")
            return False
        # Then check if bin already exists
        if bin_id in self.bins:
            error_msg = f"Bin {bin_id} already exists!"
            self._show_message_box("Error", error_msg, MB_ICONERROR)
            print(f"❌ Error: {error_msg}")
            return False
        # Environment is safe and bin doesn't exist, proceed with bin creation
        self.bins[bin_id] = StorageBin(bin_id, max_capacity, temp, humidity)
        print(f"✅ Successfully created bin {bin_id}")
        print(f"   Temp: {temp}°C ({temp * 9/5 + 32:.1f}°F) | Humidity: {humidity}% RH | Capacity: {max_capacity} units")
        return True

    def _is_environment_safe(self, temp, humidity):
        """Check if the environment is within safe storage conditions"""
        return temp <= MAX_SAFE_TEMP and humidity <= MAX_SAFE_HUMIDITY

    def _show_safety_alert(self, bin_id, temp, humidity, action="create"):
        """Show Windows message box for unsafe storage conditions"""
        temp_f = temp * 9/5 + 32  # Convert to Fahrenheit
        max_temp_f = MAX_SAFE_TEMP * 9/5 + 32
        # Determine what's unsafe
        unsafe_conditions = []
        if temp > MAX_SAFE_TEMP:
            unsafe_conditions.append(f"Temperature: {temp}°C ({temp_f:.1f}°F) > {MAX_SAFE_TEMP}°C ({max_temp_f:.1f}°F)")
        if humidity > MAX_SAFE_HUMIDITY:
            unsafe_conditions.append(f"Humidity: {humidity}% > {MAX_SAFE_HUMIDITY}%")
        title = "Storage Safety Alert"
        if action == "create":
            message = f"Cannot create bin '{bin_id}' due to unsafe conditions:\n"
        elif action == "update":
            message = f"Cannot update bin '{bin_id}' due to unsafe conditions:\n"
        else:
            message = f"Unsafe storage conditions detected in bin '{bin_id}':\n"
        message += "\n".join(unsafe_conditions)
        message += "\nRisks:"
        if temp > MAX_SAFE_TEMP:
            message += "\n• High temperature accelerates spoilage"
        if humidity > MAX_SAFE_HUMIDITY:
            message += "\n• High humidity causes condensation & mold"
        # Show message box with warning icon
        self._show_message_box(title, message, MB_ICONWARNING)

    def get_current_capacity(self, bin_id):
        """Calculate total quantity of all vegetables in the bin"""
        if bin_id not in self.bins:
            return 0
        return sum(veg.quantity for veg in self.bins[bin_id].get_all_vegetables())

    def add_vegetable_to_bin(self, bin_id, vegetable):
        if bin_id not in self.bins:
            error_msg = f"Bin '{bin_id}' does not exist!"
            self._show_message_box("Error", error_msg, MB_ICONERROR)
            print(f"❌ Error: {error_msg}")
            return False
        bin_obj = self.bins[bin_id]
        current_capacity = self.get_current_capacity(bin_id)
        # Reject and show message box if adding this vegetable would exceed capacity
        if current_capacity + vegetable.quantity > bin_obj.max_capacity:
            error_msg = (f"Cannot add {vegetable.name} (Qty: {vegetable.quantity}) to bin '{bin_id}'.\n"
                        f"Reason: Would exceed capacity\n"
                        f"Current: {current_capacity}/{bin_obj.max_capacity}\n"
                        f"After adding: {current_capacity + vegetable.quantity}/{bin_obj.max_capacity}")
            self._show_message_box("Storage Bin Full", error_msg, MB_ICONWARNING)
            print(f"🚫 REJECTED: Cannot add {vegetable.name} (Qty: {vegetable.quantity}) to bin {bin_id}")
            print(f"   Reason: Would exceed capacity ({current_capacity + vegetable.quantity} > {bin_obj.max_capacity})")
            print(f"   Current capacity: {current_capacity}/{bin_obj.max_capacity}")
            return False
        # Add vegetable normally
        success = bin_obj.add_vegetable(vegetable)
        if success:
            new_capacity = self.get_current_capacity(bin_id)
            print(f"✅ Successfully added {vegetable.name} (Qty: {vegetable.quantity}) to bin {bin_id}")
            print(f"   Bin capacity: {new_capacity}/{bin_obj.max_capacity}")
            # Auto-sort vegetables by expiration date after adding
            self._auto_sort_bin_by_expiration(bin_id)
            # Check for expired vegetables after adding and sorting
            self._check_fifo_warnings(bin_id)
        return success

    def _auto_remove_expired_vegetables(self, bin_id):
        """Automatically remove all vegetables with 0 or fewer days until expiry."""
        if bin_id not in self.bins:
            return []

        bin_obj = self.bins[bin_id]
        vegetables = list(bin_obj.get_all_vegetables())  # Copy list to avoid iteration issues
        removed_list = []

        for veg in vegetables:
            if veg.days_until_expiry() <= 0:
                removed_list.append({
                    'name': veg.name,
                    'quantity': veg.quantity
                })
                bin_obj.remove_vegetable(veg.name)

        if removed_list:
            print(f"🗑️ Auto-removed {len(removed_list)} expired vegetable(s) from bin '{bin_id}':")
            for item in removed_list:
                print(f"   • {item['name']} (Qty: {item['quantity']})")

        return removed_list

    def _auto_sort_bin_by_expiration(self, bin_id):
        """Automatically sort vegetables in bin by expiration date (FIFO order)"""
        if bin_id not in self.bins:
            return
        vegetables = self.bins[bin_id].get_all_vegetables()
        if len(vegetables) <= 1:
            return
        # Sort using quicksort by expiration date (soonest expiry first)
        sorted_vegetables = self.quicksort_by_expiration(vegetables)
        # Update the bin's vegetable list with sorted order
        self.bins[bin_id].vegetables = sorted_vegetables
        print(f"📋 Auto-sorted vegetables in bin {bin_id} by expiration date (FIFO order)")

    def quicksort_by_expiration(self, vegetables):
        """
        Quicksort vegetables by expiration date (soonest expiry first for FIFO)
        """
        if len(vegetables) <= 1:
            return vegetables
        pivot = vegetables[len(vegetables) // 2]
        pivot_days = pivot.days_until_expiry()
        left = [x for x in vegetables if x.days_until_expiry() < pivot_days]
        middle = [x for x in vegetables if x.days_until_expiry() == pivot_days]
        right = [x for x in vegetables if x.days_until_expiry() > pivot_days]
        return self.quicksort_by_expiration(left) + middle + self.quicksort_by_expiration(right)

    def _check_fifo_warnings(self, bin_id, show_warning=True):
        """Check for vegetables expiring today (0 days) and show FIFO warnings"""
        if bin_id not in self.bins:
            return

        # Auto-remove expired vegetables before checking
        removed_items = self._auto_remove_expired_vegetables(bin_id)
        vegetables = self.bins[bin_id].get_all_vegetables()

        expiring_today = []
        expiring_soon = []  # 1-2 days

        for veg in vegetables:
            days_left = veg.days_until_expiry()
            if days_left <= 0:
                expiring_today.append(veg)
            elif days_left <= 2:
                expiring_soon.append(veg)

        # Notify user about removed veggies
        if removed_items and show_warning:
            removal_message = "The following vegetables were auto-removed because they expired:\n\n"
            for item in removed_items:
                removal_message += f"• {item['name']} - Qty: {item['quantity']}\n"
            self._show_message_box("Expired Vegetables Removed", removal_message, MB_ICONWARNING)

        # Show critical warning for vegetables expiring today
        if expiring_today and show_warning:
            self._show_fifo_critical_warning(bin_id, expiring_today)

        # Show advisory warning for vegetables expiring soon
        if expiring_soon and show_warning:
            self._show_fifo_advisory_warning(bin_id, expiring_soon)

    def _show_fifo_critical_warning(self, bin_id, expiring_vegetables):
        """Show critical FIFO warning for vegetables expiring today"""
        if not expiring_vegetables:
            return
        title = "🚨 CRITICAL: Vegetables Expiring TODAY!"
        message = f"FIFO Alert - Bin '{bin_id}'\n"
        message += "The following vegetables are expiring TODAY (0 days left):\n"
        for veg in expiring_vegetables:
            days_left = veg.days_until_expiry()
            message += f"• {veg.name} (Qty: {veg.quantity}) - EXPIRED/EXPIRING TODAY\n"
        message += "\n⚠️ FIFO ACTION REQUIRED:\n"
        message += "• Use these vegetables IMMEDIATELY\n"
        message += "• Remove if already spoiled\n"
        message += "• Check quality before consumption\n"
        message += "\nFollowing FIFO principle: Use oldest items first!"
        self._show_message_box(title, message, MB_ICONERROR)
        # Also print to console
        print(f"\n🚨 CRITICAL FIFO WARNING - Bin {bin_id}:")
        for veg in expiring_vegetables:
            print(f"   • {veg.name} (Qty: {veg.quantity}) - EXPIRING TODAY!")

    def _show_fifo_advisory_warning(self, bin_id, expiring_vegetables):
        """Show advisory FIFO warning for vegetables expiring soon"""
        if not expiring_vegetables:
            return
        title = "⚠️ FIFO Advisory: Vegetables Expiring Soon"
        message = f"FIFO Alert - Bin '{bin_id}'\n"
        message += "The following vegetables are expiring soon:\n"
        for veg in expiring_vegetables:
            days_left = veg.days_until_expiry()
            message += f"• {veg.name} (Qty: {veg.quantity}) - {days_left} day(s) left\n"
        message += "\n📋 FIFO RECOMMENDATION:\n"
        message += "• Plan to use these vegetables next\n"
        message += "• Prioritize in meal planning\n"
        message += "• Monitor daily for freshness\n"
        message += "\nFollowing FIFO: First In, First Out!"
        self._show_message_box(title, message, MB_ICONWARNING)

    def get_fifo_order_display(self, bin_id):
        """Get vegetables in FIFO order for dashboard display"""
        if bin_id not in self.bins:
            return []
        vegetables = self.bins[bin_id].get_all_vegetables()
        self._check_fifo_warnings(bin_id, show_warning=True)  # Show warning only when viewing
        sorted_vegetables = self.quicksort_by_expiration(vegetables)
        fifo_display = []
        for i, veg in enumerate(sorted_vegetables):
            days_left = veg.days_until_expiry()
            status = "🚨 CRITICAL" if days_left <= 0 else "⚠️ SOON" if days_left <= 2 else "✅ OK"
            fifo_display.append({
                'fifo_position': i + 1,
                'name': veg.name,
                'quantity': veg.quantity,
                'days_until_expiry': days_left,
                'expiry_date': veg.expiry_date,
                'status': status,
                'use_priority': 'HIGH' if days_left <= 0 else 'MEDIUM' if days_left <= 2 else 'NORMAL'
            })
        return fifo_display

    def print_fifo_order(self, bin_id):
        """Print FIFO order for a specific bin"""
        self._check_fifo_warnings(bin_id, show_warning=True)  # Show warning only when viewing
        fifo_order = self.get_fifo_order_display(bin_id)
        if not fifo_order:
            print(f"📋 Bin '{bin_id}' is empty or does not exist")
            return
        print(f"\n📋 FIFO ORDER - Bin '{bin_id}' (Use in this order):")
        print("=" * 60)
        for item in fifo_order:
            print(f"{item['fifo_position']:2d}. {item['name']} (Qty: {item['quantity']}) - "
                  f"{item['days_until_expiry']} days left {item['status']}")
        print("=" * 60)
        print("FIFO Rule: Use items with fewer days remaining first!")

    def check_all_bins_fifo_status(self):
        """Check FIFO status across all bins and show warnings"""
        total_critical = 0
        total_advisory = 0
        print(f"\n🔍 CHECKING FIFO STATUS ACROSS ALL BINS...")
        for bin_id in self.bins.keys():
            vegetables = self.bins[bin_id].get_all_vegetables()
            if not vegetables:
                continue
            expiring_today = [v for v in vegetables if v.days_until_expiry() <= 0]
            expiring_soon = [v for v in vegetables if 0 < v.days_until_expiry() <= 2]
            if expiring_today:
                total_critical += len(expiring_today)
                self._check_fifo_warnings(bin_id, show_warning=False)  # Already handled
            if expiring_soon:
                total_advisory += len(expiring_soon)
        # Summary
        print(f"\n📊 FIFO STATUS SUMMARY:")
        print(f"   🚨 Critical (expiring today): {total_critical} items")
        print(f"   ⚠️  Advisory (expiring soon): {total_advisory} items")
        if total_critical == 0 and total_advisory == 0:
            print("   ✅ All vegetables have adequate shelf life")

    def remove_vegetable_from_bin(self, bin_id, name):
        if bin_id not in self.bins:
            error_msg = f"Bin '{bin_id}' does not exist!"
            self._show_message_box("Error", error_msg, MB_ICONERROR)
            return False
        success = self.bins[bin_id].remove_vegetable(name)
        if success:
            print(f"✅ Removed {name} from bin {bin_id}")
            # Re-sort after removal and check for warnings
            self._auto_sort_bin_by_expiration(bin_id)
            self._check_fifo_warnings(bin_id)
        else:
            error_msg = f"Vegetable '{name}' not found in bin '{bin_id}'!"
            self._show_message_box("Error", error_msg, MB_ICONWARNING)
        return success

    def take_out_vegetable_quantity(self, bin_id, vegetable_name, quantity_to_take):
        """
        Take out a specific quantity of vegetables from a bin following FIFO principle.
        Takes from the item with the earliest expiration date first.
        """
        if bin_id not in self.bins:
            error_msg = f"Bin '{bin_id}' does not exist!"
            self._show_message_box("Error", error_msg, MB_ICONERROR)
            print(f"❌ Error: {error_msg}")
            return 0
        bin_obj = self.bins[bin_id]
        vegetables = bin_obj.get_all_vegetables()
        # Sort vegetables by expiration date for FIFO
        sorted_vegetables = self.quicksort_by_expiration(vegetables)
        # Find the vegetable with earliest expiration date (FIFO principle)
        target_vegetable = None
        for veg in sorted_vegetables:
            if veg.name.lower() == vegetable_name.lower():
                target_vegetable = veg
                break
        if not target_vegetable:
            error_msg = f"Vegetable '{vegetable_name}' not found in bin '{bin_id}'!"
            self._show_message_box("Error", error_msg, MB_ICONWARNING)
            print(f"❌ Error: {error_msg}")
            return 0
        # Validate quantity
        if quantity_to_take <= 0:
            error_msg = f"Invalid quantity: {quantity_to_take}. Must be greater than 0."
            self._show_message_box("Error", error_msg, MB_ICONWARNING)
            print(f"❌ Error: {error_msg}")
            return 0
        available_quantity = target_vegetable.quantity
        actual_quantity_taken = min(quantity_to_take, available_quantity)
        # If taking all or more than available, remove the entire item
        if quantity_to_take >= available_quantity:
            success = bin_obj.remove_vegetable(vegetable_name)
            if success:
                print(f"✅ Took out all {actual_quantity_taken} units of {vegetable_name} from bin {bin_id} (FIFO)")
                print(f"   Item completely removed from bin")
                # Re-sort and check warnings after removal
                self._auto_sort_bin_by_expiration(bin_id)
                self._check_fifo_warnings(bin_id)
                return actual_quantity_taken
            else:
                error_msg = f"Failed to remove {vegetable_name} from bin '{bin_id}'!"
                self._show_message_box("Error", error_msg, MB_ICONERROR)
                return 0
        # Take out partial quantity - reduce the quantity in place
        target_vegetable.quantity -= actual_quantity_taken
        remaining_quantity = target_vegetable.quantity
        print(f"✅ Took out {actual_quantity_taken} units of {vegetable_name} from bin {bin_id} (FIFO)")
        print(f"   Remaining in bin: {remaining_quantity} units")
        # Update bin capacity info
        current_capacity = self.get_current_capacity(bin_id)
        print(f"   Bin capacity after removal: {current_capacity}/{bin_obj.max_capacity}")
        # Re-sort and check warnings after partial removal
        self._auto_sort_bin_by_expiration(bin_id)
        self._check_fifo_warnings(bin_id)
        return actual_quantity_taken

    def get_vegetable_info_from_bin(self, bin_id, vegetable_name):
        """Get detailed information about a specific vegetable in a bin."""
        if bin_id not in self.bins:
            return None
        vegetables = self.bins[bin_id].get_all_vegetables()
        for veg in vegetables:
            if veg.name.lower() == vegetable_name.lower():
                return {
                    'name': veg.name,
                    'quantity': veg.quantity,
                    'expiry_date': veg.expiry_date,
                    'days_until_expiry': veg.days_until_expiry(),
                    'temperature': veg.temperature,
                    'humidity': veg.humidity
                }
        return None

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
        """Print formatted bin status with FIFO information"""
        status = self.get_bin_status(bin_id)
        if not status:
            error_msg = f"Bin '{bin_id}' not found!"
            self._show_message_box("Error", error_msg, MB_ICONERROR)
            print(f"❌ {error_msg}")
            return
        print(f"\n📊 BIN STATUS - {bin_id}")
        print(f"Current Capacity: {status['current_capacity']}/{status['max_capacity']} units")
        print(f"Available Space: {status['available_capacity']} units")
        print(f"Vegetable Items: {status['vegetable_count']} different vegetables")
        print(f"Status: {'🚫 AT CAPACITY' if status['at_capacity'] else '✅ Available'}")
        # Add FIFO status
        self.print_fifo_order(bin_id)

    def get_bin_contents(self, bin_id, sort_by_expiration=True, sort_by_freshness=False):
        """Get bin contents with automatic FIFO sorting by default"""
        if bin_id not in self.bins:
            return []
        vegetables = self.bins[bin_id].get_all_vegetables()
        if sort_by_expiration:
            return self.quicksort_by_expiration(vegetables)
        elif sort_by_freshness:
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
        """Keep your original freshness sorting method"""
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

    def check_bin_safety(self, bin_id):
        """Check if an existing bin's conditions are still safe"""
        if bin_id not in self.bins:
            return False
        bin_obj = self.bins[bin_id]
        temp = bin_obj.temperature
        humidity = bin_obj.humidity
        if not self._is_environment_safe(temp, humidity):
            self._show_safety_alert(bin_id, temp, humidity, "monitor")
            print(f"⚠️  SAFETY WARNING: Bin {bin_id} has unsafe conditions!")
            print(f"   Temperature: {temp}°C ({temp * 9/5 + 32:.1f}°F) | Max Safe: {MAX_SAFE_TEMP}°C ({MAX_SAFE_TEMP * 9/5 + 32:.1f}°F)")
            print(f"   Humidity: {humidity}% RH | Max Safe: {MAX_SAFE_HUMIDITY}% RH")
            return False
        return True

    def update_bin_conditions(self, bin_id, new_temp=None, new_humidity=None):
        """Update bin environmental conditions with safety checks"""
        if bin_id not in self.bins:
            error_msg = f"Bin '{bin_id}' does not exist!"
            self._show_message_box("Error", error_msg, MB_ICONERROR)
            print(f"❌ Error: {error_msg}")
            return False
        bin_obj = self.bins[bin_id]
        current_temp = bin_obj.temperature
        current_humidity = bin_obj.humidity
        # Use current values if not specified
        temp_to_check = new_temp if new_temp is not None else current_temp
        humidity_to_check = new_humidity if new_humidity is not None else current_humidity
        # Check safety before updating
        if not self._is_environment_safe(temp_to_check, humidity_to_check):
            self._show_safety_alert(bin_id, temp_to_check, humidity_to_check, "update")
            print(f"🚫 FAILED TO UPDATE BIN {bin_id}")
            print(f"   Proposed conditions are unsafe:")
            print(f"   Temperature: {temp_to_check}°C ({temp_to_check * 9/5 + 32:.1f}°F) | Max Safe: {MAX_SAFE_TEMP}°C ({MAX_SAFE_TEMP * 9/5 + 32:.1f}°F)")
            print(f"   Humidity: {humidity_to_check}% RH | Max Safe: {MAX_SAFE_HUMIDITY}% RH")
            return False
        # Update conditions
        if new_temp is not None:
            bin_obj.temperature = new_temp
        if new_humidity is not None:
            bin_obj.humidity = new_humidity
        print(f"✅ Successfully updated bin {bin_id} conditions")
        print(f"   New Temp: {bin_obj.temperature}°C ({bin_obj.temperature * 9/5 + 32:.1f}°F) | New Humidity: {bin_obj.humidity}% RH")
        return True

    def get_all_safety_violations(self):
        """Get all bins that currently violate safety thresholds"""
        violations = []
        for bin_id, bin_obj in self.bins.items():
            temp = bin_obj.temperature
            humidity = bin_obj.humidity
            if not self._is_environment_safe(temp, humidity):
                temp_f = temp * 9/5 + 32
                violation_info = {
                    'bin_id': bin_id,
                    'temperature': temp,
                    'temperature_f': round(temp_f, 1),
                    'humidity': humidity,
                    'temp_violation': temp > MAX_SAFE_TEMP,
                    'humidity_violation': humidity > MAX_SAFE_HUMIDITY,
                    'temp_excess': max(0, temp - MAX_SAFE_TEMP),
                    'humidity_excess': max(0, humidity - MAX_SAFE_HUMIDITY)
                }
                violations.append(violation_info)
        return violations

    def check_all_bins_safety(self):
        """Check safety of all bins and show message boxes for violations"""
        violations = self.get_all_safety_violations()
        if violations:
            print(f"⚠️  SAFETY ALERT: {len(violations)} bin(s) have unsafe conditions!")
            if len(violations) > 1:
                violation_summary = f"Safety violations detected in {len(violations)} bins:\n"
                for violation in violations:
                    bin_id = violation['bin_id']
                    violation_summary += f"• Bin '{bin_id}':\n"
                    if violation['temp_violation']:
                        violation_summary += f"  - Temperature: {violation['temperature']}°C ({violation['temperature_f']}°F)\n"
                    if violation['humidity_violation']:
                        violation_summary += f"  - Humidity: {violation['humidity']}%\n"
                    violation_summary += "\n"
                violation_summary += "Please check individual bins for detailed information."
                self._show_message_box("Multiple Safety Violations", violation_summary, MB_ICONWARNING)
            else:
                violation = violations[0]
                bin_id = violation['bin_id']
                temp = violation['temperature']
                humidity = violation['humidity']
                self._show_safety_alert(bin_id, temp, humidity, "monitor")
            # Print details to console
            for violation in violations:
                bin_id = violation['bin_id']
                temp = violation['temperature']
                humidity = violation['humidity']
                print(f"\n🚨 Bin {bin_id}:")
                if violation['temp_violation']:
                    print(f"   Temperature: {temp}°C ({violation['temperature_f']}°F) - EXCEEDS SAFE LIMIT by {violation['temp_excess']:.1f}°C")
                if violation['humidity_violation']:
                    print(f"   Humidity: {humidity}% RH - EXCEEDS SAFE LIMIT by {violation['humidity_excess']:.1f}%")
            return False
        else:
            print("✅ All bins are within safe storage parameters")
            return True

    def get_all_bin_ids(self):
        return list(self.bins.keys())

    def get_safety_summary(self):
        """Get a summary of safety status across all bins"""
        total_bins = len(self.bins)
        violations = self.get_all_safety_violations()
        safe_bins = total_bins - len(violations)
        summary = {
            'total_bins': total_bins,
            'safe_bins': safe_bins,
            'unsafe_bins': len(violations),
            'safety_percentage': (safe_bins / total_bins * 100) if total_bins > 0 else 100,
            'violations': violations
        }
        return summary