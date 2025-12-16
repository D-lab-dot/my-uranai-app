"""
Secondary Progressions calculation module
セカンダリープログレッション計算
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from kerykeion import AstrologicalSubject

from uranai.core.chart import BirthChart, PlanetPosition, SIGN_JP, PLANET_JP


class SecondaryProgressions:
    """
    セカンダリープログレッションクラス
    
    「1日＝1年」の法則に基づくプログレッション計算
    """
    
    def __init__(
        self,
        natal_chart: BirthChart,
        target_year: Optional[int] = None,
        target_date: Optional[str] = None
    ):
        """
        セカンダリープログレッションを計算
        
        Args:
            natal_chart: 対象のネイタルチャート
            target_year: 対象年（デフォルトは今年）
            target_date: 対象日時（"YYYY-MM-DD"形式）
        """
        self.natal_chart = natal_chart
        
        # 対象日時の設定
        if target_date:
            parts = target_date.split("-")
            self.target_year = int(parts[0])
            self.target_month = int(parts[1])
            self.target_day = int(parts[2])
        elif target_year:
            self.target_year = target_year
            self.target_month = natal_chart.month
            self.target_day = natal_chart.day
        else:
            now = datetime.now()
            self.target_year = now.year
            self.target_month = now.month
            self.target_day = now.day
        
        # 出生日からの経過年数を計算
        birth_date = datetime(natal_chart.year, natal_chart.month, natal_chart.day)
        target_date_obj = datetime(self.target_year, self.target_month, self.target_day)
        self.years_elapsed = (target_date_obj - birth_date).days / 365.25
        
        # プログレッション日を計算（出生日 + 経過年数日）
        progressed_date = birth_date + timedelta(days=self.years_elapsed)
        
        # プログレッションチャートを計算
        self._subject = AstrologicalSubject(
            name=f"{natal_chart.name} Progressions",
            year=progressed_date.year,
            month=progressed_date.month,
            day=progressed_date.day,
            hour=natal_chart.hour,
            minute=natal_chart.minute,
            lat=natal_chart.lat,
            lng=natal_chart.lng,
            tz_str=natal_chart.tz_str
        )
        
        # Kerykeion v5: model() を呼び出す
        self._model = self._subject.model()
        
        self.progressed_year = progressed_date.year
        self.progressed_month = progressed_date.month
        self.progressed_day = progressed_date.day
    
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
    def progressed_sun(self) -> PlanetPosition:
        """プログレスの太陽"""
        return self._planet_to_position(self._model.sun)
    
    @property
    def progressed_moon(self) -> PlanetPosition:
        """プログレスの月"""
        return self._planet_to_position(self._model.moon)
    
    @property
    def progressed_mercury(self) -> PlanetPosition:
        """プログレスの水星"""
        return self._planet_to_position(self._model.mercury)
    
    @property
    def progressed_venus(self) -> PlanetPosition:
        """プログレスの金星"""
        return self._planet_to_position(self._model.venus)
    
    @property
    def progressed_mars(self) -> PlanetPosition:
        """プログレスの火星"""
        return self._planet_to_position(self._model.mars)
    
    @property
    def planets(self) -> List[PlanetPosition]:
        """プログレス惑星のリスト"""
        planets = []
        for attr in ['sun', 'moon', 'mercury', 'venus', 'mars']:
            planet = getattr(self._model, attr)
            planets.append(self._planet_to_position(planet))
        return planets
    
    def summary(self) -> str:
        """プログレッションのサマリー"""
        lines = [
            f"=== {self.natal_chart.name} のセカンダリープログレッション ===",
            f"対象年: {self.target_year}年",
            f"経過年数: {self.years_elapsed:.2f}年",
            f"プログレッション日: {self.progressed_year}年{self.progressed_month}月{self.progressed_day}日",
            "",
            "【プログレス惑星】",
            f"P.太陽: {self.progressed_sun.sign_jp} {self.progressed_sun.degree:.2f}°",
            f"P.月: {self.progressed_moon.sign_jp} {self.progressed_moon.degree:.2f}°",
            f"P.水星: {self.progressed_mercury.sign_jp} {self.progressed_mercury.degree:.2f}°",
            f"P.金星: {self.progressed_venus.sign_jp} {self.progressed_venus.degree:.2f}°",
            f"P.火星: {self.progressed_mars.sign_jp} {self.progressed_mars.degree:.2f}°",
        ]
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """プログレッションデータを辞書形式で出力"""
        return {
            "natal_name": self.natal_chart.name,
            "target_year": self.target_year,
            "years_elapsed": self.years_elapsed,
            "progressed_date": f"{self.progressed_year}-{self.progressed_month:02d}-{self.progressed_day:02d}",
            "planets": [
                {
                    "name": p.name,
                    "name_jp": PLANET_JP.get(p.name, p.name),
                    "sign": p.sign,
                    "sign_jp": p.sign_jp,
                    "degree": p.degree,
                    "retrograde": p.retrograde
                }
                for p in self.planets
            ]
        }
