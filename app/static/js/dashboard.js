// DOM Elements
const skeletonShell = document.getElementById('skeleton-shell');
const dashboard = document.getElementById('dashboard');

const tabBtns = document.querySelectorAll('.nav-btn');
const tabPanes = document.querySelectorAll('.tab-pane');

const searchInput = document.getElementById('stock-search');
const searchBtn = document.getElementById('search-btn');

const cSym = document.getElementById('current-symbol');
const marketStats = document.getElementById('market-stats');
const predList = document.getElementById('predictions-list');
const newsList = document.getElementById('stock-news');
const sentScore = document.getElementById('sentiment-score');

const trainBtn = document.getElementById('train-btn');
const predictBtn = document.getElementById('predict-btn');
const modelSelect = document.getElementById('model-select');

let chartPlot = null;
let currentSymbol = 'AAPL';

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    // Hide skeleton after basic scripts evaluate (simulating framework hydration)
    setTimeout(() => {
        skeletonShell.style.display = 'none';
        dashboard.style.display = 'flex';
        loadDashboardData(currentSymbol);
        loadGeopoliticsFeeds();
    }, 800);
});

// Tab Switching
tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const target = btn.getAttribute('data-tab');
        
        tabBtns.forEach(b => b.classList.remove('active'));
        tabPanes.forEach(p => p.classList.remove('active'));
        
        btn.classList.add('active');
        document.getElementById(target).classList.add('active');
        
        if (target === 'stock-radar' && chartPlot) {
            Plotly.Plots.resize('main-chart');
        }
    });
});

// Search functionality
searchBtn.addEventListener('click', () => {
    const sym = searchInput.value.trim().toUpperCase();
    if (sym) {
        currentSymbol = sym;
        loadDashboardData(sym);
    }
});

searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') searchBtn.click();
});

// Load all data for a symbol
async function loadDashboardData(symbol) {
    cSym.textContent = `${symbol} Radar`;
    marketStats.innerHTML = '<div class="loading-text">Fetching live data...</div>';
    newsList.innerHTML = '<div class="loading-text">Scraping intelligence...</div>';
    
    // Clear prediction list because it belongs to a past state
    predList.innerHTML = '<p class="empty-state">No forecast generated.</p>';

    try {
        // Fetch Historical Data
        const res = await fetch('/data', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({symbol: symbol, range: '6mo', interval: '1d'})
        });
        
        const data = await res.json();
        
        if (!res.ok) {
            marketStats.innerHTML = `<div class="error-text">API Error: ${data.detail || 'Unknown server error'}</div>`;
            return;
        }

        if (data.status !== 'error') {
            renderChart(data.data, symbol);
            renderStats(data.data);
        } else {
            marketStats.innerHTML = `<div class="error-text">${data.message}</div>`;
        }

        // Fetch Sentiment
        fetchSentiment(symbol);

    } catch (err) {
        console.error('Error fetching data:', err);
    }
}

function renderChart(historyData, symbol) {
    const dates = historyData.map(d => d.Timestamp);
    const opens = historyData.map(d => d.Open);
    const highs = historyData.map(d => d.High);
    const lows = historyData.map(d => d.Low);
    const closes = historyData.map(d => d.Close);

    const trace1 = {
        x: dates,
        close: closes,
        decreasing: {line: {color: '#ef4444'}},
        high: highs,
        increasing: {line: {color: '#16a34a'}},
        line: {color: 'rgba(31,119,180,1)'},
        low: lows,
        open: opens,
        type: 'candlestick',
        xaxis: 'x',
        yaxis: 'y'
    };

    const layout = {
        plot_bgcolor: 'transparent',
        paper_bgcolor: 'transparent',
        margin: {t: 20, r: 40, b: 40, l: 40},
        xaxis: {
            gridcolor: '#2a2a2a',
            tickfont: {color: '#a3a3a3', family: 'SF Mono'},
            rangeslider: {visible: false}
        },
        yaxis: {
            gridcolor: '#2a2a2a',
            tickfont: {color: '#a3a3a3', family: 'SF Mono'},
        },
        showlegend: false
    };

    Plotly.newPlot('main-chart', [trace1], layout, {responsive: true});
    chartPlot = true;
}

