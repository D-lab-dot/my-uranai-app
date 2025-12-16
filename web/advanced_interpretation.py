"""
Advanced Horoscope Interpretation Module
Gemini-level deep analysis system
"""

from datetime import datetime
from collections import Counter

# 星座のエレメント・クオリティ分類
ELEMENTS = {
    '牡羊座': '火', '獅子座': '火', '射手座': '火',
    '牡牛座': '地', '乙女座': '地', '山羊座': '地',
    '双子座': '風', '天秤座': '風', '水瓶座': '風',
    '蟹座': '水', '蠍座': '水', '魚座': '水'
}

QUALITIES = {
    '牡羊座': '活動', '蟹座': '活動', '天秤座': '活動', '山羊座': '活動',
    '牡牛座': '不動', '獅子座': '不動', '蠍座': '不動', '水瓶座': '不動',
    '双子座': '柔軟', '乙女座': '柔軟', '射手座': '柔軟', '魚座': '柔軟'
}

# ハウスルーラー
HOUSE_RULERS = {
    '牡羊座': '火星', '牡牛座': '金星', '双子座': '水星', '蟹座': '月',
    '獅子座': '太陽', '乙女座': '水星', '天秤座': '金星', '蠍座': '冥王星/火星',
    '射手座': '木星', '山羊座': '土星', '水瓶座': '天王星/土星', '魚座': '海王星/木星'
}

# ハウスの意味
HOUSE_THEMES = {
    '1': ('自己・アイデンティティ・外見', 'your identity and how others see you'),
    '2': ('財産・価値観・収入', 'your resources and values'),
    '3': ('コミュニケーション・知性・兄弟', 'communication and learning'),
    '4': ('家庭・ルーツ・心の基盤', 'home, family and emotional foundation'),
    '5': ('創造性・恋愛・子供・趣味', 'creativity, romance and self-expression'),
    '6': ('仕事・健康・日常・奉仕', 'work, health and daily routines'),
    '7': ('パートナーシップ・結婚・契約', 'partnerships and marriage'),
    '8': ('変容・共有財産・深層心理・タブー', 'transformation, shared resources, and deep psychology'),
    '9': ('哲学・海外・高等教育・旅行', 'philosophy, travel and higher learning'),
    '10': ('キャリア・社会的地位・天職', 'career and public image'),
    '11': ('友人・グループ・理想・未来', 'friends, groups and aspirations'),
    '12': ('無意識・隠れた領域・霊性・癒し', 'the unconscious, spirituality and hidden matters')
}

# ハウス番号変換（英語 → 数字）
HOUSE_NAME_TO_NUM = {
    'First_House': '1', 'Second_House': '2', 'Third_House': '3',
    'Fourth_House': '4', 'Fifth_House': '5', 'Sixth_House': '6',
    'Seventh_House': '7', 'Eighth_House': '8', 'Ninth_House': '9',
    'Tenth_House': '10', 'Eleventh_House': '11', 'Twelfth_House': '12',
    '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6',
    '7': '7', '8': '8', '9': '9', '10': '10', '11': '11', '12': '12'
}

# 初心者向けハウス説明（日常生活に即した説明）
HOUSE_BEGINNER = {
    '1': {
        'name': '1ハウス（自分自身の部屋）',
        'simple': '第一印象・見た目・性格の表れ方',
        'detail': 'これは「あなた自身」を表す部屋です。初対面の人があなたを見たときに受ける印象、外見的な特徴、無意識に出る振る舞い方がここに現れます。自撮りした時の雰囲気、自己紹介の仕方、歩き方や話し方のクセなど、「あなたらしさ」のすべてがここにあります。'
    },
    '2': {
        'name': '2ハウス（お金と価値観の部屋）',
        'simple': '収入・お金の稼ぎ方・大切にしているもの',
        'detail': '「自分の力で稼ぐお金」と「何を価値あると感じるか」を表す部屋です。給料の金額だけでなく、お金に対する態度、買い物の仕方、自分にとって「これだけは譲れない」と思うものがここに現れます。貯金が得意か浪費しがちかもわかります。'
    },
    '3': {
        'name': '3ハウス（コミュニケーションの部屋）',
        'simple': '日常会話・学習・兄弟姉妹・近所付き合い',
        'detail': 'LINEの返し方、雑談のスタイル、勉強の仕方がここでわかります。また、兄弟姉妹との関係、近所の人との付き合い方、電車で隣に座った人との距離感なども表します。頭の回転の速さや、情報収集の得意不得意もここに出ます。'
    },
    '4': {
        'name': '4ハウス（家庭とルーツの部屋）',
        'simple': '家族・実家・心の拠り所・老後',
        'detail': '「帰る場所」としての家庭を表します。実家との関係、どんな家に住みたいか、家族に対してどう接するか。また、あなたの心の奥底にある安心感の源もここにあります。人生の終盤（老後）をどう過ごすかのヒントもここから読み取れます。'
    },
    '5': {
        'name': '5ハウス（楽しみと創造性の部屋）',
        'simple': '恋愛・趣味・遊び・子供・自己表現',
        'detail': 'デートでどこに行きたいか、休日の過ごし方、推し活への熱量がここでわかります。恋愛のスタイル（追いたいか追われたいか）、創作活動への情熱、子供との関係性もここに表れます。人生を楽しむ力、ワクワクする方向性がここにあります。'
    },
    '6': {
        'name': '6ハウス（仕事と健康の部屋）',
        'simple': '日々の仕事・ルーティン・健康管理・ペット',
        'detail': '毎日の仕事への取り組み方、職場での立ち回り、健康状態や病気になりやすい部位がここでわかります。ダイエット方法が向いているか、どんなペットと相性がいいかも。「華やかな成功」ではなく「日々のコツコツした積み重ね」を表す部屋です。'
    },
    '7': {
        'name': '7ハウス（パートナーシップの部屋）',
        'simple': '結婚相手・ビジネスパートナー・契約関係',
        'detail': 'どんな人と結婚するか、恋人や配偶者に求めるもの、ビジネスパートナーとの関係性がここに現れます。「自分に足りないもの」を持つ相手に惹かれる傾向があり、ここを見れば理想のパートナー像がわかります。敵対する相手の特徴もここに出ます。'
    },
    '8': {
        'name': '8ハウス（変容と深い絆の部屋）',
        'simple': '遺産・共有財産・性・死と再生・心理的変容',
        'detail': '人生を根底から変える深い体験を表します。遺産や相続、パートナーの収入、性的な親密さ、心理的なトラウマと回復。「一度死んで生まれ変わる」ような人生の転換点がここに示されます。投資やローンなど「他者のお金」もこの部屋のテーマです。'
    },
    '9': {
        'name': '9ハウス（探求と冒険の部屋）',
        'simple': '海外・大学・哲学・宗教・長期旅行・出版',
        'detail': '「より広い世界を知りたい」という欲求を表します。海外旅行や留学への関心、大学や大学院での学び、宗教や哲学への傾向がここに。人生の意味を探し求める姿勢、本を書いたり教えたりする適性もわかります。視野を広げる冒険の部屋です。'
    },
    '10': {
        'name': '10ハウス（キャリアと社会的地位の部屋）',
        'simple': '天職・社会的な成功・評判・肩書き',
        'detail': 'LinkedInのプロフィールに書くような「社会的な自分」がここにあります。どんな仕事で成功するか、どんな肩書きを得るか、世間からどう評価されるか。「有名になる」「権威を持つ」などの社会的達成もこの部屋のテーマです。父親像もここに現れます。'
    },
    '11': {
        'name': '11ハウス（友人と理想の部屋）',
        'simple': '友人関係・コミュニティ・将来の夢・SNS',
        'detail': 'どんな友達グループに属するか、オンラインコミュニティでの立ち位置、未来への希望がここに。「社会をこう変えたい」という理想主義的な願望や、同じ志を持つ仲間との絆もこの部屋のテーマ。推しのファンコミュニティでの居場所もここでわかります。'
    },
    '12': {
        'name': '12ハウス（無意識と秘密の部屋）',
        'simple': '隠れた自分・スピリチュアル・入院・秘密・癒し',
        'detail': '表に出さない「もう一人の自分」がここにいます。無意識の行動パターン、夢の中で見る世界、スピリチュアルな感受性。病院や刑務所など「隔離された場所」、誰にも言えない秘密、人を陰から支える役割もこの部屋のテーマです。アーティストの創造性の源泉でもあります。'
    }
}

