// 등급 기준
export const GRADE_THRESHOLDS = {
  A: 0.8,  // 매우 신뢰할 수 있음
  B: 0.6,  // 신뢰할 수 있음
  C: 0.4,  // 보통
  D: 0.2,  // 주의 필요
  F: 0     // 신뢰할 수 없음
};

// 가중치
export const WEIGHTS = {
  SOURCE: 0.6,    // 출처/채널 신뢰도
  CONTENT: 0.4    // 내용 신뢰도
};

// 출처/채널 평가 요소
export const SOURCE_FACTORS = {
  SUBSCRIBERS: {
    weight: 0.3,
    thresholds: {
      high: 1000000,    // 100만 구독자
      medium: 100000,   // 10만 구독자
      low: 10000        // 1만 구독자
    }
  },
  ACTIVITY: {
    weight: 0.2,
    thresholds: {
      high: 365,        // 1년 이상
      medium: 180,      // 6개월 이상
      low: 90           // 3개월 이상
    }
  },
  ENGAGEMENT: {
    weight: 0.5,
    metrics: {
      likeRatio: 0.1,   // 좋아요 비율
      commentRatio: 0.1 // 댓글 비율
    }
  }
};

// 내용 평가 요소
export const CONTENT_FACTORS = {
  TITLE: {
    weight: 0.3,
    criteria: {
      length: {
        optimal: 50,    // 최적 길이
        max: 100        // 최대 길이
      },
      keywords: {
        required: ['연구', '데이터', '출처'],
        suspicious: ['확실', '무조건', '100%']
      }
    }
  },
  DESCRIPTION: {
    weight: 0.4,
    criteria: {
      length: {
        optimal: 200,
        min: 50
      },
      links: {
        max: 5,
        quality: ['edu', 'gov', 'org']
      }
    }
  },
  SENTIMENT: {
    weight: 0.3,
    thresholds: {
      neutral: 0.5,     // 중립적
      extreme: 0.8      // 극단적
    }
  }
};

// 점수 계산 공식
export const SCORE_FORMULAS = {
  // 출처/채널 점수 계산
  calculateSourceScore: (factors) => {
    const { SUBSCRIBERS, ACTIVITY, ENGAGEMENT } = SOURCE_FACTORS;
    
    const subscriberScore = calculateSubscriberScore(factors.subscribers);
    const activityScore = calculateActivityScore(factors.activityDays);
    const engagementScore = calculateEngagementScore(factors.engagement);
    
    return (
      subscriberScore * SUBSCRIBERS.weight +
      activityScore * ACTIVITY.weight +
      engagementScore * ENGAGEMENT.weight
    );
  },

  // 내용 점수 계산
  calculateContentScore: (factors) => {
    const { TITLE, DESCRIPTION, SENTIMENT } = CONTENT_FACTORS;
    
    const titleScore = calculateTitleScore(factors.title);
    const descriptionScore = calculateDescriptionScore(factors.description);
    const sentimentScore = calculateSentimentScore(factors.sentiment);
    
    return (
      titleScore * TITLE.weight +
      descriptionScore * DESCRIPTION.weight +
      sentimentScore * SENTIMENT.weight
    );
  },

  // 종합 점수 계산
  calculateTotalScore: (sourceScore, contentScore) => {
    return (
      sourceScore * WEIGHTS.SOURCE +
      contentScore * WEIGHTS.CONTENT
    );
  }
};

// 보조 계산 함수들
const calculateSubscriberScore = (subscribers) => {
  const { high, medium, low } = SOURCE_FACTORS.SUBSCRIBERS.thresholds;
  
  if (subscribers >= high) return 1.0;
  if (subscribers >= medium) return 0.8;
  if (subscribers >= low) return 0.6;
  return 0.4;
};

const calculateActivityScore = (activityDays) => {
  const { high, medium, low } = SOURCE_FACTORS.ACTIVITY.thresholds;
  
  if (activityDays >= high) return 1.0;
  if (activityDays >= medium) return 0.8;
  if (activityDays >= low) return 0.6;
  return 0.4;
};

const calculateEngagementScore = (engagement) => {
  const { likeRatio, commentRatio } = SOURCE_FACTORS.ENGAGEMENT.metrics;
  
  return (
    (engagement.likes * likeRatio) +
    (engagement.comments * commentRatio)
  );
};

const calculateTitleScore = (title) => {
  const { length, keywords } = CONTENT_FACTORS.TITLE.criteria;
  
  let score = 1.0;
  
  // 길이 점수
  if (title.length > length.max) score *= 0.8;
  else if (title.length < length.optimal) score *= 0.9;
  
  // 키워드 점수
  const hasRequired = keywords.required.some(kw => title.includes(kw));
  const hasSuspicious = keywords.suspicious.some(kw => title.includes(kw));
  
  if (hasRequired) score *= 1.1;
  if (hasSuspicious) score *= 0.9;
  
  return Math.min(score, 1.0);
};

const calculateDescriptionScore = (description) => {
  const { length, links } = CONTENT_FACTORS.DESCRIPTION.criteria;
  
  let score = 1.0;
  
  // 길이 점수
  if (description.length < length.min) score *= 0.8;
  else if (description.length < length.optimal) score *= 0.9;
  
  // 링크 점수
  const linkCount = description.match(/https?:\/\/[^\s]+/g)?.length || 0;
  if (linkCount > links.max) score *= 0.9;
  
  const qualityLinks = links.quality.filter(domain => 
    description.includes(domain)
  ).length;
  
  score *= 1 + (qualityLinks * 0.1);
  
  return Math.min(score, 1.0);
};

const calculateSentimentScore = (sentiment) => {
  const { neutral, extreme } = CONTENT_FACTORS.SENTIMENT.thresholds;
  
  if (Math.abs(sentiment) <= neutral) return 1.0;
  if (Math.abs(sentiment) >= extreme) return 0.7;
  return 0.85;
}; 