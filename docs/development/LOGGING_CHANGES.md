# Logging Implementation Summary

## Changes Made

Added comprehensive logging to help debug upload flow issues.

## Files Modified

### 1. Backend Files

#### `backend/src/api/routes/upload.py`
- Added `import logging` and `logger = logging.getLogger(__name__)`
- Added logs to `/funding-call` endpoint:
  - Log incoming request with session_id and filename
  - Log file size
  - Log validation status
  - Log file save location and ID
  - Log session update
  - Log indexing start/complete with chunk count
  - Log final response
- Added logs to `/supporting-docs` endpoint:
  - Log incoming request with file count and filenames
  - Log current supporting docs count
  - Log file count validation
  - Log each file processing
  - Log session update
  - Log indexing start/complete
  - Log final response with upload/fail counts
- Added logs to `/status` endpoint:
  - Log session ID in request
  - Log session details (funding_call_uploaded, file_count, total_size)
  - Log uploaded files count
  - Log index stats
  - Log quota

#### `backend/src/api/middleware.py`
- Added `import logging` and `logger = logging.getLogger(__name__)`
- Added logs to `session_validation_middleware`:
  - Log every incoming request (method + path)
  - Log skipped paths (health, docs, session creation)
  - Log where session_id was found (query, header, path)
  - Log when session_id is missing
  - Log when session doesn't exist
  - Log successful session validation

### 2. Frontend Files

#### `frontend/src/components/UploadPanel.jsx`
- Added logs to `initializeSession`:
  - Log function call
  - Log API call start
  - Log session creation response
  - Log parent notification
  - Log errors
- Added logs to `handleUploadComplete` (in App.jsx):
  - Log callback invocation with type and data
  - Log session_id extraction
  - Log state updates
  - Log current state after updates

#### `frontend/src/App.jsx`
- Enhanced `handleUploadComplete` logging:
  - Log callback type and full data object
  - Log session_id being set from each event type
  - Warn if no session_id in event data
  - Log when funding call upload flag is set
  - Log current state snapshot after each event

## Log Prefixes

All logs are prefixed for easy filtering:

### Backend
- `[SESSION CREATE]` - Session creation
- `[FUNDING UPLOAD]` - Funding call uploads
- `[SUPPORTING UPLOAD]` - Supporting doc uploads
- `[STATUS]` - Status endpoint
- `[MIDDLEWARE]` - Session validation
- `[REQUIREMENTS]` - Requirements extraction

### Frontend
- `[App]` - Main App component
- `[UploadPanel]` - Upload panel component

## How to Use

### 1. Restart Backend

The backend needs to be restarted for the logging changes to take effect:

```powershell
# Stop the current uvicorn process (Ctrl+C)
# Then restart:
cd c:\Users\hello\Documents\Projects\EasyGrant
uvicorn backend.src.main:app --reload
```

### 2. Refresh Frontend

The frontend should auto-reload via Vite HMR, but if not:

```powershell
# The server should already be running
# Just refresh your browser at http://localhost:5173
```

### 3. Test Upload Flow

1. Open browser dev tools (F12) → Console tab
2. Refresh the page to create a new session
3. Upload a funding call PDF
4. Upload a supporting document
5. Watch both:
   - **Browser console** for `[App]` and `[UploadPanel]` logs
   - **Terminal** for backend logs with `[FUNDING UPLOAD]`, etc.

### 4. Collect Logs

After testing, provide:

1. **Backend logs** from terminal (everything after starting uvicorn)
2. **Frontend logs** from browser console (filter by `[App]` and `[UploadPanel]`)
3. **Network tab** - any failed API requests

## Expected Log Flow

### Session Creation
```
Backend: INFO: 127.0.0.1:xxxxx - "POST /api/session/create HTTP/1.1" 200 OK
Frontend: [UploadPanel] Session created: {session_id: "..."}
Frontend: [App] Setting sessionId from session-created event: ...
```

### Funding Call Upload
```
Backend: [MIDDLEWARE] Request: POST /api/upload/funding-call
Backend: [MIDDLEWARE] Session validated: <session_id>
Backend: [FUNDING UPLOAD] Received request - Session ID: ..., Filename: ...
Backend: [FUNDING UPLOAD] File saved - ID: ..., Path: ...
Backend: [FUNDING UPLOAD] Success - returning response
Frontend: [UploadPanel] Upload result: {...}
Frontend: [App] Funding call uploaded, setting fundingCallUploaded to true
```

### Supporting Docs Upload
```
Backend: [SUPPORTING UPLOAD] Received request - Session ID: ..., File count: 1
Backend: [SUPPORTING UPLOAD] Success - Uploaded: 1, Failed: 0
Frontend: [UploadPanel] Upload result: {...}
Frontend: [App] handleUploadComplete called - Type: supporting-docs
```

### Status Check
```
Backend: [STATUS] Request for session: ...
Backend: [STATUS] Session details - funding_call_uploaded: True, file_count: 2
Backend: [STATUS] Quota: {...}
Frontend: [UploadPanel] Status data received: {...}
```

## Debugging Steps

See `DEBUGGING_GUIDE.md` for detailed debugging workflows and troubleshooting.

## Next Actions

1. **Restart the backend** to load the new logging code
2. **Refresh the browser** to reload the frontend
3. **Perform the upload test** (1 funding call + 1 supporting doc)
4. **Copy the logs** from both backend terminal and browser console
5. **Share the logs** so we can identify the root cause

The logs will show exactly where the flow is breaking down.
