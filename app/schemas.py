"""Marshmallow schemas for serializing models."""

from .extensions import ma
from .models import Restaurant, Reservation

class RestaurantSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Restaurant
        include_fk = True
        load_instance = True

class ReservationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Reservation
        include_fk = True
        load_instance = True
