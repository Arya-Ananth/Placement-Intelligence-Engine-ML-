import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
from Upskill_engine import init_db, train_model, sync_student_profile, calculate_skill_score, SKILL_WEIGHTS
from compile_resume import fetch_latest_student, generate_resume

# Page layout configuration
st.set_page_config(
    page_title="PIE | Placement Intelligence Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Modern Custom CSS: Glassmorphism, Custom Metrics, Radiant Gradients ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main Background Accent */
    .stApp {
        background-color: #0B0F17;
        color: #F1F5F9;
    }
    
    /* Hero Header Styling */
    .hero-container {
        padding: 1.8rem 2rem;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        backdrop-filter: blur(12px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        margin-bottom: 1.5rem;
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #6366F1 0%, #38BDF8 50%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }
    
    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        font-weight: 400;
        max-width: 850px;
    }
    
    .pill-tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .pill-active {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(52, 211, 153, 0.3);
    }
    
    .pill-accent {
        background: rgba(99, 102, 241, 0.15);
        color: #818CF8;
        border: 1px solid rgba(129, 140, 248, 0.3);
    }

    /* Glass Cards */
    .glass-card {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.4rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
        margin-bottom: 1.2rem;
    }
    
    /* Stat Metric Box */
    .metric-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: left;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        border-color: rgba(56, 189, 248, 0.4);
        transform: translateY(-2px);
    }
    .metric-label {
        color: #94A3B8;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        color: #F8FAFC;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 0.2rem;
    }
    .metric-value-highlight {
        background: linear-gradient(90deg, #38BDF8, #818CF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Custom Streamlit UI Overrides */
    div[data-testid="stSidebar"] {
        background-color: #070A10;
        border-right: 1px solid rgba(255, 255, 255, 0.07);
    }
    
    div[data-testid="stForm"] {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 14px;
        padding: 1.5rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.6);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0 16px;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4F46E5, #2563EB) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
    }
    
    .badge-chip {
        display: inline-block;
        background: rgba(56, 189, 248, 0.12);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.25);
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 500;
        margin: 3px 2px;
    }

    .badge-missing {
        background: rgba(239, 68, 68, 0.12);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.25);
    }
