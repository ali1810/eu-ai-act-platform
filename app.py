"""
app.py — EU AI Act Compliance Platform
Standalone Streamlit version — no FastAPI backend needed.
Deployable directly on Streamlit Cloud.
"""
import io
import json
import uuid
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from enum import Enum

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EU AI Act Compliance Platform",
    page_icon="🇪🇺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.hero {
    background: linear-gradient(135deg, #0d1b2a 0%, #1b2a4a 50%, #1a237e 100%);
    padding: 36px 40px; border-radius: 20px; color: white; margin-bottom: 28px;
}
.hero h1 { font-size: 2.1rem; font-weight: 800; margin: 0 0 8px 0; }
.hero p  { opacity: 0.75; margin: 0; font-size: 1rem; }
.tier-unacceptable { background:#ffebee; border-left:5px solid #c62828; padding:16px; border-radius:10px; margin:8px 0; }
.tier-high         { background:#fff3e0; border-left:5px solid #e65100; padding:16px; border-radius:10px; margin:8px 0; }
.tier-limited      { background:#fffde7; border-left:5px solid #f9a825; padding:16px; border-radius:10px; margin:8px 0; }
.tier-minimal      { background:#e8f5e9; border-left:5px solid #2e7d32; padding:16px; border-radius:10px; margin:8px 0; }
.article-compliant    { background:#e8f5e9; border:1px solid #a5d6a7; border-radius:10px; padding:14px; margin:6px 0; }
.article-partial      { background:#fff8e1; border:1px solid #ffe082; border-radius:10px; padding:14px; margin:6px 0; }
.article-noncompliant { background:#ffebee; border:1px solid #ef9a9a; border-radius:10px; padding:14px; margin:6px 0; }
.stat-card { background:white; border:1px solid #e0e0e0; border-radius:14px; padding:20px; text-align:center; }
.stat-num  { font-size:2.4rem; font-weight:800; color:#1a237e; }
.stat-lbl  { font-size:0.82rem; color:#777; margin-top:2px; }
.rec-critical  { background:#ffebee; border-left:4px solid #c62828; padding:10px 14px; border-radius:6px; margin:4px 0; font-size:0.88rem; }
.rec-important { background:#fff8e1; border-left:4px solid #f9a825; padding:10px 14px; border-radius:6px; margin:4px 0; font-size:0.88rem; }
.rec-ok        { background:#e8f5e9; border-left:4px solid #2e7d32; padding:10px 14px; border-radius:6px; margin:4px 0; font-size:0.88rem; }
.info-box  { background:#e3f2fd; border-left:4px solid #1565c0; padding:12px 16px; border-radius:8px; margin:8px 0; font-size:0.9rem; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg,#0d1b2a,#1a237e); }
section[data-testid="stSidebar"] * { color: white !important; }
</style>
""", unsafe_allow_html=True)


# ── Built-in Rule Engine (no FastAPI needed) ──────────────────────────────────

HIGH_RISK_CATEGORIES = {
    "biometric", "critical_infrastructure", "education", "employment",
    "essential_services", "law_enforcement", "migration", "justice", "medical_device"
}
LIMITED_RISK_CATEGORIES = {"chatbot", "recommendation_system"}

ARTICLES = {
    "Art.5":  {"title": "Prohibited AI Practices",            "ref": "EU AI Act, Article 5"},
    "Art.9":  {"title": "Risk Management System",             "ref": "EU AI Act, Article 9"},
    "Art.10": {"title": "Data and Data Governance",           "ref": "EU AI Act, Article 10"},
    "Art.11": {"title": "Technical Documentation",            "ref": "EU AI Act, Article 11"},
    "Art.12": {"title": "Record-Keeping and Logging",         "ref": "EU AI Act, Article 12"},
    "Art.13": {"title": "Transparency",                       "ref": "EU AI Act, Article 13"},
    "Art.14": {"title": "Human Oversight",                    "ref": "EU AI Act, Article 14"},
    "Art.15": {"title": "Accuracy, Robustness, Cybersecurity","ref": "EU AI Act, Article 15"},
    "Art.43": {"title": "Conformity Assessment",              "ref": "EU AI Act, Article 43"},
    "Art.50": {"title": "Transparency for Certain AI Systems","ref": "EU AI Act, Article 50"},
}


def classify_risk(p: dict) -> dict:
    is_prohibited = (
        p["processes_biometric_data"] and
        p["used_in_real_time"] and
        p["deployer_type"] == "public_authority"
    )
    if is_prohibited:
        return {
            "risk_tier": "unacceptable",
            "risk_label": "🔴 Unacceptable Risk — PROHIBITED",
            "rationale": "Real-time biometric identification in public spaces by a public authority is prohibited under Article 5.",
            "applicable_articles": ["Art.5"],
            "prohibited": True,
            "key_obligations": ["PROHIBITED — cannot be deployed without a specific law enforcement exception under Article 5(2)."],
        }
    is_high = (
        p["category"] in HIGH_RISK_CATEGORIES or
        p["affects_fundamental_rights"] or
        (p["makes_autonomous_decisions"] and p["processes_personal_data"])
    )
    if is_high:
        return {
            "risk_tier": "high",
            "risk_label": "🟠 High Risk",
            "rationale": f"Classified as high-risk under Annex III (category: {p['category']}). Full compliance with Articles 9–16 and conformity assessment required.",
            "applicable_articles": ["Art.9","Art.10","Art.11","Art.12","Art.13","Art.14","Art.15","Art.43"],
            "prohibited": False,
            "key_obligations": [
                "Risk management system (Art.9)",
                "Data governance (Art.10)",
                "Technical documentation (Art.11)",
                "Automatic logging (Art.12)",
                "Transparency to deployers (Art.13)",
                "Human oversight (Art.14)",
                "Accuracy & robustness (Art.15)",
                "Conformity assessment + CE marking (Art.43)",
                "EU database registration (Art.49)",
            ],
        }
    is_limited = p["category"] in LIMITED_RISK_CATEGORIES or p["processes_personal_data"]
    if is_limited:
        return {
            "risk_tier": "limited",
            "risk_label": "🟡 Limited Risk",
            "rationale": "Transparency obligations apply. Users must be informed they are interacting with an AI system.",
            "applicable_articles": ["Art.13", "Art.50"],
            "prohibited": False,
            "key_obligations": [
                "Inform users they are interacting with AI (Art.50)",
                "Label AI-generated content (Art.50)",
                "Provide capability/limitation information (Art.13)",
            ],
        }
    return {
        "risk_tier": "minimal",
        "risk_label": "🟢 Minimal Risk",
        "rationale": "No specific mandatory obligations under the EU AI Act. Voluntary codes of conduct are encouraged.",
        "applicable_articles": [],
        "prohibited": False,
        "key_obligations": ["No mandatory obligations — voluntary codes of conduct recommended."],
    }


def run_checks(p: dict, classification: dict) -> list[dict]:
    checks = []
    articles = classification["applicable_articles"]

    def c(art_id, passed, partial, f_pass, f_fail, f_partial, rec):
        if passed:
            return {"article_id": art_id, "article_title": ARTICLES[art_id]["title"],
                    "reference": ARTICLES[art_id]["ref"], "status": "compliant",
                    "score": 1.0, "findings": f_pass, "recommendation": ""}
        if partial:
            return {"article_id": art_id, "article_title": ARTICLES[art_id]["title"],
                    "reference": ARTICLES[art_id]["ref"], "status": "partial",
                    "score": 0.5, "findings": f_partial, "recommendation": rec}
        return {"article_id": art_id, "article_title": ARTICLES[art_id]["title"],
                "reference": ARTICLES[art_id]["ref"], "status": "non_compliant",
                "score": 0.0, "findings": f_fail, "recommendation": rec}

    if "Art.5" in articles:
        checks.append({"article_id":"Art.5","article_title":ARTICLES["Art.5"]["title"],
            "reference":ARTICLES["Art.5"]["ref"],"status":"non_compliant","score":0.0,
            "findings":"System falls under prohibited AI practices (Art.5).","recommendation":"Do not deploy. Seek legal counsel."})
    if "Art.9" in articles:
        checks.append(c("Art.9", p["has_bias_testing"] and p["has_accuracy_metrics"],
            p["has_bias_testing"] or p["has_accuracy_metrics"],
            "Risk management in place: bias testing and accuracy metrics present.",
            "No risk management system found.",
            "Partial: bias testing or accuracy metrics present but not both.",
            "Implement a continuous risk management process covering identification, analysis, evaluation and mitigation of risks throughout the lifecycle."))
    if "Art.10" in articles:
        checks.append(c("Art.10", p["has_data_governance"] and p["has_bias_testing"],
            p["has_data_governance"] or p["has_bias_testing"],
            "Data governance framework and bias testing confirm data quality.",
            "No data governance or bias testing in place.",
            "Partial data governance.",
            "Establish a data governance policy covering collection, labelling, quality assessment and bias detection across training/validation/test sets."))
    if "Art.11" in articles:
        checks.append(c("Art.11", p["has_technical_documentation"], False,
            "Technical documentation is in place.",
            "No technical documentation found — mandatory before market placement.",
            "", "Create technical documentation per Annex IV: system description, design choices, training methodology, performance metrics, limitations."))
    if "Art.12" in articles:
        checks.append(c("Art.12", p["has_logging_monitoring"], False,
            "Logging and monitoring are implemented.",
            "No automatic logging system — mandatory for high-risk AI.",
            "", "Implement tamper-proof automatic logging of inputs, outputs, decisions, anomalies and state changes."))
    if "Art.13" in articles:
        checks.append(c("Art.13", p["has_explainability"] and p["has_user_notification"],
            p["has_explainability"] or p["has_user_notification"],
            "Transparency requirements met.",
            "Transparency obligations not met.",
            "Partial transparency.",
            "Provide instructions for use describing: purpose, accuracy, known biases, intended users, when human oversight is required."))
    if "Art.14" in articles:
        checks.append(c("Art.14", p["has_human_oversight"], False,
            "Human oversight mechanisms implemented.",
            "No human oversight — mandatory for high-risk AI.",
            "", "Implement: ability to pause/stop the system, human review before effect, clear escalation paths for uncertain predictions."))
    if "Art.15" in articles:
        checks.append(c("Art.15", p["has_accuracy_metrics"] and p["has_bias_testing"],
            p["has_accuracy_metrics"] or p["has_bias_testing"],
            "Accuracy and robustness measures in place.",
            "No accuracy metrics or robustness testing found.",
            "Partial accuracy/robustness coverage.",
            "Establish accuracy benchmarks, perform robustness and adversarial testing, implement cybersecurity measures."))
    if "Art.43" in articles:
        checks.append(c("Art.43", p["has_conformity_assessment"], False,
            "Conformity assessment conducted.",
            "No conformity assessment — mandatory before market placement for high-risk systems.",
            "", "Conduct conformity assessment (internal or notified body). Issue EU Declaration of Conformity, affix CE marking, register in EU database."))
    if "Art.50" in articles:
        checks.append(c("Art.50", p["has_user_notification"], False,
            "Users are notified they are interacting with AI.",
            "No user notification — users must be informed they are interacting with AI.",
            "", "Implement clear, prominent AI disclosure at the start of every user interaction."))
    return checks


def compute_score(checks: list) -> float:
    if not checks:
        return 100.0
    relevant = [c for c in checks if c["status"] != "not_applicable"]
    if not relevant:
        return 100.0
    return round(sum(c["score"] for c in relevant) / len(relevant) * 100, 1)


def get_recommendations(checks: list) -> list:
    recs = []
    for c in checks:
        if c["status"] == "non_compliant" and c["recommendation"]:
            recs.append(f"[CRITICAL] {c['article_id']} — {c['recommendation']}")
    for c in checks:
        if c["status"] == "partial" and c["recommendation"]:
            recs.append(f"[IMPORTANT] {c['article_id']} — {c['recommendation']}")
    if not recs:
        recs.append("✅ All checked articles are compliant. Maintain documentation and monitor for regulatory updates.")
    return recs


async def get_gap_analysis(project: dict, checks: list, score: float, tier: str) -> str:
    """Call LLM for gap analysis — reads key from Streamlit secrets or env."""

    # ── Read API key — try all possible sources ──────────────────────────────
    key = ""
    try:
        # Streamlit Cloud secrets (primary)
        key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

    if not key:
        try:
            # Fallback: environment variable
            import os
            key = os.environ.get("GROQ_API_KEY", "")
        except Exception:
            pass

    # ── Model — hardcoded to working version ─────────────────────────────────
    MODEL = "llama-3.1-8b-instant"

    # ── No key — return rule-based summary ───────────────────────────────────
    if not key:
        failed = [c for c in checks if c["status"] in ("non_compliant", "partial")]
        if not failed:
            return "✅ No significant compliance gaps identified. All checked articles are compliant."
        gaps = "\n".join(
            f"• {c['article_id']} ({c['article_title']}): {c['findings']}"
            for c in failed
        )
        return (
            f"**Score: {score}% | Risk: {tier.upper()}**\n\n"
            f"Compliance gaps identified:\n{gaps}\n\n"
            f"➡️ To enable AI-powered analysis, add GROQ_API_KEY to Streamlit Secrets."
        )

    # ── Call Groq API ─────────────────────────────────────────────────────────
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(
            api_key=key,
            base_url="https://api.groq.com/openai/v1"
        )
        failed = [c for c in checks if c["status"] in ("non_compliant", "partial")]
        failed_txt = "\n".join(
            f"- {c['article_id']}: {c['findings']}" for c in failed
        ) or "None — all compliant."

        resp = await client.chat.completions.create(
            model=MODEL,
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": "You are an EU AI Act compliance expert. Be concise and practical. Max 250 words."
                },
                {
                    "role": "user",
                    "content": (
                        f"AI project: {project['name']}\n"
                        f"Description: {project['description']}\n"
                        f"Risk tier: {tier}\n"
                        f"Score: {score}%\n"
                        f"Non-compliant/partial articles:\n{failed_txt}\n\n"
                        f"Provide: 1) gap analysis 2) top 3 immediate actions to achieve compliance."
                    )
                }
            ]
        )
        return resp.choices[0].message.content or ""

    except Exception as e:
        return (
            f"⚠️ AI gap analysis error: {e}\n\n"
            f"Please check your GROQ_API_KEY in Streamlit Secrets and ensure "
            f"the model 'llama-3.1-8b-instant' is available at console.groq.com"
        )


def generate_pdf(project: dict, classification: dict, checks: list,
                 score: float, recs: list, gap: str) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    H1  = ParagraphStyle("H1",  parent=styles["Heading1"], fontSize=16, textColor=colors.HexColor("#1a237e"))
    H2  = ParagraphStyle("H2",  parent=styles["Heading2"], fontSize=12, textColor=colors.HexColor("#283593"))
    B   = ParagraphStyle("B",   parent=styles["Normal"],   fontSize=9,  leading=13)
    SM  = ParagraphStyle("SM",  parent=styles["Normal"],   fontSize=8,  leading=11, textColor=colors.HexColor("#555"))
    story = []
    story.append(Paragraph("🇪🇺 EU AI Act Compliance Report", H1))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a237e")))
    story.append(Spacer(1, 4*mm))
    passed = score >= 60
    meta = [
        ["Project",   project["name"]],
        ["Date",      datetime.now().strftime("%d %B %Y")],
        ["Risk Tier", classification["risk_label"]],
        ["Score",     f"{score:.1f} / 100"],
        ["Result",    "✅ PASSED" if passed else "❌ REQUIRES ACTION"],
    ]
    t = Table(meta, colWidths=[45*mm, 125*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#e8eaf6")),
        ("BACKGROUND",(0,4),(-1,4),colors.HexColor("#e8f5e9") if passed else colors.HexColor("#ffebee")),
        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),9),
        ("BOX",(0,0),(-1,-1),0.5,colors.grey),
        ("INNERGRID",(0,0),(-1,-1),0.25,colors.lightgrey),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),8),
    ]))
    story += [t, Spacer(1, 4*mm)]
    story.append(Paragraph("Rationale", H2))
    story.append(Paragraph(classification["rationale"], B))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("Article Checks", H2))
    STATUS_MAP = {"compliant":"✅","partial":"⚠️","non_compliant":"❌"}
    for ch in checks:
        icon = STATUS_MAP.get(ch["status"],"—")
        row = [[Paragraph(f"<b>{ch['article_id']}: {ch['article_title']}</b> — {icon} {ch['status'].replace('_',' ').title()}", B)],
               [Paragraph(ch["findings"], B)]]
        if ch.get("recommendation"):
            row.append([Paragraph(f"Rec: {ch['recommendation']}", SM)])
        rt = Table(row, colWidths=[170*mm])
        bg = {"compliant":colors.HexColor("#e8f5e9"),"partial":colors.HexColor("#fff8e1"),
              "non_compliant":colors.HexColor("#ffebee")}.get(ch["status"], colors.white)
        rt.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),bg),
            ("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#ccc")),
            ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
            ("LEFTPADDING",(0,0),(-1,-1),8),
        ]))
        story += [rt, Spacer(1, 2*mm)]
    story.append(Paragraph("Gap Analysis", H2))
    story.append(Paragraph(gap.replace("\n","<br/>"), B))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("Recommendations", H2))
    for r in recs:
        story.append(Paragraph(f"• {r}", B))
    story.append(Spacer(1, 4*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    story.append(Paragraph("This report is a self-assessment tool and does not constitute legal advice. Reference: Regulation (EU) 2024/1689.", SM))
    doc.build(story)
    return buf.getvalue()


# ── Session state init ────────────────────────────────────────────────────────
if "projects" not in st.session_state:
    st.session_state["projects"] = {}
if "last_result_id" not in st.session_state:
    st.session_state["last_result_id"] = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:16px 0'>
        <div style='font-size:2.8rem'>🇪🇺</div>
        <div style='font-size:1.15rem;font-weight:800'>EU AI Act</div>
        <div style='font-size:0.8rem;opacity:0.6'>Compliance Platform</div>
    </div>""", unsafe_allow_html=True)
    st.divider()
    page = st.radio("", [
        "🏠 Home",
        "🔍 New Assessment",
        "📊 Results Dashboard",
        "📁 My Projects",
        "📖 EU AI Act Guide",
    ], label_visibility="collapsed")
    st.divider()
    total = len(st.session_state["projects"])
    assessed = sum(1 for p in st.session_state["projects"].values() if p.get("score") is not None)
    st.markdown(f"<div style='font-size:0.8rem;opacity:0.6;padding:4px'>{total} projects · {assessed} assessed</div>",
                unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: Home
# ─────────────────────────────────────────────────────────────────────────────
if page == "🏠 Home":
    st.markdown("""
    <div class="hero">
        <h1>🇪🇺 EU AI Act Compliance Platform</h1>
        <p>Self-service assessment tool — determine your AI project's risk tier,
        compliance gaps, and readiness under Regulation (EU) 2024/1689.</p>
    </div>""", unsafe_allow_html=True)

    projects = st.session_state["projects"]
    assessed_list = [p for p in projects.values() if p.get("score") is not None]
    passed_list = [p for p in assessed_list if p.get("score",0) >= 60]
    avg = sum(p["score"] for p in assessed_list) / len(assessed_list) if assessed_list else 0

    c1,c2,c3,c4 = st.columns(4)
    for col, num, lbl in [
        (c1, len(projects),    "Projects"),
        (c2, len(assessed_list),"Assessed"),
        (c3, len(passed_list), "Passed"),
        (c4, f"{avg:.0f}%",    "Avg Score"),
    ]:
        col.markdown(f'<div class="stat-card"><div class="stat-num">{num}</div>'
                     f'<div class="stat-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.write("")
    st.subheader("Risk Tier Overview")
    for label, req, color, examples, desc in [
        ("🔴 Unacceptable","PROHIBITED","#c62828",
         "Social scoring · Real-time biometrics in public · Subliminal manipulation",
         "Cannot be deployed. Narrow exceptions only (terrorism/missing persons with judicial authorisation)."),
        ("🟠 High Risk","FULL COMPLIANCE","#e65100",
         "Hiring AI · Medical devices · Credit scoring · Education systems · Law enforcement",
         "Articles 9–16 + conformity assessment required before deployment."),
        ("🟡 Limited Risk","TRANSPARENCY","#f9a825",
         "Chatbots · Deepfakes · Emotion recognition · Recommendation systems",
         "Must inform users they are interacting with AI. Label AI-generated content."),
        ("🟢 Minimal Risk","NO OBLIGATIONS","#2e7d32",
         "Spam filters · AI in games · Search engines",
         "No mandatory requirements. Voluntary codes of conduct encouraged."),
    ]:
        st.markdown(f"""
        <div style="border-left:5px solid {color};background:white;border:1px solid #eee;
                    border-radius:10px;padding:16px;margin:8px 0">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="font-size:1.05rem;font-weight:700">{label}</span>
                <span style="background:{color};color:white;padding:3px 12px;
                       border-radius:20px;font-size:0.78rem;font-weight:700">{req}</span>
            </div>
            <div style="font-size:0.85rem;color:#555;margin-top:5px"><b>Examples:</b> {examples}</div>
            <div style="font-size:0.85rem;color:#333;margin-top:3px">{desc}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box" style="margin-top:16px">
        <b>📅 Key Enforcement Dates:</b><br>
        • Feb 2025 — Prohibited practices (Art.5) apply<br>
        • Aug 2025 — GPAI model provisions apply<br>
        • Aug 2026 — High-risk AI system provisions fully apply<br>
        • Aug 2027 — Existing high-risk systems must comply
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: New Assessment
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🔍 New Assessment":
    st.header("🔍 New Compliance Assessment")
    st.caption("Submit your AI project to get a risk classification, article-by-article compliance check, and readiness score.")

    with st.form("form"):
        st.subheader("📋 Project Information")
        c1, c2 = st.columns(2)
        with c1:
            name        = st.text_input("Project Name *", placeholder="e.g. HireBot AI")
            category    = st.selectbox("AI Category *", [
                "biometric","critical_infrastructure","education","employment",
                "essential_services","law_enforcement","migration","justice",
                "medical_device","general_purpose","recommendation_system","chatbot","other"])
            deployer    = st.selectbox("Deployer Type", [
                "private_company","public_authority","research","ngo","individual"])
        with c2:
            description = st.text_area("Description *", height=100,
                placeholder="What does your AI system do? What decisions does it make?")
            intended    = st.text_input("Intended Use", placeholder="e.g. Screen job applicants")
            context     = st.text_input("Deployment Context", placeholder="e.g. Enterprise HR software in EU")

        st.divider()
        st.subheader("⚙️ System Characteristics")
        r1, r2, r3 = st.columns(3)
        with r1:
            pp  = st.checkbox("Processes personal data")
            pb  = st.checkbox("Processes biometric data")
            mad = st.checkbox("Makes autonomous decisions")
        with r2:
            afr = st.checkbox("Affects fundamental rights")
            rt  = st.checkbox("Operates in real-time")
        with r3:
            ho  = st.checkbox("Human oversight in place")
            td  = st.checkbox("Technical documentation exists")
            lm  = st.checkbox("Logging & monitoring in place")

        st.divider()
        st.subheader("✅ Compliance Measures Already Implemented")
        m1, m2, m3 = st.columns(3)
        with m1:
            dg = st.checkbox("Data governance framework")
            am = st.checkbox("Accuracy metrics & benchmarks")
        with m2:
            bt = st.checkbox("Bias testing & fairness evaluation")
            ex = st.checkbox("Explainability / interpretability")
        with m3:
            un = st.checkbox("User notification (AI disclosure)")
            ca = st.checkbox("Conformity assessment conducted")

        submitted = st.form_submit_button("🚀 Run Assessment", type="primary")

    if submitted:
        if not name.strip() or not description.strip():
            st.error("Please fill in the Project Name and Description.")
        else:
            project_data = {
                "name": name, "description": description, "category": category,
                "deployer_type": deployer, "intended_use": intended,
                "deployment_context": context,
                "processes_personal_data": pp, "processes_biometric_data": pb,
                "makes_autonomous_decisions": mad, "affects_fundamental_rights": afr,
                "used_in_real_time": rt, "has_human_oversight": ho,
                "has_technical_documentation": td, "has_logging_monitoring": lm,
                "has_data_governance": dg, "has_accuracy_metrics": am,
                "has_bias_testing": bt, "has_explainability": ex,
                "has_user_notification": un, "has_conformity_assessment": ca,
            }
            with st.spinner("Running EU AI Act compliance assessment…"):
                classification = classify_risk(project_data)
                checks         = run_checks(project_data, classification)
                score          = compute_score(checks)
                recs           = get_recommendations(checks)

                import asyncio
                gap = asyncio.run(get_gap_analysis(project_data, checks, score, classification["risk_tier"]))

                pid = str(uuid.uuid4())[:8]
                st.session_state["projects"][pid] = {
                    "id": pid, "project": project_data,
                    "classification": classification, "checks": checks,
                    "score": score, "recs": recs, "gap": gap,
                    "passed": score >= 60,
                    "created_at": datetime.now().isoformat(),
                }
                st.session_state["last_result_id"] = pid

            st.success("✅ Assessment complete! Go to **Results Dashboard** to view your results.")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: Results Dashboard
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📊 Results Dashboard":
    st.header("📊 Results Dashboard")

    pid = st.session_state.get("last_result_id")
    projects = st.session_state.get("projects", {})

    if not pid or pid not in projects:
        if projects:
            pid = sorted(projects.keys(), key=lambda k: projects[k].get("created_at",""), reverse=True)[0]
        else:
            st.info("No assessment yet. Go to **New Assessment** to get started.")
            st.stop()

    data = projects[pid]
    score = data["score"]
    tier  = data["classification"]["risk_tier"]
    checks = data["checks"]
    passed = data["passed"]

    # ── Gauge + tier ──────────────────────────────────────────────────────────
    col_g, col_t = st.columns([1, 2])
    with col_g:
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=score,
            title={"text": "Compliance Score"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar":  {"color": "#2e7d32" if score>=70 else "#f9a825" if score>=50 else "#c62828"},
                "steps": [
                    {"range":[0,60],  "color":"#ffebee"},
                    {"range":[60,80], "color":"#fff8e1"},
                    {"range":[80,100],"color":"#e8f5e9"},
                ],
                "threshold": {"line":{"color":"#1a237e","width":3}, "value":60},
            },
            number={"suffix":"%"},
        ))
        fig.update_layout(height=250, margin=dict(t=30,b=0,l=10,r=10))
        st.plotly_chart(fig, use_container_width=True)
        v_color = "#2e7d32" if passed else "#c62828"
        verdict = "✅ PASSED" if passed else "❌ REQUIRES ACTION"
        st.markdown(f"<div style='text-align:center;font-size:1.25rem;font-weight:800;color:{v_color}'>{verdict}</div>",
                    unsafe_allow_html=True)

    with col_t:
        tier_css = {"unacceptable":"tier-unacceptable","high":"tier-high",
                    "limited":"tier-limited","minimal":"tier-minimal"}.get(tier,"tier-minimal")
        st.markdown(f"""
        <div class="{tier_css}">
            <div style="font-size:1.3rem;font-weight:800">{data['classification']['risk_label']}</div>
            <div style="margin-top:6px">{data['project']['name']}</div>
            <div style="font-size:0.8rem;opacity:0.6;margin-top:2px">ID: {pid}</div>
        </div>""", unsafe_allow_html=True)

        compliant = sum(1 for c in checks if c["status"]=="compliant")
        partial   = sum(1 for c in checks if c["status"]=="partial")
        non_comp  = sum(1 for c in checks if c["status"]=="non_compliant")
        fig2 = go.Figure(go.Bar(
            x=[compliant, partial, non_comp],
            y=["Compliant","Partial","Non-Compliant"],
            orientation="h",
            marker_color=["#2e7d32","#f9a825","#c62828"],
        ))
        fig2.update_layout(height=160, margin=dict(t=10,b=10,l=10,r=10), showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ── Article checks ────────────────────────────────────────────────────────
    st.subheader("📋 Article-by-Article Results")
    for ch in checks:
        icon_map = {"compliant":"✅","partial":"⚠️","non_compliant":"❌","not_applicable":"—"}
        css_map  = {"compliant":"article-compliant","partial":"article-partial",
                    "non_compliant":"article-noncompliant","not_applicable":"article-na"}
        icon = icon_map.get(ch["status"],"—")
        css  = css_map.get(ch["status"],"article-na")
        pct  = int(ch["score"]*100)
        with st.expander(f"{icon} {ch['article_id']} — {ch['article_title']}  ({pct}%)"):
            st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
            st.markdown(f"**Reference:** {ch['reference']}")
            st.markdown(f"**Findings:** {ch['findings']}")
            if ch.get("recommendation"):
                st.markdown(f"**💡 Recommendation:** {ch['recommendation']}")
            st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ── Gap analysis ──────────────────────────────────────────────────────────
    st.subheader("🤖 Gap Analysis")
    st.markdown(f'<div class="info-box">{data["gap"].replace(chr(10),"<br>")}</div>',
                unsafe_allow_html=True)
    st.divider()

    # ── Recommendations ───────────────────────────────────────────────────────
    st.subheader("🎯 Recommendations")
    for rec in data["recs"]:
        css = "rec-critical" if "[CRITICAL]" in rec else "rec-important" if "[IMPORTANT]" in rec else "rec-ok"
        st.markdown(f'<div class="{css}">{rec}</div>', unsafe_allow_html=True)
    st.divider()

    # ── PDF ───────────────────────────────────────────────────────────────────
    st.subheader("📄 Download Report")
    if st.button("⬇️ Generate PDF Report", type="primary"):
        with st.spinner("Generating PDF…"):
            pdf = generate_pdf(
                data["project"], data["classification"],
                checks, score, data["recs"], data["gap"]
            )
            st.download_button(
                "📥 Download EU_AI_Act_Report.pdf", data=pdf,
                file_name=f"EU_AI_Act_{data['project']['name'].replace(' ','_')}.pdf",
                mime="application/pdf",
            )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: My Projects
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📁 My Projects":
    st.header("📁 My Projects")
    projects = st.session_state.get("projects", {})
    if not projects:
        st.info("No projects yet. Go to **New Assessment** to get started.")
        st.stop()

    st.caption(f"{len(projects)} project(s)")
    for pid, data in sorted(projects.items(), key=lambda x: x[1].get("created_at",""), reverse=True):
        score  = data.get("score")
        tier   = data["classification"]["risk_tier"]
        passed = data.get("passed")
        emoji  = {"unacceptable":"🔴","high":"🟠","limited":"🟡","minimal":"🟢"}.get(tier,"⚪")
        verdict = ("✅ Passed" if passed else "❌ Action needed") if passed is not None else "Pending"
        score_str = f"{score:.0f}%" if score is not None else "—"

        with st.expander(f"{emoji} **{data['project']['name']}** — {score_str} — {verdict}"):
            c1,c2 = st.columns(2)
            c1.write(f"**ID:** {pid}")
            c1.write(f"**Category:** {data['project']['category']}")
            c2.write(f"**Risk:** {tier.upper()}")
            c2.write(f"**Created:** {data.get('created_at','')[:10]}")

            col_view, col_pdf, col_del = st.columns(3)
            with col_view:
                if st.button("📊 View", key=f"v_{pid}"):
                    st.session_state["last_result_id"] = pid
                    st.rerun()
            with col_pdf:
                if st.button("📄 PDF", key=f"p_{pid}"):
                    pdf = generate_pdf(
                        data["project"], data["classification"],
                        data["checks"], data["score"], data["recs"], data["gap"]
                    )
                    st.download_button("📥 Save", data=pdf,
                        file_name=f"EU_AI_Act_{data['project']['name'].replace(' ','_')}.pdf",
                        mime="application/pdf", key=f"dl_{pid}")
            with col_del:
                if st.button("🗑️ Delete", key=f"d_{pid}"):
                    del st.session_state["projects"][pid]
                    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: EU AI Act Guide
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📖 EU AI Act Guide":
    st.header("📖 EU AI Act Reference Guide")
    st.caption("Regulation (EU) 2024/1689 — in force 1 August 2024")

    for section, content in {
        "📌 What is the EU AI Act?": """
The EU AI Act is the world's first comprehensive legal framework for AI — adopted March 2024, in force August 2024.

**Scope:** Applies to any provider or deployer of AI systems in the EU, regardless of where established. Also applies outside the EU if outputs are used inside the EU.

**Penalties:** Up to €35M or 7% of global turnover for prohibited practice violations; €15M or 3% for other violations.
""",
        "🔴 Prohibited Practices (Article 5)": """
1. Subliminal manipulation beyond awareness
2. Exploitation of vulnerabilities (age, disability, social/economic situation)
3. Social scoring by public authorities
4. Real-time remote biometric ID in public spaces by law enforcement (narrow exceptions only)
5. Emotion recognition in workplaces and educational institutions
6. Biometric categorisation to infer race, religion, political views, etc.
7. Predictive policing based purely on profiling
""",
        "🟠 High-Risk Obligations (Articles 9–16)": """
| Article | Requirement |
|---|---|
| Art.9  | Continuous risk management system |
| Art.10 | Data governance — representative, bias-free training data |
| Art.11 | Technical documentation (Annex IV) |
| Art.12 | Tamper-proof automatic event logging |
| Art.13 | Transparency — instructions for use |
| Art.14 | Human oversight — pause, override, intervene |
| Art.15 | Accuracy, robustness, cybersecurity |
| Art.43 | Conformity assessment + CE marking |
| Art.49 | EU database registration |
""",
        "🟡 Transparency Obligations (Article 50)": """
- **Chatbots:** Disclose AI nature at first interaction
- **Deepfakes:** Label all AI-generated images, video, audio
- **Emotion recognition:** Inform persons when their emotions are being detected
- **Biometric categorisation:** Inform persons when being categorised
""",
        "🏗️ GPAI Models (Articles 51–55)": """
General-Purpose AI Models (GPT-4, Claude, Gemini, etc.):

**All GPAI providers:**
- Technical documentation
- Copyright compliance + training data summary
- Open source exception for weights published under free licence

**Systemic risk GPAI** (>10²⁵ FLOPs training compute):
- Adversarial testing and red-teaming
- Systemic risk assessment and mitigation
- Incident reporting to European AI Office
- Cybersecurity protection
""",
    }.items():
        with st.expander(section):
            st.markdown(content)
