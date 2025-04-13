from typing import Dict, Tuple

class ScoreCalculator:
    def __init__(self):
        # 가중치 설정 - 내용 신뢰도에 더 높은 가중치 부여
        self.weights = {
            "trust": 0.4,  # 출처/채널 신뢰도 가중치 감소
            "content": 0.6  # 내용 신뢰도 가중치 증가
        }
        
        # 등급 기준 - 더 엄격하게 조정
        self.grade_thresholds = {
            "A": 0.9,  # 매우 신뢰할 수 있음 (상향)
            "B": 0.7,  # 신뢰할 수 있음 (상향)
            "C": 0.5,  # 보통 (상향)
            "D": 0.3,  # 주의 필요 (상향)
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
        # 내용 신뢰도 점수가 낮으면 전체 점수도 크게 감소
        if content_score < 0.3:
            return content_score * 0.7  # 내용 신뢰도가 낮으면 70%만 반영
        
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
            "A": "매우 신뢰할 수 있는 콘텐츠입니다. 전문적인 내용과 신뢰할 수 있는 출처를 포함하고 있습니다.",
            "B": "신뢰할 수 있는 콘텐츠입니다. 대체로 객관적이고 검증된 정보를 포함하고 있습니다.",
            "C": "일반적인 신뢰도를 가진 콘텐츠입니다. 추가적인 검증이 필요할 수 있습니다.",
            "D": "신중하게 접근해야 하는 콘텐츠입니다. 감정적이거나 검증되지 않은 정보가 포함되어 있습니다.",
            "F": "신뢰할 수 없는 콘텐츠입니다. 클릭베이트나 의심스러운 정보가 포함되어 있습니다."
        }
        return descriptions.get(grade, "알 수 없는 등급입니다.") 