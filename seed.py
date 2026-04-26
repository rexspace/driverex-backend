import requests

cars = [
    {"name": "Toyota Camry 2023", "type": "Sedan", "seats": 5, "price": 25000, "rating": 4.9, "trips": 42, "emoji": "🚙", "badge": "Popular"},
    {"name": "Toyota Prado 2022", "type": "SUV", "seats": 7, "price": 65000, "rating": 4.8, "trips": 28, "emoji": "🚐", "badge": "Premium"},
    {"name": "Mercedes C300 2023", "type": "Sedan", "seats": 5, "price": 120000, "rating": 5.0, "trips": 15, "emoji": "🏎️", "badge": "Luxury"},
    {"name": "Honda CR-V 2023", "type": "SUV", "seats": 5, "price": 45000, "rating": 4.7, "trips": 33, "emoji": "🚗", "badge": "Popular"},
    {"name": "Toyota Corolla 2022", "type": "Sedan", "seats": 5, "price": 18000, "rating": 4.6, "trips": 58, "emoji": "🚘", "badge": "Economy"},
    {"name": "BMW X5 2023", "type": "SUV", "seats": 7, "price": 150000, "rating": 5.0, "trips": 10, "emoji": "🚙", "badge": "Luxury"},
]

for car in cars:
    response = requests.post("http://localhost:8000/cars", json=car)
    print(f"Added: {car['name']} → {response.status_code}")

print("Done! All cars added to database.")