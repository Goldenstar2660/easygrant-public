import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

def process_all_pdfs_in_folder(folder_path, vectordb_path="./chroma_db"):
    """
    Process all PDFs in a folder and save to a single vector database
    
    Args:
        folder_path: Path to folder containing PDFs
        vectordb_path: Where to save the vector database
    """
    
    # Get all PDF files in folder
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"❌ No PDF files found in {folder_path}")
        return None
    
    print(f"Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        print(f"  - {pdf}")
    print()
    
    all_chunks = []
    
    # Process each PDF
    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder_path, pdf_file)
        print(f"Processing: {pdf_file}")
        
        try:
            # Load PDF
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            print(f"  ✓ Loaded {len(pages)} pages")
            
            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
            )
            chunks = text_splitter.split_documents(pages)
            
            # Add metadata to track which PDF each chunk came from
            for chunk in chunks:
                chunk.metadata['source_file'] = pdf_file
            
            all_chunks.extend(chunks)
            print(f"  ✓ Created {len(chunks)} chunks")
            
        except Exception as e:
            print(f"  ❌ Error processing {pdf_file}: {e}")
            continue
    
    if not all_chunks:
        print("❌ No chunks created from any PDFs")
        return None
    
    print(f"\n📊 Total chunks from all PDFs: {len(all_chunks)}")
    
    # Create embeddings
    print("\n🔄 Creating embeddings and saving to vector database...")
    print("(This may take a minute...)")
    
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create and save vector database
    vectordb = Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        persist_directory=vectordb_path
    )
    
    print(f"✅ SUCCESS! Vector database created at {vectordb_path}")
    print(f"📁 Processed {len(pdf_files)} PDFs with {len(all_chunks)} total chunks\n")
    
    return vectordb


def test_search(vectordb, query, k=3):
    """Test searching the vector database"""
    print(f"\n🔍 Searching for: '{query}'")
    print("-" * 60)
    
    results = vectordb.similarity_search(query, k=k)
    
    for i, doc in enumerate(results, 1):
        print(f"\n[Result {i}] From: {doc.metadata.get('source_file', 'unknown')}")
        print(f"Page: {doc.metadata.get('page', 'unknown')}")
        print(f"Content preview:\n{doc.page_content[:300]}...")
        print("-" * 60)
    
    return results


if __name__ == "__main__":
    # Configuration
    PDF_FOLDER = "test_docs"  # Folder containing PDFs
    VECTORDB_PATH = "./chroma_db"  # Where to save vector database
    
    # Process all PDFs
    print("=" * 60)
    print("PDF TO VECTOR DATABASE PROCESSOR")
    print("=" * 60)
    print()
    
    vectordb = process_all_pdfs_in_folder(PDF_FOLDER, VECTORDB_PATH)
    
    if vectordb:
        # Test some searches
        print("\n" + "=" * 60)
        print("TESTING SEARCHES")
        print("=" * 60)
        
        test_search(vectordb, "eligibility criteria")
        test_search(vectordb, "funding amounts")
        test_search(vectordb, "application deadline")
        
        print("\n✅ All done! Your vector database is ready to use.")
        print(f"📁 Location: {VECTORDB_PATH}")
