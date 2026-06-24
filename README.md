<!-- Banner -->
<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Flag_of_Europe.svg/320px-Flag_of_Europe.svg.png" width="80" alt="EU Flag"/>
  
  <h1>🇪🇺 EU AI Act Compliance Platform</h1>
  
  <p><strong>Self-service AI compliance assessment, risk classification, and audit reporting tool</strong><br>
  Built on Regulation (EU) 2024/1689 — the world's first comprehensive AI law</p>

  <p>
    <img src="https://img.shields.io/badge/EU_AI_Act-2024/1689-003399?style=for-the-badge&logo=europeanunion&logoColor=white"/>
    <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
    <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
  </p>

  <p>
    <a href="https://ali1810-eu-ai-act-platform-app.streamlit.app">
      <img src="https://img.shields.io/badge/🚀 Live Demo-Streamlit Cloud-FF4B4B?style=for-the-badge"/>
    </a>
  </p>
</div>

---

## 📌 What Is This?

The **EU AI Act Compliance Platform** is an open-source self-service tool that helps developers, researchers, and organisations understand whether their AI project complies with the **EU AI Act (Regulation 2024/1689)**.

Any team building or deploying an AI system can use this platform to:

- 🔍 **Classify** their system's risk tier (Unacceptable / High / Limited / Minimal)
- 📋 **Check compliance** article-by-article (Art.5 through Art.50)
- 📊 **Get a readiness score** (0–100%) with per-article breakdown
- 🤖 **Receive AI-powered gap analysis** identifying what's missing and why it matters
- 📄 **Download an audit-ready PDF report** for stakeholders or legal review
- 📖 **Learn the law** through a built-in reference guide

