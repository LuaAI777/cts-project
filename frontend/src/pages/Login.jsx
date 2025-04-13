import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Login = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/token', {
        username: formData.username,
        password: formData.password
      });
      
      // 토큰 저장
      localStorage.setItem('token', response.data.access_token);
      
      // 관리자 페이지로 이동
      navigate('/admin');
    } catch (error) {
      setError(error.response?.data?.detail || '로그인에 실패했습니다. 아이디와 비밀번호를 확인하세요.');
    }
  };

  return (
    <div className="container">
      <div className="card max-w-md mx-auto">
        <h2 className="text-center text-2xl font-bold mb-8 text-gray-900">
          관리자 로그인
        </h2>
        <form onSubmit={handleSubmit}>
          {error && (
            <div className="alert alert-error">
              {error}
            </div>
          )}
          <div className="mb-4">
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">아이디</label>
            <input
              id="username"
              name="username"
              type="text"
              required
              className="input"
              placeholder="아이디를 입력하세요"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
            />
          </div>
          <div className="mb-4">
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">비밀번호</label>
            <input
              id="password"
              name="password"
              type="password"
              required
              className="input"
              placeholder="비밀번호를 입력하세요"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            />
          </div>
          <button type="submit" className="btn btn-primary w-full mt-4">
            로그인
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login; 