# Migration Guide: Root Scripts → Phase 2 Components

**Purpose**: How to migrate functionality from existing root scripts to new Phase 2 components

---

## Overview

The project has 3 existing scripts in the root directory:
1. `explore_vectordb.py` - Interactive vector DB search
2. `process_pdfs_to_vectordb.py` - Batch PDF processing
3. `test_pd_embeddings.py` - PDF embedding test

These scripts use LangChain and demonstrate MVP functionality. Phase 2 components provide equivalent (and improved) functionality without LangChain dependency.

---

## Migration Mappings

### 1. `test_pd_embeddings.py` → Phase 2 Components

**Old Code**:
```python
# test_pd_embeddings.py
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

loader = PyPDFLoader(pdf_path)
pages = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
chunks = text_splitter.split_documents(pages)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
test_embedding = embeddings.embed_query(chunks[0].page_content)
```

**New Code (Phase 2)**:
```python
# Using Phase 2 components
from backend.src.utils.parser import DocumentParser
from backend.src.utils.chunking import create_text_splitter
from backend.src.services.embedding_service import get_embedding_service

# Parse PDF (equivalent to PyPDFLoader)
pages = DocumentParser.parse_pdf(pdf_path)

# Chunk text (equivalent to LangChain splitter)
splitter = create_text_splitter(chunk_size=600, chunk_overlap=90)
chunks = []
for page in pages:
    page_chunks = splitter.split_text(page['text'])
    chunks.extend(page_chunks)

# Generate embeddings (equivalent to OpenAIEmbeddings)
embedding_service = get_embedding_service()
test_embedding = embedding_service.embed_query(chunks[0])
```

**Benefits**:
- ✅ No LangChain dependency (smaller footprint)
- ✅ Token-based chunking (more accurate)
- ✅ Page number preservation (better citations)
- ✅ Configurable via config.yaml

---

### 2. `process_pdfs_to_vectordb.py` → Phase 3 Indexing Service

**Old Code**:
```python
# process_pdfs_to_vectordb.py
from langchain_community.vectorstores import Chroma

# Process PDFs
for pdf_file in pdf_files:
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(pages)
    
    # Add metadata
    for chunk in chunks:
        chunk.metadata['source_file'] = pdf_file

vectordb = Chroma.from_documents(
    documents=all_chunks,
    embedding=embeddings,
    persist_directory=vectordb_path
)
```

**New Code (Phase 2/3)**:
```python
# Using Phase 2 components (will be wrapped in Phase 3 indexing service)
from backend.src.utils.parser import DocumentParser
from backend.src.utils.chunking import create_text_splitter
from backend.src.services.vector_store import get_vector_store

vector_store = get_vector_store()
splitter = create_text_splitter()

for pdf_file in pdf_files:
    # Parse
    pages = DocumentParser.parse_pdf(pdf_file)
    
    # Chunk
    texts = []
    metadatas = []
    for page in pages:
        page_chunks = splitter.split_text(page['text'])
        for i, chunk_text in enumerate(page_chunks):
            texts.append(chunk_text)
            metadatas.append({
                'document_title': os.path.basename(pdf_file),
                'page_number': page['page_number'],
                'chunk_index': i,
                'source_file': pdf_file
            })
    
    # Index
    vector_store.add_documents(session_id, texts, metadatas)

print(f"Indexed {vector_store.get_collection_count(session_id)} chunks")
```

**Benefits**:
- ✅ Session-based collections (better isolation)
- ✅ Metadata standardization (document_title, page_number)
- ✅ Persistent storage (ChromaDB PersistentClient)
- ✅ Quota enforcement (via session manager)

---

### 3. `explore_vectordb.py` → Vector Store Search

**Old Code**:
```python
# explore_vectordb.py
from langchain_community.vectorstores import Chroma

vectordb = Chroma(
    persist_directory=vectordb_path,
    embedding_function=embeddings
)

results = vectordb.similarity_search(query, k=5)

for doc in results:
    print(f"Source: {doc.metadata.get('source_file')}, Page {doc.metadata.get('page')}")
    print(f"{doc.page_content[:400]}...")
```

**New Code (Phase 2)**:
```python
# Using Phase 2 vector store
from backend.src.services.vector_store import get_vector_store

vector_store = get_vector_store()

results = vector_store.search(session_id, query, top_k=5)

for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Source: {result['metadata']['document_title']}, Page {result['metadata']['page_number']}")
    print(f"{result['text'][:400]}...")
```

