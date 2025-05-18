from datetime import datetime

class Vegetable:
    def __init__(self, name, quantity, temp, humidity, expiry_date):
        self.name = name
        self.quantity = quantity
        self.temp = temp
        self.humidity = humidity
        self.expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
        self.added_date = datetime.now().date()
    
    def days_until_expiry(self):
        return (self.expiry_date - datetime.now().date()).days
    
    def __str__(self):
        return f"{self.name} (Qty: {self.quantity}, Expires in {self.days_until_expiry()} days)"