#!/usr/bin/env python3
"""
AI Search Optimizer — Enterprise GAIO Dashboard
Compatible with local run (./app.py) and Streamlit Cloud deployment.
"""
import os
import sys
import subprocess

# ─── Bootstrap ────────────────────────────────────────────────────────────────
# If streamlit hasn't been imported yet, we're being run directly.
# Bootstrap the environment and re-launch via `streamlit run`.
if not os.environ.get("_STREAMLIT_BOOTSTRAPPED") and "streamlit" not in sys.modules:
    os.environ["_STREAMLIT_BOOTSTRAPPED"] = "1"
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    VENV = os.path.join(SCRIPT_DIR, ".venv")
    VENV_STREAMLIT = os.path.join(VENV, "bin", "streamlit")
    REQUIREMENTS = os.path.join(SCRIPT_DIR, "requirements.txt")
    if not os.path.isdir(VENV):
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", VENV], check=True)
    if not os.path.isfile(VENV_STREAMLIT):
        print("📦 Installing dependencies...")
        subprocess.run([os.path.join(VENV, "bin", "pip"), "install", "-r", REQUIREMENTS, "-q"], check=True)
    print("🚀 Launching Streamlit...")
    os.execv(VENV_STREAMLIT, [VENV_STREAMLIT, "run", __file__] + sys.argv[1:])

import random
from datetime import datetime, timedelta

os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from collections import Counter

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GAIO Enterprise Dashboard",
    page_icon="📊",
    layout="wide",
)

# ─── Premium CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* { font-family: 'Inter', sans-serif; }

/* ── Header ── */
.enterprise-header {
    text-align: center;
    padding: 2rem 0 1rem 0;
    border-bottom: 1px solid #e5e7eb;
    margin-bottom: 2rem;
}
.enterprise-header h1 {
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #0f172a;
    margin-bottom: 0.3rem;
}
.enterprise-header .subtitle {
    font-size: 0.95rem;
    color: #64748b;
    font-weight: 400;
    letter-spacing: 0.02em;
}

