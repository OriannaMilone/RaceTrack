-- Extensión para generar UUID automáticamente
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear la base de datos
CREATE DATABASE racetrack;

-- Tabla Piloto con UUID
CREATE TABLE Piloto (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre TEXT NOT NULL,
    numeroCompeticion INTEGER UNIQUE NOT NULL
);

-- Tabla Equipo
CREATE TABLE Equipo (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombreEscuderia TEXT NOT NULL
);

-- Tabla ParticipacionEquipo (Relación entre Piloto y Equipo por temporada)
CREATE TABLE ParticipacionEquipo (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_piloto UUID NOT NULL,
    id_equipo UUID NOT NULL,
    temporada INTEGER NOT NULL,
    CONSTRAINT fk_piloto FOREIGN KEY (id_piloto) REFERENCES Piloto(id),
    CONSTRAINT fk_equipo FOREIGN KEY (id_equipo) REFERENCES Equipo(id)
);

-- Tabla Carrera
CREATE TABLE Carrera (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tipo TEXT NOT NULL, 
    temporada INTEGER NOT NULL,
    circuito TEXT NOT NULL,
    nombre TEXT NOT NULL
);

-- Tabla ParticipacionCarrera (Relación entre Piloto y Carrera)
CREATE TABLE ParticipacionCarrera (
    id_piloto UUID NOT NULL,
    id_carrera UUID NOT NULL,
    dnf BOOLEAN NOT NULL,
    posicionInicio INTEGER NOT NULL,
    posicionFinal INTEGER,
    PRIMARY KEY (id_piloto, id_carrera), -- Clave compuesta para evitar duplicados
    CONSTRAINT fk_piloto_carrera FOREIGN KEY (id_piloto) REFERENCES Piloto(id),
    CONSTRAINT fk_carrera FOREIGN KEY (id_carrera) REFERENCES Carrera(id)
);

-- Tabla Vuelta (Cada vuelta de cada piloto en una carrera)
CREATE TABLE Vuelta (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_piloto UUID NOT NULL,
    id_carrera UUID NOT NULL,
    numeroVuelta INTEGER NOT NULL,
    posicion INTEGER NOT NULL,
    tiempoVuelta INTERVAL,
    sector1Tiempo INTERVAL, 
    sector2Tiempo INTERVAL, 
    sector3Tiempo INTERVAL, 
    compuestoNeumático INTERVAL,
    mejorVueltaPersonal BOOLEAN NOT NULL,
    CONSTRAINT fk_piloto_vuelta FOREIGN KEY (id_piloto) REFERENCES Piloto(id),
    CONSTRAINT fk_carrera_vuelta FOREIGN KEY (id_carrera) REFERENCES Carrera(id)
);

-- Tabla ParadaEnBoxes (Cada pit stop de cada piloto en una carrera)
CREATE TABLE ParadaEnBoxes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_piloto UUID NOT NULL,
    id_carrera UUID NOT NULL,
    id_vuelta_entra UUID NOT NULL,
    id_vuelta_sale UUID,
    tiempoEntrada INTERVAL,
    tiempoSalida INTERVAL,
    duracionParada INTERVAL,
    tipoParada TEXT,
    CONSTRAINT fk_piloto_pitstop FOREIGN KEY (id_piloto) REFERENCES Piloto(id),
    CONSTRAINT fk_carrera_pitstop FOREIGN KEY (id_carrera) REFERENCES Carrera(id),
    CONSTRAINT fk_vuelta_entrada FOREIGN KEY (id_vuelta_entra) REFERENCES Vuelta(id),
    CONSTRAINT fk_vuelta_salida FOREIGN KEY (id_vuelta_sale) REFERENCES Vuelta(id)
);

CREATE TABLE carreras_programadas (
    id SERIAL PRIMARY KEY,
    circuito VARCHAR(100) NOT NULL,
    vueltas INTEGER NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    temporada VARCHAR(10) NOT NULL,                      
    gran_premio VARCHAR(100) NOT NULL,                
    nombre_csv VARCHAR(150) NOT NULL,                  
    hacer_prediccion BOOLEAN DEFAULT false,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);