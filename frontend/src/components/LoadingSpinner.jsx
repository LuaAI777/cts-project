import React from 'react';
import '../styles/LoadingSpinner.css';

const LoadingSpinner = () => {
  return (
    <div className="loading-container">
      <div className="spinner" />
      <p className="loading-text">분석 중입니다...</p>
    </div>
  );
};

export default LoadingSpinner; 