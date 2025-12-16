"""
Birth Chart calculation module
出生図（ネイタルチャート）の計算と生成
"""
from typing import Optional, Dict, List, Any
from dataclasses import dataclass

from kerykeion import AstrologicalSubject

from uranai.utils.geocoding import get_coordinates
from uranai.utils.timezone import get_timezone


@dataclass
class PlanetPosition:
    """惑星位置データ"""
    name: str           # 惑星名
    sign: str           # サイン（星座）
    sign_jp: str        # サイン（日本語）
    degree: float       # サイン内の度数
    absolute_degree: float  # 黄道上の絶対度数
    house: str          # ハウス
    retrograde: bool    # 逆行中かどうか
    
    def __str__(self) -> str:
        retro = "R" if self.retrograde else ""
        return f"{self.name}: {self.sign} {self.degree:.2f}° {retro} (House {self.house})"


@dataclass
class AspectData:
    """アスペクトデータ"""
    planet1: str
    planet2: str
    aspect_type: str    # conjunction, opposition, trine, square, sextile
    aspect_name_jp: str # 日本語名
    orb: float          # オーブ（許容度数）
    
    def __str__(self) -> str:
        return f"{self.planet1} {self.aspect_type} {self.planet2} (orb: {self.orb:.2f}°)"


# サインの英語→日本語マッピング
SIGN_JP = {
    "Ari": "牡羊座", "Tau": "牡牛座", "Gem": "双子座", "Can": "蟹座",
    "Leo": "獅子座", "Vir": "乙女座", "Lib": "天秤座", "Sco": "蠍座",
    "Sag": "射手座", "Cap": "山羊座", "Aqu": "水瓶座", "Pis": "魚座"
}

# アスペクトの英語→日本語マッピング
ASPECT_JP = {
    "conjunction": "コンジャンクション（合）",
    "opposition": "オポジション（衝）",
    "trine": "トライン（120度）",
    "square": "スクエア（90度）",
    "sextile": "セクスタイル（60度）",
    "quincunx": "クインカンクス（150度）",
    "semisextile": "セミセクスタイル（30度）",
}

# 惑星名の日本語マッピング
PLANET_JP = {
    "Sun": "太陽", "Moon": "月", "Mercury": "水星", "Venus": "金星",
    "Mars": "火星", "Jupiter": "木星", "Saturn": "土星", 
    "Uranus": "天王星", "Neptune": "海王星", "Pluto": "冥王星",
    "True_Node": "ドラゴンヘッド", "Mean_Node": "平均ドラゴンヘッド",
    "Chiron": "キロン", "Lilith": "リリス"
}


