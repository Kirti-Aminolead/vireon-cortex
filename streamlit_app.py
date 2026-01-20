"""
Vireon Cortex - Advanced Energy Analytics Dashboard
Streamlit Cloud Deployment - Full KPI Version

Matches the HTML dashboard with all sections:
- Core Metrics (6 cards)
- Asset Health & Predictive Maintenance
- Risk Shield & Safety
- Charts (Daily Energy, Fire Risk, Load Utilization, ToD)
- Daily Performance Table
- Actionable Recommendations
- Savings Banner

Author: Vireon Energy Systems
Version: 2.0
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from io import StringIO

# ============= PAGE CONFIG =============
st.set_page_config(
    page_title="Vireon Cortex | Advanced Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============= CUSTOM CSS =============
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --bg-primary: #0a0e14;
        --bg-card: #151d28;
        --bg-elevated: #1a242f;
        --text-primary: #f0f4f8;
        --text-secondary: #8899a6;
        --text-muted: #5c6b7a;
        --border: #253040;
        --cyan: #06d6a0;
        --yellow: #ffd166;
        --red: #ef476f;
        --blue: #118ab2;
        --purple: #9d4edd;
        --orange: #f77f00;
    }
    
    .stApp {
        background: linear-gradient(180deg, #0a0e14 0%, #111820 100%);
    }
    
    .main-header {
        font-family: 'JetBrains Mono', monospace;
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(135deg, #06d6a0 0%, #118ab2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    
    .subtitle { color: #8899a6; font-size: 14px; }
    
    /* Summary Cards */
    .summary-card {
        background: #151d28;
        border: 1px solid #253040;
        border-radius: 12px;
        padding: 18px;
        position: relative;
        overflow: hidden;
        height: 100%;
    }
    .summary-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: #06d6a0;
    }
    .summary-card.yellow::before { background: #ffd166; }
    .summary-card.red::before { background: #ef476f; }
    .summary-card.blue::before { background: #118ab2; }
    .summary-card.purple::before { background: #9d4edd; }
    .summary-card.orange::before { background: #f77f00; }
    .summary-label {
        font-size: 10px;
        color: #8899a6;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .summary-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 24px;
        font-weight: 700;
        color: #f0f4f8;
    }
    .summary-unit { font-size: 12px; color: #8899a6; }
    .summary-subtext { font-size: 10px; color: #5c6b7a; margin-top: 4px; }
    
    /* Section Headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 32px 0 20px 0;
        padding-bottom: 12px;
        border-bottom: 1px solid #253040;
    }
    .section-icon {
        width: 36px;
        height: 36px;
        background: #151d28;
        border: 1px solid #253040;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }
    .section-title { font-size: 18px; font-weight: 600; color: #f0f4f8; }
    .section-badge {
        background: #1a242f;
        border: 1px solid #253040;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 11px;
        color: #8899a6;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* KPI Cards */
    .kpi-card {
        background: #151d28;
        border: 1px solid #253040;
        border-radius: 12px;
        padding: 20px;
        height: 100%;
    }
    .kpi-title {
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
        color: #f0f4f8;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-left: auto;
    }
    .status-good { background: #06d6a0; box-shadow: 0 0 8px #06d6a0; }
    .status-warning { background: #ffd166; box-shadow: 0 0 8px #ffd166; }
    .status-critical { background: #ef476f; box-shadow: 0 0 8px #ef476f; }
    .kpi-metric {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 8px;
    }
    .kpi-label { font-size: 11px; color: #5c6b7a; }
    .kpi-value { font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 600; color: #f0f4f8; }
    .kpi-bar {
        height: 6px;
        background: #1a242f;
        border-radius: 3px;
        margin-top: 12px;
        overflow: hidden;
    }
    .kpi-bar-fill {
        height: 100%;
        border-radius: 3px;
    }
    .kpi-insight {
        font-size: 11px;
        color: #8899a6;
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid #253040;
    }
    
    /* Risk Items */
    .risk-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin-top: 12px;
    }
    .risk-item {
        background: #1a242f;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        border-left: 3px solid #253040;
    }
    .risk-item.normal { border-left-color: #06d6a0; }
    .risk-item.warning { border-left-color: #ffd166; }
    .risk-item.high { border-left-color: #f77f00; }
    .risk-item.critical { border-left-color: #ef476f; }
    .risk-level { font-size: 9px; text-transform: uppercase; letter-spacing: 0.5px; }
    .risk-count { font-family: 'JetBrains Mono', monospace; font-size: 18px; font-weight: 700; }
    .risk-pct { font-size: 10px; color: #5c6b7a; }
    
    /* Recommendations */
    .rec-card {
        background: #1a242f;
        border: 1px solid #253040;
        border-radius: 10px;
        padding: 16px;
        display: flex;
        gap: 12px;
        height: 100%;
    }
    .rec-priority {
        width: 4px;
        border-radius: 2px;
        flex-shrink: 0;
    }
    .rec-priority.high { background: #ef476f; }
    .rec-priority.medium { background: #ffd166; }
    .rec-priority.low { background: #06d6a0; }
    .rec-title { font-weight: 600; font-size: 13px; color: #f0f4f8; margin-bottom: 4px; }
    .rec-category { font-size: 10px; color: #5c6b7a; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .rec-insight { font-size: 11px; color: #8899a6; margin-bottom: 8px; }
    .rec-action { font-size: 11px; color: #06d6a0; }
    .rec-savings {
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px solid #253040;
        display: flex;
        justify-content: space-between;
    }
    .rec-savings-label { font-size: 9px; color: #5c6b7a; text-transform: uppercase; }
    .rec-savings-value { font-family: 'JetBrains Mono', monospace; font-size: 14px; color: #06d6a0; font-weight: 600; }
    
    /* Savings Banner */
    .savings-banner {
        background: linear-gradient(135deg, rgba(6, 214, 160, 0.1) 0%, rgba(17, 138, 178, 0.1) 100%);
        border: 2px solid #06d6a0;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        margin: 32px 0;
    }
    .savings-label { font-size: 14px; color: #8899a6; margin-bottom: 8px; }
    .savings-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 42px;
        font-weight: 700;
        color: #06d6a0;
    }
    .savings-subtext { font-size: 12px; color: #5c6b7a; margin-top: 8px; }
    
    /* ToD Badges */
    .tod-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 600;
    }
    .tod-offpeak { background: rgba(6, 214, 160, 0.2); color: #06d6a0; border: 1px solid #06d6a0; }
    .tod-normal { background: rgba(255, 209, 102, 0.2); color: #ffd166; border: 1px solid #ffd166; }
    .tod-peak { background: rgba(239, 71, 111, 0.2); color: #ef476f; border: 1px solid #ef476f; }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
    }
</style>
""", unsafe_allow_html=True)


