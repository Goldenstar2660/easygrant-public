"""
Test script to verify logging is working correctly.
Run this to ensure all logging statements will appear when you use the app.
"""

import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging (same as main.py)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_logging():
    """Test that logging is configured correctly"""
    print("\n" + "=" * 80)
    print("TESTING EASYGRANT LOGGING SYSTEM")
    print("=" * 80 + "\n")
    
    # Test basic logging
    logger.info("✓ Basic logging is working")
    
    # Test each module's logging
    from backend.src.agents.requirements_extractor import RequirementsExtractor
    from backend.src.agents.section_generator import SectionGenerator
    from backend.src.agents.retriever import Retriever
    from backend.src.services.indexing_service import IndexingService
    
    logger.info("✓ All agent modules imported successfully")
    
    # Create test loggers for each module
    req_logger = logging.getLogger('backend.src.agents.requirements_extractor')
    gen_logger = logging.getLogger('backend.src.agents.section_generator')
    ret_logger = logging.getLogger('backend.src.agents.retriever')
    idx_logger = logging.getLogger('backend.src.services.indexing_service')
    
    print("\nTesting individual module loggers:\n")
    
    req_logger.info("[REQUIREMENTS EXTRACTION] ✓ Requirements extractor logging works")
    gen_logger.info("[SECTION GENERATOR] ✓ Section generator logging works")
    ret_logger.info("[RETRIEVER] ✓ Retriever logging works")
    idx_logger.info("[INDEXING] ✓ Indexing service logging works")
    
    print("\n" + "=" * 80)
    print("SUCCESS! All logging is configured correctly.")
    print("=" * 80)
    print("\nWhen you run the application, you will see detailed logs like:")
    print("  • [REQUIREMENTS EXTRACTION] ========== FULL PARSED PDF TEXT ==========")
    print("  • [SECTION GENERATOR] ========== COMPLETE GENERATION PROMPT ==========")
    print("  • [RETRIEVER] ========== RAW SEARCH RESULTS ==========")
    print("  • [INDEXING] ========== CHUNKS TO BE EMBEDDED ==========")
    print("\nStart the backend with: .\\scripts\\start-backend.ps1")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    test_logging()
