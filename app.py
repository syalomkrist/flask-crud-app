from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import db, Produk
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///produk.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# ─── READ ALL ──────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    search = request.args.get('search', '')
    if search:
        produk_list = Produk.query.filter(
            Produk.nama.ilike(f'%{search}%') | Produk.kategori.ilike(f'%{search}%')
        ).order_by(Produk.id.desc()).all()
    else:
        produk_list = Produk.query.order_by(Produk.id.desc()).all()
    return render_template('index.html', produk_list=produk_list, search=search)


# ─── CREATE ────────────────────────────────────────────────────────────────────
@app.route('/tambah', methods=['GET', 'POST'])
def tambah():
    if request.method == 'POST':
        nama      = request.form.get('nama', '').strip()
        kategori  = request.form.get('kategori', '').strip()
        harga     = request.form.get('harga', 0)
        stok      = request.form.get('stok', 0)
        deskripsi = request.form.get('deskripsi', '').strip()

        if not nama:
            flash('Nama produk wajib diisi!', 'danger')
            return render_template('form.html', action='tambah')

        try:
            harga = float(harga)
            stok  = int(stok)
        except ValueError:
            flash('Harga dan stok harus berupa angka!', 'danger')
            return render_template('form.html', action='tambah')

        produk = Produk(nama=nama, kategori=kategori, harga=harga,
                        stok=stok, deskripsi=deskripsi)
        db.session.add(produk)
        db.session.commit()
        flash(f'Produk "{nama}" berhasil ditambahkan!', 'success')
        return redirect(url_for('index'))

    return render_template('form.html', action='tambah')


# ─── READ ONE ──────────────────────────────────────────────────────────────────
@app.route('/detail/<int:id>')
def detail(id):
    produk = Produk.query.get_or_404(id)
    return render_template('detail.html', produk=produk)


# ─── UPDATE ────────────────────────────────────────────────────────────────────
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    produk = Produk.query.get_or_404(id)

    if request.method == 'POST':
        nama      = request.form.get('nama', '').strip()
        kategori  = request.form.get('kategori', '').strip()
        harga     = request.form.get('harga', 0)
        stok      = request.form.get('stok', 0)
        deskripsi = request.form.get('deskripsi', '').strip()

        if not nama:
            flash('Nama produk wajib diisi!', 'danger')
            return render_template('form.html', action='edit', produk=produk)

        try:
            harga = float(harga)
            stok  = int(stok)
        except ValueError:
            flash('Harga dan stok harus berupa angka!', 'danger')
            return render_template('form.html', action='edit', produk=produk)

        produk.nama      = nama
        produk.kategori  = kategori
        produk.harga     = harga
        produk.stok      = stok
        produk.deskripsi = deskripsi
        db.session.commit()
        flash(f'Produk "{nama}" berhasil diperbarui!', 'success')
        return redirect(url_for('index'))

    return render_template('form.html', action='edit', produk=produk)


# ─── DELETE ────────────────────────────────────────────────────────────────────
@app.route('/hapus/<int:id>', methods=['POST'])
def hapus(id):
    produk = Produk.query.get_or_404(id)
    nama = produk.nama
    db.session.delete(produk)
    db.session.commit()
    flash(f'Produk "{nama}" berhasil dihapus!', 'warning')
    return redirect(url_for('index'))


# ─── API (JSON) ────────────────────────────────────────────────────────────────
@app.route('/api/produk', methods=['GET'])
def api_list():
    produk_list = Produk.query.order_by(Produk.id.desc()).all()
    return jsonify([p.to_dict() for p in produk_list])


@app.route('/api/produk/<int:id>', methods=['GET'])
def api_detail(id):
    produk = Produk.query.get_or_404(id)
    return jsonify(produk.to_dict())


# ─── HEALTH CHECK ──────────────────────────────────────────────────────────────
@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Flask CRUD App berjalan normal'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
