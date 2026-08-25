import streamlit as st
import os
from Upskill_engine import init_db, train_model, sync_student_profile
from compile_resume import fetch_latest_student, generate_resume

st.set_page_config(page_title="PIE - PLACEMENT INTELLIGENCE ENGINE", layout="wide")

if "model_ready" not in st.session_state:
    init_db()
    st.session_state.model, st.session_state.features = train_model()
    st.session_state.model_ready = True

st.title("🎯 Placement Intelligence Engine (PIE)")
st.markdown("Real-time profile sync across LeetCode & Codeforces, ML placement score prediction, and auto-compiled ATS resumes.")

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("Student Profile Input")
    with st.form("student_input_form"):
        student_id = st.number_input("Student ID / Roll No", min_value=1, value=101, step=1)
        name = st.text_input("Full Name", value="Hrishikesh Yerrabhaneni")
        gpa = st.slider("Cumulative GPA", min_value=0.0, max_value=10.0, value=8.2, step=0.01)
        certifications = st.number_input("Verified Certifications Count", min_value=0, max_value=20, value=1, step=1)
        leetcode_username = st.text_input("LeetCode Username", value="hrishikesh-yn")
        codeforces_handle = st.text_input("Codeforces Handle (optional)", value="tourist")
        submit_btn = st.form_submit_button("Sync Profile & Evaluate")

if submit_btn:
    with col_right:
        st.subheader("📊 Live Evaluation & Ledger")
        with st.spinner("Fetching platform stats and running Random Forest evaluation..."):
            sync_student_profile(
                student_id=student_id,
                name=name,
                gpa=gpa,
                certifications=certifications,
                leetcode_username=leetcode_username,
                codeforces_handle=codeforces_handle,
                model=st.session_state.model,
                feature_names=st.session_state.features
            )
            student = fetch_latest_student(student_id)

        if student:
            score = float(student["placement_score"])
            m1, m2, m3 = st.columns(3)
            m1.metric("Problems Solved", student["problems_solved"])
            m2.metric("GPA", student["gpa"])
            m3.metric("Placement Readiness", f"{score:.2f}%")
            st.progress(score / 100.0)
            generate_resume(student)

            pdf_path = f"resume_{student_id}.pdf"
            tex_path = f"resume_{student_id}.tex"

            st.write("---")
            st.subheader("📄 Resume Export")

            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 Download ATS-Friendly PDF Resume",
                        data=f,
                        file_name=pdf_path,
                        mime="application/pdf"
                    )
            elif os.path.exists(tex_path):
                with open(tex_path, "r") as f:
                    st.download_button(
                        label="📥 Download LaTeX Source (.tex)",
                        data=f.read(),
                        file_name=tex_path,
                        mime="text/plain"
                    )