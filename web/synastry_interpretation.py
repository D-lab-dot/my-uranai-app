"""
Synastry Interpretation Module
Advanced compatibility analysis with House Overlays and Categories
"""

from transit_interpretation import get_natal_house
from advanced_interpretation import HOUSE_BEGINNER, _get_sign_archetype, get_house_num

def generate_comprehensive_synastry(syn, chart1, chart2):
    """
    包括的な相性診断を生成
    """
    
    # 1. ハウスオーバーレイ (相手の星が自分のどこに入るか)
    overlays_1 = _analyze_overlays(chart1, chart2) # Chart2 planets in Chart1 houses
    overlays_2 = _analyze_overlays(chart2, chart1) # Chart1 planets in Chart2 houses
    
    # 2. カテゴリ別相性
    compatibility = {
        'love': _analyze_love_compatibility(syn),
        'communication': _analyze_comm_compatibility(syn),
        'value': _analyze_value_compatibility(syn)
    }
    
    return {
        'overlays': {
            'chart1_view': overlays_1, # Chart1から見たChart2の影響
            'chart2_view': overlays_2  # Chart2から見たChart1の影響
        },
        'compatibility': compatibility
    }

def _analyze_overlays(base_chart, planet_chart):
    """
    planet_chartの主要惑星がbase_chartのどのハウスに入るかを分析
    """
    results = []
    target_planets = ['Sun', 'Moon', 'Venus', 'Mars', 'Jupiter', 'Saturn']
    
    base_houses = base_chart.houses
    
    for p_attr in target_planets:
        planet_name = p_attr.lower()
        if hasattr(planet_chart, planet_name):
            planet = getattr(planet_chart, planet_name)
            h_num = get_natal_house(planet.absolute_degree, base_houses)
            
            # ハウスの意味を取得
            h_info = HOUSE_BEGINNER.get(str(h_num), {})
            h_simple = h_info.get('simple', '')
            
            # 日本語の惑星名
            planet_jp = {
                'Sun': '太陽', 'Moon': '月', 'Venus': '金星', 'Mars': '火星',
                'Jupiter': '木星', 'Saturn': '土星'
            }.get(p_attr, p_attr)

            meaning_data = _get_overlay_meaning_detailed(p_attr, h_num, h_simple)
            
            results.append({
                'planet': p_attr,
                'planet_jp': planet_jp,
                'house': h_num,
                'house_theme': h_simple,
                'title': meaning_data['title'],
                'meaning': meaning_data['text']  # user requested detailed text
            })
            
    return results

