import pytest
from .t_azure_pricecaculator import MySqlPricingCalculator
import json


# Define the test fixture
@pytest.fixture
def calculator():
    with open('azure_mysql_sku_price_europe-west.json', 'r') as rf:
        sku_prices = json.load(rf)
    return MySqlPricingCalculator(sku_prices=sku_prices)


def test_calculator_0(calculator):
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
    expected_price = 100.45
    assert calculator.calculate_price(options=options, usage_unit=usage_unit) == expected_price


def test_calculator_1(calculator):
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
    expected_price = 248.84
    assert calculator.calculate_price(options=options, usage_unit=usage_unit) == expected_price