def get_house_num(house_str):
    """ハウス名から数字を取得"""
    house_str = str(house_str).strip()
    for key, val in HOUSE_NAME_TO_NUM.items():
        if key in house_str:
            return val
    # 数字だけ抽出
    import re
    nums = re.findall(r'\d+', house_str)
    return nums[0] if nums else '1'




def generate_advanced_interpretation(chart, birth_year, unknown_time=False):
    """Gemini-level advanced horoscope interpretation"""
    
    # 基本データ収集
    sun_sign = chart.sun.sign_jp
    sun_house = get_house_num(str(chart.sun.house))
    moon_sign = chart.moon.sign_jp
    moon_house = get_house_num(str(chart.moon.house))
    asc_sign = chart.ascendant['sign_jp']
    mc_sign = chart.midheaven['sign_jp']
    
    planets = {p.name: p for p in chart.planets}
    
    # 詳細分析を生成
    analysis = {
        'core_engine': generate_core_engine(sun_sign, sun_house, moon_sign, moon_house, 
                                             asc_sign, mc_sign, planets, unknown_time),
        'life_phases': generate_life_phases(birth_year, sun_sign, moon_sign, planets),
        'decade_cycles': generate_decade_cycles(birth_year, sun_sign, moon_sign, asc_sign, planets),
        'marriage_money': generate_marriage_money_analysis(planets, asc_sign, mc_sign),
        'strategic_advice': generate_strategic_advice(sun_sign, sun_house, moon_sign, moon_house, 
                                                       asc_sign, planets),
        'meta_cognition': generate_meta_cognition(sun_sign, moon_sign, asc_sign, planets)
    }
    
    return analysis


def generate_core_engine(sun_sign, sun_house, moon_sign, moon_house, asc_sign, mc_sign, planets, unknown_time):
    """チャートの本質的構造を分析"""
    
    sections = []
    
    # 1. 主人公分析（太陽・ASC）
    protagonist = analyze_protagonist(sun_sign, sun_house, asc_sign, unknown_time)
    sections.append(protagonist)
    
    # 2. 感情・内面分析（月・土星）
    emotional_core = analyze_emotional_core(moon_sign, moon_house, planets, unknown_time)
    sections.append(emotional_core)
    
    # 3. 知性・コミュニケーション（水星・金星）
    intel_style = analyze_intellect_style(planets)
    sections.append(intel_style)
    
    # 4. パターン検出
    patterns = detect_chart_patterns(sun_sign, moon_sign, asc_sign, planets)
    if patterns:
        sections.append(patterns)
    
    return sections


def analyze_protagonist(sun_sign, sun_house, asc_sign, unknown_time):
    """主人公（太陽・ASC）の分析"""
    
    title = "絶対的な主人公"
    
    # ダブルサイン検出
    if sun_sign == asc_sign:
        archetype = f"「ダブル・{sun_sign.replace('座', '')}」"
        desc = f"""上昇宮（見た目・第一印象）と太陽（本質）が共に{sun_sign}にあります。
これは{_get_sign_essence(sun_sign)}というエネルギーが二重に強調される配置です。"""
    else:
        archetype = f"「{_get_sign_archetype(sun_sign)}」の魂と「{_get_sign_archetype(asc_sign)}」の仮面"
        desc = f"""太陽{sun_sign}の本質を、{asc_sign}のペルソナで表現します。
内面では{_get_sign_drive(sun_sign)}一方、外見や第一印象は{_get_sign_impression(asc_sign)}"""
    
    # ハウス分析（詳細版に更新）
    sh_num = get_house_num(sun_house)
    house_info = HOUSE_BEGINNER.get(sh_num, {})
    
    if not unknown_time:
        house_meaning = f"""【太陽の輝く場所：{house_info.get('name', f'{sh_num}ハウス')}】
{house_info.get('detail', '')}

あなたの人生のメインテーマはこの領域にあります。ここで輝くことが、あなたにとっての「成功」です。"""
    else:
        house_meaning = "（出生時刻不明のため、ハウス配置は参考値です）"
    
    return {
        'title': title,
        'icon': '☉',
        'archetype': archetype,
        'description': desc,
        'house_meaning': house_meaning
    }


def analyze_emotional_core(moon_sign, moon_house, planets, unknown_time):
    """感情の核（月）の分析"""
    
    saturn = planets.get('Saturn')
    pluto = planets.get('Pluto')
    
    title = "深層の感情パターン"
    
    # 月の基本解釈
    moon_desc = f"""【本来の心】
{_get_moon_deep_meaning(moon_sign)}"""
    
    # 月のハウス（詳細版に更新）
    mh_num = get_house_num(moon_house)
    house_info = HOUSE_BEGINNER.get(mh_num, {})
    
    if not unknown_time:
        house_context = f"""
【心が安らぐ場所：{house_info.get('name', f'{mh_num}ハウス')}】
{house_info.get('detail', '')}

この領域で感情が満たされると、人生全体の満足度が上がります。"""
    else:
        house_context = ""
    
    # 土星との関係
    saturn_influence = ""
    if saturn and saturn.sign_jp == moon_sign:
        saturn_influence = "\n⚠️ 月と土星が同じ星座にあり、自分に厳しくなりがちです。感情を抑え込まず、時には甘やかすことも大切です。"
    
    # 冥王星との関係
    pluto_influence = ""
    if pluto:
        pluto_influence = "\n🔥 冥王星の影響により、感情の回復力が非常に高いです。辛い経験も糧にして強く生きる力を持っています。"
    
    return {
        'title': title,
        'icon': '☽',
        'archetype': f"「{_get_moon_archetype(moon_sign)}」",
        'description': moon_desc,
        'house_context': house_context,
        'saturn_influence': saturn_influence,
        'pluto_influence': pluto_influence
    }


