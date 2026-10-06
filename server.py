from flask import Flask, abort, render_template, request, url_for, redirect, jsonify, session, Response, send_from_directory
import flask_login
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import psycopg2																	
from psycopg2 import Error
import os
from werkzeug.security import generate_password_hash, check_password_hash
import random
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from datetime import datetime, date
from functools import wraps																
import secrets

app = Flask(__name__)
app.secret_key = "dhasjkdhjkasdjkasdh"

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    result = cursor.fetchone()

    if result is None:
        return None

    user = User(result[0])
    user.email = result[1]
    user.username = result[2]
    user.password = result[3]
    user.logo = result[4]
    return user

# DATABASE
conn = psycopg2.connect(host = "127.0.0.1", database = "sito", user = 'postgres', password = 'Admin24') # CONFIGURARE CON APPOSITO SERVER PSQL DA CONFIGURARE
cursor = conn.cursor()

#fnuzioni a caso di lrsmgk
EXTERNAL_LOGO_DIR = "/mnt/NAS/letters"

def getLogo(username):
    letter = username[0].upper()
    logos = os.listdir(EXTERNAL_LOGO_DIR)
    logo = [f for f in logos if f.startswith(letter)]

    if not logo:
        return '/static/images/accounts/default.png'  # fallback se non esiste
    
    fileName = logo[0]
    # Qui metti il path dell'endpoint che serviremo al browser
    logoPath = f"/external_logos/{fileName}"
    return logoPath

@app.route('/test')
def test():
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchone()
    
    data = {
        "id": result[0],
        "email": result[1],
        "username": result[2],
        "password": result[3],
        "logo": result[4]
    }

    print(data)


    return "vaffanculo"

@app.route('/')
def helloworld():
    if current_user.is_authenticated:
        return render_template('index.html', username=current_user.username)
    else:
        return redirect(url_for('register'))

from werkzeug.security import check_password_hash

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['name']
        password = request.form['password']

        try:
            #conn.autocommit = True
            cursor.execute('SELECT * FROM users WHERE username = %s OR email = %s', (username, username))
            result = cursor.fetchone()
        except Error as e:
            print(e)
            return jsonify({"result": "error", "error_text": "Errore del database."}), 500

        if result:
            user_id, storedEmail, storedUsername, storedPassword, storedLogo = result

            if check_password_hash(storedPassword, password):
                user = User(user_id)
                user.username = storedUsername
                user.email = storedEmail
                user.logo = storedLogo
                login_user(user, remember=True)
                return jsonify({"result": "success"})
            else:
                return jsonify({"result": "error", "error_text": "Password errata."})
        else:
            # Utente non trovato → frontend mostrerà modal con link a register
            return jsonify({
                "result": "error",
                "popup_text": "Utente inesistente o username errato.",
                "redirect": "/register"
            })

    else:
        return render_template('login.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']
        passwordConfirm = request.form['passwordConfirm']

        #conn.autocommit = True
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({
                "result": "error",
                "error_text": "Username già esistente"
            }), 400

        user_id = ''.join([str(random.randint(0, 9)) for _ in range(9)])
        logo = getLogo(username)
        print(logo)

        if password == passwordConfirm:
            hashed_password = generate_password_hash(
                password, method='pbkdf2:sha256'
            )

            try:
                #conn.autocommit = False
                cursor.execute(
                    'INSERT INTO users (id, email, username, password, logo) '
                    'VALUES (%s, %s, %s, %s, %s)',
                    (
                        int(user_id),
                        format(email),
                        format(username),
                        format(hashed_password),
                        format(logo)
                    )
                )
                conn.commit()
                print("ho eseguito la query nel db")
                
            except Error as e:
                print(e)
                conn.rollback()
                return jsonify({
                    "result": "error",
                    "error_text": "Errore del database"
                }), 500
        else:
            return jsonify({
                "result": "error",
                "error_text": "Le due password non corrispondono."
            }), 400

        print("HA FUNZIATO TUTTO")
        user = User(id=user_id)
        user.username = username
        user.email = email
        user.logo = logo
        login_user(user, remember=True)

        return jsonify({"result": "success"}), 200

    else:
        return render_template('register.html')

