#!/usr/bin/env python3
"""
Vireon Cortex Energy Logger v3.0
Unified L&T WL4405 3-Phase Energy Meter Monitor

Deployment:
1. Copy vireon_logger.py to each Pi
2. Copy the appropriate config.py for that Pi (config_mu01.py → config.py)
3. Copy credentials.json (OAuth client) and token.json (OAuth token)
4. Run: python3 vireon_logger.py

File structure on each Pi:
~/vireon-cortex/
├── vireon_logger.py      # This script (same on all Pis)
├── config.py             # Device-specific config
├── credentials.json      # OAuth client credentials
├── token.json            # OAuth token (from test_sheets_oauth.py)
└── data/                 # Auto-created
"""

import serial
import time
import struct
import csv
import json
import os
import math
from datetime import datetime, date, timedelta
from collections import defaultdict

# ============= LOAD CONFIG =============
try:
    from config import CONFIG
    print("Loaded config for: {}".format(CONFIG.get('device_id', 'unknown')))
except ImportError:
    print("ERROR: config.py not found!")
    print("Copy the appropriate config file (config_mu01.py, config_mu02.py, etc.) to config.py")
    exit(1)

# ============= GOOGLE SHEETS SETUP (OAuth) =============
try:
    import gspread
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False
    print("Warning: gspread/google-auth not installed. Google Sheets sync disabled.")
    print("Install with: pip install gspread google-auth google-auth-oauthlib --break-system-packages")

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


# ============= SHEET HEADERS (Full 55-column Schema - exact match to v2.1) =============
SHEET_HEADERS = [
    # Time (4)
    'Timestamp', 'Date', 'Time', 'Hour',
    # Device (4)
    'Device_ID', 'Location', 'Meter_Serial', 'Model_Number',
    # ToD (2)
    'ToD_Period', 'Rate_Rs_kWh',
    # Power Watts (5)
    'Watts_Total', 'Watts_R', 'Watts_Y', 'Watts_B', 'kW_Total',
    # Power VA (5)
    'VA_Total', 'VA_R', 'VA_Y', 'VA_B', 'kVA_Total',
    # Power Factor (4)
    'PF_Avg', 'PF_R', 'PF_Y', 'PF_B',
    # Voltages L-L (4)
    'VLL_Avg', 'V_RY', 'V_YB', 'V_BR',
    # Voltages L-N (4)
    'VLN_Avg', 'V_R', 'V_Y', 'V_B',
    # Current (4)
    'Current_Total', 'Current_R', 'Current_Y', 'Current_B',
    # Neutral & Fire Safety (2)
    'Neutral_Current_A', 'Fire_Risk_Level',
    # Frequency (1)
    'Frequency_Hz',
    # Energy (4)
    'Energy_Wh', 'Energy_kWh', 'Energy_VAh', 'Energy_VAh_Derived',
    # Unbalance (2)
    'Voltage_Unbalance_Pct', 'Current_Unbalance_Pct',
    # Load (1)
    'Load_Pct',
    # Run Hours (1)
    'Run_Hours',
    # Max Demand (2)
    'Max_Demand_kVA', 'Max_Demand_kW',
    # Session/Daily (2)
    'Session_Energy_Wh', 'Daily_Energy_Wh',
    # Cost (3)
    'PF_Rebate_Pct', 'Effective_Rate', 'Daily_Cost_Rs',
    # ESG (1)
    'Carbon_kg_CO2',
]
# Total: 4+4+2+5+5+4+4+4+4+2+1+4+2+1+1+2+2+3+1 = 55 columns


# ============= MODBUS FUNCTIONS =============

def calculate_crc(data):
    """Calculate Modbus CRC16"""
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for i in range(8):
            if (crc & 1) != 0:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc


def send_modbus_query(ser, slave_id, function_code, start_addr, num_registers):
    """Send Modbus RTU query and return response"""
    query = bytearray([
        slave_id,
        function_code,
        (start_addr >> 8) & 0xFF,
        start_addr & 0xFF,
        (num_registers >> 8) & 0xFF,
        num_registers & 0xFF
    ])
    
    crc = calculate_crc(query)
    query.append(crc & 0xFF)
    query.append((crc >> 8) & 0xFF)
    
    ser.reset_input_buffer()
    ser.write(query)
    time.sleep(0.2)
    
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting)
        return response
    return None


