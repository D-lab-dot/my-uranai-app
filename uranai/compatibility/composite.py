"""
Composite Chart calculation module
コンポジット（合成）チャート計算
"""
from typing import List, Dict, Any, Optional

from kerykeion import AstrologicalSubject

from uranai.core.chart import BirthChart, PlanetPosition, SIGN_JP, PLANET_JP


class CompositeChart:
    """
    コンポジット（合成）チャートクラス
    
    2人の惑星位置の中間点を計算して合成チャートを生成
    """
    
    def __init__(self, chart1: BirthChart, chart2: BirthChart):
        """
        コンポジットチャートを計算
        
        Args:
            chart1: 1人目の出生図
            chart2: 2人目の出生図
        """
        self.chart1 = chart1
        self.chart2 = chart2
        self.name = f"{chart1.name} & {chart2.name}"
        
        # 中間点を計算
        self._composite_planets = {}
        self._calculate_midpoints()
    
    def _midpoint(self, pos1: float, pos2: float) -> float:
        """
        2つの黄道位置の中間点を計算
        """
        diff = abs(pos1 - pos2)
        if diff > 180:
            # 短い方の弧を使用
            mid = (pos1 + pos2) / 2 + 180
            if mid >= 360:
                mid -= 360
        else:
            mid = (pos1 + pos2) / 2
        return mid
    
    def _position_to_sign(self, abs_pos: float) -> tuple:
        """
        絶対度数からサインと度数を計算
        """
        signs = ['Ari', 'Tau', 'Gem', 'Can', 'Leo', 'Vir', 
                 'Lib', 'Sco', 'Sag', 'Cap', 'Aqu', 'Pis']
        sign_index = int(abs_pos / 30)
        degree = abs_pos % 30
        return signs[sign_index], degree
    
    def _calculate_midpoints(self):
        """各惑星の中間点を計算"""
        planet_attrs = ['sun', 'moon', 'mercury', 'venus', 'mars', 
                        'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
        
        for attr in planet_attrs:
            p1 = getattr(self.chart1, attr)
            p2 = getattr(self.chart2, attr)
            
            mid_pos = self._midpoint(p1.absolute_degree, p2.absolute_degree)
            sign, degree = self._position_to_sign(mid_pos)
            
            self._composite_planets[attr] = PlanetPosition(
                name=p1.name,
                sign=sign,
                sign_jp=SIGN_JP.get(sign, sign),
                degree=degree,
                absolute_degree=mid_pos,
                house=0,  # コンポジットではハウスは別途計算が必要
                retrograde=False
            )
        
        # アセンダントの中間点
        asc1_pos = self.chart1.ascendant.get('absolute_degree', 0)
        asc2_pos = self.chart2.ascendant.get('absolute_degree', 0)
        asc_mid = self._midpoint(asc1_pos, asc2_pos)
        asc_sign, asc_degree = self._position_to_sign(asc_mid)
        self._composite_ascendant = {
            'degree': asc_degree,
            'sign': asc_sign,
            'sign_jp': SIGN_JP.get(asc_sign, asc_sign),
            'absolute_degree': asc_mid
        }
        
        # MCの中間点
        mc1_pos = self.chart1.midheaven.get('absolute_degree', 0)
        mc2_pos = self.chart2.midheaven.get('absolute_degree', 0)
        mc_mid = self._midpoint(mc1_pos, mc2_pos)
        mc_sign, mc_degree = self._position_to_sign(mc_mid)
        self._composite_midheaven = {
            'degree': mc_degree,
            'sign': mc_sign,
            'sign_jp': SIGN_JP.get(mc_sign, mc_sign),
            'absolute_degree': mc_mid
        }
    
    @property
    def sun(self) -> PlanetPosition:
        return self._composite_planets['sun']
    
    @property
    def moon(self) -> PlanetPosition:
        return self._composite_planets['moon']
    
    @property
    def mercury(self) -> PlanetPosition:
        return self._composite_planets['mercury']
    
    @property
    def venus(self) -> PlanetPosition:
        return self._composite_planets['venus']
    
    @property
    def mars(self) -> PlanetPosition:
        return self._composite_planets['mars']
    
    @property
    def jupiter(self) -> PlanetPosition:
        return self._composite_planets['jupiter']
    
    @property
    def saturn(self) -> PlanetPosition:
        return self._composite_planets['saturn']
    
    @property
    def planets(self) -> List[PlanetPosition]:
        """全惑星のリスト"""
        return list(self._composite_planets.values())
    
    @property
    def ascendant(self) -> Dict[str, Any]:
        """コンポジットアセンダント"""
        return self._composite_ascendant
    
    @property
    def midheaven(self) -> Dict[str, Any]:
        """コンポジットMC"""
        return self._composite_midheaven
    
    def summary(self) -> str:
        """コンポジットチャートのサマリー"""
        lines = [
            f"=== {self.name} のコンポジットチャート ===",
            "",
            "【コンポジット太陽・月】",
            f"太陽: {self.sun.sign_jp} {self.sun.degree:.2f}°",
            f"月: {self.moon.sign_jp} {self.moon.degree:.2f}°",
            "",
            "【コンポジットアングル】",
            f"ASC: {self.ascendant['sign_jp']} {self.ascendant['degree']:.2f}°",
            f"MC: {self.midheaven['sign_jp']} {self.midheaven['degree']:.2f}°",
            "",
            "【コンポジット惑星】"
        ]
        
        for planet in self.planets:
            lines.append(f"{PLANET_JP.get(planet.name, planet.name)}: "
                        f"{planet.sign_jp} {planet.degree:.2f}°")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """コンポジットデータを辞書形式で出力"""
        return {
            "name": self.name,
            "person1": self.chart1.name,
            "person2": self.chart2.name,
            "ascendant": self.ascendant,
            "midheaven": self.midheaven,
            "planets": [
                {
                    "name": p.name,
                    "name_jp": PLANET_JP.get(p.name, p.name),
                    "sign": p.sign,
                    "sign_jp": p.sign_jp,
                    "degree": p.degree,
                    "absolute_degree": p.absolute_degree
                }
                for p in self.planets
            ]
        }