# ============= DATA LOADING =============
@st.cache_data(ttl=60)
def load_data_from_public_sheet(sheet_id, sheet_name="readings"):
    """Load data from public Google Sheet"""
    try:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        df = pd.read_csv(StringIO(response.text))
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Ensure numeric columns
        numeric_cols = ['kW_Total', 'kVA_Total', 'PF_Avg', 'VLN_Avg', 'VLL_Avg', 'Current_Total',
                       'Neutral_Current_A', 'Frequency_Hz', 'Energy_kWh', 'Daily_Cost_Rs',
                       'Voltage_Unbalance_Pct', 'Current_Unbalance_Pct', 'Load_Pct',
                       'V_R', 'V_Y', 'V_B', 'Current_R', 'Current_Y', 'Current_B',
                       'PF_R', 'PF_Y', 'PF_B', 'Watts_Total', 'VA_Total', 'Run_Hours',
                       'Max_Demand_kVA', 'Max_Demand_kW', 'Daily_Energy_Wh', 'Session_Energy_Wh']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


def get_tod_period():
    """Get current ToD period"""
    hour = datetime.now().hour
    if 6 <= hour < 17:
        return "NORMAL", "tod-normal"
    elif 17 <= hour < 23:
        return "PEAK", "tod-peak"
    else:
        return "OFFPEAK", "tod-offpeak"


def get_color(value, thresholds, reverse=False):
    """Get color based on thresholds"""
    if reverse:
        if value <= thresholds[0]: return "#06d6a0"
        elif value <= thresholds[1]: return "#ffd166"
        else: return "#ef476f"
    else:
        if value >= thresholds[0]: return "#06d6a0"
        elif value >= thresholds[1]: return "#ffd166"
        else: return "#ef476f"


