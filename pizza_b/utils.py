# utils/coordinates.py
def parse_coordinates(coord_string):
    """
    Парсит строку координат "широта,долгота"
    Возвращает (lat, lon) или (None, None) при ошибке
    """
    if not coord_string:
        return None, None
    
    try:
        lat_str, lon_str = coord_string.split(',')
        return float(lat_str.strip()), float(lon_str.strip())
    except (ValueError, IndexError):
        return None, None

def format_coordinates(lat, lon, decimals=19):
    """
    Форматирует координаты в строку
    """
    try:
        # Преобразуем в числа, если это строки
        lat_num = float(lat)
        lon_num = float(lon)
        return f"{lat_num:.{decimals}f},{lon_num:.{decimals}f}"
    except (ValueError, TypeError):
        # Возвращаем пустую строку при ошибке
        return ""
  
def extract_route_data_from_json(api_response):
    """ 
    Формат ответа:
    {
        "features": [{
            "properties": {
                "summary": {
                    "distance": 19631.1,
                    "duration": 1885
                }
            },
            "geometry": {
                "coordinates": [[lon1, lat1], [lon2, lat2], ...]
            }
        }]
    }
    """
    if not api_response or 'features' not in api_response:
        return api_response
    
    try:
        # Берём первый элемент из features
        feature = api_response['features'][0]
        
        # Извлекаем расстояние и время
        summary = feature['properties']['summary']
        distance = summary.get('distance')
        duration = summary.get('duration')
        
        # Извлекаем координаты
        coordinates = feature['geometry']['coordinates']
        formatted_coords = [
            [coord[1],coord[0]] for coord in coordinates
        ]
        
        return {
            'distance': distance,        # расстояние в метрах
            'duration': duration,        # время в секундах
            'duration_minutes': duration // 60 if duration else 0,
            'coordinates': formatted_coords,  # массив строк "широта,долгота"
            'raw_coordinates': coordinates    # исходный массив [lon, lat]
        }
        
    except (KeyError, IndexError, TypeError) as e:
        return {'error': f'Ошибка при разборе ответа: {str(e)}'}
