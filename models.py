from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    seats = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)
    trips = Column(Integer, default=0)
    emoji = Column(String, nullable=False)
    badge = Column(String, nullable=False)
    image_url = Column(String, nullable=True)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, nullable=False)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    pickup_date = Column(String, nullable=False)
    return_date = Column(String, nullable=False)
    total_price = Column(Integer, nullable=False)
    status = Column(String, default="pending")
    phone_number = Column(String)
    home_address = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String, default="Nigeria")

    has_license = Column(Boolean, default=False)
    license_number = Column(String, nullable=True)
    license_expiry = Column(String, nullable=True)
    license_image = Column(String, nullable=True)

    needs_driver = Column(Boolean, default=False)

    nin = Column(String, nullable=True)

    emergency_contact_name = Column(String)
    emergency_contact_phone = Column(String)

    booking_status = Column(String, default="pending")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(String, default="false")
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)