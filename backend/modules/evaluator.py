from typing import Dict
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