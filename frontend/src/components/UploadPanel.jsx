/**
 * UploadPanel Component
 * 
 * File upload UI with drag-and-drop for funding call and supporting documents
 * Features:
 * - Drag-and-drop zone with visual feedback
 * - Funding call PDF upload (single file, 10MB max)
 * - Supporting docs upload (PDF/DOCX, max 5 files, 50MB total)
 * - Progress indicators for upload and indexing
 * - Quota display (file count and size)
 * - Error handling with toast messages
 */

import { useState, useEffect } from 'react';
import {
  sessionAPI,
  uploadAPI,
  samplesAPI,
  fileValidation,
  formatFileSize,
  getErrorMessage,
} from '../services/api';
import './UploadPanel.css';

export default function UploadPanel({ onUploadComplete }) {
  // Session state
  const [sessionId, setSessionId] = useState(null);
  const [sessionLoading, setSessionLoading] = useState(true);

  // Upload state
  const [fundingCallFile, setFundingCallFile] = useState(null);
  const [fundingCallUploaded, setFundingCallUploaded] = useState(false);
  const [fundingCallProgress, setFundingCallProgress] = useState(0);
  const [fundingCallUploading, setFundingCallUploading] = useState(false);
  const [fundingCallChunks, setFundingCallChunks] = useState(null);

  const [supportingDocs, setSupportingDocs] = useState([]);
  const [supportingDocsUploaded, setSupportingDocsUploaded] = useState([]);
  const [supportingDocsProgress, setSupportingDocsProgress] = useState(0);
  const [supportingDocsUploading, setSupportingDocsUploading] = useState(false);

  // Quota state
  const [quota, setQuota] = useState({
    used_mb: 0,
    max_mb: 50,
    remaining_mb: 50,
    file_count: 0,
  });

  // UI state
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  // Initialize session on mount
  useEffect(() => {
    console.log('[UploadPanel] useEffect called, sessionId:', sessionId);
    // Prevent double initialization in React StrictMode
    if (!sessionId) {
      initializeSession();
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Helper to normalize quota structure from backend
  function normalizeQuota(backendQuota) {
    if (!backendQuota) {
      return {
        used_mb: 0,
        max_mb: 50,
        remaining_mb: 50,
        file_count: 0,
      };
    }
    
    // Backend returns: total_size_mb, max_size_mb, size_remaining_mb
    // Frontend expects: used_mb, max_mb, remaining_mb
    return {
      used_mb: backendQuota.total_size_mb || 0,
      max_mb: backendQuota.max_size_mb || 50,
      remaining_mb: backendQuota.size_remaining_mb || 50,
      file_count: backendQuota.supporting_docs_count || 0,
    };
  }

  async function initializeSession() {
    console.log('[UploadPanel] initializeSession called');
    try {
      setSessionLoading(true);
      console.log('[UploadPanel] Calling sessionAPI.createSession()...');
      const session = await sessionAPI.createSession();
      console.log('[UploadPanel] Session created:', session);
      setSessionId(session.session_id);
      
      // Set initial quota from session creation response
      if (session.quota) {
        console.log('[UploadPanel] Setting initial quota from session:', session.quota);
        setQuota(normalizeQuota(session.quota));
      }
      
      setSessionLoading(false);
      showSuccess('Session created successfully');
      
      // Notify parent of session creation
      if (onUploadComplete) {
        console.log('[UploadPanel] Notifying parent with session-created event, session_id:', session.session_id);
        onUploadComplete('session-created', { session_id: session.session_id });
      }
    } catch (err) {
      console.error('[UploadPanel] Session initialization error:', err);
      setSessionLoading(false);
      showError('Failed to create session: ' + getErrorMessage(err));
    }
  }

  // Update quota periodically
  useEffect(() => {
    if (!sessionId || sessionLoading) return;

    async function updateQuota() {
      try {
        const status = await uploadAPI.getUploadStatus(sessionId);
        if (status && status.quota) {
          setQuota(normalizeQuota(status.quota));
        }
      } catch (err) {
        console.error('Failed to update quota:', err);
        // Don't show error to user - quota update is non-critical
      }
    }

    // Wait a bit before first quota update to ensure session is ready
    const initialTimeout = setTimeout(updateQuota, 500);
    const interval = setInterval(updateQuota, 5000); // Update every 5s
    
    return () => {
      clearTimeout(initialTimeout);
      clearInterval(interval);
    };
  }, [sessionId, sessionLoading, fundingCallUploaded, supportingDocsUploaded]);

  // Drag and drop handlers
  function handleDrag(e) {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }

  function handleDrop(e, type) {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = Array.from(e.dataTransfer.files);
    if (type === 'funding-call') {
      if (files.length > 0) {
        handleFundingCallFileSelect(files[0]);
      }
    } else if (type === 'supporting-docs') {
      handleSupportingDocsFileSelect(files);
    }
  }

  // Funding call handlers
  function handleFundingCallFileSelect(file) {
    const validation = fileValidation.validateFundingCall(file);
    if (!validation.valid) {
      showError(validation.error);
      return;
    }
    setFundingCallFile(file);
    setError(null);
  }

  async function loadSampleFundingCall() {
    console.log('[UploadPanel] Loading sample funding call...');
    try {
      setError(null);
      const sampleFile = await samplesAPI.loadSampleFundingCall();
      console.log('[UploadPanel] Sample funding call loaded:', sampleFile.name);
      handleFundingCallFileSelect(sampleFile);
      showSuccess('Sample funding call loaded! Click "Upload & Index" to proceed.');
    } catch (err) {
      console.error('[UploadPanel] Failed to load sample funding call:', err);
      showError('Failed to load sample funding call: ' + getErrorMessage(err));
    }
  }

  async function uploadFundingCall() {
    console.log('[UploadPanel] uploadFundingCall called');
    console.log('[UploadPanel] Session ID:', sessionId);
    console.log('[UploadPanel] File:', fundingCallFile);
    
    if (!fundingCallFile || !sessionId) {
      console.warn('[UploadPanel] Missing file or session ID');
      return;
    }

    try {
      setFundingCallUploading(true);
      setFundingCallProgress(0);
      setError(null);
      console.log('[UploadPanel] Starting funding call upload...');

      const result = await uploadAPI.uploadFundingCall(
        sessionId,
        fundingCallFile,
        (progress) => {
          console.log('[UploadPanel] Upload progress:', progress);
          setFundingCallProgress(progress);
        }
      );

      console.log('[UploadPanel] Upload result:', result);
      
      // Check if upload was successful (result.uploaded is true)
      if (result.uploaded) {
        setFundingCallUploaded(true);
        setFundingCallChunks(result.chunk_count);
        showSuccess(
          `Funding call uploaded and indexed! ${result.chunk_count} chunks created.`
        );
        
        console.log('[UploadPanel] Notifying parent with funding-call event');
        if (onUploadComplete) {
          onUploadComplete('funding-call', { ...result, session_id: sessionId });
        }
      } else {
        console.error('[UploadPanel] Upload failed - result.uploaded is false');
        showError('Failed to upload funding call');
      }
    } catch (err) {
      console.error('[UploadPanel] Upload error:', err);
      showError('Failed to upload funding call: ' + getErrorMessage(err));
      setFundingCallFile(null);
    } finally {
      setFundingCallUploading(false);
      setFundingCallProgress(0);
    }
  }

  // Supporting docs handlers
  function handleSupportingDocsFileSelect(files) {
    const validation = fileValidation.validateSupportingDocs(files);
    if (!validation.valid) {
      showError(validation.error);
      return;
    }
    
    // Check for duplicate file names
    const newFileNames = files.map(f => f.name);
    const existingFileNames = supportingDocsUploaded.map(f => f.filename || f.name);
    const duplicates = newFileNames.filter(name => existingFileNames.includes(name));
    
    if (duplicates.length > 0) {
      showError(`File(s) already uploaded: ${duplicates.join(', ')}`);
      return;
    }
    
    setSupportingDocs(files);
    setError(null);
  }

  async function loadSampleSupportingDocument() {
    console.log('[UploadPanel] Loading sample supporting document...');
    try {
      setError(null);
      const sampleFile = await samplesAPI.loadSampleSupportingDocument();
      console.log('[UploadPanel] Sample supporting document loaded:', sampleFile.name);
      handleSupportingDocsFileSelect([sampleFile]);
      showSuccess('Sample supporting document loaded! Click "Upload & Index" to proceed.');
    } catch (err) {
      console.error('[UploadPanel] Failed to load sample supporting document:', err);
      showError('Failed to load sample document: ' + getErrorMessage(err));
    }
  }

  function removeSupportingDoc(index) {
    setSupportingDocs((prev) => prev.filter((_, i) => i !== index));
  }

  async function uploadSupportingDocs() {
    console.log('[UploadPanel] uploadSupportingDocs called');
    console.log('[UploadPanel] Session ID:', sessionId);
    console.log('[UploadPanel] Files:', supportingDocs);
    
    if (supportingDocs.length === 0 || !sessionId) {
      console.warn('[UploadPanel] No files or session ID');
      return;
    }

    try {
      setSupportingDocsUploading(true);
      setSupportingDocsProgress(0);
      setError(null);
      console.log('[UploadPanel] Starting supporting docs upload...');

      const result = await uploadAPI.uploadSupportingDocs(
        sessionId,
        supportingDocs,
        (progress) => {
          console.log('[UploadPanel] Upload progress:', progress);
          setSupportingDocsProgress(progress);
        }
      );

      console.log('[UploadPanel] Upload result:', result);
      
      // Check if any files were uploaded successfully (uploaded_count > 0)
      if (result.uploaded_count > 0) {
        setSupportingDocsUploaded((prev) => [...prev, ...result.files.filter(f => f.uploaded)]);
        setSupportingDocs([]);
        showSuccess(
          `${result.uploaded_count} document(s) uploaded! ${result.total_chunks} total chunks indexed.`
        );
        
        console.log('[UploadPanel] Notifying parent with supporting-docs event');
        if (onUploadComplete) {
          onUploadComplete('supporting-docs', { ...result, session_id: sessionId });
        }
      } else {
        console.error('[UploadPanel] Upload failed - uploaded_count is 0');
        showError('Failed to upload supporting documents');
      }
    } catch (err) {
      console.error('[UploadPanel] Upload error:', err);
      showError('Failed to upload supporting documents: ' + getErrorMessage(err));
    } finally {
      setSupportingDocsUploading(false);
      setSupportingDocsProgress(0);
    }
  }

  // Toast notifications
  function showError(message) {
    setError(message);
    setSuccess(null);
    setTimeout(() => setError(null), 5000);
  }

  function showSuccess(message) {
    setSuccess(message);
    setError(null);
    setTimeout(() => setSuccess(null), 5000);
  }

  if (sessionLoading) {
    return (
      <div className="upload-panel loading">
        <div className="spinner"></div>
        <p>Initializing session...</p>
      </div>
    );
  }

  return (
    <div className="upload-panel">
      {/* Toast Notifications */}
      {error && (
        <div className="toast toast-error">
          <span className="toast-icon">⚠️</span>
          <span className="toast-message">{error}</span>
          <button className="toast-close" onClick={() => setError(null)}>
            ×
          </button>
        </div>
      )}
      {success && (
        <div className="toast toast-success">
          <span className="toast-icon">✓</span>
          <span className="toast-message">{success}</span>
          <button className="toast-close" onClick={() => setSuccess(null)}>
            ×
          </button>
        </div>
      )}

      {/* Header */}
      <div className="upload-header">
        <h2>📁 Upload Documents</h2>
        <div className="quota-display">
          <span className="quota-label">Storage:</span>
          <span className="quota-value">
            {(quota.used_mb || 0).toFixed(1)} / {quota.max_mb || 50} MB
          </span>
          <div className="quota-bar">
            <div
              className="quota-fill"
              style={{ width: `${((quota.used_mb || 0) / (quota.max_mb || 50)) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Funding Call Upload */}
      <div className="upload-section">
        <h3>1. Funding Call (Required)</h3>
        <p className="upload-description">
          Upload the funding call PDF to extract requirements
        </p>

        {/* Insert Example Button */}
        {!fundingCallUploaded && !fundingCallFile && (
          <button 
            className="example-button"
            onClick={loadSampleFundingCall}
            style={{
              marginBottom: '12px',
              padding: '8px 16px',
              backgroundColor: '#f0f9ff',
              border: '1px solid #0ea5e9',
              borderRadius: '6px',
              color: '#0369a1',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = '#e0f2fe';
              e.target.style.borderColor = '#0284c7';
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = '#f0f9ff';
              e.target.style.borderColor = '#0ea5e9';
            }}
          >
            📄 Insert Example Funding Call
          </button>
        )}

        {!fundingCallUploaded ? (
          <div
            className={`dropzone ${dragActive ? 'drag-active' : ''} ${
              fundingCallFile ? 'has-file' : ''
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={(e) => handleDrop(e, 'funding-call')}
          >
            <input
              type="file"
              id="funding-call-input"
              accept="application/pdf"
              onChange={(e) =>
                e.target.files[0] &&
                handleFundingCallFileSelect(e.target.files[0])
              }
              style={{ display: 'none' }}
            />

            {fundingCallFile ? (
              <div className="file-preview">
                <div className="file-icon">📄</div>
                <div className="file-info">
                  <div className="file-name">{fundingCallFile.name}</div>
                  <div className="file-size">
                    {formatFileSize(fundingCallFile.size)}
                  </div>
                </div>
                <button
                  className="file-remove"
                  onClick={() => setFundingCallFile(null)}
                  disabled={fundingCallUploading}
                >
                  ×
                </button>
              </div>
            ) : (
              <label htmlFor="funding-call-input" className="dropzone-label">
                <div className="dropzone-icon">📄</div>
                <div className="dropzone-text">
                  Drag & drop PDF here, or <span className="link">browse</span>
                </div>
                <div className="dropzone-hint">Maximum 10 MB</div>
              </label>
            )}

            {fundingCallUploading && (
              <div className="upload-progress">
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${fundingCallProgress}%` }}
                  ></div>
                </div>
                <div className="progress-text">
                  {fundingCallProgress < 100
                    ? `Uploading... ${fundingCallProgress}%`
                    : 'Indexing document...'}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="upload-success">
            <div className="success-icon">✓</div>
            <div className="success-message">
              <strong>Funding call uploaded!</strong>
              <br />
              {fundingCallChunks} chunks indexed
            </div>
          </div>
        )}

        {fundingCallFile && !fundingCallUploaded && !fundingCallUploading && (
          <button className="upload-button" onClick={uploadFundingCall}>
            Upload & Index Funding Call
          </button>
        )}
      </div>

      {/* Supporting Documents Upload */}
      <div className="upload-section">
        <h3>2. Supporting Documents (Optional)</h3>
        <p className="upload-description">
          Upload community documents for context (max 5 files, 50MB total)
        </p>

        {/* Insert Example Button */}
        {supportingDocs.length === 0 && supportingDocsUploaded.length < 5 && (
          <button 
            className="example-button"
            onClick={loadSampleSupportingDocument}
            style={{
              marginBottom: '12px',
              padding: '8px 16px',
              backgroundColor: '#f0fdf4',
              border: '1px solid #10b981',
              borderRadius: '6px',
              color: '#047857',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = '#dcfce7';
              e.target.style.borderColor = '#059669';
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = '#f0fdf4';
              e.target.style.borderColor = '#10b981';
            }}
          >
            📚 Insert Example Supporting Document
          </button>
        )}

        <div className="file-count-display">
          <span>
            {supportingDocsUploaded.length + supportingDocs.length} / 5 files
          </span>
          <span>
            {(quota.used_mb || 0).toFixed(1)} / {quota.max_mb || 50} MB used
          </span>
        </div>

        {supportingDocs.length === 0 &&
        supportingDocsUploaded.length < 5 &&
        quota.remaining_mb > 0 ? (
          <div
            className={`dropzone ${dragActive ? 'drag-active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={(e) => handleDrop(e, 'supporting-docs')}
          >
            <input
              type="file"
              id="supporting-docs-input"
              accept="application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              multiple
              onChange={(e) =>
                e.target.files.length > 0 &&
                handleSupportingDocsFileSelect(Array.from(e.target.files))
              }
              style={{ display: 'none' }}
            />

            <label htmlFor="supporting-docs-input" className="dropzone-label">
              <div className="dropzone-icon">📚</div>
              <div className="dropzone-text">
                Drag & drop PDF/DOCX here, or <span className="link">browse</span>
              </div>
              <div className="dropzone-hint">
                Max {5 - supportingDocsUploaded.length} files, 10MB each
              </div>
            </label>
          </div>
        ) : null}

        {/* Selected files list */}
        {supportingDocs.length > 0 && (
          <div className="file-list">
            <h4>Selected Files:</h4>
            {supportingDocs.map((file, index) => (
              <div key={index} className="file-item">
                <div className="file-icon">
                  {file.type === 'application/pdf' ? '📄' : '📝'}
                </div>
                <div className="file-info">
                  <div className="file-name">{file.name}</div>
                  <div className="file-size">{formatFileSize(file.size)}</div>
                </div>
                <button
                  className="file-remove"
                  onClick={() => removeSupportingDoc(index)}
                  disabled={supportingDocsUploading}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}

        {supportingDocsUploading && (
          <div className="upload-progress">
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${supportingDocsProgress}%` }}
              ></div>
            </div>
            <div className="progress-text">
              {supportingDocsProgress < 100
                ? `Uploading... ${supportingDocsProgress}%`
                : 'Indexing documents...'}
            </div>
          </div>
        )}

        {supportingDocs.length > 0 && !supportingDocsUploading && (
          <button className="upload-button" onClick={uploadSupportingDocs}>
            Upload & Index {supportingDocs.length} Document
            {supportingDocs.length > 1 ? 's' : ''}
          </button>
        )}

        {/* Uploaded files summary */}
        {supportingDocsUploaded.length > 0 && (
          <div className="uploaded-summary">
            <h4>Uploaded Documents ({supportingDocsUploaded.length}):</h4>
            {supportingDocsUploaded.map((doc, index) => (
              <div key={index} className="uploaded-item">
                <span className="uploaded-icon">✓</span>
                <span className="uploaded-name">{doc.filename}</span>
                <span className="uploaded-chunks">{doc.chunk_count} chunks</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
