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
    --bg: #0a0c10;
    --surface: #111318;
    --surface2: #181c24;
    --accent: #00d4aa;
    --accent2: #6366f1;
    --accent3: #a855f7;
    --text: #e8ecf4;
    --muted: #6b7280;
    --border: #252a35;
    --success: #10b981;
    --warning: #f59e0b;
  }

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: linear-gradient(160deg, #0a0c10 0%, #0d1117 50%, #0a0c10 100%) !important;
    color: var(--text) !important;
  }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111318 0%, #0d0f14 100%) !important;
    border-right: 1px solid var(--border);
    box-shadow: 4px 0 24px rgba(0,0,0,0.3);
  }

  /* Main container */
  .main .block-container {
    padding: 2rem 2.5rem;
    max-width: 1100px;
  }

  /* Hero header */
  .hero {
    text-align: center;
    padding: 3.5rem 0 2.5rem;
    position: relative;
  }
  .hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(0,212,170,0.15), rgba(99,102,241,0.15));
    border: 1px solid rgba(0,212,170,0.3);
    border-radius: 9999px;
    padding: 0.35rem 1rem;
    font-size: 0.75rem;
    color: var(--accent);
    letter-spacing: 1.5px;
    margin-bottom: 1rem;
    text-transform: uppercase;
    font-family: 'Space Mono', monospace;
  }
  .hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 3.25rem;
    font-weight: 700;
    letter-spacing: -2px;
    background: linear-gradient(135deg, #00d4aa 0%, #6366f1 50%, #a855f7 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
  }
  .hero-sub {
    color: var(--muted);
    font-size: 1.1rem;
    margin-top: 0.75rem;
    font-weight: 400;
    max-width: 480px;
    margin-left: auto;
    margin-right: auto;
    line-height: 1.6;
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
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
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
    background: linear-gradient(135deg, rgba(24,28,36,0.9) 0%, rgba(17,19,24,0.95) 100%);
    border: 1px solid var(--border);
    border-radius: 18px 18px 6px 18px;
    padding: 1.1rem 1.4rem;
    margin: 0.85rem 0;
    margin-left: 15%;
    font-size: 0.95rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  }
  .chat-assistant {
    background: linear-gradient(135deg, rgba(16,20,32,0.95) 0%, rgba(10,14,28,0.98) 100%);
    border: 1px solid rgba(0,212,170,0.2);
    border-radius: 18px 18px 18px 6px;
    padding: 1.1rem 1.4rem;
    margin: 0.85rem 0;
    margin-right: 15%;
    font-size: 0.95rem;
    line-height: 1.7;
    box-shadow: 0 4px 24px rgba(0,0,0,0.25), 0 0 1px rgba(0,212,170,0.1);
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
    box-shadow: 0 0 0 2px rgba(0, 212, 170, 0.2) !important;
  }

  /* Buttons */
  .stButton > button {
    background: linear-gradient(135deg, #00d4aa 0%, #6366f1 100%) !important;
    color: #fff !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 1.5rem !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.5px !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 14px rgba(0,212,170,0.25) !important;
  }
  .stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(0,212,170,0.35) !important;
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
    background: linear-gradient(90deg, rgba(0,212,170,0.06) 0%, var(--surface2) 100%);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: 10px;
    padding: 0.8rem 1.1rem;
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
    st.caption("Python, JS, configs, docs — all files indexed")
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
            "What does this repo do?",
            "What are the main classes?",
            "List all functions",
            "Where is the main entry point?",
            "What file types are in this repo?",
        ]
        for s in suggestions:
            if st.button(s, key=f"sug_{s}", use_container_width=True):
                st.session_state["suggested_q"] = s

    st.markdown("---")
    st.markdown(
        '<p style="font-size:0.7rem; color:#4b5563;">Powered by Groq · LangChain · Tree-sitter · NetworkX</p>',
        unsafe_allow_html=True
    )


# ── Main Area ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-badge">All file types supported</div>
  <p class="hero-title">🛰️ RepoRover</p>
  <p class="hero-sub">Drop any public GitHub repo — Python, JS, configs & more. Ask anything about the codebase.</p>
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
            st.success(f"✅ Loaded **{info['parsed_files']}** files · **{info['functions']}** functions · **{info['classes']}** classes. Ready to chat!")
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
    <div style="background:linear-gradient(135deg, #111318 0%, #181c24 100%); border:1px solid #252a35; border-radius:14px; padding:1.25rem 1.75rem; margin-bottom:1.5rem; box-shadow:0 4px 24px rgba(0,0,0,0.2);">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
        <div>
          <span style="font-family:'Space Mono',monospace; font-size:0.9rem; color:#00d4aa; font-weight:600;">📦 {repo_name}</span>
          <span style="font-size:0.72rem; color:#6b7280; margin-left:1rem;">{url}</span>
        </div>
        <div style="display:flex; gap:2.5rem; text-align:center;">
          <div><span style="font-family:'Space Mono',monospace; font-size:1.5rem; color:#00d4aa; font-weight:700;">{info['parsed_files']}</span><br><span style="font-size:0.68rem; color:#6b7280; text-transform:uppercase; letter-spacing:1.5px;">Files</span></div>
          <div><span style="font-family:'Space Mono',monospace; font-size:1.5rem; color:#6366f1; font-weight:700;">{info['functions']}</span><br><span style="font-size:0.68rem; color:#6b7280; text-transform:uppercase; letter-spacing:1.5px;">Functions</span></div>
          <div><span style="font-family:'Space Mono',monospace; font-size:1.5rem; color:#10b981; font-weight:700;">{info['classes']}</span><br><span style="font-size:0.68rem; color:#6b7280; text-transform:uppercase; letter-spacing:1.5px;">Classes</span></div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── Chat Interface ─────────────────────────────────────────────────────────────
if not st.session_state.graph:
    # Empty state
    st.markdown("""
    <div style="text-align:center; padding:4rem 2rem; color:#6b7280;">
      <div style="font-size:3.5rem; margin-bottom:1.25rem; opacity:0.9;">📂</div>
      <p style="font-size:1.05rem;">Enter your Groq API key and a GitHub repo URL in the sidebar, then click <strong style="color:#00d4aa;">Load Repository</strong>.</p>
      <p style="font-size:0.9rem; margin-top:0.75rem;">Works with any <em>public</em> repository — Python, JavaScript, configs, docs & more.</p>
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
