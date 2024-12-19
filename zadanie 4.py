import time
import csv
import random
import openrouteservice as ors
import folium
from itertools import permutations
import networkx as nx
import os
import json

# OpenRouteService client
client = ors.Client(key='5b3ce3597851110001cf624890e6125065a644b4ad5fa0e2a05d158e')

# Cache file for distances
cache_file = "distance_cache.json"

# Load cache
if os.path.exists(cache_file):
    with open(cache_file, "r") as f:
        distance_cache = json.load(f)
        # Convert keys back to tuples after loading
        distance_cache = {tuple(eval(key)): value for key, value in distance_cache.items()}
else:
    distance_cache = {}


def save_cache():
    """Save the distance cache to a file."""
    # Convert tuple keys to strings for JSON compatibility
    json_cache = {str(key): value for key, value in distance_cache.items()}
    with open(cache_file, "w") as f:
        json.dump(json_cache, f)


def get_distance(client, coord1, coord2):
    """Get the distance between two coordinates, using the cache if possible."""
    key = tuple(sorted([coord1, coord2]))  # Symmetric key
    if key in distance_cache:
        return distance_cache[key]
    else:
        route = client.directions(coordinates=[coord1, coord2], profile='driving-car', format='geojson')
        distance = route['features'][0]['properties']['segments'][0]['distance'] / 1000.0  # in km
        distance_cache[key] = distance
        save_cache()  # Save updated cache
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
    """Generate a symmetric distance matrix for the given locations."""
    n = len(locations)
    matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            coord1 = (locations[i]['longitude'], locations[i]['latitude'])
            coord2 = (locations[j]['longitude'], locations[j]['latitude'])
            distance = get_distance(client, coord1, coord2)
            matrix[i][j] = matrix[j][i] = distance
    return matrix


def repeated_nearest_neighbor(companies, depot_index, distance_matrix, iterations=10):
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


def christofides_algorithm(distance_matrix):
    n = len(distance_matrix)
    graph = nx.Graph()
    for i in range(n):
        for j in range(i + 1, n):
            graph.add_edge(i, j, weight=distance_matrix[i][j])

    mst = nx.minimum_spanning_tree(graph)

    odd_degree_nodes = [node for node in mst.nodes if mst.degree[node] % 2 == 1]

    odd_subgraph = graph.subgraph(odd_degree_nodes)

    matching = nx.algorithms.matching.min_weight_matching(odd_subgraph, weight="weight")

    multigraph = nx.MultiGraph(mst)
    for u, v in matching:
        multigraph.add_edge(u, v, weight=graph[u][v]['weight'])

    eulerian_circuit = list(nx.eulerian_circuit(multigraph))

    visited = set()
    hamiltonian_path = []
    total_distance = 0
    for u, v in eulerian_circuit:
        if u not in visited:
            hamiltonian_path.append(u)
            visited.add(u)
            if len(hamiltonian_path) > 1:
                total_distance += graph[hamiltonian_path[-2]][hamiltonian_path[-1]]['weight']

    total_distance += graph[hamiltonian_path[-1]][hamiltonian_path[0]]['weight']
    hamiltonian_path.append(hamiltonian_path[0])

    return total_distance, hamiltonian_path


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

        coords = [(start['longitude'], start['latitude']), (end['longitude'], end['latitude'])]
        route_geo = client.directions(coordinates=coords, profile='driving-car', format='geojson')

        folium.PolyLine(
            locations=[list(reversed(coord)) for coord in route_geo['features'][0]['geometry']['coordinates']],
            color="blue",
            weight=2.5
        ).add_to(m)

    folium.PolyLine(
        locations=[[locations[route[-2]]['latitude'], locations[route[-2]]['longitude']],
                   [locations[route[0]]['latitude'], locations[route[0]]['longitude']]],
        color="green",
        weight=2.5
    ).add_to(m)

    m.save(file_name)
    print(f"Map saved to {file_name}")


# Main execution
random.seed(5323)
companies = load_data('Warszawa.csv')
k = 40
random_companies = random.sample(companies, k)
random_companies.insert(0, {'latitude': 52.2296756, 'longitude': 21.0122287, 'name': 'Depot'})

distance_matrix = generate_distance_matrix(random_companies)

start_time = time.time()
rnn_distance, rnn_route = repeated_nearest_neighbor(random_companies, 0, distance_matrix)
rnn_time = time.time() - start_time

# start_time = time.time()
# chr_distance, chr_route = christofides_algorithm(distance_matrix)
# chr_time = time.time() - start_time

print(f"Repeated Nearest Neighbor: Distance = {rnn_distance:.5f} km, Time = {rnn_time:.5f} seconds")
#print(f"Christofides: Distance = {chr_distance:.5f} km, Time = {chr_time:.2f} seconds")

display_tsp_route_on_map(random_companies, rnn_route, rnn_distance, "Najbl_sasiad++_route.html")
#display_tsp_route_on_map(random_companies, chr_route, chr_distance, "christofides.html")
