import {
  GRADE_THRESHOLDS,
  SCORE_FORMULAS,
  SOURCE_FACTORS,
  CONTENT_FACTORS
} from '../constants/evaluation';

export class EvaluationService {
  constructor() {
    this.history = [];
  }

  // 비디오 평가
  evaluateVideo(videoData) {
    const sourceScore = this.evaluateSource(videoData);
    const contentScore = this.evaluateContent(videoData);
    const totalScore = SCORE_FORMULAS.calculateTotalScore(sourceScore, contentScore);
    const grade = this.calculateGrade(totalScore);

    const evaluation = {
      grade,
      totalScore,
      sourceScore,
      contentScore,
      factors: {
        source: this.getSourceFactors(videoData),
        content: this.getContentFactors(videoData)
      }
    };

    this.addToHistory(videoData, evaluation);
    return evaluation;
  }

  // 출처/채널 평가
  evaluateSource(videoData) {
    const factors = {
      subscribers: videoData.subscriberCount,
      activityDays: this.calculateActivityDays(videoData.publishedAt),
      engagement: {
        likes: videoData.likeCount / videoData.viewCount,
        comments: videoData.commentCount / videoData.viewCount
      }
    };

    return SCORE_FORMULAS.calculateSourceScore(factors);
  }

  // 내용 평가
  evaluateContent(videoData) {
    const factors = {
      title: videoData.title,
      description: videoData.description,
      sentiment: this.analyzeSentiment(videoData.title, videoData.description)
    };

    return SCORE_FORMULAS.calculateContentScore(factors);
  }

  // 등급 계산
  calculateGrade(score) {
    if (score >= GRADE_THRESHOLDS.A) return 'A';
    if (score >= GRADE_THRESHOLDS.B) return 'B';
    if (score >= GRADE_THRESHOLDS.C) return 'C';
    if (score >= GRADE_THRESHOLDS.D) return 'D';
    return 'F';
  }

  // 활동 기간 계산
  calculateActivityDays(publishedAt) {
    const publishedDate = new Date(publishedAt);
    const now = new Date();
    return Math.floor((now - publishedDate) / (1000 * 60 * 60 * 24));
  }

  // 감정 분석 (간단한 구현)
  analyzeSentiment(title, description) {
    // 실제로는 NLP API를 사용해야 함
    const text = `${title} ${description}`;
    const positiveWords = ['좋다', '유용', '정확', '신뢰'];
    const negativeWords = ['나쁘다', '거짓', '의심', '불신'];

    let sentiment = 0;
    positiveWords.forEach(word => {
      if (text.includes(word)) sentiment += 0.1;
    });
    negativeWords.forEach(word => {
      if (text.includes(word)) sentiment -= 0.1;
    });

    return Math.max(-1, Math.min(1, sentiment));
  }

  // 출처 요소 분석
  getSourceFactors(videoData) {
    return {
      subscribers: {
        count: videoData.subscriberCount,
        score: this.calculateSubscriberScore(videoData.subscriberCount)
      },
      activity: {
        days: this.calculateActivityDays(videoData.publishedAt),
        score: this.calculateActivityScore(this.calculateActivityDays(videoData.publishedAt))
      },
      engagement: {
        likeRatio: videoData.likeCount / videoData.viewCount,
        commentRatio: videoData.commentCount / videoData.viewCount,
        score: this.calculateEngagementScore({
          likes: videoData.likeCount / videoData.viewCount,
          comments: videoData.commentCount / videoData.viewCount
        })
      }
    };
  }

  // 내용 요소 분석
  getContentFactors(videoData) {
    return {
      title: {
        length: videoData.title.length,
        score: this.calculateTitleScore(videoData.title)
      },
      description: {
        length: videoData.description.length,
        score: this.calculateDescriptionScore(videoData.description)
      },
      sentiment: {
        value: this.analyzeSentiment(videoData.title, videoData.description),
        score: this.calculateSentimentScore(
          this.analyzeSentiment(videoData.title, videoData.description)
        )
      }
    };
  }

  // 히스토리 관리
  addToHistory(videoData, evaluation) {
    this.history.unshift({
      id: Date.now(),
      videoId: videoData.videoId,
      title: videoData.title,
      date: new Date().toISOString(),
      ...evaluation
    });

    // 최근 10개만 유지
    this.history = this.history.slice(0, 10);
  }

  getHistory() {
    return this.history;
  }
} 