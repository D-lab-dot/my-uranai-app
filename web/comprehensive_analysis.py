"""
Comprehensive Astrology Analysis Engine
LLM-level detailed analysis with Astro-Seek quality data
"""

from datetime import datetime
import math

# 星座シンボル
SIGN_SYMBOLS = {
    'Ari': '♈', 'Tau': '♉', 'Gem': '♊', 'Can': '♋', 'Leo': '♌', 'Vir': '♍',
    'Lib': '♎', 'Sco': '♏', 'Sag': '♐', 'Cap': '♑', 'Aqu': '♒', 'Pis': '♓'
}

SIGN_JP = {
    'Ari': '牡羊座', 'Tau': '牡牛座', 'Gem': '双子座', 'Can': '蟹座',
    'Leo': '獅子座', 'Vir': '乙女座', 'Lib': '天秤座', 'Sco': '蠍座',
    'Sag': '射手座', 'Cap': '山羊座', 'Aqu': '水瓶座', 'Pis': '魚座'
}

PLANET_SYMBOLS = {
    'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀', 'Mars': '♂',
    'Jupiter': '♃', 'Saturn': '♄', 'Uranus': '♅', 'Neptune': '♆', 'Pluto': '♇',
    'True_North_Node': '☊', 'Chiron': '⚷', 'Mean_Lilith': '⚸'
}

PLANET_JP = {
    'Sun': '太陽', 'Moon': '月', 'Mercury': '水星', 'Venus': '金星', 'Mars': '火星',
    'Jupiter': '木星', 'Saturn': '土星', 'Uranus': '天王星', 'Neptune': '海王星',
    'Pluto': '冥王星', 'True_North_Node': 'ノースノード', 'Chiron': 'キロン',
    'Mean_Lilith': 'リリス', 'True_Lilith': 'リリス'
}

HOUSE_NAME_TO_NUM = {
    'First_House': 1, 'Second_House': 2, 'Third_House': 3, 'Fourth_House': 4,
    'Fifth_House': 5, 'Sixth_House': 6, 'Seventh_House': 7, 'Eighth_House': 8,
    'Ninth_House': 9, 'Tenth_House': 10, 'Eleventh_House': 11, 'Twelfth_House': 12
}

def get_house_num(house_str):
    """ハウス名から数字を取得"""
    if isinstance(house_str, int):
        return house_str
    house_str = str(house_str)
    for key, val in HOUSE_NAME_TO_NUM.items():
        if key in house_str:
            return val
    import re
    nums = re.findall(r'\d+', house_str)
    return int(nums[0]) if nums else 1


def format_degree(degree):
    """度数を度°分'形式にフォーマット"""
    deg = int(degree)
    minutes = int((degree - deg) * 60)
    return f"{deg}°{minutes:02d}'"


def generate_comprehensive_analysis(chart, birth_year, unknown_time=False):
    """包括的なホロスコープ分析を生成"""
    
    analysis = {
        'planet_positions': generate_planet_positions(chart),
        'house_cusps': generate_house_cusps(chart, unknown_time),
        'aspects': generate_aspect_analysis(chart),
        'interpretations': generate_all_interpretations(chart, birth_year, unknown_time)
    }
    
    return analysis


def generate_planet_positions(chart):
    """全惑星位置を詳細にリスト"""
    positions = []
    
    for planet in chart.planets:
        pos = {
            'name': PLANET_JP.get(planet.name, planet.name),
            'symbol': PLANET_SYMBOLS.get(planet.name, ''),
            'sign': planet.sign_jp,
            'sign_symbol': SIGN_SYMBOLS.get(planet.sign, ''),
            'degree': format_degree(planet.degree),
            'degree_raw': planet.degree,
            'house': get_house_num(planet.house),
            'retrograde': getattr(planet, 'retrograde', False)
        }
        positions.append(pos)
    
    return positions


def generate_house_cusps(chart, unknown_time=False):
    """12ハウスのカスプ情報"""
    if unknown_time:
        return None
    
    cusps = []
    for i, house in enumerate(chart.houses, 1):
        cusp = {
            'house': i,
            'sign': house.sign_jp if hasattr(house, 'sign_jp') else '',
            'degree': format_degree(house.degree) if hasattr(house, 'degree') else '',
            'meaning': get_house_meaning(i)
        }
        cusps.append(cusp)
    
    return cusps


