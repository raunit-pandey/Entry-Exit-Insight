EntryExit Insight
Technical Documentation & Developer Guide
Version 1.0  |  April 2026



1.  OVERVIEW

What is EntryExit Insight?
EntryExit Insight is a Streamlit web application that calculates work and break durations from raw biometric punch data. It supports two role-based tabs — Team Member and Team Leader — each with separate thresholds, live metrics, and session breakdowns. The app runs locally on http://localhost:8501 and saves user feedback to Google Sheets.

Key Capabilities
•	Paste biometric log data and auto-parse all HH:MM timestamps
•	Live preview dashboard — auto-refreshes every second
•	Role-based eligibility thresholds (Full Day / Half Day)
•	Displays earliest logout time in 12-hour format
•	Human-readable work & break summary
•	Session breakdown panel (work sessions vs break sessions)
•	Light / Dark mode toggle with botanical wallpaper theme
•	Feedback form
•	Hooray banner when minimum time target is met



2.  FOLDER STRUCTURE

Your project directory should look like this:

your-project/
├── app.py                  ← Main Streamlit application
├── Icon.png                ← App icon (optional)
├── requirements.txt        ← Python dependencies



3.  REQUIREMENTS

Python Version
Python 3.10 or higher is required (zoneinfo is a stdlib module from 3.9+).

Python Packages  (requirements.txt)

Package	Minimum Version	Purpose
streamlit	>=1.32.0	Web framework & UI
gspread	>=6.0.0	Google Sheets API client
google-auth	>=2.0.0	OAuth2 / Service Account auth

Install Command
pip install -r requirements.txt

Standard Library Modules Used
•	datetime — date/time arithmetic
•	pathlib — file path handling
•	re — regex for timestamp extraction
•	zoneinfo — IST (Asia/Kolkata) timezone

[feedback_sheet] section
Key	Description
sheet_id	Google Sheet ID from the URL  (/d/<ID>/edit)
worksheet	Worksheet tab name — default "Sheet1"

Required Google Sheet Columns
The target worksheet must have these headers in Row 1:
•	Column A: Timestamp
•	Column B: Feedback

Sharing the Sheet
Open the Google Sheet → Share → paste the service account client_email → set role to Editor → Send.


5.  ROLE-BASED THRESHOLDS

Team Member  (minimum logout duration)
Day Type	Minimum Total Time	Formula
Full Day	7 hours 30 minutes	first_entry  +  7h 30m
Half Day	4 hours 30 minutes	first_entry  +  4h 30m

Team Leader  (minimum login / work time)
Day Type	Minimum Work Time	Formula
Full Day	7 hours 00 minutes	first_entry  +  7h 00m
Half Day	4 hours 00 minutes	first_entry  +  4h 00m

Break Allowance
Both roles share a break allowance target of 1 hour 30 minutes. The Remaining Break card shows budget left. Work and break sessions alternate — odd punches = active session.


6.  BIOMETRIC LOG PARSING

The parser extracts all HH:MM timestamps using this regex:
\b(?:[01]?\d|2[0-3]):[0-5]\d\b

Parsing Rules
•	Timestamps are matched in order of appearance in the pasted text
•	If a timestamp is earlier than the previous one, the calendar day is advanced by +1
•	Odd-indexed sessions (0, 2, 4…) are Work sessions
•	Even-indexed gaps (1, 3, 5…) are Break sessions
•	Odd total punches = the last session is still live (ongoing)

Example Input
Biometric.
09:02
Biometric.
10:15
Biometric.
10:45

Result: Work 09:02–10:15 (1h 13m), Break 10:15–10:45 (30m), then active work from 10:45 onwards.


7.  LIVE DASHBOARD  METRICS

The dashboard auto-refreshes every 1 second using @st.fragment(run_every='1s'). Each tab has its own independent fragment and session state.