def _get_overlay_meaning_detailed(planet, house, house_desc):
    """オーバーレイの詳細な意味を生成"""
    
    # ハウスごとの基本テーマ（より具体的・感情的に）
    house_themes = {
        1: 'あなたの存在そのものや第一印象',
        2: 'あなたの才能や物質的な豊かさ',
        3: '日々のコミュニケーションや学び',
        4: '心の安らぎやプライベートな空間',
        5: '自己表現、恋愛、創造的な喜び',
        6: '日々の仕事、健康、生活習慣',
        7: '対等なパートナーシップや結婚',
        8: '深い絆、共有する財産、信頼',
        9: '未知の世界、冒険、精神的な成長',
        10: '社会的な目標、キャリア、肩書き',
        11: '未来の夢、友人関係、サークル',
        12: '無意識の世界、秘密、癒し'
    }
    
    theme = house_themes.get(house, house_desc)

    # 惑星 x ハウス の詳細テキスト生成
    if planet == 'Sun':
        titles = {
            1: '自信を与えてくれる存在', 5: '人生を楽しむ最高の遊び相手', 
            7: '理想的なパートナー', 10: '社会的な発展をもたらす人'
        }
        text = f"相手の「太陽」が、{theme}を表すあなたの{house}ハウスに入ります。\n\n" \
               f"相手は、この分野においてあなたに強い影響力と活力をもたらします。"
        if house == 1:
            text += "一緒にいると自分らしくいられ、自信が湧いてくるでしょう。あなたにとって「なくてはならない存在」になりやすい相性です。"
        elif house == 5:
            text += "相手といると、あなたは子供のような無邪気な気持ちになれます。クリエイティブな活動や恋愛において、素晴らしい刺激をくれます。"
        elif house == 7:
            text += "あなたにとって「理想の結婚相手」や「公私とものパートナー」として映るでしょう。お互いを補完し合える素晴らしい配置です。"
        elif house == 10:
            text += "あなたの仕事やキャリアを強力にバックアップしてくれます。相手の存在が、あなたの社会的な成功を後押しするでしょう。"
        else:
            text += f"相手と関わることで、あなたの「{house_desc}」の分野が活性化し、人生の目的が明確になります。"

        return {'title': titles.get(house, f'{house_desc}で輝きを与える相性'), 'text': text}

    elif planet == 'Moon':
        titles = {
            1: '感情が同調する関係', 4: '家族のような安心感', 
            7: '妻・母のようなサポート', 12: '魂の繋がり'
        }
        text = f"相手の「月」が、{theme}を表すあなたの{house}ハウスに入ります。\n\n" \
               f"相手は、この分野においてあなたに深い安心感と癒しを与えます。"
        if house == 4:
            text += "一緒にいると、まるで実家にいるようなホッとする感覚を覚えるでしょう。結婚生活に最適な相性で、温かい家庭を築けます。"
        elif house == 7:
            text += "相手はあなたの気持ちを汲み取るのが上手で、パートナーとして精神的な支えになってくれます。あなたも自然と素直になれるでしょう。"
        elif house == 12:
            text += "言葉にしなくても通じ合う、テレパシーのような感覚があるかもしれません。あなたの隠れた不安を優しく包み込んでくれる存在です。"
        else:
            text += f"あなたが「{house_desc}」に関することに取り組むとき、相手は感情的に寄り添い、サポートしてくれます。"

        return {'title': titles.get(house, f'{house_desc}での安心感'), 'text': text}

    elif planet == 'Venus':
        titles = {
            1: 'あなたを美しくする人', 2: '豊かさをもたらす人',
            5: 'ロマンチックな恋人', 7: '愛され愛する関係'
        }
        text = f"相手の「金星」が、{theme}を表すあなたの{house}ハウスに入ります。\n\n" \
               f"相手は、この分野に「喜び」「楽しみ」「豊かさ」を運び込みます。"
        if house == 1:
            text += "相手はあなたの魅力を最大限に引き出してくれます。一緒にいると自分が美しく（かっこよく）なったように感じるでしょう。甘いムードになりやすい相性です。"
        elif house == 2:
            text += "金運アップの相性です！相手からのプレゼントや、一緒にビジネスをすることで、あなたの経済状況が潤う可能性があります。"
        elif house == 5:
            text += "恋愛の楽しさを存分に味わえる配置です。デートや趣味の時間があっという間に過ぎていくような、ドキドキする関係になれるでしょう。"
        else:
            text += f"「{house_desc}」の分野において、相手はあなたにとってのラッキーパーソンです。楽しいことが増えるでしょう。"
            
        return {'title': titles.get(house, f'{house_desc}での喜び'), 'text': text}

    elif planet == 'Mars':
        titles = {
            1: 'やる気に火をつける人', 6: '仕事の最強の相棒',
            8: 'セクシャルな魅力', 10: 'キャリアを推進する力'
        }
        text = f"相手の「火星」が、{theme}を表すあなたの{house}ハウスに入ります。\n\n" \
               f"相手は、この分野においてあなたのやる気スイッチを押し、行動力を引き出します。"
        if house == 1:
            text += "あなたに強い刺激を与える存在です。セクシャルな魅力も感じやすいですが、喧嘩をすると激しくなりがちなので注意が必要です。"
        elif house == 6:
            text += "一緒に仕事をすると素晴らしいパフォーマンスを発揮できます。相手の行動力が、あなたの実務を強力にサポートしてくれます。"
        elif house == 8:
            text += "深い部分で強く惹かれ合う、磁石のような相性です。性的な相性が良いことも多いですが、支配的にならないようバランスが大切です。"
        else:
            text += f"あなたの「{house_desc}」の分野にエネルギーを注入してくれます。相手といると、不思議と頑張れる気がするはずです。"

        return {'title': titles.get(house, f'{house_desc}への刺激'), 'text': text}

    elif planet == 'Jupiter':
        titles = {
            1: '幸運の天使', 2: '財政的な援助者',
            7: '最高のパートナーシップ', 9: '精神的導き手'
        }
        text = f"相手の「木星」が、{theme}を表すあなたの{house}ハウスに入ります。\n\n" \
               f"相手は、あなたにとっての「幸運の鍵」です。この分野において、拡大と発展をもたらしてくれます。"
        if house == 2:
            text += "あなたの金運を大きく発展させてくれる素晴らしい相性です。相手のアドバイスや存在が、あなたの豊かさに直結します。"
        elif house == 7:
            text += "結婚相手として理想的な配置の一つです。一緒にいることであなたの世界が広がり、社会的な信用や幸福感が増していくでしょう。"
        else:
            text += f"「{house_desc}」に関して、相手は常に肯定的で、あなたを応援してくれます。一緒にいると楽観的になれるでしょう。"

        return {'title': titles.get(house, f'{house_desc}での発展'), 'text': text}

    elif planet == 'Saturn':
        titles = {
            1: '成熟させてくれる人', 2: '経済観念の先生',
            7: '末長い縁', 10: '厳しくも頼れる上司'
        }
        text = f"相手の「土星」が、{theme}を表すあなたの{house}ハウスに入ります。\n\n" \
               f"相手は、この分野においてあなたに「安定」と「責任」を教える役割を持っています。"
        if house == 7:
            text += "一時の遊びではなく、真剣で長期的な交際（結婚）に向く相性です。派手さはありませんが、責任感を持った誠実な関係を築けます。"
        elif house == 10:
            text += "仕事においては厳しいかもしれませんが、あなたのキャリアを盤石なものにしてくれる恩師のような存在です。"
        else:
            text += f"「{house_desc}」の分野で、相手は少し厳しいことを言うかもしれませんが、それはあなたを思ってのこと。長い目で見れば最大の味方です。"

        return {'title': titles.get(house, f'{house_desc}での学びと安定'), 'text': text}
    
    return {'title': f'{planet_jp}が活性化', 'text': f'相手の{planet}が{house}ハウスを活性化します。'}

