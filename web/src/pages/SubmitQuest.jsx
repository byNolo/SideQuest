import React, { useState, useEffect } from 'react';
import SubmissionForm from '../components/SubmissionForm';
import { useDebugUser } from '../context/DebugUserContext';
import { useApi } from '../hooks/useApi';

const SubmitQuestPage = () => {
  const { debugUser } = useDebugUser();
  const { request } = useApi();
  const [todaysQuest, setTodaysQuest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submissionComplete, setSubmissionComplete] = useState(false);

  useEffect(() => {
    const fetchTodaysQuest = async () => {
      if (!debugUser) return;

      try {
        setLoading(true);
        setError(null);

        // Fetch today's quest using the proper API client
        const data = await request('/quests/today');
        setTodaysQuest(data.quest);

      } catch (err) {
        setError(err.message);
        console.error('Error fetching quest:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchTodaysQuest();
  }, [debugUser, request]);

  const handleSubmissionComplete = (submission) => {
    setSubmissionComplete(true);
    console.log('Submission completed:', submission);
  };

  if (!debugUser) {
    return (
      <div className="text-center text-slate-400">
        <p>Please select a debug user to continue</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
        <span className="ml-3 text-slate-400">Loading your quest...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-800 rounded-lg p-6">
        <h3 className="text-red-400 font-semibold mb-2">Error Loading Quest</h3>
        <p className="text-red-300">{error}</p>
        <button 
          onClick={() => window.location.reload()} 
          className="mt-4 px-4 py-2 bg-red-700 hover:bg-red-600 text-white rounded-lg transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (submissionComplete) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-green-900/20 border border-green-800 rounded-lg p-8 text-center">
          <div className="text-6xl mb-4">🎉</div>
          <h2 className="text-2xl font-bold text-green-400 mb-2">Quest Completed!</h2>
          <p className="text-green-300 mb-6">
            Your submission has been saved successfully. Great work on completing today's quest!
          </p>
          <div className="flex gap-4 justify-center">
            <button
              onClick={() => setSubmissionComplete(false)}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
            >
              Submit Another
            </button>
            <button
              onClick={() => window.location.href = '/'}
              className="px-6 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded-lg transition-colors"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!todaysQuest) {
    return (
      <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
        <h3 className="text-slate-400 font-semibold mb-2">No Quest Available</h3>
        <p className="text-slate-500">No quest found for today. Check back later or try refreshing the page.</p>
      </div>
    );
  }

  // Format quest data for the SubmissionForm component
  const questForForm = {
    id: todaysQuest.id,
    description: todaysQuest.generated_context?.description || todaysQuest.description,
    location: todaysQuest.generated_context?.location || todaysQuest.location,
    title: todaysQuest.generated_context?.title || 'Today\'s Quest',
    weather: todaysQuest.weather_context?.conditions?.join(', ') || 'Unknown',
    difficulty: todaysQuest.difficulty || 1,
    rarity: todaysQuest.rarity || 'common'
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-100 mb-2">Submit Your Quest</h1>
        <p className="text-slate-400">
          Complete today's quest by uploading photos/videos and sharing your experience.
        </p>
      </div>

      {/* Debug Info */}
      <div className="bg-slate-800/30 border border-slate-700 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-slate-400">Debug User</p>
            <p className="font-medium text-slate-200">{debugUser}</p>
          </div>
          <div>
            <p className="text-sm text-slate-400">Quest ID</p>
            <p className="font-medium text-slate-200">{todaysQuest.id}</p>
          </div>
        </div>
      </div>

      {/* Submission Form */}
      <div className="bg-slate-900/50 rounded-lg">
        <SubmissionForm 
          quest={questForForm} 
          onSubmissionComplete={handleSubmissionComplete}
        />
      </div>
    </div>
  );
};

export default SubmitQuestPage;