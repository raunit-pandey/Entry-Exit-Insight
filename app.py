import base64
import datetime as dt
from pathlib import Path
import re
from zoneinfo import ZoneInfo

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
ICON_PATH = BASE_DIR / "Icon.png"
PAGE_ICON = str(ICON_PATH) if ICON_PATH.exists() else "⏱️"
PUNE_TZ = ZoneInfo("Asia/Kolkata")

# Widget keys (Streamlit-owned). Never assign programmatically to these keys.
MEMBER_DAY_WIDGET_KEY = "_ui_member_day_type"
LEADER_DAY_WIDGET_KEY = "_ui_leader_day_type"
MEMBER_PASTE_WIDGET_KEY = "_ui_member_paste"
LEADER_PASTE_WIDGET_KEY = "_ui_leader_paste"
MEMBER_DAY_QUERY = "member_day"
LEADER_DAY_QUERY = "leader_day"


def now_pune() -> dt.datetime:
    return dt.datetime.now(PUNE_TZ).replace(tzinfo=None, microsecond=0)


st.set_page_config(
    page_title="EntryExit Insight",
    page_icon=PAGE_ICON,
    layout="wide",
)

# ── Signup state — restore from query param on every load ────────────────────
def _decode_user_param(val: str) -> str:
    try:
        return base64.urlsafe_b64decode(val.encode()).decode()
    except Exception:
        return ""

if "signup_done" not in st.session_state:
    _qp_u = st.query_params.get("u", "")
    if _qp_u:
        _decoded = _decode_user_param(_qp_u)          # "Name||email"
        if "||" in _decoded:
            _qp_name, _qp_email = _decoded.split("||", 1)
            if _qp_email and "@" in _qp_email:
                st.session_state.signup_done      = True
                # If name is missing in URL param, derive it from the email prefix
                if _qp_name.strip():
                    st.session_state.signup_user_name = _qp_name.strip()
                else:
                    st.session_state.signup_user_name = _qp_email.split("@")[0].replace(".", " ").title()
    if "signup_done" not in st.session_state:
        st.session_state.signup_done = False

