from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'kutuphane_gizli_anahtar_2024'

# Veritabanı bağlantısı
def get_db():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

# Veritabanı tablolarını oluştur
def init_db():
    conn = get_db()
    
    # Kitaplar tablosu
    conn.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE,
            category TEXT,
            publisher TEXT,
            year INTEGER,
            available INTEGER DEFAULT 1,
            total_copies INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Üyeler tablosu
    conn.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            address TEXT,
            membership_date DATE DEFAULT CURRENT_DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Ödünç işlemleri tablosu
    conn.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            member_id INTEGER,
            loan_date DATE NOT NULL,
            due_date DATE NOT NULL,
            return_date DATE,
            status TEXT DEFAULT 'active',
            notes TEXT,
            FOREIGN KEY (book_id) REFERENCES books (id),
            FOREIGN KEY (member_id) REFERENCES members (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Veritabanı başarıyla oluşturuldu!")

# Ana sayfa - Dashboard
@app.route('/')
def index():
    conn = get_db()
    
    # İstatistikler
    total_books = conn.execute('SELECT COUNT(*) as count FROM books').fetchone()['count']
    available_books = conn.execute('SELECT COUNT(*) as count FROM books WHERE available > 0').fetchone()['count']
    total_members = conn.execute('SELECT COUNT(*) as count FROM members').fetchone()['count']
    active_loans = conn.execute('SELECT COUNT(*) as count FROM loans WHERE status = "active"').fetchone()['count']
    
    # Son eklenen kitaplar
    recent_books = conn.execute('SELECT * FROM books ORDER BY created_at DESC LIMIT 5').fetchall()
    
    # Son üyeler
    recent_members = conn.execute('SELECT * FROM members ORDER BY created_at DESC LIMIT 5').fetchall()
    
    # Geciken kitaplar
    overdue_loans = conn.execute('''
        SELECT l.*, b.title as book_title, m.name as member_name 
        FROM loans l 
        JOIN books b ON l.book_id = b.id 
        JOIN members m ON l.member_id = m.id 
        WHERE l.status = "active" AND l.due_date < date('now')
        ORDER BY l.due_date ASC
    ''').fetchall()
    
    conn.close()
    
    return render_template('index.html',
                         total_books=total_books,
                         available_books=available_books,
                         total_members=total_members,
                         active_loans=active_loans,
                         recent_books=recent_books,
                         recent_members=recent_members,
                         overdue_loans=overdue_loans)

# Kitaplar sayfası
@app.route('/books')
def books():
    conn = get_db()
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = 'SELECT * FROM books WHERE 1=1'
    params = []
    
    if search:
        query += ' AND (title LIKE ? OR author LIKE ? OR isbn LIKE ?)'
        search_term = f'%{search}%'
        params.extend([search_term, search_term, search_term])
    
    if category:
        query += ' AND category = ?'
        params.append(category)
    
    query += ' ORDER BY title ASC'
    
    books = conn.execute(query, params).fetchall()
    
    # Kategorileri al
    categories = conn.execute('SELECT DISTINCT category FROM books WHERE category IS NOT NULL ORDER BY category').fetchall()
    
    conn.close()
    
    return render_template('books.html', books=books, categories=categories, search=search, selected_category=category)

# Kitap ekleme
@app.route('/books/add', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    isbn = request.form.get('isbn', '')
    category = request.form.get('category', '')
    publisher = request.form.get('publisher', '')
    year = request.form.get('year', '')
    total_copies = request.form.get('total_copies', 1)
    
    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO books (title, author, isbn, category, publisher, year, total_copies, available) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, author, isbn if isbn else None, category, publisher, year if year else None, total_copies, total_copies))
        conn.commit()
        flash('Kitap başarıyla eklendi!', 'success')
    except sqlite3.IntegrityError:
        flash('Bu ISBN numarası zaten kayıtlı!', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('books'))

# Kitap silme
@app.route('/books/delete/<int:book_id>')
def delete_book(book_id):
    conn = get_db()
    
    # Kitabın aktif ödüncü var mı kontrol et
    active_loan = conn.execute('SELECT COUNT(*) as count FROM loans WHERE book_id = ? AND status = "active"', (book_id,)).fetchone()
    
    if active_loan['count'] > 0:
        flash('Bu kitap şu anda ödünçte olduğu için silinemez!', 'error')
    else:
        conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
        conn.commit()
        flash('Kitap silindi!', 'success')
    
    conn.close()
    return redirect(url_for('books'))

# Üyeler sayfası
@app.route('/members')
def members():
    conn = get_db()
    search = request.args.get('search', '')
    
    query = 'SELECT * FROM members WHERE 1=1'
    params = []
    
    if search:
        query += ' AND (name LIKE ? OR email LIKE ? OR phone LIKE ?)'
        search_term = f'%{search}%'
        params.extend([search_term, search_term, search_term])
    
    query += ' ORDER BY name ASC'
    
    members = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('members.html', members=members, search=search)