def analyze_intellect_style(planets):
    """知性とコミュニケーションスタイル（微調整）"""
    
    mercury = planets.get('Mercury')
    venus = planets.get('Venus')
    
    if not mercury:
        return None
    
    merc_sign = mercury.sign_jp
    merc_house_raw = str(mercury.house)
    merc_house = get_house_num(merc_house_raw)
    house_info = HOUSE_BEGINNER.get(merc_house, {})
    
    title = "知性とコミュニケーション"
    
    # 詳細な水星の説明
    desc = f"""水星が{merc_sign}にあるあなたは、{_get_mercury_style(merc_sign)}

【あなたの思考パターン】
{_get_mercury_detailed_style(merc_sign)}"""
    
    # ハウス位置の詳細な説明
    house_name = house_info.get('name', f'{merc_house}ハウス')
    house_simple = house_info.get('simple', '')
    house_detail = house_info.get('detail', '')
    
    house_meaning = f"""【知性の発揮場所：{house_name}】
{house_detail}

{_get_mercury_house_advice(merc_house)}"""
    
    venus_note = ""
    if venus:
        v_house = get_house_num(str(venus.house))
        v_info = HOUSE_BEGINNER.get(v_house, {})
        venus_note = f"""
【愛と喜びの場所：{v_info.get('name', f'{v_house}ハウス')}】
{v_info.get('detail', '')}"""
    
    return {
        'title': title,
        'icon': '☿',
        'archetype': f"「{_get_mercury_archetype(merc_sign)}」",
        'description': desc,
        'house_meaning': house_meaning,
        'venus_note': venus_note
    }


def detect_chart_patterns(sun_sign, moon_sign, asc_sign, planets):
    """チャートパターンを検出（わかりやすい言葉に修正）"""
    
    patterns = []
    
    # エレメント集中
    signs = [sun_sign, moon_sign, asc_sign]
    for p in planets.values():
        signs.append(p.sign_jp)
    
    element_map = {'火': '情熱', '地': '堅実', '風': '知性', '水': '感情'}
    element_count = Counter([ELEMENTS.get(s, '') for s in signs])
    dominant_element = element_count.most_common(1)[0] if element_count else None
    
    if dominant_element and dominant_element[1] >= 4:
        elem_name = dominant_element[0]
        friendly_name = element_map.get(elem_name, elem_name)
        desc = ""
        if elem_name == '火':
            desc = "「直感と情熱」の人です。思い立ったら即行動するエネルギーに溢れています。"
        elif elem_name == '地':
            desc = "「現実と安定」の人です。着実に結果を出し、形にする力を持っています。"
        elif elem_name == '風':
            desc = "「拡散と論理」の人です。情報や人とのつながりを何より大切にします。"
        elif elem_name == '水':
            desc = "「共感と融合」の人です。人の気持ちに寄り添う優しい心を持っています。"
            
        patterns.append(f"🔥 **{friendly_name}タイプ（{elem_name}の過多）**\n{desc}")
    
    # ハウス集中（ステリウム）検出
    house_count = Counter()
    for p in planets.values():
        h = get_house_num(str(p.house))
        house_count[h] += 1
    
    for house, count in house_count.items():
        if count >= 3:
            h_info = HOUSE_BEGINNER.get(house, {})
            h_name = h_info.get('name', f'{house}ハウス')
            h_simple = h_info.get('simple', '特定の分野')
            patterns.append(f"⭐ **エネルギー集中エリア：{h_simple}**\n（{h_name}）\n\n多くの惑星がこの領域に集まっています。これは、あなたの人生において「{h_simple}」が極めて重要なテーマであることを示しています。良くも悪くも、この分野でドラマが起きやすい運命にあります。")
    
    if patterns:
        return {
            'title': 'あなたの特別なパターン',
            'icon': '🔮',
            'patterns': patterns
        }
    
    return None


def generate_life_phases(birth_year, sun_sign, moon_sign, planets):
    """人生の変曲点を予測（わかりやすい説明版）"""
    
    current_year = datetime.now().year
    age = current_year - birth_year
    
    phases = []
    
    # 29歳前後の転換期（サターンリターンを平易に説明）
    first_return_age = 29
    first_return_year = birth_year + first_return_age
    second_return_year = birth_year + 58
    
    # 現在〜近未来の予測
    phases.append({
        'period': f'{current_year}年〜{current_year + 2}年（現在）',
        'title': '🌍 社会と自分の変革期',
        'description': '今、社会全体が大きく変わろうとしています。働き方、人間関係、価値観...これまでの「当たり前」が通用しなくなる時期です。あなた自身も、この流れの中で新しい生き方を模索しているかもしれません。',
        'advice': '「今までのやり方にしがみつく」のではなく、「新しい可能性を探る」姿勢が大切です。不安を感じても、それは成長のサインです。新しいスキルを学んだり、新しい人間関係を築いたりする良い時期です。'
    })
    
    # 29歳前後の転換期
    if age < 29:
        years_until = first_return_year - current_year
        phases.append({
            'period': f'{first_return_year}年〜{first_return_year + 2}年（{first_return_age}〜31歳）',
            'title': '🎓 人生の成人式（29歳前後の転換期）',
            'description': f'約{years_until}年後に訪れる、人生で最も重要な転換期の一つです。「本当にこの仕事でいいのか」「この人と人生を歩むべきか」「本当の自分は何がしたいのか」という問いと向き合うことになります。多くの人がこの時期に転職、結婚、離婚、引っ越しなど大きな決断をします。',
            'advice': 'この時期の決断は、その後の30年間を左右します。焦って決める必要はありませんが、「親や周囲が望むこと」ではなく「自分が本当に望むこと」を選ぶ勇気が必要です。苦しくても、逃げずに向き合ってください。'
        })
    elif 27 <= age <= 32:
        phases.append({
            'period': '現在進行中',
            'title': '🎓 人生の成人式（真っ只中！）',
            'description': '今まさに、人生の大きな転換期を迎えています。「このままでいいのか」という問いが頭を離れないかもしれません。仕事、人間関係、人生の方向性...すべてが問い直される時期です。',
            'advice': '今の苦しさは、「魂が成長しようとしているサイン」です。安易に逃げたり、楽な方に流れたりすると、後で後悔します。この時期を乗り越えると、本当の自分として生きる土台ができます。信頼できる人に相談しながら、自分の道を見つけてください。'
        })
    elif 56 <= age <= 62:
        phases.append({
            'period': '現在進行中',
            'title': '🏆 人生の第二幕（58歳前後の転換期）',
            'description': '人生の経験を総括し、次の30年をどう生きるか考える時期です。「本当に大切なものは何か」が明確になり、不要なものを手放す覚悟ができます。',
            'advice': 'これまでの人生で得た知恵を次世代に伝えることが、この時期の使命です。新しい挑戦を恐れないでください。'
        })
    
    # 30代後半〜40代の転換期
    mid_life_year = birth_year + 40
    if age < 40:
        phases.append({
            'period': f'{mid_life_year}年〜{mid_life_year + 3}年（39〜42歳）',
            'title': '👑 実力発揮の時（40歳前後の転換期）',
            'description': '「中年の危機」と呼ばれることもありますが、これは「これまで隠れていた才能が開花する時期」でもあります。20代・30代で積み上げた経験と実力が、ようやく社会に認められます。',
            'advice': '「もう若くない」と嘆くより、「経験に基づいた本物の力がある」と自信を持ってください。リーダーシップを発揮し、後進を育てる立場になる時期です。'
        })
    
    return phases



