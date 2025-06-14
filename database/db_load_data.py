from db_operations import *

if __name__ == "__main__":
    # Years to process
    YEARS = range(2018, 2025)

    # SPA DATA -------------------------------------------------------------
    SPA_BASE_PATH = "race_data/SPA_DATA/"
    SPA_PATHS = {
        "drivers": "drivers_data/Spa_{year}_drivers_info.csv",
        "drivers_teams": "drivers_teams/Spa_{year}_drivers_teams_info.csv",
        "race_status": "race_status/Spa_{year}_race_status.csv",
        "race_laps": "spa_race_results/Spa_{year}_race_laps.csv",
        "pitstops": "pitstops/Spa_{year}_pitstops_data.csv",
        "full_data": "full_data_race/SPA_{year}_full_H_data.csv"
    }

    # Insert drivers
    drivers_files = [SPA_BASE_PATH + SPA_PATHS["drivers"].format(year=year) for year in YEARS]
    insert_drivers_from_csv(drivers_files)

    # Insert teams
    teams_files = [SPA_BASE_PATH + SPA_PATHS["drivers_teams"].format(year=year) for year in YEARS]
    insert_teams_from_csv(teams_files)

    for year in YEARS:
        drivers_teams_file = SPA_BASE_PATH + SPA_PATHS["drivers_teams"].format(year=year)
        insert_driver_team_participation(drivers_teams_file, year)

        insert_race(year, "GP Belgica", "Spa-Francorchamps", "historica")
        insert_race(year, "GP Monaco", "Circuito de Montecarlo", "historica")
        insert_race(year, "GP Monza", "Autodromo Nazionale Monza", "historica")
        insert_race(year, "GP Sao Paulo", "Autódromo José Carlos Pace", "historica")
        
        race_status_file = SPA_BASE_PATH + SPA_PATHS["race_status"].format(year=year)
        insert_race_status_from_csv(race_status_file, year)

        race_laps_file = SPA_BASE_PATH + SPA_PATHS["race_laps"].format(year=year)
        insert_laps_from_csv(race_laps_file, year)

        pitstops_file = SPA_BASE_PATH + SPA_PATHS["pitstops"].format(year=year)
        insert_pitstops_from_csv(pitstops_file)

        full_data_file = SPA_BASE_PATH + SPA_PATHS["full_data"].format(year=year)
        insert_full_race_data(full_data_file)

    # CIRCUITS FULL DATA ---------------------------------------------------
    BASE_PATHS = {
        "monaco": "race_data/MONACO_DATA/",
        "monza": "race_data/MONZA_DATA/",
        "saopaulo": "race_data/SAOPAULO_DATA/"
    }

    CIRCUIT_PREFIXES = {
        "monaco": "MONACO",
        "monza": "MONZA",
        "saopaulo": "SAOPAULO"
    }

    FULL_DATA_TEMPLATE = "full_data_race/{prefix}_{year}_full_H_data.csv"

    for circuit_key, prefix in CIRCUIT_PREFIXES.items():
        base_path = BASE_PATHS[circuit_key]
        for year in YEARS:
            file_path = base_path + FULL_DATA_TEMPLATE.format(prefix=prefix, year=year)
            insert_full_race_data(file_path)

        
    print("Away we go!")