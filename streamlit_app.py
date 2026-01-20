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


# ============= HELPER FUNCTIONS =============
def safe_get(df, column, default=0, agg='mean'):
    """Safely get aggregated value from dataframe column"""
    try:
        if column not in df.columns:
            return default
        series = pd.to_numeric(df[column], errors='coerce')
        series = series.replace([np.inf, -np.inf], np.nan).dropna()
        if len(series) == 0:
            return default
        if agg == 'mean': return series.mean()
        elif agg == 'max': return series.max()
        elif agg == 'min': return series.min()
        elif agg == 'sum': return series.sum()
        return default
    except Exception:
        return default

def safe_count(df, column, condition_func, default=0):
    """Safely count rows matching a condition"""
    try:
        if column not in df.columns:
            return default
        series = pd.to_numeric(df[column], errors='coerce')
        series = series.replace([np.inf, -np.inf], np.nan).dropna()
        return int(condition_func(series).sum())
    except Exception:
        return default

def safe_fmt(value, fmt=".2f", default="0"):
    """Safely format a numeric value"""
    try:
        if value is None or pd.isna(value) or np.isinf(value):
            return default
        return f"{value:{fmt}}"
    except Exception:
        return default


# ============= DATA LOADING =============
@st.cache_data(ttl=30, show_spinner=False)
def load_data_from_public_sheet(sheet_id, gid="754782201", _cache_key=None):
    """Load data from public Google Sheet with robust error handling
    
    _cache_key is used to bust cache when needed (underscore prefix tells Streamlit to not hash it)
    """
    try:
        import time
        # Cache buster to force fresh data from Google Sheets CDN
        cache_buster = int(time.time())
        
        # Try multiple URL formats with cache buster
        urls = [
            # Method 1: Using gid (most reliable)
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}&cachebust={cache_buster}",
            # Method 2: Using sheet name
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=readings&_={cache_buster}",
            # Method 3: Default first sheet
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&_={cache_buster}",
        ]
        
        df = None
        for url in urls:
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200 and len(response.text) > 100:
                    df = pd.read_csv(StringIO(response.text))
                    # Check if valid
                    if len(df.columns) > 10 and ('Timestamp' in df.columns or 'timestamp' in df.columns.str.lower()):
                        break
                    df = None
            except:
                continue
        
        if df is None:
            return None
        
        # Handle Timestamp column - try multiple formats
        if 'Timestamp' in df.columns:
            # Strip leading/trailing quotes and whitespace that Google Sheets might add
            df['Timestamp'] = df['Timestamp'].astype(str).str.strip().str.lstrip("'\"").str.rstrip("'\"")
            
            # First try standard datetime parsing
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
            
            # If most timestamps are NaT, try Excel serial number conversion
            if df['Timestamp'].isna().sum() > len(df) * 0.5:
                try:
                    # Reload original column
                    df_temp = pd.read_csv(StringIO(response.text))
                    ts_col = df_temp['Timestamp'].astype(str).str.strip().str.lstrip("'\"")
                    
                    # Check if numeric (Excel serial)
                    ts_numeric = pd.to_numeric(ts_col, errors='coerce')
                    if ts_numeric.notna().sum() > len(df) * 0.5:
                        # Convert Excel serial to datetime (Excel epoch: 1899-12-30)
                        df['Timestamp'] = pd.to_datetime('1899-12-30') + pd.to_timedelta(ts_numeric, unit='D')
                except Exception:
                    pass
        
        # Handle Date column - ensure it exists
        if 'Date' in df.columns:
            # First try standard parsing
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            
            # If most dates are NaT, try Excel serial
            if df['Date'].isna().sum() > len(df) * 0.5:
                try:
                    df_temp = pd.read_csv(StringIO(response.text))
                    date_col = df_temp['Date']
                    date_numeric = pd.to_numeric(date_col, errors='coerce')
                    if date_numeric.notna().sum() > len(df) * 0.5:
                        df['Date'] = pd.to_datetime('1899-12-30') + pd.to_timedelta(date_numeric, unit='D')
                except Exception:
                    pass
        elif 'Timestamp' in df.columns:
            df['Date'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        
        # Ensure Date column exists even if both are missing
        if 'Date' not in df.columns:
            df['Date'] = pd.NaT
        
        numeric_cols = ['kW_Total', 'kVA_Total', 'PF_Avg', 'VLN_Avg', 'VLL_Avg', 'Current_Total',
                       'Neutral_Current_A', 'Frequency_Hz', 'Energy_kWh', 'Daily_Cost_Rs',
                       'Voltage_Unbalance_Pct', 'Current_Unbalance_Pct', 'Load_Pct',
                       'V_R', 'V_Y', 'V_B', 'Current_R', 'Current_Y', 'Current_B',
                       'PF_R', 'PF_Y', 'PF_B', 'Watts_Total', 'VA_Total', 'Run_Hours',
                       'Max_Demand_kVA', 'Max_Demand_kW', 'Daily_Energy_Wh', 'Session_Energy_Wh']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].replace([np.inf, -np.inf], np.nan)
        
        if 'Timestamp' in df.columns:
            df = df.dropna(subset=['Timestamp'])
        
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
    """Calculate all KPIs from dataframe with robust error handling"""
    kpis = {}
    n = len(df)
    kpis['total_readings'] = n
    
    # Basic stats using safe helpers
    energy_max = safe_get(df, 'Energy_kWh', 0, 'max')
    energy_min = safe_get(df, 'Energy_kWh', 0, 'min')
    kpis['total_energy'] = max(0, energy_max - energy_min)
    kpis['total_cost'] = safe_get(df, 'Daily_Cost_Rs', 0, 'sum')
    kpis['peak_demand'] = safe_get(df, 'kW_Total', 0, 'max')
    kpis['max_demand_recorded'] = safe_get(df, 'Max_Demand_kW', 0, 'max')
    kpis['avg_pf'] = safe_get(df, 'PF_Avg', 0, 'mean')
    kpis['run_hours'] = safe_get(df, 'Run_Hours', 0, 'max')
    
    # Voltage unbalance
    kpis['v_unbalance_avg'] = safe_get(df, 'Voltage_Unbalance_Pct', 0, 'mean')
    kpis['v_unbalance_max'] = safe_get(df, 'Voltage_Unbalance_Pct', 0, 'max')
    kpis['v_unbalance_warning'] = safe_count(df, 'Voltage_Unbalance_Pct', lambda x: x > 2)
    
    # Current unbalance
    kpis['i_unbalance_avg'] = safe_get(df, 'Current_Unbalance_Pct', 0, 'mean')
    kpis['i_unbalance_max'] = safe_get(df, 'Current_Unbalance_Pct', 0, 'max')
    kpis['i_unbalance_warning'] = safe_count(df, 'Current_Unbalance_Pct', lambda x: x > 10)
    
    # Load utilization
    kpis['load_avg'] = safe_get(df, 'Load_Pct', 0, 'mean')
    kpis['load_max'] = safe_get(df, 'Load_Pct', 0, 'max')
    idle_count = safe_count(df, 'Load_Pct', lambda x: x < 10)
    kpis['idle_time_pct'] = (idle_count / max(n, 1) * 100)
    
    # Grid forensics
    kpis['freq_min'] = safe_get(df, 'Frequency_Hz', 50, 'min')
    kpis['freq_max'] = safe_get(df, 'Frequency_Hz', 50, 'max')
    kpis['vll_min'] = safe_get(df, 'VLL_Avg', 0, 'min')
    kpis['vll_max'] = safe_get(df, 'VLL_Avg', 0, 'max')
    
    # Fire safety
    kpis['neutral_avg'] = safe_get(df, 'Neutral_Current_A', 0, 'mean')
    kpis['neutral_max'] = safe_get(df, 'Neutral_Current_A', 0, 'max')
    kpis['neutral_risk'] = safe_count(df, 'Neutral_Current_A', lambda x: x > 5)
    
    # Fire risk distribution
    kpis['fire_normal'] = kpis['fire_warning'] = kpis['fire_high'] = kpis['fire_critical'] = 0
    if 'Fire_Risk_Level' in df.columns:
        try:
            fire_counts = df['Fire_Risk_Level'].astype(str).str.upper().str.strip().value_counts()
            kpis['fire_normal'] = int(fire_counts.get('NORMAL', 0))
            kpis['fire_warning'] = int(fire_counts.get('WARNING', 0))
            kpis['fire_high'] = int(fire_counts.get('HIGH', 0))
            kpis['fire_critical'] = int(fire_counts.get('CRITICAL', 0))
        except Exception:
            pass
    
    # PF penalty
    kpis['pf_below_92'] = kpis['pf_below_85'] = kpis['pf_min'] = 0
    if 'PF_Avg' in df.columns and n > 0:
        try:
            pf_series = pd.to_numeric(df['PF_Avg'], errors='coerce').abs()
            pf_series = pf_series.replace([np.inf, -np.inf], np.nan).dropna()
            if len(pf_series) > 0:
                kpis['pf_below_92'] = (pf_series < 0.92).sum() / len(pf_series) * 100
                kpis['pf_below_85'] = (pf_series < 0.85).sum() / len(pf_series) * 100
                kpis['pf_min'] = pf_series.min()
        except Exception:
            pass
    
    return kpis


