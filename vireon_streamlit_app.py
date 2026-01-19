"""
Vireon Cortex - Live Energy Analytics Dashboard
Streamlit Cloud Deployment (Public Sheet Version)

Author: Vireon Energy Systems
Version: 1.0
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from io import StringIO

# ============= PAGE CONFIG =============
st.set_page_config(
    page_title="Vireon Cortex | Energy Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============= CUSTOM CSS =============
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
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
    
    .subtitle {
        color: #8899a6;
        font-size: 14px;
        margin-top: -10px;
    }
    
    .shed-card {
        background: #151d28;
        border: 1px solid #253040;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
    }
    
    .shed-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 16px;
        font-weight: 600;
        color: #06d6a0;
        margin-bottom: 16px;
    }
    
    .alert-card {
        background: rgba(239, 71, 111, 0.1);
        border: 1px solid #ef476f;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .alert-card.warning {
        background: rgba(255, 209, 102, 0.1);
        border-color: #ffd166;
    }
    
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
    
    .savings-banner {
        background: linear-gradient(135deg, rgba(6, 214, 160, 0.15) 0%, rgba(17, 138, 178, 0.15) 100%);
        border: 1px solid #06d6a0;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        margin-top: 32px;
    }
    
    .savings-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 36px;
        font-weight: 700;
        color: #06d6a0;
    }
    
    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
    }
    
    .section-header {
        font-size: 18px;
        font-weight: 600;
        color: #f0f4f8;
        border-bottom: 1px solid #253040;
        padding-bottom: 12px;
        margin: 32px 0 20px 0;
    }
</style>
""", unsafe_allow_html=True)


# ============= DATA LOADING =============
@st.cache_data(ttl=60)
def load_data_from_public_sheet(sheet_id, sheet_name="readings"):
    """Load data from public Google Sheet (published to web as CSV)"""
    try:
        # Construct the CSV export URL
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        
        response = requests.get(url)
        response.raise_for_status()
        
        df = pd.read_csv(StringIO(response.text))
        
        # Convert timestamp
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Ensure numeric columns
        numeric_cols = ['kW_Total', 'kVA_Total', 'PF_Avg', 'VLN_Avg', 'Current_Total',
                       'Neutral_Current_A', 'Frequency_Hz', 'Energy_kWh', 'Daily_Cost_Rs',
                       'Voltage_Unbalance_Pct', 'Current_Unbalance_Pct', 'Load_Pct',
                       'V_R', 'V_Y', 'V_B', 'Current_R', 'Current_Y', 'Current_B',
                       'PF_R', 'PF_Y', 'PF_B', 'Watts_Total', 'VA_Total']
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
        return "NORMAL", "#ffd166"
    elif 17 <= hour < 23:
        return "PEAK", "#ef476f"
    else:
        return "OFFPEAK", "#06d6a0"


def get_fire_risk_color(level):
    """Get color for fire risk level"""
    colors = {
        'NORMAL': '#06d6a0',
        'WARNING': '#ffd166',
        'HIGH': '#f77f00',
        'CRITICAL': '#ef476f'
    }
    return colors.get(str(level).upper(), '#8899a6')


