import csv

def load_data(file_path):
    companies = {}
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            address = row['address'].strip().lower()
            if address not in companies:
                companies[address] = []
            companies[address].append(row)
    return companies

def find_company_by_address(companies, address):
    address = address.strip().lower()
    return companies.get(address, None)

# Przykładowe użycie
companies = load_data('Warszawa.csv')
address_to_search = 'al. Aleja Wojska Polskiego 9'
found_companies = find_company_by_address(companies, address_to_search)

if found_companies:
    for company in found_companies:
        print(company)
else:
    print("Nie znaleziono firmy pod tym adresem.")
