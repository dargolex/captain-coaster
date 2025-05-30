import json
import os
import pandas as pd
import requests

JSON_FILE = os.environ.get('JSON_FILE')
EXCEL_FILE = os.environ.get('EXCEL_FILE')
API_URL = os.environ.get('API_URL')
API_KEY = os.environ.get('API_KEY')

COLUMNS = [
    'id', 'name', 'park_name', 'manufacturer_name', 'model_name',
    'opening_date', 'height', 'speed', 'length', 'inversions_number', 'status'
]


def load_all_coasters():
    with open(JSON_FILE, 'r') as f:
        return json.load(f)


def filter_coasters_by_park(data, park_name):
    return [item for item in data if item.get('park', {}).get('name') == park_name]


def fetch_coaster_details(coaster_ids):
    headers = {
        'accept': 'application/ld+json',
        'Authorization': API_KEY
    }
    details = []
    for cid in coaster_ids:
        resp = requests.get(f"{API_URL}{cid}", headers=headers)
        if resp.status_code == 200:
            details.append(resp.json())
    return details


def extract_coaster_info(coaster):
    return {
        'id': coaster.get('id'),
        'Name': coaster.get('name'),
        'Park': coaster.get('park', {}).get('name'),
        'Manufacturer': coaster.get('manufacturer', {}).get('name'),
        'Model': coaster.get('model', {}).get('name'),
        'Opening Year': coaster.get('openingDate'),
        'Height': coaster.get('height'),
        'Max Speed': coaster.get('speed'),
        'Length': coaster.get('length'),
        'Inversions': coaster.get('inversionsNumber'),
        'status': coaster.get('status', {}).get('name'),
    }


def get_operating_coasters(coaster_details):
    return [
        extract_coaster_info(c)
        for c in coaster_details
        if c.get('status', {}).get('name') == 'status.operating'
        and c.get('speed') is not None
        and c.get('speed') > 40
    ]


def append_coasters_to_excel(new_coasters):
    if not new_coasters:
        return False, 'No new coasters to add.'
    new_df = pd.DataFrame(new_coasters)
    new_df = new_df.drop(columns=['status'])
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        if 'rank' in df.columns and not df['rank'].isnull().all():
            max_rank = df['rank'].max()
            if pd.isnull(max_rank):
                max_rank = 0
        else:
            max_rank = 0
        new_df['rank'] = range(max_rank + 1, max_rank + 1 + len(new_df))
        combined = pd.concat([df, new_df], ignore_index=True)
        combined = combined.drop_duplicates(subset=['Name'])
    else:
        new_df['rank'] = range(1, len(new_df) + 1)
        combined = new_df
    combined.to_excel(EXCEL_FILE, index=False)
    return True, f"Added {len(new_df)} coasters."


def add_park_by_name(park_name):
    data = load_all_coasters()
    filtered = filter_coasters_by_park(data, park_name)
    if not filtered:
        return False, f"No coasters found for park: {park_name}"
    ids = [item['id'] for item in filtered]
    details = fetch_coaster_details(ids)
    operating = get_operating_coasters(details)
    if not operating:
        return False, f"No operating coasters found for park: {park_name}"
    ok, msg = append_coasters_to_excel(operating)
    return ok, msg


def update_coaster_order(new_order):
    df = pd.read_excel(EXCEL_FILE)
    df['rank'] = df['id'].apply(lambda x: new_order.index(x))
    df = df.sort_values('rank')
    df.to_excel(EXCEL_FILE, index=False)


def load_coasters_for_display():
    df = pd.read_excel(EXCEL_FILE)
    df = df.sort_values('rank')
    return df.to_dict(orient='records')