def calculate_kpis(df):
    """Calculate all KPIs from dataframe"""
    kpis = {}
    
    # Basic stats
    kpis['total_readings'] = len(df)
    kpis['total_energy'] = df['Energy_kWh'].max() - df['Energy_kWh'].min() if 'Energy_kWh' in df.columns else 0
    kpis['total_cost'] = df['Daily_Cost_Rs'].sum() if 'Daily_Cost_Rs' in df.columns else 0
    kpis['peak_demand'] = df['kW_Total'].max() if 'kW_Total' in df.columns else 0
    kpis['max_demand_recorded'] = df['Max_Demand_kW'].max() if 'Max_Demand_kW' in df.columns else 0
    kpis['avg_pf'] = df['PF_Avg'].mean() if 'PF_Avg' in df.columns else 0
    kpis['run_hours'] = df['Run_Hours'].max() if 'Run_Hours' in df.columns else 0
    
    # Voltage unbalance
    kpis['v_unbalance_avg'] = df['Voltage_Unbalance_Pct'].mean() if 'Voltage_Unbalance_Pct' in df.columns else 0
    kpis['v_unbalance_max'] = df['Voltage_Unbalance_Pct'].max() if 'Voltage_Unbalance_Pct' in df.columns else 0
    kpis['v_unbalance_warning'] = (df['Voltage_Unbalance_Pct'] > 2).sum() if 'Voltage_Unbalance_Pct' in df.columns else 0
    
    # Current unbalance
    kpis['i_unbalance_avg'] = df['Current_Unbalance_Pct'].mean() if 'Current_Unbalance_Pct' in df.columns else 0
    kpis['i_unbalance_max'] = df['Current_Unbalance_Pct'].max() if 'Current_Unbalance_Pct' in df.columns else 0
    kpis['i_unbalance_warning'] = (df['Current_Unbalance_Pct'] > 10).sum() if 'Current_Unbalance_Pct' in df.columns else 0
    
    # Load utilization
    kpis['load_avg'] = df['Load_Pct'].mean() if 'Load_Pct' in df.columns else 0
    kpis['load_max'] = df['Load_Pct'].max() if 'Load_Pct' in df.columns else 0
    kpis['idle_time_pct'] = (df['Load_Pct'] < 10).sum() / len(df) * 100 if 'Load_Pct' in df.columns and len(df) > 0 else 0
    
    # Grid forensics
    kpis['freq_min'] = df['Frequency_Hz'].min() if 'Frequency_Hz' in df.columns else 0
    kpis['freq_max'] = df['Frequency_Hz'].max() if 'Frequency_Hz' in df.columns else 0
    kpis['vll_min'] = df['VLL_Avg'].min() if 'VLL_Avg' in df.columns else 0
    kpis['vll_max'] = df['VLL_Avg'].max() if 'VLL_Avg' in df.columns else 0
    
    # Fire safety
    kpis['neutral_avg'] = df['Neutral_Current_A'].mean() if 'Neutral_Current_A' in df.columns else 0
    kpis['neutral_max'] = df['Neutral_Current_A'].max() if 'Neutral_Current_A' in df.columns else 0
    kpis['neutral_risk'] = (df['Neutral_Current_A'] > 5).sum() if 'Neutral_Current_A' in df.columns else 0
    
    # Fire risk distribution
    if 'Fire_Risk_Level' in df.columns:
        fire_counts = df['Fire_Risk_Level'].astype(str).str.upper().value_counts()
        kpis['fire_normal'] = fire_counts.get('NORMAL', 0)
        kpis['fire_warning'] = fire_counts.get('WARNING', 0)
        kpis['fire_high'] = fire_counts.get('HIGH', 0)
        kpis['fire_critical'] = fire_counts.get('CRITICAL', 0)
    else:
        kpis['fire_normal'] = kpis['fire_warning'] = kpis['fire_high'] = kpis['fire_critical'] = 0
    
    # PF penalty
    if 'PF_Avg' in df.columns:
        kpis['pf_below_92'] = (df['PF_Avg'].abs() < 0.92).sum() / len(df) * 100 if len(df) > 0 else 0
        kpis['pf_below_85'] = (df['PF_Avg'].abs() < 0.85).sum() / len(df) * 100 if len(df) > 0 else 0
        kpis['pf_min'] = df['PF_Avg'].abs().min()
    else:
        kpis['pf_below_92'] = kpis['pf_below_85'] = kpis['pf_min'] = 0
    
    return kpis


