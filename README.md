# Uranai - 占星術計算ライブラリ

Astro-Seekと同等の計算ロジック（Swiss Ephemeris）をPythonで実装した占星術ライブラリ

## インストール

```bash
cd /path/to/uranai
pip install -r requirements.txt
```

## 機能

- 🌟 出生図（Birth Chart）計算
- 💑 相性占い（シナストリー/コンポジット）
- 🔄 トランジット計算
- ☀️ ソーラーリターン
- 🌙 ムーンフェイズ
- 📊 SVGチャート生成

## 使用例

```python
from uranai import BirthChart, TransitChart, Synastry

# 出生図を作成
chart = BirthChart(
    name="太郎",
    year=1990, month=5, day=15,
    hour=10, minute=30,
    city="Tokyo, Japan"
)

# 惑星位置を確認
print(chart.sun)       # 太陽の位置
print(chart.moon)      # 月の位置
print(chart.ascendant) # アセンダント

# アスペクト一覧
for aspect in chart.aspects:
    print(aspect)

# SVGチャートを保存
chart.save_svg("birth_chart.svg")
```

## ライセンス

AGPL-3.0（Kerykeion/Swiss Ephemerisと同様）
