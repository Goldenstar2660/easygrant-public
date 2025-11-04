import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

def explore_vectordb(vectordb_path="./chroma_db"):
    """Load and explore the vector database"""
    
    # Load existing database
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    vectordb = Chroma(
        persist_directory=vectordb_path,
        embedding_function=embeddings
    )
    
    # Get collection info
    collection = vectordb._collection
    print(f"📊 Vector Database Stats:")
    print(f"   Total chunks: {collection.count()}")
    print(f"   Location: {vectordb_path}\n")
    
    return vectordb


def search_database(vectordb, query, k=5):
    """Search the database"""
    print(f"🔍 Query: '{query}'")
    print("=" * 70)
    
    results = vectordb.similarity_search(query, k=k)
    
    for i, doc in enumerate(results, 1):
        print(f"\n[{i}] Source: {doc.metadata.get('source_file', 'unknown')}, Page {doc.metadata.get('page', '?')}")
        print(f"{doc.page_content[:400]}...")
        print("-" * 70)
    
    return results


if __name__ == "__main__":
    # Load the database
    vectordb = explore_vectordb()
    
    # Interactive search
    print("\n" + "=" * 70)
    print("INTERACTIVE SEARCH")
    print("=" * 70)
    print("Type your search query (or 'quit' to exit)\n")
    
    while True:
        query = input("Search: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if not query:
            continue
        
        search_database(vectordb, query)
        print()
