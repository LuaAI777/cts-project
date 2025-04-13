from typing import Dict, List, Tuple
from datetime import datetime
from .trust import TrustAnalyzer
from .nlp import ContentAnalyzer
from .scoring import ScoreCalculator

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
    def __init__(self):
        self.source_weights = {
            'subscriber': 0.3,
            'activity': 0.2,
            'engagement': 0.5
        }
        
        self.content_weights = {
            'title': 0.3,
            'description': 0.4,
            'sentiment': 0.3
        }
        
        self.final_weights = {
            'source': 0.6,
            'content': 0.4
        }

    def evaluate_source_trust(self, video_data: Dict) -> Dict:
        """출처/채널 신뢰도 평가"""
        subscriber_score = self._calculate_subscriber_score(video_data['subscriber_count'])
        activity_score = self._calculate_activity_score(video_data['channel_age'])
        engagement_score = self._calculate_engagement_score(
            video_data['likes'],
            video_data['comments'],
            video_data['views']
        )
        
        return {
            'subscriber_score': subscriber_score,
            'activity_score': activity_score,
            'engagement_score': engagement_score,
            'total_score': self._calculate_weighted_score([
                (subscriber_score, self.source_weights['subscriber']),
                (activity_score, self.source_weights['activity']),
                (engagement_score, self.source_weights['engagement'])
            ])
        }

    def evaluate_content_trust(self, video_data: Dict) -> Dict:
        """내용 신뢰도 평가"""
        title_score = self._analyze_title(video_data['title'])
        description_score = self._analyze_description(video_data['description'])
        sentiment_score = self._analyze_sentiment(video_data['title'], video_data['description'])
        
        return {
            'title_score': title_score,
            'description_score': description_score,
            'sentiment_score': sentiment_score,
            'total_score': self._calculate_weighted_score([
                (title_score, self.content_weights['title']),
                (description_score, self.content_weights['description']),
                (sentiment_score, self.content_weights['sentiment'])
            ])
        }

    def calculate_final_score(self, source_trust: Dict, content_trust: Dict) -> Dict:
        """종합 점수 계산"""
        final_score = self._calculate_weighted_score([
            (source_trust['total_score'], self.final_weights['source']),
            (content_trust['total_score'], self.final_weights['content'])
        ])
        
        return {
            'source_trust': source_trust['total_score'],
            'content_trust': content_trust['total_score'],
            'final_score': final_score,
            'grade': self._calculate_grade(final_score)
        }

    def _calculate_subscriber_score(self, subscriber_count: int) -> float:
        """구독자 수 점수 계산"""
        thresholds = {
            1000000: 1.0,
            100000: 0.8,
            10000: 0.6,
            1000: 0.4,
            0: 0.2
        }
        
        for threshold, score in sorted(thresholds.items(), reverse=True):
            if subscriber_count >= threshold:
                return score
        return 0.0

    def _calculate_activity_score(self, channel_age: int) -> float:
        """채널 활동 기간 점수 계산"""
        thresholds = {
            365 * 5: 1.0,  # 5년 이상
            365 * 3: 0.8,  # 3년 이상
            365: 0.6,      # 1년 이상
            0: 0.4
        }
        
        for threshold, score in sorted(thresholds.items(), reverse=True):
            if channel_age >= threshold:
                return score
        return 0.0

    def _calculate_engagement_score(self, likes: int, comments: int, views: int) -> float:
        """참여도 점수 계산"""
        if views == 0:
            return 0.0
            
        like_ratio = likes / views
        comment_ratio = comments / views
        
        if like_ratio >= 0.1 and comment_ratio >= 0.01:
            return 1.0
        elif like_ratio >= 0.05 and comment_ratio >= 0.005:
            return 0.8
        elif like_ratio >= 0.02 and comment_ratio >= 0.002:
            return 0.6
        else:
            return 0.4

    def _analyze_title(self, title: str) -> float:
        """제목 분석"""
        length = len(title)
        if 10 <= length <= 100:
            return 1.0
        elif 5 <= length <= 150:
            return 0.8
        else:
            return 0.6

    def _analyze_description(self, description: str) -> float:
        """설명 분석"""
        length = len(description)
        if 100 <= length <= 5000:
            return 1.0
        elif 50 <= length <= 10000:
            return 0.8
        else:
            return 0.6

    def _analyze_sentiment(self, title: str, description: str) -> float:
        """감정 분석"""
        # 긍정적인 단어 목록
        positive_words = ['연구', '데이터', '출처', '검증', '분석', '실험']
        # 부정적인 단어 목록
        negative_words = ['확실', '무조건', '100%', '절대', '완벽']
        
        text = f"{title} {description}"
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return 1.0
        elif positive_count == negative_count:
            return 0.5
        else:
            return 0.0

    def _calculate_weighted_score(self, scores: List[Tuple[float, float]]) -> float:
        """가중 평균 점수 계산"""
        total_weight = sum(weight for _, weight in scores)
        if total_weight == 0:
            return 0.0
        return sum(score * weight for score, weight in scores) / total_weight

    def _calculate_grade(self, score: float) -> str:
        """등급 계산"""
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