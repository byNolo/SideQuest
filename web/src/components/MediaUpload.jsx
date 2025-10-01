import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useDebugUser } from '../context/DebugUserContext';

const MediaUpload = ({ onUploadComplete }) => {
  const { debugUser } = useDebugUser();
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [error, setError] = useState(null);

  const uploadFile = async (file) => {
    if (!debugUser) {
      setError('Please select a debug user first');
      return;
    }

    setIsUploading(true);
    setError(null);
    
    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', file);
      
      // Upload file with debug authentication
      const response = await fetch('/api/media/upload', {
        method: 'POST',
        headers: {
          'X-Debug-User': debugUser,
        },
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Upload failed: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      // Add to uploaded files list
      const newFile = {
        id: Date.now(),
        name: file.name,
        size: file.size,
        type: file.type,
        object_name: result.file_info.object_name,
        url: result.file_info.url,
        thumbnail_url: result.thumbnail_url,
        file_hash: result.file_hash
      };
      
      setUploadedFiles(prev => [...prev, newFile]);
      
      if (onUploadComplete) {
        onUploadComplete(newFile);
      }
      
      setUploadProgress(100);
      
    } catch (err) {
      setError(err.message);
      console.error('Upload error:', err);
    } finally {
      setIsUploading(false);
      setTimeout(() => setUploadProgress(0), 2000);
    }
  };

  const onDrop = useCallback((acceptedFiles) => {
    acceptedFiles.forEach(uploadFile);
  }, [debugUser]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif'],
      'video/*': ['.mp4', '.mov', '.avi']
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    multiple: true
  });

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-6 text-center cursor-pointer
          transition-colors duration-200 
          ${isDragActive 
            ? 'border-blue-400 bg-blue-900/10' 
            : 'border-slate-600 hover:border-slate-500 bg-slate-800/30'
          }
          ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="space-y-2">
          <div className="text-4xl">📁</div>
          
          {isDragActive ? (
            <p className="text-blue-400 font-medium">Drop files here...</p>
          ) : (
            <div>
              <p className="text-slate-300 font-medium">
                Drag & drop files here, or click to select
              </p>
              <p className="text-sm text-slate-500">
                Images (PNG, JPG, GIF) and videos (MP4, MOV, AVI) up to 50MB
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Upload Progress */}
      {isUploading && (
        <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-300">Uploading...</span>
            <span className="text-sm text-blue-400">{uploadProgress}%</span>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-900/20 border border-red-800 rounded-lg p-4">
          <p className="text-red-400 font-medium">Upload Error</p>
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      )}

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-medium text-slate-300">Uploaded Files</h3>
          <div className="space-y-2">
            {uploadedFiles.map((file) => (
              <div key={file.id} className="flex items-center justify-between bg-slate-800/50 rounded-lg p-3 border border-slate-700">
                <div className="flex items-center space-x-3">
                  {/* Thumbnail or File Icon */}
                  {file.thumbnail_url ? (
                    <img 
                      src={file.thumbnail_url} 
                      alt={file.name}
                      className="w-12 h-12 object-cover rounded"
                    />
                  ) : (
                    <div className="w-12 h-12 bg-slate-700 rounded flex items-center justify-center">
                      {file.type.startsWith('video/') ? '🎥' : '📄'}
                    </div>
                  )}
                  
                  {/* File Info */}
                  <div>
                    <p className="font-medium text-slate-300">{file.name}</p>
                    <p className="text-sm text-slate-500">
                      {(file.size / 1024 / 1024).toFixed(1)} MB
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <a 
                    href={file.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors"
                  >
                    View
                  </a>
                  <button
                    onClick={() => removeFile(file.id)}
                    className="text-red-400 hover:text-red-300 text-sm font-medium transition-colors"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MediaUpload;