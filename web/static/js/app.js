// Uranai Web App - Interactive Horoscope Application

// API Base URL (adjust for production)
const API_BASE = '';

// Japanese Planet Names
const PLANET_JP = {
    'Sun': '太陽',
    'Moon': '月',
    'Mercury': '水星',
    'Venus': '金星',
    'Mars': '火星',
    'Jupiter': '木星',
    'Saturn': '土星',
    'Uranus': '天王星',
    'Neptune': '海王星',
    'Pluto': '冥王星',
    'North Node': 'ドラゴンヘッド',
    'South Node': 'ドラゴンテイル',
    'Chiron': 'キロン',
    'Lilith': 'リリス'
};

// ハウスのわかりやすい名前
const HOUSE_NAMES = {
    1: '自分自身',
    2: 'お金・価値観',
    3: 'コミュニケーション',
    4: '家庭・ルーツ',
    5: '恋愛・創造性',
    6: '仕事・健康',
    7: 'パートナー',
    8: '変容・共有財産',
    9: '探求・海外',
    10: 'キャリア・社会的地位',
    11: '友人・希望',
    12: '潜在意識・スピリチュアル'
};

// Aspect symbols
const ASPECT_SYMBOLS = {
    'conjunction': '☌', 'opposition': '☍', 'trine': '△',
    'square': '□', 'sextile': '⚹', 'quincunx': '⚻'
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initFormSelects();
    initForms();
    initDailyHoroscope();
    setDefaultDate();
});

// Tab Navigation
function initTabs() {
    const navLinks = document.querySelectorAll('.nav-link');
    const tabContents = document.querySelectorAll('.tab-content');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const tabId = link.getAttribute('data-tab');
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === tabId) content.classList.add('active');
            });
        });
    });
}

// Initialize form selects
function initFormSelects() {
    // Year selects
    const yearSelects = document.querySelectorAll('select[id$="year"], select[id$="-year"]');
    const currentYear = new Date().getFullYear();
    yearSelects.forEach(select => {
        for (let year = currentYear; year >= 1920; year--) {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year + '年';
            select.appendChild(option);
        }
    });

    // Day selects
    const daySelects = document.querySelectorAll('select[id$="day"], select[id$="-day"]');
    daySelects.forEach(select => {
        for (let day = 1; day <= 31; day++) {
            const option = document.createElement('option');
            option.value = day;
            option.textContent = day + '日';
            select.appendChild(option);
        }
    });

    // Hour selects
    const hourSelects = document.querySelectorAll('select[id$="hour"], select[id$="-hour"]');
    hourSelects.forEach(select => {
        select.innerHTML = '';
        for (let hour = 0; hour <= 23; hour++) {
            const option = document.createElement('option');
            option.value = hour;
            option.textContent = hour + '時';
            if (hour === 12) option.selected = true;
            select.appendChild(option);
        }
    });

    // Minute selects
    const minuteSelects = document.querySelectorAll('select[id$="minute"], select[id$="-minute"]');
    minuteSelects.forEach(select => {
        select.innerHTML = '';
        for (let minute = 0; minute <= 59; minute += 1) {
            const option = document.createElement('option');
            option.value = minute;
            option.textContent = minute.toString().padStart(2, '0') + '分';
            select.appendChild(option);
        }
    });
}

function setDefaultDate() {
    const today = new Date().toISOString().split('T')[0];
    const targetDate = document.getElementById('target-date');
    if (targetDate) targetDate.value = today;

    const todayDateEl = document.getElementById('today-date');
    if (todayDateEl) {
        const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };
        todayDateEl.textContent = new Date().toLocaleDateString('ja-JP', options);
    }
}

function initForms() {
    document.getElementById('birth-chart-form')?.addEventListener('submit', handleBirthChartSubmit);
    document.getElementById('transit-form')?.addEventListener('submit', handleTransitSubmit);
    document.getElementById('synastry-form')?.addEventListener('submit', handleSynastrySubmit);

    // Unknown time checkbox handler
    const unknownTimeCheckbox = document.getElementById('unknown-time');
    if (unknownTimeCheckbox) {
        unknownTimeCheckbox.addEventListener('change', function () {
            const timeInputs = document.getElementById('time-inputs');
            const hint = document.getElementById('time-unknown-hint');
            if (this.checked) {
                timeInputs.style.display = 'none';
                hint.style.display = 'block';
            } else {
                timeInputs.style.display = 'block';
                hint.style.display = 'none';
            }
        });
    }
}

function showLoading() { document.getElementById('loading').classList.remove('hidden'); }
function hideLoading() { document.getElementById('loading').classList.add('hidden'); }

// Format degree as "11°45'"
function formatDegree(degree) {
    const deg = Math.floor(degree);
    const min = Math.round((degree - deg) * 60);
    return `${deg}°${min.toString().padStart(2, '0')}'`;
}

