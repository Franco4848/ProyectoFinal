from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os
import bcrypt

app = Flask(__name__)
load_dotenv()

UPLOAD_FOLDER = os.path.join('static', 'uploads')


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = '4848'

mysql = MySQL(app)

#@app.route("/")
#def add():
#    return render_template("muro.html") 


@app.route("/add_post",methods= ["GET", "POST"])
def add_post():
    if request.method =="POST":
        titulo= request.form["titulo"]
        imagen= request.files["imagen"]
        descripcion= request.form["descripcion"]
        if imagen:
            # Guardar la imagen en el servidor
            filename = secure_filename(imagen.filename)
            imagen.save(os.path.join(os.path.abspath(app.config['UPLOAD_FOLDER']), filename))
            # Guardar la ruta en la base de datos
            #image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_path = filename

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO publi (titulo, imagen, descripcion) VALUES (%s, %s, %s)", 
                    (titulo, image_path, descripcion))
        mysql.connection.commit()

    return redirect(url_for("muro"))

@app.route("/add_comment/<int:publi_id>",methods= ["GET", "POST"])
def add_comment(publi_id):
    if request.method =="POST":
        descripcion= request.form["descripcion"]
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO comentarios (descripcion, publi_id)VALUES(%s, %s)",
        (descripcion,publi_id))
        mysql.connection.commit()
    return redirect(url_for("muro"))



@app.route('/comentarios')
def comentarios():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM comentarios")
    data = cur.fetchall()
    return render_template( 'comments.html', clientes = data)

@app.route('/muro')
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


if __name__ == '__main__':
    app.run(port=3000, debug=True)