@app.route('/logout')
def logout():
    return render_template('logout.html')

@app.route('/account')
def account():
    return render_template('account-info.html')

@app.route('/security')
def accountsecurity():
    return render_template('account-security.html')

@app.route('/danger')
def accountdangerzone():
    return render_template('account-danger.html')

@app.route('/issues')
def issues():
    return render_template('issues.html')

@app.route('/prodotti')
def prodotti_main():
    return render_template('/prodotti/prodotti.html')

@app.route('/prodotti/barrette')

def barrette():
    return render_template('prodotti/barrette/barrette.html')

@app.route('/prodotti/dolci')
def dolci():
    return render_template('prodotti/dolci/dolci.html')

@app.route('/prodotti/gallette')
def gallette():
    return render_template('prodotti/gallette/galletta.html')

@app.route('/prodotti/omogenizzati')
def omogenizzati():
    return render_template('prodotti/omogenizzati/omogenizzati.html')

@app.route('/prodotti/barrette/<product_name>')
def barretta(product_name):
    allowed = [
        'barretta1',
        'barretta2',
        'barretta3',
        'barretta4',
        'barretta5',
        'barretta6',
        'barretta7'
    ]

    if product_name not in allowed:
        abort(404)
    return render_template(f'prodotti/barrette/{product_name}.html')

@app.route('/prodotti/dolci/<product_name>')
def dolce(product_name):
    allowed = [
        'crema',
        'crema2',
        'tiramisu'
    ]

    if product_name not in allowed:
        abort(404)
    return render_template(f'prodotti/dolci/{product_name}.html')

@app.route('/prodotti/gallette/<product_name>')
def galletta(product_name):
    allowed = [
        'galletta1',
        'galletta2',
        'galletta3',
        'fiocchi',
        'soffietti',
        'soffietti2',
        'tortino',
    ]

    if product_name not in allowed:
        abort(404)
    return render_template(f'prodotti/gallette/{product_name}.html')

@app.route('/prodotti/omogenizzati/<product_name>')
def omogenizzato(product_name):
    allowed = [
        'banana',
        'fragola',
        'mela',
        'tropicale',
    ]

    if product_name not in allowed:
        abort(404)
    return render_template(f'prodotti/omogenizzati/{product_name}.html')

@app.route('/carrello')
def carrello():
    return render_template('carrello.html')

@app.route('/olio')
def olio():
    return render_template('olio.html')

@app.route('/account/changeUsername', methods=['POST'])
def changeUsername():
    newUsername = request.form.get('newUsername')
    current_password = request.form.get('currentPassword')
    user_id = current_user.id

    if not newUsername or not current_password:
        return jsonify({
            "result": "error",
            "error_text": "Compila tutti i campi."
        })

    # Controllo username già esistente
    cursor.execute(
        'SELECT id FROM users WHERE username = %s',
        (newUsername,)
    )
    existing = cursor.fetchone()

    if existing:
        return jsonify({
            "result": "error",
            "error_text": "Username già in uso."
        })

    # Recupero password
    cursor.execute(
        'SELECT password FROM users WHERE id = %s',
        (int(user_id),)
    )
    result = cursor.fetchone()

    if not result:
        return jsonify({
            "result": "error",
            "error_text": "Utente non trovato."
        })

    storedPassword = result[0]

    if not check_password_hash(storedPassword, current_password):
        return jsonify({
            "result": "error",
            "error_text": "Password errata."
        })

    try:
        # UPDATE DB
        cursor.execute(
            'UPDATE users SET username = %s WHERE id = %s',
            (newUsername, int(user_id))
        )
        conn.commit()

        current_user.username = newUsername

        return jsonify({"result": "success"})

    except Exception as e:
        print(e)
        return jsonify({
            "result": "error",
            "error_text": "Errore del database."
        })

