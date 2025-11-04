/**
 * ChecklistPanel Component
 * 
 * Displays extracted requirements from funding call as an interactive checklist.
 * Shows sections, word limits, and "Generate" buttons for each section.
 */

import React, { useState, useEffect } from 'react';
import { 
  getRequirements, 
  getRequirementsSummary,
  generateSection 
} from '../services/api';
import './ChecklistPanel.css';

const ChecklistPanel = ({ sessionId, onSectionSelect, onSectionGenerated, selectedSection }) => {
  const [blueprint, setBlueprint] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [generatingSection, setGeneratingSection] = useState(null);
  const [sectionStatus, setSectionStatus] = useState({});

  // Load requirements on mount
  useEffect(() => {
    console.log('[ChecklistPanel] useEffect called, sessionId:', sessionId);
    if (sessionId) {
      loadRequirements();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  const loadRequirements = async () => {
    console.log('[ChecklistPanel] loadRequirements called for session:', sessionId);
    setLoading(true);
    setError(null);
    
    try {
      console.log('[ChecklistPanel] Fetching requirements and summary...');
      // Get blueprint and summary in parallel
      const [blueprintData, summaryData] = await Promise.all([
        getRequirements(sessionId),
        getRequirementsSummary(sessionId)
      ]);
      
      console.log('[ChecklistPanel] Blueprint data:', blueprintData);
      console.log('[ChecklistPanel] Summary data:', summaryData);
      
      setBlueprint(blueprintData);
      setSummary(summaryData);
      
      // Initialize section status (all not started)
      const initialStatus = {};
      if (blueprintData && blueprintData.sections && Array.isArray(blueprintData.sections)) {
        blueprintData.sections.forEach(section => {
          initialStatus[section.name] = 'not-started';
        });
      }
      setSectionStatus(initialStatus);
      console.log('[ChecklistPanel] Requirements loaded successfully');
      
    } catch (err) {
      console.error('[ChecklistPanel] Error loading requirements:', err);
      if (err.response?.status === 404) {
        setError('No funding call uploaded. Please upload a funding call PDF first.');
      } else {
        setError(err.message || 'Failed to load requirements');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (section) => {
    console.log('[ChecklistPanel] ========================================');
    console.log('[ChecklistPanel] handleGenerate called');
    console.log('[ChecklistPanel] Section name:', section.name);
    console.log('[ChecklistPanel] Current status:', sectionStatus[section.name]);
    console.log('[ChecklistPanel] selectedSection:', selectedSection);
    console.log('[ChecklistPanel] ========================================');
    
    // If section is already completed, just view it (don't regenerate)
    if (sectionStatus[section.name] === 'completed') {
      console.log('[ChecklistPanel] Section already completed - switching to VIEW mode');
      if (onSectionSelect) {
        onSectionSelect(section);
      }
      return;
    }
    
    // Select the section first so user sees it in EditorPanel
    if (onSectionSelect) {
      console.log('[ChecklistPanel] Calling onSectionSelect');
      onSectionSelect(section);
    }
    
    // Mark as generating
    console.log('[ChecklistPanel] Setting status to "generating"');
    setGeneratingSection(section.name);
    setSectionStatus(prev => ({
      ...prev,
      [section.name]: 'generating'
    }));
    
    try {
      console.log('[ChecklistPanel] Calling generateSection API...');
      const result = await generateSection(sessionId, section.name);
      console.log('[ChecklistPanel] Generation successful!', result);
      
      // Mark as completed
      console.log('[ChecklistPanel] Setting status to "completed"');
      setSectionStatus(prev => ({
        ...prev,
        [section.name]: 'completed'
      }));
      
      // Notify parent (App.jsx) with the generated section data
      console.log('[ChecklistPanel] Notifying parent with onSectionGenerated');
      if (onSectionGenerated) {
        onSectionGenerated(section.name, result);
      }
      
    } catch (err) {
      console.error('[ChecklistPanel] Generation failed:', err);
      setSectionStatus(prev => ({
        ...prev,
        [section.name]: 'error'
      }));
    } finally {
      console.log('[ChecklistPanel] Clearing generatingSection state');
      setGeneratingSection(null);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'generating':
        return '🔄';
      case 'error':
        return '❌';
      default:
        return '⚪';
    }
  };

  const formatLimit = (section) => {
    if (section.word_limit) {
      return `${section.word_limit} words max`;
    } else if (section.char_limit) {
      return `${section.char_limit} characters max`;
    }
    return 'No limit specified';
  };

  if (loading) {
    return (
      <div className="checklist-panel">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Extracting requirements from funding call...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="checklist-panel">
        <div className="error-state">
          <p className="error-message">{error}</p>
          {sessionId && (
            <button onClick={loadRequirements} className="retry-button">
              Retry
            </button>
          )}
        </div>
      </div>
    );
  }

  if (!blueprint) {
    return (
      <div className="checklist-panel">
        <div className="empty-state">
          <p>No requirements extracted yet.</p>
          <p className="hint">Upload a funding call PDF to see requirements.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="checklist-panel">
      <div className="checklist-header">
        <h2>Proposal Requirements</h2>
        {summary && (
          <div className="summary-stats">
            <span className="stat">
              {summary.total_sections} sections
            </span>
            <span className="stat required">
              {summary.required_sections} required
            </span>
            {summary.optional_sections > 0 && (
              <span className="stat optional">
                {summary.optional_sections} optional
              </span>
            )}
          </div>
        )}
      </div>

      {/* Eligibility criteria */}
      {blueprint.eligibility && blueprint.eligibility.length > 0 && (
        <div className="eligibility-section">
          <h3>Eligibility Requirements</h3>
          <ul className="eligibility-list">
            {blueprint.eligibility.map((criteria, idx) => (
              <li key={idx}>{criteria}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Section checklist */}
      <div className="sections-list">
        <h3>Proposal Sections</h3>
        
        {/* Required sections */}
        <div className="section-group">
          <h4 className="group-title">Required Sections</h4>
          {blueprint.sections
            .filter(s => s.required)
            .map((section, idx) => (
              <div key={idx} className="section-item required-section">
                <div className="section-info">
                  <div className="section-header">
                    <span className="status-icon">
                      {getStatusIcon(sectionStatus[section.name])}
                    </span>
                    <span className="section-name">{section.name}</span>
                    {section.scoring_weight && (
                      <span className="scoring-weight">
                        {section.scoring_weight}%
                      </span>
                    )}
                  </div>
                  <div className="section-details">
                    <span className="word-limit">{formatLimit(section)}</span>
                    <span className="format-type">{section.format}</span>
                  </div>
                </div>
                <button
                  className="generate-button"
                  onClick={() => {
                    console.log('[ChecklistPanel] BUTTON CLICKED (required section)');
                    console.log('[ChecklistPanel] Button text would be:', 
                      sectionStatus[section.name] === 'completed' 
                        ? 'View' 
                        : generatingSection === section.name 
                          ? 'Generating...' 
                          : 'Generate'
                    );
                    handleGenerate(section);
                  }}
                  disabled={generatingSection === section.name}
                >
                  {sectionStatus[section.name] === 'completed' 
                    ? 'View' 
                    : generatingSection === section.name 
                      ? 'Generating...' 
                      : 'Generate'}
                </button>
              </div>
            ))}
        </div>

        {/* Optional sections */}
        {blueprint.sections.some(s => !s.required) && (
          <div className="section-group">
            <h4 className="group-title">Optional Sections</h4>
            {blueprint.sections
              .filter(s => !s.required)
              .map((section, idx) => (
                <div key={idx} className="section-item optional-section">
                  <div className="section-info">
                    <div className="section-header">
                      <span className="status-icon">
                        {getStatusIcon(sectionStatus[section.name])}
                      </span>
                      <span className="section-name">{section.name}</span>
                      {section.scoring_weight && (
                        <span className="scoring-weight">
                          {section.scoring_weight}%
                        </span>
                      )}
                    </div>
                    <div className="section-details">
                      <span className="word-limit">{formatLimit(section)}</span>
                      <span className="format-type">{section.format}</span>
                    </div>
                  </div>
                  <button
                    className="generate-button"
                    onClick={() => {
                      console.log('[ChecklistPanel] BUTTON CLICKED (optional section)');
                      console.log('[ChecklistPanel] Button text would be:', 
                        sectionStatus[section.name] === 'completed' 
                          ? 'View' 
                          : generatingSection === section.name 
                            ? 'Generating...' 
                            : 'Generate'
                      );
                      handleGenerate(section);
                    }}
                    disabled={generatingSection === section.name}
                  >
                    {sectionStatus[section.name] === 'completed' 
                      ? 'View' 
                      : generatingSection === section.name 
                        ? 'Generating...' 
                        : 'Generate'}
                  </button>
                </div>
              ))}
          </div>
        )}
      </div>

      {/* Deadline notice */}
      {blueprint.deadline && (
        <div className="deadline-notice">
          <strong>Deadline:</strong> {blueprint.deadline}
        </div>
      )}
    </div>
  );
};

export default ChecklistPanel;
