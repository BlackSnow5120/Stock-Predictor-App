import React from 'react';

function Sidebar({ activeTab, setActiveTab }) {
  return (
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
          className={`nav-item ${activeTab === 'news' ? 'active' : ''}`}
          onClick={() => setActiveTab('news')}
        >
          <i className="nav-icon">📰</i>
          <span>News</span>
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
  );
}

export default Sidebar;