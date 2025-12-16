"""
Synastry calculation module
シナストリー（相性）計算
"""
from typing import List, Dict, Any
from dataclasses import dataclass

from uranai.core.chart import BirthChart, PlanetPosition, SIGN_JP, ASPECT_JP, PLANET_JP


@dataclass
class SynastryAspect:
    """シナストリーアスペクトデータ"""
    person1_planet: str     # Person1の惑星
    person2_planet: str     # Person2の惑星
    aspect_type: str        # アスペクトタイプ
    aspect_name_jp: str     # 日本語名
    orb: float              # オーブ
    is_harmonious: bool     # 調和的かどうか
    
    def __str__(self) -> str:
        harmony = "◎" if self.is_harmonious else "△"
        return f"{harmony} {self.person1_planet} {self.aspect_type} {self.person2_planet} (orb: {self.orb:.2f}°)"


# アスペクトの分類
HARMONIOUS_ASPECTS = {'conjunction', 'trine', 'sextile'}
CHALLENGING_ASPECTS = {'opposition', 'square'}


class Synastry:
    """
    シナストリー（相性）クラス
    
    2人の出生図間のアスペクトを分析
    """
    
    def __init__(self, chart1: BirthChart, chart2: BirthChart):
        """
        シナストリーを計算
        
        Args:
            chart1: 1人目の出生図
            chart2: 2人目の出生図
        """
        self.chart1 = chart1
        self.chart2 = chart2
        self._aspects = None
        self._score = None
    
    @property
    def aspects(self) -> List[SynastryAspect]:
        """2人の間のアスペクト"""
        if self._aspects is not None:
            return self._aspects
        
        aspects = []
        
        # アスペクトの角度とオーブ設定
        aspect_config = {
            "conjunction": (0, 8),
            "opposition": (180, 8),
            "trine": (120, 6),
            "square": (90, 6),
            "sextile": (60, 4),
        }
        
        planet_attrs = ['sun', 'moon', 'mercury', 'venus', 'mars', 
                        'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
        
        for attr1 in planet_attrs:
            p1 = getattr(self.chart1, attr1)
            
            for attr2 in planet_attrs:
                p2 = getattr(self.chart2, attr2)
                
                # 角度差を計算
                diff = abs(p1.absolute_degree - p2.absolute_degree)
                if diff > 180:
                    diff = 360 - diff
                
                # 各アスペクトをチェック
                for aspect_name, (angle, max_orb) in aspect_config.items():
                    orb = abs(diff - angle)
                    if orb <= max_orb:
                        is_harmonious = aspect_name in HARMONIOUS_ASPECTS
                        aspects.append(SynastryAspect(
                            person1_planet=p1.name,
                            person2_planet=p2.name,
                            aspect_type=aspect_name,
                            aspect_name_jp=ASPECT_JP.get(aspect_name, aspect_name),
                            orb=orb,
                            is_harmonious=is_harmonious
                        ))
        
        # オーブの小さい順にソート
        aspects.sort(key=lambda x: x.orb)
        self._aspects = aspects
        return self._aspects
    
    @property
    def score(self) -> int:
        """
        相性スコア（0-100）
        
        調和的アスペクト: +ポイント
        挑戦的アスペクト: -ポイント（ただしオーブが小さいほどインパクト大）
        """
        if self._score is not None:
            return self._score
        
        score = 50  # 基準点
        
        # 重要な惑星ペアの重み付け
        important_pairs = {
            ('Sun', 'Moon'): 3.0,
            ('Moon', 'Sun'): 3.0,
            ('Sun', 'Venus'): 2.5,
            ('Venus', 'Sun'): 2.5,
            ('Moon', 'Venus'): 2.5,
            ('Venus', 'Moon'): 2.5,
            ('Venus', 'Mars'): 2.0,
            ('Mars', 'Venus'): 2.0,
            ('Sun', 'Sun'): 2.0,
            ('Moon', 'Moon'): 2.0,
            ('Venus', 'Venus'): 2.0,
            ('Sun', 'Ascendant'): 2.0,
            ('Moon', 'Ascendant'): 2.0,
        }
        
        for asp in self.aspects:
            weight = important_pairs.get((asp.person1_planet, asp.person2_planet), 1.0)
            orb_factor = 1 - (asp.orb / 10)  # オーブが小さいほど影響大
            
            if asp.is_harmonious:
                score += 5 * weight * orb_factor
            else:
                score -= 3 * weight * orb_factor
        
        # 0-100の範囲にクリップ
        self._score = max(0, min(100, int(score)))
        return self._score
    
    @property
    def compatibility_level(self) -> str:
        """相性レベル（日本語）"""
        s = self.score
        if s >= 80:
            return "最高の相性 ★★★★★"
        elif s >= 65:
            return "とても良い相性 ★★★★☆"
        elif s >= 50:
            return "良い相性 ★★★☆☆"
        elif s >= 35:
            return "普通の相性 ★★☆☆☆"
        else:
            return "挑戦的な相性 ★☆☆☆☆"
    
    def get_key_aspects(self, limit: int = 10) -> List[SynastryAspect]:
        """重要なアスペクトを取得"""
        # Sun, Moon, Venus, Marsを含むアスペクトを優先
        key_planets = {'Sun', 'Moon', 'Venus', 'Mars'}
        key_aspects = [a for a in self.aspects 
                      if a.person1_planet in key_planets or a.person2_planet in key_planets]
        return key_aspects[:limit]
    
    def summary(self) -> str:
        """相性のサマリー"""
        lines = [
            f"=== {self.chart1.name} と {self.chart2.name} の相性 ===",
            "",
            f"【相性スコア】 {self.score}点 / 100点",
            f"{self.compatibility_level}",
            "",
            f"【{self.chart1.name}】",
            f"太陽: {self.chart1.sun.sign_jp}  月: {self.chart1.moon.sign_jp}",
            f"金星: {self.chart1.venus.sign_jp}  火星: {self.chart1.mars.sign_jp}",
            "",
            f"【{self.chart2.name}】",
            f"太陽: {self.chart2.sun.sign_jp}  月: {self.chart2.moon.sign_jp}",
            f"金星: {self.chart2.venus.sign_jp}  火星: {self.chart2.mars.sign_jp}",
            "",
            "【重要なアスペクト】"
        ]
        
        for asp in self.get_key_aspects():
            harmony = "調和" if asp.is_harmonious else "緊張"
            p1_jp = PLANET_JP.get(asp.person1_planet, asp.person1_planet)
            p2_jp = PLANET_JP.get(asp.person2_planet, asp.person2_planet)
            lines.append(f"[{harmony}] {self.chart1.name}の{p1_jp} {asp.aspect_name_jp} "
                        f"{self.chart2.name}の{p2_jp}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """相性データを辞書形式で出力"""
        return {
            "person1": {
                "name": self.chart1.name,
                "sun": self.chart1.sun.sign_jp,
                "moon": self.chart1.moon.sign_jp,
                "venus": self.chart1.venus.sign_jp,
                "mars": self.chart1.mars.sign_jp
            },
            "person2": {
                "name": self.chart2.name,
                "sun": self.chart2.sun.sign_jp,
                "moon": self.chart2.moon.sign_jp,
                "venus": self.chart2.venus.sign_jp,
                "mars": self.chart2.mars.sign_jp
            },
            "score": self.score,
            "level": self.compatibility_level,
            "aspects": [
                {
                    "person1_planet": a.person1_planet,
                    "person2_planet": a.person2_planet,
                    "type": a.aspect_type,
                    "type_jp": a.aspect_name_jp,
                    "orb": a.orb,
                    "is_harmonious": a.is_harmonious
                }
                for a in self.aspects
            ]
        }