**Benefits**:
- ✅ Relevance scores included (1-distance/2)
- ✅ Min relevance filtering (drop low-quality results)
- ✅ Session isolation (each user has own collection)
- ✅ Consistent metadata schema

---

## Metadata Schema Standardization

### Old LangChain Metadata (Inconsistent)
```python
{
    'source': 'doc.pdf',           # or 'source_file'
    'page': 5,                      # or 'page_number'
    # Missing: chunk_index, document_title
}
```

### New Phase 2 Metadata (Standardized)
```python
{
    'document_title': 'Annual Report 2023.pdf',  # Human-readable name
    'page_number': 5,                             # Always 1-indexed
    'chunk_index': 0,                             # Position in document
    'source_file': '/path/to/doc.pdf',           # Optional: full path
}
```

**Why Standardized?**
- ✅ Citations use `document_title` and `page_number`
- ✅ Sorting by `chunk_index` preserves document order
- ✅ Consistent across PDF and DOCX files

---

## API Compatibility Layer (Optional)

If you want to keep using the old scripts temporarily, create this adapter:

```python
# langchain_adapter.py (temporary compatibility layer)
"""
Adapter to use old LangChain scripts with new Phase 2 components.
DO NOT use in production - for testing migration only.
"""

from backend.src.utils.parser import DocumentParser
from backend.src.utils.chunking import create_text_splitter
from backend.src.services.embedding_service import get_embedding_service
from backend.src.services.vector_store import get_vector_store

class LangChainDocument:
    """Mimics LangChain Document class"""
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

class PDFLoaderAdapter:
    """Adapter for PyPDFLoader → DocumentParser"""
    def __init__(self, file_path):
        self.file_path = file_path
    
    def load(self):
        pages = DocumentParser.parse_pdf(self.file_path)
        return [
            LangChainDocument(
                page_content=p['text'],
                metadata={'source': p['metadata']['source'], 'page': p['page_number']}
            )
            for p in pages
        ]

class TextSplitterAdapter:
    """Adapter for LangChain splitter → Phase 2 chunking"""
    def __init__(self, chunk_size=600, chunk_overlap=90):
        self.splitter = create_text_splitter(chunk_size, chunk_overlap)
    
    def split_documents(self, documents):
        chunks = []
        for doc in documents:
            chunk_texts = self.splitter.split_text(doc.page_content)
            for chunk_text in chunk_texts:
                chunks.append(LangChainDocument(
                    page_content=chunk_text,
                    metadata=doc.metadata
                ))
        return chunks

# Usage:
# loader = PDFLoaderAdapter(pdf_path)  # instead of PyPDFLoader
# splitter = TextSplitterAdapter()      # instead of RecursiveCharacterTextSplitter
```

**Note**: This adapter is for **testing only**. Do not use in production code.

---

## Recommended Migration Path

### Phase 1: Keep Both (Testing Phase)
- ✅ Keep old scripts in root directory
- ✅ Use new Phase 2 components for new features
- ✅ Run integration tests to verify equivalence

### Phase 2: Gradual Migration
- ✅ Move `test_pd_embeddings.py` logic to Phase 2 test suite
- ✅ Integrate `process_pdfs_to_vectordb.py` into Phase 3 indexing service
- ✅ Add `explore_vectordb.py` functionality to admin endpoints (Phase 10)

### Phase 3: Deprecate Old Scripts (Post-MVP)
- ✅ Mark old scripts as deprecated in README
- ✅ Move to `legacy/` directory
- ✅ Update documentation to reference Phase 2 components only

---

## What to Do with Existing Scripts

### Option A: Archive (Recommended for MVP)
```powershell
# Create legacy directory
mkdir legacy

# Move old scripts
mv explore_vectordb.py legacy/
mv process_pdfs_to_vectordb.py legacy/
mv test_pd_embeddings.py legacy/

# Add note
echo "# Legacy Scripts (Pre-Phase 2)" > legacy/README.md
echo "These scripts use LangChain. See Phase 2 components for new implementation." >> legacy/README.md
```

