# 🕒 EntryExit Insight

**A biometric attendance analytics platform that turns raw punch-in/punch-out data into live, actionable dashboards.**

🔗 **Live App:** [entryexit-insight.streamlit.app](https://entryexit-insight.streamlit.app/)

---

## 📌 Overview

EntryExit Insight is a Streamlit-based web application built to analyze employee/staff **entry-exit (biometric) attendance data**. It replaces manual, spreadsheet-heavy attendance tracking with a **live, interactive dashboard** — pulling data directly from Google Sheets, processing it in real time, and surfacing attendance trends, anomalies, and summaries through a clean, premium UI.

The goal: make attendance data *actually useful* instead of sitting unused in raw biometric export sheets.

---

## ✨ Features

- 📊 **Live Dashboards** — Real-time visualization of attendance data, refreshed directly from the backend sheet.
- ☁️ **Google Sheets Backend** — No traditional database setup required; Google Sheets acts as a lightweight, easily editable data source.
- 🔐 **Login Logging** — Tracks and logs user access/sessions within the app for accountability and audit purposes.
- 🎨 **Premium Navbar UI** — Custom-designed navigation for a polished, non-default Streamlit look and feel.
- ⚡ **Instant Insights** — Quickly spot attendance patterns, late entries, early exits, and irregularities without manual filtering.

---

## 🛠️ Tech Stack

| Layer            | Technology                     |
|-------------------|--------------------------------|
| Frontend/App       | [Streamlit](https://streamlit.io/) |
| Language           | Python                         |
| Data Processing    | Pandas                         |
| Backend/Storage    | Google Sheets (via Google Sheets API) |
| Deployment         | Streamlit Community Cloud      |

---

## 🚀 Live Demo

👉 Try it here: **[https://entryexit-insight.streamlit.app/](https://entryexit-insight.streamlit.app/)**

<img width="522" height="511" alt="image" src="https://github.com/user-attachments/assets/9b8ec706-ecbd-45c7-ae18-fa4987eb5b1c" />

---

## ⚙️ Installation (Run Locally)

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/entryexit-insight.git
cd entryexit-insight

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Google Sheets API credentials
#    (place credentials.json / set up .streamlit/secrets.toml)

# 5. Run the app
streamlit run app.py
```

---

## 🔑 Google Sheets Setup

This app reads live data from a connected Google Sheet. To run it yourself:

1. Create a Google Cloud project and enable the **Google Sheets API**.
2. Generate a **service account** and download its JSON credentials.
3. Share your attendance Google Sheet with the service account email.
4. Add the credentials to `.streamlit/secrets.toml` (recommended for Streamlit Cloud) or as environment variables.

---


## 🗺️ Roadmap

- [ ] Export attendance reports as PDF/Excel
- [ ] Email alerts for repeated late entries
- [ ] Multi-department / multi-location support
- [ ] Migrate backend from Google Sheets to a proper database (e.g., PostgreSQL)

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to check the [issues page](https://github.com/<your-username>/entryexit-insight/issues).

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 👤 Author

**Raunit**
📍 Pune, India
💼 Cloud/AWS Data Engineer aspirant | Ex-DataOps Engineer

- GitHub: https://github.com/raunit-pandey
- LinkedIn: https://www.linkedin.com/in/raunit-pandey/

---

⭐ If you found this project useful, consider giving it a star on GitHub!
