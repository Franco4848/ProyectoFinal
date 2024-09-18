from flask import Flask, render_template
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

@app.route('/')
def chat():
    return render_template('mensajes.html')

#Para que el server este pendiente a la escucha de los eventos:

@socketio.on('message') #Cuando escuche un evento llamado message que va a venir del cliente que haga algo.
def handleMessage(msg):
    print("Mensaje: " + msg)

if __name__ == '__main__':
    socketio.run(app)