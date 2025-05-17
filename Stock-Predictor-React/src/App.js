import React, { useState, useEffect } from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './style.css';

// Components
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import PredictionView from './components/PredictionView';
import TrainingView from './components/TrainingView';
import News from './components/news';


// Services
import { fetchMetricsData } from './services/api';
import ToastSetup from './toast';

function App() {
  // UI state
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  
  // Data state
  const [original, setOriginal] = useState([]);
  const [predicted, setPredicted] = useState([]);
  const [metricsData, setMetricsData] = useState([]);
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

  // Fetch metrics when component mounts
  useEffect(() => {
    const loadMetrics = async () => {
      const data = await fetchMetricsData();
      setMetrics(data.metrics);
      setMetricsData(data.metricsData);
    };
    
    loadMetrics();
  }, []);

  return (
    <>
      <div className="dashboard">
        {/* Sidebar */}
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

        {/* Main Content */}
        <div className="main-content">
          <Header activeTab={activeTab} />

          {/* Dashboard View */}
          {activeTab === 'dashboard' && (
            <Dashboard 
              metricsData={metricsData} 
              original={original} 
              predicted={predicted}
              setActiveTab={setActiveTab} 
            />
          )}

          {activeTab === 'news' && (
            <News
              setActiveTab={setActiveTab} 
            />
          )}

          {/* Prediction View */}
          {activeTab === 'predict' && (
            <PredictionView
              setOriginal={setOriginal}
              setPredicted={setPredicted}
              loading={loading}
              setLoading={setLoading}
              original={original}
              predicted={predicted}
            />
          )}

          {/* Training View */}
          {activeTab === 'train' && (
            <TrainingView
              loading={loading}
              setLoading={setLoading}
              setMetrics={setMetrics}
              metrics={metrics}
              setMetricsData={setMetricsData}
            />
          )}
        </div>
      </div>
      <ToastSetup />
    </>
  );
}

export default App;