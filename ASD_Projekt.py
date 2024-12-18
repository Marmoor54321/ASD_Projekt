import csv
import random
from math import radians, cos, sin, sqrt, atan2
import openrouteservice as ors
import folium
from itertools import cycle,permutations

client = ors.Client(key='5b3ce3597851110001cf624890e6125065a644b4ad5fa0e2a05d158e')


def load_data(file_path):
    companies = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['latitude'] = float(row['latitude'])
            row['longitude'] = float(row['longitude'])
            companies.append(row)
    return companies


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  #Promień ziemi w km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def find_coordinates_by_address(companies, address):
    address = address.strip().lower()
    for company in companies:
        if company['address'].strip().lower() == address:
            return company['latitude'], company['longitude']
    return None, None


def find_nearest_company(companies, depot_lat, depot_lon):
    nearest_company = None
    min_distance = float('inf')
    for company in companies:
        distance = haversine(depot_lat, depot_lon, company['latitude'], company['longitude'])
        if distance < min_distance:
            min_distance = distance
            nearest_company = company
    return nearest_company,distance


def find_nearest_company_by_address(companies, address):
    depot_lat, depot_lon = find_coordinates_by_address(companies, address)
    if depot_lat is None or depot_lon is None:
        return None
    return find_nearest_company(companies, depot_lat, depot_lon)


def calculate_distances(companies, depot_lat, depot_lon, method='haversine'):
    distances = []
    for company in companies:
        if method == 'haversine':
            distance = haversine(depot_lat, depot_lon, company['latitude'], company['longitude'])
        elif method == 'road':
            coords = [(depot_lon, depot_lat), (company['longitude'], company['latitude'])]
            route = client.directions(coordinates=coords, profile='driving-car', format='geojson')
            distance = route['features'][0]['properties']['segments'][0]['distance'] / 1000.0
        distances.append((company, distance))
    return distances


#niepotrzebna funkcja
def print_nearest_company(nearest_companies, address_to_search):
    if nearest_companies and address_to_search is None:
        print(f"Nazwa: {nearest_companies['name']}, Adres: {nearest_companies['address']}, "
              f"szerokosc: {nearest_companies['latitude']:.5f}, dlugosc: {nearest_companies['longitude']:.5f}")
    elif nearest_companies:
        print("Najbliższa firma od adresu", address_to_search, "to:")
        print(f"Nazwa: {nearest_companies['name']}, Adres: {nearest_companies['address']}, "
              f"szerokosc: {nearest_companies['latitude']:.5f}, dlugosc: {nearest_companies['longitude']:.5f}")
    else:
        print("Nie znaleziono firmy blisko podanego adresu.")


def sort_companies_by_distance(companies, depot_lat, depot_lon, method='haversine'):
    distances = calculate_distances(companies, depot_lat, depot_lon, method)
    distances.sort(key=lambda x: x[1])
    return distances


def display_on_map(depot_lat, depot_lon, sorted_companies, file_name='mapa.html', method='haversine'):
    m = folium.Map(location=[depot_lat, depot_lon], tiles="cartodbpositron", zoom_start=13)
    folium.Marker(location=[depot_lat, depot_lon], popup='Depot', icon=folium.Icon(color='red')).add_to(m)

    colors = cycle(['blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige',
                    'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'pink', 'lightblue',
                    'lightgreen', 'gray', 'black', 'lightgray'])

    if method == 'haversine':
        for company, distance in sorted_companies:
            color = next(colors)
            folium.Marker(location=[company['latitude'], company['longitude']],
                          popup=f"{company['name']} ({distance:.2f} km)",
                          icon=folium.Icon(color=color)).add_to(m)
            folium.PolyLine(locations=[[depot_lat, depot_lon], [company['latitude'], company['longitude']]],
                            color=color).add_to(m)
    elif method == 'road':
        for company, distance in sorted_companies:
            color = next(colors)
            folium.Marker(location=[company['latitude'], company['longitude']],
                          popup=f"{company['name']} ({distance:.2f} km)",
                          icon=folium.Icon(color=color)).add_to(m)
            coords = [(depot_lon, depot_lat), (company['longitude'], company['latitude'])]
            route = client.directions(coordinates=coords, profile='driving-car', format='geojson')
            folium.PolyLine(
                locations=[list(reversed(coord)) for coord in route['features'][0]['geometry']['coordinates']],
                color=color).add_to(m)

    m.save(file_name)



companies = load_data('Warszawa.csv')


k = 0
random_companies = random.sample(companies, k)


depot_address = 'al. Aleja Wojska Polskiego 9'

depot_lat, depot_lon = find_coordinates_by_address(companies, depot_address)
if depot_lat is None or depot_lon is None:
    print("Nie znaleziono adresu DEPOTU")
    quit()


#sorted_haversine = sort_companies_by_distance(random_companies, depot_lat, depot_lon, method='haversine')
#print("Posortowane po ogległości po prostej:")
#for company, distance in sorted_haversine:
#    print(f"{company['name']} - {distance:.2f} km")


#sorted_route = sort_companies_by_distance(random_companies, depot_lat, depot_lon, method='road')
#print("\nPosortowane po odległości trasy:")
#for company, distance in sorted_route:
#    print(f"{company['name']} - {distance:.2f} km")


#display_on_map(depot_lat, depot_lon, sorted_haversine, 'mapa_haversine.html', method='haversine')
#display_on_map(depot_lat, depot_lon, sorted_route, 'mapa_route.html', method='road')


#48.446511795151835, 2.9218599119035646
#print(find_nearest_company(companies, 53.119160718649454, 23.132878086305183))

