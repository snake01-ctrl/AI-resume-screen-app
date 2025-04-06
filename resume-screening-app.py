import streamlit as st
import pdfplumber
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher
from io import StringIO
import base64
import pandas as pd

# Define roles and keywords
roles_keywords = {
    "Data Scientist": ["python", "machine learning", "data analysis", "pandas", "numpy", "tensorflow", "keras", "statistics", "modeling", "data visualization"],
    "Web Developer": ["html", "css", "javascript", "react", "node.js", "express", "frontend", "backend", "web development"],
    "Software Engineer": ["java", "c++", "software development", "object-oriented programming", "algorithms", "data structures", "version control"],
    "UI/UX Designer": ["figma", "adobe xd", "wireframes", "prototyping", "user research", "design thinking", "ui", "ux"],
    "Cybersecurity Analyst": ["network security", "penetration testing", "firewalls", "encryption", "vulnerability assessment", "threat analysis"],
    "AI/ML Engineer": ["deep learning", "machine learning", "neural networks", "pytorch", "scikit-learn", "ai", "cv", "nlp"],
    "Business Analyst": ["excel", "data analysis", "sql", "requirement gathering", "stakeholder management", "business intelligence", "dashboards"],
    "Cloud Engineer": ["aws", "azure", "cloud computing", "devops", "containers", "kubernetes", "infrastructure", "terraform"],
    "Mobile App Developer": ["android", "ios", "react native", "flutter", "kotlin", "swift", "mobile development"],
    "Network Engineer": ["routing", "switching", "cisco", "firewalls", "network protocols", "lan", "wan", "vpn"],
    "Fitness Trainer": ["fitness", "exercise", "personal training", "workout", "nutrition", "strength training", "certified trainer"]
}

# Extract text from PDF
def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Preprocess text
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

# Get keyword match score
def get_keyword_match_score(resume_text, keywords):
    matched_keywords = [kw for kw in keywords if kw in resume_text]
    score = len(matched_keywords) / len(keywords)
    return score, matched_keywords

# Skill gap analysis
def skill_gap_analysis(keywords, matched):
    missing = list(set(keywords) - set(matched))
    return missing

# Generate download link
def get_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="resume_match_results.csv">Download Results as CSV</a>'
    return href

# Summarize resume
def summarize_resume(text):
    lines = text.strip().split("\n")
    summary_lines = lines[:5] if len(lines) >= 5 else lines
    return " ".join(summary_lines)

# Main app
st.title("AI Resume Screening System")
st.markdown("This app analyzes your resume against selected job roles and provides feedback.")

job_role = st.selectbox("Select a Job Role", list(roles_keywords.keys()))

uploaded_file = st.file_uploader("Upload your resume (PDF format only)", type=["pdf"])

if uploaded_file:
    resume_text = extract_text_from_pdf(uploaded_file)
    resume_text_clean = preprocess_text(resume_text)
    
    # Keyword Matching
    score, matched_keywords = get_keyword_match_score(resume_text_clean, roles_keywords[job_role])
    
    # Skill Gap
    missing_keywords = skill_gap_analysis(roles_keywords[job_role], matched_keywords)

    # Resume Summary
    summary = summarize_resume(resume_text)

    st.subheader("Selected Job Role")
    st.markdown(f"**{job_role}**")

    st.subheader("Resume Summary")
    st.write(summary)

    st.subheader("Keyword Match Score")
    st.metric(label="Match Percentage", value=f"{score*100:.2f}%")

    st.subheader("Matched Keywords")
    st.write(matched_keywords if matched_keywords else "No relevant keywords matched.")

    st.subheader("Missing Keywords (Skill Gaps)")
    st.write(missing_keywords if missing_keywords else "No skill gaps detected!")

    st.subheader("Suggestions for Improvement")
    if missing_keywords:
        for skill in missing_keywords:
            st.markdown(f"- Consider learning or showcasing **{skill}**.")
    else:
        st.write("Your resume aligns very well with the selected role!")

    # Export to CSV
    result_df = pd.DataFrame({
        "Keyword": roles_keywords[job_role],
        "Matched": ["Yes" if kw in matched_keywords else "No" for kw in roles_keywords[job_role]]
    })
    st.markdown(get_download_link(result_df), unsafe_allow_html=True)
