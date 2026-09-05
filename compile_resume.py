import sqlite3
import subprocess
import requests
import os
from jinja2 import Environment, FileSystemLoader

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
    
    languages = [s for s in raw_skills if s in ["C++", "Java", "Python", "JavaScript", "SQL"]]
    frameworks = [s for s in raw_skills if s in ["React", "Node.js", "FastAPI / Flask", "Docker", "Kubernetes", "AWS / Cloud", "PyTorch", "TensorFlow", "Pandas / NumPy", "Scikit-Learn", "NLP / LLMs"]]
    core_concepts = [s for s in raw_skills if s in ["DSA", "DBMS", "OS / Networks", "Git / GitHub", "HTML / CSS"]]

    return {
        "student_id": row[0],
        "name": row[1],
        "gpa": f"{row[2]:.2f}",
        "problems_solved": row[3],
        "certifications": row[4],
        "codeforces_rating": row[5] if row[5] > 0 else "Unrated",
        "skill_score": f"{row[6]:.1f}",
        "skills": ", ".join(raw_skills) if raw_skills else "N/A",
        "languages": ", ".join(languages) if languages else "None",
        "frameworks": ", ".join(frameworks) if frameworks else "None",
        "core_concepts": ", ".join(core_concepts) if core_concepts else "None",
        "target_role": row[8] if row[8] else "Software Engineer",
        "placement_score": f"{row[9]:.1f}",
        "leetcode_username": row[10] if row[10] else "N/A",
        "codeforces_handle": row[11] if row[11] else "N/A"
    }

def compile_latex_cloud(tex_filename, output_pdf_path):
    print("🌐 Compiling via Cloud LaTeX Engine...")
    url = "https://latexonline.cc/compile"
    
    try:
        with open(tex_filename, "rb") as f:
            response = requests.post(url, files={"file": f}, timeout=25)
            
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

def generate_resume(student_data):
    env = Environment(
        loader=FileSystemLoader("."),
        block_start_string='(\\',
        block_end_string='\\)',
        variable_start_string='((',
        variable_end_string='))'
    )
    
    template = env.get_template("resume_template.tex")
    rendered_tex = template.render(student_data)
    
    tex_filename = f"resume_{student_data['student_id']}.tex"
    pdf_filename = f"resume_{student_data['student_id']}.pdf"
    
    with open(tex_filename, "w", encoding="utf-8") as f:
        f.write(rendered_tex)
        
    print(f"✅ Generated LaTeX file: {tex_filename}")

    try:
        subprocess.run(["pdflatex", "-interaction=nonstopmode", tex_filename], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"📄 Successfully created PDF locally: {pdf_filename}")
        return
    except (subprocess.SubprocessError, FileNotFoundError):
        print("⚠️ Local 'pdflatex' not found. Falling back to Cloud LaTeX compiler...")

    success = compile_latex_cloud(tex_filename, pdf_filename)
    if not success:
        print("⚠️ Could not generate PDF. The raw .tex file is still available.")

if __name__ == "__main__":
    print("=== PIE Resume Auto-Compiler ===")
    user_id_input = input("Enter Student ID to compile resume: ").strip()
    if user_id_input.isdigit():
        student = fetch_latest_student(int(user_id_input))
        if student:
            generate_resume(student)
    else:
        print("❌ Please enter a valid numerical Student ID.")