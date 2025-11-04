# Debugging Guide - Upload Flow Issues

## Overview

This guide helps debug issues with the upload flow, particularly:
1. ChecklistPanel not showing after funding call upload
2. Progress bars not visible
3. Duplicate file uploads
4. Session propagation issues

## Logging Added

### Backend Logging

All backend logs are prefixed with tags for easy filtering:

- `[SESSION CREATE]` - Session creation endpoint
- `[FUNDING UPLOAD]` - Funding call upload endpoint
- `[SUPPORTING UPLOAD]` - Supporting docs upload endpoint
- `[STATUS]` - Upload status endpoint
- `[MIDDLEWARE]` - Session validation middleware
- `[REQUIREMENTS]` - Requirements extraction endpoint

### Frontend Logging

All frontend logs are prefixed with component names:

- `[App]` - Main App component
- `[UploadPanel]` - Upload panel component
- `[ChecklistPanel]` - Checklist panel component (if you add logging there)

## How to Use Logs

### 1. Start Backend with Logging

The backend will now output detailed logs for every request:

```bash
cd c:\Users\hello\Documents\Projects\EasyGrant
uvicorn backend.src.main:app --reload
```

### 2. Start Frontend with Dev Tools Open

```bash
cd c:\Users\hello\Documents\Projects\EasyGrant\frontend
npm run dev
```

Open browser dev tools (F12) and keep the Console tab open.

### 3. Perform Upload Test

1. Upload a funding call PDF
2. Upload a supporting document

### 4. Collect Logs

#### Backend Logs (Terminal)

Look for the sequence:

```
INFO:     127.0.0.1:xxxxx - "POST /api/session/create HTTP/1.1" 200 OK
[MIDDLEWARE] Request: POST /api/upload/funding-call
[MIDDLEWARE] Found session_id in headers: <session_id>
[MIDDLEWARE] Session validated: <session_id>
[FUNDING UPLOAD] Received request - Session ID: <session_id>, Filename: <filename>
[FUNDING UPLOAD] File size: <bytes> bytes
[FUNDING UPLOAD] Validation passed
[FUNDING UPLOAD] File saved - ID: <file_id>, Path: <path>
[FUNDING UPLOAD] Session updated - funding_call_uploaded: True
[FUNDING UPLOAD] Starting indexing...
[FUNDING UPLOAD] Indexing complete - Success: True, Chunks: <count>
[FUNDING UPLOAD] Success - returning response with quota: {...}
```

#### Frontend Logs (Browser Console)

Look for the sequence:

```javascript
[UploadPanel] Component mounted, initializing session...
[UploadPanel] initializeSession called
[UploadPanel] Calling sessionAPI.createSession()...
[UploadPanel] Session created: {session_id: "..."}
[UploadPanel] Notifying parent with session-created event, session_id: ...
[App] handleUploadComplete called - Type: session-created, Data: {session_id: "..."}
[App] Setting sessionId from session-created event: ...

[UploadPanel] uploadFundingCall called
[UploadPanel] Session ID: ...
[UploadPanel] File: File {...}
[UploadPanel] Starting funding call upload...
[UploadPanel] Upload result: {...}
[UploadPanel] Notifying parent with funding-call event
[App] handleUploadComplete called - Type: funding-call, Data: {...}
[App] Setting sessionId from funding-call event: ...
[App] Funding call uploaded, setting fundingCallUploaded to true
[App] Current state - sessionId: ..., fundingCallUploaded: true
```

## Common Issues and What to Look For

### Issue 1: ChecklistPanel Not Showing

**Expected Flow:**
1. Session created → `[App]` sets `sessionId`
2. Funding call uploaded → `[App]` sets `fundingCallUploaded = true`
3. ChecklistPanel renders when both are true

**Check:**
- Does `[App]` log show both `sessionId` and `fundingCallUploaded` set to true?
- Does `[UploadPanel]` call `onUploadComplete('funding-call', ...)` with valid `session_id`?
- Does backend `[FUNDING UPLOAD]` show `funding_call_uploaded: True`?

**Possible Causes:**
- Session ID not propagated from upload events
- `onUploadComplete` callback not passed or not called
- State update timing issues

### Issue 2: No Progress Bar Visible

**Expected Flow:**
1. Upload starts → `setFundingCallUploading(true)` → progress bar shows
2. Progress callbacks → `setFundingCallProgress(0-100)`
3. Upload completes → `setFundingCallUploading(false)` → progress bar hides