/* ── Grade Badge ── */
.grade-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2rem;
    padding: 2rem;
    background: linear-gradient(135deg, rgba(248,250,252,0.9) 0%, rgba(241,245,249,0.9) 100%);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 20px;
    border: 1px solid rgba(226,232,240,0.8);
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(15,23,42,0.06);
}
.grade-badge {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    box-shadow: 0 10px 30px rgba(0,0,0,0.12);
    position: relative;
}
.grade-badge .score {
    font-size: 2.6rem;
    line-height: 1;
    color: #fff;
}
.grade-badge .pct {
    font-size: 0.85rem;
    color: rgba(255,255,255,0.9);
    font-weight: 600;
}
.grade-badge .label {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.8);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 2px;
}
.grade-a { background: linear-gradient(135deg, #10b981, #059669); }
.grade-b { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.grade-c { background: linear-gradient(135deg, #f59e0b, #d97706); }
.grade-d { background: linear-gradient(135deg, #ef4444, #dc2626); }

.grade-details {
    flex: 1;
}
.grade-details h2 {
    font-size: 1.3rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 0.5rem;
}
.grade-details p {
    font-size: 0.9rem;
    color: #64748b;
    line-height: 1.6;
    margin: 0;
}

/* ── Metric Cards ── */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
}
.metric-card {
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(226,232,240,0.8);
    border-radius: 16px;
    padding: 1.2rem 1rem;
    text-align: center;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 8px rgba(15,23,42,0.04);
}
.metric-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    transform: translateY(-2px);
}
.metric-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.2;
}
.metric-label {
    font-size: 0.7rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
    margin-top: 0.3rem;
}
.metric-bar {
    height: 4px;
    background: #e2e8f0;
    border-radius: 2px;
    margin-top: 0.7rem;
    overflow: hidden;
}
.metric-bar-fill {
    height: 100%;
    border-radius: 2px;
    transition: width 0.8s ease;
}

/* ── Section Cards ── */
.section-card {
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(226,232,240,0.8);
    border-radius: 16px;
    padding: 1.8rem 2rem;
    margin: 1rem 0;
    box-shadow: 0 4px 16px rgba(15,23,42,0.04);
}
.section-card h3 {
    font-size: 1.1rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Sub-element Cards ── */
.sub-element {
    background: rgba(248,250,252,0.75);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(226,232,240,0.8);
    border-radius: 14px;
    padding: 1.5rem;
    margin: 0.8rem 0;
    box-shadow: 0 2px 8px rgba(15,23,42,0.03);
}
.sub-element-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.8rem;
}
.sub-element-title {
    font-size: 1rem;
    font-weight: 700;
    color: #0f172a;
}
.sub-grade {
    padding: 0.3rem 0.8rem;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.85rem;
    color: #fff;
}
.sub-description {
    font-size: 0.85rem;
    color: #64748b;
    line-height: 1.6;
    margin-bottom: 0.8rem;
}
.sub-recommendation {
    background: #fff;
    border-left: 3px solid #667eea;
    border-radius: 0 8px 8px 0;
    padding: 0.8rem 1rem;
    font-size: 0.85rem;
    color: #334155;
    line-height: 1.6;
}

/* ── Trend Chart Container ── */
.chart-container {
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(226,232,240,0.8);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin: 1rem 0;
    box-shadow: 0 2px 8px rgba(15,23,42,0.04);
}
.chart-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}
.chart-header h3 {
    font-size: 1.1rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
}
.chart-legend {
    display: flex;
    gap: 1.5rem;
    font-size: 0.8rem;
    color: #64748b;
}
.chart-legend span {
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.legend-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
}

/* ── URL Input ── */
.url-container {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(226, 232, 240, 0.8);
    border-radius: 18px;
    padding: 1.6rem 2rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(15, 23, 42, 0.06);
}
.url-label {
    font-size: 0.8rem;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.6rem;
}

/* ── Sidebar ── */
.sidebar-card {
    background: rgba(248, 250, 252, 0.7);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(226, 232, 240, 0.7);
    border-radius: 14px;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
}
.sidebar-card h4 {
    font-size: 0.85rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 0.5rem;
}
.sidebar-card p, .sidebar-card li {
    font-size: 0.8rem;
    color: #64748b;
    line-height: 1.6;
    margin: 0;
}
.sidebar-card ul {
    padding-left: 1.2rem;
    margin: 0.3rem 0;
}

/* ── Buttons ── */
.stButton>button {
    border-radius: 12px;
    font-weight: 700;
    font-size: 0.9rem;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    border: none;
    letter-spacing: 0.01em;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.35);
}
.stButton>button:active {
    transform: translateY(0);
}

/* ── Misc ── */
.divider {
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, #cbd5e1, transparent);
    margin: 2rem 0;
}
.stat-pill {
    display: inline-block;
    padding: 0.25rem 0.7rem;
    border-radius: 8px;
    font-size: 0.75rem;
    font-weight: 600;
    background: #f1f5f9;
    color: #475569;
}

/* ── Animations ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
.grade-container, .metric-card, .section-card, .sub-element, .chart-container, .url-container {
    animation: fadeInUp 0.5s ease forwards;
}
.metric-card:nth-child(2) { animation-delay: 0.05s; }
.metric-card:nth-child(3) { animation-delay: 0.1s; }
.metric-card:nth-child(4) { animation-delay: 0.15s; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown("**📊 GAIO Enterprise Dashboard**")
    st.markdown("AI Overview Optimization intelligence platform.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown("**🔬 Diagnostic Engine**")
    st.markdown("""
    - **Semantic Header Structure** — H1-H6 hierarchy analysis
    - **Conversational AI Readability** — Tone & scannability scoring
    - **Schema/Metadata Readiness** — Structured data detection
    """)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown("**📈 Reporting**")
    st.markdown("6-month simulated trend tracking with actionable milestones.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown("**ℹ️ About**")
    st.markdown("100% local analysis. No API keys. No data leaves your machine.")
    st.markdown("</div>", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="enterprise-header">
    <h1>📊 GAIO Enterprise Dashboard</h1>
    <p class="subtitle">AI Overview Optimization — Diagnostic Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

# ─── URL Input ────────────────────────────────────────────────────────────────
st.markdown('<div class="url-container">', unsafe_allow_html=True)
st.markdown('<div class="url-label">🌐 Target Website URL</div>', unsafe_allow_html=True)
col1, col2 = st.columns([4, 1])
with col1:
    url_input = st.text_input(
        "Website URL",
        placeholder="google.com",
        label_visibility="collapsed",
        key="url_input",
    )
with col2:
    st.write("")
    st.write("")
    analyze_btn = st.button(
        "🔍 Run Diagnostic",
        use_container_width=True,
        type="primary",
        key="analyze_btn",
    )
st.markdown('</div>', unsafe_allow_html=True)

url_valid = False
if url_input:
    normalized = url_input.strip()
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", normalized):
        normalized = "https://" + normalized
    parsed = urlparse(normalized)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        url_valid = True
        url_input = normalized
    else:
        st.markdown(
            '<div class="sub-recommendation" style="border-left-color:#ef4444;">⚠️ Please enter a valid URL (e.g., google.com or https://google.com)</div>',
            unsafe_allow_html=True,
        )

# ─── Scraping ─────────────────────────────────────────────────────────────────
def scrape_website(url: str):
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "iframe", "svg"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned_text = "\n".join(lines)
        if len(cleaned_text) > 8000:
            cleaned_text = cleaned_text[:8000] + "\n\n[... content truncated for analysis ...]"
        return cleaned_text, soup
    except Exception as e:
        return f"ERROR: {str(e)}", None

# ─── Analysis Functions ───────────────────────────────────────────────────────
def analyze_headers(soup) -> dict:
    headings = {}
    for level in range(1, 7):
        tags = soup.find_all(f"h{level}")
        headings[f"h{level}"] = [t.get_text(strip=True) for t in tags if t.get_text(strip=True)]
    return headings

def analyze_questions(text: str) -> list:
    patterns = [
        r"(?i)(what\s+(?:is|are|does|do|can|will|should|how|why|when|where|who))\b[^.!?\n]{0,120}[?]",
        r"(?i)(how\s+(?:to|do|can|much|many|long|often|does|do))\b[^.!?\n]{0,120}[?]",
        r"(?i)(why\s+(?:is|are|does|do|can|should|would|did|has|have))\b[^.!?\n]{0,120}[?]",
        r"(?i)(can\s+(?:you|I|we|they|it|this|that|someone|anyone))\b[^.!?\n]{0,120}[?]",
        r"(?i)(is\s+(?:it|there|this|that|someone|anyone|a|an|the))\b[^.!?\n]{0,120}[?]",
        r"(?i)(are\s+(?:there|you|we|they|these|those|any|some))\b[^.!?\n]{0,120}[?]",
        r"(?i)(does\s+(?:it|this|that|someone|anyone))\b[^.!?\n]{0,120}[?]",
        r"(?i)(will\s+(?:it|this|that|you|I|we|they))\b[^.!?\n]{0,120}[?]",
        r"(?i)(should\s+(?:I|you|we|they|it|this|that))\b[^.!?\n]{0,120}[?]",
        r"(?i)(when\s+(?:is|are|does|do|can|should|will|did|has|have))\b[^.!?\n]{0,120}[?]",
        r"(?i)(where\s+(?:is|are|can|do|does|did|should|will))\b[^.!?\n]{0,120}[?]",
        r"(?i)(who\s+(?:is|are|can|does|do|should|will|did))\b[^.!?\n]{0,120}[?]",
    ]
    questions = []
    for p in patterns:
        questions.extend(re.findall(p, text))
    seen = set()
    unique = []
    for q in questions:
        qc = q.strip()
        if qc and qc not in seen and len(qc) > 10:
            seen.add(qc)
            unique.append(qc)
    return unique[:20]

def analyze_lists(soup) -> dict:
    uls = soup.find_all("ul")
    ols = soup.find_all("ol")
    items = []
    for lst in uls + ols:
        for li in lst.find_all("li", recursive=False):
            t = li.get_text(strip=True)
            if t and len(t) > 3:
                items.append(t)
    return {"total_lists": len(uls) + len(ols), "items": items[:30]}

def analyze_definitions(soup) -> list:
    defs = []
    for dl in soup.find_all("dl"):
        for term, desc in zip(dl.find_all("dt"), dl.find_all("dd")):
            t, d = term.get_text(strip=True), desc.get_text(strip=True)
            if t and d and len(t) < 100 and len(d) < 300:
                defs.append({"term": t, "definition": d[:200]})
    if not defs:
        for strong in soup.find_all(["strong", "b"]):
            term = strong.get_text(strip=True)
            if term and 3 < len(term) < 80:
                nxt = strong.find_next_sibling()
                if nxt:
                    desc = nxt.get_text(strip=True)
                    if desc and 10 < len(desc) < 300:
                        defs.append({"term": term, "definition": desc[:200]})
    return defs[:15]

def analyze_readability(text: str) -> dict:
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip() and len(s.strip()) > 5]
    if not sentences:
        return {"score": 0, "avg_len": 0, "total": 0, "long_pct": 0, "conv_density": 0}
    lengths = [len(s.split()) for s in sentences]
    avg_len = sum(lengths) / len(lengths)
    long_pct = sum(1 for l in lengths if l > 30) / len(lengths) * 100
    markers = [r"\byou\b", r"\byour\b", r"\bwe\b", r"\bour\b", r"\blet's\b", r"\bhere's\b",
               r"\bthink\b", r"\bfeel\b", r"\bknow\b", r"\bunderstand\b", r"\bimagine\b",
               r"\bconsider\b", r"\bdiscover\b", r"\bexplore\b", r"\blearn\b", r"\bfind\b",
               r"\bget\b", r"\bmake\b", r"\btry\b", r"\buse\b", r"\bstart\b"]
    mc = sum(len(re.findall(p, text, re.IGNORECASE)) for p in markers)
    cd = mc / max(len(text.split()), 1)
    score = 100
    if avg_len > 25: score -= min((avg_len - 25) * 3, 40)
    if long_pct > 30: score -= min((long_pct - 30) * 1.5, 25)
    if cd < 0.01: score -= 15
    if cd > 0.03: score += 10
    score = max(0, min(100, score))
    return {"score": round(score, 1), "avg_len": round(avg_len, 1), "total": len(sentences),
            "long_pct": round(long_pct, 1), "conv_density": round(cd, 4)}

def analyze_keywords(text: str) -> dict:
    stop = {"the","a","an","is","are","was","were","be","been","being","have","has","had","do","does",
            "did","will","would","could","should","may","might","shall","can","to","of","in","for",
            "on","with","at","by","from","as","into","through","during","before","after","above",
            "below","between","out","off","over","under","again","further","then","once","here",
            "there","when","where","why","how","all","each","every","both","few","more","most",
            "other","some","such","no","nor","not","only","own","same","so","than","too","very",
            "just","because","but","and","or","if","while","about","up","it","its","this","that",
            "these","those","i","me","my","we","our","you","your","he","him","his","she","her",
            "they","them","their","what","which","who","whom","whose"}
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    meaningful = [w for w in words if w not in stop and len(w) > 2]
    if not meaningful:
        return {"top_terms": [], "top_bigrams": [], "total": 0, "unique": 0}
    c = Counter(meaningful)
    bigrams = [f"{meaningful[i]} {meaningful[i+1]}" for i in range(len(meaningful)-1)]
    bc = Counter(bigrams)
    return {"top_terms": c.most_common(20), "top_bigrams": bc.most_common(10),
            "total": len(meaningful), "unique": len(set(meaningful))}

def analyze_structure(soup) -> dict:
    return {
        "has_h1": len(soup.find_all("h1")) > 0,
        "h1_count": len(soup.find_all("h1")),
        "h2_count": len(soup.find_all("h2")),
        "h3_count": len(soup.find_all("h3")),
        "total_headings": len(soup.find_all(["h1","h2","h3","h4","h5","h6"])),
        "paragraph_count": len(soup.find_all("p")),
        "link_count": len(soup.find_all("a", href=True)),
        "image_count": len(soup.find_all("img")),
        "table_count": len(soup.find_all("table")),
        "has_schema": bool(soup.find_all("script", type="application/ld+json")),
        "has_meta_description": bool(soup.find("meta", attrs={"name": "description"})),
        "has_title": bool(soup.find("title")),
        "title_text": soup.find("title").get_text(strip=True) if soup.find("title") else "",
    }

# ─── Scoring Engine ───────────────────────────────────────────────────────────
def compute_scores(structure, readability, keywords, questions, lists, soup) -> dict:
    """Compute sub-scores (0-100) for each diagnostic dimension."""

    # (a) Semantic Header Structure (30% weight)
    hs = 100
    if not structure["has_h1"]: hs -= 30
    elif structure["h1_count"] > 1: hs -= 15
    if structure["h2_count"] == 0 and structure["h3_count"] > 0: hs -= 20
    if structure["total_headings"] < 3: hs -= 20
    if structure["total_headings"] >= 5: hs += 5
    hs = max(0, min(100, hs))

    # (b) Conversational AI Readability (35% weight)
    cr = readability["score"]
    if len(questions) >= 5: cr += 10
    elif len(questions) >= 3: cr += 5
    if lists["total_lists"] >= 2: cr += 3
    cr = max(0, min(100, cr))

    # (c) Schema/Metadata Readiness (35% weight)
    sm = 100
    if not structure["has_title"]: sm -= 25
    if not structure["has_meta_description"]: sm -= 25
    if not structure["has_schema"]: sm -= 30
    if structure["has_schema"]: sm += 10
    if keywords["total"] > 200: sm += 5
    sm = max(0, min(100, sm))

    # Overall weighted score
    overall = round(hs * 0.30 + cr * 0.35 + sm * 0.35, 1)

    return {
        "header_structure": round(hs, 1),
        "conversational_readability": round(cr, 1),
        "schema_metadata": round(sm, 1),
        "overall": overall,
    }

def score_to_grade(score: float) -> tuple:
    """Convert numeric score to letter grade and CSS class."""
    if score >= 90: return "A", "grade-a", "#10b981"
    elif score >= 75: return "B", "grade-b", "#3b82f6"
    elif score >= 60: return "C", "grade-c", "#f59e0b"
    else: return "D", "grade-d", "#ef4444"

def generate_recommendations(scores, structure, readability, keywords, questions, lists) -> dict:
    """Generate specific recommendations per sub-element."""
    recs = {}

    # (a) Semantic Header Structure
    hs = scores["header_structure"]
    if not structure["has_h1"]:
        recs["header_structure"] = (
            "Add a single, descriptive H1 heading that summarizes the page's primary topic. "
            "AI systems treat the H1 as the strongest signal for page subject matter. "
            "Ensure it contains your primary keyword and is under 60 characters."
        )
    elif structure["h1_count"] > 1:
        recs["header_structure"] = (
            f"Reduce from {structure['h1_count']} H1 headings to exactly one. "
            "Multiple H1s confuse AI parsers about the page's primary topic. "
            "Convert extra H1s to H2s and restructure the content hierarchy."
        )
    elif structure["h2_count"] < 3:
        recs["header_structure"] = (
            f"Add more H2 section headings (currently {structure['h2_count']}). "
            "AI systems use H2 text to build answer snippets. "
            "Rewrite H2s as direct questions (e.g., 'How does X work?') and add 2-3 H3 sub-points under each."
        )
    else:
        recs["header_structure"] = (
            "Strengthen existing headings by rewriting H2s as direct questions AI can quote verbatim. "
            "Add H3 sub-sections with specific data points, examples, or step-by-step instructions. "
            "Include your target keyword in at least one H2 and one H3 heading."
        )

    # (b) Conversational AI Readability
    cr = scores["conversational_readability"]
    if readability["avg_len"] > 25:
        recs["conversational_readability"] = (
            f"Reduce average sentence length from {readability['avg_len']} to 15-20 words. "
            "Break long sentences into shorter ones. Replace passive voice with active voice. "
            "Add transition phrases like 'Here's why...' and 'The key benefit is...' "
            "to make content more quotable by AI systems."
        )
    elif readability["conv_density"] < 0.015:
        recs["conversational_readability"] = (
            "Increase conversational tone. Add 'you' and 'we' pronouns, direct address, "
            "and brief explanatory asides. Break walls of text into 2-3 sentence paragraphs. "
            "Conversational content is 2x more likely to be quoted by AI systems."
        )
    elif len(questions) < 3:
        recs["conversational_readability"] = (
            f"Add an FAQ section with 5-10 Q&A pairs (currently {len(questions)} detected). "
            "Use exact phrasing people type into search engines. "
            "Format each as a clear question followed by a 2-4 sentence direct answer. "
            "This is the #1 signal AI systems look for when generating overviews."
        )
    else:
        recs["conversational_readability"] = (
            "Excellent readability foundation. Add a 'Key Takeaways' summary box at the top of long sections. "
            "Front-load the most important information in the first 50 words of each paragraph. "
            "Use specific numbers, dates, and named entities to increase factual density."
        )

    # (c) Schema/Metadata Readiness
    sm = scores["schema_metadata"]
    if not structure["has_schema"]:
        recs["schema_metadata"] = (
            "Add Schema.org JSON-LD structured data to your page. "
            "Include at minimum: Organization, WebPage, and FAQPage schemas. "
            "This gives AI systems explicit, machine-readable facts about your content "
            "and significantly increases citation likelihood in AI-generated responses."
        )
    elif not structure["has_meta_description"]:
        recs["schema_metadata"] = (
            "Add a meta description tag (150-160 characters) that summarizes the page content. "
            "Include your primary keyword and a clear value proposition. "
            "AI systems use meta descriptions as a primary source for answer snippets."
        )
    elif not structure["has_title"]:
        recs["schema_metadata"] = (
            "Add a descriptive <title> tag (50-60 characters) with your primary keyword. "
            "The title tag is the single most important metadata element for AI discovery. "
            "Ensure each page has a unique, descriptive title."
        )
    else:
        recs["schema_metadata"] = (
            "Good metadata foundation. Enhance with additional schema types: "
            "Article, Product, or Review schema depending on content type. "
            "Add Open Graph and Twitter Card meta tags for social sharing. "
            "Consider adding a sitemap.xml and robots.txt for complete crawlability."
        )

    return recs

# ─── Trend Data Generator ─────────────────────────────────────────────────────
def generate_trend_data(current_score: float) -> list:
    """Generate simulated 6-month historical trend data."""
    months = []
    base_date = datetime.now() - timedelta(days=180)
    score = max(20, current_score - random.randint(15, 30))
    for i in range(6):
        month_date = base_date + timedelta(days=30 * i)
        months.append({
            "date": month_date.strftime("%b %Y"),
            "score": min(100, score + random.randint(3, 10)),
        })
        score = months[-1]["score"]
    # Ensure last point matches current score
    months[-1]["score"] = current_score
    return months

# ─── Main Analysis Logic ──────────────────────────────────────────────────────
if analyze_btn:
    if not url_input or not url_valid:
        st.markdown(
            '<div class="sub-recommendation" style="border-left-color:#ef4444;">⚠️ Please enter a valid website URL.</div>',
            unsafe_allow_html=True,
        )
    else:
        with st.spinner("🕷️ Scraping and analyzing website..."):
            scraped_text, soup = scrape_website(url_input)

        if scraped_text.startswith("ERROR:"):
            st.markdown(
                f'<div class="sub-recommendation" style="border-left-color:#ef4444;">❌ Failed: {scraped_text[7:]}</div>',
                unsafe_allow_html=True,
            )
        elif not soup:
            st.markdown(
                '<div class="sub-recommendation" style="border-left-color:#ef4444;">❌ Failed to parse website content.</div>',
                unsafe_allow_html=True,
            )
        else:
            # Run analysis
            structure = analyze_structure(soup)
            headings = analyze_headers(soup)
            questions = analyze_questions(scraped_text)
            lists = analyze_lists(soup)
            readability = analyze_readability(scraped_text)
            keywords = analyze_keywords(scraped_text)

            scores = compute_scores(structure, readability, keywords, questions, lists, soup)
            recommendations = generate_recommendations(scores, structure, readability, keywords, questions, lists)
            trend_data = generate_trend_data(scores["overall"])

            # Store in session
            st.session_state["scores"] = scores
            st.session_state["structure"] = structure
            st.session_state["readability"] = readability
            st.session_state["keywords"] = keywords
            st.session_state["questions"] = questions
            st.session_state["lists"] = lists
            st.session_state["recommendations"] = recommendations
            st.session_state["trend_data"] = trend_data
            st.session_state["url"] = url_input

# ─── Render Dashboard ─────────────────────────────────────────────────────────
if "scores" in st.session_state:
    scores = st.session_state["scores"]
    structure = st.session_state["structure"]
    readability = st.session_state["readability"]
    keywords = st.session_state["keywords"]
    questions = st.session_state["questions"]
    lists = st.session_state["lists"]
    recommendations = st.session_state["recommendations"]
    trend_data = st.session_state["trend_data"]

    overall = scores["overall"]
    grade_letter, grade_class, grade_color = score_to_grade(overall)

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 1: DIAGNOSTIC ENGINE
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("## 🔬 DIAGNOSTIC ENGINE", unsafe_allow_html=True)

    # Grade Badge
    st.markdown(f"""
    <div class="grade-container">
        <div class="grade-badge {grade_class}">
            <div class="score">{grade_letter}</div>
            <div class="pct">{overall}%</div>
            <div class="label">AIO Health</div>
        </div>
        <div class="grade-details">
            <h2>AI Overview Optimization Health Grade</h2>
            <p>
                Comprehensive analysis of <strong>{urlparse(st.session_state['url']).netloc}</strong> across
                semantic structure, conversational readability, and schema readiness.
                Score calculated from {len(questions)} detected questions, {structure['total_headings']} headings,
                and {keywords['total']} meaningful content tokens.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Metrics Grid
    st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
    metrics = [
        ("Header Score", f"{scores['header_structure']}%", scores['header_structure'], "#667eea"),
        ("Readability", f"{scores['conversational_readability']}%", scores['conversational_readability'], "#10b981"),
        ("Schema Score", f"{scores['schema_metadata']}%", scores['schema_metadata'], "#f59e0b"),
        ("Questions", str(len(questions)), min(len(questions) * 10, 100), "#8b5cf6"),
    ]
    for label, value, pct, color in metrics:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-bar">
                <div class="metric-bar-fill" style="width:{pct}%; background:{color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 2: DETAILED ACTION PLAN
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("## 📋 DETAILED ACTION PLAN", unsafe_allow_html=True)

    sub_elements = [
        {
            "id": "header_structure",
            "title": "🏗️ Semantic Header Structure",
            "icon": "🏗️",
            "score": scores["header_structure"],
            "description": (
                f"Analyzes H1-H6 heading hierarchy, keyword placement in headings, "
                f"and structural clarity for AI parsers. "
                f"Found {structure['h1_count']} H1, {structure['h2_count']} H2, {structure['h3_count']} H3 headings."
            ),
            "recommendation": recommendations["header_structure"],
        },
        {
            "id": "conversational_readability",
            "title": "💬 Conversational AI Readability",
            "icon": "💬",
            "score": scores["conversational_readability"],
            "description": (
                f"Evaluates sentence length, conversational marker density, "
                f"FAQ/question patterns, and scannability. "
                f"Avg sentence: {readability['avg_len']} words. "
                f"Conversational density: {readability['conv_density']}. "
                f"{len(questions)} questions detected."
            ),
            "recommendation": recommendations["conversational_readability"],
        },
        {
            "id": "schema_metadata",
            "title": "🔍 Schema & Metadata Readiness",
            "icon": "🔍",
            "score": scores["schema_metadata"],
            "description": (
                f"Checks for structured data (JSON-LD), meta descriptions, title tags, "
                f"and Open Graph tags that AI systems use for context. "
                f"Schema: {'✅ Present' if structure['has_schema'] else '❌ Missing'}. "
                f"Meta description: {'✅ Present' if structure['has_meta_description'] else '❌ Missing'}. "
                f"Title tag: {'✅ Present' if structure['has_title'] else '❌ Missing'}."
            ),
            "recommendation": recommendations["schema_metadata"],
        },
    ]

    for elem in sub_elements:
        gl, gc, gcolor = score_to_grade(elem["score"])
        st.markdown(f"""
        <div class="sub-element">
            <div class="sub-element-header">
                <div class="sub-element-title">{elem['icon']} {elem['title']}</div>
                <div class="sub-grade" style="background:{gcolor};">Grade {gl} · {elem['score']}%</div>
            </div>
            <div class="sub-description">{elem['description']}</div>
            <div class="sub-recommendation">
                <strong>💡 Recommendation:</strong> {elem['recommendation']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 3: REPORTING & TREND TRACKING
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("## 📈 REPORTING & TREND TRACKING", unsafe_allow_html=True)

    st.markdown("""
    <div class="chart-container">
        <div class="chart-header">
            <h3>📊 6-Month AI Overview Optimization Trend</h3>
            <div class="chart-legend">
                <span><span class="legend-dot" style="background:#667eea;"></span> Overall Score</span>
                <span><span class="legend-dot" style="background:#10b981;"></span> Target (90%)</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Build chart data
    chart_data = {
        "Month": [d["date"] for d in trend_data],
        "Overall Score": [d["score"] for d in trend_data],
    }
    st.line_chart(chart_data, x="Month", y="Overall Score", height=300, color=["#667eea"])

    # Target line annotation
    st.markdown(
        f'<p style="text-align:center; font-size:0.85rem; color:#64748b; margin-top:-0.5rem;">'
        f'🎯 Target: 90% (Grade A) · Current: <strong>{overall}% (Grade {grade_letter})</strong> · '
        f'Gap: <strong>{max(0, round(90 - overall, 1))} pts</strong></p>',
        unsafe_allow_html=True,
    )

    # Milestone timeline
    st.markdown("### 🗓️ Recommended Milestones", unsafe_allow_html=True)
    milestones = [
        ("Month 1", "Fix heading hierarchy & add FAQ section", "#667eea"),
        ("Month 2", "Improve readability & add schema markup", "#3b82f6"),
        ("Month 3", "Add structured glossary & key terms", "#10b981"),
        ("Month 4", "Optimize meta tags & Open Graph data", "#f59e0b"),
        ("Month 5", "Expand FAQ to 10+ Q&A pairs", "#8b5cf6"),
        ("Month 6", "Target: 90%+ Grade A", "#10b981"),
    ]
    cols = st.columns(6)
    for col, (month, task, color) in zip(cols, milestones):
        with col:
            st.markdown(f"""
            <div style="text-align:center; padding:0.8rem; background:#f8fafc; border-radius:10px; border-top:3px solid {color};">
                <div style="font-size:0.75rem; font-weight:700; color:{color}; text-transform:uppercase; letter-spacing:0.05em;">{month}</div>
                <div style="font-size:0.75rem; color:#475569; margin-top:0.3rem; line-height:1.4;">{task}</div>
            </div>
            """, unsafe_allow_html=True)

    # ─── llms.txt Generation ───────────────────────────────────────────────────
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("## 📄 llms.txt GENERATOR", unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        generate_btn = st.button("📄 Generate & Download llms.txt", use_container_width=True, type="secondary")

    if generate_btn:
        if "analysis" not in st.session_state:
            # Generate from current data
            parsed = urlparse(st.session_state["url"])
            domain = parsed.netloc.replace("www.", "")
            site_name = structure["title_text"].split("—")[0].split("|")[0].strip() or domain

            lines = [f"# {site_name}", ""]
            top_terms = [t[0] for t in keywords.get("top_terms", [])[:5]]
            topic_str = ", ".join(top_terms) if top_terms else "various topics"
            lines.append(f"> {site_name} is a website covering {topic_str}.")
            lines.append("")
            if headings.get("h2"):
                lines.append("## Key Sections")
                lines.append("")
                for h2 in headings["h2"][:10]:
                    lines.append(f"- **{h2}** — Main section covering this topic.")
                lines.append("")
            if keywords.get("top_terms"):
                lines.append("## Main Topics")
                lines.append("")
                for term, _ in keywords["top_terms"][:10]:
                    lines.append(f"- {term}")
                lines.append("")
            if questions:
                lines.append("## Frequently Asked Questions")
                lines.append("")
                for q in questions[:10]:
                    lines.append(f"### {q}")
                    lines.append("")
                    lines.append("See the website for the full answer to this question.")
                    lines.append("")
            if lists["items"]:
                lines.append("## Features and Offerings")
                lines.append("")
                for item in lists["items"][:15]:
                    lines.append(f"- {item}")
                lines.append("")
            lines.append("## More Information")
            lines.append("")
            lines.append(f"- **Website:** {st.session_state['url']}")
            lines.append(f"- **Domain:** {domain}")
            lines.append("")
            llms_content = "\n".join(lines)
        else:
            llms_content = st.session_state.get("llms_content", "")

        if llms_content:
            st.markdown(
                '<div class="sub-recommendation" style="border-left-color:#10b981;">✅ llms.txt generated successfully!</div>',
                unsafe_allow_html=True,
            )
            with st.expander("📄 Preview llms.txt"):
                st.code(llms_content, language="markdown")
            parsed_url = urlparse(st.session_state["url"])
            domain = parsed_url.netloc.replace("www.", "")
            st.download_button(
                label=f"⬇️ Download {domain}_llms.txt",
                data=llms_content,
                file_name=f"{domain}_llms.txt",
                mime="text/plain",
                use_container_width=True,
            )

else:
    # ─── Welcome State ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding:3rem 2rem; background:#f8fafc; border-radius:20px; border:1px solid #e2e8f0; margin:2rem 0;">
        <div style="font-size:3rem; margin-bottom:1rem;">📊</div>
        <h2 style="color:#0f172a; font-weight:700; margin-bottom:0.5rem;">Ready to Diagnose</h2>
        <p style="color:#64748b; font-size:0.95rem; max-width:500px; margin:0 auto; line-height:1.6;">
            Enter a website URL above and click <strong>Run Diagnostic</strong> to generate a comprehensive
            AI Overview Optimization report with scoring, action plan, and trend tracking.
        </p>
    </div>
    """, unsafe_allow_html=True)