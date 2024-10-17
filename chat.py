from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Datiles2044'

def init_db():
    conn = sqlite3.connect('AppChat.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS login (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL UNIQUE,
        contrasena TEXT NOT NULL,
        activo INTEGER DEFAULT 1)''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        content TEXT,
        media_type TEXT,
        media BLOB,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id))''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        first_name TEXT NOT NULL, 
        alias_name TEXT NOT NULL, 
        email TEXT NOT NULL UNIQUE, 
        status TEXT, 
        last_connected TIME, 
        profile_picture BLOB)''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('AppChat.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            flash('Por favor, inicia sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    print(session)
    if 'usuario' not in session :
        return redirect(url_for('login'))
    else:
        return render_template('index.html')

# Rutas de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['usuario']
        password = request.form['contrasena']
        
        # Verificar las credenciales del usuario
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM login WHERE usuario = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        print(user)
        if user and check_password_hash(user['contrasena'], password):
            session['usuario'] = user['usuario']
<<<<<<< HEAD
            # print('entro')
            # session['rol'] = user['rol']  # Si tienes un rol en tu tabla, ajusta esto
            return jsonify({'status': 'success', 'redirect': url_for('index')})
            # return redirect(url_for('index'))

=======
            print('entro')
            # session['rol'] = user['rol']  # Si tienes un rol en tu tabla, ajusta esto
            return jsonify({'status': 'success', 'redirect': url_for('index')})
>>>>>>> cc5fca49f18fdc94f88953a7feee20a7088a2add
        else:
            return jsonify({'status': 'error', 'message': 'Nombre de usuario o contraseña incorrectos'})
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario = request.form.get('new_usuario', '').strip()
        new_password = request.form.get('new_contrasena', '').strip()

        # Validar si los campos están vacíos
        if not usuario or not new_password:
            return jsonify({'message': 'Faltan datos'}), 400

        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

        # Insertar nuevo usuario en la base de datos
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO login (usuario, contrasena) VALUES (?, ?)", (usuario, hashed_password))
            conn.commit()
            conn.close()
            return jsonify({'message': 'Usuario registrado con éxito'}), 201
        except sqlite3.IntegrityError:
            return jsonify({'message': 'El nombre de usuario ya está en uso'}), 400

    return render_template('register.html')

    if request.method == 'POST':
        usuario = request.form.get('new_usuario', '').strip()
        new_password = request.form.get('new_contrasena', '').strip()

        # Validar si los campos están vacíos
        if not usuario or not new_password:
            return jsonify({'message': 'Faltan datos'}), 400

        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

        # Insertar nuevo usuario en la base de datos
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO login (usuario, contrasena) VALUES (?, ?)", (usuario, hashed_password))
            conn.commit()
            conn.close()
            return jsonify({'message': 'Usuario registrado con éxito'}), 201
        except sqlite3.IntegrityError:
            return jsonify({'message': 'El nombre de usuario ya está en uso'}), 400

    return render_template('register.html')

if __name__ == '__main__':
    init_db()
<<<<<<< HEAD
    app.run(debug=True)
=======
    app.run(debug=True)
>>>>>>> cc5fca49f18fdc94f88953a7feee20a7088a2add