def get_house_meaning(house_num):
    """ハウスの意味を日常語で説明"""
    meanings = {
        1: {'title': '自分自身', 'keywords': '外見・第一印象・性格の表れ方', 
            'detail': 'あなたが世界に見せる「顔」。初対面の印象、外見的特徴、無意識の振る舞い方。'},
        2: {'title': 'お金と価値観', 'keywords': '収入・所有物・自己価値',
            'detail': '自分で稼ぐお金、大切にしているもの、「これだけは譲れない」価値観。'},
        3: {'title': 'コミュニケーション', 'keywords': '会話・学習・兄弟・近所',
            'detail': 'LINEの返し方、勉強のスタイル、兄弟姉妹との関係、日常の知的活動。'},
        4: {'title': '家庭とルーツ', 'keywords': '家族・実家・心の安定・老後',
            'detail': '帰る場所としての家庭、家族関係、心の奥底にある安心感の源。'},
        5: {'title': '楽しみと創造性', 'keywords': '恋愛・趣味・子供・自己表現',
            'detail': 'デートスタイル、休日の過ごし方、創作活動、人生を楽しむ力。'},
        6: {'title': '仕事と健康', 'keywords': '日常業務・ルーティン・健康管理',
            'detail': '毎日の仕事への取り組み、職場での立ち回り、健康状態。'},
        7: {'title': 'パートナーシップ', 'keywords': '結婚・契約・対人関係',
            'detail': 'どんな人と結婚するか、ビジネスパートナー、「自分に足りないもの」を持つ相手。'},
        8: {'title': '変容と深い絆', 'keywords': '遺産・共有財産・心理的変容・性',
            'detail': '人生を根底から変える体験、トラウマと回復、パートナーの収入、投資。'},
        9: {'title': '探求と冒険', 'keywords': '海外・大学・哲学・長期旅行',
            'detail': '「より広い世界を知りたい」欲求、留学、宗教や哲学、人生の意味探求。'},
        10: {'title': 'キャリアと社会的地位', 'keywords': '天職・評判・肩書き・父親',
            'detail': 'どんな仕事で成功するか、社会からの評価、公的な顔、権威。'},
        11: {'title': '友人と理想', 'keywords': '友人関係・コミュニティ・未来の夢',
            'detail': '所属するグループ、オンラインコミュニティ、「社会をこう変えたい」という理想。'},
        12: {'title': '無意識と秘密', 'keywords': 'スピリチュアル・隠れた自分・癒し',
            'detail': '表に出さない「もう一人の自分」、夢の世界、無意識のパターン、秘密。'}
    }
    return meanings.get(house_num, {})


def generate_aspect_analysis(chart):
    """全アスペクトを分析"""
    aspects = []
    
    for aspect in chart.aspects:
        asp = {
            'planet1': PLANET_JP.get(aspect.planet1, aspect.planet1),
            'planet2': PLANET_JP.get(aspect.planet2, aspect.planet2),
            'type': aspect.aspect_type,
            'type_jp': aspect.aspect_name_jp if hasattr(aspect, 'aspect_name_jp') else get_aspect_jp(aspect.aspect_type),
            'orb': f"{aspect.orb:.1f}°",
            'influence': get_aspect_influence(aspect.aspect_type),
            'interpretation': get_aspect_interpretation_text_v2(aspect)
        }
        aspects.append(asp)
    
    return aspects


def get_aspect_interpretation_text_v2(aspect):
    """アスペクトの詳細解釈（修正版）"""
    p1, p2 = aspect.planet1, aspect.planet2
    atype = aspect.aspect_type
    
    # 主要アスペクトの解釈辞書
    interpretations = get_aspect_interpretations()
    
    key = f"{p1}_{p2}_{atype}"
    alt_key = f"{p2}_{p1}_{atype}"
    
    if key in interpretations:
        return interpretations[key]
    elif alt_key in interpretations:
        return interpretations[alt_key]
    else:
        return generate_generic_aspect_text(p1, p2, atype)



