"""Script validasi startup aplikasi untuk CI/CD pipeline."""
import sys

from app import app
from database import db

app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

with app.app_context():
    db.create_all()
    print('Database initialized OK')

    client = app.test_client()
    res = client.get('/health')
    assert res.status_code == 200, f'Health check failed: {res.status_code}'
    print('Health check passed:', res.get_json())

print('Build validation PASSED')
sys.exit(0)
