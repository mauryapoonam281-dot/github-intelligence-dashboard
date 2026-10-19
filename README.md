# 📊 GitHub Intelligence Dashboard

An interactive Streamlit application that fetches, analyzes, and visualizes GitHub repository data using the GitHub API.

---

## 📌 Project Overview
The **GitHub Intelligence Dashboard** provides analytical insights into GitHub repositories. It analyzes key parameters like stars, forks, open issues, commit activity, and language distributions to help developers and recruiters evaluate repository engagement and metrics.

---

## 🚀 Features
* **Automated Data Fetching:** Scrapes repo details, star counts, fork metrics, and commit statistics using GitHub API.
* **Exploratory Data Analysis (EDA):** Jupyter notebooks dedicated to data processing, cleaning, and trend analysis.
* **Interactive Dashboard:** Built with Streamlit for dynamic filtering and visual analytics.

---

## 📁 Repository Structure
```text
github-intelligence-dashboard/
│
├── data/
│   └── github_intelligence_data (1).xls.csv  # Raw and processed datasets
│
├── notebooks/
│   ├── 01_data_collection.ipynb              # Data fetching scripts
│   └── 02_exploratory_data_analysis.ipynb   # EDA & data visualization
│
├── app.py                                    # Streamlit Dashboard application
└── README.md                                 # Project documentation

