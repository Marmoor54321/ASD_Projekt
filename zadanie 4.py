import time
import csv
import random
import openrouteservice as ors
import folium
import os
import json
import math


client = ors.Client(key='5b3ce3597851110001cf624890e6125065a644b4ad5fa0e2a05d158e')


cache_file = "distance_cache.json"


if os.path.exists(cache_file):
    with open(cache_file, "r") as f:
        distance_cache = json.load(f)
        distance_cache = {tuple(eval(key)): value for key, value in distance_cache.items()}
else:
    distance_cache = {}

def save_cache():
    json_cache = {str(key): value for key, value in distance_cache.items()}
    with open(cache_file, "w") as f:
        json.dump(json_cache, f)

def get_distance(client, coord1, coord2):
    key = tuple(sorted([coord1, coord2]))
    if key in distance_cache:
        return distance_cache[key]
    else:
        route = client.directions(coordinates=[coord1, coord2], profile='driving-car', format='geojson')
        distance = route['features'][0]['properties']['segments'][0]['distance'] / 1000.0
        distance_cache[key] = distance
        save_cache()
        return distance

def load_data(file_path):
    companies = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['latitude'] = float(row['latitude'])
            row['longitude'] = float(row['longitude'])
            companies.append(row)
    return companies

def generate_distance_matrix(locations):
    n = len(locations)
    matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            coord1 = (locations[i]['longitude'], locations[i]['latitude'])
            coord2 = (locations[j]['longitude'], locations[j]['latitude'])
            distance = get_distance(client, coord1, coord2)
            matrix[i][j] = matrix[j][i] = distance
    return matrix

def repeated_nearest_neighbor(companies, depot_index, distance_matrix, iterations=5):
    best_total_distance = float('inf')
    best_route = []
    for _ in range(iterations):
        unvisited = list(range(len(companies)))
        current_index = depot_index
        route = [current_index]
        total_distance = 0

        unvisited.remove(current_index)
        while unvisited:
            nearest = min(unvisited, key=lambda i: distance_matrix[current_index][i])
            total_distance += distance_matrix[current_index][nearest]
            current_index = nearest
            route.append(current_index)
            unvisited.remove(current_index)

        total_distance += distance_matrix[current_index][depot_index]
        if total_distance < best_total_distance:
            best_total_distance = total_distance
            best_route = route

    return best_total_distance, best_route

def simulated_annealing(distance_matrix, depot_index, initial_temp=10000, cooling_rate=0.9995, stopping_temp=1e-8):
    def calculate_total_distance(route):
        total = sum(distance_matrix[route[i]][route[i + 1]] for i in range(len(route) - 1))
        total += distance_matrix[route[-1]][route[0]]
        return total

    n = len(distance_matrix)
    current_route = list(range(n))
    current_distance = calculate_total_distance(current_route)
    temperature = initial_temp
    best_route = current_route[:]
    best_distance = current_distance

    while temperature > stopping_temp:
        new_route = current_route[:]
        a, b = random.sample(range(1, n), 2)
        new_route[a], new_route[b] = new_route[b], new_route[a]

        new_distance = calculate_total_distance(new_route)
        delta_distance = new_distance - current_distance

        if delta_distance < 0 or random.random() < math.exp(-delta_distance / temperature):
            current_route = new_route
            current_distance = new_distance

            if new_distance < best_distance:
                best_distance = new_distance
                best_route = new_route[:]

        temperature *= cooling_rate

    return best_distance, best_route

def display_tsp_route_on_map(locations, route, total_distance, file_name):
    m = folium.Map(location=[locations[0]['latitude'], locations[0]['longitude']], tiles="cartodbpositron", zoom_start=12)

    folium.Marker(
        location=[locations[0]['latitude'], locations[0]['longitude']],
        popup="Depot (Start/End)",
        icon=folium.Icon(color="red")
    ).add_to(m)

    for i in range(len(route) - 1):
        start = locations[route[i]]
        end = locations[route[i + 1]]

        folium.Marker(
            location=[end['latitude'], end['longitude']],
            popup=f"Stop {i + 1}: {end['name']}",
            icon=folium.Icon(color="blue")
        ).add_to(m)

    m.save(file_name)
    print(f"Map saved to {file_name}")


random.seed(5323)
companies = load_data('Warszawa.csv')
k = 40
random_companies = random.sample(companies, k)
random_companies.insert(0, {'latitude': 52.2296756, 'longitude': 21.0122287, 'name': 'Depot'})

distance_matrix = generate_distance_matrix(random_companies)

start_time = time.time()
rnn_distance, rnn_route = repeated_nearest_neighbor(random_companies, 0, distance_matrix)
rnn_time = time.time() - start_time

start_time = time.time()
sa_distance, sa_route = simulated_annealing(distance_matrix, 0)
sa_time = time.time() - start_time

print(f"Repeated Nearest Neighbor: Distance = {rnn_distance:.5f} km, Time = {rnn_time:.5f} seconds")
print(f"Simulated Annealing: Distance = {sa_distance:.5f} km, Time = {sa_time:.5f} seconds")

display_tsp_route_on_map(random_companies, rnn_route, rnn_distance, "rnn_route.html")
display_tsp_route_on_map(random_companies, sa_route, sa_distance, "sa_route.html")
