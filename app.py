import streamlit as st
from repo_loader import clone_and_build_graph
from llm_engine import answer_question

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RepoRover",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

  :root {
    --bg: #0d0f14;
    --surface: #13161e;
    --surface2: #1b1f2b;
    --accent: #00e5ff;
    --accent2: #7c6af7;
    --text: #e2e8f0;
    --muted: #64748b;
    --border: #1e2535;
    --success: #22c55e;
    --warning: #f59e0b;
  }

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
  }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
  }

  /* Main container */
  .main .block-container {
    padding: 2rem 2.5rem;
    max-width: 1100px;
  }

  /* Hero header */
  .hero {
    text-align: center;
    padding: 3rem 0 2rem;
  }
  .hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 3rem;
    font-weight: 700;
    letter-spacing: -1px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
  }
  .hero-sub {
    color: var(--muted);
    font-size: 1.05rem;
    margin-top: 0.5rem;
    font-weight: 300;
  }

  /* Stat cards */
  .stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
  }
  .stat-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
  }
  .stat-number {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
  }
  .stat-label {
    color: var(--muted);
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 0.4rem;
  }

  /* Chat messages */
  .chat-user {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 16px 16px 4px 16px;
    padding: 1rem 1.25rem;
    margin: 0.75rem 0;
    margin-left: 15%;
    font-size: 0.95rem;
  }
  .chat-assistant {
    background: linear-gradient(135deg, #0f1a2e, #111827);
    border: 1px solid #1e3a5f;
    border-radius: 16px 16px 16px 4px;
    padding: 1rem 1.25rem;
    margin: 0.75rem 0;
    margin-right: 15%;
    font-size: 0.95rem;
    line-height: 1.7;
  }
  .chat-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.4rem;
  }

  /* Input overrides */
  .stTextInput input, .stTextArea textarea {
    background-color: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
  }
  .stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(0, 229, 255, 0.15) !important;
  }

  /* Buttons */
  .stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: #000 !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.5rem !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.5px !important;
    transition: opacity 0.2s !important;
  }
  .stButton > button:hover {
    opacity: 0.85 !important;
  }

  /* Suggestion chips */
  .chip-row { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 0.5rem 0 1rem; }
  .chip {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.8rem;
    color: var(--muted);
    cursor: pointer;
    transition: all 0.2s;
    font-family: 'Space Mono', monospace;
  }
  .chip:hover { border-color: var(--accent); color: var(--accent); }

  /* Progress / status */
  .status-box {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.82rem;
    color: var(--muted);
    margin: 0.4rem 0;
  }

  /* Section divider */
  .divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
  }

  /* File tree display */
  .file-tree {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    color: var(--muted);
    max-height: 200px;
    overflow-y: auto;
    line-height: 1.8;
  }

  /* Sidebar labels */
  .sidebar-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.3rem;
  }

  /* Hide default Streamlit header/footer */
  #MainMenu, footer, header { visibility: hidden; }
  
  /* Scrollbar */
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ── Session state init ─────────────────────────────────────────────────────────
if "graph" not in st.session_state:
    st.session_state.graph = None
