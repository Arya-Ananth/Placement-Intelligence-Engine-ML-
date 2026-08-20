import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from fetch_leetcode import get_leetcode_stats
def init_db():
    conn = sqlite3.connect("upskill_ledger.db")
    cursor = conn.cursor()
    cursor.execute(''' 
                   CREATE TABLE IF NOT EXISTS student_profiles(
                   student_id INTEGER PRIMARY KEY,
                   name TEXT,
                   gpa REAL,
                   problems_solved INTEGER,
                   certifications INTEGER,
                   placement_score REAL)
                   ''')
    conn.commit()
    conn.close()

def train_model():
    df = pd.read_csv("data.csv")
    gpa_col = 'GPA' if 'GPA' in df.columns else 'gpa'
    probs_col = 'Problems_Solved' if 'Problems_Solved' in df.columns else 'problems_solved'
    certs_col = 'Certifications' if 'Certifications' in df.columns else 'certifications'
    placed_col = 'Placed' if 'Placed' in df.columns else 'placed'

    x=df[[gpa_col,probs_col,certs_col]]
    y= df[placed_col]
    model = RandomForestClassifier(random_state=42)
    model.fit(x,y)
    return model ,[gpa_col,probs_col,certs_col]

def update_student_record(student_id , name , gpa , problems_solved , certifications , model , feature_names):
    input_df = pd.DataFrame([[gpa,problems_solved,certifications]],columns=feature_names)
    score = model.predict_proba(input_df)[0][1]*100

    conn = sqlite3.connect("upskill_ledger.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO student_profiles (student_id, name, gpa, problems_solved, certifications, placement_score)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(student_id) DO UPDATE SET
            gpa=excluded.gpa,
            problems_solved=excluded.problems_solved,
            certifications=excluded.certifications,
            placement_score=excluded.placement_score
    ''', (student_id, name, gpa, problems_solved, certifications, score))
    conn.commit()
    conn.close()
    print(f"✅ Record saved in Upskill Ledger for {name} (ID: {student_id})")
    print(f"📊 Placement Probability Score: {score:.2f}%\n")

def sync_student_profile(student_id, name, gpa, certifications, leetcode_username, model, feature_names):
    print(f"\n--- 🔄 Fetching live LeetCode data for {name} ({leetcode_username}) ---")
    stats = get_leetcode_stats(leetcode_username)
    if stats:
        live_problems = stats["total"]
    else:
        print("Leetcode fetch failed")
        live_problems = 0
    update_student_record(student_id, name, gpa, live_problems, certifications, model, feature_names)

if __name__ == "__main__":
    init_db()
    ml_model , features = train_model()
    print("--- PIE Core Engine: Upskill Ledger & ML Integration ---")

    sync_student_profile(
        student_id=101,
        name="Hrishikesh Yerrabhaneni",
        gpa=8.2,
        certifications=1,
        leetcode_username="hrishikesh-yn",
        model=ml_model,
        feature_names=features
    )