def get_aspect_jp(aspect_type):
    """アスペクトタイプを日本語に"""
    types = {
        'conjunction': 'コンジャンクション（合）0°',
        'opposition': 'オポジション（衝）180°',
        'trine': 'トライン（三分）120°',
        'square': 'スクエア（四分）90°',
        'sextile': 'セクスタイル（六分）60°',
        'quincunx': 'クインカンクス 150°'
    }
    return types.get(aspect_type, aspect_type)


def get_aspect_influence(aspect_type):
    """アスペクトの影響（調和/緊張）"""
    harmonious = ['trine', 'sextile']
    challenging = ['square', 'opposition']
    if aspect_type in harmonious:
        return 'harmonious'
    elif aspect_type in challenging:
        return 'challenging'
    else:
        return 'neutral'


def get_aspect_interpretation_text(aspect):
    """アスペクトの詳細解釈"""
    p1, p2 = aspect.planet1, aspect.planet2
    atype = aspect.type
    
    # 主要アスペクトの解釈辞書（一部）
    interpretations = get_aspect_interpretations()
    
    key = f"{p1}_{p2}_{atype}"
    alt_key = f"{p2}_{p1}_{atype}"
    
    if key in interpretations:
        return interpretations[key]
    elif alt_key in interpretations:
        return interpretations[alt_key]
    else:
        return generate_generic_aspect_text(p1, p2, atype)


def generate_generic_aspect_text(p1, p2, atype):
    """汎用アスペクト解釈を生成"""
    p1_jp = PLANET_JP.get(p1, p1)
    p2_jp = PLANET_JP.get(p2, p2)
    
    if atype == 'conjunction':
        return f"{p1_jp}と{p2_jp}のエネルギーが融合し、強力に作用します。二つの惑星の性質が一体化しています。"
    elif atype == 'opposition':
        return f"{p1_jp}と{p2_jp}が対立と緊張を生み出します。バランスを取ることが課題であり、統合できれば大きな力になります。"
    elif atype == 'trine':
        return f"{p1_jp}と{p2_jp}が調和的に流れ、才能として自然に発揮されます。努力なしに得られる恵みです。"
    elif atype == 'square':
        return f"{p1_jp}と{p2_jp}が摩擦を起こし、行動を促します。困難を乗り越えることで強さが生まれます。"
    elif atype == 'sextile':
        return f"{p1_jp}と{p2_jp}が機会を通じて協力します。意識的に活用すれば才能になります。"
    else:
        return f"{p1_jp}と{p2_jp}が特殊な角度で関係しています。"


def get_aspect_interpretations():
    """主要アスペクトの詳細解釈辞書"""
    return {
        'Sun_Moon_conjunction': '太陽と月の合一は、意識と無意識、理性と感情が一体化しています。自分が何者かを明確に理解しており、ブレない芯があります。新月生まれで、新しいことを始める力に優れています。',
        'Sun_Moon_opposition': '太陽と月の対立は、意識と無意識の間で葛藤があります。満月生まれで、人間関係を通じて自己を発見します。内面と外面のバランスを取ることが人生のテーマです。',
        'Sun_Venus_conjunction': '太陽と金星の合一は、魅力とカリスマ性を与えます。芸術的才能があり、人に好かれやすいです。美しいものへの感性が鋭く、自己表現に喜びを見出します。',
        'Sun_Mars_conjunction': '太陽と火星の合一は、強いエネルギーと行動力を与えます。競争心が強く、リーダーシップを発揮します。時に攻撃的になりやすいので、エネルギーの建設的な使い方を学ぶ必要があります。',
        'Moon_Venus_conjunction': '月と金星の合一は、感情的な温かさと愛情深さを与えます。芸術的感性が豊かで、人を癒す力があります。恋愛では愛情表現が豊かです。',
        'Moon_Saturn_conjunction': '月と土星の合一は、感情を厳しく自己管理します。幼少期に感情的な制限があった可能性があります。責任感が強いですが、自分を許すことも大切です。',
        'Mercury_Venus_conjunction': '水星と金星の合一は、優雅なコミュニケーション能力を与えます。言葉選びが美しく、外交的です。芸術的な表現や交渉に才能があります。',
        'Venus_Mars_conjunction': '金星と火星の合一は、情熱的な魅力と性的なエネルギーを与えます。恋愛に積極的で、芸術やスポーツで才能を発揮します。',
        'Jupiter_Saturn_conjunction': '木星と土星の合一は、拡大と制限のバランスを表します。野心と現実的な計画力を持ち、長期的な成功を収める可能性があります。',
        'Saturn_Pluto_conjunction': '土星と冥王星の合一は、極端な自己規律と変容の力を持っています。権力構造を理解し、根本的な変革を起こす能力があります。'
    }


