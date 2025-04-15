const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

require('dotenv').config();

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

const session = require('express-session');
const pool = require('./web_project/backend/db'); 

app.use(session({
  secret: 'clave-super-secreta',  
  resave: false,
  saveUninitialized: false,
}));

function verificarAdmin(req, res, next) {
  if (req.session && req.session.usuario === 'admin') {
    return next();
  } else {
    res.status(403).send(`
      <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        background-color: #111;
        color: white;
        font-family: sans-serif;
        flex-direction: column;
      ">
        <h1 style="color: #e10600;">Access Denied</h1>
        <p>Incorrect <strong>credentials</strong> to access.</p>
        <a href="/login" style="
          margin-top: 20px;
          padding: 10px 20px;
          background-color: #e10600;
          color: white;
          text-decoration: none;
          border-radius: 5px;
        ">Go back to Login</a>
      </div>
    `);
    
  }
}

// Servir frontend
app.use(express.static(path.join(__dirname, 'web_project', 'public')));

// app.get('/admin', (req, res) => {
//   res.sendFile(path.join(__dirname, 'web_project', 'views', 'admin.html'));
// });

app.get('/admin', verificarAdmin, (req, res) => {
  res.sendFile(path.join(__dirname, 'web_project', 'views', 'admin.html'));
});


app.get('/login', (req, res) => {
  res.sendFile(path.join(__dirname, 'web_project', 'views', 'login.html'));
});



app.post('/login', async (req, res) => {
  const { username, password } = req.body;

  try {
    const query = `
      SELECT * FROM usuarios_admin
      WHERE username = $1
      AND password_hash = crypt($2, password_hash)
    `;
    const result = await pool.query(query, [username, password]);

    if (result.rows.length > 0) {
      req.session.usuario = 'admin';
      console.log('✅ Login correcto desde la base de datos');
      res.redirect('/admin');
    } else {
      console.log('❌ Login fallido');
      res.status(403).send(`
        <div style="
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100vh;
          background-color: #111;
          color: white;
          font-family: sans-serif;
          flex-direction: column;
        ">
          <h1 style="color: #e10600;">Access Denied</h1>
          <p>Incorrect <strong>credentials</strong> to access.</p>
          <a href="/login" style="
            margin-top: 20px;
            padding: 10px 20px;
            background-color: #e10600;
            color: white;
            text-decoration: none;
            border-radius: 5px;
          ">Go back to Login</a>
        </div>
      `);
    }

  } catch (err) {
    console.error('❌ Error al validar login:', err);
    res.status(500).send('Internal server error');
  }
});


app.get('/logout', (req, res) => {
  req.session.destroy(() => {
    res.redirect('/');
  });
});

// WebSocket: cuando se conecta un cliente (el frontend)
io.on('connection', (socket) => {
  console.log('Cliente conectado');

  socket.on('disconnect', () => {
    console.log('Cliente desconectado');
  });
});

// WebSocket: cuando el simulador envía una vuelta
io.of('/simulador').on('connection', (socket) => {
  console.log('🚗 Simulador conectado');

  socket.on('disconnect', () => {
    console.log('💥 Simulador desconectado');
  });

  socket.on('nueva-vuelta', (data) => {
    console.log(`📩 Vuelta ${data.vuelta} recibida con ${data.pilotos.length} pilotos`);
    io.emit('nueva-vuelta', data);
  });

  socket.on('prediccion-vuelta', (data) => {
      console.log(`🔮 Predicción recibida para vuelta ${data.vuelta}`);
      io.of('/').emit('prediccion-vuelta', data);  
  });

});


server.listen(3000, () => {
  console.log('Servidor corriendo en http://localhost:3000');
});
