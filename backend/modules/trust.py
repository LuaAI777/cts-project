from typing import Dict
import redis
import os

class TrustAnalyzer:
    def __init__(self):
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0
        )

    def analyze(self, video_info: Dict) -> Dict:
        """
        비디오의 출처와 채널을 분석합니다.
        
        Args:
            video_info (Dict): YouTube 비디오 정보
            
        Returns:
            Dict: 신뢰도 분석 결과
        """
        channel_score = self._analyze_channel(video_info)
        engagement_score = self._analyze_engagement(video_info)
        
        return {
            "channel_score": channel_score,
            "engagement_score": engagement_score,
            "total_score": (channel_score + engagement_score) / 2
        }

    def _analyze_channel(self, video_info: Dict) -> float:
        """
        채널의 신뢰도를 분석합니다.
        """
        # 채널 정보 캐시 확인
        channel_key = f"channel:{video_info['channel_title']}"
        cached_score = self.redis.get(channel_key)
        
        if cached_score:
            return float(cached_score)
        
        # 채널 분석 로직 (예시)
        score = 0.5  # 기본 점수
        
        # 구독자 수 기반 점수
        if "subscriber_count" in video_info:
            score += min(video_info["subscriber_count"] / 1000000, 0.3)
        
        # 채널 점수 캐시
        self.redis.setex(channel_key, 3600, str(score))  # 1시간 캐시
        
        return score

    def _analyze_engagement(self, video_info: Dict) -> float:
        """
        비디오의 참여도를 분석합니다.
        """
        try:
            view_count = int(video_info["view_count"])
            like_count = int(video_info["like_count"])
            comment_count = int(video_info["comment_count"])
            
            # 좋아요 비율
            like_ratio = like_count / view_count if view_count > 0 else 0
            
            # 댓글 비율
            comment_ratio = comment_count / view_count if view_count > 0 else 0
            
            # 참여도 점수 계산
            engagement_score = (like_ratio * 0.6 + comment_ratio * 0.4) * 100
            
            return min(engagement_score, 1.0)  # 최대 1.0
            
        except (ValueError, KeyError):
            return 0.5  # 기본 점수 