def generate_all_interpretations(chart, birth_year, unknown_time=False):
    """全惑星・ハウスの包括的解釈"""
    
    interps = []
    
    # 三大要素
    interps.append(generate_sun_interpretation(chart))
    interps.append(generate_moon_interpretation(chart, unknown_time))
    interps.append(generate_ascendant_interpretation(chart, unknown_time))
    
    # 個人惑星
    for planet in chart.planets:
        if planet.name in ['Mercury', 'Venus', 'Mars']:
            interps.append(generate_planet_interpretation(planet, unknown_time))
    
    # 社会惑星
    for planet in chart.planets:
        if planet.name in ['Jupiter', 'Saturn']:
            interps.append(generate_planet_interpretation(planet, unknown_time))
    
    # 外惑星
    for planet in chart.planets:
        if planet.name in ['Uranus', 'Neptune', 'Pluto']:
            interps.append(generate_outer_planet_interpretation(planet))
    
    return interps


def generate_sun_interpretation(chart):
    """太陽の包括的解釈"""
    sun = chart.sun
    sign = sun.sign_jp
    house = get_house_num(sun.house)
    degree = format_degree(sun.degree)
    
    return {
        'title': f'☉ 太陽 {sign} {degree}（{house}ハウス）',
        'category': 'core',
        'sections': [
            {
                'subtitle': 'あなたの本質・人生の目的',
                'content': get_sun_sign_interpretation(sign)
            },
            {
                'subtitle': f'{house}ハウスでの太陽の意味',
                'content': get_sun_house_interpretation(house)
            },
            {
                'subtitle': '人生のテーマ',
                'content': get_sun_life_theme(sign, house)
            }
        ]
    }


def generate_moon_interpretation(chart, unknown_time):
    """月の包括的解釈"""
    moon = chart.moon
    sign = moon.sign_jp
    house = get_house_num(moon.house)
    degree = format_degree(moon.degree)
    
    sections = [
        {
            'subtitle': 'あなたの感情パターン・心の欲求',
            'content': get_moon_sign_interpretation(sign)
        }
    ]
    
    if not unknown_time:
        sections.append({
            'subtitle': f'{house}ハウスでの月の意味',
            'content': get_moon_house_interpretation(house)
        })
    
    sections.append({
        'subtitle': '感情的な安定に必要なこと',
        'content': get_moon_needs(sign)
    })
    
    return {
        'title': f'☽ 月 {sign} {degree}' + (f'（{house}ハウス）' if not unknown_time else ''),
        'category': 'core',
        'sections': sections
    }


def generate_ascendant_interpretation(chart, unknown_time):
    """アセンダントの包括的解釈"""
    if unknown_time:
        return {
            'title': '↑ アセンダント（出生時刻不明）',
            'category': 'core',
            'sections': [{
                'subtitle': '注意',
                'content': '出生時刻が不明のため、アセンダントとハウス配置は正確ではありません。正確な出生時刻がわかれば、より詳細な分析が可能になります。'
            }]
        }
    
    asc = chart.ascendant
    sign = asc['sign_jp']
    degree = format_degree(asc['degree'])
    
    return {
        'title': f'↑ アセンダント {sign} {degree}',
        'category': 'core',
        'sections': [
            {
                'subtitle': 'あなたの第一印象・外見',
                'content': get_asc_interpretation(sign)
            },
            {
                'subtitle': '人生のアプローチ方法',
                'content': get_asc_life_approach(sign)
            }
        ]
    }


