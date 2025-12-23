
import requests
import json
import os
from .utils import format_coordinates, parse_coordinates, extract_route_data_from_json
from django.conf import settings
from django.core.cache import cache
apikey = '34ef38d4d8fc4d5ba29da472883852f1'
yapikey = os.getenv('YANDEX_API_KEY','')




class Routing:
    
    @staticmethod
    def Geocode(address, isNizhniy=True):
        """
        Преобразует адрес в координаты, используя кэширование.
        """
        if isNizhniy:
              address = address + 'Нижний Новгород'
        api_key = yapikey
        cache_key = f'yandex_geocode:{address}'
        result = cache.get(cache_key)
        if result is not None:
            return result
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
              
            'apikey': api_key,
            'lang': 'ru_RU',
            'geocode': address,
            'format': 'json'
        }

        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()  # Проверка на ошибки HTTP
            data = response.json()

            try:
                pos = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
                # pos возвращается в формате "долгота широта"
                lon, lat = pos.split()
                result = format_coordinates(lat,lon,10)
            except (KeyError, IndexError):
                result = 'Адрес не найден или ответ имеет неожиданную структуру.'

        except requests.exceptions.RequestException as e:
            result = f'Ошибка сети или API: {str(e)}'
        except json.JSONDecodeError:
            result = 'Не удалось разобрать ответ от сервера.'

        cache.set(cache_key, result, timeout=86400)
        return result

    @staticmethod
    def GetRoute(coords_start, coords_end): 
        """ 
         Получает маршрут между двумя точками через OpenRouteService
    
          Args:
        profile: тип маршрута (driving-car, foot-walking, cycling-regular и т.д.)
        api_url: URL локального ORS сервера
    
         Returns:
        dict: данные маршрута или None в случае ошибки
        """
        api_url = 'http://localhost:8080/'
        profile = 'driving-car'

        cache_key = f'ors_route:{coords_start}:{coords_end}:{profile}'
        result = cache.get(cache_key)
        if result is not None:
            return result

        start_location_lat, start_location_lon = parse_coordinates(coords_start)
        end_location_lat, end_location_lon = parse_coordinates(coords_end)
        
        start_location = (start_location_lon, start_location_lat)
        end_location = (end_location_lon, end_location_lat)

        url = f"{api_url}/ors/v2/directions/{profile}/geojson"
            
        payload = {
                "coordinates": [start_location, end_location],
                "profile": "driving-car",
                "language": "ru",  
                "units": "m",  
                "format": "json",
            }
            

        headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/geo+json'
            }
            
        try:
                response = requests.post(
                    url,
                    data=json.dumps(payload),
                    headers=headers,
                    timeout=5  
                )
        #raise ValueError(f'{}')       
        except requests.exceptions.ConnectionError:
                raise ConnectionError(f"Не удалось подключиться к ORS серверу по адресу {api_url}")
                return None
        except requests.exceptions.Timeout:
                raise TimeoutError("Таймаут при запросе к ORS")
                return None
        except requests.exceptions.RequestException as e:
                raise ValueError(f"Ошибка запроса: {e}")
                return None
                return None    
        if response.status_code == 200:    
                    cache.set(cache_key, result, timeout=999999)         
                    return extract_route_data_from_json(response.json())
        else:
                    print(f"Ошибка ORS API: {response.status_code}")
                    raise SystemError(f"Ошибка ORS API: {response.status_code}, || Ответ: {response.text}")
                    return None              


    @staticmethod
    def YandexGetRoute(start_location, end_location, mode='driving'): 
        """
        Строит маршрут между двумя координатами, используя кэширование.
        mode: 'driving' (авто), 'transit' (общественный транспорт), 'walking' (пешком)[citation:4][citation:10].
        """
        api_key = yapikey
        # Создаем ключ для кэша на основе всех параметров
        cache_key = f'yandex_route:{start_location}:{end_location}:{mode}'
        start_location_lat, start_location_lon = parse_coordinates(start_location)
        end_location_lat, end_location_lon = parse_coordinates(end_location)
        result = cache.get(cache_key)
        if result is not None:
            return result

        url = "https://api.routing.yandex.net/v2/route"
        params = {
            'apikey': api_key,
            'waypoints': f"{start_location_lon},{start_location_lat}|{end_location_lon},{end_location_lat}",
            'mode': mode, 
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            route = data['routes'][0]
            result = route
        except (requests.exceptions.RequestException, KeyError, IndexError) as e:
            result = {'error': f'Ошибка при построении маршрута: {str(e)}'}

        timeout = 5
        cache.set(cache_key, result, timeout=timeout)
        return result