def parse_lt_float(reg1, reg2):
    """Parse L&T float (Little-Endian format - reg2,reg1)"""
    combined = (reg2 << 16) | reg1
    return struct.unpack('>f', struct.pack('>I', combined))[0]


def parse_int32(reg1, reg2):
    """Parse as 32-bit integer"""
    return (reg1 << 16) | reg2


def read_lt_meter(ser, slave_id):
    """Read L&T WL4405 3-Phase parameters"""
    
    parameters = [
        # System Info
        ("Model_Number", 40001, "", "int32"),
        ("Run_Hours_Sec", 40217, "s", "int32"),
        # Power
        ("Watts_Total", 40101, "W", "float"),
        ("Watts_R", 40103, "W", "float"),
        ("Watts_Y", 40105, "W", "float"),
        ("Watts_B", 40107, "W", "float"),
        # Power Factor
        ("PF_Avg", 40117, "", "float"),
        ("PF_R", 40119, "", "float"),
        ("PF_Y", 40121, "", "float"),
        ("PF_B", 40123, "", "float"),
        # Apparent Power
        ("VA_Total", 40125, "VA", "float"),
        ("VA_R", 40127, "VA", "float"),
        ("VA_Y", 40129, "VA", "float"),
        ("VA_B", 40131, "VA", "float"),
        # Voltages L-L
        ("VLL_Avg", 40133, "V", "float"),
        ("V_RY", 40135, "V", "float"),
        ("V_YB", 40137, "V", "float"),
        ("V_BR", 40139, "V", "float"),
        # Voltages L-N
        ("VLN_Avg", 40141, "V", "float"),
        ("V_R", 40143, "V", "float"),
        ("V_Y", 40145, "V", "float"),
        ("V_B", 40147, "V", "float"),
        # Current
        ("Current_Total", 40149, "A", "float"),
        ("Current_R", 40151, "A", "float"),
        ("Current_Y", 40153, "A", "float"),
        ("Current_B", 40155, "A", "float"),
        # Frequency
        ("Frequency", 40157, "Hz", "float"),
        # Energy
        ("Energy_Wh", 40159, "Wh", "float"),
        ("Energy_VAh", 40161, "VAh", "float"),
    ]
    
    results = {}
    
    for param in parameters:
        param_name, address, unit, parse_type = param
        modbus_addr = address - 40001
        response = send_modbus_query(ser, slave_id, 0x03, modbus_addr, 2)
        
        if response and len(response) >= 9:
            if response[0] == slave_id and response[1] == 0x03:
                reg1 = (response[3] << 8) | response[4]
                reg2 = (response[5] << 8) | response[6]
                
                if parse_type == 'float':
                    value = parse_lt_float(reg1, reg2)
                elif parse_type == 'int32':
                    value = parse_int32(reg1, reg2)
                else:
                    value = parse_lt_float(reg1, reg2)
                
                results[param_name] = {"value": value, "unit": unit}
        time.sleep(0.1)
    
    results = add_calculated_parameters(results)
    return results


