import requests
import folium

# Twoje punkty startowy i końcowy (szerokość, długość geograficzna)
start_coords = (52.2296756, 21.0122287)  # Przykładowe koordynaty dla Warszawy
end_coords = (50.0646501, 19.9449799)    # Przykładowe koordynaty dla Krakowa

# Twój klucz API Graphhopper
api_key = '8610ac53-3959-482d-b85e-2e2b4dca1254'

# Parametry zapytania do Graphhopper
params = {
    'point': [f"{start_coords[0]},{start_coords[1]}", f"{end_coords[0]},{end_coords[1]}"],
    'vehicle': 'car',
    'locale': 'en',
    'instructions': 'false',
    'key': api_key
}

# Wysłanie zapytania do Graphhopper
response = requests.get('https://graphhopper.com/api/1/route', params=params)
data = response.json()

# Sprawdzanie, czy odpowiedź zawiera dane trasy
if 'paths' in data and len(data['paths']) > 0:
    # Pobranie punktów trasy
    route_points = data['paths'][0]['points']['coordinates']

    # Tworzenie mapy
    m = folium.Map(location=start_coords, zoom_start=6)

    # Dodanie trasy do mapy
    folium.PolyLine(
        locations=[(point[1], point[0]) for point in route_points],
        color='blue',
        weight=5
    ).add_to(m)

    # Dodanie punktów startowego i końcowego
    folium.Marker(location=start_coords, popup='Start', icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(location=end_coords, popup='End', icon=folium.Icon(color='red')).add_to(m)

    # Zapisanie mapy do pliku HTML
    m.save('map.html')

    # Wyświetlenie mapy w przeglądarce (jeśli używasz Jupyter Notebook)
    m
else:
    print("Brak danych trasy w odpowiedzi API")


