const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

// Servir frontend
app.use(express.static(path.join(__dirname, 'web_project', 'public')));

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
      io.of('/').emit('prediccion-vuelta', data);  // 👈 Aquí agregalo
  });

});


server.listen(3000, () => {
  console.log('Servidor corriendo en http://localhost:3000');
});
