import React, { useState, useEffect } from 'react';

// --- Mock API Service ---
const api = {
  getUserImpactScores: async (): Promise<UserImpact[]> => {
    console.log("Fetching user impact scores...");
    // Mocking the API call for GET /api/v1/admin/users/training-impact
    const mockUsers: UserImpact[] = [
        { user_id: "ceo_001", username: "Lynn (CEO)", training_impact_score: 1.0 },
        { user_id: "eng_001", username: "SophiaDev (Lead)", training_impact_score: 0.8 },
        { user_id: "sales_001", username: "SalesLead", training_impact_score: 0.7 },
        { user_id: "csr_001", username: "SupportRep", training_impact_score: 0.2 },
        { user_id: "user_005", username: "John Doe", training_impact_score: 0.1 },
    ];
    await new Promise(resolve => setTimeout(resolve, 500));
    return mockUsers;
  },
  setUserImpactScore: async (userId: string, score: number): Promise<{status: string}> => {
    console.log(`Setting impact score for ${userId} to ${score}...`);
    // Mocking the API call for PUT /api/v1/admin/users/{user_id}/training-impact
    await new Promise(resolve => setTimeout(resolve, 300));
    return { status: "success" };
  },
};

// --- Type Definitions ---
interface UserImpact {
  user_id: string;
  username: string;
  training_impact_score: number;
}

// --- Main Component ---
const UserImpactManagement: React.FC = () => {
  const [users, setUsers] = useState<UserImpact[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchScores = async () => {
      setIsLoading(true);
      const data = await api.getUserImpactScores();
      setUsers(data);
      setIsLoading(false);
    };
    fetchScores();
  }, []);
  
  const handleScoreChange = (userId: string, newScore: number) => {
    const updatedUsers = users.map(u => u.user_id === userId ? { ...u, training_impact_score: newScore } : u);
    setUsers(updatedUsers);
  };

  const handleSave = (userId: string, score: number) => {
    api.setUserImpactScore(userId, score).then(() => {
        alert(`Successfully updated impact score for user ${userId}.`);
    });
  };

  if (isLoading) {
    return <div className="text-center p-8">Loading User Scores...</div>;
  }

  return (
    <div className="bg-gray-800 bg-opacity-50 backdrop-blur-md rounded-lg p-6 shadow-lg text-white">
      <h3 className="text-xl font-bold mb-4">User Training Impact Scores</h3>
      <p className="text-gray-400 mb-6">
        Set the authoritative weight for each user's training input. A score of 1.0 is the highest authority.
      </p>
      <div className="space-y-4">
        {users.map(user => (
          <div key={user.user_id} className="flex items-center justify-between bg-gray-700 bg-opacity-50 p-4 rounded-lg">
            <div className="font-medium">{user.username}</div>
            <div className="flex items-center space-x-4">
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={user.training_impact_score}
                onChange={(e) => handleScoreChange(user.user_id, parseFloat(e.target.value))}
                className="w-48"
              />
              <span className="font-mono text-lg w-12 text-center">{user.training_impact_score.toFixed(1)}</span>
              <button
                onClick={() => handleSave(user.user_id, user.training_impact_score)}
                className="bg-green-600 hover:bg-green-500 text-white font-bold py-1 px-3 rounded-lg text-sm"
              >
                Save
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default UserImpactManagement;
