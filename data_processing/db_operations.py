import pandas as pd
import uuid
from db_connection import get_connection

def insert_pilotos_from_csv(csv_file):
    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        df = pd.read_csv(csv_file)

        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO Piloto (id, nombre, numeroCompeticion) 
                VALUES (%s, %s, %s);
            """, (str(uuid.uuid4()), row["nombre"], row["numeroCompeticion"]))

        conn.commit()
        print("Datos de pilotos insertados correctamente.")

    except Exception as e:
        print("Error al insertar datos:", e)
    finally:
        cursor.close()
        conn.close()
