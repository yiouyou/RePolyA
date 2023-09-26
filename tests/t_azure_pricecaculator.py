class MySqlPricingCalculator:
    def __init__(self, sku_prices):
        self.sku_prices = sku_prices
        self.sku_categories = {
            'compute': [
                [['deployment', 'tier', 'compute'], ['perhour', 'perhouroneyearreserved', 'perhourthreeyearreserved']],
                [['tier', 'compute', 'vCore'], ['perhour', 'perhouroneyearreserved']]
            ],
            'storage': [
                [['deployment', 'tier'], ['pergb']],
                [['tier'], ['pergb']]
            ],
            'iops': [
                [['iops', 'storage'], ['permillionoperations']],
                [['iops'], ['periopspermonth']]
            ],
            'backup': [
                [['deployment', 'tier', 'backup'], ['pergb']],
                [['tier', 'backup'], ['pergb']],
            ]
        }

    def get_sku(self, options, usage_unit, category, sku_formats):
        ii = {}
        for i in sku_formats:
            i_part = i[0]
            i_unit = i[1]
            if usage_unit[category][-1] in i_unit:
                jj = {}
                for j in self.sku_prices:
                    n = 0
                    i_key = {}
                    for x in i_part:
                        i_key[options[x]] = 1
                    i_key[usage_unit[category][-1]] = 1
                    i_key[category] = 1
                    for k in i_key.keys():
                        if k in j:
                            n += i_key[k]
                    jj[j] = n
                max_jj = max(jj, key=jj.get)
                # print(max_jj, jj[max_jj])
                if jj[max_jj] == len(i_part) + 2:
                    if max_jj not in ii.keys():
                        ii[max_jj] = jj[max_jj]
                    elif jj[max_jj] > ii[max_jj]:
                        ii[max_jj] = jj[max_jj]
        if ii:
            max_ii = max(ii, key=ii.get)
            if category == 'compute' and options['compute'] not in max_ii:
                return None
            else:
                return max_ii
        else:
            return None

    def calculate_price(self, options, usage_unit):
        total_price = 0
        for category, sku_formats in self.sku_categories.items():
            sku_key = ''
            print('-'*40)
            _sku = self.get_sku(options, usage_unit, category, sku_formats)
            print(_sku)
            if _sku is not None:
                sku_key = _sku
            category_usage = usage_unit[category][0]
            sku_price = self.sku_prices.get(sku_key, 0)
            if category == 'compute':
                category_usage *= usage_unit['servers'][0]
            if category == 'backup':
                category_usage *= usage_unit['backupConsumedX'][0]
            category_price = sku_price * category_usage
            total_price += category_price
            # print(">",sku_key)
            if category_price > 0:
                print(f"{sku_price} * {category_usage} = {round(category_price, 2)}, {category}, {sku_key}")
        return round(total_price, 2)


# Test Code
if __name__ == "__main__":
    import json
    with open('azure_mysql_sku_price_europe-west.json', 'r') as rf:
        sku_prices = json.load(rf)
    
    calculator = MySqlPricingCalculator(sku_prices)

    options = {
        'deployment': 'server',
        'tier': 'basic',
        'compute': 'g5',
        'vCore': '1',
        'storage': '',
        'iops': '',
        'backup': 'lrs'
    }
    usage_unit = {
        'servers': [1, 'x'],
        'compute': [730, 'perhour'],
        'storage': [500, 'pergb'],
        'iops': [0, 'periopspermonth'],
        'backup': [100, 'pergb'],
        'backupConsumedX': [1, 'x']
    }
    price = calculator.calculate_price(options, usage_unit)
    print(price)

    options = {
        'deployment': 'flexible-server',
        'tier': 'generalpurpose',
        'compute': 'd2asv4',
        'vCore': '4',
        'storage': 'zrs',
        'iops': 'additional',
        'backup': 'lrs'
    }
    usage_unit = {
        'servers': [3, 'x'],
        'compute': [730, 'perhourthreeyearreserved'],
        'storage': [5, 'pergb'],
        'iops': [1000, 'periopspermonth'],
        'backup': [100, 'pergb'],
        'backupConsumedX': [1, 'x']
    }
    price = calculator.calculate_price(options, usage_unit)
    print(price)