@app.route('/account/changeEmail', methods=['POST'])
def changeEmail():
    newEmail = request.form.get('newEmail')
    current_password = request.form.get('currentPassword')
    user_id = current_user.id

    if not newEmail or not current_password:
        return jsonify({
            "result": "error",
            "error_text": "Compila tutti i campi."
        })

    cursor.execute('SELECT password FROM users WHERE id = %s', (int(user_id),))
    result = cursor.fetchone()

    if not result:
        return jsonify({
            "result": "error",
            "error_text": "Utente non trovato."
        })

    storedPassword = result[0]

    if not check_password_hash(storedPassword, current_password):
        return jsonify({
            "result": "error",
            "error_text": "Password errata."
        })

    try:
        cursor.execute(
            'UPDATE users SET email = %s WHERE id = %s',
            (newEmail, int(user_id))
        )
        conn.commit()
        return jsonify({"result": "success"})
    except Error as e:
        print(e)
        return jsonify({
            "result": "error",
            "error_text": "Errore del database."
        })
    
@app.route('/account/changePassword', methods=['POST'])
def changePassword():
    newPassword = request.form.get('newPassword')
    current_password = request.form.get('currentPassword')
    passwordConfirm = request.form.get('passwordConfirm')
    user_id = current_user.id

    # Validazioni base
    if not current_password or not newPassword or not passwordConfirm:
        return jsonify({
            "result": "error",
            "error_text": "Compila tutti i campi."
        })

    if newPassword != passwordConfirm:
        return jsonify({
            "result": "error",
            "error_text": "Le password non coincidono."
        })

    # Recupero password attuale
    cursor.execute(
        'SELECT password FROM users WHERE id = %s',
        (int(user_id),)
    )
    result = cursor.fetchone()

    if not result:
        return jsonify({
            "result": "error",
            "error_text": "Utente non trovato."
        })

    storedPassword = result[0]

    # Verifica password attuale
    if not check_password_hash(storedPassword, current_password):
        return jsonify({
            "result": "error",
            "error_text": "Password attuale errata."
        })

    # Hash nuova password (COERENTE con il resto del progetto)
    hashed_password = generate_password_hash(
        newPassword,
        method='pbkdf2:sha256'
    )

    try:
        cursor.execute(
            'UPDATE users SET password = %s WHERE id = %s',
            (hashed_password, int(user_id))
        )
        conn.commit()

        return jsonify({"result": "success"})

    except Error as e:
        print(e)
        return jsonify({
            "result": "error",
            "error_text": "Errore del database."
        })

@app.route('/rgb')
def rgb():
    return render_template('rgb.html')

@app.route('/termini_di_servizio')
def termini_di_servizio():
    return render_template('tds.html')

@app.route('/chi_siamo')
def chi_siamo():
    return render_template('NOI.html')

@app.route('/account/accountDelete', methods=['POST'])
def accountDelete():
    user_id = current_user.id
    try:
        # Logout dell'utente
        logout_user()

        # Eliminazione dell'utente dal database
        cursor.execute('DELETE FROM users WHERE id = %s', (int(user_id),))
        conn.commit()

        # Risposta JSON di successo
        return jsonify({"result": "success", "redirect": "/login"})

    except Exception as e:
        # Risposta JSON di errore
        return jsonify({"result": "error", "popup_text": "Errore durante l'eliminazione dell'account."})
    
EXTERNAL_LOGO_DIR = "/mnt/NAS/letters"

@app.route('/external_logos/<filename>')
def external_logos(filename):
    # Flask prenderà il file dalla cartella esterna
    return send_from_directory(EXTERNAL_LOGO_DIR, filename)

MATERIALE_DIR = "/mnt/NAS/materiale"

@app.route('/videos/<filename>')
def serve_video(filename):
    return send_from_directory(MATERIALE_DIR, filename)

@app.route('/image/<filename>')
def serve_images(filename):
    return send_from_directory(MATERIALE_DIR, filename)

@app.route('/logo/<filename>')
def serve_logo(filename):
    return send_from_directory(MATERIALE_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8054, debug=True)
