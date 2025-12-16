"""
Transit Interpretation Module
Advanced analysis for transit charts
"""

from datetime import datetime
from advanced_interpretation import HOUSE_BEGINNER, get_house_num, ELEMENTS, _get_sign_archetype

def get_natal_house(transit_abs_deg, natal_houses):
    """
    トランジット惑星がネイタルのどのハウスにあるかを計算
    
    Args:
        transit_abs_deg (float): トランジット惑星の絶対度数 (0-360)
        natal_houses (list): ネイタルチャートのハウスリスト (dict containing 'absolute_degree')
    
    Returns:
        int: ハウス番号 (1-12)
    """
    if len(natal_houses) != 12:
        return 1
        
    for i in range(12):
        current_house = natal_houses[i]
        next_house = natal_houses[(i + 1) % 12]
        
        start = current_house['absolute_degree']
        end = next_house['absolute_degree']
        
        # 通常のケース (例: 10度 -> 40度)
        if start < end:
            if start <= transit_abs_deg < end:
                return current_house['house']
        # 360度を跨ぐケース (例: 350度 -> 20度)
        else:
            if start <= transit_abs_deg or transit_abs_deg < end:
                return current_house['house']
                
    return 1 # Fallback

def _get_planet_transit_meaning(planet, house_num):
    """惑星のハウス通過の意味を取得 (詳細版)"""
    h_info = HOUSE_BEGINNER.get(str(house_num), {})
    h_simple = h_info.get('simple', '')
    
    # ハウスの意味をもう少し具体的に
    house_themes = {
        1: '「自分自身」と「新しいスタート」',
        2: '「お金」と「自信」',
        3: '「コミュニケーション」と「学び」',
        4: '「家庭」と「心の安らぎ」',
        5: '「楽しみ」と「自己表現」',
        6: '「仕事」と「健康管理」',
        7: '「パートナーシップ」と「人間関係」',
        8: '「深い絆」と「変化」',
        9: '「冒険」と「ステップアップ」',
        10: '「キャリア」と「社会的な目標」',
        11: '「未来への希望」と「仲間」',
        12: '「振り返り」と「癒し」'
    }
    
    theme = house_themes.get(house_num, h_simple)

    meanings = {
        'Jupiter': {
            'title': '【12年に一度の幸運期】拡大と発展の季節',
            'desc': f'幸運の星・木星が、あなたの{theme}のエリアを輝かせています。今は「これだ！」と思ったことに積極的に挑戦すべき時です。視野が広がり、思いがけないチャンスが舞い込むでしょう。楽観的に動くことが成功の鍵です。'
        },
        'Saturn': {
            'title': '【基盤を作る】試練と定着の季節',
            'desc': f'試練の星・土星が、あなたの{theme}のエリアに入っています。少しプレッシャーを感じたり、責任が増えたりするかもしれません。しかし、これはあなたが次のステージに進むためのテストです。逃げずに取り組めば、揺るぎない実力が身につきます。'
        },
        'Uranus': {
            'title': '【現状打破】変革と目覚めの季節',
            'desc': f'革命の星・天王星が、あなたの{theme}のエリアに変革の風を吹き込んでいます。「変わらなきゃ」という衝動を感じるかもしれません。予期せぬ変化は、あなたを古いしがらみから解放するためのギフトです。新しい自分に出会えるチャンスです。'
        },
        'Neptune': {
            'title': '【夢を見る】浄化と理想の季節',
            'desc': f'夢の星・海王星が、{theme}のエリアを漂っています。境界線が曖昧になり、現実的な判断が難しくなるかもしれませんが、直感やインスピレーションは冴え渡ります。論理よりも感覚を大切にすることで、大切な何かに気づくでしょう。'
        },
        'Pluto': {
            'title': '【根本的変容】破壊と再生の季節',
            'desc': f'破壊と再生の星・冥王星が、{theme}のエリアに深く影響を与えています。表面的な変化ではなく、根底からの生まれ変わりを促されています。もう不要になった価値観を手放すことで、本当に力強い自分を再発見できるでしょう。'
        },
        'Mars': {
            'title': '【全力投球】情熱と戦いの時期',
            'desc': f'情熱の星・火星が、{theme}のエリアを刺激しています！やる気満々で、エネルギッシュに行動できる時期です。ただし、エネルギーが強すぎてイライラしたり、衝突したりもしやすいので、スポーツや仕事で健全に発散しましょう。'
        },
        'Venus': {
            'title': '【ときめき】愛と喜びの時期',
            'desc': f'愛の星・金星が、{theme}のエリアに微笑みかけています。この分野で「楽しい！」「嬉しい！」と感じる出来事が増えるでしょう。無理に頑張るよりも、楽しむことを優先するとスムーズにうまくいきます。'
        }
    }
    
    return meanings.get(planet)