def generate_planet_interpretation(planet, unknown_time):
    """個人惑星の包括的解釈"""
    name = PLANET_JP.get(planet.name, planet.name)
    symbol = PLANET_SYMBOLS.get(planet.name, '')
    sign = planet.sign_jp
    house = get_house_num(planet.house)
    degree = format_degree(planet.degree)
    retrograde = getattr(planet, 'retrograde', False)
    
    r_mark = ' (R)' if retrograde else ''
    
    sections = [
        {
            'subtitle': f'{sign}での{name}の働き',
            'content': get_planet_sign_interpretation(planet.name, sign)
        }
    ]
    
    if not unknown_time:
        sections.append({
            'subtitle': f'{house}ハウスでの{name}',
            'content': get_planet_house_interpretation(planet.name, house)
        })
    
    if retrograde:
        sections.append({
            'subtitle': '逆行の影響',
            'content': get_retrograde_interpretation(planet.name)
        })
    
    return {
        'title': f'{symbol} {name} {sign} {degree}{r_mark}' + (f'（{house}ハウス）' if not unknown_time else ''),
        'category': 'personal' if planet.name in ['Mercury', 'Venus', 'Mars'] else 'social',
        'sections': sections
    }


def generate_outer_planet_interpretation(planet):
    """外惑星の解釈（世代的影響）"""
    name = PLANET_JP.get(planet.name, planet.name)
    symbol = PLANET_SYMBOLS.get(planet.name, '')
    sign = planet.sign_jp
    degree = format_degree(planet.degree)
    
    return {
        'title': f'{symbol} {name} {sign} {degree}',
        'category': 'outer',
        'sections': [
            {
                'subtitle': '世代的テーマ',
                'content': get_outer_planet_interpretation_text(planet.name, sign)
            }
        ]
    }


# ========== 詳細解釈テキスト ==========

