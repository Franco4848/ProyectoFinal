from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_socketio import SocketIO, send

from flask_mysqldb import MySQL
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os
import bcrypt
# pip install flask-login
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
import locale
locale.setlocale(locale.LC_TIME, 'es_AR.UTF-8')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)
load_dotenv()

@app.route('/chat')
#@login_required
def chat():
    return render_template('mensajes.html')

#Para que el server este pendiente a la escucha de los eventos:
@socketio.on('message') #Cuando escuche un evento llamado message que va a venir del cliente que haga algo.
def handleMessage(msg):
    print("Mensaje: " + msg)
    send(msg, broadcast = True) #Para reenviar el mensaje a todos los clientes (Las demas pestañas).
    return msg

# Muro
UPLOAD_FOLDER = os.path.join('static', 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

PERFIL_UPLOADS= os.path.join('static', 'perfil_uploads')
ALLOWED_EXTENSIONS= {'jpg'}
app.config['PERFIL_UPLOADS'] = PERFIL_UPLOADS

app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = '4848'

mysql = MySQL(app)

#----CONFIGURACIÓN FLASK-LOGIN----#
app.secret_key= "claveclaveclave"
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor inicie sesión para acceder a esta página."

#----MODELO DE USUARIO----#
class User(UserMixin):
    def __init__(self, id_usuario, nombre_completo, username, email, contraseña):
        self.id = id_usuario
        self.nombre_completo = nombre_completo
        self.username= username
        self.email = email
        self.contraseña = contraseña

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor() 
    cur.execute('SELECT id_usuario, nombre_completo, username, email, contraseña FROM usuario WHERE id_usuario = %s', (user_id,))
    usuario = cur.fetchone()
    cur.close()
    if usuario:
        return User(usuario['id_usuario'], usuario['nombre_completo'], usuario['username'], usuario['email'], usuario['contraseña'])
    return None

@app.route('/login', methods= ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('muro'))
    if request.method == 'POST':
        email= request.form['email']
        contraseña = request.form["contraseña"]

        cur= mysql.connection.cursor()
        cur.execute('SELECT * FROM usuario WHERE email = %s AND contraseña = %s', (email, contraseña))
        usuario= cur.fetchone()
        cur.close()

        if usuario:
            user_obj = User(usuario['id_usuario'], usuario['nombre_completo'], usuario['username'], usuario['email'], usuario['contraseña'])
            login_user(user_obj)
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('muro'))
        else:
            flash('Email o contraseña incorrectos. Por favor, intenta nuevamente.', 'error')
            return render_template('login.html', email= email, contraseña= contraseña )
    else:
        return render_template('login.html')
    
def validarEmail(cur, email):
    cur.execute('SELECT * FROM usuario where email = %s', (email,))
    email_existente= cur.fetchone()
    if email_existente:
        return False
    else:
        return True

def validarUsername(cur, username, id_usuario=None):
    if id_usuario:
        cur.execute('SELECT * FROM usuario WHERE username = %s AND id_usuario != %s', (username, id_usuario))
    else:
        cur.execute('SELECT * FROM usuario WHERE username = %s', (username,))
    username_existente= cur.fetchone()
    if username_existente:
        return False
    else:
        return True

def calculoEdad(fechaNac):
    fecha= datetime.strptime(str(fechaNac), '%Y-%m-%d')
    fecha_perfil= f'{fecha.day} de {fecha.strftime('%B')} de {fecha.year}'
    edad = datetime.now().year - fecha.year
    if datetime.now().month < fecha.month:
        edad -= 1
    elif datetime.now().month == fecha.month:
        if datetime.now().day < fecha.day:
            edad -= 1
        else:
            edad= edad
    else:
        edad= edad
    return edad, fecha_perfil

def validarContraseña(contraseña):
    minuscula= any(caracter.islower() for caracter in contraseña)
    mayuscula= any(caracter.isupper() for caracter in contraseña)
    numero= any(caracter.isdigit() for caracter in contraseña)
    espacio_contraseña= any(caracter.isspace() for caracter in contraseña)
    if minuscula == False or mayuscula == False or numero == False or espacio_contraseña == True:
        return False
    else:
        return True
    
