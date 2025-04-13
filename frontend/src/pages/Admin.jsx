import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import styles from '../styles/Admin.module.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const Admin = () => {
  const navigate = useNavigate();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [config, setConfig] = useState({
    weights: {
      views: 0.3,
      likes: 0.3,
      subscribers: 0.4
    },
    thresholds: {
      views: { low: 1000, high: 10000 },
      likes: { low: 100, high: 1000 },
      subscribers: { low: 1000, high: 10000 }
    },
    keywords: []
  });
  const [history, setHistory] = useState([]);
  const [pendingChanges, setPendingChanges] = useState([]);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }

        // 토큰 유효성 검사
        await axios.get(`${API_BASE_URL}/api/admin/config`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setIsAuthenticated(true);
      } catch (error) {
        console.error('인증 실패:', error);
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
      const response = await axios.get(`${API_BASE_URL}/api/admin/config`, {
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
      const response = await axios.get(`${API_BASE_URL}/api/admin/history`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setHistory(response.data);
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
      
      await axios.post(`${API_BASE_URL}/api/admin/config`, newConfig, {
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
      await axios.post(`${API_BASE_URL}/api/admin/config/pending`, config, {
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
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_BASE_URL}/api/admin/config/approve`,
        { change_id: changeId },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      if (response.status === 200) {
        // 변경 이력과 대기 중인 변경 목록 새로고침
        await Promise.all([
          fetchPendingChanges(),
          fetchConfig(),
          fetchHistory()
        ]);
      }
    } catch (error) {
      console.error('변경 승인 중 오류 발생:', error);
    }
  };

  const handleRollback = async (historyId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_BASE_URL}/api/admin/config/rollback`,
        { history_id: historyId },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
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
      const response = await axios.get(`${API_BASE_URL}/api/admin/config/pending`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPendingChanges(response.data);
    } catch (error) {
      console.error('대기 중인 변경 조회 실패:', error);
    }
  };

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.spinner}></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>관리자 페이지</h1>
      </header>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>현재 설정</h2>
        <form className={styles.form} onSubmit={handleSubmitPending}>
          <div className={styles.formGroup}>
            <h3>가중치 설정</h3>
            <div className={styles.formGroup}>
              <label className={styles.label}>조회수 가중치:</label>
              <input
                className={styles.input}
                type="number"
                step="0.1"
                value={config.weights.views}
                onChange={(e) => handleConfigChange('weights', 'views', e.target.value)}
              />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>좋아요 가중치:</label>
              <input
                className={styles.input}
                type="number"
                step="0.1"
                value={config.weights.likes}
                onChange={(e) => handleConfigChange('weights', 'likes', e.target.value)}
              />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>구독자 수 가중치:</label>
              <input
                className={styles.input}
                type="number"
                step="0.1"
                value={config.weights.subscribers}
                onChange={(e) => handleConfigChange('weights', 'subscribers', e.target.value)}
              />
            </div>
          </div>

          <div className={styles.formGroup}>
            <h3>임계값 설정</h3>
            <div className={styles.formGroup}>
              <label className={styles.label}>조회수 하한:</label>
              <input
                className={styles.input}
                type="number"
                value={config.thresholds.views.low}
                onChange={(e) => handleConfigChange('thresholds.views', 'low', e.target.value)}
              />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>조회수 상한:</label>
              <input
                className={styles.input}
                type="number"
                value={config.thresholds.views.high}
                onChange={(e) => handleConfigChange('thresholds.views', 'high', e.target.value)}
              />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>좋아요 하한:</label>
              <input
                className={styles.input}
                type="number"
                value={config.thresholds.likes.low}
                onChange={(e) => handleConfigChange('thresholds.likes', 'low', e.target.value)}
              />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>좋아요 상한:</label>
              <input
                className={styles.input}
                type="number"
                value={config.thresholds.likes.high}
                onChange={(e) => handleConfigChange('thresholds.likes', 'high', e.target.value)}
              />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>구독자 수 하한:</label>
              <input
                className={styles.input}
                type="number"
                value={config.thresholds.subscribers.low}
                onChange={(e) => handleConfigChange('thresholds.subscribers', 'low', e.target.value)}
              />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.label}>구독자 수 상한:</label>
              <input
                className={styles.input}
                type="number"
                value={config.thresholds.subscribers.high}
                onChange={(e) => handleConfigChange('thresholds.subscribers', 'high', e.target.value)}
              />
            </div>
          </div>

          <button type="submit" className={styles.button}>
            설정 저장
          </button>
        </form>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>대기 중인 변경사항</h2>
        <ul className={styles.list}>
          {pendingChanges.map((change) => (
            <li key={change.id} className={styles.listItem}>
              <div>
                <p>변경 시각: {new Date(change.timestamp).toLocaleString()}</p>
                <p>요청자: {change.user}</p>
                <p>변경 내용: {JSON.stringify(change.config)}</p>
              </div>
              <button
                className={styles.button}
                onClick={() => handleApproveChange(change.id)}
              >
                승인
              </button>
            </li>
          ))}
        </ul>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>변경 이력</h2>
        <ul className={styles.list}>
          {history.map((change) => (
            <li key={change.id} className={styles.listItem}>
              <div>
                <p>변경 시각: {new Date(change.timestamp).toLocaleString()}</p>
                <p>요청자: {change.user}</p>
                <p>변경 내용: {JSON.stringify(change.config)}</p>
              </div>
              <button
                className={styles.button}
                onClick={() => handleRollback(change.id)}
              >
                롤백
              </button>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
};

export default Admin; 