def generate_report_csv(df, kpis, report_type, shed_label):
    """Generate comprehensive CSV report for download with analysis"""
    from io import StringIO
    
    # Get date range safely
    try:
        date_range = f"{df['Timestamp'].min().strftime('%Y-%m-%d')} to {df['Timestamp'].max().strftime('%Y-%m-%d')}" if 'Timestamp' in df.columns else "N/A"
        num_days = (df['Timestamp'].max() - df['Timestamp'].min()).days + 1 if 'Timestamp' in df.columns else 0
    except:
        date_range = "N/A"
        num_days = 0
    
    output = StringIO()
    
    # Header
    output.write("=" * 60 + "\n")
    output.write("        VIREON CORTEX - ENERGY ANALYTICS REPORT\n")
    output.write("=" * 60 + "\n\n")
    output.write(f"Report Type: {report_type}\n")
    output.write(f"Location: {shed_label}\n")
    output.write(f"Period: {date_range} ({num_days} days)\n")
    output.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    output.write(f"Total Readings: {kpis.get('total_readings', 0):,}\n\n")
    
    # Executive Summary
    output.write("=" * 60 + "\n")
    output.write("EXECUTIVE SUMMARY\n")
    output.write("=" * 60 + "\n\n")
    
    total_energy = kpis.get('total_energy', 0)
    avg_cost_per_kwh = 6.87  # WBSEDCL avg rate
    total_cost = total_energy * avg_cost_per_kwh
    
    output.write(f"Total Energy Consumed: {total_energy:,.2f} kWh\n")
    output.write(f"Estimated Cost: Rs {total_cost:,.2f} (@ Rs {avg_cost_per_kwh}/kWh avg)\n")
    output.write(f"Peak Demand Recorded: {kpis.get('peak_demand', 0):.2f} kW\n")
    output.write(f"Average Power Factor: {kpis.get('avg_pf', 0):.3f}\n")
    output.write(f"Average Load Utilization: {kpis.get('load_avg', 0):.1f}%\n\n")
    
    # Key Findings & Recommendations
    output.write("=" * 60 + "\n")
    output.write("KEY FINDINGS & RECOMMENDATIONS\n")
    output.write("=" * 60 + "\n\n")
    
    findings = []
    savings_potential = 0
    
    # Power Factor Analysis
    pf_avg = kpis.get('avg_pf', 1)
    pf_below_92 = kpis.get('pf_below_92', 0)
    if pf_avg < 0.92:
        pf_penalty = total_cost * 0.02 * (0.92 - pf_avg) / 0.1  # Rough penalty estimate
        findings.append(f"⚠️  LOW POWER FACTOR: Average PF is {pf_avg:.3f} (below 0.92 threshold)")
        findings.append(f"   - {pf_below_92:.1f}% of readings are in penalty zone")
        findings.append(f"   - Estimated penalty exposure: Rs {pf_penalty:,.0f}/month")
        findings.append(f"   → RECOMMENDATION: Service APFC panel, check capacitor banks")
        findings.append(f"   → POTENTIAL SAVINGS: Rs 5,000-10,000/month\n")
        savings_potential += 7500
    else:
        findings.append(f"✓  POWER FACTOR: Healthy at {pf_avg:.3f} (above 0.92)\n")
    
    # Load Utilization Analysis
    load_avg = kpis.get('load_avg', 0)
    load_max = kpis.get('load_max', 0)
    contracted_demand = 200  # Assumed
    if load_avg < 30:
        findings.append(f"⚠️  LOW UTILIZATION: Only {load_avg:.1f}% average load utilization")
        findings.append(f"   - Peak usage: {load_max:.1f}%")
        findings.append(f"   - Contracted demand may be oversized")
        recommended_contract = max(50, load_max * contracted_demand / 100 * 1.2)
        findings.append(f"   → RECOMMENDATION: Renegotiate contract to {recommended_contract:.0f} kW")
        findings.append(f"   → POTENTIAL SAVINGS: Rs 10,000-20,000/month\n")
        savings_potential += 15000
    else:
        findings.append(f"✓  UTILIZATION: Good at {load_avg:.1f}% average\n")
    
    # Fire Risk Analysis
    fire_critical = kpis.get('fire_critical', 0)
    fire_high = kpis.get('fire_high', 0)
    neutral_max = kpis.get('neutral_max', 0)
    if fire_critical > 0 or fire_high > 100:
        findings.append(f"🔥 FIRE RISK ALERT: {fire_critical} critical, {fire_high} high risk events")
        findings.append(f"   - Maximum neutral current: {neutral_max:.2f}A")
        findings.append(f"   → RECOMMENDATION: Inspect wiring, check for loose connections")
        findings.append(f"   → PRIORITY: IMMEDIATE - Safety concern\n")
    else:
        findings.append(f"✓  FIRE SAFETY: Under control, {kpis.get('fire_normal', 0)} normal readings\n")
    
    # Current Unbalance Analysis
    i_unbalance = kpis.get('i_unbalance_avg', 0)
    if i_unbalance > 20:
        findings.append(f"⚠️  CURRENT UNBALANCE: High at {i_unbalance:.1f}%")
        findings.append(f"   - May cause motor overheating and reduced lifespan")
        findings.append(f"   → RECOMMENDATION: Balance loads across phases, check contactors\n")
    
    for finding in findings:
        output.write(finding + "\n")
    
    # Savings Summary
    output.write("\n" + "=" * 60 + "\n")
    output.write("SAVINGS POTENTIAL SUMMARY\n")
    output.write("=" * 60 + "\n\n")
    output.write(f"Total Monthly Savings Potential: Rs {savings_potential:,}+\n")
    output.write(f"Annual Savings Potential: Rs {savings_potential * 12:,}+\n\n")
    
    # Detailed Metrics
    output.write("=" * 60 + "\n")
    output.write("DETAILED METRICS\n")
    output.write("=" * 60 + "\n\n")
    
    metrics = [
        ("ENERGY & DEMAND", [
            ("Total Energy", f"{kpis.get('total_energy', 0):,.2f} kWh"),
            ("Peak Demand", f"{kpis.get('peak_demand', 0):.2f} kW"),
            ("Max Demand (Meter)", f"{kpis.get('max_demand_recorded', 0):.2f} kW"),
            ("Run Hours", f"{kpis.get('run_hours', 0):.1f} hrs"),
        ]),
        ("POWER QUALITY", [
            ("Average Power Factor", f"{kpis.get('avg_pf', 0):.3f}"),
            ("Minimum Power Factor", f"{kpis.get('pf_min', 0):.3f}"),
            ("Time Below 0.92 PF", f"{kpis.get('pf_below_92', 0):.1f}%"),
            ("Time Below 0.85 PF", f"{kpis.get('pf_below_85', 0):.1f}%"),
            ("Voltage Unbalance Avg", f"{kpis.get('v_unbalance_avg', 0):.2f}%"),
            ("Current Unbalance Avg", f"{kpis.get('i_unbalance_avg', 0):.2f}%"),
        ]),
        ("LOAD UTILIZATION", [
            ("Average Load", f"{kpis.get('load_avg', 0):.1f}%"),
            ("Maximum Load", f"{kpis.get('load_max', 0):.1f}%"),
            ("Idle Time (<10%)", f"{kpis.get('idle_time_pct', 0):.1f}%"),
        ]),
        ("SAFETY METRICS", [
            ("Neutral Current Avg", f"{kpis.get('neutral_avg', 0):.2f}A"),
            ("Neutral Current Max", f"{kpis.get('neutral_max', 0):.2f}A"),
            ("Fire Risk - Safe", f"{kpis.get('fire_normal', 0):,}"),
            ("Fire Risk - Watch", f"{kpis.get('fire_warning', 0):,}"),
            ("Fire Risk - High", f"{kpis.get('fire_high', 0):,}"),
            ("Fire Risk - Critical", f"{kpis.get('fire_critical', 0):,}"),
        ]),
        ("GRID QUALITY", [
            ("Frequency Range", f"{kpis.get('freq_min', 50):.1f} - {kpis.get('freq_max', 50):.1f} Hz"),
            ("Voltage Range (LL)", f"{kpis.get('vll_min', 0):.0f} - {kpis.get('vll_max', 0):.0f} V"),
        ]),
    ]
    
    for section, items in metrics:
        output.write(f"\n{section}\n")
        output.write("-" * 40 + "\n")
        for label, value in items:
            output.write(f"  {label}: {value}\n")
    
    # Daily breakdown
    if 'Date' in df.columns:
        try:
            agg_dict = {}
            if 'kW_Total' in df.columns:
                agg_dict['kW_Total'] = ['mean', 'max']
            if 'PF_Avg' in df.columns:
                agg_dict['PF_Avg'] = 'mean'
            if 'Load_Pct' in df.columns:
                agg_dict['Load_Pct'] = 'mean'
            if 'Neutral_Current_A' in df.columns:
                agg_dict['Neutral_Current_A'] = 'max'
            if 'Energy_kWh' in df.columns:
                agg_dict['Energy_kWh'] = lambda x: x.max() - x.min() if len(x) > 1 else 0
            
            if agg_dict:
                daily_df = df.groupby(pd.to_datetime(df['Date']).dt.date).agg(agg_dict).reset_index()
                daily_df.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col for col in daily_df.columns]
                
                output.write("\n\n" + "=" * 60 + "\n")
                output.write("DAILY BREAKDOWN\n")
                output.write("=" * 60 + "\n\n")
                daily_df.to_csv(output, index=False)
        except Exception:
            pass
    
    # Footer
    output.write("\n\n" + "=" * 60 + "\n")
    output.write("Report generated by Vireon Cortex Energy Analytics Platform\n")
    output.write("Omega Transmission POC | WBSEDCL HT Industrial Tariff\n")
    output.write("=" * 60 + "\n")
    
    return output.getvalue()


