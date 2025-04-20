const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

require('dotenv').config();

app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));
app.use(express.json());

const session = require('express-session');
const pool = require('./web_project/backend/db'); 

const cron = require('node-cron');
const { exec } = require('child_process');

let simulacionEnCurso = false;

cron.schedule('* * * * *', async () => {
  console.log("Cron job ejecutado a:", new Date());

  if (simulacionEnCurso) {
    console.log("Ya hay una simulación en curso, no se lanza otra.");
    return;
  }

  try {
    const ahora = new Date();
    console.log("Fecha actual:", ahora.toISOString());

    const result = await pool.query(`
      SELECT *, fecha + hora AS fecha_hora
      FROM carreras_programadas
      WHERE (fecha + hora) <= CURRENT_TIMESTAMP
        AND (fecha + hora) > CURRENT_TIMESTAMP - interval '1 minute'
      ORDER BY (fecha + hora)
      LIMIT 1;
    `);

    console.log("Resultado de la query:", result.rows);

    if (result.rows.length === 0) {
      console.log("No hay carreras programadas para este minuto.");
      return;
    }

    const carrera = result.rows[0];
    const fechaHoraCarrera = new Date(carrera.fecha_hora);
    console.log("Fecha y hora exacta de la carrera (usando fecha_hora):", fechaHoraCarrera.toISOString());


    const ahoraRedondeado = new Date(ahora);
    ahoraRedondeado.setSeconds(0, 0);
    console.log("Fecha actual redondeada:", ahoraRedondeado.toISOString());

    const diferencia = Math.abs(fechaHoraCarrera.getTime() - ahoraRedondeado.getTime());

    if (diferencia <= 1000 * 60) {
      console.log(`Hora de lanzar la simulación para ${carrera.gran_premio} (${carrera.nombre_csv})`);

      const simuladorPath = __dirname;
      const comando = `python -m race_simulator.simulator ${carrera.nombre_csv}`;

      simulacionEnCurso = true;

      exec(comando, { cwd: simuladorPath }, (error, stdout, stderr) => {
        if (error) {
          console.error('Error al ejecutar simulador:', error);
          console.error('STDERR:', stderr);
          simulacionEnCurso = false;
          return;
        }
        console.log('✅ Simulación lanzada correctamente');
        console.log('STDOUT:', stdout);
        simulacionEnCurso = false;
      });

    } else {
      console.log("La diferencia de tiempo es mayor a 1 minuto, no se lanza simulación.");
    }

  } catch (err) {
    console.error("Error al verificar la carrera programada:", err);
  }
});


app.get('/api/next-race', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT *,
       fecha + hora AS fecha_hora
        FROM carreras_programadas
        WHERE (fecha + hora) > CURRENT_TIMESTAMP
        ORDER BY (fecha + hora) ASC
        LIMIT 1
    `);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'No upcoming race scheduled' });
    }

    const race = result.rows[0];

    res.json({
      fecha: race.fecha_hora,
      circuito: race.circuito,
      gran_premio: race.gran_premio,
      nombre_csv: race.nombre_csv,
      hacer_prediccion: race.hacer_prediccion,
      vueltas: race.vueltas
    });
  } catch (error) {
    console.error(' Error fetching next race:', error); 
    res.status(500).json({ error: 'Internal server error' });
  }
});



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

app.get('/admin/carreras', verificarAdmin, async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT id, gran_premio, temporada, hacer_prediccion, fecha, hora 
      FROM carreras_programadas
      ORDER BY fecha, hora
    `);
    res.json(result.rows);
  } catch (err) {
    console.error('❌ Error al obtener carreras:', err);
    res.status(500).json({ error: 'Error loading races' });
  }
});


