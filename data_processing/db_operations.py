import pandas as pd
import uuid
from db_connection import get_connection

def format_timedelta(td):
    """Convierte Timedelta a mm:ss.SSS"""
    if pd.isna(td):
        return None
    total_seconds = td.total_seconds()
    minutes, seconds = divmod(total_seconds, 60)
    return f"{int(minutes):02}:{seconds:06.3f}"

def format_timedelta2(td):
    if pd.isna(td):
        return None  
    total_seconds = td.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{seconds:06.3f}"

def insertar_pilotos_csv(csv_files):
    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        
        dfs = [pd.read_csv(archivo) for archivo in csv_files]
        df_final = pd.concat(dfs, ignore_index=True).drop_duplicates()

        print(df_final)  

        for _, row in df_final.iterrows():
            cursor.execute(
                "INSERT INTO Piloto (id, nombre, numerocompeticion) VALUES (%s, %s, %s)",
                (str(uuid.uuid4()), row["Driver"], row["DriverNumber"])
            )

        conn.commit()
        print("Datos de pilotos insertados correctamente.")

    except Exception as e:
        print("Error al insertar datos:", e)
    finally:
        cursor.close()
        conn.close()

def insertar_equipos_csv(csv_files):
    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        
        dfs = [pd.read_csv(archivo) for archivo in csv_files]
        df_final = pd.concat(dfs, ignore_index=True)
        df_final = df_final.iloc[:, 1:]
        df_final = df_final.drop_duplicates(subset=["Team"])

        print(df_final)  

        for _, row in df_final.iterrows():
            cursor.execute(
                "INSERT INTO Equipo (id, nombreescuderia) VALUES (%s, %s)",
                (str(uuid.uuid4()), row["Team"]))
        conn.commit()
        print("Datos de equipos insertados correctamente.")    
    except Exception as e:
        print("Error al insertar datos:", e)
    finally:
        cursor.close()
        conn.close()
            
def insertar_pilotos_equipos_csv(csv_file, season):
    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        
        df = pd.read_csv(csv_file)
        print(df)  

        drivers_ids = []
        teams_ids = []
        
        for _, row in df.iterrows():
            cursor.execute("SELECT id FROM Piloto WHERE nombre=%s", (row["Driver"],))
            driver_id = cursor.fetchone()
            if driver_id:
                drivers_ids.append(driver_id[0])

            cursor.execute("SELECT id FROM Equipo WHERE nombreEscuderia=%s", (row["Team"],))
            team_id = cursor.fetchone()
            if team_id:
                teams_ids.append(team_id[0])
                
        if len(drivers_ids) != len(teams_ids):
            return "Error en la obtención de ids de pilotos y equipos."
        for i in range(len(drivers_ids)):
            cursor.execute(" INSERT INTO ParticipacionEquipo (id, id_piloto, id_equipo, temporada) VALUES (%s, %s, %s, %s)",
                (str(uuid.uuid4()), drivers_ids[i], teams_ids[i], season)
            )

        conn.commit()
        print("Datos de pilotos y equipos insertados correctamente.")

    except Exception as e:
        print("Error al insertar datos:", e)
    finally:
        cursor.close()
        conn.close()  
        
def insertar_carrera_datos(year, name, circuit, type):
    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO Carrera (id, nombre, circuito, tipo, temporada) VALUES (%s, %s, %s, %s, %s)",
            (str(uuid.uuid4()), name, circuit, type, year)
        )

        conn.commit()
        print("Datos de carrera insertados correctamente.")

    except Exception as e:
        print("Error al insertar datos:", e)
    finally:
        cursor.close()
        conn.close()
    
def insertar_estado_carrera_csv(csv_file, year):
    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        
        df = pd.read_csv(csv_file)

        df["FisingPosition"] = df["FisingPosition"].astype(int)
        df["GridPosition"] = df["GridPosition"].astype(int)
        
        print(df)
        
        cursor.execute("SELECT id FROM Carrera WHERE temporada = %s", (year,))
        race_id = cursor.fetchone()

        race_id = race_id[0]

        drivers_ids = []

        for _, row in df.iterrows():
            cursor.execute("SELECT id FROM Piloto WHERE nombre = %s", (row["Driver"],))
            driver_id = cursor.fetchone()
            if driver_id:
                drivers_ids.append(driver_id[0])


        for driver_id, (_, row) in zip(drivers_ids, df.iterrows()):
            cursor.execute(
                """INSERT INTO ParticipacionCarrera (id_piloto, id_carrera, estado, posicioninicio, posicionfinal) 
                VALUES (%s, %s, %s, %s, %s)""",
                (driver_id, race_id, row["FinialStatus"], row["GridPosition"], row["FisingPosition"])
            )

        conn.commit()
        print("Datos de estado de carrera insertados correctamente.")

    except Exception as e:
        print("Error al insertar datos:", e)
    finally:
        cursor.close()
        conn.close()
        
