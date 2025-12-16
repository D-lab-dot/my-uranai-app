"""
Geocoding utilities for converting city names to coordinates
"""
from typing import Optional, Tuple
from functools import lru_cache

try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
    HAS_GEOPY = True
except ImportError:
    HAS_GEOPY = False


@lru_cache(maxsize=1000)
def get_coordinates(city: str) -> Tuple[float, float]:
    """
    都市名から緯度・経度を取得
    
    Args:
        city: 都市名（例: "Tokyo, Japan"）
    
    Returns:
        Tuple[float, float]: (緯度, 経度)
    
    Raises:
        ValueError: 都市が見つからない場合
    """
    if not HAS_GEOPY:
        # Fallback for common cities
        default_cities = {
            "tokyo": (35.6762, 139.6503),
            "tokyo, japan": (35.6762, 139.6503),
            "osaka": (34.6937, 135.5023),
            "osaka, japan": (34.6937, 135.5023),
            "new york": (40.7128, -74.0060),
            "new york, usa": (40.7128, -74.0060),
            "london": (51.5074, -0.1278),
            "london, uk": (51.5074, -0.1278),
            "paris": (48.8566, 2.3522),
            "paris, france": (48.8566, 2.3522),
        }
        city_lower = city.lower().strip()
        if city_lower in default_cities:
            return default_cities[city_lower]
        raise ValueError(f"geopyがインストールされていません。pip install geopy を実行するか、緯度経度を直接指定してください。")
    
    geolocator = Nominatim(user_agent="uranai_astrology_app")
    
    try:
        location = geolocator.geocode(city, timeout=10)
        if location is None:
            raise ValueError(f"都市 '{city}' が見つかりませんでした")
        return (location.latitude, location.longitude)
    except GeocoderTimedOut:
        raise ValueError(f"ジオコーディングがタイムアウトしました: {city}")
    except GeocoderServiceError as e:
        raise ValueError(f"ジオコーディングエラー: {e}")


def get_coordinates_safe(city: str, default_lat: float = 35.6762, default_lng: float = 139.6503) -> Tuple[float, float]:
    """
    都市名から座標を取得（エラー時はデフォルト値を返す）
    
    Args:
        city: 都市名
        default_lat: デフォルト緯度（東京）
        default_lng: デフォルト経度（東京）
    
    Returns:
        Tuple[float, float]: (緯度, 経度)
    """
    try:
        return get_coordinates(city)
    except ValueError:
        return (default_lat, default_lng)
