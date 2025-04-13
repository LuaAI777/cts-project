from typing import Dict, Tuple

class ScoreCalculator:
    def __init__(self):
        # 가중치 설정
        self.weights = {
            "trust": 0.6,  # 출처/채널 신뢰도 가중치
            "content": 0.4  # 내용 신뢰도 가중치
        }
        
        # 등급 기준
        self.grade_thresholds = {
            "A": 0.8,  # 매우 신뢰할 수 있음
            "B": 0.6,  # 신뢰할 수 있음
            "C": 0.4,  # 보통
            "D": 0.2,  # 주의 필요
            "F": 0.0   # 신뢰할 수 없음
        }

    def calculate_score(self, trust_score: float, content_score: float) -> float:
        """
        종합 점수를 계산합니다.
        
        Args:
            trust_score (float): 출처/채널 신뢰도 점수
            content_score (float): 내용 신뢰도 점수
            
        Returns:
            float: 종합 점수 (0~1)
        """
        return (
            trust_score * self.weights["trust"] +
            content_score * self.weights["content"]
        )

    def get_grade(self, score: float) -> str:
        """
        점수에 따른 등급을 반환합니다.
        
        Args:
            score (float): 종합 점수
            
        Returns:
            str: 등급 (A, B, C, D, F)
        """
        for grade, threshold in self.grade_thresholds.items():
            if score >= threshold:
                return grade
        return "F"

    def get_grade_description(self, grade: str) -> str:
        """
        등급에 대한 설명을 반환합니다.
        
        Args:
            grade (str): 등급
            
        Returns:
            str: 등급 설명
        """
        descriptions = {
            "A": "매우 신뢰할 수 있는 콘텐츠입니다.",
            "B": "신뢰할 수 있는 콘텐츠입니다.",
            "C": "일반적인 신뢰도를 가진 콘텐츠입니다.",
            "D": "신중하게 접근해야 하는 콘텐츠입니다.",
            "F": "신뢰할 수 없는 콘텐츠입니다."
        }
        return descriptions.get(grade, "알 수 없는 등급입니다.") 