def insertar_vueltas_csv(csv_file, year):
    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        
        df = pd.read_csv(csv_file)
        
        df = df.drop(columns=["Team"])
        df = df.drop(columns=["TyreLife"])
        df["LapNumber"] = df["LapNumber"].astype(int)
        df["Position"] = df["Position"].fillna(0).astype(int)
        df["Compound"] = df["Compound"].fillna("TBD") #TBD --> To be defined
        
        df["LapTime"] = pd.to_timedelta(df["LapTime"], errors="coerce")
        df["Sector1Time"] = pd.to_timedelta(df["Sector1Time"], errors="coerce")
        df["Sector2Time"] = pd.to_timedelta(df["Sector2Time"], errors="coerce")
        df["Sector3Time"] = pd.to_timedelta(df["Sector3Time"], errors="coerce")

        df["LapTime"] = df["LapTime"].apply(format_timedelta)
        df["Sector1Time"] = df["Sector1Time"].apply(format_timedelta)
        df["Sector2Time"] = df["Sector2Time"].apply(format_timedelta)
        df["Sector3Time"] = df["Sector3Time"].apply(format_timedelta)
        
        print(df)
        
        cursor.execute("SELECT id FROM Carrera WHERE temporada = %s", (year,))
        race_id = cursor.fetchone()

        drivers_ids = []

        for _, row in df.iterrows():
            cursor.execute("SELECT id FROM Piloto WHERE nombre = %s", (row["Driver"],))
            driver_id = cursor.fetchone()
            if driver_id:
                drivers_ids.append(driver_id[0])


        for driver_id, (_, row) in zip(drivers_ids, df.iterrows()):
            cursor.execute(
                """INSERT INTO vuelta (id, id_piloto, id_carrera, numerovuelta, posicion, tiempovuelta, sector1tiempo, sector2tiempo, sector3tiempo, compuestoneumatico, mejorvueltapersonal) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (str(uuid.uuid4()), driver_id, race_id, row["LapNumber"], row["Position"], row["LapTime"], row["Sector1Time"], row["Sector2Time"], row["Sector3Time"], row["Compound"], row["IsPersonalBest"])
            )

        conn.commit()
        print("Datos de vuelta insertados correctamente.")

    except Exception as e:
        print("Error al insertar datos:", e)
    finally:
        cursor.close()
        conn.close()
        
def insertar_paradas_csv(csv_file):
    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()

        df = pd.read_csv(csv_file)

        df["PitInTime"] = pd.to_timedelta(df["PitInTime"], errors="coerce")
        df["PitOutTime"] = pd.to_timedelta(df["PitOutTime"], errors="coerce")
        df["PitStopDuration"] = pd.to_timedelta(df["PitStopDuration"], errors="coerce")

        df["PitInTime"] = df["PitInTime"].apply(format_timedelta2)
        df["PitOutTime"] = df["PitOutTime"].apply(format_timedelta2)
        df["PitStopDuration"] = df["PitStopDuration"].apply(format_timedelta2)
        
        for _, row in df.iterrows():
            cursor.execute("SELECT id FROM Carrera WHERE temporada = %s", (row["Season"],))
            carrera_id = cursor.fetchone()

            if not carrera_id:
                print(f"⚠ Advertencia: No se encontró la carrera para la temporada {row['Season']}")
                continue

            carrera_id = carrera_id[0]

            cursor.execute("SELECT id FROM Piloto WHERE nombre = %s", (row["Driver"],))
            piloto_id = cursor.fetchone()

            piloto_id = piloto_id[0]  

            cursor.execute("""
                SELECT id FROM Vuelta 
                WHERE id_piloto = %s AND id_carrera = %s AND numerovuelta = %s
            """, (piloto_id, carrera_id, row["LapNumber_In"]))
            vuelta_entrada_id = cursor.fetchone()

            cursor.execute("""
                SELECT id FROM Vuelta 
                WHERE id_piloto = %s AND id_carrera = %s AND numerovuelta = %s
            """, (piloto_id, carrera_id, row["LapNumber_Out"]))
            vuelta_salida_id = cursor.fetchone()

            vuelta_entrada_id = vuelta_entrada_id[0]
            vuelta_salida_id = vuelta_salida_id[0]

            cursor.execute("""
                INSERT INTO paradaboxes (id, id_piloto, id_carrera, id_vuelta_entra, id_vuelta_sale, tiempoentrada, tiemposalida, duracionparada, tipoparada)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                str(uuid.uuid4()), piloto_id, carrera_id, vuelta_entrada_id, vuelta_salida_id,
                row["PitInTime"], row["PitOutTime"], row["PitStopDuration"], "Cambio de neumáticos"  # Puedes ajustar el tipo de parada si es necesario
            ))

        conn.commit()
        print("Datos de paradas en boxes insertados correctamente.")

    except Exception as e:
        print("Error al insertar datos:", e)

    finally:
        cursor.close()
        conn.close()

