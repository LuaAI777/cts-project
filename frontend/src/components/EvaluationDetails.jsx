import React from 'react';
import '../styles/EvaluationDetails.css';

const EvaluationDetails = ({ evaluation }) => {
  const { factors } = evaluation;

  return (
    <div className="evaluation-details">
      <div className="detail-section">
        <h3 className="section-title">출처/채널 신뢰도 분석</h3>
        <div className="factor-grid">
          <div className="factor-item">
            <h4 className="factor-title">구독자 수</h4>
            <div className="factor-content">
              <span className="factor-value">{factors.source.subscribers.count.toLocaleString()}명</span>
              <div className="score-bar">
                <div 
                  className="score-progress"
                  style={{ width: `${factors.source.subscribers.score * 100}%` }}
                />
              </div>
            </div>
          </div>

          <div className="factor-item">
            <h4 className="factor-title">활동 기간</h4>
            <div className="factor-content">
              <span className="factor-value">{factors.source.activity.days}일</span>
              <div className="score-bar">
                <div 
                  className="score-progress"
                  style={{ width: `${factors.source.activity.score * 100}%` }}
                />
              </div>
            </div>
          </div>

          <div className="factor-item">
            <h4 className="factor-title">참여도</h4>
            <div className="factor-content">
              <div className="engagement-metrics">
                <span>좋아요: {(factors.source.engagement.likeRatio * 100).toFixed(1)}%</span>
                <span>댓글: {(factors.source.engagement.commentRatio * 100).toFixed(1)}%</span>
              </div>
              <div className="score-bar">
                <div 
                  className="score-progress"
                  style={{ width: `${factors.source.engagement.score * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="detail-section">
        <h3 className="section-title">내용 신뢰도 분석</h3>
        <div className="factor-grid">
          <div className="factor-item">
            <h4 className="factor-title">제목 분석</h4>
            <div className="factor-content">
              <span className="factor-value">{factors.content.title.length}자</span>
              <div className="score-bar">
                <div 
                  className="score-progress"
                  style={{ width: `${factors.content.title.score * 100}%` }}
                />
              </div>
            </div>
          </div>

          <div className="factor-item">
            <h4 className="factor-title">설명 분석</h4>
            <div className="factor-content">
              <span className="factor-value">{factors.content.description.length}자</span>
              <div className="score-bar">
                <div 
                  className="score-progress"
                  style={{ width: `${factors.content.description.score * 100}%` }}
                />
              </div>
            </div>
          </div>

          <div className="factor-item">
            <h4 className="factor-title">감정 분석</h4>
            <div className="factor-content">
              <span className="factor-value">
                {factors.content.sentiment.value > 0 ? '긍정적' : 
                 factors.content.sentiment.value < 0 ? '부정적' : '중립적'}
              </span>
              <div className="score-bar">
                <div 
                  className="score-progress"
                  style={{ width: `${factors.content.sentiment.score * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EvaluationDetails; 