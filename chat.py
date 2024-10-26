from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
import sqlite3, io
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

def execute_query(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result


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
            # print('entro')
            # session['rol'] = user['rol']  # Si tienes un rol en tu tabla, ajusta esto
            return jsonify({'status': 'success', 'redirect': url_for('index')})
            # return redirect(url_for('index'))

            # print('entro')
            # session['rol'] = user['rol']  # Si tienes un rol en tu tabla, ajusta esto
            return jsonify({'status': 'success', 'redirect': url_for('index')})
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

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    session.clear()  # Limpiar toda la sesión
    # flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('login'))   

# Rutas de manejo de chats
@app.route('/buscar_usuarios', methods=['GET'])
def search_users():
    query = request.args.get('query', '')
    try:
        if query:
            users = execute_query("SELECT id, first_name, alias_name FROM users WHERE first_name LIKE ? OR alias_name LIKE ?", 
                                  (f'%{query}%', f'%{query}%'))
            users_list = [{'id': user['id'], 'first_name': user['first_name'], 'alias_name': user['alias_name']} for user in users]
            return jsonify(users_list)
        else:
            return jsonify([])  # Lista vacía si no hay búsqueda
    except sqlite3.DatabaseError as db_err:
        print(f"Error en la base de datos: {db_err}")
        return jsonify({'error': 'Error al buscar usuarios en la base de datos'}), 500
    except Exception as e:
        print(f"Error desconocido: {e}")
        return jsonify({'error': 'Error desconocido'}), 500

@app.route('/verificar_conversacion', methods=['GET'])
def check_conversation():
    user_id = request.args.get('user_id')
    try:
        conversation = execute_query("SELECT id FROM conversations WHERE id IN (SELECT conversation_id FROM participants WHERE user_id = ?)", 
                                     (user_id,))
        if conversation and len(conversation) > 0:
            return jsonify({'exists': True, 'id': conversation[0]['id']})
        return jsonify({'exists': False})
    except sqlite3.DatabaseError as db_err:
        print(f"Error en la base de datos: {db_err}")
        return jsonify({'error': 'Error al verificar conversación en la base de datos'}), 500
    except Exception as e:
        print(f"Error desconocido: {e}")
        return jsonify({'error': 'Error desconocido'}), 500


@app.route('/get_messages', methods=['GET'])
def get_messages():
    conversation_id = request.args.get('conversation_id')
    try:
        messages = execute_query("SELECT user_id, content, timestamp FROM messages WHERE conversation_id = ?", 
                                 (conversation_id,))
        messages_list = []
        for msg in messages:
            messages_list.append({
                'user_id': msg['user_id'],
                'content': msg['content'],
                'timestamp': msg['timestamp'],
                'class': 'active-chat-item'  # Añadiendo la clase aquí
            })
        return jsonify(messages_list)
    except sqlite3.DatabaseError as db_err:
        print(f"Error en la base de datos: {db_err}")
        return jsonify({'error': 'Error al obtener los mensajes en la base de datos'}), 500
    except Exception as e:
        print(f"Error desconocido: {e}")
        return jsonify({'error': 'Error desconocido'}), 500



@app.route('/user_image/<int:user_id>')
def user_image(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT profile_picture FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()

        if result and result['profile_picture']:
            image_blob = result['profile_picture']
            return send_file(io.BytesIO(image_blob), mimetype='image/jpeg')
        
        # Si no tiene imagen, devolvemos la predeterminada
        return redirect(url_for('static', filename='img/default.jpg'))
    except sqlite3.DatabaseError as db_err:
        print(f"Error en la base de datos al obtener imagen: {db_err}")
        return jsonify({'error': 'Error al obtener imagen de perfil'}), 500
    except Exception as e:
        print(f"Error desconocido: {e}")
        return jsonify({'error': 'Error desconocido'}), 500

@app.route('/crear_conversacion', methods=['POST'])
def crear_conversacion():
    try:
        nombre = request.json.get('nombre')
        if nombre:
            query = "INSERT INTO conversations (name) VALUES (?)"
            execute_query(query, (nombre,))
            return jsonify({'status': 'Conversación creada exitosamente'}), 201
        else:
            return jsonify({'error': 'El nombre es requerido'}), 400
    except sqlite3.DatabaseError as db_err:
        print(f"Error en la base de datos: {db_err}")
        return jsonify({'error': 'Error al crear la conversación en la base de datos'}), 500
    except Exception as e:
        print(f"Error desconocido: {e}")
        return jsonify({'error': 'Error desconocido al crear la conversación'}), 500

# Ruta para verificar usuario
@app.route('/verificar_usuario', methods=['POST'])
def verificar_usuario():
    data = request.json
    usuario = data.get('usuario')
    contrasena = data.get('contrasena')
    
    if usuario and contrasena:
        autenticado = execute_query("SELECT * FROM login WHERE usuario = ? AND contrasena = ? AND activo = 1", (usuario, contrasena))
        if autenticado:
            return jsonify({'autenticado': True}), 200
        else:
            return jsonify({'autenticado': False}), 401  # Credenciales incorrectas
    return jsonify({'error': 'Faltan parámetros'}), 400

# Ruta para crear un usuario
@app.route('/crear_usuario', methods=['POST'])
def crear_usuario():
    data = request.json
    first_name = data.get('first_name')
    alias_name = data.get('alias_name')
    email = data.get('email')
    status = data.get('status', None)
    profile_picture = data.get('profile_picture', None)
    
    if first_name and alias_name and email:
        execute_query("""
            INSERT INTO users (first_name, alias_name, email, status, profile_picture) 
            VALUES (?, ?, ?, ?, ?)
        """, (first_name, alias_name, email, status, profile_picture))
        return jsonify({'mensaje': 'Usuario creado exitosamente'}), 201
    return jsonify({'error': 'Faltan parámetros'}), 400

# Ruta para actualizar el estado de un usuario
@app.route('/actualizar_estado_usuario', methods=['PUT'])
def actualizar_estado_usuario():
    data = request.json
    user_id = data.get('user_id')
    status = data.get('status')
    last_connected = data.get('last_connected')
    
    if user_id and status and last_connected:
        execute_query("UPDATE users SET status = ?, last_connected = ? WHERE id = ?", (status, last_connected, user_id))
        return jsonify({'mensaje': 'Estado del usuario actualizado'}), 200
    return jsonify({'error': 'Faltan parámetros'}), 400

# Ruta para enviar un mensaje
@app.route('/enviar_mensaje', methods=['POST'])
def enviar_mensaje():
    data = request.json
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    content = data.get('content')
    media_type = data.get('media_type', None)
    media = data.get('media', None)
    
    if conversation_id and user_id and content:
        # Guardar el mensaje en la base de datos
        execute_query("""
            INSERT INTO messages (conversation_id, user_id, content, media_type, media) 
            VALUES (?, ?, ?, ?, ?)
        """, (conversation_id, user_id, content, media_type, media))
        
        # Retornar el mensaje guardado para mostrarlo en la interfaz
        return jsonify({
            'mensaje': 'Mensaje enviado exitosamente',
            'data': {
                'user_id': user_id,
                'content': content,
                'timestamp': datetime.now().isoformat(),  # Marca de tiempo actual
                'media_type': media_type,
                'media': media
            }
        }), 201
    
    return jsonify({'error': 'Faltan parámetros'}), 400


# Ruta para agregar un participante a una conversación
@app.route('/agregar_participante', methods=['POST'])
def agregar_participante():
    data = request.json
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    
    if conversation_id and user_id:
        execute_query("INSERT INTO participants (conversation_id, user_id) VALUES (?, ?)", (conversation_id, user_id))
        return jsonify({'mensaje': 'Participante agregado exitosamente'}), 201
    return jsonify({'error': 'Faltan parámetros'}), 400

@app.route('/chat')
def chat():
    # Asegúrate de que 'user_id' esté en la sesión
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirigir si no está autenticado

    return render_template('index.html', user_id=session['user_id'])


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
