import streamlit as st
import os
from Upskill_engine import init_db, train_model, sync_student_profile, calculate_skill_score
from compile_resume import fetch_latest_student, generate_resume

# Page layout configuration
st.set_page_config(
    page_title="PIE | Placement Intelligence Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #4F46E5, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.0rem;
        margin-bottom: 1.2rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.7rem;
        color: #38BDF8;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

if "model_ready" not in st.session_state:
    init_db()
    st.session_state.model, st.session_state.features = train_model()
    st.session_state.model_ready = True

with st.sidebar:
    st.markdown("## ⚡ **PIE Engine**")
    st.caption("v2.2 • Skills & Multi-Platform AI Evaluator")
    st.divider()
    st.markdown("### ⚙️ **Active Pipeline**")
    st.success("🟢 5-Feature Random Forest: Active")
    st.info("🌐 LeetCode & Codeforces Sync: Ready")
    st.divider()
    st.markdown("### 🎯 **Target Track Standards**")
    st.markdown("- **SDE Core:** DSA, C++/Java/Python, SQL, OS/DBMS")
    st.markdown("- **AI / ML:** Python, PyTorch/TF, Pandas, NLP/LLMs")
    st.markdown("- **Full Stack / Cloud:** React, Node/FastAPI, Docker, AWS")
st.markdown('<div class="hero-title">Placement Intelligence Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Automated competitive programming sync, skill matrix quantification, ML readiness scoring, and dynamic ATS resume compilation.</div>', unsafe_allow_html=True)

TECH_SKILL_OPTIONS = [
    "DSA", "C++", "Java", "Python", "SQL", "DBMS", "OS / Networks",
    "React", "Node.js", "FastAPI / Flask", "Docker", "Kubernetes", "AWS / Cloud",
    "PyTorch", "TensorFlow", "Pandas / NumPy", "Scikit-Learn", "NLP / LLMs",
    "Git / GitHub", "HTML / CSS", "JavaScript"
]

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

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("📋 Student Profile & Skill Setup")
    with st.form("student_input_form", border=True):
        f_id, f_name = st.columns([1, 2])
        with f_id:
            student_id = st.number_input("Student ID / Roll No", min_value=1, value=101, step=1)
        with f_name:
            name = st.text_input("Full Name", value="Abilash Prabakar")

        f_gpa, f_certs = st.columns(2)
        with f_gpa:
            gpa = st.number_input("Cumulative GPA", min_value=0.0, max_value=10.0, value=9.25, step=0.01, format="%.2f")
        with f_certs:
            certifications = st.number_input("Verified Certifications", min_value=0, max_value=20, value=2, step=1)

        target_role = st.selectbox(
            "Target Career Track",
            list(ROLE_BENCHMARKS.keys())
        )

        selected_skills = st.multiselect(
            "Technical Skills & Domain Stack",
            options=TECH_SKILL_OPTIONS,
            default=["DSA", "C++", "Python", "SQL", "Git / GitHub"]
        )

        f_lc, f_cf = st.columns(2)
        with f_lc:
            leetcode_username = st.text_input("LeetCode Username", value="Abilash_cit_codepod")
        with f_cf:
            codeforces_handle = st.text_input("Codeforces Handle (optional)", value="abicode_pod")

        submit_btn = st.form_submit_button("🚀 Sync Profile & Evaluate Readiness", use_container_width=True)

if submit_btn:
    with col_right:
        st.subheader("📊 Live Evaluation & Skill Matrix")
        with st.spinner("Fetching platform stats and running 5-feature Random Forest evaluation..."):
            sync_student_profile(
                student_id=student_id,
                name=name,
                gpa=gpa,
                certifications=certifications,
                skills_list=selected_skills,
                target_role=target_role,
                leetcode_username=leetcode_username,
                codeforces_handle=codeforces_handle,
                model=st.session_state.model,
                feature_names=st.session_state.features
            )
            student = fetch_latest_student(student_id)

        if student:
            score = float(student["placement_score"])
            live_skill_score = calculate_skill_score(selected_skills)
            benchmark_skills = ROLE_BENCHMARKS[target_role]
            matched_skills = [s for s in selected_skills if s in benchmark_skills]
            role_fit_pct = round((len(matched_skills) / len(benchmark_skills)) * 100, 1)
            m1, m2, m3 = st.columns(3)
            m1.metric("Problems Solved", student["problems_solved"])
            m2.metric("Cumulative GPA", f"{student['gpa']:.2f}")
            m3.metric("CF Contest Rating", student["codeforces_rating"] if student["codeforces_rating"] > 0 else "Unrated")

            k1, k2 = st.columns(2)
            k1.metric("Skill Stack Score", f"{live_skill_score} / 100")
            k2.metric(f"Role Fit ({target_role.split(' ')[0]})", f"{role_fit_pct}%")

            st.write("**Overall Placement Readiness Probability:**")
            st.progress(score / 100.0)

            if score >= 80:
                st.success(f"🎯 **Tier 1 Placement Readiness ({score:.1f}%)**: Profile meets top-tier product company benchmarks.")
            elif score >= 60:
                st.warning(f"⚡ **Tier 2 Placement Readiness ({score:.1f}%)**: Solid baseline. Expand problem solving count beyond 500+.")
            else:
                st.error(f"📈 **Upskill Recommended ({score:.1f}%)**: Focus on increasing high-weight core competencies and problem counts.")

            generate_resume(student)

            pdf_path = f"resume_{student_id}.pdf"
            tex_path = f"resume_{student_id}.tex"

            st.divider()
            st.subheader("📄 Resume Generation")

            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 Download ATS-Friendly PDF Resume",
                        data=f,
                        file_name=pdf_path,
                        mime="application/pdf",
                        use_container_width=True
                    )
            elif os.path.exists(tex_path):
                with open(tex_path, "r") as f:
                    st.download_button(
                        label="📥 Download LaTeX Source (.tex)",
                        data=f.read(),
                        file_name=tex_path,
                        mime="text/plain",
                        use_container_width=True
                    )
else:
    with col_right:
        st.subheader("📊 Live Evaluation & Skill Matrix")
        st.info("👈 Select your technical skill stack, enter platform handles, and click **Sync Profile & Evaluate Readiness** to run inference.")