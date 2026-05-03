from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db, engine
from auth import hash_password, verify_password, create_access_token, verify_token
import models
import resend
import os
import secrets

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

resend.api_key = os.getenv("RESEND_API_KEY")

def send_verification_email(email: str, name: str, token: str):
    verification_url = f"https://driverex-backend.onrender.com/verify-email?token={token}"
    resend.Emails.send({
        "from": "DriveRex <onboarding@resend.dev>",
        "to": email,
        "subject": "Verify your DriveRex account",
        "html": f"""
        <div style="font-family: sans-serif; max-width: 500px; margin: 0 auto; padding: 40px;">
            <h1 style="color: #0a0a0a;">Welcome to Drive<span style="color: #2563eb;">Rex</span>, {name}! 🎉</h1>
            <p style="color: #6b7280; font-size: 16px; line-height: 1.6;">
                You're almost ready to start renting premium cars. 
                Just click the button below to verify your email address.
            </p>
            <a href="{verification_url}" 
               style="display: inline-block; background: #2563eb; color: white; 
                      padding: 14px 28px; border-radius: 10px; text-decoration: none; 
                      font-weight: 600; font-size: 15px; margin: 24px 0;">
                Verify my email →
            </a>
            <p style="color: #9ca3af; font-size: 13px;">
                If you didn't create a DriveRex account, ignore this email.
            </p>
            <hr style="border: none; border-top: 1px solid #f0f0f0; margin: 24px 0;">
            <p style="color: #9ca3af; font-size: 12px;">© 2026 DriveRex. Made in Nigeria 🇳🇬</p>
        </div>
        """
    })

class CarCreate(BaseModel):
    name: str
    type: str
    seats: int
    price: int
    rating: float
    trips: int
    emoji: str
    badge: str
    image_url: Optional[str] = None

class BookingCreate(BaseModel):
    car_id: int
    customer_name: str
    customer_email: str
    pickup_date: str
    return_date: str
    total_price: int

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

@app.get("/")
def home():
    return {"message": "Welcome to DriveRex API!"}

@app.get("/cars")
def get_cars(db: Session = Depends(get_db)):
    return db.query(models.Car).all()

@app.get("/cars/{car_id}")
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car

@app.post("/cars")
def create_car(car: CarCreate, db: Session = Depends(get_db)):
    new_car = models.Car(
        name=car.name,
        type=car.type,
        seats=car.seats,
        price=car.price,
        rating=car.rating,
        trips=car.trips,
        emoji=car.emoji,
        badge=car.badge,
        image_url=car.image_url,
    )
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

@app.put("/cars/{car_id}")
def update_car(car_id: int, car: CarCreate, db: Session = Depends(get_db)):
    db_car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not db_car:
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

@app.get("/bookings")
def get_bookings(db: Session = Depends(get_db)):
    return db.query(models.Booking).all()

@app.post("/bookings")
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    new_booking = models.Booking(
        car_id=booking.car_id,
        customer_name=booking.customer_name,
        customer_email=booking.customer_email,
        pickup_date=booking.pickup_date,
        return_date=booking.return_date,
        total_price=booking.total_price,
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

    #@app.post("/signup")
    #def signup(user: UserCreate, db: Session = Depends(get_db)):
        #existing = db.query(models.User).filter(models.User.email == user.email).first()
        #if existing:
        #    raise HTTPException(status_code=400, detail="Email already registered")
        #hashed = hash_password(user.password)
        #token = secrets.token_urlsafe(32)
        #new_user = models.User(
         #   name=user.name,
          #  email=user.email,
           # hashed_password=hashed,
            #is_verified=True,
            #verification_token=token,)
        #db.add(new_user)
        #db.commit()
        #db.refresh(new_user)
    
    # Send email in background - don't let it crash signup
    try:
        if os.getenv("RESEND_API_KEY"):
            send_verification_email(user.email, user.name, token)
    except Exception as e:
        print(f"Email sending failed: {e}")
        # Continue anyway - user account is created
    
    return {
        "message": "Account created! Please check your email to verify.", 
        "name": new_user.name,
        "token": token  # temporary - for testing
    }
@app.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    user.is_verified = True
    user.verification_token = None
    db.commit()
    return {"message": "Email verified successfully! You can now login."}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not db_user.is_verified:
        raise HTTPException(status_code=401, detail="Please verify your email before logging in")
    token = create_access_token({"sub": db_user.email, "name": db_user.name})
    return {"token": token, "name": db_user.name, "email": db_user.email}

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