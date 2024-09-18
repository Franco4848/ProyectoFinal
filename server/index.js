import express from 'express'//Primero: npm install express -E
import logger from 'morgan' //Primero: npm install morgan -E
import {Server} from 'socket.io' //Primero: npm install socket.io -E
import {createServer} from 'node:http' //modulo para poder crear servidores http.

const port = process.env.PORT ?? 3000

const app = express () //Inicializo la aplicación sin llamar a nada.
const server = createServer(app) //Creamos el servidor http.
const io = new Server(server) //creamos el server de socket io
//Cuando este servidor tenga una coneccion, ejecutamos este call back:
io.on('connection', (socket) => {
    console.log('a user has connected' )
})
app.use(logger('dev'))
app.use('/static', express.static(process.cwd() + '/static')) //para que lea la carpeta de estilos.

app.get('/', (req, res) =>{
    res.sendFile(process.cwd() + '/templates/mensajes.html') 
    // cwd = current working directory (carpeta donde se ha inicializado el proceso)
    // res.send('<h1>Este es el chat</h1>')
})

server.listen(port, () => {
    console.log('Server running on port ${port}')
})
