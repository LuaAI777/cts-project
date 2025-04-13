from typing import Dict
import re
from collections import Counter

class ContentAnalyzer:
    def __init__(self):
        # 신뢰도 관련 키워드 (예시)
        self.trust_keywords = {
            "positive": ["연구", "실험", "데이터", "증명", "검증", "과학", "학술"],
            "negative": ["음모론", "가짜", "허위", "조작", "사기", "거짓"]
        }
        
        # 감정 분석 관련 키워드 (예시)
        self.emotion_keywords = {
            "positive": ["좋다", "추천", "유용", "도움", "정확", "신뢰"],
            "negative": ["나쁘다", "주의", "위험", "거짓", "의심", "불신"]
        }

    def analyze(self, video_info: Dict) -> Dict:
        """
        비디오의 내용을 분석합니다.
        
        Args:
            video_info (Dict): YouTube 비디오 정보
            
        Returns:
            Dict: 내용 분석 결과
        """
        title_score = self._analyze_title(video_info["title"])
        description_score = self._analyze_description(video_info["description"])
        
        return {
            "title_score": title_score,
            "description_score": description_score,
            "total_score": (title_score + description_score) / 2
        }

    def _analyze_title(self, title: str) -> float:
        """
        제목을 분석합니다.
        """
        # 제목 길이 점수
        length_score = min(len(title) / 50, 1.0)
        
        # 키워드 분석
        keyword_score = self._analyze_keywords(title)
        
        return (length_score * 0.3 + keyword_score * 0.7)

    def _analyze_description(self, description: str) -> float:
        """
        설명을 분석합니다.
        """
        if not description:
            return 0.5
            
        # 설명 길이 점수
        length_score = min(len(description) / 500, 1.0)
        
        # 키워드 분석
        keyword_score = self._analyze_keywords(description)
        
        # 링크 포함 여부
        has_links = bool(re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', description))
        link_score = 0.2 if has_links else 0.0
        
        return (length_score * 0.3 + keyword_score * 0.5 + link_score)

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