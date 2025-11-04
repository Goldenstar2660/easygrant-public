# Bug Fix: API Response Field Mismatch

## Issue Identified

Based on the logs provided, the root cause was found:

### Problem
The frontend upload functions were checking for `result.success` but the backend API returns different field names:
- **Funding call API** returns: `{ "uploaded": true, "indexed": true, ... }`
- **Supporting docs API** returns: `{ "uploaded_count": 1, "failed_count": 0, ... }`

Neither API returns a `success` field, so the `if (result.success)` check always failed, preventing:
1. State updates (`setFundingCallUploaded(true)`)
2. Parent notification (`onUploadComplete` callback)
3. ChecklistPanel from appearing

### Evidence from Logs

**Browser Console:**
```
[App] Current state - sessionId: null, fundingCallUploaded: false
```
- No upload logs after initial session creation
- `onUploadComplete` was never called

**Network Tab:**
```json
{
  "uploaded": true,
  "indexed": true,
  "file_id": "...",
  "chunk_count": 3,
  ...
}
```
- Backend successfully uploaded and indexed files
- But frontend didn't process the response correctly

## Changes Made

### 1. Fixed Funding Call Upload Check

**File:** `frontend/src/components/UploadPanel.jsx`

**Before:**
```javascript
if (result.success) {
  setFundingCallUploaded(true);
  // ...
}
```

**After:**
```javascript
if (result.uploaded) {  // Changed from result.success
  setFundingCallUploaded(true);
  // ...
}
```

### 2. Fixed Supporting Docs Upload Check

**Before:**
```javascript
if (result.success) {
  setSupportingDocsUploaded((prev) => [...prev, ...result.files]);
  // ...
}
```

**After:**
```javascript
if (result.uploaded_count > 0) {  // Changed from result.success
  setSupportingDocsUploaded((prev) => [...prev, ...result.files.filter(f => f.uploaded)]);
  // ...
}
```

Also added `.filter(f => f.uploaded)` to only add successfully uploaded files.

### 3. Added Comprehensive Logging

Added console.log statements to:
- `uploadFundingCall()` - Log function call, session ID, file, upload start, result, parent notification
- `uploadSupportingDocs()` - Same logging as funding call
- Both functions now log errors with full details

### 4. Fixed React StrictMode Double Mounting

**Before:**
```javascript
useEffect(() => {
  initializeSession();
}, []);
```

**After:**
```javascript
useEffect(() => {
  console.log('[UploadPanel] useEffect called, sessionId:', sessionId);
  if (!sessionId) {  // Prevent double initialization
    initializeSession();
  }
}, []); // eslint-disable-line react-hooks/exhaustive-deps
```

This prevents creating two sessions in development mode.

## Testing

After these changes, the upload flow should work as follows:

### 1. Session Creation
```
[UploadPanel] useEffect called, sessionId: null
[UploadPanel] initializeSession called
[UploadPanel] Session created: {session_id: "..."}
[App] Setting sessionId from session-created event: ...
```

### 2. Funding Call Upload
```
[UploadPanel] uploadFundingCall called
[UploadPanel] Session ID: <session_id>
[UploadPanel] Starting funding call upload...
[UploadPanel] Upload result: {uploaded: true, indexed: true, ...}
[UploadPanel] Notifying parent with funding-call event
[App] handleUploadComplete called - Type: funding-call
[App] Funding call uploaded, setting fundingCallUploaded to true
```

### 3. ChecklistPanel Appears
Once both `sessionId` and `fundingCallUploaded` are true, the ChecklistPanel should render.

## Expected Network Responses

### Funding Call Upload Response
```json
{
  "uploaded": true,      // ✅ Now checking this field
  "indexed": true,
  "file_id": "...",
  "filename": "...",
  "size": "...",
  "chunk_count": 3,
  "quota": { ... }
}
```

### Supporting Docs Upload Response
```json
{
  "uploaded_count": 1,   // ✅ Now checking this field
  "failed_count": 0,
  "total_chunks": 0,
  "files": [
    {
      "filename": "...",
      "uploaded": true,    // ✅ Now filtering by this
      "file_id": "...",
      "size": "...",
      "indexed": false,
      "chunk_count": 0
    }
  ],
  "quota": { ... }
}
```

## Next Steps

1. **Refresh the browser** - Vite should auto-reload
2. **Test the upload flow**:
   - Upload a funding call PDF
   - Verify ChecklistPanel appears
   - Upload a supporting document
   - Verify it's added to the list
3. **Check console logs** - Should now see upload function logs
4. **Verify state** - `[App]` should show both sessionId and fundingCallUploaded as true

## Secondary Issue Found

**Session ID Mismatch:**
The backend logs showed:
```
[MIDDLEWARE] Session not found: 5bbb7926-1ea1-4ca0-8724-96d756f2e830
```

But the frontend created session ID:
```
19f0ed2a-862e-4cbd-bf67-dda14e2a95a8
```

This was likely from:
1. React StrictMode creating two sessions
2. Frontend using one session ID while backend had a different one
3. Some requests going to the wrong session

The `if (!sessionId)` check in useEffect should fix this.
