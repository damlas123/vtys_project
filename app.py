from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

# Veritabanı bağlantısı
def connect_to_db():
    conn = psycopg2.connect(
        dbname="uygulama",  # Veritabanı adı
        user="postgres",       # Kullanıcı adı
        password="1205046",  # Şifre
        host="localhost",        # Sunucu
        port="5432"             # Port
    )
    return conn

# Ana sayfa: Kullanıcıları listeler
@app.route('/')
def index():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM \"user\";")  # Kullanıcıları getir
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', users=users)

# Kullanıcı ekleme sayfası
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        user_name = request.form['user_name']
        user_surname = request.form['user_surname']
        email = request.form['email']
        password = request.form['password']

        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            CALL add_user(%s, %s, %s, %s);
        """, (user_name, user_surname, email, password))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_user.html')

# Kullanıcıyı arama
@app.route('/search_user', methods=['POST'])
def search_user():
    email = request.form['email']
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM \"user\" WHERE \"email\" = %s;", (email,))
    user = cursor.fetchone()  # Bir kullanıcı döndür
    cursor.close()
    conn.close()
    if user:
        return f"User Found: {user}"
    else:
        return "User not found."

# Kullanıcı güncelleme sayfası
@app.route('/update_user/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    if request.method == 'POST':
        new_name = request.form['new_name']
        new_surname = request.form['new_surname']
        new_email = request.form['new_email']

        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            CALL update_user(%s, %s, %s, %s);
        """, (user_id, new_name, new_surname, new_email))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM \"user\" WHERE \"user_id\" = %s;", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('update_user.html', user=user)

# Kullanıcı silme
@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM \"user\" WHERE \"user_id\" = %s;", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
