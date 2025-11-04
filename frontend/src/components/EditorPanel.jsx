/* EditorPanel.jsx - Section editor with inline citations and word count */

import { useState, useEffect } from 'react';
import './EditorPanel.css';

// Get API base URL from environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function EditorPanel({ sessionId, selectedSection, generatedSections, onSectionGenerated, onCitationClick }) {
  const [generatedText, setGeneratedText] = useState('');
  const [wordCount, setWordCount] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);
  const [warning, setWarning] = useState(null);
  const [citations, setCitations] = useState([]);
  const [selectedCitation, setSelectedCitation] = useState(null);
  const [lockedParagraphs, setLockedParagraphs] = useState([]);
  const [selectedParagraph, setSelectedParagraph] = useState(null);
  const [isRegenerating, setIsRegenerating] = useState(false);

  // Load section when selected changes OR when it gets generated
  useEffect(() => {
    console.log('[EditorPanel] ========================================');
    console.log('[EditorPanel] useEffect triggered - selectedSection changed');
    console.log('[EditorPanel] sessionId:', sessionId);
    console.log('[EditorPanel] selectedSection:', selectedSection);
    console.log('[EditorPanel] selectedSection.name:', selectedSection?.name);
    
    // Check if this section has been generated
    const sectionData = selectedSection ? generatedSections?.[selectedSection.name] : null;
    console.log('[EditorPanel] Section in generatedSections?', !!sectionData);
    console.log('[EditorPanel] ========================================');
    
    if (sessionId && selectedSection) {
      // If section is in generatedSections, use that data directly
      if (sectionData) {
        console.log('[EditorPanel] Loading from generatedSections (already generated)');
        setGeneratedText(sectionData.text);
        setWordCount(sectionData.word_count);
        setWarning(sectionData.warning);
        setCitations(sectionData.citations || []);
        setLockedParagraphs(sectionData.locked_paragraphs || []);
      } else {
        console.log('[EditorPanel] Not in generatedSections, calling loadSection()...');
        loadSection();
      }
    } else {
      console.log('[EditorPanel] No section selected, clearing editor');
      // Clear if no section selected
      setGeneratedText('');
      setWordCount(0);
      setWarning(null);
      setCitations([]);
      setLockedParagraphs([]);
      setSelectedParagraph(null);
    }
  }, [sessionId, selectedSection, generatedSections]);

  // Load existing section data if already generated
  const loadSection = async () => {
    console.log('[EditorPanel] ========================================');
    console.log('[EditorPanel] loadSection() called');
    console.log('[EditorPanel] sessionId:', sessionId);
    console.log('[EditorPanel] selectedSection.name:', selectedSection?.name);
    console.log('[EditorPanel] Fetching from:', `${API_BASE_URL}/api/sections/${sessionId}/${selectedSection.name}`);
    
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/sections/${sessionId}/${selectedSection.name}`
      );
      
      console.log('[EditorPanel] Response status:', response.status);
      console.log('[EditorPanel] Response ok:', response.ok);
      
      if (response.ok) {
        const data = await response.json();
        console.log('[EditorPanel] Section data loaded:', data);
        console.log('[EditorPanel] Text length:', data.text?.length);
        console.log('[EditorPanel] Word count:', data.word_count);
        console.log('[EditorPanel] Citations count:', data.citations?.length);
        
        setGeneratedText(data.text);
        setWordCount(data.word_count);
        setWarning(data.warning);
        setCitations(data.citations || []);
        setLockedParagraphs(data.locked_paragraphs || []);
        
        // Notify parent that section was loaded with citations
        if (onSectionGenerated && data.citations) {
          console.log('[EditorPanel] Notifying parent with onSectionGenerated');
          onSectionGenerated(selectedSection.name, data);
        }
        
        console.log('[EditorPanel] Section loaded successfully');
      } else {
        console.log('[EditorPanel] Section not found (404), ready for generation');
      }
    } catch (err) {
      console.log('[EditorPanel] No existing section data, ready for generation');
      console.log('[EditorPanel] Error:', err);
      // Clear citations if no data
      setCitations([]);
      setLockedParagraphs([]);
    }
    
    console.log('[EditorPanel] ========================================');
  };

  useEffect(() => {
    // Update word count as user edits
    const words = generatedText.trim().split(/\s+/).filter(w => w.length > 0);
    setWordCount(words.length);
  }, [generatedText]);

  const handleTextClick = (e) => {
    // Get cursor position and find citations in the text
    const textarea = e.target;
    const cursorPos = textarea.selectionStart;
    const text = textarea.value;
    
    // Find if cursor is on a citation
    const citationPattern = /\[([^\]]+),\s*p\.(\d+)\]/g;
    let match;
    
    while ((match = citationPattern.exec(text)) !== null) {
      const startPos = match.index;
      const endPos = match.index + match[0].length;
      
      if (cursorPos >= startPos && cursorPos <= endPos) {
        // Find matching citation
        const docTitle = match[1];
        const pageNum = parseInt(match[2]);
        
        const citation = citations.find(c =>
          c.document_title === docTitle && c.page_number === pageNum
        );
        
        if (citation) {
          handleCitationClick(citation);
        }
        break;
      }
    }
  };

  // Extract unique citations from the text
  const extractCitationsFromText = () => {
    if (!generatedText) return [];
    
    const citationPattern = /\[([^\]]+),\s*p\.(\d+)\]/g;
    const foundCitations = [];
    let match;
    
    while ((match = citationPattern.exec(generatedText)) !== null) {
      const docTitle = match[1];
      const pageNum = parseInt(match[2]);
      
      const citation = citations.find(c =>
        c.document_title.toLowerCase().includes(docTitle.toLowerCase()) &&
        c.page_number === pageNum
      );
      
      if (citation && !foundCitations.some(fc => 
        fc.document_title === citation.document_title && 
        fc.page_number === citation.page_number
      )) {
        foundCitations.push(citation);
      }
    }
    
    return foundCitations;
  };

  // Split text into paragraphs
  const splitIntoParagraphs = (text) => {
    if (!text) return [];
    return text.split('\n\n').map(p => p.trim()).filter(p => p.length > 0);
  };

  // Handle paragraph selection for locking
  const handleParagraphClick = (index) => {
    setSelectedParagraph(index);
  };

  // Lock the selected paragraph
  const handleLockParagraph = async (index) => {
    if (index === null || index === undefined) return;
    
    // Toggle lock
    let newLockedParagraphs;
    if (lockedParagraphs.includes(index)) {
      // Unlock
      newLockedParagraphs = lockedParagraphs.filter(i => i !== index);
    } else {
      // Lock
      newLockedParagraphs = [...lockedParagraphs, index];
    }
    
    setLockedParagraphs(newLockedParagraphs);
    
    // Save to backend
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/sections/${sessionId}/${selectedSection.name}`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            text: generatedText,
            locked_paragraph_indices: newLockedParagraphs
          })
        }
      );
      
      if (!response.ok) {
        console.error('[EditorPanel] Failed to save locked paragraphs');
      } else {
        console.log(`[EditorPanel] Paragraph ${index} lock updated`);
      }
    } catch (err) {
      console.error('[EditorPanel] Error saving locked paragraphs:', err);
    }
  };

  // Handle regenerate with locked paragraphs
  const handleRegenerate = async () => {
    if (!sessionId || !selectedSection) return;

    console.log(`[EditorPanel] Regenerating section: ${selectedSection.name}`);
    console.log(`[EditorPanel] Locked paragraphs: ${lockedParagraphs}`);
    
    setIsRegenerating(true);
    setWarning(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/sections/${sessionId}/${selectedSection.name}/regenerate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            section_requirements: `Write a ${selectedSection.format || 'narrative'} section for ${selectedSection.name}`,
            word_limit: selectedSection.word_limit,
            char_limit: selectedSection.char_limit,
            format_type: selectedSection.format || 'narrative'
          })
        }
      );
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Regeneration failed');
      }

      const result = await response.json();
      console.log(`[EditorPanel] Regenerated ${result.word_count} words, ${lockedParagraphs.length} paragraphs preserved`);

      setGeneratedText(result.text);
      setWordCount(result.word_count);
      setWarning(result.warning);
      setCitations(result.citations);
      setLockedParagraphs(result.locked_paragraphs || lockedParagraphs);

      // Notify parent
      if (onSectionGenerated) {
        onSectionGenerated(selectedSection.name, result);
      }

    } catch (error) {
      console.error('[EditorPanel] Regeneration failed:', error);
      setWarning(`Regeneration failed: ${error.message}`);
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleGenerate = async () => {
    if (!sessionId || !selectedSection) return;

    console.log(`[EditorPanel] Generating section: ${selectedSection.name}`);
    console.log(`[EditorPanel] Session ID: ${sessionId}`);
    
    const requestBody = {
      session_id: sessionId,
      section_name: selectedSection.name,
      section_requirements: `Write a ${selectedSection.format || 'narrative'} section for ${selectedSection.name}`,
      word_limit: selectedSection.word_limit,
      char_limit: selectedSection.char_limit,
      format_type: selectedSection.format || 'narrative'
    };
    
    console.log(`[EditorPanel] Request body:`, requestBody);
    
    setIsGenerating(true);
    setWarning(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/sections/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });
      
      console.log(`[EditorPanel] Response status: ${response.status}`);

      if (!response.ok) {
        const error = await response.json();
        console.error(`[EditorPanel] Error response:`, error);
        throw new Error(error.detail || 'Generation failed');
      }

      const result = await response.json();
      console.log('[EditorPanel] ========================================');
      console.log('[EditorPanel] Generation result received');
      console.log('[EditorPanel] Word count:', result.word_count);
      console.log('[EditorPanel] Has citations?', !!result.citations);
      console.log('[EditorPanel] Citations count:', result.citations?.length);
      console.log('[EditorPanel] Citations data:', result.citations);
      console.log('[EditorPanel] Full result:', result);
      console.log('[EditorPanel] result.text:', result.text);
      console.log('[EditorPanel] result.text type:', typeof result.text);
      console.log('[EditorPanel] result.text length:', result.text?.length);
      console.log('[EditorPanel] result.text is undefined?', result.text === undefined);
      console.log('[EditorPanel] result.text is null?', result.text === null);
      console.log('[EditorPanel] result.text is empty string?', result.text === '');
      console.log('[EditorPanel] ========================================');

      if (!result.text) {
        console.error('[EditorPanel] WARNING: result.text is falsy!', result.text);
        console.error('[EditorPanel] This might be why nothing is displaying');
      }

      setGeneratedText(result.text || '');
      setWordCount(result.word_count);
      setWarning(result.warning);
      setCitations(result.citations);

      // Notify parent that section was generated
      if (onSectionGenerated) {
        console.log('[EditorPanel] Calling onSectionGenerated with:', {
          sectionName: selectedSection.name,
          result: result
        });
        onSectionGenerated(selectedSection.name, result);
      } else {
        console.warn('[EditorPanel] onSectionGenerated callback not provided!');
      }

    } catch (error) {
      console.error('[EditorPanel] Generation failed:', error);
      setWarning(`Generation failed: ${error.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCitationClick = (citation) => {
    setSelectedCitation(citation);
    if (onCitationClick) {
      onCitationClick(citation);
    }
  };

  const renderTextWithCitations = () => {
    if (!generatedText) return null;

    // Split text by citation pattern [Document, p.N]
    const citationPattern = /\[([^\]]+),\s*p\.(\d+)\]/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = citationPattern.exec(generatedText)) !== null) {
      // Add text before citation
      if (match.index > lastIndex) {
        parts.push({
          type: 'text',
          content: generatedText.substring(lastIndex, match.index)
        });
      }

      // Add citation
      parts.push({
        type: 'citation',
        content: match[0],
        doc_title: match[1],
        page: parseInt(match[2])
      });

      lastIndex = match.index + match[0].length;
    }

    // Add remaining text
    if (lastIndex < generatedText.length) {
      parts.push({
        type: 'text',
        content: generatedText.substring(lastIndex)
      });
    }

    return (
      <div className="rendered-text">
        {parts.map((part, index) => (
          part.type === 'citation' ? (
            <span
              key={index}
              className="inline-citation"
              onClick={() => {
                const citation = citations.find(c =>
                  c.document_title.toLowerCase().includes(part.doc_title.toLowerCase()) &&
                  c.page_number === part.page
                );
                if (citation) handleCitationClick(citation);
              }}
              title="Click to see source"
            >
              {part.content}
            </span>
          ) : (
            <span key={index}>{part.content}</span>
          )
        ))}
      </div>
    );
  };

  const getWordCountClass = () => {
    if (!selectedSection || !selectedSection.word_limit) return '';
    const percentage = (wordCount / selectedSection.word_limit) * 100;
    if (percentage > 100) return 'over-limit';
    if (percentage > 90) return 'near-limit';
    return '';
  };

  if (!selectedSection) {
    return (
      <div className="editor-panel">
        <div className="no-section-message">
          <p>Select a section from the checklist to generate content</p>
        </div>
      </div>
    );
  }

  return (
    <div className="editor-panel">
      <div className="editor-header">
        <h2>{selectedSection.name}</h2>
        {selectedSection.word_limit && (
          <div className={`word-count ${getWordCountClass()}`}>
            {wordCount} / {selectedSection.word_limit} words
          </div>
        )}
      </div>

      <div className="editor-toolbar">
        <button
          onClick={handleGenerate}
          disabled={isGenerating || isRegenerating}
          className="generate-button"
        >
          {isGenerating ? '⏳ Generating...' : '✨ Generate'}
        </button>
        {generatedText && (
          <button
            className="regenerate-button"
            onClick={handleRegenerate}
            disabled={isGenerating || isRegenerating}
            title={lockedParagraphs.length > 0 ? `Regenerate (keeps ${lockedParagraphs.length} locked paragraph${lockedParagraphs.length > 1 ? 's' : ''})` : 'Regenerate section'}
          >
            {isRegenerating ? '⏳ Regenerating...' : '🔄 Regenerate'}
            {lockedParagraphs.length > 0 && (
              <span className="lock-count"> (🔒 {lockedParagraphs.length})</span>
            )}
          </button>
        )}
      </div>

      {warning && (
        <div className={`warning-message ${warning.includes('exceeds') ? 'error' : 'warning'}`}>
          ⚠️ {warning}
        </div>
      )}

      {generatedText ? (
        <div className="editor-content">
          <div className="editable-view">
            <textarea
              value={generatedText}
              onChange={(e) => setGeneratedText(e.target.value)}
              onClick={handleTextClick}
              placeholder="Generated text will appear here..."
              className="section-textarea"
            />
            
            {/* Paragraph lock controls */}
            {splitIntoParagraphs(generatedText).length > 0 && (
              <div className="paragraph-controls">
                <h4>🔒 Paragraph Controls</h4>
                <p className="controls-hint">
                  Lock paragraphs to preserve them during regeneration. Locked paragraphs will have a yellow background.
                </p>
                <div className="paragraph-list">
                  {splitIntoParagraphs(generatedText).map((para, idx) => (
                    <div
                      key={idx}
                      className={`paragraph-item ${lockedParagraphs.includes(idx) ? 'locked' : ''} ${selectedParagraph === idx ? 'selected' : ''}`}
                      onClick={() => handleParagraphClick(idx)}
                    >
                      <div className="paragraph-preview">
                        <span className="paragraph-number">¶{idx + 1}</span>
                        <span className="paragraph-text">
                          {para.substring(0, 80)}{para.length > 80 ? '...' : ''}
                        </span>
                      </div>
                      <button
                        className={`lock-button ${lockedParagraphs.includes(idx) ? 'locked' : ''}`}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleLockParagraph(idx);
                        }}
                        title={lockedParagraphs.includes(idx) ? 'Click to unlock' : 'Click to lock'}
                      >
                        {lockedParagraphs.includes(idx) ? '🔒 Locked' : '🔓 Lock'}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Show clickable citation references */}
            {citations.length > 0 && (
              <div className="citations-reference">
                <h4>📚 In-text Citations (click to view details):</h4>
                <div className="citation-badges">
                  {extractCitationsFromText().map((citation, idx) => (
                    <button
                      key={`${citation.document_title}-${citation.page_number}-${idx}`}
                      className="citation-badge"
                      onClick={() => handleCitationClick(citation)}
                      title="Click to view source details"
                    >
                      {citation.document_title}, p.{citation.page_number}
                    </button>
                  ))}
                </div>
              </div>
            )}
            
            <div className="citation-hint">
              💡 In-text citations verify that information is grounded in your uploaded documents. 
              Detailed source information can be found in the Sources panel below. 
              Note: The exported DOCX will not include inline citations.
            </div>
          </div>
        </div>
      ) : (
        <div className="empty-state">
          <p>Click "Generate" to create content for this section using your uploaded documents.</p>
        </div>
      )}

      {selectedCitation && (
        <div className="citation-popup" onClick={() => setSelectedCitation(null)}>
          <div className="citation-card" onClick={(e) => e.stopPropagation()}>
            <button className="close-button" onClick={() => setSelectedCitation(null)}>×</button>
            <h3>Source Citation</h3>
            <p><strong>Document:</strong> {selectedCitation.document_title}</p>
            <p><strong>Page:</strong> {selectedCitation.page_number}</p>
            <p><strong>Relevance:</strong> {(selectedCitation.relevance_score * 100).toFixed(0)}%</p>
            <div className="citation-snippet">
              <strong>Excerpt:</strong>
              <p>{selectedCitation.chunk_text}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default EditorPanel;
