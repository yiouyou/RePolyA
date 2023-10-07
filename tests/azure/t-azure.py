# import os
# _RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# import sys
# sys.path.append(_RePolyA)


# from repolya.azure.app import run
# run("Create a system that can summarize a powerpoint file", "PPT")


import json
with open('azure_mysql_sku_price_europe-west.json', 'r') as rf:
    sku_prices = json.load(rf)

import pandas as pd

# # 读取所有sheets
# all_sheets = pd.read_excel('azure_mysql.xlsx', sheet_name=None)
# # 遍历每个sheet并读取数据
# for sheet_name, sheet in all_sheets.items():
#     print(sheet_name)
#     print(sheet)


##### 
perf_sheets = pd.read_excel('azure_mysql.xlsx', sheet_name='MySQL | Perf')
# for col in perf_sheets.columns:
#     print(col)

_sku_col = [
    'id',
    'skuname',
    'skutier',
    'storageSizeGB',
    'storageSku',
    'highAvailability',
    'highAvailabilityZone'
]

_sku = perf_sheets[_sku_col]


def compute_sku(row):
    _type = row['skuname'].replace('Standard_', '').replace('_', '').lower()
    _tier = row['skutier'].lower()
    _compute_sku = f"flexible-server-{_tier}-compute-{_type}--perhour"
    if _compute_sku in sku_prices.keys():
        return _compute_sku
    else:
        return None

def storage_sku(row):
    _type = row['skuname'].replace('Standard_', '').replace('_', '').lower()
    _tier = row['skutier'].lower()
    _storage_sku = f"flexible-server-{_tier}-storage--pergb"
    if _storage_sku in sku_prices.keys():
        return _storage_sku
    else:
        return None

def backup_sku(row):
    _type = row['skuname'].replace('Standard_', '').replace('_', '').lower()
    _tier = row['skutier'].lower()
    _redundancy = ''
    if row['highAvailabilityZone'] == 2:
        _redundancy = 'grs'
    elif row['highAvailabilityZone'] == 1:
        _redundancy = 'lrs'
    if _redundancy:
        _backup_sku = f"flexible-server-{_tier}-backup-{_redundancy}--pergb"
        if _backup_sku in sku_prices.keys():
            return _backup_sku
        else:
            return None

wrong_index = []
for index, row in _sku.iterrows():
    _type = row['skuname'].replace('Standard_', '').replace('_', '').lower()
    _tier = row['skutier'].lower()
    print('-'*40)
    ### compute
    _compute_sku = f"flexible-server-{_tier}-compute-{_type}--perhour"
    if _compute_sku in sku_prices.keys():
        print(index, sku_prices[_compute_sku], _compute_sku)
    else:
        ### 不考虑有错的
        print(index, _compute_sku)
        wrong_index.append(index)
    ### storage, storageSku LRS/ZRS, 价格没区别，没体现在sku_key里
    _storage_sku = f"flexible-server-{_tier}-storage--pergb"
    if _storage_sku in sku_prices.keys():
        print(index, sku_prices[_storage_sku], _storage_sku)
    else:
        ### 不考虑有错的
        print(index, _storage_sku)
        wrong_index.append(index)
    ### backup
    _redundancy = ''
    if row['highAvailabilityZone'] == 2:
        _redundancy = 'grs'
    elif row['highAvailabilityZone'] == 1:
        _redundancy = 'lrs'
    if _redundancy:
        _backup_sku = f"flexible-server-{_tier}-backup-{_redundancy}--pergb"
        if _backup_sku in sku_prices.keys():
            print(index, sku_prices[_backup_sku], _backup_sku)
        else:
            ### 不考虑有错的
            print(index, _backup_sku)
            wrong_index.append(index)
print(wrong_index)


# print('='*40)
# for index, row in _sku.iterrows():
#     if index not in wrong_index:
#         _compute_sku = compute_sku(row)
#         _storage_sku = storage_sku(row)
#         _backup_sku = backup_sku(row)
#         print(f"\n{index}")
#         if _compute_sku:
#             print(f"{sku_prices[_compute_sku]}, {_compute_sku}")
#         if _storage_sku:
#             print(f"{sku_prices[_storage_sku]}, {_storage_sku}")
#         if _backup_sku:
#             print(f"{sku_prices[_backup_sku]}, {_backup_sku}")


_perf_col = [
    'cpu_percentp95_max',
    'memory_percentp95_max',
    'storage_percentp95_max',
    'io_consumption_percentp95_max'
]

import re
from functools import partial

def repl(i, match):
    if match.group(4):
        _s = f"{match.group(1)}{i}{match.group(3)}v4"
    else:
        _s = f"{match.group(1)}{i}{match.group(3)}"
    return _s

