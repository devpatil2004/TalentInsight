# 🚀 TalentInsight – AI Resume Analytics Dashboard

An AI-powered recruitment analytics system that automates resume screening, candidate scoring, and domain classification using Natural Language Processing and interactive data visualization.

---

## 📌 Project Overview  

TalentInsight transforms unstructured resume PDFs into structured, actionable hiring insights.  
It extracts skills, experience, and domain information, assigns weighted skill scores, and visualizes candidate quality through an interactive dashboard.

### 🎯 Key Benefits  
- Automated resume parsing and screening  
- Intelligent candidate ranking  
- Faster shortlisting with smart filters  
- Data-driven hiring insights  

---

## ⚙️ Features  

### 🧠 AI-Based Skill Scoring  
Resumes are evaluated using weighted technical skills including:  
- SP3D, PDMS, E3D, CAESAR II, STAAD.Pro  
- Core engineering domains (Piping, Structural, Civil, Electrical)  

Each candidate receives a **Skill Match Score**.

---

### 📂 Automatic Domain Classification  

Candidates are categorized into:  
- Mechanical / Piping  
- Civil / Structural  
- Electrical / Instrumentation  

---

### 📊 Interactive Dashboard  

Visual analytics include:  
- Department-wise candidate distribution  
- Experience vs skill score visualization  
- Talent quality comparison  

---

### 🔍 Smart Filtering  

Filter resumes by:  
- Department  
- Experience range  
- Skill score  

Export shortlisted candidates as CSV.

---

## 🛠️ Tech Stack  

- Python  
- Streamlit  
- Pandas  
- Plotly  
- SpaCy  
- PDFPlumber  

---

## 🚀 Installation  

### Prerequisites  
Python 3.9+

### Setup  

```bash
pip install streamlit pandas plotly pdfplumber spacy
python -m spacy download en_core_web_sm