</style>
""", unsafe_allow_html=True)

# --- Model & DB Initialization ---
if "model_ready" not in st.session_state:
    init_db()
    st.session_state.model, st.session_state.features = train_model()
    st.session_state.model_ready = True

# Benchmark Track Definitions
ROLE_BENCHMARKS = {
    "AI / GenAI & LLM Application Engineer": ["Python", "LangChain", "LlamaIndex", "RAG Pipelines", "Vector DBs", "PyTorch", "Prompt Engineering", "Hugging Face"],
    "Autonomous AI Agent Developer": ["Python", "LangGraph", "CrewAI", "AutoGen", "FastAPI", "Vector DBs", "Prompt Engineering"],
    "Machine Learning Engineer (MLE)": ["Python", "PyTorch", "Scikit-Learn", "TensorFlow", "Pandas / NumPy", "MLflow", "Docker", "SQL"],
    "MLOps & AI Infrastructure Engineer": ["Docker", "Kubernetes", "MLflow", "CI/CD (GitHub Actions)", "Python", "Linux / Bash", "AWS"],
    "Computer Vision & Perception Engineer": ["OpenCV", "PyTorch", "C++", "TensorRT", "YOLO", "Python"],
    "NLP & Speech Processing Engineer": ["Python", "Hugging Face", "PyTorch", "Prompt Engineering", "FastAPI"],
    "Data Scientist (Product & Analytics)": ["Python", "R", "SQL", "Scikit-Learn", "Pandas / NumPy"],
    "Backend & Microservices Engineer": ["Java (Spring Boot)", "Go (Golang)", "FastAPI", "PostgreSQL", "Redis", "Apache Kafka", "Docker", "System Design"],
    "Frontend & UI/UX Web Engineer": ["TypeScript", "JavaScript", "React", "Next.js", "Tailwind CSS"],
    "Full Stack Web Developer": ["TypeScript", "React", "Next.js", "Node.js", "FastAPI", "PostgreSQL", "MongoDB", "Docker", "Git / GitHub"],
    "Systems & Performance Software Engineer": ["Rust", "C++", "Linux / Bash", "Docker", "System Design"],
    "Embedded Systems & Firmware Engineer": ["C", "C++", "Linux / Bash", "Git / GitHub"],
    "API & Platform Integration Engineer": ["FastAPI", "Node.js", "PostgreSQL", "Redis", "Docker", "Git / GitHub"],
    "Data Engineer (Modern Data Stack)": ["Python", "SQL", "Apache Spark (PySpark)", "dbt", "Snowflake", "Apache Kafka", "AWS", "Git / GitHub"],
    "Analytics Engineer / Modern BI Developer": ["SQL", "dbt", "Snowflake", "Python", "Git / GitHub"],
    "Real-time Data Streaming Engineer": ["Apache Kafka", "Redis", "Go (Golang)", "Java (Spring Boot)", "Docker"],
    "Database Administrator & Tuning Architect": ["PostgreSQL", "Redis", "MongoDB", "SQL", "Linux / Bash"],
    "Cloud Solutions Architect": ["AWS", "Azure", "GCP", "Terraform", "Docker", "Kubernetes", "System Design"],
    "DevOps & Infrastructure Automation Engineer": ["Docker", "Kubernetes", "Terraform", "CI/CD (GitHub Actions)", "Linux / Bash", "AWS"],
    "Site Reliability Engineer (SRE)": ["Linux / Bash", "Prometheus", "Grafana", "Go (Golang)", "Python", "Kubernetes"],
    "Platform & Internal Developer Tools Engineer": ["Kubernetes", "Terraform", "Go (Golang)", "Docker", "CI/CD (GitHub Actions)"],
    "Application Security (AppSec) Engineer": ["OWASP Top 10", "Burp Suite", "Python", "Linux / Bash", "Git / GitHub"],
    "DevSecOps & Cloud Security Engineer": ["Docker", "Kubernetes", "Terraform", "AWS", "CI/CD (GitHub Actions)", "Linux / Bash"],
    "Penetration Tester & Ethical Hacker": ["Burp Suite", "Wireshark", "Python", "Linux / Bash"],
    "SOC & Cybersecurity Incident Analyst": ["Wireshark", "Linux / Bash", "Python"],
    "Cross-Platform Mobile Developer": ["Flutter", "Dart", "React Native", "TypeScript", "Git / GitHub"],
    "Native iOS Engineer": ["Swift", "SwiftUI", "Git / GitHub"],
    "Native Android Engineer": ["Kotlin", "Jetpack Compose", "Git / GitHub"],
    "Quantitative & HFT Developer": ["C++", "Rust", "Python", "DSA", "System Design"],
    "Software Development Engineer in Test (SDET)": ["Python", "Java (Spring Boot)", "CI/CD (GitHub Actions)", "Git / GitHub"]
}

TECH_SKILL_OPTIONS = sorted(list(SKILL_WEIGHTS.keys()))

# --- Sidebar ---
with st.sidebar:
    st.markdown("### ⚡ **PIE Engine Control**")
    st.caption("v2.2 • Production ML Readiness & ATS Resume Compiler")
    st.markdown("<span class='pill-tag pill-active'>🟢 Pipeline Active</span><span class='pill-tag pill-accent'>ReportLab Local PDF</span>", unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("#### 🎯 **Target Track Categories**")
    st.markdown("• **AI / ML / MLOps** (PyTorch, LangChain, RAG, Docker)")
    st.markdown("• **SDE & Backend Core** (Java, C++, Go, Kafka, SQL)")
    st.markdown("• **Cloud & Infrastructure** (AWS, Terraform, K8s)")
    st.markdown("• **Full Stack & Modern Web** (React, Next.js, FastAPI)")

    st.divider()
    
    st.markdown("#### ⚙️ **ML Model Specs**")
    st.info("🌲 **Classifier:** Random Forest (100 Trees)\n\n📊 **Features:** GPA, Problems Solved, Certifications, CF Rating, Skill Score\n\n📄 **Resume Output:** ATS PDF & TeX Source")

# --- Hero Section ---
st.markdown("""
<div class="hero-container">
    <div class="hero-title">Placement Intelligence Engine</div>
    <div class="hero-subtitle">
        Multi-platform competitive programming sync, algorithmic skill matrix quantification, Random Forest ML readiness scoring, and instant ATS-compliant PDF resume generation.
    </div>