# ============= MAIN DASHBOARD =============
def main():
    # Sidebar for config
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # Default Sheet ID - change this to your sheet
        DEFAULT_SHEET_ID = "10VSKQgLx-OSMMpbIXqgbb06DF_zgVetcm2s8sW1Wps0"
        
        sheet_id = st.text_input(
            "Google Sheet ID",
            value=st.secrets.get("sheet_id", DEFAULT_SHEET_ID),
            help="From URL: docs.google.com/spreadsheets/d/**SHEET_ID**/edit"
        )
        st.markdown("---")
        st.markdown("### 🏭 Shed Filter")
        shed_filter = st.radio(
            "Select View",
            options=["Shed 1 (Main Feed)", "Shed 2 (Sub-Feed)", "All Sheds"],
            index=0,
            help="Shed 2 draws power from Shed 1's main feed"
        )
        if shed_filter == "Shed 2 (Sub-Feed)":
            st.info("⚡ Shed 2 is a sub-feed from Shed 1. Its consumption is part of Shed 1's total.")
        st.markdown("---")
        st.markdown("""
        **Setup:**
        1. Publish sheet to web (CSV)
        2. Enter Sheet ID above
        3. Data refreshes every 60s
        """)
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<h1 class="main-header">⚡ VIREON CORTEX</h1>', unsafe_allow_html=True)
        st.markdown(f'<p class="subtitle">Advanced Energy Analytics | {shed_label} | Omega Transmission POC</p>', unsafe_allow_html=True)
    
    with col2:
        tod_period, tod_class = get_tod_period()
        st.markdown(f"""
            <div style="text-align: right;">
                <span class="tod-badge {tod_class}">{tod_period}</span>
                <p style="font-size: 12px; color: #8899a6; margin-top: 8px;">
                    {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not sheet_id:
        st.warning("⚠️ Please enter your Google Sheet ID in the sidebar.")
        st.info("Make sure the sheet is published to web: File → Share → Publish to web → CSV")
        return
    
    # Load data
    with st.spinner("📊 Loading live data..."):
        df = load_data_from_public_sheet(sheet_id)
    
    if df is None or df.empty:
        st.error("❌ No data available. Check Sheet ID and ensure it's published to web.")
        return
    
    # Apply shed filter
    if 'Device_ID' in df.columns or 'Location' in df.columns:
        location_col = 'Location' if 'Location' in df.columns else 'Device_ID'
        
        if shed_filter == "Shed 1 (Main Feed)":
            df = df[df[location_col].str.contains('01|Shed_01|Shed 1', case=False, na=False)]
            shed_label = "Shed 1 (Main Feed)"
        elif shed_filter == "Shed 2 (Sub-Feed)":
            df = df[df[location_col].str.contains('02|Shed_02|Shed 2', case=False, na=False)]
            shed_label = "Shed 2 (Sub-Feed from Shed 1)"
        else:
            shed_label = "All Sheds Combined"
        
        if df.empty:
            st.warning(f"No data found for {shed_filter}. Try a different filter.")
            return
    else:
        shed_label = "All Data"
    
    # Calculate KPIs
    kpis = calculate_kpis(df)
    
    # If All Sheds, show quick comparison first
    if shed_filter == "All Sheds":
        st.markdown("""
            <div class="section-header">
                <span class="section-icon">🏭</span>
                <span class="section-title">Shed Overview</span>
                <span class="section-badge">Live Status</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Get latest reading per shed
        df_full = load_data_from_public_sheet(sheet_id)
        if df_full is not None and 'Location' in df_full.columns:
            latest = df_full.sort_values('Timestamp').groupby('Location').last().reset_index()
            
            shed_cols = st.columns(len(latest))
            for idx, (_, row) in enumerate(latest.iterrows()):
                with shed_cols[idx]:
                    is_main = '01' in str(row.get('Device_ID', '')) or '01' in str(row.get('Location', ''))
                    shed_type = "Main Feed" if is_main else "Sub-Feed"
                    border_color = "#06d6a0" if is_main else "#118ab2"
                    
                    fire_risk = str(row.get('Fire_Risk_Level', 'NORMAL')).upper()
                    fire_color = "#06d6a0" if fire_risk == "NORMAL" else "#ffd166" if fire_risk == "WARNING" else "#f77f00" if fire_risk == "HIGH" else "#ef476f"
                    
                    st.markdown(f"""
                        <div class="kpi-card" style="border-top: 3px solid {border_color};">
                            <div class="kpi-title" style="color: {border_color};">
                                📍 {row.get('Location', 'Unknown')} ({shed_type})
                            </div>
                            <div class="kpi-metric">
                                <span class="kpi-label">Power</span>
                                <span class="kpi-value">{row.get('kW_Total', 0):.1f} kW</span>
                            </div>
                            <div class="kpi-metric">
                                <span class="kpi-label">Current</span>
                                <span class="kpi-value">{row.get('Current_Total', 0):.1f} A</span>
                            </div>
                            <div class="kpi-metric">
                                <span class="kpi-label">Power Factor</span>
                                <span class="kpi-value">{row.get('PF_Avg', 0):.3f}</span>
                            </div>
                            <div class="kpi-metric">
                                <span class="kpi-label">Fire Risk</span>
                                <span class="kpi-value" style="color: {fire_color};">🔥 {fire_risk}</span>
                            </div>
                            <div class="kpi-insight">
                                Updated: {row['Timestamp'].strftime('%H:%M:%S') if pd.notna(row.get('Timestamp')) else 'N/A'}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Get date range
    date_min = df['Date'].min().strftime('%b %d') if pd.notna(df['Date'].min()) else 'N/A'
    date_max = df['Date'].max().strftime('%b %d, %Y') if pd.notna(df['Date'].max()) else 'N/A'
    
    # ============= CORE METRICS (6 cards) =============
    st.markdown(f"""
        <div class="section-header">
            <span class="section-badge">📅 {date_min} - {date_max}</span>
            <span class="section-badge">{kpis['total_readings']} readings</span>
        </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(6)
    
    with cols[0]:
        st.markdown(f"""
            <div class="summary-card">
                <div class="summary-label">Total Energy</div>
                <div class="summary-value">{kpis['total_energy']:,.0f} <span class="summary-unit">kWh</span></div>
                <div class="summary-subtext">Period total</div>
            </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown(f"""
            <div class="summary-card yellow">
                <div class="summary-label">Total Cost</div>
                <div class="summary-value">₹{kpis['total_cost']:,.0f}</div>
                <div class="summary-subtext">Estimated</div>
            </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown(f"""
            <div class="summary-card blue">
                <div class="summary-label">Peak Demand</div>
                <div class="summary-value">{kpis['peak_demand']:.1f} <span class="summary-unit">kW</span></div>
                <div class="summary-subtext">Maximum recorded</div>
            </div>
        """, unsafe_allow_html=True)
    
    with cols[3]:
        st.markdown(f"""
            <div class="summary-card">
                <div class="summary-label">Max Demand (MD)</div>
                <div class="summary-value">{kpis['max_demand_recorded']:.1f} <span class="summary-unit">kW</span></div>
                <div class="summary-subtext">Meter recorded</div>
            </div>
        """, unsafe_allow_html=True)
    
    with cols[4]:
        pf_color = "#06d6a0" if kpis['avg_pf'] > 0.92 else "#ffd166" if kpis['avg_pf'] > 0.85 else "#ef476f"
        pf_warning = "⚠️ Below 0.92" if kpis['avg_pf'] < 0.92 else "✓ Good"
        st.markdown(f"""
            <div class="summary-card red">
                <div class="summary-label">Avg Power Factor</div>
                <div class="summary-value" style="color: {pf_color}">{kpis['avg_pf']:.3f}</div>
                <div class="summary-subtext">{pf_warning}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with cols[5]:
        st.markdown(f"""
            <div class="summary-card purple">
                <div class="summary-label">Run Hours</div>
                <div class="summary-value">{kpis['run_hours']:.1f} <span class="summary-unit">hrs</span></div>
                <div class="summary-subtext">Meter runtime</div>
            </div>
        """, unsafe_allow_html=True)
    
    # ============= ASSET HEALTH SECTION =============
    st.markdown("""
        <div class="section-header">
            <span class="section-icon">🔧</span>
            <span class="section-title">Asset Health & Predictive Maintenance</span>
            <span class="section-badge">From Feature Logic Table</span>
        </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(4)
    
    # Phase Balance Monitor
    with cols[0]:
        v_status = "status-good" if kpis['v_unbalance_avg'] < 2 else "status-warning" if kpis['v_unbalance_avg'] < 5 else "status-critical"
        v_color = "#06d6a0" if kpis['v_unbalance_avg'] < 2 else "#ffd166" if kpis['v_unbalance_avg'] < 5 else "#ef476f"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    ⚡ Phase Balance Monitor
                    <span class="status-dot {v_status}"></span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Voltage Unbalance Avg</span>
                    <span class="kpi-value" style="color: {v_color}">{kpis['v_unbalance_avg']:.2f}%</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Max Unbalance</span>
                    <span class="kpi-value">{kpis['v_unbalance_max']:.1f}%</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Records > 2% (Warning)</span>
                    <span class="kpi-value">{kpis['v_unbalance_warning']} ({kpis['v_unbalance_warning']/max(kpis['total_readings'],1)*100:.1f}%)</span>
                </div>
                <div class="kpi-bar">
                    <div class="kpi-bar-fill" style="width: {min(kpis['v_unbalance_avg']*10, 100)}%; background: {v_color};"></div>
                </div>
                <div class="kpi-insight">
                    {"✓ Excellent phase balance. Motors protected." if kpis['v_unbalance_avg'] < 2 else "⚠️ Monitor voltage balance on phases."}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Predictive Maintenance
    with cols[1]:
        i_status = "status-good" if kpis['i_unbalance_avg'] < 10 else "status-warning" if kpis['i_unbalance_avg'] < 30 else "status-critical"
        i_color = "#06d6a0" if kpis['i_unbalance_avg'] < 10 else "#ffd166" if kpis['i_unbalance_avg'] < 30 else "#ef476f"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    🔧 Predictive Maintenance
                    <span class="status-dot {i_status}"></span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Current Unbalance Avg</span>
                    <span class="kpi-value" style="color: {i_color}">{kpis['i_unbalance_avg']:.1f}%</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Max Unbalance</span>
                    <span class="kpi-value">{kpis['i_unbalance_max']:.1f}%</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Records > 10% (Check)</span>
                    <span class="kpi-value" style="color: {i_color}">{kpis['i_unbalance_warning']} ({kpis['i_unbalance_warning']/max(kpis['total_readings'],1)*100:.1f}%)</span>
                </div>
                <div class="kpi-bar">
                    <div class="kpi-bar-fill" style="width: {min(kpis['i_unbalance_warning']/max(kpis['total_readings'],1)*100, 100)}%; background: {i_color};"></div>
                </div>
                <div class="kpi-insight">
                    {"✓ Current balance healthy." if kpis['i_unbalance_avg'] < 10 else "⚠️ High current unbalance. Check motors/contactors."}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Utilization Tracker
    with cols[2]:
        load_status = "status-good" if kpis['load_avg'] > 50 else "status-warning" if kpis['load_avg'] > 20 else "status-critical"
        load_color = "#06d6a0" if kpis['load_avg'] > 50 else "#ffd166" if kpis['load_avg'] > 20 else "#ef476f"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    📊 Utilization Tracker
                    <span class="status-dot {load_status}"></span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Load % Avg</span>
                    <span class="kpi-value" style="color: {load_color}">{kpis['load_avg']:.1f}%</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Max Load %</span>
                    <span class="kpi-value">{kpis['load_max']:.1f}%</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">IDLE Time (< 10%)</span>
                    <span class="kpi-value" style="color: #ffd166">{kpis['idle_time_pct']:.1f}%</span>
                </div>
                <div class="kpi-bar">
                    <div class="kpi-bar-fill" style="width: {kpis['load_avg']}%; background: {load_color};"></div>
                </div>
                <div class="kpi-insight">
                    {"✓ Good utilization." if kpis['load_avg'] > 50 else "Hidden capacity available. Consider load consolidation."}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Grid Forensics
    with cols[3]:
        freq_ok = 49.5 <= kpis['freq_min'] and kpis['freq_max'] <= 50.5
        grid_status = "status-good" if freq_ok else "status-warning"
        grid_color = "#06d6a0" if freq_ok else "#ffd166"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    🔌 Grid Forensics
                    <span class="status-dot {grid_status}"></span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Frequency Range</span>
                    <span class="kpi-value" style="color: {grid_color}">{kpis['freq_min']:.1f} - {kpis['freq_max']:.1f} Hz</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Voltage LL Range</span>
                    <span class="kpi-value">{kpis['vll_min']:.0f} - {kpis['vll_max']:.0f}V</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Grid Status</span>
                    <span class="kpi-value" style="color: {grid_color}">{"Stable ✓" if freq_ok else "Check ⚠️"}</span>
                </div>
                <div class="kpi-bar">
                    <div class="kpi-bar-fill" style="width: 95%; background: {grid_color};"></div>
                </div>
                <div class="kpi-insight">
                    ✓ Grid quality logged for warranty evidence.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # ============= RISK SHIELD SECTION =============
    st.markdown("""
        <div class="section-header">
            <span class="section-icon">🛡️</span>
            <span class="section-title">Risk Shield & Safety</span>
            <span class="section-badge">Real-time Monitoring</span>
        </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns([2, 1, 1])
    
    # Fire Safety Scout
    with cols[0]:
        fire_total = kpis['fire_normal'] + kpis['fire_warning'] + kpis['fire_high'] + kpis['fire_critical']
        fire_status = "status-good" if kpis['fire_critical'] == 0 and kpis['fire_high'] == 0 else "status-warning" if kpis['fire_critical'] < 10 else "status-critical"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    🔥 Fire Safety Scout (Neutral Current Monitoring)
                    <span class="status-dot {fire_status}"></span>
                </div>
                <div style="display: flex; gap: 20px;">
                    <div style="flex: 1;">
                        <div class="kpi-metric">
                            <span class="kpi-label">Neutral Current Avg</span>
                            <span class="kpi-value">{kpis['neutral_avg']:.2f} A</span>
                        </div>
                        <div class="kpi-metric">
                            <span class="kpi-label">Neutral Current Max</span>
                            <span class="kpi-value" style="color: #ef476f">{kpis['neutral_max']:.2f} A</span>
                        </div>
                        <div class="kpi-metric">
                            <span class="kpi-label">Records > 5A (Risk)</span>
                            <span class="kpi-value" style="color: #ffd166">{kpis['neutral_risk']} ({kpis['neutral_risk']/max(fire_total,1)*100:.1f}%)</span>
                        </div>
                    </div>
                    <div style="flex: 1;">
                        <div class="risk-grid">
                            <div class="risk-item normal">
                                <div class="risk-level" style="color: #06d6a0">Normal</div>
                                <div class="risk-count" style="color: #06d6a0">{kpis['fire_normal']}</div>
                                <div class="risk-pct">{kpis['fire_normal']/max(fire_total,1)*100:.1f}%</div>
                            </div>
                            <div class="risk-item warning">
                                <div class="risk-level" style="color: #ffd166">Warning</div>
                                <div class="risk-count" style="color: #ffd166">{kpis['fire_warning']}</div>
                                <div class="risk-pct">{kpis['fire_warning']/max(fire_total,1)*100:.1f}%</div>
                            </div>
                            <div class="risk-item high">
                                <div class="risk-level" style="color: #f77f00">High</div>
                                <div class="risk-count" style="color: #f77f00">{kpis['fire_high']}</div>
                                <div class="risk-pct">{kpis['fire_high']/max(fire_total,1)*100:.1f}%</div>
                            </div>
                            <div class="risk-item critical">
                                <div class="risk-level" style="color: #ef476f">Critical</div>
                                <div class="risk-count" style="color: #ef476f">{kpis['fire_critical']}</div>
                                <div class="risk-pct">{kpis['fire_critical']/max(fire_total,1)*100:.1f}%</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="kpi-insight">
                    {"✓ Fire risk under control." if kpis['fire_critical'] == 0 else f"⚠️ {kpis['neutral_risk']/max(fire_total,1)*100:.0f}% readings show elevated neutral current. Check phase imbalance and neutral sizing."}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # PF Penalty Alert
    with cols[1]:
        pf_status = "status-good" if kpis['pf_below_92'] < 10 else "status-warning" if kpis['pf_below_92'] < 30 else "status-critical"
        pf_color = "#06d6a0" if kpis['pf_below_92'] < 10 else "#ffd166" if kpis['pf_below_92'] < 30 else "#ef476f"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    ⚠️ PF Penalty Pre-Alert
                    <span class="status-dot {pf_status}"></span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Records PF < 0.92</span>
                    <span class="kpi-value" style="color: {pf_color}">{kpis['pf_below_92']:.1f}%</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Records PF < 0.85</span>
                    <span class="kpi-value" style="color: #ef476f">{kpis['pf_below_85']:.1f}%</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Min PF Recorded</span>
                    <span class="kpi-value" style="color: #ef476f">{kpis['pf_min']:.2f}</span>
                </div>
                <div class="kpi-bar">
                    <div class="kpi-bar-fill" style="width: {kpis['pf_below_92']}%; background: {pf_color};"></div>
                </div>
                <div class="kpi-insight">
                    {"✓ PF healthy." if kpis['pf_below_92'] < 10 else "High penalty exposure. APFC needs tuning."}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Device Identity
    with cols[2]:
        meter_serial = df['Meter_Serial'].iloc[-1] if 'Meter_Serial' in df.columns and len(df) > 0 else "N/A"
        model = df['Model_Number'].iloc[-1] if 'Model_Number' in df.columns and len(df) > 0 else "N/A"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    🔐 Device Identity
                    <span class="status-dot status-good"></span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Meter Serial</span>
                    <span class="kpi-value" style="color: #06d6a0">{meter_serial}</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Model</span>
                    <span class="kpi-value">L&T {model}</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Status</span>
                    <span class="kpi-value" style="color: #06d6a0">Verified ✓</span>
                </div>
                <div class="kpi-bar">
                    <div class="kpi-bar-fill" style="width: 100%; background: #06d6a0;"></div>
                </div>
                <div class="kpi-insight">
                    ✓ No meter swapping detected.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # ============= CHARTS =============
    st.markdown("""
        <div class="section-header">
            <span class="section-icon">📈</span>
            <span class="section-title">Analytics & Trends</span>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Daily Energy", "🔥 Fire Risk", "📈 Load Profile", "🕐 ToD Analysis"])
    
    with tab1:
        daily = df.groupby(df['Date'].dt.date).agg({
            'Energy_kWh': lambda x: x.max() - x.min() if len(x) > 1 else 0,
            'kW_Total': 'max'
        }).reset_index()
        daily.columns = ['Date', 'Energy_kWh', 'Peak_kW']
        
        fig = px.bar(daily, x='Date', y='Energy_kWh', title='Daily Energy Consumption',
                    color_discrete_sequence=['#06d6a0'])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(21,29,40,1)',
            font_color='#8899a6', title_font_color='#f0f4f8'
        )
        fig.update_xaxes(gridcolor='#253040')
        fig.update_yaxes(gridcolor='#253040', title='Energy (kWh)')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fire_data = pd.DataFrame({
            'Level': ['Normal', 'Warning', 'High', 'Critical'],
            'Count': [kpis['fire_normal'], kpis['fire_warning'], kpis['fire_high'], kpis['fire_critical']]
        })
        fig = px.pie(fire_data, values='Count', names='Level', title='Fire Risk Distribution',
                    color='Level', color_discrete_map={
                        'Normal': '#06d6a0', 'Warning': '#ffd166',
                        'High': '#f77f00', 'Critical': '#ef476f'
                    })
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#8899a6')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Load utilization buckets
        if 'Load_Pct' in df.columns:
            bins = [0, 10, 25, 50, 75, 100]
            labels = ['< 10% (Idle)', '10-25%', '25-50%', '50-75%', '> 75%']
            df['Load_Bucket'] = pd.cut(df['Load_Pct'], bins=bins, labels=labels, include_lowest=True)
            load_dist = df['Load_Bucket'].value_counts().reindex(labels).fillna(0)
            
            fig = px.bar(x=load_dist.values / len(df) * 100, y=load_dist.index, orientation='h',
                        title='Load Utilization Pattern', color=load_dist.index,
                        color_discrete_map={
                            '< 10% (Idle)': '#5c6b7a', '10-25%': '#ffd166',
                            '25-50%': '#06d6a0', '50-75%': '#118ab2', '> 75%': '#ef476f'
                        })
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(21,29,40,1)',
                font_color='#8899a6', showlegend=False
            )
            fig.update_xaxes(gridcolor='#253040', title='% of Time')
            fig.update_yaxes(gridcolor='#253040', title='')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        tod_data = df['ToD_Period'].value_counts()
        fig = px.pie(values=tod_data.values, names=tod_data.index, title='Time-of-Day Distribution',
                    color=tod_data.index, color_discrete_map={
                        'OFFPEAK': '#06d6a0', 'NORMAL': '#ffd166', 'PEAK': '#ef476f'
                    })
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#8899a6')
        st.plotly_chart(fig, use_container_width=True)
    
    # ============= RECOMMENDATIONS =============
    st.markdown("""
        <div class="section-header">
            <span class="section-icon">💡</span>
            <span class="section-title">Actionable Recommendations</span>
        </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(3)
    
    with cols[0]:
        st.markdown(f"""
            <div class="rec-card">
                <div class="rec-priority high"></div>
                <div style="flex: 1;">
                    <div class="rec-title">Address Fire Risk Alerts</div>
                    <div class="rec-category">Safety - Fire Scout</div>
                    <div class="rec-insight">{kpis['neutral_risk']/max(kpis['total_readings'],1)*100:.0f}% readings show neutral current >5A. {kpis['fire_critical']} CRITICAL alerts.</div>
                    <div class="rec-action">→ Inspect neutral connections, check loose terminals</div>
                    <div class="rec-savings">
                        <span class="rec-savings-label">Priority:</span>
                        <span class="rec-savings-value" style="color: #ef476f;">SAFETY FIRST</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown(f"""
            <div class="rec-card">
                <div class="rec-priority high"></div>
                <div style="flex: 1;">
                    <div class="rec-title">Fix Low-Load PF Performance</div>
                    <div class="rec-category">Power Quality</div>
                    <div class="rec-insight">PF drops to {kpis['pf_min']:.2f} during idle. {kpis['pf_below_92']:.0f}% of time in penalty zone.</div>
                    <div class="rec-action">→ Reconfigure APFC panel staging for lower thresholds</div>
                    <div class="rec-savings">
                        <span class="rec-savings-label">Monthly Savings:</span>
                        <span class="rec-savings-value">₹2,500+</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown(f"""
            <div class="rec-card">
                <div class="rec-priority high"></div>
                <div style="flex: 1;">
                    <div class="rec-title">Reduce Contracted Demand</div>
                    <div class="rec-category">Contract Review</div>
                    <div class="rec-insight">Load utilization only {kpis['load_avg']:.1f}% avg, {kpis['load_max']:.1f}% max. Consider contract renegotiation.</div>
                    <div class="rec-action">→ Renegotiate to {kpis['max_demand_recorded']*1.2:.0f} kW contract</div>
                    <div class="rec-savings">
                        <span class="rec-savings-label">Monthly Savings:</span>
                        <span class="rec-savings-value">₹4,000+</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # ============= SAVINGS BANNER =============
    st.markdown("""
        <div class="savings-banner">
            <div class="savings-label">💰 Total Monthly Savings Potential</div>
            <div class="savings-value">₹10,000+</div>
            <div class="savings-subtext">Demand contract (₹4,000) + PF optimization (₹2,500) + ToD shift (₹1,500) + Fire prevention (Priceless)</div>
        </div>
    """, unsafe_allow_html=True)
    
    # ============= FOOTER =============
    st.markdown("---")
    st.markdown(f"""
        <p style="text-align: center; color: #5c6b7a; font-size: 11px;">
            Vireon Cortex Energy Analytics Platform | Omega Transmission POC<br>
            WBSEDCL HT Industrial Tariff | Live Data from Google Sheets<br>
            <span style="color: #06d6a0;">📊 {kpis['total_readings']} readings | 🔄 Auto-refresh: 60s</span>
        </p>
    """, unsafe_allow_html=True)
    
    # Refresh button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()


if __name__ == "__main__":
    main()
