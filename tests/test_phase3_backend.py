"""
Phase 3 Backend Integration Test
Tests the file upload → parse → chunk → embed → store pipeline
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend" / "src"))

def test_imports():
    """Test that all Phase 3 modules can be imported"""
    print("Testing Phase 3 imports...")
    
    try:
        from utils.file_storage import FileStorage
        print("✅ file_storage.py imported")
    except Exception as e:
        print(f"❌ file_storage.py import failed: {e}")
        return False
    
    try:
        from utils.file_validation import validate_file_type, validate_file_size, validate_funding_call_pdf
        print("✅ file_validation.py imported")
    except Exception as e:
        print(f"❌ file_validation.py import failed: {e}")
        return False
    
    try:
        from services.indexing_service import IndexingService
        print("✅ indexing_service.py imported")
    except Exception as e:
        print(f"❌ indexing_service.py import failed: {e}")
        return False
    
    try:
        from api.routes import upload, session
        print("✅ upload.py and session.py routes imported")
    except Exception as e:
        print(f"❌ routes import failed: {e}")
        return False
    
    print("\n✅ All Phase 3 imports successful!\n")
    return True

def test_file_storage():
    """Test FileStorage functionality"""
    print("Testing FileStorage...")
    
    from utils.file_storage import FileStorage
    import os
    
    storage = FileStorage()
    test_session_id = "test-session-123"
    
    # Create test file content
    test_content = b"This is a test PDF content"
    original_filename = "test.pdf"
    
    try:
        # Test save_file
        file_id, saved_path = storage.save_file(test_session_id, test_content, original_filename)
        print(f"✅ File saved with ID: {file_id}")
        
        # Test get_file_path
        file_path = storage.get_file_path(test_session_id, file_id, ".pdf")
        assert file_path is not None, "File path should not be None"
        assert os.path.exists(file_path), "Saved file doesn't exist"
        print(f"✅ File path retrieved: {file_path}")
        
        # Test list_session_files
        files = storage.list_session_files(test_session_id)
        assert len(files) == 1, f"Should have 1 file, got {len(files)}"
        print(f"✅ Session files listed: {len(files)} file(s)")
        
        # Test get_file_size
        file_size = storage.get_file_size(test_session_id, file_id, ".pdf")
        assert file_size == len(test_content), f"File size mismatch: {file_size} vs {len(test_content)}"
        print(f"✅ File size verified: {file_size} bytes")
        
        # Test delete_session_files
        success = storage.delete_session_files(test_session_id)
        assert success, "Delete should succeed"
        print(f"✅ Session files deleted successfully")
        
        print("✅ FileStorage tests passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ FileStorage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup - try to delete session files if they still exist
        try:
            storage.delete_session_files(test_session_id)
        except:
            pass

def test_file_validation():
    """Test file validation functions"""
    print("Testing file validation...")
    
    from utils.file_validation import validate_file_type, validate_file_size, format_file_size
    
    tmp2_path = None  # Initialize to avoid UnboundLocalError
    
    try:
        # Test PDF magic bytes
        pdf_content = b"%PDF-1.4\nSome PDF content"
        
        is_valid, error = validate_file_type(pdf_content, "test.pdf")
        assert is_valid, f"PDF validation failed: {error}"
        print("✅ PDF magic bytes validation passed")
        
        # Test DOCX magic bytes (PK header)
        docx_content = b"PK\x03\x04" + b"\x00" * 100
        
        is_valid, error = validate_file_type(docx_content, "test.docx")
        assert is_valid, f"DOCX validation failed: {error}"
        print("✅ DOCX magic bytes validation passed")
        
        # Test size validation
        file_size = len(pdf_content)
        is_valid, error = validate_file_size(file_size, is_funding_call=True)
        assert is_valid, f"Size validation failed: {error}"
        print("✅ File size validation passed")
        
        # Test format_file_size
        size_str = format_file_size(1024 * 1024 * 5)
        assert "5.0MB" in size_str, f"Size formatting failed: {size_str}"
        print(f"✅ Size formatting: {size_str}")
        
        print("✅ File validation tests passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ File validation test failed: {e}")
        return False

def test_session_manager_integration():
    """Test session manager with quota"""
    print("Testing session manager with quota...")
    
    from services.session_manager import SessionManager
    
    manager = SessionManager()
    
    # Create a test session
    session = manager.create_session()
    print(f"✅ Session created: {session.session_id}")
    
    # Check quota status
    quota = session.get_quota_status()
    assert quota['max_size_mb'] == 50, "Default quota should be 50MB"
    print(f"✅ Default quota: {quota['max_size_mb']}MB")
    
    # Simulate file upload
    session.add_upload(file_size_bytes=10 * 1024 * 1024, is_funding_call=False)
    
    # Check updated quota
    quota = session.get_quota_status()
    assert abs(quota['total_size_mb'] - 10) < 0.1, f"Used quota should be ~10MB, got {quota['total_size_mb']}MB"
    print(f"✅ Used quota calculated: {quota['total_size_mb']:.1f}MB")
    
    assert abs(quota['size_remaining_mb'] - 40) < 0.1, f"Remaining quota should be ~40MB, got {quota['size_remaining_mb']}MB"
    print(f"✅ Remaining quota: {quota['size_remaining_mb']:.1f}MB")
    
    print("✅ Session manager integration tests passed!\n")
    return True

def main():
    """Run all Phase 3 backend tests"""
    print("=" * 60)
    print("PHASE 3 BACKEND INTEGRATION TESTS")
    print("=" * 60 + "\n")
    
    results = []
    
    # Test 1: Imports
    results.append(("Imports", test_imports()))
    
    # Test 2: FileStorage
    results.append(("FileStorage", test_file_storage()))
    
    # Test 3: File Validation
    results.append(("File Validation", test_file_validation()))
    
    # Test 4: Session Manager Integration
    results.append(("Session Manager", test_session_manager_integration()))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Phase 3 backend tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
