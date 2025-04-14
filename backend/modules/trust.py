from typing import Dict
import redis
import os
import logging
from redis.retry import Retry
from redis.backoff import ExponentialBackoff
import math

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrustAnalyzer:
    def __init__(self):
        self.redis = None
        self._connect_redis()
        
    def _connect_redis(self):
        """Redis 연결을 시도합니다."""
        try:
            retry = Retry(ExponentialBackoff(), 3)  # 최대 3번 재시도
            self.redis = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=0,
                decode_responses=True,
                retry=retry,
                retry_on_timeout=True
            )
            self.redis.ping()  # 연결 테스트
            logger.info("Redis 연결 성공")
        except redis.ConnectionError as e:
            logger.warning(f"Redis 연결 실패: {str(e)}")
            self.redis = None

    def analyze(self, video_info: Dict) -> Dict:
        """비디오 신뢰도 분석"""
        try:
            # 각 요소별 점수 계산
            channel_score = self._analyze_channel(video_info)
            engagement_score = self._analyze_engagement(video_info)
            activity_score = self._analyze_activity(video_info)
            
            # 가중치 적용
            weights = self.admin_config['weights']
            weighted_scores = {
                'channel': channel_score * weights['channel'],
                'engagement': engagement_score * weights['engagement'],
                'activity': activity_score * weights['activity']
            }
            
            # 총점 계산 (0~1 범위)
            total_score = sum(weighted_scores.values())
            
            logger.info(f"[TRUST] 신뢰도 분석 완료: {total_score}")
            
            return {
                'channel_score': channel_score,
                'engagement_score': engagement_score,
                'activity_score': activity_score,
                'total_score': total_score
            }
        except Exception as e:
            logger.error(f"[TRUST] 신뢰도 분석 중 오류 발생: {str(e)}")
            raise

    def _analyze_channel(self, video_info: Dict) -> float:
        """
        채널의 신뢰도를 분석합니다.
        """
        try:
            # 채널 정보 캐시 확인
            if self.redis:
                channel_key = f"channel:{video_info['channel_title']}"
                cached_score = self.redis.get(channel_key)
                if cached_score:
                    return float(cached_score)
            
            # 채널 분석 로직
            score = 0.5  # 기본 점수 (0~1 범위)
            
            # 구독자 수 기반 점수 (로그 스케일 적용)
            if "subscriber_count" in video_info:
                subscribers = video_info["subscriber_count"]
                if subscribers > 0:
                    # 로그 스케일로 점수 계산 (100만 구독자 = 1.0)
                    subscriber_score = min(1.0, math.log10(subscribers) / 6.0)
                    score = (score + subscriber_score) / 2.0  # 기본 점수와 평균
            
            # 채널 연령 기반 점수
            if "channel_age" in video_info:
                age = video_info["channel_age"]
                if age > 0:
                    # 채널 연령 점수 (1년 = 1.0)
                    age_score = min(1.0, age / 365.0)
                    score = (score + age_score) / 2.0  # 현재 점수와 평균
            
            # 채널 점수 캐시
            if self.redis:
                self.redis.setex(channel_key, 3600, str(score))  # 1시간 캐시
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"채널 분석 중 오류 발생: {str(e)}")
            return 0.5

    def _analyze_engagement(self, video_info: Dict) -> float:
        """
        비디오의 참여도를 분석합니다.
        """
        try:
            view_count = int(video_info["view_count"])
            like_count = int(video_info["like_count"])
            comment_count = int(video_info["comment_count"])
            
            if view_count == 0:
                return 0.3
                
            # 좋아요 비율 (일반적인 좋아요 비율은 1~5%)
            like_ratio = like_count / view_count
            like_score = min(1.0, like_ratio / 0.05)  # 5% = 1.0
            
            # 댓글 비율 (일반적인 댓글 비율은 0.1~0.5%)
            comment_ratio = comment_count / view_count
            comment_score = min(1.0, comment_ratio / 0.005)  # 0.5% = 1.0
            
            # 참여도 점수 계산 (가중치 적용)
            engagement_score = (like_score * 0.6 + comment_score * 0.4)  # 0~1 범위
            
            return max(0.0, min(1.0, engagement_score))
            
        except (ValueError, KeyError) as e:
            logger.error(f"참여도 분석 중 오류 발생: {str(e)}")
            return 0.3

    def _analyze_activity(self, video_info: Dict) -> float:
        """
        채널의 활동성을 분석합니다.
        """
        try:
            if "channel_age" not in video_info or "video_count" not in video_info:
                return 0.3
                
            age = video_info["channel_age"]
            video_count = video_info["video_count"]
            
            if age == 0:
                return 0.3
                
            # 평균 업로드 빈도 (일 단위)
            upload_frequency = video_count / age
            
            # 업로드 빈도 점수 계산
            if upload_frequency >= 1.0:  # 하루 1개 이상
                activity_score = 1.0
            elif upload_frequency >= 0.5:  # 이틀에 1개
                activity_score = 0.8
            elif upload_frequency >= 0.2:  # 주 1개
                activity_score = 0.6
            elif upload_frequency >= 0.1:  # 10일 1개
                activity_score = 0.4
            elif upload_frequency >= 0.05:  # 20일 1개
                activity_score = 0.3
            else:
                activity_score = 0.2
                
            return max(0.0, min(1.0, activity_score))
                
        except Exception as e:
            logger.error(f"활동성 분석 중 오류 발생: {str(e)}")
            return 0.3 