def get_sun_sign_interpretation(sign):
    """太陽星座の詳細解釈"""
    interps = {
        '牡羊座': '''あなたの魂の本質は「開拓者」「戦士」です。

生まれながらにして、誰も踏み入れたことのない領域に飛び込む勇気を持っています。「一番になりたい」「新しいことを始めたい」という欲求があなたを駆り立てます。

【強み】
・ 決断力と行動力が抜群
・ 困難な状況でも前に進める勇気
・ リーダーシップを自然に発揮
・ 直感的な判断力

【注意点】
・ せっかちになりすぎて周囲を置いていく
・ 忍耐が必要な場面で投げ出しやすい
・ 衝動的な行動で後悔することも

【人生の目的】
新しい道を切り開き、他の人が続ける道を作ること。行動で世界を変えていくことがあなたの使命です。''',

        '牡牛座': '''あなたの魂の本質は「創造者」「職人」です。

五感を通じて世界を深く味わい、本物の価値を見抜く審美眼を持っています。一度始めたことは最後までやり遂げる粘り強さがあり、周囲からの信頼は絶大です。

【強み】
・ 驚異的な持続力と忍耐力
・ 本物を見抜く審美眼
・ 実用的で現実的な判断力
・ 危機に動じない安定感

【注意点】
・ 変化を恐れて動けなくなることも
・ 執着心が強くなりすぎる
・ 物質的なことへのこだわり

【人生の目的】
価値あるものを創造し、長期的に育てていくこと。あなたが作ったものは時の試練に耐えます。''',

        '双子座': '''あなたの魂の本質は「伝達者」「メッセンジャー」です。

情報を収集し、人と人をつなぐ橋渡し役を担います。一つのことに縛られるのが苦手で、常に複数のことを同時進行することで輝きます。知的好奇心の塊です。

【強み】
・ 情報収集と分析の達人
・ コミュニケーション能力が抜群
・ 柔軟な思考と適応力
・ 飽きることなく学び続ける

【注意点】
・ 一つのことを深掘りするのが苦手
・ 落ち着きがなく見られることも
・ 二面性を疑われることがある

【人生の目的】
知識を広め、人々をつなぐこと。あなたの言葉が世界を動かします。''',

        '蟹座': '''あなたの魂の本質は「養育者」「守護者」です。

大切な人を守り育てることに深い使命感を持っています。感受性が非常に豊かで、他者の痛みを自分のことのように感じ取ります。

【強み】
・ 深い共感力と直感力
・ 人を育てる才能
・ 記憶力が優れている
・ 危険を察知する本能

【注意点】
・ 過去への執着が強くなりやすい
・ 感情に振り回されることも
・ 過保護になりすぎる

【人生の目的】
安全な居場所を作り、人を守り育てること。あなたの存在が誰かの「帰る場所」になります。''',

        '獅子座': '''あなたの魂の本質は「王/女王」「創造主」です。

生まれながらにして人の中心に立つ資質を持ち、自らの光で周囲を照らします。創造性と自己表現への欲求が強く、ドラマティックな人生を歩みます。

【強み】
・ 圧倒的なカリスマ性と存在感
・ 創造性と表現力
・ 寛大さと温かい心
・ リーダーシップ

【注意点】
・ プライドが高すぎることも
・ 注目されないと落ち込む
・ 批判に敏感

【人生の目的】
自分の光で人を照らし、勇気を与えること。あなたが輝くことで、周囲も輝きます。''',

        '乙女座': '''あなたの魂の本質は「奉仕者」「完璧主義者」です。

細部まで気を配り、物事を完璧に仕上げる能力を持っています。健康や実用性に関心が高く、日常生活を向上させることに喜びを見出します。

【強み】
・ 驚異的な分析力と観察力
・ 実務能力が抜群
・ 改善と最適化の達人
・ 謙虚で誠実

【注意点】
・ 完璧を求めすぎて苦しむ
・ 批判的になりすぎる
・ 心配性

【人生の目的】
物事をより良くし、人の役に立つこと。あなたの細かい配慮が世界を動かします。''',

        '天秤座': '''あなたの魂の本質は「調停者」「外交官」です。

美とバランスを追求し、人間関係における調和を大切にします。他者の視点を理解する能力に優れ、公平な判断ができます。

【強み】
・ 優れた外交能力と交渉力
・ 美的センスが抜群
・ 公平で客観的な視点
・ 人間関係を円滑にする才能

【注意点】
・ 決断を先延ばしにしがち
・ 対立を避けすぎる
・ 人に合わせすぎて自分を見失う

【人生の目的】
人々の間に調和をもたらし、美を創造すること。あなたがいることで世界は平和になります。''',

        '蠍座': '''あなたの魂の本質は「変容者」「探求者」です。

表面的なことに満足せず、物事の本質を見抜こうとします。一度コミットしたら徹底的に取り組む集中力と、危機を乗り越えて再生する力を持っています。

【強み】
・ 驚異的な集中力と執念
・ 本質を見抜く洞察力
・ 心理学的な理解力
・ 危機からの再生力

【注意点】
・ 執着心が強すぎる
・ 秘密主義になりやすい
・ 信頼するまで時間がかかる

【人生の目的】
深い変容を経験し、その知恵を伝えること。あなたは人生の深淵を知り、光を見つける人です。''',

        '射手座': '''あなたの魂の本質は「探求者」「哲学者」です。

真理と自由を求めて人生という冒険を進みます。視野が広く、異なる文化や思想に興味を持ちます。

【強み】
・ 楽観主義と希望を失わない力
・ 哲学的な視点
・ 冒険心と探求心
・ インスピレーションを与える力

【注意点】
・ 詳細を見落としがち
・ 約束を軽く考えることも
・ 落ち着きがない

【人生の目的】
人生の意味を探求し、その知恵を広めること。あなたの冒険が他の人に希望を与えます。''',

        '山羊座': '''あなたの魂の本質は「建設者」「達成者」です。

長期的なビジョンを持ち、着実に成功への階段を登ります。責任感が強く、社会的な達成を重要視します。

【強み】
・ 驚異的な忍耐力と持続力
・ 現実的な計画能力
・ 権威を獲得する力
・ 自己規律

【注意点】
・ 仕事中毒になりやすい
・ 感情を抑圧しがち
・ 楽しむことを忘れる

【人生の目的】
時間をかけて偉大なものを築くこと。あなたの業績は何世代にも残ります。''',

        '水瓶座': '''あなたの魂の本質は「革命家」「ヴィジョナリー」です。

既存のルールに縛られず、より良い未来のための新しいシステムを追求します。人道主義的な理想を持ち、個性と自由を大切にします。

【強み】
・ 独創的な発想力
・ 平等と公正への強いコミットメント
・ グループを導く能力
・ 未来を見通す力

【注意点】
・ 感情的なつながりが苦手
・ 頑固になりやすい
・ 「普通」を軽視しすぎる

【人生の目的】
社会を進化させる新しいアイデアを生み出すこと。あなたは時代を先取りする人です。''',

        '魚座': '''あなたの魂の本質は「夢見人」「癒し手」です。

現実と夢の境界を自在に行き来し、芸術的・霊的な感性が豊かです。すべての存在とのつながりを感じ、深い共感力を持っています。

【強み】
・ 深い共感力と直感力
・ 芸術的な創造性
・ 癒しの力
・ スピリチュアルな感受性

【注意点】
・ 現実逃避しやすい
・ 境界線があいまい
・ 人の感情を吸収しすぎる

【人生の目的】
見えない世界とつながり、癒しと美を世界にもたらすこと。あなたの存在自体が癒しです。'''
    }
    return interps.get(sign, f'{sign}の太陽は、独自の方法で人生を歩みます。')


