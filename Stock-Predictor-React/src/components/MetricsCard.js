import React from 'react';

function MetricsCard({ metric }) {
  return (
    <div className="card card-sm">
      <div className="stat-card">
        <div className="stat-value">{metric.value}</div>
        <div className="stat-label">{metric.label}</div>
        <div className={`stat-change ${metric.isPositive ? 'positive' : 'negative'}`}>
          {metric.isPositive ? '↑' : '↓'} 
          {metric.changeval.toFixed(2)}
        </div>
      </div>  
    </div>
  );
}

export default MetricsCard;