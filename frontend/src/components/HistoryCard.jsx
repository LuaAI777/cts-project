import React from 'react';

const HistoryCard = ({ history }) => {
  return (
    <div className="card mb-4">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold">{history.title}</h3>
          <p className="text-gray-600">{history.description}</p>
        </div>
        <div className="text-sm text-gray-500">
          {new Date(history.created_at).toLocaleDateString()}
        </div>
      </div>
      <div className="mt-2">
        <span className={`inline-block px-2 py-1 text-xs rounded-full ${
          history.status === 'approved' ? 'bg-green-100 text-green-800' :
          history.status === 'rejected' ? 'bg-red-100 text-red-800' :
          'bg-yellow-100 text-yellow-800'
        }`}>
          {history.status}
        </span>
      </div>
    </div>
  );
};

export default HistoryCard; 