// Birth Chart Submit
async function handleBirthChartSubmit(e) {
    e.preventDefault();
    showLoading();

    const unknownTime = document.getElementById('unknown-time').checked;

    const formData = {
        name: document.getElementById('name').value,
        year: document.getElementById('year').value,
        month: document.getElementById('month').value,
        day: document.getElementById('day').value,
        hour: unknownTime ? 12 : (document.getElementById('hour').value || 12),
        minute: unknownTime ? 0 : (document.getElementById('minute').value || 0),
        city: document.getElementById('city').value,
        unknown_time: unknownTime
    };

    try {
        const response = await fetch(`${API_BASE}/api/birth-chart`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (result.success) {
            displayProfessionalHoroscope(result);
        } else {
            alert('エラー: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('通信エラーが発生しました');
    } finally {
        hideLoading();
    }
}

// Display Professional Horoscope
function displayProfessionalHoroscope(result) {
    const resultArea = document.getElementById('birth-chart-result');
    resultArea.classList.remove('hidden');

    const data = result.data;

    // Chart Info Header
    const chartInfo = document.getElementById('chart-info-header');
    chartInfo.innerHTML = `
        <div class="chart-meta">
            <h2 class="chart-name">${data.name} のネイタルチャート</h2>
            <div class="chart-details">
                <span>📅 ${data.birth_date}</span>
                <span>🕐 ${data.birth_time}</span>
                <span>📍 ${data.location.city || `${data.location.lat.toFixed(2)}°, ${data.location.lng.toFixed(2)}°`}</span>
                <span>🌐 ${data.location.timezone}</span>
            </div>
        </div>
    `;

    // SVG Chart
    const chartContainer = document.getElementById('chart-svg');
    if (result.svg_url) {
        chartContainer.innerHTML = `<img src="${result.svg_url}" alt="Natal Chart" />`;
    } else {
        chartContainer.innerHTML = '<p class="text-muted">チャート画像を生成できませんでした</p>';
    }

    // Planets Section - Professional Format
    const planetsContainer = document.getElementById('planets-data');
    let planetsHTML = '<div class="data-list">';

    data.planets.forEach(planet => {
        const planetJP = PLANET_JP[planet.name] || planet.name;
        const retrograde = planet.retrograde ? ', Retrograde' : '';
        const retroSymbol = planet.retrograde ? ' ℞' : '';

        planetsHTML += `
            <div class="data-row planet-row">
                <span class="planet-name">${planetJP}${retroSymbol}</span>
                <span class="planet-position">
                    in <strong>${planet.sign_jp}</strong> ${formatDegree(planet.degree)}${retrograde}, 
                    in <strong>${planet.house}ハウス</strong>
                </span>
            </div>
        `;
    });

    // Add Ascendant and MC
    planetsHTML += `
        <div class="data-row planet-row highlight">
            <span class="planet-name">アセンダント (ASC)</span>
            <span class="planet-position">
                in <strong>${data.ascendant.sign_jp}</strong> ${formatDegree(data.ascendant.degree)}
            </span>
        </div>
        <div class="data-row planet-row highlight">
            <span class="planet-name">MC (天頂)</span>
            <span class="planet-position">
                in <strong>${data.midheaven.sign_jp}</strong> ${formatDegree(data.midheaven.degree)}
            </span>
        </div>
    `;

    planetsHTML += '</div>';
    planetsContainer.innerHTML = planetsHTML;

    // Houses Section
    const housesContainer = document.getElementById('houses-data');
    let housesHTML = '<div class="data-list houses-grid">';

    data.houses.forEach(house => {
        const houseNum = parseInt(house.house);
        const houseName = HOUSE_NAMES[houseNum] || '';
        housesHTML += `
            <div class="data-row house-row">
                <span class="house-number">${house.house}ハウス<span class="house-name-hint">（${houseName}）</span></span>
                <span class="house-position">
                    <strong>${house.sign_jp}</strong> ${formatDegree(house.degree)}
                </span>
            </div>
        `;
    });

    housesHTML += '</div>';
    housesContainer.innerHTML = housesHTML;

    // Aspects Section
    const aspectsContainer = document.getElementById('aspects-data');
    let aspectsHTML = '<div class="data-list">';

    // Group aspects by type
    const majorAspects = data.aspects.filter(a =>
        ['conjunction', 'opposition', 'trine', 'square', 'sextile'].includes(a.type)
    );

    majorAspects.forEach(aspect => {
        const p1JP = PLANET_JP[aspect.planet1] || aspect.planet1;
        const p2JP = PLANET_JP[aspect.planet2] || aspect.planet2;
        const symbol = ASPECT_SYMBOLS[aspect.type] || '';
        const aspectName = getAspectName(aspect.type);

        // Determine if aspect is applying or separating (simplified)
        const orbStr = `Orb: ${aspect.orb.toFixed(2)}°`;

        aspectsHTML += `
            <div class="data-row aspect-row ${aspect.type}">
                <span class="aspect-planets">${p1JP} ${symbol} ${p2JP}</span>
                <span class="aspect-details">
                    ${aspectName} (${orbStr})
                </span>
            </div>
        `;
    });

    if (majorAspects.length === 0) {
        aspectsHTML += '<p class="text-muted">主要なアスペクトはありません</p>';
    }

    aspectsHTML += '</div>';
    aspectsContainer.innerHTML = aspectsHTML;

    // Interpretation
    displayInterpretation(result.interpretation, data);

    // Advanced Analysis (Gemini-level)
    if (result.advanced_analysis) {
        displayAdvancedAnalysis(result.advanced_analysis);
    }

    // Scroll to results
    resultArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Display Advanced Analysis (Gemini-level)
function displayAdvancedAnalysis(analysis) {
    // Core Engine
    const coreEngineContainer = document.getElementById('core-engine-content');
    if (analysis.core_engine && coreEngineContainer) {
        let html = '';
        analysis.core_engine.forEach(section => {
            if (!section) return;
            html += `
                <div class="core-section">
                    <h5 class="core-title">
                        <span class="core-icon">${section.icon || '✧'}</span>
                        ${section.title} ${section.archetype || ''}
                    </h5>
                    <p>${section.description || ''}</p>
                    ${section.house_meaning ? `<p class="house-meaning">${section.house_meaning}</p>` : ''}
                    ${section.house_context ? `<p class="detail-note">${section.house_context}</p>` : ''}
                    ${section.saturn_influence ? `<p class="detail-note">${section.saturn_influence}</p>` : ''}
                    ${section.pluto_influence ? `<p class="detail-note">${section.pluto_influence}</p>` : ''}
                    ${section.venus_note ? `<p class="detail-note">${section.venus_note}</p>` : ''}
                    ${section.patterns ? section.patterns.map(p => `<p class="pattern-note">🔮 ${p}</p>`).join('') : ''}
                </div>
            `;
        });
        coreEngineContainer.innerHTML = html;
    }

    // Life Phases
    const lifePhasesContainer = document.getElementById('life-phases-content');
    if (analysis.life_phases && lifePhasesContainer) {
        const phaseNumbers = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩'];
        let html = '';
        analysis.life_phases.forEach((phase, idx) => {
            html += `
                <div class="phase-card">
                    <div class="phase-header">
                        <span class="phase-number">${phaseNumbers[idx] || '•'}</span>
                        <span class="phase-period">${phase.period}</span>
                    </div>
                    <h5 class="phase-title">${phase.title}</h5>
                    <p>${phase.description}</p>
                    ${phase.advice ? `<p class="phase-advice">💡 ${phase.advice}</p>` : ''}
                </div>
            `;
        });
        lifePhasesContainer.innerHTML = html;
    }

    // Decade Cycles
    const decadeCyclesContainer = document.getElementById('decade-cycles-content');
    if (analysis.decade_cycles && decadeCyclesContainer) {
        let html = '';
        analysis.decade_cycles.forEach(cycle => {
            html += `
                <div class="cycle-card">
                    <h5 class="cycle-period">【${cycle.period}】</h5>
                    <p class="cycle-theme"><strong>テーマ:</strong> ${cycle.theme}</p>
                    <p>${cycle.description}</p>
                </div>
            `;
        });
        decadeCyclesContainer.innerHTML = html;
    }

    // Marriage & Money
    const marriageMoneyContainer = document.getElementById('marriage-money-content');
    if (analysis.marriage_money && marriageMoneyContainer) {
        const mm = analysis.marriage_money;
        let html = `
            <div class="mm-section">
                <h5>💍 ${mm.marriage?.title || '結婚・パートナーシップ'}</h5>
                <p><strong>パートナー像:</strong> ${mm.marriage?.partner_type || ''}</p>
                <p><strong>特徴:</strong> ${mm.marriage?.style || ''}</p>
                <p><strong>婚期:</strong> ${mm.marriage?.timing || ''}</p>
            </div>
            <div class="mm-section">
                <h5>💰 ${mm.money?.title || '金運・財運'}</h5>
                <p><strong>稼ぎ方:</strong> ${mm.money?.earning_style || ''}</p>
                <p><strong>増やし方:</strong> ${mm.money?.wealth_building || ''}</p>
                <p><strong>最強の時期:</strong> ${mm.money?.peak_period || ''}</p>
            </div>
        `;
        marriageMoneyContainer.innerHTML = html;
    }

    // Strategic Advice
    const strategicAdviceContainer = document.getElementById('strategic-advice-content');
    if (analysis.strategic_advice && strategicAdviceContainer) {
        const sa = analysis.strategic_advice;
        let html = `
            <p class="archetype-statement">あなたは${sa.archetype || ''}として生きる運命にあります。</p>
            
            <div class="advice-section">
                <h5>💪 あなたの強み</h5>
                <ul>${(sa.strengths || []).map(s => `<li>${s}</li>`).join('') || '<li>多くの才能を持っています。</li>'}</ul>
            </div>
            
            <div class="advice-section">
                <h5>⚠️ 成長のための課題</h5>
                <ul>${(sa.weaknesses || []).map(w => `<li>${w}</li>`).join('') || '<li>課題を乗り越えることで成長できます。</li>'}</ul>
            </div>
            
            <div class="advice-section">
                <h5>🎯 今すぐできるアクション</h5>
                <ul>${(sa.actions || []).map(a => `<li>${a}</li>`).join('') || '<li>自分の強みを活かせる場所を見つけてください。</li>'}</ul>
            </div>
            
            ${sa.summary ? `
            <div class="advice-summary">
                <pre style="white-space: pre-wrap; font-family: inherit; margin: 0;">${sa.summary}</pre>
            </div>
            ` : ''}
        `;
        strategicAdviceContainer.innerHTML = html;
    }


    // Meta Cognition
    const metaContainer = document.getElementById('meta-content');
    if (analysis.meta_cognition && metaContainer) {
        const mc = analysis.meta_cognition;
        metaContainer.innerHTML = `
            <p class="meta-essence">このチャートの本質は<strong>${mc.essence || ''}</strong>です。</p>
            <p>${mc.description || ''}</p>
        `;
    }
}

function getAspectName(type) {
    const names = {
        'conjunction': 'コンジャンクション (合)',
        'opposition': 'オポジション (衝)',
        'trine': 'トライン (120°)',
        'square': 'スクエア (90°)',
        'sextile': 'セクスタイル (60°)',
        'quincunx': 'クインカンクス (150°)'
    };
    return names[type] || type;
}

function displayInterpretation(interp, data) {
    const container = document.getElementById('interpretation');
    if (!interp) {
        container.innerHTML = '<p class="text-muted">解釈データがありません</p>';
        return;
    }

    let html = '';

    // Unknown time warning
    if (interp.unknown_time) {
        html += `
            <div class="interp-section" style="background: rgba(251, 191, 36, 0.1); border-left-color: #fbbf24;">
                <div class="interp-header">
                    <span class="interp-icon">⚠️</span>
                    <h4>出生時刻不明</h4>
                </div>
                <p>出生時刻が不明のため、正午（12:00）で計算しています。アセンダント、ハウスカスプ、月の位置は実際と異なる可能性があります。</p>
            </div>
        `;
    }

    // カテゴリベースの簡易表示（メイン）
    if (interp.categories && interp.categories.length > 0) {
        html += `
            <div class="category-section">
                <div class="category-header">
                    <h4>✨ あなたの星が教えてくれること</h4>
                    <p class="category-subtitle">カードをクリックして詳しく見る</p>
                </div>
                <div class="category-grid">
        `;

        interp.categories.forEach((cat, index) => {
            const keywords = (cat.keywords || []).slice(0, 3).map(k => `<span class="keyword-tag">${k}</span>`).join('');
            html += `
                <div class="category-card" data-category-id="${cat.id}" onclick="toggleCategoryDetail(this)">
                    <div class="category-card-header">
                        <span class="category-icon">${cat.icon}</span>
                        <h5 class="category-title">${cat.title}</h5>
                    </div>
                    <p class="category-summary">${cat.summary}</p>
                    <div class="category-keywords">${keywords}</div>
                    <div class="category-details" style="display: none;">
                        <p>${cat.details ? cat.details.replace(/\n/g, '<br>') : ''}</p>
                    </div>
                    <span class="category-expand-hint">タップで詳細を見る ▼</span>
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;

        // 詳細表示へのトグル
        html += `
            <div class="detail-toggle-section">
                <button class="btn-detail-toggle" onclick="toggleDetailedView()">
                    <span class="toggle-icon">📊</span>
                    <span>占星術データを詳しく見る（惑星・ハウス配置）</span>
                </button>
            </div>
        `;
    }

    // 詳細表示（惑星ベース）- デフォルトで非表示
    html += `<div id="detailed-interpretation" class="detailed-interp-section" style="display: none;">`;

    // Sun
    if (interp.sun) {
        html += `
            <div class="interp-section sun-section">
                <div class="interp-header">
                    <span class="interp-icon">☉</span>
                    <h4>太陽 in ${data.sun.sign_jp} (${data.sun.house}ハウス)</h4>
                </div>
                <p>${interp.sun}</p>
                ${interp.sun_detail ? `<p class="interp-detail">${interp.sun_detail}</p>` : ''}
                ${interp.sun_house ? `<p class="interp-detail">【ハウス配置】${interp.sun_house}</p>` : ''}
            </div>
        `;
    }

    // Moon
    if (interp.moon) {
        html += `
            <div class="interp-section moon-section">
                <div class="interp-header">
                    <span class="interp-icon">☽</span>
                    <h4>月 in ${data.moon.sign_jp} (${data.moon.house}ハウス)</h4>
                </div>
                <p>${interp.moon}</p>
                ${interp.moon_detail ? `<p class="interp-detail">${interp.moon_detail}</p>` : ''}
                ${interp.moon_house ? `<p class="interp-detail">【ハウス配置】${interp.moon_house}</p>` : ''}
            </div>
        `;
    }

    // Ascendant
    if (interp.ascendant) {
        html += `
            <div class="interp-section asc-section">
                <div class="interp-header">
                    <span class="interp-icon">⬆</span>
                    <h4>アセンダント in ${data.ascendant.sign_jp}</h4>
                </div>
                <p>${interp.ascendant}</p>
            </div>
        `;
    }

    // Mercury
    if (interp.mercury) {
        const mercury = data.planets.find(p => p.name === 'Mercury');
        html += `
            <div class="interp-section">
                <div class="interp-header">
                    <span class="interp-icon">☿</span>
                    <h4>水星 in ${mercury?.sign_jp || ''} (${mercury?.house}ハウス)</h4>
                </div>
                <p>${interp.mercury}</p>
            </div>
        `;
    }

    // Venus
    if (interp.venus) {
        const venus = data.planets.find(p => p.name === 'Venus');
        html += `
            <div class="interp-section">
                <div class="interp-header">
                    <span class="interp-icon">♀</span>
                    <h4>金星 in ${venus?.sign_jp || ''} (${venus?.house}ハウス)</h4>
                </div>
                <p>${interp.venus}</p>
            </div>
        `;
    }

    // Mars
    if (interp.mars) {
        const mars = data.planets.find(p => p.name === 'Mars');
        html += `
            <div class="interp-section">
                <div class="interp-header">
                    <span class="interp-icon">♂</span>
                    <h4>火星 in ${mars?.sign_jp || ''} (${mars?.house}ハウス)</h4>
                </div>
                <p>${interp.mars}</p>
            </div>
        `;
    }

    // Jupiter
    if (interp.jupiter) {
        const jupiter = data.planets.find(p => p.name === 'Jupiter');
        const retroSymbol = jupiter?.retrograde ? ' ℞' : '';
        html += `
            <div class="interp-section" style="border-left-color: #8b5cf6;">
                <div class="interp-header">
                    <span class="interp-icon">♃</span>
                    <h4>木星${retroSymbol} in ${jupiter?.sign_jp || ''} (${jupiter?.house}ハウス)</h4>
                </div>
                <p style="white-space: pre-line;">${interp.jupiter}</p>
            </div>
        `;
    }

    // Saturn
    if (interp.saturn) {
        const saturn = data.planets.find(p => p.name === 'Saturn');
        const retroSymbol = saturn?.retrograde ? ' ℞' : '';
        html += `
            <div class="interp-section" style="border-left-color: #64748b;">
                <div class="interp-header">
                    <span class="interp-icon">♄</span>
                    <h4>土星${retroSymbol} in ${saturn?.sign_jp || ''} (${saturn?.house}ハウス)</h4>
                </div>
                <p style="white-space: pre-line;">${interp.saturn}</p>
            </div>
        `;
    }

    // Outer Planets (generational)
    if (interp.outer_planets) {
        html += `
            <div class="interp-section" style="border-left-color: #0ea5e9;">
                <div class="interp-header">
                    <span class="interp-icon">🌌</span>
                    <h4>トランスサタニアン（世代的影響）</h4>
                </div>
                <p style="white-space: pre-line;">${interp.outer_planets}</p>
            </div>
        `;
    }

    // Aspect Highlights
    if (interp.aspect_highlights && interp.aspect_highlights.length > 0) {
        let aspectHTML = '';
        interp.aspect_highlights.forEach(asp => {
            aspectHTML += `<div style="margin-bottom: 12px;"><strong>${asp.aspect}</strong><br>${asp.meaning}</div>`;
        });
        html += `
            <div class="interp-section" style="border-left-color: #f59e0b;">
                <div class="interp-header">
                    <span class="interp-icon">⚹</span>
                    <h4>主要アスペクト解釈</h4>
                </div>
                <div>${aspectHTML}</div>
            </div>
        `;
    }

    // Overall
    if (interp.overall) {
        html += `
            <div class="interp-section overall-section">
                <div class="interp-header">
                    <span class="interp-icon">🔮</span>
                    <h4>総合リーディング</h4>
                </div>
                <p style="white-space: pre-line;">${interp.overall}</p>
            </div>
        `;
    }

    html += `</div>`; // Close detailed-interpretation

    container.innerHTML = html;
}

// カテゴリ詳細の展開/折りたたみ
function toggleCategoryDetail(cardElement) {
    const details = cardElement.querySelector('.category-details');
    const hint = cardElement.querySelector('.category-expand-hint');

    if (details.style.display === 'none') {
        details.style.display = 'block';
        cardElement.classList.add('expanded');
        if (hint) hint.textContent = 'タップで閉じる ▲';
    } else {
        details.style.display = 'none';
        cardElement.classList.remove('expanded');
        if (hint) hint.textContent = 'タップで詳細を見る ▼';
    }
}

// 詳細表示のトグル
function toggleDetailedView() {
    const detailedSection = document.getElementById('detailed-interpretation');
    const btn = document.querySelector('.btn-detail-toggle');

    if (detailedSection.style.display === 'none') {
        detailedSection.style.display = 'block';
        btn.innerHTML = '<span class="toggle-icon">📊</span><span>占星術データを閉じる</span>';
        detailedSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else {
        detailedSection.style.display = 'none';
        btn.innerHTML = '<span class="toggle-icon">📊</span><span>占星術データを詳しく見る（惑星・ハウス配置）</span>';
    }
}






























// Transit Submit
async function handleTransitSubmit(e) {
    e.preventDefault();
    showLoading();

    const formData = {
        name: document.getElementById('transit-name').value,
        year: document.getElementById('transit-year').value,
        month: document.getElementById('transit-month').value,
        day: document.getElementById('transit-day').value,
        hour: document.getElementById('transit-hour').value || 12,
        minute: document.getElementById('transit-minute').value || 0,
        city: document.getElementById('transit-city').value,
        target_date: document.getElementById('target-date').value
    };

    try {
        const response = await fetch(`${API_BASE} /api/transit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (result.success) {
            displayTransitResult(result);
        } else {
            alert('エラー: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('通信エラーが発生しました');
    } finally {
        hideLoading();
    }
}

function displayTransitResult(result) {
    const resultArea = document.getElementById('transit-result');
    resultArea.classList.remove('hidden');

    // Transit aspects display (Existing logic preserved)
    const aspectsContainer = document.getElementById('transit-aspects');
    if (result.data && result.data.aspects) {
        let html = '<div class="data-list">';
        // ... (Keep existing aspect list code if needed, or simplify)
        // Let's keep it simple for now, maybe toggleable?
        // Updating to show list properly
        result.data.aspects.forEach(aspect => {
            const symbol = ASPECT_SYMBOLS[aspect.aspect_type] || '';
            html += `
                <div class="data-row aspect-row ${aspect.orb < 2 ? 'tight-orb' : ''}">
                    <span class="aspect-planets">T-${aspect.transit_planet} ${symbol} N-${aspect.natal_planet}</span>
                    <span class="aspect-details">${aspect.type_jp} (Orb: ${aspect.orb.toFixed(2)}°)</span>
                </div>
            `;
        });
        html += '</div>';
        aspectsContainer.innerHTML = html;
    }

    // New Interpretation Display
    const interpContainer = document.getElementById('transit-interpretation');
    if (result.interpretation) {
        const { major_themes, advice } = result.interpretation;
        let html = '';

        // 1. Current Advice Cards (Love, Work, Mental)
        if (advice) {
            html += '<h3 class="section-title">🔮 今日の運勢アドバイス</h3>';
            html += '<div class="category-grid" style="grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">';

            // Love
            html += `
                <div class="category-card" style="border-left: 4px solid #ec4899;">
                    <div class="card-header">
                        <span class="card-icon">💖</span>
                        <h4>恋愛・対人運</h4>
                    </div>
                    <div class="card-body">
                        <div class="star-rating">${'★'.repeat(advice.love.score || 3)}</div>
                        <p>${advice.love.text}</p>
                    </div>
                </div>
            `;

            // Work
            html += `
                <div class="category-card" style="border-left: 4px solid #3b82f6;">
                    <div class="card-header">
                        <span class="card-icon">💼</span>
                        <h4>仕事・金運</h4>
                    </div>
                    <div class="card-body">
                        <p>${advice.work.text}</p>
                    </div>
                </div>
            `;

            // Mental
            html += `
                <div class="category-card" style="border-left: 4px solid #8b5cf6;">
                    <div class="card-header">
                        <span class="card-icon">🧘</span>
                        <h4>メンタル・内面</h4>
                    </div>
                    <div class="card-body">
                        <p>${advice.mental.text}</p>
                    </div>
                </div>
            `;

            html += '</div>';
        }

        // 2. Major Themes (Seasons of Life)
        if (major_themes && major_themes.length > 0) {
            html += '<h3 class="section-title">🌍 あなたの人生の「季節」</h3>';
            html += '<p class="section-intro">動きの遅い惑星が告げる、長期的なテーマです。</p>';
            major_themes.forEach(theme => {
                html += `
                    <div class="feature-box" style="margin-bottom: 1rem;">
                        <div class="feature-icon">${getPlanetIcon(theme.planet)}</div>
                        <div class="feature-content">
                            <h4>${theme.title}</h4>
                            <p style="font-size: 0.9em; color: #666; margin-bottom: 0.5rem;">(${theme.planet} in House ${theme.house})</p>
                            <p>${theme.description}</p>
                        </div>
                    </div>
                `;
            });
        }

        // 3. Aspect Insights (New)
        if (result.interpretation.aspect_insights && result.interpretation.aspect_insights.length > 0) {
            html += '<h3 class="section-title">⚡️ 現在の重要な星の配置 (アスペクト)</h3>';
            html += '<p class="section-intro">惑星同士が角度を取り合い、あなたに具体的な影響を与えています。</p>';
            result.interpretation.aspect_insights.forEach(insight => {
                html += `
                    <div class="feature-box" style="margin-bottom: 1rem; border-left-color: #f59e0b;">
                        <div class="feature-icon">⚡️</div>
                        <div class="feature-content">
                            <h4>${insight.title}</h4>
                            <p>${insight.description}</p>
                        </div>
                    </div>
                `;
            });
        }

        interpContainer.innerHTML = html;
    }

    resultArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function getPlanetIcon(name) {
    const icons = { 'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀', 'Mars': '♂', 'Jupiter': '♃', 'Saturn': '♄', 'Uranus': '♅', 'Neptune': '♆', 'Pluto': '♇' };
    return icons[name] || '★';
}

// Synastry Submit
async function handleSynastrySubmit(e) {
    e.preventDefault();
    showLoading();

    const formData = {
        person1: {
            name: document.getElementById('p1-name').value,
            year: document.getElementById('p1-year').value,
            month: document.getElementById('p1-month').value,
            day: document.getElementById('p1-day').value,
            city: document.getElementById('p1-city').value
        },
        person2: {
            name: document.getElementById('p2-name').value,
            year: document.getElementById('p2-year').value,
            month: document.getElementById('p2-month').value,
            day: document.getElementById('p2-day').value,
            city: document.getElementById('p2-city').value
        }
    };

    try {
        const response = await fetch(`${API_BASE}/api/synastry`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (result.success) {
            displaySynastryResult(result);
        } else {
            alert('エラー: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('通信エラーが発生しました');
    } finally {
        hideLoading();
    }
}

function displaySynastryResult(result) {
    const resultArea = document.getElementById('synastry-result');
    resultArea.classList.remove('hidden');

    const data = result.data;
    const interp = result.interpretation;

    // Score
    const scoreContainer = document.getElementById('synastry-score');
    scoreContainer.innerHTML = `
        <div class="score-number">${data.score} <span class="score-unit">点</span></div>
        <div class="score-label">${data.level}</div>
    `;

    // Interpretation (New Layout)
    const interpContainer = document.getElementById('synastry-interpretation');
    if (interp) {
        let html = '';

        // 1. Compatibility Cards
        if (interp.compatibility) {
            html += '<div class="category-grid" style="grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">';

            // Love
            html += _createSynastryCard('💖', '恋愛・情熱',
                interp.compatibility.love.score,
                interp.compatibility.love.description);

            // Comm
            html += _createSynastryCard('🗣', 'コミュニケーション',
                interp.compatibility.communication.score,
                interp.compatibility.communication.description);

            html += '</div>';
        }

        // 2. House Overlays (Deep Dive)
        if (interp.overlays) {
            html += '<h3 class="section-title">🏠 ハウス相互作用 (相手の星があなたに与える影響)</h3>';

            html += '<div class="overlay-section">';
            html += '<h4 class="overlay-subtitle">相手の星 → あなたのハウス</h4>';
            interp.overlays.chart1_view.forEach(ov => {
                html += _createOverlayRow(ov);
            });
            html += '</div>';

            html += '<div class="overlay-section" style="margin-top:20px;">';
            html += '<h4 class="overlay-subtitle">あなたの星 → 相手のハウス</h4>';
            interp.overlays.chart2_view.forEach(ov => {
                html += _createOverlayRow(ov);
            });
            html += '</div>';
        }

        interpContainer.innerHTML = html;
    }

    // Aspects (Existing)
    const aspectsContainer = document.getElementById('synastry-aspects');
    // ... (Keep simpler aspect list or existing)
    if (data.aspects) {
        let html = '<div class="data-list">';
        data.aspects.forEach(aspect => {
            const symbol = ASPECT_SYMBOLS[aspect.aspect_type] || '';
            html += `
                <div class="data-row aspect-row ${aspect.is_harmonious ? 'positive' : 'challenging'}">
                    <span class="aspect-planets">${aspect.person1_planet} ${symbol} ${aspect.person2_planet}</span>
                    <span class="aspect-details">${aspect.type_jp} (Orb: ${aspect.orb.toFixed(2)}°)</span>
                </div>
            `;
        });
        html += '</div>';
        aspectsContainer.innerHTML = html;
    }

    resultArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function _createSynastryCard(icon, title, score, text) {
    return `
        <div class="category-card">
            <div class="card-header">
                <span class="card-icon">${icon}</span>
                <h4>${title}</h4>
            </div>
            <div class="card-body">
                <div class="star-rating">${'★'.repeat(score > 70 ? 5 : score > 50 ? 4 : 3)}</div>
                <p>${text}</p>
            </div>
        </div>
    `;
}

function _createOverlayRow(ov) {
    // If backend provides rich title/meaning, use it. Otherwise fallback.
    const title = ov.title || `${ov.planet} in House ${ov.house}`;
    const meaning = ov.meaning || '';

    return `
        <div class="feature-box" style="margin-bottom: 0.5rem; padding: 15px;">
            <div class="feature-content">
                <h5 style="margin-bottom: 8px; color: #4f46e5; font-weight: bold;">${title}</h5>
                <p style="font-size: 0.9em; margin-bottom: 8px; color: #666;">
                    <strong>[配置]</strong> 相手の${ov.planet_jp || ov.planet}が、あなたの${ov.house}ハウス(${ov.house_theme || ''})に入室
                </p>
                <div style="white-space: pre-wrap; line-height: 1.6;">${meaning}</div>
            </div>
        </div>
    `;
}

// Daily Horoscope Logic
function initDailyHoroscope() {
    // ... (This function is stable, no changes needed for init)
    const zodiacGrid = document.getElementById('zodiac-grid');
    if (!zodiacGrid) return;

    // Check if buttons already exist to avoid duplication if init called twice
    if (zodiacGrid.children.length > 0) return;

    const signs = [
        { name: '牡羊座', emoji: '♈', period: '3/21-4/19' },
        { name: '牡牛座', emoji: '♉', period: '4/20-5/20' },
        { name: '双子座', emoji: '♊', period: '5/21-6/21' },
        { name: '蟹座', emoji: '♋', period: '6/22-7/22' },
        { name: '獅子座', emoji: '♌', period: '7/23-8/22' },
        { name: '乙女座', emoji: '♍', period: '8/23-9/22' },
        { name: '天秤座', emoji: '♎', period: '9/23-10/23' },
        { name: '蠍座', emoji: '♏', period: '10/24-11/22' },
        { name: '射手座', emoji: '♐', period: '11/23-12/21' },
        { name: '山羊座', emoji: '♑', period: '12/22-1/19' },
        { name: '水瓶座', emoji: '♒', period: '1/20-2/18' },
        { name: '魚座', emoji: '♓', period: '2/19-3/20' }
    ];

    signs.forEach(sign => {
        const btn = document.createElement('button');
        btn.className = 'zodiac-btn';
        btn.innerHTML = `
            <span class="sign-emoji">${sign.emoji}</span>
            <span class="sign-name">${sign.name}</span>
            <span class="sign-period">${sign.period}</span>
        `;
        btn.addEventListener('click', () => showDailyHoroscope(sign));
        zodiacGrid.appendChild(btn);
    });
}

async function showDailyHoroscope(sign) {
    showLoading();

    try {
        const response = await fetch(`${API_BASE}/api/daily`);
        const result = await response.json();

        if (result.success) {
            const horoscope = result.horoscopes[sign.name];
            displayDailyResult(sign, horoscope);
        } else {
            alert('エラー: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('通信エラーが発生しました');
    } finally {
        hideLoading();
    }
}

function displayDailyResult(sign, horoscope) {
    const resultArea = document.getElementById('daily-result');
    resultArea.classList.remove('hidden');

    const content = document.getElementById('daily-content');
    const stars = '★'.repeat(horoscope.score) + '☆'.repeat(5 - horoscope.score);

    content.innerHTML = `
        <div class="horoscope-sign">${sign.emoji}</div>
        <h3 class="horoscope-title">${sign.name}の今日の運勢</h3>
        <p style="text-align:center; color:#666; margin-bottom:1rem;">月が${horoscope.moon_sign}にあり、${horoscope.house}ハウス（${horoscope.theme}）を活性化させています。</p>
        
        <div class="horoscope-stars">${stars}</div>
        <div class="horoscope-message">${horoscope.message}</div>
        
        <div class="horoscope-details">
            <div class="detail">
                <div class="detail-label">ラッキーカラー</div>
                <div class="detail-value" style="color:${_getColorCode(horoscope.lucky_color)}">${horoscope.lucky_color}</div>
            </div>
            <div class="detail">
                <div class="detail-label">テーマ</div>
                <div class="detail-value">${horoscope.theme}</div>
            </div>
        </div>
    `;

    resultArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function _getColorCode(name) {
    const map = { 'レッド': '#e53e3e', 'ブルー': '#3182ce', 'イエロー': '#d69e2e', 'グリーン': '#38a169', 'ピンク': '#d53f8c', 'パープル': '#805ad5', 'オレンジ': '#dd6b20', 'ホワイト': '#718096', 'ブラック': '#1a202c', 'ゴールド': '#d69e2e', 'シルバー': '#a0aec0', 'ブラウン': '#744210' };
    return map[name] || '#333';
}
