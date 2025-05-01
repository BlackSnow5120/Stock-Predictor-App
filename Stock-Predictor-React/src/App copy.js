import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';
import ToastSetup from './toast';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './style.css'; // Use the improved CSS

function App() {
  // State for stock data
  const [stock, setStock] = useState('GOOG');
  const [stockTrain, setStockTrain] = useState('GOOG');
  const [original, setOriginal] = useState([]);
  const [predicted, setPredicted] = useState([]);
  
  // UI states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Model parameters
  const [modelType, setModelType] = useState('simplernn');
  const [modelPred, setModelPred] = useState('simplernn');

  const [epochs, setEpochs] = useState(1);
  
  // Training dates - set defaults to match backend
  const [startDate, setStartDate] = useState('2012-01-01');
  const [endDate, setEndDate] = useState('2022-12-31');
  
  // Metrics data
  const [metrics, setMetrics] = useState({
    current: {
      "Accuracy": "0.00%",
      "RMSE": "0.0000",
      "MAE": "0.0000",
      "Training Time": "0m 0s"
    },
    changes: {},
    previous: {}
  });
  const [metricsData, setMetricsData] = useState([]);

  // Fetch metrics when component mounts
  useEffect(() => {
    fetchMetrics();
  }, []);

  // Fetch metrics from API
  const fetchMetrics = async () => {
    const response = await axios.get('http://localhost:5000/metrics');
  
    const currentMetrics = response.data.metrics.current_metrics;
    const previousMetrics = response.data.metrics.previous_metrics;
    const changes = calculateChanges(previousMetrics, currentMetrics);
    setMetrics({
      current: response.data.metrics.current_metrics,
      changes: calculateChanges(response.data.previous_metrics, response.data.current_metrics),
      previous: response.data.metrics.previous_metrics
    });
    setMetricsData(
      [{
        label: 'Accuracy',
        value: currentMetrics.Accuracy,
        isPositive: changes.Accuracy === "positive",
        changeval: parseFloat(currentMetrics.Accuracy) - parseFloat(previousMetrics.Accuracy)
      },
      {
        label: 'RMSE',
        value: currentMetrics.RMSE,
        isPositive: changes.RMSE === "positive",
        changeval: parseFloat(currentMetrics.RMSE) - parseFloat(previousMetrics.RMSE)
      },
      {
        label: 'MAE',
        value: currentMetrics.MAE,
        isPositive: changes.MAE === "positive",
        changeval: parseFloat(currentMetrics.MAE) - parseFloat(previousMetrics.MAE)
      },
      {
        label: 'Training Time',
        value: currentMetrics["Training Time"],
        isPositive: changes["Training Time"] === "positive",
        changeval: parseFloat(currentMetrics["Training Time"]) - parseFloat(previousMetrics["Training Time"])
      }]
    )
  
    console.log(metricsData);
  };
  

  // Calculate changes between current and previous metrics
  const calculateChanges = (previous, current) => {
    if (!previous || !current) return {};
    
    return {
      "Accuracy": parseFloat(current.Accuracy) > parseFloat(previous.Accuracy) ? "positive" : "negative",
      "RMSE": parseFloat(current.RMSE) < parseFloat(previous.RMSE) ? "positive" : "negative",
      "MAE": parseFloat(current.MAE) < parseFloat(previous.MAE) ? "positive" : "negative",
      "Training Time": parseFloat(current["Training Time"]) < parseFloat(previous["Training Time"]) ? "positive" : "negative"
    };
  };

  // Fetch stock prediction data


const fetchPrediction = async () => {
    setLoading(true);
    setError('');
    
    // Create a toast and store its ID to update later
    const toastId = toast.loading('Fetching prediction...',{ autoClose: 1 });
  
    try {
      const response = await axios.post('http://localhost:5000/predict', { stock,model_type: modelPred});
  
      // Update the toast after the successful response
      toast.update(toastId, {
        render: 'Prediction fetched successfully!',
        type: 'success', // Use 'success' as string
        isLoading: false, // Mark the toast as not loading
        autoClose: 3000, // Automatically close the toast after 3 seconds
      });
  
      setOriginal(response.data.original);
      setPredicted(response.data.predicted);
    } catch (err) {
      console.error(err);
  
      // Update the toast after an error occurs
      toast.update(toastId, {
        render: err.response?.data?.error || 'Something went wrong. Please try again.',
        type: 'error', // Use 'error' as string
        isLoading: false, // Mark the toast as not loading
        autoClose: 3000, // Automatically close the toast after 3 seconds
      });
  
      setError(err.response?.data?.error || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false); // This will ensure loading state is set to false in all cases (success or error)
    }
  };
  

  // Train model
  const trainModel = async () => {
    setLoading(true);
    const toastId = toast.loading('Starting model training...', { autoClose: false });
  
    try {
      const response = await axios.post('http://localhost:5000/train', {
        stock: stockTrain,
        start: startDate,
        end: endDate,
        epochs,
        model_type: modelType
      });
  
      toast.update(toastId, {
        render: 'Model training completed successfully!',
        type: 'success',
        isLoading: false,
        autoClose: 5000
      });
  
      // Update metrics after training
      if (response.data.metrics) {
        setMetrics({
          current: response.data.metrics,
          previous: metrics.current,
          changes: response.data.changes || {}
        });
      }
    } catch (err) {
      console.error(err);
      toast.update(toastId, {
        render: err.response?.data?.error || 'Error during model training.',
        type: 'error',
        isLoading: false,
        autoClose: 5000
      });
    }
  
    setLoading(false);
  };
  

  // Chart data configuration
  const chartData = {
    labels: original.map((_, i) => i),
    datasets: [
      {
        label: 'Original Price',
        data: original,
        fill: false,
        borderColor: '#2ecc71',
        backgroundColor: 'rgba(46, 204, 113, 0.1)',
        borderWidth: 2,
        pointRadius: 1,
        tension: 0.4,
      },
      {
        label: 'Predicted Price',
        data: predicted,
        fill: false,
        borderColor: '#3498db',
        backgroundColor: 'rgba(52, 152, 219, 0.1)',
        borderWidth: 2,
        pointRadius: 1,
        tension: 0.4,
      },
    ],
  };

  // Chart options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(44, 62, 80, 0.9)',
        bodyFont: {
          family: "'Inter', sans-serif",
          size: 13
        },
        titleFont: {
          family: "'Inter', sans-serif",
          size: 14,
          weight: 'bold'
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        }
      },
      y: {
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        }
      }
    }
  };

  // Prepare metrics for display


  return (
    <>
    <div className="dashboard">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <span className="logo-icon">📈</span>
            <span>FinanceAI Pro</span>
          </div>
        </div>
        <div className="nav-menu">
          <div 
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <i className="nav-icon">📊</i>
            <span>Dashboard</span>
          </div>
          <div 
            className={`nav-item ${activeTab === 'predict' ? 'active' : ''}`}
            onClick={() => setActiveTab('predict')}
          >
            <i className="nav-icon">🔮</i>
            <span>Predict</span>
          </div>
          <div 
            className={`nav-item ${activeTab === 'train' ? 'active' : ''}`}
            onClick={() => setActiveTab('train')}
          >
            <i className="nav-icon">⚙️</i>
            <span>Train Model</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <div className="header">
          <h1 className="page-title">
            {activeTab === 'dashboard' && 'Stock Prediction Dashboard'}
            {activeTab === 'predict' && 'Stock Price Prediction'}
            {activeTab === 'train' && 'Model Training'}
          </h1>
          <div className="user-avatar">JD</div>
        </div>

        {/* Dashboard View */}
        {activeTab === 'dashboard' && (
          <>
            <div className="dashboard-grid">
              {console.log(metricsData)}
              {metricsData.map((metric, index) => (
                <div className="card card-sm" key={index}>
                  <div className="stat-card">
                    <div className="stat-value">{metric.value}</div>
                    <div className="stat-label">{metric.label}</div>
                    { (
                      <div className={`stat-change ${metric.isPositive ? 'positive' : 'negative'}`}>
                        {metric.isPositive ? '↑' : '↓'} 
                        {metric.changeval.toFixed(2)}
                      </div>
                    )}
                  </div>  
                </div>
              ))}
            </div>

            <div className="dashboard-grid">
              <div className="card card-lg">
                <div className="card-header">
                  <h2 className="card-title">Latest Predictions</h2>
                  <div className="card-actions">
                    <button className="btn btn-primary" onClick={() => setActiveTab('predict')}>New Prediction</button>
                  </div>
                </div>
                <div className="card-body">
                  {original.length > 0 ? (
                    <>
                      <div className="chart-container">
                        <Line data={chartData} options={chartOptions} />
                      </div>
                      <div className="chart-legend">
                        <div className="legend-item">
                          <div className="legend-color color-original"></div>
                          <span>Original Price</span>
                        </div>
                        <div className="legend-item">
                          <div className="legend-color color-predicted"></div>
                          <span>Predicted Price</span>
                        </div>
                      </div>
                    </>
                  ) : (
                    <div style={{ padding: '3rem 0', textAlign: 'center', color: '#95a5a6' }}>
                      No prediction data available. Make a prediction to see results.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </>
        )}

        {/* Prediction View */}
        {activeTab === 'predict' && (
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
                        <option value="lstm">LSTM</option>
                        <option value="simplernn">Simple RNN</option>
                      </select>
                    </div>
                    <button 
                      onClick={fetchPrediction} 
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
                  <>
                    <div className="chart-container">
                      <Line data={chartData} options={chartOptions} />
                    </div>
                    <div className="chart-legend">
                      <div className="legend-item">
                        <div className="legend-color color-original"></div>
                        <span>Original Price</span>
                      </div>
                      <div className="legend-item">
                        <div className="legend-color color-predicted"></div>
                        <span>Predicted Price</span>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Training View */}
        {activeTab === 'train' && (
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
                        min="1"
                        max="100"
                      />
                    </div>
                    <div className="form-col">
                      <select
                        value={modelType}
                        onChange={(e) => setModelType(e.target.value)}
                        className="form-control"
                      >
                        <option value="lstm">LSTM</option>
                        <option value="simplernn">Simple RNN</option>
                      </select>
                    </div>
                    <button 
                      onClick={trainModel} 
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
        )}

        {/* Toast Container */}
      </div>
    </div>
    <ToastSetup/>

    </>
  );
}

export default App;