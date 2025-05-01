import React, { useState } from 'react';
import ChartDisplay from './ChartDisplay';
import { fetchPrediction } from '../services/api';

function PredictionView({ setOriginal, setPredicted, loading, setLoading, original, predicted }) {
  const [stock, setStock] = useState('GOOG');
  const [modelPred, setModelPred] = useState('100d');
  const [error, setError] = useState('');

  const handlePrediction = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await fetchPrediction(stock, modelPred);
      setOriginal(data.original);
      setPredicted(data.predicted);
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-grid">
      <div className="card card-lg">
        <div className="card-header">
          <h2 className="card-title">Stock Price Prediction</h2>
        </div>
        <div className="card-body">
          <div className="form-group">
            <label className="form-label">Stock Symbol</label>
            <div className="form-row">
              <div className="form-col">
                <input
                  type="text"
                  value={stock}
                  onChange={(e) => setStock(e.target.value.toUpperCase())}
                  placeholder="Enter stock symbol (e.g., AAPL)"
                  className="form-control"
                />
              </div>
              <div className="form-col">
                <select
                  value={modelPred}
                  onChange={(e) => setModelPred(e.target.value)}
                  className="form-control"
                >
                  <option value="100d">LSTM_100</option>
                  <option value="200d">LSTM_200</option>
                  <option value="300d">LSTM_300</option>

                </select>
              </div>
              <button 
                onClick={handlePrediction} 
                className="btn btn-primary action-button" 
                disabled={loading}
              >
                {loading ? 'Loading...' : 'Predict'}
              </button>
            </div>
          </div>

          {error && <div style={{ color: 'var(--danger)', marginBottom: '1rem' }}>{error}</div>}

          {loading ? (
            <div className="loader">Loading prediction data...</div>
          ) : original.length > 0 && (
            <ChartDisplay original={original} predicted={predicted} />
          )}
        </div>
      </div>
    </div>
  );
}

export default PredictionView;