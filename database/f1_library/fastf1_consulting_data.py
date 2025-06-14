import fastf1 as ff1
''' fastf1 is a library to access Formula 1 data.
    It allows users to retrieve different events, sessions, and telemetry data from Formula 1. 
    For more information, visit https://github.com/theOehrly/Fast-F1
'''

schedule = ff1.get_event_schedule(2018) # Year's racing schedule
print(schedule)

event = ff1.get_event(2018, 'Belgian Grand Prix') # Event's information (Whole Weekend schedule)
print(event)

event = ff1.get_event(2018, 'Italian Grand Prix') # Event's information (Whole Weekend schedule)
print(event)

event = ff1.get_event(2018, 'Monaco Grand Prix') # Event's information (Whole Weekend schedule)
print(event)

event = ff1.get_event(2018, 'Brazilian Grand Prix') # Event's information (Whole Weekend schedule)
print(event)

# specific event information
session = ff1.get_session(2018, 'Belgian Grand Prix', 'R') # 'R'ace ('Q'ualifying o 'P'ractice)
session.load()
session_info = session._session_info
print(session._session_info)

results =  session.results
driver = results[["Abbreviation", "Position", "GridPosition", "Status"]]
print(driver)

laps = session.laps
drivers = laps[['Team']]
drivers = drivers.drop_duplicates()
print(drivers)

race_control = session.race_control_messages
print(race_control.columns)
print(race_control)

#We are no gonna go so deep in the telemetry data
# lap_1 = laps.iloc[0]
# telemetry = lap_1.get_telemetry()
# print(telemetry.columns)

tyres_lap_data = laps[['LapNumber','Driver','TyreLife', 'Compound']]
print(tyres_lap_data)