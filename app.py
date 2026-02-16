import streamlit as st
import pandas as pd
import pdfplumber
import spacy
import re
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="TalentInsight | AI Resume Analytics Dashboard", layout="wide", page_icon="📊")

# Load NLP model
@st.cache_resource
def load_nlp():
    return spacy.load("en_core_web_sm")

nlp = load_nlp()

# --- DOMAIN KNOWLEDGE BASE ---
# Categorizing skills to auto-detect the Department
SKILL_MAPPING = {
    "Piping / Mechanical": ["SP3D", "PDMS", "E3D", "PDS", "Piping", "Isometrics", "Stress Analysis", "CAESAR II", "PV Elite", "Static Equipment", "Pressure Vessels", "Tanks"],
    "Civil / Structural": ["STAAD.Pro", "Tekla", "Civil", "Structural", "Foundation", "Concrete", "Steel Structure", "Revit"],
    "Electrical / Instrumentation": ["SPI", "SmartPlant Instrumentation", "Cable Tray", "Loop Diagrams", "Electrical", "Instrumentation", "P&ID", "Earthing"],
    "Process": ["HYSYS", "Simulation", "PFD", "Hydraulic", "Line Sizing", "Hazop"]
}

# Unified weighted scoring system
WEIGHTS = {
    "High Value": ["SP3D", "PDMS", "E3D", "CAESAR II", "STAAD.Pro", "Tekla", "SPI"], # The expensive software
    "Core": ["Piping", "Structural", "Civil", "Instrumentation", "Process", "ASME", "API"]
}

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t: text += t + "\n"
    return text

def extract_details(text):
    """Extracts Email, Phone, and estimated Years of Experience."""
    email = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    phone = re.findall(r'\+?\d[\d -]{8,12}\d', text)
    
    # Heuristic for Experience: Look for patterns like "5 Years Experience" or "Total Exp: 8"
    exp_pattern = re.search(r'(\d+)\+?\s*(?:years?|yrs?)', text, re.IGNORECASE)
    experience = int(exp_pattern.group(1)) if exp_pattern else 0
    
    return {
        "email": email[0] if email else "Not Found",
        "phone": phone[0] if phone else "Not Found",
        "experience": experience
    }

def analyze_profile(text):
    """
    1. Identifies Skills
    2. Calculates Score
    3. Predicts Department (Civil vs Mech vs Elec)
    """
    text_lower = text.lower()
    found_skills = []
    score = 0
    dept_scores = {k: 0 for k in SKILL_MAPPING.keys()}

    # Skill Scanning & Scoring
    for dept, skills in SKILL_MAPPING.items():
        for skill in skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
                dept_scores[dept] += 1 # Vote for department
                
                # Global Score Calculation
                if any(hv.lower() == skill.lower() for hv in WEIGHTS["High Value"]):
                    score += 15 # Huge boost for main software
                elif any(c.lower() == skill.lower() for c in WEIGHTS["Core"]):
                    score += 5
                else:
                    score += 2

    # Determine Department (Highest skill count wins)
    predicted_dept = max(dept_scores, key=dept_scores.get)
    if dept_scores[predicted_dept] == 0:
        predicted_dept = "General / Unclassified"

    return list(set(found_skills)), score, predicted_dept

def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return "Candidate"

