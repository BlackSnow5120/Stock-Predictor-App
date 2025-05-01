import React from 'react';

function Header({ activeTab }) {
  return (
    <div className="header">
      <h1 className="page-title">
        {activeTab === 'dashboard' && 'Stock Prediction Dashboard'}
        {activeTab === 'predict' && 'Stock Price Prediction'}
        {activeTab === 'train' && 'Model Training'}
      </h1>
      <div className="user-avatar">JD</div>
    </div>
  );
}

export default Header;