import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Admin = () => {
  const navigate = useNavigate();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [config, setConfig] = useState({
    weights: {
      source: 0.6,
      content: 0.4
    },
    thresholds: {
      subscribers: {
        high: 1000000,
        medium: 100000,
        low: 10000
      },
      activity: {
        high: 365,
        medium: 180,
        low: 90
      }
    },
    keywords: {
      required: ['연구', '데이터', '출처'],
      suspicious: ['확실', '무조건', '100%']
    }
  });
  const [history, setHistory] = useState([]);
  const [pendingChanges, setPendingChanges] = useState([]);
  const [showPendingModal, setShowPendingModal] = useState(false);
  const [showRollbackModal, setShowRollbackModal] = useState(false);
  const [selectedHistoryId, setSelectedHistoryId] = useState(null);
  const [activeTab, setActiveTab] = useState('settings');

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }

        // 토큰 유효성 검사
        await axios.get('http://localhost:8000/api/admin/config', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setIsAuthenticated(true);
      } catch (error) {
        localStorage.removeItem('token');
        navigate('/login');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [navigate]);

  useEffect(() => {
    fetchConfig();
    fetchHistory();
    fetchPendingChanges();
  }, []);

  const fetchConfig = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:8000/api/admin/config', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConfig(response.data);
    } catch (error) {
      console.error('설정 조회 실패:', error);
    }
  };

  const fetchHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:8000/api/admin/history', {
        headers: { Authorization: `Bearer ${token}` }
      });
      // 각 변경 이력에 고유한 id 추가
      const historyWithId = response.data.map((item, index) => ({
        ...item,
        id: index
      }));
      setHistory(historyWithId);
    } catch (error) {
      console.error('히스토리 조회 실패:', error);
    }
  };

  const handleConfigChange = async (section, key, value) => {
    try {
      const token = localStorage.getItem('token');
      const newConfig = {
        ...config,
        [section]: {
          ...config[section],
          [key]: value
        }
      };
      
      // 숫자로 변환
      if (typeof value === 'string' && !isNaN(value)) {
        newConfig[section][key] = parseFloat(value);
      }
      
      await axios.post('http://localhost:8000/api/admin/config', newConfig, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      setConfig(newConfig);
    } catch (error) {
      console.error('설정 변경 실패:', error);
    }
  };

  const handleSubmitPending = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:8000/api/admin/config/pending', config, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('변경 요청이 제출되었습니다.');
      // 즉시 데이터를 새로고침
      await Promise.all([
        fetchPendingChanges(),
        fetchConfig(),
        fetchHistory()
      ]);
    } catch (error) {
      console.error('변경 요청 제출 실패:', error);
    }
  };

  const handleApproveChange = async (changeId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/admin/config/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ change_id: changeId })
      });
      
      if (!response.ok) {
        throw new Error('변경 승인에 실패했습니다.');
      }
      
      // 변경 이력과 대기 중인 변경 목록 새로고침
      await Promise.all([
        fetchPendingChanges(),
        fetchConfig(),
        fetchHistory()
      ]);
    } catch (error) {
      console.error('변경 승인 중 오류 발생:', error);
    }
  };

  const handleRollback = async (index) => {
    try {
      const token = localStorage.getItem('token');
      const change = history[index];
      await axios.post('http://localhost:8000/api/admin/config/rollback', change, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // 모든 데이터 새로고침
      await Promise.all([
        fetchConfig(),
        fetchHistory()
      ]);
    } catch (error) {
      console.error('롤백 실패:', error);
    }
  };

  const fetchPendingChanges = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:8000/api/admin/config/pending', {
        headers: { Authorization: `Bearer ${token}` }
      });
      // 각 변경 요청에 고유한 id 추가
      const changesWithId = response.data.map((change, index) => ({
        ...change,
        id: index
      }));
      setPendingChanges(changesWithId);
    } catch (error) {
      console.error('대기 중인 변경 조회 실패:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* 헤더 */}
      <div className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-2xl font-bold text-gray-900">CTS 관리자</h1>
              </div>
              <nav className="ml-6 flex space-x-8">
                <button
                  onClick={() => setActiveTab('settings')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                    activeTab === 'settings' 
                      ? 'bg-blue-600 text-white shadow-md' 
                      : 'text-white bg-gray-500 hover:bg-gray-600'
                  }`}
                >
                  설정
                </button>
                <button
                  onClick={() => setActiveTab('pending')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                    activeTab === 'pending' 
                      ? 'bg-blue-600 text-white shadow-md' 
                      : 'text-white bg-gray-500 hover:bg-gray-600'
                  }`}
                >
                  대기 중인 변경
                </button>
                <button
                  onClick={() => setActiveTab('history')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                    activeTab === 'history' 
                      ? 'bg-blue-600 text-white shadow-md' 
                      : 'text-white bg-gray-500 hover:bg-gray-600'
                  }`}
                >
                  변경 이력
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>

      {/* 메인 컨텐츠 */}
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {activeTab === 'settings' && (
          <div className="bg-white shadow-lg rounded-lg p-6 transform transition-all duration-200 hover:shadow-xl">
            <h2 className="text-xl font-semibold text-gray-900 mb-6 border-b pb-2">평가 기준 설정</h2>
            
            {/* 가중치 설정 */}
            <div className="mb-8 bg-gray-50 p-4 rounded-lg">
              <h3 className="text-md font-medium text-gray-700 mb-4">가중치 설정</h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <label className="block text-sm font-medium text-gray-700">출처/채널 가중치</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="1"
                    value={config.weights.source}
                    onChange={(e) => handleConfigChange('weights', 'source', parseFloat(e.target.value))}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <label className="block text-sm font-medium text-gray-700">내용 가중치</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="1"
                    value={config.weights.content}
                    onChange={(e) => handleConfigChange('weights', 'content', parseFloat(e.target.value))}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            {/* 구독자 기준 설정 */}
            <div className="mb-8 bg-gray-50 p-4 rounded-lg">
              <h3 className="text-md font-medium text-gray-700 mb-4">구독자 기준 설정</h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <label className="block text-sm font-medium text-gray-700">높음</label>
                  <input
                    type="number"
                    value={config.thresholds.subscribers.high}
                    onChange={(e) => handleConfigChange('thresholds', 'subscribers', {
                      ...config.thresholds.subscribers,
                      high: parseInt(e.target.value)
                    })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <label className="block text-sm font-medium text-gray-700">중간</label>
                  <input
                    type="number"
                    value={config.thresholds.subscribers.medium}
                    onChange={(e) => handleConfigChange('thresholds', 'subscribers', {
                      ...config.thresholds.subscribers,
                      medium: parseInt(e.target.value)
                    })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <label className="block text-sm font-medium text-gray-700">낮음</label>
                  <input
                    type="number"
                    value={config.thresholds.subscribers.low}
                    onChange={(e) => handleConfigChange('thresholds', 'subscribers', {
                      ...config.thresholds.subscribers,
                      low: parseInt(e.target.value)
                    })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            {/* 활동성 기준 설정 */}
            <div className="mb-8 bg-gray-50 p-4 rounded-lg">
              <h3 className="text-md font-medium text-gray-700 mb-4">활동성 기준 설정</h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <label className="block text-sm font-medium text-gray-700">높음</label>
                  <input
                    type="number"
                    value={config.thresholds.activity.high}
                    onChange={(e) => handleConfigChange('thresholds', 'activity', {
                      ...config.thresholds.activity,
                      high: parseInt(e.target.value)
                    })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <label className="block text-sm font-medium text-gray-700">중간</label>
                  <input
                    type="number"
                    value={config.thresholds.activity.medium}
                    onChange={(e) => handleConfigChange('thresholds', 'activity', {
                      ...config.thresholds.activity,
                      medium: parseInt(e.target.value)
                    })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <label className="block text-sm font-medium text-gray-700">낮음</label>
                  <input
                    type="number"
                    value={config.thresholds.activity.low}
                    onChange={(e) => handleConfigChange('thresholds', 'activity', {
                      ...config.thresholds.activity,
                      low: parseInt(e.target.value)
                    })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            {/* 키워드 설정 */}
            <div className="mb-8 bg-gray-50 p-4 rounded-lg">
              <h3 className="text-md font-medium text-gray-700 mb-4">키워드 설정</h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <label className="block text-sm font-medium text-gray-700">필수 키워드</label>
                  <textarea
                    value={config.keywords.required.join(', ')}
                    onChange={(e) => handleConfigChange('keywords', 'required', e.target.value.split(',').map(k => k.trim()))}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    rows="3"
                  />
                </div>
                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <label className="block text-sm font-medium text-gray-700">의심 키워드</label>
                  <textarea
                    value={config.keywords.suspicious.join(', ')}
                    onChange={(e) => handleConfigChange('keywords', 'suspicious', e.target.value.split(',').map(k => k.trim()))}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    rows="3"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end">
              <button
                onClick={handleSubmitPending}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors duration-200 shadow-md"
              >
                변경 요청
              </button>
            </div>
          </div>
        )}

        {activeTab === 'pending' && (
          <div className="bg-white shadow-lg rounded-lg p-6 transform transition-all duration-200 hover:shadow-xl">
            <h2 className="text-xl font-semibold text-gray-900 mb-6 border-b pb-2">대기 중인 변경</h2>
            {pendingChanges.length === 0 ? (
              <p className="text-gray-500 text-center py-8">대기 중인 변경이 없습니다.</p>
            ) : (
              <div className="space-y-4">
                {pendingChanges.map((change) => (
                  <div key={change.id} className="border rounded-lg p-4 bg-gray-50 hover:bg-gray-100 transition-colors duration-200">
                    <div className="flex justify-between items-center mb-2">
                      <h3 className="text-md font-medium text-gray-900">변경 요청 #{change.id}</h3>
                      <button
                        onClick={() => handleApproveChange(change.id)}
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors duration-200 shadow-md"
                      >
                        승인
                      </button>
                    </div>
                    <pre className="text-sm text-gray-600 whitespace-pre-wrap bg-white p-4 rounded-lg">
                      {JSON.stringify(change.changes, null, 2)}
                    </pre>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'history' && (
          <div className="bg-white shadow-lg rounded-lg p-6 transform transition-all duration-200 hover:shadow-xl">
            <h2 className="text-xl font-semibold text-gray-900 mb-6 border-b pb-2">변경 이력</h2>
            {history.length === 0 ? (
              <p className="text-gray-500 text-center py-8">변경 이력이 없습니다.</p>
            ) : (
              <div className="space-y-4">
                {history.map((item, index) => (
                  <div key={`history-${index}`} className="p-4 border-b">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">{item.timestamp}</span>
                      <span className="text-gray-800">{item.user}</span>
                    </div>
                    <div className="mt-2">{item.changes}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* 롤백 모달 */}
      {showRollbackModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center">
          <div className="bg-white rounded-lg p-6 max-w-md w-full shadow-xl">
            <h3 className="text-lg font-medium text-gray-900 mb-4">변경 롤백</h3>
            <p className="text-sm text-gray-500 mb-4">
              선택한 변경을 롤백하시겠습니까?
            </p>
            <div className="flex justify-end space-x-4">
              <button
                onClick={() => setShowRollbackModal(false)}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors duration-200 shadow-md"
              >
                취소
              </button>
              <button
                onClick={() => handleRollback(selectedHistoryId)}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors duration-200 shadow-md"
              >
                롤백
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Admin; 