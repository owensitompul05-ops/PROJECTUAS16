from flask import Flask, render_template, request, session, redirect, url_for
import requests

app = Flask(__name__)
# Secret key diperlukan agar fitur 'session' (keranjang) bisa berfungsi
app.secret_key = 'toko_python_rahasia_123'

# Fungsi pembantu untuk mengambil dan memfilter data dari API
def ambil_data_produk():
    try:
        response = requests.get('https://fakestoreapi.com/products')
        all_products = response.json()
    except:
        return []

    # Filter: Hapus ID 1 sampai 8 (sesuai update kamu) dan konversi ke Rupiah
    id_dihapus = list(range(1, 9))
    kurs_idr = 16000
    
    products_clean = []
    for p in all_products:
        if p['id'] not in id_dihapus:
            p['price_idr'] = p['price'] * kurs_idr
            products_clean.append(p)
    return products_clean

@app.route('/')
def index():
    products = ambil_data_produk()
    # Hitung jumlah barang di keranjang untuk ditampilkan di navbar
    cart_count = len(session.get('cart', []))
    return render_template('index.html', products=products, cart_count=cart_count)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    products = ambil_data_produk()
    # Cari produk yang diklik berdasarkan ID
    product = next((p for p in products if p['id'] == product_id), None)
    
    if product:
        if 'cart' not in session:
            session['cart'] = []
        
        # Ambil data keranjang saat ini, tambah barang baru, lalu simpan lagi
        cart = session['cart']
        cart.append({
            'id': product['id'],
            'title': product['title'],
            'price': product['price_idr'],
            'image': product['image']
        })
        session['cart'] = cart
        session.modified = True 
        
    return redirect(url_for('index'))

@app.route('/cart')
def view_cart():
    cart_items = session.get('cart', [])
    total_harga = sum(item['price'] for item in cart_items)
    return render_template('cart.html', items=cart_items, total=total_harga)

# --- RUTE BARU UNTUK STRUK PEMBAYARAN ---
@app.route('/bayar_sukses')
def bayar_sukses():
    # 1. Ambil data keranjang saat ini sebelum dihapus
    items = session.get('cart', [])
    
    # Jika keranjang kosong tapi paksa akses, balikkan ke home
    if not items:
        return redirect(url_for('index'))
        
    total_harga = sum(item['price'] for item in items)
    
    # 2. Simpan data ke variabel sementara untuk ditampilkan di struk
    # 3. Kosongkan keranjang di session (LUNAS)
    session.pop('cart', None)
    
    return render_template('struk.html', items=items, total=total_harga)

@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('view_cart'))

if __name__ == '__main__':
    app.run(debug=True)