def _generate_aspect_advice(transit_chart):
    """トランジットアスペクトに基づく詳細アドバイスを生成"""
    major_aspects = []
    
    # 影響力の強い外惑星のハードアスペクトを優先的にピックアップ
    priority_planets = ['Pluto', 'Neptune', 'Uranus', 'Saturn']
    
    for aspect in transit_chart.aspects:
        # オーブが狭いもの（影響が強い）を厳選
        if aspect.orb > 3.0:
            continue
            
        t_planet = aspect.transit_planet
        n_planet = aspect.natal_planet
        aspect_type = aspect.aspect_type
        
        if t_planet in priority_planets and aspect_type in ['conjunction', 'square', 'opposition']:
             major_aspects.append(_interpret_aspect(t_planet, n_planet, aspect_type))
             
    return major_aspects

def _interpret_aspect(t_planet, n_planet, type):
    """アスペクトごとの解釈文"""
    
    # 簡易的な解釈辞書（拡張可能）
    interpretations = {
        ('Pluto', 'Sun'): 'あなたの人生の目的やアイデンティティが根底から変容する時期です。権力闘争に注意が必要ですが、信じられないほどの底力を発揮できます。',
        ('Pluto', 'Moon'): '感情が激しく揺れ動くかもしれません。過去の心の傷を癒やし、精神的に生まれ変わる深いプロセスの中にいます。',
        ('Neptune', 'Sun'): '自分の方向性が分からなくなったり、自信が揺らぎやすい時期です。しかし、エゴを手放すことで、より大きな流れに乗ることができます。',
        ('Uranus', 'Sun'): '突然の変化が起こりやすい時期です。これまでの自分を壊し、自由になりたいという衝動に従うことで、新しい道が開けます。',
        ('Saturn', 'Sun'): '責任や義務が重くのしかかる時期です。自己評価が下がりがちですが、コツコツ努力したことは必ず報われます。健康管理も大切に。',
        ('Saturn', 'Moon'): '孤独を感じやすかったり、感情を抑圧しやすい時期です。無理をせず、自分のための時間を確保して心を休めることが重要です。',
        ('Jupiter', 'Sun'): '自信と活力が溢れる幸運期です。何をやってもうまくいきやすく、周囲からの援助も期待できます。新しいことを始めるのに最適です。'
    }
    
    # マッチするものを探す（なければ汎用）
    text = interpretations.get((t_planet, n_planet))
    
    if not text:
        # ネイタル惑星に基づく汎用メッセージ
        if n_planet == 'Sun':
            target = 'あなたの人生の目的や意志'
        elif n_planet == 'Moon':
            target = 'あなたの私生活や感情'
        elif n_planet == 'Venus':
            target = 'あなたの恋愛や金運'
        elif n_planet == 'Mars':
            target = 'あなたの行動力や情熱'
        else:
            target = f'あなたの{n_planet}'
            
        jp_name = {'Pluto': '冥王星', 'Neptune': '海王星', 'Uranus': '天王星', 'Saturn': '土星', 'Jupiter': '木星'}.get(t_planet, t_planet)
        
        if type == 'conjunction':
            text = f'トランジットの{jp_name}が{target}に重なっています。大きなエネルギーの刷新が行われる重要なタイミングです。'
        elif type in ['square', 'opposition']:
            text = f'トランジットの{jp_name}が{target}に刺激を与えています。変化のためのプレッシャーを感じるかもしれませんが、成長のチャンスです。'
        elif type == 'trine':
             text = f'トランジットの{jp_name}が{target}をスムーズにサポートしています。物事が有利に進みやすい時期です。'
    
    return {
        'title': f'{t_planet}と{n_planet}のアスペクト',
        'description': text
    }

