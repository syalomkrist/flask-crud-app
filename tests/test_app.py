"""
Test Suite - Flask CRUD App (Manajemen Produk)
============================================================
Mencakup: Health check, CRUD routes, API endpoints, validasi input
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app
from database import db, Produk


# ── Fixtures ──────────────────────────────────────────────────────────────────
@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['WTF_CSRF_ENABLED'] = False
    flask_app.config['SECRET_KEY'] = 'test-secret-key'

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_produk(app):
    """Buat produk contoh untuk digunakan dalam test."""
    with app.app_context():
        p = Produk(nama='Laptop Tes', kategori='Elektronik', harga=12000000.0, stok=5, deskripsi='Produk tes')
        db.session.add(p)
        db.session.commit()
        return p.id


# ── Health Check ─────────────────────────────────────────────────────────────
class TestHealthCheck:
    def test_health_endpoint_returns_ok(self, client):
        res = client.get('/health')
        assert res.status_code == 200
        data = res.get_json()
        assert data['status'] == 'ok'


# ── Index / Read All ──────────────────────────────────────────────────────────
class TestIndex:
    def test_index_returns_200(self, client):
        res = client.get('/')
        assert res.status_code == 200

    def test_index_kosong(self, client):
        res = client.get('/')
        assert b'Manajemen Produk' in res.data or res.status_code == 200

    def test_index_dengan_produk(self, client, sample_produk):
        res = client.get('/')
        assert res.status_code == 200
        assert b'Laptop Tes' in res.data

    def test_index_search(self, client, sample_produk):
        res = client.get('/?search=Laptop')
        assert res.status_code == 200
        assert b'Laptop Tes' in res.data

    def test_index_search_tidak_ada(self, client, sample_produk):
        res = client.get('/?search=tidakada999')
        assert res.status_code == 200


# ── Create ────────────────────────────────────────────────────────────────────
class TestTambahProduk:
    def test_form_tambah_get(self, client):
        res = client.get('/tambah')
        assert res.status_code == 200

    def test_tambah_produk_sukses(self, client):
        res = client.post('/tambah', data={
            'nama'     : 'Mouse Gaming',
            'kategori' : 'Aksesoris',
            'harga'    : '350000',
            'stok'     : '20',
            'deskripsi': 'Mouse gaming RGB'
        }, follow_redirects=True)
        assert res.status_code == 200
        assert b'Mouse Gaming' in res.data

    def test_tambah_tanpa_nama(self, client):
        res = client.post('/tambah', data={
            'nama' : '',
            'harga': '100000',
            'stok' : '5'
        }, follow_redirects=True)
        assert res.status_code == 200

    def test_tambah_harga_tidak_valid(self, client):
        res = client.post('/tambah', data={
            'nama' : 'Produk Error',
            'harga': 'abc',
            'stok' : '5'
        }, follow_redirects=True)
        assert res.status_code == 200


# ── Read One ──────────────────────────────────────────────────────────────────
class TestDetailProduk:
    def test_detail_produk_ada(self, client, sample_produk):
        res = client.get(f'/detail/{sample_produk}')
        assert res.status_code == 200
        assert b'Laptop Tes' in res.data

    def test_detail_produk_tidak_ada(self, client):
        res = client.get('/detail/9999')
        assert res.status_code == 404


# ── Update ────────────────────────────────────────────────────────────────────
class TestEditProduk:
    def test_form_edit_get(self, client, sample_produk):
        res = client.get(f'/edit/{sample_produk}')
        assert res.status_code == 200

    def test_edit_produk_sukses(self, client, sample_produk):
        res = client.post(f'/edit/{sample_produk}', data={
            'nama'     : 'Laptop Updated',
            'kategori' : 'Elektronik',
            'harga'    : '13000000',
            'stok'     : '3',
            'deskripsi': 'Sudah diupdate'
        }, follow_redirects=True)
        assert res.status_code == 200
        assert b'Laptop Updated' in res.data

    def test_edit_produk_tidak_ada(self, client):
        res = client.get('/edit/9999')
        assert res.status_code == 404

    def test_edit_tanpa_nama(self, client, sample_produk):
        res = client.post(f'/edit/{sample_produk}', data={
            'nama' : '',
            'harga': '100000',
            'stok' : '5'
        }, follow_redirects=True)
        assert res.status_code == 200


# ── Delete ────────────────────────────────────────────────────────────────────
class TestHapusProduk:
    def test_hapus_produk_sukses(self, client, sample_produk):
        res = client.post(f'/hapus/{sample_produk}', follow_redirects=True)
        assert res.status_code == 200

    def test_hapus_produk_tidak_ada(self, client):
        res = client.post('/hapus/9999')
        assert res.status_code == 404


# ── API Endpoints ─────────────────────────────────────────────────────────────
class TestApiEndpoints:
    def test_api_list_kosong(self, client):
        res = client.get('/api/produk')
        assert res.status_code == 200
        assert res.get_json() == []

    def test_api_list_ada_data(self, client, sample_produk):
        res = client.get('/api/produk')
        assert res.status_code == 200
        data = res.get_json()
        assert len(data) == 1
        assert data[0]['nama'] == 'Laptop Tes'

    def test_api_detail_ada(self, client, sample_produk):
        res = client.get(f'/api/produk/{sample_produk}')
        assert res.status_code == 200
        data = res.get_json()
        assert data['nama'] == 'Laptop Tes'
        assert data['harga'] == 12000000.0
        assert data['stok'] == 5

    def test_api_detail_tidak_ada(self, client):
        res = client.get('/api/produk/9999')
        assert res.status_code == 404

    def test_api_response_fields(self, client, sample_produk):
        res = client.get(f'/api/produk/{sample_produk}')
        data = res.get_json()
        assert 'id' in data
        assert 'nama' in data
        assert 'kategori' in data
        assert 'harga' in data
        assert 'stok' in data
        assert 'deskripsi' in data
