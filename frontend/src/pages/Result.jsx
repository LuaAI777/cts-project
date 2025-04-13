import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import VideoCard from '../components/VideoCard';
import ScoreCard from '../components/ScoreCard';
import LoadingSpinner from '../components/LoadingSpinner';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const Result = () => {
  const { videoId } = useParams();
  const navigate = useNavigate();
  const [videoInfo, setVideoInfo] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_BASE_URL}/evaluate/${videoId}`, {
          headers: {
            ...(localStorage.getItem('token') && {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }),
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error(`데이터를 불러오는 중 오류가 발생했습니다: ${response.status}`);
        }

        const data = await response.json();
        setVideoInfo(data.video_info);
        setEvaluation({
          trust_analysis: {
            details: `구독자 수: ${data.source_trust.subscriber_score * 100}%, 
                     채널 활동: ${data.source_trust.activity_score * 100}%, 
                     참여도: ${data.source_trust.engagement_score * 100}%`,
            total_score: data.source_trust.total_score
          },
          content_analysis: {
            details: `제목 분석: ${data.content_trust.title_score * 100}%, 
                     설명 분석: ${data.content_trust.description_score * 100}%, 
                     감정 분석: ${data.content_trust.sentiment_score * 100}%`,
            total_score: data.content_trust.total_score
          },
          total_score: data.final_score.final_score,
          grade: data.final_score.grade
        });
      } catch (err) {
        console.error('데이터 로딩 중 오류:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [videoId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-4">오류가 발생했습니다</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            홈으로 돌아가기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <button
            onClick={() => navigate('/')}
            className="text-blue-600 hover:text-blue-800 flex items-center"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            홈으로 돌아가기
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">비디오 정보</h2>
            {videoInfo && <VideoCard video={videoInfo} />}
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">신뢰도 평가</h2>
            {evaluation && <ScoreCard evaluation={evaluation} />}
          </div>
        </div>

        <div className="mt-8 bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">상세 분석</h2>
          {evaluation && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium text-gray-900 mb-2">출처/채널 신뢰도</h3>
                  <p className="text-gray-600">{evaluation.trust_analysis.details}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium text-gray-900 mb-2">내용 신뢰도</h3>
                  <p className="text-gray-600">{evaluation.content_analysis.details}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Result; 