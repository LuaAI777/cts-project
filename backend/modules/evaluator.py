from typing import Dict, List, Tuple
from datetime import datetime
from .trust import TrustAnalyzer
from .nlp import ContentAnalyzer
from .scoring import ScoreCalculator
import logging
import os
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentEvaluator:
    def __init__(self):
        self.trust_analyzer = TrustAnalyzer()
        self.content_analyzer = ContentAnalyzer()
        self.score_calculator = ScoreCalculator()

    def evaluate(self, video_info: Dict) -> Dict:
        """
        비디오의 신뢰도를 종합적으로 평가합니다.
        
        Args:
            video_info (Dict): YouTube 비디오 정보
            
        Returns:
            Dict: 평가 결과
        """
        try:
            # 출처 및 채널 분석
            trust_analysis = self.trust_analyzer.analyze(video_info)
            trust_score = trust_analysis["total_score"]
            
            # 내용 분석
            content_analysis = self.content_analyzer.analyze(video_info)
            content_score = content_analysis["total_score"]
            
            # 종합 점수 계산
            final_score = self.score_calculator.calculate_score(
                trust_score=trust_score,
                content_score=content_score
            )
            
            return {
                "video_info": video_info,
                "trust_analysis": trust_analysis,
                "content_analysis": content_analysis,
                "final_score": final_score,
                "grade": self.score_calculator.get_grade(final_score),
                "grade_description": self.score_calculator.get_grade_description(
                    self.score_calculator.get_grade(final_score)
                )
            }
        except Exception as e:
            return {"error": f"평가 중 오류 발생: {str(e)}"}

