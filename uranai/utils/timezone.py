"""
Timezone utilities for astrology calculations
"""
from typing import Optional
from datetime import datetime
from functools import lru_cache

try:
    import pytz
    from pytz import timezone as pytz_timezone
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False

try:
    from timezonefinder import TimezoneFinder
    HAS_TZF = True
    _tf = TimezoneFinder()
except ImportError:
    HAS_TZF = False
    _tf = None


# 主要都市のタイムゾーンマッピング（フォールバック用）
CITY_TIMEZONES = {
    "tokyo": "Asia/Tokyo",
    "osaka": "Asia/Tokyo",
    "kyoto": "Asia/Tokyo",
    "new york": "America/New_York",
    "los angeles": "America/Los_Angeles",
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "berlin": "Europe/Berlin",
    "sydney": "Australia/Sydney",
    "beijing": "Asia/Shanghai",
    "shanghai": "Asia/Shanghai",
    "seoul": "Asia/Seoul",
    "singapore": "Asia/Singapore",
}


@lru_cache(maxsize=1000)
def get_timezone(lat: float, lng: float) -> str:
    """
    緯度・経度からタイムゾーン名を取得
    
    Args:
        lat: 緯度
        lng: 経度
    
    Returns:
        str: タイムゾーン名（例: "Asia/Tokyo"）
    """
    if HAS_TZF and _tf is not None:
        tz = _tf.timezone_at(lat=lat, lng=lng)
        if tz:
            return tz
    
    # フォールバック: 経度から大まかなタイムゾーンを推定
    if 135 <= lng <= 145:
        return "Asia/Tokyo"
    elif 120 <= lng < 135:
        return "Asia/Shanghai"
    elif -5 <= lng <= 5:
        return "Europe/London"
    elif -80 <= lng <= -70:
        return "America/New_York"
    elif -125 <= lng <= -115:
        return "America/Los_Angeles"
    else:
        return "UTC"


def get_timezone_from_city(city: str) -> Optional[str]:
    """
    都市名からタイムゾーンを取得
    
    Args:
        city: 都市名
    
    Returns:
        Optional[str]: タイムゾーン名、見つからない場合はNone
    """
    city_lower = city.lower().split(",")[0].strip()
    return CITY_TIMEZONES.get(city_lower)


def get_utc_offset(timezone_str: str, dt: Optional[datetime] = None) -> float:
    """
    タイムゾーンのUTCオフセット（時間単位）を取得
    
    Args:
        timezone_str: タイムゾーン名
        dt: 日時（デフォルトは現在）
    
    Returns:
        float: UTCオフセット（時間）
    """
    if not HAS_PYTZ:
        # 簡易的なオフセット計算
        offsets = {
            "Asia/Tokyo": 9.0,
            "Asia/Shanghai": 8.0,
            "Europe/London": 0.0,
            "America/New_York": -5.0,
            "America/Los_Angeles": -8.0,
            "UTC": 0.0,
        }
        return offsets.get(timezone_str, 0.0)
    
    if dt is None:
        dt = datetime.now()
    
    tz = pytz_timezone(timezone_str)
    offset = tz.utcoffset(dt)
    if offset:
        return offset.total_seconds() / 3600
    return 0.0
