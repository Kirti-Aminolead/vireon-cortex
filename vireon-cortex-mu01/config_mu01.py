# Vireon Cortex - MU-01 Configuration
# Location: Shed 01 (Pi 5)
# Hostname: pi-mu-01
# Pi Serial: e6aff0650cfc7062
# 
# Usage: Copy this to config.py on the Pi

CONFIG = {
    # ===== DEVICE IDENTIFICATION =====
    'device_id': 'vireon-cortex-cl01-mu-01',
    'location': 'Shed_01',
    'meter_serial': '24057940303',
    'slave_id': 1,
    
    # Pi Info (for reference)
    'pi_hostname': 'pi-mu-01',
    'pi_serial': 'e6aff0650cfc7062',
    
    # ===== SERIAL PORT =====
    'serial_port': '/dev/ttyUSB0',
    'baudrate': 9600,
    
    # ===== GOOGLE SHEETS (OAuth) =====
    'google_sheets_enabled': True,
    'google_sheet_id': 'YOUR_SHEET_ID_HERE',  # <-- UPDATE THIS
    'credentials_file': 'credentials.json',   # OAuth client credentials
    'token_file': 'token.json',               # OAuth token (from test_sheets_oauth.py)
    'worksheet_name': 'readings',
    
    # ===== METER INFO =====
    'meter_type': 'LT_WL4405',
    'meter_model': 4405,
    'contracted_load_kw': 200,
    'contracted_load_kva': 250,
    
    # CT/PT Configuration
    'ct_primary': 800,
    'ct_secondary': 5,
    'pt_primary': 1,
    'pt_secondary': 1,
    
    # ===== DATA STORAGE =====
    'data_folder': 'data',
    'raw_folder': 'data/raw',
    'daily_folder': 'data/daily',
    'state_file': 'meter_state.json',
    
    # ===== LOGGING INTERVALS =====
    'display_interval': 5,
    'raw_log_interval': 300,
    
    # ===== WBSEDCL HT INDUSTRIAL ToD RATES =====
    'rate_normal': 6.95,
    'rate_peak': 8.37,
    'rate_offpeak': 5.18,
    
    'tod_normal_start': 6,
    'tod_normal_end': 17,
    'tod_peak_start': 17,
    'tod_peak_end': 23,
    
    # ===== THRESHOLDS =====
    'neutral_current_warning': 2,
    'neutral_current_high': 5,
    'neutral_current_critical': 10,
    'voltage_unbalance_warning': 2,
    'current_unbalance_warning': 10,
    
    # ===== ESG =====
    'carbon_factor_kg_per_kwh': 0.85,
}
