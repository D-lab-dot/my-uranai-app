"""
Transit Chart calculation module
トランジット（経過）計算
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass

from kerykeion import AstrologicalSubject

from uranai.core.chart import BirthChart, PlanetPosition, SIGN_JP, ASPECT_JP, PLANET_JP


@dataclass
class TransitAspect:
    """トランジットアスペクトデータ"""
    transit_planet: str      # トランジット惑星
    natal_planet: str        # ネイタル惑星
    aspect_type: str         # アスペクトタイプ
    aspect_name_jp: str      # 日本語名
    orb: float               # オーブ
    
    def __str__(self) -> str:
        return f"T.{self.transit_planet} {self.aspect_type} N.{self.natal_planet} (orb: {self.orb:.2f}°)"


class TransitChart:
    """
    トランジットチャートクラス
    
    指定日時のトランジット惑星とネイタルチャートとの関係を計算
    """
    
    def __init__(
        self,
        natal_chart: BirthChart,
        target_date: Optional[str] = None,
        target_datetime: Optional[datetime] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        hour: int = 12,
        minute: int = 0
    ):
        """
        トランジットチャートを作成
        
        Args:
            natal_chart: 対象のネイタルチャート
            target_date: 対象日時（"YYYY-MM-DD"形式）
            target_datetime: 対象日時（datetimeオブジェクト）
            year, month, day: 対象日時（個別指定）
            hour, minute: 対象時刻
        """
        self.natal_chart = natal_chart
        
        # 日時の解析
        if target_datetime:
            self.year = target_datetime.year
            self.month = target_datetime.month
            self.day = target_datetime.day
            self.hour = target_datetime.hour
            self.minute = target_datetime.minute
        elif target_date:
            parts = target_date.split("-")
            self.year = int(parts[0])
            self.month = int(parts[1])
            self.day = int(parts[2])
            self.hour = hour
            self.minute = minute
        elif year and month and day:
            self.year = year
            self.month = month
            self.day = day
            self.hour = hour
            self.minute = minute
        else:
            # デフォルト: 現在
            now = datetime.now()
            self.year = now.year
            self.month = now.month
            self.day = now.day
            self.hour = now.hour
            self.minute = now.minute
        
        # トランジットチャートを計算（同じ場所で）
        self._transit_subject = AstrologicalSubject(
            name=f"Transit {self.year}-{self.month:02d}-{self.day:02d}",
            year=self.year,
            month=self.month,
            day=self.day,
            hour=self.hour,
            minute=self.minute,
            lat=natal_chart.lat,
            lng=natal_chart.lng,
            tz_str=natal_chart.tz_str
        )
        
        # Kerykeion v5: model() を呼び出す
        self._transit_model = self._transit_subject.model()
        self._natal_model = natal_chart.get_model()
    
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
    def transit_planets(self) -> List[PlanetPosition]:
        """トランジット惑星のリスト"""
        planets = []
        for attr in ['sun', 'moon', 'mercury', 'venus', 'mars', 
                     'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']:
            planet = getattr(self._transit_model, attr)
            planets.append(self._planet_to_position(planet))
        return planets
    
    @property
    def aspects(self) -> List[TransitAspect]:
        """
        トランジット惑星とネイタル惑星間のアスペクト
        """
        aspects = []
        
        # アスペクトの角度とオーブ設定
        aspect_angles = {
            "conjunction": (0, 8),
            "opposition": (180, 8),
            "trine": (120, 6),
            "square": (90, 6),
            "sextile": (60, 4),
        }
        
        planet_attrs = ['sun', 'moon', 'mercury', 'venus', 'mars', 
                        'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
        
        for t_attr in planet_attrs:
            t_planet = getattr(self._transit_model, t_attr)
            t_pos = getattr(t_planet, 'abs_pos', 0.0)
            
            for n_attr in planet_attrs:
                n_planet = getattr(self._natal_model, n_attr)
                n_pos = getattr(n_planet, 'abs_pos', 0.0)
                
                # 角度差を計算
                diff = abs(t_pos - n_pos)
                if diff > 180:
                    diff = 360 - diff
                
                # 各アスペクトをチェック
                for aspect_name, (angle, max_orb) in aspect_angles.items():
                    orb = abs(diff - angle)
                    if orb <= max_orb:
                        aspects.append(TransitAspect(
                            transit_planet=t_planet.name,
                            natal_planet=n_planet.name,
                            aspect_type=aspect_name,
                            aspect_name_jp=ASPECT_JP.get(aspect_name, aspect_name),
                            orb=orb
                        ))
        
        # オーブの小さい順にソート
        aspects.sort(key=lambda x: x.orb)
        return aspects
    
    def get_major_transits(self) -> List[TransitAspect]:
        """
        重要なトランジットのみを取得
        （外惑星のアスペクトを優先）
        """
        major_planets = {'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto'}
        return [a for a in self.aspects if a.transit_planet in major_planets]
    
    def summary(self) -> str:
        """トランジットのサマリーを日本語で出力"""
        lines = [
            f"=== {self.natal_chart.name} へのトランジット ===",
            f"日時: {self.year}年{self.month}月{self.day}日 {self.hour}:{self.minute:02d}",
            "",
            "【現在の惑星配置】"
        ]
        
        for planet in self.transit_planets:
            retro = " (R)" if planet.retrograde else ""
            lines.append(f"{PLANET_JP.get(planet.name, planet.name)}: {planet.sign_jp} {planet.degree:.2f}°{retro}")
        
        lines.append("")
        lines.append("【重要なトランジット】")
        
        major = self.get_major_transits()[:10]
        for asp in major:
            lines.append(f"T.{PLANET_JP.get(asp.transit_planet, asp.transit_planet)} "
                        f"{asp.aspect_name_jp} "
                        f"N.{PLANET_JP.get(asp.natal_planet, asp.natal_planet)} "
                        f"(orb: {asp.orb:.2f}°)")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """トランジットデータを辞書形式で出力"""
        return {
            "natal_name": self.natal_chart.name,
            "transit_date": f"{self.year}-{self.month:02d}-{self.day:02d}",
            "transit_time": f"{self.hour:02d}:{self.minute:02d}",
            "transit_planets": [
                {
                    "name": p.name,
                    "name_jp": PLANET_JP.get(p.name, p.name),
                    "sign": p.sign,
                    "sign_jp": p.sign_jp,
                    "degree": p.degree,
                    "retrograde": p.retrograde
                }
                for p in self.transit_planets
            ],
            "aspects": [
                {
                    "transit_planet": a.transit_planet,
                    "natal_planet": a.natal_planet,
                    "type": a.aspect_type,
                    "type_jp": a.aspect_name_jp,
                    "orb": a.orb
                }
                for a in self.aspects
            ]
        }
