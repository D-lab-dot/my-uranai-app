"""
Uranai デモスクリプト
占星術ライブラリの使用例
"""
from uranai import BirthChart, TransitChart, SolarReturnChart, Synastry, CompositeChart


def main():
    print("=" * 60)
    print("Uranai - 占星術ライブラリ デモ")
    print("=" * 60)
    print()
    
    # 1. 出生図の作成
    print("【1. 出生図の作成】")
    print("-" * 40)
    
    chart1 = BirthChart(
        name="太郎",
        year=1990,
        month=5,
        day=15,
        hour=10,
        minute=30,
        city="Tokyo, Japan"
    )
    
    print(chart1.summary())
    print()
    
    # 2. トランジットの計算
    print("【2. トランジット（2024年12月4日）】")
    print("-" * 40)
    
    transit = TransitChart(chart1, target_date="2024-12-04")
    print(transit.summary())
    print()
    
    # 3. ソーラーリターン
    print("【3. ソーラーリターン（2025年）】")
    print("-" * 40)
    
    solar_return = SolarReturnChart(chart1, return_year=2025)
    print(solar_return.summary())
    print()
    
    # 4. 相性占い（シナストリー）
    print("【4. 相性占い】")
    print("-" * 40)
    
    chart2 = BirthChart(
        name="花子",
        year=1992,
        month=8,
        day=20,
        hour=14,
        minute=0,
        city="Osaka, Japan"
    )
    
    synastry = Synastry(chart1, chart2)
    print(synastry.summary())
    print()
    
    # 5. コンポジットチャート
    print("【5. コンポジットチャート】")
    print("-" * 40)
    
    composite = CompositeChart(chart1, chart2)
    print(composite.summary())
    print()
    
    # 6. データのエクスポート
    print("【6. データエクスポート（JSON形式）】")
    print("-" * 40)
    
    import json
    chart_data = chart1.to_dict()
    print(f"太陽星座: {chart_data['sun']['sign_jp']}")
    print(f"月星座: {chart_data['moon']['sign_jp']}")
    print(f"アセンダント: {chart_data['ascendant']['sign_jp']}")
    print()
    
    # 7. SVGチャート生成（オプション）
    print("【7. SVGチャート生成】")
    print("-" * 40)
    try:
        svg_path = chart1.save_svg("./output/birth_chart.svg")
        print(f"SVGチャートを保存しました: {svg_path}")
    except Exception as e:
        print(f"SVG生成をスキップ: {e}")
    
    print()
    print("=" * 60)
    print("デモ完了")
    print("=" * 60)


if __name__ == "__main__":
    main()