# Üye ekleme
@app.route('/members/add', methods=['POST'])
def add_member():
    name = request.form['name']
    email = request.form['email']
    phone = request.form.get('phone', '')
    address = request.form.get('address', '')
    
    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO members (name, email, phone, address) 
            VALUES (?, ?, ?, ?)
        ''', (name, email, phone, address))
        conn.commit()
        flash('Üye başarıyla eklendi!', 'success')
    except sqlite3.IntegrityError:
        flash('Bu e-posta adresi zaten kayıtlı!', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('members'))

# Üye silme
@app.route('/members/delete/<int:member_id>')
def delete_member(member_id):
    conn = get_db()
    
    # Üyenin aktif ödüncü var mı kontrol et
    active_loan = conn.execute('SELECT COUNT(*) as count FROM loans WHERE member_id = ? AND status = "active"', (member_id,)).fetchone()
    
    if active_loan['count'] > 0:
        flash('Bu üyenin aktif ödüncü olduğu için silinemez!', 'error')
    else:
        conn.execute('DELETE FROM members WHERE id = ?', (member_id,))
        conn.commit()
        flash('Üye silindi!', 'success')
    
    conn.close()
    return redirect(url_for('members'))

# Ödünç işlemleri sayfası
@app.route('/loans')
def loans():
    conn = get_db()
    status_filter = request.args.get('status', 'all')
    
    query = '''
        SELECT l.*, b.title as book_title, b.author as book_author, m.name as member_name, m.email as member_email 
        FROM loans l 
        JOIN books b ON l.book_id = b.id 
        JOIN members m ON l.member_id = m.id 
        WHERE 1=1
    '''
    params = []
    
    if status_filter == 'active':
        query += ' AND l.status = "active"'
    elif status_filter == 'returned':
        query += ' AND l.status = "returned"'
    elif status_filter == 'overdue':
        query += ' AND l.status = "active" AND l.due_date < date("now")'
    
    query += ' ORDER BY l.loan_date DESC'
    
    loans = conn.execute(query, params).fetchall()
    
    # Ödünç verilebilir kitaplar
    available_books = conn.execute('SELECT * FROM books WHERE available > 0 ORDER BY title').fetchall()
    
    # Üyeler
    members = conn.execute('SELECT * FROM members ORDER BY name').fetchall()
    
    conn.close()
    
    return render_template('loans.html', 
                         loans=loans, 
                         available_books=available_books,
                         members=members,
                         status_filter=status_filter)

# Ödünç verme
@app.route('/loans/add', methods=['POST'])
def add_loan():
    book_id = request.form['book_id']
    member_id = request.form['member_id']
    days = int(request.form.get('days', 14))
    notes = request.form.get('notes', '')
    
    loan_date = datetime.now().strftime('%Y-%m-%d')
    due_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    
    conn = get_db()
    
    # Kitap müsait mi kontrol et
    book = conn.execute('SELECT available FROM books WHERE id = ?', (book_id,)).fetchone()
    
    if book and book['available'] > 0:
        conn.execute('''
            INSERT INTO loans (book_id, member_id, loan_date, due_date, notes) 
            VALUES (?, ?, ?, ?, ?)
        ''', (book_id, member_id, loan_date, due_date, notes))
        
        # Kitap sayısını azalt
        conn.execute('UPDATE books SET available = available - 1 WHERE id = ?', (book_id,))
        conn.commit()
        flash('Kitap başarıyla ödünç verildi!', 'success')
    else:
        flash('Bu kitap şu anda mevcut değil!', 'error')
    
    conn.close()
    return redirect(url_for('loans'))

# İade alma
@app.route('/loans/return/<int:loan_id>')
def return_loan(loan_id):
    return_date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db()
    
    # Loan bilgilerini al
    loan = conn.execute('SELECT book_id FROM loans WHERE id = ?', (loan_id,)).fetchone()
    
    if loan:
        # Loan'ı güncelle
        conn.execute('''
            UPDATE loans 
            SET status = "returned", return_date = ? 
            WHERE id = ?
        ''', (return_date, loan_id))
        
        # Kitap sayısını artır
        conn.execute('UPDATE books SET available = available + 1 WHERE id = ?', (loan['book_id'],))
        conn.commit()
        flash('Kitap başarıyla iade alındı!', 'success')
    
    conn.close()
    return redirect(url_for('loans'))

# Ödünç süresini uzat
@app.route('/loans/extend/<int:loan_id>')
def extend_loan(loan_id):
    conn = get_db()
    
    # Mevcut due_date'i al ve 7 gün ekle
    loan = conn.execute('SELECT due_date FROM loans WHERE id = ?', (loan_id,)).fetchone()
    
    if loan:
        old_due_date = datetime.strptime(loan['due_date'], '%Y-%m-%d')
        new_due_date = (old_due_date + timedelta(days=7)).strftime('%Y-%m-%d')
        
        conn.execute('UPDATE loans SET due_date = ? WHERE id = ?', (new_due_date, loan_id))
        conn.commit()
        flash('Ödünç süresi 7 gün uzatıldı!', 'success')
    
    conn.close()
    return redirect(url_for('loans'))

if __name__ == '__main__':
    # Veritabanını başlat
    if not os.path.exists('library.db'):
        init_db()
    
    print("=" * 70)
    print("📚 Akıllı Kütüphane Yönetim Sistemi Başlatılıyor...")
    print("=" * 70)
    print("\n🌐 Tarayıcınızda şu adresi açın: http://127.0.0.1:5000")
    print("\n💡 Durdurmak için: CTRL + C")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)