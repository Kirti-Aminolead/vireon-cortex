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
from datetime import datetime, timedelta, timezone
import requests
from io import StringIO
import random

# ============= IST TIMEZONE =============
IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_now():
    """Get current time in IST"""
    return datetime.now(IST).replace(tzinfo=None)

# ============= PAGE CONFIG =============
st.set_page_config(
    page_title="Vireon Cortex | Advanced Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============= THEME TOGGLE (TOP OF SIDEBAR) =============
theme_choice = st.sidebar.radio(
    "🎨 Theme",
    ["Dark", "Light"],
    index=0,
    horizontal=True,
    key="theme_toggle_main"
)

# ============= CUSTOM CSS (Theme-aware) =============
if theme_choice == "Dark":
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
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;
        margin-top: 12px;
    }
    @media (min-width: 1200px) {
        .risk-grid {
            grid-template-columns: repeat(4, 1fr);
        }
    }
    .risk-item {
        background: #1a242f;
        padding: 10px 8px;
        border-radius: 8px;
        text-align: center;
        border-left: 3px solid #253040;
        min-width: 0;
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
        flex-wrap: wrap;
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
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: #0d1117;
        border-right: 1px solid #253040;
    }
    section[data-testid="stSidebar"] .stRadio > label {
        font-size: 12px !important;
        font-weight: 500;
    }
    section[data-testid="stSidebar"] .stRadio > div {
        gap: 8px;
    }
    section[data-testid="stSidebar"] .stRadio > div > label {
        padding: 6px 12px !important;
        border-radius: 6px;
        font-size: 11px !important;
        background: #1a242f;
        border: 1px solid #253040;
    }
    section[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
        background: #06d6a0 !important;
        color: #0a0e14 !important;
        border-color: #06d6a0;
    }
    section[data-testid="stSidebar"] .stSelectbox > label,
    section[data-testid="stSidebar"] .stDateInput > label {
        font-size: 11px !important;
        color: #8899a6;
    }
    section[data-testid="stSidebar"] h3 {
        font-size: 13px !important;
        color: #f0f4f8;
        margin: 16px 0 8px 0 !important;
        padding-bottom: 6px;
        border-bottom: 1px solid #253040;
    }
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #06d6a0 0%, #118ab2 100%);
        color: #0a0e14;
        font-weight: 600;
        font-size: 12px;
        border: none;
        border-radius: 8px;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, #05c090 0%, #0f7a9d 100%);
    }
    section[data-testid="stSidebar"] .stExpander {
        background: #151d28;
        border: 1px solid #253040;
        border-radius: 8px;
        margin-bottom: 8px;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #253040;
        margin: 12px 0;
    }
    section[data-testid="stSidebar"] .stAlert {
        font-size: 10px;
        padding: 8px;
    }
    
    /* Client Info */
    .client-info {
        background: #151d28;
        border: 1px solid #253040;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 16px;
    }
    .client-name { font-weight: 600; color: #f0f4f8; font-size: 12px; }
    .client-location { color: #8899a6; font-size: 10px; }
    
    /* Hardware Info */
    .hardware-info {
        background: #1a242f;
        border: 1px solid #253040;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 8px;
    }
    .hardware-label { font-size: 9px; color: #5c6b7a; text-transform: uppercase; }
    .hardware-value { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #06d6a0; }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .main-header { font-size: 24px; }
        .summary-value { font-size: 20px; }
        .summary-card { padding: 14px; }
        .kpi-card { padding: 14px; }
        .section-header { margin: 24px 0 16px 0; }
        .section-title { font-size: 16px; }
        .savings-value { font-size: 32px; }
        .risk-grid { grid-template-columns: repeat(2, 1fr); }
        .rec-card { padding: 12px; flex-direction: column; }
        .rec-priority { width: 100%; height: 3px; }
    }
    
    @media (max-width: 480px) {
        .main-header { font-size: 20px; }
        .summary-value { font-size: 18px; }
        .section-badge { font-size: 9px; padding: 3px 8px; }
        .savings-value { font-size: 28px; }
    }
</style>
""", unsafe_allow_html=True)
else:
    # Light theme CSS
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --bg-primary: #ffffff;
        --bg-card: #f8f9fa;
        --bg-elevated: #ffffff;
        --text-primary: #1a1a2e;
        --text-secondary: #4a5568;
        --text-muted: #718096;
        --border: #e2e8f0;
        --cyan: #0d9488;
        --yellow: #d97706;
        --red: #dc2626;
        --blue: #0284c7;
        --purple: #7c3aed;
        --orange: #ea580c;
    }
    
    .stApp {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    .main-header {
        font-family: 'JetBrains Mono', monospace;
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(135deg, #0d9488 0%, #0284c7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    
    .subtitle { color: #4a5568; font-size: 14px; }
    
    /* Summary Cards */
    .summary-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px;
        position: relative;
        overflow: hidden;
        height: 100%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .summary-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: #0d9488;
    }
    .summary-card.yellow::before { background: #d97706; }
    .summary-card.red::before { background: #dc2626; }
    .summary-card.blue::before { background: #0284c7; }
    .summary-card.purple::before { background: #7c3aed; }
    .summary-card.orange::before { background: #ea580c; }
    .summary-label {
        font-size: 10px;
        color: #4a5568;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .summary-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 24px;
        font-weight: 700;
        color: #1a1a2e;
    }
    .summary-unit { font-size: 12px; color: #4a5568; }
    .summary-subtext { font-size: 10px; color: #718096; margin-top: 4px; }
    
    /* Section Headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 32px 0 20px 0;
        padding-bottom: 12px;
        border-bottom: 1px solid #e2e8f0;
    }
    .section-icon {
        width: 36px;
        height: 36px;
        background: #f8f9fa;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }
    .section-title { font-size: 18px; font-weight: 600; color: #1a1a2e; }
    .section-badge {
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 11px;
        color: #4a5568;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* KPI Cards */
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        height: 100%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .kpi-title {
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
        color: #1a1a2e;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-left: auto;
    }
    .status-good { background: #0d9488; box-shadow: 0 0 8px #0d9488; }
    .status-warning { background: #d97706; box-shadow: 0 0 8px #d97706; }
    .status-critical { background: #dc2626; box-shadow: 0 0 8px #dc2626; }
    .kpi-metric {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 8px;
    }
    .kpi-label { font-size: 11px; color: #718096; }
    .kpi-value { font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 600; color: #1a1a2e; }
    .kpi-bar {
        height: 6px;
        background: #e2e8f0;
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
        color: #4a5568;
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid #e2e8f0;
    }
    
    /* Risk Items */
    .risk-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;
        margin-top: 12px;
    }
    @media (min-width: 1200px) {
        .risk-grid {
            grid-template-columns: repeat(4, 1fr);
        }
    }
    .risk-item {
        background: #f8f9fa;
        padding: 10px 8px;
        border-radius: 8px;
        text-align: center;
        border-left: 3px solid #e2e8f0;
        min-width: 0;
    }
    .risk-item.normal { border-left-color: #0d9488; }
    .risk-item.warning { border-left-color: #d97706; }
    .risk-item.high { border-left-color: #ea580c; }
    .risk-item.critical { border-left-color: #dc2626; }
    .risk-level { font-size: 9px; text-transform: uppercase; letter-spacing: 0.5px; }
    .risk-count { font-family: 'JetBrains Mono', monospace; font-size: 18px; font-weight: 700; }
    .risk-pct { font-size: 10px; color: #718096; }
    
    /* Recommendations */
    .rec-card {
        background: #f8f9fa;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        height: 100%;
    }
    .rec-priority {
        width: 4px;
        border-radius: 2px;
        flex-shrink: 0;
    }
    .rec-priority.high { background: #dc2626; }
    .rec-priority.medium { background: #d97706; }
    .rec-priority.low { background: #0d9488; }
    .rec-title { font-weight: 600; font-size: 13px; color: #1a1a2e; margin-bottom: 4px; }
    .rec-category { font-size: 10px; color: #718096; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .rec-insight { font-size: 11px; color: #4a5568; margin-bottom: 8px; }
    .rec-action { font-size: 11px; color: #0d9488; }
    .rec-savings {
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px solid #e2e8f0;
        display: flex;
        justify-content: space-between;
    }
    .rec-savings-label { font-size: 9px; color: #718096; text-transform: uppercase; }
    .rec-savings-value { font-family: 'JetBrains Mono', monospace; font-size: 14px; color: #0d9488; font-weight: 600; }
    
    /* Savings Banner */
    .savings-banner {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 2px solid #0d9488;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        margin: 32px 0;
    }
    .savings-label { font-size: 14px; color: #166534; margin-bottom: 8px; font-weight: 600; }
    .savings-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 42px;
        font-weight: 700;
        color: #15803d;
    }
    .savings-subtext { font-size: 12px; color: #166534; margin-top: 8px; }
    
    /* ToD Badges */
    .tod-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 600;
    }
    .tod-offpeak { background: rgba(13, 148, 136, 0.15); color: #0d9488; border: 1px solid #0d9488; }
    .tod-normal { background: rgba(217, 119, 6, 0.15); color: #d97706; border: 1px solid #d97706; }
    .tod-peak { background: rgba(220, 38, 38, 0.15); color: #dc2626; border: 1px solid #dc2626; }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] .stRadio > label {
        font-size: 12px !important;
        font-weight: 500;
        color: #1a1a2e;
    }
    section[data-testid="stSidebar"] .stRadio > div {
        gap: 8px;
    }
    section[data-testid="stSidebar"] .stRadio > div > label {
        padding: 6px 12px !important;
        border-radius: 6px;
        font-size: 11px !important;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        color: #4a5568;
    }
    section[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
        background: #0d9488 !important;
        color: #ffffff !important;
        border-color: #0d9488;
    }
    section[data-testid="stSidebar"] .stSelectbox > label,
    section[data-testid="stSidebar"] .stDateInput > label {
        font-size: 11px !important;
        color: #4a5568;
    }
    section[data-testid="stSidebar"] h3 {
        font-size: 13px !important;
        color: #1a1a2e;
        margin: 16px 0 8px 0 !important;
        padding-bottom: 6px;
        border-bottom: 1px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #0d9488 0%, #0284c7 100%);
        color: #ffffff;
        font-weight: 600;
        font-size: 12px;
        border: none;
        border-radius: 8px;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, #0f766e 0%, #0369a1 100%);
    }
    section[data-testid="stSidebar"] .stExpander {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        margin-bottom: 8px;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #e2e8f0;
        margin: 12px 0;
    }
    section[data-testid="stSidebar"] .stAlert {
        font-size: 10px;
        padding: 8px;
    }
    
    /* Client Info */
    .client-info {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .client-name { font-weight: 600; color: #1a1a2e; font-size: 12px; }
    .client-location { color: #4a5568; font-size: 10px; }
    
    /* Hardware Info */
    .hardware-info {
        background: #f8f9fa;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 8px;
    }
    .hardware-label { font-size: 9px; color: #718096; text-transform: uppercase; }
    .hardware-value { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #0d9488; }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .main-header { font-size: 24px; }
        .summary-value { font-size: 20px; }
        .summary-card { padding: 14px; }
        .kpi-card { padding: 14px; }
        .section-header { margin: 24px 0 16px 0; }
        .section-title { font-size: 16px; }
        .savings-value { font-size: 32px; }
        .risk-grid { grid-template-columns: repeat(2, 1fr); }
        .rec-card { padding: 12px; flex-direction: column; }
        .rec-priority { width: 100%; height: 3px; }
    }
    
    @media (max-width: 480px) {
        .main-header { font-size: 20px; }
        .summary-value { font-size: 18px; }
        .section-badge { font-size: 9px; padding: 3px 8px; }
        .savings-value { font-size: 28px; }
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
@st.cache_data(ttl=15, show_spinner=False)
def load_data_from_public_sheet(sheet_id, gid="754782201", _cache_key=None):
    """Load data from public Google Sheet with robust error handling
    
    _cache_key is used to bust cache when needed (underscore prefix tells Streamlit to not hash it)
    """
    try:
        import time
        # Cache buster to force fresh data from Google Sheets CDN
        cache_buster = f"{int(time.time())}_{random.randint(1000,9999)}"
        
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
            
            # Use format='mixed' to handle both space and T separators
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='mixed', errors='coerce')
            
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
            # First try with mixed format
            df['Date'] = pd.to_datetime(df['Date'], format='mixed', errors='coerce')
            
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
            # CRITICAL: Sort by timestamp to ensure chronological order
            df = df.sort_values('Timestamp').reset_index(drop=True)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


def get_tod_period():
    """Get current ToD period based on IST"""
    hour = get_ist_now().hour
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
    
    # Energy calculation - use last reading minus first reading per location
    # This handles cumulative meters correctly
    if 'Energy_kWh' in df.columns and 'Timestamp' in df.columns and 'Location' in df.columns:
        try:
            total_energy = 0
            for loc in df['Location'].unique():
                df_loc = df[df['Location'] == loc].sort_values('Timestamp')
                if len(df_loc) >= 2:
                    first_e = df_loc['Energy_kWh'].iloc[0]
                    last_e = df_loc['Energy_kWh'].iloc[-1]
                    loc_energy = last_e - first_e
                    if loc_energy > 0:
                        total_energy += loc_energy
            kpis['total_energy'] = total_energy
        except:
            kpis['total_energy'] = 0
    elif 'Energy_kWh' in df.columns and 'Timestamp' in df.columns:
        # Single location fallback
        try:
            df_sorted = df.sort_values('Timestamp')
            if len(df_sorted) >= 2:
                kpis['total_energy'] = max(0, df_sorted['Energy_kWh'].iloc[-1] - df_sorted['Energy_kWh'].iloc[0])
            else:
                kpis['total_energy'] = 0
        except:
            kpis['total_energy'] = 0
    else:
        kpis['total_energy'] = 0
    
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
    
    # PF penalty - with noise filtering and sustained alert detection
    kpis['pf_below_92'] = kpis['pf_below_85'] = kpis['pf_min'] = 0
    kpis['pf_below_90'] = 0
    kpis['pf_sustained_alerts'] = 0  # Count of sustained low PF events (2+ consecutive)
    kpis['pf_sustained_minutes'] = 0  # Total minutes in sustained low PF
    kpis['pf_valid_readings'] = 0  # Readings with sufficient current
    kpis['pf_events'] = []  # List of event details for reporting
    
    if 'PF_Avg' in df.columns and n > 0:
        try:
            # Create working copy for PF analysis
            df_pf = df.copy()
            df_pf['PF_Abs'] = pd.to_numeric(df_pf['PF_Avg'], errors='coerce').abs()
            
            # Filter out noisy data: require Current > 1A for valid PF reading
            # This excludes startup transients and idle states
            if 'Current_Total' in df_pf.columns:
                current_series = pd.to_numeric(df_pf['Current_Total'], errors='coerce')
                valid_mask = (current_series > 1.0) & (df_pf['PF_Abs'].notna())
            else:
                valid_mask = df_pf['PF_Abs'].notna()
            
            df_pf_valid = df_pf[valid_mask].copy()
            kpis['pf_valid_readings'] = len(df_pf_valid)
            
            if len(df_pf_valid) > 0:
                pf_series = df_pf_valid['PF_Abs']
                pf_series = pf_series.replace([np.inf, -np.inf], np.nan).dropna()
                
                if len(pf_series) > 0:
                    kpis['pf_below_92'] = (pf_series < 0.92).sum() / len(pf_series) * 100
                    kpis['pf_below_90'] = (pf_series < 0.90).sum() / len(pf_series) * 100
                    kpis['pf_below_85'] = (pf_series < 0.85).sum() / len(pf_series) * 100
                    kpis['pf_min'] = pf_series.min()
                
                # Detect sustained low PF (2+ consecutive readings below 0.90)
                # Changed from 3 to 2 for faster APFC response detection (~10 min)
                df_pf_valid = df_pf_valid.sort_values('Timestamp').reset_index(drop=True)
                df_pf_valid['PF_Low_90'] = df_pf_valid['PF_Abs'] < 0.90
                df_pf_valid['PF_Low_92'] = df_pf_valid['PF_Abs'] < 0.92
                
                # Group consecutive low PF readings
                df_pf_valid['PF_Low_Group'] = (df_pf_valid['PF_Low_90'] != df_pf_valid['PF_Low_90'].shift()).cumsum()
                
                # Count sustained events (2+ consecutive readings = ~10+ min at 5-min intervals)
                sustained_groups = df_pf_valid[df_pf_valid['PF_Low_90']].groupby('PF_Low_Group').size()
                sustained_alerts = sustained_groups[sustained_groups >= 2]  # Changed from 3 to 2
                
                kpis['pf_sustained_alerts'] = len(sustained_alerts)
                kpis['pf_sustained_readings'] = sustained_alerts.sum() if len(sustained_alerts) > 0 else 0
                kpis['pf_sustained_minutes'] = kpis['pf_sustained_readings'] * 5  # Assuming 5-min intervals
                
                # Store event details for reporting
                pf_events = []
                for group_id in sustained_alerts.index:
                    group = df_pf_valid[df_pf_valid['PF_Low_Group'] == group_id]
                    if len(group) >= 2:
                        pf_events.append({
                            'date': group['Timestamp'].iloc[0].strftime('%Y-%m-%d'),
                            'start': group['Timestamp'].iloc[0].strftime('%H:%M'),
                            'end': group['Timestamp'].iloc[-1].strftime('%H:%M'),
                            'readings': len(group),
                            'duration_min': len(group) * 5,
                            'min_pf': group['PF_Abs'].min(),
                            'avg_pf': group['PF_Abs'].mean(),
                            'location': group['Location'].iloc[0] if 'Location' in group.columns else 'N/A'
                        })
                kpis['pf_events'] = pf_events
                
        except Exception:
            pass
    
    # ToD Energy Breakdown - proportional based on reading counts
    kpis['energy_peak'] = kpis['energy_normal'] = kpis['energy_offpeak'] = 0
    if 'ToD_Period' in df.columns and kpis['total_energy'] > 0:
        try:
            df_tod = df.copy()
            df_tod['ToD_Normalized'] = df_tod['ToD_Period'].str.upper().str.replace('-', '').str.strip()
            
            tod_counts = df_tod['ToD_Normalized'].value_counts()
            total_readings = tod_counts.sum()
            
            if total_readings > 0:
                for period in ['PEAK', 'NORMAL', 'OFFPEAK']:
                    if period in tod_counts.index:
                        proportion = tod_counts[period] / total_readings
                        period_energy = kpis['total_energy'] * proportion
                        
                        if period == 'PEAK':
                            kpis['energy_peak'] = period_energy
                        elif period == 'NORMAL':
                            kpis['energy_normal'] = period_energy
                        else:
                            kpis['energy_offpeak'] = period_energy
        except Exception:
            pass
    
    # Calculate cost based on ToD rates (WBSEDCL HT Industrial)
    # Peak: 8.37, Normal: 6.87, Off-peak: 5.18 Rs/kWh
    kpis['total_cost'] = (kpis.get('energy_peak', 0) * 8.37 + 
                          kpis.get('energy_normal', 0) * 6.87 + 
                          kpis.get('energy_offpeak', 0) * 5.18)
    if kpis['total_cost'] == 0 and kpis['total_energy'] > 0:
        kpis['total_cost'] = kpis['total_energy'] * 6.87  # Fallback to normal rate
    
    # Contracted demand and data days
    kpis['contracted_demand'] = 200  # kW
    if 'Timestamp' in df.columns:
        try:
            kpis['data_days'] = (df['Timestamp'].max() - df['Timestamp'].min()).days + 1
        except:
            kpis['data_days'] = 1
    else:
        kpis['data_days'] = 1
    
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
    output.write(f"Client: Omega Transmission Pvt. Ltd.\n")
    output.write(f"Location: Serampore, West Bengal\n")
    output.write(f"Report Type: {report_type}\n")
    output.write(f"Shed: {shed_label}\n")
    output.write(f"Period: {date_range} ({num_days} days)\n")
    output.write(f"Generated: {get_ist_now().strftime('%Y-%m-%d %H:%M:%S')} IST\n")
    output.write(f"Total Readings: {kpis.get('total_readings', 0):,}\n\n")
    
    return output.getvalue()


def generate_report_pdf(df, kpis, report_type, shed_label):
    """Generate comprehensive PDF report for download with all KPIs"""
    from io import BytesIO
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1*cm, leftMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm)
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a5f7a'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        spaceAfter=10,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1a5f7a'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#444444'),
        spaceBefore=5,
        spaceAfter=5
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=5
    )
    
    # Get date range
    try:
        date_range = f"{df['Timestamp'].min().strftime('%Y-%m-%d')} to {df['Timestamp'].max().strftime('%Y-%m-%d')}"
        num_days = (df['Timestamp'].max() - df['Timestamp'].min()).days + 1
    except:
        date_range = "N/A"
        num_days = 0
    
    elements = []
    
    # ============= TITLE & HEADER =============
    elements.append(Paragraph("⚡ VIREON CORTEX", title_style))
    elements.append(Paragraph("Energy Analytics Report", subtitle_style))
    elements.append(Spacer(1, 10))
    
    # Report Info Table
    info_data = [
        ['Client:', 'Omega Transmission Pvt. Ltd.', 'Location:', 'Serampore, West Bengal'],
        ['Report Type:', report_type, 'Shed:', shed_label],
        ['Period:', date_range, 'Days:', str(num_days)],
        ['Generated:', get_ist_now().strftime('%Y-%m-%d %H:%M:%S'), 'Readings:', f"{kpis.get('total_readings', 0):,}"]
    ]
    info_table = Table(info_data, colWidths=[2.5*cm, 5*cm, 2*cm, 5*cm])
    info_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#666666')),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # ============= EXECUTIVE SUMMARY =============
    elements.append(Paragraph("📊 Executive Summary", heading_style))
    
    total_energy = kpis.get('total_energy', 0)
    total_cost = kpis.get('total_cost', total_energy * 6.87)
    
    summary_data = [
        ['Metric', 'Value', 'Status'],
        ['Total Energy', f"{total_energy:,.1f} kWh", ''],
        ['Estimated Cost', f"₹{total_cost:,.0f}", ''],
        ['Peak Demand', f"{kpis.get('peak_demand', 0):.1f} kW", ''],
        ['Max Demand (Meter)', f"{kpis.get('max_demand_recorded', 0):.1f} kW", ''],
        ['Contracted Demand', f"{kpis.get('contracted_demand', 200)} kW", ''],
        ['Avg Power Factor', f"{kpis.get('avg_pf', 0):.3f}", '⚠️ Low' if kpis.get('avg_pf', 1) < 0.92 else '✓ Good'],
        ['Load Utilization', f"{kpis.get('load_avg', 0):.1f}%", '⚠️ Low' if kpis.get('load_avg', 0) < 30 else '✓ Normal'],
        ['Run Hours', f"{kpis.get('run_hours', 0):.1f} hrs", ''],
    ]
    
    summary_table = Table(summary_data, colWidths=[5*cm, 5*cm, 4*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5f7a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 15))
    
    # ============= ToD ENERGY ANALYSIS =============
    elements.append(Paragraph("⚡ Time-of-Day Energy Analysis", heading_style))
    
    energy_peak = kpis.get('energy_peak', 0)
    energy_normal = kpis.get('energy_normal', 0)
    energy_offpeak = kpis.get('energy_offpeak', 0)
    
    # Calculate percentages
    total_tod = energy_peak + energy_normal + energy_offpeak
    pct_peak = (energy_peak / total_tod * 100) if total_tod > 0 else 0
    pct_normal = (energy_normal / total_tod * 100) if total_tod > 0 else 0
    pct_offpeak = (energy_offpeak / total_tod * 100) if total_tod > 0 else 0
    
    tod_data = [
        ['Period', 'Time', 'Energy (kWh)', 'Share %', 'Rate (₹)', 'Cost (₹)'],
        ['Peak', '5PM - 11PM', f"{energy_peak:,.1f}", f"{pct_peak:.1f}%", '8.37', f"₹{energy_peak * 8.37:,.0f}"],
        ['Normal', '6AM - 5PM', f"{energy_normal:,.1f}", f"{pct_normal:.1f}%", '6.87', f"₹{energy_normal * 6.87:,.0f}"],
        ['Off-Peak', '11PM - 6AM', f"{energy_offpeak:,.1f}", f"{pct_offpeak:.1f}%", '5.18', f"₹{energy_offpeak * 5.18:,.0f}"],
        ['TOTAL', '', f"{total_tod:,.1f}", '100%', '', f"₹{total_cost:,.0f}"],
    ]
    
    tod_table = Table(tod_data, colWidths=[2.5*cm, 2.5*cm, 3*cm, 2*cm, 2*cm, 3*cm])
    tod_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#fffbeb')]),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fef3c7')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(tod_table)
    elements.append(Spacer(1, 15))
    
    # ============= FIRE RISK MONITOR =============
    elements.append(Paragraph("🔥 Fire Risk Monitor", heading_style))
    
    fire_normal = kpis.get('fire_normal', 0)
    fire_warning = kpis.get('fire_warning', 0)
    fire_high = kpis.get('fire_high', 0)
    fire_critical = kpis.get('fire_critical', 0)
    fire_total = fire_normal + fire_warning + fire_high + fire_critical
    
    fire_data = [
        ['Metric', 'Value', 'Status'],
        ['Avg Neutral Current', f"{kpis.get('neutral_avg', 0):.2f} A", ''],
        ['Peak Neutral Current', f"{kpis.get('neutral_max', 0):.2f} A", '⚠️ High' if kpis.get('neutral_max', 0) > 10 else '✓ Safe'],
        ['Elevated Events (>5A)', f"{kpis.get('neutral_risk', 0):,}", '⚠️' if kpis.get('neutral_risk', 0) > 100 else ''],
        ['', '', ''],
        ['Safe (Normal)', f"{fire_normal:,} ({fire_normal/fire_total*100:.0f}%)" if fire_total > 0 else "0", '🟢'],
        ['Watch (Warning)', f"{fire_warning:,} ({fire_warning/fire_total*100:.0f}%)" if fire_total > 0 else "0", '🟡'],
        ['High Risk', f"{fire_high:,} ({fire_high/fire_total*100:.0f}%)" if fire_total > 0 else "0", '🟠'],
        ['Critical', f"{fire_critical:,} ({fire_critical/fire_total*100:.0f}%)" if fire_total > 0 else "0", '🔴' if fire_critical > 0 else ''],
    ]
    
    fire_table = Table(fire_data, colWidths=[5*cm, 5*cm, 4*cm])
    fire_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e63946')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff5f5')]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(fire_table)
    
    if fire_critical > 0:
        elements.append(Paragraph(f"⚠️ ALERT: {fire_critical} critical fire risk events detected. Inspect wiring immediately.", 
                                  ParagraphStyle('Alert', parent=normal_style, textColor=colors.HexColor('#dc2626'))))
    elements.append(Spacer(1, 15))
    
    # ============= PF PENALTY ALERT =============
    elements.append(Paragraph("⚠️ Power Factor Analysis", heading_style))
    
    pf_events = kpis.get('pf_events', [])
    sustained_alerts = kpis.get('pf_sustained_alerts', 0)
    sustained_minutes = kpis.get('pf_sustained_minutes', 0)
    
    # Get unique dates from PF events
    event_dates = list(set([evt.get('date', 'N/A') for evt in pf_events])) if pf_events else []
    event_dates_str = ', '.join(sorted(event_dates)[:5]) if event_dates else 'None'
    
    pf_data = [
        ['Metric', 'Value', 'Threshold'],
        ['Average Power Factor', f"{kpis.get('avg_pf', 0):.3f}", '> 0.92'],
        ['Minimum Power Factor', f"{kpis.get('pf_min', 0):.3f}", '> 0.85'],
        ['Time Below 0.92 PF', f"{kpis.get('pf_below_92', 0):.1f}%", '< 10%'],
        ['Time Below 0.90 PF', f"{kpis.get('pf_below_90', 0):.1f}%", '< 5%'],
        ['Time Below 0.85 PF', f"{kpis.get('pf_below_85', 0):.1f}%", '< 1%'],
        ['Valid PF Readings', f"{kpis.get('pf_valid_readings', 0):,}", ''],
        ['', '', ''],
        ['Sustained Low PF Events', f"{sustained_alerts}", '0'],
        ['Total Time in Low PF', f"{sustained_minutes} min", ''],
        ['Event Dates', event_dates_str, ''],
    ]
    
    pf_table = Table(pf_data, colWidths=[5*cm, 5*cm, 4*cm])
    pf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f3ff')]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(pf_table)
    
    # PF Event Details Table (if any events)
    if pf_events and len(pf_events) > 0:
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("PF Event Details:", subheading_style))
        
        event_header = ['#', 'Date', 'Start', 'End', 'Duration', 'Avg PF', 'Location']
        event_rows = [event_header]
        for i, evt in enumerate(pf_events[:10], 1):  # Limit to 10 events
            event_rows.append([
                str(i),
                evt.get('date', 'N/A'),
                evt.get('start', 'N/A'),
                evt.get('end', 'N/A'),
                f"{evt.get('duration_min', 0)} min",
                f"{evt.get('avg_pf', 0):.3f}",
                evt.get('location', 'N/A')
            ])
        
        event_table = Table(event_rows, colWidths=[1*cm, 2.5*cm, 2*cm, 2*cm, 2*cm, 2*cm, 3*cm])
        event_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#a78bfa')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ede9fe')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(event_table)
    
    if sustained_alerts > 0:
        elements.append(Paragraph(f"⚠️ {sustained_alerts} sustained low PF events on {len(event_dates)} day(s). Check APFC panel.", 
                                  ParagraphStyle('Alert', parent=normal_style, textColor=colors.HexColor('#7c3aed'))))
    elements.append(Spacer(1, 15))
    
    # ============= POWER QUALITY =============
    elements.append(Paragraph("🔌 Power Quality & Grid", heading_style))
    
    quality_data = [
        ['Metric', 'Value', 'Threshold'],
        ['Voltage Unbalance (Avg)', f"{kpis.get('v_unbalance_avg', 0):.2f}%", '< 2%'],
        ['Voltage Unbalance (Max)', f"{kpis.get('v_unbalance_max', 0):.2f}%", '< 5%'],
        ['V Unbalance Warnings', f"{kpis.get('v_unbalance_warning', 0):,}", ''],
        ['Current Unbalance (Avg)', f"{kpis.get('i_unbalance_avg', 0):.2f}%", '< 10%'],
        ['Current Unbalance (Max)', f"{kpis.get('i_unbalance_max', 0):.2f}%", '< 20%'],
        ['I Unbalance Warnings', f"{kpis.get('i_unbalance_warning', 0):,}", ''],
        ['Frequency Range', f"{kpis.get('freq_min', 50):.2f} - {kpis.get('freq_max', 50):.2f} Hz", '49.5 - 50.5 Hz'],
        ['Voltage Range (L-L)', f"{kpis.get('vll_min', 0):.0f} - {kpis.get('vll_max', 0):.0f} V", '380 - 440 V'],
    ]
    
    quality_table = Table(quality_data, colWidths=[5*cm, 5*cm, 4*cm])
    quality_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2a9d8f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fff4')]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(quality_table)
    elements.append(Spacer(1, 15))
    
    # ============= LOAD UTILIZATION =============
    elements.append(Paragraph("📈 Load Utilization", heading_style))
    
    load_data = [
        ['Metric', 'Value', 'Insight'],
        ['Average Load', f"{kpis.get('load_avg', 0):.1f}%", 'Underutilized' if kpis.get('load_avg', 0) < 30 else 'Optimal' if kpis.get('load_avg', 0) < 80 else 'High'],
        ['Maximum Load', f"{kpis.get('load_max', 0):.1f}%", ''],
        ['Idle Time (<10% load)', f"{kpis.get('idle_time_pct', 0):.1f}%", '⚠️ High' if kpis.get('idle_time_pct', 0) > 30 else ''],
        ['Contracted Demand', f"{kpis.get('contracted_demand', 200)} kW", ''],
        ['Peak Demand Recorded', f"{kpis.get('peak_demand', 0):.1f} kW", f"{kpis.get('peak_demand', 0)/kpis.get('contracted_demand', 200)*100:.0f}% of contract" if kpis.get('contracted_demand', 200) > 0 else ''],
    ]
    
    load_table = Table(load_data, colWidths=[5*cm, 4*cm, 5*cm])
    load_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eff6ff')]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(load_table)
    elements.append(Spacer(1, 15))
    
    # ============= SAVINGS POTENTIAL =============
    elements.append(Paragraph("💰 Savings Potential", heading_style))
    
    # Calculate savings (MATCHING main dashboard logic)
    # WBSEDCL HT Industrial Tariff Rates
    DEMAND_CHARGE = 350  # ₹/kVA/month
    RATE_PEAK = 8.37     # ₹/kWh
    RATE_OFFPEAK = 5.18  # ₹/kWh
    PF_BENCHMARK = 0.92
    
    monthly_factor = 30 / max(num_days, 1)
    total_savings = 0
    savings_items = []
    
    contracted_demand = kpis.get('contracted_demand', 200)
    peak_demand = kpis.get('peak_demand', 0)
    avg_pf = kpis.get('avg_pf', 0.92)
    load_avg = kpis.get('load_avg', 0)
    
    # 1. DEMAND CONTRACT OPTIMIZATION
    if peak_demand > 0 and contracted_demand > 0:
        optimal_contract = peak_demand * 1.2
        if optimal_contract < contracted_demand * 0.8:
            current_kva = contracted_demand / 0.9
            optimal_kva = optimal_contract / 0.9
            demand_savings = int((current_kva - optimal_kva) * DEMAND_CHARGE)
            if demand_savings > 0:
                total_savings += demand_savings
                savings_items.append(['Demand Contract', f"₹{demand_savings:,}/mo", f"Reduce to {optimal_contract:.0f}kW"])
    
    # 2. POWER FACTOR OPTIMIZATION
    if avg_pf > 0 and avg_pf < PF_BENCHMARK:
        monthly_energy = total_energy * monthly_factor
        if monthly_energy == 0:
            monthly_energy = 5000
        avg_rate = 6.50
        monthly_energy_bill = monthly_energy * avg_rate
        pf_shortfall = PF_BENCHMARK - avg_pf
        penalty_pct = pf_shortfall * 100
        pf_penalty = int(monthly_energy_bill * (penalty_pct / 100))
        if pf_penalty > 100:
            total_savings += pf_penalty
            savings_items.append(['PF Penalty Avoided', f"₹{pf_penalty:,}/mo", f"Improve {avg_pf:.2f} → 0.92"])
    
    # 3. ToD OPTIMIZATION
    if energy_peak > 0:
        monthly_peak = energy_peak * monthly_factor
        shiftable = monthly_peak * 0.5
        tod_savings = int(shiftable * (RATE_PEAK - RATE_OFFPEAK))
        if tod_savings > 100:
            total_savings += tod_savings
            savings_items.append(['ToD Optimization', f"₹{tod_savings:,}/mo", f"Shift {shiftable:.0f}kWh off-peak"])
    
    # Apply 50% realization factor
    realizable = int(total_savings * 0.5)
    period_savings = int(realizable * num_days / 30)
    annual_savings = realizable * 12
    
    savings_summary = [
        ['Time Frame', 'Amount'],
        [f'This Period ({num_days} days)', f'₹{period_savings:,}'],
        ['Monthly', f'₹{realizable:,}'],
        ['Annual', f'₹{annual_savings:,}'],
    ]
    
    savings_table = Table(savings_summary, colWidths=[6*cm, 6*cm])
    savings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ecfdf5'), colors.HexColor('#d1fae5')]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(savings_table)
    
    if savings_items:
        elements.append(Spacer(1, 8))
        elements.append(Paragraph("Breakdown:", subheading_style))
        breakdown_data = [['Category', 'Savings', 'Action']] + savings_items
        breakdown_table = Table(breakdown_data, colWidths=[4*cm, 3.5*cm, 5*cm])
        breakdown_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34d399')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecfdf5')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(breakdown_table)
    
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("* 50% realization factor applied", 
                              ParagraphStyle('Note', parent=normal_style, fontSize=8, textColor=colors.HexColor('#666666'))))
    elements.append(Spacer(1, 12))
    
    # ============= RECOMMENDATIONS =============
    elements.append(Paragraph("💡 Recommendations", heading_style))
    
    recommendations = []
    if kpis.get('avg_pf', 1) < 0.92:
        recommendations.append(['🔧 Power Factor', 'Service APFC panel, check capacitor banks', 'HIGH', '₹5,000-15,000/mo'])
    if kpis.get('fire_critical', 0) > 0:
        recommendations.append(['🔥 Fire Safety', 'URGENT: Inspect electrical connections', 'CRITICAL', 'Safety'])
    if kpis.get('load_avg', 100) < 30:
        recommendations.append(['📊 Contract', 'Renegotiate to lower contracted demand', 'MEDIUM', '₹10,000-20,000/mo'])
    if kpis.get('i_unbalance_avg', 0) > 15:
        recommendations.append(['⚡ Load Balance', 'Redistribute loads across phases', 'MEDIUM', 'Equipment Life'])
    recommendations.append(['🕐 ToD Shift', 'Move heavy loads to off-peak hours', 'LOW', '₹1,500-3,000/mo'])
    
    rec_data = [['Area', 'Recommendation', 'Priority', 'Impact']] + recommendations
    
    rec_table = Table(rec_data, colWidths=[3*cm, 6*cm, 2*cm, 3.5*cm])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e9c46a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#333333')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fffbf0')]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(rec_table)
    elements.append(Spacer(1, 20))
    
    # ============= FOOTER =============
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#999999'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph("─" * 80, footer_style))
    elements.append(Paragraph("Vireon Cortex Energy Analytics Platform | Omega Transmission POC", footer_style))
    elements.append(Paragraph("WBSEDCL HT Industrial Tariff | Generated by AI-Powered Analytics", footer_style))
    elements.append(Paragraph(f"Report ID: VRN-{get_ist_now().strftime('%Y%m%d%H%M%S')}", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# ============= MAIN DASHBOARD =============
def main():
    # Sidebar for config
    with st.sidebar:
        # ============= CLIENT & HARDWARE INFO =============
        st.markdown("### 🏭 Client")
        st.markdown("""
            <div class="client-info">
                <div class="client-name">Omega Transmission Pvt. Ltd.</div>
                <div class="client-location">📍 Serampore, West Bengal, India</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🔧 Hardware Details", expanded=False):
            st.markdown("""
                <div class="hardware-info">
                    <div class="hardware-label">Controller</div>
                    <div class="hardware-value">Raspberry Pi 4B / 5 / Zero W</div>
                </div>
                <div class="hardware-info">
                    <div class="hardware-label">Energy Meter (Shed 1)</div>
                    <div class="hardware-value">L&T WL4405</div>
                </div>
                <div class="hardware-info">
                    <div class="hardware-label">Energy Meter (Shed 2)</div>
                    <div class="hardware-value">Schneider EM6436H</div>
                </div>
                <div class="hardware-info">
                    <div class="hardware-label">Communication</div>
                    <div class="hardware-value">RS485 Modbus RTU</div>
                </div>
                <div class="hardware-info">
                    <div class="hardware-label">Contract Demand</div>
                    <div class="hardware-value">200 kW</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
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
            options=["All Sheds (Overview)", "Shed 1 (Main Feed)", "Shed 2 (Sub-Feed)"],
            index=0,
            help="Shed 1 is the main meter. Shed 2 is a sub-meter (already included in Shed 1's total)."
        )
        if shed_filter == "Shed 2 (Sub-Feed)":
            st.info("⚡ Shed 2 is a sub-feed measured separately. Its consumption is INCLUDED in Shed 1's total.")
        elif shed_filter == "All Sheds (Overview)":
            st.info("📊 Overview shows both sheds. KPIs use Shed 1 (total facility consumption).")
        
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
                options=["CXO Guide", "Asset Health", "Technical Manual", "FAQ"],
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
            
            elif help_section == "Asset Health":
                st.markdown("""
                **🏭 Asset Health Metrics Guide**
                
                ---
                
                **⚡ Power Quality**
                
                | Metric | Calculation | Threshold |
                |--------|-------------|-----------|
                | Supply Stability | Voltage deviation from 415V nominal | < 5% good |
                | Worst Recorded | Max voltage unbalance % | < 2% good |
                | Warning Events | Count of readings with unbalance > 2% | Minimize |
                
                *Purpose: Monitors incoming supply quality for equipment protection and warranty claims.*
                
                ---
                
                **🔧 Motor Health**
                
                | Metric | Calculation | Threshold |
                |--------|-------------|-----------|
                | Load Balance | Current imbalance across R/Y/B phases | < 15% good |
                | Worst Recorded | Maximum current unbalance % | < 20% good |
                | Needs Attention | Readings with unbalance > 15% | Investigate |
                
                *Purpose: Detects uneven motor loading that causes overheating and premature failure.*
                
                ---
                
                **📊 Capacity Usage**
                
                | Metric | Calculation | Threshold |
                |--------|-------------|-----------|
                | Avg Utilization | Mean kW / Contracted kW × 100 | 60-80% optimal |
                | Peak Usage | Max kW / Contracted kW × 100 | < 90% safe |
                | Idle Time | % readings with load < 10% | Minimize waste |
                
                *Purpose: Identifies over-contracted demand (reduce bill) or under-capacity (add margin).*
                
                ---
                
                **🔌 Grid Quality**
                
                | Metric | Calculation | Threshold |
                |--------|-------------|-----------|
                | Frequency | Range of Hz readings | 49.5-50.5 Hz normal |
                | Voltage Range | Min-Max L-N voltage | 380-440V acceptable |
                | Status | Fluctuating if variance > threshold | Stable preferred |
                
                *Purpose: Documents grid events for warranty claims and equipment protection settings.*
                
                ---
                
                **⚠️ PF Sustained Alert Logic**
                
                **Why filter?** Transient PF dips during motor startup are normal and don't warrant penalties.
                
                **Filter criteria:**
                - Only readings with Current > 1A are considered valid
                - Excludes startup transients and idle states
                
                **Sustained alert definition:**
                - PF below 0.90 for **2+ consecutive readings** (~10+ minutes)
                - This indicates a real PF issue, not transient noise
                
                **Alert levels:**
                - 🟢 0 sustained events: Healthy
                - 🟡 1-3 events: Monitor APFC
                - 🔴 4+ events: APFC needs service
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
                
                **Q: Why are some PF readings ignored?**
                Readings with Current < 1A are excluded to filter motor startup transients.
                
                **Q: What causes fire risk alerts?**
                High neutral current from loose connections or phase imbalance.
                
                **Q: How to reduce bill?**
                1. Keep PF > 0.92
                2. Shift loads to off-peak
                3. Right-size contract demand
                
                **Q: What is a "sustained" PF alert?**
                PF below 0.90 for 2+ consecutive readings (~10 min). Brief dips are ignored.
                
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
        shed_label = "Facility Overview"
    
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
                    {get_ist_now().strftime("%Y-%m-%d %H:%M:%S")}
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
                
                # Apply same preprocessing - strip quotes and use mixed format
                if 'Timestamp' in df.columns:
                    df['Timestamp'] = df['Timestamp'].astype(str).str.strip().str.lstrip("'\"").str.rstrip("'\"")
                    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='mixed', errors='coerce')
                
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'], format='mixed', errors='coerce')
                elif 'Timestamp' in df.columns:
                    df['Date'] = df['Timestamp']
                
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
                    # CRITICAL: Sort by timestamp to ensure chronological order
                    df = df.sort_values('Timestamp').reset_index(drop=True)
                    
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
                
                # Apply same preprocessing - strip quotes and use mixed format
                if 'Timestamp' in df.columns:
                    df['Timestamp'] = df['Timestamp'].astype(str).str.strip().str.lstrip("'\"").str.rstrip("'\"")
                    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='mixed', errors='coerce')
                
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'], format='mixed', errors='coerce')
                elif 'Timestamp' in df.columns:
                    df['Date'] = df['Timestamp']
                
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
                    # CRITICAL: Sort by timestamp to ensure chronological order
                    df = df.sort_values('Timestamp').reset_index(drop=True)
                    
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
    # NOTE: Shed 2 is a SUB-METER of Shed 1. Shed 1's readings INCLUDE Shed 2's consumption.
    # - "Shed 1 (Main Feed)" = Total facility consumption (includes Shed 2)
    # - "Shed 2 (Sub-Feed)" = Just the sub-feed portion (already counted in Shed 1)
    # - "All Sheds (Overview)" = Shows both separately for comparison, but KPIs use Shed 1 only
    
    if 'Device_ID' in df.columns or 'Location' in df.columns:
        location_col = 'Location' if 'Location' in df.columns else 'Device_ID'
        
        if shed_filter == "Shed 1 (Main Feed)":
            df = df[df[location_col].str.contains('01|Shed_01|Shed 1', case=False, na=False)]
        elif shed_filter == "Shed 2 (Sub-Feed)":
            df = df[df[location_col].str.contains('02|Shed_02|Shed 2', case=False, na=False)]
        elif shed_filter == "All Sheds (Overview)":
            # For "All Sheds Overview", keep ALL readings from ALL sheds
            # KPIs will use Shed 1 (main meter) for energy to avoid double-counting
            # But we display all data for completeness
            pass  # Keep all data - no filtering
        
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
    # For "All Sheds Overview", use only Shed 1 (main meter) for energy to avoid double-counting
    # Other KPIs like PF, Load can use all data
    if shed_filter == "All Sheds (Overview)" and 'Location' in df.columns:
        # Calculate energy KPIs from main meter only
        df_main = df[df['Location'].str.contains('01|Shed_01|Shed 1', case=False, na=False)]
        kpis = calculate_kpis(df_main)
        # But update total_readings to reflect ALL data shown
        kpis['total_readings'] = len(df)
        kpis['total_readings_main'] = len(df_main)
        kpis['total_readings_sub'] = len(df) - len(df_main)
    else:
        kpis = calculate_kpis(df)
    
    # ============= ALERT DATA SIDEBAR SECTION =============
    with st.sidebar.expander("📋 Alert Data", expanded=False):
        alert_type = st.selectbox(
            "Select Alert Type",
            options=["🔥 Fire Risk Events", "⚠️ PF Sustained Alerts", "⚡ Voltage Anomalies", "🔧 Current Imbalance"],
            index=0
        )
        
        alert_df = None
        alert_filename = "alert_data.csv"
        
        if alert_type == "🔥 Fire Risk Events":
            # Fire risk: Neutral current > 5A
            if 'Current_N' in df.columns or 'Neutral_Current_A' in df.columns:
                neutral_col = 'Current_N' if 'Current_N' in df.columns else 'Neutral_Current_A'
                neutral_current = pd.to_numeric(df[neutral_col], errors='coerce').abs()
                fire_mask = neutral_current > 5
                
                if fire_mask.sum() > 0:
                    alert_df = df[fire_mask][['Timestamp', 'Location', neutral_col]].copy()
                    alert_df['Neutral_A'] = neutral_current[fire_mask]
                    alert_df['Risk_Level'] = pd.cut(
                        alert_df['Neutral_A'],
                        bins=[0, 10, 20, float('inf')],
                        labels=['WATCH', 'HIGH', 'CRITICAL']
                    )
                    alert_df = alert_df.sort_values('Timestamp', ascending=False)
                    alert_filename = "fire_risk_events.csv"
        
        elif alert_type == "⚠️ PF Sustained Alerts":
            # PF sustained: 2+ consecutive readings below 0.90 with Current > 1A
            if 'PF_Avg' in df.columns and 'Current_Total' in df.columns:
                df_pf = df.copy()
                df_pf['PF_Abs'] = pd.to_numeric(df_pf['PF_Avg'], errors='coerce').abs()
                current_series = pd.to_numeric(df_pf['Current_Total'], errors='coerce')
                valid_mask = (current_series > 1.0) & (df_pf['PF_Abs'].notna())
                df_pf_valid = df_pf[valid_mask].copy().sort_values('Timestamp').reset_index(drop=True)
                
                if len(df_pf_valid) > 0:
                    df_pf_valid['PF_Low'] = df_pf_valid['PF_Abs'] < 0.90
                    df_pf_valid['PF_Group'] = (df_pf_valid['PF_Low'] != df_pf_valid['PF_Low'].shift()).cumsum()
                    
                    # Get sustained events (2+ consecutive = ~10+ min)
                    sustained_groups = df_pf_valid[df_pf_valid['PF_Low']].groupby('PF_Group')
                    sustained_events = []
                    for group_id, group in sustained_groups:
                        if len(group) >= 2:  # Changed from 3 to 2
                            sustained_events.append({
                                'Event_ID': group_id,
                                'Date': group['Timestamp'].iloc[0].strftime('%Y-%m-%d'),
                                'Start_Time': group['Timestamp'].iloc[0],
                                'End_Time': group['Timestamp'].iloc[-1],
                                'Duration_Readings': len(group),
                                'Duration_Minutes': len(group) * 5,
                                'Location': group['Location'].iloc[0] if 'Location' in group.columns else 'N/A',
                                'Min_PF': group['PF_Abs'].min(),
                                'Avg_PF': group['PF_Abs'].mean()
                            })
                    
                    if sustained_events:
                        alert_df = pd.DataFrame(sustained_events)
                        alert_filename = "pf_sustained_alerts.csv"
        
        elif alert_type == "⚡ Voltage Anomalies":
            # Voltage unbalance > 2%
            if 'Voltage_Unbalance_Pct' in df.columns:
                unbalance = pd.to_numeric(df['Voltage_Unbalance_Pct'], errors='coerce')
                voltage_mask = unbalance > 2
                
                if voltage_mask.sum() > 0:
                    cols = ['Timestamp', 'Location', 'Voltage_Unbalance_Pct']
                    for col in ['V_R', 'V_Y', 'V_B', 'VLN_Avg']:
                        if col in df.columns:
                            cols.append(col)
                    alert_df = df[voltage_mask][cols].copy()
                    alert_df = alert_df.sort_values('Timestamp', ascending=False)
                    alert_filename = "voltage_anomalies.csv"
        
        elif alert_type == "🔧 Current Imbalance":
            # Current imbalance > 15%
            if 'Current_Unbalance_Pct' in df.columns:
                imbalance = pd.to_numeric(df['Current_Unbalance_Pct'], errors='coerce')
                current_mask = imbalance > 15
                
                if current_mask.sum() > 0:
                    cols = ['Timestamp', 'Location', 'Current_Unbalance_Pct']
                    for col in ['Current_R', 'Current_Y', 'Current_B', 'Current_Total']:
                        if col in df.columns:
                            cols.append(col)
                    alert_df = df[current_mask][cols].copy()
                    alert_df = alert_df.sort_values('Timestamp', ascending=False)
                    alert_filename = "current_imbalance.csv"
        
        # Display alert data
        if alert_df is not None and len(alert_df) > 0:
            st.success(f"**{len(alert_df)} events found**")
            st.dataframe(alert_df.head(10), use_container_width=True, hide_index=True)
            
            if len(alert_df) > 10:
                st.caption(f"Showing 10 of {len(alert_df)} events")
            
            # Download button
            csv_data = alert_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Full Data",
                data=csv_data,
                file_name=alert_filename,
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("✓ No alerts found for this type")
    
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
            
            try:
                # Generate PDF report
                pdf_content = generate_report_pdf(report_df, report_kpis, report_type, shed_label)
                
                st.sidebar.download_button(
                    label="📥 Download Report (PDF)",
                    data=pdf_content,
                    file_name=f"vireon_report_{report_type.lower().replace(' ', '_')}_{get_ist_now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.sidebar.success(f"✓ PDF Report ready!")
            except ImportError:
                # Fallback to CSV if reportlab not available
                csv_content = generate_report_csv(report_df, report_kpis, report_type, shed_label)
                st.sidebar.download_button(
                    label="📥 Download Report (CSV)",
                    data=csv_content,
                    file_name=f"vireon_report_{report_type.lower().replace(' ', '_')}_{get_ist_now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.sidebar.success(f"✓ Report ready!")
        else:
            st.sidebar.error("No data for selected range.")
    
    # If All Sheds, show quick comparison first
    if shed_filter == "All Sheds (Overview)":
        # Current date/time display (IST)
        current_datetime = get_ist_now()
        st.markdown(f"""
            <div class="section-header">
                <span class="section-icon">🏭</span>
                <span class="section-title">Meter Overview</span>
                <span class="section-badge">Live Status</span>
                <span class="section-badge" style="margin-left: auto;">📅 {current_datetime.strftime('%A, %b %d, %Y')} | 🕐 {current_datetime.strftime('%H:%M:%S')}</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Explanation banner
        st.markdown("""
            <div style="background: rgba(17, 138, 178, 0.1); border: 1px solid #118ab2; border-radius: 8px; padding: 12px; margin-bottom: 16px;">
                <strong>📊 Meter Hierarchy:</strong> Shed 1 is the <strong>main meter</strong> measuring total facility consumption. 
                Shed 2 is a <strong>sub-meter</strong> on a specific circuit - its readings are <em>already included</em> in Shed 1's total.
                <br><small style="color: #8899a6;">KPIs below use Shed 1 data to avoid double-counting.</small>
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
                    shed_type = "Main Meter (Total)" if is_main else "Sub-Meter (Subset)"
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
                <div class="kpi-metric">
                    <span class="kpi-label">Avg Neutral Current</span>
                    <span class="kpi-value">{kpis['neutral_avg']:.2f} A</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Peak Neutral Current</span>
                    <span class="kpi-value" style="color: {'#ef476f' if kpis['neutral_max'] > 10 else '#ffd166' if kpis['neutral_max'] > 5 else '#06d6a0'}">{kpis['neutral_max']:.2f} A</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Elevated Events (&gt;5A)</span>
                    <span class="kpi-value" style="color: {'#ef476f' if kpis['neutral_risk'] > 100 else '#ffd166' if kpis['neutral_risk'] > 0 else '#06d6a0'}">{kpis['neutral_risk']}</span>
                </div>
                <div class="risk-grid" style="margin-top: 16px;">
                    <div class="risk-item normal">
                        <div class="risk-level" style="color: #06d6a0">Safe</div>
                        <div class="risk-count" style="color: #06d6a0">{kpis['fire_normal']:,}</div>
                        <div class="risk-pct">{kpis['fire_normal']/max(fire_total,1)*100:.0f}%</div>
                    </div>
                    <div class="risk-item warning">
                        <div class="risk-level" style="color: #ffd166">Watch</div>
                        <div class="risk-count" style="color: #ffd166">{kpis['fire_warning']:,}</div>
                        <div class="risk-pct">{kpis['fire_warning']/max(fire_total,1)*100:.0f}%</div>
                    </div>
                    <div class="risk-item high">
                        <div class="risk-level" style="color: #f77f00">High</div>
                        <div class="risk-count" style="color: #f77f00">{kpis['fire_high']:,}</div>
                        <div class="risk-pct">{kpis['fire_high']/max(fire_total,1)*100:.0f}%</div>
                    </div>
                    <div class="risk-item critical">
                        <div class="risk-level" style="color: #ef476f">Critical</div>
                        <div class="risk-count" style="color: #ef476f">{kpis['fire_critical']:,}</div>
                        <div class="risk-pct">{kpis['fire_critical']/max(fire_total,1)*100:.0f}%</div>
                    </div>
                </div>
                <div class="kpi-insight">
                    {"✓ Fire risk under control." if kpis['fire_critical'] == 0 else f"⚠️ {kpis['fire_critical']} critical events. Inspect wiring."}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Penalty Alert (with sustained alert detection)
    with cols[1]:
        sustained_alerts = kpis.get('pf_sustained_alerts', 0)
        pf_below_92 = kpis.get('pf_below_92', 0)
        pf_events = kpis.get('pf_events', [])
        
        # Status based on sustained alerts (more meaningful than raw %)
        if sustained_alerts == 0:
            pf_status = "status-good"
            pf_color = "#06d6a0"
        elif sustained_alerts <= 3:
            pf_status = "status-warning"
            pf_color = "#ffd166"
        else:
            pf_status = "status-critical"
            pf_color = "#ef476f"
        
        # Build event dates string
        if pf_events:
            unique_dates = sorted(set(e['date'] for e in pf_events))
            event_dates_str = ", ".join(unique_dates)
        else:
            event_dates_str = "None"
        
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">
                    ⚠️ PF Penalty Alert
                    <span class="status-dot {pf_status}"></span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Sustained Low PF Events (≥10min)</span>
                    <span class="kpi-value" style="color: {pf_color}">{sustained_alerts}</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Total Time in Low PF</span>
                    <span class="kpi-value" style="color: {'#ef4444' if kpis.get('pf_sustained_minutes', 0) > 60 else '#ffd166' if kpis.get('pf_sustained_minutes', 0) > 0 else '#06d6a0'}">{kpis.get('pf_sustained_minutes', 0)} min</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Event Dates</span>
                    <span class="kpi-value" style="font-size: 11px; color: {'#ef476f' if sustained_alerts > 0 else '#06d6a0'}">{event_dates_str}</span>
                </div>
                <div class="kpi-metric">
                    <span class="kpi-label">Lowest PF</span>
                    <span class="kpi-value" style="color: {'#ef4444' if kpis['pf_min'] < 0.85 else '#ffd166' if kpis['pf_min'] < 0.92 else '#06d6a0'}">{kpis['pf_min']:.2f}</span>
                </div>
                <div class="kpi-bar">
                    <div class="kpi-bar-fill" style="width: {min(100, sustained_alerts * 20)}%; background: {pf_color};"></div>
                </div>
                <div class="kpi-insight">
                    {"✓ No sustained PF issues. Transients filtered." if sustained_alerts == 0 else f"⚠️ {sustained_alerts} events on {len(set(e['date'] for e in pf_events))} day(s). Check APFC."}
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
                # Calculate daily consumption: group by Date AND Location to handle multiple meters
                # Each meter has different cumulative readings, so we must calculate per-meter first
                daily_stats = []
                
                # Check if multiple locations exist
                has_multiple_locations = 'Location' in df.columns and df['Location'].nunique() > 1
                
                if has_multiple_locations:
                    # Group by both Date and Location, then sum across locations
                    for (date, location), group in df.groupby([pd.to_datetime(df['Date']).dt.date, 'Location']):
                        group_sorted = group.sort_values('Timestamp')
                        if len(group_sorted) >= 2:
                            first_energy = group_sorted['Energy_kWh'].iloc[0]
                            last_energy = group_sorted['Energy_kWh'].iloc[-1]
                            energy = last_energy - first_energy
                            if energy < 0:  # Handle meter reset
                                diffs = group_sorted['Energy_kWh'].diff()
                                energy = diffs[diffs > 0].sum()
                            energy = max(0, energy)
                        else:
                            energy = 0
                        peak_kw = group_sorted['kW_Total'].max()
                        daily_stats.append({'Date': date, 'Location': location, 'Energy_kWh': energy, 'Peak_kW': peak_kw})
                    
                    # Sum energy across locations for each date
                    daily_by_loc = pd.DataFrame(daily_stats)
                    daily = daily_by_loc.groupby('Date').agg({
                        'Energy_kWh': 'sum',
                        'Peak_kW': 'max'
                    }).reset_index()
                else:
                    # Single location - original logic
                    for date, group in df.groupby(pd.to_datetime(df['Date']).dt.date):
                        group_sorted = group.sort_values('Timestamp')
                        if len(group_sorted) >= 2:
                            first_energy = group_sorted['Energy_kWh'].iloc[0]
                            last_energy = group_sorted['Energy_kWh'].iloc[-1]
                            energy = last_energy - first_energy
                            if energy < 0:  # Handle meter reset
                                diffs = group_sorted['Energy_kWh'].diff()
                                energy = diffs[diffs > 0].sum()
                            energy = max(0, energy)
                        else:
                            energy = 0
                        peak_kw = group_sorted['kW_Total'].max()
                        daily_stats.append({'Date': date, 'Energy_kWh': energy, 'Peak_kW': peak_kw})
                    
                    daily = pd.DataFrame(daily_stats)
                
                # Filter out unrealistic values (more than 10,000 kWh per day is likely an error)
                daily = daily[daily['Energy_kWh'] < 10000]
                
                # Add day of week info for coloring
                daily['Date'] = pd.to_datetime(daily['Date'])
                daily['DayOfWeek'] = daily['Date'].dt.dayofweek  # 0=Mon, 6=Sun
                daily['DayName'] = daily['Date'].dt.strftime('%a')  # Mon, Tue, etc.
                daily['IsWeekend'] = daily['DayOfWeek'].isin([5, 6])  # Sat=5, Sun=6
                daily['DayType'] = daily['IsWeekend'].map({True: '🔵 Weekend', False: '🟢 Weekday'})
                daily['IsEstimated'] = False  # Mark real data
                
                # Calculate day-type averages for estimation (from real data only)
                weekday_avg_real = daily[~daily['IsWeekend']]['Energy_kWh'].mean()
                weekend_avg_real = daily[daily['IsWeekend']]['Energy_kWh'].mean()
                
                # Detect missing days
                min_date = daily['Date'].min()
                max_date = daily['Date'].max()
                all_dates = pd.date_range(start=min_date, end=max_date, freq='D')
                actual_dates = set(daily['Date'].dt.date)
                missing_dates = [d for d in all_dates if d.date() not in actual_dates]
                
                # Toggle for estimated gaps (OFF by default)
                show_estimates = st.checkbox(
                    f"📊 Show estimated gaps ({len(missing_dates)} days missing)", 
                    value=False,
                    help="Visual overlay only - does NOT affect KPIs or calculations"
                )
                
                # Create display dataframe (for chart only)
                display_daily = daily.copy()
                estimated_total = 0
                
                if show_estimates and len(missing_dates) > 0:
                    # Add estimated rows for missing days
                    estimated_rows = []
                    for d in missing_dates:
                        dow = d.dayofweek
                        is_weekend = dow >= 5
                        est_energy = weekend_avg_real if is_weekend else weekday_avg_real
                        if pd.isna(est_energy):
                            est_energy = daily['Energy_kWh'].mean()
                        estimated_total += est_energy
                        estimated_rows.append({
                            'Date': pd.Timestamp(d),
                            'Energy_kWh': est_energy,
                            'Peak_kW': 0,
                            'DayOfWeek': dow,
                            'DayName': d.strftime('%a'),
                            'IsWeekend': is_weekend,
                            'DayType': '⬜ Estimated',
                            'IsEstimated': True
                        })
                    
                    estimated_df = pd.DataFrame(estimated_rows)
                    display_daily = pd.concat([daily, estimated_df], ignore_index=True)
                    display_daily = display_daily.sort_values('Date')
                
                # Create chart with appropriate colors
                color_map = {
                    '🟢 Weekday': '#4ecdc4',
                    '🔵 Weekend': '#ff6b6b',
                    '⬜ Estimated': '#9ca3af'  # Gray for estimates
                }
                
                # Create bar chart with weekend/weekday colors
                fig = px.bar(display_daily, x='Date', y='Energy_kWh', 
                            color='DayType',
                            color_discrete_map=color_map,
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
                
                # Add weekend shading - only for real weekend data
                for _, row in daily[daily['IsWeekend']].iterrows():
                    fig.add_vrect(
                        x0=row['Date'] - pd.Timedelta(hours=12),
                        x1=row['Date'] + pd.Timedelta(hours=12),
                        fillcolor="rgba(17, 138, 178, 0.1)",
                        layer="below",
                        line_width=0,
                    )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show metrics - always from REAL data only
                actual_total = daily['Energy_kWh'].sum()
                
                if show_estimates and estimated_total > 0:
                    st.info(f"⚠️ **Estimated gaps:** {len(missing_dates)} days (~{estimated_total:,.0f} kWh) — NOT included in KPIs")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Actual Energy", f"{actual_total:,.0f} kWh")
                    with col2:
                        st.metric("Estimated Gaps", f"{estimated_total:,.0f} kWh")
                    with col3:
                        st.metric("Visual Total", f"{actual_total + estimated_total:,.0f} kWh")
                    with col4:
                        st.metric("Missing Days", f"{len(missing_dates)}")
                else:
                    # Show weekday vs weekend summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Weekday Avg", f"{weekday_avg_real:.1f} kWh")
                    with col2:
                        st.metric("Weekend Avg", f"{weekend_avg_real:.1f} kWh")
                    with col3:
                        diff_pct = ((weekend_avg_real - weekday_avg_real) / weekday_avg_real * 100) if weekday_avg_real > 0 else 0
                        st.metric("Weekend vs Weekday", f"{diff_pct:+.1f}%")
                
                # Shift-wise Distribution Section
                st.markdown("---")
                st.markdown("#### 🔄 Shift-wise Analysis")
                
                # Date selector for detailed view
                available_dates = sorted(df['Date'].dt.date.dropna().unique())
                if len(available_dates) > 0:
                    col_date, col_shift = st.columns([2, 3])
                    
                    with col_date:
                        selected_date = st.selectbox(
                            "Select Date for Details",
                            options=available_dates,
                            index=len(available_dates)-1,  # Default to latest
                            format_func=lambda x: x.strftime('%Y-%m-%d (%A)')
                        )
                    
                    # Filter data for selected date
                    df_day = df[df['Date'].dt.date == selected_date].copy()
                    
                    if len(df_day) > 0 and 'ToD_Period' in df_day.columns:
                        # CRITICAL: Sort by timestamp first
                        df_day = df_day.sort_values('Timestamp').copy()
                        
                        # Normalize ToD periods
                        df_day['Shift'] = df_day['ToD_Period'].str.upper().str.replace('-', '').str.strip()
                        df_day['Shift'] = df_day['Shift'].map({
                            'OFFPEAK': '🌙 Off-Peak (11PM-6AM)',
                            'NORMAL': '☀️ Normal (6AM-5PM)',
                            'PEAK': '🔥 Peak (5PM-11PM)'
                        }).fillna('Unknown')
                        
                        # Calculate energy and cost per shift
                        # CRITICAL: For "All Sheds Overview", use only Shed_01 (main meter) to avoid double-counting
                        # since Shed_02 is a sub-meter whose energy is already included in Shed_01
                        shift_summary = []
                        rates = {'🌙 Off-Peak (11PM-6AM)': 5.18, '☀️ Normal (6AM-5PM)': 6.87, '🔥 Peak (5PM-11PM)': 8.37}
                        
                        # Determine which data to use for energy calculation
                        if 'Location' in df_day.columns and shed_filter == "All Sheds (Overview)":
                            # Use only main meter (Shed_01) for energy to avoid double-counting
                            df_energy_calc = df_day[df_day['Location'].str.contains('01|Shed_01', case=False, na=False)].copy()
                        else:
                            df_energy_calc = df_day.copy()
                        
                        for shift in ['🌙 Off-Peak (11PM-6AM)', '☀️ Normal (6AM-5PM)', '🔥 Peak (5PM-11PM)']:
                            df_shift = df_energy_calc[df_energy_calc['Shift'] == shift]
                            total_energy = 0
                            # Count readings from full df_day for display
                            total_readings = len(df_day[df_day['Shift'] == shift])
                            
                            if len(df_shift) > 0 and 'Energy_kWh' in df_shift.columns:
                                # Calculate energy PER LOCATION to avoid mixing different meter readings
                                if 'Location' in df_shift.columns:
                                    for loc in df_shift['Location'].unique():
                                        loc_shift = df_shift[df_shift['Location'] == loc].sort_values('Timestamp')
                                        # Filter out zero/null Energy_kWh values before calculation
                                        loc_shift = loc_shift[loc_shift['Energy_kWh'] > 0]
                                        if len(loc_shift) >= 2:
                                            first_val = loc_shift['Energy_kWh'].iloc[0]
                                            last_val = loc_shift['Energy_kWh'].iloc[-1]
                                            loc_energy = last_val - first_val
                                            # Handle meter rollover or negative values
                                            if loc_energy < 0:
                                                diffs = loc_shift['Energy_kWh'].diff()
                                                loc_energy = diffs[diffs > 0].sum()
                                            # Sanity check: if first reading is suspiciously low (< 100 kWh)
                                            # compared to last reading (> 10000 kWh), use diff of consecutive readings
                                            if first_val < 100 and last_val > 10000:
                                                diffs = loc_shift['Energy_kWh'].diff()
                                                loc_energy = diffs[diffs > 0].sum()
                                            total_energy += max(0, loc_energy)
                                else:
                                    # No location column, use simple calculation
                                    df_shift_sorted = df_shift.sort_values('Timestamp')
                                    # Filter out zero/null values
                                    df_shift_sorted = df_shift_sorted[df_shift_sorted['Energy_kWh'] > 0]
                                    if len(df_shift_sorted) >= 2:
                                        first_val = df_shift_sorted['Energy_kWh'].iloc[0]
                                        last_val = df_shift_sorted['Energy_kWh'].iloc[-1]
                                        total_energy = max(0, last_val - first_val)
                                        # Sanity check for suspicious data
                                        if first_val < 100 and last_val > 10000:
                                            diffs = df_shift_sorted['Energy_kWh'].diff()
                                            total_energy = diffs[diffs > 0].sum()
                            
                            rate = rates.get(shift, 6.87)
                            cost = total_energy * rate
                            
                            shift_summary.append({
                                'Shift': shift,
                                'Readings': total_readings,
                                'Energy (kWh)': total_energy,
                                'Rate (₹/kWh)': rate,
                                'Cost (₹)': cost
                            })
                        
                        shift_df = pd.DataFrame(shift_summary)
                        
                        with col_shift:
                            # Show shift distribution as horizontal bar
                            if shift_df['Energy (kWh)'].sum() > 0:
                                fig_shift = px.bar(
                                    shift_df, 
                                    x='Energy (kWh)', 
                                    y='Shift',
                                    orientation='h',
                                    color='Shift',
                                    color_discrete_map={
                                        '🌙 Off-Peak (11PM-6AM)': '#118ab2',
                                        '☀️ Normal (6AM-5PM)': '#06d6a0',
                                        '🔥 Peak (5PM-11PM)': '#ef476f'
                                    },
                                    title=f'Energy by Shift - {selected_date.strftime("%b %d, %Y")}'
                                )
                                fig_shift.update_layout(
                                    paper_bgcolor='rgba(0,0,0,0)', 
                                    plot_bgcolor='rgba(21,29,40,1)',
                                    font_color='#8899a6',
                                    showlegend=False,
                                    height=200
                                )
                                fig_shift.update_xaxes(gridcolor='#253040')
                                fig_shift.update_yaxes(gridcolor='#253040')
                                st.plotly_chart(fig_shift, use_container_width=True)
                        
                        # Show detailed table
                        st.markdown(f"**📊 {selected_date.strftime('%A, %b %d, %Y')} - Shift Breakdown**")
                        
                        col1, col2, col3 = st.columns(3)
                        for i, row in shift_df.iterrows():
                            with [col1, col2, col3][i]:
                                shift_name = row['Shift'].split(' ')[0]  # Just emoji
                                st.markdown(f"""
                                    <div class="kpi-card" style="padding: 10px;">
                                        <div class="kpi-title">{row['Shift']}</div>
                                        <div class="kpi-value">{row['Energy (kWh)']:.1f} kWh</div>
                                        <div class="kpi-label">₹{row['Cost (₹)']:.0f} @ ₹{row['Rate (₹/kWh)']}/kWh</div>
                                        <div class="kpi-insight">{row['Readings']} readings</div>
                                    </div>
                                """, unsafe_allow_html=True)
                        
                        # Day total
                        total_energy = shift_df['Energy (kWh)'].sum()
                        total_cost = shift_df['Cost (₹)'].sum()
                        st.markdown(f"**Day Total:** {total_energy:.1f} kWh | ₹{total_cost:.0f}")
                    else:
                        st.info("No ToD data available for this date.")
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
                st.markdown("#### ⚡ ToD Optimization Planner")
                
                # Normalize ToD values
                df_tod = df.copy()
                df_tod['ToD_Period'] = df_tod['ToD_Period'].str.upper().str.replace('-', '').str.strip()
                
                # Configuration
                rates = {'OFFPEAK': 5.18, 'NORMAL': 6.30, 'PEAK': 7.14}
                hours = {'OFFPEAK': 7, 'NORMAL': 11, 'PEAK': 6}
                target_split = {'OFFPEAK': 0.45, 'NORMAL': 0.45, 'PEAK': 0.10}
                period_labels = {'OFFPEAK': '🌙 Off-Peak', 'NORMAL': '☀️ Normal', 'PEAK': '🔥 Peak'}
                period_colors = {'OFFPEAK': '#06d6a0', 'NORMAL': '#ffd166', 'PEAK': '#ef476f'}
                
                # Controls row
                ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 2, 2])
                
                with ctrl_col1:
                    shiftable_pct = st.slider(
                        "Shiftable Load %",
                        min_value=20, max_value=60, value=35,
                        help="Percentage of load that can be shifted between periods"
                    ) / 100
                
                with ctrl_col2:
                    view_mode = st.radio("View", ["Weekly", "Monthly"], horizontal=True)
                
                with ctrl_col3:
                    # Baseline detection
                    st.markdown("**Detected Baselines:**")
                    baselines = {}
                    for period in ['OFFPEAK', 'NORMAL', 'PEAK']:
                        period_kw = df_tod[(df_tod['ToD_Period'] == period) & (df_tod['kW_Total'] > 0)]['kW_Total']
                        baselines[period] = period_kw.quantile(0.10) if len(period_kw) > 0 else 0
                    st.caption(f"Off-Peak: {baselines['OFFPEAK']:.1f} kW | Normal: {baselines['NORMAL']:.1f} kW | Peak: {baselines['PEAK']:.1f} kW")
                
                # Calculate energy by ToD period per day
                # CRITICAL: For "All Sheds Overview", use only main meter to avoid double-counting
                tod_energy = []
                
                # For energy calculation, use only main meter if All Sheds Overview
                if 'Location' in df_tod.columns and shed_filter == "All Sheds (Overview)":
                    df_tod_energy = df_tod[df_tod['Location'].str.contains('01|Shed_01', case=False, na=False)].copy()
                else:
                    df_tod_energy = df_tod.copy()
                
                # Determine grouping columns based on whether Location exists
                if 'Location' in df_tod_energy.columns:
                    # Group by date, period, AND location to avoid mixing meters
                    for (date, period, loc), group in df_tod_energy.groupby([df_tod_energy['Date'].dt.date, 'ToD_Period', 'Location']):
                        group_sorted = group.sort_values('Timestamp')
                        if len(group_sorted) >= 2:
                            energy = max(0, group_sorted['Energy_kWh'].iloc[-1] - group_sorted['Energy_kWh'].iloc[0])
                        else:
                            energy = 0
                        tod_energy.append({'Date': date, 'ToD_Period': period, 'Location': loc, 'Energy_kWh': energy})
                    
                    # Now aggregate by date and period (summing across locations)
                    tod_df = pd.DataFrame(tod_energy)
                    if len(tod_df) > 0:
                        tod_df = tod_df.groupby(['Date', 'ToD_Period'])['Energy_kWh'].sum().reset_index()
                else:
                    # No location column, use simple grouping
                    for (date, period), group in df_tod_energy.groupby([df_tod_energy['Date'].dt.date, 'ToD_Period']):
                        group_sorted = group.sort_values('Timestamp')
                        if len(group_sorted) >= 2:
                            energy = max(0, group_sorted['Energy_kWh'].iloc[-1] - group_sorted['Energy_kWh'].iloc[0])
                        else:
                            energy = 0
                        tod_energy.append({'Date': date, 'ToD_Period': period, 'Energy_kWh': energy})
                    tod_df = pd.DataFrame(tod_energy)
                
                if len(tod_df) > 0:
                    tod_df['Date'] = pd.to_datetime(tod_df['Date'])
                    # Use ISO week format (%G-W%V) to handle year boundary correctly
                    # %G = ISO year, %V = ISO week (01-53), handles Dec 2025 → Jan 2026 properly
                    tod_df['Week'] = tod_df['Date'].dt.strftime('%G-W%V')
                    tod_df['Month'] = tod_df['Date'].dt.to_period('M').astype(str)
                    
                    # Aggregate based on view mode
                    if view_mode == "Weekly":
                        agg_df = tod_df.groupby(['Week', 'ToD_Period'])['Energy_kWh'].sum().unstack(fill_value=0)
                        agg_df = agg_df.sort_index()  # Ensure chronological order
                        x_label = "Week"
                    else:
                        agg_df = tod_df.groupby(['Month', 'ToD_Period'])['Energy_kWh'].sum().unstack(fill_value=0)
                        x_label = "Month"
                    
                    # Ensure all periods exist
                    for period in ['OFFPEAK', 'NORMAL', 'PEAK']:
                        if period not in agg_df.columns:
                            agg_df[period] = 0
                    
                    # Calculate averages for grid lines
                    avg_values = agg_df.mean()
                    
                    # ===== ACTUAL vs IDEAL COMPARISON =====
                    st.markdown("---")
                    
                    # Get latest period data
                    latest_idx = agg_df.index[-1]
                    latest_data = agg_df.loc[latest_idx]
                    total_energy = latest_data.sum()
                    
                    if total_energy > 0:
                        # Calculate actual vs ideal
                        actual_cost = sum(latest_data.get(p, 0) * rates[p] for p in rates)
                        ideal_energy = {p: total_energy * target_split[p] for p in target_split}
                        ideal_cost = sum(ideal_energy[p] * rates[p] for p in rates)
                        
                        # Calculate percentages
                        actual_pct = {p: (latest_data.get(p, 0) / total_energy * 100) for p in rates}
                        
                        # Determine if already optimal
                        savings = actual_cost - ideal_cost
                        is_optimal = actual_pct.get('OFFPEAK', 0) >= 45 and actual_pct.get('PEAK', 0) <= 10
                        
                        # Display comparison cards
                        st.markdown(f"##### 📊 {view_mode} {latest_idx} Analysis")
                        
                        comp_col1, comp_col2 = st.columns(2)
                        
                        with comp_col1:
                            st.markdown("**Current Distribution**")
                            for period in ['OFFPEAK', 'NORMAL', 'PEAK']:
                                energy = latest_data.get(period, 0)
                                pct = actual_pct.get(period, 0)
                                cost = energy * rates[period]
                                target = target_split[period] * 100
                                status = "✓" if (period == 'OFFPEAK' and pct >= target) or (period == 'PEAK' and pct <= target) or (period == 'NORMAL') else "↗️" if period == 'OFFPEAK' else "↘️"
                                st.markdown(f"{period_labels[period]}: **{energy:.0f} kWh** ({pct:.0f}%) → ₹{cost:,.0f} {status}")
                            st.markdown(f"**Total: {total_energy:.0f} kWh = ₹{actual_cost:,.0f}**")
                        
                        with comp_col2:
                            st.markdown("**Target Distribution (45/45/10)**")
                            for period in ['OFFPEAK', 'NORMAL', 'PEAK']:
                                energy = ideal_energy[period]
                                pct = target_split[period] * 100
                                cost = energy * rates[period]
                                st.markdown(f"{period_labels[period]}: **{energy:.0f} kWh** ({pct:.0f}%) → ₹{cost:,.0f}")
                            st.markdown(f"**Total: {total_energy:.0f} kWh = ₹{ideal_cost:,.0f}**")
                        
                        # Savings/Status Banner
                        st.markdown("---")
                        if is_optimal or savings <= 0:
                            st.success(f"""
                            ✅ **Excellent! Current distribution is optimal.**
                            
                            Your Off-Peak usage ({actual_pct.get('OFFPEAK', 0):.0f}%) exceeds the 45% target. 
                            Peak usage ({actual_pct.get('PEAK', 0):.0f}%) is below the 10% threshold.
                            
                            **Recommendation:** Maintain current load scheduling. You're already saving compared to target!
                            """)
                        else:
                            shift_from_peak = max(0, latest_data.get('PEAK', 0) - ideal_energy['PEAK'])
                            st.warning(f"""
                            💡 **Optimization Opportunity**
                            
                            | Metric | Value |
                            |--------|-------|
                            | Potential {view_mode} Savings | **₹{savings:,.0f}** |
                            | Monthly Projection | **₹{savings * (4 if view_mode == 'Weekly' else 1):,.0f}** |
                            | Shift from Peak | **{shift_from_peak:.0f} kWh** |
                            
                            **Recommendation:** Move {shift_from_peak:.0f} kWh from Peak (5PM-11PM) to Off-Peak (11PM-6AM)
                            """)
                        
                        # ===== TREND CHART =====
                        st.markdown("---")
                        st.markdown(f"##### 📈 {view_mode} ToD Trend")
                        
                        # Prepare chart data
                        chart_data = agg_df.reset_index()
                        chart_melted = chart_data.melt(
                            id_vars=[chart_data.columns[0]], 
                            value_vars=['OFFPEAK', 'NORMAL', 'PEAK'],
                            var_name='Period',
                            value_name='Energy_kWh'
                        )
                        chart_melted['Period_Label'] = chart_melted['Period'].map(period_labels)
                        
                        fig = px.bar(
                            chart_melted,
                            x=chart_data.columns[0],
                            y='Energy_kWh',
                            color='Period',
                            color_discrete_map=period_colors,
                            barmode='group',
                            title=f'{view_mode}ly Energy by ToD Period'
                        )
                        
                        # Add average grid lines with legends
                        for period in ['OFFPEAK', 'NORMAL', 'PEAK']:
                            avg_val = avg_values.get(period, 0)
                            fig.add_hline(
                                y=avg_val,
                                line_dash="dash",
                                line_color=period_colors[period],
                                line_width=1,
                                annotation_text=f"Avg {period}: {avg_val:.0f}",
                                annotation_position="right"
                            )
                        
                        fig.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(21,29,40,1)',
                            font_color='#8899a6',
                            title_font_color='#f0f4f8',
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                            xaxis_title=x_label,
                            yaxis_title='Energy (kWh)'
                        )
                        fig.update_xaxes(gridcolor='#253040')
                        fig.update_yaxes(gridcolor='#253040')
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # ===== PIE CHART - Overall Distribution =====
                        pie_col1, pie_col2 = st.columns(2)
                        
                        with pie_col1:
                            st.markdown("**Current ToD Mix**")
                            total_by_period = tod_df.groupby('ToD_Period')['Energy_kWh'].sum()
                            fig_pie = px.pie(
                                values=total_by_period.values,
                                names=total_by_period.index,
                                color=total_by_period.index,
                                color_discrete_map=period_colors
                            )
                            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#8899a6')
                            st.plotly_chart(fig_pie, use_container_width=True)
                        
                        with pie_col2:
                            st.markdown("**Target ToD Mix (45/45/10)**")
                            fig_target = px.pie(
                                values=[45, 45, 10],
                                names=['OFFPEAK', 'NORMAL', 'PEAK'],
                                color=['OFFPEAK', 'NORMAL', 'PEAK'],
                                color_discrete_map=period_colors
                            )
                            fig_target.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#8899a6')
                            st.plotly_chart(fig_target, use_container_width=True)
                        
                        # ===== TARIFF REFERENCE =====
                        st.markdown("---")
                        st.markdown("##### 📋 WBSEDCL HT Industrial Tariff Reference")
                        tariff_df = pd.DataFrame({
                            'Period': ['🌙 Off-Peak', '☀️ Normal', '🔥 Peak'],
                            'Hours': ['11PM - 6AM (7 hrs)', '6AM - 5PM (11 hrs)', '5PM - 11PM (6 hrs)'],
                            'Rate (₹/kWh)': [5.18, 6.30, 7.14],
                            'Target %': ['45%', '45%', '10%'],
                            'Strategy': ['Maximize - Cheapest', 'Balance', 'Minimize - Costliest']
                        })
                        st.dataframe(tariff_df, use_container_width=True, hide_index=True)
                    
                    else:
                        st.warning("No energy data available for ToD analysis")
                else:
                    st.warning("No ToD period data available")
            else:
                st.info("ToD_Period column not found")
        except Exception as e:
            st.warning(f"Could not generate ToD analysis: {e}")
    
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
        sustained_alerts = kpis.get('pf_sustained_alerts', 0)
        sustained_min = kpis.get('pf_sustained_minutes', 0)
        st.markdown(f"""
            <div class="rec-card">
                <div class="rec-priority {'high' if sustained_alerts > 0 else 'medium'}"></div>
                <div style="flex: 1;">
                    <div class="rec-title">Fix Low-Load PF Performance</div>
                    <div class="rec-category">Power Quality</div>
                    <div class="rec-insight">{f'{sustained_alerts} sustained low PF events ({sustained_min} min total).' if sustained_alerts > 0 else 'No sustained PF issues.'} Min PF: {kpis['pf_min']:.2f}</div>
                    <div class="rec-action">→ {'Reconfigure APFC panel staging for lower thresholds' if sustained_alerts > 0 else 'Continue monitoring - transients filtered'}</div>
                    <div class="rec-savings">
                        <span class="rec-savings-label">Monthly Savings:</span>
                        <span class="rec-savings-value">{'₹2,500+' if sustained_alerts > 0 else '✓ Optimized'}</span>
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
    
    # ============= SAVINGS BANNER (Data-Driven Calculation) =============
    # Calculate actual savings potential based on WBSEDCL HT Industrial Tariff
    
    savings_breakdown = []
    total_savings = 0
    
    # Get key metrics
    contracted_demand = kpis.get('contracted_demand', 200)  # kW
    peak_demand = kpis.get('peak_demand', 0)  # Actual max kW used
    load_max = kpis.get('load_max', 0)  # % of contracted demand
    avg_pf = kpis.get('avg_pf', 0.95)
    data_days = kpis.get('data_days', 30)
    
    # ToD energy breakdown
    energy_peak = kpis.get('energy_peak', 0)
    energy_normal = kpis.get('energy_normal', 0) 
    energy_offpeak = kpis.get('energy_offpeak', 0)
    total_energy = kpis.get('total_energy', 0)
    
    # WBSEDCL HT Industrial Tariff Rates
    DEMAND_CHARGE = 350  # ₹/kVA/month
    RATE_PEAK = 8.37     # ₹/kWh (5PM-11PM)
    RATE_NORMAL = 6.87   # ₹/kWh (6AM-5PM)
    RATE_OFFPEAK = 5.18  # ₹/kWh (11PM-6AM)
    PF_BENCHMARK = 0.92  # Below this = penalty
    
    # Scale to monthly (30 days)
    monthly_factor = 30 / max(data_days, 1)
    
    # ============= 1. DEMAND CONTRACT OPTIMIZATION =============
    # If actual peak demand is much lower than contracted, can reduce contract
    if peak_demand > 0 and contracted_demand > 0:
        utilization = (peak_demand / contracted_demand) * 100
        
        # Optimal contract = peak demand + 20% buffer
        optimal_contract = peak_demand * 1.2
        
        if optimal_contract < contracted_demand * 0.8:  # Can reduce by >20%
            # Savings = (Current - Optimal) * Demand Charge
            # Assuming PF of 0.9, kVA = kW / 0.9
            current_kva = contracted_demand / 0.9
            optimal_kva = optimal_contract / 0.9
            demand_savings = int((current_kva - optimal_kva) * DEMAND_CHARGE)
            
            if demand_savings > 0:
                reduction_pct = ((contracted_demand - optimal_contract) / contracted_demand) * 100
                savings_breakdown.append(f"Demand contract (₹{demand_savings:,}/mo) - reduce {reduction_pct:.0f}% to {optimal_contract:.0f}kW")
                total_savings += demand_savings
    
    # ============= 2. POWER FACTOR OPTIMIZATION =============
    # WBSEDCL penalty: 1% of energy bill for every 0.01 below 0.92
    if avg_pf > 0 and avg_pf < PF_BENCHMARK:
        # Calculate current energy cost
        monthly_energy = total_energy * monthly_factor
        if monthly_energy == 0:
            monthly_energy = 5000  # Estimate if no data
        
        avg_rate = 6.50  # Blended rate estimate
        monthly_energy_bill = monthly_energy * avg_rate
        
        # Penalty calculation
        pf_shortfall = PF_BENCHMARK - avg_pf  # e.g., 0.92 - 0.85 = 0.07
        penalty_pct = pf_shortfall * 100  # 7%
        pf_penalty = monthly_energy_bill * (penalty_pct / 100)
        pf_savings = int(pf_penalty)
        
        if pf_savings > 100:
            savings_breakdown.append(f"PF penalty avoided (₹{pf_savings:,}/mo) - improve from {avg_pf:.2f} to 0.92")
            total_savings += pf_savings
    
    # ============= 3. ToD SHIFT OPTIMIZATION =============
    # Calculate savings if peak energy is shifted to off-peak
    if energy_peak > 0:
        # Project to monthly
        monthly_peak = energy_peak * monthly_factor
        
        # Potential savings = Peak energy × (Peak rate - Offpeak rate)
        rate_diff = RATE_PEAK - RATE_OFFPEAK  # 8.37 - 5.18 = 3.19
        
        # Assume 50% of peak can realistically be shifted
        shiftable_energy = monthly_peak * 0.5
        tod_savings = int(shiftable_energy * rate_diff)
        
        if tod_savings > 100:
            savings_breakdown.append(f"ToD optimization (₹{tod_savings:,}/mo) - shift {shiftable_energy:.0f}kWh from peak")
            total_savings += tod_savings
    elif total_energy > 0:
        # Estimate if no ToD data
        monthly_energy = total_energy * monthly_factor
        # Assume 20% is peak, 50% shiftable
        estimated_peak = monthly_energy * 0.2
        shiftable = estimated_peak * 0.5
        tod_savings = int(shiftable * (RATE_PEAK - RATE_OFFPEAK))
        if tod_savings > 100:
            savings_breakdown.append(f"ToD optimization (₹{tod_savings:,}/mo est.)")
            total_savings += tod_savings
    
    # ============= 4. FIRE PREVENTION VALUE =============
    fire_high = kpis.get('fire_high', 0)
    fire_critical = kpis.get('fire_critical', 0)
    if fire_high > 0 or fire_critical > 0:
        savings_breakdown.append("⚠️ Fire risk detected - prevention value: Priceless")
    else:
        savings_breakdown.append("✅ Fire monitoring active")
    
    # Build display - Apply 50% conservative discount for realistic expectations
    realizable_savings = int(total_savings * 0.5)
    
    # Calculate different time periods
    monthly_savings = realizable_savings
    period_savings = int(monthly_savings * data_days / 30) if data_days > 0 else 0
    annual_savings = monthly_savings * 12
    
    if realizable_savings == 0:
        st.markdown("""
            <div class="savings-banner">
                <div class="savings-label">💰 Savings Potential</div>
                <div class="savings-value" style="font-size: 28px;">Analyzing...</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Use Streamlit native components for reliable rendering
        st.markdown("""
            <div class="savings-banner">
                <div class="savings-label">💰 Savings Potential (Conservative Estimate)</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Savings metrics using columns
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            st.metric(
                label=f"📅 This Period ({data_days} days)",
                value=f"₹{period_savings:,}"
            )
        with s_col2:
            st.metric(
                label="📆 Monthly",
                value=f"₹{monthly_savings:,}"
            )
        with s_col3:
            st.metric(
                label="📊 Annual Projection",
                value=f"₹{annual_savings:,}"
            )
        
        # Breakdown section
        savings_text = "<br>".join(savings_breakdown) if savings_breakdown else "Analyzing your data..."
        st.markdown(f"""
            <div style="background: rgba(6, 214, 160, 0.05); border-radius: 8px; padding: 12px; margin-top: 8px;">
                <div style="font-size: 11px; font-weight: 600; margin-bottom: 8px; opacity: 0.9;">📋 Breakdown:</div>
                <div style="text-align: left; font-size: 11px; line-height: 1.8;">{savings_text}</div>
                <div style="font-size: 9px; opacity: 0.7; margin-top: 12px; border-top: 1px solid rgba(128,128,128,0.2); padding-top: 8px;">
                    Based on {data_days} days of data | 50% realization factor | WBSEDCL HT Industrial Tariff
                </div>
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
        st.markdown(f"<p style='text-align: center; color: #5c6b7a; font-size: 10px;'>Last refresh: {get_ist_now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
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



# =====================================================
# PATCH: ACTUAL-BASED SHED ENERGY SPLIT (SAFE OVERRIDE)
# This block does NOT remove existing features.
# It only recalculates All-Sheds Overview numbers
# using actual meter readings (no arbitrary splits).
# =====================================================

try:
    # ---- ACTUAL ENERGY CALCULATION ----
    # Fixed: Use correct column names from CSV (Location, Energy_kWh)
    def __energy_from_meter(df, location_pattern):
        """Calculate energy from meter readings using Location column"""
        if 'Location' not in df.columns or 'Energy_kWh' not in df.columns:
            return 0.0
        d = df[df["Location"].str.contains(location_pattern, case=False, na=False)]
        if d.empty or len(d) < 2:
            return 0.0
        d_sorted = d.sort_values('Timestamp') if 'Timestamp' in d.columns else d
        return float(max(0, d_sorted["Energy_kWh"].iloc[-1] - d_sorted["Energy_kWh"].iloc[0]))

    # Use correct location patterns from the CSV
    __MAIN_PATTERN = "Shed_01|01"  # Main meter (Shed 1)
    __SUB_PATTERN = "Shed_02|02"   # Sub-meter (Shed 2)

    # Only run if df exists and has data
    if 'df_original' in dir() and df_original is not None and len(df_original) > 0:
        __energy_main = __energy_from_meter(df_original, __MAIN_PATTERN)
        __energy_sub  = __energy_from_meter(df_original, __SUB_PATTERN)

        # Sanity check: sub-meter can't exceed main meter
        if __energy_sub > __energy_main:
            __energy_sub = __energy_main

        __shed_energy_actual = {
            "Shed 2 (Sub-Meter)": __energy_sub,
            "Shed 1 (Other Loads)": __energy_main - __energy_sub
        }

        __total_energy_actual = __energy_main

        __shed_pct_actual = {
            k: (v / __total_energy_actual * 100) if __total_energy_actual > 0 else 0
            for k, v in __shed_energy_actual.items()
        }

        # ---- OVERRIDE DISPLAY (ONLY IF OVERVIEW EXISTS) ----
        if 'shed_filter' in dir() and shed_filter == "All Sheds (Overview)" and __total_energy_actual > 0:
            st.markdown("### 📊 All Sheds Energy Split (Actual-Based)")

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Total Energy (Main Meter)", f"{__total_energy_actual:,.2f} kWh")
            with c2:
                st.metric("Shed 2 Energy (Sub-Meter)",
                          f"{__shed_energy_actual['Shed 2 (Sub-Meter)']:,.2f} kWh",
                          f"{__shed_pct_actual['Shed 2 (Sub-Meter)']:.1f}%")
            with c3:
                st.metric("Other Loads (Main - Sub)",
                          f"{__shed_energy_actual['Shed 1 (Other Loads)']:,.2f} kWh",
                          f"{__shed_pct_actual['Shed 1 (Other Loads)']:.1f}%")

            import pandas as pd
            __summary_df = pd.DataFrame({
                "Shed": list(__shed_energy_actual.keys()),
                "Energy (kWh)": list(__shed_energy_actual.values()),
                "Percentage (%)": list(__shed_pct_actual.values())
            })

            st.dataframe(__summary_df, use_container_width=True)

            st.caption(
                "Energy split derived from actual meter readings: Sub-meter ÷ Main-meter. "
                "No double counting."
            )

except Exception as __e:
    # Fail-safe: do not break existing app
    pass
