class Vegetable:
    def __init__(self, name, quantity, temperature, humidity, expiry_date):
        self.name = name
        self.quantity = quantity
        self.temperature = temperature
        self.humidity = humidity
        self.expiry_date = expiry_date

    def __str__(self):
        return f"{self.name} (Qty: {self.quantity}, Temp: {self.temperature}, Humidity: {self.humidity}, Exp: {self.expiry_date})"