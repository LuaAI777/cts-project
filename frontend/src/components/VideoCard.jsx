import React from 'react';
import '../styles/VideoCard.css';

const VideoCard = ({ video }) => {
  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="video-card">
      <div className="thumbnail-container">
        <img
          src={video.thumbnail}
          alt={video.title}
          className="thumbnail"
        />
      </div>
      <div className="video-info">
        <h3 className="video-title">{video.title}</h3>
        <p className="channel-name">{video.channelTitle}</p>
        <div className="video-stats">
          <span className="stat">
            👁️ {formatNumber(video.viewCount)} 조회수
          </span>
          <span className="stat">
            👍 {formatNumber(video.likeCount)} 좋아요
          </span>
          <span className="stat">
            💬 {formatNumber(video.commentCount)} 댓글
          </span>
        </div>
        <p className="publish-date">
          📅 {formatDate(video.publishedAt)}
        </p>
      </div>
    </div>
  );
};

export default VideoCard; 