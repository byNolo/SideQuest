import React, { useState } from 'react';
import MediaUpload from '../components/MediaUpload';
import { useDebugUser } from '../context/DebugUserContext';

const SubmissionForm = ({ quest, onSubmissionComplete }) => {
  const { debugUser } = useDebugUser();
  const [caption, setCaption] = useState('');
  const [mediaFiles, setMediaFiles] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleMediaUpload = (file) => {
    setMediaFiles(prev => [...prev, {
      object_name: file.object_name,
      url: file.url,
      thumbnail_url: file.thumbnail_url,
      type: file.type,
      size: file.size,
      name: file.name
    }]);
  };

  const submitQuest = async () => {
    if (!debugUser) {
      setError('Please select a debug user first');
      return;
    }

    if (mediaFiles.length === 0 && !caption.trim()) {
      setError('Please add at least a photo/video or a caption');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch('/api/submissions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Debug-User': debugUser,
        },
        body: JSON.stringify({
          quest_id: quest.id,
          caption: caption.trim() || null,
          media: mediaFiles
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Failed to submit quest');
      }

      const result = await response.json();
      
      if (onSubmissionComplete) {
        onSubmissionComplete(result.submission);
      }

      // Reset form
      setCaption('');
      setMediaFiles([]);

    } catch (err) {
      setError(err.message);
      console.error('Submission error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-slate-800/50 rounded-lg border border-slate-700">
      <h2 className="text-2xl font-bold mb-6 text-slate-100">Complete Your Quest</h2>
      
      {/* Quest Context */}
      {quest && (
        <div className="mb-6 p-4 bg-blue-900/20 border border-blue-800 rounded-lg">
          <h3 className="font-semibold text-blue-300 mb-2">Today's Quest</h3>
          <p className="text-blue-200">{quest.description}</p>
          {quest.location && (
            <p className="text-sm text-blue-400 mt-2">📍 {quest.location}</p>
          )}
          <div className="flex gap-4 mt-3 text-sm">
            {quest.difficulty && (
              <span className="text-slate-400">
                Difficulty: <span className="text-yellow-400">{'★'.repeat(quest.difficulty)}</span>
              </span>
            )}
            {quest.rarity && (
              <span className="text-slate-400">
                Rarity: <span className={`font-medium ${
                  quest.rarity === 'legendary' ? 'text-purple-400' :
                  quest.rarity === 'rare' ? 'text-orange-400' : 'text-green-400'
                }`}>
                  {quest.rarity}
                </span>
              </span>
            )}
          </div>
        </div>
      )}

      {/* Media Upload */}
      <div className="mb-6">
        <h3 className="font-semibold mb-3 text-slate-200">Add Photos or Videos</h3>
        <MediaUpload onUploadComplete={handleMediaUpload} />
      </div>

      {/* Caption Input */}
      <div className="mb-6">
        <label htmlFor="caption" className="block font-semibold mb-2 text-slate-200">
          Caption (Optional)
        </label>
        <textarea
          id="caption"
          value={caption}
          onChange={(e) => setCaption(e.target.value)}
          placeholder="Tell us about your quest experience..."
          maxLength="500"
          rows="4"
          className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <div className="flex justify-between mt-1">
          <span className="text-sm text-slate-400">
            Share your experience, discoveries, or thoughts about this quest
          </span>
          <span className="text-sm text-slate-500">
            {caption.length}/500
          </span>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 bg-red-900/20 border border-red-800 rounded-lg p-4">
          <p className="text-red-300">{error}</p>
        </div>
      )}

      {/* Submission Summary */}
      {mediaFiles.length > 0 && (
        <div className="mb-6 p-4 bg-green-900/20 border border-green-800 rounded-lg">
          <p className="text-green-300 font-medium">
            Ready to submit with {mediaFiles.length} media file{mediaFiles.length !== 1 ? 's' : ''}
            {caption.trim() && ' and a caption'}
          </p>
        </div>
      )}

      {/* Submit Button */}
      <button
        onClick={submitQuest}
        disabled={isSubmitting || (mediaFiles.length === 0 && !caption.trim())}
        className={`
          w-full py-3 px-6 rounded-lg font-semibold transition-colors duration-200
          ${isSubmitting || (mediaFiles.length === 0 && !caption.trim())
            ? 'bg-slate-600 text-slate-400 cursor-not-allowed' 
            : 'bg-blue-600 text-white hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500'
          }
        `}
      >
        {isSubmitting ? 'Submitting Quest...' : 'Submit Quest'}
      </button>

      {/* Submission Guidelines */}
      <div className="mt-6 p-4 bg-slate-700/50 rounded-lg">
        <h4 className="font-semibold text-slate-200 mb-2">Submission Guidelines</h4>
        <ul className="text-sm text-slate-400 space-y-1">
          <li>• Add photos or videos that showcase your quest completion</li>
          <li>• Write a caption describing your experience (optional but encouraged)</li>
          <li>• Be authentic and creative in your approach</li>
          <li>• Respect privacy and local rules when taking photos</li>
        </ul>
      </div>
    </div>
  );
};

export default SubmissionForm;