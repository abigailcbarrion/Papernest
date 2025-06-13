from flask import request
import requests
import time

# Function to get the user's country based on IP
def get_user_country():
    try:
        # Get the user's IP address
        user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if user_ip == '127.0.0.1':  # Fallback for local testing
            user_ip = '27.110.152.250'  # dns of makati city

        # Use a geolocation API to get the country
        response = requests.get(f"http://ip-api.com/json/{user_ip}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('country', 'Philippines')  # Default to Philippines
        else:
            print(f"Error: Received status code {response.status_code}")
            return 'Philippines'
    except requests.exceptions.RequestException as e:
        print("Request Exception:", e)
        return 'Philippines'

# Fetch all provinces
def fetch_provinces():
    try:
        response = requests.get("https://psgc.gitlab.io/api/provinces/", timeout=10)
        if response.status_code == 200:
            provinces_data = response.json()
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
        response = requests.get(f"https://psgc.gitlab.io/api/provinces/{province_code}/cities-municipalities/", timeout=10)
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
        response = requests.get(f"https://psgc.gitlab.io/api/cities-municipalities/{city_code}/barangays/", timeout=10)
        if response.status_code == 200:
            barangays_data = response.json()
            return [{"code": b["code"], "name": b["name"]} for b in barangays_data]
        else:
            print(f"Error fetching barangays: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print("Request Exception:", e)
        return []

def generate_default_postal_code(city_name):
    """Generate a reasonable default postal code based on city name"""
    if not city_name:
        return "1000"
    
    # Simple hash-based approach to generate consistent postal codes
    city_clean = city_name.lower().replace("city of ", "").replace(" city", "").strip()
    hash_val = hash(city_clean) % 9000 + 1000  # Generate between 1000-9999
    return str(hash_val)

def fetch_postal_code_with_retry(city, country_code="PH", username="jamesonnn", max_retries=2):
    """Fetch postal code with retry mechanism"""
    for attempt in range(max_retries):
        try:
            url = f"http://api.geonames.org/postalCodeSearchJSON?placename={city}&country={country_code}&username={username}"
            response = requests.get(url, timeout=5)  # Reduced timeout
            
            if response.status_code == 200:
                data = response.json()
                if data.get("postalCodes") and len(data["postalCodes"]) > 0:
                    postal_code = data["postalCodes"][0].get("postalCode", "")
                    if postal_code:
                        return postal_code
                
                print(f"No postal code found for {city}, {country_code}")
                return generate_default_postal_code(city)
            else:
                print(f"GeoNames API error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"Timeout on attempt {attempt + 1} for {city}")
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait before retry
                continue
                
        except requests.exceptions.RequestException as e:
            print(f"Request error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
                
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
    
    # All attempts failed, return default
    print(f"All attempts failed for {city}, using default postal code")
    return generate_default_postal_code(city)

# Main postal code fetch function
def fetch_postal_code(city, country_code="PH", username="jamesonnn"):
    """Fetch postal code with fallback to generated code"""
    try:
        return fetch_postal_code_with_retry(city, country_code, username)
    except Exception as e:
        print(f"Critical error in postal code fetch: {e}")
        return generate_default_postal_code(city)