class BirthChart:
    """
    出生図（ネイタルチャート）クラス
    
    Astro-Seekと同等の計算をKerykeion（Swiss Ephemeris）で実行
    """
    
    def __init__(
        self,
        name: str,
        year: int,
        month: int,
        day: int,
        hour: int = 12,
        minute: int = 0,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        tz_str: Optional[str] = None,
        house_system: str = "P",  # P=Placidus, K=Koch, W=Whole Sign
        sidereal: bool = False
    ):
        """
        出生図を作成
        
        Args:
            name: 名前
            year: 出生年
            month: 出生月
            day: 出生日
            hour: 出生時（24時間制）
            minute: 出生分
            city: 都市名（lat/lngが指定されない場合に使用）
            lat: 緯度（直接指定する場合）
            lng: 経度（直接指定する場合）
            tz_str: タイムゾーン名（例: "Asia/Tokyo"）
            house_system: ハウスシステム（Placidus, Koch, Whole Sign等）
            sidereal: サイドリアル（恒星時）を使用するか
        """
        self.name = name
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.city = city
        self.house_system = house_system
        self.sidereal = sidereal
        
        # 座標の取得
        if lat is not None and lng is not None:
            self.lat = lat
            self.lng = lng
        elif city:
            self.lat, self.lng = get_coordinates(city)
        else:
            # デフォルト: 東京
            self.lat, self.lng = 35.6762, 139.6503
        
        # タイムゾーンの取得
        if tz_str:
            self.tz_str = tz_str
        else:
            self.tz_str = get_timezone(self.lat, self.lng)
        
        # Kerykeionでチャートを計算
        self._subject = AstrologicalSubject(
            name=name,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            lat=self.lat,
            lng=self.lng,
            tz_str=self.tz_str,
            houses_system_identifier=house_system,
            sidereal_mode=sidereal if sidereal else None
        )
        
        # Kerykeion v5: model() を呼び出してデータを取得
        self._model = self._subject.model()
    
    def _planet_to_position(self, planet) -> PlanetPosition:
        """Kerykeionの惑星オブジェクトをPlanetPositionに変換"""
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
    
    # 主要惑星へのアクセサ
    @property
    def sun(self) -> PlanetPosition:
        """太陽の位置"""
        return self._planet_to_position(self._model.sun)
    
    @property
    def moon(self) -> PlanetPosition:
        """月の位置"""
        return self._planet_to_position(self._model.moon)
    
    @property
    def mercury(self) -> PlanetPosition:
        """水星の位置"""
        return self._planet_to_position(self._model.mercury)
    
    @property
    def venus(self) -> PlanetPosition:
        """金星の位置"""
        return self._planet_to_position(self._model.venus)
    
    @property
    def mars(self) -> PlanetPosition:
        """火星の位置"""
        return self._planet_to_position(self._model.mars)
    
    @property
    def jupiter(self) -> PlanetPosition:
        """木星の位置"""
        return self._planet_to_position(self._model.jupiter)
    
    @property
    def saturn(self) -> PlanetPosition:
        """土星の位置"""
        return self._planet_to_position(self._model.saturn)
    
    @property
    def uranus(self) -> PlanetPosition:
        """天王星の位置"""
        return self._planet_to_position(self._model.uranus)
    
    @property
    def neptune(self) -> PlanetPosition:
        """海王星の位置"""
        return self._planet_to_position(self._model.neptune)
    
    @property
    def pluto(self) -> PlanetPosition:
        """冥王星の位置"""
        return self._planet_to_position(self._model.pluto)
    
    @property
    def chiron(self) -> PlanetPosition:
        """キロンの位置"""
        return self._planet_to_position(self._model.chiron)
    
    @property
    def true_node(self) -> PlanetPosition:
        """ドラゴンヘッド（トゥルーノード）の位置"""
        return self._planet_to_position(self._model.true_north_lunar_node)
    
    # アングル（感受点）
    @property
    def ascendant(self) -> Dict[str, Any]:
        """アセンダント（上昇点）"""
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
    
    @property
    def descendant(self) -> Dict[str, Any]:
        """ディセンダント（下降点）"""
        desc = self._model.seventh_house
        sign = getattr(desc, 'sign', 'Unknown')
        return {
            "degree": getattr(desc, 'position', 0.0),
            "sign": sign,
            "sign_jp": SIGN_JP.get(str(sign)[:3], str(sign)),
            "absolute_degree": getattr(desc, 'abs_pos', 0.0)
        }
    
    @property
    def imum_coeli(self) -> Dict[str, Any]:
        """IC（天底）"""
        ic = self._model.fourth_house
        sign = getattr(ic, 'sign', 'Unknown')
        return {
            "degree": getattr(ic, 'position', 0.0),
            "sign": sign,
            "sign_jp": SIGN_JP.get(str(sign)[:3], str(sign)),
            "absolute_degree": getattr(ic, 'abs_pos', 0.0)
        }
    
    @property
    def houses(self) -> List[Dict[str, Any]]:
        """全12ハウスのカスプ"""
        houses = []
        house_attrs = [
            'first_house', 'second_house', 'third_house', 'fourth_house',
            'fifth_house', 'sixth_house', 'seventh_house', 'eighth_house',
            'ninth_house', 'tenth_house', 'eleventh_house', 'twelfth_house'
        ]
        for i, attr in enumerate(house_attrs, 1):
            house = getattr(self._model, attr)
            sign = getattr(house, 'sign', 'Unknown')
            houses.append({
                "house": i,
                "degree": getattr(house, 'position', 0.0),
                "sign": sign,
                "sign_jp": SIGN_JP.get(str(sign)[:3], str(sign)),
                "absolute_degree": getattr(house, 'abs_pos', 0.0)
            })
        return houses
    
    @property
    def planets(self) -> List[PlanetPosition]:
        """全惑星のリスト"""
        return [
            self.sun, self.moon, self.mercury, self.venus, self.mars,
            self.jupiter, self.saturn, self.uranus, self.neptune, self.pluto,
            self.chiron, self.true_node
        ]
    
    @property
    def aspects(self) -> List[AspectData]:
        """全アスペクトのリスト"""
        aspects = []
        # アスペクトの計算
        aspect_angles = {
            "conjunction": (0, 8),
            "opposition": (180, 8),
            "trine": (120, 6),
            "square": (90, 6),
            "sextile": (60, 4),
        }
        
        planets = self.planets
        for i, p1 in enumerate(planets):
            for p2 in planets[i+1:]:
                diff = abs(p1.absolute_degree - p2.absolute_degree)
                if diff > 180:
                    diff = 360 - diff
                
                for aspect_name, (angle, max_orb) in aspect_angles.items():
                    orb = abs(diff - angle)
                    if orb <= max_orb:
                        aspects.append(AspectData(
                            planet1=p1.name,
                            planet2=p2.name,
                            aspect_type=aspect_name,
                            aspect_name_jp=ASPECT_JP.get(aspect_name, aspect_name),
                            orb=orb
                        ))
        
        aspects.sort(key=lambda x: x.orb)
        return aspects
    
    def get_kerykeion_subject(self) -> AstrologicalSubject:
        """内部のKerykeion AstrologicalSubjectを取得"""
        return self._subject
    
    def get_model(self):
        """内部のKerykeionモデルを取得"""
        return self._model
    
    def save_svg(self, filepath: str, chart_type: str = "natal") -> str:
        """
        SVGチャートを保存
        
        Args:
            filepath: 保存先パス
            chart_type: チャートタイプ
        
        Returns:
            str: 保存されたファイルパス
        """
        from kerykeion import KerykeionChartSVG
        import shutil
        import os
        import glob
        
        chart = KerykeionChartSVG(self._subject)
        chart.makeSVG()
        
        # デフォルトの保存先を探す（スペースあり/なしの両パターン）
        home = os.path.expanduser("~")
        possible_paths = [
            os.path.join(home, f"{self.name}NatalChart.svg"),
            os.path.join(home, f"{self.name} - Natal Chart.svg"),
            os.path.join(home, f"{self.name}Chart.svg"),
        ]
        
        # globでマッチするファイルも探す
        for pattern in glob.glob(os.path.join(home, f"{self.name}*Chart*.svg")):
            if pattern not in possible_paths:
                possible_paths.append(pattern)
        
        for default_path in possible_paths:
            if os.path.exists(default_path) and default_path != filepath:
                # 保存先ディレクトリを作成
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                shutil.move(default_path, filepath)
                return filepath
        
        return filepath
    
    def summary(self) -> str:
        """チャートのサマリーを日本語で出力"""
        lines = [
            f"=== {self.name} の出生図 ===",
            f"生年月日: {self.year}年{self.month}月{self.day}日 {self.hour}:{self.minute:02d}",
            f"場所: {self.city or f'({self.lat:.4f}, {self.lng:.4f})'}",
            "",
            "【太陽星座・月星座】",
            f"太陽: {self.sun.sign_jp} {self.sun.degree:.2f}°",
            f"月: {self.moon.sign_jp} {self.moon.degree:.2f}°",
            f"アセンダント: {self.ascendant['sign_jp']} {self.ascendant['degree']:.2f}°",
            "",
            "【惑星配置】"
        ]
        for planet in self.planets:
            retro = " (逆行)" if planet.retrograde else ""
            lines.append(f"{PLANET_JP.get(planet.name, planet.name)}: {planet.sign_jp} {planet.degree:.2f}°{retro}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """チャートデータを辞書形式で出力"""
        return {
            "name": self.name,
            "birth_date": f"{self.year}-{self.month:02d}-{self.day:02d}",
            "birth_time": f"{self.hour:02d}:{self.minute:02d}",
            "location": {
                "city": self.city,
                "lat": self.lat,
                "lng": self.lng,
                "timezone": self.tz_str
            },
            "sun": {
                "sign": self.sun.sign,
                "sign_jp": self.sun.sign_jp,
                "degree": self.sun.degree,
                "house": self.sun.house
            },
            "moon": {
                "sign": self.moon.sign,
                "sign_jp": self.moon.sign_jp,
                "degree": self.moon.degree,
                "house": self.moon.house
            },
            "ascendant": self.ascendant,
            "midheaven": self.midheaven,
            "planets": [
                {
                    "name": p.name,
                    "sign": p.sign,
                    "sign_jp": p.sign_jp,
                    "degree": p.degree,
                    "house": p.house,
                    "retrograde": p.retrograde
                }
                for p in self.planets
            ],
            "houses": self.houses,
            "aspects": [
                {
                    "planet1": a.planet1,
                    "planet2": a.planet2,
                    "type": a.aspect_type,
                    "type_jp": a.aspect_name_jp,
                    "orb": a.orb
                }
                for a in self.aspects
            ]
        }
