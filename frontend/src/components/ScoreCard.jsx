import React from 'react';
import '../styles/ScoreCard.css';

const ScoreCard = ({ score }) => {
  const getGradeColor = (grade) => {
    switch (grade) {
      case 'A': return '#10B981';
      case 'B': return '#3B82F6';
      case 'C': return '#F59E0B';
      case 'D': return '#EF4444';
      case 'F': return '#6B7280';
      default: return '#6B7280';
    }
  };

  const getGradeDescription = (grade) => {
    switch (grade) {
      case 'A': return '매우 신뢰할 수 있음';
      case 'B': return '신뢰할 수 있음';
      case 'C': return '보통';
      case 'D': return '주의 필요';
      case 'F': return '신뢰할 수 없음';
      default: return '평가 불가';
    }
  };

  return (
    <div className="score-card">
      <div className="grade-section">
        <div 
          className="grade-circle"
          style={{ backgroundColor: getGradeColor(score.grade) }}
        >
          {score.grade}
        </div>
        <div className="grade-info">
          <h3 className="grade-title">종합 등급</h3>
          <p className="grade-description">
            {getGradeDescription(score.grade)}
          </p>
        </div>
      </div>

      <div className="score-section">
        <div className="score-bar">
          <div 
            className="score-progress"
            style={{ width: `${score.totalScore * 100}%` }}
          />
        </div>
        <span className="score-value">
          {Math.round(score.totalScore * 100)}점
        </span>
      </div>

      <div className="detail-section">
        <div className="detail-item">
          <span className="detail-label">출처/채널 신뢰도</span>
          <span className="detail-value">
            {Math.round(score.sourceScore * 100)}점
          </span>
        </div>
        <div className="detail-item">
          <span className="detail-label">내용 신뢰도</span>
          <span className="detail-value">
            {Math.round(score.contentScore * 100)}점
          </span>
        </div>
      </div>
    </div>
  );
};

export default ScoreCard; 