function renderStats(historyData) {
    if(!historyData || historyData.length === 0) return;
    
    const latest = historyData[historyData.length - 1];
    const prev = historyData[historyData.length - 2];
    
    // Calculate deltas
    const change = latest.Close - prev.Close;
    const pctChange = (change / prev.Close) * 100;
    const colorClass = change >= 0 ? 'up' : 'down';
    const sign = change >= 0 ? '+' : '';

    marketStats.innerHTML = `
        <div class="stat-box">
            <div class="stat-label">Last Close</div>
            <div class="stat-value">$${latest.Close.toFixed(2)}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Day Change</div>
            <div class="stat-value ${colorClass}">${sign}${change.toFixed(2)} (${sign}${pctChange.toFixed(2)}%)</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Volume</div>
            <div class="stat-value">${latest.Volume.toLocaleString()}</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Day Range</div>
            <div class="stat-value" style="font-size: 14px;">$${latest.Low.toFixed(1)} - $${latest.High.toFixed(1)}</div>
        </div>
    `;
}

async function fetchSentiment(symbol) {
    try {
        const res = await fetch('/sentiment', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({symbol: symbol, snippet_count: 5})
        });
        
        const data = await res.json();
        
        if (data.status !== 'error') {
            // Render Score
            const st = data.overall_sentiment || 'NEUTRAL';
            let color = '#a3a3a3';
            if (st === 'Positive') color = 'var(--primary-light)';
            if (st === 'Negative') color = 'var(--danger)';
            
            sentScore.innerHTML = `<span style="color: ${color}">${st.toUpperCase()}</span>`;
            
            // Render Articles
            const articles = data.articles || [];
            if(articles.length === 0) {
                newsList.innerHTML = '<p class="empty-state">No intel found.</p>';
                return;
            }

            newsList.innerHTML = articles.map(art => {
                let borderCol = 'transparent';
                if(art.Sentiment === 'Positive') borderCol = 'var(--primary-light)';
                if(art.Sentiment === 'Negative') borderCol = 'var(--danger)';
                
                return `
                <div class="news-item" style="border-left-color: ${borderCol}">
                    <div class="news-title">${art.Headline}</div>
                    <div class="news-meta">
                        <span>${new Date(art.Date).toLocaleDateString()}</span>
                        <span>Scr: ${art.SentimentScore.toFixed(2)}</span>
                    </div>
                </div>
                `;
            }).join('');

        } else {
            newsList.innerHTML = `<p class="empty-state">Sentiment error.</p>`;
        }
    } catch(err) {
        newsList.innerHTML = `<p class="empty-state">Failed to reach sentiment agent.</p>`;
    }
}

// Prediction Handlers
trainBtn.addEventListener('click', async () => {
    const model = modelSelect.value;
    if (model !== 'lstm') {
        alert(model + ' is pre-trained. Proceed to prediction.');
        return;
    }

    trainBtn.disabled = true;
    trainBtn.textContent = 'Training...';
    try {
        const res = await fetch('/train', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ symbol: currentSymbol, model_type: model, epochs: 20 })
        });
        const result = await res.json();
        if(result.status !== 'error') alert('Training complete!');
        else alert('Error: ' + result.message);
    } catch(err) {
        alert('Exception: ' + err.message);
    } finally {
        trainBtn.disabled = false;
        trainBtn.textContent = 'Train Model';
    }
});

