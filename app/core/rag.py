import google.generativeai as genai
from chromadb import Documents, EmbeddingFunction, Embeddings
import os
from typing import List, Dict, Any, Tuple
import chromadb
from datetime import datetime

# region : gemini
import google.generativeai as genai

class GeminiEmbeddingFunction(EmbeddingFunction):
    """
    Custom embedding function using the Gemini AI API for document retrieval.

    This class extends the EmbeddingFunction class and implements the __call__ method
    to generate embeddings for a given set of documents using the Gemini AI API.

    Parameters:
    - input (Documents): A collection of documents to be embedded.

    Returns:
    - Embeddings: Embeddings generated for the input documents.
    """
    def __call__(self, input: Documents) -> Embeddings:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("Gemini API Key not provided. Please provide GEMINI_API_KEY as an environment variable")
        genai.configure(api_key=gemini_api_key)
        model = "models/embedding-001"
        title = "Custom query"
        return genai.embed_content(model=model,
                                   content=input,
                                   task_type="retrieval_document",
                                   title=title)["embedding"]



def format_chat_history(messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Format messages for Gemini chat history"""
    formatted_messages = []
    
    # Add system message at the start
    formatted_messages.append({
        "role": "system",
        "content": """You are a helpful AI assistant with access to a knowledge base. 
        Your responses should be:
        1. Accurate and based on the provided context
        2. Comprehensive yet concise
        3. In a conversational, friendly tone
        4. Include relevant examples when helpful
        If you're not sure about something, say so rather than making assumptions."""
    })
    
    # Add conversation history
    for msg in messages:
        formatted_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    return formatted_messages

def create_chroma_db(documents: List[str], path: str, name: str, batch_size: int = 50) -> Tuple[chromadb.Collection, str]:
    """
    Creates a Chroma database with proper document handling and metadata.
    Uses batching for better performance.
    
    Args:
        documents: List of text chunks to be added
        path: Path for ChromaDB storage
        name: Collection name
        batch_size: Number of documents to process in each batch
        
    Returns:
        Tuple of (ChromaDB collection, collection name)
    """
    chroma_client = chromadb.PersistentClient(path=path)
    
    # Check if collection exists and delete if it does
    try:
        chroma_client.delete_collection(name)
    except:
        pass
        
    # Create new collection with optimized settings
    db = chroma_client.create_collection(
        name=name,
        embedding_function=GeminiEmbeddingFunction(),
        metadata={"created_at": datetime.now().isoformat()}
    )

    # Process documents in batches
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        
        # Prepare batch metadata
        metadatas = [{
            "chunk_id": str(i + j),
            "chunk_index": i + j,
            "total_chunks": len(documents),
            "batch_number": i // batch_size,
            "timestamp": datetime.now().isoformat()
        } for j in range(len(batch))]
        
        # Add batch to collection
        db.add(
            documents=batch,
            metadatas=metadatas,
            ids=[f"chunk_{i + j}" for j in range(len(batch))]
        )

    return db, name

def load_chroma_collection(path: str, name: str) -> chromadb.Collection:
    """
    Loads an existing Chroma collection with the embedding function.
    """
    chroma_client = chromadb.PersistentClient(path=path)
    db = chroma_client.get_collection(
        name=name,
        embedding_function=GeminiEmbeddingFunction()
    )
    return db

