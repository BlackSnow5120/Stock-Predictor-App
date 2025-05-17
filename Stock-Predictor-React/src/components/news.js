import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ArrowUp, ArrowDown, Search, RefreshCw, ExternalLink } from 'lucide-react';

const News = ({ setActiveTab }) => {
  const [stockSymbol, setStockSymbol] = useState('GOOG');
  const [newsData, setNewsData] = useState([]);
  const [goodScore, setGoodScore] = useState(0);
  const [badScore, setBadScore] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchNewsData = async (symbol) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('http://localhost:5000/sentiment', {
        stock: symbol
      });

      setNewsData(response.data.news || []);
      setGoodScore(response.data.g_score || 0);
      setBadScore(response.data.b_score || 0);
    } catch (err) {
      console.error('Error fetching news:', err);
      setError('Failed to fetch news data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchNewsData(stockSymbol);
  };

  const getSentimentColor = (sentiment) => {
    return sentiment === 1 ? 'sentiment-label-positive' : 'sentiment-label-negative';
  };

  const getSentimentIcon = (sentiment) => {
    return sentiment === 1 ?
      <ArrowUp className="sentiment-icon-positive" size={16} /> :
      <ArrowDown className="sentiment-icon-negative" size={16} />;
  };

  const getTruncatedHeadline = (headline) => {
    return headline.length > 100 ? `${headline.substring(0, 100)}...` : headline;
  };

  return (
    <div className="news-container">
      <div className="news-header">
        <h1 className="news-title">Stock News Sentiment Analysis</h1>
        <p className="news-description">Get the latest news and sentiment analysis for any stock symbol</p>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-container">
          <input
            type="text"
            value={stockSymbol}
            onChange={(e) => setStockSymbol(e.target.value.toUpperCase())}
            className="search-input"
            placeholder="Enter stock symbol (e.g. AAPL)"
          />
          <div className="search-icon">
            <Search size={16} />
          </div>
        </div>
        <button
          type="submit"
          className="search-button"
          disabled={loading}
        >
          {loading ? <RefreshCw size={16} className="spinner" /> : 'Search'}
        </button>
      </form>

      {/* Sentiment Overview */}
      {!loading && !error && newsData.length > 0 && (
        <div className="sentiment-grid">
          <div className="sentiment-card">
            <h2 className="sentiment-card-title">Sentiment Overview</h2>
            <div className="sentiment-data">
              <div className="sentiment-counts">
                <div className="sentiment-count-item">
                  <div className="sentiment-count-value sentiment-count-positive">{goodScore}</div>
                  <div className="sentiment-count-label">Positive</div>
                </div>
                <div className="sentiment-count-item">
                  <div className="sentiment-count-value sentiment-count-negative">{badScore}</div>
                  <div className="sentiment-count-label">Negative</div>
                </div>
              </div>
            </div>
            <div className="sentiment-progress">
              <div className="progress-bar-container">
                <div
                  className="progress-bar"
                  style={{ width: `${(goodScore / (goodScore + badScore) * 100) || 0}%` }}
                ></div>
              </div>
              <div className="progress-stats">
                {goodScore + badScore} articles analyzed
              </div>
            </div>
          </div>

          <div className="sentiment-card">
            <h2 className="sentiment-card-title">Market Sentiment</h2>
            <div className="sentiment-data">
              {goodScore >= badScore ? (
                <div className="sentiment-indicator">
                  <div className="sentiment-icon">
                    <ArrowUp className="sentiment-icon-positive" size={64} />
                  </div>
                  <div className="sentiment-status">
                    {goodScore === badScore ? "Neutral" : "Positive"} Sentiment
                  </div>
                </div>
              ) : (
                <div className="sentiment-indicator">
                  <div className="sentiment-icon">
                    <ArrowDown className="sentiment-icon-negative" size={64} />
                  </div>
                  <div className="sentiment-status">Negative Sentiment</div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="loading-container">
          <RefreshCw size={48} className="spinner" />
        </div>
      )}

      {/* News List */}
      {!loading && !error && (
        <div className="news-list-container">
          <div className="news-list-header">
            <h2 className="news-list-title">Latest News for {stockSymbol}</h2>
          </div>

          {newsData.length === 0 ? (
            <div className="news-empty">
              No news articles found for {stockSymbol}.
            </div>
          ) : (
            <ul className="news-list">
              {newsData.map((item, index) => (
                <li key={index} className="news-item">
                  <a
                    href={item.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="news-link"
                  >
                    <div className="news-icon">
                      {getSentimentIcon(item.sentiment)}
                    </div>
                    <div className="news-content">
                      <h3 className="news-headline">
                        {getTruncatedHeadline(item.headline)}
                      </h3>
                      <div className="news-meta">
                        <span className={`sentiment-label ${getSentimentColor(item.sentiment)}`}>
                          {item.sentiment === 1 ? 'Positive' : 'Negative'}
                        </span>
                        <span className="meta-divider">|</span>
                        <span className="sentiment-score">
                          Score: {item.compound_score.toFixed(2)}
                        </span>
                      </div>
                    </div>
                    <ExternalLink size={16} className="external-link-icon" />
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

export default News;