def add_calculated_parameters(data):
    """Add calculated and derived parameters"""
    
    def get_val(key):
        return data.get(key, {}).get('value', 0)
    
    # 1. Neutral Current (Fire Safety Scout)
    # Formula: I_N = sqrt(I_R² + I_Y² + I_B² - I_R×I_Y - I_Y×I_B - I_B×I_R)
    i_r = abs(get_val('Current_R'))
    i_y = abs(get_val('Current_Y'))
    i_b = abs(get_val('Current_B'))
    
    try:
        neutral_sq = (i_r**2 + i_y**2 + i_b**2 - i_r*i_y - i_y*i_b - i_b*i_r)
        neutral_current = math.sqrt(max(0, neutral_sq))
    except:
        neutral_current = 0
    
    data['Neutral_Current_Calc'] = {"value": neutral_current, "unit": "A"}
    
    # Fire risk level
    if neutral_current >= CONFIG['neutral_current_critical']:
        fire_risk = "CRITICAL"
    elif neutral_current >= CONFIG['neutral_current_high']:
        fire_risk = "HIGH"
    elif neutral_current >= CONFIG['neutral_current_warning']:
        fire_risk = "WARNING"
    else:
        fire_risk = "NORMAL"
    data['Fire_Risk_Level'] = {"value": fire_risk, "unit": ""}
    
    # 2. Voltage Unbalance %
    v_r = get_val('V_R')
    v_y = get_val('V_Y')
    v_b = get_val('V_B')
    
    v_avg = (v_r + v_y + v_b) / 3 if (v_r + v_y + v_b) > 0 else 1
    v_max_dev = max(abs(v_r - v_avg), abs(v_y - v_avg), abs(v_b - v_avg))
    voltage_unbalance = (v_max_dev / v_avg) * 100
    data['Voltage_Unbalance_Pct'] = {"value": voltage_unbalance, "unit": "%"}
    
    # 3. Current Unbalance %
    i_avg = (i_r + i_y + i_b) / 3 if (i_r + i_y + i_b) > 0 else 1
    i_max_dev = max(abs(i_r - i_avg), abs(i_y - i_avg), abs(i_b - i_avg))
    current_unbalance = (i_max_dev / i_avg) * 100
    data['Current_Unbalance_Pct'] = {"value": current_unbalance, "unit": "%"}
    
    # 4. Derived kVAh (if meter returns 0)
    energy_wh = get_val('Energy_Wh')
    energy_vah = get_val('Energy_VAh')
    pf_avg = abs(get_val('PF_Avg'))
    
    if energy_vah == 0 and pf_avg > 0.1:
        derived_vah = energy_wh / pf_avg
        data['Energy_VAh_Derived'] = {"value": derived_vah, "unit": "VAh"}
    else:
        data['Energy_VAh_Derived'] = {"value": energy_vah, "unit": "VAh"}
    
    # 5. Run Hours
    run_hours_sec = get_val('Run_Hours_Sec')
    run_hours = run_hours_sec / 3600 if run_hours_sec > 0 else 0
    data['Run_Hours'] = {"value": run_hours, "unit": "hrs"}
    
    # 6. Load %
    watts_total = get_val('Watts_Total')
    load_pct = (watts_total / 1000 / CONFIG['contracted_load_kw']) * 100 if CONFIG['contracted_load_kw'] > 0 else 0
    data['Load_Pct'] = {"value": load_pct, "unit": "%"}
    
    # 7. Carbon Footprint (ESG)
    energy_kwh = energy_wh / 1000
    carbon_kg = energy_kwh * CONFIG['carbon_factor_kg_per_kwh']
    data['Carbon_kg'] = {"value": carbon_kg, "unit": "kg CO2"}
    
    # 8. kW and kVA
    data['kW_Total'] = {"value": watts_total / 1000, "unit": "kW"}
    data['kVA_Total'] = {"value": get_val('VA_Total') / 1000, "unit": "kVA"}
    
    return data


# ============= ToD BILLING FUNCTIONS =============

def get_tod_period():
    """Get current Time of Day period"""
    hour = datetime.now().hour
    if CONFIG['tod_normal_start'] <= hour < CONFIG['tod_normal_end']:
        return 'NORMAL'
    elif CONFIG['tod_peak_start'] <= hour < CONFIG['tod_peak_end']:
        return 'PEAK'
    else:
        return 'OFFPEAK'


def get_tod_rate(period):
    """Get rate for given ToD period"""
    rates = {
        'NORMAL': CONFIG['rate_normal'],
        'PEAK': CONFIG['rate_peak'],
        'OFFPEAK': CONFIG['rate_offpeak']
    }
    return rates.get(period, CONFIG['rate_normal'])


def get_pf_rebate_percent(pf, period):
    """WBSEDCL PF Rebate Structure for HT Industrial"""
    pf = abs(pf)
    
    rebate_table = [
        (0.99, 1.00, {'NORMAL': 8, 'PEAK': 9, 'OFFPEAK': 7}),
        (0.98, 0.99, {'NORMAL': 7, 'PEAK': 8, 'OFFPEAK': 6}),
        (0.97, 0.98, {'NORMAL': 6, 'PEAK': 7, 'OFFPEAK': 5}),
        (0.96, 0.97, {'NORMAL': 5, 'PEAK': 6, 'OFFPEAK': 4}),
        (0.95, 0.96, {'NORMAL': 4, 'PEAK': 5, 'OFFPEAK': 3}),
        (0.94, 0.95, {'NORMAL': 3, 'PEAK': 4, 'OFFPEAK': 2}),
        (0.93, 0.94, {'NORMAL': 2, 'PEAK': 3, 'OFFPEAK': 1}),
        (0.92, 0.93, {'NORMAL': 1, 'PEAK': 2, 'OFFPEAK': 0}),
    ]
    
    for low, high, rebates in rebate_table:
        if low <= pf < high:
            return rebates.get(period, 0)
    
    return 0


