"""
SVG Chart generation module
SVGチャート生成
"""
from typing import Optional
import os

from kerykeion import AstrologicalSubject, KerykeionChartSVG

from uranai.core.chart import BirthChart


class ChartDrawer:
    """
    SVGチャート生成クラス
    
    Kerykeionを使用してホロスコープチャートをSVGで描画
    """
    
    def __init__(self, chart: BirthChart):
        """
        チャートドローワーを初期化
        
        Args:
            chart: 出生図
        """
        self.chart = chart
        self._subject = chart.get_kerykeion_subject()
    
    def draw_natal_chart(
        self, 
        filepath: Optional[str] = None,
        theme: str = "classic"
    ) -> str:
        """
        ネイタルチャートを描画
        
        Args:
            filepath: 保存先パス（Noneの場合はデフォルトパス）
            theme: テーマ（classic, dark等）
        
        Returns:
            str: 保存されたファイルパス
        """
        chart_svg = KerykeionChartSVG(self._subject)
        chart_svg.makeSVG()
        
        # デフォルトの保存先
        default_path = os.path.join(
            os.path.expanduser("~"),
            f"{self.chart.name}NatalChart.svg"
        )
        
        if filepath and os.path.exists(default_path):
            import shutil
            shutil.move(default_path, filepath)
            return filepath
        
        return default_path
    
    @staticmethod
    def draw_synastry_chart(
        chart1: BirthChart,
        chart2: BirthChart,
        filepath: Optional[str] = None
    ) -> str:
        """
        シナストリーチャート（二重円）を描画
        
        Args:
            chart1: 1人目の出生図（内円）
            chart2: 2人目の出生図（外円）
            filepath: 保存先パス
        
        Returns:
            str: 保存されたファイルパス
        """
        subject1 = chart1.get_kerykeion_subject()
        subject2 = chart2.get_kerykeion_subject()
        
        chart_svg = KerykeionChartSVG(subject1, chart_type="Synastry", second_obj=subject2)
        chart_svg.makeSVG()
        
        default_path = os.path.join(
            os.path.expanduser("~"),
            f"{chart1.name}_{chart2.name}_Synastry.svg"
        )
        
        if filepath and os.path.exists(default_path):
            import shutil
            shutil.move(default_path, filepath)
            return filepath
        
        return default_path
    
    @staticmethod
    def draw_transit_chart(
        natal_chart: BirthChart,
        transit_date: str,
        filepath: Optional[str] = None
    ) -> str:
        """
        トランジットチャート（二重円）を描画
        
        Args:
            natal_chart: ネイタルチャート（内円）
            transit_date: トランジット日時（"YYYY-MM-DD"形式）
            filepath: 保存先パス
        
        Returns:
            str: 保存されたファイルパス
        """
        from uranai.predictive.transit import TransitChart
        
        natal_subject = natal_chart.get_kerykeion_subject()
        
        # トランジット用のSubjectを作成
        parts = transit_date.split("-")
        transit_subject = AstrologicalSubject(
            name="Transit",
            year=int(parts[0]),
            month=int(parts[1]),
            day=int(parts[2]),
            hour=12,
            minute=0,
            lat=natal_chart.lat,
            lng=natal_chart.lng,
            tz_str=natal_chart.tz_str
        )
        
        chart_svg = KerykeionChartSVG(natal_subject, chart_type="Transit", second_obj=transit_subject)
        chart_svg.makeSVG()
        
        default_path = os.path.join(
            os.path.expanduser("~"),
            f"{natal_chart.name}_Transit_{transit_date}.svg"
        )
        
        if filepath and os.path.exists(default_path):
            import shutil
            shutil.move(default_path, filepath)
            return filepath
        
        return default_path
