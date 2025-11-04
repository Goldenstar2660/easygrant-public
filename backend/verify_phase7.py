"""
Manual verification script for Phase 7 Export functionality
Run this to verify all Phase 7 components are properly implemented
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("PHASE 7 EXPORT FUNCTIONALITY VERIFICATION")
print("=" * 60)

# Test 1: Import Assembler
print("\n[1/6] Testing Assembler import...")
try:
    from backend.src.agents.assembler import Assembler
    print("✓ Assembler imported successfully")
except Exception as e:
    print(f"✗ Failed to import Assembler: {e}")
    exit(1)

# Test 2: Initialize Assembler
print("\n[2/6] Testing Assembler initialization...")
try:
    assembler = Assembler()
    print("✓ Assembler initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize Assembler: {e}")
    exit(1)

# Test 3: Create test document
print("\n[3/6] Testing document assembly...")
try:
    sections = [
        {
            'section_name': 'Project Summary',
            'text': 'This is a test project summary with a citation [Test Doc, p.1].',
            'word_count': 10,
            'citations': []
        },
        {
            'section_name': 'Project Description',
            'text': 'Detailed description here.\n\nSecond paragraph with more info [Source, p.5].',
            'word_count': 12,
            'citations': []
        }
    ]
    
    doc = assembler.assemble_proposal(
        sections=sections,
        funding_call_name='Test Funding Call 2025',
        program_name='Test Organization'
    )
    
    print(f"✓ Document assembled successfully")
    print(f"  - Paragraphs: {len(doc.paragraphs)}")
    print(f"  - Sections included: {len(sections)}")
except Exception as e:
    print(f"✗ Failed to assemble document: {e}")
    exit(1)

# Test 4: Convert to bytes
print("\n[4/6] Testing DOCX bytes conversion...")
try:
    docx_bytes = assembler.get_docx_bytes(doc)
    print(f"✓ DOCX bytes generated")
    print(f"  - Size: {len(docx_bytes):,} bytes")
    print(f"  - Magic bytes: {docx_bytes[:2]} (should be b'PK')")
    
    # Verify it's a valid ZIP/DOCX file
    if docx_bytes[:2] != b'PK':
        print("✗ Invalid DOCX format (missing PK magic bytes)")
        exit(1)
except Exception as e:
    print(f"✗ Failed to convert to bytes: {e}")
    exit(1)

# Test 5: Verify export route exists
print("\n[5/6] Testing export route import...")
try:
    from backend.src.api.routes.export import router, export_docx
    print("✓ Export router imported successfully")
    print(f"  - Routes: {[r.path for r in router.routes]}")
except Exception as e:
    print(f"✗ Failed to import export router: {e}")
    exit(1)

# Test 6: Verify frontend API function exists
print("\n[6/6] Testing frontend API integration...")
try:
    import os
    frontend_api_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'frontend',
        'src',
        'services',
        'api.js'
    )
    
    if not os.path.exists(frontend_api_path):
        print(f"✗ Frontend API file not found: {frontend_api_path}")
        exit(1)
    
    with open(frontend_api_path, 'r', encoding='utf-8') as f:
        api_content = f.read()
    
    if 'exportAPI' in api_content and 'exportDOCX' in api_content:
        print("✓ Frontend export API function exists")
    else:
        print("✗ Frontend export API function not found")
        exit(1)
    
    if 'exportProposal' in api_content:
        print("✓ Frontend exportProposal helper exists")
    else:
        print("✗ Frontend exportProposal helper not found")
        exit(1)
except Exception as e:
    print(f"✗ Failed to verify frontend API: {e}")
    exit(1)

# Test 7: Verify ExportButton component exists
print("\n[7/7] Testing ExportButton component...")
try:
    import os
    export_button_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'frontend',
        'src',
        'components',
        'ExportButton.jsx'
    )
    
    if not os.path.exists(export_button_path):
        print(f"✗ ExportButton component not found")
        exit(1)
    
    with open(export_button_path, 'r', encoding='utf-8') as f:
        button_content = f.read()
    
    # Check for key functionality
    checks = {
        'exportProposal import': 'exportProposal' in button_content,
        'Loading state': 'isExporting' in button_content,
        'Download trigger': 'download' in button_content or 'Download' in button_content,
        'Error handling': 'error' in button_content,
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        if passed:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    if all_passed:
        print("✓ ExportButton component has all required features")
    else:
        print("✗ ExportButton component missing some features")
        exit(1)
        
except Exception as e:
    print(f"✗ Failed to verify ExportButton: {e}")
    exit(1)

# Final summary
print("\n" + "=" * 60)
print("✓ ALL PHASE 7 VERIFICATION CHECKS PASSED!")
print("=" * 60)
print("\nImplemented components:")
print("  ✓ Backend: assembler.py (merge sections to DOCX)")
print("  ✓ Backend: routes/export.py (POST /api/export/docx)")
print("  ✓ Frontend: ExportButton.jsx (UI component)")
print("  ✓ Frontend: api.js (exportProposal function)")
print("\nPhase 7 is complete and ready for testing!")
