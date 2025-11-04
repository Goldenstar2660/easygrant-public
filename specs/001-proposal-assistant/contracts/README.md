# API Contracts: Smart Proposal Assistant

**Feature**: 001-proposal-assistant  
**Generated**: 2025-10-26  
**OpenAPI Version**: 3.0.3

## Overview

This directory contains API contracts for the Smart Proposal Assistant backend. All endpoints are RESTful, use JSON payloads (except file uploads), and follow standard HTTP status codes.

## Contract Files

- **`openapi.yaml`**: Complete OpenAPI 3.0 specification with all endpoints, request/response schemas, and validation rules

## Base URLs

- **Local Development**: `http://localhost:8000`
- **Production (Render)**: `https://easygrant.onrender.com`

## Endpoint Summary

### Upload Endpoints

| Method | Path | Purpose | Max Size |
|--------|------|---------|----------|
| POST | `/api/upload/funding-call` | Upload funding call PDF | 10MB |
| POST | `/api/upload/supporting-docs` | Upload 1-5 context docs | 50MB total |

### Requirements Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/requirements/{session_id}` | Get extracted requirements checklist |

### Section Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/sections/generate` | Generate section draft with citations |
| GET | `/api/sections/{section_id}` | Get section details |
| PATCH | `/api/sections/{section_id}` | Update section (user edits) |
| POST | `/api/sections/{section_id}/regenerate` | Regenerate section (keep edits) |
| POST | `/api/sections/{section_id}/lock` | Lock section (prevent regen) |

### Export Endpoints

| Method | Path | Purpose | Response Type |
|--------|------|---------|---------------|
| POST | `/api/export/docx` | Export proposal as DOCX | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |

### Data Management Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| DELETE | `/api/data/{session_id}` | Delete all session data (one-click) |

## Request/Response Patterns

### Standard Success Response
```json
{
  "session_id": "uuid",
  "...": "resource-specific fields"
}
```

### Standard Error Response
```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE_CONSTANT",
  "details": {
    "field": "Additional context"
  }
}
```

## File Upload Format

All file uploads use `multipart/form-data`:

```http
POST /api/upload/funding-call
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="file"; filename="grant.pdf"
Content-Type: application/pdf

[binary PDF data]
--boundary
Content-Disposition: form-data; name="session_id"

uuid-string
--boundary--
```

## Citation Format

Citations in generated sections follow this structure:

**Inline (in text)**:
```
...our community faces broadband challenges [Strategic Plan 2024, p.5]...
```

**API Response**:
```json
{
  "citations": [
    {
      "citation_id": "cite_001",
      "position_in_text": 145,
      "document_id": "doc_uuid_123",
      "document_title": "Strategic Plan 2024",
      "page_number": 5,
      "chunk_text": "...our community lacks reliable internet...",
      "relevance_score": 0.87
    }
  ]
}
```

## Validation Rules

### Upload Limits
- Funding call PDF: ≤10MB, must be `.pdf`
- Supporting docs: ≤5 files, ≤50MB total, formats: `.pdf`, `.docx`, `.txt`

### Word Limits
- `GeneratedSection.word_count` validated against `SectionRequirement.word_limit`
- If exceeded: `limit_exceeded: true` in response
- Auto-retry with stricter prompt if first generation exceeds by >10%

### Session Management
- `session_id` generated on first upload if not provided
- All subsequent requests must include same `session_id`
- Session expires after 30 days of inactivity (auto-cleanup)

## Error Codes

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| `FILE_TOO_LARGE` | 400 | File exceeds size limit (10MB for funding call, 50MB total for supporting docs) |
| `INVALID_FILE_TYPE` | 400 | File type not supported (must be PDF, DOCX, or TXT) |
| `UPLOAD_QUOTA_EXCEEDED` | 400 | More than 5 supporting docs or >50MB total |
| `PARSING_FAILED` | 400 | Could not extract text from PDF (may be scanned/encrypted) |
| `EXTRACTION_FAILED` | 500 | Requirements extraction failed (LLM error) |
| `NO_CONTEXT_FOUND` | 400 | No relevant content in supporting docs for section |
| `WORD_LIMIT_EXCEEDED` | 400 | Generated section exceeds limit after max retries |
| `SESSION_NOT_FOUND` | 404 | Invalid or expired session_id |
| `SECTION_NOT_FOUND` | 404 | Invalid section_id |
| `SECTION_LOCKED` | 400 | Attempted to regenerate locked section |

## Rate Limiting

Not implemented in MVP. For production:
- Suggestion: 10 requests/minute per IP for generation endpoints
- File uploads: 5 uploads/minute per session

## Authentication

None required for demo. All endpoints are public. For production:
- Add JWT-based session tokens
- Implement per-user session isolation

## Testing

### Manual Testing
1. Import `openapi.yaml` into Postman or Insomnia
2. Set base URL to `http://localhost:8000` (dev) or production URL
3. Follow workflow:
   - Upload funding call → note `session_id` + `funding_call_id`
   - Upload supporting docs with `session_id`
   - GET requirements to see extracted sections
   - POST generate for first section
   - PATCH section with user edits
   - POST regenerate with `keep_edits: true`
   - POST export DOCX

### Contract Testing
- Use `pytest` with `httpx` client to test each endpoint
- Validate request/response against OpenAPI schema with `openapi-spec-validator`
- Test error cases (file too large, invalid session, etc.)

## OpenAPI Documentation

FastAPI auto-generates interactive docs:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Changelog

**v1.0.0** (2025-10-26):
- Initial API contract
- 10 endpoints covering full workflow
- OpenAPI 3.0 specification complete
