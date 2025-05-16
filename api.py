from flask import request
import requests

# Function to get the user's country based on IP
def get_user_country():
    try:
        # Get the user's IP address
        user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if user_ip == '127.0.0.1':  # Fallback for local testing
            user_ip = '27.110.152.250'  # dns of makati city

        # Use a geolocation API to get the country
        response = requests.get(f"http://ip-api.com/json/{user_ip}")
        if response.status_code == 200:
            data = response.json()
            return data.get('country', 'Unknown')  # Return the country name
        else:
            print(f"Error: Received status code {response.status_code}")
            return 'Unknown'
    except requests.exceptions.RequestException as e:
        print("Request Exception:", e)
        return 'Unknown'


# Fetch all provinces
def fetch_provinces():
    try:
        response = requests.get("https://psgc.gitlab.io/api/provinces/")
        if response.status_code == 200:
            provinces_data = response.json()
            # Each province has 'code' and 'name'
            return [{"code": p["code"], "name": p["name"]} for p in provinces_data]
        else:
            print(f"Error fetching provinces: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print("Request Exception:", e)
        return []

# Fetch cities/municipalities for a given province code
def fetch_cities(province_code):
    try:
        response = requests.get(f"https://psgc.gitlab.io/api/provinces/{province_code}/cities-municipalities/")
        if response.status_code == 200:
            cities_data = response.json()
            return [{"code": c["code"], "name": c["name"]} for c in cities_data]
        else:
            print(f"Error fetching cities: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print("Request Exception:", e)
        return []

# Fetch barangays for a given city/municipality code
def fetch_barangays(city_code):
    try:
        response = requests.get(f"https://psgc.gitlab.io/api/cities-municipalities/{city_code}/barangays/")
        if response.status_code == 200:
            barangays_data = response.json()
            return [{"code": b["code"], "name": b["name"]} for b in barangays_data]
        else:
            print(f"Error fetching barangays: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print("Request Exception:", e)
        return []

# Fetch postal code for a given city/municipality code (if available)
def fetch_postal_code(city, country_code="PH", username="jamesonnn"):
    try:
        url = f"http://api.geonames.org/postalCodeSearchJSON?placename={city}&country={country_code}&username={username}"
        print("GeoNames URL:", url)
        response = requests.get(url)
        print("GeoNames Response:", response.text)
        if response.status_code == 200:
            data = response.json()
            if data.get("postalCodes"):
                city_lower = city.lower().replace("city of ", "").replace("city", "").strip()
                # Try to find a placeName that matches or contains the city name
                for place in data["postalCodes"]:
                    place_name = place.get("placeName", "").lower()
                    if city_lower in place_name or place_name in city_lower:
                        return place.get("postalCode", "Unknown")
                # Fallback: return the first postal code
                return data["postalCodes"][0].get("postalCode", "Unknown")
            else:
                return "Unknown"
        else:
            print(f"Error fetching postal code: {response.status_code}")
            return "Unknown"
    except requests.exceptions.RequestException as e:
        print("Request Exception:", e)
        return "Unknown"