def get_sun_house_interpretation(house):
    """太陽のハウス位置の解釈"""
    interps = {
        1: '1ハウスの太陽は、強いアイデンティティと自己表現力を示します。あなたは「自分自身」として生きることにエネルギーを注ぎ、存在感があります。リーダーシップを自然に発揮し、周囲に影響を与えます。ただ存在するだけで注目を集める力があります。',
        2: '2ハウスの太陽は、物質的な安定と自己価値を重視します。お金を稼ぐことや所有物に対して強い関心があり、自分の力で財を築く才能を持っています。自分の価値を認められることが人生の重要なテーマです。',
        3: '3ハウスの太陽は、コミュニケーションと知的活動で輝きます。話すこと、書くこと、教えることに才能があり、情報を扱う仕事で成功しやすいです。兄弟姉妹との関係も人生の重要なテーマになります。',
        4: '4ハウスの太陽は、家庭と家族が人生の中心です。ルーツや伝統を大切にし、安心できる居場所を築くことに力を注ぎます。晩年に輝く傾向があり、家族の中心人物になることが多いです。',
        5: '5ハウスの太陽は、創造性と自己表現で輝きます。芸術、趣味、恋愛、子供に関することで喜びを見出します。人生を楽しむ才能があり、遊び心を忘れません。注目されることで力を発揮します。',
        6: '6ハウスの太陽は、仕事と健康に焦点を当てます。日々のルーティンを通じて自己を表現し、人の役に立つことに喜びを感じます。健康的な生活習慣を確立することも重要なテーマです。',
        7: '7ハウスの太陽は、パートナーシップを通じて輝きます。1対1の関係性があなたのアイデンティティに大きく影響し、結婚や重要な契約関係が人生のテーマになります。他者と協力することで最高の自分を発揮できます。',
        8: '8ハウスの太陽は、深い変容と再生に関わります。心理学、オカルト、投資など、タブーとされる領域に興味があります。人生の危機を乗り越えて何度も再生する力を持っています。',
        9: '9ハウスの太陽は、哲学と冒険で輝きます。高等教育、海外旅行、宗教、法律に強い関心があり、人生の意味を探求することがテーマです。教育者や出版に関わる才能があります。',
        10: '10ハウスの太陽は、キャリアと社会的地位で輝きます。仕事での成功と社会的な認知を強く求め、権威的な立場に立つ可能性が高いです。公的な顔として知られることが運命づけられています。',
        11: '11ハウスの太陽は、グループと理想で輝きます。友人関係、組織活動、社会的理想の追求が人生のテーマです。未来志向で革新的な考え方を持ち、同じ志を持つ仲間と共に活動することで力を発揮します。',
        12: '12ハウスの太陽は、霊的な成長と無意識の探求に関わります。舞台裏で働くことが得意で、表に出ない形での大きな影響力を持っています。瞑想、芸術、奉仕活動を通じて輝きます。'
    }
    return interps.get(house, '')


