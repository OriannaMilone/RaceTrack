import fastf1 as ff1
import pandas as pd

# ff1.Cache.enable_cache('cache') 

def load_session_data(season, event='Belgian Grand Prix', session_type='R'):
    """Carga la sesión de FastF1 y devuelve los datos de vueltas."""
    session = ff1.get_session(season, event, session_type)
    session.load()
    return session.laps, session.results

def get_drivers_info():
    for season in range(2018, 2025):
        laps, _ = load_session_data(season)
        drivers = laps[['Driver', 'DriverNumber']].drop_duplicates()
        drivers.to_csv(f'Spa_{season}_drivers_info.csv', index=False)

def get_teams_info():
    for season in range(2018, 2025):
        laps, _ = load_session_data(season)
        teams = laps[['Team']].drop_duplicates()
        teams.to_csv(f'Spa_{season}_teams_info.csv', index=False)

def get_drivers_teams_info():
    for season in range(2018, 2025):
        laps, _ = load_session_data(season)
        driver_team = laps[['Driver', 'Team']].drop_duplicates()
        driver_team.to_csv(f'Spa_{season}_drivers_teams_info.csv', index=False)

def get_lap_data():
    for season in range(2018, 2025):
        laps, _ = load_session_data(season)
        lap_data = laps[['LapNumber', 'Driver', 'Team', 'LapTime', 'Position', 'IsPersonalBest', 'Compound', 'TyreLife']]
        lap_data_sectors = laps[['LapNumber', 'Driver', 'Sector1Time', 'Sector2Time', 'Sector3Time']]
        complete_data = lap_data.merge(lap_data_sectors, on=['LapNumber', 'Driver'])
        complete_data.to_csv(f'Spa_{season}_race_info.csv', index=False)

def get_race_status_data():
    for season in range(2018, 2025):
        _, results = load_session_data(season)
        race_status = results[["Abbreviation", "Position", "GridPosition", "Status"]].rename(columns={
            "Abbreviation": "Driver",
            "Position": "FinishingPosition",
            "Status": "FinalStatus"
        })
        race_status.to_csv(f'Spa_{season}_race_status.csv', index=False)

def get_pitstops_data():
    for season in range(2018, 2025):
        print(f"\nProcesando temporada {season}...")
        laps, _ = load_session_data(season)
        
        pit_in_laps = laps[laps['PitInTime'].notnull()][['LapNumber', 'Driver', 'PitInTime']].rename(columns={'LapNumber': 'LapNumber_In'})
        pit_out_laps = laps[laps['PitOutTime'].notnull()][['LapNumber', 'Driver', 'PitOutTime']].rename(columns={'LapNumber': 'LapNumber_Out'})

        pit_stops = pd.merge(pit_in_laps, pit_out_laps, on='Driver', suffixes=('_In', '_Out'))
        pit_stops = pit_stops[pit_stops['LapNumber_Out'] == pit_stops['LapNumber_In'] + 1]
        pit_stops['PitStopDuration'] = pit_stops['PitOutTime'] - pit_stops['PitInTime']
        pit_stops['Season'] = season

        filename = f'Spa_{season}_pitstops_data.csv'
        pit_stops.to_csv(filename, index=False)
        print(f"Archivo guardado: {filename}")

