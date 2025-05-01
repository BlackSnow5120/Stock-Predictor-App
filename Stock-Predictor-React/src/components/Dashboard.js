import React from 'react';
import MetricsCard from './MetricsCard';
import ChartDisplay from './ChartDisplay';

function Dashboard({ metricsData, original, predicted, setActiveTab }) {
  return (
    <>
      <div className="dashboard-grid">
        {metricsData.map((metric, index) => (
          <MetricsCard key={index} metric={metric} />
        ))}
      </div>

      <div className="dashboard-grid">
        <div className="card card-lg">
          <div className="card-header">
            <h2 className="card-title">Latest Predictions</h2>
            <div className="card-actions">
              <button className="btn btn-primary" onClick={() => setActiveTab('predict')}>
                New Prediction
              </button>
            </div>
          </div>
          <div className="card-body">
            {original.length > 0 ? (
              <ChartDisplay original={original} predicted={predicted} />
            ) : (
              <div style={{ padding: '3rem 0', textAlign: 'center', color: '#95a5a6' }}>
                No prediction data available. Make a prediction to see results.
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default Dashboard;