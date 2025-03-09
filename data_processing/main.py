from db_operations import *

if __name__ == "__main__":

    csv_drivers_files = ["../SPA_DATA/drivers_data/Spa_2018_drivers_info.csv", "../SPA_DATA/drivers_data/Spa_2019_drivers_info.csv", "../SPA_DATA/drivers_data/Spa_2020_drivers_info.csv","../SPA_DATA/drivers_data/Spa_2021_drivers_info.csv", "../SPA_DATA/drivers_data/Spa_2022_drivers_info.csv", "../SPA_DATA/drivers_data/Spa_2023_drivers_info.csv", "../SPA_DATA/drivers_data/Spa_2024_drivers_info.csv"]
    insert_pilotos_from_csv(csv_drivers_files)

    csv_drivers_files = ["../SPA_DATA/drivers_teams/Spa_2018_drivers_teams_info.csv","../SPA_DATA/drivers_teams/Spa_2019_drivers_teams_info.csv", "../SPA_DATA/drivers_teams/Spa_2020_drivers_teams_info.csv", "../SPA_DATA/drivers_teams/Spa_2021_drivers_teams_info.csv", "../SPA_DATA/drivers_teams/Spa_2022_drivers_teams_info.csv", "../SPA_DATA/drivers_teams/Spa_2023_drivers_teams_info.csv", "../SPA_DATA/drivers_teams/Spa_2024_drivers_teams_info.csv"]
    insert_equipos_from_csv(csv_drivers_files)

    for year in range(2018, 2025):
        csv_file = f"../SPA_DATA/drivers_teams/Spa_{year}_drivers_teams_info.csv"
        insert_pilotos_equipos_from_csv(csv_file, year)
    
    