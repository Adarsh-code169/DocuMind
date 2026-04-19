import streamlit as st
import os
import sys
import logging
import json
from dotenv import load_dotenv

# Add the current directory to sys.path so we can import from the backend folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.chroma_store import ChromaVectorStore
from backend.pipeline.ingestion import extract_text_from_pdf, chunk_text
from backend.pipeline.retrieval import RetrievalPipeline
from backend.embeddings import embedding_model

# Page Configuration
st.set_page_config(
    page_title="DocuMind | Intelligent Knowledge Engine",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Environment Variables
load_dotenv()

# Custom CSS for Premium Look
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stChatFloatingInputContainer {
        bottom: 20px;
    }
    .st-emotion-cache-1cypcdb {
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px;
        background-color: #161b22;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .st-emotion-cache-v0 {  /* Chat user */
        background-color: #21262d !important;
    }
    .st-emotion-cache-4oy321 { /* Chat assistant */
        background-color: #161b22 !important;
    }
    div[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #30363d;
    }
    .status-card {
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #30363d;
        margin-bottom: 10px;
    }
    h1, h2, h3 {
        color: #f0f6fc !important;
    }
    p {
        color: #8b949e !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

@st.cache_resource
def get_vector_store():
    persist_dir = os.path.join(os.path.dirname(__file__), "backend", "chroma_db")
    return ChromaVectorStore(persist_directory=persist_dir)

@st.cache_resource
def get_retrieval_pipeline(_vector_store):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.warning("⚠️ GROQ_API_KEY is missing. AI chat will not work.")
        return None
    return RetrievalPipeline(api_key=api_key, vector_store=_vector_store)

# Load resources
vector_store = get_vector_store()
retrieval_pipeline = get_retrieval_pipeline(vector_store)

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/isometric-folders/100/brain.png", width=60)
    st.title("DocuMind")
    st.caption("v1.0.0-beta")
    
    st.divider()
    
    # Status
    st.subheader("System Status")
    status_col1, status_col2 = st.columns(2)
    with status_col1:
        st.success("Online")
    with status_col2:
        if os.getenv("GROQ_API_KEY"):
            st.success("API Ready")
        else:
            st.error("Missing Key")
            
    st.divider()
    
    # Document Management
    st.subheader("Knowledge Base")
    uploaded_file = st.file_uploader("Upload PDF Documents", type=["pdf"])
    
    if uploaded_file:
        if st.button("Process & Ingest"):
            with st.status(f"Ingesting {uploaded_file.name}...", expanded=True) as status:
                try:
                    file_content = uploaded_file.read()
                    
                    st.write("🔍 Extracting text...")
                    pages = extract_text_from_pdf(file_content, uploaded_file.name)
                    
                    st.write(f"✂️ Chunking into segments...")
                    chunks = chunk_text(pages)
                    
                    st.write("🧠 Generating embeddings...")
                    texts = [c["text"] for c in chunks]
                    embeddings = embedding_model.generate_batch(texts)
                    
                    st.write("💾 Syncing to ChromaDB...")
                    success = vector_store.insert(embeddings, chunks)
                    
                    if success:
                        status.update(label=f"Successfully ingested {uploaded_file.name}!", state="complete", expanded=False)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Database sync failed.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # List Documents
    st.divider()
    docs = vector_store.list_documents()
    if docs:
        st.write(f"📚 **Current Library ({len(docs)})**")
        for doc in docs:
            fname = doc["filename"]
            col1, col2 = st.columns([4, 1])
            col1.text(f"📄 {fname[:20]}...")
            if col2.button("🗑️", key=f"del_{fname}"):
                if vector_store.delete_document(fname):
                    st.toast(f"Deleted {fname}")
                    st.rerun()
    else:
        st.info("No documents uploaded yet.")

# --- Main Interface ---
st.title("Research Assistant")
st.markdown("Ask questions about your uploaded documents. Powered by **Llama 3** and **ChromaDB**.")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "citations" in message and message["citations"]:
            with st.expander("Sources"):
                for cite in message["citations"]:
                    st.write(f"- {cite.get('filename')} (Page {cite.get('page_number')})")

# Chat Input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        if not retrieval_pipeline:
            st.error("Retrieval pipeline not initialized. Please check your API key.")
        else:
            with st.spinner("Searching knowledge base..."):
                try:
                    # Run RAG
                    response_data = retrieval_pipeline.run(prompt)
                    answer = response_data["answer"]
                    citations = response_data["citations"]
                    
                    st.markdown(answer)
                    if citations:
                        with st.expander("Sources"):
                            unique_cites = { (c['filename'], c['page_number']) for c in citations }
                            for f, p in unique_cites:
                                st.write(f"- {f} (Page {p})")
                    
                    # Store in history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "citations": citations
                    })
                except Exception as e:
                    st.error(f"Something went wrong: {str(e)}")

# Footer
st.divider()
st.caption("DocuMind Knowledge Engine — Built for Endee Assignment")
