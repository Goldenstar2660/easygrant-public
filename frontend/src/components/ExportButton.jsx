/**
 * ExportButton Component
 * 
 * Allows users to download generated proposal as DOCX.
 * Shows loading state during export generation.
 */

import { useState } from 'react';
import PropTypes from 'prop-types';
import { exportProposal } from '../services/api';
import './ExportButton.css';

export default function ExportButton({ sessionId, disabled = false }) {
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState(null);

  async function handleExport() {
    if (!sessionId || disabled) {
      return;
    }

    setIsExporting(true);
    setError(null);

    try {
      console.log('[ExportButton] Starting export for session:', sessionId);
      
      // Call export API
      const blob = await exportProposal(sessionId);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Set filename with timestamp
      const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '');
      link.download = `Proposal_${timestamp}.docx`;
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('[ExportButton] Export successful');
    } catch (err) {
      console.error('[ExportButton] Export failed:', err);
      setError(err.message || 'Failed to export proposal');
    } finally {
      setIsExporting(false);
    }
  }

  return (
    <div className="export-button-container">
      <button
        className={`export-button ${disabled ? 'disabled' : ''} ${isExporting ? 'loading' : ''}`}
        onClick={handleExport}
        disabled={disabled || isExporting}
        title={disabled ? 'Generate at least one section to export' : 'Download proposal as DOCX'}
      >
        {isExporting ? (
          <>
            <span className="export-spinner"></span>
            <span>Generating DOCX...</span>
          </>
        ) : (
          <>
            <span className="export-icon">📄</span>
            <span>Export DOCX</span>
          </>
        )}
      </button>
      
      {error && (
        <div className="export-error">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}

ExportButton.propTypes = {
  sessionId: PropTypes.string,
  disabled: PropTypes.bool
};