#print(find_coordinates_by_address(companies,'Aleja Dzieci Polskich 67C'))

#print_nearest_company(nearest_companies, address_to_search)

#address_to_search = 'al. Aleja Wojska Polskiego 9'
#nearest_companies = find_nearest_company_by_address(companies, address_to_search)
#print(nearest_companies)



def brute_force(companies, depot_lat, depot_lon):

    cities = [(company['latitude'], company['longitude'], company['name']) for company in companies]
    best_distance = float('inf')
    best_route = None


    for perm in permutations(cities):
        total_distance = 0
        current_lat, current_lon = depot_lat, depot_lon
        for lat, lon, _ in perm:
            total_distance += haversine(current_lat, current_lon, lat, lon)
            current_lat, current_lon = lat, lon

        total_distance += haversine(current_lat, current_lon, depot_lat, depot_lon)

        if total_distance < best_distance:
            best_distance = total_distance
            best_route = perm


    return best_distance, best_route



def display_tsp_route_on_map(depot_lat, depot_lon, route, file_name):

    m = folium.Map(location=[depot_lat, depot_lon], tiles="cartodbpositron", zoom_start=12)
    folium.Marker(
        location=[depot_lat, depot_lon],
        popup="Depot (Start/End)",
        icon=folium.Icon(color="red")
    ).add_to(m)


    current_lat, current_lon = depot_lat, depot_lon
    for i, (lat, lon, name) in enumerate(route, start=1):
        folium.Marker(
            location=[lat, lon],
            popup=f"{i}. {name}",
            icon=folium.Icon(color="blue")
        ).add_to(m)


        folium.PolyLine(
            locations=[[current_lat, current_lon], [lat, lon]],
            color="blue",
            weight=2.5
        ).add_to(m)
        current_lat, current_lon = lat, lon


    folium.PolyLine(
        locations=[[current_lat, current_lon], [depot_lat, depot_lon]],
        color="green",
        weight=2.5,

    ).add_to(m)


    m.save(file_name)
    print(f"Mapa zapisana w pliku: {file_name}")


def nearest_neighbor(companies, depot_lat, depot_lon):
    unvisited = [(company['latitude'], company['longitude'], company['name']) for company in companies]
    current_lat, current_lon = depot_lat, depot_lon
    route = []
    total_distance = 0

    while unvisited:

        nearest = min(unvisited, key=lambda city: haversine(current_lat, current_lon, city[0], city[1]))
        unvisited.remove(nearest)
        route.append(nearest)

        total_distance += haversine(current_lat, current_lon, nearest[0], nearest[1])
        current_lat, current_lon = nearest[0], nearest[1]


    total_distance += haversine(current_lat, current_lon, depot_lat, depot_lon)
    return total_distance, route




k =100

random_companies = random.sample(companies, k)

depot_address = 'al. Aleja Wojska Polskiego 9'
depot_lat, depot_lon = find_coordinates_by_address(companies, depot_address)
if depot_lat is None or depot_lon is None:
    print("Nie znaleziono adresu DEPOTU")
    quit()


# best_distance, best_route = brute_force(random_companies, depot_lat, depot_lon)
#
#
# print(f"Najkrótsza trasa: {best_distance:.2f} km")
# print("Kolejność odwiedzin miast:")
# for lat, lon, name in best_route:
#     print(f"{name} ({lat}, {lon})")
# print(f"Powrót do depotu ({depot_lat}, {depot_lon})")
#
# display_tsp_route_on_map(depot_lat, depot_lon, best_route, "Brute_force.html")
#
# print("\n")

best_distance, best_route = nearest_neighbor(random_companies, depot_lat, depot_lon)
print(f"Najkrótsza trasa (Może): {best_distance:.2f} km")
print("Kolejność odwiedzin miast:")
# for lat, lon, name in best_route:
#     print(f"{name} ({lat}, {lon})")

display_tsp_route_on_map(depot_lat, depot_lon, best_route, "Najbl_sąsiad.html")

def repeated_nearest_neighbor(companies, depot_lat, depot_lon, iterations=10):
    best_total_distance = float('inf')
    best_route = []

    for _ in range(iterations):
        unvisited = [(company['latitude'], company['longitude'], company['name']) for company in companies]
        current_company = random.choice(unvisited)
        current_lat, current_lon = current_company[0], current_company[1]
        route = [current_company]
        unvisited.remove(current_company)
        total_distance = haversine(depot_lat, depot_lon, current_lat, current_lon)

        while unvisited:
            nearest = min(unvisited, key=lambda city: haversine(current_lat, current_lon, city[0], city[1]))
            unvisited.remove(nearest)
            route.append(nearest)
            total_distance += haversine(current_lat, current_lon, nearest[0], nearest[1])
            current_lat, current_lon = nearest[0], nearest[1]

        total_distance += haversine(current_lat, current_lon, depot_lat, depot_lon)

        if total_distance < best_total_distance:
            best_total_distance = total_distance
            best_route = route

    return best_total_distance, best_route

# Przykładowe użycie:
iterations = 10  # Liczba iteracji do wykonania
best_distance, best_route = repeated_nearest_neighbor(random_companies, depot_lat, depot_lon, iterations)

print(f"Najkrótsza trasa (po {iterations} iteracjach): {best_distance:.2f} km")
print("Kolejność odwiedzin miast:")
# for lat, lon, name in best_route:
#     print(f"{name} ({lat}, {lon})")

display_tsp_route_on_map(depot_lat, depot_lon, best_route, "Powtarzalny_Najbl_sąsiad.html")



