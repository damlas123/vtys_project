from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
from psycopg2.extras import DictCursor
import bcrypt

app = Flask(__name__)
app.secret_key = "secretkey" 

def connect_to_db():
    return psycopg2.connect(
        dbname="girisimci_kadinlar",
        user="postgres",
        password="1205046",
        host="localhost",
        port="5432"
    )

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        isim = request.form['isim']
        soyisim = request.form['soyisim']
        email = request.form['email']
        sifre = request.form['sifre']
        kullanici_tipi = request.form['kullanici_tipi']

        hashed_password = bcrypt.hashpw(sifre.encode('utf-8'), bcrypt.gensalt())

        with connect_to_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Kullanici (isim, soyisim, email, sifre, kullanici_tipi)
                    VALUES (%s, %s, %s, %s, %s);
                """, (isim, soyisim, email, hashed_password, kullanici_tipi))
            conn.commit()
        return redirect(url_for('index'))
    return render_template('add_user.html')

@app.route('/update_user/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    if request.method == 'POST':
        isim = request.form['isim']
        soyisim = request.form['soyisim']
        email = request.form['email']
        kullanici_tipi = request.form['kullanici_tipi']

        with connect_to_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE Kullanici
                    SET isim = %s, soyisim = %s, email = %s, kullanici_tipi = %s
                    WHERE id = %s;
                """, (isim, soyisim, email, kullanici_tipi, user_id))
            conn.commit()
        return redirect(url_for('index'))

    with connect_to_db() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT * FROM Kullanici WHERE id = %s;", (user_id,))
            user = cursor.fetchone()
    return render_template('update_user.html', user=user)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    with connect_to_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Kullanici WHERE id = %s;", (user_id,))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        kullanici_id = request.form['kullanici_id']
        baslik = request.form['baslik']
        aciklama = request.form['aciklama']
        durum = request.form['durum']

        with connect_to_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Proje (kullanici_id, baslik, aciklama, durum)
                    VALUES (%s, %s, %s, %s);
                """, (kullanici_id, baslik, aciklama, durum))
            conn.commit()
        return redirect(url_for('index'))
    return render_template('add_project.html')

@app.route('/delete_project/<int:proje_id>', methods=['POST'])
def delete_project(proje_id):
    with connect_to_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Proje WHERE proje_id = %s;", (proje_id,))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/search_user', methods=['GET', 'POST'])
def search_user():
    users = []
    if request.method == 'POST':
        email = request.form['email']
        with connect_to_db() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("SELECT * FROM Kullanici WHERE email = %s;", (email,))
                users = cursor.fetchall()
    return render_template('search.html', users=users)




@app.route('/messages')
def messages():
    with connect_to_db() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    m.mesaj_id, 
                    gonderen.isim AS gonderen_isim, 
                    alici.isim AS alici_isim, 
                    m.mesaj_metni, 
                    m.tarih
                FROM mesaj m
                JOIN kullanici gonderen ON m.gonderen_id = gonderen.id
                JOIN kullanici alici ON m.alici_id = alici.id
                ORDER BY m.tarih DESC;
            """)
            mesajlar = cursor.fetchall()
    return render_template('add_messages.html', mesajlar=mesajlar)


@app.route('/comments')
def comments():
    with connect_to_db() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    y.yorum_id, 
                    k.isim AS kullanici_isim, 
                    p.baslik AS proje_baslik, 
                    y.yorum_metni, 
                    y.tarih
                FROM yorum y
                JOIN kullanici k ON y.kullanici_id = k.id
                JOIN proje p ON y.proje_id = p.proje_id
                ORDER BY y.tarih DESC;
            """)
            yorumlar = cursor.fetchall()
    return render_template('add_comments.html', yorumlar=yorumlar)


@app.route('/add_message', methods=['GET', 'POST'])
def add_message():
    if request.method == 'POST':
        gonderen_id = request.form['gonderen_id']
        alici_id = request.form['alici_id']
        mesaj_metni = request.form['mesaj_metni']

        with connect_to_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO mesaj (gonderen_id, alici_id, mesaj_metni)
                    VALUES (%s, %s, %s);
                """, (gonderen_id, alici_id, mesaj_metni))
            conn.commit()
        return redirect(url_for('messages'))

    with connect_to_db() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT id, isim FROM kullanici;")
            kullanicilar = cursor.fetchall()
    return render_template('add_message.html', kullanicilar=kullanicilar)



@app.route('/add_comment', methods=['GET', 'POST'])
def add_comment():
    if request.method == 'POST':
        kullanici_id = request.form['kullanici_id']
        proje_id = request.form['proje_id']
        yorum_metni = request.form['yorum_metni']

        with connect_to_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO yorum (kullanici_id, proje_id, yorum_metni)
                    VALUES (%s, %s, %s);
                """, (kullanici_id, proje_id, yorum_metni))
            conn.commit()
        return redirect(url_for('comments'))

    with connect_to_db() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT id, isim FROM kullanici;")
            kullanicilar = cursor.fetchall()
            cursor.execute("SELECT proje_id, baslik FROM proje;")
            projeler = cursor.fetchall()
    return render_template('add_comment.html', kullanicilar=kullanicilar, projeler=projeler)




@app.route('/')
def index():
    with connect_to_db() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # Kullanıcıları çek
            cursor.execute("SELECT id, isim, soyisim, email, kullanici_tipi FROM Kullanici;")
            kullanicilar = cursor.fetchall()

            # Projeleri çek
            cursor.execute("SELECT proje_id, baslik, aciklama, durum, kullanici_id FROM Proje;")
            projeler = cursor.fetchall()

            # Mesajları çek
            cursor.execute("""
                SELECT 
                    m.mesaj_id, 
                    gonderen.isim AS gonderen_isim, 
                    alici.isim AS alici_isim, 
                    m.mesaj_metni, 
                    m.tarih
                FROM mesaj m
                JOIN kullanici gonderen ON m.gonderen_id = gonderen.id
                JOIN kullanici alici ON m.alici_id = alici.id
                ORDER BY m.tarih DESC;
            """)
            mesajlar = cursor.fetchall()

            # Yorumları çek
            cursor.execute("""
                SELECT 
                    y.yorum_id, 
                    k.isim AS kullanici_isim, 
                    p.baslik AS proje_baslik, 
                    y.yorum_metni, 
                    y.tarih
                FROM yorum y
                JOIN kullanici k ON y.kullanici_id = k.id
                JOIN proje p ON y.proje_id = p.proje_id
                ORDER BY y.tarih DESC;
            """)
            yorumlar = cursor.fetchall()

    return render_template('index.html', kullanicilar=kullanicilar, projeler=projeler, mesajlar=mesajlar, yorumlar=yorumlar)

if __name__ == '__main__':
    app.run(debug=True)

