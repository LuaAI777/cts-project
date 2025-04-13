import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import SearchBar from '../components/SearchBar';

const Home = () => {
  const navigate = useNavigate();
  const [error, setError] = useState('');

  const handleSearch = async (input) => {
    try {
      // YouTube URL에서 비디오 ID 추출
      const videoId = extractVideoId(input);
      if (!videoId) {
        setError('유효한 YouTube URL 또는 비디오 ID를 입력하세요');
        return;
      }

      navigate(`/result/${videoId}`);
    } catch (err) {
      setError('오류가 발생했습니다. 다시 시도하세요.');
    }
  };

  const extractVideoId = (input) => {
    // YouTube URL 패턴
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/,
      /^[a-zA-Z0-9_-]{11}$/
    ];

    for (const pattern of patterns) {
      const match = input.match(pattern);
      if (match) {
        return match[1] || input;
      }
    }
    return null;
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          CTS (Content Trust Score)
        </h1>
        <p className="text-gray-600">
          YouTube 콘텐츠의 신뢰도를 평가합니다
        </p>
      </div>

      <SearchBar onSearch={handleSearch} />

      {error && (
        <p className="mt-4 text-red-600 text-sm">{error}</p>
      )}
    </div>
  );
};

export default Home; 