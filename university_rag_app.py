"""
University RAG – Streamlit Interface
=====================================
Run with:
    streamlit run university_rag_app.py

Requirements (add to your existing env):
    pip install streamlit
"""

import os
import time
import json
from getpass import getpass

import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="MS-ADS Knowledge Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Source+Sans+3:wght@300;400;600&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
}

/* ── Background ── */
.stApp {
    background: linear-gradient(135deg, #0f1923 0%, #1a2a3a 50%, #0f1923 100%);
    min-height: 100vh;
}

/* ── Header ── */
.uni-header {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    border-bottom: 1px solid rgba(212, 175, 55, 0.25);
    margin-bottom: 2rem;
}
.uni-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    font-weight: 700;
    color: #f0e6c8;
    letter-spacing: 0.02em;
    margin: 0 0 0.4rem;
}
.uni-header p {
    color: #8fa8be;
    font-size: 1.05rem;
    font-weight: 300;
    margin: 0;
}
.gold-line {
    width: 60px;
    height: 3px;
    background: linear-gradient(90deg, #d4af37, #f0c040);
    margin: 0.9rem auto 0;
    border-radius: 2px;
}
.uni-logo {
    display: block;
    margin: 0 auto 1.2rem;
    height: 80px;
    width: auto;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #111c27 !important;
    border-right: 1px solid rgba(212,175,55,0.15);
}
.sidebar-title {
    font-family: 'Playfair Display', serif;
    color: #d4af37;
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(212,175,55,0.2);
}
.sidebar-label {
    color: #8fa8be;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 1.2rem 0 0.4rem;
}

/* ── Strategy badge ── */
.strategy-badge {
    display: inline-block;
    background: rgba(212,175,55,0.12);
    border: 1px solid rgba(212,175,55,0.35);
    color: #d4af37;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 0.25rem 0.7rem;
    border-radius: 20px;
    margin-bottom: 1.2rem;
}

/* ── Answer card ── */
.answer-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(212,175,55,0.2);
    border-left: 4px solid #d4af37;
    border-radius: 8px;
    padding: 1.5rem 1.8rem;
    margin: 1.2rem 0;
    color: #e8dfc8;
    font-size: 1.05rem;
    line-height: 1.75;
}
.answer-label {
    font-family: 'Playfair Display', serif;
    color: #d4af37;
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}

/* ── Source cards ── */
.sources-header {
    font-family: 'Playfair Display', serif;
    color: #8fa8be;
    font-size: 0.88rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 1.8rem 0 0.8rem;
}
.source-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(143,168,190,0.15);
    border-radius: 6px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
    transition: border-color 0.2s;
}
.source-card:hover { border-color: rgba(212,175,55,0.3); }
.source-url {
    color: #6ba3c8;
    font-size: 0.8rem;
    font-family: 'Source Code Pro', monospace;
    word-break: break-all;
    margin-bottom: 0.4rem;
}
.source-snippet {
    color: #7a8fa0;
    font-size: 0.85rem;
    line-height: 1.55;
}

/* ── History item ── */
.history-item {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(143,168,190,0.1);
    border-radius: 6px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    cursor: pointer;
    transition: all 0.2s;
}
.history-item:hover {
    border-color: rgba(212,175,55,0.25);
    background: rgba(212,175,55,0.04);
}
.history-q {
    color: #c8d8e4;
    font-size: 0.88rem;
    line-height: 1.4;
}
.history-time {
    color: #4a6070;
    font-size: 0.75rem;
    margin-top: 0.25rem;
}

