import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from fetch_leetcode import get_leetcode_stats
from fetch_stats import get_codeforces_stats

SKILL_WEIGHTS = {
    
    "DSA": 20, "C++": 15, "Java (Spring Boot)": 15, "Python": 15, "Go (Golang)": 15, "Rust": 16,
    "TypeScript": 14, "JavaScript": 12, "SQL": 15, "C": 14, "Kotlin": 14, "Swift": 14, "Dart": 12, "R": 10,
    "LangChain": 16, "LlamaIndex": 15, "LangGraph": 16, "CrewAI": 15, "AutoGen": 14, "RAG Pipelines": 18,
    "Vector DBs": 15, "Prompt Engineering": 12, "Hugging Face": 14, "PyTorch": 16, "TensorFlow": 14,
    "Scikit-Learn": 12, "Pandas / NumPy": 10, "OpenCV": 14, "YOLO": 13, "TensorRT": 15, "MLflow": 14,
    "FastAPI": 13, "Node.js": 12, "React": 12, "Next.js": 14, "Docker": 15, "Kubernetes": 16,
    "AWS": 15, "Azure": 14, "GCP": 14, "Terraform": 15, "CI/CD (GitHub Actions)": 14, "Apache Kafka": 16,
    "Apache Spark (PySpark)": 15, "PostgreSQL": 14, "Redis": 14, "MongoDB": 12, "Snowflake": 14, "dbt": 14,
    "Linux / Bash": 12, "Prometheus": 13, "Grafana": 13, "OWASP Top 10": 15, "Burp Suite": 14,
    "Wireshark": 12, "Flutter": 14, "React Native": 13, "SwiftUI": 14, "Jetpack Compose": 14,
    "Tailwind CSS": 8, "Git / GitHub": 10, "System Design": 18
}

def calculate_skill_score(skills_list):
    if not skills_list:
        return 0.0
    raw_score = sum(SKILL_WEIGHTS.get(skill, 8) for skill in skills_list)
    return round(min(100.0, raw_score), 2)

def init_db():
    conn = sqlite3.connect("upskill_ledger.db")
    cursor = conn.cursor()
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS student_profiles (
            student_id INTEGER PRIMARY KEY,
            name TEXT,
            gpa REAL,
            problems_solved INTEGER,
            certifications INTEGER,
            codeforces_rating INTEGER,
            skill_score REAL,
            skills TEXT,
            target_role TEXT,
            placement_score REAL,
            leetcode_username TEXT,
            codeforces_handle TEXT
        )
    ''')
    conn.commit()
    conn.close()

def train_model():
    df = pd.read_csv("data.csv")
    feature_cols = ["GPA", "Problems_Solved", "Certifications", "CF_Rating", "Skill_Score"]
    
    # Fallback to standard columns if dataset hasn't been re-generated yet
    available_cols = [c for c in feature_cols if c in df.columns]
    if len(available_cols) < 5:
        available_cols = [c for c in ["GPA", "Problems_Solved", "Certifications"] if c in df.columns]
    
    x = df[available_cols]
    y = df["Placed"]
    model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    model.fit(x, y)
    return model, available_cols

def update_student_record(student_id, name, gpa, problems_solved, certifications, cf_rating, skills_list, target_role, model, feature_names, leetcode_username="N/A", codeforces_handle="N/A"):
    skill_score = calculate_skill_score(skills_list)
    skills_str = ", ".join(skills_list) if skills_list else "None"
    
    # Build feature row matching trained columns
    input_data = {}
    if "GPA" in feature_names: input_data["GPA"] = gpa
    if "Problems_Solved" in feature_names: input_data["Problems_Solved"] = problems_solved
    if "Certifications" in feature_names: input_data["Certifications"] = certifications
    if "CF_Rating" in feature_names: input_data["CF_Rating"] = cf_rating
    if "Skill_Score" in feature_names: input_data["Skill_Score"] = skill_score

    input_df = pd.DataFrame([input_data], columns=feature_names)
    score = model.predict_proba(input_df)[0][1] * 100

    conn = sqlite3.connect("upskill_ledger.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO student_profiles (
            student_id, name, gpa, problems_solved, certifications,
            codeforces_rating, skill_score, skills, target_role,
            placement_score, leetcode_username, codeforces_handle
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(student_id) DO UPDATE SET
            name = excluded.name,
            gpa = excluded.gpa,
            problems_solved = excluded.problems_solved,
            certifications = excluded.certifications,
            codeforces_rating = excluded.codeforces_rating,
            skill_score = excluded.skill_score,
            skills = excluded.skills,
            target_role = excluded.target_role,
            placement_score = excluded.placement_score,
            leetcode_username = excluded.leetcode_username,
            codeforces_handle = excluded.codeforces_handle
    ''', (student_id, name, gpa, problems_solved, certifications, cf_rating, skill_score, skills_str, target_role, score, leetcode_username, codeforces_handle))
    
    conn.commit()
    conn.close()
    print(f"✅ Record saved in Upskill Ledger for {name} (ID: {student_id})")
    print(f"📊 Placement Probability Score: {score:.2f}%\n")

def sync_student_profile(student_id, name, gpa, certifications, skills_list, target_role, leetcode_username, codeforces_handle, model, feature_names):
    print(f"\n--- 🔄 Fetching live platform data for {name} ---")
    
    # 1. Fetch LeetCode stats
    lc_stats = get_leetcode_stats(leetcode_username) if leetcode_username else None
    live_problems = lc_stats["total"] if lc_stats else 0
    
    # 2. Fetch Codeforces stats
    cf_stats = get_codeforces_stats(codeforces_handle) if codeforces_handle else None
    cf_rating = cf_stats["rating"] if (cf_stats and isinstance(cf_stats.get("rating"), int)) else 0

    print(f"📈 Sync Summary -> Problems Solved: {live_problems} | Codeforces Rating: {cf_rating} | Skills Tagged: {len(skills_list)}")

    update_student_record(
        student_id=student_id,
        name=name,
        gpa=gpa,
        problems_solved=live_problems,
        certifications=certifications,
        cf_rating=cf_rating,
        skills_list=skills_list,
        target_role=target_role,
        model=model,
        feature_names=feature_names,
        leetcode_username=leetcode_username,
        codeforces_handle=codeforces_handle
    )

if __name__ == "__main__":
    init_db()
    ml_model, features = train_model()
    print("--- PIE Core Engine: Upskill Ledger & ML Integration ---")
    try:
        user_student_id = int(input("Enter Student ID: ").strip())
        user_name = input("Enter Full Name: ").strip()
        user_gpa = float(input("Enter College GPA (e.g. 8.5): ").strip())
        user_certs = int(input("Enter Verified Certifications Count: ").strip())
        user_role = input("Enter Target Role (e.g. SDE, Data Scientist): ").strip()
        user_skills_input = input("Enter Skills comma-separated (e.g. C++, DSA, Python, Docker): ").strip()
        user_skills = [s.strip() for s in user_skills_input.split(",") if s.strip()]
        user_leetcode = input("Enter LeetCode Handle: ").strip()
        user_codeforces = input("Enter Codeforces Handle (optional, press Enter to skip): ").strip()

        sync_student_profile(
            student_id=user_student_id,
            name=user_name,
            gpa=user_gpa,
            certifications=user_certs,
            skills_list=user_skills,
            target_role=user_role,
            leetcode_username=user_leetcode,
            codeforces_handle=user_codeforces,
            model=ml_model,
            feature_names=features
        )
    except ValueError:
        print("Invalid input format. Please ensure numerical fields are formatted properly.")