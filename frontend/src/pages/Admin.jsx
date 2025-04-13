import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Admin = () => {
  const [config, setConfig] = useState({
    weights: { source: 0.6, content: 0.4 },
    thresholds: {
      subscribers: { high: 1000000, medium: 100000, low: 10000 },
      activity: { high: 365, medium: 180, low: 90 }
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
    fetchConfig();
    fetchHistory();
    fetchPendingChanges();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await axios.get('/api/admin/config');
      setConfig(response.data);
    } catch (error) {
      console.error('설정 조회 실패:', error);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await axios.get('/api/admin/history');
      setHistory(response.data);
    } catch (error) {
      console.error('히스토리 조회 실패:', error);
    }
  };

  const handleConfigChange = (section, key, value) => {
    setConfig(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }));
  };

  const handleSubmitPending = async () => {
    try {
      await axios.post('/api/admin/config/pending', config);
      setShowPendingModal(false);
      alert('변경 요청이 제출되었습니다.');
      fetchPendingChanges();
    } catch (error) {
      console.error('변경 요청 제출 실패:', error);
    }
  };

  const handleApproveChange = async (changeId) => {
    try {
      await axios.post(`/api/admin/config/approve/${changeId}`);
      alert('변경이 승인되었습니다.');
      fetchPendingChanges();
      fetchConfig();
    } catch (error) {
      console.error('변경 승인 실패:', error);
    }
  };

  const handleRollback = async (historyId) => {
    try {
      await axios.post(`/api/admin/config/rollback/${historyId}`);
      setShowRollbackModal(false);
      alert('설정이 롤백되었습니다.');
      fetchConfig();
      fetchHistory();
    } catch (error) {
      console.error('롤백 실패:', error);
    }
  };

  const fetchPendingChanges = async () => {
    try {
      const response = await axios.get('/api/admin/pending');
      setPendingChanges(response.data);
    } catch (error) {
      console.error('대기 중인 변경 조회 실패:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-xl font-bold text-gray-900">CTS 관리자</h1>
              </div>
              <nav className="ml-6 flex space-x-8">
                <button
                  onClick={() => setActiveTab('settings')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === 'settings' ? 'bg-gray-100 text-gray-900' : 'text-gray-500 hover:text-gray-900'
                  }`}
                >
                  설정
                </button>
                <button
                  onClick={() => setActiveTab('pending')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === 'pending' ? 'bg-gray-100 text-gray-900' : 'text-gray-500 hover:text-gray-900'
                  }`}
                >
                  대기 중인 변경
                </button>
                <button
                  onClick={() => setActiveTab('history')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === 'history' ? 'bg-gray-100 text-gray-900' : 'text-gray-500 hover:text-gray-900'
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
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">평가 기준 설정</h2>
            
            {/* 가중치 설정 */}
            <div className="mb-6">
              <h3 className="text-md font-medium text-gray-700 mb-3">가중치 설정</h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
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
                <div>
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
            <div className="mb-6">
              <h3 className="text-md font-medium text-gray-700 mb-3">구독자 기준 설정</h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div>
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
                <div>
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
                <div>
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

            {/* 키워드 설정 */}
            <div className="mb-6">
              <h3 className="text-md font-medium text-gray-700 mb-3">키워드 설정</h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">신뢰성 키워드</label>
                  <textarea
                    value={config.keywords.required.join(', ')}
                    onChange={(e) => handleConfigChange('keywords', 'required', e.target.value.split(',').map(k => k.trim()))}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    rows="3"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">의심스러운 키워드</label>
                  <textarea
                    value={config.keywords.suspicious.join(', ')}
                    onChange={(e) => handleConfigChange('keywords', 'suspicious', e.target.value.split(',').map(k => k.trim()))}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    rows="3"
                  />
                </div>
              </div>
            </div>

            {/* 버튼 */}
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowRollbackModal(true)}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
              >
                롤백
              </button>
              <button
                onClick={() => setShowPendingModal(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                변경 요청
              </button>
            </div>
          </div>
        )}

        {activeTab === 'pending' && (
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">대기 중인 변경</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">제출자</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">제출일시</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">상태</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">작업</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {pendingChanges.map((change, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {change.submitted_by}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(change.submitted_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {change.status}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <button
                          onClick={() => handleApproveChange(index)}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          승인
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">변경 이력</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">일시</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">변경 내용</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">사용자</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {history.map((item, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(item.timestamp).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {item.changes}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {item.user}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* 변경 요청 모달 */}
      {showPendingModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-medium text-gray-900 mb-4">변경 요청</h3>
            <p className="text-sm text-gray-500 mb-4">
              현재 설정을 변경 요청으로 제출하시겠습니까?
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowPendingModal(false)}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
              >
                취소
              </button>
              <button
                onClick={handleSubmitPending}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                제출
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 롤백 모달 */}
      {showRollbackModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-medium text-gray-900 mb-4">설정 롤백</h3>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700">롤백할 히스토리 선택</label>
              <select
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                onChange={(e) => setSelectedHistoryId(parseInt(e.target.value))}
              >
                {history.map((item, index) => (
                  <option key={index} value={index}>
                    {new Date(item.timestamp).toLocaleString()} - {item.changes}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowRollbackModal(false)}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
              >
                취소
              </button>
              <button
                onClick={() => handleRollback(selectedHistoryId)}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
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