class Evaluator:
    def __init__(self, admin_config: Dict = None):
        """
        평가기 초기화
        
        Args:
            admin_config (Dict): 관리자 설정
        """
        self.admin_config = admin_config or {
            "weights": {
                "source": 0.7,
                "content": 0.3
            },
            "thresholds": {
                "subscribers": {
                    "high": 1000000,
                    "medium": 100000,
                    "low": 10000
                },
                "activity": {
                    "high": 365,
                    "medium": 180,
                    "low": 90
                }
            },
            "keywords": {
                "required": ["연구", "데이터", "출처", "근거", "확인", "검증", "인용", "참고", "인터뷰", "전문가"],
                "suspicious": ["확실", "무조건", "100%", "절대", "완벽", "최고", "최초", "최강", "최고급", "최상급"],
                "clickbait": ["충격", "경악", "폭로", "진실", "비밀", "숨겨진", "알려지지 않은", "깜짝", "놀라운"],
                "emotional": ["놀랍다", "충격적", "경악", "믿을 수 없다", "믿기지 않는다", "믿기 어렵다"],
                "professional": ["연구", "데이터", "분석", "조사", "통계", "전문가", "학자", "교수", "박사"]
            }
        }
        
        logger.info("평가기가 초기화되었습니다.")
        logger.debug(f"관리자 설정: {self.admin_config}")

    def evaluate_source_trust(self, video_data: Dict) -> Dict:
        """출처/채널 신뢰도 평가"""
        try:
            if not video_data or not isinstance(video_data, dict):
                raise ValueError("[TRUST] 비디오 데이터가 유효하지 않습니다.")
                
            required_fields = ['channel_id', 'subscriber_count', 'channel_age', 'likes', 'comments', 'views']
            for field in required_fields:
                if field not in video_data:
                    raise ValueError(f"[TRUST] 필수 필드가 누락되었습니다: {field}")
            
            logger.info(f"[TRUST] 출처 신뢰도 평가 시작: {video_data['channel_id']}")
            
            # 각 점수 계산 (0~100점)
            subscriber_score = self._calculate_subscriber_score(video_data['subscriber_count'])
            activity_score = self._calculate_activity_score(video_data['channel_age'])
            engagement_score = self._calculate_engagement_score(
                video_data['likes'],
                video_data['comments'],
                video_data['views']
            )
            
            # 가중치 적용
            source_weights = {
                'subscriber': 0.3,
                'activity': 0.2,
                'engagement': 0.5
            }
            
            # 가중 평균 계산
            total_score = (
                subscriber_score * source_weights['subscriber'] +
                activity_score * source_weights['activity'] +
                engagement_score * source_weights['engagement']
            )
            
            logger.info(f"[TRUST] 출처 신뢰도 평가 완료: {total_score}")
            
            return {
                'subscriber_score': subscriber_score,
                'activity_score': activity_score,
                'engagement_score': engagement_score,
                'total_score': total_score
            }
        except ValueError as e:
            logger.error(f"[TRUST] 입력값 검증 오류: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[TRUST] 출처 신뢰도 평가 중 오류 발생: {str(e)}")
            raise

    def evaluate_content_trust(self, video_data: Dict) -> Dict:
        """내용 신뢰도 평가"""
        try:
            if not video_data or not isinstance(video_data, dict):
                raise ValueError("[NLP] 비디오 데이터가 유효하지 않습니다.")
                
            required_fields = ['video_id', 'title', 'description']
            for field in required_fields:
                if field not in video_data:
                    raise ValueError(f"[NLP] 필수 필드가 누락되었습니다: {field}")
            
            logger.info(f"[NLP] 내용 신뢰도 평가 시작: {video_data['video_id']}")
            
            # 각 점수 계산 (0~100점)
            title_score = self._analyze_title(video_data['title'])
            description_score = self._analyze_description(video_data['description'])
            sentiment_score = self._analyze_sentiment(video_data['title'], video_data['description'])
            
            # 가중치 적용
            content_weights = {
                'title': 0.2,
                'description': 0.5,
                'sentiment': 0.3
            }
            
            # 가중 평균 계산
            total_score = (
                title_score * content_weights['title'] +
                description_score * content_weights['description'] +
                sentiment_score * content_weights['sentiment']
            )
            
            logger.info(f"[NLP] 내용 신뢰도 평가 완료: {total_score}")
            
            return {
                'title_score': title_score,
                'description_score': description_score,
                'sentiment_score': sentiment_score,
                'total_score': total_score
            }
        except ValueError as e:
            logger.error(f"[NLP] 입력값 검증 오류: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[NLP] 내용 신뢰도 평가 중 오류 발생: {str(e)}")
            raise

    def calculate_final_score(self, source_trust: Dict, content_trust: Dict) -> Dict:
        """종합 점수 계산"""
        try:
            if not source_trust or not content_trust:
                raise ValueError("[SCORING] 출처 신뢰도와 내용 신뢰도 데이터가 필요합니다.")
                
            if 'total_score' not in source_trust or 'total_score' not in content_trust:
                raise ValueError("[SCORING] 신뢰도 데이터에 총점이 포함되어 있지 않습니다.")
            
            logger.info("[SCORING] 종합 점수 계산 시작")
            
            # 가중치 적용
            weights = self.admin_config['weights']
            final_score = (
                source_trust['total_score'] * weights['source'] +
                content_trust['total_score'] * weights['content']
            )
            
            grade = self._calculate_grade(final_score)
            
            logger.info(f"[SCORING] 종합 점수 계산 완료: {final_score} (등급: {grade})")
            
            return {
                'source_trust': source_trust['total_score'],
                'content_trust': content_trust['total_score'],
                'final_score': final_score,
                'grade': grade
            }
        except ValueError as e:
            logger.error(f"[SCORING] 입력값 검증 오류: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[SCORING] 종합 점수 계산 중 오류 발생: {str(e)}")
            raise

    def _calculate_subscriber_score(self, subscriber_count: int) -> float:
        """구독자 수에 따른 점수 계산 (100점 만점)"""
        thresholds = self.admin_config['thresholds']['subscribers']
        
        if subscriber_count >= thresholds['high']:
            return 100.0
        elif subscriber_count >= thresholds['medium']:
            return 70.0
        elif subscriber_count >= thresholds['low']:
            return 40.0
        else:
            return 20.0

    def _calculate_activity_score(self, channel_age: int) -> float:
        """채널 활동 기간에 따른 점수 계산 (100점 만점)"""
        thresholds = self.admin_config['thresholds']['activity']
        
        if channel_age >= thresholds['high']:
            return 100.0
        elif channel_age >= thresholds['medium']:
            return 70.0
        elif channel_age >= thresholds['low']:
            return 40.0
        else:
            return 20.0

    def _calculate_engagement_score(self, likes: int, comments: int, views: int) -> float:
        """참여도 점수 계산 (100점 만점)"""
        if views == 0:
            return 0.0
            
        engagement_rate = ((likes + comments) / views) * 100
        if engagement_rate >= 5.0:
            return 100.0
        elif engagement_rate >= 2.0:
            return 70.0
        elif engagement_rate >= 1.0:
            return 40.0
        else:
            return 20.0

    def _analyze_title(self, title: str) -> float:
        """제목 분석 (100점 만점)"""
        score = 100.0
        
        # 클릭베이트 단어 감지 (최대 30점 감점)
        clickbait_count = sum(1 for word in self.admin_config['keywords']['clickbait'] if word in title)
        clickbait_penalty = min(30.0, clickbait_count * 20.0)
        score = max(0.0, score - clickbait_penalty)
        
        # 감정적 단어 감지 (최대 20점 감점)
        emotional_count = sum(1 for word in self.admin_config['keywords']['emotional'] if word in title)
        emotional_penalty = min(20.0, emotional_count * 15.0)
        score = max(0.0, score - emotional_penalty)
        
        # 전문성 단어 감지 (최대 20점)
        professional_count = sum(1 for word in self.admin_config['keywords']['professional'] if word in title)
        professional_bonus = min(20.0, professional_count * 10.0)
        score = min(100.0, score + professional_bonus)
        
        return max(0.0, min(100.0, score))

    def _analyze_description(self, description: str) -> float:
        """설명 분석 (100점 만점)"""
        score = 100.0
        
        # 필수 단어 확인 (최대 30점)
        required_count = sum(1 for word in self.admin_config['keywords']['required'] if word in description)
        required_bonus = min(30.0, required_count * 10.0)
        score = min(100.0, score + required_bonus)
        
        # 의심스러운 단어 감지 (최대 30점 감점)
        suspicious_count = sum(1 for word in self.admin_config['keywords']['suspicious'] if word in description)
        suspicious_penalty = min(30.0, suspicious_count * 15.0)
        score = max(0.0, score - suspicious_penalty)
        
        # 전문성 단어 감지 (최대 20점)
        professional_count = sum(1 for word in self.admin_config['keywords']['professional'] if word in description)
        professional_bonus = min(20.0, professional_count * 5.0)
        score = min(100.0, score + professional_bonus)
        
        return max(0.0, min(100.0, score))

    def _analyze_sentiment(self, title: str, description: str) -> float:
        """감정 분석 (100점 만점)"""
        score = 100.0
        text = f"{title} {description}"
        
        # 감정적 단어 감지 (최대 30점 감점)
        emotional_count = sum(1 for word in self.admin_config['keywords']['emotional'] if word in text)
        emotional_penalty = min(30.0, emotional_count * 10.0)
        score = max(0.0, score - emotional_penalty)
        
        # 의심스러운 단어 감지 (최대 30점 감점)
        suspicious_count = sum(1 for word in self.admin_config['keywords']['suspicious'] if word in text)
        suspicious_penalty = min(30.0, suspicious_count * 15.0)
        score = max(0.0, score - suspicious_penalty)
        
        return max(0.0, min(100.0, score))

    def _calculate_grade(self, score: float) -> str:
        """등급 계산"""
        try:
            if score >= 0.8:
                return "A"
            elif score >= 0.6:
                return "B"
            elif score >= 0.4:
                return "C"
            elif score >= 0.2:
                return "D"
            else:
                return "F"
        except Exception as e:
            logger.error(f"[SCORING] 등급 계산 중 오류 발생: {str(e)}")
            raise 