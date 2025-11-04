/**
 * Main App Component
 * EasyGrant Smart Proposal Assistant
 */

import { useState } from 'react';
import UploadPanel from './components/UploadPanel';
import ChecklistPanel from './components/ChecklistPanel';
import EditorPanel from './components/EditorPanel';
import SourcesPanel from './components/SourcesPanel';
import ExportButton from './components/ExportButton';
import './App.css';

export default function App() {
  const [sessionId, setSessionId] = useState(null);
  const [fundingCallUploaded, setFundingCallUploaded] = useState(false);
  const [selectedSection, setSelectedSection] = useState(null);
  const [generatedSections, setGeneratedSections] = useState({});
  const [highlightedCitation, setHighlightedCitation] = useState(null);

  function handleUploadComplete(type, data) {
    console.log(`[App] handleUploadComplete called - Type: ${type}, Data:`, data);
    
    // Set sessionId when session is created or from any upload
    if (data.session_id) {
      console.log(`[App] Setting sessionId from ${type} event: ${data.session_id}`);
      setSessionId(prevId => {
        console.log(`[App] sessionId updated from ${prevId} to ${data.session_id}`);
        return data.session_id;
      });
    } else {
      console.warn(`[App] No session_id in ${type} event data`);
    }
    
    // Track funding call upload specifically to show ChecklistPanel
    if (type === 'funding-call') {
      console.log('[App] Funding call uploaded, setting fundingCallUploaded to true');
      setFundingCallUploaded(prevState => {
        console.log(`[App] fundingCallUploaded updated from ${prevState} to true`);
        return true;
      });
    }
  }

  function handleSectionSelect(section) {
    console.log('[App] ========================================');
    console.log('[App] handleSectionSelect called');
    console.log('[App] Section:', section);
    console.log('[App] Section name:', section?.name);
    console.log('[App] Previous selectedSection:', selectedSection);
    console.log('[App] Current generatedSections keys:', Object.keys(generatedSections));
    console.log('[App] Is this section already generated?', 
      section?.name && generatedSections[section.name] ? 'YES' : 'NO'
    );
    console.log('[App] ========================================');
    setSelectedSection(section);
  }

  function handleSectionGenerated(sectionName, data) {
    console.log('[App] ========================================');
    console.log('[App] handleSectionGenerated called');
    console.log('[App] Section name:', sectionName);
    console.log('[App] Data received:', data);
    console.log('[App] Previous generatedSections:', Object.keys(generatedSections));
    console.log('[App] ========================================');
    setGeneratedSections(prev => {
      const updated = {
        ...prev,
        [sectionName]: data
      };
      console.log('[App] Updated generatedSections keys:', Object.keys(updated));
      return updated;
    });
  }

  function handleCitationClick(citation) {
    console.log('[App] Citation clicked:', citation);
    setHighlightedCitation(citation);
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-title">
            <h1>EasyGrant Smart Proposal Assistant</h1>
            <p className="app-subtitle">
              Upload funding call + supporting docs → Generate grant proposal
            </p>
          </div>
          {sessionId && Object.keys(generatedSections).length > 0 && (
            <div className="header-actions">
              <ExportButton 
                sessionId={sessionId}
                disabled={Object.keys(generatedSections).length === 0}
              />
            </div>
          )}
        </div>
      </header>

      <main className="app-main">
        <UploadPanel onUploadComplete={handleUploadComplete} />

        {fundingCallUploaded && sessionId && (
          <div className="workspace">
            <div className="workspace-panel checklist-column">
              <ChecklistPanel 
                sessionId={sessionId}
                onSectionSelect={handleSectionSelect}
                onSectionGenerated={handleSectionGenerated}
                selectedSection={selectedSection}
              />
            </div>
            
            <div className="workspace-panel editor-column">
              <EditorPanel 
                sessionId={sessionId}
                selectedSection={selectedSection}
                generatedSections={generatedSections}
                onSectionGenerated={handleSectionGenerated}
                onCitationClick={handleCitationClick}
              />
            </div>
            
            <div className="workspace-panel sources-column">
              <SourcesPanel 
                citations={(() => {
                  const sectionName = selectedSection?.name;
                  const sectionData = generatedSections[sectionName];
                  const citations = sectionData?.citations || [];
                  
                  console.log('[App] SourcesPanel citations calculation:');
                  console.log('[App]   selectedSection:', selectedSection);
                  console.log('[App]   selectedSection.name:', sectionName);
                  console.log('[App]   generatedSections keys:', Object.keys(generatedSections));
                  console.log('[App]   sectionData:', sectionData);
                  console.log('[App]   citations:', citations);
                  console.log('[App]   citations length:', citations?.length);
                  
                  return citations;
                })()}
                highlightedCitationId={highlightedCitation}
                onCitationClick={handleCitationClick}
              />
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>
          Built for small and remote communities • Open source • Privacy-first
        </p>
      </footer>
    </div>
  );
}
