import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append(_RePolyA)


# from repolya.azure.app import run
# run("Create a system that can summarize a powerpoint file", "PPT")


import pandas as pd

# 读取所有sheets
all_sheets = pd.read_excel('azure_mysql.xlsx', sheet_name=None)

# 遍历每个sheet并读取数据
for sheet_name, sheet in all_sheets.items():
    print(sheet_name)
    print(sheet)

