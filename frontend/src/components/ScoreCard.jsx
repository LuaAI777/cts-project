const ScoreCard = ({ result }) => {
  const getGradeColor = (grade) => {
    switch (grade) {
      case 'A': return 'text-green-600';
      case 'B': return 'text-blue-600';
      case 'C': return 'text-yellow-600';
      case 'D': return 'text-orange-600';
      case 'F': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="p-6">
        <div className="text-center mb-6">
          <div className={`text-6xl font-bold ${getGradeColor(result.grade)}`}>
            {result.grade}
          </div>
          <p className="text-gray-600 mt-2">{result.grade_description}</p>
        </div>

        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-1">종합 점수</h4>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-primary-600 h-2.5 rounded-full"
                style={{ width: `${result.final_score * 100}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600 mt-1">
              {(result.final_score * 100).toFixed(1)}%
            </p>
          </div>

          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-1">출처/채널 신뢰도</h4>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-primary-600 h-2.5 rounded-full"
                style={{ width: `${result.trust_analysis.total_score * 100}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600 mt-1">
              {(result.trust_analysis.total_score * 100).toFixed(1)}%
            </p>
          </div>

          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-1">내용 신뢰도</h4>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-primary-600 h-2.5 rounded-full"
                style={{ width: `${result.content_analysis.total_score * 100}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600 mt-1">
              {(result.content_analysis.total_score * 100).toFixed(1)}%
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScoreCard; 