def compute_downgrade(_compute_sku, sku_prices):
    _s1 = _compute_sku.split('--')[0]
    _s2 = _s1.split('-')[-1]
    _new = []
    match = re.search(r'(\w+)(\d+)(\w+)(v4)?$', _s2)
    if match:
        num = int(match.group(2))
        if num > 1 and num % 2 == 0:
            # print(num)
            n = 1
            while num % (2 ** n) ==0:
                _new.append(int(num/(2**n)))
                n += 1
    if _new:
        # print(_new)
        _key = []
        for i in _new:
            _new_s2 = re.sub(r'(\w+)(\d+)(\w+)(v4)?$', partial(repl, i), _s2)
            _sku_key = _compute_sku.replace(_s2, _new_s2)
            if _sku_key in sku_prices.keys():
                _key.append(_sku_key)
                # print(_sku_key)
        return _key
    else:
        return None


print('='*40)
for index, row in perf_sheets.iterrows():
    if index not in wrong_index:
        _compute_sku = compute_sku(row)
        _storage_sku = storage_sku(row)
        _backup_sku = backup_sku(row)
        _cpu = row['cpu_percentp95_max']
        _storage = row['storage_percentp95_max']
        _io = row['io_consumption_percentp95_max']
        print(f"\n{index} ({row['name']}): {_cpu}(cpu), {_storage}(storage), {_io}(io)")
        ### compute
        print('compute', '-'*40)
        if _compute_sku:
            print(f"{sku_prices[_compute_sku]}, {_compute_sku}")
        if _cpu < 50:
            _down = compute_downgrade(_compute_sku, sku_prices)
            if _down is not None:
                if _down:
                    for i in _down:
                        print(f">>> {_cpu}(cpu): {sku_prices[_compute_sku]} -> {sku_prices[i]}, {i}")
        ### storage
        print('storage', '-'*40)
        if _storage_sku:
            print(f"{sku_prices[_storage_sku]}, {_storage_sku}")
        # if _storage < 50:
        #     print('-'*20)
        #     print(f"{_storage}(storage): downgraded to")
        # ### io, NO IOS sku info
        # print('-'*40)
        # if _io < 50:
        #     print(f"{_io}(io): downgraded to")
        # ### bakcup, NO backup perf info
        # if _backup_sku:
        #     print(f"{sku_prices[_backup_sku]}, {_backup_sku}")



_perf_col_all = [
    'cpu_percentp95_max',
    'cpu_percentp99_max',
    'cpu_percentp100_max',
    'memory_percentp95_max',
    'memory_percentp99_max',
    'memory_percentp100_max',
    'cpu_credits_consumedp95_max',
    'cpu_credits_consumedp99_max',
    'cpu_credits_consumedp100_max',
    'cpu_credits_remainingp95_max',
    'cpu_credits_remainingp99_max',
    'cpu_credits_remainingp100_max',
    'network_bytes_ingressp95_max',
    'network_bytes_ingressp99_max',
    'network_bytes_ingressp100_max',
    'network_bytes_egressp95_max',
    'network_bytes_egressp99_max',
    'network_bytes_egressp100_max',
    'active_connectionsp95_max',
    'active_connectionsp99_max',
    'active_connectionsp100_max',
    'io_consumption_percentp95_max',
    'io_consumption_percentp99_max',
    'io_consumption_percentp100_max',
    'storage_percentp95_max',
    'storage_percentp99_max',
    'storage_percentp100_max',
    'total_connectionsp95_max',
    'total_connectionsp99_max',
    'total_connectionsp100_max',
    'queries'
]



##### 比对 'MySQL | SKU (Manual)' 和 azure_mysql_sku_price_europe-west.json
# sku_sheet = pd.read_excel('azure_mysql.xlsx', sheet_name='MySQL | SKU (Manual)')
# _sku = sku_sheet[['Deployment Option', 'Tier', 'Type', 'Cores', 'Price']]
# for index, row in _sku.iterrows():
#     _depl = row['Deployment Option'].replace(' ', '-').lower()
#     _tier = row['Tier'].replace(' ', '').lower()
#     _type = row['Type'].replace('_', '').lower()
#     if _depl == 'single-server':
#         _sku_key = f"{_tier}-compute-{_type.replace('gen5', 'g5')}-{row['Cores']}--perhour"
#     else:
#         _sku_key = f"{_depl}-{_tier}-compute-{_type}--perhour" # flexible-server-businesscritical-compute-e8asv4--perhour
#     # print(_depl, _tier, _type, _sku_key)
#     if _sku_key in sku_prices.keys():
#         if row['Price'] != sku_prices[_sku_key]:
#             print(index, row['Price'], sku_prices[_sku_key], _depl, _tier, _type, _sku_key)
#     else:
#         print(_depl, _tier, _type, _sku_key)




