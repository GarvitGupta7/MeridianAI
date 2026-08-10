"""Self-service Streamlit retail intelligence portal."""
from __future__ import annotations

import io
import hashlib
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))
from retail_segmentation.config import settings
from retail_segmentation.database import RetailRepository
from retail_segmentation.service import RetailSegmentationService
from retail_segmentation.data import auto_map_transaction_schema
from retail_segmentation.eda import profile_dataset
from retail_segmentation.predictive import MODEL_FEATURES, score_predictions, PredictiveBundle


st.set_page_config(page_title="Meridian · Retail Intelligence", page_icon="M", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Serif:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
:root { --ink:#181B20; --paper:#EEF0EF; --panel:#FFF; --line:#D8DBD8; --muted:#5C6660; --green:#2F6B4E; --slate:#34567A; --mustard:#A9791F; --rust:#A94A2E; --plum:#675269; }
:root { color-scheme: light !important; }
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background:var(--paper) !important; color:var(--ink) !important; color-scheme:light !important; }
[data-baseweb="select"] > div, [data-baseweb="input"] > div, [data-baseweb="base-input"] { background:#FFFFFF !important; color:var(--ink) !important; border-color:var(--line) !important; }
[data-baseweb="select"] input, [data-baseweb="input"] input, [data-baseweb="base-input"] input { color:var(--ink) !important; background:#FFFFFF !important; }
[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] { background:#FFFFFF !important; color:var(--ink) !important; }
[data-baseweb="menu"] li, [role="option"] { color:var(--ink) !important; background:#FFFFFF !important; }
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label, .stRadio label, .stCheckbox label, .stSelectbox label, .stSlider label { color:var(--ink) !important; }
[data-baseweb="slider"] { color:var(--green) !important; }
[data-baseweb="slider"] [role="slider"] { background:var(--green) !important; border-color:var(--green) !important; }
[data-baseweb="slider"] [data-testid="stSliderTrack"] { background:var(--line) !important; }
/* Never inherit the browser/OS dark theme. Meridian is intentionally light. */
[data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] { background:var(--paper) !important; color:var(--ink) !important; }
[data-testid="stHeader"] { border-bottom:1px solid var(--line) !important; }
[data-testid="stToolbar"] button, [data-testid="stToolbar"] svg { color:var(--ink) !important; fill:var(--ink) !important; }
[data-testid="stAppViewContainer"] * { color-scheme:light !important; }
.stRadio [data-baseweb="radio"] > div:first-child, .stCheckbox [data-baseweb="checkbox"] > div:first-child { background:#FFFFFF !important; border-color:var(--line) !important; }
.stSlider [data-baseweb="slider"] div { color:var(--ink) !important; }
html,body,[class*="css"] {font-family:'IBM Plex Sans',sans-serif;}
#MainMenu,footer {visibility:hidden;}
.stApp {background:var(--paper);}
.block-container {max-width:1450px; padding:1.2rem 2.5rem 3rem;}
[data-testid="stSidebar"] {display:none;}
.meridian-header {display:flex; align-items:center; justify-content:space-between; gap:1rem; border-bottom:1px solid var(--line); padding:.35rem 0 1rem; margin-bottom:1.2rem;}
.meridian-mark {font-family:'IBM Plex Serif',serif; font-size:1.35rem; font-weight:600; color:var(--ink); margin:0;}
.meridian-mark-sub {font-family:'IBM Plex Mono',monospace; font-size:.65rem; letter-spacing:.1em; color:var(--muted); text-transform:uppercase; margin:.15rem 0 0;}
.meridian-mark-author {font-family:'IBM Plex Mono',monospace; font-size:.62rem; letter-spacing:.06em; color:var(--muted); margin:.3rem 0 0;}
.meridian-kicker {font-family:'IBM Plex Mono',monospace; color:var(--muted); font-size:.7rem; letter-spacing:.09em; text-transform:uppercase; margin-bottom:.55rem; border-left:2px solid var(--green); padding-left:.5rem;}
.meridian-title {font-family:'IBM Plex Serif',serif; color:var(--ink); font-size:2.15rem; font-weight:600; line-height:1.2; margin:0;}
.meridian-subtitle {color:var(--muted); font-size:.95rem; margin:.8rem 0 0; max-width:58ch; line-height:1.55;}
.hero-panel {background:var(--panel); border:1px solid var(--line); border-left:3px solid var(--green); border-radius:2px; padding:1.15rem 1.35rem; min-height:108px;}
.hero-panel h3 {font-family:'IBM Plex Mono',monospace; font-size:.74rem; letter-spacing:.05em; text-transform:uppercase; margin:0 0 .5rem; color:var(--ink);}
.hero-panel p {margin:0; color:var(--muted); font-size:.87rem; line-height:1.55;}
.metric-card {background:var(--panel); border:1px solid var(--line); border-radius:2px; padding:.95rem 1.05rem .85rem; min-height:100px; border-top:2px solid var(--accent);}
.metric-label {font-family:'IBM Plex Mono',monospace; font-size:.66rem; letter-spacing:.06em; text-transform:uppercase; font-weight:600; color:var(--muted); margin-bottom:.4rem;}
.metric-value {font-family:'IBM Plex Mono',monospace; font-size:1.45rem; font-weight:600; color:var(--ink); line-height:1.05;}
.metric-caption {font-size:.75rem; color:var(--muted); margin-top:.4rem;}
.section-label {font-family:'IBM Plex Mono',monospace; font-size:.7rem; letter-spacing:.07em; text-transform:uppercase; font-weight:600; color:var(--green); margin:2.1rem 0 .3rem; padding-top:.9rem; border-top:1px solid var(--line);}
.stTabs [data-baseweb="tab-list"] {gap:.05rem; border-bottom:1px solid var(--line); background:transparent;}
.stTabs [data-baseweb="tab"] {height:44px; border-radius:0; color:var(--muted); font-weight:600; padding:0 .8rem;}
.stTabs [aria-selected="true"] {background:transparent; color:var(--ink); border-bottom:2px solid var(--green);}
[data-testid="stDataFrame"] {border:1px solid var(--line); border-radius:2px; overflow:hidden;}
.stDownloadButton button,.stButton button {border-radius:2px; border:1px solid var(--line); font-weight:600; box-shadow:none;}
.stButton button[kind="primary"] {background:var(--green); border-color:var(--green);}
h2,h3 {font-family:'IBM Plex Serif',serif !important; color:var(--ink) !important; font-weight:600 !important;}
[data-testid="stMetricValue"] {font-family:'IBM Plex Mono',monospace;}
.predictive-callout {background:#F6F7F5; border:1px solid var(--line); border-left:3px solid var(--slate); padding:1rem 1.1rem; margin:.5rem 0 1rem;}
.predictive-callout strong {color:var(--ink);}
.small-note {font-size:.78rem; color:var(--muted);}
.top-nav-label {font-family:'IBM Plex Mono',monospace; font-size:.68rem; letter-spacing:.08em; color:var(--muted); margin-bottom:.2rem;}
.nav-rule {border-bottom:1px solid var(--line); margin:.15rem 0 1.35rem;}
.card-kicker {font-family:'IBM Plex Mono',monospace; font-size:.68rem; letter-spacing:.08em; color:var(--green); font-weight:600; margin-bottom:.25rem;}
.card-title {font-family:'IBM Plex Serif',serif !important; font-size:1.15rem !important; margin:.1rem 0 .75rem !important;}
[data-testid="stVerticalBlockBorderWrapper"] {background:rgba(255,255,255,.72); border-color:var(--line) !important; border-radius:3px !important; padding:.35rem .55rem .6rem;}
.empty-state {padding:2.5rem 0 1rem;}
.stSelectbox > div > div {border-radius:2px;}
</style>
""", unsafe_allow_html=True)

# Meridian visual system: one restrained palette is used consistently across every chart.
# Categorical charts use these fixed colors so the same category keeps the same visual identity.
PALETTE = ["#2F6B4E", "#34567A", "#A9791F", "#3E7A87", "#A94A2E", "#675269", "#4C7A5B"]
MERIDIAN_GREEN_SCALE = ["#E8F0EB", "#C8DCCE", "#9FBEAA", "#6F9A7F", "#4D7F63", "#2F6B4E"]
TIER_COLORS = {
    "Bronze": PALETTE[2],
    "Silver": PALETTE[1],
    "Gold": PALETTE[0],
    "Platinum": PALETTE[3],
}
PERSONA_COLORS = {
    "At-risk customers": PALETTE[4],
    "Loyal customers": PALETTE[0],
    "Big spenders": PALETTE[2],
    "Bargain shoppers": PALETTE[1],
    "New customers": PALETTE[3],
    "Regular customers": PALETTE[6],
    "Premium customers": PALETTE[5],
}
pio.templates["meridian"] = pio.templates["plotly_white"]
pio.templates["meridian"].layout.update(
    font=dict(family="IBM Plex Sans, sans-serif", color="#181B20", size=13),
    colorway=PALETTE,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    title_font=dict(family="IBM Plex Serif, serif", size=15),
    margin=dict(t=30,l=10,r=10,b=10),
)
pio.templates.default = "meridian"

repository = RetailRepository(settings.database_path)
service = RetailSegmentationService()


def read_upload(uploaded) -> pd.DataFrame:
    if uploaded.name.lower().endswith(".csv"):
        return pd.read_csv(uploaded)
    if uploaded.name.lower().endswith(".json"):
        return pd.read_json(uploaded)
    return pd.read_excel(uploaded)


def uploaded_signature(uploaded) -> str:
    """Stable signature used to detect a newly selected file without losing session state."""
    uploaded.seek(0)
    digest = hashlib.sha256(uploaded.getvalue()).hexdigest()
    uploaded.seek(0)
    return digest


def session_frame(name: str, fallback: pd.DataFrame | None = None) -> pd.DataFrame:
    """Read analysis output from the active user session, never from another user's upload."""
    active = st.session_state.get("active_analysis")
    if isinstance(active, dict):
        if isinstance(active.get(name), pd.DataFrame):
            return active[name].copy()
        eda = active.get("eda", {})
        if isinstance(eda, dict) and isinstance(eda.get(name), pd.DataFrame):
            return eda[name].copy()
    return fallback.copy() if isinstance(fallback, pd.DataFrame) else pd.DataFrame()


def active_dataset_label() -> str:
    return st.session_state.get("active_dataset_label", "Meridian Demo Dataset")


def render_mapping_review(raw: pd.DataFrame, mapped: pd.DataFrame, detected: dict[str, str], missing: list[str]) -> pd.DataFrame:
    """Show automatic mappings and ask the user only about unresolved concepts."""
    required = ["invoice_id", "customer_id", "invoice_date", "quantity", "unit_price"]
    final_mapping = dict(detected)
    if detected:
        rows = [{"Meridian field": target.replace("_", " ").title(), "Your column": source, "Status": "Auto-detected"}
                for source, target in detected.items() if target in required]
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if missing:
        st.warning("Meridian needs your help with only these fields: " + ", ".join(x.replace("_", " ") for x in missing) + ".")
        st.caption("Choose the column that best represents the business concept. You do not need to know Meridian's internal field names.")
        aliases = {
            "invoice_id": ["invoice", "order", "transaction", "receipt", "bill"],
            "customer_id": ["customer", "client", "buyer", "member", "shopper", "account"],
            "invoice_date": ["date", "time", "timestamp", "purchase", "order", "transaction", "sale"],
            "quantity": ["quantity", "qty", "unit", "units", "item", "count", "sold"],
            "unit_price": ["price", "selling", "sale", "amount", "rate", "cost", "value"],
        }
        selections = {}
        available = list(raw.columns)
        for field in missing:
            field_label = field.replace("_", " ").title()
            scored = []
            for col in available:
                label = str(col).lower().replace("_", " ")
                score = max((1.0 if word in label else 0.0) for word in aliases[field])
                scored.append((score, str(col)))
            suggested = max(scored, key=lambda x: x[0])[1] if scored else "-- Select --"
            options = ["-- Select --"] + available
            default_index = options.index(suggested) if suggested in options and max(scored, default=(0, ""))[0] > 0 else 0
            selected = st.selectbox(field_label, options, index=default_index, key=f"pending_map_{field}")
            if selected != "-- Select --":
                selections[selected] = field
        if set(selections.values()) != set(missing):
            raise ValueError("Please resolve the remaining required fields before running analysis.")
        mapped = raw.rename(columns={source: target for source, target in selections.items()})
        final_mapping.update(selections)
    st.session_state.pending_final_mapping = final_mapping
    return mapped


def map_columns(frame: pd.DataFrame) -> pd.DataFrame:
    required = ["invoice_id", "customer_id", "invoice_date", "quantity", "unit_price"]
    aliases = {
        "invoice_id": ["invoice_id", "invoiceno", "invoice no", "invoice", "order_id", "order id"],
        "customer_id": ["customer_id", "customerid", "customer id", "customer"],
        "invoice_date": ["invoice_date", "invoicedate", "invoice date", "date", "order_date"],
        "quantity": ["quantity", "qty", "units"],
        "unit_price": ["unit_price", "unitprice", "unit price", "price", "sales_price"],
    }
    lower = {str(c).strip().lower(): c for c in frame.columns}
    mapping = {}
    with st.expander("Column mapping", expanded=True):
        st.caption("Confirm the five required transaction concepts. Product, country, and category fields remain optional.")
        cols = st.columns(5)
        for col, field in zip(cols, required):
            default = next((lower[name] for name in aliases[field] if name in lower), None)
            choices = ["-- Select --", *frame.columns.tolist()]
            index = choices.index(default) if default in choices else 0
            selected = col.selectbox(field.replace("_", " ").title(), choices, index=index, key=f"map_{field}")
            if selected != "-- Select --":
                mapping[selected] = field
    if set(mapping.values()) != set(required):
        raise ValueError("Map all five required fields: invoice ID, customer ID, date, quantity, and unit price.")
    return frame.rename(columns=mapping)


def load_predictive_bundle() -> PredictiveBundle:
    path = settings.artifacts_dir / "predictive_models.joblib"
    if not path.exists():
        return PredictiveBundle({}, {})
    try:
        return PredictiveBundle(joblib.load(path), {})
    except Exception:
        return PredictiveBundle({}, {})


def prediction_metrics(summary: dict) -> dict:
    return summary.get("predictive_metrics", {}) if isinstance(summary, dict) else {}


def report_explanation(title: str, text: str, bullets: list[str] | None = None):
    """Render a plain-English interpretation block for report-oriented pages."""
    st.markdown(f'<div class="section-label">{title}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="hero-panel"><h3>What this means</h3><p>{text}</p></div>',
        unsafe_allow_html=True,
    )
    if bullets:
        st.markdown("<div class=\"small-note\" style=\"margin:.65rem 0 .2rem\"><strong>How to use it</strong></div>", unsafe_allow_html=True)
        for bullet in bullets:
            st.markdown(f"- {bullet}")


def pct(value) -> float:
    try:
        return float(value) * 100
    except (TypeError, ValueError):
        return 0.0



def render_customer_filters(customers: pd.DataFrame, key_prefix: str = "customer_page"):
    """Render independent, real-time Persona/Tier filters for a page."""
    persona_options = sorted(customers["persona"].dropna().astype(str).unique().tolist())
    tier_options = sorted(customers["customer_tier"].dropna().astype(str).unique().tolist())

    persona_key = f"{key_prefix}_persona_selection"
    tier_key = f"{key_prefix}_tier_selection"
    persona_count_key = f"{key_prefix}_persona_count"
    tier_count_key = f"{key_prefix}_tier_count"
    health_key = f"{key_prefix}_health"

    # Widget state is initialized once. Do NOT overwrite widget keys on every
    # rerun; doing that is what caused the previous delayed/stale behaviour.
    if persona_key not in st.session_state:
        st.session_state[persona_key] = []
    if tier_key not in st.session_state:
        st.session_state[tier_key] = []
    if persona_count_key not in st.session_state:
        st.session_state[persona_count_key] = 0
    if tier_count_key not in st.session_state:
        st.session_state[tier_count_key] = 0
    if health_key not in st.session_state:
        st.session_state[health_key] = 0

    # Keep selections valid if the underlying dataset changes.
    valid_personas = [x for x in st.session_state[persona_key] if x in persona_options]
    valid_tiers = [x for x in st.session_state[tier_key] if x in tier_options]
    st.session_state[persona_key] = valid_personas
    st.session_state[tier_key] = valid_tiers
    st.session_state[persona_count_key] = len(valid_personas)
    st.session_state[tier_count_key] = len(valid_tiers)

    def sync_personas():
        st.session_state[persona_count_key] = len(st.session_state[persona_key])

    def sync_tiers():
        st.session_state[tier_count_key] = len(st.session_state[tier_key])

    st.markdown('<div class="section-label">Customer filters</div>', unsafe_allow_html=True)
    st.caption(
        "Select the customer groups to include. Changes are applied immediately. "
        "No Persona or Tier is selected by default."
    )

    f1, f2, f3 = st.columns([1.15, 1.15, 1.0])

    with f1:
        persona_count = st.session_state[persona_count_key]
        persona_label = (
            f"{persona_count} persona selected" if persona_count == 1
            else f"{persona_count} personas selected"
        )
        with st.popover(persona_label, use_container_width=True):
            st.markdown("**Select personas**")
            a, b = st.columns(2)
            with a:
                if st.button("Select all", key=f"{key_prefix}_persona_all", use_container_width=True):
                    st.session_state[persona_key] = persona_options.copy()
                    st.session_state[persona_count_key] = len(persona_options)
                    st.rerun()
            with b:
                if st.button("Clear", key=f"{key_prefix}_persona_clear", use_container_width=True):
                    st.session_state[persona_key] = []
                    st.session_state[persona_count_key] = 0
                    st.rerun()
            st.divider()
            st.multiselect(
                "Personas",
                options=persona_options,
                key=persona_key,
                label_visibility="collapsed",
                placeholder="Choose personas...",
                on_change=sync_personas,
            )

    with f2:
        tier_count = st.session_state[tier_count_key]
        tier_label = (
            f"{tier_count} tier selected" if tier_count == 1
            else f"{tier_count} tiers selected"
        )
        with st.popover(tier_label, use_container_width=True):
            st.markdown("**Select customer tiers**")
            a, b = st.columns(2)
            with a:
                if st.button("Select all", key=f"{key_prefix}_tier_all", use_container_width=True):
                    st.session_state[tier_key] = tier_options.copy()
                    st.session_state[tier_count_key] = len(tier_options)
                    st.rerun()
            with b:
                if st.button("Clear", key=f"{key_prefix}_tier_clear", use_container_width=True):
                    st.session_state[tier_key] = []
                    st.session_state[tier_count_key] = 0
                    st.rerun()
            st.divider()
            st.multiselect(
                "Customer tiers",
                options=tier_options,
                key=tier_key,
                label_visibility="collapsed",
                placeholder="Choose tiers...",
                on_change=sync_tiers,
            )

    with f3:
        health_min = st.slider(
            "Minimum health score",
            min_value=0,
            max_value=100,
            value=int(st.session_state[health_key]),
            key=health_key,
        )

    selected_personas = st.session_state[persona_key]
    selected_tiers = st.session_state[tier_key]

    if not selected_personas or not selected_tiers:
        return customers.iloc[0:0].copy()

    return customers[
        customers["persona"].isin(selected_personas)
        & customers["customer_tier"].isin(selected_tiers)
        & (customers["health_score"] >= health_min)
    ].copy()

# Top navigation — visible page buttons keep the workspace accessible without a sidebar or dropdown.
PAGE_OPTIONS = [
    "Overview", "Customers", "Predictive Engine", "Customer Visuals",
    "Campaigns", "Sales Planning", "Data Quality", "Model Trust"
]

st.markdown(
    '<div class="meridian-header">'
    '<div><p class="meridian-mark">Meridian</p>'
    '<p class="meridian-mark-sub">Retail intelligence — internal build</p><p class="meridian-mark-author">Created by Garvit Gupta</p></div>'
    '<div class="small-note">Private workspace · company data stays local</div>'
    '</div>',
    unsafe_allow_html=True,
)

if "workspace_page" not in st.session_state:
    st.session_state.workspace_page = "Overview"

st.markdown('<div class="top-nav-label">WORKSPACE</div>', unsafe_allow_html=True)
nav_cols = st.columns(len(PAGE_OPTIONS) + 1, gap="small")

for col, nav_page in zip(nav_cols[:-1], PAGE_OPTIONS):
    with col:
        active = st.session_state.workspace_page == nav_page
        if st.button(
            nav_page,
            key=f"nav_{nav_page.lower().replace(' ', '_')}",
            use_container_width=True,
            type="primary" if active else "secondary",
        ):
            st.session_state.workspace_page = nav_page
            st.rerun()

with nav_cols[-1]:
    with st.popover("＋ Data", use_container_width=True):
        st.markdown("**Data controls**")
        st.caption("Upload a company transaction export or restore the secure demo dataset.")
        uploaded = st.file_uploader(
            "Upload company transactions",
            type=["csv", "xlsx", "xls", "json"],
            help="Required concepts: order ID, customer ID, date, quantity, and unit price.",
            key="global_data_upload",
        )
        use_demo = st.button(
            "Use secure demo data",
            use_container_width=True,
            key="global_demo_data",
        )
        if uploaded:
            st.caption(
                f"Selected: **{uploaded.name}** · "
                f"{getattr(uploaded, 'size', 0) / 1024:.0f} KB"
            )
        else:
            st.caption("CSV · XLSX · XLS · JSON · up to 200 MB")

st.markdown('<div class="nav-rule"></div>', unsafe_allow_html=True)

page = st.session_state.workspace_page
st.markdown('<div class="nav-rule"></div>', unsafe_allow_html=True)

# Uploaded data is session-scoped. This prevents a deployed Streamlit instance from
# leaking one company's data into another user's session, while keeping the active
# dataset, mapping, cleaning report and model outputs intact during page navigation.
if "active_analysis" not in st.session_state:
    st.session_state.active_analysis = None
if "active_dataset_label" not in st.session_state:
    st.session_state.active_dataset_label = "Meridian Demo Dataset"
if "pending_upload_signature" not in st.session_state:
    st.session_state.pending_upload_signature = None
if "pending_raw_data" not in st.session_state:
    st.session_state.pending_raw_data = None
if "pending_mapped_data" not in st.session_state:
    st.session_state.pending_mapped_data = None
if "pending_detected_mapping" not in st.session_state:
    st.session_state.pending_detected_mapping = {}
if "pending_missing_mapping" not in st.session_state:
    st.session_state.pending_missing_mapping = []
if "pending_final_mapping" not in st.session_state:
    st.session_state.pending_final_mapping = {}

# Read the currently selected upload from the persistent file-uploader widget.
if uploaded:
    try:
        signature = uploaded_signature(uploaded)
        if signature != st.session_state.pending_upload_signature:
            incoming = read_upload(uploaded)
            mapped, detected, missing = auto_map_transaction_schema(incoming)
            st.session_state.pending_upload_signature = signature
            st.session_state.pending_raw_data = incoming
            st.session_state.pending_mapped_data = mapped
            st.session_state.pending_detected_mapping = detected
            st.session_state.pending_missing_mapping = missing
            st.session_state.pending_final_mapping = detected.copy()
            # A newly selected file must never silently continue showing the previous analysis.
            st.session_state.active_analysis = None
            st.session_state.active_dataset_label = f"{uploaded.name} · awaiting analysis"
    except Exception as error:
        st.error(f"Could not read the uploaded dataset: {error}")

# Demo mode is explicit and remains isolated from uploaded user data.
if use_demo:
    with st.spinner("Building the demo intelligence workspace..."):
        demo_result = service.run_demo()
    st.session_state.active_analysis = demo_result
    st.session_state.active_dataset_label = "Meridian Demo Dataset"
    st.session_state.pending_raw_data = None
    st.session_state.pending_mapped_data = None
    st.session_state.pending_upload_signature = None
    st.session_state.pending_final_mapping = {}
    st.rerun()

# If a file is pending, show the mapping/review workflow on every page until analysis is run.
if st.session_state.pending_raw_data is not None and st.session_state.active_analysis is None:
    raw_pending = st.session_state.pending_raw_data
    mapped_pending = st.session_state.pending_mapped_data
    st.markdown('<div class="section-label">Uploaded dataset</div>', unsafe_allow_html=True)
    st.subheader("Review your dataset")
    st.caption(f"**{active_dataset_label()}** · {len(raw_pending):,} raw rows · {len(raw_pending.columns):,} columns")
    st.info("Meridian automatically maps familiar business column names. Only unresolved fields require your input.")
    try:
        mapped_pending = render_mapping_review(
            raw_pending,
            mapped_pending,
            st.session_state.pending_detected_mapping,
            st.session_state.pending_missing_mapping,
        )
        st.session_state.pending_mapped_data = mapped_pending
        if st.button("Run analysis", type="primary", use_container_width=True, key="run_analysis_pending"):
            with st.spinner("Cleaning your data, validating it, training models, and creating insights..."):
                result = service.run(mapped_pending, persist=False)
            result["raw_data"] = raw_pending.copy()
            result["mapping"] = st.session_state.pending_final_mapping.copy()
            st.session_state.active_analysis = result
            st.session_state.active_dataset_label = uploaded.name if uploaded else "Uploaded dataset"
            st.success("Analysis complete. The dashboard is now using your uploaded and cleaned dataset.")
            st.rerun()
    except Exception as error:
        st.warning(str(error))
    st.markdown('<div class="nav-rule"></div>', unsafe_allow_html=True)
    # Do not render demo/default analytics underneath an uploaded dataset waiting for confirmation.
    st.stop()

# Use the active session result when available; otherwise use Meridian's safe demo state.
if st.session_state.active_analysis is None:
    if "customers" not in repository.tables():
        st.markdown(
            '<div class="empty-state">'
            '<div class="meridian-kicker">Retail operating system</div>'
            '<h1 class="meridian-title">Know your customers.<br>Grow with confidence.</h1>'
            '<p class="meridian-subtitle">Open <strong>＋ Data</strong> above to upload a transaction export or use secure demo data.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.stop()

customers = session_frame("customers", repository.load_frame("customers"))
transactions = session_frame("transactions", repository.load_frame("transactions"))
evaluation = session_frame("evaluation", repository.load_frame("cluster_evaluation"))
campaigns = session_frame("campaigns", repository.load_frame("campaign_recommendations"))
retention = session_frame("retention", repository.load_frame("cohort_retention"))
forecast = session_frame("forecast", repository.load_frame("sales_forecast"))
explanations = session_frame("model_explanations", repository.load_frame("model_explanations"))
quality = session_frame("quality", repository.load_frame("data_quality_comparison"))
cleaning_audit = session_frame("cleaning_audit", repository.load_frame("cleaning_audit") if "cleaning_audit" in repository.tables() else pd.DataFrame())
column_profile = session_frame("cleaned_columns", repository.load_frame("cleaned_column_profile"))
monthly_revenue = session_frame("monthly_revenue", repository.load_frame("monthly_revenue"))
top_products = session_frame("top_products", repository.load_frame("top_products"))
country_performance = session_frame("country_performance", repository.load_frame("country_performance"))

summary = {}
if isinstance(st.session_state.get("active_analysis"), dict):
    summary = st.session_state.active_analysis.get("summary", {})
else:
    summary_path = settings.artifacts_dir / "run_summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))

# Persistent dataset indicator: every page now makes the active data source explicit.
st.markdown(
    f'<div class="small-note" style="margin:.25rem 0 .8rem"><strong>Active dataset:</strong> {active_dataset_label()} · '
    f'<strong>{len(transactions):,} cleaned transaction rows</strong> · analysis state preserved while navigating</div>',
    unsafe_allow_html=True,
)

# Pages without a customer-filter workflow use the complete portfolio.
filtered = customers.copy()

# Selected page only — no open tab strip and no page contents rendered together.
if page == "Overview":
    # Executive report: narrative, KPIs, ranked tables, and decision queues.
    # Main hero stays above the operational controls. Uploading and filtering are
    # workflow controls; they should not dominate the first screen.
    title_col, insight_col = st.columns([3.4, 1.6], gap="large")
    with title_col:
        st.markdown(
            '<div class="meridian-kicker">Retail operating system</div>'
            '<h1 class="meridian-title">Know your customers.<br>Grow with confidence.</h1>'
            '<p class="meridian-subtitle">Customer intelligence, growth actions, predictive customer scoring, and sales planning from one transaction upload.</p>',
            unsafe_allow_html=True,
        )
    with insight_col:
        critical = int((campaigns.priority == "Critical").sum())
        anomalies = int(customers.anomaly_flag.sum())
        st.markdown(
            f'<div class="hero-panel"><h3>Where to look first</h3>'
            f'<p><strong>{critical}</strong> account{"s" if critical != 1 else ""} are flagged Critical for retention and '
            f'<strong>{anomalies}</strong> customer record{"s" if anomalies != 1 else ""} triggered an anomaly check. '
            f'Use <strong>Predictive Engine</strong> for forward-looking decisions.</p></div>',
            unsafe_allow_html=True,
        )

    metrics = st.columns(6)
    revenue, orders = transactions.revenue.sum(), transactions.invoice_id.nunique()
    metric_data = [
        ("Revenue", f"${revenue:,.0f}", "All captured sales", "#2F6B4E"),
        ("Customers", f"{len(customers):,}", "Current portfolio", "#34567A"),
        ("Orders", f"{orders:,}", "Completed transactions", "#A9791F"),
        ("Health score", f"{customers.health_score.mean():.1f}", "Portfolio average", "#3E7A87"),
        ("Critical actions", str(critical), "Retention required", "#A94A2E"),
        ("Anomalies", str(anomalies), "Needs review", "#675269"),
    ]
    for column, (label, value, caption, accent) in zip(metrics, metric_data):
        column.markdown(
            f'<div class="metric-card" style="--accent:{accent}"><div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div><div class="metric-caption">{caption}</div></div>',
            unsafe_allow_html=True,
        )


    # Visual exploration is intentionally reserved for Customer Visuals.
    st.markdown('<div class="section-label">Executive report</div>', unsafe_allow_html=True)
    critical_customers = campaigns[campaigns.priority == "Critical"].copy() if "priority" in campaigns.columns else pd.DataFrame()
    high_risk = filtered.sort_values(["predicted_churn_probability", "churn_risk"], ascending=[False, False]).head(10).copy()
    high_value = filtered.sort_values("predicted_90d_spend", ascending=False).head(10).copy()

    avg_order = float(transactions.revenue.sum() / max(transactions.invoice_id.nunique(), 1))
    top_tier = filtered["customer_tier"].value_counts().index[0] if not filtered.empty else "—"
    top_persona = filtered["persona"].value_counts().index[0] if not filtered.empty else "—"
    top_country = country_performance.sort_values("revenue", ascending=False).iloc[0]["country"] if not country_performance.empty else "—"
    predicted_value = float(filtered["predicted_90d_spend"].sum()) if "predicted_90d_spend" in filtered else 0.0

    report_cols = st.columns(4)
    report_items = [
        ("Portfolio revenue", f"${revenue:,.0f}", "Captured transaction revenue"),
        ("Predicted 90-day value", f"${predicted_value:,.0f}", "Current filtered portfolio"),
        ("Average order value", f"${avg_order:,.0f}", "Revenue per completed order"),
        ("Critical retention accounts", f"{len(critical_customers):,}", "Customers needing immediate review"),
    ]
    for c, (label, value, caption) in zip(report_cols, report_items):
        c.markdown(
            f'<div class="metric-card" style="--accent:#2F6B4E"><div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div><div class="metric-caption">{caption}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-label">Management reading</div>', unsafe_allow_html=True)
    st.markdown(
        f"**Current portfolio:** {len(filtered):,} customers are in the active view. "
        f"The largest customer group is **{top_tier}**, while **{top_persona}** is the most common persona. "
        f"The strongest revenue market is **{top_country}**. "
        f"The filtered portfolio carries approximately **${predicted_value:,.0f}** of predicted 90-day spend. "
        f"There are **{len(critical_customers):,} Critical** retention accounts requiring prioritisation.",
    )

    report_explanation(
        "How to read the executive report",
        f"This page is a management summary of the current customer portfolio. The portfolio currently contains {len(filtered):,} customers. "
        f"The most common tier is {top_tier} and the most common persona is {top_persona}. "
        f"The predicted 90-day value is an estimate of future customer spend based on the predictive model; it should be used for prioritisation, not treated as guaranteed revenue. "
        f"Critical retention accounts are the customers Meridian believes deserve the fastest review because their current portfolio risk is high.",
        [
            "Start with the management reading to understand the overall business situation before opening individual customer records.",
            "Use the priority report to decide who needs retention attention first.",
            "Use the growth opportunity report to identify customers with stronger future-value potential.",
            "Open Customer Visuals when the reason behind a pattern needs deeper exploration.",
        ],
    )

    st.markdown('<div class="section-label">Priority customer report</div>', unsafe_allow_html=True)
    if high_risk.empty:
        st.info("No customers match the current filters.")
    else:
        risk_cols = [c for c in [
            "customer_id", "persona", "customer_tier", "health_score", "recency_days",
            "predicted_churn_probability", "predicted_90d_spend", "recommended_action"
        ] if c in high_risk.columns]
        risk_report = high_risk[risk_cols].copy()
        if "predicted_churn_probability" in risk_report:
            risk_report["predicted_churn_probability"] = (risk_report["predicted_churn_probability"] * 100).round(1).astype(str) + "%"
        risk_report = risk_report.rename(columns={
            "customer_id":"Customer ID", "persona":"Persona", "customer_tier":"Tier",
            "health_score":"Health", "recency_days":"Recency (days)",
            "predicted_churn_probability":"Churn probability",
            "predicted_90d_spend":"Predicted 90-day spend", "recommended_action":"Recommended action"
        })
        st.dataframe(risk_report, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-label">Growth opportunity report</div>', unsafe_allow_html=True)
    if high_value.empty:
        st.info("No customers match the current filters.")
    else:
        value_cols = [c for c in [
            "customer_id", "persona", "customer_tier", "monetary_value",
            "purchase_probability", "predicted_90d_spend", "clv_estimate"
        ] if c in high_value.columns]
        value_report = high_value[value_cols].copy()
        for col in ["purchase_probability"]:
            if col in value_report:
                value_report[col] = (value_report[col] * 100).round(1).astype(str) + "%"
        value_report = value_report.rename(columns={
            "customer_id":"Customer ID", "persona":"Persona", "customer_tier":"Tier",
            "monetary_value":"Historical spend", "purchase_probability":"Purchase probability",
            "predicted_90d_spend":"Predicted 90-day spend", "clv_estimate":"Estimated CLV"
        })
        st.dataframe(value_report, use_container_width=True, hide_index=True)

    st.download_button(
        "Download executive customer report",
        filtered.to_csv(index=False).encode(),
        "meridian_executive_customer_report.csv",
        "text/csv",
    )

elif page == "Customers":
    filtered = render_customer_filters(customers, "customers_page")
    st.subheader("Prioritized customer list")
    st.caption("Use the portfolio filters to narrow the report to the customers that matter for this task.")
    report_explanation(
        "How to read the customer report",
        "Each row represents one customer and combines current behaviour with Meridian's predictive assessment. "
        "Health and recency describe the customer's present condition, while purchase probability, churn probability and predicted 90-day spend describe what the model expects next. "
        "A high churn probability means the customer deserves retention review; a high predicted value means that customer may be commercially important even if their current activity looks average.",
        [
            "Sort or filter for high churn probability when the immediate goal is retention.",
            "Prioritise high predicted 90-day spend when the goal is protecting or growing future revenue.",
            "Use Customer ID in Predictive Engine for a complete individual report and recommended action.",
        ],
    )
    if filtered.empty:
        st.warning("No customers match the active filters.")
    else:
        priority_cols = [c for c in ["customer_id", "persona", "customer_tier", "health_score", "churn_risk", "predicted_churn_probability", "purchase_probability", "predicted_next_purchase_days", "predicted_90d_spend", "clv_estimate"] if c in filtered.columns]
        st.dataframe(filtered.sort_values(["churn_risk", "clv_estimate"], ascending=[False, False])[priority_cols], use_container_width=True, hide_index=True)
        st.download_button("Download customer intelligence CSV", filtered.to_csv(index=False).encode(), "customer_intelligence.csv", "text/csv")

elif page == "Predictive Engine":
    bundle = load_predictive_bundle()
    st.subheader("Predictive Engine")
    st.markdown(
        '<div class="predictive-callout"><strong>Predict a specific customer or a customer profile.</strong> '
        'Use Customer ID when the goal is an individual customer report, or use the filters to estimate the future behavior of a customer segment. '
        'The result is presented as a decision report; detailed charts are intentionally kept on the separate Customer Visuals page.</div>',
        unsafe_allow_html=True,
    )

    if not bundle.models:
        st.warning("Predictive models are not available. Run the analysis once with at least 20 customers.")
    else:
        st.markdown('<div class="section-label">Prediction target</div>', unsafe_allow_html=True)
        mode = st.radio(
            "Prediction target",
            ["Specific customer", "Customer profile from filters"],
            horizontal=True,
            key="prediction_target_mode",
            label_visibility="collapsed",
        )

        selected_customer = None
        cohort = pd.DataFrame()
        profile = None
        report_label = "Customer profile"

        if mode == "Specific customer":
            st.markdown('<div class="section-label">Customer lookup</div>', unsafe_allow_html=True)
            customer_ids = sorted(customers["customer_id"].astype(str).dropna().unique().tolist())
            selected_id = st.selectbox(
                "Customer ID",
                ["Select a customer ID"] + customer_ids,
                key="pred_customer_id",
                help="Type in the box to quickly find a customer ID.",
            )
            if selected_id != "Select a customer ID":
                matches = customers[customers["customer_id"].astype(str) == str(selected_id)].copy()
                if not matches.empty:
                    selected_customer = matches.iloc[0].copy()
                    profile = selected_customer[MODEL_FEATURES].replace([np.inf, -np.inf], np.nan).fillna(0).to_frame().T
                    cohort = matches
                    report_label = f"Customer {selected_id}"
        else:
            st.markdown('<div class="section-label">Customer definition filters</div>', unsafe_allow_html=True)
            p1, p2, p3, p4 = st.columns(4)
            with p1:
                pred_persona = st.selectbox("Persona", ["Any"] + sorted(customers.persona.dropna().unique().tolist()), key="pred_persona")
            with p2:
                pred_tier = st.selectbox("Customer tier", ["Any"] + sorted(customers.customer_tier.dropna().unique().tolist()), key="pred_tier")
            with p3:
                health_range = st.slider("Health score range", 0, 100, (0, 100), key="pred_health")
            with p4:
                recency_range = st.slider(
                    "Recency range (days)",
                    0,
                    max(30, int(customers.recency_days.max())),
                    (0, max(30, int(customers.recency_days.max()))),
                    key="pred_recency",
                )

            q1, q2, q3 = st.columns(3)
            with q1:
                frequency_range = st.slider(
                    "Frequency range", 1, max(2, int(customers.frequency.max())),
                    (1, max(2, int(customers.frequency.max()))), key="pred_frequency"
                )
            with q2:
                monetary_max = max(100.0, float(customers.monetary_value.max()))
                monetary_range = st.slider(
                    "Monetary value range", 0.0, monetary_max, (0.0, monetary_max), key="pred_monetary"
                )
            with q3:
                match_threshold = st.slider(
                    "Minimum matching customers", 1, min(25, len(customers)),
                    min(5, len(customers)), key="pred_min_match"
                )

            cohort = customers[
                (customers.health_score.between(*health_range))
                & (customers.recency_days.between(*recency_range))
                & (customers.frequency.between(*frequency_range))
                & (customers.monetary_value.between(*monetary_range))
            ].copy()
            if pred_persona != "Any":
                cohort = cohort[cohort.persona == pred_persona]
            if pred_tier != "Any":
                cohort = cohort[cohort.customer_tier == pred_tier]

            if len(cohort) >= match_threshold:
                profile = cohort[MODEL_FEATURES].replace([np.inf, -np.inf], np.nan).fillna(0).median().to_frame().T
                report_label = "Filtered customer profile"

        report_explanation(
            "How to read the prediction report",
            "The prediction report translates the customer's behavioural data into four forward-looking outcomes. "
            "Purchase probability estimates the likelihood of a near-term purchase, churn probability estimates the likelihood of disengagement, next-purchase timing estimates when another purchase may occur, and predicted 90-day spend estimates the customer's future monetary value. "
            "These are model estimates rather than guarantees. For an individual customer, the recommended action below connects the prediction to a practical business decision.",
            [
                "High churn + high value usually means retention should be prioritised quickly.",
                "High purchase probability can support timely engagement or cross-sell activity.",
                "Low probabilities across the board suggest monitoring rather than aggressive intervention.",
                "The Customer Visuals page is the place to investigate portfolio-level patterns behind these results.",
            ],
        )

        st.markdown('<div class="section-label">Prediction report</div>', unsafe_allow_html=True)

        if mode == "Specific customer" and selected_customer is None:
            st.info("Select a Customer ID above to generate the individual prediction report.")
        elif mode == "Customer profile from filters" and len(cohort) < match_threshold:
            st.warning(
                f"Only {len(cohort)} customer(s) match these filters. "
                "Relax the filters or lower the minimum matching-customer threshold."
            )
        else:
            purchase_p = float(bundle.models["purchase"].predict_proba(profile)[0, 1])
            churn_p = float(bundle.models["churn"].predict_proba(profile)[0, 1])
            next_days = max(1.0, float(bundle.models["next_purchase"].predict(profile)[0]))
            spend_90d = max(0.0, float(bundle.models["spending"].predict(profile)[0]))

            r1, r2, r3, r4, r5 = st.columns(5)
            # Never put a long identifier or descriptive phrase inside an
            # st.metric value: Streamlit truncates it when the column is
            # narrow. Show the actual Customer ID in full, or show the
            # cohort count when the report is filter-based.
            if mode == "Specific customer":
                r1.metric("Customer ID", str(selected_customer.get("customer_id", selected_id)))
            else:
                r1.metric("Matching customers", f"{len(cohort):,}")
            r2.metric("Purchase probability", f"{purchase_p:.1%}")
            r3.metric("Churn probability", f"{churn_p:.1%}")
            r4.metric("Predicted next purchase", f"{next_days:.0f} days")
            r5.metric("Predicted 90-day spend", f"${spend_90d:,.0f}")

            left, right = st.columns(2)
            with left:
                st.subheader("Predicted customer information")
                if mode == "Specific customer":
                    persona_value = str(selected_customer.get("persona", "—"))
                    tier_value = str(selected_customer.get("customer_tier", "—"))
                    info_rows = [
                        ("Customer ID", str(selected_customer.get("customer_id", "—"))),
                        ("Current persona", persona_value),
                        ("Current customer tier", tier_value),
                        ("Health score", f"{float(selected_customer.get('health_score', 0)):.1f}"),
                        ("Recency", f"{float(selected_customer.get('recency_days', 0)):.1f} days"),
                        ("Frequency", f"{float(selected_customer.get('frequency', 0)):.1f}"),
                        ("Monetary value", f"${float(selected_customer.get('monetary_value', 0)):,.2f}"),
                        ("Average order value", f"${float(selected_customer.get('avg_order_value', 0)):,.2f}"),
                        ("Tenure", f"{float(selected_customer.get('tenure_days', 0)):.1f} days"),
                        ("Purchase rate", f"{float(selected_customer.get('purchase_rate', 0)):.3f}"),
                        ("Return rate", f"{float(selected_customer.get('return_rate', 0)):.3f}"),
                        ("Product diversity", f"{float(selected_customer.get('product_diversity', 0)):.1f}"),
                    ]
                else:
                    info_rows = [
                        ("Predicted persona", cohort.persona.mode().iat[0] if not cohort.persona.mode().empty else "—"),
                        ("Predicted customer tier", cohort.customer_tier.mode().iat[0] if not cohort.customer_tier.mode().empty else "—"),
                        ("Typical health score", f"{cohort.health_score.median():.1f}"),
                        ("Typical recency", f"{profile.recency_days.iloc[0]:.1f} days"),
                        ("Typical frequency", f"{profile.frequency.iloc[0]:.1f}"),
                        ("Typical monetary value", f"${profile.monetary_value.iloc[0]:,.2f}"),
                        ("Typical average order value", f"${profile.avg_order_value.iloc[0]:,.2f}"),
                        ("Typical tenure", f"{profile.tenure_days.iloc[0]:.1f} days"),
                        ("Typical purchase rate", f"{profile.purchase_rate.iloc[0]:.3f}"),
                        ("Typical return rate", f"{profile.return_rate.iloc[0]:.3f}"),
                        ("Typical product diversity", f"{profile.product_diversity.iloc[0]:.1f}"),
                    ]
                predicted_info = pd.DataFrame(info_rows, columns=["Information", "Value"])
                st.dataframe(predicted_info, use_container_width=True, hide_index=True)

            with right:
                if mode == "Specific customer":
                    st.subheader("Customer prediction summary")
                    summary_rows = pd.DataFrame({
                        "Prediction": [
                            "Purchase probability", "Churn probability", "Predicted next purchase",
                            "Predicted 90-day spend", "Current churn risk", "Current CLV estimate",
                        ],
                        "Result": [
                            f"{purchase_p:.1%}", f"{churn_p:.1%}", f"{next_days:.0f} days",
                            f"${spend_90d:,.0f}",
                            f"{float(selected_customer.get('churn_risk', 0)):.1f}",
                            f"${float(selected_customer.get('clv_estimate', 0)):,.2f}",
                        ],
                    })
                    st.dataframe(summary_rows, use_container_width=True, hide_index=True)
                    st.caption("This report is based on the selected customer's current behavioral feature vector.")
                else:
                    st.subheader("Customers represented by the prediction")
                    sample_cols = [c for c in [
                        "customer_id", "persona", "customer_tier", "health_score", "recency_days",
                        "frequency", "monetary_value", "predicted_churn_probability", "predicted_90d_spend"
                    ] if c in cohort.columns]
                    st.dataframe(
                        cohort.sort_values("health_score", ascending=False)[sample_cols].head(25),
                        use_container_width=True,
                        hide_index=True,
                    )
                    st.caption("The report uses median behavioral features from the filtered cohort to create a representative customer profile.")

            st.markdown('<div class="section-label">Decision summary</div>', unsafe_allow_html=True)
            risk_level = "High" if churn_p >= 0.65 else "Moderate" if churn_p >= 0.35 else "Low"
            purchase_level = "High" if purchase_p >= 0.65 else "Moderate" if purchase_p >= 0.35 else "Low"
            decision_col1, decision_col2, decision_col3 = st.columns(3)
            decision_col1.metric("Churn risk level", risk_level)
            decision_col2.metric("Purchase likelihood", purchase_level)
            decision_col3.metric("Expected 90-day value", f"${spend_90d:,.0f}")
            if churn_p >= 0.65:
                st.warning("Retention should be prioritized: the model assigns a high probability of churn.")
            elif purchase_p >= 0.65:
                st.success("The customer profile shows strong near-term purchase potential.")
            else:
                st.info("The prediction is moderate. Use Customer Visuals for deeper portfolio-level context.")

            # For an individual lookup, surface the same portfolio-aware action
            # that appears in Campaigns so the user does not have to leave the
            # predictive report to find the recommended next step.
            if mode == "Specific customer" and selected_customer is not None:
                st.markdown('<div class="section-label">Recommended action for this customer</div>', unsafe_allow_html=True)
                customer_campaign = campaigns[
                    campaigns["customer_id"].astype(str) == str(selected_customer.get("customer_id", selected_id))
                ].copy() if "customer_id" in campaigns.columns else pd.DataFrame()

                if not customer_campaign.empty:
                    action_row = customer_campaign.iloc[0]
                    action = str(action_row.get("recommended_action", "Personalized product recommendation"))
                    offer = str(action_row.get("suggested_offer", "—"))
                    priority = str(action_row.get("priority", "Normal"))
                    action_priority = "High" if priority in {"Critical", "High"} else "Normal"

                    ac1, ac2, ac3 = st.columns([2.2, 2.2, 1])
                    ac1.markdown(
                        f'<div class="metric-card" style="--accent:#2F6B4E"><div class="metric-label">Recommended action</div>'
                        f'<div class="metric-value" style="font-size:1.45rem">{action}</div>'
                        f'<div class="metric-caption">Next best portfolio action</div></div>',
                        unsafe_allow_html=True,
                    )
                    ac2.markdown(
                        f'<div class="metric-card" style="--accent:#A9791F"><div class="metric-label">Suggested offer</div>'
                        f'<div class="metric-value" style="font-size:1.25rem">{offer}</div>'
                        f'<div class="metric-caption">Offer aligned to this customer portfolio</div></div>',
                        unsafe_allow_html=True,
                    )
                    ac3.metric("Campaign priority", action_priority)
                    st.caption(
                        "This recommendation is the customer-specific campaign action generated from the same portfolio record shown in Campaigns, "
                        "so the predictive report and campaign plan remain consistent."
                    )
                else:
                    st.info("No campaign recommendation is currently available for this customer.")

elif page == "Customer Visuals":
    # Visual-only customer intelligence page. The page deliberately avoids operational
    # tables and follows a business-first narrative: understand the portfolio, value,
    # behaviour, trends, predictive risk, markets, actions, then advanced analysis.
    filtered = render_customer_filters(customers, "visuals_page")

    st.subheader("Customer intelligence visual lab")
    st.markdown(
        '<div class="predictive-callout"><strong>See the customer base, not the numbers.</strong> '
        'Use the filters above to change every visual on this page. The charts answer the questions a business user asks first: '
        'who are the customers, where is the money, how do they behave, what is changing, who is at risk, and where are the opportunities?</div>',
        unsafe_allow_html=True,
    )

    if filtered.empty:
        st.warning("No customers match the selected filters. Select at least one persona and one customer tier.")
    else:
        # ──────────────────────────────────────────────────────────────────────
        # 1. PORTFOLIO AT A GLANCE
        # ──────────────────────────────────────────────────────────────────────
        st.markdown('<div class="section-label">Portfolio at a glance</div>', unsafe_allow_html=True)
        v1, v2, v3, v4 = st.columns(4)
        v1.metric("Customers represented", f"{len(filtered):,}")
        v2.metric("Revenue represented", f"${filtered['monetary_value'].sum():,.0f}")
        v3.metric("Average health", f"{filtered['health_score'].mean():.1f}/100")
        v4.metric("Average recency", f"{filtered['recency_days'].mean():.0f} days")

        # ──────────────────────────────────────────────────────────────────────
        # 2. WHO ARE THE CUSTOMERS?
        # ──────────────────────────────────────────────────────────────────────
        st.markdown('<div class="section-label">Who are the customers?</div>', unsafe_allow_html=True)
        v1, v2 = st.columns(2)
        with v1:
            st.subheader("Customers by tier")
            tier_counts = filtered["customer_tier"].value_counts().rename_axis("tier").reset_index(name="customers")
            st.plotly_chart(
                px.bar(
                    tier_counts,
                    x="tier", y="customers", text="customers",
                    labels={"tier": "Customer tier", "customers": "Customers"},
                    color="tier", color_discrete_map=TIER_COLORS, color_discrete_sequence=PALETTE,
                    template="meridian",
                ),
                use_container_width=True,
            )
            st.caption("Shows where the customer base is concentrated across value tiers.")
        with v2:
            st.subheader("Customer mix by persona")
            persona_counts = filtered["persona"].value_counts().rename_axis("persona").reset_index(name="customers")
            st.plotly_chart(
                px.pie(
                    persona_counts, names="persona", values="customers", hole=0.42,
                    color="persona", color_discrete_map=PERSONA_COLORS, color_discrete_sequence=PALETTE,
                    template="meridian",
                ),
                use_container_width=True,
            )
            st.caption("Shows the share of the portfolio represented by each customer behaviour type.")

        # ──────────────────────────────────────────────────────────────────────
        # 3. CUSTOMER VALUE
        # ──────────────────────────────────────────────────────────────────────
        st.markdown('<div class="section-label">Customer value</div>', unsafe_allow_html=True)
        v3, v4 = st.columns(2)
        with v3:
            st.subheader("Revenue by customer tier")
            tier_rev = (
                filtered.groupby("customer_tier", as_index=False)["monetary_value"]
                .sum().sort_values("monetary_value", ascending=False)
            )
            st.plotly_chart(
                px.bar(
                    tier_rev, x="customer_tier", y="monetary_value", text_auto=".2s",
                    labels={"customer_tier": "Customer tier", "monetary_value": "Revenue"},
                    color="customer_tier", color_discrete_map=TIER_COLORS, color_discrete_sequence=PALETTE,
                    template="meridian",
                ),
                use_container_width=True,
            )
            st.caption("Shows which customer tiers contribute the most money, not simply which tiers contain the most customers.")
        with v4:
            st.subheader("Spend by customer tier")
            st.plotly_chart(
                px.box(
                    filtered, x="customer_tier", y="monetary_value", color="customer_tier",
                    points="outliers",
                    labels={"customer_tier": "Customer tier", "monetary_value": "Customer spend"},
                    color_discrete_map=TIER_COLORS, color_discrete_sequence=PALETTE, template="meridian",
                ),
                use_container_width=True,
            )
            st.caption("Shows the typical spend and the variation in spend within each tier.")

        v5, v6 = st.columns(2)
        with v5:
            st.subheader("Spending distribution")
            st.plotly_chart(
                px.histogram(
                    filtered, x="monetary_value", nbins=25, marginal="box",
                    labels={"monetary_value": "Customer spend"},
                    color_discrete_sequence=[PALETTE[0]], template="meridian",
                ),
                use_container_width=True,
            )
            st.caption("Shows whether spending is broadly distributed or concentrated among a smaller group of customers.")
        with v6:
            st.subheader("Frequency of purchases")
            st.plotly_chart(
                px.violin(
                    filtered, x="customer_tier", y="frequency", color="customer_tier", box=True, points=False,
                    labels={"customer_tier": "Customer tier", "frequency": "Purchase frequency"},
                    color_discrete_map=TIER_COLORS, color_discrete_sequence=PALETTE, template="meridian",
                ),
                use_container_width=True,
            )
            st.caption("Shows how frequently customers purchase in each tier. Wider areas represent more customers at that frequency.")

        # ──────────────────────────────────────────────────────────────────────
        # 4. CUSTOMER BEHAVIOUR
        # ──────────────────────────────────────────────────────────────────────
        st.markdown('<div class="section-label">Customer behaviour</div>', unsafe_allow_html=True)
        v7, v8 = st.columns(2)
        with v7:
            st.subheader("Recency vs spending")
            st.plotly_chart(
                px.scatter(
                    filtered, x="recency_days", y="monetary_value", size="frequency", color="customer_tier",
                    hover_data=["customer_id", "persona", "health_score"],
                    labels={
                        "recency_days": "Days since last purchase",
                        "monetary_value": "Customer spend",
                        "frequency": "Purchase frequency",
                    },
                    color_discrete_map=TIER_COLORS, color_discrete_sequence=PALETTE, template="meridian",
                ),
                use_container_width=True,
            )
            st.caption("Customers farther right have gone longer without purchasing; higher points represent greater spend. High-value customers far right deserve attention.")
        with v8:
            st.subheader("Health vs churn risk")
            if "churn_risk" in filtered.columns:
                st.plotly_chart(
                    px.scatter(
                        filtered, x="health_score", y="churn_risk", color="persona", size="clv_estimate",
                        hover_data=["customer_id", "customer_tier", "predicted_90d_spend"],
                        labels={"health_score": "Customer health", "churn_risk": "Churn risk", "clv_estimate": "Estimated value"},
                        color_discrete_map=PERSONA_COLORS, color_discrete_sequence=PALETTE, template="meridian",
                    ),
                    use_container_width=True,
                )
                st.caption("The warning area is weaker customer health combined with higher churn risk. Larger points represent higher estimated value.")
            else:
                st.info("Churn-risk data is not available for this run.")

        # ──────────────────────────────────────────────────────────────────────
        # 5. TIME & RETENTION
        # ──────────────────────────────────────────────────────────────────────
        st.markdown('<div class="section-label">Time and retention</div>', unsafe_allow_html=True)
        v9, v10 = st.columns(2)
        with v9:
            st.subheader("Revenue over time")
            trend = monthly_revenue.copy()
            trend["month"] = pd.to_datetime(trend["month"])
            st.plotly_chart(
                px.line(
                    trend.sort_values("month"), x="month", y="revenue", markers=True,
                    labels={"month": "Month", "revenue": "Revenue"},
                    color_discrete_sequence=[PALETTE[0]], template="meridian",
                ),
                use_container_width=True,
            )
            st.caption("Shows whether captured revenue is growing, declining, or fluctuating over time.")
        with v10:
            st.subheader("Customer retention curve")
            if not retention.empty:
                retention_plot = retention.copy()
                st.plotly_chart(
                    px.line(
                        retention_plot, x="period", y="retention_rate", color="cohort_month", markers=True,
                        labels={
                            "period": "Months since first purchase",
                            "retention_rate": "Customers retained",
                            "cohort_month": "Starting month",
                        },
                        color_discrete_sequence=PALETTE, template="meridian",
                    ),
                    use_container_width=True,
                )
                st.caption("Shows how much of each customer cohort remains active as time passes. Higher curves indicate stronger retention.")
            else:
                st.info("Retention data is not available for this run.")

        # ──────────────────────────────────────────────────────────────────────
        # 6. PREDICTIVE CUSTOMER INTELLIGENCE
        # ──────────────────────────────────────────────────────────────────────
        st.markdown('<div class="section-label">Predictive customer intelligence</div>', unsafe_allow_html=True)
        v11, v12 = st.columns(2)
        with v11:
            st.subheader("Churn-risk distribution")
            st.plotly_chart(
                px.histogram(
                    filtered, x="predicted_churn_probability", nbins=20, marginal="box",
                    labels={"predicted_churn_probability": "Predicted churn probability"},
                    color_discrete_sequence=[PALETTE[0]], template="meridian",
                ),
                use_container_width=True,
            )
            st.caption("A concentration toward the right means more customers are predicted to be at higher risk of leaving.")
        with v12:
            st.subheader("Predicted 90-day spend")
            st.plotly_chart(
                px.histogram(
                    filtered, x="predicted_90d_spend", nbins=20, marginal="box",
                    labels={"predicted_90d_spend": "Predicted spend in next 90 days"},
                    color_discrete_sequence=[PALETTE[0]], template="meridian",
                ),
                use_container_width=True,
            )
            st.caption("Shows the expected spending range for the next 90 days across the selected customers.")

        st.subheader("Churn risk vs predicted value")
        st.plotly_chart(
            px.scatter(
                filtered,
                x="predicted_churn_probability", y="predicted_90d_spend",
                size="monetary_value", color="customer_tier",
                hover_data=["customer_id", "persona", "health_score", "recency_days"],
                labels={
                    "predicted_churn_probability": "Predicted churn probability",
                    "predicted_90d_spend": "Predicted 90-day spend",
                    "monetary_value": "Current spend",
                },
                color_discrete_map=TIER_COLORS, color_discrete_sequence=PALETTE, template="meridian",
            ),
            use_container_width=True,
        )
        st.caption("Top-left contains valuable customers with lower predicted churn; top-right contains valuable customers who may need retention action first.")

        # ──────────────────────────────────────────────────────────────────────
        # 7. PRODUCTS & MARKETS
        # ──────────────────────────────────────────────────────────────────────
        st.markdown('<div class="section-label">Products and markets</div>', unsafe_allow_html=True)
        v13, v14 = st.columns(2)
        with v13:
            st.subheader("Top products by revenue")
            if not top_products.empty:
                prod = top_products.sort_values("revenue", ascending=True).tail(15)
                st.plotly_chart(
                    px.bar(
                        prod, x="revenue", y="product", orientation="h", text_auto=".2s",
                        labels={"revenue": "Revenue", "product": "Product"},
                        color_discrete_sequence=[PALETTE[0]], template="meridian",
                    ),
                    use_container_width=True,
                )
                st.caption("Ranks the products generating the most revenue. Longer bars indicate stronger commercial contribution.")
            else:
                st.info("Product data is not available for this run.")
        with v14:
            st.subheader("Revenue by country")
            if not country_performance.empty:
                geo = country_performance.sort_values("revenue", ascending=True).tail(15)
                st.plotly_chart(
                    px.bar(
                        geo, x="revenue", y="country", orientation="h", text_auto=".2s",
                        labels={"revenue": "Revenue", "country": "Country"},
                        color_discrete_sequence=[PALETTE[0]], template="meridian",
                    ),
                    use_container_width=True,
                )
                st.caption("Shows which markets currently contribute the most revenue.")
            else:
                st.info("Country data is not available for this run.")

        # ──────────────────────────────────────────────────────────────────────
        # 8. WHO NEEDS ATTENTION?
        # ──────────────────────────────────────────────────────────────────────
        st.markdown('<div class="section-label">Who needs attention?</div>', unsafe_allow_html=True)
        risk_view = filtered.sort_values("predicted_churn_probability", ascending=False).head(10)
        value_view = filtered.sort_values("predicted_90d_spend", ascending=False).head(10)
        v15, v16 = st.columns(2)
        with v15:
            st.subheader("Highest predicted churn")
            st.plotly_chart(
                px.bar(
                    risk_view.sort_values("predicted_churn_probability"),
                    x="predicted_churn_probability", y="customer_id", orientation="h",
                    labels={"predicted_churn_probability": "Churn probability", "customer_id": "Customer"},
                    color_discrete_sequence=[PALETTE[0]], template="meridian",
                ),
                use_container_width=True,
            )
            st.caption("Customers with the strongest predicted likelihood of churn within the selected portfolio.")
        with v16:
            st.subheader("Highest predicted 90-day value")
            st.plotly_chart(
                px.bar(
                    value_view.sort_values("predicted_90d_spend"),
                    x="predicted_90d_spend", y="customer_id", orientation="h",
                    labels={"predicted_90d_spend": "Predicted 90-day spend", "customer_id": "Customer"},
                    color_discrete_sequence=[PALETTE[0]], template="meridian",
                ),
                use_container_width=True,
            )
            st.caption("Customers with the strongest predicted future spending potential.")

        # ──────────────────────────────────────────────────────────────────────
        # 9. ADVANCED CUSTOMER RELATIONSHIPS
        # ──────────────────────────────────────────────────────────────────────
        st.markdown('<div class="section-label">Advanced customer relationships</div>', unsafe_allow_html=True)
        st.subheader("Customer behavior relationship map")
        corr_candidates = [
            "recency_days", "frequency", "monetary_value", "avg_order_value", "tenure_days",
            "purchase_rate", "return_rate", "product_diversity", "health_score", "churn_risk",
            "predicted_churn_probability", "predicted_90d_spend", "clv_estimate",
        ]
        corr_cols = [c for c in corr_candidates if c in filtered.columns]
        if len(corr_cols) >= 2:
            corr = filtered[corr_cols].apply(pd.to_numeric, errors="coerce").corr()
            corr = corr.dropna(axis=0, how="all").dropna(axis=1, how="all")
            corr = corr.rename(columns={
                "recency_days": "Recency Days", "frequency": "Frequency", "monetary_value": "Monetary Value",
                "avg_order_value": "Avg Order Value", "tenure_days": "Tenure Days", "purchase_rate": "Purchase Rate",
                "return_rate": "Return Rate", "product_diversity": "Product Diversity", "health_score": "Health Score",
                "churn_risk": "Churn Risk", "predicted_churn_probability": "Predicted Churn Probability",
                "predicted_90d_spend": "Predicted 90D Spend", "clv_estimate": "CLV Estimate",
            })
            corr.index = corr.columns
            st.plotly_chart(
                px.imshow(
                    corr,
                    text_auto=".2f",
                    zmin=-1, zmax=1,
                    color_continuous_scale=[[0.0, "#34567A"], [0.5, "#EEF0EF"], [1.0, "#2F6B4E"]],
                    labels={"color": "Correlation"},
                    aspect="auto",
                    template="meridian",
                ),
                use_container_width=True,
            )
            st.caption("Advanced view: positive relationships move together, while negative relationships move in opposite directions. This is intended for deeper analysis rather than first-pass decision making.")
        else:
            st.info("Not enough numeric customer metrics are available to build the relationship map.")

        # Final plain-language interpretation. No table: the page remains visual.
        top_persona = filtered["persona"].value_counts().index[0]
        top_tier = filtered["customer_tier"].value_counts().index[0]
        avg_health = filtered["health_score"].mean()
        avg_recency = filtered["recency_days"].mean()
        st.markdown('<div class="section-label">What should a business user take away?</div>', unsafe_allow_html=True)
        st.info(
            f"The selected portfolio is concentrated in **{top_persona}** customers and **{top_tier}** tier. "
            f"Average health is **{avg_health:.1f}/100**, while customers are on average **{avg_recency:.0f} days** from their last purchase. "
            "Use the visuals to understand the portfolio pattern first, then use Customers, Predictive Engine, or Campaigns when an individual customer action is required."
        )

elif page == "Campaigns":
    st.subheader("Campaign decision engine")
    st.caption("Meridian separates customers into differentiated treatments instead of applying one offer to an entire risk group.")
    report_explanation(
        "How to read the campaign engine",
        "Campaign strategy is selected from customer value, churn risk, health, recency, frequency, tier, and persona. The goal is to protect high-value customers without unnecessarily discounting customers who are likely to return or grow organically.",
        [
            "Critical and High priorities should normally be reviewed first.",
            "Campaign strategy tells you which treatment Meridian selected.",
            "Suggested offer describes the commercial treatment, while the reason explains why it was selected.",
            "Opportunity score ranks where intervention is most commercially important; it is not a guaranteed response probability.",
        ],
    )

    # Portfolio allocation view: make the campaign mix visible before the customer-level table.
    strategy_counts = campaigns["campaign_strategy"].value_counts() if "campaign_strategy" in campaigns.columns else pd.Series(dtype=int)
    critical_count = int((campaigns.get("priority", pd.Series(index=campaigns.index)) == "Critical").sum())
    high_count = int((campaigns.get("priority", pd.Series(index=campaigns.index)) == "High").sum())
    incentive_count = int((campaigns.get("incentive_level", pd.Series(index=campaigns.index)) != "None").sum())
    no_incentive = int((campaigns.get("incentive_level", pd.Series(index=campaigns.index)) == "None").sum())

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Customers in campaign plan", f"{len(campaigns):,}")
    m2.metric("Critical", f"{critical_count:,}")
    m3.metric("High", f"{high_count:,}")
    m4.metric("No incentive required", f"{no_incentive:,}")

    st.markdown("### Campaign allocation")
    if not strategy_counts.empty:
        allocation = strategy_counts.rename_axis("Campaign").reset_index(name="Customers")
        allocation["Share"] = (allocation["Customers"] / max(len(campaigns), 1) * 100).round(1)
        st.dataframe(allocation, use_container_width=True, hide_index=True)

    st.markdown("### Customer-level campaign plan")
    f1, f2, f3 = st.columns(3)
    with f1:
        priority_options = ["All", *campaigns["priority"].dropna().unique().tolist()] if "priority" in campaigns else ["All"]
        priority_filter = st.selectbox("Priority", priority_options, key="campaign_priority_filter")
    with f2:
        strategy_options = ["All", *campaigns["campaign_strategy"].dropna().unique().tolist()] if "campaign_strategy" in campaigns else ["All"]
        strategy_filter = st.selectbox("Campaign", strategy_options, key="campaign_strategy_filter")
    with f3:
        incentive_options = ["All", *campaigns["incentive_level"].dropna().unique().tolist()] if "incentive_level" in campaigns else ["All"]
        incentive_filter = st.selectbox("Incentive level", incentive_options, key="campaign_incentive_filter")

    campaign_view = campaigns.copy()
    if priority_filter != "All" and "priority" in campaign_view:
        campaign_view = campaign_view[campaign_view["priority"] == priority_filter]
    if strategy_filter != "All" and "campaign_strategy" in campaign_view:
        campaign_view = campaign_view[campaign_view["campaign_strategy"] == strategy_filter]
    if incentive_filter != "All" and "incentive_level" in campaign_view:
        campaign_view = campaign_view[campaign_view["incentive_level"] == incentive_filter]

    display_columns = [
        "customer_id", "persona", "customer_tier", "priority", "campaign_strategy",
        "recommended_action", "suggested_offer", "recommended_channel", "incentive_level",
        "campaign_reason", "campaign_opportunity_score", "churn_risk", "clv_estimate", "predicted_90d_spend",
    ]
    display_columns = [column for column in display_columns if column in campaign_view.columns]
    st.dataframe(campaign_view[display_columns], use_container_width=True, hide_index=True)
    st.download_button(
        "Download campaign plan CSV",
        campaign_view.to_csv(index=False).encode(),
        "campaign_plan.csv",
        "text/csv",
    )

elif page == "Sales Planning":
    st.subheader("Sales planning report")
    st.caption("Use the forecast, retention, and market reports to plan revenue allocation and commercial attention.")
    report_explanation(
        "How to read the sales planning report",
        "The forecast table estimates future revenue, the retention table shows whether customer cohorts are remaining active, and the market table shows where revenue is currently concentrated. "
        "Together, these reports answer three planning questions: how much revenue may be coming, whether the customer base is staying engaged, and where commercial attention is currently concentrated.",
        [
            "Use the forecast horizon and average monthly forecast for high-level revenue planning.",
            "Compare starting customers with latest active customers to understand cohort retention.",
            "Use revenue share to identify markets that currently have the greatest commercial weight.",
            "Use Customer Visuals when you need to investigate the trend or distribution behind a planning result.",
        ],
    )
    st.markdown(
        "This page is designed as a planning report rather than a chart dashboard. "
        "Use the forecast table for expected revenue, the retention table for cohort health, and the market table for allocation decisions."
    )

    forecast_report = forecast.copy()
    if not forecast_report.empty:
        forecast_report["month"] = pd.to_datetime(forecast_report["month"]).dt.strftime("%b %Y")
        forecast_report["forecast_revenue"] = forecast_report["forecast_revenue"].round(2)
        forecast_report = forecast_report.rename(columns={
            "month":"Forecast month", "forecast_revenue":"Forecast revenue", "method":"Forecast method"
        })

        total_forecast = float(forecast["forecast_revenue"].sum()) if "forecast_revenue" in forecast else 0.0
        avg_forecast = float(forecast["forecast_revenue"].mean()) if "forecast_revenue" in forecast else 0.0
        peak_row = forecast.loc[forecast["forecast_revenue"].idxmax()] if not forecast.empty else None
        peak_month = pd.to_datetime(peak_row["month"]).strftime("%b %Y") if peak_row is not None else "—"

        a, b, c = st.columns(3)
        a.metric("Forecast horizon value", f"${total_forecast:,.0f}")
        b.metric("Average monthly forecast", f"${avg_forecast:,.0f}")
        c.metric("Highest forecast month", peak_month)

        st.markdown('<div class="section-label">Revenue forecast</div>', unsafe_allow_html=True)
        st.dataframe(forecast_report, use_container_width=True, hide_index=True)
    else:
        st.info("A sales forecast is not available for this run.")

    st.markdown('<div class="section-label">Retention planning report</div>', unsafe_allow_html=True)
    if retention.empty:
        st.info("Cohort retention data is not available for this run.")
    else:
        retention_report = retention.copy()
        cohort_summary = (
            retention_report.sort_values(["cohort_month", "period"])
            .groupby("cohort_month", as_index=False)
            .agg(
                starting_customers=("active_customers", "first"),
                latest_customers=("active_customers", "last"),
                latest_retention=("retention_rate", "last"),
                observed_periods=("period", "max"),
            )
        )
        cohort_summary["latest_retention"] = cohort_summary["latest_retention"].round(1).astype(str) + "%"
        cohort_summary = cohort_summary.rename(columns={
            "cohort_month":"Cohort month", "starting_customers":"Starting customers",
            "latest_customers":"Latest active customers", "latest_retention":"Latest retention",
            "observed_periods":"Observed periods"
        })
        st.dataframe(cohort_summary, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-label">Market planning report</div>', unsafe_allow_html=True)
    if not country_performance.empty:
        market_report = country_performance.sort_values("revenue", ascending=False).copy()
        market_report["revenue"] = market_report["revenue"].round(2)
        market_report["revenue_share"] = (market_report["revenue"] / market_report["revenue"].sum() * 100).round(1).astype(str) + "%"
        market_report = market_report.rename(columns={
            "country":"Country", "revenue":"Revenue", "orders":"Orders", "revenue_share":"Revenue share"
        })
        st.dataframe(market_report, use_container_width=True, hide_index=True)
    else:
        st.info("Country-level sales data is not available for this run.")

    st.download_button(
        "Download sales planning report",
        forecast_report.to_csv(index=False).encode() if not forecast_report.empty else b"",
        "meridian_sales_planning_report.csv",
        "text/csv",
    )

elif page == "Data Quality":
    st.subheader("Automatic data-quality report")
    report_explanation(
        "How to read the data-quality report",
        "This report tells you whether the uploaded transaction data is reliable enough to support the downstream analysis. "
        "The quality table describes what was observed in the input and the cleaned column profile describes the resulting analytical dataset. "
        "A clean report does not mean the business data is perfect; it means the pipeline has applied its defined validation and cleaning rules successfully.",
        [
            "Pay attention to rows removed during cleaning because large removals can materially change the analysis.",
            "Check required columns and data types before interpreting ML results.",
            "Treat returns and unusual values as business information unless there is evidence they are data errors.",
            "If quality problems are substantial, fix the source data before relying on the predictive outputs.",
        ],
    )
    raw_rows = len(st.session_state.active_analysis.get("raw_data", transactions)) if isinstance(st.session_state.get("active_analysis"), dict) else len(transactions)
    st.caption(f"Source: **{active_dataset_label()}** · {raw_rows:,} raw rows → {len(transactions):,} cleaned transaction rows. The report below is generated from this exact active dataset, not from the demo database.")
    active_mapping = st.session_state.active_analysis.get("mapping", {}) if isinstance(st.session_state.get("active_analysis"), dict) else {}
    if active_mapping:
        st.subheader("Confirmed column mapping")
        st.dataframe(pd.DataFrame([{"Your column": source, "Meridian field": target.replace("_", " ").title()} for source, target in active_mapping.items()]), use_container_width=True, hide_index=True)
    st.dataframe(quality, use_container_width=True, hide_index=True)
    if not cleaning_audit.empty:
        st.subheader("Cleaning actions performed")
        st.dataframe(cleaning_audit, use_container_width=True, hide_index=True)
    st.subheader("Cleaned dataset column profile")
    st.dataframe(column_profile, use_container_width=True, hide_index=True)
    st.download_button("Download cleaned transactions CSV", transactions.to_csv(index=False).encode(), "cleaned_transactions.csv", "text/csv")

elif page == "Model Trust":
    st.subheader("Model trust report")
    report_explanation(
        "How to read the model trust report",
        "This page is evidence about model behaviour, not a claim that every prediction is correct. "
        "For classification, higher accuracy and ROC-AUC generally indicate stronger discrimination; for regression, lower MAE means predictions are closer to observed values. "
        "Clustering quality is interpreted separately because segmentation is unsupervised. The current predictive prototype also uses proxy targets for some outcomes, so production decisions should be validated against genuine future-period labels.",
        [
            "Do not interpret a single metric in isolation; compare it with the business cost of false positives and false negatives.",
            "Remember that in-sample regression metrics can look better than performance on unseen future customers.",
            "Use feature importance to understand model reliance, not to claim that a feature causes the outcome.",
            "Use the Data Quality page alongside this report because poor input data can undermine otherwise strong model metrics.",
        ],
    )
    st.markdown(
        "This page reports whether the analytical and predictive components are behaving credibly. "
        "Detailed visual diagnostics remain on Customer Visuals; this page focuses on metrics, thresholds, and interpretation."
    )

    pm = prediction_metrics(summary)
    if pm:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Purchase accuracy", pm.get("purchase_accuracy", "—"))
        m2.metric("Purchase ROC-AUC", pm.get("purchase_auc", "—"))
        m3.metric("Next-purchase MAE", pm.get("next_purchase_mae_in_sample", "—"))
        m4.metric("Spending MAE", pm.get("spending_mae_in_sample", "—"))

        trust_rows = []
        for label, key, direction in [
            ("Purchase accuracy", "purchase_accuracy", "Higher is better"),
            ("Purchase ROC-AUC", "purchase_auc", "Higher is better; 0.50 is weak discrimination"),
            ("Next-purchase MAE", "next_purchase_mae_in_sample", "Lower is better"),
            ("Spending MAE", "spending_mae_in_sample", "Lower is better"),
        ]:
            trust_rows.append({"Metric": label, "Result": pm.get(key, "—"), "Interpretation": direction})
        st.markdown('<div class="section-label">Predictive evaluation</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(trust_rows), use_container_width=True, hide_index=True)
    else:
        st.info("Predictive evaluation metrics will be persisted the next time an analysis run is completed.")

    st.markdown('<div class="section-label">Clustering quality report</div>', unsafe_allow_html=True)
    if not evaluation.empty:
        eval_report = evaluation.copy()
        for col in ["silhouette", "davies_bouldin", "calinski_harabasz", "noise_ratio"]:
            if col in eval_report:
                eval_report[col] = eval_report[col].round(3)
        eval_report = eval_report.rename(columns={
            "silhouette":"Silhouette", "davies_bouldin":"Davies-Bouldin",
            "calinski_harabasz":"Calinski-Harabasz", "n_clusters":"Clusters",
            "noise_ratio":"Noise ratio", "method":"Method", "parameter":"Parameter"
        })
        st.dataframe(eval_report, use_container_width=True, hide_index=True)
        best = evaluation.sort_values("silhouette", ascending=False).iloc[0]
        st.caption(
            f"Best observed clustering configuration: {best['method']} with {int(best['n_clusters'])} clusters "
            f"and silhouette score {best['silhouette']:.3f}. Higher silhouette and lower Davies-Bouldin generally indicate cleaner separation."
        )
    else:
        st.info("Clustering evaluation is not available for this run.")

    st.markdown('<div class="section-label">Model explanation report</div>', unsafe_allow_html=True)
    if not explanations.empty:
        explanation_report = explanations.copy()
        explanation_report["importance"] = explanation_report["importance"].round(4)
        explanation_report["importance_share"] = (
            explanation_report.groupby("model")["importance"].transform(lambda x: x / x.sum() * 100).round(1).astype(str) + "%"
        )
        explanation_report = explanation_report.sort_values(["model", "importance"], ascending=[True, False])
        explanation_report = explanation_report.rename(columns={
            "model":"Model", "feature":"Feature", "importance":"Importance", "importance_share":"Within-model share"
        })
        st.dataframe(explanation_report, use_container_width=True, hide_index=True)
        top_drivers = (
            explanations.sort_values("importance", ascending=False)
            .groupby("model", as_index=False)
            .first()
            .rename(columns={"model":"Model", "feature":"Primary driver", "importance":"Importance"})
        )
        top_drivers["Importance"] = top_drivers["Importance"].round(4)
        st.markdown("**Primary model drivers**")
        st.dataframe(top_drivers, use_container_width=True, hide_index=True)
    else:
        st.info("Model explanation data is not available for this run.")

    st.markdown('<div class="section-label">Trust notes</div>', unsafe_allow_html=True)
    st.markdown("""
- **Accuracy / ROC-AUC:** describe classification discrimination; higher is generally stronger.
- **MAE:** measures the average size of prediction errors; lower is better.
- **Clustering scores:** assess whether customer segments are internally coherent and separated from one another.
- **Feature importance:** identifies which input variables the trained models relied on most; it does not establish causation.
- Re-run the analysis when the source data or customer behavior changes materially.
""")
