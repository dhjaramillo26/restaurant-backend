"""Database models used by the API."""

from .extensions import db

class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.String(200))
    city = db.Column(db.String(50))
    image_url = db.Column(db.String(300))
    reservations = db.relationship('Reservation', backref='restaurant', lazy=True)

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)  # formato YYYY-MM-DD
    table_number = db.Column(db.Integer, nullable=False) 
    created_at = db.Column(db.DateTime, server_default=db.func.now())