def get_full_race_data(race_prefix, race_name, GP_name, season, session_type='H'):
    session = ff1.get_session(season, GP_name, 'R') 
    session.load()
    
    laps = session.laps
    results = session.results
    
    lap_data = laps[['LapNumber', 'Driver', 'DriverNumber', 'Team', 'Position', 'LapTime', 'IsPersonalBest']]
    lap_data_sectors = laps[['LapNumber', 'Driver', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'Compound']]
    laps_data = lap_data.merge(lap_data_sectors, on=['LapNumber', 'Driver'])


    pit_in_laps = laps[laps['PitInTime'].notnull()][['LapNumber', 'Driver', 'PitInTime']].rename(columns={'LapNumber': 'LapNumber_In'})
    pit_out_laps = laps[laps['PitOutTime'].notnull()][['LapNumber', 'Driver', 'PitOutTime']].rename(columns={'LapNumber': 'LapNumber_Out'})

    pit_stops = pd.merge(pit_in_laps, pit_out_laps, on='Driver', suffixes=('_In', '_Out'))
    pit_stops = pit_stops[pit_stops['LapNumber_Out'] == pit_stops['LapNumber_In'] + 1]
    pit_stops['PitStopDuration'] = pit_stops['PitOutTime'] - pit_stops['PitInTime']

    # Combinar datos de vueltas y paradas en boxes 
    merged_data = laps_data.merge(pit_stops[['LapNumber_In', 'Driver', 'PitInTime', 'PitOutTime', 'PitStopDuration']], 
                          how='left', left_on=['LapNumber', 'Driver'], right_on=['LapNumber_In', 'Driver'])

    merged_data.drop(columns=['LapNumber_In'], inplace=True)

    race_status = results[["Abbreviation", "Position", "GridPosition", "Status"]].rename(columns={
                "Abbreviation": "Driver",
                "Position": "FinishingPosition",
                "Status": "FinalStatus"
            })

    merged_data = merged_data.merge(race_status, on='Driver')

    merged_data['Season'] = season
    merged_data['RaceName'] = race_name 
    merged_data['RaceType'] = 'historica'

    # Guardar archivo CSV
    filename = f'{race_prefix}_{season}_full_{session_type}_data.csv'
    merged_data.to_csv(filename, index=False)
    print(f"Archivo guardado: {filename}")

def get_full_races_data(season, session_type='H'):
    session = ff1.get_session(season, 'Belgian Grand Prix', 'R') 
    session.load()
    
    laps = session.laps
    results = session.results
    
    lap_data = laps[['LapNumber', 'Driver', 'DriverNumber', 'Team', 'Position', 'LapTime', 'IsPersonalBest']]
    lap_data_sectors = laps[['LapNumber', 'Driver', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'Compound']]
    laps_data = lap_data.merge(lap_data_sectors, on=['LapNumber', 'Driver'])

    pit_in_laps = laps[laps['PitInTime'].notnull()][['LapNumber', 'Driver', 'PitInTime']].rename(columns={'LapNumber': 'LapNumber_In'})
    pit_out_laps = laps[laps['PitOutTime'].notnull()][['LapNumber', 'Driver', 'PitOutTime']].rename(columns={'LapNumber': 'LapNumber_Out'})

    pit_stops = pd.merge(pit_in_laps, pit_out_laps, on='Driver', suffixes=('_In', '_Out'))
    pit_stops = pit_stops[pit_stops['LapNumber_Out'] == pit_stops['LapNumber_In'] + 1]
    pit_stops['PitStopDuration'] = pit_stops['PitOutTime'] - pit_stops['PitInTime']

    merged_data = laps_data.merge(pit_stops[['LapNumber_In', 'Driver', 'PitInTime', 'PitOutTime', 'PitStopDuration']], 
                                  how='left', left_on=['LapNumber', 'Driver'], right_on=['LapNumber_In', 'Driver'])

    merged_data.drop(columns=['LapNumber_In'], inplace=True)

    race_status = results[["Abbreviation", "Position", "GridPosition", "Status"]].rename(columns={
                "Abbreviation": "Driver",
                "Position": "FinishingPosition",
                "Status": "FinalStatus"
            })

    merged_data = merged_data.merge(race_status, on='Driver')
    merged_data['Season'] = season
    merged_data['RaceName'] = 'GP Belgica'
    merged_data['RaceType'] = 'historica'

    return merged_data

# all_years_data = []

# for season in range(2018, 2025):  
#     try:
#         data = get_full_races_data(season)
#         all_years_data.append(data)
#     except Exception as e:
#         print(f"Error en la temporada {season}: {e}")

# df_final = pd.concat(all_years_data, ignore_index=True)
# df_final.to_csv('SPA_2018_2025_full_H_data.csv', index=False)
# print("Archivo guardado: SPA_2018_2025_full_H_data.csv")

# GPs = ["Brazilian Grand Prix", "Italian Grand Prix", "Belgian Grand Prix", "Monaco Grand Prix"]

for season in range(2018, 2025):
    get_full_race_data('MONZA', 'GP Monza', 'Italian Grand Prix', season)
    get_full_race_data('SAOPAULO', 'GP São Paulo', 'Brazilian Grand Prix', season)