from db_connection import get_connection
import pandas as pd
import uuid

def format_timedelta(td):
    """Converts Timedelta to mm:ss.SSS format."""
    if pd.isna(td):
        return None
    total_seconds = td.total_seconds()
    minutes, seconds = divmod(total_seconds, 60)
    return f"{int(minutes):02}:{seconds:06.3f}"

def format_timedelta2(td):
    """Converts Timedelta to hh:mm:ss.SSS format."""
    if pd.isna(td):
        return None  
    total_seconds = td.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{seconds:06.3f}"

def insert_drivers_from_csv(csv_files):
    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        
        dfs = [pd.read_csv(file) for file in csv_files]
        final_df = pd.concat(dfs, ignore_index=True).drop_duplicates()

        for _, row in final_df.iterrows():
            cursor.execute(
                "INSERT INTO Piloto (id, nombre, numerocompeticion) VALUES (%s, %s, %s)",
                (str(uuid.uuid4()), row["Driver"], row["DriverNumber"])
            )

        conn.commit()
        print("Drivers inserted successfully.")

    except Exception as e:
        print("Error inserting drivers:", e)
    finally:
        cursor.close()
        conn.close()

def insert_teams_from_csv(csv_files):
    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        
        dfs = [pd.read_csv(file) for file in csv_files]
        final_df = pd.concat(dfs, ignore_index=True)
        final_df = final_df.iloc[:, 1:]
        final_df = final_df.drop_duplicates(subset=["Team"])

        for _, row in final_df.iterrows():
            cursor.execute(
                "INSERT INTO Equipo (id, nombreescuderia) VALUES (%s, %s)",
                (str(uuid.uuid4()), row["Team"]))
        
        conn.commit()
        print("Teams inserted successfully.")    
    except Exception as e:
        print("Error inserting teams:", e)
    finally:
        cursor.close()
        conn.close()

def insert_driver_team_participation(csv_file, season):
    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        
        df = pd.read_csv(csv_file)
        
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
            return "Error matching drivers and teams IDs."
        
        for i in range(len(drivers_ids)):
            cursor.execute("INSERT INTO ParticipacionEquipo (id, id_piloto, id_equipo, temporada) VALUES (%s, %s, %s, %s)",
                (str(uuid.uuid4()), drivers_ids[i], teams_ids[i], season)
            )

        conn.commit()
        print("Driver-Team participations inserted successfully.")

    except Exception as e:
        print("Error inserting participations:", e)
    finally:
        cursor.close()
        conn.close()  
        
def insert_race(year, name, circuit, race_type):
    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO Carrera (id, nombre, circuito, tipo, temporada) VALUES (%s, %s, %s, %s, %s)",
            (str(uuid.uuid4()), name, circuit, race_type, year)
        )

        conn.commit()
        print("Race inserted successfully.")

    except Exception as e:
        print("Error inserting race:", e)
    finally:
        cursor.close()
        conn.close()        

def insert_race_status_from_csv(csv_file, year):
    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        df = pd.read_csv(csv_file)

        df["FisingPosition"] = df["FisingPosition"].astype(int)
        df["GridPosition"] = df["GridPosition"].astype(int)
        
        cursor.execute("SELECT id FROM Carrera WHERE temporada = %s", (year,))
        race_id = cursor.fetchone()[0]

        drivers_ids = []

        for _, row in df.iterrows():
            cursor.execute("SELECT id FROM Piloto WHERE nombre = %s", (row["Driver"],))
            driver_id = cursor.fetchone()
            if driver_id:
                drivers_ids.append(driver_id[0])

        for driver_id, (_, row) in zip(drivers_ids, df.iterrows()):
            cursor.execute("INSERT INTO ParticipacionCarrera (id_piloto, id_carrera, estado, posicioninicio, posicionfinal) VALUES (%s, %s, %s, %s, %s)",
                (driver_id, race_id, row["FinialStatus"], row["GridPosition"], row["FisingPosition"])
            )

        conn.commit()
        print("Race status inserted successfully.")

    except Exception as e:
        print("Error inserting race status:", e)
    finally:
        cursor.close()
        conn.close()
           

        cursor.close()
        conn.close()
        
