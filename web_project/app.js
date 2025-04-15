const express = require('express');
const path = require('path');
const app = express();

// app.use(express.static(path.join(__dirname, 'web_project')));
app.use(express.static('public'));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Ruta protegida
// app.get('/admin', verificarAdmin, (req, res) => {
app.get('/admin', (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'admin.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Servidor corriendo en http://localhost:${PORT}`);
});