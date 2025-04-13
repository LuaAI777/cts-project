import React from 'react';
import '../styles/ScoreCard.css';

const ScoreCard = ({ evaluation }) => {
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
          style={{ backgroundColor: getGradeColor(evaluation.grade) }}
        >
          {evaluation.grade}
        </div>
        <div className="grade-info">
          <h3 className="grade-title">종합 등급</h3>
          <p className="grade-description">
            {getGradeDescription(evaluation.grade)}
          </p>
        </div>
      </div>

      <div className="score-section">
        <div className="score-bar">
          <div 
            className="score-progress"
            style={{ width: `${evaluation.total_score * 100}%` }}
          />
        </div>
        <span className="score-value">
          {Math.round(evaluation.total_score * 100)}점
        </span>
      </div>

      <div className="detail-section">
        <div className="detail-item">
          <span className="detail-label">출처/채널 신뢰도</span>
          <span className="detail-value">
            {Math.round(evaluation.trust_analysis.total_score * 100)}점
          </span>
        </div>
        <div className="detail-item">
          <span className="detail-label">내용 신뢰도</span>
          <span className="detail-value">
            {Math.round(evaluation.content_analysis.total_score * 100)}점
          </span>
        </div>
      </div>
    </div>
  );
};

export default ScoreCard; 