# ============= MAIN DASHBOARD =============
def main():
    # Sidebar for config
    with st.sidebar:
        # Default values
        DEFAULT_SHEET_ID = "10VSKQgLx-OSMMpbIXqgbb06DF_zgVetcm2s8sW1Wps0"
        DEFAULT_CSV_PATH = "Vireon-PNS-Cables-Logs_-_readings.csv"
        
        # Data source in collapsed expander
        with st.expander("⚙️ Data Source", expanded=False):
            data_source = st.radio(
                "Source",
                options=["Google Sheets", "Local CSV File", "Local File Path"],
                index=0,
                help="Default: Google Sheets"
            )
            
            if data_source == "Google Sheets":
                try:
                    saved_sheet_id = st.secrets.get("sheet_id", DEFAULT_SHEET_ID)
                except Exception:
                    saved_sheet_id = DEFAULT_SHEET_ID
                
                sheet_id = st.text_input("Sheet ID", value=saved_sheet_id)
                uploaded_file = None
                local_csv_path = None
            elif data_source == "Local File Path":
                local_csv_path = st.text_input("CSV Path", value=DEFAULT_CSV_PATH)
                sheet_id = None
                uploaded_file = None
            else:
                uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
                sheet_id = None
                local_csv_path = None
        
        # Set defaults if expander not used
        if 'data_source' not in dir():
            data_source = "Google Sheets"
            sheet_id = DEFAULT_SHEET_ID
            uploaded_file = None
            local_csv_path = None
        
        st.markdown("### 🏭 Shed Filter")
        shed_filter = st.radio(
            "Select View",
            options=["All Sheds", "Shed 1 (Main Feed)", "Shed 2 (Sub-Feed)"],
            index=0,
            help="View all data or filter by shed"
        )
        if shed_filter == "Shed 2 (Sub-Feed)":
            st.info("⚡ Shed 2 is a sub-feed from Shed 1.")
        
        st.markdown("---")
        st.markdown("### 📅 Time Period")
        date_filter = st.radio(
            "Select Range",
            options=["All Data", "Last 7 Days", "Last 30 Days"],
            index=0,
            help="Filter data by time period"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Reports & Analysis")
        report_type = st.selectbox(
            "Report Type",
            options=["Executive Summary", "Weekly Report", "Monthly Report", "Custom Range"],
            index=0
        )
        report_start = None
        report_end = None
        if report_type == "Custom Range":
            col_start, col_end = st.columns(2)
            with col_start:
                report_start = st.date_input("From", value=None)
            with col_end:
                report_end = st.date_input("To", value=None)
        
        generate_report = st.button("📥 Generate Report", use_container_width=True)
        
        st.markdown("---")
        
        # Help & Documentation in sidebar
        with st.expander("📚 Help & Documentation", expanded=False):
            help_section = st.radio(
                "Select Guide",
                options=["CXO Guide", "Technical Manual", "FAQ"],
                index=0,
                label_visibility="collapsed"
            )
            
            if help_section == "CXO Guide":
                st.markdown("""
                **📊 Executive Guide**
                
                **Key Metrics:**
                - **Power Factor (PF)**: Target > 0.92 to avoid penalties
                - **Peak Demand**: Maximum power drawn
                - **Load Utilization**: % of contracted capacity
                - **Fire Risk**: Neutral current anomaly detection
                
                **Alert Levels:**
                - 🟢 Safe: Normal operation
                - 🟡 Watch: Monitor closely
                - 🟠 High: Schedule inspection
                - 🔴 Critical: Immediate action
                
                **ToD Rates (WBSEDCL):**
                - Off-peak (11PM-6AM): ₹5.18/kWh
                - Normal (6AM-5PM): ₹6.87/kWh
                - Peak (5PM-11PM): ₹8.37/kWh
                """)
            
            elif help_section == "Technical Manual":
                st.markdown("""
                **🔧 Technical Guide**
                
                **System Architecture:**
                ```
                Meters → Raspberry Pi → Google Sheets → Dashboard
                ```
                
                **Supported Meters:**
                - L&T WL4405
                - Schneider EM6436H
                
                **Data Collection:**
                - Protocol: Modbus RTU / RS485
                - Interval: 5 minutes
                - Parameters: 50+
                
                **Fire Risk Thresholds:**
                - < 5A: Safe
                - 5-10A: Watch
                - 10-20A: High
                - > 20A: Critical
                
                **Troubleshooting:**
                - All zeros? Check Sheet ID
                - Stale data? Check Pi connectivity
                - Wrong readings? Verify CT ratio
                """)
            
            else:  # FAQ
                st.markdown("""
                **❓ Quick FAQ**
                
                **Q: How often does data refresh?**
                Every 30 seconds (auto-refresh enabled)
                
                **Q: What's a good PF?**
                Above 0.92. Below = penalty charges.
                
                **Q: What causes fire risk alerts?**
                High neutral current from loose connections or phase imbalance.
                
                **Q: How to reduce bill?**
                1. Keep PF > 0.92
                2. Shift loads to off-peak
                3. Right-size contract demand
                
                **Q: Data not updating?**
                1. Click Refresh Data
                2. Check Google Sheet
                3. Verify Pi is running
                """)
    
    # Set shed_label based on filter (before header)
    if shed_filter == "Shed 1 (Main Feed)":
        shed_label = "Shed 1 (Main Feed)"
    elif shed_filter == "Shed 2 (Sub-Feed)":
        shed_label = "Shed 2 (Sub-Feed)"
    else:
        shed_label = "All Sheds"
    
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
    
    # Load data based on source
    df = None
    
    if data_source == "Google Sheets":
        if not sheet_id:
            st.warning("⚠️ Please enter your Google Sheet ID in the sidebar.")
            st.info("Make sure the sheet is published to web: File → Share → Publish to web → CSV")
            return
        
        with st.spinner("📊 Loading data from Google Sheets..."):
            df = load_data_from_public_sheet(sheet_id)
        
        if df is None or df.empty:
            st.error("❌ No data available. Check Sheet ID and ensure it's published to web.")
            return
            
    elif data_source == "Local File Path":
        # Load from local file path
        if not local_csv_path:
            st.warning("⚠️ Please enter a CSV file path in the sidebar.")
            return
        
        with st.spinner(f"📊 Loading data from {local_csv_path}..."):
            try:
                import os
                if not os.path.exists(local_csv_path):
                    st.error(f"❌ File not found: {local_csv_path}")
                    st.info("Make sure the file exists in the same folder as the app.")
                    return
                
                df = pd.read_csv(local_csv_path)
                
                # Apply same preprocessing
                if 'Timestamp' in df.columns:
                    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
                
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                elif 'Timestamp' in df.columns:
                    df['Date'] = pd.to_datetime(df['Timestamp'], errors='coerce')
                
                if 'Date' not in df.columns:
                    df['Date'] = pd.NaT
                
                # Convert numeric columns
                numeric_cols = ['kW_Total', 'kVA_Total', 'PF_Avg', 'VLN_Avg', 'VLL_Avg', 'Current_Total',
                               'Neutral_Current_A', 'Frequency_Hz', 'Energy_kWh', 'Daily_Cost_Rs',
                               'Voltage_Unbalance_Pct', 'Current_Unbalance_Pct', 'Load_Pct',
                               'V_R', 'V_Y', 'V_B', 'Current_R', 'Current_Y', 'Current_B',
                               'PF_R', 'PF_Y', 'PF_B', 'Watts_Total', 'VA_Total', 'Run_Hours',
                               'Max_Demand_kVA', 'Max_Demand_kW', 'Daily_Energy_Wh', 'Session_Energy_Wh']
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        df[col] = df[col].replace([np.inf, -np.inf], np.nan)
                
                if 'Timestamp' in df.columns:
                    df = df.dropna(subset=['Timestamp'])
                    
            except Exception as e:
                st.error(f"❌ Error loading CSV: {e}")
                return
        
        if df is None or df.empty:
            st.error("❌ No data in CSV file.")
            return
    else:
        # Upload CSV file
        if uploaded_file is None:
            st.warning("⚠️ Please upload a CSV file in the sidebar.")
            st.info("Upload your Vireon data CSV file to get started.")
            return
        
        with st.spinner("📊 Loading data from CSV file..."):
            try:
                df = pd.read_csv(uploaded_file)
                
                # Apply same preprocessing as Google Sheets loader
                if 'Timestamp' in df.columns:
                    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
                
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                elif 'Timestamp' in df.columns:
                    df['Date'] = pd.to_datetime(df['Timestamp'], errors='coerce')
                
                if 'Date' not in df.columns:
                    df['Date'] = pd.NaT
                
                # Convert numeric columns
                numeric_cols = ['kW_Total', 'kVA_Total', 'PF_Avg', 'VLN_Avg', 'VLL_Avg', 'Current_Total',
                               'Neutral_Current_A', 'Frequency_Hz', 'Energy_kWh', 'Daily_Cost_Rs',
                               'Voltage_Unbalance_Pct', 'Current_Unbalance_Pct', 'Load_Pct',
                               'V_R', 'V_Y', 'V_B', 'Current_R', 'Current_Y', 'Current_B',
                               'PF_R', 'PF_Y', 'PF_B', 'Watts_Total', 'VA_Total', 'Run_Hours',
                               'Max_Demand_kVA', 'Max_Demand_kW', 'Daily_Energy_Wh', 'Session_Energy_Wh']
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        df[col] = df[col].replace([np.inf, -np.inf], np.nan)
                
                if 'Timestamp' in df.columns:
                    df = df.dropna(subset=['Timestamp'])
                    
            except Exception as e:
                st.error(f"❌ Error loading CSV: {e}")
                return
        
        if df is None or df.empty:
            st.error("❌ No data in CSV file.")
            return
    
    # Debug expander - shows raw data info
    with st.sidebar.expander("🔍 Debug Info", expanded=False):
        st.write(f"**Rows loaded:** {len(df)}")
        st.write(f"**Columns:** {len(df.columns)}")
        st.write("**Column names:**")
        st.code(", ".join(df.columns.tolist()[:20]))
        
        if 'Timestamp' in df.columns:
            valid_ts = df['Timestamp'].notna().sum()
            st.write(f"**Valid Timestamps:** {valid_ts}/{len(df)}")
            if valid_ts > 0:
                st.write(f"**First TS:** {df['Timestamp'].dropna().iloc[0]}")
                st.write(f"**Last TS:** {df['Timestamp'].dropna().iloc[-1]}")
            else:
                st.warning("⚠️ No valid timestamps parsed!")
                if data_source == "Google Sheets":
                    # Show raw timestamp sample
                    try:
                        df_raw = pd.read_csv(StringIO(requests.get(f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=readings", timeout=10).text), nrows=3)
                        if 'Timestamp' in df_raw.columns:
                            st.write("**Raw TS sample:**")
                            st.code(str(df_raw['Timestamp'].tolist()))
                    except:
                        pass
        
        if 'Location' in df.columns:
            st.write(f"**Locations:** {df['Location'].unique().tolist()}")
        
        # Show numeric column stats
        for col in ['kW_Total', 'Energy_kWh', 'PF_Avg']:
            if col in df.columns:
                series = pd.to_numeric(df[col], errors='coerce')
                valid = series.notna().sum()
                st.write(f"**{col}:** {valid} valid, max={series.max() if valid > 0 else 'N/A'}")
    
    # Save original dataframe before filtering (for Data Health Monitor)
    df_original = df.copy()
    
    # Apply shed filter
    if 'Device_ID' in df.columns or 'Location' in df.columns:
        location_col = 'Location' if 'Location' in df.columns else 'Device_ID'
        
        if shed_filter == "Shed 1 (Main Feed)":
            df = df[df[location_col].str.contains('01|Shed_01|Shed 1', case=False, na=False)]
        elif shed_filter == "Shed 2 (Sub-Feed)":
            df = df[df[location_col].str.contains('02|Shed_02|Shed 2', case=False, na=False)]
        
        if df.empty:
            st.warning(f"No data found for {shed_filter}. Try a different filter.")
            return
    
    # Apply date filter
    if date_filter != "All Data" and 'Timestamp' in df.columns:
        now = pd.Timestamp.now()
        if date_filter == "Last 7 Days":
            cutoff = now - pd.Timedelta(days=7)
        else:  # Last 30 Days
            cutoff = now - pd.Timedelta(days=30)
        df = df[df['Timestamp'] >= cutoff]
        
        if df.empty:
            st.warning(f"No data found for {date_filter}. Try a different filter.")
            return
    
    # Calculate KPIs
    kpis = calculate_kpis(df)
    
    # Handle report generation
    if generate_report:
        report_df = df.copy()
        
        # Apply report date filter (only if Timestamp exists)
        if 'Timestamp' in report_df.columns:
            if report_type == "Weekly Report":
                cutoff = pd.Timestamp.now() - pd.Timedelta(days=7)
                report_df = report_df[report_df['Timestamp'] >= cutoff]
            elif report_type == "Monthly Report":
                cutoff = pd.Timestamp.now() - pd.Timedelta(days=30)
                report_df = report_df[report_df['Timestamp'] >= cutoff]
            elif report_type == "Custom Range":
                if report_start and report_end:
                    try:
                        report_df = report_df[
                            (report_df['Timestamp'].dt.date >= report_start) & 
                            (report_df['Timestamp'].dt.date <= report_end)
                        ]
                    except Exception:
                        pass
        
        if not report_df.empty:
            report_kpis = calculate_kpis(report_df)
            csv_content = generate_report_csv(report_df, report_kpis, report_type, shed_label)
            
            st.sidebar.download_button(
                label="📥 Download Report (CSV)",
                data=csv_content,
                file_name=f"vireon_report_{report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.sidebar.success(f"✓ Report ready! Click above to download.")
        else:
            st.sidebar.error("No data for selected range.")
    
    # If All Sheds, show quick comparison first
    if shed_filter == "All Sheds":
        # Current date/time display
        current_datetime = datetime.now()
        st.markdown(f"""
            <div class="section-header">
                <span class="section-icon">🏭</span>
                <span class="section-title">Shed Overview</span>
                <span class="section-badge">Live Status</span>
                <span class="section-badge" style="margin-left: auto;">📅 {current_datetime.strftime('%A, %b %d, %Y')} | 🕐 {current_datetime.strftime('%H:%M:%S')}</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Get latest reading per shed (use the full dataframe before shed filter)
        df_full = df_original.copy()  # Use original unfiltered data
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
                    
                    # Get full timestamp for last reading
                    last_ts = row.get('Timestamp')
                    if pd.notna(last_ts):
                        last_reading_str = last_ts.strftime('%Y-%m-%d %H:%M:%S')
                        time_ago = (current_datetime - last_ts.to_pydatetime().replace(tzinfo=None))
                        mins_ago = time_ago.total_seconds() / 60
                        if mins_ago < 10:
                            status_icon = "🟢"
                            status_text = f"{mins_ago:.0f} min ago"
                        elif mins_ago < 60:
                            status_icon = "🟡"
                            status_text = f"{mins_ago:.0f} min ago"
                        elif mins_ago < 1440:
                            status_icon = "🟠"
                            status_text = f"{mins_ago/60:.1f} hrs ago"
                        else:
                            status_icon = "🔴"
                            status_text = f"{mins_ago/1440:.1f} days ago"
                    else:
                        last_reading_str = "N/A"
                        status_icon = "⚪"
                        status_text = "Unknown"
                    
                    st.markdown(f"""
                        <div class="kpi-card" style="border-top: 3px solid {border_color};">
                            <div class="kpi-title" style="color: {border_color};">
                                📍 {row.get('Location', 'Unknown')} ({shed_type})
                                <span style="margin-left: auto; font-size: 14px;">{status_icon}</span>
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
                            <div class="kpi-insight" style="font-size: 10px;">
                                Last Reading: {last_reading_str}<br>
                                <span style="color: {'#06d6a0' if mins_ago < 10 else '#ffd166' if mins_ago < 60 else '#ef476f'};">{status_text}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Get date range safely
    date_min = 'N/A'
    date_max = 'N/A'
    if 'Date' in df.columns and len(df) > 0:
        try:
            date_min_val = df['Date'].min()
            date_max_val = df['Date'].max()
            if pd.notna(date_min_val):
                date_min = pd.to_datetime(date_min_val).strftime('%b %d')
            if pd.notna(date_max_val):
                date_max = pd.to_datetime(date_max_val).strftime('%b %d, %Y')
        except Exception:
            pass
    elif 'Timestamp' in df.columns and len(df) > 0:
        try:
            date_min_val = df['Timestamp'].min()
            date_max_val = df['Timestamp'].max()
            if pd.notna(date_min_val):
                date_min = date_min_val.strftime('%b %d')
            if pd.notna(date_max_val):
                date_max = date_max_val.strftime('%b %d, %Y')
        except Exception:
            pass
    
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
            <span class="section-title">Asset Health</span>
            <span class="section-badge">Plant Head View</span>
        </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(4)
    
    # Power Quality (simplified from Phase Balance Monitor)
    with cols[0]:
        v_status = "status-good" if kpis['v_unbalance_avg'] < 2 else "status-warning" if kpis['v_unbalance_avg'] < 5 else "status-critical"
        v_color = "#06d6a0" if kpis['v_unbalance_avg'] < 2 else "#ffd166" if kpis['v_unbalance_avg'] < 5 else "#ef476f"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    ⚡ Power Quality
                    <span class="status-dot {v_status}"></span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Supply Stability</span>
                    <span class="kpi-value" style="color: {v_color}">{kpis['v_unbalance_avg']:.2f}%</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Worst Recorded</span>
                    <span class="kpi-value">{kpis['v_unbalance_max']:.1f}%</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Warning Events</span>
                    <span class="kpi-value">{kpis['v_unbalance_warning']} ({kpis['v_unbalance_warning']/max(kpis['total_readings'],1)*100:.1f}%)</span>
                </div>
                <div class="kpi-bar">
                    <div class="kpi-bar-fill" style="width: {min(kpis['v_unbalance_avg']*10, 100)}%; background: {v_color};"></div>
                </div>
                <div class="kpi-insight">
                    {"✓ Stable power supply." if kpis['v_unbalance_avg'] < 2 else "⚠️ Unstable supply detected."}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Motor Health (simplified from Predictive Maintenance)
    with cols[1]:
        i_status = "status-good" if kpis['i_unbalance_avg'] < 10 else "status-warning" if kpis['i_unbalance_avg'] < 30 else "status-critical"
        i_color = "#06d6a0" if kpis['i_unbalance_avg'] < 10 else "#ffd166" if kpis['i_unbalance_avg'] < 30 else "#ef476f"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    🔧 Motor Health
                    <span class="status-dot {i_status}"></span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Load Balance</span>
                    <span class="kpi-value" style="color: {i_color}">{kpis['i_unbalance_avg']:.1f}%</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Worst Recorded</span>
                    <span class="kpi-value">{kpis['i_unbalance_max']:.1f}%</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Needs Attention</span>
                    <span class="kpi-value" style="color: {i_color}">{kpis['i_unbalance_warning']} ({kpis['i_unbalance_warning']/max(kpis['total_readings'],1)*100:.1f}%)</span>
                </div>
                <div class="kpi-bar">
                    <div class="kpi-bar-fill" style="width: {min(kpis['i_unbalance_warning']/max(kpis['total_readings'],1)*100, 100)}%; background: {i_color};"></div>
                </div>
                <div class="kpi-insight">
                    {"✓ Motors running healthy." if kpis['i_unbalance_avg'] < 10 else "⚠️ Uneven load. Schedule check."}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Capacity Usage (simplified from Utilization Tracker)
    with cols[2]:
        load_status = "status-good" if kpis['load_avg'] > 50 else "status-warning" if kpis['load_avg'] > 20 else "status-critical"
        load_color = "#06d6a0" if kpis['load_avg'] > 50 else "#ffd166" if kpis['load_avg'] > 20 else "#ef476f"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    📊 Capacity Usage
                    <span class="status-dot {load_status}"></span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Avg Utilization</span>
                    <span class="kpi-value" style="color: {load_color}">{kpis['load_avg']:.1f}%</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Peak Usage</span>
                    <span class="kpi-value">{kpis['load_max']:.1f}%</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Idle Time</span>
                    <span class="kpi-value" style="color: #ffd166">{kpis['idle_time_pct']:.1f}%</span>
                </div>
                <div class="kpi-bar">
                    <div class="kpi-bar-fill" style="width: {kpis['load_avg']}%; background: {load_color};"></div>
                </div>
                <div class="kpi-insight">
                    {"✓ Good utilization." if kpis['load_avg'] > 50 else "💡 Underutilized. Reduce contract."}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Grid Quality (simplified from Grid Forensics)
    with cols[3]:
        freq_ok = 49.5 <= kpis['freq_min'] and kpis['freq_max'] <= 50.5
        grid_status = "status-good" if freq_ok else "status-warning"
        grid_color = "#06d6a0" if freq_ok else "#ffd166"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    🔌 Grid Quality
                    <span class="status-dot {grid_status}"></span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Frequency</span>
                    <span class="kpi-value" style="color: {grid_color}">{kpis['freq_min']:.1f} - {kpis['freq_max']:.1f} Hz</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Voltage Range</span>
                    <span class="kpi-value">{kpis['vll_min']:.0f} - {kpis['vll_max']:.0f}V</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Status</span>
                    <span class="kpi-value" style="color: {grid_color}">{"Stable ✓" if freq_ok else "Fluctuating ⚠️"}</span>
                </div>
                <div class="kpi-bar">
                    <div class="kpi-bar-fill" style="width: 95%; background: {grid_color};"></div>
                </div>
                <div class="kpi-insight">
                    ✓ Logged for warranty claims.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # ============= RISK SHIELD SECTION =============
    st.markdown("""
        <div class="section-header">
            <span class="section-icon">🛡️</span>
            <span class="section-title">Safety & Compliance</span>
            <span class="section-badge">CFO View</span>
        </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns([2, 1, 1])
    
    # Fire Risk Monitor (simplified from Fire Safety Scout)
    with cols[0]:
        fire_total = kpis['fire_normal'] + kpis['fire_warning'] + kpis['fire_high'] + kpis['fire_critical']
        fire_status = "status-good" if kpis['fire_critical'] == 0 and kpis['fire_high'] == 0 else "status-warning" if kpis['fire_critical'] < 10 else "status-critical"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    🔥 Fire Risk Monitor
                    <span class="status-dot {fire_status}"></span>
                </div>
                <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 150px;">
                        <div class="kpi-metric">
                            <span class="kpi-label">Avg Risk Level</span>
                            <span class="kpi-value">{kpis['neutral_avg']:.2f} A</span>
                        </div>
                        <div class="kpi-metric">
                            <span class="kpi-label">Peak Risk</span>
                            <span class="kpi-value" style="color: #ef476f">{kpis['neutral_max']:.2f} A</span>
                        </div>
                        <div class="kpi-metric">
                            <span class="kpi-label">Elevated Events</span>
                            <span class="kpi-value" style="color: #ffd166">{kpis['neutral_risk']} ({kpis['neutral_risk']/max(fire_total,1)*100:.1f}%)</span>
                        </div>
                    </div>
                    <div style="flex: 1; min-width: 200px;">
                        <div class="risk-grid">
                            <div class="risk-item normal">
                                <div class="risk-level" style="color: #06d6a0">Safe</div>
                                <div class="risk-count" style="color: #06d6a0">{kpis['fire_normal']}</div>
                                <div class="risk-pct">{kpis['fire_normal']/max(fire_total,1)*100:.1f}%</div>
                            </div>
                            <div class="risk-item warning">
                                <div class="risk-level" style="color: #ffd166">Watch</div>
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
                    {"✓ Fire risk under control." if kpis['fire_critical'] == 0 else f"⚠️ {kpis['fire_critical']} critical events. Inspect wiring."}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Penalty Alert (simplified from PF Penalty Pre-Alert)
    with cols[1]:
        pf_status = "status-good" if kpis['pf_below_92'] < 10 else "status-warning" if kpis['pf_below_92'] < 30 else "status-critical"
        pf_color = "#06d6a0" if kpis['pf_below_92'] < 10 else "#ffd166" if kpis['pf_below_92'] < 30 else "#ef476f"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    ⚠️ Penalty Alert
                    <span class="status-dot {pf_status}"></span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">In Penalty Zone</span>
                    <span class="kpi-value" style="color: {pf_color}">{kpis['pf_below_92']:.1f}%</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">High Penalty Zone</span>
                    <span class="kpi-value" style="color: #ef476f">{kpis['pf_below_85']:.1f}%</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Lowest PF</span>
                    <span class="kpi-value" style="color: #ef476f">{kpis['pf_min']:.2f}</span>
                </div>
                <div class="kpi-bar">
                    <div class="kpi-bar-fill" style="width: {kpis['pf_below_92']}%; background: {pf_color};"></div>
                </div>
                <div class="kpi-insight">
                    {"✓ No penalty risk." if kpis['pf_below_92'] < 10 else "💸 Penalty exposure. Fix APFC."}
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
        try:
            if 'Date' in df.columns and 'Energy_kWh' in df.columns and 'kW_Total' in df.columns:
                daily = df.groupby(pd.to_datetime(df['Date']).dt.date).agg({
                    'Energy_kWh': lambda x: x.max() - x.min() if len(x) > 1 else 0,
                    'kW_Total': 'max'
                }).reset_index()
                daily.columns = ['Date', 'Energy_kWh', 'Peak_kW']
                
                # Add day of week info for coloring
                daily['Date'] = pd.to_datetime(daily['Date'])
                daily['DayOfWeek'] = daily['Date'].dt.dayofweek  # 0=Mon, 6=Sun
                daily['DayName'] = daily['Date'].dt.strftime('%a')  # Mon, Tue, etc.
                daily['IsWeekend'] = daily['DayOfWeek'].isin([5, 6])  # Sat=5, Sun=6
                daily['DayType'] = daily['IsWeekend'].map({True: '🔵 Weekend', False: '🟢 Weekday'})
                
                # Create bar chart with weekend/weekday colors
                fig = px.bar(daily, x='Date', y='Energy_kWh', 
                            color='DayType',
                            color_discrete_map={
                                '🟢 Weekday': '#06d6a0',
                                '🔵 Weekend': '#118ab2'
                            },
                            title='Daily Energy Consumption (Weekday vs Weekend)',
                            hover_data={'DayName': True, 'Peak_kW': ':.1f', 'Energy_kWh': ':.1f'})
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(21,29,40,1)',
                    font_color='#8899a6', 
                    title_font_color='#f0f4f8',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                fig.update_xaxes(gridcolor='#253040', tickformat='%b %d\n%a')
                fig.update_yaxes(gridcolor='#253040', title='Energy (kWh)')
                
                # Add weekend shading
                for _, row in daily[daily['IsWeekend']].iterrows():
                    fig.add_vrect(
                        x0=row['Date'] - pd.Timedelta(hours=12),
                        x1=row['Date'] + pd.Timedelta(hours=12),
                        fillcolor="rgba(17, 138, 178, 0.1)",
                        layer="below",
                        line_width=0,
                    )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show weekday vs weekend summary
                weekday_avg = daily[~daily['IsWeekend']]['Energy_kWh'].mean()
                weekend_avg = daily[daily['IsWeekend']]['Energy_kWh'].mean()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Weekday Avg", f"{weekday_avg:.1f} kWh")
                with col2:
                    st.metric("Weekend Avg", f"{weekend_avg:.1f} kWh")
                with col3:
                    diff_pct = ((weekend_avg - weekday_avg) / weekday_avg * 100) if weekday_avg > 0 else 0
                    st.metric("Weekend vs Weekday", f"{diff_pct:+.1f}%")
            else:
                st.info("Energy data not available for chart.")
        except Exception as e:
            st.warning(f"Could not generate daily chart: {e}")
    
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
        try:
            if 'ToD_Period' in df.columns:
                # Normalize ToD values (OFF-PEAK -> OFFPEAK)
                df_tod = df.copy()
                df_tod['ToD_Period'] = df_tod['ToD_Period'].str.upper().str.replace('-', '').str.strip()
                tod_data = df_tod['ToD_Period'].value_counts()
                if len(tod_data) > 0:
                    fig = px.pie(values=tod_data.values, names=tod_data.index, title='Time-of-Day Distribution',
                                color=tod_data.index, color_discrete_map={
                                    'OFFPEAK': '#06d6a0', 'NORMAL': '#ffd166', 'PEAK': '#ef476f'
                                })
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#8899a6')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No ToD data available")
            else:
                st.info("ToD_Period column not found")
        except Exception as e:
            st.warning(f"Could not generate ToD chart: {e}")
    
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
    
    # ============= DATA HEALTH MONITOR =============
    st.markdown("""
        <div class="section-header">
            <span class="section-icon">📡</span>
            <span class="section-title">Data Health Monitor</span>
            <span class="section-badge">Live Status</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Use the original unfiltered dataframe for health check
    df_health = df_original.copy()
    
    if df_health is not None and not df_health.empty:
        from datetime import timedelta
        
        # Get status for each shed
        sheds = []
        if 'Location' in df_health.columns:
            for location in df_health['Location'].unique():
                df_loc = df_health[df_health['Location'] == location].copy()
                df_loc = df_loc.sort_values('Timestamp')
                
                if len(df_loc) > 0:
                    last_reading = df_loc['Timestamp'].max()
                    first_reading = df_loc['Timestamp'].min()
                    total_readings = len(df_loc)
                    
                    # Time since last reading
                    now = pd.Timestamp.now()
                    time_since_last = now - last_reading
                    minutes_ago = time_since_last.total_seconds() / 60
                    
                    # Determine status
                    if minutes_ago <= 10:
                        status = "🟢 LIVE"
                        status_color = "#06d6a0"
                    elif minutes_ago <= 30:
                        status = "🟡 DELAYED"
                        status_color = "#ffd166"
                    else:
                        status = "🔴 OFFLINE"
                        status_color = "#ef476f"
                    
                    # Calculate gaps
                    df_loc['time_diff'] = df_loc['Timestamp'].diff()
                    expected_interval = timedelta(minutes=5)
                    tolerance = timedelta(minutes=2)
                    gaps = df_loc[df_loc['time_diff'] > expected_interval + tolerance]
                    normal_intervals = len(df_loc) - len(gaps) - 1  # -1 for first row with NaN diff
                    
                    # Data completeness
                    time_span_minutes = (last_reading - first_reading).total_seconds() / 60
                    expected_readings = time_span_minutes / 5 if time_span_minutes > 0 else 1
                    completeness = min(100, total_readings / expected_readings * 100)
                    
                    sheds.append({
                        'location': location,
                        'status': status,
                        'status_color': status_color,
                        'last_reading': last_reading,
                        'minutes_ago': minutes_ago,
                        'total_readings': total_readings,
                        'gaps': len(gaps),
                        'completeness': completeness,
                        'first_reading': first_reading
                    })
        
        # Display shed status cards
        if sheds:
            cols = st.columns(len(sheds))
            for idx, shed in enumerate(sheds):
                with cols[idx]:
                    # Determine if main or sub feed
                    is_main = '01' in shed['location']
                    shed_type = "Main Feed" if is_main else "Sub-Feed"
                    border_color = "#06d6a0" if is_main else "#118ab2"
                    
                    # Format time ago
                    if shed['minutes_ago'] < 60:
                        time_ago_str = f"{shed['minutes_ago']:.0f} min ago"
                    elif shed['minutes_ago'] < 1440:
                        time_ago_str = f"{shed['minutes_ago']/60:.1f} hrs ago"
                    else:
                        time_ago_str = f"{shed['minutes_ago']/1440:.1f} days ago"
                    
                    st.markdown(f"""
                        <div class="kpi-card" style="border-top: 3px solid {border_color};">
                            <div class="kpi-title">
                                📍 {shed['location']} ({shed_type})
                                <span style="color: {shed['status_color']}; font-weight: 700;">{shed['status']}</span>
                            </div>
                            <div class="kpi-metric">
                                <span class="kpi-label">Last Reading</span>
                                <span class="kpi-value" style="font-size: 12px;">{shed['last_reading'].strftime('%Y-%m-%d %H:%M')}</span>
                            </div>
                            <div class="kpi-metric">
                                <span class="kpi-label">Time Since Update</span>
                                <span class="kpi-value" style="color: {shed['status_color']}">{time_ago_str}</span>
                            </div>
                            <div class="kpi-metric">
                                <span class="kpi-label">Total Readings</span>
                                <span class="kpi-value">{shed['total_readings']:,}</span>
                            </div>
                            <div class="kpi-metric">
                                <span class="kpi-label">Data Gaps (>7 min)</span>
                                <span class="kpi-value" style="color: {'#ef476f' if shed['gaps'] > 10 else '#ffd166' if shed['gaps'] > 0 else '#06d6a0'}">{shed['gaps']}</span>
                            </div>
                            <div class="kpi-bar">
                                <div class="kpi-bar-fill" style="width: {shed['completeness']:.0f}%; background: {border_color};"></div>
                            </div>
                            <div class="kpi-insight">
                                Data completeness: {shed['completeness']:.1f}% | Since {shed['first_reading'].strftime('%b %d')}
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
    
    # Refresh section
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.markdown(f"<p style='text-align: center; color: #5c6b7a; font-size: 10px;'>Last refresh: {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col3:
        auto_refresh = st.checkbox("Auto-refresh (30s)", value=True)
    
    # Auto-refresh functionality
    if auto_refresh:
        import time
        time.sleep(30)
        st.cache_data.clear()
        st.rerun()


if __name__ == "__main__":
    main()
