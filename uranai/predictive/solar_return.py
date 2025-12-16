"""
Solar Return Chart calculation module
ソーラーリターン（太陽回帰）チャート計算
"""
from typing import Optional, Dict, Any, List
from datetime import datetime

from kerykeion import AstrologicalSubject

from uranai.core.chart import BirthChart, PlanetPosition, SIGN_JP, PLANET_JP


class SolarReturnChart:
    """
    ソーラーリターンチャートクラス
    
    指定年の太陽回帰（誕生日）チャートを計算
    """
    
    def __init__(
        self,
        natal_chart: BirthChart,
        return_year: Optional[int] = None,
        location_city: Optional[str] = None,
        location_lat: Optional[float] = None,
        location_lng: Optional[float] = None
    ):
        """
        ソーラーリターンチャートを作成
        
        Args:
            natal_chart: 対象のネイタルチャート
            return_year: ソーラーリターンの年（デフォルトは今年）
            location_city: ソーラーリターン時の場所（都市名）
            location_lat: ソーラーリターン時の緯度
            location_lng: ソーラーリターン時の経度
        """
        self.natal_chart = natal_chart
        
        # 年の設定
        if return_year is None:
            return_year = datetime.now().year
        self.return_year = return_year
        
        # 場所の設定（指定がなければ出生地を使用）
        if location_lat is not None and location_lng is not None:
            self.lat = location_lat
            self.lng = location_lng
            self.location_city = location_city
        elif location_city:
            from uranai.utils.geocoding import get_coordinates
            self.lat, self.lng = get_coordinates(location_city)
            self.location_city = location_city
        else:
            self.lat = natal_chart.lat
            self.lng = natal_chart.lng
            self.location_city = natal_chart.city
        
        # ネイタル太陽の正確な度数を取得
        natal_sun = natal_chart.sun
        self.natal_sun_position = natal_sun.absolute_degree
        
        # ソーラーリターンの日時を計算
        self._calculate_return_datetime()
        
        # ソーラーリターンチャートを計算
        from uranai.utils.timezone import get_timezone
        tz_str = get_timezone(self.lat, self.lng)
        
        self._subject = AstrologicalSubject(
            name=f"{natal_chart.name} Solar Return {self.return_year}",
            year=self.return_year,
            month=natal_chart.month,
            day=natal_chart.day,
            hour=natal_chart.hour,
            minute=natal_chart.minute,
            lat=self.lat,
            lng=self.lng,
            tz_str=tz_str
        )
        
        # Kerykeion v5: model() を呼び出す
        self._model = self._subject.model()
    
    def _calculate_return_datetime(self):
        """
        ソーラーリターンの正確な日時を計算
        （簡易実装: 出生日時を使用）
        """
        self.return_month = self.natal_chart.month
        self.return_day = self.natal_chart.day
        self.return_hour = self.natal_chart.hour
        self.return_minute = self.natal_chart.minute
    
    def _planet_to_position(self, planet) -> PlanetPosition:
        """惑星データをPlanetPositionに変換"""
        sign = getattr(planet, 'sign', 'Unknown')
        return PlanetPosition(
            name=planet.name,
            sign=sign,
            sign_jp=SIGN_JP.get(sign[:3] if sign else "Unk", str(sign)),
            degree=getattr(planet, 'position', 0.0),
            absolute_degree=getattr(planet, 'abs_pos', 0.0),
            house=getattr(planet, 'house', 'Unknown'),
            retrograde=getattr(planet, 'retrograde', False)
        )
    
    @property
    def planets(self) -> List[PlanetPosition]:
        """惑星位置のリスト"""
        planets = []
        for attr in ['sun', 'moon', 'mercury', 'venus', 'mars', 
                     'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']:
            planet = getattr(self._model, attr)
            planets.append(self._planet_to_position(planet))
        return planets
    
    @property
    def ascendant(self) -> Dict[str, Any]:
        """アセンダント"""
        asc = self._model.first_house
        sign = getattr(asc, 'sign', 'Unknown')
        return {
            "degree": getattr(asc, 'position', 0.0),
            "sign": sign,
            "sign_jp": SIGN_JP.get(str(sign)[:3], str(sign)),
            "absolute_degree": getattr(asc, 'abs_pos', 0.0)
        }
    
    @property
    def midheaven(self) -> Dict[str, Any]:
        """MC（天頂）"""
        mc = self._model.tenth_house
        sign = getattr(mc, 'sign', 'Unknown')
        return {
            "degree": getattr(mc, 'position', 0.0),
            "sign": sign,
            "sign_jp": SIGN_JP.get(str(sign)[:3], str(sign)),
            "absolute_degree": getattr(mc, 'abs_pos', 0.0)
        }
    
    def summary(self) -> str:
        """ソーラーリターンのサマリー"""
        lines = [
            f"=== {self.natal_chart.name} のソーラーリターン {self.return_year} ===",
            f"日時: {self.return_year}年{self.return_month}月{self.return_day}日",
            f"場所: {self.location_city or f'({self.lat:.4f}, {self.lng:.4f})'}",
            "",
            f"【ソーラーリターンのアセンダント】",
            f"ASC: {self.ascendant['sign_jp']} {self.ascendant['degree']:.2f}°",
            f"MC: {self.midheaven['sign_jp']} {self.midheaven['degree']:.2f}°",
            "",
            "【惑星配置】"
        ]
        
        for planet in self.planets:
            retro = " (R)" if planet.retrograde else ""
            lines.append(f"{PLANET_JP.get(planet.name, planet.name)}: "
                        f"{planet.sign_jp} {planet.degree:.2f}° (House {planet.house}){retro}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """ソーラーリターンデータを辞書形式で出力"""
        return {
            "natal_name": self.natal_chart.name,
            "return_year": self.return_year,
            "return_date": f"{self.return_year}-{self.return_month:02d}-{self.return_day:02d}",
            "location": {
                "city": self.location_city,
                "lat": self.lat,
                "lng": self.lng
            },
            "ascendant": self.ascendant,
            "midheaven": self.midheaven,
            "planets": [
                {
                    "name": p.name,
                    "name_jp": PLANET_JP.get(p.name, p.name),
                    "sign": p.sign,
                    "sign_jp": p.sign_jp,
                    "degree": p.degree,
                    "house": p.house,
                    "retrograde": p.retrograde
                }
                for p in self.planets
            ]
        }
    
    def save_svg(self, filepath: str) -> str:
        """SVGチャートを保存"""
        from kerykeion import KerykeionChartSVG
        import shutil
        import os
        
        chart = KerykeionChartSVG(self._subject)
        chart.makeSVG()
        
        default_path = os.path.join(
            os.path.expanduser("~"), 
            f"{self._subject.name.replace(' ', '_')}NatalChart.svg"
        )
        if os.path.exists(default_path) and default_path != filepath:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            shutil.move(default_path, filepath)
        
        return filepath
