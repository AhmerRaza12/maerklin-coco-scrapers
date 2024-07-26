import requests
import pandas as pd
import os
import re
import time
file_path = 'maerklin_shops_data.xlsx'

def shop_id_exists(shop_id, df):
    return shop_id in df['Shop ID'].values

def append_shop_details(file_path, data):
    if os.path.isfile(file_path):
        df = pd.read_excel(file_path)
    else:
        df = pd.DataFrame(columns=['Shop ID', 'Shop Name', 'Street Address', 'Street Number', 'City', 'Country', 'Phone Number', 'Email', 'Website', 'Postal Code'])

    df_new_row = pd.DataFrame([data])
    df = pd.concat([df, df_new_row], ignore_index=True)

    df.to_excel(file_path, index=False)

def get_street_name_and_number(street):
    match = re.match(r'([^\d]+)\s?(\d.*)?', street)
    if match:
        street_name = match.group(1).strip()
        street_number = match.group(2).strip() if match.group(2) else ''
        return street_name, street_number
    return street, ''

def get_shop_details(lat, lon, lat_delta, lon_delta):
    url = f"https://www.maerklin.de/de/service/haendlersuche/ajaxCall.json?tx_torrmapi_ajax%5Bcontroller%5D=Ajax&tx_torrmapi_ajax%5Baction%5D=retailersearch&tx_torrmapi_ajax%5Bcountry%5D=&tx_torrmapi_ajax%5Blatitude%5D={lat}&tx_torrmapi_ajax%5Blongitude%5D={lon}&tx_torrmapi_ajax%5BlatitudeDelta%5D={lat_delta}&tx_torrmapi_ajax%5BlongitudeDelta%5D={lon_delta}"
    response = requests.get(url)
    data = response.json()

    if 'matches' in data and 'match' in data['matches']:
        matches = data['matches']['match']
        if os.path.isfile(file_path):
            existing_df = pd.read_excel(file_path)
        else:
            existing_df = pd.DataFrame(columns=['Shop ID'])

        for match in matches:
            shop_id = match.get('id', '')
            company = match.get('company', '')
            street = match.get('street', '')
            street_name, street_number = get_street_name_and_number(street)
            city = match.get('city', '')
            country = match.get('country', '')
            phone = match.get('phone', '') if 'phone' in match else ''
            email = match.get('email', '') if 'email' in match else ''
            website = f"https://{match.get('web', '')}" if 'web' in match else ''
            postal_code = match.get('zip', '')

            shop_data = {
                'Shop ID': shop_id,
                'Shop Name': company,
                'Street Address': street_name,
                'Street Number': street_number,
                'City': city,
                'Country': country,
                'Phone Number': phone,
                'Email': email,
                'Website': website,
                'Postal Code': postal_code
            }

            if not shop_id_exists(shop_id, existing_df):
                append_shop_details(file_path, shop_data)
                print(shop_data)

latitude = 44.28108635600787
longitude = 3.5043847311191367
latitude_delta = 1.9663227699164594
longitude_delta = 3.7188720703125


for lat_shift in range(-40, 41):  
    for lon_shift in range(-40, 41):  
        lat = latitude + (lat_shift * latitude_delta)
        lon = longitude + (lon_shift * longitude_delta)
        get_shop_details(lat, lon, latitude_delta, longitude_delta)
        time.sleep(1)