def _analyze_love_compatibility(syn):
    """恋愛相性"""
    # 金星・火星・太陽・月のアスペクトをチェック
    score = 50
    comments = []
    
    key_interactions = [
        ('Venus', 'Mars', 10, '強烈な惹かれ合いがあります。'),
        ('Sun', 'Moon', 10, '夫婦としての相性が抜群です。'),
        ('Venus', 'Venus', 5, '感性が似ていて一緒にいて楽しい関係です。'),
        ('Moon', 'Moon', 5, 'お互いの感情を理解し合える関係です。')
    ]
    
    positive_aspects = [a for a in syn.aspects if a.is_harmonious]
    challenging_aspects = [a for a in syn.aspects if not a.is_harmonious]
    
    # 簡易スコアリング
    for asp in positive_aspects:
        for p1, p2, pt, msg in key_interactions:
            if (asp.person1_planet == p1 and asp.person2_planet == p2) or \
               (asp.person1_planet == p2 and asp.person2_planet == p1):
                score += pt
                comments.append(msg)
                
    # その他のコメント
    if score >= 80:
        desc = "情熱的で深い絆で結ばれた素晴らしい相性です。"
    elif score >= 60:
        desc = "お互いに惹かれ合い、楽しく過ごせる相性です。"
    else:
        desc = "違い刺激し合う関係ですが、理解への努力も必要です。"
        
    return {'score': min(100, score), 'description': desc, 'details': list(set(comments))[:3]}

def _analyze_comm_compatibility(syn):
    """コミュニケーション相性 (水星)"""
    score = 50
    comments = []
    
    mercury_aspects = [a for a in syn.aspects if 'Mercury' in (a.person1_planet, a.person2_planet)]
    
    has_pos = any(a.is_harmonious for a in mercury_aspects)
    has_neg = any(not a.is_harmonious for a in mercury_aspects)
    
    if has_pos:
        score += 20
        comments.append("会話が弾み、自然とお互いの考えを理解できます。")
    if has_neg:
        score -= 10
        comments.append("議論になることがありますが、それによって理解が深まります。")
    if not mercury_aspects:
        comments.append("特に問題なく意思疎通ができます。")
        
    return {'score': score, 'description': comments[0] if comments else ""}

def _analyze_value_compatibility(syn):
    """価値観の相性 (金星・木星)"""
    score = 50
    # 実装は簡易的に
    return {'score': syn.score, 'description': "全体的な相性スコアに基づきます。"}