# ============= ENERGY TRACKER =============

class EnergyTracker:
    def __init__(self):
        self.state_file = os.path.join(CONFIG['data_folder'], CONFIG['state_file'])
        self.daily_data = defaultdict(lambda: {
            'energy_start': 0,
            'energy_end': 0,
            'energy_normal': 0,
            'energy_peak': 0,
            'energy_offpeak': 0,
            'cost_normal': 0,
            'cost_peak': 0,
            'cost_offpeak': 0,
            'max_demand_kva': 0,
            'max_demand_kw': 0,
            'max_neutral_current': 0,
        })
        self.last_reading = 0
        self.session_start_energy = 0
        self._ensure_folders()
        self.load_state()
    
    def _ensure_folders(self):
        """Create data folders if they don't exist"""
        for folder in [CONFIG['data_folder'], CONFIG['raw_folder'], CONFIG['daily_folder']]:
            if not os.path.exists(folder):
                os.makedirs(folder)
                print("Created folder: {}".format(folder))
    
    def load_state(self):
        """Load saved state from file"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.last_reading = state.get('last_reading', 0)
                    self.session_start_energy = state.get('session_start_energy', 0)
                    for day, data in state.get('daily_data', {}).items():
                        for key, value in data.items():
                            self.daily_data[day][key] = value
                    print("Loaded state from {}".format(self.state_file))
            except Exception as e:
                print("Error loading state: {}".format(e))
    
    def save_state(self):
        """Save current state to file"""
        try:
            state = {
                'last_reading': self.last_reading,
                'session_start_energy': self.session_start_energy,
                'last_save': datetime.now().isoformat(),
                'daily_data': dict(self.daily_data)
            }
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print("Error saving state: {}".format(e))
    
    def update(self, meter_data):
        """Update tracking with new meter data"""
        today = date.today().isoformat()
        
        def get_val(key):
            return meter_data.get(key, {}).get('value', 0)
        
        energy_wh = get_val('Energy_Wh')
        kva = get_val('VA_Total') / 1000
        kw = get_val('Watts_Total') / 1000
        pf = abs(get_val('PF_Avg'))
        neutral_current = get_val('Neutral_Current_Calc')
        
        # Initialize session
        if self.session_start_energy == 0:
            self.session_start_energy = energy_wh
            print("Session start energy: {} Wh".format(energy_wh))
        
        # Initialize daily tracking
        if self.daily_data[today]['energy_start'] == 0:
            self.daily_data[today]['energy_start'] = energy_wh
        
        # Calculate consumption since last reading
        if self.last_reading > 0 and energy_wh >= self.last_reading:
            delta_wh = energy_wh - self.last_reading
            tod_period = get_tod_period()
            base_rate = get_tod_rate(tod_period)
            pf_rebate = get_pf_rebate_percent(pf, tod_period)
            effective_rate = base_rate * (1 - pf_rebate / 100)
            
            delta_cost = (delta_wh / 1000) * effective_rate
            
            if tod_period == 'NORMAL':
                self.daily_data[today]['energy_normal'] += delta_wh
                self.daily_data[today]['cost_normal'] += delta_cost
            elif tod_period == 'PEAK':
                self.daily_data[today]['energy_peak'] += delta_wh
                self.daily_data[today]['cost_peak'] += delta_cost
            else:
                self.daily_data[today]['energy_offpeak'] += delta_wh
                self.daily_data[today]['cost_offpeak'] += delta_cost
        
        self.last_reading = energy_wh
        self.daily_data[today]['energy_end'] = energy_wh
        
        # Track max demand
        if kva > self.daily_data[today]['max_demand_kva']:
            self.daily_data[today]['max_demand_kva'] = kva
        if kw > self.daily_data[today]['max_demand_kw']:
            self.daily_data[today]['max_demand_kw'] = kw
        if neutral_current > self.daily_data[today]['max_neutral_current']:
            self.daily_data[today]['max_neutral_current'] = neutral_current
        
        self.save_state()
        return self.daily_data[today]
    
    def get_session_consumption(self, current_energy):
        """Get consumption for current session"""
        if self.session_start_energy > 0:
            return current_energy - self.session_start_energy
        return 0
    
    def get_today_summary(self):
        """Get today's summary data"""
        today = date.today().isoformat()
        return self.daily_data[today]