def generate_comprehensive_transit_interpretation(transit_chart):
    """
    包括的なトランジット解釈を生成
    """
    # 1. ハウスごとのテーマ（人生の季節）
    major_themes = []
    
    t_planets = transit_chart.transit_planets
    n_houses = transit_chart.natal_chart.houses
    
    target_planets = ['Pluto', 'Neptune', 'Uranus', 'Saturn', 'Jupiter', 'Mars'] # Marsも追加
    
    for tp in t_planets:
        if tp.name in target_planets:
            h_num = get_natal_house(tp.absolute_degree, n_houses)
            meaning = _get_planet_transit_meaning(tp.name, h_num)
            
            if meaning:
                major_themes.append({
                    'planet': tp.name,
                    'house': h_num,
                    'title': meaning['title'],
                    'description': meaning['description'] if 'description' in meaning else meaning['desc']
                })
    
    # 2. カテゴリ別アドバイス（既存ロジック強化）
    advice = {
        'love': _generate_love_transit_advice(transit_chart, n_houses),
        'work': _generate_work_transit_advice(transit_chart, n_houses),
        'mental': _generate_mental_transit_advice(transit_chart, n_houses)
    }
    
    # 3. アスペクト分析（新規追加）
    aspect_insights = _generate_aspect_advice(transit_chart)
    
    return {
        'major_themes': major_themes,
        'advice': advice,
        'aspect_insights': aspect_insights
    }

def _generate_love_transit_advice(transit_chart, n_houses):
    """現在の恋愛運 (詳細版)"""
    t_venus = next((p for p in transit_chart.transit_planets if p.name == 'Venus'), None)
    
    if not t_venus:
        return {'score': 3, 'text': '特筆すべき動きはありませんが、穏やかな運気です。'}
        
    h_num = get_natal_house(t_venus.absolute_degree, n_houses)
    
    # より豊かな表現に
    if h_num == 1:
        text = "【モテ期到来！】金星があなたの星座（1ハウス）を通過中です。あなたの魅力が自然と輝き出し、周囲からの注目を集める時期です。オシャレをして出かけると素敵なことがありそう！"
        score = 5
    elif h_num == 5:
        text = "【恋愛最高潮！】金星が「愛と喜び」の部屋（5ハウス）に入っています。ドラマのようなロマンスが期待できるとき。自分から楽しむことで、さらに運気が上がります。"
        score = 5
    elif h_num == 7:
        text = "【パートナーシップの充実】金星が「パートナー」の部屋（7ハウス）を通過中。結婚につながる出会いや、パートナーとの絆が深まる最高のタイミングです。"
        score = 5
    elif h_num == 8:
        text = "【深い愛】金星が8ハウスにあり、特定の相手と深く結びつく時期です。表面的な付き合いよりも、密な関係を求めると心が満たされます。"
        score = 4
    elif h_num == 11:
        text = "【友情から始まる恋】友人やサークル活動の中で素敵な出会いがありそう。恋人とも友達のように爽やかな関係を築けます。"
        score = 4
    else:
        info = _get_planet_transit_meaning('Venus', h_num)
        text = info['desc'] if info else "穏やかで安定した恋愛運です。"
        score = 3
        
    return {'score': score, 'text': text}

