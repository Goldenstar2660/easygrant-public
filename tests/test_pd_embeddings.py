import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

load_dotenv()

def pdf_to_embeddings(pdf_path):
    """Load PDF and create embeddings"""
    
    # Step 1: Load PDF
    print(f"Loading PDF: {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    print(f"✓ Loaded {len(pages)} pages")
    
    # Step 2: Split into chunks
    print("Splitting into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = text_splitter.split_documents(pages)
    print(f"✓ Created {len(chunks)} chunks")
    
    # Step 3: Create embeddings model
    print("Creating embeddings...")
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Test on first chunk
    test_embedding = embeddings.embed_query(chunks[0].page_content)
    print(f"✓ Embedding dimension: {len(test_embedding)}")
    print(f"✓ First few values: {test_embedding[:5]}")
    
    print(f"\n✅ SUCCESS! PDF converted to embeddings")
    print(f"\nSample chunk:\n{chunks[0].page_content[:300]}...")
    
    return chunks, embeddings

if __name__ == "__main__":
    pdf_path = "test_docs/NICI_guidelines.pdf"
    chunks, embeddings = pdf_to_embeddings(pdf_path)