# ============= GOOGLE SHEETS LOGGER =============

class GoogleSheetsLogger:
    def __init__(self):
        self.enabled = CONFIG.get('google_sheets_enabled', False) and GSHEETS_AVAILABLE
        self.sheet = None
        self.last_push_error = None
        
        if self.enabled:
            self._connect()
    
    def _connect(self):
        """Connect to Google Sheets using OAuth"""
        try:
            creds_file = CONFIG.get('credentials_file', 'credentials.json')
            token_file = CONFIG.get('token_file', 'token.json')
            
            if not os.path.exists(creds_file):
                print("Warning: {} not found. Google Sheets disabled.".format(creds_file))
                self.enabled = False
                return
            
            creds = None
            
            # Load existing token
            if os.path.exists(token_file):
                try:
                    creds = Credentials.from_authorized_user_file(token_file, SCOPES)
                except Exception as e:
                    print("Warning: Could not load token: {}".format(e))
                    creds = None
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    print("Refreshing Google credentials...")
                    try:
                        creds.refresh(Request())
                        # Save refreshed token
                        with open(token_file, 'w') as f:
                            f.write(creds.to_json())
                    except Exception as e:
                        print("Warning: Token refresh failed: {}".format(e))
                        creds = None
                
                if not creds:
                    # Need interactive login - only works with display
                    print("Warning: No valid token. Run test_sheets_oauth.py first to generate token.json")
                    self.enabled = False
                    return
            
            gc = gspread.authorize(creds)
            
            sheet_id = CONFIG.get('google_sheet_id', '')
            if not sheet_id or sheet_id == 'YOUR_SHEET_ID_HERE':
                print("Warning: Google Sheet ID not configured. Sheets disabled.")
                self.enabled = False
                return
            
            spreadsheet = gc.open_by_key(sheet_id)
            
            # Get or create worksheet
            worksheet_name = CONFIG.get('worksheet_name', 'readings')
            try:
                self.sheet = spreadsheet.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                self.sheet = spreadsheet.add_worksheet(
                    title=worksheet_name,
                    rows=100000,
                    cols=len(SHEET_HEADERS)
                )
                self.sheet.append_row(SHEET_HEADERS)
                print("Created worksheet: {}".format(worksheet_name))
            
            print("Connected to Google Sheets")
            
        except Exception as e:
            print("Google Sheets connection failed: {}".format(e))
            self.enabled = False
    
    def push(self, meter_data, tracker):
        """Push reading to Google Sheets"""
        if not self.enabled or not self.sheet:
            return False
        
        try:
            now = datetime.now()
            today_data = tracker.get_today_summary()
            
            def get_val(key):
                return meter_data.get(key, {}).get('value', 0)
            
            tod_period = get_tod_period()
            base_rate = get_tod_rate(tod_period)
            pf_avg = abs(get_val('PF_Avg'))
            pf_rebate = get_pf_rebate_percent(pf_avg, tod_period)
            effective_rate = base_rate * (1 - pf_rebate / 100)
            
            energy_wh = get_val('Energy_Wh')
            session_energy = tracker.get_session_consumption(energy_wh)
            daily_energy = (today_data['energy_normal'] + today_data['energy_peak'] + 
                           today_data['energy_offpeak'])
            daily_cost = today_data['cost_normal'] + today_data['cost_peak'] + today_data['cost_offpeak']
            
            # Full 48-column row matching v2.1 schema
            row = [
                # Time (4)
                now.isoformat(),
                now.strftime('%Y-%m-%d'),
                now.strftime('%H:%M:%S'),
                now.hour,
                # Device (4)
                CONFIG['device_id'],
                CONFIG['location'],
                CONFIG.get('meter_serial', ''),
                get_val('Model_Number'),
                # ToD (2)
                tod_period,
                base_rate,
                # Power Watts (5)
                get_val('Watts_Total'),
                get_val('Watts_R'),
                get_val('Watts_Y'),
                get_val('Watts_B'),
                round(get_val('kW_Total'), 2),
                # Power VA (5)
                get_val('VA_Total'),
                get_val('VA_R'),
                get_val('VA_Y'),
                get_val('VA_B'),
                round(get_val('kVA_Total'), 2),
                # Power Factor (4)
                round(pf_avg, 4),
                round(get_val('PF_R'), 4),
                round(get_val('PF_Y'), 4),
                round(get_val('PF_B'), 4),
                # Voltages L-L (4)
                round(get_val('VLL_Avg'), 2),
                round(get_val('V_RY'), 2),
                round(get_val('V_YB'), 2),
                round(get_val('V_BR'), 2),
                # Voltages L-N (4)
                round(get_val('VLN_Avg'), 2),
                round(get_val('V_R'), 2),
                round(get_val('V_Y'), 2),
                round(get_val('V_B'), 2),
                # Current (4)
                round(get_val('Current_Total'), 2),
                round(get_val('Current_R'), 2),
                round(get_val('Current_Y'), 2),
                round(get_val('Current_B'), 2),
                # Neutral & Fire Safety (2)
                round(get_val('Neutral_Current_Calc'), 2),
                get_val('Fire_Risk_Level'),
                # Frequency (1)
                round(get_val('Frequency'), 2),
                # Energy (4)
                energy_wh,
                round(energy_wh / 1000, 3),
                get_val('Energy_VAh'),
                round(get_val('Energy_VAh_Derived'), 2),
                # Unbalance (2)
                round(get_val('Voltage_Unbalance_Pct'), 2),
                round(get_val('Current_Unbalance_Pct'), 2),
                # Load (1)
                round(get_val('Load_Pct'), 1),
                # Run Hours (1)
                round(get_val('Run_Hours'), 2),
                # Max Demand (2)
                round(today_data['max_demand_kva'], 2),
                round(today_data['max_demand_kw'], 2),
                # Session/Daily (2)
                round(session_energy, 2),
                round(daily_energy, 2),
                # Cost (3)
                round(pf_rebate, 2),
                round(effective_rate, 4),
                round(daily_cost, 2),
                # ESG (1)
                round(get_val('Carbon_kg'), 2),
            ]
            
            self.sheet.append_row(row, value_input_option='RAW')
            self.last_push_error = None
            return True
            
        except Exception as e:
            self.last_push_error = str(e)
            print("Google Sheets push failed: {}".format(e))
            return False


