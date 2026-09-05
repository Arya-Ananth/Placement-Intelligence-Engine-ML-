import numpy as np
import pandas as pd

np.random.seed(42)
n_samples = 1000

# 1. Academic CGPA (5.5 to 9.9)
gpa = np.clip(np.random.normal(loc=7.75, scale=0.85, size=n_samples), 5.5, 9.9).round(2)

# 2. Total competitive coding problems solved across platforms
probs_raw = np.random.gamma(shape=3.0, scale=120, size=n_samples)
problems_solved = np.clip((probs_raw + (gpa - 6.0) * 45).astype(int), 0, 1300)

# 3. Verified Certifications (0 to 5)
certifications = np.clip(np.random.poisson(lam=1.4, size=n_samples), 0, 5)

# 4. Codeforces Rating (0 for unrated/beginners, up to 2100+)
# Roughly 40% unrated (0), rest distributed around 1100-1600
is_rated = np.random.rand(n_samples) > 0.40
cf_raw = np.random.normal(loc=1250, scale=220, size=n_samples)
cf_rating = np.where(is_rated, np.clip(cf_raw, 800, 2200).astype(int), 0)

# 5. Skill Score (0 to 100 based on stack breadth & depth)
skill_raw = np.random.normal(loc=55, scale=20, size=n_samples) + (problems_solved / 25)
skill_score = np.clip(skill_raw, 10.0, 100.0).round(2)

# 6. Placement Shortlisting Logic
# Weightings calibrated for 8.0+ CGPA and 500+ problems benchmarks
gpa_factor = 2.5 * (gpa - 8.0)
probs_factor = 0.008 * (problems_solved - 500)
cert_factor = 0.35 * (certifications - 1)
cf_factor = np.where(cf_rating > 0, 0.002 * (cf_rating - 1200), -0.2)
skill_factor = 0.03 * (skill_score - 50)

z = gpa_factor + probs_factor + cert_factor + cf_factor + skill_factor - 0.2

# Strict corporate eligibility gates
hard_filter = (gpa < 7.0) | (problems_solved < 150)
z = np.where(hard_filter, z - 3.5, z)

probs = 1 / (1 + np.exp(-z))
placed = (np.random.rand(n_samples) < probs).astype(int)

df = pd.DataFrame({
    "GPA": gpa,
    "Problems_Solved": problems_solved,
    "Certifications": certifications,
    "CF_Rating": cf_rating,
    "Skill_Score": skill_score,
    "Placed": placed
})

df.to_csv("data.csv", index=False)
print("✅ Generated data.csv with 5 features and 1,000 calibrated records.")