predictBtn.addEventListener('click', async () => {
    predictBtn.disabled = true;
    predictBtn.textContent = 'Analyzing...';
    predList.innerHTML = '<div class="loading-state">Synthesizing forecast...</div>';
    
    try {
        const res = await fetch('/predict', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ symbol: currentSymbol, model_type: modelSelect.value, days: 5 })
        });
        const result = await res.json();
        
        if(result.status !== 'error') {
            const preds = result.predictions;
            predList.innerHTML = preds.map(p => `
                <div class="pred-row">
                    <span>${new Date(p.date).toLocaleDateString()}</span>
                    <span style="color: var(--primary-light)">$${p.price.toFixed(2)}</span>
                </div>
            `).join('');

            // Also draw them on chart if possible
            if(chartPlot) {
                const dates = preds.map(p => p.date);
                const prices = preds.map(p => p.price);
                const predTrace = {
                    x: dates, y: prices,
                    mode: 'lines+markers',
                    name: 'Prediction',
                    line: {dash: 'dot', color: '#16a34a', width: 2},
                    marker: {size: 6}
                };
                Plotly.addTraces('main-chart', predTrace);
            }
        } else {
            predList.innerHTML = `<p class="error-text">${result.message}</p>`;
        }
    } catch(err) {
         predList.innerHTML = `<p class="error-text">Request failed.</p>`;
    } finally {
        predictBtn.disabled = false;
        predictBtn.textContent = 'Generate Forecast';
    }
});

// Geopolitics News Scraper & Multi-Channel YouTube Grid
async function loadGeopoliticsFeeds() {
    // Load both in parallel
    Promise.all([loadChannelsGrid(), loadNewsFeed()]);
}

async function loadChannelsGrid() {
    const grid = document.getElementById('channels-grid');
    try {
        const res = await fetch('/api/youtube/channels');
        const data = await res.json();

        if (data.status === 'success' && data.channels.length > 0) {
            grid.innerHTML = ''; // clear loading state
            
            const initPlayers = () => {
                data.channels.forEach((ch, idx) => {
                    const cellId = 'yt-cell-' + idx;
                    const fallbackHtml = `
                        <a href="${ch.url}" target="_blank" class="channel-card fallback-card" style="width:100%; height:100%; display:block;">
                            ${ch.isLive ? '<span class="channel-live-badge">LIVE</span>' : ''}
                            <img src="${ch.thumbnail}" alt="${ch.name}" style="width:100%; height:100%; object-fit:cover;"
                                 onerror="this.src='https://img.youtube.com/vi/${ch.videoId}/hqdefault.jpg'">
                            <div class="channel-card-overlay">
                                <div class="channel-name">${ch.name}</div>
                                <div class="channel-title">${ch.title}</div>
                            </div>
                        </a>
                    `;

                    const wrapper = document.createElement('div');
                    wrapper.className = 'yt-grid-wrapper';
                    wrapper.innerHTML = `
                        <div id="${cellId}" class="yt-player-target"></div>
                        <div class="yt-grid-overlay">
                            ${ch.isLive ? '<span class="channel-live-badge" style="position:static; display:inline-block; margin-right:4px;">LIVE</span>' : ''}
                            <div style="flex:1;">
                                <div class="channel-name" style="text-shadow: 0 1px 3px rgba(0,0,0,0.8);">${ch.name}</div>
                                <div class="channel-title" style="text-shadow: 0 1px 3px rgba(0,0,0,0.8); font-size:10px;">${ch.title}</div>
                            </div>
                            <div class="yt-action-bar">
                                <button class="nav-btn btn-mute-toggle" title="Toggle Mute">🔇</button>
                                <a href="${ch.url}" target="_blank" class="nav-btn ext-btn" title="Watch on YouTube">🔗</a>
                            </div>
                        </div>
                    `;
                    grid.appendChild(wrapper);

                    const muteBtn = wrapper.querySelector('.btn-mute-toggle');
                    let player;

                    player = new YT.Player(cellId, {
                        height: '100%',
                        width: '100%',
                        videoId: ch.videoId,
                        host: 'https://www.youtube-nocookie.com',
                        playerVars: {
                            'autoplay': 1,
                            'mute': 1, // Must be muted for autoplay
                            'playsinline': 1,
                            'rel': 0,
                            'controls': 1,
                            'origin': window.location.origin,
                            'widget_referrer': window.location.origin
                        },
                        events: {
                            'onReady': (e) => {
                                e.target.playVideo();
                                muteBtn.addEventListener('click', () => {
                                    if (player.isMuted()) {
                                        player.unMute();
                                        if (player.getVolume() === 0) player.setVolume(50);
                                        muteBtn.textContent = '🔊';
                                    } else {
                                        player.mute();
                                        muteBtn.textContent = '🔇';
                                    }
                                });
                            },
                            'onError': (e) => {
                                // 101, 150, or 2 indicates embedding is disabled by the owner
                                if (e.data === 101 || e.data === 150 || e.data === 2) {
                                    wrapper.innerHTML = fallbackHtml;
                                }
                            }
                        }
                    });
                });
            };

            if (window.YT && window.YT.Player) {
                initPlayers();
            } else {
                const tag = document.createElement('script');
                tag.src = "https://www.youtube.com/iframe_api";
                document.body.appendChild(tag);
                window.onYouTubeIframeAPIReady = initPlayers;
            }
        } else {
            grid.innerHTML = '<p class="empty-state" style="padding:20px;">Could not load channels.</p>';
        }
    } catch(err) {
        grid.innerHTML = '<p class="error-text" style="padding:20px;">Channel fetch failed.</p>';
    }
}

