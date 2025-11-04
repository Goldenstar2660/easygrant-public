"""
EasyGrant Smart Proposal Assistant - Main FastAPI Application
Constitution-compliant RAG-based grant writing assistant
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging - less verbose, only important events
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and errors by default
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Output to console/terminal
    ]
)

# Set specific loggers to INFO for important operations
logging.getLogger('backend.src.services.indexing_service').setLevel(logging.INFO)
logging.getLogger('backend.src.agents.requirements_extractor').setLevel(logging.INFO)
logging.getLogger('backend.src.agents.retriever').setLevel(logging.INFO)  # SHOW RETRIEVAL DECISIONS
logging.getLogger('backend.src.agents.section_generator').setLevel(logging.INFO)  # SHOW WHAT'S SENT TO AI
logging.getLogger('backend.src.services.vector_store').setLevel(logging.WARNING)  # Keep quiet
logging.getLogger('backend.src.api.middleware').setLevel(logging.WARNING)  # Suppress middleware logs
logging.getLogger('httpx').setLevel(logging.WARNING)  # Suppress HTTP request logs

# Set logging level for specific modules
logger = logging.getLogger(__name__)
logger.info("=" * 80)
logger.info("EasyGrant Smart Proposal Assistant - Starting Up")
logger.info("Detailed logging enabled for AI prompts and PDF parsing")
logger.info("=" * 80)

# Import routers
from backend.src.api.routes import session, upload, requirements, sections, debug, export, samples
from backend.src.api.middleware import session_validation_middleware

# Initialize FastAPI app
app = FastAPI(
    title="EasyGrant Smart Proposal Assistant",
    description="RAG-based grant writing assistant for small and remote communities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add session validation middleware
app.middleware("http")(session_validation_middleware)

# Load configuration
# TODO: Load from config.yaml in Phase 2
CORS_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",   # Alternative dev port
    "https://easy-grant.vercel.app",  # Vercel production
    "https://easy-grant-*.vercel.app",  # Vercel preview deployments
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(session.router)
app.include_router(upload.router)
app.include_router(requirements.router)
app.include_router(sections.router)
app.include_router(debug.router)
app.include_router(export.router)
app.include_router(samples.router)

# Ensure data directories exist
DATA_DIR = Path("./data/uploads")
VECTOR_DIR = Path("./vector")
DATA_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DIR.mkdir(parents=True, exist_ok=True)

# Log startup information
logger.info(f"Data directory: {DATA_DIR.absolute()}")
logger.info(f"Vector directory: {VECTOR_DIR.absolute()}")
logger.info(f"OpenAI API key configured: {bool(os.getenv('OPENAI_API_KEY'))}")


@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("=" * 80)
    logger.info("FastAPI application started successfully")
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("Health Check: http://localhost:8000/health")
    logger.info("")
    logger.info("📊 LOGGING ENABLED FOR:")
    logger.info("  • [REQUIREMENTS EXTRACTION] - Funding call analysis")
    logger.info("  • [SECTION GENERATOR] - Proposal section generation")
    logger.info("  • [RETRIEVER] - Semantic search results")
    logger.info("  • [INDEXING] - Document parsing and chunking")
    logger.info("")
    logger.info("📝 Look for log sections marked with '=========='")
    logger.info("=" * 80)


@app.get("/")
async def root():
    """Root endpoint - redirect to docs"""
    return {
        "message": "EasyGrant Smart Proposal Assistant API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for deployment monitoring
    Returns system status and configuration verification
    """
    health_status = {
        "status": "healthy",
        "service": "EasyGrant Proposal Assistant",
        "version": "1.0.0",
        "environment": {
            "data_directory": str(DATA_DIR.absolute()),
            "data_directory_exists": DATA_DIR.exists(),
            "vector_directory": str(VECTOR_DIR.absolute()),
            "vector_directory_exists": VECTOR_DIR.exists(),
            "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
        }
    }
    
    return JSONResponse(content=health_status, status_code=200)


if __name__ == "__main__":
    import uvicorn
    
    # Run with: python -m backend.src.main
    # Or: uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
    uvicorn.run(
        "backend.src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
