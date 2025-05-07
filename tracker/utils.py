# utils.py
import requests
from django.conf import settings

def geocode_city_state(city, state):
    address = f"{city}, {state}"
    api_key = settings.GOOGLE_MAPS_API_KEY
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key=AIzaSyAtjZE5pRf_kM-P3l2mDTItjg9KgA7RgDE"

    response = requests.get(url)
    data = response.json()

    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    return None, None
