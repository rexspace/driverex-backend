from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db, engine
from auth import hash_password, verify_password, create_access_token, verify_token
import models

# Create all database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic schemas — define what data looks like coming in
class CarCreate(BaseModel):
    name: str
    type: str
    seats: int
    price: int
    rating: float
    trips: int
    emoji: str
    badge: str
    image_url: str = None

class BookingCreate(BaseModel):
    car_id: int
    customer_name: str
    customer_email: str
    pickup_date: str
    return_date: str
    total_price: int

# ─── CAR ENDPOINTS ───────────────────────────────────────

@app.get("/")
def home():
    return {"message": "Welcome to DriveRex API!"}

@app.get("/cars")
def get_cars(db: Session = Depends(get_db)):
    cars = db.query(models.Car).all()
    return cars

@app.get("/cars/{car_id}")
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car

@app.post("/cars")
def create_car(car: CarCreate, db: Session = Depends(get_db)):
    new_car = models.Car(**car.dict())
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car

@app.delete("/cars/{car_id}")
def delete_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    db.delete(car)
    db.commit()
    return {"message": "Car deleted"}

# ─── BOOKING ENDPOINTS ───────────────────────────────────

@app.get("/bookings")
def get_bookings(db: Session = Depends(get_db)):
    bookings = db.query(models.Booking).all()
    return bookings

@app.post("/bookings")
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    new_booking = models.Booking(**booking.dict())
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

# ─── AUTH ENDPOINTS ──────────────────────────────────────

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password before saving
    hashed = hash_password(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Account created successfully", "name": new_user.name}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Find user by email
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check password
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create and return token
    token = create_access_token({"sub": db_user.email, "name": db_user.name})
    return {
        "token": token,
        "name": db_user.name,
        "email": db_user.email
    }

@app.get("/me")
def get_me(token: str, db: Session = Depends(get_db)):
    email = verify_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).filter(models.User.email == email).first()
    return {"name": user.name, "email": user.email}

@app.get("/admin/stats")
def get_stats(db: Session = Depends(get_db)):
    total_cars = db.query(models.Car).count()
    total_bookings = db.query(models.Booking).count()
    total_users = db.query(models.User).count()
    bookings = db.query(models.Booking).all()
    total_revenue = sum(b.total_price for b in bookings)
    return {
        "total_cars": total_cars,
        "total_bookings": total_bookings,
        "total_users": total_users,
        "total_revenue": total_revenue,
    }

@app.get("/admin/bookings")
def get_all_bookings(db: Session = Depends(get_db)):
    bookings = db.query(models.Booking).all()
    result = []
    for b in bookings:
        car = db.query(models.Car).filter(models.Car.id == b.car_id).first()
        result.append({
            "id": b.id,
            "customer_name": b.customer_name,
            "customer_email": b.customer_email,
            "car_name": car.name if car else "Unknown",
            "car_emoji": car.emoji if car else "🚗",
            "pickup_date": b.pickup_date,
            "return_date": b.return_date,
            "total_price": b.total_price,
            "status": b.status,
        })
    return result

@app.put("/cars/{car_id}")
def update_car(car_id: int, car: CarCreate, db: Session = Depends(get_db)):
    db_car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    db_car.name = car.name
    db_car.type = car.type
    db_car.seats = car.seats
    db_car.price = car.price
    db_car.rating = car.rating
    db_car.trips = car.trips
    db_car.emoji = car.emoji
    db_car.badge = car.badge
    db_car.image_url = car.image_url
    db.commit()
    db.refresh(db_car)
    return db_car