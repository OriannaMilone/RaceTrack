from db_operations import insert_pilotos_from_csv
from db_connection import get_connection

if __name__ == "__main__":
    # csv_file = "../SPA_DATA/drivers_data/.csv"

    # insert_pilotos_from_csv(csv_file)
    conn = get_connection()

    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT version();")  
        print(cursor.fetchone())
        cursor.close()
        conn.close()
    else:
        print("No se pudo conectar a la base de datos.")
