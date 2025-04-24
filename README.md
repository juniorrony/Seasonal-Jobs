# 🌾 Seasonal Jobs Portal (H2A & H2B)

A Flask web application that fetches and displays seasonal job listings (H2A & H2B) from the U.S. Department of Labor’s API. Jobs are fetched daily and presented in a modern, searchable, filterable interface.

## 🔍 Features

- 🗂 View **H2A** (agricultural) and **H2B** (non-agricultural) jobs
- 📆 Automatically fetches and extracts daily job listings from government ZIP archives
- 📄 Filter jobs by title and location
- 🔍 Global search with clearable input
- 📊 Responsive and interactive job table with modal details
- 🕛 Daily job data refresh via APScheduler
- 🖥️ Hosted-ready for platforms like **Render**, **Heroku**, etc.

---

## 🚀 Live Demo

> Add your deployed URL here once hosted  
Example: `https://seasonaljobs.onrender.com`

---

## 📦 Requirements

- Python 3.8+
- Flask
- APScheduler
- requests
- gunicorn (for deployment)

---

## ⚙️ Installation

```bash
git clone https://github.com/yourusername/seasonal-jobs.git
cd seasonal-jobs
pip install -r requirements.txt

📁 Project Structure
seasonal-jobs/
│
├── templates/
│   ├── index.html       # Job listing UI
│   └── landing.html     # Landing page with job type selector
│
├── data/                # Extracted and cached JSON files
├── app.py               # Main Flask application
├── requirements.txt     # Python dependencies
├── Procfile             # For deployment (Render, Heroku)
└── README.md            # You're reading this!