@app.route('/registro', methods= ["GET", "POST"])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('muro'))
    cur= mysql.connection.cursor()
    if request.method == 'POST':
        nombre_completo= request.form['nombre_completo']
        username= request.form['username']
        email= request.form['email']
        fechaNac= request.form['fechaNac']
        contraseña= request.form['contraseña']
        contraseña2= request.form['contraseña2']

        edad, _ = calculoEdad(fechaNac)

        flash_msg= None
        if validarUsername(cur, username) == False:
            flash_msg= 'Este nombre de usuario no está disponible, prueba con otro.'
        elif validarEmail(cur, email) == False:
            flash_msg= 'Este correo electrónico ya está en uso, prueba con otro.'
        elif edad < 18:
            flash_msg= 'No es posible crear la cuenta en este momento.'
        elif validarContraseña(contraseña) == False:
            flash_msg= 'La contraseña debe incluir números y letras tanto mayúsculas como minúsculas sin espacios.'
        elif contraseña != contraseña2:
            flash_msg= 'Las contraseñas no coinciden, intente de nuevo.'
        if flash_msg:
            flash(flash_msg, 'error')
            return render_template('registro.html', nombre_completo= nombre_completo, username= username, email= email,
                                   fechaNac= fechaNac, contraseña= contraseña, contraseña2= contraseña2)
        else:
            cur.execute('''INSERT INTO usuario (nombre_completo, username, email, fechaNac, contraseña)
                         VALUES (%s, %s, %s, %s, %s)''', (nombre_completo, username, email, fechaNac, contraseña))
            mysql.connection.commit()
            nuevo_usuario_id = cur.lastrowid
            cur.close()
            user_obj = User(nuevo_usuario_id, nombre_completo, username, email, contraseña)
            login_user(user_obj)
            flash('Registro exitoso. ¡Bienvenido!', 'success')
            return redirect(url_for('muro'))
    else:
        return render_template('registro.html')

@app.route('/logout', methods= ["POST", "GET"])
@login_required
def logout():
    if request.method == "POST":
        logout_user()
        flash('Ha cerrado sesión', 'success')
        return redirect(url_for('login'))
    else:
        flash('No fue posible cerrar sesión', 'error')
        return redirect(url_for('muro'))

@app.route("/add_post",methods= ["GET", "POST"])
#@login_required
def add_post():
    if request.method =="POST":
        titulo= request.form["titulo"]
        imagen= request.files["imagen"]
        descripcion= request.form["descripcion"]
        id_usuario = current_user.id
        if imagen:
            # Guardar la imagen en el servidor
            filename = secure_filename(imagen.filename)
            imagen.save(os.path.join(os.path.abspath(app.config['UPLOAD_FOLDER']), filename))
            # Guardar la ruta en la base de datos
            #image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_path = filename

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO publi (titulo, imagen, descripcion, id_usuario) VALUES (%s, %s, %s, %s)", 
                    (titulo, image_path, descripcion, id_usuario))
        mysql.connection.commit()

    return redirect(url_for("muro"))

@app.route("/add_comment/<int:publi_id>",methods= ["GET", "POST"])
#@login_required
def add_comment(publi_id):
    if request.method =="POST":
        descripcion= request.form["descripcion"]
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO comentarios (descripcion, publi_id)VALUES(%s, %s)",
        (descripcion,publi_id))
        mysql.connection.commit()
    return redirect(request.referrer or url_for('muro'))
#si haces un comentario vacio se guarda igual


@app.route('/comentarios')
#@login_required
def comentarios():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM comentarios")
    data = cur.fetchall()
    return render_template( 'comments.html', clientes = data)

