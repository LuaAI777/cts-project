import React, { useState } from 'react';
import '../styles/SearchBar.css';

const SearchBar = ({ onSearch }) => {
  const [input, setInput] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    // URL 또는 비디오 ID 추출
    const videoId = extractVideoId(input);
    if (!videoId) {
      setError('유효한 YouTube URL 또는 비디오 ID를 입력해주세요.');
      return;
    }

    onSearch(videoId);
  };

  const extractVideoId = (url) => {
    // YouTube URL 패턴
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&?/]+)/,
      /^[a-zA-Z0-9_-]{11}$/ // 비디오 ID 패턴
    ];

    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) return match[1] || match[0];
    }

    return null;
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="input-group">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="YouTube URL 또는 비디오 ID를 입력하세요"
            className="search-input"
          />
          <button type="submit" className="search-button">
            검색
          </button>
        </div>
        {error && <p className="error-message">{error}</p>}
      </form>
    </div>
  );
};

export default SearchBar; 