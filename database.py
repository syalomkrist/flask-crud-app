from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Produk(db.Model):
    __tablename__ = 'produk'

    id         = db.Column(db.Integer, primary_key=True)
    nama       = db.Column(db.String(100), nullable=False)
    kategori   = db.Column(db.String(50), default='Umum')
    harga      = db.Column(db.Float, nullable=False, default=0.0)
    stok       = db.Column(db.Integer, nullable=False, default=0)
    deskripsi  = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id'        : self.id,
            'nama'      : self.nama,
            'kategori'  : self.kategori,
            'harga'     : self.harga,
            'stok'      : self.stok,
            'deskripsi' : self.deskripsi,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Produk {self.nama}>'