</div>
""", unsafe_allow_html=True)

# --- Navigation Tabs ---
tab_eval, tab_resume, tab_roadmap = st.tabs([
    "🎯 Profile & Live Evaluation",
    "📄 ATS Resume Hub",
    "🛠️ Skill Gap & Roadmap"
])

# -------------------------------------------------------------------
# TAB 1: PROFILE & LIVE EVALUATION
# -------------------------------------------------------------------
with tab_eval:

    col_input, col_results = st.columns([1, 1], gap="large")

    with col_input:
        st.markdown("### 📋 Student Profile Setup")
        with st.form("student_input_form", border=True):
            f_id, f_name = st.columns([1, 2])
            with f_id:
                student_id = st.number_input("Student ID / Roll No", min_value=1, value=101, step=1)
            with f_name:
                name = st.text_input("Full Name", value="", placeholder="e.g. Alex Rivera")

            f_gpa, f_certs = st.columns(2)
            with f_gpa:
                gpa = st.number_input("Cumulative GPA (0-10)", min_value=0.0, max_value=10.0, value=9.25, step=0.01, format="%.2f")
            with f_certs:
                certifications = st.number_input("Verified Certifications", min_value=0, max_value=20, value=2, step=1)

            target_role = st.selectbox("Target Career Track", list(ROLE_BENCHMARKS.keys()))

            default_skills = ["DSA", "C++", "Python", "SQL", "Git / GitHub"]
            if target_role in ROLE_BENCHMARKS:
                default_skills = ROLE_BENCHMARKS[target_role][:4] + ["DSA", "Git / GitHub"]
                default_skills = list(set([s for s in default_skills if s in TECH_SKILL_OPTIONS]))

            selected_skills = st.multiselect(
                "Technical Skills & Stack Matrix",
                options=TECH_SKILL_OPTIONS,
                default=default_skills
            )

            f_lc, f_cf = st.columns(2)
            with f_lc:
                leetcode_username = st.text_input("LeetCode Handle", value="", placeholder="e.g. alex_rivera")
            with f_cf:
                codeforces_handle = st.text_input("Codeforces Handle", value="", placeholder="e.g. alex_cf")

            submit_btn = st.form_submit_button("🚀 Sync Profile & Evaluate Readiness", use_container_width=True)

    with col_results:
        st.markdown("### 📊 Live Evaluation Dashboard")
        
        if submit_btn:
            benchmark_skills = ROLE_BENCHMARKS[target_role]
            matched_skills = [s for s in selected_skills if s in benchmark_skills]
            role_fit_pct = round((len(matched_skills) / len(benchmark_skills)) * 100, 1)

            with st.spinner("Fetching platform handles and running Random Forest inference..."):
                sync_student_profile(
                    student_id=student_id,
                    name=name if name else f"Student #{student_id}",
                    gpa=gpa,
                    certifications=certifications,
                    skills_list=selected_skills,
                    target_role=target_role,
                    leetcode_username=leetcode_username,
                    codeforces_handle=codeforces_handle,
                    model=st.session_state.model,
                    feature_names=st.session_state.features,
                    role_fit_pct=role_fit_pct
                )
                student = fetch_latest_student(student_id)

            if student:
                score = float(student["placement_score"])
                st.session_state.active_student = student
                st.session_state.active_skills = selected_skills

                # --- Plotly Gauge Chart for Readiness ---
                gauge_color = "#10B981" if score >= 80 else ("#F59E0B" if score >= 60 else "#EF4444")
                
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    number={"suffix": "%", "font": {"size": 36, "color": "#F8FAFC"}},
                    title={"text": f"<b>Placement Probability ({target_role.split(' ')[0]})</b>", "font": {"size": 14, "color": "#94A3B8"}},
                    gauge={
                        "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#475569"},
                        "bar": {"color": gauge_color},
                        "bgcolor": "rgba(30, 41, 59, 0.5)",
                        "borderwidth": 1,
                        "bordercolor": "rgba(255,255,255,0.1)",
                        "steps": [
                            {"range": [0, 60], "color": "rgba(239, 68, 68, 0.15)"},
                            {"range": [60, 80], "color": "rgba(245, 158, 11, 0.15)"},
                            {"range": [80, 100], "color": "rgba(16, 185, 129, 0.15)"}
                        ]
                    }
                ))
                fig_gauge.update_layout(
                    height=220,
                    margin=dict(l=20, r=20, t=30, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_gauge, use_container_width=True)

                # --- Key Metrics Grid ---
                m1, m2, m3 = st.columns(3)
                m1.markdown(f"<div class='metric-card'><div class='metric-label'>Problems Solved</div><div class='metric-value'>{student['problems_solved']}</div></div>", unsafe_allow_html=True)
                m2.markdown(f"<div class='metric-card'><div class='metric-label'>Cumulative GPA</div><div class='metric-value'>{student['gpa']}</div></div>", unsafe_allow_html=True)
                m3.markdown(f"<div class='metric-card'><div class='metric-label'>CF Contest Rating</div><div class='metric-value'>{student['codeforces_rating']}</div></div>", unsafe_allow_html=True)

                st.write("")
                k1, k2 = st.columns(2)
                live_skill_score = calculate_skill_score(selected_skills)
                k1.markdown(f"<div class='metric-card'><div class='metric-label'>Skill Stack Score</div><div class='metric-value metric-value-highlight'>{live_skill_score} <span style='font-size:1rem;'>/ 100</span></div></div>", unsafe_allow_html=True)
                k2.markdown(f"<div class='metric-card'><div class='metric-label'>Target Track Fit</div><div class='metric-value metric-value-highlight'>{role_fit_pct}%</div></div>", unsafe_allow_html=True)

                st.write("")
                if score >= 80:
                    st.success(f"🎯 **Tier 1 Placement Readiness ({score:.1f}%)**: Candidate meets product company benchmarks.")
                elif score >= 60:
                    st.warning(f"⚡ **Tier 2 Placement Readiness ({score:.1f}%)**: Solid baseline. Expand problem solving count beyond 400+.")
                else:
                    st.error(f"📈 **Upskill Recommended ({score:.1f}%)**: Focus on increasing high-weight core competencies.")

                # Generate Resume
                pdf_path = generate_resume(student)

                st.divider()
                st.markdown("#### 📄 Resume Available")
                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📥 Download ATS PDF Resume",
                            data=f,
                            file_name=f"resume_{student_id}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key="dl_pdf_tab1"
                        )
        else:
            if "active_student" in st.session_state and st.session_state.active_student:
                st.info("💡 Displaying last evaluated student profile. Modify inputs and submit to run a new evaluation.")
            else:
                st.info("👈 Fill out the student profile on the left and click **Sync Profile & Evaluate Readiness** to run inference.")

# -------------------------------------------------------------------
# TAB 2: ATS RESUME HUB
# -------------------------------------------------------------------
with tab_resume:
    st.markdown("### 📄 Dynamic ATS Resume Engine")
    
    if "active_student" in st.session_state and st.session_state.active_student:
        student = st.session_state.active_student
        student_id = student["student_id"]
        pdf_path = os.path.join("resumes", f"resume_{student_id}.pdf")

        res_card, download_sec = st.columns([1.2, 1], gap="large")

        with res_card:
            st.markdown(f"#### 👤 Evaluated Profile: **{student['name']}**")
            st.write(f"• **Target Role Track:** `{student['target_role']}`")
            st.write(f"• **Placement Probability Score:** `{student['placement_score']}%`")
            st.write(f"• **LeetCode Username:** `{student['leetcode_username']}`")
            st.write(f"• **Codeforces Handle:** `{student['codeforces_handle']}`")
            st.write(f"• **Skills Tagged:** `{student['skills']}`")

        with download_sec:
            st.markdown("#### 📥 Instant PDF Download")
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                    st.download_button(
                        label=f"📥 Download ATS PDF Resume ({len(pdf_bytes)//1024} KB)",
                        data=pdf_bytes,
                        file_name=f"resume_{student_id}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key="dl_pdf_tab2"
                    )
                st.success("✅ **ATS PDF Resume Ready**")
            else:
                st.warning("⚠️ PDF file not yet compiled. Click Evaluate in Tab 1 to generate PDF.")
    else:
        st.info("ℹ️ No active student profile loaded yet. Please complete Tab 1 (Profile & Live Evaluation) to generate an ATS resume.")


# -------------------------------------------------------------------
# TAB 3: SKILL GAP & ROADMAP
# -------------------------------------------------------------------
with tab_roadmap:
    st.markdown("### 🛠️ Career Track Benchmark & Skill Gap Analyzer")
    
    selected_role_roadmap = st.selectbox("Select Target Track to Analyze", list(ROLE_BENCHMARKS.keys()), key="roadmap_role")
    
    benchmark = ROLE_BENCHMARKS[selected_role_roadmap]
    
    current_skills = st.session_state.get("active_skills", ["DSA", "C++", "Python", "SQL", "Git / GitHub"])
    
    acquired = [s for s in benchmark if s in current_skills]
    missing = [s for s in benchmark if s not in current_skills]
    
    gap_col1, gap_col2 = st.columns(2, gap="large")

    with gap_col1:
        st.markdown(f"#### 🎯 Target Track: **{selected_role_roadmap}**")
        st.markdown(f"**Benchmark Skill Coverage:** `{len(acquired)} / {len(benchmark)}` skills ({round(len(acquired)/len(benchmark)*100, 1)}%)")
        
        st.write("")
        st.markdown("##### ✅ Acquired Benchmark Skills")
        if acquired:
            chips_html = "".join([f"<span class='badge-chip'>{s}</span>" for s in acquired])
            st.markdown(chips_html, unsafe_allow_html=True)
        else:
            st.caption("No benchmark skills matched in current stack.")

        st.write("")
        st.markdown("##### ❌ Skill Gaps (Missing Benchmark Requirements)")
        if missing:
            missing_chips = "".join([f"<span class='badge-chip badge-missing'>{s}</span>" for s in missing])
            st.markdown(missing_chips, unsafe_allow_html=True)
        else:
            st.success("🎉 Perfect Benchmark Alignment! All required track skills are present.")

    with gap_col2:
        st.markdown("#### 🚀 Actionable Upskill Recommendations")
        
        if missing:
            st.markdown("To maximize placement probability for this track, prioritize acquiring:")
            for sk in missing:
                weight = SKILL_WEIGHTS.get(sk, 10)
                st.markdown(f"• **{sk}** *(Weight: +{weight} pts)*: Essential core dependency for {selected_role_roadmap}.")
        else:
            st.markdown("• Focus on competitive platform ratings (LeetCode 1800+ / Codeforces 1400+).")
            st.markdown("• Build high-impact open source or production project applications.")

        st.divider()
        st.markdown("##### 📈 Strategic Skill Weight Distribution")
        df_weights = pd.DataFrame([
            {"Skill": sk, "Impact Weight": SKILL_WEIGHTS.get(sk, 10), "Status": "Acquired" if sk in acquired else "Missing"}
            for sk in benchmark
        ])
        fig_bars = px.bar(
            df_weights,
            x="Skill",
            y="Impact Weight",
            color="Status",
            color_discrete_map={"Acquired": "#38BDF8", "Missing": "#F87171"},
            title=f"Impact Weights for {selected_role_roadmap}"
        )
        fig_bars.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94A3B8"),
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_bars, use_container_width=True)
