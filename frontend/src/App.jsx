import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { HistoryProvider } from './contexts/HistoryContext';
import SearchBar from './components/SearchBar';
import VideoCard from './components/VideoCard';
import ScoreCard from './components/ScoreCard';
import LoadingSpinner from './components/LoadingSpinner';
import History from './pages/History';
import Home from './pages/Home';
import Result from './pages/Result';
import Admin from './pages/Admin';
import Login from './pages/Login';
import './styles/global.css';

const App = () => {
  return (
    <HistoryProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/result/:videoId" element={<Result />} />
          <Route path="/login" element={<Login />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </Router>
    </HistoryProvider>
  );
};

export default App;
