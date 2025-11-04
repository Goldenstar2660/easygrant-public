# 🧪 EasyGrant Tests

Test files for validating EasyGrant functionality across different phases.

## Test Files

### `run_phase2_tests.py`
Tests for Phase 2 functionality (Requirements Extraction).

**Runs tests for:**
- Funding call parsing
- Requirements extraction
- Section identification
- Eligibility criteria extraction

**Usage:**
```powershell
python tests\run_phase2_tests.py
```

### `test_phase3_backend.py`
Tests for Phase 3 functionality (RAG and Section Generation).

**Runs tests for:**
- Vector database operations
- Document chunking
- Embedding generation
- Context retrieval
- Section generation

**Usage:**
```powershell
python tests\test_phase3_backend.py
```

### `test_pd_embeddings.py`
Tests for embedding generation and vector similarity.

**Runs tests for:**
- Embedding model integration
- Vector similarity calculations
- Embedding dimensions
- Batch processing

**Usage:**
```powershell
python tests\test_pd_embeddings.py
```

## Running All Tests

### Using pytest (recommended)
```powershell
# Run all tests
pytest

# Run specific test file
pytest tests/run_phase2_tests.py

# Run with verbose output
pytest -v

# Run backend tests only
pytest backend/tests/
```

### Running individual test files
```powershell
python tests\run_phase2_tests.py
python tests\test_phase3_backend.py
python tests\test_pd_embeddings.py
```

## Test Documentation

For comprehensive testing guides, see:
- [Testing Guide](../docs/testing/TESTING_GUIDE.md) - Complete testing documentation
- [Test Checklist](../docs/testing/TEST_CHECKLIST.md) - Quick testing checklist
- [Testing Frontend](../docs/testing/TESTING_FRONTEND.md) - Frontend-specific tests

## Backend Unit Tests

Backend unit tests are located in `backend/tests/`:
- `backend/tests/test_phase4_requirements.py` - Phase 4 requirements tests

Run backend tests:
```powershell
cd backend
pytest tests/
```

---

**Note:** Make sure to activate your virtual environment before running tests:
```powershell
.\.venv\Scripts\Activate.ps1
```
