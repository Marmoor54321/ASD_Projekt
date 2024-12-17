import csv
from math import radians, cos, sin, sqrt, atan2

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
    R = 6371.0  # promień Ziemi w kilometrach
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
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


companies = load_data('Warszawa.csv')
address_to_search = 'al. Aleja Wojska Polskiego 9'
nearest_companies = find_nearest_company_by_address(companies, address_to_search)


#48.446511795151835, 2.9218599119035646
print(find_nearest_company(companies, 53.119160718649454, 23.132878086305183))

#print(find_coordinates_by_address(companies,'Aleja Dzieci Polskich 67C'))

#print_nearest_company(nearest_companies, address_to_search)

#print_nearest_company(nearest_companies2, None)