# --- MAIN APP ---
def main():
    # Sidebar Branding
    st.sidebar.image("logo_2.png", use_container_width=True)
    st.sidebar.markdown("## ⚙️ Control Panel")
    
    st.title("TalentInsight | AI Resume Analytics Dashboard")
    st.markdown("### 🚀 Next-Gen Resume Parsing & Fitment Engine")

    # File Upload
    uploaded_files = st.sidebar.file_uploader("Upload Resumes (PDF)", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files:
        data = []
        for file in uploaded_files:
            text = extract_text_from_pdf(file)
            details = extract_details(text)
            name = extract_name(text[:300])
            skills, score, dept = analyze_profile(text)
            
            data.append({
                "Name": name,
                "Department": dept,
                "Experience (Yrs)": details['experience'],
                "Proton Score": score,
                "Skills": ", ".join(skills),
                "Email": details['email'],
                "Filename": file.name
            })
        
        df = pd.DataFrame(data)

        # --- ADVANCED FILTERS ---
        st.sidebar.divider()
        st.sidebar.subheader("🎯 Filters")
        
        # Department Filter
        all_depts = ["All"] + list(df["Department"].unique())
        selected_dept = st.sidebar.selectbox("Filter by Department", all_depts)
        
        # Experience Slider
        min_exp, max_exp = int(df["Experience (Yrs)"].min()), int(df["Experience (Yrs)"].max())

        # [FIX] Handle crash if only 1 resume is uploaded (min == max)
        if min_exp == max_exp:
            min_slider = 0
            max_slider = max(max_exp, 10) # Force a range of at least 0-10
        else:
            min_slider = min_exp
            max_slider = max_exp
            
        exp_range = st.sidebar.slider(
            "Experience Range (Years)", 
            min_value=min_slider, 
            max_value=max_slider, 
            value=(min_exp, max_exp)
        )
        
        # Apply Filters
        filtered_df = df[
            (df["Experience (Yrs)"] >= exp_range[0]) & 
            (df["Experience (Yrs)"] <= exp_range[1])
        ]
        if selected_dept != "All":
            filtered_df = filtered_df[filtered_df["Department"] == selected_dept]

        # --- DASHBOARD LAYOUT ---
        
        # Top Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Candidates Found", len(filtered_df))
        m2.metric("Avg Experience", f"{round(filtered_df['Experience (Yrs)'].mean(), 1)} Yrs")
        m3.metric("Avg Skill Score", round(filtered_df['Proton Score'].mean(), 1))
        top_talent = filtered_df.loc[filtered_df['Proton Score'].idxmax()]['Name'] if not filtered_df.empty else "N/A"
        m4.metric("Top Talent", top_talent)

        st.divider()

        # --- ROW 1: DEPARTMENT & SKILL VISUALS ---
        col_charts_1, col_charts_2 = st.columns(2)
        
        with col_charts_1:
            st.subheader("Distribution by Department")
            # Donut Chart for Departments
            fig_pie = px.pie(filtered_df, names='Department', title='Talent Pool Composition', hole=0.4, color_discrete_sequence=px.colors.qualitative.Prism)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_charts_2:
            st.subheader("Score vs. Experience Analysis")
            # Scatter Plot to find "Hidden Gems" (High Score but Low Exp) or "Experts"
            fig_scatter = px.scatter(
                filtered_df, 
                x="Experience (Yrs)", 
                y="Proton Score", 
                color="Department", 
                size="Proton Score",
                hover_data=["Name", "Skills"],
                title="Talent Quadrant: Experience vs. Fit"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        # --- ROW 2: DETAILED ANALYSIS ---
        col_charts_3, col_charts_4 = st.columns(2)

        with col_charts_3:
            st.subheader("Score Distribution (Histogram)")
            # Histogram to see if candidates are mostly good or bad
            fig_hist = px.histogram(filtered_df, x="Proton Score", nbins=10, color="Department", title="Quality Spread of Candidates")
            st.plotly_chart(fig_hist, use_container_width=True)

        with col_charts_4:
            st.subheader("Departmental Skill Gap")
            # Box Plot to compare quality across departments
            fig_box = px.box(filtered_df, x="Department", y="Proton Score", points="all", title="Skill Depth per Department")
            st.plotly_chart(fig_box, use_container_width=True)

        # --- ROW 3: DATAFRAME ---
        st.subheader("📋 Detailed Candidate Registry")
        st.dataframe(
            filtered_df.sort_values(by="Proton Score", ascending=False).style.background_gradient(cmap="Greens", subset=["Proton Score"]),
            use_container_width=True
        )

        # Download
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Filtered Data", csv, "proton_analytics_report.csv", "text/csv")

    else:
        # Empty State - Professional Instructions
        st.info("👋 Welcome to the Proton Engineering Analytics Dashboard.")
        st.write("Please upload candidate resumes from the sidebar to generate the analysis.")
        st.write("Supported Formats: **PDF** (Searchable text)")

if __name__ == "__main__":
    main()