def generate_decade_cycles(birth_year, sun_sign, moon_sign, asc_sign, planets):
    """10年ごとの運気の流れ"""
    
    current_year = datetime.now().year
    age = current_year - birth_year
    
    cycles = []
    
    # 現在の10年
    current_decade_start = (age // 10) * 10
    current_decade_end = current_decade_start + 9
    
    if age < 30:
        cycles.append({
            'period': '20代後半：実力養成期',
            'theme': '「秘密裏の準備」と「基盤形成」',
            'description': '表立った派手な活動よりも、水面下でのスキルアップや資産形成が大きな実を結びます。この時期に培った「人に見せない努力」が、後の爆発的な成功の火薬になります。'
        })
    
    if age < 40:
        cycles.append({
            'period': '30代：力の行使と拡大',
            'theme': '「権力の掌握」と「視野の拡大」',
            'description': 'サターンリターンを終え、本当の自分として社会に出ていく時期。海外や高等教育との縁が強まり、手に入れた知識や洞察をより広い世界で試す時期になります。'
        })
    
    if age < 50:
        cycles.append({
            'period': '40代：収穫と表舞台',
            'theme': '「社会的成功」と「自己表現」',
            'description': 'これまでの「隠れた実力者」から、堂々たる「リーダー」として世に出る時期。カリスマ性が社会的に認知され、多くの人を惹きつけます。'
        })
    
    cycles.append({
        'period': '50代以降：知恵の伝達',
        'theme': '「メンター」と「レガシー」',
        'description': '蓄積した知識と経験を次世代に伝える時期。教育、執筆、コンサルティングなどで真価を発揮します。'
    })
    
    return cycles


def generate_marriage_money_analysis(planets, asc_sign, mc_sign):
    """結婚と金運の分析"""
    
    venus = planets.get('Venus')
    mars = planets.get('Mars')
    jupiter = planets.get('Jupiter')
    pluto = planets.get('Pluto')
    
    # 7ハウス（結婚）の分析
    # 簡易的にASCの対面星座を計算
    sign_order = ['牡羊座', '牡牛座', '双子座', '蟹座', '獅子座', '乙女座', 
                  '天秤座', '蠍座', '射手座', '山羊座', '水瓶座', '魚座']
    try:
        asc_idx = sign_order.index(asc_sign)
        descendant_sign = sign_order[(asc_idx + 6) % 12]
    except:
        descendant_sign = '天秤座'  # デフォルト
    
    marriage = {
        'title': '結婚・パートナーシップ',
        'partner_type': f'{descendant_sign}的な人を求めます。{_get_partner_description(descendant_sign)}',
        'style': _get_marriage_style(venus) if venus else '愛情深く誠実なパートナーシップを築きます。',
        'timing': _get_marriage_timing(jupiter) if jupiter else '木星が7ハウスや金星に好配置の時期に縁が深まります。'
    }
    
    # 金運分析（2ハウス・8ハウス）
    money = {
        'title': '金運・財運',
        'earning_style': _get_earning_style(pluto) if pluto else '着実に収入を築いていくタイプです。',
        'wealth_building': '8ハウスの影響により、投資やパートナーからの共有財産での利益が期待できます。',
        'peak_period': '30代中盤以降、木星が好配置になる時期に財運が最大化します。'
    }
    
    return {
        'marriage': marriage,
        'money': money
    }


def generate_strategic_advice(sun_sign, sun_house, moon_sign, moon_house, asc_sign, planets):
    """戦略的アドバイス - 強み・弱み・アクションを網羅"""
    
    strengths = []
    weaknesses = []
    actions = []
    
    # 1. 太陽星座に基づく強み
    strengths.append(_get_sign_strength(sun_sign))
    
    # 2. 太陽星座に基づく弱み（新規追加）
    weaknesses.append(_get_sign_weakness(sun_sign))
    
    # 3. ハウスに基づく活動領域と強み
    if sun_house in ['1', '10']:
        strengths.append("リーダーシップを発揮し、表舞台で輝く資質があります。人前に立つことで力が発揮されます。")
        actions.append("積極的に人前に出る機会を作ってください。プレゼン、講演、SNSでの発信などが効果的です。")
    elif sun_house in ['8', '12']:
        strengths.append("舞台裏での影響力と深い洞察力を持っています。見えないところで大きな力を発揮します。")
        actions.append("顔を出さない形での発信やオンラインビジネスで大きな成果が期待できます。")
    elif sun_house in ['2', '6']:
        strengths.append("実務能力と着実な積み上げ力があります。コツコツと成果を出すタイプです。")
        actions.append("毎日のルーティンを大切にし、小さな成功を積み重ねてください。")
    elif sun_house in ['3', '9']:
        strengths.append("学びと発信の才能があります。知識を広げ、それを伝えることで輝きます。")
        actions.append("ブログ、YouTube、書籍執筆など、知識を発信する活動を始めてください。")
    elif sun_house in ['4', '7']:
        strengths.append("人との関係構築に優れています。家族やパートナーとの絆が幸運を引き寄せます。")
        actions.append("大切な人との時間を優先し、人間関係に投資してください。")
    elif sun_house in ['5', '11']:
        strengths.append("創造性とコミュニティ形成の才能があります。楽しみながら成功を掴めます。")
        actions.append("趣味や創作活動を大切にし、同じ志を持つ仲間を見つけてください。")
    
    # 4. 月のハウス位置に基づく感情的課題
    moon_weaknesses = _get_moon_house_weakness(moon_house)
    if moon_weaknesses:
        weaknesses.append(moon_weaknesses)
    
    # 5. 月星座に基づく感情的アドバイス
    moon_action = _get_moon_sign_action(moon_sign)
    if moon_action:
        actions.append(moon_action)
    
    # 6. 各惑星のハウス配置に基づくアドバイス
    mercury = planets.get('Mercury')
    venus = planets.get('Venus')
    mars = planets.get('Mars')
    saturn = planets.get('Saturn')
    
    if mercury:
        m_house = get_house_num(str(mercury.house))
        if m_house == '12':
            actions.append("SNSで全てをさらけ出す必要はありません。匿名や半匿名での発信が向いています。")
        elif m_house == '3':
            actions.append("話す・書く・教えることで才能が開花します。情報発信を積極的に行ってください。")
        elif m_house == '10':
            actions.append("仕事上のコミュニケーションが評価されます。企画書やプレゼンに力を入れてください。")
    
    if venus:
        v_house = get_house_num(str(venus.house))
        if v_house == '12':
            actions.append("芸術・スピリチュアル・癒しの活動を副業的に始めると、思いがけない収入源になります。")
        elif v_house == '2':
            actions.append("美しいものや質の高いものへの投資が金運アップにつながります。")
        elif v_house == '7':
            actions.append("パートナーシップを通じて幸運が訪れます。良縁を大切にしてください。")
    
    if mars:
        m_house = get_house_num(str(mars.house))
        if m_house in ['1', '10']:
            actions.append("競争環境で力を発揮します。挑戦的な目標を設定し、積極的に行動してください。")
        elif m_house == '6':
            actions.append("日々の仕事への情熱が成功を引き寄せます。健康管理も重要です。")
    
    if saturn:
        s_house = get_house_num(str(saturn.house))
        saturn_weakness = _get_saturn_house_weakness(s_house)
        if saturn_weakness:
            weaknesses.append(saturn_weakness)
        saturn_action = _get_saturn_house_action(s_house)
        if saturn_action:
            actions.append(saturn_action)
    
    # 7. アーキタイプの決定
    archetype = _determine_archetype(sun_sign, sun_house, moon_sign, moon_house, planets)
    
    # 8. 総合まとめを生成
    summary = _generate_strategic_summary(sun_sign, moon_sign, asc_sign, sun_house, strengths, weaknesses)
    
    return {
        'archetype': archetype,
        'strengths': strengths,
        'weaknesses': weaknesses,
        'actions': actions,
        'summary': summary
    }



def generate_meta_cognition(sun_sign, moon_sign, asc_sign, planets):
    """メタ認知（チャートの本質）"""
    
    # 強調されているハウスを検出
    emphasized_houses = []
    for p in planets.values():
        h = get_house_num(str(p.house))
        emphasized_houses.append(h)
    
    house_count = Counter(emphasized_houses)
    
    # 本質を判定
    if '12' in emphasized_houses and '8' in emphasized_houses:
        essence = "「隠蔽と集中」"
        description = "エネルギーを外に漏らさず内側に溜め込み、臨界点を超えた時に爆発的な成果として具現化させる構造です。「沈黙は金」が文字通り通用するタイプです。"
    elif '1' in emphasized_houses or '10' in emphasized_houses:
        essence = "「表現と達成」"
        description = "自己を表に出し、社会的成功を収めることでエネルギーが循環する構造です。リーダーシップを発揮することで真価を発揮します。"
    elif '7' in emphasized_houses:
        essence = "「関係と調和」"
        description = "他者との関係を通じて自己を発見し成長する構造です。パートナーシップが人生の鍵を握ります。"
    else:
        essence = "「探求と成長」"
        description = "常に学び、成長し続けることでエネルギーが循環する構造です。"
    
    return {
        'essence': essence,
        'description': description
    }


# ========== ヘルパー関数 ==========

def _get_sign_essence(sign):
    essences = {
        '牡羊座': '開拓と自己主張', '牡牛座': '安定と美の追求', '双子座': '知性とコミュニケーション',
        '蟹座': '養育と感情的絆', '獅子座': '創造性と自己表現', '乙女座': '分析と奉仕',
        '天秤座': '調和とパートナーシップ', '蠍座': '変容と深い絆', '射手座': '探求と自由',
        '山羊座': '達成と責任', '水瓶座': '革新と人道主義', '魚座': '共感と霊性'
    }
    return essences.get(sign, sign)

def _get_sign_archetype(sign):
    archetypes = {
        '牡羊座': '戦士', '牡牛座': '創造者', '双子座': '伝達者', '蟹座': '養育者',
        '獅子座': '王者', '乙女座': '奉仕者', '天秤座': '調停者', '蠍座': '変容者',
        '射手座': '探求者', '山羊座': '建設者', '水瓶座': '革命家', '魚座': '夢見人'
    }
    return archetypes.get(sign, sign)

def _get_sign_drive(sign):
    drives = {
        '牡羊座': '常に新しいことに挑戦したい衝動があり、', 
        '牡牛座': '安定と心地よさを追求し、', 
        '双子座': '多様な情報と人との交流を求め、',
        '蟹座': '大切な人を守りたいという強い欲求があり、', 
        '獅子座': '自己表現と認知を求め、', 
        '乙女座': '完璧を追求し細部まで気を配り、',
        '天秤座': '調和とバランスを追求し、', 
        '蠍座': '深い真実と変容を求め、', 
        '射手座': '自由と冒険を求め、',
        '山羊座': '社会的達成を目指し、', 
        '水瓶座': '革新と独自性を追求し、', 
        '魚座': '精神的なつながりと癒しを求め、'
    }
    return drives.get(sign, '')

def _get_sign_impression(sign):
    impressions = {
        '牡羊座': 'エネルギッシュでダイナミックな印象を与えます。', 
        '牡牛座': '落ち着いて信頼感のある印象を与えます。', 
        '双子座': '知的で社交的な印象を与えます。',
        '蟹座': '親しみやすく温かい印象を与えます。', 
        '獅子座': '堂々として華やかな印象を与えます。', 
        '乙女座': '知的で清潔感のある印象を与えます。',
        '天秤座': '洗練されて魅力的な印象を与えます。', 
        '蠍座': 'ミステリアスで強烈な印象を与えます。', 
        '射手座': 'オープンで楽観的な印象を与えます。',
        '山羊座': '真面目で信頼できる印象を与えます。', 
        '水瓶座': '独特で知的な印象を与えます。', 
        '魚座': '神秘的で優しい印象を与えます。'
    }
    return impressions.get(sign, '')

def _get_moon_deep_meaning(sign):
    meanings = {
        '牡羊座': '感情が昂ると即座に行動に移す傾向があり、待つことが苦手です。自立した環境で最も安心を感じ、怒りは爆発的に出やすいですがすぐに収まります。',
        '牡牛座': '慣れ親しんだものに安心を感じ、変化には時間をかけて適応します。五感を満たすこと（美味しい食事、音楽、自然）が心のケアになります。',
        '双子座': '感情を言語化することで処理し、誰かに聞いてもらうことで落ち着きます。退屈が最大の敵で、知的刺激を常に求めます。感情の切り替えが早いです。',
        '蟹座': '家族や親しい人への愛着が非常に強く、別離に敏感です。過去の思い出を大切にし、感情の波が月のように周期的に変化します。',
        '獅子座': '認められることで生き生きとし、創造的活動で感情を発散します。プライドが高く批判に敏感ですが、基本的に寛大で温かい心を持っています。',
        '乙女座': '感情を分析的に処理し、問題解決で安心します。完璧主義的ですが、根は思いやりに溢れています。',
        '天秤座': 'パートナーがいることで安定し、対立を避けます。美的なものに囲まれていると心が落ち着きます。',
        '蠍座': '感情が非常に深く激しく、一度傷つくと長く記憶しています。信頼した相手には全身全霊で尽くしますが、裏切りは決して許しません。',
        '射手座': '楽観的で、未来に希望を持つことで安心します。束縛を嫌い、広い世界を探検することで感情が満たされます。',
        '山羊座': '感情を表に出すのが苦手で、自己コントロールを重視します。責任を果たすことで安心を得ますが、実は繊細な一面を隠しています。',
        '水瓶座': '感情的に客観的で、自分の感情を一歩引いて観察します。「普通」であることを嫌い、ユニークであることに誇りを持っています。',
        '魚座': '非常に敏感で、他者の感情を吸収してしまうことも。芸術や音楽、スピリチュアルな活動が心を癒します。'
    }
    return meanings.get(sign, '')

def _get_moon_archetype(sign):
    archetypes = {
        '牡羊座': '即断即決の独立心', '牡牛座': '安定を求める心', '双子座': '好奇心の塊',
        '蟹座': '守護者の心', '獅子座': '輝きを求める心', '乙女座': '完璧を求める心',
        '天秤座': '調和を求める心', '蠍座': '深淵の分析家', '射手座': '自由を求める心',
        '山羊座': '達成を求める心', '水瓶座': '独立独歩の心', '魚座': '共感の海'
    }
    return archetypes.get(sign, sign)

def _get_mercury_style(sign):
    styles = {
        '牡羊座': '素早く直感的に考え、議論に強いです。',
        '牡牛座': 'じっくり考え、実用的な結論を出します。',
        '双子座': '（本来の場所）多才で言葉巧み、学習能力が高いです。',
        '蟹座': '感情と記憶を結びつけて考えます。',
        '獅子座': '堂々と自信を持って表現します。',
        '乙女座': '（本来の場所）分析力が高く、細部に気づきます。',
        '天秤座': '公平に両面を見て判断します。',
        '蠍座': '本質を見抜く洞察力があります。',
        '射手座': '大きなビジョンで考え、哲学的です。',
        '山羊座': '論理的で実践的な思考をします。',
        '水瓶座': '革新的で独創的な発想をします。',
        '魚座': '直感的で創造的な思考をします。'
    }
    return styles.get(sign, '')

def _get_mercury_archetype(sign):
    archetypes = {
        '牡羊座': '即断の戦略家', '牡牛座': '実務の職人', '双子座': '情報の錬金術師',
        '蟹座': '記憶の語り部', '獅子座': '表現のアーティスト', '乙女座': '分析の達人',
        '天秤座': '交渉の名手', '蠍座': '真実の探求者', '射手座': '哲学者',
        '山羊座': 'ビジネスの頭脳', '水瓶座': '未来の設計者', '魚座': '直感の詩人'
    }
    return archetypes.get(sign, sign)

def _get_partner_description(sign):
    descriptions = {
        '牡羊座': 'エネルギッシュで自立した、チャレンジ精神のある人。',
        '牡牛座': '穏やかで五感が鋭く、経済的に安定している人。',
        '双子座': '知的で話が面白く、多趣味な人。',
        '蟹座': '家庭的で感情豊かな、守ってくれる人。',
        '獅子座': '華やかで自信に満ち、太陽のように輝く人。',
        '乙女座': '知的で几帳面、実務能力の高い人。',
        '天秤座': '洗練されていて社交的、バランス感覚のある人。',
        '蠍座': '深い絆を築ける、ミステリアスで情熱的な人。',
        '射手座': '冒険心があり、自由を愛する楽観的な人。',
        '山羊座': '責任感が強く、社会的に成功している人。',
        '水瓶座': '独特な視点を持ち、知的で革新的な人。',
        '魚座': '感受性豊かで、霊的なつながりを感じられる人。'
    }
    return descriptions.get(sign, '')

def _get_marriage_style(venus):
    if not venus:
        return ''
    
    # ハウス番号を正確に取得
    v_house = get_house_num(str(venus.house))
    
    # ハウス情報を取得
    h_info = HOUSE_BEGINNER.get(v_house, {})
    h_name = h_info.get('name', f'{v_house}ハウス')
    h_detail = h_info.get('detail', '')
    
    return f"""金星が{h_name}にあります。
{h_detail}

この領域での経験が、あなたの恋愛観やパートナーシップの形を決定づけます。「どのような人と結ばれるか」だけでなく、「どのような状況で愛が育まれるか」もここから読み取れます。"""

def _get_marriage_timing(jupiter):
    return '木星があなたの金星や7ハウスにアスペクト（角度）を形成する時期に、運命的な出会いや結婚の決意が固まる可能性が高いです。具体的な時期は、トランジット（現在の星の動き）を確認することをおすすめします。'

def _get_earning_style(pluto):
    if not pluto:
        return ''
    
    p_house = get_house_num(str(pluto.house))
    h_info = HOUSE_BEGINNER.get(p_house, {})
    h_name = h_info.get('name', f'{p_house}ハウス')
    
    if p_house == '2':
        return f'{h_name}に冥王星があり、「0か100か」の徹底的な財運を持っています。普通の収入では満足できず、爆発的に稼ぐポテンシャルがありますが、執着しすぎると失うリスクもあります。極端な変動を経験しながら、真の豊かさを学びます。'
    elif p_house == '8':
        return f'{h_name}に冥王星があります。遺産、パートナーの収入、投資など「他者のリソース」を通じて大きな富を得る可能性があります。金融や心理学など、深層に関わる分野でのビジネスも適しています。'
    else:
        return f'財運の究極的なカギは{h_name}の領域にあります。\n冥王星の影響により、この分野で徹底的に取り組むことで、莫大な富やリソースを引き寄せる可能性があります。「諦めずに深掘りすること」が金脈を掘り当てる秘訣です。'

def _get_sign_strength(sign):
    strengths = {
        '牡羊座': '決断力と行動力が最強クラス。誰も踏み込まない領域に飛び込む勇気があります。',
        '牡牛座': '持続力と信頼性が最強クラス。一度始めたことは最後までやり遂げます。',
        '双子座': '情報収集力とコミュニケーション能力が最強クラス。人と人をつなぐ力があります。',
        '蟹座': '共感力と養育力が最強クラス。大切な人を守る力に優れています。',
        '獅子座': 'カリスマ性と創造力が最強クラス。存在するだけで周囲を明るくします。',
        '乙女座': '分析力と改善力が最強クラス。物事を完璧に仕上げる能力があります。',
        '天秤座': '外交力とバランス感覚が最強クラス。人間関係を円滑にする才能があります。',
        '蠍座': '洞察力と再生力が最強クラス。人の嘘を見抜くレントゲンのような目を持っています。',
        '射手座': '楽観性と拡張力が最強クラス。視野を広げ、人生に意味を見出す力があります。',
        '山羊座': '忍耐力と達成力が最強クラス。長期的な目標に向かって着実に歩みます。',
        '水瓶座': '革新力と独創性が最強クラス。既存の枠を超えた発想ができます。',
        '魚座': '直感力と癒しの力が最強クラス。目に見えない世界とつながる感受性があります。'
    }
    return strengths.get(sign, '')

def _determine_archetype(sun_sign, sun_house, moon_sign, moon_house, planets):
    """チャート全体からアーキタイプを決定"""
    
    # ハウス 8, 12 が強調されている場合
    emphasized = []
    for p in planets.values():
        h = get_house_num(str(p.house))
        emphasized.append(h)
    
    if emphasized.count('12') >= 2 or (moon_house == '8' and '12' in emphasized):
        return "「黒幕（フィクサー）」あるいは「孤高のカリスマ」"
    elif sun_house in ['1', '10'] or emphasized.count('10') >= 2:
        return "「王者」あるいは「リーダー」"
    elif sun_house == '7' or emphasized.count('7') >= 2:
        return "「外交官」あるいは「調停者」"
    elif emphasized.count('9') >= 2:
        return "「哲学者」あるいは「探求者」"
    elif emphasized.count('5') >= 2:
        return "「アーティスト」あるいは「表現者」"
    else:
        return f"「{_get_sign_archetype(sun_sign)}」"


def _get_mercury_detailed_style(sign):
    """水星星座の詳細な思考スタイル（初心者向け）"""
    styles = {
        '牡羊座': '頭の回転が非常に速く、「とりあえずやってみる」タイプ。議論では負けず嫌いで、自分の意見をストレートに主張します。じっくり考えるより直感で判断することが多く、決断力があります。ただし、せっかちになりすぎて早とちりすることも。',
        '牡牛座': '物事をじっくり考え、一度決めたら簡単には変えません。急かされるのが苦手で、自分のペースで情報を消化します。実用的で現実的な思考をし、「机上の空論」より具体的な結果を重視します。記憶力が良く、五感を通じて学ぶのが得意。',
        '双子座': '水星のホーム（本来の場所）！好奇心旺盛で、複数のことを同時に考えられます。話すのも書くのも得意で、情報通。ただ、興味が次々と移り変わりやすく、一つのことを深掘りするより広く浅く知ることを好む傾向があります。',
        '蟹座': '感情と記憶が結びついた思考スタイル。「あの時どう感じたか」を覚えていて、過去の経験から学びます。直感的に人の気持ちを読み取るのが得意。ただし、感情に左右されやすく、客観的な判断が苦手なことも。',
        '獅子座': '堂々と自信を持って意見を述べます。話すときにドラマチックな表現を使い、人を惹きつけるプレゼン力があります。創造的なアイデアが得意ですが、自分の意見に固執しやすい面も。',
        '乙女座': '水星のもう一つのホーム！分析力と細部への注意力が抜群。論理的に問題を解決し、完璧を目指します。批判的思考が得意ですが、細かいことにこだわりすぎて全体像を見失うことも。',
        '天秤座': '常に公平な視点で物事を見ます。「相手の立場に立って考える」のが得意で、交渉やディスカッションが上手。ただし、両面を見すぎて決断に時間がかかることも。美しい言葉遣いを好みます。',
        '蠍座': '表面的な答えに満足せず、本質を見抜こうとします。「なぜ？」を繰り返し、深く掘り下げる思考スタイル。秘密を守るのが得意で、人の本音を読み取る力があります。疑い深い面も。',
        '射手座': '大きなビジョンで考え、細かいことより全体像を重視します。哲学的・抽象的な思考が得意で、人生の意味を探求します。楽観的で、新しいアイデアにオープン。ただし、詳細を見落としがち。',
        '山羊座': '現実的で計画的な思考。「これをやったら何が得られるか」を常に考えます。目標達成のためのステップを論理的に組み立て、長期的な視点で判断します。権威ある情報を重視します。',
        '水瓶座': '既存の常識にとらわれない独創的な発想。「みんながこう考えるからといって正しいとは限らない」と考え、革新的なアイデアを生み出します。客観的で論理的ですが、時に理屈っぽくなることも。',
        '魚座': '直感的で創造的な思考。言葉にならないものを感じ取り、芸術的なビジョンを持っています。ただし、現実と想像の区別が曖昧になることも。人の気持ちを敏感に察知します。'
    }
    return styles.get(sign, '')


def _get_mercury_house_advice(house_num):
    """水星のハウス位置に基づく具体的アドバイス"""
    advice = {
        '1': '自己紹介やプレゼンが得意分野。ブログやSNSで「自分の考え」を発信すると良いでしょう。',
        '2': 'お金の管理や価値判断に知性を使います。副業のアイデアを考えたり、投資を学ぶのに向いています。',
        '3': '話す・書く・教えることが天職の可能性。SNS運用、ライティング、コーチングなどで才能を発揮できます。',
        '4': '家族との対話や、家に関する調べ物が得意。不動産、インテリア、家族史の研究などに向いています。',
        '5': '創作活動や恋愛で知性を発揮。小説を書いたり、デートプランを考えたり、子供と遊ぶアイデアを出すのが得意。',
        '6': '仕事の効率化や健康情報の収集が得意。ToDoリスト作りや、最新の健康法を調べることで力を発揮します。',
        '7': 'パートナーとの対話や交渉が得意。カップルカウンセラー、仲介業、契約交渉などに向いています。',
        '8': '心理学や投資、相続など「深い」テーマに知性を使います。人の本音を見抜く力があります。',
        '9': '海外や哲学、高等教育に関心があります。留学、旅行記の執筆、宗教・哲学の研究などに向いています。',
        '10': '仕事上のコミュニケーションで評価されます。企画書作成、プレゼン、広報などで才能を発揮できます。',
        '11': '友人やコミュニティ内での情報交換が活発。SNSでの発信、グループ活動の企画立案などが得意。',
        '12': '一人で考える時間が必要。日記を書いたり、瞑想したりすることで良いアイデアが浮かびます。匿名での発信も向いています。'
    }
    return advice.get(house_num, '')


def _get_sign_weakness(sign):
    """太陽星座に基づく弱み"""
    weaknesses = {
        '牡羊座': 'せっかちで衝動的になりやすく、他人の意見を聞かずに突っ走ることがあります。忍耐力が課題です。',
        '牡牛座': '変化への抵抗が強く、頑固になりやすいです。執着心が強すぎて新しい可能性を逃すことも。',
        '双子座': '興味が分散しやすく、一つのことを深く掘り下げるのが苦手。約束を忘れたり、飽きっぽい面も。',
        '蟹座': '感情的になりすぎて客観性を失うことがあります。過去への執着や、過保護になる傾向も。',
        '獅子座': 'プライドが高く、批判に過敏に反応しやすいです。自己中心的に見られることも。',
        '乙女座': '完璧主義で自分にも他人にも厳しくなりすぎます。細部にこだわって全体像を見失うことも。',
        '天秤座': '優柔不断で決断に時間がかかります。人に合わせすぎて自分を見失うこともあります。',
        '蠍座': '執念深く、一度傷つくと許せないことがあります。疑り深さが人間関係を難しくすることも。',
        '射手座': '無責任に見られやすく、約束を軽視することがあります。細かいことを見落としがちです。',
        '山羊座': '仕事中心になりすぎて、プライベートや感情面を犠牲にしがち。柔軟性に欠けることも。',
        '水瓶座': '理屈っぽく、感情面で冷たく見られることがあります。協調性に欠ける面も。',
        '魚座': '現実逃避しやすく、優柔不断になることがあります。境界線が曖昧で、人に利用されやすい面も。'
    }
    return weaknesses.get(sign, '')


def _get_moon_house_weakness(moon_house):
    """月のハウス位置に基づく感情的課題"""
    weaknesses = {
        '1': '感情が顔に出やすく、自分の気持ちを隠せません。感情の起伏が周囲に影響を与えやすいです。',
        '2': '経済的な不安が感情を大きく左右します。物質的な安定がないと落ち着けない傾向があります。',
        '3': '言葉で感情を処理するため、話しすぎたり、考えすぎて眠れなくなることがあります。',
        '4': '家族問題が感情に強く影響します。過去のトラウマを引きずりやすい傾向があります。',
        '5': '恋愛やクリエイティブな問題で感情が大きく揺れます。認められたい欲求が強いです。',
        '6': 'ストレスが健康に出やすく、心配性になりがち。完璧を求めすぎて疲れることも。',
        '7': 'パートナーに依存しやすく、一人でいることに不安を感じます。人の評価を気にしすぎます。',
        '8': '感情を極端に隠す傾向があり、他人に弱みを見せることを恐れます。トラウマを抱えやすいです。',
        '9': '現実から逃げたいという衝動に駆られることがあります。落ち着きがないと見られることも。',
        '10': '仕事と感情を切り離せず、キャリアの問題が精神的に大きく影響します。',
        '11': '友人関係や社会的な居場所がないと不安を感じます。孤独への恐れがあります。',
        '12': '感情を内側に閉じ込めやすく、孤独感や無力感を感じやすいです。自己犠牲的になることも。'
    }
    return weaknesses.get(moon_house, '')


def _get_moon_sign_action(moon_sign):
    """月星座に基づく感情的アドバイス"""
    actions = {
        '牡羊座': '感情のエネルギーを運動や競争的な活動に発散させてください。じっとしているより動くことで心が安定します。',
        '牡牛座': '心が疲れたときは美味しいものを食べ、自然の中を散歩し、好きな音楽を聴いてください。五感を満たすことが癒しです。',
        '双子座': '感情を言葉にして信頼できる人に話すか、日記に書き出してください。頭の中を整理することで心が軽くなります。',
        '蟹座': '安心できる場所と人を大切にしてください。家族や親しい友人との時間が、最大の心のケアになります。',
        '獅子座': '創作活動や自己表現を通じて感情を発散させてください。認められる体験が自信と安定につながります。',
        '乙女座': '問題を分析して解決策を見つけることで気持ちが落ち着きます。To Doリストを作って一つずつ片付けてください。',
        '天秤座': '美しいものに囲まれ、調和のとれた環境を作ってください。信頼できるパートナーとの対話も重要です。',
        '蠍座': '表面的な付き合いより、深く信頼できる少数の人との関係を大切にしてください。秘密を守れる相手を見つけましょう。',
        '射手座': '新しい場所を旅したり、新しいことを学んだりして視野を広げてください。束縛を感じたら離れる勇気を。',
        '山羊座': '目標を設定し、達成することで自信が生まれます。成果を出せる環境に身を置いてください。',
        '水瓶座': '自分のユニークさを認めてくれる仲間を見つけてください。「普通」であることを求めないで。',
        '魚座': '音楽、アート、瞑想などスピリチュアルな活動で心を癒してください。一人の時間と睡眠も大切です。'
    }
    return actions.get(moon_sign, '')


def _get_saturn_house_weakness(s_house):
    """土星のハウス位置に基づく課題"""
    weaknesses = {
        '1': '自信を持つことに時間がかかり、自己肯定感の構築が人生の課題です。',
        '2': 'お金に対する不安が強く、経済的な安定を築くまでに苦労する傾向があります。',
        '3': 'コミュニケーションに自信がなく、話すことや書くことへの苦手意識を持ちやすいです。',
        '4': '家族関係や家庭環境に課題があり、「安心できる居場所」を見つけることが人生のテーマです。',
        '5': '楽しむこと、創造的になること、恋愛に対してブレーキがかかりやすいです。',
        '6': '健康問題や仕事でのストレスを抱えやすく、日常生活の管理が課題になります。',
        '7': 'パートナーシップに慎重になりすぎたり、結婚が遅れる傾向があります。',
        '8': '他者との深い結びつきや共有財産に関して試練を経験しやすいです。',
        '9': '信念や人生観の確立に時間がかかり、海外や高等教育で苦労することも。',
        '10': 'キャリアの確立に時間がかかりますが、努力を重ねれば大きな成功が待っています。',
        '11': '友人関係やコミュニティへの帰属に課題を感じやすく、孤独を感じることも。',
        '12': '隠れた恐れや無意識のブロックと向き合う必要があります。精神的な成長が課題です。'
    }
    return weaknesses.get(s_house, '')


def _get_saturn_house_action(s_house):
    """土星のハウス位置に基づくアドバイス"""
    actions = {
        '1': '自己肯定感を育てる小さな成功体験を積み重ねてください。時間をかけて自信は必ず育ちます。',
        '2': '地道な貯金と着実な収入源の構築を心がけてください。30代以降に経済的安定が訪れます。',
        '3': '話すこと・書くことを意識的に練習してください。コミュニケーション力は必ず向上します。',
        '4': '過去の家族問題を癒し、自分自身の「安心の基盤」を新たに作ってください。',
        '5': '楽しむことに罪悪感を持たないで。創作活動や趣味に時間を投資する許可を自分に与えてください。',
        '6': '健康管理と仕事の効率化を優先してください。無理をせず、持続可能なルーティンを作りましょう。',
        '7': '焦らず、信頼できるパートナーを見つけてください。結婚は遅くても良いご縁があります。',
        '8': '心理的な深い癒しのワークに取り組んでください。トラウマを乗り越えることで強くなれます。',
        '9': '学び続けることで人生観が確立されます。海外や新しい思想との出会いを大切に。',
        '10': '長期的なキャリアプランを立て、着実に実績を積んでください。晩成型の成功が待っています。',
        '11': '同じ志を持つ仲間を時間をかけて見つけてください。深い友情は必ず築けます。',
        '12': '瞑想やセラピー、スピリチュアルな実践を通じて内面と向き合ってください。'
    }
    return actions.get(s_house, '')


def _generate_strategic_summary(sun_sign, moon_sign, asc_sign, sun_house, strengths, weaknesses):
    """総合的なまとめを生成"""
    
    # 強みのハイライト
    strength_highlight = strengths[0] if strengths else "多くの才能を持っています。"
    
    # 弱みのハイライト
    weakness_highlight = weaknesses[0] if weaknesses else "課題と向き合うことで成長できます。"
    
    summary = f"""【あなたへの総合メッセージ】

太陽{sun_sign}・月{moon_sign}・アセンダント{asc_sign}を持つあなたは、
{_get_sign_archetype(sun_sign)}の魂と{_get_sign_archetype(asc_sign)}の表現力を併せ持っています。

✨ 最大の強み：
{strength_highlight}

⚠️ 成長のための課題：
{weakness_highlight}

この強みを活かし、課題を乗り越えることで、あなたは人生の使命を果たすことができます。
自分の個性を信じ、一歩ずつ前に進んでください。"""
    
    return summary
