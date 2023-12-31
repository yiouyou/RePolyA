# filename: recommend2.py

def get_service_price(path_of_service_options, given_service):
    with open(path_of_service_options, 'r') as f:
        for line in f:
            service, price = line.strip().split(', ')
            if service == given_service:
                return float(price)
    return None

def cheapest_option(path_of_service_options, given_service):
    given_price = get_service_price(path_of_service_options, given_service)
    if given_price is None:
        return None, None

    given_os = given_service.split('-')[0]
    cheapest_service = None
    cheapest_price = float('inf')

    with open(path_of_service_options, 'r') as f:
        for line in f:
            service, price = line.strip().split(', ')
            os = service.split('-')[0]
            price = float(price)

            if os == given_os and 0.0 < price < given_price and price < cheapest_price:
                cheapest_service = service
                cheapest_price = price

    if cheapest_service is None:
        return None, None
    else:
        return cheapest_service, cheapest_price