# ============= CSV LOGGER =============

class CSVLogger:
    def __init__(self):
        self.current_date = None
        self.current_file = None
    
    def _get_filename(self, log_date):
        """Generate filename for raw log"""
        month_folder = os.path.join(
            CONFIG['raw_folder'],
            log_date.strftime('%Y-%m')
        )
        if not os.path.exists(month_folder):
            os.makedirs(month_folder)
        
        return os.path.join(
            month_folder,
            "{}_{}.csv".format(CONFIG['device_id'], log_date.strftime('%Y-%m-%d'))
        )
    
    def _check_rotation(self):
        """Check if we need to rotate to new file"""
        today = date.today()
        if self.current_date != today:
            self.current_date = today
            self.current_file = self._get_filename(today)
            if not os.path.exists(self.current_file):
                with open(self.current_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(SHEET_HEADERS)
                print("Created CSV log: {}".format(self.current_file))
    
    def log(self, meter_data, tracker):
        """Log to CSV (same format as Google Sheets - full 48 columns)"""
        self._check_rotation()
        
        now = datetime.now()
        today_data = tracker.get_today_summary()
        
        def get_val(key):
            return meter_data.get(key, {}).get('value', 0)
        
        tod_period = get_tod_period()
        base_rate = get_tod_rate(tod_period)
        pf_avg = abs(get_val('PF_Avg'))
        pf_rebate = get_pf_rebate_percent(pf_avg, tod_period)
        effective_rate = base_rate * (1 - pf_rebate / 100)
        
        energy_wh = get_val('Energy_Wh')
        session_energy = tracker.get_session_consumption(energy_wh)
        daily_energy = (today_data['energy_normal'] + today_data['energy_peak'] + 
                       today_data['energy_offpeak'])
        daily_cost = today_data['cost_normal'] + today_data['cost_peak'] + today_data['cost_offpeak']
        
        # Full 48-column row matching v2.1 schema
        row = [
            # Time (4)
            now.isoformat(),
            now.strftime('%Y-%m-%d'),
            now.strftime('%H:%M:%S'),
            now.hour,
            # Device (4)
            CONFIG['device_id'],
            CONFIG['location'],
            CONFIG.get('meter_serial', ''),
            get_val('Model_Number'),
            # ToD (2)
            tod_period,
            base_rate,
            # Power Watts (5)
            get_val('Watts_Total'),
            get_val('Watts_R'),
            get_val('Watts_Y'),
            get_val('Watts_B'),
            round(get_val('kW_Total'), 2),
            # Power VA (5)
            get_val('VA_Total'),
            get_val('VA_R'),
            get_val('VA_Y'),
            get_val('VA_B'),
            round(get_val('kVA_Total'), 2),
            # Power Factor (4)
            round(pf_avg, 4),
            round(get_val('PF_R'), 4),
            round(get_val('PF_Y'), 4),
            round(get_val('PF_B'), 4),
            # Voltages L-L (4)
            round(get_val('VLL_Avg'), 2),
            round(get_val('V_RY'), 2),
            round(get_val('V_YB'), 2),
            round(get_val('V_BR'), 2),
            # Voltages L-N (4)
            round(get_val('VLN_Avg'), 2),
            round(get_val('V_R'), 2),
            round(get_val('V_Y'), 2),
            round(get_val('V_B'), 2),
            # Current (4)
            round(get_val('Current_Total'), 2),
            round(get_val('Current_R'), 2),
            round(get_val('Current_Y'), 2),
            round(get_val('Current_B'), 2),
            # Neutral & Fire Safety (2)
            round(get_val('Neutral_Current_Calc'), 2),
            get_val('Fire_Risk_Level'),
            # Frequency (1)
            round(get_val('Frequency'), 2),
            # Energy (4)
            energy_wh,
            round(energy_wh / 1000, 3),
            get_val('Energy_VAh'),
            round(get_val('Energy_VAh_Derived'), 2),
            # Unbalance (2)
            round(get_val('Voltage_Unbalance_Pct'), 2),
            round(get_val('Current_Unbalance_Pct'), 2),
            # Load (1)
            round(get_val('Load_Pct'), 1),
            # Run Hours (1)
            round(get_val('Run_Hours'), 2),
            # Max Demand (2)
            round(today_data['max_demand_kva'], 2),
            round(today_data['max_demand_kw'], 2),
            # Session/Daily (2)
            round(session_energy, 2),
            round(daily_energy, 2),
            # Cost (3)
            round(pf_rebate, 2),
            round(effective_rate, 4),
            round(daily_cost, 2),
            # ESG (1)
            round(get_val('Carbon_kg'), 2),
        ]
        
        with open(self.current_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        
        return self.current_file


# ============= MAIN MONITOR CLASS =============

class MeterMonitor:
    def __init__(self):
        self.port = None
        self.tracker = EnergyTracker()
        self.csv_logger = CSVLogger()
        self.sheets_logger = GoogleSheetsLogger()
        self.last_log_time = 0
    
    def connect(self):
        """Connect to serial port"""
        try:
            self.port = serial.Serial(
                port=CONFIG['serial_port'],
                baudrate=CONFIG['baudrate'],
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            print("Connected to {}".format(CONFIG['serial_port']))
            return True
        except Exception as e:
            print("Serial connection failed: {}".format(e))
            return False
    
    def display_readings(self, data):
        """Display current readings"""
        print("\n" + "="*80)
        print("VIREON CORTEX | {} | {}".format(
            CONFIG['device_id'],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        print("="*80)
        
        def get_val(key):
            return data.get(key, {}).get('value', 0)
        
        tod_period = get_tod_period()
        base_rate = get_tod_rate(tod_period)
        pf_avg = abs(get_val('PF_Avg'))
        
        print("\nToD: {} | Rate: Rs.{}/kWh | PF: {:.3f}".format(
            tod_period, base_rate, pf_avg))
        
        print("\n{:<15} {:>10} {:>10} {:>10} {:>10}".format(
            "", "R", "Y", "B", "Total"))
        print("-"*55)
        print("{:<15} {:>9.1f}V {:>9.1f}V {:>9.1f}V {:>9.1f}V".format(
            "Voltage (L-N)",
            get_val('V_R'), get_val('V_Y'), get_val('V_B'), get_val('VLN_Avg')))
        print("{:<15} {:>9.2f}A {:>9.2f}A {:>9.2f}A {:>9.2f}A".format(
            "Current",
            get_val('Current_R'), get_val('Current_Y'), get_val('Current_B'),
            get_val('Current_Total')))
        print("{:<15} {:>9.2f}  {:>9.2f}  {:>9.2f}  {:>9.2f}".format(
            "Power Factor",
            get_val('PF_R'), get_val('PF_Y'), get_val('PF_B'), pf_avg))
        
        print("\n{:<20} {:>15}".format("Active Power", "{:.2f} kW".format(get_val('kW_Total'))))
        print("{:<20} {:>15}".format("Apparent Power", "{:.2f} kVA".format(get_val('kVA_Total'))))
        print("{:<20} {:>15}".format("Neutral Current", "{:.2f} A ({})".format(
            get_val('Neutral_Current_Calc'), get_val('Fire_Risk_Level'))))
        print("{:<20} {:>15}".format("Frequency", "{:.2f} Hz".format(get_val('Frequency'))))
        print("{:<20} {:>15}".format("Energy", "{:.2f} kWh".format(get_val('Energy_Wh') / 1000)))
        
        today = self.tracker.get_today_summary()
        daily_cost = today['cost_normal'] + today['cost_peak'] + today['cost_offpeak']
        print("\n{:<20} {:>15}".format("Today's Cost", "Rs. {:.2f}".format(daily_cost)))
        
        if self.sheets_logger.enabled:
            status = "OK" if not self.sheets_logger.last_push_error else "Error"
            print("{:<20} {:>15}".format("Google Sheets", status))
        
        print("="*80)
    
    def run(self):
        """Main monitoring loop"""
        print("\n" + "="*80)
        print("VIREON CORTEX ENERGY MONITOR v3.0")
        print("="*80)
        print("Device: {} | Location: {}".format(CONFIG['device_id'], CONFIG['location']))
        print("Meter: {} | Serial: {}".format(
            CONFIG.get('meter_type', 'LT_WL4405'), 
            CONFIG.get('meter_serial', 'N/A')))
        print("Log Interval: {} seconds".format(CONFIG['raw_log_interval']))
        print("Google Sheets: {}".format("Enabled" if self.sheets_logger.enabled else "Disabled"))
        print("="*80)
        print("\nPress Ctrl+C to stop\n")
        
        if not self.connect():
            return
        
        try:
            while True:
                data = read_lt_meter(self.port, CONFIG['slave_id'])
                
                if data:
                    self.tracker.update(data)
                    self.display_readings(data)
                    
                    current_time = time.time()
                    if current_time - self.last_log_time >= CONFIG['raw_log_interval']:
                        csv_file = self.csv_logger.log(data, self.tracker)
                        print("\n[CSV: {}]".format(csv_file))
                        
                        if self.sheets_logger.enabled:
                            if self.sheets_logger.push(data, self.tracker):
                                print("[Sheets: Pushed]")
                            else:
                                print("[Sheets: Failed - {}]".format(
                                    self.sheets_logger.last_push_error))
                        
                        self.last_log_time = current_time
                else:
                    print("Failed to read meter")
                
                time.sleep(CONFIG['display_interval'])
                
        except KeyboardInterrupt:
            print("\n\nStopping...")
            self.tracker.save_state()
            print("State saved.")
        finally:
            if self.port:
                self.port.close()
                print("Port closed.")


# ============= MAIN =============

if __name__ == "__main__":
    monitor = MeterMonitor()
    monitor.run()