def _generate_work_transit_advice(transit_chart, n_houses):
    """現在の仕事・金運 (詳細版)"""
    t_mars = next((p for p in transit_chart.transit_planets if p.name == 'Mars'), None)
    t_jupiter = next((p for p in transit_chart.transit_planets if p.name == 'Jupiter'), None)
    
    messages = []
    
    # Mars Checks
    if t_mars:
        h_mars = get_natal_house(t_mars.absolute_degree, n_houses)
        if h_mars == 10:
            messages.append("🔥 **キャリアの勝負時**: 火星が10ハウスにあります。仕事で大きな成果を出せるチャンス！野心を持って挑戦しましょう。忙しくなりますが、充実感も大きいはず。")
        elif h_mars == 6:
            messages.append("⚙️ **実務能力アップ**: 火星が6ハウスに入り、テキパキと仕事をこなせるとき。職場での評価も上がりますが、オーバーワークには注意して。")
        elif h_mars == 2:
            messages.append("💰 **稼ぐ力アップ**: 火星が収入の部屋にあり、お金を稼ぐ意欲が湧いてきます。短期的な収入アップも見込めますが、衝動買いも激しくなりそう。")
            
    # Jupiter Checks
    if t_jupiter:
        h_jup = get_natal_house(t_jupiter.absolute_degree, n_houses)
        if h_jup == 2:
            messages.append("✨ **金運の拡大期**: 木星が収入の部屋（2ハウス）に滞在中。12年に一度の金運アッパー期です！収入源を増やすアクションを起こすのに最適です。")
        elif h_jup == 6:
            messages.append("✨ **職場環境の改善**: 木星が6ハウスにあり、働きやすい環境が整います。良い条件の仕事が見つかったり、同僚との関係も良好に。")
        elif h_jup == 10:
            messages.append("✨ **社会的成功**: 木星がキャリアの部屋（10ハウス）で輝いています。昇進、栄転、独立など、社会的なステータスが上がる大チャンスです。")
            
    if not messages:
        messages.append("現在は準備期間です。目の前のタスクに着実に取り組むことで、次のチャンスへの土台が作られます。")
        
    return {'text': "\n\n".join(messages)}

def _generate_mental_transit_advice(transit_chart, n_houses):
    """現在のメンタル・内面 (詳細版)"""
    t_moon = next((p for p in transit_chart.transit_planets if p.name == 'Moon'), None)
    
    if not t_moon:
        return {'text': '穏やかな日です。自分のペースで過ごしましょう。'}
        
    h_moon = get_natal_house(t_moon.absolute_degree, n_houses)
    
    # 感情的なニーズを丁寧に記述
    moon_msg = {
        1: "今日は**自分ファースト**で過ごしましょう。自分の気持ちに素直になることで、運気が開けます。",
        2: "美味しいものを食べたり、マッサージに行ったり、**五感を満たす**ことで心が安定します。",
        3: "好奇心が旺盛になる日。本屋に行ったり、友達とおしゃべりすると良いリフレッシュになります。",
        4: "**お家時間**を大切にしたい日。早く帰宅して、リラックスできる環境でくつろぎましょう。",
        5: "クリエイティブなエネルギーが高まっています。趣味や推し活など、**好きなことに没頭**して！",
        6: "部屋の片付けやスケジュールの整理など、**身の回りを整える**と心がスッキリします。",
        7: "人と接することで元気をもらえる日。一人で悩まず、信頼できる誰かに相談してみましょう。",
        8: "集中力が高まっています。一つのことを深く掘り下げたり、静かな時間を過ごすのが吉。",
        9: "少し遠出をしたり、いつもと違う道を歩いてみて。**新しい景色**が心に刺激をくれます。",
        10: "仕事モードになりやすい日。やるべきことを終わらせて達成感を味わうと、自己肯定感がアップ。",
        11: "未来に思いを馳せる日。友達と夢を語り合ったり、ネットで情報収集するとワクワクできそう。",
        12: "少し疲れが出やすいかも。今日は無理せず、早めに寝たり、**一人の時間**を確保して充電しましょう。"
    }
    
    return {'text': moon_msg.get(h_moon, '今日は無理せず、リラックスして過ごしましょう。')}
