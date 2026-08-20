import sqlite3
import subprocess
from jinja2 import Environment, FileSystemLoader

def fetch_latest_student(student_id):
    conn = sqlite3.connect("upskill_ledger.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT student_id, name, gpa, problems_solved, certifications, placement_score 
        FROM student_profiles 
        WHERE student_id = ?
    """, (student_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"❌ Student ID {student_id} not found in database.")
        return None 

    return {
        "student_id": row[0],
        "name": row[1],
        "gpa": row[2],
        "problems_solved": row[3],
        "certifications": row[4],
        "placement_score": f"{row[5]:.2f}",
        "leetcode_username": "hrishikesh-yn"
    }

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
    with open(tex_filename, "w") as f:
        f.write(rendered_tex)
        
    print(f"✅ Generated LaTeX file: {tex_filename}")

    try:
        subprocess.run(["pdflatex", "-interaction=nonstopmode", tex_filename], check=True)
        print(f"📄 Successfully created PDF: resume_{student_data['student_id']}.pdf")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("⚠️ 'pdflatex' binary not found locally. You can upload the generated .tex file to Overleaf to view the final PDF.")

if __name__ == "__main__":
    student = fetch_latest_student(101)
    if student:
        generate_resume(student)