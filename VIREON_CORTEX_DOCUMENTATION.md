# VIREON CORTEX - Dashboard Documentation

> **Version:** 2.0  
> **Last Updated:** 2026-01-21  
> **Files:** `streamlit_app.py` (dark theme), `streamlit_app_light.py` (light theme)  
> **Purpose:** Industrial energy monitoring dashboard for manufacturing facilities

---

## TABLE OF CONTENTS

1. [Architecture Overview](#1-architecture-overview)
2. [Data Sources & Credentials](#2-data-sources--credentials)
3. [Core Modules](#3-core-modules)
4. [Feature Catalog](#4-feature-catalog)
5. [KPI Calculations](#5-kpi-calculations)
6. [Constraints & Assumptions](#6-constraints--assumptions)
7. [Configuration Parameters](#7-configuration-parameters)
8. [Agent Instructions](#8-agent-instructions)

---

## 1. ARCHITECTURE OVERVIEW

### System Flow
```
Industrial Meters (L&T WL4405, Schneider EM6436H)
        ↓ Modbus RTU / RS485
Raspberry Pi (Data Collector)
        ↓ API Push (5-min intervals)
Google Sheets (Cloud Storage)
        ↓ gspread API
Streamlit Dashboard (Analytics & Visualization)
```

### File Structure
```
streamlit_app.py          # Main app (dark theme)
streamlit_app_light.py    # Light theme variant
config.py                 # Credentials configuration
credentials.json          # Google Service Account
token.json               # OAuth tokens
```

### Key Dependencies
```python
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.18.0
gspread>=5.12.0
google-auth>=2.23.0
numpy>=1.24.0
```

---

## 2. DATA SOURCES & CREDENTIALS

### Google Sheets Configuration

| Parameter | Value | Location |
|-----------|-------|----------|
| Default Sheet ID | `1fBXCMWMT8v8Q0qfGklTjKqEkbGYiy45RXTQXK2lnH80` | Sidebar input |
| Worksheet Name | `readings` | Hardcoded |
| API Scope | `https://www.googleapis.com/auth/spreadsheets.readonly` | credentials.json |

### Authentication Methods

**Method 1: Service Account (Production)**
```python
from google.oauth2.service_account import Credentials
creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
```

**Method 2: OAuth (Development)**
```python
from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
```

### Data Schema (Expected Columns)

| Column | Type | Description | Required |
|--------|------|-------------|----------|
| `Timestamp` | datetime | Reading timestamp (IST) | ✓ |
| `Date` | date | Date portion | ✓ |
| `Location` | string | Shed identifier (Shed_01, Shed_02) | ✓ |
| `kW_Total` | float | Total active power (kW) | ✓ |
| `Energy_kWh` | float | Cumulative energy meter reading | ✓ |
| `PF_Avg` | float | Average power factor (-1 to 1) | ✓ |
| `Current_Total` | float | Total current (A) | ✓ |
| `Current_R` | float | R-phase current | |
| `Current_Y` | float | Y-phase current | |
| `Current_B` | float | B-phase current | |
| `Current_N` | float | Neutral current (fire risk) | |
| `Voltage_RY` | float | Line voltage R-Y | |
| `Voltage_YB` | float | Line voltage Y-B | |
| `Voltage_BR` | float | Line voltage B-R | |
| `Frequency` | float | Grid frequency (Hz) | |
| `ToD_Period` | string | PEAK/NORMAL/OFFPEAK | ✓ |
| `Meter_Serial` | string | Meter serial number | |
| `Model_Number` | string | Meter model | |

---

## 3. CORE MODULES

### 3.1 Data Loading Module

**Function:** `load_data_from_sheets(sheet_id)`

**Location:** Lines ~250-350

**Logic:**
```python
1. Authenticate with Google Sheets API
2. Fetch all records from 'readings' worksheet
3. Convert to pandas DataFrame
4. Parse timestamps with format='mixed' (handles both space and T separators)
5. Convert to IST timezone
6. Cache for 30 seconds (st.cache_data with ttl=30)
```

**Error Handling:**
- Invalid Sheet ID → Warning message
- Authentication failure → Retry with OAuth
- Empty sheet → Return None

---

### 3.2 KPI Calculation Module

**Function:** `calculate_kpis(df)`

**Location:** Lines ~459-580

**Returns:** Dictionary with 40+ KPI values

**Categories:**
- Energy metrics
- Power factor metrics
- Fire risk metrics
- Load utilization metrics
- ToD breakdown metrics

---

### 3.3 Visualization Module

**Location:** Lines ~1800-2400 (tabs section)

**Components:**
- Daily Energy Chart (tab1)
- Fire Risk Analysis (tab2)
- Load Profile (tab3)
- ToD Optimization (tab4)

---

### 3.4 Report Generation Module

**Function:** `generate_report_csv(df, kpis, report_type, shed_label)`

**Location:** Lines ~543-700

**Outputs:**
- Executive Summary CSV
- Detailed Analysis CSV
- PDF Report (optional)

---

## 4. FEATURE CATALOG

### 4.1 Daily Energy Analysis

**Location:** Tab 1 (`with tab1:`)

**Sub-features:**

| Feature | Description | Logic |
|---------|-------------|-------|
| Daily Consumption Chart | Bar chart showing kWh per day | `last_reading - first_reading` per day |
| Weekday/Weekend Coloring | Visual distinction | `DayOfWeek >= 5` = Weekend |
| Multi-Shed Handling | Handles multiple meter locations | Group by Date AND Location, then sum |
| **Estimated Gaps Toggle** | Shows missing days with estimates | Weekday avg for missing weekdays, Weekend avg for weekends |

**Estimated Gaps Logic:**
```python
# Detect missing days
all_dates = pd.date_range(start=min_date, end=max_date, freq='D')
missing_dates = [d for d in all_dates if d.date() not in actual_dates]

# Estimate using day-type averages
for d in missing_dates:
    est_energy = weekend_avg if d.dayofweek >= 5 else weekday_avg
```

**Constraints:**
- Estimates shown in GRAY color (#9ca3af)
- Toggle is OFF by default
- Estimates do NOT affect KPIs

---

### 4.2 Fire Risk Analysis

**Location:** Tab 2 (`with tab2:`)

**Logic:**
```python
# Neutral current thresholds
SAFE = Current_N < 5A
WATCH = 5A <= Current_N < 10A
HIGH = 10A <= Current_N < 20A
CRITICAL = Current_N >= 20A
```

**Display:**
- Pie chart of risk distribution
- Critical event counter
- Timeline of high-risk events

---

### 4.3 Load Profile Analysis

**Location:** Tab 3 (`with tab3:`)

**Features:**
- 24-hour load curve
- Peak demand identification
- Load factor calculation
- Capacity utilization metrics

---

### 4.4 ToD Optimization Planner

**Location:** Tab 4 (`with tab4:`)

**Configuration:**
```python
rates = {'OFFPEAK': 5.18, 'NORMAL': 6.30, 'PEAK': 7.14}  # ₹/kWh
hours = {'OFFPEAK': 7, 'NORMAL': 11, 'PEAK': 6}
target_split = {'OFFPEAK': 0.40, 'NORMAL': 0.40, 'PEAK': 0.20}
```

**Sub-features:**

| Feature | Description | Parameters |
|---------|-------------|------------|
| Shiftable Load Slider | User adjusts shiftable % | Range: 20-60%, Default: 35% |
| Weekly/Monthly Toggle | Switch aggregation period | Radio buttons |
| Baseline Detection | Auto-detect minimum load | 10th percentile of non-zero kW |
| Actual vs Ideal Comparison | Side-by-side cost analysis | Based on target split |
| Trend Chart | Grouped bar chart by ToD | With average grid lines |
| Optimization Status | Green (optimal) or Yellow (opportunity) | Based on actual vs target |

**Optimization Logic:**
```python
# Calculate actual distribution
actual_pct = {period: energy / total * 100 for period, energy in latest_data.items()}

# Compare with target
is_optimal = actual_pct['OFFPEAK'] >= 40 and actual_pct['PEAK'] <= 20

# Calculate savings
actual_cost = sum(energy * rates[period] for period, energy in latest_data.items())
ideal_cost = sum(total * target_split[period] * rates[period] for period in rates)
savings = actual_cost - ideal_cost
```

---

### 4.5 PF Penalty Alert System

**Location:** KPI Cards section, `calculate_kpis()` function

**Logic (with noise filtering):**
```python
# Step 1: Filter noisy data (Current > 1A required)
valid_mask = (current_series > 1.0) & (pf_series.notna())
df_pf_valid = df[valid_mask]

# Step 2: Calculate percentages on valid data only
pf_below_92 = (pf_series < 0.92).sum() / len(pf_series) * 100
pf_below_90 = (pf_series < 0.90).sum() / len(pf_series) * 100

# Step 3: Detect sustained events (3+ consecutive readings below 0.90)
df_pf_valid['PF_Low_90'] = df_pf_valid['PF_Abs'] < 0.90
df_pf_valid['PF_Low_Group'] = (df_pf_valid['PF_Low_90'] != df_pf_valid['PF_Low_90'].shift()).cumsum()
sustained_groups = df_pf_valid[df_pf_valid['PF_Low_90']].groupby('PF_Low_Group').size()
sustained_alerts = sustained_groups[sustained_groups >= 3]
```

**KPI Outputs:**
| KPI | Description |
|-----|-------------|
| `pf_valid_readings` | Count of readings with Current > 1A |
| `pf_below_92` | % of valid readings below 0.92 |
| `pf_below_90` | % of valid readings below 0.90 |
| `pf_sustained_alerts` | Count of sustained low PF events |
| `pf_sustained_minutes` | Total minutes in sustained low PF |
| `pf_min` | Minimum PF recorded (valid readings) |

**Alert Levels:**
- 🟢 0 sustained events: Healthy
- 🟡 1-3 sustained events: Monitor APFC
- 🔴 4+ sustained events: APFC needs service

---

### 4.6 Asset Health Metrics

**Location:** Asset Health section (~line 1750)

**Metrics:**

| Card | Metric | Calculation | Threshold |
|------|--------|-------------|-----------|
| ⚡ Power Quality | Supply Stability | Voltage deviation from 415V | < 5% good |
| | Worst Recorded | Max voltage unbalance % | < 2% good |
| | Warning Events | Count of unbalance > 2% | Minimize |
| 🔧 Motor Health | Load Balance | Current imbalance R/Y/B | < 15% good |
| | Worst Recorded | Max current unbalance % | < 20% good |
| | Needs Attention | Readings with unbalance > 15% | Investigate |
| 📊 Capacity Usage | Avg Utilization | Mean kW / Contracted kW × 100 | 60-80% optimal |
| | Peak Usage | Max kW / Contracted kW × 100 | < 90% safe |
| | Idle Time | % readings with load < 10% | Minimize |
| 🔌 Grid Quality | Frequency | Range of Hz readings | 49.5-50.5 Hz normal |
| | Voltage Range | Min-Max L-N voltage | 380-440V acceptable |

---

### 4.7 Data Health Monitor

**Location:** Bottom section (~line 2720)

**Checks:**
- Last reading timestamp
- Time since last update
- Data gaps detection
- Expected interval: 5 minutes
- Status: LIVE (≤10 min) / DELAYED (≤30 min) / OFFLINE (>30 min)

---

## 5. KPI CALCULATIONS

### Energy KPIs

```python
# Total Energy (handles meter resets)
if len(df) >= 2:
    first_reading = df['Energy_kWh'].iloc[0]
    last_reading = df['Energy_kWh'].iloc[-1]
    total_energy = last_reading - first_reading
    if total_energy < 0:  # Meter reset
        diffs = df['Energy_kWh'].diff()
        total_energy = diffs[diffs > 0].sum()

# Daily Energy
daily_energy = df.groupby('Date').apply(lambda g: g['Energy_kWh'].iloc[-1] - g['Energy_kWh'].iloc[0])
```

### Demand KPIs

```python
# Peak Demand
max_demand = df['kW_Total'].max()

# Average Demand
avg_demand = df['kW_Total'].mean()

# Load Factor
load_factor = avg_demand / max_demand * 100 if max_demand > 0 else 0

# Utilization (vs contracted demand)
contracted_demand = 200  # kW (configurable)
load_utilization = max_demand / contracted_demand * 100
```

### Power Factor KPIs

```python
# Only valid readings (Current > 1A)
valid_pf = df[df['Current_Total'] > 1.0]['PF_Avg'].abs()

pf_avg = valid_pf.mean()
pf_min = valid_pf.min()
pf_below_92 = (valid_pf < 0.92).sum() / len(valid_pf) * 100
```

### Fire Risk KPIs

```python
neutral_current = df['Current_N'].abs()

fire_safe = (neutral_current < 5).sum()
fire_watch = ((neutral_current >= 5) & (neutral_current < 10)).sum()
fire_high = ((neutral_current >= 10) & (neutral_current < 20)).sum()
fire_critical = (neutral_current >= 20).sum()
```

### ToD KPIs

```python
# Normalize period names
df['ToD_Normalized'] = df['ToD_Period'].str.upper().str.replace('-', '')

# Energy by period (proportional to reading counts)
for period in ['PEAK', 'NORMAL', 'OFFPEAK']:
    proportion = (df['ToD_Normalized'] == period).sum() / len(df)
    energy_by_period[period] = total_energy * proportion
```

---

## 6. CONSTRAINTS & ASSUMPTIONS

### Data Constraints

| Constraint | Value | Reason |
|------------|-------|--------|
| Minimum readings for KPIs | 2 | Need first/last for energy diff |
| Maximum daily energy | 2,000 kWh (light) / 10,000 kWh (main) | Filter outliers |
| Valid PF reading current | > 1A | Filter startup transients |
| Sustained PF threshold | 3 consecutive readings | ~15 min at 5-min intervals |
| Data refresh interval | 30 seconds | Cache TTL |

### Business Assumptions

| Assumption | Value | Source |
|------------|-------|--------|
| Contracted Demand | 200 kW | Omega Transmission contract |
| Data Collection Interval | 5 minutes | Pi configuration |
| Timezone | IST (Asia/Kolkata) | India operations |
| ToD Off-Peak Hours | 23:00-06:00 | WBSEDCL tariff |
| ToD Normal Hours | 06:00-17:00 | WBSEDCL tariff |
| ToD Peak Hours | 17:00-23:00 | WBSEDCL tariff |

### Tariff Assumptions (WBSEDCL HT Industrial)

| Parameter | Value |
|-----------|-------|
| Off-Peak Rate | ₹5.18/kWh |
| Normal Rate | ₹6.30/kWh |
| Peak Rate | ₹7.14/kWh |
| PF Penalty Threshold | < 0.92 |
| PF Incentive Threshold | > 0.95 |

### Technical Assumptions

| Assumption | Description |
|------------|-------------|
| Meter cumulative | Energy_kWh is cumulative (never resets except maintenance) |
| Timestamp format | Mixed format support (space or T separator) |
| Location naming | Shed_01, Shed_02 format |
| ToD naming | PEAK, NORMAL, OFFPEAK (or OFF-PEAK) |

---

## 7. CONFIGURATION PARAMETERS

### Editable Constants

```python
# Location: Top of file or in config section

# Contracted Demand
CONTRACTED_DEMAND_KW = 200

# Fire Risk Thresholds (Neutral Current)
FIRE_SAFE_THRESHOLD = 5      # A
FIRE_WATCH_THRESHOLD = 10    # A
FIRE_HIGH_THRESHOLD = 20     # A

# PF Thresholds
PF_PENALTY_THRESHOLD = 0.92
PF_CRITICAL_THRESHOLD = 0.85
PF_SUSTAINED_THRESHOLD = 0.90
PF_MIN_CURRENT_FOR_VALID = 1.0  # A

# ToD Rates (₹/kWh)
TOD_RATES = {
    'OFFPEAK': 5.18,
    'NORMAL': 6.30,
    'PEAK': 7.14
}

# Target ToD Split
TARGET_SPLIT = {
    'OFFPEAK': 0.40,
    'NORMAL': 0.40,
    'PEAK': 0.20
}

# Shiftable Load Slider
SHIFTABLE_MIN = 20   # %
SHIFTABLE_MAX = 60   # %
SHIFTABLE_DEFAULT = 35  # %

# Cache TTL
CACHE_TTL_SECONDS = 30

# Daily Energy Filter
MAX_DAILY_ENERGY_KWH = 2000  # light version
# MAX_DAILY_ENERGY_KWH = 10000  # main version
```

### UI Configuration

```python
# Page Config
st.set_page_config(
    page_title="Vireon Cortex",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Auto-refresh
st_autorefresh(interval=30000, key="data_refresh")  # 30 seconds

# Color Schemes
COLORS = {
    'weekday': '#4ecdc4',
    'weekend': '#ff6b6b',
    'estimated': '#9ca3af',
    'offpeak': '#06d6a0',
    'normal': '#ffd166',
    'peak': '#ef476f',
    'safe': '#06d6a0',
    'warning': '#ffd166',
    'critical': '#ef476f'
}
```

---

## 8. AGENT INSTRUCTIONS

### For AI Agents Modifying This Codebase

#### File Locations

| Component | Light Version | Main Version |
|-----------|---------------|--------------|
| KPI Calculation | `calculate_kpis()` ~line 459 | `calculate_kpis()` ~line 459 |
| Daily Energy Tab | `with tab1:` ~line 1923 | `with tab1:` ~line 1868 |
| Fire Risk Tab | `with tab2:` ~line 2100 | `with tab2:` ~line 2050 |
| Load Profile Tab | `with tab3:` ~line 2150 | `with tab3:` ~line 2100 |
| ToD Analysis Tab | `with tab4:` ~line 2221 | `with tab4:` ~line 2197 |
| Asset Health | ~line 1750 | ~line 1700 |
| Recommendations | ~line 2680 | ~line 2590 |
| Sidebar Documentation | ~line 1144 | ~line 1094 |

#### Modification Guidelines

1. **Adding a new KPI:**
   - Add calculation in `calculate_kpis()` function
   - Add display in appropriate KPI card section
   - Update documentation in sidebar "Asset Health" guide

2. **Adding a new chart:**
   - Add within appropriate tab (`with tabN:`)
   - Use Plotly for consistency
   - Apply theme colors from `COLORS` dict
   - Handle empty data gracefully with `st.warning()`

3. **Adding a new feature toggle:**
   - Use `st.checkbox()` with OFF default
   - Add help text explaining the feature
   - Ensure original data is not modified

4. **Modifying thresholds:**
   - Update constant at top of file
   - Update documentation in sidebar
   - Test with sample data

#### Testing Commands

```bash
# Syntax check
python3 -m py_compile streamlit_app_light.py

# Run locally
streamlit run streamlit_app_light.py --server.port 8501

# Check for specific features
grep -n "feature_name" streamlit_app_light.py
```

#### Rollback Procedure

1. Keep backup before changes: `cp streamlit_app_light.py streamlit_app_light.py.bak`
2. Test changes locally before deployment
3. If issues, restore: `cp streamlit_app_light.py.bak streamlit_app_light.py`

#### Common Pitfalls

| Issue | Cause | Solution |
|-------|-------|----------|
| Empty chart | No data in filtered range | Add `if len(df) > 0:` check |
| KeyError in KPIs | Missing column | Add `if 'column' in df.columns:` |
| Wrong energy values | Multi-shed without grouping | Group by Date AND Location |
| Noisy PF alerts | Startup transients | Filter Current > 1A |
| Stale data | Cache not cleared | Use `st.cache_data.clear()` |

---

## CHANGELOG

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-21 | 2.0 | Added: Estimated gaps toggle, ToD optimizer, PF sustained alerts, Asset Health docs |
| 2026-01-20 | 1.9 | Fixed: Multi-shed daily energy calculation, timestamp parsing |
| 2026-01-19 | 1.8 | Added: All Sheds view, daily chart fix |

---

## CONTACT

**Project:** Vireon Cortex  
**Client:** Omega Transmission Pvt. Ltd.  
**Location:** Serampore, West Bengal, India  

---

*This document is auto-generated and should be updated whenever features are added or modified.*
