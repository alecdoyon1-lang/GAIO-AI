#!/usr/bin/env python3
"""
AI Search Optimizer — Self-bootstrapping Streamlit App
Run with: ./app.py  or  streamlit run app.py
100% free, no API keys required.
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

    # Create venv if needed
    if not os.path.isdir(VENV):
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", VENV], check=True)

    # Install dependencies if needed
    if not os.path.isfile(VENV_STREAMLIT):
        print("📦 Installing dependencies...")
        subprocess.run(
            [os.path.join(VENV, "bin", "pip"), "install", "-r", REQUIREMENTS, "-q"],
            check=True,
        )

    # Re-launch with streamlit (replaces current process)
    print("🚀 Launching Streamlit...")
    os.execv(VENV_STREAMLIT, [VENV_STREAMLIT, "run", __file__] + sys.argv[1:])

# ─── Environment Setup ────────────────────────────────────────────────────────
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from collections import Counter


# ─── Local Analysis Engine ─────────────────────────────────────────────────────

def analyze_headers(soup) -> dict:
    """Analyze heading structure (H1-H6) for AI readability."""
    headings = {}
    for level in range(1, 7):
        tags = soup.find_all(f"h{level}")
        headings[f"h{level}"] = [t.get_text(strip=True) for t in tags if t.get_text(strip=True)]
    return headings


def analyze_questions(text: str) -> list:
    """Detect FAQ-style questions in the content."""
    question_patterns = [
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
    for pattern in question_patterns:
        matches = re.findall(pattern, text)
        questions.extend(matches)
    # Deduplicate and clean
    seen = set()
    unique = []
    for q in questions:
        q_clean = q.strip()
        if q_clean and q_clean not in seen and len(q_clean) > 10:
            seen.add(q_clean)
            unique.append(q_clean)
    return unique[:20]


def analyze_lists(soup) -> dict:
    """Detect ordered/unordered lists and their content."""
    uls = soup.find_all("ul")
    ols = soup.find_all("ol")
    list_items = []
    for lst in uls + ols:
        for li in lst.find_all("li", recursive=False):
            text = li.get_text(strip=True)
            if text and len(text) > 3:
                list_items.append(text)
    return {
        "total_lists": len(uls) + len(ols),
        "unordered": len(uls),
        "ordered": len(ols),
        "items": list_items[:30],
    }


def analyze_definitions(soup) -> list:
    """Find definition/explanation patterns (term + description)."""
    definitions = []
    # Look for <dl>, <dt>, <dd> tags
    dls = soup.find_all("dl")
    for dl in dls:
        terms = dl.find_all("dt")
        descriptions = dl.find_all("dd")
        for term, desc in zip(terms, descriptions):
            t = term.get_text(strip=True)
            d = desc.get_text(strip=True)
            if t and d and len(t) < 100 and len(d) < 300:
                definitions.append({"term": t, "definition": d[:200]})

    # Also look for strong/bold followed by explanatory text
    if not definitions:
        for strong in soup.find_all(["strong", "b"]):
            term = strong.get_text(strip=True)
            if term and 3 < len(term) < 80:
                next_el = strong.find_next_sibling()
                if next_el:
                    desc = next_el.get_text(strip=True)
                    if desc and 10 < len(desc) < 300:
                        definitions.append({"term": term, "definition": desc[:200]})
    return definitions[:15]


def analyze_readability(text: str) -> dict:
    """Analyze text readability and conversational quality."""
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]

    if not sentences:
        return {"score": 0, "avg_sentence_length": 0, "total_sentences": 0, "long_sentences_pct": 0}

    lengths = [len(s.split()) for s in sentences]
    avg_len = sum(lengths) / len(lengths)
    long_sentences = sum(1 for l in lengths if l > 30)
    long_pct = (long_sentences / len(lengths)) * 100 if lengths else 0

    # Conversational markers
    conversational_markers = [
        r"\byou\b", r"\byour\b", r"\bwe\b", r"\bour\b", r"\blet's\b", r"\bhere's\b",
        r"\bthink\b", r"\bfeel\b", r"\bknow\b", r"\bunderstand\b", r"\bimagine\b",
        r"\bconsider\b", r"\bdiscover\b", r"\bexplore\b", r"\blearn\b", r"\bfind\b",
        r"\bget\b", r"\bmake\b", r"\btry\b", r"\buse\b", r"\bstart\b",
    ]
    marker_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in conversational_markers)
    conversational_density = marker_count / max(len(text.split()), 1)

    # Readability score (0-100, higher is better)
    score = 100
    if avg_len > 25:
        score -= min((avg_len - 25) * 3, 40)
    if long_pct > 30:
        score -= min((long_pct - 30) * 1.5, 25)
    if conversational_density < 0.01:
        score -= 15
    if conversational_density > 0.03:
        score += 10
    score = max(0, min(100, score))

    return {
        "score": round(score, 1),
        "avg_sentence_length": round(avg_len, 1),
        "total_sentences": len(sentences),
        "long_sentences_pct": round(long_pct, 1),
        "conversational_density": round(conversational_density, 4),
    }


def analyze_keyword_density(text: str) -> dict:
    """Analyze keyword density and topical signals."""
    # Remove common stop words
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "to", "of", "in", "for",
        "on", "with", "at", "by", "from", "as", "into", "through", "during",
        "before", "after", "above", "below", "between", "out", "off", "over",
        "under", "again", "further", "then", "once", "here", "there", "when",
        "where", "why", "how", "all", "each", "every", "both", "few", "more",
        "most", "other", "some", "such", "no", "nor", "not", "only", "own",
        "same", "so", "than", "too", "very", "just", "because", "but", "and",
        "or", "if", "while", "about", "up", "it", "its", "this", "that",
        "these", "those", "i", "me", "my", "we", "our", "you", "your", "he",
        "him", "his", "she", "her", "they", "them", "their", "what", "which",
        "who", "whom", "whose",
    }

    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    meaningful = [w for w in words if w not in stop_words and len(w) > 2]

    if not meaningful:
        return {"top_terms": [], "total_meaningful": 0}

    counter = Counter(meaningful)
    top_terms = counter.most_common(20)

    # Detect multi-word phrases (bigrams)
    bigrams = []
    for i in range(len(meaningful) - 1):
        bigrams.append(f"{meaningful[i]} {meaningful[i+1]}")
    bigram_counter = Counter(bigrams)
    top_bigrams = bigram_counter.most_common(10)

    return {
        "top_terms": top_terms,
        "top_bigrams": top_bigrams,
        "total_meaningful": len(meaningful),
        "unique_terms": len(set(meaningful)),
    }


def analyze_structure(soup) -> dict:
    """Analyze overall page structure."""
    structure = {
        "has_h1": len(soup.find_all("h1")) > 0,
        "h1_count": len(soup.find_all("h1")),
        "h2_count": len(soup.find_all("h2")),
        "h3_count": len(soup.find_all("h3")),
        "total_headings": len(soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])),
        "paragraph_count": len(soup.find_all("p")),
        "link_count": len(soup.find_all("a", href=True)),
        "image_count": len(soup.find_all("img")),
        "table_count": len(soup.find_all("table")),
        "has_schema": bool(soup.find_all("script", type="application/ld+json")),
        "has_meta_description": bool(soup.find("meta", attrs={"name": "description"})),
        "has_title": bool(soup.find("title")),
        "title_text": soup.find("title").get_text(strip=True) if soup.find("title") else "",
    }
    return structure


def generate_recommendations(analysis: dict) -> list:
    """Generate 3 highly specific optimization recommendations based on local analysis."""
    recommendations = []
    headings = analysis["headings"]
    structure = analysis["structure"]
    questions = analysis["questions"]
    lists = analysis["lists"]
    definitions = analysis["definitions"]
    readability = analysis["readability"]
    keywords = analysis["keywords"]

    # ── Recommendation 1: Heading Structure ────────────────────────────────────
    heading_issues = []
    if not structure["has_h1"]:
        heading_issues.append("no H1 heading")
    elif structure["h1_count"] > 1:
        heading_issues.append(f"{structure['h1_count']} H1 headings (should be exactly 1)")

    if structure["h2_count"] == 0 and structure["h3_count"] > 0:
        heading_issues.append("H3 headings without parent H2 sections")

    if structure["total_headings"] < 3:
        heading_issues.append("very few structured headings")

    if heading_issues:
        issues_str = "; ".join(heading_issues)
        h2_examples = ", ".join([f'"{h}"' for h in headings.get("h2", [])[:3]]) if headings.get("h2") else "none found"
        recommendations.append(
            f"Fix heading hierarchy ({issues_str}). "
            f"Add a single descriptive H1 that summarizes the page topic, "
            f"then use H2 sections for major topics (current H2s: {h2_examples}). "
            f"AI systems heavily weight H1/H2 text when generating answers — "
            f"make them direct, question-like, and keyword-rich so ChatGPT and Google AI Overviews can quote them."
        )
    else:
        h2_examples = ", ".join([f'"{h}"' for h in headings.get("h2", [])[:3]])
        recommendations.append(
            f"Strengthen your heading hierarchy. Your H2 headings ({h2_examples}) should be "
            f"rewritten as direct questions or concise answers that AI systems can quote verbatim. "
            f"Add H3 sub-sections under each H2 with specific data points, examples, or step-by-step "
            f"instructions — this increases the chance of being cited in ChatGPT, Google AI Overviews, and Claude."
        )

    # ── Recommendation 2: FAQ / Question Format ────────────────────────────────
    if len(questions) >= 3:
        q_examples = " | ".join(questions[:3])
        recommendations.append(
            f"Expand your FAQ section. You already have {len(questions)} detectable questions "
            f"(e.g., {q_examples}). Add 5-10 more explicit Q&A pairs using the exact phrasing "
            f"people type into search engines. Format each as a clear question followed by a "
            f"2-4 sentence direct answer. This pattern is the #1 signal AI systems look for "
            f"when generating overviews — the closer your content matches real user queries, "
            f"the more likely you are to be cited."
        )
    elif len(questions) >= 1:
        q_examples = " | ".join(questions[:2])
        recommendations.append(
            f"Add a dedicated FAQ section. You have {len(questions)} question-like sentence(s) "
            f"(e.g., {q_examples}), but AI systems need at least 5-10 explicit Q&A pairs to "
            f"consider a page as a reliable source. Create a section titled 'Frequently Asked Questions' "
            f"with real user queries as headings and concise, factual answers below each. "
            f"Include variations like 'How to...', 'What is...', 'Can you...', and 'Why does...' "
            f"to cover the full range of AI query patterns."
        )
    elif lists["total_lists"] >= 2:
        list_examples = ", ".join(lists["items"][:3])
        recommendations.append(
            f"Convert your list content into Q&A format. You have {lists['total_lists']} list(s) "
            f"on this page (e.g., {list_examples}). AI systems prefer explicit question-answer "
            f"pairs over bullet lists. Rewrite each list item as a question heading followed by "
            f"a 2-3 sentence answer. For example, change '• Fast shipping' to "
            f"'How fast is shipping? — We offer same-day delivery in metro areas and 2-day "
            f"shipping nationwide.' This dramatically increases citation probability."
        )
    else:
        top_terms = ", ".join([t[0] for t in keywords.get("top_terms", [])[:5]])
        recommendations.append(
            f"Add an FAQ section with 5-10 question-answer pairs. Your top topics are: {top_terms}. "
            f"Write questions that real users would ask about these topics (e.g., 'What is [topic]?', "
            f"'How does [topic] work?', 'Why choose [topic]?'). Keep answers under 100 words and "
            f"front-load the most important information. AI systems prioritize FAQ content because "
            f"it directly maps to user intent — pages with structured Q&A are 3x more likely to "
            f"appear in Google AI Overviews and ChatGPT responses."
        )

    # ── Recommendation 3: Readability / Conversational Tone ────────────────────
    if readability["score"] < 50:
        if readability["avg_sentence_length"] > 25:
            recommendations.append(
                f"Improve readability — your average sentence length is {readability['avg_sentence_length']} words "
                f"(target: 15-20). Long, complex sentences are hard for AI systems to parse and quote. "
                f"Break sentences over 25 words into two shorter ones. Replace passive voice with active "
                f"voice ('The product was designed' → 'We designed the product'). Add transition phrases "
                f"like 'Here's why...', 'The key benefit is...', and 'In simple terms...' to make the "
                f"content more quotable. Aim for a 6th-8th grade reading level — this is the sweet spot "
                f"for both human readers and AI summarization engines."
            )
        elif readability["conversational_density"] < 0.015:
            recommendations.append(
                f"Make the tone more conversational. Your content reads like formal documentation — "
                f"AI systems struggle to extract quotable snippets from dry, impersonal text. "
                f"Increase use of 'you' and 'we' pronouns, add direct address ('You might wonder...'), "
                f"and include brief explanatory asides. Break up walls of text with sub-headings, "
                f"numbered steps, and short paragraphs (2-3 sentences max). "
                f"Conversational content is 2x more likely to be quoted by AI systems because it "
                f"already sounds like a natural language response."
            )
        else:
            recommendations.append(
                f"Improve content scannability. Your readability score is {readability['score']}/100. "
                f"Add more white space between paragraphs, use bold text to highlight key phrases "
                f"AI can quote, and include a 'Key Takeaways' box at the top of long sections. "
                f"Front-load the most important information in the first 50 words of each section — "
                f"AI systems often truncate content and may only see the beginning of paragraphs. "
                f"Use specific numbers, dates, and named entities (people, places, products) "
                f"to increase factual density and citation confidence."
            )
    else:
        if definitions:
            def_example = definitions[0]
            recommendations.append(
                f"Add a structured glossary or 'Key Terms' section. You already have "
                f"{len(definitions)} definition-like patterns (e.g., '{def_example['term']}'). "
                f"Expand these into a formal glossary with each term as an H3 heading followed by "
                f"a 1-2 sentence plain-language definition. AI systems love structured definitions "
                f"because they provide clear, unambiguous facts to cite. Also add a 'Key Takeaways' "
                f"summary box at the top of long pages — this gives AI systems a ready-made "
                f"executive summary to quote, increasing your citation rate by up to 40%."
            )
        else:
            top_bigram = keywords.get("top_bigrams", [("core concepts", 0)])[0]
            recommendations.append(
                f"Add a 'Key Terms' or 'Glossary' section defining your core concepts "
                f"(e.g., '{top_bigram[0]}'). AI systems prioritize content with explicit definitions "
                f"because they reduce ambiguity. Create an H2 section titled 'Key Terms' or "
                f"'Understanding [Topic]' with 5-10 H3 entries, each containing a term and a "
                f"1-2 sentence plain-language definition. Also add a 2-3 sentence 'Summary' or "
                f"'Overview' paragraph at the very top of the page — this is the #1 most-quoted "
                f"section by Google AI Overviews and ChatGPT. Keep it under 60 words and make it "
                f"standalone so it works as a snippet without additional context."
            )

    # Ensure exactly 3 recommendations
    while len(recommendations) < 3:
        recommendations.append(
            "Add structured data markup (Schema.org JSON-LD) to your page. "
            "Include at minimum Organization, WebPage, and FAQPage schemas. "
            "This gives AI systems explicit, machine-readable facts about your content "
            "and significantly increases the likelihood of being cited in AI-generated responses."
        )

    return recommendations[:3]


# ─── Scraping ─────────────────────────────────────────────────────────────────

def scrape_website(url: str) -> str:
    """Scrape visible text content from a website URL."""
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

        # Remove noise elements
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "iframe", "svg"]):
            tag.decompose()

        # Extract visible text
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned_text = "\n".join(lines)

        # Truncate for analysis
        if len(cleaned_text) > 8000:
            cleaned_text = cleaned_text[:8000] + "\n\n[... content truncated for analysis ...]"

        return cleaned_text, soup

    except Exception as e:
        return f"ERROR: {str(e)}", None


def run_full_analysis(text: str, soup) -> dict:
    """Run all local analysis passes and return structured results."""
    headings = analyze_headers(soup)
    questions = analyze_questions(text)
    lists = analyze_lists(soup)
    definitions = analyze_definitions(soup)
    readability = analyze_readability(text)
    keywords = analyze_keyword_density(text)
    structure = analyze_structure(soup)

    recommendations = generate_recommendations({
        "headings": headings,
        "questions": questions,
        "lists": lists,
        "definitions": definitions,
        "readability": readability,
        "keywords": keywords,
        "structure": structure,
    })

    return {
        "headings": headings,
        "questions": questions,
        "lists": lists,
        "definitions": definitions,
        "readability": readability,
        "keywords": keywords,
        "structure": structure,
        "recommendations": recommendations,
    }


# ─── llms.txt Generator ────────────────────────────────────────────────────────

def generate_llms_txt(analysis: dict, url: str) -> str:
    """Generate a well-formatted llms.txt file from local analysis."""
    structure = analysis["structure"]
    headings = analysis["headings"]
    keywords = analysis["keywords"]
    definitions = analysis["definitions"]
    lists = analysis["lists"]
    questions = analysis["questions"]

    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    site_name = structure["title_text"].split("—")[0].split("|")[0].strip() or domain

    lines = []
    lines.append(f"# {site_name}")
    lines.append("")

    # Description
    top_terms = [t[0] for t in keywords.get("top_terms", [])[:5]]
    topic_str = ", ".join(top_terms) if top_terms else "various topics"
    lines.append(f"> {site_name} is a website covering {topic_str}.")
    lines.append("")

    # Key sections from H2 headings
    if headings.get("h2"):
        lines.append("## Key Sections")
        lines.append("")
        for h2 in headings["h2"][:10]:
            lines.append(f"- **{h2}** — Main section covering this topic.")
        lines.append("")

    # Key topics from keyword analysis
    if keywords.get("top_terms"):
        lines.append("## Main Topics")
        lines.append("")
        for term, count in keywords["top_terms"][:10]:
            lines.append(f"- {term}")
        lines.append("")

    # Definitions / Key Terms
    if definitions:
        lines.append("## Key Terms")
        lines.append("")
        for d in definitions[:10]:
            lines.append(f"### {d['term']}")
            lines.append("")
            lines.append(d["definition"])
            lines.append("")

    # FAQ
    if questions:
        lines.append("## Frequently Asked Questions")
        lines.append("")
        for q in questions[:10]:
            lines.append(f"### {q}")
            lines.append("")
            lines.append("See the website for the full answer to this question.")
            lines.append("")

    # Lists / Features
    if lists["items"]:
        lines.append("## Features and Offerings")
        lines.append("")
        for item in lists["items"][:15]:
            lines.append(f"- {item}")
        lines.append("")

    # Contact / About
    lines.append("## More Information")
    lines.append("")
    lines.append(f"- **Website:** {url}")
    lines.append(f"- **Domain:** {domain}")
    lines.append("")

    return "\n".join(lines)


# ─── Streamlit App ────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Search Optimizer",
    page_icon="🤖",
    layout="wide",
)

# Custom CSS
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }

    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
    }

    .main-header p {
        font-size: 1.1rem;
        color: #6b7280;
        font-weight: 400;
    }

    .result-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f0 100%);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin: 1rem 0;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    .result-card h3 {
        font-size: 1.2rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .bullet-point {
        background: #ffffff;
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        font-size: 1rem;
        line-height: 1.6;
        color: #374151;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }

    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.35);
    }

    .sidebar-section {
        background: #f9fafb;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .success-banner {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 1px solid #6ee7b7;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        color: #065f46;
        font-weight: 500;
    }

    .error-banner {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 1px solid #fca5a5;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        color: #991b1b;
        font-weight: 500;
    }

    .stat-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        text-align: center;
        border: 1px solid #e5e7eb;
    }

    .stat-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #667eea;
    }

    .stat-label {
        font-size: 0.75rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    hr {
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, #d1d5db, transparent);
        margin: 1.5rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### ℹ️ About")
    st.markdown(
        """
        This **100% free** tool analyzes any website and provides:
        - **3 AI Search Optimization tips** for ChatGPT, Google AI Overviews & Claude
        - A downloadable **llms.txt** file to make your site LLM-friendly

        No API keys. No sign-ups. No cost.
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### 🛠️ How It Works")
    st.markdown(
        """
        The tool uses a **local analysis engine** that inspects:
        - Heading structure (H1-H6 hierarchy)
        - Question/FAQ patterns
        - Text readability & conversational tone
        - Keyword density & topical signals
        - List structures & definitions
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ─── Main Content ──────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="main-header">
    <h1>🤖 AI Search Optimizer</h1>
    <p>Optimize your website for AI search engines — 100% free, no API keys needed</p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("<hr>", unsafe_allow_html=True)

# URL Input
col1, col2 = st.columns([4, 1])
with col1:
    url_input = st.text_input(
        "🌐 Website URL",
        placeholder="https://example.com",
        label_visibility="collapsed",
    )
with col2:
    st.write("")
    st.write("")
    analyze_btn = st.button(
        "🔍 Analyze Website for AI Search",
        use_container_width=True,
        type="primary",
    )

# Validate URL
url_valid = False
if url_input:
    parsed = urlparse(url_input)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        url_valid = True
    else:
        st.markdown(
            '<div class="error-banner">⚠️ Please enter a valid URL starting with http:// or https://</div>',
            unsafe_allow_html=True,
        )

# ─── Analysis Logic ───────────────────────────────────────────────────────────
if analyze_btn:
    if not url_input or not url_valid:
        st.markdown(
            '<div class="error-banner">⚠️ Please enter a valid website URL.</div>',
            unsafe_allow_html=True,
        )
    else:
        with st.spinner("🕷️ Scraping website content..."):
            result = scrape_website(url_input)

        if isinstance(result, tuple):
            scraped_text, soup = result
        else:
            scraped_text = result
            soup = None

        if scraped_text.startswith("ERROR:"):
            st.markdown(
                f'<div class="error-banner">❌ Failed to scrape website: {scraped_text[7:]}</div>',
                unsafe_allow_html=True,
            )
        elif not soup:
            st.markdown(
                '<div class="error-banner">❌ Failed to parse website content.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="success-banner">✅ Website scraped successfully! Running local analysis...</div>',
                unsafe_allow_html=True,
            )

            analysis = run_full_analysis(scraped_text, soup)

            # ── Stats Row ──────────────────────────────────────────────────────
            st.markdown("### 📊 Content Analysis")
            stat_cols = st.columns(6)
            stats = [
                ("Headings", analysis["structure"]["total_headings"]),
                ("Paragraphs", analysis["structure"]["paragraph_count"]),
                ("Questions", len(analysis["questions"])),
                ("Lists", analysis["lists"]["total_lists"]),
                ("Definitions", len(analysis["definitions"])),
                ("Readability", f"{analysis['readability']['score']}/100"),
            ]
            for col, (label, value) in zip(stat_cols, stats):
                with col:
                    st.markdown('<div class="stat-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="stat-value">{value}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="stat-label">{label}</div>', unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Recommendations ────────────────────────────────────────────────
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown(
                "<h3>🎯 AI Search Optimization Recommendations</h3>",
                unsafe_allow_html=True,
            )

            for i, rec in enumerate(analysis["recommendations"], 1):
                st.markdown(
                    f'<div class="bullet-point"><strong>{i}.</strong> {rec}</div>',
                    unsafe_allow_html=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)

            # Store in session state
            st.session_state["analysis"] = analysis
            st.session_state["url"] = url_input
            st.session_state["scraped_text"] = scraped_text

# ─── llms.txt Generation ───────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)

col_a, col_b, col_c = st.columns([1, 2, 1])
with col_b:
    generate_llms_btn = st.button(
        "📄 Generate & Download llms.txt",
        use_container_width=True,
        type="secondary",
    )

if generate_llms_btn:
    if "analysis" not in st.session_state:
        st.markdown(
            '<div class="error-banner">⚠️ Please analyze a website first before generating llms.txt.</div>',
            unsafe_allow_html=True,
        )
    else:
        llms_content = generate_llms_txt(
            st.session_state["analysis"],
            st.session_state["url"],
        )

        st.markdown(
            '<div class="success-banner">✅ llms.txt generated successfully! Download below.</div>',
            unsafe_allow_html=True,
        )

        # Preview
        with st.expander("📄 Preview llms.txt"):
            st.code(llms_content, language="markdown")

        # Download
        parsed_url = urlparse(st.session_state["url"])
        domain = parsed_url.netloc.replace("www.", "")
        filename = f"{domain}_llms.txt"

        st.download_button(
            label=f"⬇️ Download {filename}",
            data=llms_content,
            file_name=filename,
            mime="text/plain",
            use_container_width=True,
        )