def insertar_datos_full_carrera(csv_file):
    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()

        df = pd.read_csv(csv_file)

        # Convertir tiempos a INTERVAL
        df["LapTime"] = pd.to_timedelta(df["LapTime"], errors="coerce").apply(format_timedelta)
        df["Sector1Time"] = pd.to_timedelta(df["Sector1Time"], errors="coerce").apply(format_timedelta)
        df["Sector2Time"] = pd.to_timedelta(df["Sector2Time"], errors="coerce").apply(format_timedelta)
        df["Sector3Time"] = pd.to_timedelta(df["Sector3Time"], errors="coerce").apply(format_timedelta)
        df["PitInTime"] = pd.to_timedelta(df["PitInTime"], errors="coerce").apply(format_timedelta2)
        df["PitOutTime"] = pd.to_timedelta(df["PitOutTime"], errors="coerce").apply(format_timedelta2)
        df["PitStopDuration"] = pd.to_timedelta(df["PitStopDuration"], errors="coerce").apply(format_timedelta2)

        # Manejo de valores nulos para columnas categóricas
        df["Compound"] = df["Compound"].fillna("TBD")
        df["RaceName"] = df["RaceName"].fillna("GP")  
        df["Season"] = df["Season"].fillna(0).astype(int)  

        df["LapNumber"] = df["LapNumber"].fillna(0).astype(int)
        df["DriverNumber"] = df["DriverNumber"].fillna(0).astype(int)
        df["Position"] = df["Position"].fillna(0).astype(int)
        df["FinishingPosition"] = df["FinishingPosition"].fillna(0).astype(int)
        df["GridPosition"] = df["GridPosition"].fillna(0).astype(int)
        df["IsPersonalBest"] = df["IsPersonalBest"].apply(lambda x: bool(x) if pd.notna(x) else False)

        for _, row in df.iterrows():
            try:
                    # print("Intentando insertar fila:", row.to_dict())
                    cursor.execute("""
                    INSERT INTO fullDatosCarreras (
                        id, numerovuelta, piloto, numeropiloto, equipo, posicion, tiempovuelta, mejorvueltapersonal, 
                        sector1tiempo, sector2tiempo, sector3tiempo, compuestoneumatico, pittiempoentrada, 
                        pittiemposalida, duracionparada, temporada, nombreGP, posicionfinal, 
                        posicioninicio, estadofinalcarrera, tipocarrera
                    ) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()), row["LapNumber"], row["Driver"], row["DriverNumber"], row["Team"], 
                    row["Position"], row["LapTime"], row["IsPersonalBest"], row["Sector1Time"], row["Sector2Time"], 
                    row["Sector3Time"], row["Compound"], row["PitInTime"], row["PitOutTime"], row["PitStopDuration"],
                    row["Season"], row["RaceName"], row["FinishingPosition"], row["GridPosition"], 
                    row["FinalStatus"], row["RaceType"]
                ))
            except Exception as e:
                print(f"Error en la fila {row.to_dict()}: {e}")
        
        conn.commit()
        print("Datos de carrera completa insertados correctamente.")

    except Exception as e:
        print("Error al insertar datos:", e)

    finally:
        cursor.close()
        conn.close()
    
