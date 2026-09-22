# Placement Intelligence Engine (PIE)

> **Automated placement readiness scoring, live competitive programming sync, skill matrix quantification, and ATS-grade resume compilation — powered by a calibrated synthetic dataset and a tuned Random Forest classifier.**

---

## What is PIE?

PIE is an end-to-end ML pipeline that helps engineering students benchmark their placement readiness against role-specific industry standards. It combines live LeetCode/Codeforces data, a weighted skill scoring system, and a 5-feature Random Forest model to produce a probabilistic placement readiness score. A Streamlit UI ties everything together, and LaTeX-rendered ATS-friendly resumes are compiled automatically.

---

## Pipeline Overview

`
generate_dataset.py          # Synthesise 1,000 calibrated training records -> data.csv
       |
Upskill_engine.py            # Train 5-feature Random Forest; expose sync + score APIs
       |
fetch_leetcode.py            # Live LeetCode GraphQL stats (problems solved, contest rating)
fetch_stats.py               # Live Codeforces REST stats (rating, rank)
       |
app.py  (streamlit run app.py)   # Streamlit UI: form input, live sync, skill matrix display
       |
compile_resume.py            # Jinja2 -> LaTeX -> PDF (local pdflatex or latexonline.cc cloud)
       |
resumes/resume_{id}.pdf      # Generated output (gitignored)
`

---

## Setup

### 1. Clone and create a virtual environment

`ash
git clone https://github.com/Arya-Ananth/Placement-Intelligence-Engine-ML-.git
cd Placement-Intelligence-Engine-ML-
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
`

### 2. Install dependencies

`ash
pip install -r requirements.txt
`

### 3. (Optional) Regenerate the training dataset

The repo ships with a pre-generated data.csv. To regenerate it with a fresh seed:

`ash
python generate_dataset.py
`

### 4. Run the Streamlit app

`ash
streamlit run app.py
`

The model is trained automatically on first launch. Evaluation metrics (accuracy, precision, recall) are printed to the terminal.

---

## How to Use

1. Enter your Student ID, full name, GPA, and certifications count.
2. Select your target career track from the dropdown.
3. Pick the skills in your current stack from the multi-select.
4. Enter your LeetCode username and (optionally) Codeforces handle.
5. Click **Sync Profile & Evaluate Readiness**.

PIE will:
- Fetch your live problem-solving stats from LeetCode and Codeforces.
- Compute your weighted skill score against the role benchmark.
- Run the 5-feature Random Forest to generate a placement probability.
- Persist everything to upskill_ledger.db (SQLite).
- Render and compile a personalised ATS resume into esumes/.

---

## Dataset Generation Logic (generate_dataset.py)

The training data is **synthetically calibrated** to approximate real-world placement shortlisting behaviour, rather than being random or uniform.

### Feature generation

| Feature | Distribution | Rationale |
|---|---|---|
| GPA | Normal(7.75, 0.85), clipped [5.5, 9.9] | Mirrors typical engineering college spread |
| Problems Solved | Gamma(shape=3, scale=120) + GPA boost | Gamma captures right-skewed practice patterns; GPA-correlated bonus reflects motivated students |
| Certifications | Poisson(λ=1.4), clipped [0, 5] | Rare but not absent; Poisson is the natural count distribution |
| CF Rating | 40% unrated (0), rest Normal(1250, 220) clipped [800, 2200] | Mirrors actual Codeforces participation rates |
| Skill Score | Normal(55, 20) + Problems/25, clipped [10, 100] | Stack breadth estimated from coding activity |

### Placement label (Placed) — logistic scoring

A logistic sigmoid maps a linear score z to a placement probability:

`
z = 2.5*(GPA - 8.0)          # high GPA is the single strongest signal
  + 0.008*(Problems - 500)   # 500 problems is the industry benchmark
  + 0.35*(Certs - 1)
  + 0.002*(CF_Rating - 1200) if rated, else -0.2
  + 0.03*(Skill_Score - 50)
  - 0.2                      # intercept calibration

P(Placed) = sigmoid(z)
`

### Hard eligibility gates

Two strict filters apply a -3.5 penalty to z (pushing P(Placed) near 0) for disqualifying profiles:
- **GPA < 7.0** — below most company cutoffs
- **Problems Solved < 150** — insufficient competitive programming exposure

This ensures the dataset reflects real corporate shortlisting gates, not just a smooth probability curve.

---

## Architecture Notes

- **Model**: RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42) trained on 5 features. An 80/20 hold-out evaluation is printed at startup; the production model is re-fitted on the full 1,000 rows.
- **Skill Scoring**: SKILL_WEIGHTS in Upskill_engine.py assigns weights (8–20) to 60+ technologies. Raw sum is capped at 100.
- **Role Fit**: Percentage of the student's selected skills that overlap with a role's required benchmark skill list. Validated at startup to catch typos. Applied as a post-model heuristic penalty multiplier (`adjusted_score = raw_score * (0.5 + 0.5 * (role_fit_pct / 100))`) on the raw ML score, ensuring role alignment meaningfully impacts the placement probability without fabricating ground-truth training features.
- **Resume Compilation**: LaTeX template rendered via Jinja2. Attempts local pdflatex first; falls back to latexonline.cc only with an explicit user warning and an llow_cloud_compile flag.
- **Database**: SQLite (upskill_ledger.db). Student profiles are upserted on every sync.

---

## File Reference

| File | Purpose |
|---|---|
| generate_dataset.py | Synthesise data.csv |
| data.csv | 1,000-row calibrated training set |
| Upskill_engine.py | Model training, DB ops, sync orchestration |
| etch_leetcode.py | LeetCode GraphQL client |
| etch_stats.py | Codeforces REST client |
| pp.py | Streamlit web UI |
| compile_resume.py | LaTeX resume compiler |
| esume_template.tex | Jinja2 LaTeX template |
| upskill_ledger.db | SQLite student profile store |
| esumes/ | Generated resume output (gitignored) |
| equirements.txt | Pinned Python dependencies |

---

## Requirements

- Python 3.10+
- (Optional) pdflatex for local PDF compilation — install via [MiKTeX](https://miktex.org/) on Windows or 	exlive-latex-base on Linux.
