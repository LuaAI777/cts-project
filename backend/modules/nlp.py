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
        """
        비디오의 내용을 분석합니다.
        """
        title_score = self._analyze_title(video_info["title"])
        description_score = self._analyze_description(video_info["description"])
        sentiment_score = self._analyze_sentiment(video_info["title"], video_info["description"])
        
        # 가중치 적용
        weights = {
            "title": 0.3,
            "description": 0.5,
            "sentiment": 0.2
        }
        
        total_score = (
            title_score * weights["title"] +
            description_score * weights["description"] +
            sentiment_score * weights["sentiment"]
        )
        
        return {
            "title_score": title_score,
            "description_score": description_score,
            "sentiment_score": sentiment_score,
            "total_score": total_score
        }

    def _analyze_title(self, title: str) -> float:
        """
        제목을 분석합니다.
        """
        if not title:
            return 0.3
            
        # 제목 길이 점수
        length = len(title)
        if length < 10 or length > 100:
            return 0.2
            
        # 키워드 분석
        keyword_score = self._analyze_keywords(title)
        
        # 감정적 표현 체크
        emotional_count = sum(title.count(keyword) for keyword in self.emotion_keywords["negative"])
        if emotional_count > 0:
            return 0.2
            
        return max(0.3, keyword_score)

    def _analyze_description(self, description: str) -> float:
        """
        설명을 분석합니다.
        """
        if not description:
            return 0.3
            
        # 설명 길이 점수
        length = len(description)
        if length < 100 or length > 5000:
            return 0.2
            
        # 키워드 분석
        keyword_score = self._analyze_keywords(description)
        
        # 전문성 지표 체크
        professional_count = sum(description.count(keyword) for keyword in self.trust_keywords["positive"])
        if professional_count > 0:
            return min(1.0, 0.6 + (professional_count * 0.1))
            
        return max(0.3, keyword_score)

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
        
        # 점수 계산
        trust_score = (positive_count - negative_count) / (positive_count + negative_count + 1)
        emotion_score = (positive_emotion - negative_emotion) / (positive_emotion + negative_emotion + 1)
        
        return (trust_score * 0.7 + emotion_score * 0.3 + 1) / 2  # 0~1 사이로 정규화

    def _analyze_keywords(self, text: str) -> float:
        """
        텍스트의 키워드를 분석합니다.
        """
        if not text:
            return 0.5
            
        # 키워드 카운트
        positive_count = sum(text.count(keyword) for keyword in self.trust_keywords["positive"])
        negative_count = sum(text.count(keyword) for keyword in self.trust_keywords["negative"])
        
        # 감정 키워드 카운트
        positive_emotion = sum(text.count(keyword) for keyword in self.emotion_keywords["positive"])
        negative_emotion = sum(text.count(keyword) for keyword in self.emotion_keywords["negative"])
        
        # 점수 계산
        trust_score = (positive_count - negative_count) / (positive_count + negative_count + 1)
        emotion_score = (positive_emotion - negative_emotion) / (positive_emotion + negative_emotion + 1)
        
        return (trust_score * 0.6 + emotion_score * 0.4 + 1) / 2  # 0~1 사이로 정규화 