**Check:**
- Does `[UploadPanel]` log show "Upload progress:" messages?
- Is the upload completing too fast (< 1 second)?

**Possible Causes:**
- Upload completes before progress UI renders (file too small)
- Progress callback not being called
- CSS hiding the progress bar

### Issue 3: Duplicate File Uploads

**Expected Flow:**
1. User selects file
2. `handleSupportingDocsFileSelect` checks if filename already in `supportingDocsUploaded`
3. If duplicate → show error, return early
4. If new → add to `supportingDocs` array

**Check:**
- Does `[UploadPanel]` log show the duplicate check code running?
- What is the value of `supportingDocsUploaded` before the check?

**Possible Causes:**
- Duplicate check code not running
- `supportingDocsUploaded` not updated after upload
- Filenames not matching due to encoding issues

### Issue 4: Session Not Found (404)

**Expected Flow:**
1. Frontend creates session
2. Frontend stores `session_id` in state
3. Frontend passes `session_id` in header or query param for all requests
4. Backend middleware validates session exists

**Check:**
- Does `[MIDDLEWARE]` log show the session_id being extracted?
- Does `[MIDDLEWARE]` log show "Session validated" or "Session not found"?
- Does frontend include session_id in the request?

**Possible Causes:**
- Session ID not being sent in requests
- Session expired or cleared from backend
- Multiple sessions being created

## Debugging Workflow

### Step 1: Verify Session Creation

1. Refresh the page
2. Check browser console for:
   ```
   [UploadPanel] Session created: {session_id: "..."}
   [App] Setting sessionId from session-created event: ...
   ```
3. Check backend terminal for:
   ```
   INFO:     127.0.0.1:xxxxx - "POST /api/session/create HTTP/1.1" 200 OK
   ```

### Step 2: Verify Funding Call Upload

1. Upload a PDF
2. Check browser console for:
   ```
   [UploadPanel] uploadFundingCall called
   [UploadPanel] Upload result: {...}
   [App] Funding call uploaded, setting fundingCallUploaded to true
   ```
3. Check backend terminal for:
   ```
   [FUNDING UPLOAD] Success - returning response with quota: {...}
   ```

### Step 3: Verify ChecklistPanel Appearance

1. After funding call upload completes
2. Check browser console for:
   ```
   [App] Current state - sessionId: <id>, fundingCallUploaded: true
   ```
3. Look in the DOM - does `<div class="checklist-section">` exist?
4. If yes but not visible → CSS issue
5. If no → React state issue

### Step 4: Verify Supporting Docs Upload

1. Upload a DOCX/PDF supporting doc
2. Check browser console for:
   ```
   [UploadPanel] uploadSupportingDocs called
   [UploadPanel] Upload result: {...}
   ```
3. Check backend terminal for:
   ```
   [SUPPORTING UPLOAD] Success - Uploaded: 1, Failed: 0, Chunks: ...
   ```

## Collecting Logs for Bug Report

When reporting an issue, provide:

### 1. Backend Logs

Copy everything from the backend terminal from when you:
- Start the server
- Refresh the page (session creation)
- Upload funding call
- Upload supporting docs

### 2. Frontend Console Logs

In browser dev tools Console tab:
- Right-click → "Save as..."
- Or copy all logs with `[App]` and `[UploadPanel]` prefixes

### 3. Network Tab

In browser dev tools Network tab:
- Filter by "api"
- For each failed request, copy:
  - Request URL
  - Request Headers (especially `X-Session-ID`)
  - Request Payload
  - Response Status
  - Response Body

### 4. React DevTools (Optional)

If you have React DevTools installed:
- Inspect `<App>` component
- Check state: `sessionId`, `fundingCallUploaded`
- Inspect `<UploadPanel>` component
- Check state: `sessionId`, `fundingCallUploaded`, `supportingDocsUploaded`

## Next Steps After Collecting Logs

Once you have the logs, look for:

1. **Missing logs** - If a log message is missing, that code path didn't run
2. **Error messages** - Any `console.error` or `ERROR:` in logs
3. **State mismatches** - Frontend thinks session exists, backend says 404
4. **Timing issues** - State updated but UI didn't re-render
5. **Data format issues** - `session_id: undefined` or similar

Share the logs and the specific issue observed, and we can debug further!
