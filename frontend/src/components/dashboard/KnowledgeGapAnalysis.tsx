import React, { useState, useEffect } from 'react';

// --- Mock API Service ---
// In a real application, this would be in a separate api.ts file
// and would use a library like axios with proper auth headers.
const api = {
  getKnowledgeGaps: async (): Promise<KnowledgeGap[]> => {
    console.log("Fetching knowledge gaps...");
    // Mocking the API call for frontend development.
    // The real endpoint is GET /api/v1/admin/training/gaps
    const mockGaps: KnowledgeGap[] = [
      { topic: "Q4 Sales Strategy", queries_missed: 15, priority: "High" },
      { topic: "Project Phoenix Budget", queries_missed: 12, priority: "High" },
      { topic: "Competitor X Pricing Model", queries_missed: 9, priority: "Medium" },
      { topic: "New Employee Onboarding Process", queries_missed: 5, priority: "Low" },
    ];
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 500));
    return mockGaps;
  },
};

// --- Type Definitions ---
interface KnowledgeGap {
  topic: string;
  queries_missed: number;
  priority: 'High' | 'Medium' | 'Low';
}

const priorityStyles = {
  High: 'bg-red-500 text-white',
  Medium: 'bg-yellow-500 text-black',
  Low: 'bg-blue-500 text-white',
};

// --- Main Component ---
const KnowledgeGapAnalysis: React.FC = () => {
  const [gaps, setGaps] = useState<KnowledgeGap[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchGaps = async () => {
      try {
        setIsLoading(true);
        const data = await api.getKnowledgeGaps();
        // Sort by priority and then by queries missed
        data.sort((a, b) => {
          const priorityOrder = { High: 3, Medium: 2, Low: 1 };
          if (priorityOrder[a.priority] !== priorityOrder[b.priority]) {
            return priorityOrder[b.priority] - priorityOrder[a.priority];
          }
          return b.queries_missed - a.queries_missed;
        });
        setGaps(data);
      } catch (err) {
        setError('Failed to fetch knowledge gaps. Please try again later.');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchGaps();
  }, []);

  const handleDefineTopic = (topic: string) => {
    // In a real implementation, this would open a modal where the user
    // could type a definition, which would then be sent to the
    // `submit_training_data` MCP tool.
    alert(`Define Topic modal for: "${topic}"\n\n(This would trigger a call to the 'submit_training_data' MCP tool.)`);
  };

  if (isLoading) {
    return <div className="text-center p-8">Loading Knowledge Gaps...</div>;
  }

  if (error) {
    return <div className="text-center p-8 text-red-500">{error}</div>;
  }

  return (
    <div className="bg-gray-800 bg-opacity-50 backdrop-blur-md rounded-lg p-6 shadow-lg text-white">
      <h2 className="text-2xl font-bold mb-4">AI Knowledge Gap Analysis</h2>
      <p className="text-gray-400 mb-6">
        The AI has proactively identified these topics from recent company communications as areas where its knowledge is weak. Provide definitions to make the system smarter.
      </p>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-gray-600">
              <th className="p-3">Priority</th>
              <th className="p-3">Topic / Knowledge Gap</th>
              <th className="p-3 text-center">Frequency</th>
              <th className="p-3 text-center">Action</th>
            </tr>
          </thead>
          <tbody>
            {gaps.map((gap, index) => (
              <tr key={index} className="border-b border-gray-700 hover:bg-gray-700 bg-opacity-50">
                <td className="p-3">
                  <span className={`px-3 py-1 text-xs font-bold rounded-full ${priorityStyles[gap.priority]}`}>
                    {gap.priority}
                  </span>
                </td>
                <td className="p-3 font-medium">{gap.topic}</td>
                <td className="p-3 text-center text-gray-300">{gap.queries_missed} times</td>
                <td className="p-3 text-center">
                  <button
                    onClick={() => handleDefineTopic(gap.topic)}
                    className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-2 px-4 rounded-lg transition-colors duration-200"
                  >
                    Define Topic
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default KnowledgeGapAnalysis;
