import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app, db
from app.models import Restaurant


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Crea un restaurante base para todas las pruebas
            rest = Restaurant(
                name="Restaurante Test",
                description="Test desc",
                address="Test addr",
                city="Test City",
                image_url="img.jpg"
            )
            db.session.add(rest)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def test_create_reservation(client):
    resp = client.post('/reservations', json={
        "restaurant_id": 1,
        "date": "2024-07-22",
        "table_number": 4
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["table_number"] == 4
    assert data["restaurant_id"] == 1

def test_create_reservation_missing_fields(client):
    resp = client.post('/reservations', json={
        "restaurant_id": 1,
        "date": "2024-07-22"
    })
    assert resp.status_code == 400
    assert "table_number" in resp.get_json()["error"]

def test_table_number_out_of_range(client):
    resp = client.post('/reservations', json={
        "restaurant_id": 1,
        "date": "2024-07-22",
        "table_number": 20
    })
    assert resp.status_code == 400
    assert "entre 1 y 15" in resp.get_json()["error"]

def test_table_taken(client):
    client.post('/reservations', json={
        "restaurant_id": 1,
        "date": "2024-07-22",
        "table_number": 5
    })
    resp = client.post('/reservations', json={
        "restaurant_id": 1,
        "date": "2024-07-22",
        "table_number": 5
    })
    assert resp.status_code == 400
    assert "ya está reservada" in resp.get_json()["error"]

def test_max_reservations_per_restaurant(client):
    for i in range(1, 16):
        client.post('/reservations', json={
            "restaurant_id": 1,
            "date": "2024-07-23",
            "table_number": i
        })
    resp = client.post('/reservations', json={
        "restaurant_id": 1,
        "date": "2024-07-23",
        "table_number": 1
    })
    assert resp.status_code == 400

def test_max_total_reservations_per_day(client):
    for i in range(1, 16):
        client.post('/reservations', json={
            "restaurant_id": 1,
            "date": "2024-07-24",
            "table_number": i
        })
    with client.application.app_context():
        rest = Restaurant(
            name="R2",
            description="d",
            address="a",
            city="b",
            image_url="img2.jpg"
        )
        db.session.add(rest)
        db.session.commit()
    for i in range(1, 6):
        client.post('/reservations', json={
            "restaurant_id": 2,
            "date": "2024-07-24",
            "table_number": i
        })
    resp = client.post('/reservations', json={
        "restaurant_id": 2,
        "date": "2024-07-24",
        "table_number": 6
    })
    assert resp.status_code == 400
    assert "No hay más cupo total" in resp.get_json()["error"]

def test_list_reservations(client):
    client.post('/reservations', json={
        "restaurant_id": 1,
        "date": "2024-07-25",
        "table_number": 2
    })
    client.post('/reservations', json={
        "restaurant_id": 1,
        "date": "2024-07-25",
        "table_number": 3
    })
    resp = client.get('/reservations')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    resp = client.get('/reservations?date=2024-07-25')
    data = resp.get_json()
    assert all(r["date"] == "2024-07-25" for r in data)

def test_update_reservation(client):
    client.post('/reservations', json={
        "restaurant_id": 1,
        "date": "2024-07-26",
        "table_number": 7
    })
    resp = client.put('/reservations/1', json={
        "table_number": 8
    })
    assert resp.status_code == 200
    assert resp.get_json()["table_number"] == 8

def test_update_reservation_table_taken(client):
    client.post('/reservations', json={
        "restaurant_id": 1,
        "date": "2024-07-27",
        "table_number": 9
    })
    client.post('/reservations', json={
        "restaurant_id": 1,
        "date": "2024-07-27",
        "table_number": 10
    })
    resp = client.put('/reservations/2', json={
        "table_number": 9
    })
    assert resp.status_code == 400
    assert "ya está reservada" in resp.get_json()["error"]

def test_update_reservation_not_found(client):
    resp = client.put('/reservations/999', json={
        "table_number": 1
    })
    assert resp.status_code == 404
    assert "Reserva no encontrada" in resp.get_json()["error"]

def test_delete_reservation(client):
    client.post('/reservations', json={
        "restaurant_id": 1,
        "date": "2024-07-28",
        "table_number": 11
    })
    resp = client.delete('/reservations/1')
    assert resp.status_code == 200
    assert resp.get_json()["message"] == "Reserva eliminada"

def test_delete_reservation_not_found(client):
    resp = client.delete('/reservations/999')
    assert resp.status_code == 404
    assert "Reserva no encontrada" in resp.get_json()["error"]