def insert_laps_from_csv(csv_file, year):
    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        df = pd.read_csv(csv_file)
        df = df.drop(columns=["Team", "TyreLife"])
        df["LapNumber"] = df["LapNumber"].astype(int)
        df["Position"] = df["Position"].fillna(0).astype(int)
        df["Compound"] = df["Compound"].fillna("TBD")

        df["LapTime"] = pd.to_timedelta(df["LapTime"], errors="coerce").apply(format_timedelta)
        df["Sector1Time"] = pd.to_timedelta(df["Sector1Time"], errors="coerce").apply(format_timedelta)
        df["Sector2Time"] = pd.to_timedelta(df["Sector2Time"], errors="coerce").apply(format_timedelta)
        df["Sector3Time"] = pd.to_timedelta(df["Sector3Time"], errors="coerce").apply(format_timedelta)
        df["IsPersonalBest"] = df["IsPersonalBest"].fillna(0).astype(int).astype(bool)
        
        cursor.execute("SELECT id FROM Carrera WHERE temporada = %s", (year,))
        race_id = cursor.fetchone()[0]

        drivers_ids = []

        for _, row in df.iterrows():
            cursor.execute("SELECT id FROM Piloto WHERE nombre = %s", (row["Driver"],))
            driver_id = cursor.fetchone()
            if driver_id:
                drivers_ids.append(driver_id[0])

        for driver_id, (_, row) in zip(drivers_ids, df.iterrows()):
            cursor.execute("""
                INSERT INTO vuelta (id, id_piloto, id_carrera, numerovuelta, posicion, tiempovuelta, sector1tiempo, sector2tiempo, sector3tiempo, compuestoneumático, mejorvueltapersonal) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (str(uuid.uuid4()), driver_id, race_id, row["LapNumber"], row["Position"], row["LapTime"], row["Sector1Time"], row["Sector2Time"], row["Sector3Time"], row["Compound"], row["IsPersonalBest"])
            )

        conn.commit()
        print("Laps inserted successfully.")

    except Exception as e:
        print("Error inserting laps:", e)
    finally:
        cursor.close()
        conn.close()

def insert_pitstops_from_csv(csv_file): 
    conn = get_connection()
    if not conn:
        print("No se pudo establecer conexión con la base de datos.")
        return

    try:
        cursor = conn.cursor()
        df = pd.read_csv(csv_file)

        df["PitInTime"] = pd.to_timedelta(df["PitInTime"], errors="coerce").apply(format_timedelta2)
        df["PitOutTime"] = pd.to_timedelta(df["PitOutTime"], errors="coerce").apply(format_timedelta2)
        df["PitStopDuration"] = pd.to_timedelta(df["PitStopDuration"], errors="coerce").apply(format_timedelta2)

        for _, row in df.iterrows():
            cursor.execute("SELECT id FROM Carrera WHERE temporada = %s", (row["Season"],))
            race_result = cursor.fetchone()
            if not race_result:
                print(f"Warning: Race not found for season {row['Season']}")
                continue
            race_id = race_result[0]

            cursor.execute("SELECT id FROM Piloto WHERE nombre = %s", (row["Driver"],))
            driver_result = cursor.fetchone()
            if not driver_result:
                print(f"Warning: Driver not found for name {row['Driver']}")
                continue
            driver_id = driver_result[0]

            cursor.execute("SELECT id FROM Vuelta WHERE id_piloto = %s AND id_carrera = %s AND numerovuelta = %s", 
                           (driver_id, race_id, row["LapNumber_In"]))
            lap_in_result = cursor.fetchone()
            if not lap_in_result:
                print(f"Warning: Lap In not found for piloto {driver_id}, carrera {race_id}, vuelta {row['LapNumber_In']}")
                continue
            lap_in_id = lap_in_result[0]

            cursor.execute("SELECT id FROM Vuelta WHERE id_piloto = %s AND id_carrera = %s AND numerovuelta = %s", 
                           (driver_id, race_id, row["LapNumber_Out"]))
            lap_out_result = cursor.fetchone()
            if not lap_out_result:
                print(f"Warning: Lap Out not found for piloto {driver_id}, carrera {race_id}, vuelta {row['LapNumber_Out']}")
                continue
            lap_out_id = lap_out_result[0]

            cursor.execute("""
                INSERT INTO paradaenboxes (id, id_piloto, id_carrera, id_vuelta_entra, id_vuelta_sale, tiempoentrada, tiemposalida, duracionparada, tipoparada)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (str(uuid.uuid4()), driver_id, race_id, lap_in_id, lap_out_id, row["PitInTime"], row["PitOutTime"], row["PitStopDuration"], "Cambio de neumáticos")
            )

        conn.commit()
        print("Pitstops inserted successfully.")

    except Exception as e:
        print("Error inserting pitstops:", e)
    finally:
        cursor.close()
        conn.close()


def insert_full_race_data(csv_file):
    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        df = pd.read_csv(csv_file)

        df["LapTime"] = pd.to_timedelta(df["LapTime"], errors="coerce").apply(format_timedelta)
        df["Sector1Time"] = pd.to_timedelta(df["Sector1Time"], errors="coerce").apply(format_timedelta)
        df["Sector2Time"] = pd.to_timedelta(df["Sector2Time"], errors="coerce").apply(format_timedelta)
        df["Sector3Time"] = pd.to_timedelta(df["Sector3Time"], errors="coerce").apply(format_timedelta)
        df["PitInTime"] = pd.to_timedelta(df["PitInTime"], errors="coerce").apply(format_timedelta2)
        df["PitOutTime"] = pd.to_timedelta(df["PitOutTime"], errors="coerce").apply(format_timedelta2)
        df["PitStopDuration"] = pd.to_timedelta(df["PitStopDuration"], errors="coerce").apply(format_timedelta2)

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
                cursor.execute("""
                    INSERT INTO fullDatosCarreras (
                        id, numerovuelta, piloto, numeropiloto, equipo, posicion, tiempovuelta, mejorvueltapersonal, 
                        sector1tiempo, sector2tiempo, sector3tiempo, compuestoneumatico, pittiempoentrada, 
                        pittiemposalida, duracionparada, temporada, nombreGP, posicionfinal, 
                        posicioninicio, estadofinalcarrera, tipocarrera
                    ) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (str(uuid.uuid4()), row["LapNumber"], row["Driver"], row["DriverNumber"], row["Team"], 
                 row["Position"], row["LapTime"], row["IsPersonalBest"], row["Sector1Time"], row["Sector2Time"], 
                 row["Sector3Time"], row["Compound"], row["PitInTime"], row["PitOutTime"], row["PitStopDuration"],
                 row["Season"], row["RaceName"], row["FinishingPosition"], row["GridPosition"], 
                 row["FinalStatus"], row["RaceType"])
                )
            except Exception as e:
                print(f"Error in row {row.to_dict()}: {e}")
        
        conn.commit()
        print("Full race data inserted successfully.")

    except Exception as e:
        print("Error inserting full race data:", e)
    finally:
        cursor.close()
        conn.close()
