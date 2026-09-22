import sys
import sqlite3
import subprocess
import requests
import os
from jinja2 import Environment, FileSystemLoader

# Force UTF-8 stdout so emoji in print() don't raise UnicodeEncodeError on Windows (cp1252)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ReportLab imports for 100% reliable local PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import inch

def fetch_latest_student(student_id):
    conn = sqlite3.connect("upskill_ledger.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT student_id, name, gpa, problems_solved, certifications, 
               codeforces_rating, skill_score, skills, target_role, placement_score, 
               leetcode_username, codeforces_handle 
        FROM student_profiles 
        WHERE student_id = ?
    """, (student_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"❌ Student ID {student_id} not found in database.")
        return None 

    raw_skills = [s.strip() for s in row[7].split(",") if s.strip()] if row[7] else []
    
    languages = [s for s in raw_skills if s in ["C++", "Java", "Python", "JavaScript", "TypeScript", "C", "Go (Golang)", "Rust", "Kotlin", "Swift", "Dart", "R", "SQL"]]
    frameworks = [s for s in raw_skills if s in ["React", "Next.js", "Node.js", "FastAPI", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "PyTorch", "TensorFlow", "Pandas / NumPy", "Scikit-Learn", "LangChain", "LlamaIndex", "LangGraph", "CrewAI", "AutoGen", "RAG Pipelines", "Vector DBs", "Prompt Engineering", "Hugging Face", "OpenCV", "YOLO", "TensorRT", "MLflow", "Terraform", "CI/CD (GitHub Actions)", "Apache Kafka", "Apache Spark (PySpark)", "PostgreSQL", "Redis", "MongoDB", "Snowflake", "dbt", "Flutter", "React Native", "SwiftUI", "Jetpack Compose", "Tailwind CSS"]]
    core_concepts = [s for s in raw_skills if s in ["DSA", "DBMS", "OS / Networks", "Git / GitHub", "HTML / CSS", "System Design", "Linux / Bash", "Prometheus", "Grafana", "OWASP Top 10", "Burp Suite", "Wireshark"]]

    return {
        "student_id": row[0],
        "name": row[1] if row[1] else f"Student #{row[0]}",
        "gpa": f"{row[2]:.2f}",
        "problems_solved": row[3],
        "certifications": row[4],
        "codeforces_rating": row[5] if (row[5] or 0) > 0 else "Unrated",
        "skill_score": f"{row[6]:.1f}",
        "skills": ", ".join(raw_skills) if raw_skills else "N/A",
        "languages": ", ".join(languages) if languages else "None Specified",
        "frameworks": ", ".join(frameworks) if frameworks else "None Specified",
        "core_concepts": ", ".join(core_concepts) if core_concepts else "None Specified",
        "target_role": row[8] if row[8] else "Software Engineer",
        "placement_score": f"{row[9]:.1f}",
        "leetcode_username": row[10] if row[10] else "N/A",
        "codeforces_handle": row[11] if row[11] else "N/A"
    }

def compile_pdf_reportlab(student_data, output_pdf_path):
    """
    Generates a crisp, professional ATS-friendly PDF resume using ReportLab.
    Runs 100% locally in Python without external LaTeX dependencies.
    """
    print(f"📄 Building ATS PDF Resume locally via ReportLab for {student_data['name']}...")
    
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom typography & colors
    primary_color = colors.HexColor("#0F172A")    # Dark slate
    accent_color = colors.HexColor("#2563EB")     # Royal blue
    text_dark = colors.HexColor("#334155")        # Body charcoal
    bg_light = colors.HexColor("#F8FAFC")         # Light blue-gray

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=accent_color
    )

    contact_style = ParagraphStyle(
        'ContactText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_dark
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=4
    )

    body_bold = ParagraphStyle(
        'BodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=text_dark
    )

    body_text = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=text_dark
    )

    story = []

    # --- Header Section ---
    name_str = student_data['name'].upper()
    role_str = student_data['target_role'].upper()
    
    story.append(Paragraph(f"{name_str}", title_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph(f"Target Career Track: <b>{role_str}</b>", subtitle_style))
    story.append(Spacer(1, 4))
    
    contact_info = f"<b>Student ID:</b> {student_data['student_id']} &nbsp;|&nbsp; <b>LeetCode:</b> {student_data['leetcode_username']} &nbsp;|&nbsp; <b>Codeforces:</b> {student_data['codeforces_handle']} &nbsp;|&nbsp; <b>GPA:</b> {student_data['gpa']}/10.0"
    story.append(Paragraph(contact_info, contact_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceBefore=0, spaceAfter=8))

    # --- Metrics & Score Summary Table ---
    story.append(Paragraph("PLACEMENT READINESS & BENCHMARK SUMMARY", section_heading))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=0, spaceAfter=6))
    
    score_val = float(student_data['placement_score'])
    tier_label = "Tier 1 (Product Benchmark)" if score_val >= 80 else ("Tier 2 (High Potential)" if score_val >= 60 else "Upskill Action Required")
    
    metrics_data = [
        [
            Paragraph("<b>Overall Placement Score:</b>", body_text),
            Paragraph(f"<b><font color='#2563EB'>{student_data['placement_score']}%</font></b> ({tier_label})", body_text),
            Paragraph("<b>Skill Stack Index:</b>", body_text),
            Paragraph(f"{student_data['skill_score']} / 100.0", body_text)
        ],
        [
            Paragraph("<b>Problems Solved:</b>", body_text),
            Paragraph(f"{student_data['problems_solved']} Problems", body_text),
            Paragraph("<b>Codeforces Rating:</b>", body_text),
            Paragraph(f"{student_data['codeforces_rating']}", body_text)
        ],
        [
            Paragraph("<b>Cumulative GPA:</b>", body_text),
            Paragraph(f"{student_data['gpa']} / 10.0", body_text),
            Paragraph("<b>Certifications:</b>", body_text),
            Paragraph(f"{student_data['certifications']} Verified", body_text)
        ]
    ]

    metrics_table = Table(metrics_data, colWidths=[1.8*inch, 2.0*inch, 1.5*inch, 1.9*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_light),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#F1F5F9")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 10))

    # --- Technical Skills Matrix ---
    story.append(Paragraph("TECHNICAL COMPETENCIES & STACK MATRIX", section_heading))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=0, spaceAfter=6))

    skills_table_data = [
        [Paragraph("<b>Languages:</b>", body_bold), Paragraph(student_data['languages'], body_text)],
        [Paragraph("<b>Frameworks & Tools:</b>", body_bold), Paragraph(student_data['frameworks'], body_text)],
        [Paragraph("<b>Core CS & Infra:</b>", body_bold), Paragraph(student_data['core_concepts'], body_text)],
    ]

    skills_table = Table(skills_table_data, colWidths=[1.8*inch, 5.4*inch])
    skills_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 10))

    # --- Automated Evaluation & Career Action Plan ---
    story.append(Paragraph("AUTOMATED EVALUATION & STRATEGIC RECOMMENDATIONS", section_heading))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=0, spaceAfter=6))

    rec_1 = f"<b>Profile Alignment:</b> Candidate evaluated for <b>{student_data['target_role']}</b> with a calculated Placement Readiness Probability of <b>{student_data['placement_score']}%</b>."
    
    if score_val >= 80:
        rec_2 = "<b>Recommendation:</b> Profile demonstrates excellent readiness for Tier 1 Product and Core engineering roles. Maintain active contest participation and system architecture practice."
    elif score_val >= 60:
        rec_2 = "<b>Recommendation:</b> Strong baseline foundation. Expand problem-solving count on competitive platforms to 400+ and add verified projects in target framework stack."
    else:
        rec_2 = "<b>Recommendation:</b> Focused upskilling required. Target core CS fundamentals (DSA, System Design, SQL) and increase coding practice hours."

    rec_3 = f"<b>Platform Sync Verification:</b> LeetCode handle <code>{student_data['leetcode_username']}</code> ({student_data['problems_solved']} problems solved) and Codeforces handle <code>{student_data['codeforces_handle']}</code>."

    story.append(Paragraph(f"• {rec_1}", body_text))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"• {rec_2}", body_text))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"• {rec_3}", body_text))

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=0, spaceAfter=6))
    story.append(Paragraph("<i>Generated automatically by Placement Intelligence Engine (PIE v2.2) • ATS Compliant Document</i>", ParagraphStyle('Footer', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, textColor=colors.HexColor("#94A3B8"))))

    doc.build(story)
    print(f"✅ Successfully created ATS PDF resume locally: {output_pdf_path}")
    return True

def compile_latex_cloud(tex_filename, output_pdf_path):
    print("🌐 Compiling via Cloud LaTeX Engine...")
    url = "https://latexonline.cc/compile"
    
    try:
        with open(tex_filename, "rb") as f:
            response = requests.post(url, files={"file": f}, timeout=15)
            
        if response.status_code == 200:
            with open(output_pdf_path, "wb") as pdf_out:
                pdf_out.write(response.content)
            print(f"📄 Successfully created PDF via Cloud: {output_pdf_path}")
            return True
        else:
            print(f"⚠️ Cloud compilation failed with status code {response.status_code}.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Cloud connection error: {e}")
        return False

def generate_resume(student_data, allow_cloud_compile=True):
    os.makedirs("resumes", exist_ok=True)

    # 1. Render LaTeX template (.tex)
    env = Environment(
        loader=FileSystemLoader("."),
        block_start_string='(\\',
        block_end_string='\\)',
        variable_start_string='((',
        variable_end_string='))'
    )

    template = env.get_template("resume_template.tex")
    rendered_tex = template.render(student_data)

    tex_filename = os.path.join("resumes", f"resume_{student_data['student_id']}.tex")
    pdf_filename = os.path.join("resumes", f"resume_{student_data['student_id']}.pdf")

    with open(tex_filename, "w", encoding="utf-8") as f:
        f.write(rendered_tex)

    print(f"[PIE] Generated LaTeX source file: {tex_filename}")

    # 2. Try Local ReportLab PDF generation first (Guaranteed 100% success locally without pdflatex)
    try:
        compile_pdf_reportlab(student_data, pdf_filename)
        return pdf_filename
    except Exception as e:
        print(f"⚠️ ReportLab compilation error: {e}")

    # 3. Fallback to pdflatex if available
    try:
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory=resumes", tex_filename],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print(f"[PIE] Successfully created PDF locally via pdflatex: {pdf_filename}")
        return pdf_filename
    except (subprocess.SubprocessError, FileNotFoundError):
        print("[PIE] Local 'pdflatex' not found.")

    # 4. Fallback to cloud compile if allowed
    if allow_cloud_compile:
        success = compile_latex_cloud(tex_filename, pdf_filename)
        if success:
            return pdf_filename

    print("[PIE] Could not compile PDF via pdflatex or cloud. The raw .tex file is available.")
    return None

if __name__ == "__main__":
    print("=== PIE Resume Auto-Compiler ===")
    user_id_input = input("Enter Student ID to compile resume: ").strip()
    if user_id_input.isdigit():
        student = fetch_latest_student(int(user_id_input))
        if student:
            generate_resume(student)
    else:
        print("❌ Please enter a valid numerical Student ID.")