Metric Card	Description
Total Work Time	Sum of all completed + ongoing work sessions
Total Break Time	Sum of all completed break sessions
Total Logged Time	Work + Break combined (Team Member only)
Eligible Logout At	first_entry + threshold → displayed in 12hr format
Time Until Eligible	Countdown to earliest logout; shows — when passed
Remaining Break	Break allowance (1h 30m) minus breaks taken so far

Status Banner
•	Before threshold: blue info box — '🚀  You Need to Punch Out At :- HH:MM AM/PM'
•	After threshold: green hooray banner — '🎉  Target Completed! You're Free to Go!!'


8.  SESSION STATE  KEYS

Key	Purpose
member_day_type	Selected day type for Team Member tab
leader_day_type	Selected day type for Team Leader tab
member_biometric_points	Parsed datetime list for Team Member
leader_biometric_points	Parsed datetime list for Team Leader
member_session_panel_open	Toggle state for session breakdown panel
leader_session_panel_open	Toggle state for session breakdown panel
dark_mode	Boolean — current theme (True = dark)
feedback_saved	Flag to show success banner after rerun
_entryexit_cleared_caches	One-time cache-clear guard on startup


9.  THEMING  &  DESIGN

Light / Dark Toggle
A sun/moon pill toggle in the header switches themes. The toggle sets st.session_state.dark_mode and calls st.rerun(). THEME_CSS is an f-string that injects theme-specific colors dynamically on every render.

CSS Variables
•	--accent-gold: #D4AF72  — primary gold accent
•	--accent-gold-hover: #C49C5F  — hover state
•	--accent-gold-soft: #F2DDBB  — light gold for dark mode highlights
•	--card-topline: #1E3A8A  — metric card top border (light) / gold (dark)

Botanical Wallpaper
Background SVG wallpapers are embedded as base64 data URIs. Dark mode uses warm amber-bronze leaf patterns on #1A1308. Light mode uses sage-green patterns on #F0FAF5. A frosted overlay ensures content readability.


10.  FEEDBACK  SYSTEM

How it Works
•	User types feedback in the st.form text area
•	Ctrl+Enter or 'Submit Feedback' button triggers submission
•	App authenticates with Google using the Service Account credentials
•	gspread appends a new row: [Timestamp (IST), Feedback text]
•	st.session_state.feedback_saved = True is set, then st.rerun() is called
•	On next render the success banner appears, then the flag resets

Error Handling
If the Google Sheets call fails (network error, invalid credentials, sheet not shared), an error message is displayed: '❌ Could not save feedback. Please try again.'

Google Sheets API Scopes Used
•	https://www.googleapis.com/auth/spreadsheets
•	https://www.googleapis.com/auth/drive


11.  RUNNING  THE  APP

Local Setup
•	Step 1 — Clone or download the project folder
•	Step 2 — Create .streamlit/secrets.toml (see Section 4)
•	Step 3 — Install dependencies:
pip install -r requirements.txt
•	Step 4 — Run the app:
streamlit run app.py
•	Step 5 — Open browser at  http://localhost:8501

Stopping the App
Press Ctrl+C in the terminal where Streamlit is running.

Port Conflict
If port 8501 is already in use, run on a different port:
streamlit run app.py --server.port 8502


12.  KNOWN  LIMITATIONS

•	Data is not persisted between sessions — biometric input must be re-pasted after refresh
•	The app assumes all punches belong to a single calendar day (midnight rollover is handled but rare)
•	No authentication — anyone with the URL can access the app
•	Google Sheets write requires active internet connection
•	Scroll-to-top JS relies on Streamlit's DOM structure which may change with Streamlit upgrades


13.  TROUBLESHOOTING

Error / Symptom	Fix
Could not save feedback	Share the Google Sheet with the service account email as Editor
ModuleNotFoundError: zoneinfo	Upgrade to Python 3.10+
StreamlitAPIException: cannot modify session_state after widget	Do not assign to widget key directly; use a separate state key
No timestamps parsed	Ensure input contains times in HH:MM or H:MM format
Metrics not updating	The @st.fragment auto-refresh requires Streamlit ≥1.32


EntryExit Insight  —  Internal Tool  —  April 2026
