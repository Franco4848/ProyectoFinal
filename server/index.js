import express from 'express'
import logger from 'morgan'

const port = process.env.PORT ?? 3000

const app = express () //Inicializo la aplicación sin llamar a nada.
app.use(logger('dev'))

app.get('/', (req, res) =>{
    res.sendFile(process.cwd() + '/templates/mensajes.html') 
    // cwd = current working directory (carpeta donde se ha inicializado el proceso)
    // res.send('<h1>Este es el chat</h1>')
})

app.listen(port, () => {
    console.log('Server running on port ${port}')
})
