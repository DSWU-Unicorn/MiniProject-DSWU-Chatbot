import csv
import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

input_file_name = "crawling_library_notice_content.csv"
output_file_name = "../notice.json"

data = {}

with open(input_file_name, "r", encoding='utf-8-sig') as csv_f:
    csvReader = csv.DictReader(csv_f)
    for rows in csvReader:
        print(rows)
        id = rows['id']
        data[id] = rows
with open(output_file_name, "w", encoding='utf-8-sig') as json_f:
    json_f.write(json.dumps(data, ensure_ascii=False))