st.markdown(
    """
    <style>
    :root {
        --accent-gold: #d4af72;
        --accent-gold-hover: #c49c5f;
        --accent-gold-soft: #f2ddbb;
        --card-topline: #1e3a8a;
    }

    .stApp {
        background: var(--background-color);
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2.2rem;
    }

    h1, h2, h3 {
        color: #000000 !important;
        letter-spacing: 0.3px;
        font-weight: 700;
        text-wrap: balance;
    }

    h1 {
        font-size: 3rem !important;
        margin-bottom: 0.2rem;
        font-family: "Georgia", "Times New Roman", serif;
    }

    p, label, .stCaption {
        color: #000000 !important;
    }

    /* High-specificity light mode text fix */
    .stApp p,
    .stApp label,
    .stApp span,
    .stApp div,
    .stApp .stCaption,
    .stApp .stMarkdown,
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stMarkdownContainer"] span,
    .stApp [data-testid="stMarkdownContainer"] div,
    .stApp [data-testid="stMarkdownContainer"] strong,
    .stApp [data-testid="stMarkdownContainer"] b,
    .stApp [data-testid="stRadio"] label,
    .stApp [data-testid="stRadio"] span,
    .stApp [data-testid="stTabs"] [role="tab"] {
        color: #000000 !important;
    }

    /* Caption colour is intentionally NOT set here — controlled by theme-aware font-sync block */

    div[data-testid="stMetric"] {
        background: linear-gradient(
            180deg,
            color-mix(in srgb, var(--secondary-background-color) 95%, transparent) 0%,
            color-mix(in srgb, var(--secondary-background-color) 85%, transparent) 100%
        );
        border: 1px solid color-mix(in srgb, var(--accent-gold) 22%, var(--text-color));
        border-radius: 16px;
        padding: 14px;
        box-shadow: 0 12px 26px color-mix(in srgb, black 20%, transparent);
        backdrop-filter: blur(2px);
        position: relative;
        overflow: hidden;
    }

    div[data-testid="stMetric"]::before {
        content: "";
        position: absolute;
        inset: 0 0 auto 0;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, var(--card-topline) 50%, transparent 100%);
        opacity: 0.85;
    }

    div[data-testid="stMetricLabel"] {
        color: var(--muted) !important;
    }

    div[data-testid="stMetricValue"] {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    .stTextArea textarea {
        border: 1px solid color-mix(in srgb, var(--accent-gold) 22%, var(--text-color));
        border-radius: 12px;
        background: var(--secondary-background-color);
        color: #000000;
        box-shadow: inset 0 1px 0 color-mix(in srgb, white 8%, transparent);
    }

    .stTextArea textarea:focus {
        border-color: var(--accent-gold) !important;
        box-shadow: 0 0 0 2px color-mix(in srgb, var(--accent-gold) 28%, transparent) !important;
    }

    /* Hide "Press Ctrl+Enter / Enter to submit" hints everywhere */
    [data-testid="InputInstructions"],
    .stTextArea [data-testid="InputInstructions"],
    .stTextInput [data-testid="InputInstructions"],
    .stTextArea small,
    .stTextInput small {
        display: none !important;
    }

    /* Disable all hyperlinks — plain non-clickable text */
    a, a:hover, a:visited, a:active, a:focus {
        pointer-events: none !important;
        cursor: default !important;
        text-decoration: none !important;
        color: #000000 !important;
    }

    /* Hide Streamlit anchor link icons */
    a[data-testid="stMarkdownAnchorLink"],
    .st-anchor-link,
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        background: linear-gradient(180deg, #e2c18a 0%, var(--accent-gold) 100%);
        color: #1a1308 !important;
        border-radius: 12px;
        border: 1px solid color-mix(in srgb, #fff 22%, var(--accent-gold));
        font-weight: 700;
        transition: all 0.15s ease;
        box-shadow: 0 10px 22px rgba(212, 175, 114, 0.28);
        opacity: 1 !important;
        min-height: 2.8rem;
    }

    .stButton > button:hover:not(:disabled),
    .stFormSubmitButton > button:hover:not(:disabled) {
        background: linear-gradient(180deg, #edd2a5 0%, var(--accent-gold-hover) 100%);
        transform: translateY(-1px) scale(1.01);
        box-shadow: 0 14px 30px rgba(212, 175, 114, 0.34);
    }

    .stButton > button:disabled {
        background-color: #6f634f !important;
        color: #d7c9b2 !important;
        opacity: 0.7 !important;
        cursor: not-allowed;
        box-shadow: none;
    }

    .stMarkdown, .stText {
        color: #000000;
    }

    hr {
        border-color: color-mix(in srgb, var(--accent-gold) 25%, transparent);
    }

    /* Disable all hyperlinks globally — plain non-clickable text */
    a, a:hover, a:visited, a:active, a:focus {
        pointer-events: none !important;
        cursor: default !important;
        text-decoration: none !important;
        color: #000000 !important;
    }

    div[data-testid="stAlert"] {
        border: 1px solid color-mix(in srgb, var(--accent-gold) 28%, var(--text-color));
        border-radius: 12px;
        background: color-mix(in srgb, var(--secondary-background-color) 90%, transparent);
    }

    /* Tab switch: fade + slide animation */
    @keyframes entryexit-tab-reveal {
        from { opacity: 0; transform: translateX(14px); }
        to   { opacity: 1; transform: translateX(0); }
    }

    [data-testid="stTabs"] [role="tabpanel"],
    [data-testid="stTabs"] [data-baseweb="tab-panel"] {
        transition: opacity 0.28s ease, transform 0.28s ease;
    }

    [data-testid="stTabs"] [role="tabpanel"]:not([aria-hidden="true"]),
    [data-testid="stTabs"] [data-baseweb="tab-panel"]:not([hidden]) {
        animation: entryexit-tab-reveal 0.38s cubic-bezier(0.22, 1, 0.36, 1) both;
    }

    .entryexit-hooray-banner {
        background: linear-gradient(180deg, #1f6b3a 0%, #145a2e 100%);
        color: #ffffff !important;
        text-shadow: 0 1px 3px rgba(0,0,0,0.35);
        padding: 14px 18px;
        border-radius: 12px;
        border: 1px solid color-mix(in srgb, #34d399 55%, #14532d);
        font-weight: 700;
        font-size: 1.1rem;
        text-align: center;
        box-shadow: 0 10px 28px color-mix(in srgb, #22c55e 35%, transparent);
        margin-top: 0.35rem;
    }

    .entryexit-hooray-banner,
    .entryexit-hooray-banner p,
    .entryexit-hooray-banner span {
        color: #ffffff !important;
    }

    .entryexit-summary-box {
        background: color-mix(in srgb, var(--secondary-background-color) 80%, transparent);
        border: 1px solid color-mix(in srgb, var(--accent-gold) 22%, var(--text-color));
        border-radius: 14px;
        padding: 16px 20px;
        margin-top: 0.6rem;
        line-height: 2.2;
        user-select: none;
        -webkit-user-select: none;
    }

    .entryexit-summary-box *::selection {
        background: transparent;
    }

    .entryexit-summary-box *::-moz-selection {
        background: transparent;
    }

    @media (prefers-color-scheme: dark) {
        :root { --card-topline: var(--accent-gold-soft); }

        .stApp {
            background:
                radial-gradient(circle at 14% -10%, rgba(148,137,121,0.10), transparent 34%),
                radial-gradient(circle at 86% 0%, rgba(57,62,70,0.20), transparent 32%),
                #605B51;
        }

        div[data-testid="stMetric"] {
            background: linear-gradient(180deg, #706B61 0%, #605B51 100%);
            border: 1px solid #424850;
            box-shadow: 0 16px 30px rgba(0, 0, 0, 0.50);
        }

        .stTextArea textarea {
            background: #605B51;
            border-color: #7a746a;
        }

        .entryexit-hooray-banner {
            background: linear-gradient(180deg, #166534 0%, #0f3d1f 100%);
            border-color: #22c55e;
            box-shadow: 0 12px 32px rgba(34, 197, 94, 0.22);
        }

        .entryexit-summary-box {
            background: #605B51;
            border-color: #7a746a;
        }

        .stButton > button,
        .stButton > button p,
        .stButton > button span,
        .stButton > button div {
            color: #000000 !important;
            text-shadow: none !important;
        }
        .stApp .stButton > button {
            color: #000000 !important;
        }

        /* ── Fix: all text white in dark mode ── */
        .stApp p,
        .stApp label,
        .stApp span,
        .stApp div,
        .stApp .stCaption,
        .stApp .stMarkdown,
        .stApp [data-testid="stCaptionContainer"] p,
        .stApp [data-testid="stMarkdownContainer"] p,
        .stApp [data-testid="stMarkdownContainer"] span,
        .stApp [data-testid="stMarkdownContainer"] div,
        .stApp [data-testid="stMarkdownContainer"] strong,
        .stApp [data-testid="stMarkdownContainer"] b,
        .stApp [data-testid="stRadio"] label,
        .stApp [data-testid="stRadio"] span,
        .stApp [data-testid="stTabs"] [role="tab"],
        .stApp h1, .stApp h2, .stApp h3,
        .stApp h4, .stApp h5, .stApp h6 {
            color: #ffffff !important;
        }
    }

    /* ── Session panel ── */
    .ee-session-panel {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-top: 14px;
    }

    .ee-session-col {
        background: color-mix(in srgb, var(--secondary-background-color) 80%, transparent);
        border: 1px solid color-mix(in srgb, var(--accent-gold) 20%, var(--text-color));
        border-radius: 14px;
        padding: 16px 18px 12px;
        position: relative;
        overflow: hidden;
    }

    .ee-session-col::before {
        content: "";
        position: absolute;
        inset: 0 0 auto 0;
        height: 2px;
    }

    .ee-session-col.work::before {
        background: linear-gradient(90deg, transparent, #3b82f6, transparent);
    }

    .ee-session-col.brk::before {
        background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
    }

    .ee-col-header {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 7px;
    }

    .ee-col-header.work { color: #60a5fa; }
    .ee-col-header.brk  { color: var(--accent-gold); }

    .ee-col-count {
        font-size: 0.68rem;
        padding: 2px 7px;
        border-radius: 20px;
        font-weight: 700;
        letter-spacing: 0;
    }

    .ee-col-header.work .ee-col-count { background: rgba(59,130,246,0.18); color: #93c5fd; }
    .ee-col-header.brk  .ee-col-count { background: rgba(212,175,114,0.18); color: var(--accent-gold); }

    .ee-row {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        padding: 7px 0;
        border-bottom: 1px solid color-mix(in srgb, var(--text-color) 8%, transparent);
        gap: 8px;
        font-size: 0.82rem;
    }

    .ee-row:last-child { border-bottom: none; }

    .ee-row-label {
        color: color-mix(in srgb, var(--text-color) 55%, transparent);
        white-space: nowrap;
        flex-shrink: 0;
        font-size: 0.78rem;
    }

    .ee-row-range {
        color: color-mix(in srgb, var(--text-color) 80%, transparent);
        font-size: 0.8rem;
        text-align: center;
        flex: 1;
    }

    .ee-row-dur {
        font-weight: 700;
        white-space: nowrap;
        font-size: 0.84rem;
    }

    .ee-row-dur.work { color: #60a5fa; }
    .ee-row-dur.brk  { color: var(--accent-gold); }

    .ee-ongoing-badge {
        font-size: 0.65rem;
        background: rgba(34,197,94,0.18);
        color: #4ade80;
        border-radius: 10px;
        padding: 1px 6px;
        font-weight: 700;
        letter-spacing: 0.06em;
        vertical-align: middle;
        margin-left: 4px;
    }

    @media (prefers-color-scheme: dark) {
        .ee-session-col {
            background: #605B51;
            border-color: #7a746a;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Utility functions ──────────────────────────────────────────────────────────

def hms_to_seconds(hours: int, minutes: int, seconds: int) -> int:
    return (hours * 3_600) + (minutes * 60) + seconds


def format_short(total_seconds: int) -> str:
    total_seconds = max(total_seconds, 0)
    h = total_seconds // 3_600
    m = (total_seconds % 3_600) // 60
    s = total_seconds % 60
    return f"{h}h {m:02d}m {s:02d}s"


def format_clock(total_seconds: int) -> str:
    total_seconds = max(total_seconds, 0)
    h = total_seconds // 3_600
    m = (total_seconds % 3_600) // 60
    s = total_seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def format_hours_minutes(total_seconds: int) -> str:
    total_seconds = max(total_seconds, 0)
    h = total_seconds // 3_600
    m = (total_seconds % 3_600) // 60
    return f"{h}h {m:02d}m"


def format_human(total_seconds: int) -> str:
    """Plain English duration: '8 hrs 50 mins'"""
    total_seconds = max(total_seconds, 0)
    h = total_seconds // 3_600
    m = (total_seconds % 3_600) // 60
    parts = []
    if h:
        parts.append(f"{h} hr{'s' if h != 1 else ''}")
    if m or not h:
        parts.append(f"{m} min{'s' if m != 1 else ''}")
    return " ".join(parts)


def get_first_name() -> str:
    """Return only the first word of the stored signup name.
    If an email was accidentally stored, derive a display name from the prefix."""
    full = st.session_state.get("signup_user_name", "")
    stripped = full.strip()
    if not stripped:
        return ""
    # If it looks like an email, derive name from the prefix
    if "@" in stripped:
        prefix = stripped.split("@")[0].replace(".", " ").replace("_", " ")
        return prefix.split()[0].capitalize() if prefix.strip() else ""
    return stripped.split()[0].capitalize()


# ── Constants ──────────────────────────────────────────────────────────────────

DAY_FULL = "Full Day"
DAY_HALF = "Half Day"
DAY_TYPE_OPTIONS = (DAY_FULL, DAY_HALF)

# Team Member: minimum total logged time (work + breaks on site)
MEMBER_THRESHOLDS: dict[str, int] = {
    DAY_FULL: hms_to_seconds(7, 30, 0),
    DAY_HALF: hms_to_seconds(4, 30, 0),
}
# Team Leader: minimum login / work time
LEADER_THRESHOLDS: dict[str, int] = {
    DAY_FULL: hms_to_seconds(7, 0, 0),
    DAY_HALF: hms_to_seconds(4, 0, 0),
}
# Break allowance for Team Member
MEMBER_BREAK_TARGET = hms_to_seconds(1, 30, 0)


# ── Threshold helpers ──────────────────────────────────────────────────────────

def member_threshold_seconds(day_type: str) -> int:
    return MEMBER_THRESHOLDS.get(day_type, MEMBER_THRESHOLDS[DAY_FULL])


def leader_threshold_seconds(day_type: str) -> int:
    return LEADER_THRESHOLDS.get(day_type, LEADER_THRESHOLDS[DAY_FULL])


def min_duration_from_first_entry(day_type: str, *, role: str) -> dt.timedelta:
    if role == "member":
        sec = member_threshold_seconds(day_type)
    else:
        sec = leader_threshold_seconds(day_type)
    return dt.timedelta(seconds=sec)


def format_logout_at_display(first_entry: dt.datetime, deadline: dt.datetime) -> str:
    """12hr format; adds date if logout rolls past first-entry calendar day."""
    if deadline.date() == first_entry.date():
        return deadline.strftime("%I:%M %p").lstrip("0")
    return deadline.strftime("%d-%b %I:%M %p").lstrip("0")


def render_logout_eligibility_status(
    first_entry: dt.datetime, deadline: dt.datetime, now: dt.datetime
) -> None:
    _uname = get_first_name()
    st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)
    if now < deadline:
        at = format_logout_at_display(first_entry, deadline)
        st.info(f"🎯 Earliest Logout at :- **{at}**")
    else:
        # Fallback: if first name empty, try full stored name
        _display = _uname or st.session_state.get("signup_user_name", "").strip().split()[0].capitalize() if st.session_state.get("signup_user_name", "").strip() else ""
        name_part = f", <span style='color:#86efac;font-weight:800;letter-spacing:0.02em;'>{_display}</span>" if _display else ""
        name_txt = f", {_uname}" if _uname else ""
        st.markdown(
            f'''<div style="
                background: linear-gradient(135deg, #14532d 0%, #166534 40%, #15803d 80%, #16a34a 100%);
                padding: 18px 24px;
                border-radius: 14px;
                border: 1px solid rgba(74,222,128,0.45);
                font-weight: 700;
                font-size: 1.13rem;
                text-align: center;
                box-shadow: 0 0 0 1px rgba(255,255,255,0.06) inset,
                            0 12px 36px rgba(22,163,74,0.35),
                            0 4px 12px rgba(0,0,0,0.3);
                position: relative;
                overflow: hidden;
                margin-bottom: 1.2rem;
            ">
            <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(255,255,255,0.07) 0%,transparent 55%);border-radius:14px;pointer-events:none;"></div>
            <p style="margin:0;padding:0;color:#ffffff;-webkit-text-fill-color:#ffffff;text-shadow:0 7px 4px rgba(0,0,0,0.4);letter-spacing:0.015em;">
                🎉 Target Completed<span style="color:#86efac;-webkit-text-fill-color:#86efac;font-weight:900;">{name_txt}</span>! You're Free to Log out anytime · no restrictions!!
            </p>
            </div>''',
            unsafe_allow_html=True,
        )


def render_summary(result: dict) -> None:
    """Human-readable work & break summary box."""
    total_work = result["total_work"] + result["ongoing_work"]
    total_break = result["total_break"]
    total_time = total_work + total_break
    num_breaks = len(result["break_sessions"])
    break_label = f"{num_breaks} break{'s' if num_breaks != 1 else ''} taken"

    st.markdown(
        f"""
        <div class="entryexit-summary-box">
            🕐 &nbsp;<b>Work Time:</b> {format_human(total_work)}<br>
            ☕ &nbsp;<b>Break Time:</b> {format_human(total_break)}
            &nbsp;<span style="opacity:0.6;font-size:0.88em;">({break_label})</span><br>
            📊 &nbsp;<b>Total Time in office:</b> {format_human(total_time)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_session_panel(result: dict) -> None:
    """Premium side-by-side work & break session breakdown."""
    work_data = result.get("work_sessions_data", [])
    break_data = result.get("break_sessions_data", [])

    def work_rows_html() -> str:
        if not work_data:
            return '<div class="ee-row"><span class="ee-row-label" style="opacity:0.45">No sessions yet</span></div>'
        rows = []
        for i, s in enumerate(work_data, 1):
            ongoing_badge = '<span class="ee-ongoing-badge">LIVE</span>' if s.get("ongoing") else ""
            rows.append(
                f'<div class="ee-row">'
                f'<span class="ee-row-label">Session {i}</span>'
                f'<span class="ee-row-range">{s["start"]} → {s["end"]}{ongoing_badge}</span>'
                f'<span class="ee-row-dur work">{s["human"]}</span>'
                f'</div>'
            )
        return "".join(rows)

    def break_rows_html() -> str:
        if not break_data:
            return '<div class="ee-row"><span class="ee-row-label" style="opacity:0.45">No breaks yet</span></div>'
        rows = []
        for i, s in enumerate(break_data, 1):
            rows.append(
                f'<div class="ee-row">'
                f'<span class="ee-row-label">Break {i}</span>'
                f'<span class="ee-row-range">{s["start"]} → {s["end"]}</span>'
                f'<span class="ee-row-dur brk">{s["human"]}</span>'
                f'</div>'
            )
        return "".join(rows)

    st.markdown(
        f"""
        <div class="ee-session-panel">
            <div class="ee-session-col work">
                <div class="ee-col-header work">
                    🕐 Work Sessions
                    <span class="ee-col-count">{len(work_data)}</span>
                </div>
                {work_rows_html()}
            </div>
            <div class="ee-session-col brk">
                <div class="ee-col-header brk">
                    ☕ Break Sessions
                    <span class="ee-col-count">{len(break_data)}</span>
                </div>
                {break_rows_html()}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Dashboard renderers ────────────────────────────────────────────────────────

def render_team_member_dashboard(
    result: dict,
    day_type: str,
    first_entry: dt.datetime,
    now: dt.datetime,
) -> None:
    """Team Member: logout when net work time (excluding breaks) >= threshold."""
    required_work_secs = member_threshold_seconds(day_type)
    total_work = result["total_work"] + result["ongoing_work"]
    total_break = result["total_break"]
    total_logged = total_work + total_break
    remaining_work = max(required_work_secs - total_work, 0)
    deadline = now + dt.timedelta(seconds=remaining_work)
    remaining_break = max(MEMBER_BREAK_TARGET - total_break, 0)

    st.markdown(
        f'<div class="ee-info-pill" style="'
        f'font-size:0.80rem;letter-spacing:0.03em;'
        f'padding:0.45rem 0.85rem;border-radius:8px;margin-bottom:0.2rem;'
        f'background:rgba(212,175,114,0.10);'
        f'border:1px solid rgba(212,175,114,0.22);'
        f'display:inline-block;">'
        f'👤&nbsp; <b>Team Member</b>&ensp;·&ensp;{day_type}'
        f'&ensp;·&ensp;Clocked in at&nbsp;<b>{first_entry.strftime("%I:%M %p").lstrip("0")}</b>'
        f'&nbsp;on&nbsp;{first_entry.strftime("%d %b %Y")}'
        f'&ensp;·&ensp;Earliest logout&nbsp;<b>{format_logout_at_display(first_entry, deadline)}</b>'
        f'</div>',
        unsafe_allow_html=True,
    )

    render_logout_eligibility_status(first_entry, deadline, now)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Work Time", format_clock(total_work))
    c2.metric("Total Break Time", format_clock(total_break))
    c3.metric("Total Logged Time", format_clock(total_logged))
    c4.metric("Remaining Work", format_clock(remaining_work) if remaining_work > 0 else "—")
    c5.metric("Remaining Break", format_clock(remaining_break) if remaining_break > 0 else "—")

    if result["ongoing_work_text"]:
        label = "▲ Hide session breakdown" if st.session_state.member_session_panel_open else "▼ Active work session — tap to see breakdown"
        if st.button(label, key="btn_member_session_toggle", use_container_width=True):
            st.session_state.member_session_panel_open = not st.session_state.member_session_panel_open
        if st.session_state.member_session_panel_open:
            render_session_panel(result)


def render_team_leader_dashboard(
    result: dict,
    day_type: str,
    first_entry: dt.datetime,
    now: dt.datetime,
) -> None:
    """Team Leader: logout when net work time (excluding breaks) >= threshold."""
    required_work_secs = leader_threshold_seconds(day_type)
    total_work = result["total_work"] + result["ongoing_work"]
    total_break = result["total_break"]
    total_time = total_work + total_break
    remaining_work = max(required_work_secs - total_work, 0)
    deadline = now + dt.timedelta(seconds=remaining_work)
    remaining_break = max(MEMBER_BREAK_TARGET - total_break, 0)

    st.markdown(
        f'<div class="ee-info-pill" style="'
        f'font-size:0.80rem;letter-spacing:0.03em;'
        f'padding:0.45rem 0.85rem;border-radius:8px;margin-bottom:0.2rem;'
        f'background:rgba(212,175,114,0.10);'
        f'border:1px solid rgba(212,175,114,0.22);'
        f'display:inline-block;">'
        f'👑&nbsp; <b>Team Leader</b>&ensp;·&ensp;{day_type}'
        f'&ensp;·&ensp;Clocked in at&nbsp;<b>{first_entry.strftime("%I:%M %p").lstrip("0")}</b>'
        f'&nbsp;on&nbsp;{first_entry.strftime("%d %b %Y")}'
        f'&ensp;·&ensp;Earliest logout&nbsp;<b>{format_logout_at_display(first_entry, deadline)}</b>'
        f'</div>',
        unsafe_allow_html=True,
    )

    render_logout_eligibility_status(first_entry, deadline, now)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Work (login) Time", format_clock(total_work))
    c2.metric("Total Break Time", format_clock(total_break))
    c3.metric("Total Time", format_clock(total_time))
    c4.metric("Remaining Work", format_clock(remaining_work) if remaining_work > 0 else "—")
    c5.metric("Remaining Break", format_clock(remaining_break) if remaining_break > 0 else "—")

    if result["ongoing_work_text"]:
        label = "▲ Hide session breakdown" if st.session_state.leader_session_panel_open else "▼ Active work session — tap to see breakdown"
        if st.button(label, key="btn_leader_session_toggle", use_container_width=True):
            st.session_state.leader_session_panel_open = not st.session_state.leader_session_panel_open
        if st.session_state.leader_session_panel_open:
            render_session_panel(result)


# ── Parsing ────────────────────────────────────────────────────────────────────

def extract_times(log_text: str) -> list[dt.datetime]:
    matches = re.findall(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b", log_text)
    now = now_pune()
    current_day = now.date()
    points: list[dt.datetime] = []
    last_dt = None

    for i, item in enumerate(matches):
        hh, mm = map(int, item.split(":"))
        candidate = dt.datetime.combine(current_day, dt.time(hh, mm))
        if last_dt and candidate < last_dt:
            # sequence rolled over midnight — advance day
            current_day += dt.timedelta(days=1)
            candidate = dt.datetime.combine(current_day, dt.time(hh, mm))
        # First punch: if it lands in the future (e.g. 12:00 but now is 05:54)
        # it belongs to yesterday
        if i == 0 and candidate > now:
            current_day -= dt.timedelta(days=1)
            candidate = dt.datetime.combine(current_day, dt.time(hh, mm))
        points.append(candidate)
        last_dt = candidate

    return points


@st.cache_data(show_spinner=False)
def normalize_paste_text(raw: str) -> str:
    return (raw or "").replace("\r\n", "\n")


def fresh_parse_biometric_log(log_text: str) -> tuple[dt.datetime, ...] | None:
    pts = extract_times(log_text)
    if len(pts) < 1:
        return None
    return tuple(pts)


def summarize_sessions(
    time_points: list[dt.datetime], current_time: dt.datetime | None = None
) -> dict:
    work_sessions: list[str] = []
    break_sessions: list[str] = []
    work_sessions_data: list[dict] = []
    break_sessions_data: list[dict] = []
    total_work = 0
    total_break = 0
    ongoing_work = 0
    ongoing_work_text = None

    for idx in range(len(time_points) - 1):
        start_dt = time_points[idx]
        end_dt = time_points[idx + 1]
        seconds = round((end_dt - start_dt).total_seconds())
        session_text = (
            f"{start_dt.strftime('%Y-%m-%d %H:%M')} -> "
            f"{end_dt.strftime('%Y-%m-%d %H:%M')} - {format_short(seconds)}"
        )
        session_data = {
            "start": start_dt.strftime("%d-%b %H:%M"),
            "end": end_dt.strftime("%d-%b %H:%M"),
            "seconds": seconds,
            "human": format_human(seconds),
        }
        if idx % 2 == 0:
            work_sessions.append(session_text)
            work_sessions_data.append(session_data)
            total_work += seconds
        else:
            break_sessions.append(session_text)
            break_sessions_data.append(session_data)
            total_break += seconds

    # Odd number of punches = active work session ongoing
    if len(time_points) % 2 == 1:
        current_time = current_time or now_pune()
        if current_time < time_points[-1]:
            current_time += dt.timedelta(days=1)
        ongoing_work = round((current_time - time_points[-1]).total_seconds())
        ongoing_work_text = (
            f"{time_points[-1].strftime('%Y-%m-%d %H:%M')} -> "
            f"{current_time.strftime('%Y-%m-%d %H:%M')} - {format_short(ongoing_work)} "
            "(ongoing)"
        )
        work_sessions_data.append({
            "start": time_points[-1].strftime("%d-%b %H:%M"),
            "end": current_time.strftime("%d-%b %H:%M"),
            "seconds": ongoing_work,
            "human": format_human(ongoing_work),
            "ongoing": True,
        })

    return {
        "work_sessions": work_sessions,
        "break_sessions": break_sessions,
        "work_sessions_data": work_sessions_data,
        "break_sessions_data": break_sessions_data,
        "total_work": total_work,
        "total_break": total_break,
        "ongoing_work": max(ongoing_work, 0),
        "ongoing_work_text": ongoing_work_text,
    }


# ── Session state persistence ──────────────────────────────────────────────────

def persist_member_day_query() -> None:
    st.session_state.member_day_type = st.session_state[MEMBER_DAY_WIDGET_KEY]
    st.query_params[MEMBER_DAY_QUERY] = st.session_state.member_day_type


def persist_leader_day_query() -> None:
    st.session_state.leader_day_type = st.session_state[LEADER_DAY_WIDGET_KEY]
    st.query_params[LEADER_DAY_QUERY] = st.session_state.leader_day_type


# ── Live dashboard fragments (auto-refresh every 30s) ─────────────────────────
# Biometric punches are minute-resolution only, so refreshing every 30s is
# sufficient — no new information changes faster than once per minute, and
# sub-minute drift was causing the displayed timer to visually race past
# pay-threshold boundaries (e.g. half-day cutoff) before they were truly reached.

@st.fragment(run_every="1s")
def member_live_dashboard() -> None:
    pts = st.session_state.get("member_biometric_points")
    if not pts:
        return
    now = now_pune()
    result = summarize_sessions(pts, current_time=now)
    day_type = st.session_state.get(MEMBER_DAY_WIDGET_KEY, st.session_state.member_day_type)
    render_team_member_dashboard(result, day_type, pts[0], now)


@st.fragment(run_every="1s")
def leader_live_dashboard() -> None:
    pts = st.session_state.get("leader_biometric_points")
    if not pts:
        return
    now = now_pune()
    result = summarize_sessions(pts, current_time=now)
    day_type = st.session_state.get(LEADER_DAY_WIDGET_KEY, st.session_state.leader_day_type)
    render_team_leader_dashboard(result, day_type, pts[0], now)


# ── Initialise session state ───────────────────────────────────────────────────



if "member_day_type" not in st.session_state:
    mq = st.query_params.get(MEMBER_DAY_QUERY)
    st.session_state.member_day_type = mq if mq in DAY_TYPE_OPTIONS else DAY_FULL

if "leader_day_type" not in st.session_state:
    lq = st.query_params.get(LEADER_DAY_QUERY)
    st.session_state.leader_day_type = lq if lq in DAY_TYPE_OPTIONS else DAY_FULL

if "member_biometric_points" not in st.session_state:
    st.session_state.member_biometric_points = None

if "leader_biometric_points" not in st.session_state:
    st.session_state.leader_biometric_points = None

if "member_session_panel_open" not in st.session_state:
    st.session_state.member_session_panel_open = False

if "leader_session_panel_open" not in st.session_state:
    st.session_state.leader_session_panel_open = False

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "light"


# ── Page layout ───────────────────────────────────────────────────────────────

# Premium inline SVG clock icon (no external file dependency)
CLOCK_SVG = """
<svg width="54" height="54" viewBox="0 0 54 54" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="faceGrad" cx="50%" cy="38%" r="55%">
      <stop offset="0%" stop-color="#f5e6c8"/>
      <stop offset="100%" stop-color="#c9a96e"/>
    </radialGradient>
    <radialGradient id="rimGrad" cx="50%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#e8c97a"/>
      <stop offset="60%" stop-color="#b8892a"/>
      <stop offset="100%" stop-color="#7a5510"/>
    </radialGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#00000055"/>
    </filter>
  </defs>
  <!-- Outer gold rim -->
  <circle cx="27" cy="27" r="26" fill="url(#rimGrad)" filter="url(#shadow)"/>
  <!-- Inner highlight ring -->
  <circle cx="27" cy="27" r="22.5" fill="none" stroke="#f0d080" stroke-width="0.7" opacity="0.5"/>
  <!-- Clock face -->
  <circle cx="27" cy="27" r="21" fill="url(#faceGrad)"/>
  <!-- Hour markers -->
  <g stroke="#7a5510" stroke-width="1.5" stroke-linecap="round">
    <line x1="27" y1="8"  x2="27" y2="11"/>
    <line x1="27" y1="43" x2="27" y2="46"/>
    <line x1="8"  y1="27" x2="11" y2="27"/>
    <line x1="43" y1="27" x2="46" y2="27"/>
  </g>
  <!-- Minor tick marks -->
  <g stroke="#b8892a" stroke-width="0.8" stroke-linecap="round" opacity="0.6">
    <line x1="35.5" y1="9.6"  x2="34.2" y2="11.9"/>
    <line x1="18.5" y1="9.6"  x2="19.8" y2="11.9"/>
    <line x1="44.4" y1="18.5" x2="42.1" y2="19.8"/>
    <line x1="44.4" y1="35.5" x2="42.1" y2="34.2"/>
    <line x1="35.5" y1="44.4" x2="34.2" y2="42.1"/>
    <line x1="18.5" y1="44.4" x2="19.8" y2="42.1"/>
    <line x1="9.6"  y1="35.5" x2="11.9" y2="34.2"/>
    <line x1="9.6"  y1="18.5" x2="11.9" y2="19.8"/>
  </g>
  <!-- Hour hand (pointing ~10) -->
  <line x1="27" y1="27" x2="19.5" y2="16" stroke="#3b2a0e" stroke-width="2.4" stroke-linecap="round"/>
  <!-- Minute hand (pointing ~2) -->
  <line x1="27" y1="27" x2="36"   y2="17" stroke="#3b2a0e" stroke-width="1.6" stroke-linecap="round"/>
  <!-- Second hand -->
  <line x1="27" y1="27" x2="30"   y2="40" stroke="#c0392b" stroke-width="1" stroke-linecap="round"/>
  <!-- Center jewel -->
  <circle cx="27" cy="27" r="2.2" fill="#7a5510"/>
  <circle cx="27" cy="27" r="1.1" fill="#f0d080"/>
</svg>
"""

# Theme-aware CSS injection
_tm = st.session_state.theme_mode
_is_dark = _tm == "dark"

# ── Botanical SVG wallpaper patterns ─────────────────────────────────────────
# Dark: deep indigo/violet leaves (like the reference image)
# Light: soft sage/mint botanical illustration
DARK_BG_SVG = """url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22600%22%20height%3D%22600%22%3E%0A%3Crect%20width%3D%22600%22%20height%3D%22600%22%20fill%3D%22%23605B51%22%2F%3E%0A%3Cstyle%3E.la%7Bfill%3A%233a3428%3Bstroke%3A%23d4af72%3Bstroke-width%3A1.0%3Bstroke-opacity%3A0.58%7D.lb%7Bfill%3A%232e2a22%3Bstroke%3A%23d4af72%3Bstroke-width%3A1.0%3Bstroke-opacity%3A0.52%7D.lc%7Bfill%3A%2346403a%3Bstroke%3A%23d4af72%3Bstroke-width%3A1.0%3Bstroke-opacity%3A0.55%7D.v%7Bstroke%3A%23c9a84c%3Bstroke-width%3A0.9%3Bfill%3Anone%3Bopacity%3A0.65%7D.v2%7Bstroke%3A%23b8922a%3Bstroke-width%3A0.55%3Bfill%3Anone%3Bopacity%3A0.48%7D%3C%2Fstyle%3E%0A%3Cg%20transform%3D%22translate%28120%2C170%29%20rotate%28-42%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C12%2C-55%2052%2C-85%2072%2C-88%20C90%2C-90%20105%2C-75%2095%2C-45%20C82%2C-10%2045%2C18%200%2C0%20Z%22%20class%3D%22la%22%20opacity%3D%220.82%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C12%2C-55%2052%2C-85%2072%2C-88%20C90%2C-90%20105%2C-75%2095%2C-45%20C82%2C-10%2045%2C18%200%2C0%20Z%22%20fill%3D%22none%22%20stroke%3D%22%235a5040%22%20stroke-width%3D%220.6%22%20opacity%3D%220.5%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C30%2C-44%2065%2C-68%2095%2C-45%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M20%2C-18%20C32%2C-36%2050%2C-50%2070%2C-56%22%20class%3D%22v2%22%2F%3E%3Cpath%20d%3D%22M40%2C-35%20C46%2C-44%2055%2C-52%2064%2C-57%22%20class%3D%22v2%22%2F%3E%3Cpath%20d%3D%22M15%2C-12%20C20%2C-24%2028%2C-36%2038%2C-42%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%2882%2C128%29%20rotate%28-20%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C8%2C-40%2038%2C-68%2060%2C-70%20C76%2C-71%2088%2C-58%2080%2C-32%20C70%2C-5%2035%2C14%200%2C0%20Z%22%20class%3D%22lb%22%20opacity%3D%220.70%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C20%2C-34%2050%2C-55%2080%2C-32%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M18%2C-14%20C25%2C-28%2038%2C-42%2055%2C-50%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28148%2C230%29%20rotate%28-58%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C10%2C-48%2045%2C-76%2068%2C-78%20C88%2C-80%20100%2C-65%2090%2C-38%20C78%2C-8%2042%2C20%200%2C0%20Z%22%20class%3D%22lc%22%20opacity%3D%220.75%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C25%2C-40%2058%2C-62%2090%2C-38%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M22%2C-20%20C30%2C-34%2045%2C-50%2062%2C-60%22%20class%3D%22v2%22%2F%3E%3Cpath%20d%3D%22M12%2C-10%20C16%2C-22%2024%2C-34%2036%2C-42%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28480%2C195%29%20rotate%2838%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-10%2C-52%20-48%2C-82%20-70%2C-84%20C-88%2C-86%20-102%2C-70%20-92%2C-42%20C-80%2C-10%20-44%2C20%200%2C0%20Z%22%20class%3D%22la%22%20opacity%3D%220.78%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-22%2C-42%20-60%2C-65%20-92%2C-42%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M-20%2C-18%20C-30%2C-34%20-46%2C-50%20-62%2C-58%22%20class%3D%22v2%22%2F%3E%3Cpath%20d%3D%22M-38%2C-36%20C-44%2C-46%20-54%2C-56%20-64%2C-62%22%20class%3D%22v2%22%2F%3E%3Cpath%20d%3D%22M-12%2C-10%20C-18%2C-24%20-28%2C-36%20-40%2C-44%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28510%2C255%29%20rotate%2854%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-8%2C-38%20-40%2C-64%20-60%2C-66%20C-76%2C-68%20-86%2C-54%20-78%2C-30%20C-68%2C-4%20-36%2C16%200%2C0%20Z%22%20class%3D%22lb%22%20opacity%3D%220.65%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-20%2C-32%20-50%2C-52%20-78%2C-30%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M-18%2C-14%20C-26%2C-26%20-40%2C-40%20-55%2C-48%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28448%2C145%29%20rotate%2822%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-6%2C-34%20-36%2C-58%20-54%2C-60%20C-68%2C-62%20-78%2C-50%20-70%2C-28%20C-60%2C-4%20-30%2C14%200%2C0%20Z%22%20class%3D%22lc%22%20opacity%3D%220.60%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-18%2C-28%20-44%2C-48%20-70%2C-28%22%20class%3D%22v%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28295%2C440%29%20rotate%28-8%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-14%2C-58%20-56%2C-88%20-82%2C-90%20C-104%2C-92%20-118%2C-74%20-106%2C-44%20C-92%2C-10%20-50%2C24%200%2C0%20Z%22%20class%3D%22la%22%20opacity%3D%220.80%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-30%2C-48%20-70%2C-72%20-106%2C-44%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M-25%2C-22%20C-36%2C-40%20-54%2C-58%20-72%2C-68%22%20class%3D%22v2%22%2F%3E%3Cpath%20d%3D%22M-48%2C-44%20C-56%2C-54%20-66%2C-64%20-76%2C-70%22%20class%3D%22v2%22%2F%3E%3Cpath%20d%3D%22M-15%2C-14%20C-20%2C-28%20-30%2C-44%20-44%2C-54%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28340%2C492%29%20rotate%2818%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C10%2C-50%2046%2C-78%2068%2C-80%20C86%2C-82%20100%2C-66%2088%2C-38%20C76%2C-8%2040%2C22%200%2C0%20Z%22%20class%3D%22lb%22%20opacity%3D%220.72%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C22%2C-42%2058%2C-64%2088%2C-38%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M20%2C-18%20C28%2C-34%2044%2C-52%2062%2C-62%22%20class%3D%22v2%22%2F%3E%3Cpath%20d%3D%22M10%2C-10%20C14%2C-22%2022%2C-34%2034%2C-42%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28238%2C488%29%20rotate%28-32%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-8%2C-44%20-44%2C-72%20-64%2C-74%20C-80%2C-76%20-92%2C-62%20-82%2C-36%20C-70%2C-8%20-38%2C18%200%2C0%20Z%22%20class%3D%22lc%22%20opacity%3D%220.68%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-22%2C-36%20-54%2C-58%20-82%2C-36%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M-20%2C-16%20C-28%2C-30%20-42%2C-46%20-58%2C-55%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28300%2C128%29%20rotate%2810%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-12%2C-52%20-50%2C-80%20-74%2C-82%20C-94%2C-84%20-108%2C-68%20-96%2C-40%20C-82%2C-8%20-44%2C22%200%2C0%20Z%22%20class%3D%22la%22%20opacity%3D%220.72%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-28%2C-44%20-64%2C-66%20-96%2C-40%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M-24%2C-20%20C-34%2C-38%20-52%2C-56%20-70%2C-66%22%20class%3D%22v2%22%2F%3E%3Cpath%20d%3D%22M-14%2C-12%20C-20%2C-26%20-30%2C-40%20-44%2C-50%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28258%2C90%29%20rotate%28-14%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-8%2C-36%20-40%2C-62%20-60%2C-64%20C-76%2C-66%20-86%2C-52%20-76%2C-28%20C-66%2C-4%20-34%2C16%200%2C0%20Z%22%20class%3D%22lb%22%20opacity%3D%220.58%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-20%2C-30%20-48%2C-50%20-76%2C-28%22%20class%3D%22v%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28348%2C98%29%20rotate%2826%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C10%2C-38%2042%2C-64%2062%2C-66%20C78%2C-68%2088%2C-54%2080%2C-30%20C70%2C-5%2036%2C16%200%2C0%20Z%22%20class%3D%22lc%22%20opacity%3D%220.56%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C20%2C-32%2050%2C-52%2080%2C-30%22%20class%3D%22v%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28720%2C170%29%20rotate%28-42%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C12%2C-55%2052%2C-85%2072%2C-88%20C90%2C-90%20105%2C-75%2095%2C-45%20C82%2C-10%2045%2C18%200%2C0%20Z%22%20class%3D%22la%22%20opacity%3D%220.82%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C30%2C-44%2065%2C-68%2095%2C-45%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M20%2C-18%20C32%2C-36%2050%2C-50%2070%2C-56%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28682%2C128%29%20rotate%28-20%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C8%2C-40%2038%2C-68%2060%2C-70%20C76%2C-71%2088%2C-58%2080%2C-32%20C70%2C-5%2035%2C14%200%2C0%20Z%22%20class%3D%22lb%22%20opacity%3D%220.70%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C20%2C-34%2050%2C-55%2080%2C-32%22%20class%3D%22v%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28748%2C230%29%20rotate%28-58%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C10%2C-48%2045%2C-76%2068%2C-78%20C88%2C-80%20100%2C-65%2090%2C-38%20C78%2C-8%2042%2C20%200%2C0%20Z%22%20class%3D%22lc%22%20opacity%3D%220.75%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C25%2C-40%2058%2C-62%2090%2C-38%22%20class%3D%22v%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28-120%2C195%29%20rotate%2838%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-10%2C-52%20-48%2C-82%20-70%2C-84%20C-88%2C-86%20-102%2C-70%20-92%2C-42%20C-80%2C-10%20-44%2C20%200%2C0%20Z%22%20class%3D%22la%22%20opacity%3D%220.78%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-22%2C-42%20-60%2C-65%20-92%2C-42%22%20class%3D%22v%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28-90%2C255%29%20rotate%2854%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-8%2C-38%20-40%2C-64%20-60%2C-66%20C-76%2C-68%20-86%2C-54%20-78%2C-30%20C-68%2C-4%20-36%2C16%200%2C0%20Z%22%20class%3D%22lb%22%20opacity%3D%220.65%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-20%2C-32%20-50%2C-52%20-78%2C-30%22%20class%3D%22v%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28295%2C-160%29%20rotate%28-8%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-14%2C-58%20-56%2C-88%20-82%2C-90%20C-104%2C-92%20-118%2C-74%20-106%2C-44%20C-92%2C-10%20-50%2C24%200%2C0%20Z%22%20class%3D%22la%22%20opacity%3D%220.80%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-30%2C-48%20-70%2C-72%20-106%2C-44%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M-25%2C-22%20C-36%2C-40%20-54%2C-58%20-72%2C-68%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28340%2C-108%29%20rotate%2818%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C10%2C-50%2046%2C-78%2068%2C-80%20C86%2C-82%20100%2C-66%2088%2C-38%20C76%2C-8%2040%2C22%200%2C0%20Z%22%20class%3D%22lb%22%20opacity%3D%220.72%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C22%2C-42%2058%2C-64%2088%2C-38%22%20class%3D%22v%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28300%2C728%29%20rotate%2810%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-12%2C-52%20-50%2C-80%20-74%2C-82%20C-94%2C-84%20-108%2C-68%20-96%2C-40%20C-82%2C-8%20-44%2C22%200%2C0%20Z%22%20class%3D%22la%22%20opacity%3D%220.72%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-28%2C-44%20-64%2C-66%20-96%2C-40%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M-24%2C-20%20C-34%2C-38%20-52%2C-56%20-70%2C-66%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28258%2C690%29%20rotate%28-14%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-8%2C-36%20-40%2C-62%20-60%2C-64%20C-76%2C-66%20-86%2C-52%20-76%2C-28%20C-66%2C-4%20-34%2C16%200%2C0%20Z%22%20class%3D%22lb%22%20opacity%3D%220.58%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-20%2C-30%20-48%2C-50%20-76%2C-28%22%20class%3D%22v%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28348%2C698%29%20rotate%2826%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C10%2C-38%2042%2C-64%2062%2C-66%20C78%2C-68%2088%2C-54%2080%2C-30%20C70%2C-5%2036%2C16%200%2C0%20Z%22%20class%3D%22lc%22%20opacity%3D%220.56%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C20%2C-32%2050%2C-52%2080%2C-30%22%20class%3D%22v%22%2F%3E%3C%2Fg%3E%0A%3C%2Fsvg%3E")"""

LIGHT_BG_SVG = """url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22600%22%20height%3D%22600%22%3E%0A%3Crect%20width%3D%22600%22%20height%3D%22600%22%20fill%3D%22%23F6F4E8%22%2F%3E%0A%3Cstyle%3E.la%7Bfill%3A%236abf8a%3Bstroke%3A%23c9a030%3Bstroke-width%3A0.85%3Bstroke-opacity%3A0.50%7D.lb%7Bfill%3A%2386c9a0%3Bstroke%3A%23c9a030%3Bstroke-width%3A0.85%3Bstroke-opacity%3A0.45%7D.lc%7Bfill%3A%234caf78%3Bstroke%3A%23c9a030%3Bstroke-width%3A0.85%3Bstroke-opacity%3A0.48%7D.v%7Bstroke%3A%23a07820%3Bstroke-width%3A0.85%3Bfill%3Anone%3Bopacity%3A0.42%7D.v2%7Bstroke%3A%238a6818%3Bstroke-width%3A0.55%3Bfill%3Anone%3Bopacity%3A0.32%7D%3C%2Fstyle%3E%0A%3Cg%20transform%3D%22translate%28120%2C170%29%20rotate%28-42%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C12%2C-55%2052%2C-85%2072%2C-88%20C90%2C-90%20105%2C-75%2095%2C-45%20C82%2C-10%2045%2C18%200%2C0%20Z%22%20class%3D%22la%22%20opacity%3D%220.42%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C12%2C-55%2052%2C-85%2072%2C-88%20C90%2C-90%20105%2C-75%2095%2C-45%20C82%2C-10%2045%2C18%200%2C0%20Z%22%20fill%3D%22none%22%20stroke%3D%22%233a9060%22%20stroke-width%3D%220.6%22%20opacity%3D%220.26%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C30%2C-44%2065%2C-68%2095%2C-45%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M20%2C-18%20C32%2C-36%2050%2C-50%2070%2C-56%22%20class%3D%22v2%22%2F%3E%3Cpath%20d%3D%22M40%2C-35%20C46%2C-44%2055%2C-52%2064%2C-57%22%20class%3D%22v2%22%2F%3E%3Cpath%20d%3D%22M15%2C-12%20C20%2C-24%2028%2C-36%2038%2C-42%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%2882%2C128%29%20rotate%28-20%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C8%2C-40%2038%2C-68%2060%2C-70%20C76%2C-71%2088%2C-58%2080%2C-32%20C70%2C-5%2035%2C14%200%2C0%20Z%22%20class%3D%22lb%22%20opacity%3D%220.36%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C20%2C-34%2050%2C-55%2080%2C-32%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M18%2C-14%20C25%2C-28%2038%2C-42%2055%2C-50%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28148%2C230%29%20rotate%28-58%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C10%2C-48%2045%2C-76%2068%2C-78%20C88%2C-80%20100%2C-65%2090%2C-38%20C78%2C-8%2042%2C20%200%2C0%20Z%22%20class%3D%22lc%22%20opacity%3D%220.39%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C25%2C-40%2058%2C-62%2090%2C-38%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M22%2C-20%20C30%2C-34%2045%2C-50%2062%2C-60%22%20class%3D%22v2%22%2F%3E%3Cpath%20d%3D%22M12%2C-10%20C16%2C-22%2024%2C-34%2036%2C-42%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28480%2C195%29%20rotate%2838%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-10%2C-52%20-48%2C-82%20-70%2C-84%20C-88%2C-86%20-102%2C-70%20-92%2C-42%20C-80%2C-10%20-44%2C20%200%2C0%20Z%22%20class%3D%22la%22%20opacity%3D%220.41%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-22%2C-42%20-60%2C-65%20-92%2C-42%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M-20%2C-18%20C-30%2C-34%20-46%2C-50%20-62%2C-58%22%20class%3D%22v2%22%2F%3E%3Cpath%20d%3D%22M-38%2C-36%20C-44%2C-46%20-54%2C-56%20-64%2C-62%22%20class%3D%22v2%22%2F%3E%3Cpath%20d%3D%22M-12%2C-10%20C-18%2C-24%20-28%2C-36%20-40%2C-44%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28510%2C255%29%20rotate%2854%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-8%2C-38%20-40%2C-64%20-60%2C-66%20C-76%2C-68%20-86%2C-54%20-78%2C-30%20C-68%2C-4%20-36%2C16%200%2C0%20Z%22%20class%3D%22lb%22%20opacity%3D%220.34%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-20%2C-32%20-50%2C-52%20-78%2C-30%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M-18%2C-14%20C-26%2C-26%20-40%2C-40%20-55%2C-48%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28448%2C145%29%20rotate%2822%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-6%2C-34%20-36%2C-58%20-54%2C-60%20C-68%2C-62%20-78%2C-50%20-70%2C-28%20C-60%2C-4%20-30%2C14%200%2C0%20Z%22%20class%3D%22lc%22%20opacity%3D%220.31%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-18%2C-28%20-44%2C-48%20-70%2C-28%22%20class%3D%22v%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28295%2C440%29%20rotate%28-8%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-14%2C-58%20-56%2C-88%20-82%2C-90%20C-104%2C-92%20-118%2C-74%20-106%2C-44%20C-92%2C-10%20-50%2C24%200%2C0%20Z%22%20class%3D%22la%22%20opacity%3D%220.42%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-30%2C-48%20-70%2C-72%20-106%2C-44%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M-25%2C-22%20C-36%2C-40%20-54%2C-58%20-72%2C-68%22%20class%3D%22v2%22%2F%3E%3Cpath%20d%3D%22M-48%2C-44%20C-56%2C-54%20-66%2C-64%20-76%2C-70%22%20class%3D%22v2%22%2F%3E%3Cpath%20d%3D%22M-15%2C-14%20C-20%2C-28%20-30%2C-44%20-44%2C-54%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28340%2C492%29%20rotate%2818%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C10%2C-50%2046%2C-78%2068%2C-80%20C86%2C-82%20100%2C-66%2088%2C-38%20C76%2C-8%2040%2C22%200%2C0%20Z%22%20class%3D%22lb%22%20opacity%3D%220.37%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C22%2C-42%2058%2C-64%2088%2C-38%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M20%2C-18%20C28%2C-34%2044%2C-52%2062%2C-62%22%20class%3D%22v2%22%2F%3E%3Cpath%20d%3D%22M10%2C-10%20C14%2C-22%2022%2C-34%2034%2C-42%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28238%2C488%29%20rotate%28-32%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-8%2C-44%20-44%2C-72%20-64%2C-74%20C-80%2C-76%20-92%2C-62%20-82%2C-36%20C-70%2C-8%20-38%2C18%200%2C0%20Z%22%20class%3D%22lc%22%20opacity%3D%220.35%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-22%2C-36%20-54%2C-58%20-82%2C-36%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M-20%2C-16%20C-28%2C-30%20-42%2C-46%20-58%2C-55%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28300%2C128%29%20rotate%2810%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-12%2C-52%20-50%2C-80%20-74%2C-82%20C-94%2C-84%20-108%2C-68%20-96%2C-40%20C-82%2C-8%20-44%2C22%200%2C0%20Z%22%20class%3D%22la%22%20opacity%3D%220.37%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-28%2C-44%20-64%2C-66%20-96%2C-40%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M-24%2C-20%20C-34%2C-38%20-52%2C-56%20-70%2C-66%22%20class%3D%22v2%22%2F%3E%3Cpath%20d%3D%22M-14%2C-12%20C-20%2C-26%20-30%2C-40%20-44%2C-50%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28258%2C90%29%20rotate%28-14%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-8%2C-36%20-40%2C-62%20-60%2C-64%20C-76%2C-66%20-86%2C-52%20-76%2C-28%20C-66%2C-4%20-34%2C16%200%2C0%20Z%22%20class%3D%22lb%22%20opacity%3D%220.30%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-20%2C-30%20-48%2C-50%20-76%2C-28%22%20class%3D%22v%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28348%2C98%29%20rotate%2826%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C10%2C-38%2042%2C-64%2062%2C-66%20C78%2C-68%2088%2C-54%2080%2C-30%20C70%2C-5%2036%2C16%200%2C0%20Z%22%20class%3D%22lc%22%20opacity%3D%220.29%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C20%2C-32%2050%2C-52%2080%2C-30%22%20class%3D%22v%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28720%2C170%29%20rotate%28-42%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C12%2C-55%2052%2C-85%2072%2C-88%20C90%2C-90%20105%2C-75%2095%2C-45%20C82%2C-10%2045%2C18%200%2C0%20Z%22%20class%3D%22la%22%20opacity%3D%220.42%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C30%2C-44%2065%2C-68%2095%2C-45%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M20%2C-18%20C32%2C-36%2050%2C-50%2070%2C-56%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28682%2C128%29%20rotate%28-20%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C8%2C-40%2038%2C-68%2060%2C-70%20C76%2C-71%2088%2C-58%2080%2C-32%20C70%2C-5%2035%2C14%200%2C0%20Z%22%20class%3D%22lb%22%20opacity%3D%220.36%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C20%2C-34%2050%2C-55%2080%2C-32%22%20class%3D%22v%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28748%2C230%29%20rotate%28-58%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C10%2C-48%2045%2C-76%2068%2C-78%20C88%2C-80%20100%2C-65%2090%2C-38%20C78%2C-8%2042%2C20%200%2C0%20Z%22%20class%3D%22lc%22%20opacity%3D%220.39%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C25%2C-40%2058%2C-62%2090%2C-38%22%20class%3D%22v%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28-120%2C195%29%20rotate%2838%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-10%2C-52%20-48%2C-82%20-70%2C-84%20C-88%2C-86%20-102%2C-70%20-92%2C-42%20C-80%2C-10%20-44%2C20%200%2C0%20Z%22%20class%3D%22la%22%20opacity%3D%220.41%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-22%2C-42%20-60%2C-65%20-92%2C-42%22%20class%3D%22v%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28-90%2C255%29%20rotate%2854%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-8%2C-38%20-40%2C-64%20-60%2C-66%20C-76%2C-68%20-86%2C-54%20-78%2C-30%20C-68%2C-4%20-36%2C16%200%2C0%20Z%22%20class%3D%22lb%22%20opacity%3D%220.34%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-20%2C-32%20-50%2C-52%20-78%2C-30%22%20class%3D%22v%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28295%2C-160%29%20rotate%28-8%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-14%2C-58%20-56%2C-88%20-82%2C-90%20C-104%2C-92%20-118%2C-74%20-106%2C-44%20C-92%2C-10%20-50%2C24%200%2C0%20Z%22%20class%3D%22la%22%20opacity%3D%220.42%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-30%2C-48%20-70%2C-72%20-106%2C-44%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M-25%2C-22%20C-36%2C-40%20-54%2C-58%20-72%2C-68%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28340%2C-108%29%20rotate%2818%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C10%2C-50%2046%2C-78%2068%2C-80%20C86%2C-82%20100%2C-66%2088%2C-38%20C76%2C-8%2040%2C22%200%2C0%20Z%22%20class%3D%22lb%22%20opacity%3D%220.37%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C22%2C-42%2058%2C-64%2088%2C-38%22%20class%3D%22v%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28300%2C728%29%20rotate%2810%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-12%2C-52%20-50%2C-80%20-74%2C-82%20C-94%2C-84%20-108%2C-68%20-96%2C-40%20C-82%2C-8%20-44%2C22%200%2C0%20Z%22%20class%3D%22la%22%20opacity%3D%220.37%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-28%2C-44%20-64%2C-66%20-96%2C-40%22%20class%3D%22v%22%2F%3E%3Cpath%20d%3D%22M-24%2C-20%20C-34%2C-38%20-52%2C-56%20-70%2C-66%22%20class%3D%22v2%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28258%2C690%29%20rotate%28-14%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C-8%2C-36%20-40%2C-62%20-60%2C-64%20C-76%2C-66%20-86%2C-52%20-76%2C-28%20C-66%2C-4%20-34%2C16%200%2C0%20Z%22%20class%3D%22lb%22%20opacity%3D%220.30%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C-20%2C-30%20-48%2C-50%20-76%2C-28%22%20class%3D%22v%22%2F%3E%3C%2Fg%3E%0A%3Cg%20transform%3D%22translate%28348%2C698%29%20rotate%2826%29%22%3E%3Cpath%20d%3D%22M0%2C0%20C10%2C-38%2042%2C-64%2062%2C-66%20C78%2C-68%2088%2C-54%2080%2C-30%20C70%2C-5%2036%2C16%200%2C0%20Z%22%20class%3D%22lc%22%20opacity%3D%220.29%22%2F%3E%3Cpath%20d%3D%22M0%2C0%20C20%2C-32%2050%2C-52%2080%2C-30%22%20class%3D%22v%22%2F%3E%3C%2Fg%3E%0A%3C%2Fsvg%3E")"""

THEME_CSS = f"""
<style>
/* ── Wallpaper background ───────────────────────────────────────── */
.stApp {{
    background-image: {DARK_BG_SVG if _is_dark else LIGHT_BG_SVG} !important;
    background-size: 600px 600px !important;
    background-repeat: repeat !important;
    background-attachment: fixed !important;
}}

/* Frosted overlay so content stays readable */
.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    background: {"rgba(60,55,48,0.62)" if _is_dark else "rgba(246,244,232,0.78)"};
    pointer-events: none;
    z-index: 0;
}}

.block-container {{
    position: relative;
    z-index: 1;
}}

/* ── Typography — fully visible in both themes ──────────────────── */
html, body {{
    color-scheme: {"dark" if _is_dark else "light"} !important;
}}

h1, h2, h3, h4, h5, h6 {{
    color: {"#f5e6c8" if _is_dark else "#12200e"} !important;
    text-shadow: 0 1px 8px rgba(0,0,0,0.55) !important;
}}

[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {{
    color: {"#f5e6c8" if _is_dark else "#12200e"} !important;
    text-shadow: 0 1px 8px rgba(0,0,0,0.55) !important;
}}

/* General body text — broad but high-specificity */
p, span, div, label, .stMarkdown,
.stCaption {{
    color: {"#d8ccb8" if _is_dark else "#1e3a28"} !important;
}}

/* Streamlit markdown containers — all text inside */
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] div,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] strong,
[data-testid="stMarkdownContainer"] b,
[data-testid="stMarkdownContainer"] em {{
    color: {"#f0e8d8" if _is_dark else "#12200e"} !important;
}}

/* Caption text — solid black/white, always wins */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p,
[data-testid="stCaptionContainer"] span,
[data-testid="stCaptionContainer"] strong,
[data-testid="stCaptionContainer"] b,
[data-testid="stCaptionContainer"] * {{
    color: {"#ffffff" if _is_dark else "#000000"} !important;
    font-size: 14px !important;
}}

/* Bold/strong text in markdown */
[data-testid="stMarkdownContainer"] strong,
[data-testid="stMarkdownContainer"] b {{
    color: {"#faf0d8" if _is_dark else "#0a1a0e"} !important;
}}

/* Welcome line, Biometric log label, all stText */
.stText, .stText p,
[data-testid="stText"],
[data-testid="stText"] p {{
    color: {"#f0e8d8" if _is_dark else "#12200e"} !important;
}}

/* Metric labels & values */
div[data-testid="stMetricLabel"] > div,
div[data-testid="stMetricLabel"] label,
div[data-testid="stMetricLabel"] span {{
    color: {"#cfc0a0" if _is_dark else "#3a5a42"} !important;
    font-size: 0.78rem !important;
}}

div[data-testid="stMetricValue"] > div,
div[data-testid="stMetricValue"] span {{
    color: {"#f5e6c8" if _is_dark else "#12200e"} !important;
    font-weight: 800 !important;
    font-size: 1.5rem !important;
}}

/* ── Metric cards ───────────────────────────────────────────────── */
div[data-testid="stMetric"] {{
    background: {"linear-gradient(160deg,rgba(80,75,68,0.92) 0%,rgba(60,55,48,0.96) 100%)" if _is_dark else "linear-gradient(160deg,rgba(255,255,255,0.82) 0%,rgba(246,244,232,0.88) 100%)"} !important;
    border: {"1px solid rgba(148,137,121,0.30)" if _is_dark else "1px solid rgba(80,170,110,0.45)"} !important;
    box-shadow: {"0 8px 32px rgba(0,0,0,0.55),inset 0 1px 0 rgba(223,208,184,0.08)" if _is_dark else "0 8px 24px rgba(60,140,80,0.12),inset 0 1px 0 rgba(255,255,255,0.8)"} !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-radius: 16px !important;
}}

div[data-testid="stMetric"]::before {{
    background: {"linear-gradient(90deg,transparent,rgba(212,175,114,0.65),transparent)" if _is_dark else "linear-gradient(90deg,transparent,rgba(60,160,90,0.5),transparent)"} !important;
}}

/* ── Text areas ─────────────────────────────────────────────────── */
.stTextArea textarea {{
    background: {"rgba(50,46,40,0.95)" if _is_dark else "rgba(246,244,232,0.92)"} !important;
    border: {"1px solid rgba(180,165,135,0.45)" if _is_dark else "1px solid rgba(80,170,110,0.4)"} !important;
    color: {"#f5ead8" if _is_dark else "#12200e"} !important;
    backdrop-filter: blur(8px) !important;
    border-radius: 12px !important;
    font-size: 0.9rem !important;
}}

.stTextArea textarea::placeholder {{
    color: {"rgba(220,200,165,0.70)" if _is_dark else "rgba(20,80,40,0.55)"} !important;
    font-style: italic !important;
}}

/* ── Summary & session boxes ────────────────────────────────────── */
.entryexit-summary-box {{
    background: {"rgba(60,55,48,0.90)" if _is_dark else "rgba(246,244,232,0.85)"} !important;
    border-color: {"rgba(148,137,121,0.25)" if _is_dark else "rgba(80,170,110,0.4)"} !important;
    backdrop-filter: blur(10px) !important;
    color: {"#f0e0c8" if _is_dark else "#12200e"} !important;
}}

.entryexit-summary-box b {{
    color: {"#faf0d8" if _is_dark else "#0a1a0e"} !important;
}}

.ee-session-col {{
    background: {"rgba(60,55,48,0.90)" if _is_dark else "rgba(246,244,232,0.85)"} !important;
    border-color: {"rgba(148,137,121,0.25)" if _is_dark else "rgba(80,170,110,0.35)"} !important;
    backdrop-filter: blur(10px) !important;
}}

.ee-row-label, .ee-row-range {{
    color: {"rgba(230,210,175,0.90)" if _is_dark else "rgba(15,50,25,0.85)"} !important;
}}

/* ── Tabs ───────────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {{
    gap: 4px !important;
    border-bottom: {"1px solid rgba(212,175,114,0.20)" if _is_dark else "1px solid rgba(60,140,80,0.18)"} !important;
    background: transparent !important;
}}

[data-testid="stTabs"] [role="tab"] {{
    color: {"rgba(212,185,140,0.80)" if _is_dark else "rgba(40,100,60,0.75)"} !important;
    font-weight: 700 !important;
    font-size: 0.93rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 0.55rem 1.4rem !important;
    border-radius: 8px 8px 0 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    transition: color 0.20s ease, background 0.20s ease, box-shadow 0.20s ease !important;
}}

[data-testid="stTabs"] [role="tab"]:hover {{
    color: {"rgba(212,175,114,0.90)" if _is_dark else "rgba(30,100,50,0.90)"} !important;
    background: {"rgba(212,175,114,0.06)" if _is_dark else "rgba(60,140,80,0.06)"} !important;
    box-shadow: none !important;
    border: none !important;
}}

[data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
    color: {"#e8c96a" if _is_dark else "#0f3d1f"} !important;
    background: {"rgba(212,175,114,0.09)" if _is_dark else "rgba(60,140,80,0.08)"} !important;
    border: none !important;
    border-bottom: {"2px solid #d4af72" if _is_dark else "2px solid #14532d"} !important;
    box-shadow: {"inset 0 2px 8px rgba(212,175,114,0.10)" if _is_dark else "inset 0 2px 8px rgba(60,140,80,0.08)"} !important;
    text-shadow: {"0 0 16px rgba(212,175,114,0.45)" if _is_dark else "none"} !important;
}}

/* ── Radio & other form elements ────────────────────────────────── */
[data-testid="stRadio"] label span,
[data-testid="stRadio"] label p {{
    color: {"#f0e8d8" if _is_dark else "#12200e"} !important;
    font-weight: 500 !important;
}}

/* "Day Type" radio group label */
[data-testid="stRadio"] > label,
[data-testid="stRadio"] > div > label {{
    color: {"#f0e8d8" if _is_dark else "#12200e"} !important;
}}

/* ── Alerts / info boxes ────────────────────────────────────────── */
div[data-testid="stAlert"] {{
    background: {"rgba(60,55,48,0.92)" if _is_dark else "rgba(246,244,232,0.85)"} !important;
    border-color: {"rgba(148,137,121,0.30)" if _is_dark else "rgba(80,170,110,0.4)"} !important;
    backdrop-filter: blur(10px) !important;
    color: {"#f0e0c8" if _is_dark else "#12200e"} !important;
}}

div[data-testid="stAlert"] p, div[data-testid="stAlert"] span {{
    color: {"#faf0d8" if _is_dark else "#12200e"} !important;
}}

/* ── Buttons — text color ───────────────────────────────────────── */
.stButton > button, .stButton > button p, .stButton > button span, .stButton > button div,
.stFormSubmitButton > button, .stFormSubmitButton > button p, .stFormSubmitButton > button span {{
    color: {"#000000" if _is_dark else "#1a1308"} !important;
    text-shadow: none !important;
}}

/* ── Buttons — text color ───────────────────────────────────────── */
.stButton > button, .stButton > button p, .stButton > button span, .stButton > button div,
.stFormSubmitButton > button, .stFormSubmitButton > button p, .stFormSubmitButton > button span {{
    color: {"#000000" if _is_dark else "#1a1308"} !important;
    text-shadow: none !important;
}}

/* ── Hooray banner ──────────────────────────────────────────────── */
.entryexit-hooray-banner {{
    backdrop-filter: blur(10px) !important;
}}

/* ── Divider ────────────────────────────────────────────────────── */
hr {{
    border-color: {"rgba(180,140,80,0.28)" if _is_dark else "rgba(80,170,110,0.3)"} !important;
}}

/* ── Text inputs (signup fields) ────────────────────────────────── */
.stTextInput input,
.stTextInput > div > div > input,
div[data-baseweb="input"] input,
div[data-baseweb="input"] {{
    background: {"rgba(60,55,48,0.90)" if _is_dark else "#F6F4E8"} !important;
    border: {"1px solid rgba(148,137,121,0.28)" if _is_dark else "1px solid rgba(80,170,110,0.4)"} !important;
    color: {"#e8d8c0" if _is_dark else "#12200e"} !important;
    border-radius: 12px !important;
    backdrop-filter: blur(8px) !important;
}}

.stTextInput input::placeholder,
div[data-baseweb="input"] input::placeholder {{
    color: {"rgba(200,185,155,0.75)" if _is_dark else "rgba(40,100,55,0.65)"} !important;
}}

.stTextInput input:focus,
div[data-baseweb="input"]:focus-within {{
    border-color: {"#d4af72" if _is_dark else "rgba(80,170,110,0.8)"} !important;
    box-shadow: {"0 0 0 2px rgba(212,175,114,0.28)" if _is_dark else "0 0 0 2px rgba(80,170,110,0.2)"} !important;
}}

/* ── Hide "Press Enter to submit" hints ─────────────────────────── */
[data-testid="InputInstructions"],
.stTextArea [data-testid="InputInstructions"],
.stTextInput [data-testid="InputInstructions"],
.stTextArea small,
.stTextInput small {{
    display: none !important;
}}

/* ── Tooltip icon ────────────────────────────────────────────────── */
div[data-testid="tooltipHoverTarget"] {{
    filter: {"invert(1) brightness(2)" if _is_dark else "none"} !important;
    opacity: 1 !important;
}}
div[data-testid="tooltipHoverTarget"] > div,
div[data-testid="tooltipHoverTarget"] > div > button,
div[data-testid="tooltipHoverTarget"] > div > button > div,
div[data-testid="tooltipHoverTarget"] > div > button svg,
div[data-testid="tooltipHoverTarget"] > div > button svg path {{
    filter: {"invert(1) brightness(2)" if _is_dark else "none"} !important;
    fill: {"#ffffff" if _is_dark else "currentColor"} !important;
    color: {"#ffffff" if _is_dark else "currentColor"} !important;
    opacity: 1 !important;
}}
[data-testid="stRadio"] [data-testid="tooltipHoverTarget"] svg {{
    filter: {"invert(1) brightness(2)" if _is_dark else "none"} !important;
    opacity: 1 !important;
}}

/* ── Tooltip popup ───────────────────────────────────────────────── */
div[data-testid="tooltipHoverTarget"] + div,
[data-testid="stTooltipContent"],
div[role="tooltip"],
.stTooltipContent {{
    background: {"#2a2f3a" if _is_dark else "#ffffff"} !important;
    color: {"#f0e8d8" if _is_dark else "#12200e"} !important;
    border: {"1px solid rgba(212,175,114,0.30)" if _is_dark else "1px solid rgba(0,0,0,0.10)"} !important;
    border-radius: 8px !important;
    box-shadow: {"0 4px 20px rgba(0,0,0,0.6)" if _is_dark else "0 4px 16px rgba(0,0,0,0.12)"} !important;
}}
div[role="tooltip"] *, [data-testid="stTooltipContent"] * {{
    color: {"#f0e8d8" if _is_dark else "#12200e"} !important;
}}
</style>
"""
st.markdown(THEME_CSS.replace("<style>", "<div hidden><style>").replace("</style>", "</style></div>"), unsafe_allow_html=True)

# ── Font color synced to theme toggle ─────────────────────────────────────────
_font_color = "#ffffff" if _is_dark else "#000000"
st.markdown(f"""
<style>

/* ── Universal text colour ──────────────────────────────────────── */
.stApp,
.stApp *:not(button):not(.entryexit-hooray-banner):not(.entryexit-hooray-banner *):not([style*='#14532d']):not([style*='#14532d'] *) {{
    color: {_font_color} !important;
}}

/* ── Preserve button text ───────────────────────────────────────── */
.stButton > button,
.stButton > button *,
.stFormSubmitButton > button,
.stFormSubmitButton > button * {{
    color: #000000 !important;
}}

/* ── Metric cards ───────────────────────────────────────────────── */
.stApp div[data-testid="stMetricLabel"] * {{
    color: {_font_color} !important;
    opacity: 0.75;
}}
.stApp div[data-testid="stMetricValue"] * {{
    color: {_font_color} !important;
    opacity: 1;
}}
.stApp div[data-testid="stMetric"] {{
    background: {"#605B51" if _is_dark else "#F6F4E8"} !important;
}}

/* ── Session panel ──────────────────────────────────────────────── */
.stApp .ee-session-col {{
    background: {"#605B51" if _is_dark else "#F6F4E8"} !important;
}}
.stApp .ee-col-header,
.stApp .ee-col-header * {{
    color: {_font_color} !important;
}}
.stApp .ee-row-label,
.stApp .ee-row-range,
.stApp .ee-row-dur {{
    color: {_font_color} !important;
}}
.stApp .ee-row-dur.work {{ color: {"#60a5fa" if _is_dark else "#000000"} !important; }}
.stApp .ee-row-dur.brk  {{ color: {"#d4af72" if _is_dark else "#000000"} !important; }}

/* ── Textarea ───────────────────────────────────────────────────── */
.stApp .stTextArea textarea {{
    color: {_font_color} !important;
    background: {"#605B51" if _is_dark else "#F6F4E8"} !important;
    border: {"1px solid #7a746a" if _is_dark else "1px solid rgba(60,140,80,0.35)"} !important;
}}
.stApp .stTextArea textarea::placeholder {{
    color: {"rgba(255,255,255,0.45)" if _is_dark else "rgba(0,0,0,0.38)"} !important;
}}

/* ── Alerts ─────────────────────────────────────────────────────── */
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span,
div[data-testid="stAlert"] * {{
    color: {_font_color} !important;
}}

/* ── Tabs ───────────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {{
    gap: 4px !important;
    border-bottom: {"1px solid rgba(212,175,114,0.20)" if _is_dark else "1px solid rgba(60,140,80,0.18)"} !important;
    background: transparent !important;
}}
[data-testid="stTabs"] [role="tab"] {{
    color: {"rgba(255,255,255,0.45)" if _is_dark else "rgba(0,0,0,0.40)"} !important;
    font-weight: 700 !important;
    font-size: 0.93rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 0.55rem 1.4rem !important;
    border-radius: 8px 8px 0 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    transition: color 0.20s ease, background 0.20s ease !important;
}}
[data-testid="stTabs"] [role="tab"]:hover {{
    color: {"rgba(255,255,255,0.85)" if _is_dark else "rgba(0,0,0,0.80)"} !important;
    background: {"rgba(255,255,255,0.06)" if _is_dark else "rgba(0,0,0,0.05)"} !important;
    box-shadow: none !important;
    border: none !important;
}}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
    color: {"#ffffff" if _is_dark else "#000000"} !important;
    background: {"rgba(255,255,255,0.08)" if _is_dark else "rgba(0,0,0,0.06)"} !important;
    border: none !important;
    border-bottom: {"2px solid #d4af72" if _is_dark else "2px solid #14532d"} !important;
    box-shadow: {"inset 0 2px 8px rgba(255,255,255,0.06)" if _is_dark else "inset 0 2px 8px rgba(0,0,0,0.05)"} !important;
    text-shadow: none !important;
}}

/* ── Green banner — always white ───────────────────────────────── */
.stApp .entryexit-hooray-banner,
.stApp .entryexit-hooray-banner *,
[data-testid="stMarkdownContainer"] .entryexit-hooray-banner,
[data-testid="stMarkdownContainer"] .entryexit-hooray-banner * {{
    color: #ffffff !important;
    text-shadow: 0 1px 4px rgba(0,0,0,0.4) !important;
}}

/* ── Info pill ──────────────────────────────────────────────────── */ ──────────────────────────────────────────────────── */
.ee-info-pill {{
    color: {_font_color} !important;
    font-weight: 500 !important;
}}
.ee-info-pill b {{
    color: {_font_color} !important;
    font-weight: 700 !important;
}}

</style>
""", unsafe_allow_html=True)

# ── Signup helpers ────────────────────────────────────────────────────────────

def _get_signup_worksheet():
    """Return the gspread worksheet for signups."""
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(st.secrets["signup_sheet"]["sheet_id"])
    return sheet.worksheet(st.secrets["signup_sheet"].get("worksheet", "Sheet1"))


def check_existing_signup(email: str):
    """Return existing row dict if email already registered, else None."""
    try:
        ws = _get_signup_worksheet()
        records = ws.get_all_records()
        email_lower = email.strip().lower()
        for row in records:
            if str(row.get("Email", "")).strip().lower() == email_lower:
                return row
        return None
    except Exception:
        return None


def submit_signup_to_sheets(full_name: str, email: str) -> bool:
    """Append signup record only if email not already registered."""
    try:
        ws = _get_signup_worksheet()
        timestamp = now_pune().strftime("%Y-%m-%d %H:%M:%S")
        ws.append_row([timestamp, full_name, email])
        return True
    except Exception as e:
        st.error(f"Could not save registration: {e}")
        return False


def _set_user_param(name: str, email: str) -> None:
    """Encode name+email into URL query param so it persists on refresh/bookmark."""
    encoded = base64.urlsafe_b64encode(f"{name}||{email}".encode()).decode()
    st.query_params["u"] = encoded


def _inject_signup_css(dark: bool) -> None:
    """Inject signup page CSS via hidden-div trick — reliable in all Streamlit versions."""
    gold     = '#d4af72'
    # Dark: deep navy | Light: warm cream
    right_bg = '#1a1e26'                        if dark else '#F6F4E8'
    left_bg  = 'linear-gradient(150deg,#1c3f28 0%,#0d1f14 55%,#172f20 100%)' if dark else 'linear-gradient(150deg,#1a3d24 0%,#0f2e18 55%,#163322 100%)'
    lbl_c    = 'rgba(230,215,185,0.90)'         if dark else 'rgba(20,60,30,0.85)'
    div_c    = 'rgba(212,175,114,0.22)'         if dark else 'rgba(30,100,55,0.22)'
    inp_bg   = '#252b35'                        if dark else '#ffffff'
    inp_bdr  = 'rgba(212,175,114,0.25)'         if dark else 'rgba(30,120,60,0.35)'
    inp_txt  = '#ffffff'                        if dark else '#12200e'
    inp_ph   = 'rgba(200,185,155,0.70)'         if dark else 'rgba(40,100,55,0.65)'
    bdr_c    = 'rgba(212,175,114,0.18)'         if dark else 'rgba(30,100,55,0.18)'
    shad     = ('0 28px 80px rgba(0,0,0,0.65),0 6px 22px rgba(0,0,0,0.40)' if dark else
                '0 20px 64px rgba(15,60,30,0.14),0 4px 16px rgba(15,60,30,0.07)')
    txt_c    = 'rgba(230,215,185,0.90)'         if dark else 'rgba(20,60,30,0.85)'
    left_txt = '#ffffff'                        if dark else '#ffffff'

    css = f"""
    div[data-testid="stHorizontalBlock"] {{
        gap: 0 !important;
        align-items: stretch !important;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: {shad};
        border: 1px solid {bdr_c};
        margin: 0.5rem 0 1.5rem;
    }}
    .ee-hdr-toggle div[data-testid="stHorizontalBlock"] {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        overflow: visible !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    .ee-hdr-toggle div[data-testid="stColumn"] {{
        background: transparent !important;
        padding: 0 !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {{
        padding: 0 !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] {{
        gap: 0 !important;
        padding: 0 !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child {{
        background: {left_bg} !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child p,
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child span,
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child div,
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child [data-testid="stMarkdownContainer"] *,
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child [data-testid="stVerticalBlock"] * {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child {{
        background: {right_bg} !important;
        padding: 2.6rem 2.2rem 2.2rem !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child label {{
        color: {lbl_c} !important;
        font-size: 0.79rem !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child input {{
        background: {inp_bg} !important;
        border: 1px solid {inp_bdr} !important;
        color: {inp_txt} !important;
        -webkit-text-fill-color: {inp_txt} !important;
        border-radius: 10px !important;
        caret-color: {inp_txt} !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child input:-webkit-autofill,
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child input:-webkit-autofill:hover,
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child input:-webkit-autofill:focus {{
        -webkit-text-fill-color: {inp_txt} !important;
        -webkit-box-shadow: 0 0 0px 1000px {inp_bg} inset !important;
        box-shadow: 0 0 0px 1000px {inp_bg} inset !important;
        caret-color: {inp_txt} !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child input:focus {{
        border-color: {gold} !important;
        box-shadow: 0 0 0 2px rgba(212,175,114,0.18) !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child [data-testid="stForm"] {{
        border: 1px solid {div_c} !important;
        border-radius: 12px !important;
        padding: 0.75rem !important;
        background: transparent !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child p,
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child span,
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child div,
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child h1,
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child h2,
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child h3 {{
        color: {txt_c} !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child [data-testid="stMarkdownContainer"] * {{
        color: {txt_c} !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child * {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child input::placeholder {{
        color: {inp_ph} !important;
        -webkit-text-fill-color: {inp_ph} !important;
        opacity: 1 !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child input::-webkit-input-placeholder {{
        color: {inp_ph} !important;
        -webkit-text-fill-color: {inp_ph} !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child .stButton > button,
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child .stFormSubmitButton > button {{
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }}
    """
    st.markdown(f'<div hidden><style>{css}</style></div>', unsafe_allow_html=True)


def render_signup_page() -> None:
    """Full-page signup gate rendered before the main app."""
    _tm = st.session_state.theme_mode
    D   = (_tm == "dark")

    # ── Colours ───────────────────────────────────────────────────────────────
    gold      = '#d4af72'
    title_c   = '#ffffff'                           # left panel always dark green bg
    sub_c     = 'rgba(220,200,162,0.75)'            # left panel subtitle
    chip_bg   = 'rgba(255,255,255,0.08)'            # left panel chips (dark bg)
    chip_bdr  = 'rgba(212,175,114,0.22)'
    chip_txt  = '#ffffff'
    lbl_c     = 'rgba(230,215,185,0.90)'  if D else 'rgba(20,60,30,0.80)'
    div_c     = 'rgba(212,175,114,0.22)'  if D else 'rgba(30,100,55,0.22)'
    div_txt   = 'rgba(210,190,145,0.70)'  if D else 'rgba(20,80,40,0.55)'
    foot_c    = 'rgba(210,195,165,0.65)'  if D else 'rgba(20,80,40,0.50)'
    form_ttl  = '#ffffff'                 if D else '#12200e'
    eye_c     = '#c9a855'                 if D else '#1a6035'

    # Inject CSS
    _inject_signup_css(D)

    # ── Max-width wrapper (limits signup card horizontal spread) ─────────────
    st.markdown(
        '<div style="max-width:780px;margin:0 auto;">',
        unsafe_allow_html=True,
    )

    # ── Toggle button ─────────────────────────────────────────────────────────
    _name_col, _tog = st.columns([10, 2])
    with _name_col:
        st.markdown(
            f'<div style="display:flex;align-items:center;justify-content:center;'
            f'padding:0.5rem 0;margin-top:25px;">'
            f'<div style="text-align:center;">'
            f'<div style="display:flex;align-items:center;justify-content:center;gap:0.9rem;">'
            f'<span style="font-size:2.4rem;line-height:1;'
            f'filter:drop-shadow(0 2px 8px rgba(0,0,0,0.55));">⏱️</span>'
            f'<span style="font-family:Georgia,serif;font-size:2.6rem;font-weight:700;'
            f'color:#ffffff;letter-spacing:0.04em;line-height:1;'
            f'text-shadow:0 2px 20px rgba(0,0,0,0.7),0 1px 6px rgba(0,0,0,0.45),'
            f'0 0 40px rgba(212,175,114,0.15);">'
            f'EntryExit Insight</span>'
            f'</div>'
            f'<div style="margin:0 auto;margin-top:7px;width:70%;height:4.5px;'
            f'background:linear-gradient(90deg,transparent,#d4af72,rgba(212,175,114,0.5),transparent);'
            f'border-radius:2px;"></div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with _tog:
        tgl = "\u2600\ufe0f  Light" if D else "\U0001f319  Dark"
        if st.button(tgl, key="btn_signup_theme_toggle"):
            st.session_state.theme_mode = "light" if D else "dark"
            st.rerun()

    # ── Chips HTML ────────────────────────────────────────────────────────────
    chips_data = [
        ("\U0001f516", "Sign up once \u00b7 bookmark your link, no re-signup again"),
        ("\U0001f512",  "No passwords  ·  No OTP  ·  No spam \u2014 ever"),
        ("\u23f1\ufe0f",  "Every second matters \u2014 we track them all"),
        ("\U0001f4c5", "Full Day & Half Day shift support"),
        ("\U0001f464", "Team Member & Team Leader dashboards"),
        ("\u2705",     "Instant logout eligibility status"),
        ("\u26a1",     "Real-time biometric punch tracking"),
    ]
    cs = (f'display:flex;align-items:center;gap:0.65rem;padding:0.80rem 0.85rem;'
          f'border-radius:10px;background:{chip_bg};border:1px solid {chip_bdr};margin-bottom:0.70rem;')
    chips_html = "".join(
        f'<div style="{cs}">'
        f'<span style="font-size:0.92rem;flex-shrink:0;">{ic}</span>'
        f'<span style="font-size:0.79rem !important;color:{chip_txt} !important;">{tx}</span>'
        f'</div>'
        for ic, tx in chips_data
    )

    # ── Two columns ───────────────────────────────────────────────────────────
    lc, rc = st.columns(2)

    # LEFT ────────────────────────────────────────────────────────────────────
    with lc:
        st.markdown(
            # Outer wrapper — fills full column height via padding
            f'<div style="padding:3.2rem 3rem 3rem;height:100%;box-sizing:border-box;'
            f'position:relative;overflow:hidden;">'

            # Ambient glow
            f'<div style="position:absolute;inset:0;pointer-events:none;'
            f'background:radial-gradient(ellipse at 25% 15%,rgba(212,175,114,0.12) 0%,transparent 55%),'
            f'radial-gradient(ellipse at 78% 85%,rgba(34,200,100,0.05) 0%,transparent 50%);"></div>'

            # Badge
            f'<div style="display:inline-flex;align-items:center;gap:0.4rem;'
            f'background:rgba(212,175,114,0.12);border:1px solid rgba(212,175,114,0.28);'
            f'border-radius:100px;padding:0.25rem 0.75rem;font-size:0.66rem !important;'
            f'font-weight:700 !important;letter-spacing:0.13em;text-transform:uppercase;'
            f'color:{gold} !important;width:fit-content;margin-bottom:1.3rem;">'
            f'&#10022;&nbsp; Your Time Intelligence Hub</div>'

            # Gold bar
            f'<div style="width:300px;height:2px;'
            f'background:linear-gradient(90deg,{gold},transparent);'
            f'border-radius:5px;margin-bottom:1.3rem;"></div>'

            + chips_html +
            f'</div>',
            unsafe_allow_html=True,
        )

    # RIGHT ───────────────────────────────────────────────────────────────────
    with rc:
        # Header
        st.markdown(
            f'<div style="margin-bottom:0.9rem;">'
            f'<div style="font-size:0.67rem !important;font-weight:700 !important;'
            f'letter-spacing:0.15em;text-transform:uppercase;color:{eye_c} !important;'
            f'<div style="font-family:Georgia,serif !important;font-size:1.8rem !important;'
            f'font-weight:600 !important;color:{form_ttl} !important;'
            f'line-height:1.15 !important;margin-bottom:0.9rem !important;">'
            f'Let\'s set up your profile.</div>'
            f'<div style="font-size:0.81rem !important;color:{lbl_c} !important;">'
            f'</div>',
            unsafe_allow_html=True,
        )

        if "signup_error" not in st.session_state:
            st.session_state.signup_error = ""

        # Already registered
        st.markdown(
            f'<p style="font-size:0.67rem !important;font-weight:700 !important;'
            f'letter-spacing:0.13em;text-transform:uppercase;'
            f'color:{lbl_c} !important;margin:0.5rem 0 0.2rem !important;">Already registered</p>',
            unsafe_allow_html=True,
        )
        with st.form(key="returning_form", clear_on_submit=False):
            ret_email = st.text_input("Email address", placeholder="ravi.kumar@company.com", key="_ret_email")
            ret_submitted = st.form_submit_button("Continue \u2192", use_container_width=True)

        if ret_submitted:
            ret_email_clean = (ret_email or "").strip().lower()
            if not ret_email_clean or "@" not in ret_email_clean:
                st.warning("Please enter a valid email.")
            else:
                with st.spinner("Verifying\u2026"):
                    existing = check_existing_signup(ret_email_clean)
                if existing:
                    st.session_state.signup_done = True
                    st.session_state.signup_user_name = existing.get("Full Name", "")
                    _set_user_param(existing.get("Full Name", ""), ret_email_clean)
                    st.rerun()
                else:
                    st.warning("Email not found. Please register below.")

        # Divider
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:0.6rem;margin:0.6rem 0;">'
            f'<div style="flex:1;height:1px;background:{div_c};"></div>'
            f'<span style="font-size:0.68rem !important;letter-spacing:0.10em;'
            f'color:{div_txt} !important;white-space:nowrap;">New here? Register below</span>'
            f'<div style="flex:1;height:1px;background:{div_c};"></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # New registration
        # Guard: hide the form entirely while a registration is in progress
        if "signup_submitting" not in st.session_state:
            st.session_state.signup_submitting = False

        st.markdown(
            f'<p style="font-size:0.67rem !important;font-weight:700 !important;'
            f'letter-spacing:0.13em;text-transform:uppercase;'
            f'color:{lbl_c} !important;padding:0 10px; !important;">Create your profile</p>',
            unsafe_allow_html=True,
        )

        if st.session_state.signup_submitting:
            # Show only a spinner — no form rendered underneath
            st.spinner("Registering\u2026")
        else:
            with st.form(key="signup_form", clear_on_submit=False):
                full_name = st.text_input("Full Name", placeholder="Ravi Kumar", key="_signup_name")
                email     = st.text_input("Official Email", placeholder="ravi.kumar@company.com", key="_signup_email")
                submitted = st.form_submit_button("Register & Continue \u2192", use_container_width=True)

            if submitted:
                name_clean  = (full_name or "").strip()
                email_clean = (email or "").strip().lower()
                if not name_clean:
                    st.warning("Please enter your full name.")
                elif not email_clean:
                    st.warning("Please enter your official email.")
                elif "@" not in email_clean or "." not in email_clean.split("@")[-1]:
                    st.warning("That doesn\'t look like a valid email address.")
                else:
                    with st.spinner("Checking\u2026"):
                        existing = check_existing_signup(email_clean)
                    if existing:
                        st.session_state.signup_done = True
                        st.session_state.signup_user_name = existing.get("Full Name", name_clean)
                        st.rerun()
                    else:
                        st.session_state.signup_submitting = True
                        st.session_state._pending_name  = name_clean
                        st.session_state._pending_email = email_clean
                        st.rerun()

        # Process pending registration (runs on the rerun after flag is set)
        if st.session_state.signup_submitting:
            name_clean  = st.session_state.get("_pending_name", "")
            email_clean = st.session_state.get("_pending_email", "")
            with st.spinner("Registering\u2026"):
                ok = submit_signup_to_sheets(name_clean, email_clean)
            st.session_state.signup_submitting = False
            if ok:
                st.session_state.signup_done = True
                st.session_state.signup_user_name = name_clean
                _set_user_param(name_clean, email_clean)
            st.rerun()

        st.markdown(
            f'<p style="font-size:0.70rem !important;color:{foot_c} !important;'
            f'text-align:center;margin-top:0.7rem !important;line-height:2.65;">'
            f'Your details are only used to identify registered users.<br>',
            unsafe_allow_html=True,
        )

    # Close max-width wrapper
    st.markdown('</div>', unsafe_allow_html=True)



# ── Signup gate — block app until registered ──────────────────────────────────
if not st.session_state.signup_done:
    render_signup_page()
    st.stop()


# Scroll to top on every page load/refresh
st.markdown(
    """<script>
    (function() {
        function scrollTop() {
            var container = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
            if (container) container.scrollTop = 0;
            window.parent.document.documentElement.scrollTop = 0;
            window.parent.document.body.scrollTop = 0;
        }
        scrollTop();
        setTimeout(scrollTop, 100);
        setTimeout(scrollTop, 300);
    })();
    </script>""",
    unsafe_allow_html=True,
)

# ── Header row: icon | title | spacer | theme toggle ──────────────────────────
hdr_icon, hdr_title, hdr_spacer, hdr_toggle = st.columns([1.1, 8.4, 1.3, 2], vertical_alignment="center")

with hdr_icon:
    st.markdown(CLOCK_SVG, unsafe_allow_html=True)

with hdr_title:
    st.markdown(
        '<div style="font-family:Georgia,serif;font-size:1.85rem;font-weight:700;'
        'color:#ffffff;margin:0;letter-spacing:-0.01em;line-height:1.0;'
        'text-shadow:0 2px 8px rgba(0,0,0,0.8);">'
        'EntryExit Insight</div>',
        unsafe_allow_html=True,
    )

with hdr_toggle:
    toggle_label = "☀️  Light" if _is_dark else "🌙  Dark"
    st.markdown(
        f"""
        <style>
        @keyframes ee-toggle-pulse {{
            0%   {{ box-shadow: {"0 0 0 0 rgba(212,175,114,0.35)" if _is_dark else "0 0 0 0 rgba(180,140,60,0.28)"}; }}
            70%  {{ box-shadow: {"0 0 0 7px rgba(212,175,114,0)" if _is_dark else "0 0 0 7px rgba(180,140,60,0)"}; }}
            100% {{ box-shadow: {"0 0 0 0 rgba(212,175,114,0)" if _is_dark else "0 0 0 0 rgba(180,140,60,0)"}; }}
        }}

        div[data-testid="column"]:last-child .stButton > button {{
            background: {"linear-gradient(145deg,#4a453c 0%,#3a3530 50%,#423d34 100%)" if _is_dark else "linear-gradient(145deg,#fffdf5 0%,#f7e8c0 50%,#f0d898 100%)"} !important;
            color: {"#d4af72" if _is_dark else "#6b4a0e"} !important;
            border: {"1px solid rgba(212,175,114,0.35)" if _is_dark else "1px solid rgba(180,130,40,0.45)"} !important;
            border-radius: 14px !important;
            font-size: 0.78rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
            padding: 0.35rem 1.1rem !important;
            min-height: 2.2rem !important;
            position: relative !important;
            overflow: hidden !important;
            box-shadow: {
                "0 2px 8px rgba(0,0,0,0.55), 0 1px 2px rgba(0,0,0,0.4), inset 0 1px 0 rgba(212,175,114,0.18), inset 0 -1px 0 rgba(0,0,0,0.3)"
                if _is_dark else
                "0 2px 8px rgba(160,120,40,0.22), 0 1px 2px rgba(0,0,0,0.08), inset 0 1px 0 rgba(255,255,255,0.9), inset 0 -1px 0 rgba(160,120,40,0.15)"
            } !important;
            transition: all 0.22s cubic-bezier(0.34,1.56,0.64,1) !important;
            backdrop-filter: blur(8px) !important;
        }}

        div[data-testid="column"]:last-child .stButton > button::after {{
            content: "" !important;
            position: absolute !important;
            inset: 0 !important;
            background: {"linear-gradient(180deg,rgba(212,175,114,0.08) 0%,transparent 60%)" if _is_dark else "linear-gradient(180deg,rgba(255,255,255,0.55) 0%,transparent 60%)"} !important;
            border-radius: inherit !important;
            pointer-events: none !important;
        }}

        div[data-testid="column"]:last-child .stButton > button:hover {{
            background: {"linear-gradient(145deg,#524d44 0%,#423d34 50%,#4a4540 100%)" if _is_dark else "linear-gradient(145deg,#fff9e8 0%,#f5e0a8 50%,#edcf80 100%)"} !important;
            color: {"#e8c87a" if _is_dark else "#5a3c08"} !important;
            border-color: {"rgba(232,200,122,0.55)" if _is_dark else "rgba(160,110,20,0.6)"} !important;
            transform: translateY(-2px) scale(1.03) !important;
            box-shadow: {
                "0 6px 20px rgba(0,0,0,0.5), 0 2px 6px rgba(0,0,0,0.35), inset 0 1px 0 rgba(232,200,122,0.25), 0 0 12px rgba(212,175,114,0.18)"
                if _is_dark else
                "0 6px 18px rgba(160,120,40,0.3), 0 2px 6px rgba(0,0,0,0.1), inset 0 1px 0 rgba(255,255,255,0.95), 0 0 12px rgba(200,160,60,0.2)"
            } !important;
        }}

        div[data-testid="column"]:last-child .stButton > button:active {{
            transform: translateY(0px) scale(0.98) !important;
            transition: all 0.08s ease !important;
            box-shadow: {
                "0 1px 4px rgba(0,0,0,0.6), inset 0 2px 4px rgba(0,0,0,0.3)"
                if _is_dark else
                "0 1px 4px rgba(160,120,40,0.2), inset 0 2px 4px rgba(160,120,40,0.1)"
            } !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    if st.button(toggle_label, key="btn_theme_toggle"):
        st.session_state.theme_mode = "light" if _is_dark else "dark"
        st.rerun()

st.caption(
    "Paste biometric punches under the role that applies to you. "
    "Team Member and Team Leader each keep their own log, day type, and metrics."
)
st.caption(f"Pune time (IST): {now_pune().strftime('%d-%b-%Y %I:%M:%S %p')}")
if get_first_name():
    st.caption(f"👋 Welcome, **{get_first_name()}**")

st.markdown("**Biometric log**")
tab_member_in, tab_leader_in = st.tabs(["👤  Team Member", "👑  Team Leader"])

with tab_member_in:
    st.radio(
        "Day Type",
        DAY_TYPE_OPTIONS,
        index=DAY_TYPE_OPTIONS.index(st.session_state.member_day_type),
        key=MEMBER_DAY_WIDGET_KEY,
        on_change=persist_member_day_query,
        horizontal=True,
        help="Min logout time: Full Day = 7h 30m | Half Day = 4h 30m",
    )
    with st.form(key="member_calc_form", clear_on_submit=False):
        st.text_area(
            "Team Member biometric log paste",
            height=170,
            label_visibility="collapsed",
            placeholder="Biometric.\n01:55\nBiometric.\n01:56\nBiometric.\n01:58\n...",
            key=MEMBER_PASTE_WIDGET_KEY,
        )
        member_submitted = st.form_submit_button("Calculate Times", use_container_width=True)
    if member_submitted:
        raw = normalize_paste_text(st.session_state.get(MEMBER_PASTE_WIDGET_KEY, ""))
        parsed = fresh_parse_biometric_log(raw)
        if parsed is None:
            st.error("Please enter at least one valid time in HH:MM format.")
            st.session_state.member_biometric_points = None
        else:
            st.session_state.member_biometric_points = list(parsed)

    st.markdown("**Live preview**")
    member_live_dashboard()

with tab_leader_in:
    st.radio(
        "Day Type",
        DAY_TYPE_OPTIONS,
        index=DAY_TYPE_OPTIONS.index(st.session_state.leader_day_type),
        key=LEADER_DAY_WIDGET_KEY,
        on_change=persist_leader_day_query,
        horizontal=True,
        help="Min login time: Full Day = 7h 00m | Half Day = 4h 00m",
    )
    with st.form(key="leader_calc_form", clear_on_submit=False):
        st.text_area(
            "Team Leader biometric log paste",
            height=170,
            label_visibility="collapsed",
            placeholder="Biometric.\n01:55\nBiometric.\n01:56\nBiometric.\n01:58\n...",
            key=LEADER_PASTE_WIDGET_KEY,
        )
        leader_submitted = st.form_submit_button("Calculate Times", use_container_width=True)
    if leader_submitted:
        raw = normalize_paste_text(st.session_state.get(LEADER_PASTE_WIDGET_KEY, ""))
        parsed = fresh_parse_biometric_log(raw)
        if parsed is None:
            st.error("Please enter at least one valid time in HH:MM format.")
            st.session_state.leader_biometric_points = None
        else:
            st.session_state.leader_biometric_points = list(parsed)

    st.markdown("**Live preview**")
    leader_live_dashboard()

st.markdown("---")
st.markdown("#### Feedback")


def submit_feedback_to_sheets(feedback_text: str) -> bool:
    """Append feedback + timestamp to the configured Google Sheet."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scopes
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(st.secrets["feedback_sheet"]["sheet_id"])
        worksheet = sheet.worksheet(st.secrets["feedback_sheet"].get("worksheet", "Sheet1"))
        timestamp = now_pune().strftime("%Y-%m-%d %H:%M:%S")
        user_name = st.session_state.get("signup_user_name", "")
        worksheet.append_row([timestamp, feedback_text, user_name])
        return True
    except Exception as e:
        st.error(f"Could not save feedback: {e}")
        return False


# Use a counter-based key so we can reset the widget by changing its key
if "feedback_reset_counter" not in st.session_state:
    st.session_state.feedback_reset_counter = 0
if "feedback_saved" not in st.session_state:
    st.session_state.feedback_saved = False

# Show success banner BEFORE text area (persists after rerun)
if st.session_state.feedback_saved:
    _fname = get_first_name()
    _thank = f"❤️ Thank you, {_fname}! Your valuable feedback has been noted." if _fname else "❤️ Thank you for your valuable feedback!"
    st.success(f"{_thank} Our team is actively working to make your experience even better.")
    st.session_state.feedback_saved = False

with st.form(key="feedback_form", clear_on_submit=True):
    feedback_text = st.text_area(
        "Share your feedback",
        label_visibility="collapsed",
        placeholder=(
            "Want a new feature? Share it in the feedback form, so our team will notify you once it’s implemented."
        ),
        height=100,
    )
    submitted = st.form_submit_button("Submit Feedback", use_container_width=True)

if submitted:
    stripped = (feedback_text or "").strip()
    if not stripped:
        st.warning("Please write something before submitting.")
    else:
        with st.spinner("Saving your feedback…"):
            ok = submit_feedback_to_sheets(stripped)
        if ok:
            st.session_state.feedback_saved = True
            st.rerun()
        else:
            st.error("❌ Could not save feedback. Please try again.")