async function loadNewsFeed() {
    const feedCont = document.getElementById('geo-news-list');
    try {
        const res = await fetch('/api/news/global');
        const data = await res.json();

        if (data.status === 'success' && data.news.length > 0) {
            feedCont.innerHTML = data.news.map(f => `
                <a href="${f.url}" target="_blank" class="feed-item ${f.type}"
                   style="display:block; text-decoration:none; color:inherit;">
                    <div class="feed-title">${f.title}</div>
                    <div class="feed-time">${f.time} 🔗</div>
                </a>
            `).join('');
        } else {
            feedCont.innerHTML = '<p class="empty-state">No intel available right now.</p>';
        }
    } catch(err) {
        feedCont.innerHTML = '<p class="error-text">RSS feed fetch failed.</p>';
    }
}

// Global YouTube callback - kept for compatibility but unused now
window.onYouTubeIframeAPIReady = function() {};

async function initializeYouTube(channelName) {
    try {
        const res = await fetch(`/api/youtube/live?channel=${encodeURIComponent(channelName)}`);
        const data = await res.json();

        const loading = document.getElementById('yt-loading');
        const thumbContent = document.getElementById('yt-thumb-content');
        const thumbImg = document.getElementById('yt-thumb-img');
        const watchBtn = document.getElementById('yt-watch-btn');
        const extLink = document.getElementById('yt-external-link');
        const liveBadge = document.getElementById('yt-live-badge');
        const overlayLabel = document.getElementById('yt-overlay-label');
        const channelNameEl = document.getElementById('yt-channel-name');

        if (data.videoId) {
            const videoId = data.videoId;
            const ytUrl = `https://www.youtube.com/watch?v=${videoId}`;

            // Use maxresdefault thumbnail, fallback to hqdefault
            thumbImg.src = `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;
            thumbImg.onerror = () => { thumbImg.src = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`; };

            watchBtn.href = ytUrl;

            if (extLink) { extLink.href = ytUrl; extLink.style.display = 'inline-block'; }

            if (data.isLive) {
                liveBadge.style.display = 'inline-block';
                overlayLabel.textContent = '● LIVE NOW';
            } else {
                overlayLabel.textContent = 'LATEST VIDEO';
            }

            if (channelNameEl && data.channel) {
                channelNameEl.textContent = data.channel;
            }

            loading.style.display = 'none';
            thumbContent.style.display = 'block';
        } else {
            loading.innerHTML = '<span class="error-text">Stream offline or unavailable.</span>';
        }
    } catch(err) {
        document.getElementById('yt-loading').innerHTML = '<span class="error-text">Failed to connect to satellite feed.</span>';
    }
}


