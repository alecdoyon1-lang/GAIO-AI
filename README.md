# GAIO Enterprise Suite — AI Search Optimizer

> **Ahrefs-Style SEO & AI Suite** — 4-Category Diagnostic Intelligence + Semantic Visibility

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![License](https://img.shields.io/badge/License-Proprietary-purple)

## 🚀 Overview

GAIO Enterprise Suite is a professional-grade SEO and AI optimization platform that analyzes websites across four critical dimensions:

- **🔵 Technical SEO** — Heading structure, title metadata, word density, schema markup
- **🟢 LSO (Local Search Optimization)** — Geographic terms, "near me" phrases, address signals
- **🟡 GAIO/AEO (Generative AI Optimization)** — Conversational readability, Q&A patterns, AI crawlability
- **🟣 SMO (Social Media Optimization)** — Open Graph tags, Twitter Cards, social share readiness

### Key Features

- **Dual-Grade Analysis**: On-Page SEO Code Grade + Search Visibility Score
- **AI-Powered Insights**: Context-aware chatbot that analyzes your audit results
- **PDF Export**: Professional audit reports with all scores and recommendations
- **6-Month Trend Tracking**: Simulated performance trends with actionable milestones
- **User Authentication**: Google OAuth + email/password login with 7-day free trial
- **100% Local Analysis**: No API keys required, no data leaves your machine

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/gaio-ai/gaio-enterprise-suite.git
cd gaio-enterprise-suite

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Dependencies

```
streamlit>=1.28.0
requests>=2.31.0
beautifulsoup4>=4.12.0
fpdf2>=2.7.0
streamlit-authenticator>=0.2.0
PyYAML>=6.0
```

## 🎯 How to Use

### 1. **Launch the App**

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

### 2. **Sign Up or Log In**

- **New users**: Click "Start 7-Day Free Trial" to create an account
- **Returning users**: Sign in with Google OAuth or email/password
- **Owner access**: Enter license key `GAIO2024OWNER` in the sidebar for unlimited access

### 3. **Run Your First Audit**

1. Enter a website URL (e.g., `google.com` or `https://example.com`)
2. Click **"🚀 Run Full Audit"**
3. Wait 10-30 seconds for analysis to complete

### 4. **Explore Results**

Navigate through 7 specialized tabs:

- **📊 Dashboard Overview**: Dual-grade badges, 4-category metrics, 6-month trends
- **🔍 Site Explorer & Audit**: Automated HTML parsing checklist, detailed score breakdown
- **🏷️ Keywords & GAIO Explorer**: AI-detected keywords, GAIO/AEO action plan
- **📍 Local & Social Explorer**: LSO and SMO detailed analysis
- **💬 AI Assistant**: Context-aware chatbot for personalized recommendations
- **❓ Help & Guide**: 5-step getting started guide, troubleshooting
- **💡 Feedback**: Submit suggestions, bug reports, or feature requests

### 5. **Export Reports**

Download professional PDF reports:
- **Full Audit PDF**: All scores, keywords, and recommendations
- **Chat Transcript PDF**: AI assistant conversation
- **Chat TXT**: Plain text export

## 📊 Scoring System

### Grade Scale

| Grade | Score Range | Performance Level |
|-------|-------------|-------------------|
| **A** | 90-100% | Excellent — Industry leading |
| **B** | 75-89% | Good — Above average |
| **C** | 60-74% | Fair — Needs improvement |
| **D** | 0-59% | Poor — Critical issues |

### On-Page SEO Code Grade

Average of all 4 categories (SEO, LSO, GAIO, SMO). Represents raw content quality without multipliers.

### Search Visibility Score

Semantic intent analysis based on:
- Keyword presence in `<title>` tag (+15% per keyword)
- Keyword presence in `<h1>` tag (+10% per keyword)
- Base score: 30%
- **Capped at 95%**

### Category Scoring Details

#### Technical SEO (100 points base)

**Deductions:**
- Missing H1 tag: -25
- Multiple H1s: -20
- No H2 headings: -15
- Few H2 headings (<3): -8
- Missing title tag: -20
- Title too short (<30 chars): -10
- Title too long (>70 chars): -10
- Missing meta description: -10
- Thin content (<300 words): -15
- Below optimal length (<500 words): -8
- Low word diversity (<30%): -10
- Keyword stuffing risk (>60%): -5
- Most images missing alt text: -10
- Some images missing alt text: -5
- No schema markup: -5
- No links: -5
- Excessive links (>100): -5

**Bonuses:**
- Optimal title length (30-70 chars): +5
- Good content length (≥500 words): +5
- Good word diversity (30-60%): +5
- All images have alt text: +5
- Schema markup present: +5

#### Local SEO (100 points base)

**Deductions:**
- No geographic terms: -40
- Few geographic terms (<2): -25
- Moderate geographic terms (<5): -10
- No "near me" phrases: -30
- Few "near me" phrases (<2): -15
- No address information: -20
- Limited address info (<2): -10

**Bonuses:**
- Strong geographic presence (≥5): +5
- Good "near me" usage (≥2): +5
- Complete address info (≥2): +5
- Strong local context signals (≥3): +5

#### GAIO/AEO (100 points base)

**Deductions:**
- Very long sentences (>30 words avg): -25
- Long sentences (>25 words avg): -15
- Very short sentences (<15 words avg): -5
- Too many long sentences (>40%): -20
- Many long sentences (>30%): -10
- Very low conversational tone (<0.005): -20
- Low conversational tone (<0.01): -10
- No Q&A patterns: -20
- Limited Q&A content (1-2 questions): -10
- Limited list structure (<2 lists): -10
- Weak heading structure (<3 headings): -10
- Very thin content (<200 words): -5

**Bonuses:**
- Optimal sentence length (15-25 words): +5
- Good sentence variety (≤30% long): +5
- Excellent conversational tone (≥0.03): +10
- Good conversational tone (≥0.02): +5
- Excellent Q&A content (≥10 questions): +15
- Strong Q&A content (7-9 questions): +10
- Good Q&A content (5-6 questions): +5
- Excellent list structure (≥5 lists): +10
- Good list structure (3-4 lists): +5
- Strong heading hierarchy (≥8 headings): +5
- Schema markup present: +5
- Comprehensive content (≥1000 words): +5

#### SMO (100 points base)

**Deductions:**
- Missing `og:title`: -25
- Missing `og:description`: -25
- Missing `og:image`: -25
- Missing `og:url`: -25
- No Twitter Cards: -10
- Relative image URL: -3
- Small OG image size (<600x315): -3
- OG title too long (>100 chars): -3
- OG description too long (>300 chars): -3

**Bonuses:**
- Each required OG tag present: +2
- Optional OG tags (capped at 10): +1-5 each
- Twitter Cards present (capped at 15): +1-10 each
- Absolute image URL: +3
- Optimal OG image size (≥1200x630): +5
- Adequate OG image size (≥600x315): +2
- Optimal OG title length (30-70 chars): +3
- Optimal OG description length (100-200 chars): +3

## 🏗️ Project Structure

```
gaio-enterprise-suite/
├── app.py                      # Main application (2,500+ lines)
├── requirements.txt            # Python dependencies
├── fix_app.py                  # Utility script for app fixes
├── credentials.yaml            # Google OAuth credentials (auto-generated)
├── users.json                  # User database (auto-generated)
├── activity_log.json           # Activity tracking (auto-generated)
├── feedback.json               # User feedback (auto-generated)
├── .venv/                      # Virtual environment (auto-created)
└── README.md                   # This file
```

## 🔧 Configuration

### Environment Variables

The app automatically sets these Streamlit environment variables:

```python
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
```

### Google OAuth Setup (Optional)

To enable Google Sign-In:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable **Google+ API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Application type: **Web application**
6. Add redirect URI: `https://your-app-url.streamlit.app/`
7. Copy Client ID and Client Secret
8. Update `credentials.yaml`:

```yaml
google:
  client_id: "YOUR_CLIENT_ID"
  client_secret: "YOUR_CLIENT_SECRET"
  redirect_uri: "https://your-app-url.streamlit.app/"
```

## 🎨 UI/UX Features

### Premium Design System

- **Glassmorphism Effects**: Backdrop blur, semi-transparent cards
- **Smooth Animations**: Fade-in-up effects on all cards
- **Responsive Layout**: Mobile, tablet, and desktop optimized
- **Custom Scrollbar**: Styled scrollbars for better aesthetics
- **Interactive Buttons**: Hover effects with elevation changes
- **Color-Coded Grades**: Green (A), Blue (B), Yellow (C), Red (D)

### Accessibility

- High contrast text ratios
- Clear visual hierarchy
- Keyboard navigation support
- Screen reader friendly labels

## 🔒 Security & Privacy

### Data Handling

- **100% Local Analysis**: No data sent to external APIs
- **No API Keys Required**: All analysis runs locally
- **Session-Based Storage**: Data stored in browser session
- **Optional Authentication**: Use without login for basic features

### User Data

- Passwords hashed with streamlit-authenticator
- Activity logs for monitoring (optional)
- Feedback stored locally in JSON files
- No third-party analytics or tracking

## 🚀 Deployment

### Streamlit Cloud (Recommended)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy with one click

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t gaio-enterprise-suite .
docker run -p 8501:8501 gaio-enterprise-suite
```

### AWS / GCP / Azure

Deploy as a containerized app or use Streamlit Cloud for easiest setup.

## 🧪 Testing

### Manual Testing Checklist

- [ ] User registration and login
- [ ] Google OAuth (if configured)
- [ ] URL validation and scraping
- [ ] All 4 category analyses
- [ ] PDF export functionality
- [ ] Chatbot responses
- [ ] Feedback submission
- [ ] Mobile responsiveness
- [ ] Error handling (invalid URLs, timeouts)

### Test URLs

```
google.com              # Search engine (95% visibility)
example.com             # Basic website
github.com              # Developer platform
microsoft.com           # Enterprise platform
```

## 📈 Performance

### Optimization Features

- **Enterprise Scale Detection**: Automatically detects massive JS-heavy sites
- **Fallback Analysis**: Provides simulated data if scraping fails
- **Content Truncation**: Limits analysis to 8000 characters for speed
- **Cached Results**: Session-based caching for faster re-analysis

### Benchmarks

- **Scraping**: 10-30 seconds per URL
- **Analysis**: <1 second
- **PDF Generation**: 2-3 seconds
- **Chat Response**: <500ms

## 🐛 Troubleshooting

### Common Issues

**Problem**: App won't start
```bash
# Solution: Reinstall dependencies
pip install --upgrade --force-reinstall -r requirements.txt
```

**Problem**: Scraping fails
- Check internet connection
- Try a different URL
- Some sites block automated access (fallback data will be used)

**Problem**: PDF generation fails
- Ensure audit completed successfully
- Try TXT export instead
- Check browser console for errors

**Problem**: Authentication not working
- Clear browser cache
- Try incognito mode
- Check `credentials.yaml` exists

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/gaio-ai/gaio-enterprise-suite.git
cd gaio-enterprise-suite
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## 📝 Recent Updates

### Version 2.0 (Current)

- ✅ Fixed Pylance warnings for conditional imports
- ✅ Updated all pricing from $30 to $15 USD
- ✅ Improved SEO scoring algorithm with weighted factors
- ✅ Enhanced LSO scoring with expanded geo-term detection
- ✅ Advanced GAIO/AEO scoring with Q&A pattern analysis
- ✅ Comprehensive SMO scoring with OG and Twitter Card analysis
- ✅ Added detailed scoring explanations to UI
- ✅ Performance insights with gap-to-Grade-A metrics
- ✅ Improved error handling and fallback mechanisms
- ✅ Enhanced mobile responsiveness
- ✅ Fixed duplicate UI elements

### Version 1.0

- Initial release
- 4-category analysis engine
- PDF export functionality
- User authentication system
- AI assistant chatbot

## 📄 License

© 2024 GAIO AI. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, or modification is prohibited.

## 📧 Support

- **Email**: support@gaio.ai
- **GitHub**: [github.com/gaio-ai](https://github.com/gaio-ai)
- **Issues**: [GitHub Issues](https://github.com/gaio-ai/gaio-enterprise-suite/issues)

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- PDF generation by [FPDF2](https://pyfpdf.github.io/)
- Web scraping with [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)
- Authentication by [Streamlit Authenticator](https://github.com/mkhorasani/Streamlit-Authenticator)

---

**Engineered for Global Search Intelligence** | © 2024 GAIO AI