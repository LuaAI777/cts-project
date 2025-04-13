import React, { createContext, useContext, useState, useEffect } from 'react';

const HistoryContext = createContext();

export const HistoryProvider = ({ children }) => {
  const [histories, setHistories] = useState([]);

  useEffect(() => {
    // 로컬 스토리지에서 히스토리 로드
    const savedHistories = localStorage.getItem('cts_histories');
    if (savedHistories) {
      setHistories(JSON.parse(savedHistories));
    }
  }, []);

  const addHistory = (video, score) => {
    const newHistory = {
      id: Date.now(),
      title: video.title,
      videoId: video.videoId,
      date: new Date().toISOString(),
      grade: score.grade,
      totalScore: score.totalScore,
      sourceScore: score.sourceScore,
      contentScore: score.contentScore
    };

    const updatedHistories = [newHistory, ...histories].slice(0, 10); // 최근 10개만 유지
    setHistories(updatedHistories);
    localStorage.setItem('cts_histories', JSON.stringify(updatedHistories));
  };

  const clearHistory = () => {
    setHistories([]);
    localStorage.removeItem('cts_histories');
  };

  return (
    <HistoryContext.Provider value={{ histories, addHistory, clearHistory }}>
      {children}
    </HistoryContext.Provider>
  );
};

export const useHistory = () => {
  const context = useContext(HistoryContext);
  if (!context) {
    throw new Error('useHistory must be used within a HistoryProvider');
  }
  return context;
}; 