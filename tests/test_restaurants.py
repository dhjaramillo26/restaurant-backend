import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app, db


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_create_restaurant(client):
    resp = client.post('/restaurants', json={
        "name": "Mi Restaurante",
        "description": "Comida colombiana",
        "address": "Calle 123",
        "city": "Bogotá",
        "image_url": "http://example.com/foto.jpg"
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Mi Restaurante"

def test_list_restaurants(client):
    client.post('/restaurants', json={
        "name": "Rápido",
        "description": "Fast food",
        "address": "Avenida 1",
        "city": "Medellín",
        "image_url": "http://example.com/foto2.jpg"
    })
    resp = client.get('/restaurants')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_list_restaurants_with_filters(client):
    client.post('/restaurants', json={
        "name": "Azulito",
        "description": "Restaurante azul",
        "address": "Cra 10",
        "city": "Cali",
        "image_url": "img.jpg"
    })
    # Filtro por letra
    resp = client.get('/restaurants?letra=A')
    data = resp.get_json()
    assert resp.status_code == 200
    assert all(r["name"].startswith("A") for r in data)
    # Filtro por ciudad
    resp = client.get('/restaurants?ciudad=Cali')
    data = resp.get_json()
    assert resp.status_code == 200
    assert all(r["city"] == "Cali" for r in data)

def test_filter_invalid(client):
    resp = client.get('/restaurants?filtro=noexiste')
    assert resp.status_code == 400
    assert "Filtro no soportado" in resp.get_json()["error"]

def test_update_restaurant(client):
    client.post('/restaurants', json={
        "name": "UpdateMe",
        "description": "Desc",
        "address": "Cra 2",
        "city": "Barranquilla",
        "image_url": "img.jpg"
    })
    resp = client.put('/restaurants/1', json={"name": "Nuevo Nombre"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "Nuevo Nombre"

def test_update_restaurant_not_found(client):
    resp = client.put('/restaurants/999', json={"name": "No existe"})
    assert resp.status_code == 404
    assert "Restaurante no encontrado" in resp.get_json()["error"]

def test_delete_restaurant(client):
    client.post('/restaurants', json={
        "name": "DeleteMe",
        "description": "Desc",
        "address": "Cra 3",
        "city": "Cartagena",
        "image_url": "img.jpg"
    })
    resp = client.delete('/restaurants/1')
    assert resp.status_code == 200
    assert resp.get_json()["message"] == "Restaurante eliminado"

def test_delete_restaurant_not_found(client):
    resp = client.delete('/restaurants/999')
    assert resp.status_code == 404
    assert "Restaurante no encontrado" in resp.get_json()["error"]

def test_create_restaurant_invalid(client):
    resp = client.post('/restaurants', json={
        "description": "Sin nombre",
        "address": "Calle 123"
    })
    assert resp.status_code == 400
    assert "name" in resp.get_json()["error"]