@app.route('/muro')
#@login_required
def muro():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.id, p.titulo, p.imagen, p.descripcion, c.descripcion AS comentario 
        FROM publi p
        LEFT JOIN comentarios c ON p.id = c.publi_id
        ORDER BY p.id
    """)
    
    rows = cur.fetchall()
    
    if rows:
        publicaciones = {}
        
        for row in rows:
            publi_id = row['id']
            if publi_id not in publicaciones:
                publicaciones[publi_id] = {
                    'id': publi_id,
                    'titulo': row['titulo'],
                    'imagen': row['imagen'],
                    'descripcion': row['descripcion'],
                    'comentarios': []
                }
            if row['comentario']:
                publicaciones[publi_id]['comentarios'].append(row['comentario'])

        publicaciones_list = list(publicaciones.values())
    else:
        publicaciones_list = []

    return render_template('muro.html', clientes=publicaciones_list)


@app.route('/support')
#@login_required
def suppot():
    return render_template('support.html')

def extension_permitida(archivo):
    return '.' in archivo and \
           archivo.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/perfil/<id_usuario>', defaults= {'id_publicacion' : None})
@app.route('/perfil/<id_usuario>/<id_publicacion>')
@login_required
def perfil(id_usuario, id_publicacion):

    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT u.*, p.id AS pub_id, p.titulo, p.imagen, p.descripcion, c.descripcion AS comentario 
        FROM usuario u 
        LEFT JOIN publi p ON u.id_usuario = p.id_usuario 
        LEFT JOIN comentarios c ON p.id = c.publi_id 
        WHERE u.id_usuario = %s
    ''', (id_usuario,))
    resultados= cur.fetchall()
    cur.close()

    if resultados:
        usuario= resultados[0]
        publicaciones_dict= {}
        publicaciones_list= []

        for resultado in resultados:
            publi_id= resultado['pub_id']

            if publi_id is not None and publi_id not in publicaciones_dict:
                publicaciones_dict[publi_id] = {
                        'publi_id': publi_id,
                        'titulo': resultado['titulo'],
                        'imagen': resultado['imagen'],
                        'descripcion': resultado['descripcion'],
                        'comentarios': []
                }
                publicaciones_list.append(publicaciones_dict[publi_id])

            if resultado['comentario']:
                publicaciones_dict[publi_id]['comentarios'].append(resultado['comentario'])

        edad, fecha_perfil = calculoEdad(usuario['fechaNac'])
        
        publicacion_individual = None
        if id_publicacion:
            for publi in publicaciones_list:
                if int(publi['publi_id']) == int(id_publicacion):
                    publicacion_individual= publi
                    break

        return render_template('perfil.html', datos= usuario, publicaciones = publicaciones_list, 
                            edad = edad, fecha_perfil = fecha_perfil, publicacion_individual = publicacion_individual)
    else:
        return render_template('perfil.html', datos= [])

@app.route('/editarPerfil', methods= ['GET', 'POST'])
@login_required
def editarPerfil():
    cur= mysql.connection.cursor()
    id_usuario= current_user.id

    if request.method == 'POST':
        nombre_completo= request.form['nombre_completo']
        username= request.form['username']
        email= request.form['email']
        fotoPerfil= request.files['fotoPerfil']
        fechaNac= request.form['fechaNac']
        presentacion= request.form['presentacion']
        ubicacion= request.form['ubicacion']
        enlace= request.form['enlace']
        mostrarSiNo= request.form['mostrarSiNo']
        eliminar_foto= request.form.get('eliminar_foto')
        foto_actual= request.form['fotoActual']

        if eliminar_foto:
            os.remove(os.path.join(app.config['PERFIL_UPLOADS'], foto_actual ))
            filename = None
        elif fotoPerfil and fotoPerfil.filename != '' :
            if extension_permitida(fotoPerfil.filename):
                filename= secure_filename(fotoPerfil.filename)
                fotoPerfil.save(os.path.join(app.config['PERFIL_UPLOADS'], filename))
            else:
                flash('Formato de imagen no permitido.', 'error')
                return redirect(url_for('editarPerfil'))
        else:
            filename= foto_actual
            
        if validarUsername(cur, username, id_usuario) == False:
            flash('El nombre de usuario ya está en uso, prueba con otro.', 'error')
            return render_template('editarPerfil.html', nombre_completo= nombre_completo, username= username, email= email, 
                                    fotoPerfil= filename, fechaNac= fechaNac, presentacion= presentacion, ubicacion= ubicacion,
                                    enlace= enlace, mostrarSiNo= mostrarSiNo, id_usuario= id_usuario)
        else:
            cur.execute('''UPDATE usuario SET nombre_completo = %s, username = %s, fotoPerfil = %s, presentacion = %s,
                            ubicacion = %s, enlace = %s, mostrarSiNo = %s WHERE id_usuario = %s''', (nombre_completo, username, filename, 
                                                                                    presentacion, ubicacion, enlace, mostrarSiNo, id_usuario))
            mysql.connection.commit()
            flash('Tu perfil fue actualizado.', 'success')
            cur.close()
            return redirect(url_for('perfil', id_usuario= id_usuario))
    else:
        cur.execute('SELECT * FROM usuario WHERE id_usuario = %s', (id_usuario,))
        datos= cur.fetchone()
        cur.close()
        return render_template('editarPerfil.html', nombre_completo= datos['nombre_completo'], username= datos['username'], 
                               email= datos['email'], fotoPerfil= datos['fotoPerfil'], fechaNac= datos['fechaNac'], presentacion= datos['presentacion'], 
                               ubicacion= datos['ubicacion'], enlace= datos['enlace'], mostrarSiNo= datos['mostrarSiNo'], id_usuario= datos['id_usuario'])

if __name__ == '__main__':
    socketio.run(app, debug= True)
    #app.run(port=3000, debug=True)
