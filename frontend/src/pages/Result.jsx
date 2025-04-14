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
    let isMounted = true;

    const fetchData = async () => {
      try {
        if (!videoId) {
          throw new Error('비디오 ID가 제공되지 않았습니다.');
        }

        setLoading(true);
        setError(null);

        const token = localStorage.getItem('token');
        const headers = {
          'Content-Type': 'application/json'
        };

        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${API_BASE_URL}/evaluate/${videoId}`, {
          headers,
          credentials: 'include'
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `서버 오류 (${response.status})`);
        }

        const data = await response.json();

        if (!isMounted) return;

        // 데이터 유효성 검사
        if (!data.video_info || !data.source_trust || !data.content_trust || !data.final_score) {
          throw new Error('서버에서 불완전한 데이터를 받았습니다.');
        }

        setVideoInfo(data.video_info);
        setEvaluation({
          trust_analysis: {
            details: [
              { label: '구독자 수', score: data.source_trust.subscriber_score },
              { label: '채널 활동', score: data.source_trust.activity_score },
              { label: '참여도', score: data.source_trust.engagement_score }
            ],
            total_score: data.source_trust.total_score
          },
          content_analysis: {
            details: [
              { label: '제목 분석', score: data.content_trust.title_score },
              { label: '설명 분석', score: data.content_trust.description_score },
              { label: '감정 분석', score: data.content_trust.sentiment_score }
            ],
            total_score: data.content_trust.total_score
          },
          total_score: data.final_score,
          grade: data.grade,
          grade_description: data.grade_description
        });
      } catch (err) {
        if (!isMounted) return;
        console.error('데이터 로딩 중 오류:', err);
        setError(err.message);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      isMounted = false;
    };
  }, [videoId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center">
        <LoadingSpinner />
        <p className="mt-4 text-gray-600">데이터를 불러오는 중입니다...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
        <div className="text-center max-w-md">
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

  const scores = [
    {
      label: '출처/채널 신뢰도',
      items: [
        { label: '구독자 수', score: evaluation.trust_analysis.details[0].score },
        { label: '채널 활동', score: evaluation.trust_analysis.details[1].score },
        { label: '참여도', score: evaluation.trust_analysis.details[2].score }
      ]
    },
    {
      label: '내용 신뢰도',
      items: [
        { label: '제목 분석', score: evaluation.content_analysis.details[0].score },
        { label: '설명 분석', score: evaluation.content_analysis.details[1].score },
        { label: '감정 분석', score: evaluation.content_analysis.details[2].score }
      ]
    }
  ];

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
            <div className="space-y-8">
              {scores.map((section, index) => (
                <div key={index} className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold mb-4">{section.label}</h3>
                  <div className="space-y-4">
                    {section.items.map((item, idx) => (
                      <div key={idx} className="flex items-center justify-between">
                        <span className="text-gray-600">{item.label}</span>
                        <div className="flex items-center gap-2">
                          <div className="w-32 h-2 bg-gray-200 rounded-full">
                            <div 
                              className={`h-full rounded-full ${
                                section.label.includes('출처') ? 'bg-blue-500' : 'bg-green-500'
                              }`}
                              style={{ width: `${item.score}%` }}
                            />
                          </div>
                          <span className="text-gray-700 font-medium">{item.score.toFixed(1)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Result; 
export default Result; 