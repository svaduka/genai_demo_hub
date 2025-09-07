import requests
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load the Google Maps API key securely
maps_api_key = "AIzaSyBSknPFmT6qM9Gb2FHgSnOTEJT_dbvVSbg"  # Replace with secure method like environment variable

def geocode_address(address):
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": maps_api_key}
        response = requests.get(url, params=params).json()
        if response['status'] == 'OK':
            location = response['results'][0]['geometry']['location']
            return location['lat'], location['lng'], 'OK'
        else:
            return None, None, response['status']
    except Exception as e:
        return None, None, str(e)

TYPE_PRIORITY = {
    "pharmacy": 10,
    "grocery_or_supermarket": 8,
    "supermarket": 7,
    "convenience_store": 6,
    "store": 5,
    "health": 4,
    "doctor": 3,
    "point_of_interest": 1,
    "establishment": 0
}

def get_nearby_place(lat, lng, address):
    try:
        # Step 1: Find place_id using findplacefromtext
        find_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        find_params = {
            "input": address,
            "inputtype": "textquery",
            "fields": "place_id",
            "key": maps_api_key
        }
        find_resp = requests.get(find_url, params=find_params).json()
        if find_resp["status"] != "OK" or not find_resp.get("candidates"):
            return None, None, "Not Found", None
        place_id = find_resp["candidates"][0]["place_id"]

        # Step 2: Fetch place details
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        details_params = {
            "place_id": place_id,
            "fields": "name,types,business_status",
            "key": maps_api_key
        }
        details_resp = requests.get(details_url, params=details_params).json()
        if details_resp["status"] != "OK":
            return None, None, details_resp["status"], None

        result = details_resp.get("result", {})
        name = result.get("name")
        types = result.get("types", [])
        business_status = result.get("business_status")
        return name, ",".join(types), "OK", business_status
    except Exception as e:
        return None, None, str(e), None

def map_place_types(types):
    if not types:
        return "Other"
    best_type = None
    best_score = -1
    for t in types:
        score = TYPE_PRIORITY.get(t, 0)
        if score > best_score:
            best_score = score
            best_type = t
    return best_type or "Other"

def enrich_row(row):
    address = f"{row.get('Account Source Name', '') or ''}, {row.get('Store Address Line 1', '') or ''}, {row.get('Store Address Line 2', '') or ''}, {row.get('Store City Name', '') or ''}, {row.get('Store Postal Code Number', '') or ''}, {row.get('Store Territory Short Name', '') or ''}, {row.get('Store Country Short Name', '') or ''}"
    lat, lng, geo_status = geocode_address(address)
    place_name, types_str, place_status, business_status = get_nearby_place(lat, lng, address) if lat and lng else (None, None, 'Skipped', None)
    category = map_place_types(types_str.split(",") if types_str else [])
    confidence = 1.0 if category == "pharmacy" else 0.85 if category == "grocery_or_supermarket" else 0.75 if category == "store" else 0.6

    # Include all original columns
    result = row.to_dict()
    result.update({
        "place_name": place_name,
        "latitude": lat,
        "longitude": lng,
        "category": category,
        "types": types_str,
        "confidence": confidence,
        "geocode_status": geo_status,
        "place_status": place_status,
        "business_status": business_status
    })
    return result

# Load input data
import pandas as pd

input_path = "/Users/Sainagaraju_Vaduka/Documents/SAI_LOCAL_WS/GitHubWS/personal/genai_demo_hub/address_classifier/FY25_Customer_Accounts_Shared.txt"

try:
    df = pd.read_csv(input_path, delimiter="\t", encoding="utf-8")
except UnicodeDecodeError:
    df = pd.read_csv(input_path, delimiter="\t", encoding="latin1")

df = df.fillna("")
print(df.head())

# Process in parallel
results = []
with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(enrich_row, row) for _, row in df.iterrows()]
    for future in as_completed(futures):
        results.append(future.result())

# Create final dataframe
final_df = pd.DataFrame(results)

# Display sample
print(final_df.head())


# Save result
final_df.to_csv("enriched_addresses.csv", index=False)