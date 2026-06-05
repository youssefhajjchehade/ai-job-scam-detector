"""Streamlit dashboard for the JobShield AI demo.

The dashboard loads the trained Keras model directly, so it can run on
Hugging Face Spaces without a separate FastAPI server. FastAPI remains in
api/ for API testing and for showing model-serving knowledge.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Make project root importable when this file is run directly.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.model_loader import load_job_scam_model, load_thresholds
from src.predict import predict_job_risk


st.set_page_config(
    page_title="JobShield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_resource(show_spinner=False)
def get_model():
    """Load the trained Keras model once per Streamlit session."""
    return load_job_scam_model()


@st.cache_data(show_spinner=False)
def get_thresholds() -> dict:
    return load_thresholds()


thresholds = get_thresholds()
LOW_THRESHOLD = thresholds.get("default_threshold", 0.5)
HIGH_THRESHOLD = thresholds.get("high_risk_threshold", 0.9345)

SUSPICIOUS_SAMPLE = """We are hiring remote workers immediately. No experience needed.
Earn $5000 per week from home. Training provided.
Send your personal details and payment information to get started.
Apply now, limited spots available."""

NORMAL_SAMPLE = """Software Engineering Intern needed for a technology company.
Responsibilities include building backend APIs, writing unit tests,
working with Git, and collaborating with senior engineers.
Applicants should know Python, JavaScript, and basic databases."""

if "job_text" not in st.session_state:
    st.session_state.job_text = ""
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "analysis_error" not in st.session_state:
    st.session_state.analysis_error = None


st.markdown(
    """
    <style>
        :root {
            --bg: #020617;
            --panel: rgba(15, 23, 42, 0.78);
            --panel-strong: rgba(15, 23, 42, 0.95);
            --border: rgba(148, 163, 184, 0.20);
            --text: #e5e7eb;
            --muted: #94a3b8;
            --blue: #38bdf8;
            --blue-strong: #2563eb;
            --green: #22c55e;
            --yellow: #f59e0b;
            --red: #ef4444;
        }

        html, body, .stApp,
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at top left, rgba(56, 189, 248, 0.20), transparent 30%),
                radial-gradient(circle at 90% 10%, rgba(37, 99, 235, 0.20), transparent 30%),
                linear-gradient(135deg, #020617 0%, #0f172a 52%, #111827 100%) !important;
            color: var(--text) !important;
        }

        [data-testid="stHeader"], [data-testid="stToolbar"] {
            background: transparent !important;
        }

        [data-testid="stToolbar"] {
            display: none !important;
        }

        .block-container {
            max-width: 1180px !important;
            padding-top: 2.1rem !important;
            padding-bottom: 2.5rem !important;
        }

        .hero {
            padding: 2rem 2.2rem;
            border-radius: 28px;
            background:
                radial-gradient(circle at 96% 0%, rgba(34, 211, 238, 0.18), transparent 31%),
                linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(30, 41, 59, 0.93));
            border: 1px solid rgba(148, 163, 184, 0.22);
            box-shadow: 0 26px 80px rgba(0, 0, 0, 0.34);
            margin-bottom: 1.45rem;
        }

        .kicker {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            color: #67e8f9;
            background: rgba(8, 145, 178, 0.10);
            border: 1px solid rgba(103, 232, 249, 0.20);
            padding: 0.32rem 0.72rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 900;
            letter-spacing: 0.11em;
            text-transform: uppercase;
            margin-bottom: 0.95rem;
        }

        .title {
            color: #ffffff;
            font-size: clamp(2.6rem, 5vw, 4.6rem);
            line-height: 0.95;
            font-weight: 950;
            letter-spacing: -0.07em;
            margin-bottom: 0.85rem;
        }

        .subtitle {
            color: #cbd5e1;
            max-width: 840px;
            font-size: 1.03rem;
            line-height: 1.7;
        }

        .panel {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 1.25rem;
            box-shadow: 0 20px 55px rgba(0, 0, 0, 0.25);
            min-height: 505px;
        }

        .section-label {
            color: #f8fafc;
            font-size: 1.04rem;
            font-weight: 900;
            letter-spacing: -0.01em;
            margin-bottom: 0.35rem;
        }

        .section-caption {
            color: var(--muted);
            font-size: 0.88rem;
            line-height: 1.55;
            margin-bottom: 1rem;
        }

        .small-note {
            color: #64748b;
            font-size: 0.8rem;
            line-height: 1.6;
            margin-top: 0.9rem;
        }

        .result-card {
            padding: 1.25rem;
            border-radius: 21px;
            margin-bottom: 1rem;
            box-shadow: 0 18px 46px rgba(0, 0, 0, 0.18);
        }

        .risk-high {
            background: linear-gradient(135deg, rgba(127, 29, 29, 0.96), rgba(239, 68, 68, 0.24));
            border: 1px solid rgba(248, 113, 113, 0.34);
        }

        .risk-medium {
            background: linear-gradient(135deg, rgba(120, 53, 15, 0.96), rgba(245, 158, 11, 0.24));
            border: 1px solid rgba(251, 191, 36, 0.34);
        }

        .risk-low {
            background: linear-gradient(135deg, rgba(20, 83, 45, 0.96), rgba(34, 197, 94, 0.20));
            border: 1px solid rgba(74, 222, 128, 0.34);
        }

        .risk-label {
            color: #ffffff;
            font-size: 1.75rem;
            font-weight: 950;
            line-height: 1.05;
            letter-spacing: -0.04em;
            margin-bottom: 0.26rem;
        }

        .risk-sub {
            color: #e5e7eb;
            font-weight: 700;
            font-size: 0.96rem;
        }

        .score-box {
            background: rgba(2, 6, 23, 0.48);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 18px;
            padding: 1rem;
            margin-bottom: 1rem;
        }

        .score-number {
            color: #f8fafc;
            font-size: 2.35rem;
            font-weight: 950;
            line-height: 1;
            letter-spacing: -0.04em;
        }

        .score-label {
            color: var(--muted);
            font-size: 0.76rem;
            font-weight: 850;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 0.4rem;
        }

        .bar-bg {
            width: 100%;
            height: 12px;
            background: rgba(148, 163, 184, 0.18);
            border-radius: 999px;
            margin-top: 0.85rem;
            overflow: hidden;
        }

        .bar-fill {
            height: 12px;
            border-radius: 999px;
            background: linear-gradient(90deg, #22c55e, #f59e0b, #ef4444);
        }

        .empty-state, .warning, .clean {
            padding: 0.9rem 1rem;
            border-radius: 16px;
            margin-bottom: 0.65rem;
            font-size: 0.92rem;
            line-height: 1.6;
        }

        .empty-state {
            background: rgba(2, 6, 23, 0.35);
            border: 1px dashed rgba(148, 163, 184, 0.28);
            color: #cbd5e1;
        }

        .warning {
            background: rgba(239, 68, 68, 0.10);
            border: 1px solid rgba(248, 113, 113, 0.24);
            color: #fecaca;
            font-weight: 700;
        }

        .clean {
            background: rgba(34, 197, 94, 0.10);
            border: 1px solid rgba(74, 222, 128, 0.24);
            color: #bbf7d0;
            font-weight: 700;
        }

        div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stMarkdownContainer"] li,
        label, span {
            color: inherit;
        }

        div[data-testid="stTextArea"] textarea {
            background: rgba(2, 6, 23, 0.62) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(148, 163, 184, 0.24) !important;
            border-radius: 18px !important;
            min-height: 300px !important;
            font-size: 0.95rem !important;
            line-height: 1.55 !important;
            box-shadow: 0 14px 30px rgba(0, 0, 0, 0.18) !important;
        }

        div[data-testid="stTextArea"] textarea::placeholder {
            color: #64748b !important;
            opacity: 1 !important;
        }

        div[data-testid="stTextArea"] textarea:focus {
            border-color: rgba(56, 189, 248, 0.72) !important;
            box-shadow: 0 0 0 1px rgba(56, 189, 248, 0.24), 0 14px 30px rgba(0, 0, 0, 0.18) !important;
        }

        div.stButton > button,
        div[data-testid="stButton"] > button,
        button[kind="secondary"],
        button[kind="primary"] {
            background: linear-gradient(135deg, #2563eb, #0891b2) !important;
            color: #ffffff !important;
            border: 1px solid rgba(125, 211, 252, 0.30) !important;
            border-radius: 14px !important;
            min-height: 44px !important;
            font-weight: 850 !important;
            box-shadow: 0 12px 26px rgba(37, 99, 235, 0.18) !important;
            transition: 0.18s ease !important;
        }

        div.stButton > button:hover,
        div[data-testid="stButton"] > button:hover,
        button[kind="secondary"]:hover,
        button[kind="primary"]:hover {
            transform: translateY(-1px) !important;
            color: #ffffff !important;
            border-color: rgba(186, 230, 253, 0.62) !important;
            box-shadow: 0 16px 32px rgba(37, 99, 235, 0.25) !important;
        }

        div.stButton > button p,
        div[data-testid="stButton"] > button p,
        button[kind="secondary"] p,
        button[kind="primary"] p {
            color: #ffffff !important;
            font-weight: 850 !important;
        }

        div[data-testid="stAlert"] {
            border-radius: 16px !important;
            background: rgba(120, 53, 15, 0.50) !important;
            color: #fde68a !important;
            border: 1px solid rgba(251, 191, 36, 0.22) !important;
        }

        @media (max-width: 900px) {
            .block-container { padding-top: 1rem !important; }
            .hero { padding: 1.35rem !important; }
            .panel { min-height: auto !important; margin-bottom: 1rem !important; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="hero">
        <div class="kicker">Local AI job safety tool</div>
        <div class="title">JobShield AI</div>
        <div class="subtitle">
            Paste a job post and get a risk tier, scam probability, and warning signals.
            The dashboard runs the trained Keras NLP model directly, so no paid AI API is required.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1.05, 0.95], gap="large")

with left:
    with st.container():
       
        st.markdown('<div class="section-label">Job post</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-caption">Use one of the samples or paste a real job description.</div>',
            unsafe_allow_html=True,
        )

        sample_col_1, sample_col_2 = st.columns(2)
        with sample_col_1:
            if st.button("Suspicious sample", use_container_width=True):
                st.session_state.job_text = SUSPICIOUS_SAMPLE
                st.session_state.analysis_result = None
                st.session_state.analysis_error = None
                st.rerun()
        with sample_col_2:
            if st.button("Normal sample", use_container_width=True):
                st.session_state.job_text = NORMAL_SAMPLE
                st.session_state.analysis_result = None
                st.session_state.analysis_error = None
                st.rerun()

        job_text = st.text_area(
            "Job post",
            key="job_text",
            label_visibility="collapsed",
            placeholder="Paste the job post here...",
            height=300,
        )

        if st.button("Analyze job post", use_container_width=True):
            st.session_state.analysis_result = None
            st.session_state.analysis_error = None

            if len(job_text.strip()) < 20:
                st.session_state.analysis_error = "Please paste a longer job post before running analysis."
            else:
                with st.spinner("Loading model and analyzing..."):
                    model = get_model()
                    st.session_state.analysis_result = predict_job_risk(
                        job_text=job_text,
                        model=model,
                        low_threshold=LOW_THRESHOLD,
                        high_threshold=HIGH_THRESHOLD,
                    )

        st.markdown(
            """
            <div class="small-note">
                FastAPI is included for API testing, but this dashboard runs the model directly for simple free deployment.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

with right:
    with st.container():

        st.markdown('<div class="section-label">Analysis result</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-caption">Prediction, confidence score, and rule-based warning signals.</div>',
            unsafe_allow_html=True,
        )

        if st.session_state.analysis_error:
            st.warning(st.session_state.analysis_error)

        elif st.session_state.analysis_result is None:
            st.markdown(
                """
                <div class="empty-state">
                    No analysis yet. Paste a job post, then click <strong>Analyze job post</strong>.
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:
            result = st.session_state.analysis_result
            prediction = result["prediction"]
            risk_level = result["risk_level"]
            scam_probability = result["scam_probability"]
            warning_signs = result["warning_signs"]

            risk_class = {
                "High Risk": "risk-high",
                "Medium Risk": "risk-medium",
                "Low Risk": "risk-low",
            }.get(risk_level, "risk-medium")

            probability_percent = scam_probability * 100
            bar_width = max(2, min(100, probability_percent))

            st.markdown(
                f"""
                <div class="result-card {risk_class}">
                    <div class="risk-label">{risk_level}</div>
                    <div class="risk-sub">{prediction}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="score-box">
                    <div class="score-number">{probability_percent:.2f}%</div>
                    <div class="score-label">Scam probability</div>
                    <div class="bar-bg">
                        <div class="bar-fill" style="width: {bar_width}%;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown('<div class="section-label" style="font-size: 0.98rem; margin-top: 1rem;">Warning signals</div>', unsafe_allow_html=True)
            if warning_signs:
                for sign in warning_signs:
                    st.markdown(f'<div class="warning">{sign}</div>', unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div class="clean">No major rule-based warning signs detected.</div>',
                    unsafe_allow_html=True,
                )

            st.markdown(
                """
                <div class="small-note">
                    This is a decision-support demo. Always verify the company, recruiter identity,
                    salary claims, and any request for personal or financial information.
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)