# ============= MAIN DASHBOARD =============
def main():
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<h1 class="main-header">⚡ VIREON CORTEX</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Industrial Energy Analytics Platform | Omega Transmission POC</p>', unsafe_allow_html=True)
    
    with col2:
        tod_period, tod_color = get_tod_period()
        st.markdown(f"""
            <div style="text-align: right;">
                <span class="tod-badge tod-{tod_period.lower()}">{tod_period}</span>
                <p style="font-size: 12px; color: #8899a6; margin-top: 8px;">
                    {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sheet ID from secrets or sidebar
    sheet_id = st.secrets.get("sheet_id", None)
    
    if not sheet_id:
        with st.sidebar:
            st.markdown("### Configuration")
            sheet_id = st.text_input("Google Sheet ID", help="Enter your Google Sheet ID")
            st.markdown("""
                **How to find Sheet ID:**
                From URL: `https://docs.google.com/spreadsheets/d/`**`SHEET_ID`**`/edit`
                
                **Important:** Make sure the sheet is published to web:
                1. File > Share > Publish to web
                2. Select 'readings' sheet
                3. Choose CSV format
                4. Click Publish
            """)
    
    if not sheet_id:
        st.warning("Please enter your Google Sheet ID in the sidebar.")
        return
    
    # Load data
    with st.spinner("Loading live data..."):
        df = load_data_from_public_sheet(sheet_id)
    
    if df is None or df.empty:
        st.error("No data available. Please check your Google Sheet ID and ensure it's published to web.")
        return
    
    # Get latest readings per shed
    latest = df.sort_values('Timestamp').groupby('Device_ID').last().reset_index()
    
    # ============= SUMMARY METRICS =============
    total_power = latest['kW_Total'].sum()
    total_kva = latest['kVA_Total'].sum()
    avg_pf = latest['PF_Avg'].mean()
    avg_voltage = latest['VLN_Avg'].mean()
    
    # Today's data
    today = datetime.now().date()
    today_df = df[df['Date'].dt.date == today] if 'Date' in df.columns else pd.DataFrame()
    today_cost = today_df.groupby('Device_ID')['Daily_Cost_Rs'].last().sum() if not today_df.empty and 'Daily_Cost_Rs' in today_df.columns else 0
    today_energy = today_df.groupby('Device_ID')['Daily_Energy_Wh'].last().sum() / 1000 if not today_df.empty and 'Daily_Energy_Wh' in today_df.columns else 0
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("⚡ Active Power", f"{total_power:.1f} kW")
    with col2:
        st.metric("🔌 Apparent Power", f"{total_kva:.1f} kVA")
    with col3:
        pf_status = "✅" if avg_pf > 0.95 else "⚠️" if avg_pf > 0.9 else "❌"
        st.metric(f"{pf_status} Power Factor", f"{avg_pf:.3f}")
    with col4:
        st.metric("🔋 Avg Voltage", f"{avg_voltage:.1f} V")
    with col5:
        st.metric("📊 Today's Energy", f"{today_energy:.1f} kWh")
    with col6:
        st.metric("💰 Today's Cost", f"₹{today_cost:.0f}")
    
    # ============= SHED-WISE LIVE STATUS =============
    st.markdown('<h2 class="section-header">🏭 Live Shed Status</h2>', unsafe_allow_html=True)
    
    shed_cols = st.columns(len(latest))
    
    for idx, (_, row) in enumerate(latest.iterrows()):
        with shed_cols[idx]:
            fire_risk = str(row.get('Fire_Risk_Level', 'NORMAL')).upper()
            fire_color = get_fire_risk_color(fire_risk)
            
            st.markdown(f"""
                <div class="shed-card">
                    <div class="shed-title">📍 {row['Location']} ({row['Device_ID'].split('-')[-1].upper()})</div>
                    <table style="width: 100%; color: #f0f4f8; font-size: 13px;">
                        <tr><td style="color: #8899a6;">Power</td><td style="text-align: right; font-family: 'JetBrains Mono', monospace;">{row['kW_Total']:.1f} kW</td></tr>
                        <tr><td style="color: #8899a6;">Current</td><td style="text-align: right; font-family: 'JetBrains Mono', monospace;">{row['Current_Total']:.1f} A</td></tr>
                        <tr><td style="color: #8899a6;">Voltage</td><td style="text-align: right; font-family: 'JetBrains Mono', monospace;">{row['VLN_Avg']:.1f} V</td></tr>
                        <tr><td style="color: #8899a6;">Power Factor</td><td style="text-align: right; font-family: 'JetBrains Mono', monospace;">{row['PF_Avg']:.3f}</td></tr>
                        <tr><td style="color: #8899a6;">Frequency</td><td style="text-align: right; font-family: 'JetBrains Mono', monospace;">{row['Frequency_Hz']:.2f} Hz</td></tr>
                        <tr><td style="color: #8899a6;">Load</td><td style="text-align: right; font-family: 'JetBrains Mono', monospace;">{row['Load_Pct']:.1f}%</td></tr>
                        <tr><td style="color: #8899a6;">Neutral I</td><td style="text-align: right; font-family: 'JetBrains Mono', monospace; color: {fire_color};">{row['Neutral_Current_A']:.2f} A</td></tr>
                        <tr><td style="color: #8899a6;">Fire Risk</td><td style="text-align: right; font-family: 'JetBrains Mono', monospace; color: {fire_color};">🔥 {fire_risk}</td></tr>
                    </table>
                    <p style="font-size: 10px; color: #5c6b7a; margin-top: 12px;">
                        🕐 {row['Timestamp'].strftime('%H:%M:%S') if pd.notna(row['Timestamp']) else 'N/A'}
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    # ============= ALERTS =============
    critical_alerts = latest[latest['Fire_Risk_Level'].astype(str).str.upper().isin(['HIGH', 'CRITICAL'])]
    unbalance_alerts = latest[latest['Current_Unbalance_Pct'] > 10]
    
    if not critical_alerts.empty or not unbalance_alerts.empty:
        st.markdown('<h2 class="section-header">🚨 Active Alerts</h2>', unsafe_allow_html=True)
        
        for _, row in critical_alerts.iterrows():
            st.markdown(f"""
                <div class="alert-card">
                    <strong style="color: #ef476f;">🔥 FIRE RISK: {row['Fire_Risk_Level']}</strong><br>
                    <span style="color: #8899a6;">{row['Location']} | Neutral Current: {row['Neutral_Current_A']:.2f} A</span>
                </div>
            """, unsafe_allow_html=True)
        
        for _, row in unbalance_alerts.iterrows():
            if row['Device_ID'] not in critical_alerts['Device_ID'].values:
                st.markdown(f"""
                    <div class="alert-card warning">
                        <strong style="color: #ffd166;">⚡ HIGH CURRENT UNBALANCE</strong><br>
                        <span style="color: #8899a6;">{row['Location']} | Unbalance: {row['Current_Unbalance_Pct']:.1f}%</span>
                    </div>
                """, unsafe_allow_html=True)
    
    # ============= CHARTS =============
    st.markdown('<h2 class="section-header">📈 Analytics</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["⚡ Power Trend", "🕐 ToD Analysis", "🔥 Fire Risk", "📊 Load Profile"])
    
    with tab1:
        fig = px.line(
            df.sort_values('Timestamp').tail(500),
            x='Timestamp',
            y='kW_Total',
            color='Device_ID',
            title='Power Consumption Trend (Last 500 readings)',
            color_discrete_sequence=['#06d6a0', '#118ab2', '#ffd166']
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(21,29,40,1)',
            font_color='#8899a6',
            title_font_color='#f0f4f8',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig.update_xaxes(gridcolor='#253040')
        fig.update_yaxes(gridcolor='#253040', title='Power (kW)')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            tod_data = df['ToD_Period'].value_counts().reset_index()
            tod_data.columns = ['Period', 'Count']
            
            fig = px.pie(
                tod_data,
                values='Count',
                names='Period',
                title='Readings by ToD Period',
                color='Period',
                color_discrete_map={'OFFPEAK': '#06d6a0', 'NORMAL': '#ffd166', 'PEAK': '#ef476f'}
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#8899a6'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("""
                <div class="shed-card">
                    <h4 style="color: #f0f4f8; margin-bottom: 16px;">⏰ WBSEDCL HT Industrial Rates</h4>
                    <table style="width: 100%; color: #f0f4f8; font-size: 14px;">
                        <tr>
                            <td><span class="tod-badge tod-offpeak">OFF-PEAK</span></td>
                            <td style="color: #8899a6;">23:00 - 06:00</td>
                            <td style="text-align: right; font-family: 'JetBrains Mono', monospace;">₹5.18/kWh</td>
                        </tr>
                        <tr><td colspan="3" style="height: 12px;"></td></tr>
                        <tr>
                            <td><span class="tod-badge tod-normal">NORMAL</span></td>
                            <td style="color: #8899a6;">06:00 - 17:00</td>
                            <td style="text-align: right; font-family: 'JetBrains Mono', monospace;">₹6.95/kWh</td>
                        </tr>
                        <tr><td colspan="3" style="height: 12px;"></td></tr>
                        <tr>
                            <td><span class="tod-badge tod-peak">PEAK</span></td>
                            <td style="color: #8899a6;">17:00 - 23:00</td>
                            <td style="text-align: right; font-family: 'JetBrains Mono', monospace;">₹8.37/kWh</td>
                        </tr>
                    </table>
                    <p style="margin-top: 16px; font-size: 12px; color: #5c6b7a;">
                        💡 Tip: Shift loads to OFF-PEAK for 38% savings vs PEAK rates
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            fire_data = df['Fire_Risk_Level'].astype(str).str.upper().value_counts().reset_index()
            fire_data.columns = ['Level', 'Count']
            
            fig = px.pie(
                fire_data,
                values='Count',
                names='Level',
                title='Fire Risk Distribution (All Readings)',
                color='Level',
                color_discrete_map={
                    'NORMAL': '#06d6a0',
                    'WARNING': '#ffd166',
                    'HIGH': '#f77f00',
                    'CRITICAL': '#ef476f'
                }
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#8899a6'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Neutral current trend
            fig = px.line(
                df.sort_values('Timestamp').tail(200),
                x='Timestamp',
                y='Neutral_Current_A',
                color='Device_ID',
                title='Neutral Current Trend (Fire Safety)',
                color_discrete_sequence=['#ef476f', '#f77f00']
            )
            fig.add_hline(y=10, line_dash="dash", line_color="#ef476f", annotation_text="Critical (10A)")
            fig.add_hline(y=5, line_dash="dash", line_color="#f77f00", annotation_text="High (5A)")
            fig.add_hline(y=2, line_dash="dash", line_color="#ffd166", annotation_text="Warning (2A)")
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(21,29,40,1)',
                font_color='#8899a6'
            )
            fig.update_xaxes(gridcolor='#253040')
            fig.update_yaxes(gridcolor='#253040', title='Neutral Current (A)')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        df['Hour'] = df['Timestamp'].dt.hour
        hourly_load = df.groupby(['Hour', 'Device_ID'])['kW_Total'].mean().reset_index()
        
        fig = px.bar(
            hourly_load,
            x='Hour',
            y='kW_Total',
            color='Device_ID',
            title='Average Hourly Load Profile',
            barmode='group',
            color_discrete_sequence=['#06d6a0', '#118ab2']
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(21,29,40,1)',
            font_color='#8899a6',
            title_font_color='#f0f4f8'
        )
        fig.update_xaxes(gridcolor='#253040', title='Hour of Day')
        fig.update_yaxes(gridcolor='#253040', title='Average Power (kW)')
        st.plotly_chart(fig, use_container_width=True)
    
    # ============= SAVINGS BANNER =============
    st.markdown("""
        <div class="savings-banner">
            <p style="color: #8899a6; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">💰 Monthly Savings Potential</p>
            <p class="savings-value">₹10,000+</p>
            <p style="color: #8899a6; font-size: 13px;">Demand optimization (₹4,000) + PF improvement (₹2,500) + ToD load shifting (₹1,500) + Fire prevention (Priceless)</p>
        </div>
    """, unsafe_allow_html=True)
    
    # ============= DATA TABLE =============
    with st.expander("📋 View Raw Data (Last 50 readings)"):
        display_cols = ['Timestamp', 'Device_ID', 'Location', 'kW_Total', 'PF_Avg', 
                       'VLN_Avg', 'Current_Total', 'Neutral_Current_A', 'Fire_Risk_Level', 'ToD_Period']
        available_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(
            df.sort_values('Timestamp', ascending=False).head(50)[available_cols],
            use_container_width=True
        )
    
    # ============= FOOTER =============
    st.markdown("---")
    st.markdown(f"""
        <p style="text-align: center; color: #5c6b7a; font-size: 12px;">
            ⚡ Vireon Cortex Energy Analytics Platform | Omega Transmission POC<br>
            WBSEDCL HT Industrial Tariff | Live Data from Google Sheets<br>
            <span style="color: #06d6a0;">📊 Total Readings: {len(df)} | 🔄 Auto-refresh: 60 seconds</span>
        </p>
    """, unsafe_allow_html=True)
    
    # Auto-refresh button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()


if __name__ == "__main__":
    main()
