# filename: recommend.py

def parse_service_options(path_of_service_options):
    with open(path_of_service_options, 'r') as f:
        lines = f.readlines()
    service_options = {}
    for line in lines:
        service, price = line.strip().split(', ')
        os = service.split('-')[0]
        if os not in service_options:
            service_options[os] = {}
        service_options[os][service] = float(price)
    return service_options

def get_service_price(path_of_service_options, given_service):
    service_options = parse_service_options(path_of_service_options)
    os = given_service.split('-')[0]
    if os in service_options and given_service in service_options[os]:
        return service_options[os][given_service]
    return None

def cheapest_option(path_of_service_options, given_service):
    service_options = parse_service_options(path_of_service_options)
    os = given_service.split('-')[0]
    if os in service_options:
        services = [(service, price) for service, price in service_options[os].items() if price < service_options[os][given_service] and price != 0.0]
        if services:
            return min(services, key=lambda x: x[1])
    return None, None