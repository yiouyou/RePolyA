import json
import random
from pprint import pprint


file_path = "azure_mysql.json"  # JSON文件的路径
with open(file_path, 'r') as file:
    pricing_data = json.load(file)

_options = {}
_keys = pricing_data.keys()
for i in _keys:
    if i not in ['offers', 'regions', 'discounts', 'resources', 'schema', 'skus', 'responseId', 'responseTime']:
        # print(f"\n## {i}")
        _options[i] = []
        for j in pricing_data[i]:
            # print(f"- {j['slug']}")
            _options[i].append(j['slug'])

print("## pricing related options")
pprint(_options)

sku_price = {}
offers = pricing_data['offers']
# print(f"\n## offers")
for i in offers:
    prices = offers[i]['prices']
    for j in prices:
        # print(f"{i} ({j}): {prices[j]['us-east']['value']}")
        sku_price[f"{i}--{j}"] = prices[j]['us-east']['value']

with open('azure_mysql_sku_price.json', 'w') as wf:
    wf.write(json.dumps(sku_price, indent=4, ensure_ascii=False))

skus = pricing_data['skus']
print(f"\n## skus examples")
for i in skus.keys():
    for j in skus[i].keys():
        _sku = skus[i][j][0]
        if _sku in sku_price.keys():
            # print(f"{_sku}: {sku_price[_sku]}")
            if random.random() < 1/10:
                print(f"{_sku}")
        else:
            print(F"ERROR: {_sku}")

_variables = [f"'{var}'" for var in _options]
_vs = ", ".join(_variables)
_desp = f"""----------
{_vs} are the available options to Azure MySQL service pricing caculator. 'skus examples' shows the naming rules of a single SKU. Please design a 'MySqlPricingCalculator' class based on the above information to calculate the mysql service price given the choosen options and actual usage of mysql. Assume sku_prices data (A dictionary containing SKU as a key and price as value) is given, and take following options and usage as the input:
```
    options = {{
        'deployment': 'flexible-server',
        'tier': 'generalpurpose',
        'compute': 'd2asv4',
        'vCore': '4',
        'storage': 'zrs',
        'iops': 'additional',
        'backup': 'lrs'
    }}
    usage_unit = {{
        'servers': [3, 'x'],
        'compute': [730, 'perhourthreeyearreserved'],
        'storage': [5, 'pergb'],
        'iops': [1000, 'periopspermonth'],
        'backup': [100, 'pergb'],
        'backupConsumedX': [1, 'x']
    }}
```
Please follow the idea of the following code:
```
        sku_categories = {{
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
        }}
        for category, sku_formats in sku_categories.items():
            sku_key = ''
            ii = {{}}
            print('-'*40)
            for i in sku_formats:
                i_part = i[0]
                i_unit = i[1]
                if usage_unit[category][-1] in i_unit:
                    jj = {{}}
                    for j in sku_prices:
                        n = 0
                        i_key = {{}}
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
            max_ii = max(ii, key=ii.get)
            if category == 'compute' and options['compute'] not in max_ii:
                return None
            else:
                sku_key = max_ii
            category_usage = usage_unit[category][0]
            sku_price = self.sku_prices.get(sku_key, 0)
            if category == 'compute':
                category_usage *= usage_unit['servers'][0]
            if category == 'backup':
                category_usage *= usage_unit['backupConsumedX'][0]
            category_price = round(sku_price * category_usage, 2)
            total_price += category_price
        return round(total_price, 2)
```
Now, please output class code, test code and short comments, nothing else:"""
print(_desp)

