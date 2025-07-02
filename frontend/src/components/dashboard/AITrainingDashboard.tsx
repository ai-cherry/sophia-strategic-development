import React from 'react';
import KnowledgeGapAnalysis from './KnowledgeGapAnalysis';
import UserImpactManagement from './UserImpactManagement'; 

const AITrainingDashboard: React.FC = () => {
  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-8">
      <header>
        <h1 className="text-4xl font-extrabold text-white tracking-tight">
          AI Training & Curation Dashboard
        </h1>
        <p className="mt-2 text-lg text-gray-400">
          Oversee, manage, and enhance the intelligence of the Sophia AI platform.
        </p>
      </header>

      {/* Knowledge Gap Analysis Section 
      <section>
        <KnowledgeGapAnalysis />
      </section>

      {/* User Impact Management Section 
      <section>
        <UserImpactManagement />
      </section>

      {/* Live Feed Section - To be added later 
      {/*
      <section>
        <h2 className="text-2xl font-bold text-white mb-4">Live Knowledge Feed</h2>
        // Component would go here
      </section>
      
    </div>
  );
};

export default AITrainingDashboard;