# region : for the gemini answer
def get_relevant_passage(query: str, db: chromadb.Collection, n_results: int = 3) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Retrieves relevant passages with improved relevance scoring.
    
    Args:
        query: The search query
        db: ChromaDB collection
        n_results: Number of results to retrieve
        
    Returns:
        Tuple of (passages, metadata)
    """
    # Add query preprocessing
    query = query.strip().lower()
    
    # Get results with more context
    results = db.query(
        query_texts=[query],
        n_results=n_results + 2,  # Get extra results for better filtering
        include=["documents", "metadatas", "distances"]
    )
    
    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0]
    
    # Improved scoring
    max_dist = max(distances)
    min_dist = min(distances)
    dist_range = max_dist - min_dist
    
    scored_results = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        # Normalize distance to similarity score
        norm_dist = (dist - min_dist) / dist_range if dist_range > 0 else 1.0
        similarity = 1.0 - (norm_dist * 0.7)
        
        # Additional scoring factors
        chunk_position = meta.get('chunk_index', 0) / meta.get('total_chunks', 1)
        recency_score = 0.1  # Base score for all results
        
        # Combined score
        final_score = (
            similarity * 0.6 +  # Similarity is most important
            (1 - chunk_position) * 0.3 +  # Earlier chunks slightly preferred
            recency_score * 0.1  # Small boost for recency
        )
        
        meta['relevance_score'] = final_score
        scored_results.append((final_score, doc, meta))
    
    # Sort by score and take top n_results
    scored_results.sort(reverse=True)
    top_results = scored_results[:n_results]
    
    # Return in original format
    return (
        [doc for _, doc, _ in top_results],
        [meta for _, _, meta in top_results]
    )

def make_rag_prompt(query: str, relevant_passages: List[str], metadata: List[Dict[str, Any]], chat_history: List[Dict[str, Any]] = None) -> str:
    """
    Creates a contextual prompt using passage metadata, relevance, and chat history.
    """
    # Sort passages by relevance score
    sorted_passages = sorted(
        zip(relevant_passages, metadata),
        key=lambda x: x[1].get('relevance_score', 0),
        reverse=True
    )
    
    # Combine passages with relevance information
    context = "\n\n".join([
        f"[Relevance: {meta.get('relevance_score', 0):.2f}]\n{passage}"
        for passage, meta in sorted_passages
    ])
    
    # Format chat history if provided
    history_text = ""
    if chat_history:
        history_text = "\n\nPrevious conversation:\n" + "\n".join([
            f"{msg['role'].title()}: {msg['content']}"
            for msg in chat_history[-3:]  # Include last 3 messages for context
        ])
    
    prompt = f"""You are a helpful and informative AI assistant with access to specific documents.
Please provide a comprehensive answer that includes relevant background information.
Use a friendly and conversational tone, and break down any complex concepts for a non-technical audience.
Base your answer primarily on the most relevant passages (those with higher relevance scores).
Consider the conversation history for context, but focus on the current question.
If the passages don't contain relevant information to answer the question, please say so.

Relevant Passages:
{context}

{history_text}

Current Question: {query}

Answer:"""
    
    return prompt

def generate_gemini_answer(prompt: str, chat_history: List[Dict[str, Any]] = None) -> str:
    """
    Generates an answer using Gemini model with chat history context.
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("Gemini API Key not provided")
    
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    try:
        # Start a new chat
        chat = model.start_chat()
        
        # Add system message
        chat.send_message("""You are a helpful AI assistant with access to specific documents.
        Please provide comprehensive answers based on the provided context.
        Use a friendly and conversational tone, and break down complex concepts.""")
        
        # Add chat history if provided
        if chat_history:
            for msg in chat_history:
                chat.send_message(msg['content'])
        
        # Send the prompt and get response
        response = chat.send_message(prompt)
        return response.text
        
    except Exception as e:
        return f"Error generating response: {str(e)}"

def generate_answer(db: chromadb.Collection, query: str, chat_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generates an answer with supporting information and chat context.
    
    Returns:
    - Dictionary containing answer and supporting information
    """
    # Get relevant passages and metadata
    relevant_passages, metadata = get_relevant_passage(query, db, n_results=3)
    
    # Create prompt with chat history
    prompt = make_rag_prompt(query, relevant_passages, metadata, chat_history)
    
    # Generate answer
    answer = generate_gemini_answer(prompt, chat_history)
    
    # Return comprehensive response
    return {
        "answer": answer,
        "supporting_info": {
            "passages": relevant_passages,
            "metadata": metadata
        }
    }
