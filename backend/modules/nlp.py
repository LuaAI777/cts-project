from typing import Dict
import re
from collections import Counter

class ContentAnalyzer:
    def __init__(self):
        # 신뢰도 관련 키워드 확장
        self.trust_keywords = {
            "positive": [
                "연구", "실험", "데이터", "증명", "검증", "과학", "학술",
                "전문가", "박사", "교수", "연구원", "학자", "기관",
                "통계", "분석", "조사", "실증", "검증", "실험",
                "논문", "저널", "학회", "학술지", "보고서", "자료"
            ],
            "negative": [
                "음모론", "가짜", "허위", "조작", "사기", "거짓",
                "확실", "무조건", "100%", "절대", "완벽", "최고",
                "충격", "경악", "폭로", "진실", "비밀", "숨겨진"
            ]
        }
        
        # 감정 분석 관련 키워드 확장
        self.emotion_keywords = {
            "positive": [
                "좋다", "추천", "유용", "도움", "정확", "신뢰",
                "객관적", "이성적", "논리적", "분석적", "합리적"
            ],
            "negative": [
                "나쁘다", "주의", "위험", "거짓", "의심", "불신",
                "감정적", "주관적", "편향적", "극단적", "과장"
            ]
        }

    def analyze(self, video_info: Dict) -> Dict:
        """비디오 내용 분석"""
        try:
            # 각 요소별 점수 계산
            title_score = self._analyze_title(video_info.get('title', ''))
            description_score = self._analyze_description(video_info.get('description', ''))
            sentiment_score = self._analyze_sentiment(video_info.get('title', ''), video_info.get('description', ''))
            
            # 가중치 적용
            weights = self.admin_config['weights']
            weighted_scores = {
                'title': title_score * weights['title'],
                'description': description_score * weights['description'],
                'sentiment': sentiment_score * weights['sentiment']
            }
            
            # 총점 계산 (0~1 범위)
            total_score = sum(weighted_scores.values())
            
            logger.info(f"[NLP] 내용 분석 완료: {total_score}")
            
            return {
                'title_score': title_score,
                'description_score': description_score,
                'sentiment_score': sentiment_score,
                'total_score': total_score
            }
        except Exception as e:
            logger.error(f"[NLP] 내용 분석 중 오류 발생: {str(e)}")
            raise

    def _analyze_title(self, title: str) -> float:
        """
        제목을 분석합니다.
        """
        if not title:
            return 30.0
            
        # 제목 길이 점수
        length = len(title)
        if length < 10 or length > 100:
            return 20.0
            
        # 키워드 분석
        keyword_score = self._analyze_keywords(title)
        
        # 감정적 표현 체크
        emotional_count = sum(title.count(keyword) for keyword in self.emotion_keywords["negative"])
        if emotional_count > 0:
            return max(20.0, keyword_score * 0.5)  # 감정적 표현이 있으면 점수 50% 감소
            
        return max(30.0, keyword_score)

    def _analyze_description(self, description: str) -> float:
        """
        설명을 분석합니다.
        """
        if not description:
            return 30.0
            
        # 설명 길이 점수
        length = len(description)
        if length < 100 or length > 5000:
            return 20.0
            
        # 광고/멤버십 링크 체크
        if "광고문의" in description or "멤버십" in description or "business@" in description:
            return 30.0
            
        # 키워드 분석
        keyword_score = self._analyze_keywords(description)
        
        # 전문성 지표 체크
        professional_count = sum(description.count(keyword) for keyword in self.trust_keywords["positive"])
        if professional_count > 0:
            return min(80.0, 50.0 + (professional_count * 5.0))  # 전문성 점수 상한선 80점
            
        return max(30.0, keyword_score)

    def _analyze_sentiment(self, title: str, description: str) -> float:
        """
        감정을 분석합니다.
        """
        text = f"{title} {description}"
        
        # 긍정/부정 키워드 카운트
        positive_count = sum(text.count(keyword) for keyword in self.trust_keywords["positive"])
        negative_count = sum(text.count(keyword) for keyword in self.trust_keywords["negative"])
        
        # 감정 키워드 카운트
        positive_emotion = sum(text.count(keyword) for keyword in self.emotion_keywords["positive"])
        negative_emotion = sum(text.count(keyword) for keyword in self.emotion_keywords["negative"])
        
        # 신뢰도 점수 계산 (0~1)
        total_trust = positive_count + negative_count
        trust_score = 0.5  # 기본 점수
        if total_trust > 0:
            trust_score = positive_count / total_trust
            
        # 감정 점수 계산 (0~1)
        total_emotion = positive_emotion + negative_emotion
        emotion_score = 0.5  # 기본 점수
        if total_emotion > 0:
            emotion_score = positive_emotion / total_emotion
            
        # 최종 점수 계산 (가중치 적용)
        final_score = (trust_score * 0.7 + emotion_score * 0.3) * 100  # 0~100 범위로 변환
        
        return max(0.0, min(100.0, final_score))

    def _analyze_keywords(self, text: str) -> float:
        """
        텍스트의 키워드를 분석합니다.
        """
        if not text:
            return 50.0
            
        # 키워드 카운트
        positive_count = sum(text.count(keyword) for keyword in self.trust_keywords["positive"])
        negative_count = sum(text.count(keyword) for keyword in self.trust_keywords["negative"])
        
        # 감정 키워드 카운트
        positive_emotion = sum(text.count(keyword) for keyword in self.emotion_keywords["positive"])
        negative_emotion = sum(text.count(keyword) for keyword in self.emotion_keywords["negative"])
        
        # 신뢰도 점수 계산 (0~1)
        total_trust = positive_count + negative_count
        trust_score = 0.5  # 기본 점수
        if total_trust > 0:
            trust_score = positive_count / total_trust
            
        # 감정 점수 계산 (0~1)
        total_emotion = positive_emotion + negative_emotion
        emotion_score = 0.5  # 기본 점수
        if total_emotion > 0:
            emotion_score = positive_emotion / total_emotion
            
        # 최종 점수 계산 (가중치 적용)
        final_score = (trust_score * 0.6 + emotion_score * 0.4) * 100  # 0~100 범위로 변환
        
        return max(0.0, min(100.0, final_score)) 