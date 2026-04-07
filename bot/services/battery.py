import os
import subprocess
from datetime import datetime

def get_battery_info():
    """Reads battery capacity and status, and includes hostname and timestamp."""
    try:
        capacity_path = "/sys/class/power_supply/bq27541-0/capacity"
        status_path = "/sys/class/power_supply/bq27541-0/status"
        
        # Get Hostname
        hostname = subprocess.check_output(["hostname"], universal_newlines=True).strip()
        
        # Get Current Time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        if not os.path.exists(capacity_path) or not os.path.exists(status_path):
            return f"{hostname}\nBattery data not available.\nTime: {timestamp}"
            
        with open(capacity_path, "r") as f:
            capacity = f.read().strip()
            
        with open(status_path, "r") as f:
            status = f.read().strip()
            
        return f"{hostname}\nBattery: {capacity}%\nStatus: {status}\nTime: {timestamp}"
    except Exception as e:
        return f"Error retrieving battery info: {str(e)}"
