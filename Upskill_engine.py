import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from fetch_leetcode import get_leetcode_stats
from fetch_stats import get_codeforces_stats

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
                   placement_score REAL,
                   leetcode_username TEXT,
                   codeforces_handle TEXT)
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

def update_student_record(student_id, name, gpa, problems_solved, certifications, model, feature_names, leetcode_username="N/A", codeforces_handle="N/A"):
    input_df = pd.DataFrame([[gpa, problems_solved, certifications]], columns=feature_names)
    score = model.predict_proba(input_df)[0][1] * 100

    conn = sqlite3.connect("upskill_ledger.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO student_profiles (
            student_id, name, gpa, problems_solved, certifications, placement_score, leetcode_username, codeforces_handle
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(student_id) DO UPDATE SET
            name = excluded.name,
            gpa = excluded.gpa,
            problems_solved = excluded.problems_solved,
            certifications = excluded.certifications,
            placement_score = excluded.placement_score,
            leetcode_username = excluded.leetcode_username,
            codeforces_handle = excluded.codeforces_handle
    ''', (student_id, name, gpa, problems_solved, certifications, score, leetcode_username, codeforces_handle))
    conn.commit()
    conn.close()
    print(f"✅ Record saved in Upskill Ledger for {name} (ID: {student_id})")
    print(f"📊 Placement Probability Score: {score:.2f}%\n")

def sync_student_profile(student_id, name, gpa, certifications, leetcode_username, codeforces_handle, model, feature_names):
    print(f"\n--- 🔄 Fetching live platform data for {name} ---")
    
    # Fetch LeetCode stats
    lc_stats = get_leetcode_stats(leetcode_username) if leetcode_username else None
    live_problems = lc_stats["total"] if lc_stats else 0
    
    # Fetch Codeforces stats
    cf_stats = get_codeforces_stats(codeforces_handle) if codeforces_handle else None
    cf_rating = cf_stats["rating"] if cf_stats else "Unrated"

    print(f"📈 Sync Summary -> Problems Solved: {live_problems} | Codeforces Rating: {cf_rating}")

    update_student_record(
        student_id=student_id,
        name=name,
        gpa=gpa,
        problems_solved=live_problems,
        certifications=certifications,
        model=model,
        feature_names=feature_names,
        leetcode_username=leetcode_username,
        codeforces_handle=codeforces_handle
    )

if __name__ == "__main__":
    init_db()
    ml_model , features = train_model()
    print("--- PIE Core Engine: Upskill Ledger & ML Integration ---")
    try:
        user_student_id = int(input("Enter Student ID: ").strip())
        user_name = input("Enter Full Name: ").strip()
        user_gpa = float(input("Enter College GPA (e.g. 8.5): ").strip())
        user_certs = int(input("Enter Verified Certifications Count: ").strip())
        user_leetcode = input("Enter LeetCode Handle: ").strip()
        user_codeforces = input("Enter Codeforces Handle (optional, press Enter to skip): ").strip()

        sync_student_profile(
            student_id=user_student_id,
            name=user_name,
            gpa=user_gpa,
            certifications=user_certs,
            leetcode_username=user_leetcode,
            codeforces_handle=user_codeforces,
            model=ml_model,
            feature_names=features
        )
    except ValueError:
        print("Invalid input format. Please ensure ID, GPA, and Certifications are numbers.")