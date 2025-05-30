import json
import requests
import os
import pandas as pd
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
import pyspark.sql.functions as F

JSON_FILE = 'all_coasters.json'

def extract_coaster_id_by_park(data, park_names):
    result = []
    for item in data:
        if item.get('park', {}).get('name') in park_names:
            result.append(item)
    return result

def open_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def get_coaster_info_by_id(coaster_list):
    ids = [item['id'] for item in coaster_list]
    base_url = 'https://captaincoaster.com/api/coasters/'
    headers = {
        'accept': 'application/ld+json',
        'Authorization': '47cbe095-3b64-404b-8e7f-1e94fca94940'
    }
    coaster_info = []
    for coaster_id in ids:
        response = requests.get(f"{base_url}{coaster_id}", headers=headers)
        if response.status_code == 200:
            coaster_info.append(response.json())
        else:
            print(f"Failed to retrieve data for coaster ID {coaster_id}")
    return coaster_info

def filter_coaster_info(coaster_info):
    spark = SparkSession.builder.appName("CoasterInfo").getOrCreate()
    schema = StructType([
        StructField('id', IntegerType(), True),
        StructField('Nom', StringType(), True),
        StructField('park_name', StringType(), True),
        StructField('manufacturer_name', StringType(), True),
        StructField('model_name', StringType(), True),
        StructField('opening_date', StringType(), True),
        StructField('height', IntegerType(), True),
        StructField('speed', IntegerType(), True),
        StructField('length', IntegerType(), True),
        StructField('inversions_number', IntegerType(), True),
        StructField('status', StringType(), True)
    ])
    data = [{
        'id': coaster.get('id'),
        'Nom': coaster.get('name'),
        'park_name': coaster.get('park', {}).get('name'),
        'manufacturer_name': coaster.get('manufacturer', {}).get('name'),
        'model_name': coaster.get('model', {}).get('name'),
        'opening_date': coaster.get('openingDate'),
        'height': coaster.get('height'),
        'speed': coaster.get('speed'),
        'length': coaster.get('length'),
        'inversions_number': coaster.get('inversionsNumber'),
        'status': coaster.get('status', {}).get('name'),
    } for coaster in coaster_info]
    df = spark.createDataFrame(data, schema)
    return df

def filter_by_status(df: DataFrame) -> DataFrame:
    return (
        df
        .filter(
            (F.col("status") == 'status.operating')
        )
        .select(
            "id",
            "Nom",
            "park_name",
            "manufacturer_name",
            "model_name",
            "opening_date",
            "height",
            "speed",
            "length",
            "inversions_number"
        )
    )

def process_park(park_name):
    data = open_json_file(JSON_FILE)
    filtered_data = extract_coaster_id_by_park(data, [park_name])
    if not filtered_data:
        print(f"No coasters found for park: {park_name}")
        return
    coaster_info = get_coaster_info_by_id(filtered_data)
    df_filtered = filter_coaster_info(coaster_info)
    df_final = filter_by_status(df_filtered)
    df_final_pd = df_final.toPandas()
    excel_path = 'coasters_info.xlsx'
    if os.path.exists(excel_path):
        existing_df = pd.read_excel(excel_path)
        if 'rank' in existing_df.columns and not existing_df['rank'].isnull().all():
            max_rank = existing_df['rank'].max()
            if pd.isnull(max_rank):
                max_rank = 0
        else:
            max_rank = 0
        df_final_pd['rank'] = range(max_rank + 1, max_rank + 1 + len(df_final_pd))
        combined_df = pd.concat([existing_df, df_final_pd], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=['Nom'])
    else:
        df_final_pd['rank'] = range(1, len(df_final_pd) + 1)
        combined_df = df_final_pd
    combined_df.to_excel(excel_path, index=False)
    print(f"Coaster information for '{park_name}' has been appended to 'coasters_info.xlsx'")

if __name__ == "__main__":
    park_name = input("Enter the park name: ")
    process_park(park_name)
