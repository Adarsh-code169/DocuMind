import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="RAG Research Assistant", page_icon="📚", layout="wide")

# --- custom CSS for a polished look ---
st.markdown("""
<style>
    /* main background */
    .stApp {
        background: #9BB4C0;
        color: #703B3B;
    }

    /* Global text color override */
    .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp span, .stApp label {
        color: #703B3B !important;
    }

    /* sidebar */
    section[data-testid="stSidebar"] {
        background: #8aa4b0;
        border-right: 1px solid rgba(112, 59, 59, 0.2);
    }

    /* header styling */
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #703B3B;
        margin-bottom: 0;
    }
    .sub-title {
        font-size: 1rem;
        color: rgba(112, 59, 59, 0.8);
        margin-top: 0;
        margin-bottom: 2rem;
    }

    /* chat messages */
    .stChatMessage {
        border-radius: 12px;
        border: 1px solid rgba(112, 59, 59, 0.2);
        background: rgba(255, 255, 255, 0.3) !important;
    }

    /* buttons */
    .stButton > button {
        background: #703B3B;
        color: #FAFAFA99 !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: #8b4a4a;
        box-shadow: 0 4px 15px rgba(112, 59, 59, 0.3);
    }

    /* specific style for clear chat button in sidebar (the second/last button) */
    section[data-testid="stSidebar"] .stButton:nth-last-of-type(1) button {
        background: #FAFAFA !important;
        color: #703B3B !important;
        border: 1px solid rgba(112, 59, 59, 0.2) !important;
    }
    section[data-testid="stSidebar"] .stButton:nth-last-of-type(1) button:hover {
        background: #ffffff !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
    }

    /* metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #703B3B !important;
    }

    /* status badge overrides */
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1rem;
    }
    .status-online {
        background: rgba(34, 197, 94, 0.2);
        color: #166534 !important;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    .status-offline {
        background: rgba(239, 68, 68, 0.2);
        color: #991b1b !important;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    /* welcome card */
    .welcome-card {
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(112, 59, 59, 0.2);
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin: 3rem auto;
        max-width: 600px;
    }
    .welcome-card h3 {
        color: #703B3B;
        margin-bottom: 1rem;
    }
    .welcome-card p {
        color: rgba(112, 59, 59, 0.9);
        font-size: 0.95rem;
    }

    hr {
        border-color: rgba(112, 59, 59, 0.15);
    }
</style>
""", unsafe_allow_html=True)

# --- sidebar ---
with st.sidebar:
    st.markdown("### 📄 Document Upload")
    st.markdown('<p style="color: #94a3b8; font-size: 0.85rem;">Upload research papers to start asking questions</p>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"], label_visibility="collapsed")

    if uploaded_file and st.button("⬆️ Process Document", use_container_width=True):
        with st.spinner("Processing..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            try:
                resp = requests.post(f"{API_URL}/upload", files=files, timeout=120)
                if resp.status_code == 200:
                    result = resp.json()
                    st.success(f"✅ {result['message']}")
                    st.session_state["doc_count"] = st.session_state.get("doc_count", 0) + 1
                else:
                    st.error(f"Error: {resp.json().get('detail', resp.text)}")
            except requests.ConnectionError:
                st.error("Can't connect to backend — is FastAPI running?")
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()

    # stats section
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📄 Docs", st.session_state.get("doc_count", 0))
    with col2:
        st.metric("💬 Chats", len(st.session_state.get("messages", [])) // 2)

    # backend health check
    try:
        health = requests.get(f"{API_URL}/health", timeout=3)
        if health.status_code == 200:
            st.markdown('<span class="status-badge status-online">● Backend Online</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge status-offline">● Backend Offline</span>', unsafe_allow_html=True)
    except:
        st.markdown('<span class="status-badge status-offline">● Backend Offline</span>', unsafe_allow_html=True)

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # footer
    st.markdown("---")
    st.markdown(
        '<p style="color: #64748b; font-size: 0.75rem; text-align: center;">'
        'Built with Endee Vector DB<br>& Groq (Llama 3.1)'
        '</p>',
        unsafe_allow_html=True
    )

# --- main area ---
st.markdown('<h1 class="main-title">📚 Intelligent Research Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Upload papers, ask questions, get cited answers — powered by RAG</p>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# show welcome card if no messages yet
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <h3>📄 Ask Questions About Your Research Paper</h3>
<p>
    Upload a research paper using the sidebar and start asking questions.<br><br>
    I'll scan the document and return answers along with the exact page citations.
</p>
    </div>
    """, unsafe_allow_html=True)

# render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("citations"):
            with st.expander("📖 View Sources"):
                for i, c in enumerate(msg["citations"]):
                    st.markdown(f"**Source {i+1}** — `{c.get('filename')}` (Page {c.get('page_number')})")

# handle new message
if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching & generating answer..."):
            try:
                history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
                resp = requests.post(f"{API_URL}/chat", json={"message": prompt, "history": history}, timeout=60)

                if resp.status_code == 200:
                    data = resp.json()
                    st.markdown(data["answer"])

                    citations = data.get("citations", [])
                    if citations:
                        with st.expander("📖 View Sources"):
                            for i, c in enumerate(citations):
                                st.markdown(f"**Source {i+1}** — `{c.get('filename')}` (Page {c.get('page_number')})")

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data["answer"],
                        "citations": citations
                    })
                else:
                    st.error(f"Error: {resp.json().get('detail', resp.text)}")
            except requests.ConnectionError:
                st.error("Can't reach the backend — make sure FastAPI is running")
            except Exception as e:
                st.error(f"Something went wrong: {e}")
