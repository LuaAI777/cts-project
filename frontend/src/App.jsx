import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation, Navigate } from 'react-router-dom';
import { HistoryProvider, useHistory } from './contexts/HistoryContext';
import SearchBar from './components/SearchBar';
import VideoCard from './components/VideoCard';
import ScoreCard from './components/ScoreCard';
import LoadingSpinner from './components/LoadingSpinner';
import History from './pages/History';
import './styles/global.css';

const Home = () => {
  const navigate = useNavigate();
  const { addHistory } = useHistory();
  const [loading, setLoading] = useState(false);

  const handleSearch = async (videoId) => {
    setLoading(true);
    try {
      // API 호출
      const videoResponse = await fetch(`/api/youtube/video/${videoId}`);
      const videoData = await videoResponse.json();

      const scoreResponse = await fetch(`/api/evaluate/${videoId}`);
      const scoreData = await scoreResponse.json();

      // 히스토리에 추가
      addHistory(videoData, scoreData);

      // 결과 페이지로 이동
      navigate('/result', { state: { video: videoData, score: scoreData } });
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1 className="text-center text-3xl font-bold mb-8">
        CTS (Content Trust Score)
      </h1>
      {loading ? (
        <LoadingSpinner />
      ) : (
        <SearchBar onSearch={handleSearch} />
      )}
    </div>
  );
};

const Result = () => {
  const { video, score } = useLocation().state || {};

  if (!video || !score) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="container">
      <div className="grid gap-6">
        <VideoCard video={video} />
        <ScoreCard score={score} />
      </div>
    </div>
  );
};

const App = () => {
  return (
    <HistoryProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/result" element={<Result />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </Router>
    </HistoryProvider>
  );
};

export default App;
