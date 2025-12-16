"""
Daily Interpretation Module
Logic for Daily Horoscope based on Solar Houses
"""
from datetime import datetime
from uranai import BirthChart, TransitChart

SIGNS = ['牡羊座', '牡牛座', '双子座', '蟹座', '獅子座', '乙女座',
         '天秤座', '蠍座', '射手座', '山羊座', '水瓶座', '魚座']

SOLAR_HOUSE_ADVICE = {
    1: {'theme': '自分自身・スタート', 'advice': '今日は主役の日！新しいことを始めるのに最適です。自分の直感に従って行動しましょう。'},
    2: {'theme': '金運・五感', 'advice': '美味しいものを食べたり、ショッピングを楽しむのに良い日。五感を満たすことで運気が上がります。'},
    3: {'theme': 'コミュニケーション', 'advice': '情報収集や連絡のやり取りが活発になります。友人との会話からヒントが得られそう。'},
    4: {'theme': '家庭・居場所', 'advice': '家でゆっくり過ごすのがおすすめ。部屋の片付けや家族団らんで心が安らぎます。'},
    5: {'theme': '創造性・恋愛', 'advice': 'ワクワクすることを優先しましょう！趣味や恋愛、推し活に全力投球すると良い日です。'},
    6: {'theme': 'メンテナンス・健康', 'advice': '生活リズムを整える日。仕事や勉強が捗ります。健康管理を見直すのにも最適。'},
    7: {'theme': '対人関係', 'advice': '誰かと協力することで物事が進みます。パートナーや親友と過ごすと良い刺激をもらえます。'},
    8: {'theme': '集中・深める', 'advice': '一つのことに没頭するのに良い日。誰かからのプレゼントや引き継ぎがあるかも。'},
    9: {'theme': '冒険・学び', 'advice': '遠くに行きたくなる日。知らない街を歩いたり、新しい分野の勉強を始めると運気UP。'},
    10: {'theme': '社会・成果', 'advice': '仕事で成果が出やすい日。目上の人からの評価も期待できます。責任ある行動が吉。'},
    11: {'theme': '仲間・未来', 'advice': '友人やグループ活動が盛り上がります。未来の夢について語り合うと良いでしょう。'},
    12: {'theme': '休息・癒し', 'advice': '少し疲れやすくなるかも。一人の時間を大切にし、心身のデトックスを心がけて。'}
}

def get_moon_sign_jp(date):
    """指定日の月星座（日本語）を取得"""
    # ダミーのチャートを作成して月位置を計算
    # 場所は東京固定
    dummy_chart = BirthChart(
        name="Daily",
        year=date.year,
        month=date.month,
        day=date.day,
        hour=12,
        minute=0,
        city="Tokyo"
    )
    return dummy_chart.moon.sign_jp

def generate_daily_forecast(sign, date):
    """12星座占い（ソーラーハウス法）"""
    
    # 1. 今日の月星座を取得
    moon_sign_jp = get_moon_sign_jp(date)
    
    # 2. ハウスを計算
    try:
        user_idx = SIGNS.index(sign)
        moon_idx = SIGNS.index(moon_sign_jp)
    except ValueError:
        return {'score': 3, 'message': 'データエラー', 'house': 1}
        
    # ハウス番号 = (月座 - 自分座 + 12) % 12 + 1
    # Example: 自分=牡羊(0), 月=牡羊(0) -> 1ハウス
    # Example: 自分=牡羊(0), 月=牡牛(1) -> 2ハウス
    house_num = (moon_idx - user_idx + 12) % 12 + 1
    
    # 3. アドバイス生成
    info = SOLAR_HOUSE_ADVICE.get(house_num, {})
    
    # スコア計算（簡易的: 1,5,9,10ハウスは高め、6,8,12は低め設定など）
    base_scores = {1:5, 5:5, 9:5, 10:5, 3:4, 7:4, 11:4, 2:3, 4:3, 6:3, 8:2, 12:2}
    score = base_scores.get(house_num, 3)
    
    colors = ['レッド', 'ブルー', 'イエロー', 'グリーン', 'ピンク', 'ホワイト', 'ゴールド', 'パープル', 'オレンジ', 'ブラック', 'シルバー', 'ブラウン']
    lucky_color = colors[house_num % len(colors)]
    
    return {
        'score': score,
        'house': house_num,
        'moon_sign': moon_sign_jp,
        'theme': info.get('theme', ''),
        'message': info.get('advice', ''),
        'lucky_color': lucky_color
    }
