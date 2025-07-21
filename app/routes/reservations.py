from flask import Blueprint, request, jsonify, abort
from app.models import Reservation, Restaurant
from app.schemas import ReservationSchema
from app.extensions import db
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException
import traceback

reservations_bp = Blueprint('reservations', __name__, url_prefix='/reservations')

# CREAR
@reservations_bp.route('', methods=['POST'])
def create_reservation():
    try:
        data = request.json
        if not data or "restaurant_id" not in data or "date" not in data or "table_number" not in data:
            abort(400, description="Debes enviar 'restaurant_id', 'date' y 'table_number'")

        restaurant_id = data['restaurant_id']
        date = data['date']
        table_number = data['table_number']

        # Validar que el restaurante exista
        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant:
            abort(400, description="El restaurante no existe")

        # Validar número de mesa
        if not isinstance(table_number, int) or not (1 <= table_number <= 15):
            abort(400, description="El número de mesa debe estar entre 1 y 15")

        # Validar que esa mesa no esté reservada ese día
        existing_reservation = Reservation.query.filter_by(
            restaurant_id=restaurant_id, date=date, table_number=table_number
        ).first()
        if existing_reservation:
            abort(400, description=f"La mesa {table_number} ya está reservada para ese restaurante en esa fecha")

        # Validar máximo 15 reservas por restaurante y día
        count_by_rest = Reservation.query.filter_by(restaurant_id=restaurant_id, date=date).count()
        if count_by_rest >= 15:
            abort(400, description="No hay más cupo en este restaurante para esa fecha")

        # Validar máximo 20 reservas globales por día
        total_by_day = Reservation.query.filter_by(date=date).count()
        if total_by_day >= 20:
            abort(400, description="No hay más cupo total para esa fecha")

        schema = ReservationSchema()
        reservation = schema.load(data, session=db.session)
        db.session.add(reservation)
        db.session.commit()
        return schema.dump(reservation), 201

    except ValidationError as err:
        abort(400, description=err.messages)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        traceback.print_exc()
        abort(500, description=f"Error al crear la reserva. Detalle: {str(e)}")

# LISTAR
@reservations_bp.route('', methods=['GET'])
def list_reservations():
    try:
        query = Reservation.query
        restaurant_id = request.args.get('restaurant_id', type=int)
        date = request.args.get('date')
        table_number = request.args.get('table_number', type=int)

        if restaurant_id is not None:
            query = query.filter_by(restaurant_id=restaurant_id)
        if date:
            query = query.filter_by(date=date)
        if table_number is not None:
            query = query.filter_by(table_number=table_number)

        reservations = query.all()
        schema = ReservationSchema(many=True)
        return jsonify(schema.dump(reservations)), 200
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        traceback.print_exc()
        abort(500, description=f"Error al listar las reservas. Detalle: {str(e)}")

# ACTUALIZAR
@reservations_bp.route('/<int:reservation_id>', methods=['PUT'])
def update_reservation(reservation_id):
    try:
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            abort(404, description="Reserva no encontrada")
        data = request.json

        if 'restaurant_id' in data:
            reservation.restaurant_id = data['restaurant_id']
        if 'date' in data:
            reservation.date = data['date']
        if 'table_number' in data:
            table_number = data['table_number']
            if not isinstance(table_number, int) or not (1 <= table_number <= 15):
                abort(400, description="El número de mesa debe estar entre 1 y 15")
            # Validar disponibilidad
            existing_reservation = Reservation.query.filter_by(
                restaurant_id=reservation.restaurant_id,
                date=reservation.date,
                table_number=table_number
            ).filter(Reservation.id != reservation.id).first()
            if existing_reservation:
                abort(400, description=f"La mesa {table_number} ya está reservada para ese restaurante en esa fecha")
            reservation.table_number = table_number

        db.session.commit()
        schema = ReservationSchema()
        return schema.dump(reservation), 200

    except ValidationError as err:
        abort(400, description=err.messages)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        traceback.print_exc()
        abort(500, description=f"Error al actualizar la reserva. Detalle: {str(e)}")

# ELIMINAR
@reservations_bp.route('/<int:reservation_id>', methods=['DELETE'])
def delete_reservation(reservation_id):
    try:
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            abort(404, description="Reserva no encontrada")
        db.session.delete(reservation)
        db.session.commit()
        return {"message": "Reserva eliminada"}, 200
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        traceback.print_exc()
        abort(500, description=f"Error al eliminar la reserva. Detalle: {str(e)}")