### Option B: Keep as Examples
Add comment at top of each file:
```python
"""
DEPRECATED: This script uses LangChain and is kept for reference only.

For new code, use Phase 2 components:
- backend/src/utils/parser.py (instead of PyPDFLoader)
- backend/src/utils/chunking.py (instead of RecursiveCharacterTextSplitter)
- backend/src/services/vector_store.py (instead of Chroma)
- backend/src/services/embedding_service.py (instead of OpenAIEmbeddings)

See PHASE2_QUICKREF.md for migration guide.
"""
```

### Option C: Convert to Tests
Transform scripts into Phase 2 integration tests:
```powershell
# Convert to test format
cp test_pd_embeddings.py tests/test_pdf_pipeline.py
# Then update to use Phase 2 components
```

---

## Key Differences to Remember

### 1. Chunking Strategy
- **Old**: Character-based (1000 chars)
- **New**: Token-based (600 tokens)
- **Impact**: New chunks align better with LLM context windows

### 2. Collection Management
- **Old**: Single global Chroma collection
- **New**: Session-based collections (`session_{session_id}`)
- **Impact**: Better data isolation, easier cleanup

### 3. Metadata Schema
- **Old**: Varies by script (`source` vs `source_file`, `page` vs `page_number`)
- **New**: Standardized (`document_title`, `page_number`, `chunk_index`)
- **Impact**: Consistent citations across all documents

### 4. Page Number Handling
- **Old**: LangChain extracts but doesn't always preserve correctly
- **New**: Explicit page tracking in parser
- **Impact**: More accurate citations

### 5. Error Handling
- **Old**: Minimal (scripts crash on errors)
- **New**: Pydantic validation, quota checks, type safety
- **Impact**: Production-ready error messages

---

## Testing Equivalence

To verify Phase 2 components produce same results as old scripts:

```python
# test_migration_equivalence.py
"""
Verify Phase 2 components produce equivalent results to old LangChain scripts.
"""

import os
from backend.src.utils.parser import DocumentParser
from backend.src.utils.chunking import create_text_splitter
from backend.src.services.embedding_service import get_embedding_service

# Old LangChain approach
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

def test_pdf_parsing():
    """Verify PDF parsing produces same text"""
    pdf_path = "test_docs/NICI_guidelines.pdf"
    
    # Old
    old_loader = PyPDFLoader(pdf_path)
    old_pages = old_loader.load()
    old_text = "\n".join(p.page_content for p in old_pages)
    
    # New
    new_pages = DocumentParser.parse_pdf(pdf_path)
    new_text = "\n".join(p['text'] for p in new_pages)
    
    # Compare (allow minor whitespace differences)
    old_clean = old_text.replace('\n', ' ').strip()
    new_clean = new_text.replace('\n', ' ').strip()
    
    similarity = len(set(old_clean.split()) & set(new_clean.split())) / len(set(old_clean.split()))
    print(f"Text similarity: {similarity:.2%}")
    assert similarity > 0.95, "Text extraction differs significantly"

def test_embedding_equivalence():
    """Verify embeddings are identical"""
    text = "This is a test document about grant proposals."
    
    # Old
    old_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    old_emb = old_embeddings.embed_query(text)
    
    # New
    new_service = get_embedding_service()
    new_emb = new_service.embed_query(text)
    
    # Compare
    assert len(old_emb) == len(new_emb), "Embedding dimensions differ"
    diff = sum(abs(a - b) for a, b in zip(old_emb, new_emb))
    print(f"Embedding difference: {diff:.6f}")
    assert diff < 0.001, "Embeddings differ (should be identical)"

if __name__ == "__main__":
    if os.getenv("OPENAI_API_KEY"):
        test_pdf_parsing()
        test_embedding_equivalence()
        print("✅ Migration equivalence verified")
    else:
        print("⚠️ Set OPENAI_API_KEY to run equivalence tests")
```

---

## Summary

**Do This**:
- ✅ Use Phase 2 components for all new code
- ✅ Archive old scripts to `legacy/` directory
- ✅ Update documentation to reference new components
- ✅ Add deprecation warnings to old scripts

**Don't Do This**:
- ❌ Mix LangChain and Phase 2 components in same feature
- ❌ Import from both old scripts and new components
- ❌ Copy-paste old script code into Phase 3+

**When in Doubt**:
- 📖 Check `PHASE2_QUICKREF.md` for code patterns
- 🧪 Run `python run_phase2_tests.py` to verify components work
- 📝 Review `TESTING_PHASE2.md` for detailed examples

---

**Last Updated**: 2025-10-26  
**Status**: Ready for Phase 3 implementation