def get_sun_life_theme(sign, house):
    """太陽星座とハウスから人生テーマを導出"""
    return f'''あなたの人生全体のテーマは、{sign}的な資質を{house}ハウスの領域で発揮することです。

これは単なる性格ではなく、あなたの魂が今世で達成したいと願っていることです。この方向に進むとき、あなたは最も輝き、充実感を感じるでしょう。

逆に、この方向から外れると、「何か違う」という違和感を感じることがあります。それはあなたの魂が本来の道に戻るよう促しているサインです。'''


def get_moon_sign_interpretation(sign):
    """月星座の詳細解釈"""
    # 簡略化のため代表的な解釈のみ
    return f'''{sign}に月があるあなたの感情パターンは、この星座の特性に深く影響されています。

月は「心の欲求」「感情の反応パターン」「安心感を得る方法」を示します。意識的に選ぶわけではなく、自然と体が反応する部分です。

幼少期の環境や母親との関係がこのパターンを形成しました。'''


def get_moon_house_interpretation(house):
    """月のハウス位置の解釈"""
    info = get_house_meaning(house)
    return f'''{house}ハウスに月があることで、感情的なエネルギーが「{info["title"]}」の領域に向かいます。

{info["detail"]}

この領域での体験があなたの感情に強く影響し、ここで安心感を得ることができます。'''


def get_moon_needs(sign):
    """月星座の感情的ニーズ"""
    return f'''{sign}月のあなたが感情的に安定するために必要なことは、この星座の根本的な欲求を満たすことです。

これは「贅沢」ではなく「必要不可欠」なものとして理解してください。この欲求を無視すると、心身のバランスを崩しやすくなります。'''


def get_asc_interpretation(sign):
    """アセンダント星座の解釈"""
    return f'''初対面であなたは{sign}的な印象を与えます。これは意識的に演じているわけではなく、自然と外に現れるあなたの「ペルソナ」です。

この星座の特徴があなたの外見、話し方、雰囲気に現れています。'''


def get_asc_life_approach(sign):
    """アセンダント星座の人生アプローチ"""
    return f'''あなたは人生を{sign}的なアプローチで歩みます。新しい状況に直面したとき、この星座のエネルギーが最初に反応します。

これはあなたの「デフォルト設定」であり、意識せずとも発動する行動パターンです。'''


def get_planet_sign_interpretation(planet, sign):
    """惑星×星座の解釈"""
    return f'''このあなたの{PLANET_JP.get(planet, planet)}は{sign}で働いています。

{planet}のエネルギーが{sign}のスタイルで表現されます。'''


def get_planet_house_interpretation(planet, house):
    """惑星×ハウスの解釈"""
    info = get_house_meaning(house)
    return f'''{house}ハウス（{info["title"]}の領域）に{PLANET_JP.get(planet, planet)}があります。

{info["detail"]}

この領域で{PLANET_JP.get(planet, planet)}のエネルギーが活性化し、この分野であなたの才能が発揮されます。'''


def get_retrograde_interpretation(planet):
    """逆行惑星の解釈"""
    return f'''{PLANET_JP.get(planet, planet)}が逆行しています。

逆行は「内向き」のエネルギーを表します。外に向かって発揮されるべきエネルギーが内省的に働き、深い洞察を与える一方で、外界での表現に時間がかかることがあります。

これは欠点ではなく、内面を豊かにするための特別な配置です。'''


def get_outer_planet_interpretation_text(planet, sign):
    """外惑星の世代的解釈"""
    return f'''これは世代的な配置です。同世代の多くの人が{PLANET_JP.get(planet, planet)}を{sign}に持っています。

この配置は個人の性格というより、あなたの世代全体が共有するテーマを表しています。'''
