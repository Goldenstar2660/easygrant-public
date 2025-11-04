/**
 * API Client for EasyGrant Backend
 * 
 * Axios wrappers for upload, session, and requirements endpoints
 */

import axios from 'axios';

// Base API URL (from environment or default to localhost)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60s timeout for large file uploads
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Session API
 */

export const sessionAPI = {
  /**
   * Create a new session
   * @returns {Promise<{session_id: string, created_at: string, quota: object}>}
   */
  async createSession() {
    const response = await apiClient.post('/api/session/create');
    return response.data;
  },

  /**
   * Get session details
   * @param {string} sessionId - Session ID
   * @returns {Promise<object>}
   */
  async getSession(sessionId) {
    const response = await apiClient.get(`/api/session/${sessionId}`);
    return response.data;
  },
};

/**
 * Upload API
 */

export const uploadAPI = {
  /**
   * Upload funding call PDF
   * @param {string} sessionId - Session ID
   * @param {File} file - PDF file to upload
   * @param {function} onProgress - Progress callback (0-100)
   * @returns {Promise<{success: boolean, message: string, file_id: string, chunk_count: number}>}
   */
  async uploadFundingCall(sessionId, file, onProgress = null) {
    const formData = new FormData();
    formData.append('file', file);

    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
        'X-Session-ID': sessionId,
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    };

    const response = await apiClient.post(
      '/api/upload/funding-call',
      formData,
      config
    );
    return response.data;
  },

  /**
   * Upload supporting documents
   * @param {string} sessionId - Session ID
   * @param {File[]} files - Array of PDF/DOCX files (max 5)
   * @param {function} onProgress - Progress callback (0-100)
   * @returns {Promise<{success: boolean, files: Array, total_chunks: number}>}
   */
  async uploadSupportingDocs(sessionId, files, onProgress = null) {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
        'X-Session-ID': sessionId,
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    };

    const response = await apiClient.post(
      '/api/upload/supporting-docs',
      formData,
      config
    );
    return response.data;
  },

  /**
   * Get upload status and quota
   * @param {string} sessionId - Session ID
   * @returns {Promise<{quota: object, files: Array}>}
   */
  async getUploadStatus(sessionId) {
    const response = await apiClient.get('/api/upload/status', {
      headers: {
        'X-Session-ID': sessionId,
      },
    });
    return response.data;
  },
};

/**
 * Error handling utility
 * @param {Error} error - Axios error
 * @returns {string} User-friendly error message
 */
export function getErrorMessage(error) {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    
    if (status === 400) {
      return data.detail || 'Invalid request. Please check your input.';
    } else if (status === 413) {
      return 'File too large. Maximum size is 10MB per file.';
    } else if (status === 422) {
      return 'Validation error. Please check file type and size.';
    } else if (status === 500) {
      return 'Server error. Please try again later.';
    }
    
    return data.detail || `Error: ${status}`;
  } else if (error.request) {
    // Request made but no response
    return 'Network error. Please check your connection.';
  } else {
    // Something else went wrong
    return error.message || 'An unexpected error occurred.';
  }
}

/**
 * File validation utilities (client-side)
 */

export const fileValidation = {
  /**
   * Validate file type
   * @param {File} file - File to validate
   * @param {string[]} allowedTypes - Allowed MIME types
   * @returns {{valid: boolean, error: string|null}}
   */
  validateFileType(file, allowedTypes) {
    if (!allowedTypes.includes(file.type)) {
      return {
        valid: false,
        error: `Invalid file type. Allowed: ${allowedTypes.join(', ')}`,
      };
    }
    return { valid: true, error: null };
  },

  /**
   * Validate file size
   * @param {File} file - File to validate
   * @param {number} maxSizeMB - Maximum size in MB
   * @returns {{valid: boolean, error: string|null}}
   */
  validateFileSize(file, maxSizeMB) {
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      return {
        valid: false,
        error: `File too large. Maximum size: ${maxSizeMB}MB (got ${(
          file.size /
          1024 /
          1024
        ).toFixed(1)}MB)`,
      };
    }
    return { valid: true, error: null };
  },

  /**
   * Validate funding call PDF
   * @param {File} file - File to validate
   * @returns {{valid: boolean, error: string|null}}
   */
  validateFundingCall(file) {
    // Check type
    if (file.type !== 'application/pdf') {
      return {
        valid: false,
        error: 'Funding call must be a PDF file',
      };
    }

    // Check size (10MB max)
    const sizeCheck = this.validateFileSize(file, 10);
    if (!sizeCheck.valid) {
      return sizeCheck;
    }

    return { valid: true, error: null };
  },

  /**
   * Validate supporting document
   * @param {File} file - File to validate
   * @returns {{valid: boolean, error: string|null}}
   */
  validateSupportingDoc(file) {
    // Check type (PDF or DOCX)
    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ];
    
    const typeCheck = this.validateFileType(file, allowedTypes);
    if (!typeCheck.valid) {
      return {
        valid: false,
        error: 'Supporting documents must be PDF or DOCX files',
      };
    }

    // Check size (10MB max per file)
    const sizeCheck = this.validateFileSize(file, 10);
    if (!sizeCheck.valid) {
      return sizeCheck;
    }

    return { valid: true, error: null };
  },

  /**
   * Validate multiple supporting documents
   * @param {File[]} files - Files to validate
   * @returns {{valid: boolean, error: string|null}}
   */
  validateSupportingDocs(files) {
    // Check count (max 5)
    if (files.length > 5) {
      return {
        valid: false,
        error: 'Maximum 5 supporting documents allowed',
      };
    }

    // Check total size (50MB max)
    const totalSize = files.reduce((sum, file) => sum + file.size, 0);
    const totalSizeMB = totalSize / 1024 / 1024;
    if (totalSizeMB > 50) {
      return {
        valid: false,
        error: `Total size exceeds 50MB limit (got ${totalSizeMB.toFixed(1)}MB)`,
      };
    }

    // Validate each file
    for (const file of files) {
      const fileCheck = this.validateSupportingDoc(file);
      if (!fileCheck.valid) {
        return fileCheck;
      }
    }

    return { valid: true, error: null };
  },
};

