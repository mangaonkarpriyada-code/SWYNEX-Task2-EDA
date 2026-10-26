from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "cleaned_student_data.csv"
CHART_DIR = BASE_DIR / "charts"
REPORT_DIR = BASE_DIR / "reports"
CHART_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

df = pd.read_csv(INPUT_FILE)
numeric_cols = ["age", "marks", "attendance_percentage"]

print("\n--- Dataset overview ---")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print("\nData types:")
print(df.dtypes)
print("\nMissing values:")
print(df.isna().sum())
print("\nDescriptive statistics:")
print(df[numeric_cols].describe().round(2))

# Save descriptive statistics
df[numeric_cols].describe().round(2).to_csv(REPORT_DIR / "descriptive_statistics.csv")

# Data quality checks
duplicate_names = df["name"].duplicated().sum()
invalid_marks = (~df["marks"].between(0, 100)).sum()
invalid_attendance = (~df["attendance_percentage"].between(0, 100)).sum()
quality_report = pd.DataFrame({
    "check": ["Rows", "Duplicate names after first occurrence",
              "Marks outside 0-100", "Attendance outside 0-100",
              "Total missing cells"],
    "result": [len(df), int(duplicate_names), int(invalid_marks),
               int(invalid_attendance), int(df.isna().sum().sum())]
})
quality_report.to_csv(REPORT_DIR / "data_quality_checks.csv", index=False)
print("\nData quality checks:")
print(quality_report.to_string(index=False))

# Treat marks outside 0-100 as invalid for valid-score summaries.
valid_marks = df.loc[df["marks"].between(0, 100), "marks"]
print("\nValid marks summary (excluding values outside 0-100):")
print(valid_marks.describe().round(2))

# Chart 1: marks distribution; invalid values are excluded and reported separately.
plt.figure()
plt.hist(valid_marks, bins=6, edgecolor="black")
plt.title("Distribution of Valid Student Marks")
plt.xlabel("Marks (0-100)")
plt.ylabel("Number of students")
plt.tight_layout()
plt.savefig(CHART_DIR / "marks_distribution.png", dpi=160)
plt.close()

# Chart 2: attendance distribution
plt.figure()
plt.hist(df["attendance_percentage"].dropna(), bins=6, edgecolor="black")
plt.title("Distribution of Attendance Percentage")
plt.xlabel("Attendance (%)")
plt.ylabel("Number of students")
plt.tight_layout()
plt.savefig(CHART_DIR / "attendance_distribution.png", dpi=160)
plt.close()

# Chart 3: marks vs attendance, excluding invalid marks
valid_rows = df[df["marks"].between(0, 100)]
plt.figure()
plt.scatter(valid_rows["attendance_percentage"], valid_rows["marks"])
plt.title("Marks vs Attendance (Valid Marks Only)")
plt.xlabel("Attendance (%)")
plt.ylabel("Marks")
plt.tight_layout()
plt.savefig(CHART_DIR / "marks_vs_attendance.png", dpi=160)
plt.close()

# Chart 4: average valid marks by age
age_marks = valid_rows.groupby("age", as_index=False)["marks"].mean()
plt.figure()
plt.bar(age_marks["age"].astype(str), age_marks["marks"])
plt.title("Average Valid Marks by Age")
plt.xlabel("Age")
plt.ylabel("Average marks")
plt.tight_layout()
plt.savefig(CHART_DIR / "average_marks_by_age.png", dpi=160)
plt.close()

# Chart 5: correlation heatmap using valid marks only
corr = valid_rows[["age", "marks", "attendance_percentage"]].corr()
plt.figure()
plt.imshow(corr, aspect="auto")
plt.xticks(range(len(corr.columns)), corr.columns, rotation=25, ha="right")
plt.yticks(range(len(corr.index)), corr.index)
plt.colorbar(label="Correlation")
plt.title("Correlation Between Age, Marks and Attendance")
plt.tight_layout()
plt.savefig(CHART_DIR / "correlation_heatmap.png", dpi=160)
plt.close()

# Save correlation matrix
corr.round(3).to_csv(REPORT_DIR / "correlation_matrix.csv")

print("\nCharts saved in the charts folder.")
print("Reports saved in the reports folder.")
print("\nImportant note: a repeated name is not automatically a duplicate student because the student IDs differ.")
print("The negative marks value is invalid for a 0-100 scale; verify it against the original source.")
