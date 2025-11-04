# Sample PDFs for Demo

This folder contains example PDF files for demonstrating EasyGrant functionality to hackathon judges and testers.

## Files

- **Sample_Funding_Call.pdf** - Example funding call document for testing requirements extraction
- **Sample_Supporting_Document.pdf** - Example supporting document for testing context retrieval

## Usage

These files are served via the `/api/samples/` endpoints and can be loaded with one click using the "Insert Example PDF" buttons in the upload panel:

- 📄 **Insert Example Funding Call** - Loads the sample funding call
- 📚 **Insert Example Supporting Document** - Loads the sample supporting document

The buttons automatically:
1. Fetch the PDF from the backend
2. Convert it to a File object
3. Load it into the upload UI
4. Validate it like a real user upload

This makes it easy for judges to test the full application flow without needing to find their own PDFs.

## API Endpoints

- `GET /api/samples/funding-call` - Returns Sample_Funding_Call.pdf
- `GET /api/samples/supporting-document` - Returns Sample_Supporting_Document.pdf

These endpoints do NOT require session authentication (exempted in middleware).
