import React from 'react';
import { useHistory } from '../contexts/HistoryContext';
import HistoryCard from '../components/HistoryCard';
import '../styles/History.css';

const History = () => {
  const { histories, clearHistory } = useHistory();

  return (
    <div className="container">
      <div className="history-header">
        <h1 className="history-title">검색 히스토리</h1>
        {histories.length > 0 && (
          <button className="clear-button" onClick={clearHistory}>
            전체 삭제
          </button>
        )}
      </div>

      {histories.length === 0 ? (
        <div className="empty-history">
          <p>아직 검색 기록이 없습니다.</p>
        </div>
      ) : (
        <div className="history-list">
          {histories.map((history) => (
            <HistoryCard key={history.id} history={history} />
          ))}
        </div>
      )}
    </div>
  );
};

export default History; 