app.get('/admin/carreras/:id/editar', verificarAdmin, async (req, res) => {
  const carreraId = req.params.id;

  try {
    const result = await pool.query('SELECT * FROM carreras_programadas WHERE id = $1', [carreraId]);

    if (result.rows.length === 0) {
      return res.status(404).send('Carrera no encontrada');
    }

    const carrera = result.rows[0];

    res.send(`
      <html>
      <head><title>Edit Race</title></head>
      <body style="font-family: sans-serif; background-color: #111; color: white; padding: 40px;">
        <h2>Edit Race: ${carrera.gran_premio} (${carrera.temporada})</h2>
        <form action="/admin/carreras/${carrera.id}/editar" method="POST">
          <label>Time:</label><br>
          <input type="time" name="hora" value="${carrera.hora.slice(0,5)}" required><br><br>

          <label>
            <input type="checkbox" name="hacer_prediccion" ${carrera.hacer_prediccion ? 'checked' : ''}>
            Enable predictions
          </label><br><br>

          <button type="submit">Save Changes</button>
          <a href="/admin" style="margin-left: 20px; color: #e10600;">Cancel</a>
        </form>
      </body>
      </html>
    `);
  } catch (err) {
    console.error('❌ Error al cargar carrera para edición:', err);
    res.status(500).send('Internal server error');
  }
});

app.post('/admin/carreras/:id/editar', verificarAdmin, async (req, res) => {
  const carreraId = req.params.id;
  const nuevaHora = req.body.hora;
  const hacerPrediccion = req.body.hacer_prediccion === 'on';

  try {
    await pool.query(
      'UPDATE carreras_programadas SET hora = $1, hacer_prediccion = $2 WHERE id = $3',
      [nuevaHora, hacerPrediccion, carreraId]
    );
    console.log(`✏️ Carrera ${carreraId} actualizada`);
    res.redirect('/admin');
  } catch (err) {
    console.error('❌ Error al editar carrera:', err);
    res.status(500).send('Internal server error');
  }
});


app.post('/admin/carreras/:id/eliminar', verificarAdmin, async (req, res) => {
  const carreraId = req.params.id;

  try {
    await pool.query('DELETE FROM carreras_programadas WHERE id = $1', [carreraId]);
    console.log(`🗑️ Carrera ${carreraId} eliminada correctamente`);
    res.redirect('/admin');
  } catch (err) {
    console.error('❌ Error al eliminar carrera:', err);
    res.status(500).send('Internal server error');
  }
});


app.post('/admin/programar', verificarAdmin, async (req, res) => {
  const {circuito, vueltas, fecha, hora, temporada, temporada_base_simulacion, gran_premio, predicciones } = req.body;
  // Generar nombre del CSV automáticamente
  const nombre_csv = `${circuito.split(' ').join('_')}_${temporada_base_simulacion}_full_H_data.csv`;

  try {
    const query = `
      INSERT INTO carreras_programadas 
      (circuito, vueltas, fecha, hora, temporada, temporada_base_simulacion, gran_premio, nombre_csv, hacer_prediccion)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    `;
    const values = [
      circuito,
      parseInt(vueltas),
      fecha,
      hora,
      temporada,
      parseInt(temporada_base_simulacion),
      gran_premio,
      nombre_csv,
      predicciones ? true : false
    ];

    await pool.query(query, values);
    console.log('✅ Carrera programada correctamente');
    res.redirect('/admin');

  } catch (err) {
    res.status(400).send(`
      <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        background-color: #111;
        color: white;
        font-family: sans-serif;
        flex-direction: column;
        text-align: center;
      ">
        <h1 style="color: #e10600;"> 🚫 Scheduling Failed</h1>
        <p>A race is already <strong>scheduled</strong> for that Grand Prix and season.</p>
        <a href="/admin" style="
          margin-top: 20px;
          padding: 10px 20px;
          background-color: #e10600;
          color: white;
          text-decoration: none;
          border-radius: 5px;
        "> ⬅ Return to Admin Race Control</a>
      </div>
    `);
    console.error('❌ Error al programar carrera:', err);
  }
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