if "repo_info" not in st.session_state:
    st.session_state.repo_info = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "loading_logs" not in st.session_state:
    st.session_state.loading_logs = []


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="sidebar-label">🛰️ RepoRover</p>', unsafe_allow_html=True)
    st.markdown("**Chat with any public GitHub repo**")
    st.markdown("---")

    st.markdown('<p class="sidebar-label">Groq API Key</p>', unsafe_allow_html=True)
    groq_key = st.text_input(
        "", type="password", placeholder="gsk_...",
        help="Free key at console.groq.com", label_visibility="collapsed"
    )
    if groq_key:
        st.markdown("✅ Key set")

    st.markdown('<p class="sidebar-label" style="margin-top:1rem">GitHub Repo URL</p>', unsafe_allow_html=True)
    repo_url = st.text_input(
        "", placeholder="https://github.com/user/repo",
        label_visibility="collapsed"
    )

    load_btn = st.button("🚀 Load Repository", use_container_width=True)

    if st.session_state.repo_info:
        st.markdown("---")
        info = st.session_state.repo_info
        st.markdown('<p class="sidebar-label">Repo Stats</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Files", info.get("parsed_files", 0))
            st.metric("Classes", info.get("classes", 0))
        with col2:
            st.metric("Functions", info.get("functions", 0))
            st.metric("Entities", info.get("total_entities", 0))

        st.markdown("---")
        st.markdown('<p class="sidebar-label">Try asking</p>', unsafe_allow_html=True)
        suggestions = [
            "What are the main classes?",
            "List all functions",
            "What does this repo do?",
            "Where is the main entry point?",
            "What files are there?",
        ]
        for s in suggestions:
            if st.button(s, key=f"sug_{s}", use_container_width=True):
                st.session_state["suggested_q"] = s

    st.markdown("---")
    st.markdown(
        '<p style="font-size:0.72rem; color:#475569;">Powered by Groq · LangChain · Tree-sitter · NetworkX</p>',
        unsafe_allow_html=True
    )


# ── Main Area ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <p class="hero-title">🛰️ RepoRover</p>
  <p class="hero-sub">Drop any public GitHub repo. Ask anything about its code.</p>
</div>
""", unsafe_allow_html=True)


# ── Load Repo Logic ────────────────────────────────────────────────────────────
if load_btn:
    if not groq_key:
        st.error("Please enter your Groq API key in the sidebar.")
    elif not repo_url:
        st.error("Please enter a GitHub repository URL.")
    else:
        st.session_state.graph = None
        st.session_state.repo_info = None
        st.session_state.messages = []
        st.session_state.loading_logs = []

        logs_placeholder = st.empty()
        status_lines = []

        def on_progress(msg):
            status_lines.append(msg)
            logs_placeholder.markdown(
                "\n".join(f'<div class="status-box">{l}</div>' for l in status_lines[-6:]),
                unsafe_allow_html=True
            )

        try:
            graph, info = clone_and_build_graph(repo_url, progress_callback=on_progress)
            st.session_state.graph = graph
            st.session_state.repo_info = info
            st.session_state.loading_logs = status_lines
            logs_placeholder.empty()
            st.success(f"✅ Loaded **{info['parsed_files']}** files · **{info['functions']}** functions · **{info['classes']}** classes. Start chatting!")
            st.rerun()
        except Exception as e:
            logs_placeholder.empty()
            st.error(f"❌ {e}")


# ── Stats bar (when repo loaded) ───────────────────────────────────────────────
if st.session_state.repo_info:
    info = st.session_state.repo_info
    url = info.get("repo_url", "")
    repo_name = url.rstrip("/").split("/")[-1] if url else "Repository"

    st.markdown(f"""
    <div style="background:#13161e; border:1px solid #1e2535; border-radius:12px; padding:1rem 1.5rem; margin-bottom:1.5rem;">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <span style="font-family:'Space Mono',monospace; font-size:0.85rem; color:#00e5ff;">📦 {repo_name}</span>
          <span style="font-size:0.75rem; color:#475569; margin-left:1rem;">{url}</span>
        </div>
        <div style="display:flex; gap:2rem; text-align:center;">
          <div><span style="font-family:'Space Mono',monospace; font-size:1.4rem; color:#00e5ff;">{info['parsed_files']}</span><br><span style="font-size:0.7rem; color:#64748b; text-transform:uppercase; letter-spacing:1px;">Files</span></div>
          <div><span style="font-family:'Space Mono',monospace; font-size:1.4rem; color:#7c6af7;">{info['functions']}</span><br><span style="font-size:0.7rem; color:#64748b; text-transform:uppercase; letter-spacing:1px;">Functions</span></div>
          <div><span style="font-family:'Space Mono',monospace; font-size:1.4rem; color:#22c55e;">{info['classes']}</span><br><span style="font-size:0.7rem; color:#64748b; text-transform:uppercase; letter-spacing:1px;">Classes</span></div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── Chat Interface ─────────────────────────────────────────────────────────────
if not st.session_state.graph:
    # Empty state
    st.markdown("""
    <div style="text-align:center; padding:4rem 2rem; color:#475569;">
      <div style="font-size:3rem; margin-bottom:1rem;">📂</div>
      <p style="font-size:1rem;">Enter a Groq API key and a GitHub repo URL in the sidebar, then click <strong style="color:#00e5ff;">Load Repository</strong>.</p>
      <p style="font-size:0.85rem; margin-top:0.5rem;">Works with any <em>public</em> Python repository.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-user">
              <div class="chat-label">You</div>
              {msg['content']}
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-assistant">
              <div class="chat-label">🛰️ RepoRover</div>
              {msg['content']}
            </div>""", unsafe_allow_html=True)

    # Handle suggested question from sidebar
    suggested = st.session_state.pop("suggested_q", None)

    # Chat input
    user_input = st.chat_input("Ask anything about this codebase...")

    question = suggested or user_input

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        st.markdown(f"""
        <div class="chat-user">
          <div class="chat-label">You</div>
          {question}
        </div>""", unsafe_allow_html=True)

        with st.spinner("🛰️ Analyzing..."):
            try:
                result = answer_question(question, st.session_state.graph, groq_key)
                answer = result["answer"]
            except Exception as e:
                answer = f"⚠️ Error: {e}"

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.markdown(f"""
        <div class="chat-assistant">
          <div class="chat-label">🛰️ RepoRover</div>
          {answer}
        </div>""", unsafe_allow_html=True)

    # Clear chat button
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
