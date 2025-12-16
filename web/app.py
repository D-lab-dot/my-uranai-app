"""
Uranai Web Application - Flask Server
占星術アプリケーションのAPIサーバー
"""
import os
import sys
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory

# Add parent directory to path for uranai import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Add current directory to path for sibling imports (fixes Render/gunicorn ModuleNotFoundError)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from uranai import BirthChart, TransitChart, SolarReturnChart, Synastry, CompositeChart

try:
    # When running as a package (e.g. via Gunicorn)
    from web.advanced_interpretation import generate_advanced_interpretation
    from web.transit_interpretation import generate_comprehensive_transit_interpretation
    from web.synastry_interpretation import generate_comprehensive_synastry
    from web.daily_interpretation import generate_daily_forecast
    from web.comprehensive_analysis import generate_comprehensive_analysis
except ImportError:
    # When running locally as script
    from advanced_interpretation import generate_advanced_interpretation
    from transit_interpretation import generate_comprehensive_transit_interpretation
    from synastry_interpretation import generate_comprehensive_synastry
    from daily_interpretation import generate_daily_forecast
    from comprehensive_analysis import generate_comprehensive_analysis


app = Flask(__name__)

# SVGチャートの保存先
CHARTS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'charts')
os.makedirs(CHARTS_DIR, exist_ok=True)


@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')


@app.route('/robots.txt')
def robots():
    """SEO: robots.txtを返す"""
    return send_from_directory('static', 'robots.txt')


@app.route('/sitemap.xml')
def sitemap():
    """SEO: sitemap.xmlを返す"""
    return send_from_directory('static', 'sitemap.xml')


