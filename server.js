const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

const session = require('express-session');

app.use(session({
  secret: 'clave-super-secreta',  
  resave: false,
  saveUninitialized: false,
}));

function verificarAdmin(req, res, next) {
  if (req.session && req.session.usuario === 'admin') {
    return next();
  } else {
    res.status(403).send('<h3 style="color: red;">Access denied: Admins only</h3>');
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

app.post('/login', (req, res) => {
  const { username, password } = req.body;

  const validUsername = 'admin';
  const validPassword = '1234';

  if (username === validUsername && password === validPassword) {
    req.session.usuario = 'admin';  
    console.log('✅ Admin logged in');
    res.redirect('/admin');
  } else {
    console.log('❌ Invalid credentials');
    res.status(401).send('<h3 style="color: red;">Invalid username or password</h3>');
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