> **Inspired by** [AISC](https://github.com/lux-ai-factory/aisc) by Luxembourg's LIST/SnT — the AI Assessment Sandbox Configurator.

---

## 🖼️ Screenshots

| Dashboard | Assessment Form | Results |
|---|---|---|
| Risk tier overview + stats | Submit your AI project | Score, article checks, gap analysis |

---

## 🚀 Quick Start

### Option A — Run locally (Full stack)

```bash
# 1. Clone
git clone https://github.com/ali1810/eu-ai-act-platform.git
cd eu-ai-act-platform

# 2. Set up environment
cp .env.example .env
# Edit .env → add your GROQ_API_KEY (free at console.groq.com)

# 3. Start FastAPI backend (Terminal 1)
cd apps/api
python -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\activate
pip install ".[dev]"
uvicorn core.main:app --reload
# → http://127.0.0.1:8000/docs

# 4. Start Streamlit frontend (Terminal 2)
cd apps/streamlit
pip install -r requirements.txt
streamlit run app.py
# → http://localhost:8501
```

### Option B — Standalone Streamlit only (no backend)

```bash
git clone https://github.com/ali1810/eu-ai-act-platform.git
cd eu-ai-act-platform
pip install -r requirements.txt
streamlit run app.py
```

---

## 🏗️ Architecture

```
eu-ai-act-platform/
├── apps/
│   ├── api/                          # FastAPI backend
│   │   ├── core/
│   │   │   ├── config.py             # Pydantic-settings config
│   │   │   └── main.py               # App factory, routing
│   │   ├── models/
│   │   │   └── schemas.py            # All Pydantic schemas
│   │   ├── services/
│   │   │   ├── eu_ai_act_rules.py    # ⭐ Core rule engine
│   │   │   ├── llm_service.py        # AI gap analysis (Groq/OpenAI/Ollama)
│   │   │   └── project_store.py      # JSON persistence
│   │   ├── routers/
│   │   │   ├── classify.py           # Risk classification endpoint
│   │   │   ├── assess.py             # Full assessment endpoint
│   │   │   ├── projects.py           # Project CRUD
│   │   │   └── report.py             # PDF generation
│   │   └── utils/
│   │       └── pdf_report.py         # ReportLab PDF builder
│   └── streamlit/
│       ├── app.py                    # 5-page Streamlit UI
│       └── api_client.py             # HTTP client wrapper
├── .env.example
├── requirements.txt                  # Standalone deployment
└── README.md
```

---

## 📋 EU AI Act Risk Tiers

| Tier | Examples | Platform Action |
|---|---|---|
| 🔴 **Unacceptable** | Social scoring · Real-time biometrics in public · Subliminal manipulation | Flags as PROHIBITED under Art.5 |
| 🟠 **High Risk** | Hiring AI · Medical devices · Credit scoring · Education systems · Law enforcement | Checks 9 articles (Art.9–15, Art.43) |
| 🟡 **Limited Risk** | Chatbots · Deepfakes · Recommendation systems | Checks transparency obligations (Art.50) |
| 🟢 **Minimal Risk** | Spam filters · AI in games | No mandatory obligations |

---

## 📐 Articles Covered

| Article | Title | Risk Tier |
|---|---|---|
| Art.5  | Prohibited AI Practices | Unacceptable |
| Art.9  | Risk Management System | High |
| Art.10 | Data and Data Governance | High |
| Art.11 | Technical Documentation | High |
| Art.12 | Record-Keeping and Logging | High |
| Art.13 | Transparency | High + Limited |
| Art.14 | Human Oversight | High |
| Art.15 | Accuracy, Robustness, Cybersecurity | High |
| Art.43 | Conformity Assessment | High |
| Art.50 | Transparency for Certain AI Systems | Limited |

---

## 🤖 AI-Powered Gap Analysis

The platform uses **LLMs** to provide human-readable gap analysis explaining:
- What compliance gaps exist and why they matter
- The risk of deploying non-compliant
- Concrete first steps to achieve compliance

### Supported LLM Providers

| Provider | Cost | Setup |
|---|---|---|
| [Groq](https://console.groq.com) | 🆓 Free | `GROQ_API_KEY=gsk_...` |
| [Google Gemini](https://aistudio.google.com) | 🆓 Free tier | `GEMINI_API_KEY=AIza...` |
| [Ollama](https://ollama.com) | 🆓 Local | No key needed |
| OpenAI | 💳 Paid | `OPENAI_API_KEY=sk-...` |

> The platform works **without any API key** — rule-based classification and article checks run fully offline. Only the AI gap analysis paragraph requires a key.

---

## ☁️ Deploy to Streamlit Cloud (Free)

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repo → `app.py` → **Deploy**
5. Add `GROQ_API_KEY` in **Settings → Secrets**

Your live URL:
```
[https://eu-ai-act-platform.streamlit.app/]
```

---

## 🔑 Environment Variables

```env
# LLM Provider
LLM_PROVIDER=groq            # groq | openai | ollama | gemini

# Keys (only the one you use)
GROQ_API_KEY=gsk_...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...

# App
APP_ENV=development
LOG_LEVEL=DEBUG
```

---

## 📄 Sample PDF Report

The platform generates an **audit-ready PDF** containing:

- ✅ Project metadata and risk tier
- ✅ Article-by-article compliance status with colour coding
- ✅ Findings and recommendations per article
- ✅ AI-powered gap analysis
- ✅ Prioritised action list
- ✅ Legal disclaimer and regulation reference

---

## 🗺️ Roadmap

- [ ] GPAI model assessment (Art.51–55)
- [ ] Multi-language support (DE, FR, ES)
- [ ] Team collaboration (shared projects)
- [ ] Integration with AISC plugin architecture
- [ ] Automated re-assessment on regulation updates
- [ ] API webhook for CI/CD compliance gates
- [ ] DSGVO / GDPR cross-compliance checker

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/gpai-assessment`
3. Commit your changes: `git commit -m "Add GPAI model assessment"`
4. Push: `git push origin feature/gpai-assessment`
5. Open a Pull Request

---

## 📚 References

- 📜 [EU AI Act Full Text (EUR-Lex)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689)
- 🏛️ [European AI Office](https://digital-strategy.ec.europa.eu/en/policies/european-ai-office)
- 🗄️ [EU AI Act Database](https://artificialintelligenceact.eu/)
- 🔬 [AISC by LIST/SnT Luxembourg](https://github.com/lux-ai-factory/aisc)
- 📅 [Implementation Timeline](https://artificialintelligenceact.eu/implementation-timeline/)

---

## ⚠️ Disclaimer

> This platform is a **self-assessment tool** intended to help teams understand their obligations under the EU AI Act. It does **not constitute legal advice**. For official conformity assessment, consult a notified body or qualified legal counsel.
>
> Reference: Regulation (EU) 2024/1689 of the European Parliament and of the Council of 13 June 2024.

---

## 📝 License

MIT License — free to use, modify, and distribute.

---

<div align="center">
  <p>Built with ❤️ to make AI compliance accessible to everyone</p>
  <p>
    <a href="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689">EU AI Act</a> ·
    <a href="https://share.streamlit.io">Streamlit Cloud</a> ·
    <a href="https://console.groq.com">Groq (Free LLM)</a>
  </p>
</div>