@app.route('/api/birth-chart', methods=['POST'])
def birth_chart():
    """出生図API"""
    try:
        data = request.json
        unknown_time = data.get('unknown_time', False)
        birth_year = int(data['year'])
        
        chart = BirthChart(
            name=data.get('name', 'Guest'),
            year=birth_year,
            month=int(data['month']),
            day=int(data['day']),
            hour=int(data.get('hour', 12)),
            minute=int(data.get('minute', 0)),
            city=data.get('city'),
            lat=float(data['lat']) if data.get('lat') else None,
            lng=float(data['lng']) if data.get('lng') else None
        )
        
        # SVGチャート生成
        chart_filename = f"{chart.name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.svg"
        chart_path = os.path.join(CHARTS_DIR, chart_filename)
        try:
            chart.save_svg(chart_path)
            svg_url = f"/static/charts/{chart_filename}"
        except Exception as e:
            svg_url = None
        
        # 基本解釈テキストを生成
        basic_interpretation = generate_detailed_interpretation(chart, unknown_time=unknown_time)
        
        # 高度な分析を生成（Gemini-level）
        advanced_analysis = generate_advanced_interpretation(chart, birth_year, unknown_time=unknown_time)
        
        # 包括的分析を生成（LLM-level詳細）
        comprehensive = generate_comprehensive_analysis(chart, birth_year, unknown_time=unknown_time)
        
        return jsonify({
            'success': True,
            'data': chart.to_dict(),
            'summary': chart.summary(),
            'svg_url': svg_url,
            'interpretation': basic_interpretation,
            'advanced_analysis': advanced_analysis,
            'comprehensive': comprehensive,
            'unknown_time': unknown_time
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 400



@app.route('/api/transit', methods=['POST'])
def transit():
    """トランジットAPI"""
    try:
        data = request.json
        
        chart = BirthChart(
            name=data.get('name', 'Guest'),
            year=int(data['year']),
            month=int(data['month']),
            day=int(data['day']),
            hour=int(data.get('hour', 12)),
            minute=int(data.get('minute', 0)),
            city=data.get('city'),
            lat=float(data['lat']) if data.get('lat') else None,
            lng=float(data['lng']) if data.get('lng') else None
        )
        
        target_date = data.get('target_date', datetime.now().strftime('%Y-%m-%d'))
        transit_chart = TransitChart(chart, target_date=target_date)
        
        # トランジットの解釈を生成
        # 新しい包括的な解釈を生成
        interpretation = generate_comprehensive_transit_interpretation(transit_chart)
        
        return jsonify({
            'success': True,
            'data': transit_chart.to_dict(),
            'summary': transit_chart.summary(),
            'interpretation': interpretation
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/synastry', methods=['POST'])
def synastry():
    """相性占いAPI"""
    try:
        data = request.json
        
        chart1 = BirthChart(
            name=data['person1'].get('name', 'Person 1'),
            year=int(data['person1']['year']),
            month=int(data['person1']['month']),
            day=int(data['person1']['day']),
            hour=int(data['person1'].get('hour', 12)),
            minute=int(data['person1'].get('minute', 0)),
            city=data['person1'].get('city'),
            lat=float(data['person1']['lat']) if data['person1'].get('lat') else None,
            lng=float(data['person1']['lng']) if data['person1'].get('lng') else None
        )
        
        chart2 = BirthChart(
            name=data['person2'].get('name', 'Person 2'),
            year=int(data['person2']['year']),
            month=int(data['person2']['month']),
            day=int(data['person2']['day']),
            hour=int(data['person2'].get('hour', 12)),
            minute=int(data['person2'].get('minute', 0)),
            city=data['person2'].get('city'),
            lat=float(data['person2']['lat']) if data['person2'].get('lat') else None,
            lng=float(data['person2']['lng']) if data['person2'].get('lng') else None
        )
        
        syn = Synastry(chart1, chart2)
        
        # 相性の解釈を生成 (新しい包括的ロジック)
        interpretation = generate_comprehensive_synastry(syn, chart1, chart2)
        
        return jsonify({
            'success': True,
            'data': syn.to_dict(),
            'summary': syn.summary(),
            'interpretation': interpretation
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/solar-return', methods=['POST'])
def solar_return():
    """ソーラーリターンAPI"""
    try:
        data = request.json
        
        chart = BirthChart(
            name=data.get('name', 'Guest'),
            year=int(data['year']),
            month=int(data['month']),
            day=int(data['day']),
            hour=int(data.get('hour', 12)),
            minute=int(data.get('minute', 0)),
            city=data.get('city'),
            lat=float(data['lat']) if data.get('lat') else None,
            lng=float(data['lng']) if data.get('lng') else None
        )
        
        return_year = int(data.get('return_year', datetime.now().year))
        sr = SolarReturnChart(chart, return_year=return_year)
        
        return jsonify({
            'success': True,
            'data': sr.to_dict(),
            'summary': sr.summary()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/daily', methods=['GET'])
def daily_horoscope():
    """今日の運勢API"""
    try:
        now = datetime.now()
        signs = ['牡羊座', '牡牛座', '双子座', '蟹座', '獅子座', '乙女座',
                 '天秤座', '蠍座', '射手座', '山羊座', '水瓶座', '魚座']
        
        horoscopes = {}
        horoscopes = {}
        for sign in signs:
            horoscopes[sign] = generate_daily_forecast(sign, now)
        
        return jsonify({
            'success': True,
            'date': now.strftime('%Y年%m月%d日'),
            'horoscopes': horoscopes
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ==========================================
# 詳細な解釈テキスト生成
# ==========================================

def generate_detailed_interpretation(chart, unknown_time=False):
    """詳細なホロスコープ解釈を生成"""
    sun_sign = chart.sun.sign_jp
    moon_sign = chart.moon.sign_jp
    asc_sign = chart.ascendant['sign_jp']
    
    # 惑星データを取得
    planets = {p.name: p for p in chart.planets}
    
    # 従来の惑星ベース解釈（詳細表示用）
    interpretation = {
        'sun': get_sun_detailed(sun_sign),
        'sun_detail': get_sun_life_path(sun_sign),
        'sun_house': get_sun_house_meaning(chart.sun.house) if not unknown_time else None,
        'moon': get_moon_detailed(moon_sign),
        'moon_detail': get_moon_needs(moon_sign),
        'moon_house': get_moon_house_meaning(chart.moon.house) if not unknown_time else None,
        'ascendant': get_asc_detailed(asc_sign) if not unknown_time else '※出生時刻不明のため、アセンダントの解釈は参考値です。正確な時刻がわかれば、より精密な分析が可能になります。',
        'mercury': get_mercury_interpretation(planets.get('Mercury')),
        'venus': get_venus_interpretation(planets.get('Venus')),
        'mars': get_mars_interpretation(planets.get('Mars')),
        'jupiter': get_jupiter_interpretation(planets.get('Jupiter')),
        'saturn': get_saturn_interpretation(planets.get('Saturn')),
        'outer_planets': get_outer_planets_interpretation(planets),
        'aspect_highlights': get_aspect_interpretation(chart.aspects[:8]),
        'overall': generate_overall_reading(sun_sign, moon_sign, asc_sign),
        'unknown_time': unknown_time,
        # 新規: カテゴリベース解釈（簡易表示用）
        'categories': generate_category_interpretation(chart, planets, unknown_time)
    }
    
    return interpretation


def generate_category_interpretation(chart, planets, unknown_time=False):
    """ユーザーフレンドリーなカテゴリベース解釈を生成"""
    sun_sign = chart.sun.sign_jp
    moon_sign = chart.moon.sign_jp
    asc_sign = chart.ascendant['sign_jp']
    venus = planets.get('Venus')
    mars = planets.get('Mars')
    mercury = planets.get('Mercury')
    jupiter = planets.get('Jupiter')
    saturn = planets.get('Saturn')
    
    categories = []
    
    # 1. あなたの性格
    personality_summary = _get_personality_summary(sun_sign, asc_sign, unknown_time)
    categories.append({
        'id': 'personality',
        'title': 'あなたの性格',
        'icon': '🧑',
        'summary': personality_summary['short'],
        'details': personality_summary['long'],
        'keywords': personality_summary['keywords']
    })
    
    # 2. 恋愛・結婚運
    love_summary = _get_love_summary(venus, moon_sign)
    categories.append({
        'id': 'love',
        'title': '恋愛・結婚運',
        'icon': '💗',
        'summary': love_summary['short'],
        'details': love_summary['long'],
        'keywords': love_summary['keywords']
    })
    
    # 3. 金運・仕事運
    money_summary = _get_money_summary(chart, jupiter, saturn, unknown_time)
    categories.append({
        'id': 'money',
        'title': '金運・仕事運',
        'icon': '💰',
        'summary': money_summary['short'],
        'details': money_summary['long'],
        'keywords': money_summary['keywords']
    })
    
    # 4. 思考・コミュニケーション
    communication_summary = _get_communication_summary(mercury)
    categories.append({
        'id': 'communication',
        'title': '思考・話し方',
        'icon': '🧠',
        'summary': communication_summary['short'],
        'details': communication_summary['long'],
        'keywords': communication_summary['keywords']
    })
    
    # 5. 行動力・エネルギー
    action_summary = _get_action_summary(mars)
    categories.append({
        'id': 'action',
        'title': '行動力・エネルギー',
        'icon': '💪',
        'summary': action_summary['short'],
        'details': action_summary['long'],
        'keywords': action_summary['keywords']
    })
    
    # 6. 幸運と成長
    fortune_summary = _get_fortune_summary(jupiter)
    categories.append({
        'id': 'fortune',
        'title': '幸運のポイント',
        'icon': '⭐',
        'summary': fortune_summary['short'],
        'details': fortune_summary['long'],
        'keywords': fortune_summary['keywords']
    })
    
    # 7. 課題と成長
    challenge_summary = _get_challenge_summary(saturn)
    categories.append({
        'id': 'challenge',
        'title': '人生の課題',
        'icon': '🎯',
        'summary': challenge_summary['short'],
        'details': challenge_summary['long'],
        'keywords': challenge_summary['keywords']
    })
    
    return categories


def _get_personality_summary(sun_sign, asc_sign, unknown_time):
    """性格カテゴリの解釈を生成"""
    personality_traits = {
        '牡羊座': {'short': '情熱的なパイオニア', 'keywords': ['行動力', '勇気', 'リーダーシップ'], 'trait': '挑戦を恐れず、常に新しい道を切り開く開拓者精神の持ち主'},
        '牡牛座': {'short': '安定を愛するアーティスト', 'keywords': ['忍耐力', '感性', '堅実'], 'trait': '五感を大切にし、美と安定を追求する穏やかな心の持ち主'},
        '双子座': {'short': '好奇心旺盛なコミュニケーター', 'keywords': ['知性', '適応力', '社交性'], 'trait': '情報を集め、人と繋がることで輝く言葉の魔術師'},
        '蟹座': {'short': '思いやり深い守護者', 'keywords': ['共感力', '家庭的', '直感'], 'trait': '大切な人を守り育てる深い愛情の持ち主'},
        '獅子座': {'short': '輝くカリスマリーダー', 'keywords': ['自信', '創造性', '寛大'], 'trait': '自然と人の中心に立ち、周囲を照らす太陽のような存在'},
        '乙女座': {'short': '完璧を目指す分析家', 'keywords': ['分析力', '誠実', '奉仕精神'], 'trait': '細部まで気を配り、実用的な改善を追求する実務家'},
        '天秤座': {'short': 'バランス感覚の調停者', 'keywords': ['調和', '美的センス', '外交力'], 'trait': '公平さと美しさを追求し、人と人を繋ぐ架け橋'},
        '蠍座': {'short': '深い洞察力の変革者', 'keywords': ['情熱', '洞察力', '再生力'], 'trait': '表面的なことに満足せず、物事の本質を見抜く探求者'},
        '射手座': {'short': '自由を愛する冒険家', 'keywords': ['楽観性', '哲学', '冒険心'], 'trait': '広い視野で真理と自由を求めて旅する探求者'},
        '山羊座': {'short': '野心あふれる建設者', 'keywords': ['責任感', '野心', '忍耐'], 'trait': '長期的なビジョンを持ち、着実に頂点を目指す努力家'},
        '水瓶座': {'short': '独創的な革命家', 'keywords': ['独創性', '人道主義', '自由'], 'trait': '常識にとらわれず、より良い未来を追求する改革者'},
        '魚座': {'short': '共感力豊かな夢想家', 'keywords': ['直感', '芸術性', '共感'], 'trait': '境界を超えて全てと繋がる深い感受性の持ち主'}
    }
    
    sun_data = personality_traits.get(sun_sign, {'short': sun_sign, 'keywords': [], 'trait': ''})
    asc_data = personality_traits.get(asc_sign, {'short': asc_sign, 'keywords': [], 'trait': ''})
    
    short_summary = f"{sun_data['short']}"
    if not unknown_time:
        short_summary += f"（第一印象は{asc_data['short']}）"
    
    long_text = f"あなたの核となる性格は「{sun_sign}」。{sun_data['trait']}です。\n\n"
    if not unknown_time:
        long_text += f"一方、初対面の人に与える印象は「{asc_sign}」の特徴を持っています。{asc_data['trait']}という一面が、人からは見えやすいでしょう。"
    else:
        long_text += "※出生時刻が不明のため、第一印象（アセンダント）の解釈は含まれていません。"
    
    keywords = sun_data['keywords']
    if not unknown_time:
        keywords = list(set(sun_data['keywords'] + asc_data['keywords']))[:4]
    
    return {'short': short_summary, 'long': long_text, 'keywords': keywords}


def _get_love_summary(venus, moon_sign):
    """恋愛カテゴリの解釈を生成"""
    venus_love = {
        '牡羊座': {'style': '情熱的で積極的', 'partner': '刺激的で独立した人', 'short': '追いかける恋が好き'},
        '牡牛座': {'style': '一途で官能的', 'partner': '安定感があり信頼できる人', 'short': 'ゆっくり深める愛'},
        '双子座': {'style': '軽やかで知的', 'partner': '会話が楽しく飽きさせない人', 'short': '会話で繋がる恋'},
        '蟹座': {'style': '家庭的で献身的', 'partner': '家族を大切にする人', 'short': '守り守られる愛'},
        '獅子座': {'style': 'ロマンチックでドラマティック', 'partner': '自分を称えてくれる人', 'short': '華やかなロマンス'},
        '乙女座': {'style': '実直で献身的', 'partner': '誠実で信頼できる人', 'short': '行動で示す愛'},
        '天秤座': {'style': '調和を重んじロマンティック', 'partner': '美意識が高くバランスの取れた人', 'short': '理想的なパートナーシップ'},
        '蠍座': {'style': '深く情熱的', 'partner': '100%心を開ける人', 'short': '魂レベルの絆'},
        '射手座': {'style': '自由で冒険的', 'partner': '一緒に冒険できる友のような人', 'short': '自由を共有する愛'},
        '山羊座': {'style': '真面目で長期志向', 'partner': '社会的に信頼できる人', 'short': '将来を見据えた恋'},
        '水瓶座': {'style': '独立的で友情ベース', 'partner': '自立心があり理解ある人', 'short': '友情から始まる愛'},
        '魚座': {'style': 'ロマンチックで献身的', 'partner': '魂で繋がれる人', 'short': '運命の愛を信じる'}
    }
    
    moon_emotion = {
        '牡羊座': '感情表現がストレート',
        '牡牛座': '安心感を求める',
        '双子座': '話し合いで安心する',
        '蟹座': '守られたい気持ちが強い',
        '獅子座': '愛情表現を求める',
        '乙女座': '実際の行動を重視',
        '天秤座': 'パートナーと共にいたい',
        '蠍座': '深い絆を求める',
        '射手座': '自由を尊重してほしい',
        '山羊座': '信頼と安定を求める',
        '水瓶座': '独自の空間も必要',
        '魚座': '情緒的な繋がりを重視'
    }
    
    venus_sign = venus.sign_jp if venus else '不明'
    venus_data = venus_love.get(venus_sign, {'style': '', 'partner': '', 'short': ''})
    moon_data = moon_emotion.get(moon_sign, '')
    
    short = venus_data.get('short', f'{venus_sign}の金星')
    long_text = f"【恋愛スタイル】{venus_data.get('style', '')}なタイプです。\n\n"
    long_text += f"【理想のパートナー】{venus_data.get('partner', '')}\n\n"
    long_text += f"【心が求めるもの】月が{moon_sign}にあるため、{moon_data}傾向があります。"
    
    keywords = ['恋愛', venus_data.get('short', '')[:4] if venus_data.get('short') else '', moon_sign]
    keywords = [k for k in keywords if k]
    
    return {'short': short, 'long': long_text, 'keywords': keywords}


def _get_money_summary(chart, jupiter, saturn, unknown_time):
    """金運・仕事運カテゴリの解釈を生成"""
    mc_sign = chart.midheaven.get('sign_jp', '') if hasattr(chart, 'midheaven') and chart.midheaven else ''
    
    career_by_mc = {
        '牡羊座': {'career': 'リーダー・起業家・スポーツ関連', 'style': '先頭に立って道を切り開く'},
        '牡牛座': {'career': '金融・美術・食品関連', 'style': '堅実に信頼を積み上げる'},
        '双子座': {'career': 'メディア・教育・営業', 'style': 'コミュニケーション力を活かす'},
        '蟹座': {'career': '介護・飲食・不動産', 'style': '人を育て守る仕事'},
        '獅子座': {'career': 'エンタメ・芸術・マネジメント', 'style': '注目を浴びる立場で輝く'},
        '乙女座': {'career': '医療・分析・品質管理', 'style': '細部まで完璧を追求する'},
        '天秤座': {'career': '法律・外交・デザイン', 'style': '人と人を繋ぎ調整する'},
        '蠍座': {'career': '調査・心理・投資', 'style': '深く掘り下げ変革する'},
        '射手座': {'career': '教育・出版・旅行業', 'style': '広い世界に知識を広める'},
        '山羊座': {'career': '経営・政治・建築', 'style': '組織のトップで責任を担う'},
        '水瓶座': {'career': 'IT・科学・社会活動', 'style': '革新的なアイデアで変革する'},
        '魚座': {'career': '芸術・ヒーリング・福祉', 'style': '人を癒し夢を与える'}
    }
    
    jupiter_sign = jupiter.sign_jp if jupiter else ''
    fortune_areas = {
        '牡羊座': '起業・独立で成功',
        '牡牛座': '資産形成・美術投資',
        '双子座': '情報・人脈で成功',
        '蟹座': '不動産・家業',
        '獅子座': 'クリエイティブ事業',
        '乙女座': '実務・健康ビジネス',
        '天秤座': 'パートナーシップ事業',
        '蠍座': '投資・相続',
        '射手座': '海外・教育ビジネス',
        '山羊座': '大企業・長期投資',
        '水瓶座': 'テクノロジー・SNS',
        '魚座': '芸術・スピリチュアル'
    }
    
    mc_data = career_by_mc.get(mc_sign, {'career': '', 'style': ''})
    fortune_area = fortune_areas.get(jupiter_sign, '')
    
    if unknown_time:
        short = f"幸運分野: {fortune_area[:10]}..." if fortune_area else "金運"
        long_text = f"【幸運の分野】木星が{jupiter_sign}にあるため、{fortune_area}に恵まれやすいです。\n\n"
        long_text += "※出生時刻が不明のため、適職（MC）の詳細分析は含まれていません。"
    else:
        short = mc_data.get('style', '')[:15] + '型'
        long_text = f"【適職・天職】MCが{mc_sign}にあるため、{mc_data.get('style', '')}キャリアが向いています。\n\n"
        long_text += f"【おすすめの職種】{mc_data.get('career', '')}\n\n"
        long_text += f"【幸運の分野】木星が{jupiter_sign}にあるため、{fortune_area}に恵まれやすいです。"
    
    keywords = ['仕事運', '金運', mc_sign if not unknown_time else jupiter_sign]
    
    return {'short': short, 'long': long_text, 'keywords': keywords}


def _get_communication_summary(mercury):
    """思考・コミュニケーションカテゴリの解釈を生成"""
    mercury_styles = {
        '牡羊座': {'short': 'スピード重視・直感型', 'long': '結論を早く出し、ストレートに伝えます。回りくどい話は苦手。', 'keywords': ['直感', '即決', 'ストレート']},
        '牡牛座': {'short': 'じっくり型・実践的', 'long': '考えを熟成させてから発言。実用的で地に足のついた思考。', 'keywords': ['熟考', '実用的', '着実']},
        '双子座': {'short': 'マルチタスク・話し上手', 'long': '複数のことを同時に考え、言葉巧みに表現。情報収集が得意。', 'keywords': ['多才', '話し上手', '情報通']},
        '蟹座': {'short': '共感型・記憶力抜群', 'long': '感情と思考が結びつき、過去を覚えている。相手の気持ちを察する。', 'keywords': ['共感', '記憶力', '察する']},
        '獅子座': {'short': '表現力豊か・プレゼン上手', 'long': 'ドラマティックに伝える才能。自信を持って意見を述べる。', 'keywords': ['表現力', '自信', 'プレゼン']},
        '乙女座': {'short': '分析的・論理的', 'long': '細部まで検討し、論理的に整理。批評的な視点を持つ。', 'keywords': ['分析', '論理', '緻密']},
        '天秤座': {'short': 'バランス型・外交的', 'long': '相手の立場も考慮し、公平に判断。人当たりの良い話し方。', 'keywords': ['公平', '外交的', 'バランス']},
        '蠍座': {'short': '洞察型・核心を突く', 'long': '表面下を見抜き、本質的な議論を好む。秘密を守る。', 'keywords': ['洞察', '深い', '秘密主義']},
        '射手座': {'short': '大局観・哲学的', 'long': '広い視野で考え、意味を探求。率直で楽観的な話し方。', 'keywords': ['哲学', '大局観', '率直']},
        '山羊座': {'short': '戦略的・目標志向', 'long': '実現可能な計画を立て、責任ある発言をする。無駄を嫌う。', 'keywords': ['戦略', '責任感', '効率']},
        '水瓶座': {'short': '革新的・独創的', 'long': '型破りな発想を持ち、未来志向。客観的で論理的。', 'keywords': ['独創的', '未来志向', '客観的']},
        '魚座': {'short': '直感的・詩的', 'long': '言葉にならない感覚で理解し、イメージで思考する。詩的表現。', 'keywords': ['直感', '詩的', 'イメージ']}
    }
    
    if not mercury:
        return {'short': '不明', 'long': '', 'keywords': []}
    
    mercury_sign = mercury.sign_jp
    data = mercury_styles.get(mercury_sign, {'short': mercury_sign, 'long': '', 'keywords': []})
    
    return {
        'short': data['short'],
        'long': f"水星が{mercury_sign}にあるあなたは、{data['long']}",
        'keywords': data['keywords']
    }


def _get_action_summary(mars):
    """行動力・エネルギーカテゴリの解釈を生成"""
    mars_styles = {
        '牡羊座': {'short': '即断即決・突撃型', 'long': '思い立ったらすぐ行動。競争心が強く、チャレンジ精神旺盛。', 'keywords': ['即行動', '競争', 'チャレンジ']},
        '牡牛座': {'short': 'ゆっくり確実・持続型', 'long': '始動は遅いが一度動けば止まらない。粘り強く継続する力。', 'keywords': ['持続力', '粘り強い', '着実']},
        '双子座': {'short': 'マルチ行動・器用型', 'long': '複数のことを同時にこなす。言葉で戦う傾向。興味が移りやすい。', 'keywords': ['器用', 'マルチ', '言葉で勝負']},
        '蟹座': {'short': '守るための行動・感情型', 'long': '大切な人のために動く。感情が行動の原動力。', 'keywords': ['守る', '感情', '家族のため']},
        '獅子座': {'short': '堂々と行動・リーダー型', 'long': '情熱的で大胆。注目を集める行動を取る。プライド高い。', 'keywords': ['堂々', '大胆', 'リーダー']},
        '乙女座': {'short': '計画的・効率型', 'long': '計画を立ててから行動。完璧を目指し細部に気を配る。', 'keywords': ['計画的', '効率', '完璧主義']},
        '天秤座': {'short': '協調行動・調整型', 'long': 'チームで動くことを好む。対立を避け、調整役に回る。', 'keywords': ['協調', '調整', 'チームワーク']},
        '蠍座': {'short': '徹底的・戦略型', 'long': '目標に向かって執念深く行動。戦略的で全力投球。', 'keywords': ['徹底的', '戦略', '執念']},
        '射手座': {'short': '冒険的・直感型', 'long': '広いフィールドで自由に動く。スケールの大きな行動。', 'keywords': ['冒険', '自由', '大きな目標']},
        '山羊座': {'short': '計画的・野心型', 'long': '長期目標に向かって規律正しく行動。責任感が原動力。', 'keywords': ['計画', '野心', '責任']},
        '水瓶座': {'short': '独自路線・革新型', 'long': '型破りな方法で行動。大義のために動く改革者。', 'keywords': ['独自', '革新', '大義']},
        '魚座': {'short': '直感行動・奉仕型', 'long': '直感に導かれて動く。他者を助けるための行動が多い。', 'keywords': ['直感', '奉仕', '共感']}
    }
    
    if not mars:
        return {'short': '不明', 'long': '', 'keywords': []}
    
    mars_sign = mars.sign_jp
    data = mars_styles.get(mars_sign, {'short': mars_sign, 'long': '', 'keywords': []})
    
    return {
        'short': data['short'],
        'long': f"火星が{mars_sign}にあるあなたは、{data['long']}",
        'keywords': data['keywords']
    }


def _get_fortune_summary(jupiter):
    """幸運と成長カテゴリの解釈を生成"""
    jupiter_fortune = {
        '牡羊座': {'short': '挑戦と独立で幸運', 'long': '新しいことに挑戦するほど運が開けます。リーダーシップを発揮する場面で幸運に恵まれます。', 'keywords': ['挑戦', '独立', 'リーダー']},
        '牡牛座': {'short': '資産形成で幸運', 'long': '物質的な豊かさを築く才能があります。芸術や美に関する分野でも恵まれます。', 'keywords': ['資産', '芸術', '安定']},
        '双子座': {'short': '学びと人脈で幸運', 'long': '多様な人脈と情報が幸運を運びます。教育やメディア関連で成功しやすいです。', 'keywords': ['学習', '人脈', '情報']},
        '蟹座': {'short': '家庭と不動産で幸運', 'long': '家族を通じて恵みを受けます。不動産投資や家業にも良い運があります。', 'keywords': ['家庭', '不動産', '育成']},
        '獅子座': {'short': '創造と表現で幸運', 'long': 'クリエイティブな活動で幸運に恵まれます。子供に関することでも良い運。', 'keywords': ['創造', '表現', 'エンタメ']},
        '乙女座': {'short': '実務と健康で幸運', 'long': '仕事の効率化や健康ビジネスで成功しやすいです。細かい作業が実を結びます。', 'keywords': ['実務', '健康', 'サービス']},
        '天秤座': {'short': 'パートナーシップで幸運', 'long': '良いパートナーとの出会いに恵まれます。外交や法律関係も吉。', 'keywords': ['協力', '結婚', '契約']},
        '蠍座': {'short': '変革と投資で幸運', 'long': '変化を恐れず飛び込むことで幸運が訪れます。投資や相続にも恵まれる可能性。', 'keywords': ['投資', '変革', '深い絆']},
        '射手座': {'short': '海外と教育で幸運', 'long': '旅行や海外との関わりで運が開けます。高等教育や出版も吉。', 'keywords': ['海外', '教育', '冒険']},
        '山羊座': {'short': 'キャリアで幸運', 'long': '仕事での成功に恵まれます。時間をかけた努力が大きな成果に。', 'keywords': ['キャリア', '責任', '長期']},
        '水瓶座': {'short': 'テクノロジーと仲間で幸運', 'long': 'IT分野や社会活動で運が開けます。友人やコミュニティを通じた恵み。', 'keywords': ['IT', '友人', '革新']},
        '魚座': {'short': '芸術とスピリチュアルで幸運', 'long': '芸術、音楽、スピリチュアルな分野で恵まれます。癒しと共感の才能。', 'keywords': ['芸術', '癒し', '直感']}
    }
    
    if not jupiter:
        return {'short': '不明', 'long': '', 'keywords': []}
    
    jupiter_sign = jupiter.sign_jp
    data = jupiter_fortune.get(jupiter_sign, {'short': jupiter_sign, 'long': '', 'keywords': []})
    
    return {
        'short': data['short'],
        'long': f"木星が{jupiter_sign}にあるため、{data['long']}",
        'keywords': data['keywords']
    }


def _get_challenge_summary(saturn):
    """課題と成長カテゴリの解釈を生成"""
    saturn_challenge = {
        '牡羊座': {'short': '自己主張の課題', 'long': '自分を押し出すことに抵抗を感じるかもしれませんが、これを乗り越えると真の強さが身につきます。', 'keywords': ['自己主張', 'リーダーシップ', '勇気']},
        '牡牛座': {'short': '物質への執着の課題', 'long': 'お金や物への不安を感じやすいですが、克服すると持続可能な豊かさを築けます。', 'keywords': ['お金', '所有', '価値観']},
        '双子座': {'short': 'コミュニケーションの課題', 'long': '表現することに苦手意識があるかもしれませんが、努力で優れた伝達者になれます。', 'keywords': ['表現', '学習', '伝達']},
        '蟹座': {'short': '感情表現の課題', 'long': '感情を見せることに壁を感じるかもしれませんが、これを克服すると深い絆が生まれます。', 'keywords': ['感情', '家族', '安心感']},
        '獅子座': {'short': '自己表現の課題', 'long': '自分を表現することに抵抗があるかもしれませんが、時間をかけて自信を築けます。', 'keywords': ['自信', '創造性', '認知']},
        '乙女座': {'short': '完璧主義の課題', 'long': '自分に厳しすぎる傾向がありますが、「十分に良い」を受け入れることで楽になります。', 'keywords': ['完璧主義', '自己批判', '奉仕']},
        '天秤座': {'short': '人間関係の課題', 'long': '関係性において責任を学びます。公平さを追求することで優れた調停者になれます。', 'keywords': ['関係性', '公平', '責任']},
        '蠍座': {'short': '信頼の課題', 'long': '人を信頼することに時間がかかるかもしれませんが、克服すると深い絆を築けます。', 'keywords': ['信頼', '親密さ', 'コントロール']},
        '射手座': {'short': '楽観主義の壁', 'long': '自由と責任のバランスを学びます。現実的な知恵を持つ賢者になれます。', 'keywords': ['責任', '現実', '信念']},
        '山羊座': {'short': 'キャリアの課題', 'long': '仕事での成功に時間がかかりますが、忍耐が報われ大きな達成を遂げられます。', 'keywords': ['キャリア', '忍耐', '達成']},
        '水瓶座': {'short': '個性と社会の課題', 'long': '自分らしさと社会の期待の間で葛藤するかもしれませんが、両立できます。', 'keywords': ['個性', '社会', '改革']},
        '魚座': {'short': '境界線の課題', 'long': '現実と理想の間でバランスを取ることを学びます。地に足のついた霊性を目指せます。', 'keywords': ['境界線', '現実', '霊性']}
    }
    
    if not saturn:
        return {'short': '不明', 'long': '', 'keywords': []}
    
    saturn_sign = saturn.sign_jp
    data = saturn_challenge.get(saturn_sign, {'short': saturn_sign, 'long': '', 'keywords': []})
    
    return {
        'short': data['short'],
        'long': f"土星が{saturn_sign}にあるため、{data['long']}この課題を克服することで、大きな成長を遂げられます。",
        'keywords': data['keywords']
    }


def get_sun_house_meaning(house):
    """太陽のハウス配置の意味"""
    meanings = {
        '1': '1ハウスの太陽は、強いアイデンティティと自己表現力を示します。あなたは自分自身であることにエネルギーを注ぎ、存在感があります。リーダーシップを発揮しやすく、自己主張が得意です。',
        '2': '2ハウスの太陽は、物質的な安定と自己価値を重視します。お金を稼ぐことや所有物に関心があり、資源を築くことに才能があります。自分の価値を認められることが重要です。',
        '3': '3ハウスの太陽は、コミュニケーションと学習に輝きます。話すこと、書くこと、教えることに才能があります。兄弟姉妹や近所との関係も重要なテーマです。',
        '4': '4ハウスの太陽は、家庭と家族が人生の中心です。ルーツや伝統を大切にし、安心できる居場所を築くことに力を注ぎます。晩年に輝く傾向があります。',
        '5': '5ハウスの太陽は、創造性と自己表現で輝きます。芸術、趣味、恋愛、子供に関することで喜びを見出します。人生を楽しむことが大切です。',
        '6': '6ハウスの太陽は、仕事と健康に焦点を当てます。日々のルーティンを通じて自己を表現し、奉仕や改善に喜びを感じます。健康管理も重要なテーマです。',
        '7': '7ハウスの太陽は、パートナーシップを通じて輝きます。1対1の関係性があなたのアイデンティティに大きく影響します。結婚や契約関係が人生の重要なテーマです。',
        '8': '8ハウスの太陽は、深い変容と再生に関わります。心理学、オカルト、他者の資源に関心があります。人生の深い側面を探求することで輝きます。',
        '9': '9ハウスの太陽は、哲学と冒険で輝きます。高等教育、旅行、宗教、法律に関心があります。人生の意味を探求することがテーマです。',
        '10': '10ハウスの太陽は、キャリアと社会的地位で輝きます。仕事での成功と認知を強く求めます。権威的な立場に立つ可能性が高いです。',
        '11': '11ハウスの太陽は、グループと理想で輝きます。友人関係、組織活動、社会的理想の追求が人生のテーマです。未来志向で革新的です。',
        '12': '12ハウスの太陽は、霊的な成長と無意識の探求に関わります。瞑想、芸術、奉仕活動を通じて輝きます。舞台裏で働くことも得意です。'
    }
    house_num = str(house).replace('ハウス', '').replace('House', '').strip()
    return meanings.get(house_num, '')


def get_moon_house_meaning(house):
    """月のハウス配置の意味"""
    meanings = {
        '1': '1ハウスの月は、感情が表に出やすく、ムードが外見に表れます。直感的で、環境に敏感に反応します。母性的な印象を与えることが多いです。',
        '2': '2ハウスの月は、物質的な安定が感情の安定に直結します。お金や所有物に対して感情的なつながりを感じます。安心できる財政状況を求めます。',
        '3': '3ハウスの月は、言葉や情報に感情的に反応します。話すことで感情を処理し、兄弟姉妹との絆が深いです。知的刺激が感情の安定に必要です。',
        '4': '4ハウスの月は、家庭が感情の基盤です。家族、特に母親との関係が深く影響します。居心地の良い家を持つことが重要です。',
        '5': '5ハウスの月は、創造的な表現と楽しみを通じて感情を発散します。恋愛に情熱的で、子供（または創作活動）に深い愛着を持ちます。',
        '6': '6ハウスの月は、日常のルーティンと仕事に感情的な満足を求めます。役に立つことで安心し、健康状態が感情に影響します。',
        '7': '7ハウスの月は、パートナーシップで感情的な安定を得ます。関係性に依存する傾向があり、パートナーの影響を強く受けます。',
        '8': '8ハウスの月は、感情が深く激しいです。信頼と親密さに強い欲求があり、心理的・霊的な事柄に惹かれます。',
        '9': '9ハウスの月は、冒険と学びに感情的な満足を得ます。旅行、異文化、哲学が心を満たします。精神的な成長を求めます。',
        '10': '10ハウスの月は、キャリアと社会的地位に感情を投じます。仕事での認知が感情の安定に影響します。公の場で母性的役割を果たすことも。',
        '11': '11ハウスの月は、友人やグループから感情的なサポートを得ます。社会的理想に情熱を感じ、コミュニティへの帰属意識が重要です。',
        '12': '12ハウスの月は、感情を隠す傾向があり、孤独を必要とします。直感が強く、霊的な感受性があります。過去の記憶が感情に影響します。'
    }
    house_num = str(house).replace('ハウス', '').replace('House', '').strip()
    return meanings.get(house_num, '')


def get_sun_detailed(sign):
    """太陽星座の詳細解釈"""
    meanings = {
        '牡羊座': 'あなたの魂は「開拓者」です。常に新しいフロンティアを求め、誰も踏み入れたことのない領域に飛び込む勇気を持っています。競争心が強く、「一番になりたい」という欲求があなたを駆り立てます。直感的でスピーディーな判断力が武器です。',
        '牡牛座': 'あなたの魂は「創造者」です。五感を通じて世界を深く味わい、物質的な美と安定を追求します。一度始めたことは最後までやり遂げる粘り強さがあり、信頼性が高い存在です。本物の価値を見抜く審美眼を持っています。',
        '双子座': 'あなたの魂は「伝達者」です。情報を収集し、人と人をつなぐ橋渡し役を担います。一つのことに縛られるのが苦手で、常に複数のプロジェクトや興味を持つことで輝きます。言葉の魔術師であり、コミュニケーションの達人です。',
        '蟹座': 'あなたの魂は「養育者」です。大切な人を守り育てることに深い使命感を持っています。感受性が非常に豊かで、他者の痛みを自分のことのように感じ取ります。家庭や仲間との絆があなたのパワーの源です。',
        '獅子座': 'あなたの魂は「王/女王」です。生まれながらにして人の中心に立つ資質を持ち、自らの光で周囲を照らします。創造性と自己表現への欲求が強く、ドラマティックな人生を歩む傾向があります。寛大さと誇り高さが魅力です。',
        '乙女座': 'あなたの魂は「奉仕者」です。細部まで気を配り、物事を完璧に仕上げる能力を持っています。健康や実用性に関心が高く、日常生活を向上させることに喜びを見出します。分析力と改善力があなたの強みです。',
        '天秤座': 'あなたの魂は「調停者」です。美とバランスを追求し、人間関係における調和を大切にします。他者の視点を理解する能力に優れ、公平な判断ができます。パートナーシップを通じて自己を発見していくタイプです。',
        '蠍座': 'あなたの魂は「変容者」です。表面的なことに満足せず、物事の本質を見抜こうとします。一度コミットしたら徹底的に取り組む集中力と、危機を乗り越えて再生する力を持っています。深い絆と真実を求めます。',
        '射手座': 'あなたの魂は「探求者」です。真理と自由を求めて人生という冒険を進みます。視野が広く、異なる文化や思想に興味を持ちます。楽観主義と哲学的な視点があなたの人生を彩ります。教育や旅が魂を成長させます。',
        '山羊座': 'あなたの魂は「建設者」です。長期的なビジョンを持ち、着実に成功への階段を登ります。責任感が強く、社会的な達成を重要視します。自己規律と忍耐力で、時間をかけて偉業を成し遂げるタイプです。',
        '水瓶座': 'あなたの魂は「革命家」です。既存のルールに縛られず、より良い未来のための新しいシステムを追求します。人道主義的な理想を持ち、個性と自由を大切にします。グループや社会のために革新をもたらす使命があります。',
        '魚座': 'あなたの魂は「夢見人」です。現実と夢の境界を自在に行き来し、芸術的・霊的な感性が豊かです。すべての存在とのつながりを感じ、深い共感力を持っています。癒しと創造の才能に恵まれています。'
    }
    return meanings.get(sign, '')


def get_sun_life_path(sign):
    """太陽星座の人生テーマ"""
    paths = {
        '牡羊座': '人生のテーマは「自己確立」。自分らしさを貫き、道を切り開くことで成長します。恐れずに挑戦することが、あなたの魂の成長につながります。',
        '牡牛座': '人生のテーマは「価値の創造」。本当に大切なものを見極め、それを育てることで満足を得ます。急がず、着実に歩むことが成功の鍵です。',
        '双子座': '人生のテーマは「知識の統合」。多様な経験と学びを通じて、ユニークな視点を築きます。好奇心を追求することが、あなたの道を照らします。',
        '蟹座': '人生のテーマは「感情的な安全」。心の居場所を見つけ、守ることで強さを発揮します。過去を大切にしながら未来を築くことが課題です。',
        '獅子座': '人生のテーマは「創造的な自己表現」。あなたの輝きを世界に示すことが使命です。謙虚さと誇りのバランスを取ることで、真のリーダーになれます。',
        '乙女座': '人生のテーマは「完成と奉仕」。スキルを磨き、他者の役に立つことで充実を得ます。完璧主義を手放し、"十分に良い"を受け入れることも学びです。',
        '天秤座': '人生のテーマは「関係性とバランス」。他者との関わりの中で自己を発見します。自分の意見をしっかり持つことと、調和を両立させることが課題です。',
        '蠍座': '人生のテーマは「変容と再生」。人生の深い谷を経験することで、より強い自分に生まれ変わります。手放すことと信頼することが鍵です。',
        '射手座': '人生のテーマは「意味の探求」。経験と学びを通じて人生の意味を見出します。自由を守りながらコミットメントを学ぶことが課題です。',
        '山羊座': '人生のテーマは「社会的達成」。努力と忍耐で頂点を目指します。成功だけでなく、その過程も楽しむことを忘れないでください。',
        '水瓶座': '人生のテーマは「変革と貢献」。社会をより良くするためのビジョンを持っています。個性を保ちながら仲間と協力することが成長のポイントです。',
        '魚座': '人生のテーマは「超越と癒し」。物質世界を超えた領域とつながり、他者を癒す力があります。現実と夢のバランスを取ることが課題です。'
    }
    return paths.get(sign, '')


def get_moon_detailed(sign):
    """月星座の詳細解釈"""
    meanings = {
        '牡羊座': '心の奥底で、あなたは常に「自分らしくありたい」と願っています。感情が昂ると即座に行動に移す傾向があり、待つことが苦手です。自立した環境で最も安心を感じます。怒りが爆発的に出やすいですが、すぐに収まります。',
        '牡牛座': '心の奥底で、あなたは「安定と心地よさ」を求めています。慣れ親しんだものに安心を感じ、変化には時間をかけて適応します。五感を満たすこと（美味しい食事、心地よい音楽、自然）が心のケアになります。',
        '双子座': '心の奥底で、あなたは「知りたい、話したい」と願っています。感情を言語化することで処理し、誰かに聞いてもらうことで落ち着きます。退屈が最大の敵で、刺激と変化を求めます。感情の切り替えが早いのが特徴です。',
        '蟹座': '心の奥底で、あなたは「守られたい、守りたい」と願っています。家族や親しい人への愛着が非常に強く、別離に敏感です。過去の思い出を大切にし、感情の波が月の満ち欠けのように周期的に変化します。',
        '獅子座': '心の奥底で、あなたは「認められたい、愛されたい」と願っています。注目されることで生き生きとし、創造的な表現で感情を発散します。プライドが高く、批判されると深く傷つきますが、基本的に寛大で温かい心を持っています。',
        '乙女座': '心の奥底で、あなたは「役に立ちたい、秩序が欲しい」と願っています。感情を分析的に処理し、問題を解決することで安心します。完璧主義的な傾向があり、自分にも他者にも厳しいですが、根は思いやりに溢れています。',
        '天秤座': '心の奥底で、あなたは「調和と美しい関係」を求めています。一人でいることが苦手で、パートナーがいることで安定します。対立を避け、公平であることを大切にします。美的なものに囲まれていると心が落ち着きます。',
        '蠍座': '心の奥底で、あなたは「深い絆と真実」を求めています。感情が非常に深く激しく、一度傷つくと長く記憶しています。信頼した相手には全身全霊で尽くしますが、裏切りは決して許しません。',
        '射手座': '心の奥底で、あなたは「自由と冒険」を求めています。楽観的で、未来に希望を持つことで安心します。束縛を嫌い、広い世界を探検することで感情が満たされます。哲学や宗教に慰めを見出すこともあります。',
        '山羊座': '心の奥底で、あなたは「成果と認められること」を求めています。感情を表に出すのが苦手で、自己コントロールを重視します。責任を果たし、社会的に成功することで安心を得ます。実は繊細な一面を隠しています。',
        '水瓶座': '心の奥底で、あなたは「独立と理解」を求めています。感情的に客観的で、自分の感情を一歩引いて観察する傾向があります。「普通」であることを嫌い、ユニークであることに誇りを持っています。',
        '魚座': '心の奥底で、あなたは「つながりと救い」を求めています。非常に敏感で、他者の感情を吸収してしまうことも。現実逃避の傾向がありますが、直感と想像力は驚異的です。芸術や音楽、スピリチュアルな活動が心を癒します。'
    }
    return meanings.get(sign, '')


def get_moon_needs(sign):
    """月星座の感情的ニーズ"""
    needs = {
        '牡羊座': '感情的な安定のために、新しいチャレンジとアクションが必要です。じっとしていると落ち着かなくなります。',
        '牡牛座': '感情的な安定のために、物理的な安心と慣れ親しんだルーティンが必要です。急激な変化は避けたいタイプです。',
        '双子座': '感情的な安定のために、会話と知的刺激が必要です。考えを言葉にして整理することで落ち着きます。',
        '蟹座': '感情的な安定のために、家庭的な安心感と親しい人のそばにいることが必要です。',
        '獅子座': '感情的な安定のために、愛情表現と創造的な活動が必要です。認められることで輝きます。',
        '乙女座': '感情的な安定のために、整理整頓と有用な仕事が必要です。何か役に立っている実感が重要です。',
        '天秤座': '感情的な安定のために、美しい環境とハーモニーのある人間関係が必要です。',
        '蠍座': '感情的な安定のために、深い信頼関係と真正性が必要です。表面的な付き合いでは満足できません。',
        '射手座': '感情的な安定のために、希望と可能性を感じられることが必要です。閉じ込められると息苦しくなります。',
        '山羊座': '感情的な安定のために、目標と達成感が必要です。計画通りに進むことで安心します。',
        '水瓶座': '感情的な安定のために、個性と自由を認めてもらうことが必要です。理解し合える仲間も大切です。',
        '魚座': '感情的な安定のために、安らぎと霊的なつながりが必要です。音楽や芸術が癒しになります。'
    }
    return needs.get(sign, '')


def get_asc_detailed(sign):
    """アセンダントの詳細解釈"""
    meanings = {
        '牡羊座': '初対面であなたは、エネルギッシュで活発、やや競争的な印象を与えます。行動的で率直なアプローチを取り、まずやってみることを好みます。顔立ちやオーラに、どこか戦士のような鋭さがあるかもしれません。',
        '牡牛座': '初対面であなたは、落ち着いて安定感のある印象を与えます。ゆったりとしたペースと穏やかな雰囲気で、人を安心させます。センスが良く、上質なものを好む傾向が外見にも表れます。',
        '双子座': '初対面であなたは、快活で機敏、好奇心旺盛な印象を与えます。話し上手で、様々な話題に対応できる柔軟性があります。若々しく見られることが多く、永遠の学生のような雰囲気を持っています。',
        '蟹座': '初対面であなたは、親しみやすく温かい印象を与えます。保護的で共感力があり、相手を安心させる雰囲気があります。丸みを帯びた優しい外見や、守りたくなるような雰囲気を持っているかもしれません。',
        '獅子座': '初対面であなたは、自信に満ちた華やかな印象を与えます。存在感があり、自然と人の注目を集めます。姿勢が良く、堂々とした振る舞いで、リーダーシップを感じさせます。',
        '乙女座': '初対面であなたは、知的で控えめ、きちんとした印象を与えます。細部に気を配り、清潔感があります。はじめは少し距離を置くタイプですが、信頼できる実務的な人という印象です。',
        '天秤座': '初対面であなたは、優雅で洗練された印象を与えます。人当たりが良く、バランスの取れた対応をします。美的センスに優れ、調和の取れた外見を持っていることが多いです。',
        '蠍座': '初対面であなたは、神秘的で深みのある印象を与えます。目力が強く、見透かすような視線を持っています。静かですがポーカーフェイスの奥に強い情熱を秘めています。',
        '射手座': '初対面であなたは、陽気でオープン、冒険心のある印象を与えます。率直で、気さくに話しかけることができます。背が高い、または大きなジェスチャーで存在感を示すタイプです。',
        '山羊座': '初対面であなたは、真面目で信頼できる印象を与えます。年齢より落ち着いて見られることが多く、野心的でしっかりした人という印象です。骨格がしっかりした外見を持つことも。',
        '水瓶座': '初対面であなたは、個性的でどこか変わった印象を与えます。普通とは違う何かを持っていて、独自のスタイルがあります。フレンドリーですが、どこか一歩距離を置いています。',
        '魚座': '初対面であなたは、夢見るような柔らかい印象を与えます。境界線が曖昧なところがあり、とらえどころがないとも言えます。どこか儚げで、芸術的な雰囲気を持っています。'
    }
    return meanings.get(sign, '')


def get_mercury_interpretation(planet):
    """水星の解釈"""
    if not planet:
        return ''
    sign = planet.sign_jp
    meanings = {
        '牡羊座': 'あなたの思考は直感的でスピーディー。結論に早く到達しますが、細部を見落とすことも。正直で率直なコミュニケーションスタイルです。',
        '牡牛座': 'あなたの思考は着実で実用的。時間をかけて考えを熟成させ、一度決めたことはなかなか変えません。具体的で現実的な話し方をします。',
        '双子座': 'あなたの思考は機敏で多面的。複数のことを同時に考え、情報を素早く処理します。話し上手で、言葉を巧みに操ります。',
        '蟹座': 'あなたの思考は感情と結びついています。記憶力が良く、過去の経験から学びます。繊細な言葉遣いで、相手の気持ちを考慮したコミュニケーションをします。',
        '獅子座': 'あなたの思考は創造的でドラマティック。自己表現力に優れ、プレゼンテーションが得意です。自信を持って意見を述べます。',
        '乙女座': 'あなたの思考は分析的で細部に注意。論理的で、事実に基づいた議論を好みます。批評的な視点を持ち、改善点を見つけるのが得意です。',
        '天秤座': 'あなたの思考は公平でバランスを重視。すべての側面を考慮し、外交的なコミュニケーションをします。対話を通じてアイデアを発展させます。',
        '蠍座': 'あなたの思考は深く洞察力があります。表面下を見抜き、隠された真実を探ります。言葉を慎重に選び、核心を突く発言をします。',
        '射手座': 'あなたの思考は広範で哲学的。大局的な視点を持ち、率直に意見を述べます。学ぶことへの情熱があり、知識を共有したがります。',
        '山羊座': 'あなたの思考は構造的で目標志向。戦略的に物事を考え、実現可能な計画を立てます。権威ある発言スタイルです。',
        '水瓶座': 'あなたの思考は独創的で革新的。型破りなアイデアを持ち、未来志向の発想をします。客観的で理性的なコミュニケーションを好みます。',
        '魚座': 'あなたの思考は直感的で想像力豊か。言葉にならない感覚やイメージで理解します。詩的な表現力を持っています。'
    }
    return meanings.get(sign, f'{sign}の水星')


def get_venus_interpretation(planet):
    """金星の解釈"""
    if not planet:
        return ''
    sign = planet.sign_jp
    meanings = {
        '牡羊座': '恋愛では積極的に追いかけるタイプ。情熱的で、刺激的な関係を求めます。独立した相手に惹かれ、駆け引きよりも直球勝負を好みます。',
        '牡牛座': '恋愛では安定と官能的な喜びを求めます。一途で忠実、ゆっくりと絆を深めていきます。物質的な安心感も大切にします。',
        '双子座': '恋愛では知的なつながりを重視。会話が楽しい相手に惹かれます。バラエティを好み、マンネリを避けたいタイプです。',
        '蟹座': '恋愛では感情的な安全と家庭的な温かさを求めます。世話好きで、相手を大切に守ります。過保護になることもあります。',
        '獅子座': '恋愛ではロマンチックでドラマティックな関係を求めます。愛情表現が豊かで、大げさなジェスチャーで愛を示します。注目される恋愛を楽しみます。',
        '乙女座': '恋愛では実用的で献身的。小さな行動で愛を示し、相手の役に立とうとします。完璧を求めるあまり、批判的になることもあります。',
        '天秤座': '恋愛ではパートナーシップを最も重視。調和のとれた美しい関係を求め、ロマンチックな雰囲気を大切にします。相手に合わせすぎることも。',
        '蠍座': '恋愛では深い絆と完全な一体感を求めます。非常に情熱的で、嫉妬深い一面も。すべてを共有したいと望みます。',
        '射手座': '恋愛では自由と冒険を共有できる相手を求めます。束縛を嫌い、友人のようなパートナーシップを好みます。楽観的な恋愛観です。',
        '山羊座': '恋愛では長期的なコミットメントと社会的に適切な関係を求めます。感情表現は控えめですが、忠実で責任感があります。',
        '水瓶座': '恋愛では友情と独立を重視。型破りな関係を恐れず、お互いの自由を尊重します。知的なつながりが愛の土台です。',
        '魚座': '恋愛ではロマンチックで夢見がち。魂のレベルでの結びつきを求め、理想の愛を追い求めます。自己犠牲的になりやすい面もあります。'
    }
    return meanings.get(sign, f'{sign}の金星')


def get_mars_interpretation(planet):
    """火星の解釈"""
    if not planet:
        return ''
    sign = planet.sign_jp
    meanings = {
        '牡羊座': '行動力抜群で、思い立ったらすぐ動きます。競争に燃え、チャレンジ精神旺盛。怒りは瞬間的に爆発しますが、すぐに冷めます。',
        '牡牛座': '行動は着実でゆっくり。一度動き出すと止まりませんが、始動に時間がかかります。怒りを溜め込み、限界を超えると爆発することも。',
        '双子座': '複数のことを同時にこなす器用さがあります。言葉で戦う傾向があり、議論が得意。興味が移りやすく、一つのことを続けるのは苦手かも。',
        '蟹座': '大切な人を守るために行動します。感情が行動の原動力となり、ムードに左右されることも。受動攻撃的な傾向があります。',
        '獅子座': '情熱的で堂々と行動します。リーダーシップを発揮し、大胆なアクションを取ります。プライドが傷つくと激しく反応することも。',
        '乙女座': '計画的で効率的に行動します。完璧を目指して細部まで気を配ります。批判に敏感で、神経質になることもあります。',
        '天秤座': '行動の前に慎重に検討します。協力して物事を進めることを好み、対立を避けたがります。優柔不断に見られることも。',
        '蠍座': '目標に向かって執念深く行動します。戦略的で、必要とあれば激しく戦います。感情をコントロールしますが、内側では激しく燃えています。',
        '射手座': '冒険心に駆られて行動します。行動範囲が広く、スケールの大きなことを好みます。細部を見落としがちなことも。',
        '山羊座': '長期的な目標に向かって規律正しく行動します。野心家で、障害があってもあきらめません。責任感が行動の原動力です。',
        '水瓶座': '型破りで独自の方法で行動します。大義のために戦い、改革を推進します。集団行動も個人プレーもできます。',
        '魚座': '直感に導かれて行動します。他者を助けるために動くことが多いですが、自分のために行動するのは苦手かもしれません。'
    }
    return meanings.get(sign, f'{sign}の火星')


def get_jupiter_interpretation(planet):
    """木星の解釈"""
    if not planet:
        return ''
    sign = planet.sign_jp
    retrograde = planet.retrograde
    meanings = {
        '牡羊座': '【幸運と拡大】新しい挑戦を通じて成長します。リーダーシップを発揮する場面で幸運が訪れやすく、先駆者としての役割に恵まれます。独立や起業にも良い影響。',
        '牡牛座': '【幸運と拡大】物質的な豊かさを築く才能があります。金銭面での幸運に恵まれやすく、芸術や美に関する分野で成功しやすいです。ゆっくりと確実に富を築きます。',
        '双子座': '【幸運と拡大】コミュニケーションと学習を通じて成長します。多様な人脈と情報が幸運を運び、教育、執筆、メディア関連で活躍できます。',
        '蟹座': '【幸運と拡大】家庭と家族を通じて成長します。不動産や食に関する分野で幸運があり、人を育てる・世話をすることで繁栄します。',
        '獅子座': '【幸運と拡大】創造性と自己表現で成長します。エンターテイメント、芸術、子供に関することで幸運に恵まれます。寛大さが人を惹きつけます。',
        '乙女座': '【幸運と拡大】実務能力と奉仕を通じて成長します。健康、仕事の効率化、サービス業で成功しやすいです。細部への配慮が実を結びます。',
        '天秤座': '【幸運と拡大】人間関係とパートナーシップを通じて成長します。結婚、契約、外交に恵まれ、公平さと調和を大切にすることで成功します。',
        '蠍座': '【幸運と拡大】深い変容と再生を通じて成長します。心理学、調査、他者の資源に関わることで成功します。危機を乗り越える力があります。',
        '射手座': '【幸運と拡大】（本来の位置）旅行、高等教育、哲学、出版に幸運があります。視野を広げることで成長し、楽観主義が道を開きます。',
        '山羊座': '【幸運と拡大】キャリアと社会的成功を通じて成長します。ビジネス、政治、組織運営に才能があり、時間をかけて大きな成果を上げます。',
        '水瓶座': '【幸運と拡大】革新とグループ活動を通じて成長します。テクノロジー、社会改革、ネットワークで幸運があります。未来志向が鍵。',
        '魚座': '【幸運と拡大】（高揚の位置）霊性と創造性で成長します。芸術、音楽、スピリチュアル、癒しの分野で恵まれます。無条件の愛と共感が力。'
    }
    result = meanings.get(sign, '')
    if retrograde:
        result += '\n※逆行中: 幸運は外からではなく内面から見つける時期です。過去の機会を見直すことで成長できます。'
    return result


def get_saturn_interpretation(planet):
    """土星の解釈"""
    if not planet:
        return ''
    sign = planet.sign_jp
    retrograde = planet.retrograde
    meanings = {
        '牡羊座': '【責任と試練】自立と主導権に関する課題があります。自分を主張しながらも他者を尊重することを学びます。忍耐力を養う過程で強いリーダーになれます。',
        '牡牛座': '【責任と試練】財政と所有に関する課題があります。持続可能な資産形成と、物質への執着を手放すことを学びます。着実さが報われます。',
        '双子座': '【責任と試練】コミュニケーションと学習に課題があります。浅い知識ではなく深い理解を目指すことで、優れた教師や作家になれます。',
        '蟹座': '【責任と試練】家庭と感情に関する課題があります。感情を成熟させ、家族の責任を引き受けることで、強い守護者になれます。',
        '獅子座': '【責任と試練】自己表現と認知に課題があります。真の自信を築くには時間がかかりますが、努力で得た栄光は永続します。',
        '乙女座': '【責任と試練】仕事と健康に課題があります。完璧主義との闘いがありますが、実務能力の高さは時間とともに認められます。',
        '天秤座': '【責任と試練】（高揚の位置）人間関係に課題がありますが、公正さと調和を学ぶことで、優れた調停者・外交官になれます。',
        '蠍座': '【責任と試練】信頼と親密さに課題があります。コントロール欲求を手放し、脆弱さを受け入れることで深い変容を経験します。',
        '射手座': '【責任と試練】信念と自由に課題があります。無責任な楽観を超え、実践的な知恵を持つ賢者になることが求められます。',
        '山羊座': '【責任と試練】（本来の位置）キャリアと野心に集中します。長期的な成功のために忍耐を続けることで、大きな成果を収めます。',
        '水瓶座': '【責任と試練】（本来の位置）社会と個性に課題があります。革新的でありながら現実的な改革者になることが求められます。',
        '魚座': '【責任と試練】境界線と霊性に課題があります。現実と夢の間でバランスを取り、地に足のついた霊的成長を遂げます。'
    }
    result = meanings.get(sign, '')
    if retrograde:
        result += '\n※逆行中: 内面的な責任と向き合う時期。過去のカルマ的なテーマを解消する機会があります。'
    return result


def get_outer_planets_interpretation(planets):
    """天王星・海王星・冥王星の解釈"""
    result = []
    
    uranus = planets.get('Uranus')
    if uranus:
        result.append(f"【天王星 in {uranus.sign_jp}】これは世代的な配置です。あなたの世代は{_get_uranus_generation(uranus.sign_jp)}を通じて社会に変革をもたらす使命があります。")
    
    neptune = planets.get('Neptune')
    if neptune:
        result.append(f"【海王星 in {neptune.sign_jp}】これは世代的な配置です。あなたの世代は{_get_neptune_generation(neptune.sign_jp)}という集合的な夢を持っています。")
    
    pluto = planets.get('Pluto')
    if pluto:
        result.append(f"【冥王星 in {pluto.sign_jp}】これは世代的な配置です。あなたの世代は{_get_pluto_generation(pluto.sign_jp)}に関する深い変容を体験します。")
    
    return '\n\n'.join(result)


def _get_uranus_generation(sign):
    meanings = {
        '牡羊座': '個人の自由と独立',
        '牡牛座': 'テクノロジーと経済システム',
        '双子座': '情報とコミュニケーション',
        '蟹座': '家族の形態と住居',
        '獅子座': '創造性と自己表現',
        '乙女座': '健康と労働',
        '天秤座': '人間関係と結婚',
        '蠍座': '性と共有資源',
        '射手座': '教育と信仰',
        '山羊座': '政府と社会構造',
        '水瓶座': 'テクノロジーと人道主義',
        '魚座': '霊性と芸術'
    }
    return meanings.get(sign, sign)


def _get_neptune_generation(sign):
    meanings = {
        '牡羊座': '精神的な戦士としての理想',
        '牡牛座': '物質と霊性の融合',
        '双子座': '精神的なコミュニケーション',
        '蟹座': '感情的な癒しと家族の理想',
        '獅子座': '創造的な霊性',
        '乙女座': '奉仕と健康への癒し',
        '天秤座': '理想的な人間関係',
        '蠍座': '深い変容と霊的覚醒',
        '射手座': '信仰と真実の探求',
        '山羊座': '現実的な理想主義',
        '水瓶座': 'デジタルと霊性の融合',
        '魚座': '普遍的な愛と共感'
    }
    return meanings.get(sign, sign)


def _get_pluto_generation(sign):
    meanings = {
        '蟹座': '家族と国家',
        '獅子座': '創造性と個性',
        '乙女座': '仕事と健康',
        '天秤座': '関係性とパートナーシップ',
        '蠍座': '権力と変容',
        '射手座': '信仰と国際関係',
        '山羊座': '政府と社会構造',
        '水瓶座': 'テクノロジーと社会革命'
    }
    return meanings.get(sign, sign)


def get_aspect_interpretation(aspects):
    """主要アスペクトの解釈"""
    result = []
    for asp in aspects[:5]:  # 最初の5つのみ
        p1_jp = PLANET_JP_MAP.get(asp.planet1, asp.planet1)
        p2_jp = PLANET_JP_MAP.get(asp.planet2, asp.planet2)
        meaning = _get_aspect_meaning_detailed(asp.planet1, asp.planet2, asp.aspect_type)
        if meaning:
            result.append({
                'aspect': f"{p1_jp} {asp.aspect_type} {p2_jp}",
                'meaning': meaning
            })
    return result


PLANET_JP_MAP = {
    'Sun': '太陽', 'Moon': '月', 'Mercury': '水星', 'Venus': '金星',
    'Mars': '火星', 'Jupiter': '木星', 'Saturn': '土星',
    'Uranus': '天王星', 'Neptune': '海王星', 'Pluto': '冥王星'
}


def _get_aspect_meaning_detailed(p1, p2, aspect_type):
    """詳細なアスペクト解釈"""
    # 太陽と月の組み合わせ
    if {p1, p2} == {'Sun', 'Moon'}:
        if aspect_type == 'conjunction':
            return '新月生まれ。意識と無意識が一体化しており、本能的に行動します。新しいことを始める力がありますが、客観性を養うことも大切です。'
        elif aspect_type == 'opposition':
            return '満月生まれ。意識と無意識の間にテンションがあり、人間関係を通じて自己を発見します。バランス感覚を養う人生です。'
        elif aspect_type == 'trine':
            return '意志と感情が調和しています。自然体で生きることができ、内面の葛藤が少ないです。'
        elif aspect_type == 'square':
            return '意志と感情の間に挑戦があります。内面的な緊張がありますが、それが成長の原動力になります。'
    
    # 太陽と金星
    if {p1, p2} == {'Sun', 'Venus'}:
        return '愛情と美への感性が自己表現と結びついています。芸術的才能があり、人を惹きつける魅力があります。'
    
    # 太陽と火星
    if {p1, p2} == {'Sun', 'Mars'}:
        if aspect_type in ['conjunction', 'trine', 'sextile']:
            return 'エネルギッシュで行動力があります。競争心が強く、リーダーシップを発揮します。'
        else:
            return '意志と行動の間に葛藤があります。怒りのコントロールを学ぶことで、より効果的に力を使えます。'
    
    # 月と金星
    if {p1, p2} == {'Moon', 'Venus'}:
        return '感情と愛情が調和しています。人から愛される魅力があり、芸術的感性も豊かです。'
    
    # 木星と土星
    if {p1, p2} == {'Jupiter', 'Saturn'}:
        return '拡大と制限のバランスを取ることがテーマです。現実的な楽観主義者になれる配置です。'
    
    # 一般的な解釈
    return ''


def generate_overall_reading(sun_sign, moon_sign, asc_sign):
    """総合リーディングを生成"""
    # 星座のエレメントを判定
    fire = ['牡羊座', '獅子座', '射手座']
    earth = ['牡牛座', '乙女座', '山羊座']
    air = ['双子座', '天秤座', '水瓶座']
    water = ['蟹座', '蠍座', '魚座']
    
    elements = []
    for sign in [sun_sign, moon_sign, asc_sign]:
        if sign in fire:
            elements.append('火')
        elif sign in earth:
            elements.append('地')
        elif sign in air:
            elements.append('風')
        elif sign in water:
            elements.append('水')
    
    # エレメントの傾向を分析
    from collections import Counter
    count = Counter(elements)
    dominant = count.most_common(1)[0] if count else ('', 0)
    
    element_meanings = {
        '火': 'あなたは情熱的でエネルギッシュ。行動力があり、新しいことを始める力に溢れています。時に衝動的になることもありますが、そのバイタリティは周囲を巻き込む魅力があります。',
        '地': 'あなたは現実的で着実。具体的な成果を生み出す力があり、信頼性が高いです。物事をじっくり進め、安定した基盤を築くことが得意です。',
        '風': 'あなたは知的で社交的。アイデアとコミュニケーションの力に優れ、人と人をつなぐ役割を担います。常に新しい情報や刺激を求めています。',
        '水': 'あなたは感受性豊かで直感的。他者の気持ちを深く理解し、共感する力があります。感情の波を航海しながら、深い人間関係を築きます。'
    }
    
    overall = f"【あなたのエレメントバランス】\n太陽（{sun_sign}）+ 月（{moon_sign}）+ アセンダント（{asc_sign}）\n\n"
    
    if dominant[1] >= 2:
        overall += f"あなたは「{dominant[0]}」のエネルギーが強く出ています。\n{element_meanings.get(dominant[0], '')}"
    else:
        overall += "あなたは複数のエレメントがバランスよく配置されており、多面的な性質を持っています。状況に応じて様々な側面を見せることができる柔軟性があります。"
    
    return overall


def generate_synastry_interpretation(syn, chart1, chart2):
    """相性の解釈を生成"""
    interpretations = []
    
    # 太陽と月の組み合わせを分析
    sun1 = chart1.sun.sign_jp
    moon1 = chart1.moon.sign_jp
    sun2 = chart2.sun.sign_jp
    moon2 = chart2.moon.sign_jp
    
    # 太陽星座の相性
    sun_compat = get_element_compatibility(sun1, sun2)
    interpretations.append({
        'title': f'太陽星座の相性（{sun1}×{sun2}）',
        'message': sun_compat['message'],
        'is_positive': sun_compat['score'] >= 3
    })
    
    # 月星座の相性
    moon_compat = get_element_compatibility(moon1, moon2)
    interpretations.append({
        'title': f'月星座の相性（{moon1}×{moon2}）- 感情面',
        'message': f'感情レベルでの相性: {moon_compat["message"]}',
        'is_positive': moon_compat['score'] >= 3
    })
    
    # 一方の太陽と他方の月
    sun_moon_compat = get_element_compatibility(sun1, moon2)
    interpretations.append({
        'title': f'{chart1.name}の太陽×{chart2.name}の月',
        'message': f'{chart1.name}の意志と{chart2.name}の感情の相性: {sun_moon_compat["message"]}',
        'is_positive': sun_moon_compat['score'] >= 3
    })
    
    return interpretations


def get_element_compatibility(sign1, sign2):
    """エレメントによる相性を判定"""
    elements = {
        '牡羊座': '火', '獅子座': '火', '射手座': '火',
        '牡牛座': '地', '乙女座': '地', '山羊座': '地',
        '双子座': '風', '天秤座': '風', '水瓶座': '風',
        '蟹座': '水', '蠍座': '水', '魚座': '水'
    }
    
    e1 = elements.get(sign1, '')
    e2 = elements.get(sign2, '')
    
    if e1 == e2:
        return {'score': 5, 'message': '同じエレメント同士で、自然と理解し合えます。お互いの価値観や行動パターンに親近感を感じるでしょう。'}
    elif (e1 in ['火', '風'] and e2 in ['火', '風']) or (e1 in ['地', '水'] and e2 in ['地', '水']):
        return {'score': 4, 'message': '相性の良いエレメントの組み合わせです。お互いを刺激し合い、良い影響を与え合えます。'}
    elif (e1 == '火' and e2 == '水') or (e1 == '水' and e2 == '火'):
        return {'score': 2, 'message': '情熱と感情がぶつかり合うこともあれば、相互に補い合うこともあります。理解し合うには努力が必要ですが、成長の機会にもなります。'}
    elif (e1 == '地' and e2 == '風') or (e1 == '風' and e2 == '地'):
        return {'score': 2, 'message': '現実と理想のバランスを取る必要がある関係です。お互いの違いを認め合うことで、視野が広がります。'}
    else:
        return {'score': 3, 'message': '異なる視点を持ち寄ることで、お互いを補完し合える関係です。'}


# Legacy functions removed (generate_synastry_interpretation, generate_daily_horoscope)


@app.route('/static/charts/<path:filename>')
def serve_chart(filename):
    """SVGチャートを配信"""
    return send_from_directory(CHARTS_DIR, filename)


if __name__ == '__main__':
    print("🌟 Uranai Server Starting...")
    print("📍 Open http://localhost:5555 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5555)
