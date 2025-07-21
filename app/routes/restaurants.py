from flask import Blueprint, request, jsonify, abort
from app.models import Restaurant
from app.schemas import RestaurantSchema
from app.extensions import db
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

restaurants_bp = Blueprint('restaurants', __name__, url_prefix='/restaurants')

# LISTAR (con filtros)
@restaurants_bp.route('', methods=['GET'])
def list_restaurants():
    allowed_filters = ['letra', 'ciudad']
    for key in request.args.keys():
        if key not in allowed_filters:
            abort(400, description=f"Filtro no soportado: {key}")

    letra = request.args.get('letra')
    ciudad = request.args.get('ciudad')
    query = Restaurant.query
    if letra:
        query = query.filter(Restaurant.name.startswith(letra))
    if ciudad:
        query = query.filter(Restaurant.city == ciudad)
    try:
        restaurants = query.all()
        schema = RestaurantSchema(many=True)
        return jsonify(schema.dump(restaurants)), 200
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        abort(500, description="Error al listar los restaurantes. Detalle: " + str(e))

# CREAR
@restaurants_bp.route('', methods=['POST'])
def create_restaurant():
    try:
        data = request.json
        schema = RestaurantSchema()
        restaurant = schema.load(data, session=db.session)
        db.session.add(restaurant)
        db.session.commit()
        return schema.dump(restaurant), 201
    except ValidationError as err:
        abort(400, description=err.messages)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        abort(500, description=f"Error al crear el restaurante. Detalle: {str(e)}")

# ACTUALIZAR
@restaurants_bp.route('/<int:restaurant_id>', methods=['PUT'])
def update_restaurant(restaurant_id):
    try:
        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant:
            abort(404, description="Restaurante no encontrado")
        data = request.json
        for field in ['name', 'description', 'address', 'city', 'image_url']:
            if field in data:
                setattr(restaurant, field, data[field])
        db.session.commit()
        schema = RestaurantSchema()
        return schema.dump(restaurant), 200
    except ValidationError as err:
        abort(400, description=err.messages)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        abort(500, description=f"Error al actualizar el restaurante. Detalle: {str(e)}")

# ELIMINAR
@restaurants_bp.route('/<int:restaurant_id>', methods=['DELETE'])
def delete_restaurant(restaurant_id):
    try:
        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant:
            abort(404, description="Restaurante no encontrado")
        db.session.delete(restaurant)
        db.session.commit()
        return {"message": "Restaurante eliminado"}, 200
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        abort(500, description=f"Error al eliminar el restaurante. Detalle: {str(e)}")
