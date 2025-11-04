import React from 'react';
import './SourcesPanel.css';

/**
 * SourcesPanel Component
 * 
 * Displays retrieved source citations that support the generated section.
 * Shows document title, page number, relevance score, and text snippet.
 * Citations can be highlighted when clicked in the editor.
 * 
 * Props:
 * - citations: Array of citation objects from generation response
 * - highlightedCitationId: ID of currently highlighted citation (from editor click)
 * - onCitationClick: Callback when citation is clicked in panel
 */
export default function SourcesPanel({ 
  citations = [], 
  highlightedCitationId = null,
  onCitationClick = null
}) {
  console.log('[SourcesPanel] ========================================');
  console.log('[SourcesPanel] Component rendered');
  console.log('[SourcesPanel] citations prop:', citations);
  console.log('[SourcesPanel] citations type:', typeof citations);
  console.log('[SourcesPanel] citations is array?', Array.isArray(citations));
  console.log('[SourcesPanel] citations length:', citations?.length);
  console.log('[SourcesPanel] highlightedCitationId:', highlightedCitationId);
  console.log('[SourcesPanel] ========================================');
  
  if (!citations || citations.length === 0) {
    console.log('[SourcesPanel] No citations - showing empty state');
    return (
      <div className="sources-panel">
        <div className="sources-header">
          <h2>Sources</h2>
          <div className="citation-count">0 sources</div>
        </div>
        <div className="empty-sources">
          <p>No sources yet.</p>
          <p className="hint">Sources will appear here after generating a section.</p>
        </div>
      </div>
    );
  }
  
  console.log('[SourcesPanel] Rendering', citations.length, 'citations');

  // Helper to calculate relevance percentage
  const getRelevancePercentage = (score) => {
    return Math.round(score * 100);
  };

  // Helper to get relevance badge class
  const getRelevanceBadgeClass = (score) => {
    if (score >= 0.7) return 'high';
    if (score >= 0.5) return 'medium';
    return 'low';
  };

  return (
    <div className="sources-panel">
      <div className="sources-header">
        <h2>Sources</h2>
        <div className="citation-count">
          {citations.length} {citations.length === 1 ? 'source' : 'sources'}
        </div>
      </div>

      <div className="sources-list">
        {citations.map((citation, index) => {
          const isHighlighted = highlightedCitationId && 
            citation.document_title === highlightedCitationId.document_title &&
            citation.page_number === highlightedCitationId.page_number;
          
          const relevancePercent = getRelevancePercentage(citation.relevance_score);
          const relevanceClass = getRelevanceBadgeClass(citation.relevance_score);

          return (
            <div 
              key={`${citation.document_title}-${citation.page_number}-${index}`}
              className={`source-card ${isHighlighted ? 'highlighted' : ''}`}
              onClick={() => onCitationClick && onCitationClick(citation)}
            >
              <div className="source-header">
                <div className="source-number">#{index + 1}</div>
                <div className={`relevance-badge ${relevanceClass}`}>
                  {relevancePercent}% relevant
                </div>
              </div>

              <h3 className="source-title">{citation.document_title}</h3>
              
              <div className="source-meta">
                <span className="page-indicator">Page {citation.page_number}</span>
              </div>

              <div className="source-snippet">
                <p>{citation.chunk_text}</p>
              </div>

              {isHighlighted && (
                <div className="highlight-indicator">
                  <span>● Currently viewing</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="sources-footer">
        <p className="usage-hint">
          💡 Click citations in the editor to highlight sources
        </p>
      </div>
    </div>
  );
}
