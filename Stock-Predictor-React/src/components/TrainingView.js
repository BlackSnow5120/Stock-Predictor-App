import React, { useState } from 'react';
import { trainModel } from '../services/api';

function TrainingView({ loading, setLoading, setMetrics, metrics, setMetricsData }) {
  const [stockTrain, setStockTrain] = useState('GOOG');
  const [startDate, setStartDate] = useState('2012-01-01');
  const [endDate, setEndDate] = useState('2022-12-31');
  const [epochs, setEpochs] = useState(1);
  const [modelType, setModelType] = useState('100d');

  const handleTraining = async () => {
    try {
      setLoading(true);
      const result = await trainModel({
        stock: stockTrain,
        start: startDate,
        end: endDate,
        epochs,
        model_type: modelType
      });
      
      if (result.metrics) {
        const updatedMetrics = {
          current: result.metrics,
          previous: metrics.current,
          changes: result.changes || {}
        };
        setMetrics(updatedMetrics);
        
        // Update metrics data for display
        const newMetricsData = [
          {
            label: 'Accuracy',
            value: result.metrics.Accuracy,
            isPositive: (result.changes?.Accuracy === "positive"),
            changeval: parseFloat(result.metrics.Accuracy) - parseFloat(metrics.current.Accuracy)
          },
          {
            label: 'RMSE',
            value: result.metrics.RMSE,
            isPositive: (result.changes?.RMSE === "positive"),
            changeval: parseFloat(result.metrics.RMSE) - parseFloat(metrics.current.RMSE)
          },
          {
            label: 'MAE',
            value: result.metrics.MAE,
            isPositive: (result.changes?.MAE === "positive"),
            changeval: parseFloat(result.metrics.MAE) - parseFloat(metrics.current.MAE)
          },
          {
            label: 'Training Time',
            value: result.metrics["Training Time"],
            isPositive: (result.changes?.["Training Time"] === "positive"),
            changeval: parseFloat(result.metrics["Training Time"]) - parseFloat(metrics.current["Training Time"])
          }
        ];
        setMetricsData(newMetricsData);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-grid">
      <div className="card card-lg">
        <div className="card-header">
          <h2 className="card-title">Train Prediction Model</h2>
        </div>
        <div className="card-body">
          <div className="form-group">
            <label className="form-label">Stock Symbol</label>
            <input
              type="text"
              value={stockTrain}
              onChange={(e) => setStockTrain(e.target.value.toUpperCase())}
              placeholder="Enter stock symbol (e.g., AAPL)"
              className="form-control"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Training Period</label>
            <div className="form-row">
              <div className="form-col">
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="form-control"
                />
              </div>
              <div className="form-col">
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="form-control"
                />
              </div>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Model Configuration</label>
            <div className="form-row">
              <div className="form-col">
                <input
                  type="number"
                  value={epochs}
                  onChange={(e) => setEpochs(Number(e.target.value))}
                  placeholder="Epochs"
                  className="form-control"
                  min="0"
                  max="100"
                />
              </div>
              <div className="form-col">
                <select
                  value={modelType}
                  onChange={(e) => setModelType(e.target.value)}
                  className="form-control"
                >
                  <option value="100d">LSTM_100</option>
                  <option value="200d">LSTM_200</option>
                  <option value="300d">LSTM_300</option>
                </select>
              </div>
              <button 
                onClick={handleTraining} 
                className="btn btn-primary action-button" 
                disabled={loading}
              >
                {loading ? 'Training...' : 'Train Model'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TrainingView;