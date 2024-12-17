import pandas as pd
import folium
import csv
import branca
import requests

start_coords = (52.2296756, 21.0122287)
end_coords = (50.0646501, 19.9449799)

api_key = "8610ac53-3959-482d-b85e-2e2b4dca1254"

params ={
    'point': [f"{start_coords[0]},{start_coords[1]}", f"{end_coords[0]},{end_coords[1]}"],
    'vehicel': 'car',
    'locale': 'en',
    'instructions': 'false',
    'key': api_key
}

respone = requests.get('https://graphhopper.com/api/1/route', params=params)
data = respone.json()

route_points = data['paths'][0]['points']['coordinates']
m = folium.Map(location=start_coords,zoom_start=6)

folium.PolyLine(
    locations=[(point[1], point[0]) for point in route_points],
    color='blue',
    weight=5
).add_to(m)

folium.Marker(location=start_coords, popup='Start', icon=folium.Icon(color='green')).add_to(m)
folium.Marker(location=end_coords, popup='End', icon=folium.Icon(color='red')).add_to(m)

m.save('map.html')

my_map = folium.Map(location=[52.231321303746476, 21.09808072815419])
my_map.save('warszawa_mapa.html')


def load_data(file_path):
    companies = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['latitude'] = float(row['latitude'])
            row['longitude'] = float(row['longitude'])
            companies.append(row)
    return companies

def place_markers(companies, my_map):
    tooltip = 'Nacisnij mnie'
    for company in companies:
        folium.Marker([company['latitude'], company['longitude']],
        popup= f'Nazwa: {company["name"]}, adres: {company["address"]}',
        tooltip = tooltip).add_to(my_map)

companies = load_data('warszawa.csv')
place_markers(companies, my_map)

my_map.save('warszawa_map.html')