/**
 * Format file size for display
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted size (e.g., "5.2 MB")
 */
export function formatFileSize(bytes) {
  if (bytes < 1024) {
    return `${bytes} B`;
  } else if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  } else {
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  }
}

/**
 * Requirements API
 */

export const requirementsAPI = {
  /**
   * Get requirements blueprint from funding call
   * @param {string} sessionId - Session ID
   * @returns {Promise<{sections: Array, eligibility: Array, scoring_criteria: object}>}
   */
  async getRequirements(sessionId) {
    const response = await apiClient.get(`/api/requirements/${sessionId}`);
    return response.data;
  },

  /**
   * Get requirements summary
   * @param {string} sessionId - Session ID
   * @returns {Promise<{summary: string, total_sections: number, required_sections: number}>}
   */
  async getRequirementsSummary(sessionId) {
    const response = await apiClient.get(`/api/requirements/${sessionId}/summary`);
    return response.data;
  },
};

/**
 * Generation API (placeholder for Phase 5)
 */

export const generationAPI = {
  /**
   * Generate section content using RAG
   * @param {string} sessionId - Session ID
   * @param {string} sectionName - Section name to generate
   * @param {object} params - Additional parameters (requirements, limits, etc.)
   * @returns {Promise<object>} Generated section with text and citations
   */
  async generateSection(sessionId, sectionName, params = {}) {
    console.log('[generationAPI] generateSection called');
    console.log('[generationAPI] sessionId:', sessionId);
    console.log('[generationAPI] sectionName:', sectionName);
    console.log('[generationAPI] params:', params);
    
    const requestBody = {
      session_id: sessionId,
      section_name: sectionName,
      section_requirements: params.requirements || `Write a ${params.format || 'narrative'} section for ${sectionName}`,
      word_limit: params.word_limit,
      char_limit: params.char_limit,
      format_type: params.format || 'narrative'
    };
    
    console.log('[generationAPI] Request body:', requestBody);
    
    const response = await fetch(`${API_BASE_URL}/api/sections/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });
    
    console.log('[generationAPI] Response status:', response.status);

    if (!response.ok) {
      const error = await response.json();
      console.error('[generationAPI] Error response:', error);
      throw new Error(error.detail || 'Section generation failed');
    }

    const result = await response.json();
    console.log('[generationAPI] Success response:', result);
    console.log('[generationAPI] Response has citations?', !!result.citations);
    console.log('[generationAPI] Citations count:', result.citations?.length);
    console.log('[generationAPI] Citations data:', result.citations);
    return result;
  },
};

/**
 * Export API
 */

export const exportAPI = {
  /**
   * Export proposal as DOCX
   * @param {string} sessionId - Session ID
   * @param {object} params - Export parameters (section_names, program_name)
   * @returns {Promise<Blob>} DOCX file blob
   */
  async exportDOCX(sessionId, params = {}) {
    console.log('[exportAPI] exportDOCX called');
    console.log('[exportAPI] sessionId:', sessionId);
    console.log('[exportAPI] params:', params);
    
    const requestBody = {
      session_id: sessionId,
      section_names: params.section_names || null,
      program_name: params.program_name || null
    };
    
    console.log('[exportAPI] Request body:', requestBody);
    
    const response = await fetch(`${API_BASE_URL}/api/export/docx`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });
    
    console.log('[exportAPI] Response status:', response.status);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Export failed' }));
      console.error('[exportAPI] Error response:', error);
      throw new Error(error.detail || 'DOCX export failed');
    }

    const blob = await response.blob();
    console.log('[exportAPI] Export successful, blob size:', blob.size);
    return blob;
  },
};

/**
 * Samples API - Load demo PDFs for hackathon judges
 */

export const samplesAPI = {
  /**
   * Load sample funding call PDF
   * @returns {Promise<File>} File object with sample PDF
   */
  async loadSampleFundingCall() {
    const response = await apiClient.get('/api/samples/funding-call', {
      responseType: 'blob',
    });
    
    // Convert blob to File object
    const file = new File([response.data], 'Sample_Funding_Call.pdf', {
      type: 'application/pdf',
    });
    
    return file;
  },

  /**
   * Load sample supporting document PDF
   * @returns {Promise<File>} File object with sample PDF
   */
  async loadSampleSupportingDocument() {
    const response = await apiClient.get('/api/samples/supporting-document', {
      responseType: 'blob',
    });
    
    // Convert blob to File object
    const file = new File([response.data], 'Sample_Supporting_Document.pdf', {
      type: 'application/pdf',
    });
    
    return file;
  },
};

// Named exports for convenience
export const getRequirements = (sessionId) => requirementsAPI.getRequirements(sessionId);
export const getRequirementsSummary = (sessionId) => requirementsAPI.getRequirementsSummary(sessionId);
export const generateSection = (sessionId, sectionName) => generationAPI.generateSection(sessionId, sectionName);
export const exportProposal = (sessionId, params = {}) => exportAPI.exportDOCX(sessionId, params);

export default {
  sessionAPI,
  uploadAPI,
  requirementsAPI,
  generationAPI,
  exportAPI,
  samplesAPI,
  getErrorMessage,
  fileValidation,
  formatFileSize,
};