/* ── Metrics ── */
.metrics-row {
    display: flex;
    gap: 1rem;
    margin: 1rem 0 1.5rem;
}
.metric-chip {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(143,168,190,0.15);
    border-radius: 6px;
    padding: 0.5rem 1rem;
    text-align: center;
    flex: 1;
}
.metric-val {
    color: #d4af37;
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    font-weight: 700;
}
.metric-lbl {
    color: #5a7080;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── Input area ── */
.stTextArea textarea {
    background: #16222f !important;
    border: 1px solid rgba(143,168,190,0.2) !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 1rem !important;
    width: 100% !important;
}

/* ── Full-width content area ── */
.block-container {
    max-width: 100% !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
}
.stTextArea textarea:focus {
    background: #16222f !important;
    border-color: rgba(212,175,55,0.5) !important;
    color: #e6edf3 !important; 
    box-shadow: 0 0 0 2px rgba(212,175,55,0.1) !important;
}
.stButton > button {
    background: linear-gradient(135deg, #c9972a, #d4af37) !important;
    color: #0f1923 !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.04em !important;
    padding: 0.5rem 2rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(212,175,55,0.3) !important;
}

/* ── Selectbox / slider labels ── */
.stSelectbox label, .stSlider label, .stRadio label {
    color: #8fa8be !important;
    font-size: 0.85rem !important;
}
div[data-testid="stSelectbox"] > div {
    background: rgba(255,255,255,0.04) !important;
    border-color: rgba(143,168,190,0.2) !important;
    color: #c8d8e4 !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #d4af37 !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.03) !important;
    color: #8fa8be !important;
    border-color: rgba(143,168,190,0.1) !important;
}

/* ── Divider ── */
hr { border-color: rgba(212,175,55,0.12) !important; }

/* ── Success / info / warning ── */
.stAlert { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)


# ── Lazy imports (so Streamlit can render even before RAG libs install) ────────

@st.cache_resource(show_spinner=False)
def load_rag_pipeline(openai_key: str, persist_dir: str, collection: str, k: int):
    """Build (or reload) the retriever + LLM.  Cached across reruns."""
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    from langchain_community.vectorstores import Chroma
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough

    embedding_model = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=openai_key,
    )
    vectorstore = Chroma(
        collection_name=collection,
        embedding_function=embedding_model,
        persist_directory=persist_dir,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=openai_key)

    RAG_PROMPT = """You are a knowledgeable assistant for the MS-ADS program at the University of Chicago.
Use ONLY the following context to answer the question.
If the answer is not in the context, say exactly: "I don't have that information in the knowledge base."

Context:
{context}

Question: {question}

Answer:"""

    prompt = ChatPromptTemplate.from_template(RAG_PROMPT)

    def format_docs(docs):
        return "\n\n---\n\n".join(
            f"[Source: {d.metadata['source']}]\n{d.page_content}" for d in docs
        )

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return retriever, llm, rag_chain, prompt, format_docs


# ── Query strategy runners ────────────────────────────────────────────────────

def run_standard(query, retriever, rag_chain, **_):
    docs = retriever.invoke(query)
    answer = rag_chain.invoke(query)
    return answer, docs


def run_multi_query(query, retriever, llm, prompt, format_docs, n_alt=3, **_):
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnableLambda

    mq_prompt = ChatPromptTemplate.from_template(
        "Generate {n} alternative phrasings of this question, one per line, no numbering.\n\nQuestion: {question}"
    )
    chain = (
        mq_prompt | llm | StrOutputParser()
        | RunnableLambda(lambda s: [q.strip() for q in s.strip().split("\n") if q.strip()])
    )
    alternatives = chain.invoke({"question": query, "n": n_alt})
    all_queries  = [query] + alternatives
    docs_lists   = [retriever.invoke(q) for q in all_queries]

    seen, unique = set(), []
    for docs in docs_lists:
        for doc in docs:
            key = doc.page_content[:100]
            if key not in seen:
                seen.add(key)
                unique.append(doc)

    context = "\n\n---\n\n".join(
        f"[Source: {d.metadata['source']}]\n{d.page_content}" for d in unique
    )
    answer = (prompt | llm | StrOutputParser()).invoke({"context": context, "question": query})
    return answer, unique


def run_rag_fusion(query, retriever, llm, prompt, format_docs, n_alt=3, **_):
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnableLambda

    mq_prompt = ChatPromptTemplate.from_template(
        "Generate {n} alternative phrasings of this question, one per line, no numbering.\n\nQuestion: {question}"
    )
    chain = (
        mq_prompt | llm | StrOutputParser()
        | RunnableLambda(lambda s: [q.strip() for q in s.strip().split("\n") if q.strip()])
    )
    alternatives = chain.invoke({"question": query, "n": n_alt})
    all_queries  = [query] + alternatives
    docs_lists   = [retriever.invoke(q) for q in all_queries]

    # RRF
    scores, doc_lookup = {}, {}
    for results in docs_lists:
        for rank, doc in enumerate(results):
            key = doc.page_content[:100]
            doc_lookup[key] = doc
            scores[key] = scores.get(key, 0) + 1.0 / (60 + rank + 1)
    ranked   = sorted(scores.items(), key=lambda x: -x[1])
    top_docs = [doc_lookup[key] for key, _ in ranked[:6]]

    context = "\n\n---\n\n".join(
        f"[Source: {d.metadata['source']}]\n{d.page_content}" for d in top_docs
    )
    answer = (prompt | llm | StrOutputParser()).invoke({"context": context, "question": query})
    return answer, top_docs


def run_hyde(query, retriever, llm, prompt, format_docs, **_):
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    hyde_p = ChatPromptTemplate.from_template(
        "Write a detailed, factual university website page excerpt that answers this question.\n\nQuestion: {question}\n\nAnswer:"
    )
    hypothetical = (hyde_p | llm | StrOutputParser()).invoke({"question": query})
    docs   = retriever.invoke(hypothetical)
    context = "\n\n---\n\n".join(
        f"[Source: {d.metadata['source']}]\n{d.page_content}" for d in docs
    )
    answer = (prompt | llm | StrOutputParser()).invoke({"context": context, "question": query})
    return answer, docs


def run_step_back(query, retriever, llm, prompt, format_docs, **_):
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    sb_p = ChatPromptTemplate.from_template(
        "Given a specific question about a university, generate a broader background question.\n\nSpecific: {question}\nAbstract:"
    )
    abstract = (sb_p | llm | StrOutputParser()).invoke({"question": query})

    specific_docs = retriever.invoke(query)
    abstract_docs = retriever.invoke(abstract)

    seen, combined = set(), []
    for doc in specific_docs + abstract_docs:
        key = doc.page_content[:100]
        if key not in seen:
            seen.add(key)
            combined.append(doc)

    sb_answer_p = ChatPromptTemplate.from_template(
        "You are a university assistant. Use the context (specific + background) to answer.\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    )
    context = "\n\n---\n\n".join(
        f"[Source: {d.metadata['source']}]\n{d.page_content}" for d in combined
    )
    answer = (sb_answer_p | llm | StrOutputParser()).invoke({"context": context, "question": query})
    return answer, combined


STRATEGY_RUNNERS = {
    "Standard RAG":        run_standard,
    "Multi-Query":         run_multi_query,
    "RAG-Fusion + RRF":    run_rag_fusion,
    "HyDE":                run_hyde,
    "Step-Back":           run_step_back,
}

STRATEGY_DESCRIPTIONS = {
    "Standard RAG":     "Direct similarity search — fast and reliable for clear, specific questions.",
    "Multi-Query":      "Generates multiple phrasings of your question and unions the results — great for ambiguous queries.",
    "RAG-Fusion + RRF": "Multiple phrasings reranked by Reciprocal Rank Fusion — best overall retrieval quality.",
    "HyDE":             "Generates a hypothetical answer first, then searches — bridges casual questions and formal document language.",
    "Step-Back":        "Retrieves both specific and background context — ideal for questions that need foundational knowledge.",
}


# ── Session state initialisation ─────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []      # list of {query, answer, docs, strategy, elapsed}
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0
if "total_sources" not in st.session_state:
    st.session_state.total_sources = 0


# ── Header moved inside col_main ────────────────────────────────────────────


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">⚙ Configuration</div>', unsafe_allow_html=True)

    # API Key
    st.markdown('<div class="sidebar-label">OpenAI API Key</div>', unsafe_allow_html=True)
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.environ.get("OPENAI_API_KEY", ""),
        placeholder="sk-...",
        label_visibility="collapsed",
    )

    # Vector store path
    st.markdown('<div class="sidebar-label">Vector Store Path</div>', unsafe_allow_html=True)
    persist_dir = st.text_input(
        "Vector Store Path",
        value= "./chroma_university_kb",
        label_visibility="collapsed",
    )

    # Collection name
    st.markdown('<div class="sidebar-label">Collection Name</div>', unsafe_allow_html=True)
    collection = st.text_input(
        "Collection Name",
        value="university_kb",
        label_visibility="collapsed",
    )

    # Retrieval k
    st.markdown('<div class="sidebar-label">Chunks to Retrieve (k)</div>', unsafe_allow_html=True)
    k_val = st.slider("k", min_value=2, max_value=12, value=6, label_visibility="collapsed")

    # Strategy selector
    st.markdown('<div class="sidebar-label">Query Strategy</div>', unsafe_allow_html=True)
    strategy = st.selectbox(
        "Strategy",
        options=list(STRATEGY_RUNNERS.keys()),
        index=2,           # default: RAG-Fusion + RRF
        label_visibility="collapsed",
    )
    st.caption(STRATEGY_DESCRIPTIONS[strategy])

    st.markdown("---")

    # Session metrics
    st.markdown('<div class="sidebar-title">📊 Session Stats</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Queries", st.session_state.total_queries)
    with col2:
        st.metric("Avg Sources", (
            round(st.session_state.total_sources / st.session_state.total_queries, 1)
            if st.session_state.total_queries > 0 else 0
        ))

    # Clear history
    if st.button("🗑 Clear History", use_container_width=True):
        st.session_state.history = []
        st.session_state.total_queries = 0
        st.session_state.total_sources = 0
        st.rerun()

    st.markdown("---")

    # Query history
    if st.session_state.history:
        st.markdown('<div class="sidebar-title">🕑 Recent Questions</div>', unsafe_allow_html=True)
        for i, item in enumerate(reversed(st.session_state.history[-8:])):
            short_q = item["query"][:60] + ("..." if len(item["query"]) > 60 else "")
            st.markdown(
                f'<div class="history-item">'
                f'<div class="history-q">{short_q}</div>'
                f'<div class="history-time">⏱ {item["elapsed"]:.1f}s · {item["strategy"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ── Main content ──────────────────────────────────────────────────────────────
col_main = st.container()

with col_main:

    # ── Header ──
    st.markdown(f"""
<div class="uni-header">
  <img
    class="uni-logo"
    src="https://raw.githubusercontent.com/amadan1-ai/RAG-MSADS/main/logo-background.svg"
    alt="University of Chicago"
  />
  <h1>MS-ADS Knowledge Assistant</h1>
  <div class="gold-line"></div>
</div>
""", unsafe_allow_html=True)

    # Query input
    query = st.text_area(
        "Your Question",
        placeholder="e.g. What are the admission requirements for the MBA program?",
        height=100,
        label_visibility="collapsed",
    )

    btn_col, tag_col = st.columns([1, 3])
    with btn_col:
        submitted = st.button("Ask →", use_container_width=True)
    with tag_col:
        st.markdown(
            f'<div style="padding-top:0.55rem">'
            f'<span class="strategy-badge">{strategy}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Sample questions
    with st.expander("💡 Sample questions to try"):
        samples = [
            "What undergraduate majors are available in the College of Engineering?",
            "How do I apply for on-campus housing?",
            "What research centers focus on artificial intelligence?",
            "What financial aid is available for graduate students?",
            "How do I contact the Office of International Student Services?",
            "What are the library hours and remote access options?",
        ]
        for s in samples:
            if st.button(s, key=f"sample_{s[:30]}"):
                query = s
                submitted = True

    # ── Run query ──
    if submitted and query.strip():
        if not api_key:
            st.error("Please enter your OpenAI API key in the sidebar.")
        elif not os.path.exists(persist_dir):
            st.error(f"Vector store not found at `{persist_dir}`. Run the RAG notebook to build it first.")
        else:
            with st.spinner("Searching knowledge base…"):
                try:
                    retriever, llm, rag_chain, prompt, format_docs = load_rag_pipeline(
                        api_key, persist_dir, collection, k_val
                    )
                    runner = STRATEGY_RUNNERS[strategy]

                    t0 = time.time()
                    answer, docs = runner(
                        query,
                        retriever=retriever,
                        llm=llm,
                        rag_chain=rag_chain,
                        prompt=prompt,
                        format_docs=format_docs,
                    )
                    elapsed = time.time() - t0

                    # Save to history
                    st.session_state.history.append({
                        "query":    query,
                        "answer":   answer,
                        "docs":     docs,
                        "strategy": strategy,
                        "elapsed":  elapsed,
                    })
                    st.session_state.total_queries += 1
                    st.session_state.total_sources += len(docs)

                except Exception as e:
                    st.error(f"Error: {e}")
                    st.stop()

    # ── Display latest result ──
    if st.session_state.history:
        latest = st.session_state.history[-1]

        # Metrics row
        st.markdown(
            f'<div class="metrics-row">'
            f'  <div class="metric-chip"><div class="metric-val">{latest["elapsed"]:.1f}s</div><div class="metric-lbl">Response Time</div></div>'
            f'  <div class="metric-chip"><div class="metric-val">{len(latest["docs"])}</div><div class="metric-lbl">Sources Found</div></div>'
            f'  <div class="metric-chip"><div class="metric-val">{len(latest["answer"].split())}</div><div class="metric-lbl">Answer Words</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Question echo
        st.markdown(
            f'<div style="color:#8fa8be;font-size:0.85rem;text-transform:uppercase;'
            f'letter-spacing:0.08em;margin-bottom:0.4rem;">Question</div>'
            f'<div style="color:#c8d8e4;font-size:1.05rem;font-style:italic;'
            f'margin-bottom:0.5rem;">"{latest["query"]}"</div>',
            unsafe_allow_html=True,
        )

        # Answer card
        
        st.markdown(
            f'<div class="answer-card">'
            f'  <div class="answer-label">Answer</div>'
            f'  {latest["answer"]}'
            f'</div>',
            unsafe_allow_html=True,
        )
        # Sources
        if latest["docs"]:
            st.markdown('<div class="sources-header">📄 Retrieved Sources</div>', unsafe_allow_html=True)
        
            for i, doc in enumerate(latest["docs"], 1):
                url     = doc.metadata.get("source", "Unknown source")
                title   = doc.metadata.get("title", "")
                snippet = doc.page_content[:280].replace("\n", " ")
        
                # Build title HTML safely
                title_html = ""
                if title:
                    title_html = (
                        f'<div style="color:#9ab0c0;'
                        f'font-size:0.82rem;margin-bottom:0.3rem;">{title}</div>'
                    )
        
                # Final card
                card_html = (
                    f'<div class="source-card">'
                    f'  <div class="source-url">📎 {url}</div>'
                    f'  {title_html}'
                    f'  <div class="source-snippet">{snippet}…</div>'
                    f'</div>'
                )
        
                st.markdown(card_html, unsafe_allow_html=True)


        # Older results in expander
        if len(st.session_state.history) > 1:
            st.markdown("---")
            with st.expander(f"📚 Previous answers ({len(st.session_state.history) - 1})"):
                for item in reversed(st.session_state.history[:-1]):
                    st.markdown(
                        f'<div style="color:#8fa8be;font-size:0.85rem;font-style:italic;'
                        f'margin:0.8rem 0 0.2rem;">"{item["query"]}"</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f'<div style="color:#c0b090;font-size:0.9rem;line-height:1.6;'
                        f'margin-bottom:0.4rem;">{item["answer"][:500]}'
                        f'{"..." if len(item["answer"]) > 500 else ""}</div>',
                        unsafe_allow_html=True,
                    )
                    st.caption(f"Strategy: {item['strategy']} · {item['elapsed']:.1f}s · {len(item['docs'])} sources")
                    st.markdown("---")

    elif not submitted:
        # Empty state
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;color:#3a5060;">
            <div style="font-size:3rem;margin-bottom:1rem;">🎓</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.3rem;color:#4a6878;margin-bottom:0.5rem;">
                Ready to answer your questions
            </div>
            <div style="font-size:0.9rem;color:#2e4050;">
                Type a question above or choose a sample from the suggestions
            </div>
        </div>
        """, unsafe_allow_html=True)
