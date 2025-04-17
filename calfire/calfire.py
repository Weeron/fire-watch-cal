import pandas as pd # to read CSV
import requests # to gather real-time data from the API

# Using data from CAL FIRE: https://www.fire.ca.gov/incidents
CSV_FILE = "mapdataall.csv"
ACTIVE_URL = "https://www.fire.ca.gov/umbraco/api/IncidentApi/List?inactive=false"

# Loads historical data from csv file
def load_csv(file):
    df = pd.read_csv(file)
    df['incident_dateonly_created'] = pd.to_datetime(df['incident_dateonly_created'], errors='coerce')
    return df

# Finds the top 5 fires by acres burned in a specific year
def get_top_5(df, year):
    df = df[df['incident_dateonly_created'].dt.year == int(year)] # filter by year
    df = df.sort_values(by='incident_acres_burned', ascending=False).head(5) # sort by top 5 acres burned

    fire_list = [] # compile results into one list
    for _, row in df.iterrows():
        end_date = row['incident_dateonly_extinguished']
        if pd.isna(end_date) or end_date == "": # instead of nan, rename end date to "unknown" if extinguish date isn't provided
            end_date = "unknown"
        fire = f"'{row['incident_name']}' in {row['incident_county']} County - {int(row['incident_acres_burned'])} acres - Started: {row['incident_dateonly_created'].date()} - Ended: {end_date}"
        fire_list.append(fire)
    return fire_list

# Uses the json api to sort through currently active fires
def get_active_fires():
    response = requests.get(ACTIVE_URL)
    fire_data = response.json()

    fire_list = [] 
    for fire in fire_data: # collect results in a list
        name = fire['Name']
        county = fire['County']
        acres = int(float(fire['AcresBurned']))
        containment = fire['PercentContained']
        started = fire['StartedDateOnly']

        fire = f"'{name}' in {county} County - {acres} acres - Containment: {containment}% - Started: {started}"
        fire_list.append(fire)
    return fire_list

if __name__ == "__main__":
    print("Track Fires in California")
    print("1. View top 5 historical fires by year")
    print("2. View currently active fires")

    choice = input("Enter 1 or 2: ")

    if choice == "1":
        year = input("Enter a year (2013-2025): ")
        df = load_csv(CSV_FILE)
        fires = get_top_5(df, year)
        for fire in fires:
            print(fire)

    elif choice == "2":
        fires = get_active_fires()
        for fire in fires:
            print(fire)
