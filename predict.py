import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv("data.csv")
X = df[["GPA", "Problems_Solved", "Certifications"]]
Y = df["Placed"]

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

model = RandomForestClassifier()
model.fit(X_train, Y_train)
sample_student = pd.DataFrame([[8.2, 185, 1]], columns=["GPA", "Problems_Solved", "Certifications"])
probability = model.predict_proba(sample_student)[0][1] * 100

print(f"--- PIE Core Engine Output ---")
print(f"Placement Probability Score: {probability:.2f}%")